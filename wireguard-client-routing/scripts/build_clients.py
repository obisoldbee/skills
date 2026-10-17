#!/usr/bin/env python3
"""Build complete IPv4 WireGuard routing files from explicit, private inputs. No network or server writes."""
import argparse
import base64
import configparser
import hashlib
import io
import ipaddress
import json
import os
from pathlib import Path
import re
import stat
import sys

PLATFORMS = {'iphone', 'android', 'windows', 'macos'}
FILENAMES = {'iphone': 'iphone-shadowrocket.conf', 'android': 'android-mihomo.yaml',
             'windows': 'windows-mihomo.yaml', 'macos': 'macos-mihomo.yaml'}


class InvalidInput(Exception):
    pass


def require(condition, code):
    if not condition:
        raise InvalidInput(code)


def valid_domain(value):
    try:
        ascii_value = value.encode('idna').decode('ascii')
        return len(ascii_value) <= 253 and all(re.fullmatch(r'[A-Za-z0-9_](?:[A-Za-z0-9_-]{0,61}[A-Za-z0-9_])?', label) for label in ascii_value.split('.'))
    except UnicodeError:
        return False


def build(manifest_path):
    require(os.name == 'posix', 'posix_generation_host_required')
    manifest_path = Path(manifest_path).resolve()
    m = json.loads(manifest_path.read_text(encoding='utf-8'))
    targets = m.get('targets', [])
    require(isinstance(targets, list) and targets and all(isinstance(x, str) for x in targets), 'targets_required')
    require(len(set(targets)) == len(targets) and set(targets) <= PLATFORMS, 'invalid_target_list')
    require(set(m.get('client_configs', {})) == set(targets), 'client_map_must_match_all_targets')
    require(m.get('ipv6_policy') == 'ipv4-only', 'explicit_ipv4_only_policy_required')
    require(isinstance(m.get('rules_as_of'), str) and m['rules_as_of'].strip(), 'rules_as_of_required')
    node = m.get('node_name', 'WG-OUT')
    require(bool(re.fullmatch(r'[A-Za-z][A-Za-z0-9_-]{0,47}', node)), 'invalid_node_name')
    require(node.upper() not in {'OVERSEAS', 'DIRECT', 'REJECT', 'REJECT-DROP', 'GLOBAL', 'PASS', 'COMPATIBLE'}, 'reserved_node_name')
    out = Path(m['output_dir']).expanduser()
    require(out.is_absolute(), 'absolute_output_dir_required')
    out = out.resolve()
    require(not out.exists(), 'refuse_existing_output_directory')
    hashes = []

    def read_input(value):
        p = Path(value).expanduser()
        require(p.is_absolute() and p.is_file(), 'absolute_existing_input_required')
        p = p.resolve()
        require(not p.is_relative_to(out), 'source_output_overlap')
        data = p.read_bytes()
        hashes.append({'path': str(p), 'sha256': hashlib.sha256(data).hexdigest()})
        return data.decode('utf-8-sig')

    domains = []
    for row in read_input(m['cn_domains']).splitlines():
        s = row.strip()
        if not s or s.startswith('#'):
            continue
        require(s.startswith('+.') and valid_domain(s[2:]), 'invalid_cn_domain_row')
        domains.append(s.lower())
    domains = list(dict.fromkeys(domains))
    networks = []
    for row in read_input(m['cn_networks']).splitlines():
        s = row.strip()
        if not s or s.startswith('#'):
            continue
        n = ipaddress.ip_network(s)
        if n.version == 4:
            networks.append(n)
    networks = [str(n) for n in ipaddress.collapse_addresses(networks)]
    require(bool(domains) and bool(networks), 'empty_cn_snapshot')
    expected = m.get('expected_rule_counts', {})
    require(expected.get('domains') == len(domains) and expected.get('ipv4_networks') == len(networks), 'cn_snapshot_count_mismatch')
    custom = []
    if m.get('custom_direct_rules'):
        for row in read_input(m['custom_direct_rules']).splitlines():
            row = row.strip()
            if not row or row.startswith('#'):
                continue
            parts = row.split(',')
            require(len(parts) in (3, 4) and parts[2] == 'DIRECT', 'custom_rules_must_be_direct')
            require(parts[0] in {'DOMAIN', 'DOMAIN-SUFFIX', 'IP-CIDR', 'IP-CIDR6', 'PROCESS-NAME', 'PROCESS-PATH', 'PROCESS-PATH-REGEX'}, 'unsupported_custom_rule')
            kind, value = parts[:2]
            require(bool(value) and not any(ord(c) < 32 for c in value), 'empty_or_control_custom_value')
            require(len(parts) == 3 or (parts[3] == 'no-resolve' and kind in {'IP-CIDR', 'IP-CIDR6'}), 'invalid_custom_rule_option')
            if kind in {'DOMAIN', 'DOMAIN-SUFFIX'}:
                require(valid_domain(value), 'invalid_custom_domain')
            elif kind in {'IP-CIDR', 'IP-CIDR6'}:
                try:
                    network = ipaddress.ip_network(value)
                except ValueError:
                    raise InvalidInput('invalid_custom_cidr') from None
                require(network.version == (4 if kind == 'IP-CIDR' else 6), 'custom_cidr_family_mismatch')
            custom.append(row)
    custom = list(dict.fromkeys(custom))

    peers = {}
    for platform in targets:
        text = read_input(m['client_configs'][platform])
        cp = configparser.ConfigParser(interpolation=None)
        cp.optionxform = str
        try:
            cp.read_string(text)
            require(set(cp.sections()) == {'Interface', 'Peer'}, 'one_peer_source_required')
            interface, peer = cp['Interface'], cp['Peer']
            address = ipaddress.ip_interface(interface['Address'])
            require(address.version == 4 and address.network.prefixlen == 32, 'one_ipv4_client_32_required')
            private, public = interface['PrivateKey'], peer['PublicKey']
            private_bytes = bytearray(base64.b64decode(private, validate=True))
            require(len(private_bytes) == 32, 'invalid_private_key')
            # X25519 ignores these scalar bits. Distinct spellings must not reuse a peer identity.
            private_bytes[0] &= 248
            private_bytes[31] = (private_bytes[31] & 127) | 64
            require(len(base64.b64decode(public, validate=True)) == 32, 'invalid_server_public_key')
            endpoint = peer['Endpoint'].rsplit(':', 1)
            require(len(endpoint) == 2 and ipaddress.ip_address(endpoint[0]).version == 4, 'literal_ipv4_endpoint_required')
            require('MTU' in interface, 'confirmed_mtu_required')
            port = int(endpoint[1]); mtu = int(interface['MTU']); keepalive = int(peer.get('PersistentKeepalive', '0'))
            require(1 <= port <= 65535 and 576 <= mtu <= 9000 and 0 <= keepalive <= 65535, 'invalid_numeric_field')
            psk = peer.get('PresharedKey')
            if psk:
                require(len(base64.b64decode(psk, validate=True)) == 32, 'invalid_preshared_key')
        except InvalidInput:
            raise
        except Exception:
            raise InvalidInput('invalid_source_config_' + platform) from None
        # The bundled Shadowrocket profile has no independently verified PSK field schema.
        require(not (platform == 'iphone' and psk), 'shadowrocket_psk_schema_requires_target_verification')
        peers[platform] = {'cp': cp, 'ip': str(address.ip), 'private': private, 'identity': bytes(private_bytes), 'public': public,
                           'server': endpoint[0], 'port': port, 'mtu': mtu, 'keepalive': keepalive, 'psk': psk}
    require(len({p['ip'] for p in peers.values()}) == len(peers), 'duplicate_client_address')
    require(len({p['identity'] for p in peers.values()}) == len(peers), 'duplicate_client_private_key')
    require(len({(p['server'], p['port'], p['public']) for p in peers.values()}) == 1, 'mixed_server_bindings')
    direct_dns = ['223.5.5.5#DIRECT', '119.29.29.29#DIRECT']
    dns_policy = {'rule-set:cn_domain': direct_dns, '+.lan': ['system'], '+.local': ['system']}
    for r in custom:
        kind, value = r.split(',')[:2]
        if kind in ('DOMAIN', 'DOMAIN-SUFFIX'):
            dns_policy[value if kind == 'DOMAIN' else '+.' + value] = direct_dns
    lan = ['0.0.0.0/8', '10.0.0.0/8', '100.64.0.0/10', '127.0.0.0/8', '169.254.0.0/16', '172.16.0.0/12', '192.168.0.0/16', '224.0.0.0/4', '255.255.255.255/32']
    rendered, counts = {}, {}
    for platform, p in peers.items():
        mobile = platform in ('iphone', 'android')
        selected = [r for r in custom if not mobile or not r.startswith('PROCESS-')]
        rules = list(dict.fromkeys(['IP-CIDR6,::/0,REJECT,no-resolve', f'IP-CIDR,{p["server"]}/32,DIRECT,no-resolve'] + selected +
                    ['DOMAIN,localhost,DIRECT', 'DOMAIN-SUFFIX,local,DIRECT', 'DOMAIN-SUFFIX,lan,DIRECT'] +
                    ['IP-CIDR,' + n + ',DIRECT,no-resolve' for n in lan]))
        counts[platform] = {'custom_rules_preserved': len(selected), 'desktop_process_rules_not_applied': len(custom) - len(selected)}
        if platform == 'iphone':
            node_line = f'{node} = wireguard, {p["server"]}, {p["port"]}, privateKey={p["private"]}, publicKey={p["public"]}, ip={p["ip"]}/32, dns=1.1.1.1, mtu={p["mtu"]}, keepalive={p["keepalive"]}, udp=1'
            text = ['# Private iPhone configuration; Global Routing = Configuration.', '[General]', 'bypass-system = true',
                    'ipv6 = false', 'prefer-ipv6 = false', 'dns-direct-system = false', 'dns-direct-fallback-proxy = false',
                    'dns-server = https://1.1.1.1/dns-query#proxy=' + node + ', https://8.8.8.8/dns-query#proxy=' + node,
                    'direct-dns-server = 223.5.5.5, 119.29.29.29', '', '[Proxy]', node_line,
                    '', '[Proxy Group]', 'Overseas = select, ' + node, '', '[Rule]']
            text += rules + ['DOMAIN-SUFFIX,' + d[2:] + ',DIRECT' for d in domains] + ['IP-CIDR,' + n + ',DIRECT' for n in networks] + ['FINAL,Overseas', '']
            rendered[FILENAMES[platform]] = '\n'.join(text)
            rendered['iphone-node-fields.txt'] = '\n'.join(['Private iPhone node fields', 'Type WireGuard', 'Server ' + p['server'], 'Port ' + str(p['port']),
                'IP ' + p['ip'] + '/32', 'Private key ' + p['private'], 'Server public key ' + p['public'], 'MTU ' + str(p['mtu']), 'Keepalive ' + str(p['keepalive']), 'PSK empty', 'IPv6 empty', ''])
        else:
            mixed_port = m.get('mixed_ports', {}).get(platform, 7890 if platform == 'android' else 7897)
            require(type(mixed_port) is int and 1 <= mixed_port <= 65535, 'invalid_mixed_port')
            wgpeer = {'server': p['server'], 'port': p['port'], 'public-key': p['public'], 'allowed-ips': ['0.0.0.0/0']}
            if p['psk']:
                wgpeer['pre-shared-key'] = p['psk']
            cfg = {'mixed-port': mixed_port, 'mode': 'rule', 'ipv6': False, 'allow-lan': False, 'bind-address': '127.0.0.1',
                   'log-level': 'info', 'geo-auto-update': False,
                   'dns': {'enable': True, 'listen': '127.0.0.1:1053', 'ipv6': False, 'enhanced-mode': 'fake-ip',
                           'fake-ip-range': '198.18.0.1/16', 'fake-ip-filter': ['*.lan', '*.local', 'localhost', '*.localhost'],
                           'respect-rules': True, 'default-nameserver': ['223.5.5.5', '119.29.29.29'],
                           'nameserver-policy': dns_policy, 'direct-nameserver': direct_dns, 'direct-nameserver-follow-policy': True,
                           'proxy-server-nameserver': direct_dns, 'nameserver': ['https://1.1.1.1/dns-query#' + node, 'https://8.8.8.8/dns-query#' + node]},
                   'proxies': [{'name': node, 'type': 'wireguard', 'ip': p['ip'], 'private-key': p['private'], 'mtu': p['mtu'],
                                'udp': True, 'persistent-keepalive': p['keepalive'], 'peers': [wgpeer]}],
                   'proxy-groups': [{'name': 'Overseas', 'type': 'select', 'proxies': [node]}],
                   'rule-providers': {'cn_domain': {'type': 'inline', 'behavior': 'domain', 'payload': domains},
                                      'cn_ip': {'type': 'inline', 'behavior': 'ipcidr', 'payload': networks}},
                   'rules': rules + ['RULE-SET,cn_domain,DIRECT', 'RULE-SET,cn_ip,DIRECT', 'MATCH,Overseas']}
            if platform != 'android':
                cfg['find-process-mode'] = 'strict'
                cfg['tun'] = {'enable': True, 'stack': 'gvisor' if platform == 'macos' else 'mixed', 'auto-route': True,
                              'auto-detect-interface': True, 'strict-route': platform == 'windows',
                              'dns-hijack': ['any:53', 'tcp://any:53'], 'route-exclude-address': [p['server'] + '/32']}
            # JSON is a YAML 1.2 subset accepted by Mihomo, avoiding a generator dependency on PyYAML.
            rendered[FILENAMES[platform]] = json.dumps(cfg, ensure_ascii=False, indent=2) + '\n'
        cp = p['cp']
        cp['Peer']['AllowedIPs'] = '0.0.0.0/0'
        stream = io.StringIO(); cp.write(stream)
        rendered['wireguard-reference-ipv4/' + platform + '.conf'] = '# Parameter reference, not the main routing-client import file.\n' + stream.getvalue()

    for x in hashes:
        require(hashlib.sha256(Path(x['path']).read_bytes()).hexdigest() == x['sha256'], 'input_changed_before_write')
    out.mkdir(parents=True, mode=0o700)
    require(stat.S_IMODE(out.stat().st_mode) == 0o700, 'private_output_directory_permissions_required')
    for name, content in rendered.items():
        p = out / name; p.parent.mkdir(parents=True, mode=0o700, exist_ok=True)
        require(stat.S_IMODE(p.parent.stat().st_mode) == 0o700, 'private_output_directory_permissions_required')
        with p.open('x', encoding='utf-8', newline='\n') as f:
            f.write(content)
        p.chmod(0o600)
        require(stat.S_IMODE(p.stat().st_mode) == 0o600, 'private_output_file_permissions_required')
    receipt = {'schema_version': 1, 'targets': targets, 'inputs': hashes, 'rules_as_of': m['rules_as_of'],
               'domain_count': len(domains), 'ipv4_network_count': len(networks), 'platform_rules': counts,
               'files': [{'file': name, 'sha256': hashlib.sha256((out / name).read_bytes()).hexdigest()} for name in rendered],
               'server_changed': False, 'keys_regenerated': False, 'network_called': False,
               'device_runtime': {p: 'pending_target_device' for p in targets}}
    with (out / 'build-receipt.json').open('x', encoding='utf-8') as f:
        json.dump(receipt, f, ensure_ascii=False, indent=2); f.write('\n')
    (out / 'build-receipt.json').chmod(0o600)
    require(stat.S_IMODE((out / 'build-receipt.json').stat().st_mode) == 0o600, 'private_output_file_permissions_required')
    return {'output_dir': str(out), 'targets': targets, 'file_count': len(rendered), 'domain_count': len(domains), 'ipv4_network_count': len(networks)}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--manifest', required=True, type=Path)
    args = parser.parse_args()
    os.umask(0o077)
    try:
        print(json.dumps(build(args.manifest), ensure_ascii=False))
    except InvalidInput as exc:
        print(json.dumps({'error': str(exc)}), file=sys.stderr); return 2
    except Exception as exc:
        # ConfigParser and decoder error messages can contain original key lines.
        print(json.dumps({'error': 'build_failed', 'error_type': type(exc).__name__}), file=sys.stderr); return 2
    return 0


if __name__ == '__main__':
    sys.exit(main())
