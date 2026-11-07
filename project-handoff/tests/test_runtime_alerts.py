import json
import hashlib
import os
from contextlib import closing
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPTS = Path(__file__).resolve().parents[1] / 'scripts'
sys.path.insert(0, str(SCRIPTS))
import runtime_alerts as alerts


class RuntimeAlertsTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        self.path = self.root / 'session.jsonl'
        self.contract = dict(selection_ref='original-user-route', model='gpt-6-luna',
                             reasoning='max', model_basis='explicit_skill_route',
                             reasoning_basis='explicit_skill_route')
        self.registry = dict(transcript_root=str(self.root), sessions={'session': self.contract})
        self.event = dict(session_id='session', turn_id='turn', model='gpt-6-luna',
                          hook_event_name='Stop', transcript_path=str(self.path))
        self.write_turn()
        self.db = alerts.connect(self.root / 'state')
        self.addCleanup(self.db.close)

    def write_turn(self, turn='turn', model='gpt-6-luna', effort='max', session='session'):
        self.path.write_text('\n'.join(json.dumps(x) for x in [
            {'type': 'session_meta', 'payload': {'id': session}},
            {'type': 'turn_context', 'payload': dict(turn_id=turn, model=model, effort=effort)}
        ]))

    def test_actual_low_is_detected_and_deduplicated_across_ticks(self):
        self.write_turn(effort='low')
        self.assertIsNotNone(alerts.observe(self.event, self.registry, self.db))
        self.event['turn_id'] = 'next'
        self.write_turn(turn='next', effort='low')
        self.assertIsNone(alerts.observe(self.event, self.registry, self.db))
        payload = json.loads(self.db.execute('SELECT payload FROM alerts').fetchone()[0])
        self.assertEqual(payload['actual']['reasoning'], 'low')
        self.assertEqual(payload['kind'], 'route_mismatch')

    def test_stale_or_wrong_session_never_proves_current_effort(self):
        for kw in ({'turn': 'old'}, {'session': 'different'}, {'model': 'other'}):
            self.write_turn(**kw)
            self.assertIsNone(alerts.read_effort(self.event, self.root))
            self.assertEqual(alerts.classify(self.event, self.contract, self.root)[0], 'route_unverified')

    def test_newest_turn_wins_even_if_an_old_match_is_in_transcript(self):
        with self.path.open('a') as out:
            out.write('\n' + json.dumps({'type':'turn_context','payload':{'turn_id':'new'}}))
        self.assertIsNone(alerts.read_effort(self.event, self.root))

    def test_unselected_effort_is_not_frozen(self):
        self.contract.update(reasoning=None, reasoning_basis='platform_default')
        self.write_turn(effort='low')
        self.assertIsNone(alerts.observe(self.event, self.registry, self.db))
        self.contract['reasoning'] = 'max'
        with self.assertRaises(ValueError):
            alerts.observe(self.event, self.registry, self.db)

    def test_unknown_does_not_clear_dedup_but_match_allows_recurrence(self):
        self.write_turn(effort='low')
        alerts.observe(self.event, self.registry, self.db)
        self.write_turn(turn='old')
        alerts.observe(self.event, self.registry, self.db)
        self.write_turn(effort='low')
        self.assertIsNone(alerts.observe(self.event, self.registry, self.db))
        self.write_turn()
        alerts.observe(self.event, self.registry, self.db)
        self.write_turn(effort='low')
        self.assertIsNotNone(alerts.observe(self.event, self.registry, self.db))

    def test_model_switch_detected_even_without_effort(self):
        self.event['model'] = 'gpt-6.1-sol'
        status, actual, mismatch, unknown = alerts.classify(self.event, self.contract, self.root)
        self.assertEqual(status, 'route_mismatch')
        self.assertEqual(mismatch, ['model'])
        self.assertEqual(unknown, ['reasoning'])

    def test_permission_payload_never_copies_sensitive_input(self):
        self.event.update(hook_event_name='PermissionRequest', tool_name='Bash',
                          tool_input={'command':'secret-test-value'})
        alerts.observe(self.event, self.registry, self.db)
        payload = self.db.execute('SELECT payload FROM alerts').fetchone()[0]
        self.assertNotIn('secret-test-value', payload)
        self.assertIn('permission_required', payload)

    def test_unknown_session_and_out_of_root(self):
        self.assertIsNone(alerts.observe(dict(self.event, session_id='other'), self.registry, self.db))
        self.assertIsNone(alerts.read_effort(self.event, self.root / 'different'))

    def test_cli_pending_receipt_and_no_continuation(self):
        registry = self.root / 'registry.json'
        registry.write_text(json.dumps(self.registry))
        self.write_turn(effort='low')
        base = [sys.executable, '-B', str(SCRIPTS/'runtime_alerts.py'), '--state-dir', str(self.root/'state')]
        result = subprocess.run(base+['hook','--registry',str(registry)], input=json.dumps(self.event),
                                text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertNotIn('decision', json.loads(result.stdout))
        pending = json.loads(subprocess.check_output(base+['pending'], text=True))
        self.assertEqual(len(pending), 1)
        subprocess.run(base+['ack','--id',str(pending[0]['alert_id']),'--receipt','test-message'],
                       check=True, capture_output=True)
        self.assertEqual(json.loads(subprocess.check_output(base+['pending'], text=True)), [])


    def test_utf8_input_and_ascii_json_work_with_legacy_pipe_encodings(self):
        self.contract['selection_ref'] = 'TEST 原始选择'
        self.path = self.root / 'TEST-本轮.jsonl'
        self.event['transcript_path'] = str(self.path)
        self.write_turn(effort='low')
        registry = self.root / 'registry.json'
        registry.write_text(json.dumps(self.registry, ensure_ascii=False), encoding='utf-8')
        for encoding in ('cp1252', 'ascii'):
            with self.subTest(encoding=encoding):
                state = self.root / ('state-' + encoding)
                base = [sys.executable, '-B', str(SCRIPTS/'runtime_alerts.py'),
                        '--state-dir', str(state)]
                env = dict(os.environ, PYTHONIOENCODING=encoding)

                def run(args, data=None):
                    result = subprocess.run(base + args, input=data,
                                            capture_output=True, env=env)
                    self.assertEqual(result.returncode, 0,
                                     result.stderr.decode('utf-8', 'replace'))
                    return json.loads(result.stdout.decode('ascii'))

                data = json.dumps(self.event, ensure_ascii=False).encode('utf-8')
                self.assertNotIn('decision', run(['hook', '--registry', str(registry)], data))
                pending = run(['pending'])
                self.assertEqual(pending[0]['actual']['reasoning'], 'low')
                self.assertEqual(pending[0]['selection_ref'], self.contract['selection_ref'])
                self.assertIn('核对本轮路由', pending[0]['next_action'])
                # Output escaping must not change any already persisted dedup key.
                canonical = json.dumps(self.contract, ensure_ascii=False, sort_keys=True)
                key = 'session:' + hashlib.sha256(canonical.encode()).hexdigest() + ':route'
                with closing(alerts.connect_readonly(state)) as db:
                    self.assertEqual(db.execute('SELECT key FROM states').fetchone()[0], key)
                run(['hook', '--registry', str(registry)], data)
                self.assertEqual(len(run(['pending'])), 1)
                receipt = 'TEST 回执（仅单元测试）'
                result = run(['ack', '--id', str(pending[0]['alert_id']), '--receipt', receipt])
                self.assertEqual(result['receipt'], receipt)
                self.assertFalse(result['receipt_verified_by_helper'])
                self.assertEqual(run(['pending']), [])

    def test_hook_diagnostic_is_safe_with_non_utf8_stdout(self):
        registry = self.root / 'registry.json'
        registry.write_text(json.dumps(self.registry), encoding='utf-8')
        result = subprocess.run([sys.executable, '-B', str(SCRIPTS/'runtime_alerts.py'),
                                 '--state-dir', str(self.root/'state'), 'hook',
                                 '--registry', str(registry)], input=b'{', capture_output=True,
                                env=dict(os.environ, PYTHONIOENCODING='cp1252'))
        self.assertEqual(result.returncode, 0, result.stderr.decode('utf-8', 'replace'))
        output = json.loads(result.stdout.decode('ascii'))
        self.assertIn('检测器未完成检查', output['systemMessage'])
        self.assertNotIn('decision', output)

    def test_pending_is_readonly_and_missing_queue_is_not_created(self):
        self.write_turn(effort='low')
        alerts.observe(self.event, self.registry, self.db)
        path = self.root / 'state' / 'alerts.sqlite3'
        before = (path.read_bytes(), path.stat().st_mtime_ns, path.stat().st_mode)
        base = [sys.executable, '-B', str(SCRIPTS/'runtime_alerts.py'), '--state-dir']
        result = subprocess.run(base + [str(path.parent), 'pending'], capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(len(json.loads(result.stdout)), 1)
        self.assertEqual((path.read_bytes(), path.stat().st_mtime_ns, path.stat().st_mode), before)
        missing = self.root / 'missing-state'
        result = subprocess.run(base + [str(missing), 'pending'], capture_output=True)
        self.assertEqual(result.returncode, 1)
        self.assertIn('error', json.loads(result.stdout))
        self.assertFalse(missing.exists())

    def test_route_only_pickup_leaves_permission_events_pending(self):
        alerts.observe(dict(self.event, hook_event_name='PermissionRequest', tool_name='Bash'),
                       self.registry, self.db)
        self.write_turn(effort='low')
        alerts.observe(self.event, self.registry, self.db)
        result = subprocess.run([sys.executable, '-B', str(SCRIPTS/'runtime_alerts.py'),
                                 '--state-dir', str(self.root/'state'), 'pending', '--route-only'],
                                capture_output=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        pending = json.loads(result.stdout)
        self.assertEqual([p['kind'] for p in pending], ['route_mismatch'])
        self.assertNotIn('selection_ref', pending[0])
        self.assertEqual(self.db.execute('SELECT COUNT(*) FROM alerts WHERE receipt IS NULL').fetchone()[0], 2)


if __name__ == '__main__':
    unittest.main()
