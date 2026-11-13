#!/usr/bin/env python3
"""Reconcile a private rule inventory or prepare a patch; never apply proxy config."""
import argparse
from contextlib import contextmanager
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import re
import sys

LIMIT = 16 * 1024 * 1024
PACKAGE = Path(__file__).resolve().parents[1]

class ContractError(Exception):
    pass


def need(condition, code):
    if not condition:
        raise ContractError(code)


def digest(data):
    return hashlib.sha256(data).hexdigest()


def encoded(value):
    return (json.dumps(value, ensure_ascii=False, sort_keys=True, indent=2) + '\n').encode()


def read_bytes(path):
    with Path(path).open('rb') as f:
        data = f.read(LIMIT + 1)
    need(len(data) <= LIMIT, 'input_too_large')
    return data


def load(path):
    return json.loads(read_bytes(path))


def private_path(path):
    p = Path(path)
    need(p.is_absolute(), 'absolute_private_path_required')
    need(p == p.resolve(), 'private_path_must_be_resolved')
    need(not p.is_relative_to(PACKAGE), 'private_data_inside_package')
    need(not any((parent / '.git').exists() for parent in [p, *p.parents]), 'private_data_inside_git')
    return p


def binding(path):
    b = load(path)
    need(b.get('schema_version') == 1, 'binding_schema')
    need(isinstance(b.get('device_id'), str) and b['device_id'], 'device_binding_required')
    need(re.fullmatch(r'[A-Za-z_$][\w$]*', b.get('rule_array', '')) is not None, 'rule_array_required')
    source = Path(b['source'])
    need(source.is_absolute() and source == source.resolve(), 'source_path_must_be_resolved')
    state = private_path(b['state_dir'])
    need(not source.is_relative_to(state), 'source_inside_inventory')
    b['source'] = str(source)
    b['state_dir'] = str(state)
    return b


def code_mask(text):
    """Locate a literal assignment outside JS strings/comments, without eval."""
    chars = list(text)
    i = 0
    while i < len(text):
        start = i
        if text.startswith('//', i):
            i = text.find('\n', i)
            if i < 0:
                i = len(text)
        elif text.startswith('/*', i):
            end = text.find('*/', i + 2)
            need(end >= 0, 'unsupported_script_syntax')
            i = end + 2
        elif text[i] in '\"\'`':
            quote = text[i]
            i += 1
            while i < len(text):
                if text[i] == '\\':
                    i += 2
                elif text[i] == quote:
                    i += 1
                    break
                else:
                    i += 1
            else:
                raise ContractError('unsupported_script_syntax')
        else:
            i += 1
            continue
        for j in range(start, min(i, len(text))):
            if chars[j] != '\n':
                chars[j] = ' '
    return ''.join(chars)


def rule_list(rules):
    need(isinstance(rules, list) and all(isinstance(x, str) and x and '\n' not in x and '\r' not in x for x in rules), 'invalid_rule_array')
    need(len(rules) == len(set(rules)), 'duplicate_rules')
    return rules


def parse_source(data, name):
    text = data.decode('utf-8')
    mask = code_mask(text)
    matches = list(re.finditer(r'\bconst\s+' + re.escape(name) + r'\s*=\s*\[', mask))
    need(len(matches) == 1, 'unsupported_rule_assignment')
    start = matches[0].end() - 1
    try:
        rules, consumed = json.JSONDecoder().raw_decode(text[start:])
    except ValueError:
        raise ContractError('rule_array_must_be_json_literal') from None
    end = start + consumed
    need(re.match(r'\s*;', mask[end:]) is not None, 'dynamic_rule_expression')
    return rule_list(rules), text, start, end


def policy(b, rules):
    need(all(x in rules for x in b.get('protected_rules', [])), 'protected_rule_missing')
    need(not set(rules).intersection(b.get('excluded_rules', [])), 'excluded_rule_present')


def source_state(b):
    data = read_bytes(b['source'])
    rules, text, start, end = parse_source(data, b['rule_array'])
    return {'source_sha256': digest(data), 'rules': rules, 'rules_sha256': digest(encoded(rules)),
            'rule_count': len(rules)}, (text, start, end)


