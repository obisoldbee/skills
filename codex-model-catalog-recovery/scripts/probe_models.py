#!/usr/bin/env python3
"""Bounded catalog query. No turns, config edits, or cache-deletion commands."""
import argparse
import hashlib
import json
import os
from pathlib import Path
import queue
import stat
import subprocess
import sys
import threading
import time


class ProbeError(Exception):
    def __init__(self, kind, *, stage=None, rpc_code=None):
        super().__init__(kind)
        self.stage = stage
        self.rpc_code = rpc_code


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

    def response(request_id, method):
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
                error = obj['error']
                code = error.get('code') if isinstance(error, dict) else None
                raise ProbeError('rpc_error', stage=method, rpc_code=code if type(code) is int else None)
            if not isinstance(obj.get('result'), dict):
                raise ProbeError('invalid_result')
            return obj['result']
        raise ProbeError('notification_limit')

    try:
        send({'id': 1, 'method': 'initialize', 'params': {
            'clientInfo': {'name': 'model_catalog_diagnostic', 'version': '1.0'}}})
        response(1, 'initialize')
        send({'method': 'initialized', 'params': {}})
        models, cursors, cursor = [], set(), None
        for request_id in range(2, 22):
            params = {'includeHidden': True}
            if cursor is not None:
                params['cursor'] = cursor
            send({'id': request_id, 'method': 'model/list', 'params': params})
            result = response(request_id, 'model/list')
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


def inspect_core(binary, home, cwd, expected, timeout):
    env = dict(os.environ, CODEX_HOME=str(home))
    try:
        models = query([str(binary), 'app-server', '--listen', 'stdio://'],
                       cwd=str(cwd), env=env, timeout=timeout)
    except (ProbeError, OSError) as exc:
        result = {'status': 'query_failed', 'error': 'process_io_error'}
        if isinstance(exc, ProbeError):
            result['error'] = str(exc)
            if exc.stage:
                result['stage'] = exc.stage
            if exc.rpc_code is not None:
                result['rpc_code'] = exc.rpc_code
        return result, 2
    matches = [m for m in models if m['model'] == expected]
    visible = any(not m['hidden'] for m in matches)
    return {'status': 'catalog_received', 'binary': str(binary),
            'codex_home': str(home), 'cwd': str(cwd), 'expected_model': expected,
            'expected_visible': visible, 'desktop_ui_verified': False, 'inference_tested': False,
            'config_context_verified': False, 'launch_context': 'default_app_server_no_profile_overrides',
            'models': models}, 0 if visible else 3


def cache_start(home):
    """Return a comparable starting fingerprint, 'absent', or None when unknown."""
    path = home / 'models_cache.json'
    limit = 16 * 1024 * 1024
    try:
        info = path.lstat()
    except FileNotFoundError:
        return 'absent'
    except OSError:
        return None
    try:
        if not stat.S_ISREG(info.st_mode) or info.st_size > limit:
            return None
        with path.open('rb') as handle:
            data = handle.read(limit + 1)
        end = path.lstat()
        if (len(data) != info.st_size or end.st_size != info.st_size or
            (end.st_dev, end.st_ino, end.st_mtime_ns) != (info.st_dev, info.st_ino, info.st_mtime_ns)):
            return None
        return hashlib.sha256(data).hexdigest()
    except OSError:
        return None


def compare_cores(desktop, candidate, home, cwd, expected, timeout):
    observations = []
    for role, binary in (('desktop', desktop), ('candidate', candidate), ('desktop_recheck', desktop)):
        stamp = cache_start(home)
        result, code = inspect_core(binary, home, cwd, expected, timeout)
        observations.append({'core': role, 'cache_before': stamp, 'exit_code': code})
        if code == 2:
            next_check = 'query_error'
            break
        if role != 'candidate' and code == 0:
            next_check = 'inspect_desktop_menu'
            break
        if role == 'candidate' and code == 3:
            next_check = 'check_shared_catalog_context'
            break
    else:
        # Both desktop checks missed. A core comparison needs equal starting cache contents.
        first, candidate_run, recheck = (x['cache_before'] for x in observations)
        next_check = ('check_desktop_update_and_compatibility'
                      if candidate_run is not None and candidate_run in (first, recheck)
                      else 'check_cache_context')
    result.update(comparison=observations, next_check=next_check)
    return result, code


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--binary', required=True, type=Path)
    parser.add_argument('--compare-binary', type=Path, help='Candidate core for a controlled desktop recheck')
    parser.add_argument('--codex-home', required=True, type=Path)
    parser.add_argument('--cwd', required=True, type=Path)
    parser.add_argument('--expect', required=True)
    parser.add_argument('--timeout', type=float, default=45)
    args = parser.parse_args()
    binaries = [p for p in (args.binary, args.compare_binary) if p is not None]
    if (not all(p.is_absolute() and p.is_file() for p in binaries) or
        not all(p.is_absolute() and p.is_dir() for p in (args.codex_home, args.cwd)) or
        not 0 < args.timeout <= 60):
        parser.error('existing absolute binary/home/cwd and timeout in (0, 60] required')
    context = (args.codex_home, args.cwd, args.expect, args.timeout)
    if args.compare_binary:
        result, code = compare_cores(args.binary, args.compare_binary, *context)
    else:
        result, code = inspect_core(args.binary, *context)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return code


if __name__ == '__main__':
    sys.exit(main())
