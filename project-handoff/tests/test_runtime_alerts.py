import json
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
                                text=True, capture_output=True, check=True)
        self.assertNotIn('decision', json.loads(result.stdout))
        pending = json.loads(subprocess.check_output(base+['pending'], text=True))
        self.assertEqual(len(pending), 1)
        subprocess.run(base+['ack','--id',str(pending[0]['alert_id']),'--receipt','test-message'],
                       check=True, capture_output=True)
        self.assertEqual(json.loads(subprocess.check_output(base+['pending'], text=True)), [])


if __name__ == '__main__':
    unittest.main()