def current(b):
    path = Path(b['state_dir']) / 'CURRENT.json'
    if not path.exists():
        return None, 'absent'
    need(not path.is_symlink(), 'inventory_symlink')
    raw = read_bytes(path)
    doc = json.loads(raw)
    need(doc.get('schema_version') == 1 and type(doc.get('revision')) is int and doc['revision'] >= 1, 'inventory_schema')
    rule_list(doc['rules'])
    need(doc['rules_sha256'] == digest(encoded(doc['rules'])) and doc['rule_count'] == len(doc['rules']), 'inventory_integrity')
    need(doc['source'] == b['source'] and doc['device_id'] == b['device_id'] and doc['rule_array'] == b['rule_array'], 'inventory_binding_mismatch')
    return doc, digest(raw)


def delta(old, new):
    before = old['rules'] if old else []
    return {'added_count': len(set(new['rules']) - set(before)),
            'removed_count': len(set(before) - set(new['rules'])),
            'order_changed': [x for x in before if x in new['rules']] != [x for x in new['rules'] if x in before]}


def generated_rules(path):
    """Read only a conventional generated YAML block sequence, not general YAML."""
    lines = read_bytes(path).decode('utf-8').splitlines()
    markers = [i for i, x in enumerate(lines) if x == 'rules:']
    need(len(markers) == 1, 'unsupported_generated_rules')
    rules = []
    for line in lines[markers[0] + 1:]:
        if not line.strip() or line.lstrip().startswith('#'):
            continue
        if not line[0].isspace() and not line.startswith('- '):
            break
        m = re.fullmatch(r'\s*- (.+)', line)
        need(m is not None, 'unsupported_generated_rules')
        value = m[1]
        if value.startswith('"'):
            value = json.loads(value)
        elif value.startswith("'"):
            need(value.endswith("'"), 'unsupported_generated_rules')
            value = value[1:-1].replace("''", "'")
        else:
            need(value[0] not in '[{&*!>|' and ' #' not in value, 'unsupported_generated_rules')
        need(isinstance(value, str), 'unsupported_generated_rules')
        rules.append(value)
    return rules


def check(b):
    old, old_hash = current(b)
    now, _ = source_state(b)
    source_status = 'uninitialized'
    if old:
        matches = old['source_sha256'] == now['source_sha256'] and old['rules_sha256'] == now['rules_sha256']
        source_status = 'current' if matches else 'stale_source'
    result = {'status': source_status, 'source_status': source_status,
              'source_sha256': now['source_sha256'], 'rule_count': now['rule_count'],
              'inventory_sha256': old_hash, 'revision': old['revision'] if old else None,
              **delta(old, now)}
    policy(b, now['rules'])
    if b.get('generated_config'):
        result['generated_prefix_matches'] = None
        try:
            rules = generated_rules(b['generated_config'])
        except FileNotFoundError:
            generated_status = 'missing'
        except OSError:
            generated_status = 'unreadable'
        except (ContractError, ValueError):
            generated_status = 'unsupported'
        else:
            prefix_matches = rules[:now['rule_count']] == now['rules']
            result.update(generated_rule_count=len(rules), generated_prefix_matches=prefix_matches)
            generated_status = 'matched' if prefix_matches else 'mismatch'
        result['generated_status'] = generated_status
        if source_status == 'current' and generated_status != 'matched':
            result['status'] = 'generated_' + generated_status
    return result


@contextmanager
def record_lock(state):
    state.mkdir(mode=0o700, parents=True, exist_ok=True)
    need(state.stat().st_mode & 0o077 == 0, 'private_directory_permissions')
    lock = state / '.inventory-lock'
    try:
        lock.mkdir(mode=0o700)
    except FileExistsError:
        raise ContractError('inventory_writer_busy') from None
    try:
        yield
    finally:
        lock.rmdir()


def write_new(path, data):
    fd = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
    with os.fdopen(fd, 'wb') as out:
        out.write(data)
        out.flush()
        os.fsync(out.fileno())


