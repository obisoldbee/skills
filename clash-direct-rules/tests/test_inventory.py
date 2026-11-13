import contextlib
import importlib.util
import io
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/rules_inventory.py'
spec = importlib.util.spec_from_file_location('inventory', SCRIPT)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class InventoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.root = Path(self.temp.name).resolve()
        self.source = self.root / 'Script.js'
        self.base = ['DOMAIN,existing.example,DIRECT', 'DOMAIN,keep.example,REJECT']
        self.source.write_text(self.render(self.base))
        self.proof = self.root / 'evidence.json'
        self.proof.write_text('{"review":"synthetic"}')
        self.bind = {'schema_version': 1, 'device_id': 'fixture', 'source': str(self.source),
                     'rule_array': 'restoredRules', 'state_dir': str(self.root/'records')}
        self.bind_path = self.root/'binding.json'
        self.bind_path.write_bytes(m.encoded(self.bind))
        self.source_hash = m.digest(self.source.read_bytes())

    def tearDown(self):
        self.temp.cleanup()

    @staticmethod
    def render(rules):
        return 'function main(config) {\n const restoredRules = ' + json.dumps(rules) + ';\n config.rules = restoredRules.concat((config.rules || []).filter(x => !restoredRules.includes(x)));\n return config;\n}\n'

    def snapshot(self, **overrides):
        args = dict(b=self.bind, expected_source=self.source_hash, expected_current='absent', evidence=str(self.proof), write=True)
        args.update(overrides)
        return m.snapshot(**args)

    def prepare(self, changes):
        self.snapshot()
        self.change = self.root / 'changes.json'
        self.change.write_bytes(m.encoded(changes))
        return m.current(self.bind)[1]

    def test_check_read_only_and_initial_snapshot(self):
        self.assertEqual(m.check(self.bind)['status'], 'uninitialized')
        self.assertFalse(Path(self.bind['state_dir']).exists())
        result = self.snapshot(write=False)
        self.assertEqual(result['status'], 'snapshot_preview')
        self.assertFalse(Path(self.bind['state_dir']).exists())
        self.snapshot()
        self.assertEqual(m.check(self.bind)['status'], 'current')
        self.assertEqual(self.source.read_bytes(), self.render(self.base).encode())
        current = Path(self.bind['state_dir'])/'CURRENT.json'
        self.assertEqual(current.stat().st_mode & 0o777, 0o600)

    def test_source_change_does_not_overwrite_inventory(self):
        self.snapshot()
        old, h = m.current(self.bind)
        self.source.write_text(self.render(['DOMAIN,new.example,DIRECT'] + self.base))
        self.assertEqual(m.check(self.bind)['status'], 'stale_source')
        with self.assertRaisesRegex(m.ContractError, 'source_changed'):
            self.snapshot(expected_current=h)
        self.assertEqual(m.current(self.bind)[0], old)

    def test_old_inventory_cannot_replace_new_revision(self):
        first = self.snapshot()
        self.snapshot(expected_current=first['inventory_sha256'])
        with self.assertRaisesRegex(m.ContractError, 'inventory_changed'):
            self.snapshot(expected_current=first['inventory_sha256'])
        self.assertEqual(m.current(self.bind)[0]['revision'], 2)
        self.assertEqual(len(list((self.root/'records/history').glob('*.json'))), 2)

    def test_removal_requires_review(self):
        self.snapshot()
        h = m.current(self.bind)[1]
        self.source.write_text(self.render(self.base[:1]))
        new_hash = m.digest(self.source.read_bytes())
        with self.assertRaisesRegex(m.ContractError, 'removals_require_review'):
            self.snapshot(expected_source=new_hash, expected_current=h)
        self.snapshot(expected_source=new_hash, expected_current=h, allow_removals=True)
        self.assertEqual(m.check(self.bind)['rule_count'], 1)

    def test_comment_change_is_stale_even_with_same_rules(self):
        self.snapshot()
        self.source.write_text('// new wrapper behavior\n'+self.source.read_text())
        result = m.check(self.bind)
        self.assertEqual(result['status'], 'stale_source')
        self.assertEqual(result['added_count'], 0)

    def test_order_change_detected(self):
        self.snapshot()
        self.source.write_text(self.render(list(reversed(self.base))))
        self.assertTrue(m.check(self.bind)['order_changed'])

    def test_plan_keeps_conditions_and_non_target_bytes(self):
        condition = 'AND,((DOMAIN,cdn.example),(GEOIP,CN)),DIRECT'
        h = self.prepare({'add':[condition, self.base[0]], 'remove':[]})
        before = self.source.read_bytes()
        out = self.root/'candidate'
        result = m.plan(self.bind, self.change, self.source_hash, h, out)
        candidate = (out/'candidate.js').read_bytes()
        rules, text, a, z = m.parse_source(candidate, 'restoredRules')
        self.assertEqual(rules, [condition] + self.base)
        _, original, start, end = m.parse_source(before, 'restoredRules')
        self.assertEqual(text[:a], original[:start])
        self.assertEqual(text[z:], original[end:])
        self.assertEqual(before, self.source.read_bytes())
        self.assertEqual(m.current(self.bind)[1], h)
        self.assertEqual(result['status'], 'candidate_only')
        self.assertEqual(json.loads((out/'plan.json').read_text())['add'], [condition])
        self.assertEqual(result['added_count'], 1)
        self.assertEqual((out/'candidate.js').stat().st_mode & 0o777, 0o600)

    def test_plan_repeated_add_preserves_original_bytes(self):
        data = ('// fixture\r\nconst restoredRules = ' + json.dumps(self.base) + ';\r\n').encode()
        self.source.write_bytes(data)
        self.source_hash = m.digest(data)
        h = self.prepare({'add':[self.base[0]], 'remove':[]})
        out = self.root/'candidate'
        result = m.plan(self.bind, self.change, self.source_hash, h, out)
        self.assertEqual(json.loads((out/'plan.json').read_text())['add'], [])
        self.assertEqual((result['added_count'], result['removed_count']), (0, 0))
        self.assertEqual(result['candidate_sha256'], self.source_hash)
        self.assertEqual((out/'candidate.js').read_bytes(), data)
        self.assertEqual(m.current(self.bind)[1], h)

    def test_plan_explicit_remove_preserves_other_rules(self):
        h=self.prepare({'add':[], 'remove':[self.base[0]]})
        out=self.root/'candidate'
        m.plan(self.bind, self.change, self.source_hash,h,out)
        self.assertEqual(m.parse_source((out/'candidate.js').read_bytes(),'restoredRules')[0],[self.base[1]])

    def test_exclusions_and_protected_rules(self):
        self.bind['protected_rules']=[self.base[0]]
        self.bind['excluded_rules']=['DOMAIN-SUFFIX,revoked.example,DIRECT']
        h=self.prepare({'add':[], 'remove':[self.base[0]]})
        with self.assertRaisesRegex(m.ContractError,'protected_rule_missing'):
            m.plan(self.bind,self.change,self.source_hash,h,self.root/'bad')
        self.change.write_bytes(m.encoded({'add':self.bind['excluded_rules'],'remove':[]}))
        with self.assertRaisesRegex(m.ContractError,'excluded_rule_present'):
            m.plan(self.bind,self.change,self.source_hash,h,self.root/'bad')
        self.assertFalse((self.root/'bad').exists())

    def test_dynamic_javascript_is_not_executed(self):
        marker=self.root/'executed'
        malicious='const restoredRules = ["DOMAIN,a.example,DIRECT"].concat(run());'
        with self.assertRaisesRegex(m.ContractError,'dynamic_rule_expression'):
            m.parse_source(malicious.encode(),'restoredRules')
        self.assertFalse(marker.exists())
        for data in ['const restoredRules = buildRules();', 'const restoredRules = ["x",];']:
            with self.assertRaises(m.ContractError):m.parse_source(data.encode(),'restoredRules')

    def test_comment_and_string_decoys(self):
        data='/* const restoredRules = ["wrong"]; */\nconst s="const restoredRules = [];";\n'+self.render(self.base)
        self.assertEqual(m.parse_source(data.encode(),'restoredRules')[0],self.base)
        with self.assertRaises(m.ContractError):
            m.parse_source((self.render(self.base)+self.render(self.base)).encode(),'restoredRules')

    def test_generated_prefix_check(self):
        self.snapshot()
        y=self.root/'generated.yaml'
        self.bind['generated_config']=str(y)
        y.write_text('secret: DO_NOT_OUTPUT\nrules:\n'+''.join('- '+x+'\n' for x in self.base)+ '- MATCH,proxy\n')
        result=m.check(self.bind)
        self.assertEqual(result['generated_rule_count'],3)
        self.assertTrue(result['generated_prefix_matches'])
        self.assertNotIn('DO_NOT_OUTPUT',json.dumps(result))
        y.write_text('rules:\n- MATCH,proxy\n')
        self.assertEqual(m.check(self.bind)['status'],'generated_mismatch')

    def test_stale_source_survives_generated_file_errors_and_prefix_differences(self):
        inventory_hash = self.snapshot()['inventory_sha256']
        self.source.write_text(self.render(['DOMAIN,new.example,DIRECT'] + self.base))
        source_hash = m.digest(self.source.read_bytes())
        generated = self.root/'generated.yaml'
        self.bind['generated_config'] = str(generated)
        self.bind_path.write_bytes(m.encoded(self.bind))
        for state, content, matches in (
                ('mismatch', 'rules:\n- MATCH,proxy\n', False),
                ('missing', None, None),
                ('unsupported', 'private_field: SYNTHETIC_HIDDEN\n', None)):
            with self.subTest(state=state):
                if content is None:
                    generated.unlink()
                else:
                    generated.write_text(content)
                proc = subprocess.run([sys.executable,'-B',str(SCRIPT),'--binding',str(self.bind_path),'check'],
                                      capture_output=True,text=True)
                self.assertEqual(proc.returncode, 2)
                result = json.loads(proc.stdout)
                self.assertEqual((result['status'], result['source_status']), ('stale_source','stale_source'))
                self.assertEqual((result['generated_status'], result['generated_prefix_matches']), (state,matches))
                self.assertEqual((result['source_sha256'], result['inventory_sha256']), (source_hash, inventory_hash))
                self.assertEqual((result['added_count'], result['removed_count'], result['order_changed']), (1,0,False))
                self.assertNotIn('SYNTHETIC_HIDDEN', proc.stdout + proc.stderr)
                self.assertNotIn(str(self.root), proc.stdout + proc.stderr)
                self.assertEqual(m.current(self.bind)[1], inventory_hash)

    def test_integrity_mismatch(self):
        self.snapshot()
        f=self.root/'records/CURRENT.json';d=json.loads(f.read_text());d['rules'][0]='changed'
        f.write_bytes(m.encoded(d))
        with self.assertRaisesRegex(m.ContractError,'inventory_integrity'):m.check(self.bind)

    def test_private_data_cannot_enter_git_or_package(self):
        (self.root/'.git').mkdir()
        with self.assertRaisesRegex(m.ContractError,'private_data_inside_git'):m.private_path(str(self.root/'records'))
        with self.assertRaisesRegex(m.ContractError,'private_data_inside_package'):m.private_path(str(m.PACKAGE/'private'))

    def test_safe_error_output(self):
        self.source.write_text('const restoredRules = [SECRET_TOKEN_BROWSING_HISTORY];')
        proc=subprocess.run([sys.executable,'-B',str(SCRIPT),'--binding',str(self.bind_path),'check'],capture_output=True,text=True)
        self.assertEqual(proc.returncode,2)
        self.assertNotIn('SECRET_TOKEN',proc.stdout+proc.stderr)
        self.assertNotIn(str(self.source),proc.stdout+proc.stderr)
        self.assertEqual(json.loads(proc.stdout)['code'],'rule_array_must_be_json_literal')

    def test_restore_missing_or_reset_source_from_latest_snapshot(self):
        self.snapshot()
        h=m.current(self.bind)[1]
        original=self.source.read_bytes()
        self.source.unlink()
        result=m.restore_plan(self.bind,'absent',h,self.root/'restore')
        self.assertEqual((self.root/'restore/candidate.js').read_bytes(),original)
        self.assertFalse(self.source.exists())
        self.source.write_text('function main(config, profileName) { return config; }')
        m.restore_plan(self.bind,m.digest(self.source.read_bytes()),h,self.root/'reset')
        self.assertEqual((self.root/'reset/candidate.js').read_bytes(),original)

    def test_restore_preserves_new_live_edits(self):
        self.snapshot()
        self.source.write_text(self.render(['DOMAIN,new.example,DIRECT']+self.base))
        h=m.current(self.bind)[1]
        with self.assertRaisesRegex(m.ContractError,'live_source_diverged_manual_merge_required'):
            m.restore_plan(self.bind,m.digest(self.source.read_bytes()),h,self.root/'bad-restore')
        self.assertFalse((self.root/'bad-restore').exists())

    def test_restore_rejects_tampered_backup(self):
        self.snapshot()
        backup=self.root/'records/history'/('source-'+self.source_hash+'.js')
        backup.write_text('tampered')
        self.source.unlink()
        with self.assertRaisesRegex(m.ContractError,'backup_integrity'):
            m.restore_plan(self.bind,'absent',m.current(self.bind)[1],self.root/'bad-restore')

    def test_busy_writer_and_existing_output_preserved(self):
        self.snapshot()
        lock=self.root/'records/.inventory-lock';lock.mkdir()
        with self.assertRaisesRegex(m.ContractError,'inventory_writer_busy'):
            self.snapshot(expected_current=m.current(self.bind)[1])
        self.assertTrue(lock.exists())
        lock.rmdir()
        self.change=self.root/'changes.json';self.change.write_bytes(m.encoded({'add':[],'remove':[]}))
        out=self.root/'existing';out.mkdir();(out/'mine').write_text('keep')
        with self.assertRaises(FileExistsError):
            m.plan(self.bind,self.change,self.source_hash,m.current(self.bind)[1],out)
        self.assertEqual((out/'mine').read_text(),'keep')


if __name__ == '__main__':
    unittest.main()
