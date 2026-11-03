#!/usr/bin/env python3
"""Send via an explicitly configured local bot, isolated from host OAuth injection."""
import argparse
import json
import os
from pathlib import Path
import subprocess

parser = argparse.ArgumentParser(description=__doc__)
parser.add_argument('--config', required=True, type=Path)
parser.add_argument('--chat-id', required=True)
parser.add_argument('--text', required=True,
                    choices=['Ikuuu 签到异常。', 'Ikuuu 流量不足。'])
parser.add_argument('--idempotency-key', required=True)
parser.add_argument('--dry-run', action='store_true')
args = parser.parse_args()
if not args.chat_id.startswith('oc_') or not 1 <= len(args.idempotency_key) <= 50:
    parser.error('valid caller chat ID and 1-50 character idempotency key required')
config = json.loads(args.config.read_text())
cli = Path(config['cli']).expanduser()
if not cli.is_absolute() or not cli.is_file() or not config.get('profile'):
    parser.error('configured local CLI and explicit bot profile required')
# Use the authorized standalone local bot credential store. Never inherit the
# host plugin's user OAuth provider, override its policy, or rewrite global config.
names = ('HOME', 'PATH', 'TMPDIR', 'LANG', 'LC_ALL', 'SSL_CERT_FILE',
         'SSL_CERT_DIR', 'HTTP_PROXY', 'HTTPS_PROXY', 'ALL_PROXY', 'NO_PROXY',
         'http_proxy', 'https_proxy', 'all_proxy', 'no_proxy')
env = {k: os.environ[k] for k in names if k in os.environ}
env.update(LARKSUITE_CLI_NO_UPDATE_NOTIFIER='1', LARKSUITE_CLI_NO_SKILLS_NOTIFIER='1')
base = [str(cli), '--profile', config['profile']]
identity = subprocess.run(base + ['whoami', '--as', 'bot'], env=env,
                          capture_output=True, text=True)
try:
    state = json.loads(identity.stdout)
except ValueError:
    state = {}
if identity.returncode or state.get('identity') != 'bot' or state.get('available') is not True:
    print(json.dumps({'ok': False, 'error': {'type': 'bot_identity_unavailable',
                     'detail': state.get('error', 'local bot identity not confirmed')}}))
    raise SystemExit(1)
command = base + ['im', '+messages-send', '--as', 'bot', '--chat-id', args.chat_id,
                 '--text', args.text, '--idempotency-key', args.idempotency_key,
                 '--format', 'json']
if args.dry_run:
    command.append('--dry-run')
# Exactly one send attempt. Preserve the actual CLI receipt and exit code.
raise SystemExit(subprocess.run(command, env=env).returncode)
