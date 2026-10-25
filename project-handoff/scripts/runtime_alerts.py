#!/usr/bin/env python3
"""Local, deterministic Stop/PermissionRequest hook and receipted alert outbox.

No network, model calls, scheduler mutation, or hook trust changes. Transcript
effort is a version-dependent adapter; absent/current-turn mismatches stay unknown.
"""
import argparse
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sqlite3
import sys

from validate_execution_binding import BASES

MAX_BYTES = 4 * 1024 * 1024


def encoded(value):
    return json.dumps(value, ensure_ascii=False, sort_keys=True)


def emit_json(value):
    # Escape the wire output for redirected Windows consoles; retain encoded()
    # for storage and fingerprints so existing notification keys stay stable.
    print(json.dumps(value, ensure_ascii=True, sort_keys=True))


def validate_contract(contract):
    if not isinstance(contract, dict) or not contract.get('selection_ref'):
        raise ValueError('contract needs original selection_ref')
    for axis in ('model', 'reasoning'):
        basis = contract.get(axis + '_basis', 'platform_default')
        value = contract.get(axis)
        if basis not in BASES or (basis == 'platform_default' and value is not None):
            raise ValueError('invalid basis/default for ' + axis)
        if basis != 'platform_default' and (not isinstance(value, str) or not value.strip()):
            raise ValueError('selected axis needs value: ' + axis)


def read_effort(event, root):
    """Only the newest turn context of this exact session/turn can prove effort."""
    try:
        path = Path(event.get('transcript_path') or '').resolve()
        path.relative_to(Path(root).resolve())
        with path.open('rb') as stream:
            first = json.loads(stream.readline(MAX_BYTES))
            if first.get('type') != 'session_meta' or first['payload'].get('id') != event['session_id']:
                return None
            stream.seek(0, 2)
            offset = max(0, stream.tell() - MAX_BYTES)
            stream.seek(offset)
            if offset:
                stream.readline()  # discard a possibly partial record
            data = stream.read(MAX_BYTES)
        latest = None
        for line in data.splitlines():
            try:
                row = json.loads(line)
            except (ValueError, UnicodeError):
                continue
            if row.get('type') == 'turn_context':
                latest = row.get('payload', {})
        if (latest and latest.get('turn_id') == event.get('turn_id')
                and latest.get('model') == event.get('model')):
            return latest.get('effort')
    except (OSError, ValueError, KeyError, TypeError, AttributeError):
        pass
    return None


def classify(event, contract, root):
    validate_contract(contract)
    if not event.get('turn_id') or not event.get('session_id'):
        raise ValueError('hook lacks session_id/turn_id')
    actual = {'model': event.get('model'), 'reasoning': read_effort(event, root)}
    mismatched, unknown = [], []
    for axis in ('model', 'reasoning'):
        if contract.get(axis + '_basis', 'platform_default') == 'platform_default':
            continue
        if not actual[axis]:
            unknown.append(axis)
        elif actual[axis] != contract[axis]:
            mismatched.append(axis)
    status = 'route_mismatch' if mismatched else ('route_unverified' if unknown else 'matched')
    return status, actual, mismatched, unknown


def connect(directory):
    directory.mkdir(mode=0o700, parents=True, exist_ok=True)
    db = sqlite3.connect(directory / 'alerts.sqlite3', timeout=3)
    os.chmod(directory / 'alerts.sqlite3', 0o600)
    db.execute('CREATE TABLE IF NOT EXISTS states (key TEXT NOT NULL, fingerprint TEXT NOT NULL, PRIMARY KEY(key,fingerprint))')
    db.execute('CREATE TABLE IF NOT EXISTS alerts (id INTEGER PRIMARY KEY, payload TEXT NOT NULL, receipt TEXT)')
    return db


def record(db, key, condition, payload):
    """Serialize change detection and enqueue. Repeated ticks do not re-notify."""
    fingerprint = hashlib.sha256(encoded(condition).encode()).hexdigest()
    with db:
        db.execute('BEGIN IMMEDIATE')
        if payload is None:
            db.execute('DELETE FROM states WHERE key=?', (key,))
            return None
        prior = db.execute('SELECT 1 FROM states WHERE key=? AND fingerprint=?', (key, fingerprint)).fetchone()
        if prior:
            return None
        db.execute('INSERT INTO states VALUES (?,?)', (key, fingerprint))
        payload['observed_at'] = datetime.now(timezone.utc).isoformat()
        cursor = db.execute('INSERT INTO alerts(payload) VALUES (?)', (encoded(payload),))
        return cursor.lastrowid


