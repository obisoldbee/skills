"""Offline stdio servers; never start Codex or access real credentials."""
import importlib.util
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import time
import unittest
from unittest.mock import patch
import contextlib
import io

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts' / 'probe_models.py'
spec = importlib.util.spec_from_file_location('probe_models', SCRIPT)
probe = importlib.util.module_from_spec(spec)
spec.loader.exec_module(probe)

SERVER = r'''
import json, os, sys, time
from pathlib import Path
mode = sys.argv[1]
Path('child.pid').write_text(str(os.getpid()))
def read():
    return json.loads(sys.stdin.readline())
def reply(i, result):
    print(json.dumps({'id': i, 'result': result}), flush=True)
def fail(i, code):
    error = {'code':code, 'message':'SECRET-SHOULD-NOT-LEAK', 'data':{'private':'SYNTHETIC-HIDDEN'}}
    print(json.dumps({'id':i, 'error':error}), flush=True)
first = read()
assert first['method'] == 'initialize'
if mode == 'initialize_error':
    fail(first['id'], -32602)
    assert sys.stdin.readline() == ''
    sys.exit()
if mode == 'timeout':
    time.sleep(10)
    sys.exit()
reply(first['id'], {'userAgent': 'offline-fixture'})
assert read()['method'] == 'initialized'
request = read()
assert request['method'] == 'model/list'
assert request['params'] == {'includeHidden': True}
if mode == 'error':
    print(json.dumps({'id': request['id'], 'error': {'message': 'SECRET-SHOULD-NOT-LEAK'}}), flush=True)
elif mode in ('method_error', 'non_integer', 'bool_code'):
    fail(request['id'], {'method_error':-32601, 'non_integer':'PRIVATE-ERROR', 'bool_code':True}[mode])
elif mode == 'eof':
    sys.exit()
elif mode == 'invalid':
    reply(request['id'], {'data': [{'model': 'target', 'hidden': 'false'}]})
else:
    print(json.dumps({'method': 'notice', 'params': {}}), flush=True)
    entry = {'model': 'target', 'hidden': mode == 'hidden',
             'supportedReasoningEfforts': [{'reasoningEffort': 'max'}]}
    if mode in ('pages', 'loop'):
        reply(request['id'], {'data': [], 'nextCursor': 'second'})
        request = read()
        assert request['method'] == 'model/list'
        assert request['params']['cursor'] == 'second'
    if mode == 'shared':
        cache = Path(os.environ['CODEX_HOME']) / 'models_cache.json'
        if not cache.exists():
            mode = 'missing'
            cache.write_text('{"synthetic":true}')
    reply(request['id'], {'data': [] if mode == 'missing' else [entry],
                          'nextCursor': 'second' if mode == 'loop' else None})
# No other RPCs (such as thread/start or turn/start) are permitted.
assert sys.stdin.readline() == ''
'''


class ProbeTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name)
        self.server = self.root / 'fake_server.py'
        self.server.write_text(SERVER, encoding='utf-8')

    def tearDown(self):
        self.temp.cleanup()

    def run_server(self, mode, timeout=3):
        return probe.query([sys.executable, '-B', str(self.server), mode],
                           cwd=str(self.root), env=dict(os.environ), timeout=timeout)

    def cli_with_servers(self, modes, compare=False):
        original_query = probe.query
        modes = iter(modes)
        def fake_core(command, **kwargs):
            return original_query([sys.executable, '-B', str(self.server), next(modes)], **kwargs)
        argv = [str(SCRIPT), '--binary', sys.executable, '--codex-home', str(self.root),
                '--cwd', str(self.root), '--expect', 'target']
        if compare:
            argv += ['--compare-binary', str(self.server)]
        with patch.object(sys, 'argv', argv), patch.object(probe, 'query', side_effect=fake_core), \
             contextlib.redirect_stdout(io.StringIO()) as output:
            code = probe.main()
        return code, json.loads(output.getvalue())

    def test_success_and_reasoning(self):
        self.assertEqual(self.run_server('success'), [
            {'model': 'target', 'hidden': False, 'reasoning_efforts': ['max']}])

    def test_pagination_and_notifications(self):
        self.assertEqual(self.run_server('pages')[0]['model'], 'target')

    def test_hidden_preserved(self):
        self.assertTrue(self.run_server('hidden')[0]['hidden'])

    def test_missing_preserved(self):
        self.assertEqual(self.run_server('missing'), [])

    def test_rpc_error_does_not_echo_secret(self):
        with self.assertRaisesRegex(probe.ProbeError, '^rpc_error$'):
            self.run_server('error')

    def test_cli_rpc_errors_keep_only_local_stage_and_integer_code(self):
        for mode, stage, rpc_code in [('initialize_error', 'initialize', -32602),
                                      ('method_error', 'model/list', -32601),
                                      ('non_integer', 'model/list', None),
                                      ('bool_code', 'model/list', None)]:
            with self.subTest(mode=mode):
                code, result = self.cli_with_servers([mode])
                expected = {'status':'query_failed', 'error':'rpc_error', 'stage':stage}
                if rpc_code is not None:
                    expected['rpc_code'] = rpc_code
                self.assertEqual((code, result), (2, expected))

    def test_shared_cache_rechecks_desktop_and_routes_to_its_menu(self):
        code, result = self.cli_with_servers(['shared']*3, compare=True)
        runs = result['comparison']
        self.assertEqual(code, 0)
        self.assertEqual([(r['core'], r['exit_code']) for r in runs],
                         [('desktop',3), ('candidate',0), ('desktop_recheck',0)])
        self.assertEqual(runs[0]['cache_before'], 'absent')
        self.assertEqual(len(runs[1]['cache_before']), 64)
        self.assertEqual(runs[1]['cache_before'], runs[2]['cache_before'])
        self.assertEqual(result['next_check'], 'inspect_desktop_menu')
        self.assertFalse(result['desktop_ui_verified'])

    def test_comparison_requires_comparable_cache_for_persistent_difference(self):
        modes = ['missing', 'success', 'missing']
        code, result = self.cli_with_servers(modes, compare=True)
        self.assertEqual((code, result['next_check']), (3, 'check_desktop_update_and_compatibility'))
        (self.root/'models_cache.json').mkdir()
        code, result = self.cli_with_servers(modes, compare=True)
        self.assertEqual((code, result['next_check']), (3, 'check_cache_context'))

    def test_comparison_stops_after_visible_desktop_or_query_error(self):
        for modes, code, next_check in ((['success'], 0, 'inspect_desktop_menu'),
                                        (['missing','missing'], 3, 'check_shared_catalog_context'),
                                        (['initialize_error'], 2, 'query_error'),
                                        (['missing','method_error'], 2, 'query_error')):
            with self.subTest(modes=modes):
                actual, result = self.cli_with_servers(modes, compare=True)
                self.assertEqual((actual, result['next_check']), (code, next_check))
                self.assertEqual(len(result['comparison']), len(modes))

    def test_eof(self):
        with self.assertRaisesRegex(probe.ProbeError, 'server_eof'):
            self.run_server('eof')

    def test_invalid_visibility_is_not_false(self):
        with self.assertRaisesRegex(probe.ProbeError, 'invalid_model_entry'):
            self.run_server('invalid')

    def test_repeated_cursor(self):
        with self.assertRaisesRegex(probe.ProbeError, 'invalid_pagination_cursor'):
            self.run_server('loop')

    def test_timeout_bounded_and_child_reaped(self):
        before = time.monotonic()
        with self.assertRaisesRegex(probe.ProbeError, 'timeout'):
            self.run_server('timeout', timeout=0.3)
        self.assertLess(time.monotonic() - before, 4)
        if os.name == 'posix':
            pid = int((self.root / 'child.pid').read_text())
            with self.assertRaises(ProcessLookupError):
                os.kill(pid, 0)

    def test_cli_rejects_missing_paths_without_launch(self):
        out = subprocess.run([sys.executable, '-B', str(SCRIPT),
            '--binary', str(self.root / 'absent'), '--codex-home', str(self.root),
            '--cwd', str(self.root), '--expect', 'target'], capture_output=True, text=True)
        self.assertEqual(out.returncode, 2)
        self.assertFalse((self.root / 'child.pid').exists())

    def test_cli_exit_codes_and_no_ui_claim(self):
        argv = [str(SCRIPT), '--binary', sys.executable,
                '--codex-home', str(self.root), '--cwd', str(self.root),
                '--expect', 'target']
        for models, code in [([], 3), ([{'model': 'target', 'hidden': True}], 3),
                             ([{'model': 'target', 'hidden': False}], 0)]:
            with self.subTest(models=models), patch.object(sys, 'argv', argv), \
                 patch.object(probe, 'query', return_value=models), \
                 contextlib.redirect_stdout(io.StringIO()) as output:
                self.assertEqual(probe.main(), code)
                result = json.loads(output.getvalue())
                self.assertFalse(result['desktop_ui_verified'])
                self.assertFalse(result['inference_tested'])
                self.assertFalse(result['config_context_verified'])
                self.assertEqual('default_app_server_no_profile_overrides', result['launch_context'])


if __name__ == '__main__':
    unittest.main()
