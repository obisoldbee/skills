import fcntl
import json
from pathlib import Path
from tempfile import TemporaryDirectory
from types import SimpleNamespace
import unittest
from unittest.mock import Mock, patch
from run_checkin import run_once


class RunTests(unittest.TestCase):
    def setUp(self):
        self.tmp=TemporaryDirectory(); self.addCleanup(self.tmp.cleanup)
        self.root=Path(self.tmp.name); self.directory=self.root/'runs/2026-09-25-scheduled'
        self.args=SimpleNamespace(mode='scheduled',config=self.root/'config.json',chat_id='oc_fixture',state_dir=self.root)

    def result(self,**values):
        r=dict(service_day='2026-09-25',outcome='already_completed',remaining_points=1400,
            click_attempted=False,points_before=None,reward=None,space_ids=[71],page='closed',
            evidence='当前签到卡片显示今日已签到',actions=[{'action':'space_verified','absent':True}])
        return dict(r,**values)

    def run_round(self,result,delivery=None):
        browser=Mock(return_value=result)
        with patch('run_checkin.send_notice',return_value=delivery or {'status':'sent','message_id':'om_fixture'}) as send:
            output=run_once(self.args,self.directory,'2026-09-25',browser=browser)
        return output,browser,send

    def test_normal_once_and_cached_exact_result(self):
        first,browser,send=self.run_round(self.result())
        second,again,send_again=self.run_round(self.result(page='unconfirmed'))
        self.assertEqual(first,second);self.assertEqual(first[1],0)
        browser.assert_called_once();again.assert_not_called();send.assert_not_called();send_again.assert_not_called()

    def test_delivery_is_persisted_before_return_and_not_erased_or_resent(self):
        first,browser,send=self.run_round(self.result(outcome='failure',page='preserved',reason='自动登录未成功'))
        self.assertIn('飞书：已发送',first[0]);send.assert_called_once()
        receipt=json.loads((self.directory/'receipt.json').read_text())
        self.assertEqual(receipt['notifications'][0]['message_id'],'om_fixture')
        second,again,send_again=self.run_round(self.result())
        self.assertEqual(first,second);again.assert_not_called();send_again.assert_not_called()

    def test_interrupted_claim_reads_checkpoint_without_new_browser_or_notification(self):
        self.directory.mkdir(parents=True)
        (self.directory/'receipt.json').write_text(json.dumps({'phase':'browser_running'}))
        (self.directory/'browser.json').write_text(json.dumps(self.result(click_attempted=True,page='unconfirmed')))
        result,browser,send=self.run_round(self.result())
        self.assertIn('已尝试签到，结果待核查',result[0]);self.assertIn('71',result[0]);self.assertEqual(result[1],1)
        browser.assert_not_called();send.assert_not_called()

    def test_crash_during_sending_does_not_assume_unsent_or_resend(self):
        self.directory.mkdir(parents=True)
        (self.directory/'receipt.json').write_text(json.dumps({'phase':'reporting','notifications':[{'status':'unknown'}]}))
        result,browser,send=self.run_round(self.result())
        self.assertIn('送达未确认',result[0]);browser.assert_not_called();send.assert_not_called()

    def test_known_delivery_survives_crash_before_final_report(self):
        self.directory.mkdir(parents=True)
        (self.directory/'receipt.json').write_text(json.dumps({'phase':'reporting','notifications':[{'status':'sent','message_id':'om_fixture'}]}))
        result,browser,send=self.run_round(self.result())
        self.assertIn('飞书：已发送',result[0]);browser.assert_not_called();send.assert_not_called()

    def test_simultaneous_invocation_does_not_launch_a_second_browser(self):
        self.directory.mkdir(parents=True)
        with (self.directory/'run.lock').open('w') as lock:
            fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
            result,browser,send=self.run_round(self.result())
        self.assertIn('正在运行',result[0]);browser.assert_not_called();send.assert_not_called()

    def test_unverified_closed_flag_is_rejected(self):
        result,browser,send=self.run_round(self.result(actions=[]))
        self.assertIn('页面清理未完成',result[0]);self.assertEqual(result[1],1);send.assert_not_called()
        receipt=json.loads((self.directory/'receipt.json').read_text())
        self.assertEqual(receipt['browser']['page'],'unconfirmed')
        self.assertEqual(receipt['notifications'],[])

    def test_query_has_no_notification_or_service_state_change(self):
        self.args.mode='query-only'
        result,browser,send=self.run_round(self.result())
        self.assertEqual(result[1],0);send.assert_not_called()
        receipt=json.loads((self.directory/'receipt.json').read_text())
        self.assertNotIn('health',receipt);self.assertEqual(receipt['notifications'],[])

    def test_failed_delivery_does_not_retry_or_erase_business_result(self):
        result,browser,send=self.run_round(self.result(outcome='failure',page='preserved',reason='签到结果未核验'),{'status':'failed'})
        self.assertIn('结果：未完成',result[0]);self.assertIn('飞书：发送失败',result[0]);send.assert_called_once()
        repeated,again,retry=self.run_round(self.result());self.assertEqual(result,repeated)
        again.assert_not_called();retry.assert_not_called()


if __name__=='__main__': unittest.main()