def snapshot(b, expected_source, expected_current, evidence, write=False, allow_removals=False):
    now, _ = source_state(b)
    old, old_hash = current(b)
    need(now['source_sha256'] == expected_source, 'source_changed')
    need(old_hash == expected_current, 'inventory_changed')
    policy(b, now['rules'])
    diff = delta(old, now)
    need(allow_removals or not diff['removed_count'], 'removals_require_review')
    proof = Path(evidence).resolve()
    evidence_hash = digest(read_bytes(proof))
    need(proof.is_file(), 'evidence_required')
    result = {'status': 'snapshot_preview', 'source_sha256': now['source_sha256'], 'rule_count': now['rule_count'], **diff}
    if not write:
        return result
    state = private_path(b['state_dir'])
    with record_lock(state):
        need(current(b)[1] == expected_current, 'inventory_changed')
        need(digest(read_bytes(b['source'])) == expected_source, 'source_changed')
        doc = {'schema_version': 1, 'revision': old['revision'] + 1 if old else 1,
               'updated_at': datetime.now(timezone.utc).isoformat(), 'device_id': b['device_id'],
               'source': b['source'], 'rule_array': b['rule_array'], 'evidence_ref': str(proof),
               'evidence_sha256': evidence_hash, 'previous_inventory_sha256': old_hash, **now}
        raw = encoded(doc)
        history = state / 'history'
        history.mkdir(mode=0o700, exist_ok=True)
        need(not history.is_symlink() and history.stat().st_mode & 0o077 == 0, 'private_history_permissions')
        backup = history / ('source-' + expected_source + '.js')
        source_bytes = read_bytes(b['source'])
        need(digest(source_bytes) == expected_source, 'source_changed')
        if backup.exists():
            need(not backup.is_symlink() and digest(read_bytes(backup)) == expected_source, 'backup_integrity')
        else:
            write_new(backup, source_bytes)
        name = f"{doc['revision']:06d}-{digest(raw)}.json"
        write_new(history / name, raw)
        tmp = state / (name + '.tmp')
        write_new(tmp, raw)
        try:
            need(current(b)[1] == expected_current, 'inventory_changed')
            need(digest(read_bytes(b['source'])) == expected_source, 'source_changed')
            os.replace(tmp, state / 'CURRENT.json')
        finally:
            tmp.unlink(missing_ok=True)
        result.update(status='snapshot_saved', revision=doc['revision'], inventory_sha256=digest(raw))
        if digest(read_bytes(b['source'])) != expected_source:
            result['status'] = 'source_changed_after_snapshot'
    return result


def plan(b, changes, expected_source, expected_current, out):
    old, old_hash = current(b)
    now, (text, start, end) = source_state(b)
    need(old is not None and old_hash == expected_current, 'inventory_changed')
    need(now['source_sha256'] == expected_source == old['source_sha256'], 'source_changed')
    need(old['rules_sha256'] == now['rules_sha256'], 'inventory_integrity')
    change = load(changes)
    need(set(change) == {'add', 'remove'}, 'change_schema')
    add, remove = rule_list(change['add']), rule_list(change['remove'])
    need(not set(add).intersection(remove), 'conflicting_change')
    need(set(remove).issubset(now['rules']), 'removal_not_present')
    need(all(re.search(r',DIRECT(?:,no-resolve)?$', x) and x.count(',') >= 2 for x in add), 'addition_must_be_direct_rule')
    actual_add = [x for x in add if x not in now['rules']]
    proposed = actual_add + [x for x in now['rules'] if x not in remove]
    policy(b, proposed)
    candidate = text
    if actual_add or remove:
        candidate = text[:start] + json.dumps(proposed, ensure_ascii=False, indent=2) + text[end:]
    candidate_bytes = candidate.encode('utf-8')
    need(parse_source(candidate_bytes, b['rule_array'])[0] == proposed, 'candidate_parse_failed')
    directory = private_path(out)
    need(not Path(b['source']).is_relative_to(directory) and not Path(b['state_dir']).is_relative_to(directory), 'output_overlaps_binding')
    need(digest(read_bytes(b['source'])) == expected_source and current(b)[1] == expected_current, 'inputs_changed')
    directory.mkdir(mode=0o700, parents=False, exist_ok=False)
    write_new(directory / 'candidate.js', candidate_bytes)
    doc = {'status': 'candidate_only', 'source_sha256': expected_source, 'inventory_sha256': expected_current,
           'candidate_sha256': digest(candidate_bytes), 'rules_sha256': digest(encoded(proposed)),
           'add': actual_add, 'remove': remove, 'added_count': len(actual_add), 'removed_count': len(remove),
           'before_count': len(now['rules']), 'after_count': len(proposed)}
    write_new(directory / 'plan.json', encoded(doc))
    return {k: v for k, v in doc.items() if k not in {'add', 'remove'}}



