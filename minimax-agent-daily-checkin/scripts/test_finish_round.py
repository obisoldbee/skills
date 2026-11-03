import json
from pathlib import Path
import subprocess
import tempfile
import unittest
from unittest.mock import patch
from finish_round import complete, verify_cleanup, read_task_spaces
from check_runtime import check
from service_health import send_notice


class FinishTests(unittest.TestCase):
    def data(self, **values):
        d={'service_day':'2030-01-01','outcome':'already_completed','remaining_points':1200,
           'click_attempted':False,'reward':None,'points_before':None,'page':'closed',
           'evidence':'今日已签到','space_ids':[16]}
        return {**d,**values}

    def run_result(self,d,mode='scheduled',delivery=None):
        self.sent=[]; self.phases=[]
        def sender(key,n):
            self.sent.append(n); return delivery or {'status':'sent','message_id':'om_fixture'}
        def health(phase,*args):
            self.phases.append(phase); return {'status':'not_triggered'}
        return complete(d,mode,sender,health,lambda:[])

    def test_completed_short_report_no_notice(self):
        self.assertEqual(self.run_result(self.data()).splitlines(),[
            'MiniMax｜2030-01-01','结果：今日已签到','剩余积分：1200','页面：已关闭','飞书：未触发'])
        self.assertEqual(self.sent,[]); self.assertEqual(self.phases,['available'])

    def test_runtime_failure_is_unknown_not_historical_available(self):
        text=self.run_result(self.data(outcome='runtime_unavailable',remaining_points=None,
            evidence='',page='not_created',reason='浏览器命令实际失败'))
        self.assertEqual(self.phases,['unknown']); self.assertEqual(len(self.sent),1)
        self.assertIn('未执行',text); self.assertIn('飞书：已发送',text)
        self.assertEqual(self.sent,[('MiniMax 签到异常。',[])])
        self.assertIn('浏览器命令实际失败',text)

    def test_new_reward_requires_verified_delta(self):
        d=self.data(outcome='newly_completed',click_attempted=True,points_before=800,reward=400)
        self.assertIn('结果：签到成功（+400 积分）',self.run_result(d))
        d['points_before']=900
        with self.assertRaisesRegex(ValueError,'delta'): self.run_result(d)
        self.assertEqual(self.sent,[])

    def test_old_reward_and_click_cannot_be_rewritten(self):
        for d in (self.data(reward=400),self.data(click_attempted=True)):
            with self.assertRaises(ValueError): self.run_result(d)

    def test_notification_failure_keeps_unverified_business_facts(self):
        text=self.run_result(self.data(outcome='failure',page='preserved',reason='签到结果尚未核验'),delivery={'status':'failed'})
        self.assertIn('结果：未完成',text); self.assertIn('页面：已保留',text)
        self.assertIn('飞书：发送失败',text)

    def test_completed_cleanup_defect_stays_local_for_new_and_existing_checkin(self):
        for extra in ({},{'outcome':'newly_completed','click_attempted':True,'points_before':800,'reward':400}):
            with self.subTest(extra=extra):
                text=self.run_result(self.data(page='unconfirmed',reason='本轮空间关闭未确认',**extra))
                self.assertIn('页面清理未完成',text)
                self.assertIn('飞书：未触发',text)
                self.assertEqual(self.sent,[])

    def test_missing_id_is_not_a_user_action_or_notification(self):
        d=self.data(outcome='newly_completed',click_attempted=True,points_before=800,reward=400)
        del d['space_ids']
        text=self.run_result(d)
        self.assertIn('缺少本轮完整空间 ID',text)
        self.assertIn('结果：签到成功（+400 积分）',text)
        self.assertIn('页面：关闭未确认',text)
        self.assertIn('飞书：未触发',text)
        self.assertEqual(self.sent,[])

    def test_query_has_no_health_or_message_side_effects(self):
        self.run_result(self.data(),mode='query-only')
        self.assertEqual(self.phases,[]); self.assertEqual(self.sent,[])

    def test_maintenance_uses_health_only(self):
        self.run_result(self.data(outcome='maintenance',remaining_points=None,evidence='平台维护中'))
        self.assertEqual(self.phases,['maintenance']); self.assertEqual(self.sent,[])

    def test_tracked_space_cannot_report_closed(self):
        spaces=[{'id':15,'name':'MiniMax daily checkin','createdBy':'agent'}]
        d=verify_cleanup(self.data(space_ids=[15,16]),lambda:spaces)
        self.assertEqual(d['page'],'unconfirmed')
        self.assertIn('15',d['reason'])
        text=self.run_result(d)
        self.assertIn('页面清理未完成',text)
        self.assertEqual(self.sent,[])

    def test_tracked_space_remains_even_if_renamed(self):
        d=verify_cleanup(self.data(),lambda:[{'id':16,'name':'renamed','createdBy':'user'}])
        self.assertEqual(d['page'],'unconfirmed')

    def test_unrelated_user_space_not_residue(self):
        d=verify_cleanup(self.data(),lambda:[{'id':1,'name':'MiniMax daily checkin','createdBy':'agent','ownership':'agentDelegatedToUser'}])
        self.assertEqual(d['page'],'closed')

    def test_missing_ids_or_failed_probe_never_report_closed(self):
        d=self.data(); del d['space_ids']
        self.assertEqual(verify_cleanup(d,lambda:[])['page'],'unconfirmed')
        def failed(): raise subprocess.TimeoutExpired('ego-browser',20)
        self.assertEqual(verify_cleanup(self.data(),failed)['page'],'unconfirmed')
        d=self.data(page='preserved')
        self.assertEqual(verify_cleanup(d,lambda:self.fail('must not reconnect'))['page'],'preserved')

    def test_space_reader_handles_both_streams_without_creation(self):
        for stdout,stderr in [('MINIMAX_SPACES=[]',''),('','notice\nMINIMAX_SPACES=[]')]:
            with patch('finish_round.subprocess.run',return_value=subprocess.CompletedProcess([],0,stdout,stderr)) as run:
                self.assertEqual(read_task_spaces(),[])
            self.assertIn('listTaskSpaces()',run.call_args.args[0][-1])
            self.assertNotIn('taskSpace(',run.call_args.args[0][-1])
            self.assertNotIn('finish(',run.call_args.args[0][-1])

    def test_runtime_probe_calls_cli_without_mcp_or_new_space(self):
        result=subprocess.CompletedProcess([],0,'MINIMAX_RUNTIME_OK','')
        with patch('check_runtime.shutil.which',return_value='/cli/ego-browser'),patch('check_runtime.subprocess.run',return_value=result) as run:
            self.assertEqual(check()['status'],'available')
        self.assertIn('listTaskSpaces()',run.call_args.args[0][-1])
        self.assertNotIn('taskSpace(',run.call_args.args[0][-1])

    def test_bot_transport_uses_config_and_reads_stderr(self):
        with tempfile.TemporaryDirectory() as tmp:
            cli=Path(tmp)/'cli'; cli.touch()
            cfg=Path(tmp)/'bot.json'; cfg.write_text(json.dumps({'cli':str(cli),'profile':'fixture'}))
            responses=[subprocess.CompletedProcess([],0,'{"identity":"bot","available":true}',''),
                       subprocess.CompletedProcess([],1,'','{"ok":false,"error":{"type":"authorization"}}')]
            with patch('subprocess.run',side_effect=responses) as run:
                result=send_notice(cfg,'oc_fixture','test-key',('Title',[('状态','测试')]))
            self.assertEqual(result['status'],'failed')
            self.assertEqual(run.call_args.args[0][:3],[str(cli),'--profile','fixture'])


if __name__=='__main__': unittest.main()
