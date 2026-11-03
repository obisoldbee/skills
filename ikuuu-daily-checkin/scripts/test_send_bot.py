"""Check the actual sender boundary with a fake bot; never send a real message."""
import contextlib
import io
import json
from pathlib import Path
import runpy
import subprocess
import tempfile
import unittest
from unittest.mock import patch


class NoticeTests(unittest.TestCase):
    def test_only_approved_one_sentence_text_reaches_bot(self):
        with tempfile.TemporaryDirectory() as directory:
            cli=Path(directory)/'fake-cli'; cli.touch()
            config=Path(directory)/'config.json'
            config.write_text(json.dumps({'cli':str(cli),'profile':'fixture'}))
            for text in ('Ikuuu 签到异常。','Ikuuu 流量不足。'):
                args=['send-bot.py','--config',str(config),'--chat-id','oc_fixture',
                      '--text',text,'--idempotency-key','fixture-notice']
                identity=subprocess.CompletedProcess([],0,'{"identity":"bot","available":true}')
                sent=subprocess.CompletedProcess([],0)
                with patch('sys.argv',args),patch('subprocess.run',side_effect=[identity,sent]) as run:
                    with self.assertRaises(SystemExit) as exit_code:
                        runpy.run_path(str(Path(__file__).with_name('send-bot.py')),run_name='__main__')
                self.assertEqual(exit_code.exception.code,0)
                self.assertEqual(run.call_count,2)
                command=run.call_args.args[0]
                self.assertEqual(command[command.index('--text')+1],text)
                self.assertIn('bot',command)

    def test_diagnostic_paragraph_rejected_before_any_bot_call(self):
        args=['send-bot.py','--config','unused.json','--chat-id','oc_fixture',
              '--text','Ikuuu 签到异常；剩余流量未确认；空间 60；原因详情',
              '--idempotency-key','fixture-notice']
        with patch('sys.argv',args),patch('subprocess.run') as run,contextlib.redirect_stderr(io.StringIO()):
            with self.assertRaises(SystemExit) as exit_code:
                runpy.run_path(str(Path(__file__).with_name('send-bot.py')),run_name='__main__')
        self.assertEqual(exit_code.exception.code,2)
        run.assert_not_called()


if __name__=='__main__': unittest.main()