def restore_plan(b, expected_source, expected_current, out):
    old, h = current(b)
    need(old is not None and h == expected_current, 'inventory_changed')
    policy(b, old['rules'])
    source = Path(b['source'])
    live = read_bytes(source) if source.exists() else None
    need((digest(live) if live is not None else 'absent') == expected_source, 'source_changed')
    if live is not None and digest(live) != old['source_sha256']:
        mask = code_mask(live.decode('utf-8'))
        # Only the known empty enhancement is an automatic reset candidate.
        need(re.fullmatch(r'\s*function\s+main\s*\(\s*config\s*(?:,\s*profileName\s*)?\)\s*{\s*return\s+config\s*;?\s*}\s*', mask) is not None,
             'live_source_diverged_manual_merge_required')
        # String literals hidden by the locator cannot be silently discarded.
        need(not any(ch in live.decode('utf-8') for ch in '\"\'`'), 'live_source_diverged_manual_merge_required')
    backup = Path(b['state_dir']) / 'history' / ('source-' + old['source_sha256'] + '.js')
    need(not backup.is_symlink(), 'backup_symlink')
    raw = read_bytes(backup)
    need(digest(raw) == old['source_sha256'] and parse_source(raw, b['rule_array'])[0] == old['rules'], 'backup_integrity')
    directory = private_path(out)
    need(not source.is_relative_to(directory) and not Path(b['state_dir']).is_relative_to(directory), 'output_overlaps_binding')
    need(current(b)[1] == expected_current, 'inventory_changed')
    actual = digest(read_bytes(source)) if source.exists() else 'absent'
    need(actual == expected_source, 'source_changed')
    directory.mkdir(mode=0o700, parents=False, exist_ok=False)
    write_new(directory / 'candidate.js', raw)
    result = {'status': 'candidate_only', 'operation': 'restore', 'expected_live_source_sha256': expected_source,
              'inventory_sha256': h, 'candidate_sha256': digest(raw), 'rule_count': old['rule_count']}
    write_new(directory / 'plan.json', encoded(result))
    return result


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--binding', required=True)
    sub = parser.add_subparsers(dest='command', required=True)
    sub.add_parser('check')
    for cmd in ('snapshot', 'plan', 'restore-plan'):
        p = sub.add_parser(cmd)
        p.add_argument('--expected-source-sha256', required=True)
        p.add_argument('--expected-current-sha256', required=True)
        if cmd == 'snapshot':
            p.add_argument('--evidence', required=True)
            p.add_argument('--write', action='store_true')
            p.add_argument('--allow-removals', action='store_true')
        else:
            if cmd == 'plan':
                p.add_argument('--changes', required=True)
            p.add_argument('--out', required=True)
    args = parser.parse_args()
    try:
        b = binding(args.binding)
        if args.command == 'check':
            result = check(b)
        elif args.command == 'snapshot':
            result = snapshot(b, args.expected_source_sha256, args.expected_current_sha256, args.evidence, args.write, args.allow_removals)
        elif args.command == 'restore-plan':
            result = restore_plan(b, args.expected_source_sha256, args.expected_current_sha256, args.out)
        else:
            result = plan(b, args.changes, args.expected_source_sha256, args.expected_current_sha256, args.out)
        print(json.dumps(result, ensure_ascii=False))
        return 0 if result['status'] in {'current', 'snapshot_saved', 'snapshot_preview', 'candidate_only'} else 2
    except (ContractError, OSError, ValueError, KeyError, TypeError, UnicodeError) as exc:
        # Never print parser/source excerpts, credentials, private paths or raw rules.
        print(json.dumps({'status': 'error', 'code': str(exc) if isinstance(exc, ContractError) else type(exc).__name__}))
        return 2


if __name__ == '__main__':
    sys.exit(main())
