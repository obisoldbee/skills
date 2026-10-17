#!/usr/bin/env python3
"""Offline contract tests. All keys and rule snapshots are synthetic temporary fixtures."""
import base64
import importlib.util
import json
from pathlib import Path
import stat
import tempfile
import unittest
from unittest.mock import patch

spec = importlib.util.spec_from_file_location('builder', Path(__file__).with_name('build_clients.py'))
builder = importlib.util.module_from_spec(spec)
spec.loader.exec_module(builder)


class BuildContract(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix='wg-client-test-')
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)
        (self.root / 'domains').write_text('# synthetic\n+.cn\n+.example.cn\n+.CN\n')
        (self.root / 'nets').write_text('1.0.1.0/24\n1.0.2.0/24\n1.0.3.0/24\n2001:db8::/32\n')
        (self.root / 'custom').write_text('DOMAIN,example.com,DIRECT\nPROCESS-NAME,ExampleApp,DIRECT\n')
        public = base64.b64encode(bytes([91]) * 32).decode()
        self.sources, self.keys = {}, {}
        for i, target in enumerate(('iphone', 'android', 'windows', 'macos'), 2):
            key = base64.b64encode(bytes([i]) * 32).decode()
            p = self.root / (target + '.conf')
            p.write_text(f'[Interface]\nPrivateKey = {key}\nAddress = 10.77.0.{i}/32\nMTU = 1380\n[Peer]\nPublicKey = {public}\nEndpoint = 203.0.113.10:51820\nAllowedIPs = 0.0.0.0/0, ::/0\nPersistentKeepalive = 25\n')
            self.sources[target], self.keys[target] = str(p), key
        self.m = {'targets': list(self.sources), 'client_configs': self.sources,
                  'output_dir': str(self.root / 'delivery'), 'ipv6_policy': 'ipv4-only',
                  'cn_domains': str(self.root / 'domains'), 'cn_networks': str(self.root / 'nets'),
                  'custom_direct_rules': str(self.root / 'custom'),
                  'expected_rule_counts': {'domains': 2, 'ipv4_networks': 2}, 'rules_as_of': 'synthetic-test'}

    def run_build(self):
        p = self.root / 'manifest.json'; p.write_text(json.dumps(self.m))
        return builder.build(p)

    def fails_without_output(self, code):
        with self.assertRaisesRegex(builder.InvalidInput, code):
            self.run_build()
        self.assertFalse(Path(self.m['output_dir']).exists())

    def test_four_targets_preserve_independent_keys_and_source_bytes(self):
        before = {k: Path(v).read_bytes() for k, v in self.sources.items()}
        self.run_build(); out = Path(self.m['output_dir'])
        for target in ('android', 'windows', 'macos'):
            c = json.loads((out / builder.FILENAMES[target]).read_text())
            self.assertEqual(c['proxies'][0]['private-key'], self.keys[target])
            self.assertEqual(c['proxies'][0]['peers'][0]['allowed-ips'], ['0.0.0.0/0'])
            self.assertEqual(c['proxy-groups'][0]['proxies'], ['WG-OUT'])
            self.assertFalse(c['ipv6']); self.assertFalse(c['dns']['ipv6'])
            self.assertTrue(c['dns']['direct-nameserver-follow-policy'])
            self.assertEqual(c['rules'][-1], 'MATCH,Overseas')
            self.assertEqual('tun' in c, target != 'android')
            self.assertEqual('PROCESS-NAME,ExampleApp,DIRECT' in c['rules'], target != 'android')
        iphone = (out / builder.FILENAMES['iphone']).read_text()
        self.assertIn('privateKey=' + self.keys['iphone'], iphone)
        self.assertIn('FINAL,Overseas', iphone)
        self.assertNotIn('PROCESS-NAME', iphone)
        for target, src in self.sources.items():
            self.assertEqual(Path(src).read_bytes(), before[target])
            self.assertNotIn('::/0', (out / 'wireguard-reference-ipv4' / (target + '.conf')).read_text())
        for p in out.rglob('*'):
            self.assertEqual(stat.S_IMODE(p.stat().st_mode), 0o700 if p.is_dir() else 0o600)
        self.assertEqual(stat.S_IMODE(out.stat().st_mode), 0o700)

    def test_missing_android_source_is_atomic(self):
        self.m['client_configs'] = {k: v for k, v in self.sources.items() if k != 'android'}
        self.fails_without_output('client_map_must_match_all_targets')

    def test_duplicate_address_and_key_are_rejected(self):
        Path(self.sources['android']).write_bytes(Path(self.sources['iphone']).read_bytes())
        self.fails_without_output('duplicate_client_address')

    def test_duplicate_key_alone_is_rejected(self):
        p = Path(self.sources['android'])
        p.write_text(p.read_text().replace(self.keys['android'], self.keys['iphone']))
        self.fails_without_output('duplicate_client_private_key')

    def test_equivalent_x25519_scalars_are_rejected(self):
        raw = bytearray(base64.b64decode(self.keys['iphone']))
        raw[0] ^= 1
        raw[31] ^= 128
        equivalent = base64.b64encode(raw).decode()
        p = Path(self.sources['android'])
        p.write_text(p.read_text().replace(self.keys['android'], equivalent))
        self.fails_without_output('duplicate_client_private_key')

    def test_mixed_server_is_rejected(self):
        p = Path(self.sources['android']); p.write_text(p.read_text().replace('203.0.113.10', '203.0.113.11'))
        self.fails_without_output('mixed_server_bindings')

    def test_incomplete_rules_are_rejected(self):
        self.m['expected_rule_counts']['domains'] = 100
        self.fails_without_output('cn_snapshot_count_mismatch')

    def test_ipv6_policy_is_explicit(self):
        del self.m['ipv6_policy']
        self.fails_without_output('explicit_ipv4_only_policy_required')

    def test_mtu_cannot_be_guessed(self):
        p = Path(self.sources['android']); p.write_text(p.read_text().replace('MTU = 1380\n', ''))
        self.fails_without_output('confirmed_mtu_required')

    def test_psk_preserved_on_mihomo_and_iphone_blocked(self):
        psk = base64.b64encode(bytes([51]) * 32).decode()
        p = Path(self.sources['android']); p.write_text(p.read_text() + 'PresharedKey = ' + psk + '\n')
        self.m['targets'] = ['android']; self.m['client_configs'] = {'android': str(p)}
        self.run_build()
        c = json.loads((Path(self.m['output_dir']) / 'android-mihomo.yaml').read_text())
        self.assertEqual(c['proxies'][0]['peers'][0]['pre-shared-key'], psk)
        p = Path(self.sources['iphone']); p.write_text(p.read_text() + 'PresharedKey = ' + psk + '\n')
        self.m['targets'] = ['iphone']; self.m['client_configs'] = {'iphone': str(p)}
        self.m['output_dir'] = str(self.root / 'second-delivery')
        self.fails_without_output('shadowrocket_psk_schema_requires_target_verification')

    def test_no_overwrite(self):
        self.run_build()
        with self.assertRaisesRegex(builder.InvalidInput, 'refuse_existing_output_directory'):
            self.run_build()

    def test_non_posix_host_stops_before_reading_inputs(self):
        with patch.object(builder.os, 'name', 'nt'), patch.object(Path, 'read_text') as read:
            with self.assertRaisesRegex(builder.InvalidInput, 'posix_generation_host_required'):
                builder.build('unused-manifest.json')
            read.assert_not_called()
        self.assertFalse(Path(self.m['output_dir']).exists())

    def test_unsafe_output_directory_stops_before_writing_secrets(self):
        original_mkdir = Path.mkdir
        output = Path(self.m['output_dir']).resolve()

        def unsafe_mkdir(path, *args, **kwargs):
            original_mkdir(path, *args, **kwargs)
            if path == output:
                path.chmod(0o755)

        with patch.object(Path, 'mkdir', unsafe_mkdir):
            with self.assertRaisesRegex(builder.InvalidInput, 'private_output_directory_permissions_required'):
                self.run_build()
        self.assertEqual(list(output.iterdir()), [])

    def test_reserved_names_are_rejected(self):
        for name in ('Overseas', 'DIRECT', 'REJECT', 'GLOBAL'):
            self.m['node_name'] = name
            self.fails_without_output('reserved_node_name')

    def test_invalid_custom_rules_fail_before_write(self):
        for rule, code in [('DOMAIN,,DIRECT', 'empty_or_control_custom_value'),
                           ('DOMAIN,-bad.example,DIRECT', 'invalid_custom_domain'),
                           ('IP-CIDR,2001:db8::/32,DIRECT', 'custom_cidr_family_mismatch'),
                           ('DOMAIN,example.com,DIRECT,no-resolve', 'invalid_custom_rule_option'),
                           ('IP-CIDR,192.0.2.0/24,DIRECT,other', 'invalid_custom_rule_option')]:
            (self.root / 'custom').write_text(rule + '\n')
            self.fails_without_output(code)


if __name__ == '__main__':
    unittest.main(verbosity=2)