def observe(event, registry, db):
    if not isinstance(event, dict) or not isinstance(registry, dict):
        raise ValueError('event and registry must be objects')
    if not isinstance(registry.get('sessions'), dict):
        raise ValueError('registry.sessions must be an object')
    session = event.get('session_id')
    contract = registry.get('sessions', {}).get(session)
    if contract is None or event.get('hook_event_name') not in ('Stop', 'PermissionRequest'):
        return None
    status, actual, mismatched, unknown = classify(event, contract, registry['transcript_root'])
    base = {'session_id': session, 'turn_id': event['turn_id'],
            'selection_ref': contract['selection_ref'], 'expected': {
                axis: contract.get(axis) for axis in ('model', 'reasoning')},
            'actual': actual, 'kind': status, 'mismatched_axes': mismatched,
            'unknown_axes': unknown, 'delivery': 'pending',
            'next_action': '核对本轮路由；只暂停受影响的自动执行，保留产物和收件责任。'}
    # Unknown effort must not clear a confirmed mismatch or manufacture recovery.
    condition = [status, actual, mismatched, unknown]
    key = session + ':' + hashlib.sha256(encoded(contract).encode()).hexdigest()
    alert = record(db, key + ':route', condition, None if status == 'matched' else base)
    if event['hook_event_name'] == 'PermissionRequest':
        permission = dict(base, kind='permission_required',
                          next_action='请在原任务处理实际权限请求；通知不代表授权。')
        # Never forward command arguments, prompts, transcript text or credentials.
        permission['tool_name'] = str(event.get('tool_name', 'unknown'))[:160]
        alert = record(db, key + ':permission:' + event['turn_id'],
                       ['permission_required', permission['tool_name']], permission) or alert
    return alert


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--state-dir', required=True, type=Path)
    sub = parser.add_subparsers(dest='command', required=True)
    hook = sub.add_parser('hook')
    hook.add_argument('--registry', required=True, type=Path)
    sub.add_parser('pending')
    ack = sub.add_parser('ack')
    ack.add_argument('--id', type=int, required=True)
    ack.add_argument('--receipt', required=True, help='actual destination message/receipt reference')
    args = parser.parse_args()
    try:
        with connect(args.state_dir) as db:
            if args.command == 'hook':
                raw = sys.stdin.buffer.read(MAX_BYTES + 1)
                if len(raw) > MAX_BYTES:
                    raise ValueError('hook input too large')
                event = json.loads(raw)
                registry = json.loads(args.registry.read_text(encoding='utf-8'))
                alert = observe(event, registry, db)
                # No decision:block, exit 2 or model continuation for notification.
                emit_json({'systemMessage': '执行异常已记录到本地待通知队列；尚未证明 dots 送达。'} if alert else {})
            elif args.command == 'pending':
                emit_json([dict(json.loads(payload), alert_id=aid)
                           for aid, payload in db.execute('SELECT id,payload FROM alerts WHERE receipt IS NULL ORDER BY id')])
            else:
                if not args.receipt.strip():
                    raise ValueError('delivery receipt must not be empty')
                with db:
                    count = db.execute('UPDATE alerts SET receipt=? WHERE id=? AND receipt IS NULL',
                                       (args.receipt, args.id)).rowcount
                if count != 1:
                    raise ValueError('unknown or already acknowledged alert')
                emit_json({'acknowledged': args.id, 'receipt': args.receipt,
                           'receipt_verified_by_helper': False})
    except (OSError, ValueError, KeyError, TypeError, sqlite3.Error) as exc:
        if args.command == 'hook':
            emit_json({'systemMessage': '执行异常检测器未完成检查：' + type(exc).__name__})
            return 0  # diagnostics must never force another model turn
        emit_json({'error': str(exc)})
        return 1
    return 0


if __name__ == '__main__':
    sys.exit(main())
