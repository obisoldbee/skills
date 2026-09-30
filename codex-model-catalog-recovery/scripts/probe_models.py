#!/usr/bin/env python3
"""Bounded catalog query. No turns, config edits, or cache-deletion commands."""
import argparse
import json
import os
from pathlib import Path
import queue
import subprocess
import sys
import threading
import time


class ProbeError(Exception):
    pass


def query(command, *, cwd, env, timeout=45):
    """command is an argv list; injectable only in Python for offline testing."""
    deadline = time.monotonic() + timeout
    proc = subprocess.Popen(command, cwd=cwd, env=env, stdin=subprocess.PIPE,
                            stdout=subprocess.PIPE, stderr=subprocess.DEVNULL)
    inbox = queue.Queue()

    def read():
        try:
            while True:
                line = proc.stdout.readline(2 * 1024 * 1024 + 1)
                if not line:
                    inbox.put(ProbeError('server_eof'))
                    return
                if len(line) > 2 * 1024 * 1024:
                    inbox.put(ProbeError('response_too_large'))
                    return
                inbox.put(line)
                # Bound unsolicited chatter as well as individual responses.
                if inbox.qsize() > 100:
                    inbox.put(ProbeError('response_queue_limit'))
                    return
        except (OSError, ValueError):
            inbox.put(ProbeError('stdout_read_failed'))

    reader = threading.Thread(target=read, daemon=True)
    reader.start()

    def send(obj):
        if time.monotonic() >= deadline:
            raise ProbeError('timeout')
        try:
            proc.stdin.write((json.dumps(obj) + '\n').encode('utf-8'))
            proc.stdin.flush()
        except (OSError, ValueError):
            raise ProbeError('stdin_write_failed') from None

    def response(request_id):
        for _ in range(200):
            remaining = deadline - time.monotonic()
            if remaining <= 0:
                raise ProbeError('timeout')
            try:
                line = inbox.get(timeout=remaining)
            except queue.Empty:
                raise ProbeError('timeout') from None
            if isinstance(line, ProbeError):
                raise line
            try:
                obj = json.loads(line)
            except (ValueError, UnicodeDecodeError):
                raise ProbeError('invalid_json_response') from None
            if not isinstance(obj, dict):
                raise ProbeError('invalid_response_shape')
            if obj.get('id') != request_id:
                # Notifications do not count as a successful response.
                if 'id' in obj:
                    raise ProbeError('unexpected_response_id')
                continue
            if 'error' in obj:
                # Do not echo arbitrary server messages that may contain secrets.
                raise ProbeError('rpc_error')
            if not isinstance(obj.get('result'), dict):
                raise ProbeError('invalid_result')
            return obj['result']
        raise ProbeError('notification_limit')

    try:
        send({'id': 1, 'method': 'initialize', 'params': {
            'clientInfo': {'name': 'model_catalog_diagnostic', 'version': '1.0'}}})
        response(1)
        send({'method': 'initialized', 'params': {}})
        models, cursors, cursor = [], set(), None
        for request_id in range(2, 22):
            params = {'includeHidden': True}
            if cursor is not None:
                params['cursor'] = cursor
            send({'id': request_id, 'method': 'model/list', 'params': params})
            result = response(request_id)
            data = result.get('data')
            if not isinstance(data, list):
                raise ProbeError('invalid_model_list')
            for entry in data:
                if (not isinstance(entry, dict) or
                    not isinstance(entry.get('model'), str) or
                    type(entry.get('hidden')) is not bool):
                    raise ProbeError('invalid_model_entry')
                efforts = entry.get('supportedReasoningEfforts', [])
                if not isinstance(efforts, list) or any(
                    not isinstance(e, dict) or not isinstance(e.get('reasoningEffort'), str)
                    for e in efforts
                ):
                    raise ProbeError('invalid_reasoning_efforts')
                models.append({'model': entry['model'], 'hidden': entry['hidden'],
                               'reasoning_efforts': [e['reasoningEffort'] for e in efforts]})
            cursor = result.get('nextCursor')
            if cursor is None:
                return models
            if not isinstance(cursor, str) or not cursor or cursor in cursors:
                raise ProbeError('invalid_pagination_cursor')
            cursors.add(cursor)
        raise ProbeError('page_limit')
    finally:
        # Kill only our diagnostic child if it does not exit after stdin closes.
        proc.stdin.close()
        try:
            proc.wait(timeout=1)
        except subprocess.TimeoutExpired:
            proc.terminate()
            try:
                proc.wait(timeout=1)
            except subprocess.TimeoutExpired:
                proc.kill()
                proc.wait(timeout=2)
        reader.join(timeout=1)
        proc.stdout.close()


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--binary', required=True)
    parser.add_argument('--codex-home', required=True)
    parser.add_argument('--cwd', required=True)
    parser.add_argument('--expect', required=True)
    parser.add_argument('--timeout', type=float, default=45)
    args = parser.parse_args()
    binary, home, cwd = map(Path, (args.binary, args.codex_home, args.cwd))
    if (not all(p.is_absolute() for p in (binary, home, cwd)) or
        not binary.is_file() or not home.is_dir() or not cwd.is_dir() or
        not 0 < args.timeout <= 60):
        parser.error('existing absolute binary/home/cwd and timeout in (0, 60] required')
    env = dict(os.environ, CODEX_HOME=str(home))
    try:
        models = query([str(binary), 'app-server', '--listen', 'stdio://'],
                       cwd=str(cwd), env=env, timeout=args.timeout)
    except (ProbeError, OSError) as exc:
        code = str(exc) if isinstance(exc, ProbeError) else 'process_io_error'
        print(json.dumps({'status': 'query_failed', 'error': code}))
        return 2
    matches = [m for m in models if m['model'] == args.expect]
    visible = any(not m['hidden'] for m in matches)
    print(json.dumps({'status': 'catalog_received', 'binary': str(binary),
                      'codex_home': str(home), 'cwd': str(cwd),
                      'expected_model': args.expect, 'expected_visible': visible,
                      'desktop_ui_verified': False, 'inference_tested': False,
                      'models': models}, ensure_ascii=False, indent=2))
    return 0 if visible else 3


if __name__ == '__main__':
    sys.exit(main())
