"""Persistent maintenance transitions, delivery ambiguity and fixed rich-text layout."""
import json
from pathlib import Path
import tempfile
import unittest
from unittest.mock import patch
from service_health import observe, post_payload, NAMES, send_notice, locked

class HealthTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name)
        self.calls = []

    def send(self,key,notice):
        self.calls.append((key,notice))
        return {'status':'sent','message_id':'om_fixture'}

    def run_phase(self,phase,sender=None,service='volcengine-invites-monitor',extra=None):
        return observe(self.path,service,phase,sender or self.send,page='已关闭',
                       evidence='当前明确页面证据' if phase != 'unknown' else '',extra=extra)

    def test_entry_unchanged_unknown_recovery_unchanged_all_services(self):
        for service in NAMES:
            with self.subTest(service=service):
                (self.path/'state.json').unlink(missing_ok=True); self.calls=[]
                states=['available','maintenance','maintenance','unknown','maintenance','available','available']
                results=[self.run_phase(s,service=service) for s in states]
                self.assertEqual([r.get('transition') for r in results],[None,'entered',None,None,None,'recovered',None])
                self.assertEqual(len(self.calls),2)
                self.assertIn('｜维护中',self.calls[0][1][0]); self.assertIn('｜维护结束',self.calls[1][1][0])

    def test_initial_maintenance_alerts_without_previous_success(self):
        self.assertEqual(self.run_phase('maintenance')['transition'],'entered')

    def test_persistence_survives_new_helper_process(self):
        self.run_phase('maintenance')
        # A freshly imported function reads the same disk, with no in-memory incident cache.
        import runpy
        new_observe=runpy.run_path(str(Path(__file__).with_name('service_health.py')))['observe']
        result=new_observe(self.path,'volcengine-invites-monitor','maintenance',self.send,page='已关闭',evidence='维护')
        self.assertEqual(result['status'],'not_triggered'); self.assertEqual(len(self.calls),1)

    def test_rejected_delivery_retries_later_with_same_key(self):
        def rejected(key,notice):
            self.calls.append((key,notice)); return {'status':'failed'}
        self.run_phase('maintenance',rejected)
        self.run_phase('maintenance')
        self.run_phase('maintenance')
        self.assertEqual(len(self.calls),2); self.assertEqual(self.calls[0][0],self.calls[1][0])

    def test_ambiguous_delivery_not_blindly_repeated(self):
        self.run_phase('maintenance',lambda k,n:{'status':'unknown'})
        self.assertEqual(self.run_phase('maintenance')['status'],'unknown')
        self.assertEqual(self.calls,[])

    def test_interrupted_send_is_not_marked_sent_or_repeated(self):
        with self.assertRaises(RuntimeError):
            self.run_phase('maintenance',lambda k,n:(_ for _ in ()).throw(RuntimeError('crash')))
        state=json.loads((self.path/'state.json').read_text())
        self.assertEqual(state['pending']['delivery'],'attempting')
        self.assertEqual(self.run_phase('maintenance')['status'],'unknown')
        self.assertEqual(self.calls,[])

    def test_obsolete_failed_entry_is_superseded_by_recovery(self):
        self.run_phase('maintenance',lambda k,n:{'status':'failed'})
        self.assertEqual(self.run_phase('available')['transition'],'recovered')
        self.assertEqual(len(self.calls),1)

    def test_second_outage_is_a_new_incident(self):
        for phase in ['maintenance','available','maintenance']: self.run_phase(phase)
        self.assertEqual(len({k for k,n in self.calls}),3)

    def test_corrupt_state_is_not_reset_to_fresh_incident(self):
        (self.path/'state.json').write_text('not-json')
        self.assertEqual(self.run_phase('maintenance')['status'],'failed')
        self.assertEqual(self.calls,[])
        self.assertEqual((self.path/'state.json').read_text(),'not-json')

    def test_concurrent_observer_does_not_double_send(self):
        with locked(self.path):
            self.assertEqual(self.run_phase('maintenance')['status'],'failed')
            self.assertEqual(self.calls,[])
        self.run_phase('maintenance'); self.assertEqual(len(self.calls),1)

    def test_recovery_combines_actionable_business_result(self):
        self.run_phase('maintenance')
        extra=('有 3 条邀请',[('待处理','3 条'),('页面','已关闭'),('时间','now')])
        self.run_phase('available',extra=extra)
        post=post_payload(self.calls[-1][1])['zh_cn']
        labels=[row[0]['text'] for row in post['content']]
        self.assertEqual(labels.count('页面：'),1)
        self.assertIn('任务结果：',labels); self.assertIn('待处理：',labels)
        self.assertTrue(all(len(row)==2 for row in post['content']))

    def test_confirmation_requires_evidence(self):
        with self.assertRaises(ValueError):
            observe(self.path,'volcengine-invites-monitor','maintenance',self.send,page='已关闭')

    def test_sent_without_message_receipt_is_unknown(self):
        result=self.run_phase('maintenance',lambda k,n:{'status':'sent'})
        self.assertEqual(result['status'],'unknown')
        self.assertEqual(self.run_phase('maintenance')['status'],'unknown')

if __name__ == '__main__': unittest.main()
