#!/usr/bin/env python3
"""Portable maintenance transitions. State lives outside the Skill; no browser I/O."""
import argparse
from contextlib import contextmanager
from datetime import datetime
import json
import os
from pathlib import Path
import secrets
import sqlite3
import subprocess
from zoneinfo import ZoneInfo

NAMES = {'volcengine-invites-monitor':'方舟众测', 'ikuuu-daily-checkin':'Ikuuu',
         'minimax-agent-daily-checkin':'MiniMax', 'buddy-travelling':'WorkBuddy'}

def now():
    return datetime.now(ZoneInfo('Asia/Shanghai')).strftime('%Y-%m-%d %H:%M:%S')

def default_state(service):
    return Path(os.environ.get('XDG_STATE_HOME', Path.home()/'.local/state'))/'skill-automations'/service

def default_config():
    return Path(os.environ.get('XDG_CONFIG_HOME', Path.home()/'.config'))/'skill-automations/lark-bot.json'

def post_payload(notice):
    title, rows = notice
    return {'zh_cn': {'title': title, 'content': [[
        {'tag':'text','text':str(k)+'：','style':['bold']},
        {'tag':'text','text':str(v)}] for k,v in rows]}}

def send_notice(config_path, chat_id, key, notice):
    """Use an explicitly configured bot profile, not a host-injected user identity."""
    try:
        config = json.loads(Path(config_path).read_text())
        cli = Path(config['cli']).expanduser()
        if not cli.is_absolute() or not cli.is_file() or not config.get('profile'):
            raise ValueError('configuration')
        if not isinstance(chat_id,str) or not chat_id.startswith('oc_') or not 1 <= len(key) <= 50:
            raise ValueError('parameters')
        names = ('HOME','PATH','TMPDIR','LANG','LC_ALL','SSL_CERT_FILE','SSL_CERT_DIR',
                 'HTTP_PROXY','HTTPS_PROXY','ALL_PROXY','NO_PROXY',
                 'http_proxy','https_proxy','all_proxy','no_proxy')
        env = {k:os.environ[k] for k in names if k in os.environ}
        env.update(LARKSUITE_CLI_NO_UPDATE_NOTIFIER='1',LARKSUITE_CLI_NO_SKILLS_NOTIFIER='1')
        base = [str(cli),'--profile',config['profile']]
        check = subprocess.run(base+['whoami','--as','bot'],env=env,capture_output=True,text=True,timeout=30)
        identity = json.loads(check.stdout or '{}')
        if check.returncode or identity.get('identity') != 'bot' or identity.get('available') is not True:
            return {'status':'failed','error':'bot_identity_unavailable'}
    except (OSError,ValueError,KeyError,subprocess.TimeoutExpired):
        return {'status':'failed','error':'bot_configuration_or_identity'}
    try:
        done = subprocess.run(base+['im','+messages-send','--as','bot','--chat-id',chat_id,
            '--msg-type','post','--content',json.dumps(post_payload(notice),ensure_ascii=False),
            '--idempotency-key',key,'--format','json'],env=env,capture_output=True,text=True,timeout=45)
        data = json.loads(done.stdout or '{}')
        mid = data.get('data',{}).get('message_id')
        if done.returncode == 0 and data.get('ok') is True and mid:
            return {'status':'sent','message_id':mid}
        # A rejected request did not send. An ambiguous response must not be retried blindly.
        if data.get('ok') is False:
            return {'status':'failed','error':'delivery_rejected'}
        return {'status':'unknown','error':'delivery_not_confirmed'}
    except OSError:
        return {'status':'failed','error':'sender_not_started'}
    except (ValueError,subprocess.TimeoutExpired):
        return {'status':'unknown','error':'delivery_not_confirmed'}

def save(path, state):
    temp = path.with_name('.state-'+secrets.token_hex(8)+'.tmp')
    try:
        with temp.open('x') as file:
            json.dump(state,file,ensure_ascii=False,indent=2)
            file.write('\n'); file.flush(); os.fsync(file.fileno())
        temp.replace(path)
    finally:
        temp.unlink(missing_ok=True)

@contextmanager
def locked(directory):
    directory.mkdir(parents=True,exist_ok=True)
    # SQLite supplies a process-death-safe OS lock on macOS, Linux and Windows.
    # State itself is saved separately before sending, so a crashed send stays ambiguous.
    connection = sqlite3.connect(directory/'state-lock.sqlite3',timeout=1)
    try:
        connection.execute('BEGIN IMMEDIATE')
        yield directory/'state.json'
    finally:
        connection.rollback()
        connection.close()

def transition_notice(service, event, page, detail, extra=None):
    entered = event['kind'] == 'entered'
    title = NAMES[service] + ('｜维护中' if entered else '｜维护结束')
    rows = [('时间',event['time']+'（北京）'),
            ('状态','已确认服务维护，本轮暂停业务' if entered else '已确认服务恢复'),
            ('页面',page)]
    if detail: rows.append(('本轮',' '.join(detail.split())[:160]))
    rows.append(('后续','持续维护不重复提醒；恢复时通知' if entered else '已恢复原任务流程'))
    if extra:
        rows.append(('任务结果',extra[0]))
        rows.extend((k,v) for k,v in extra[1] if k not in ('时间','页面','后续'))
    return title, rows

def observe(directory, service, phase, sender, *, page, evidence='', detail='', extra=None):
    """Serialize observation and delivery; suppress unchanged states across processes/days."""
    if service not in NAMES or phase not in ('maintenance','available','unknown'):
        raise ValueError('invalid health observation')
    if phase != 'unknown' and not evidence.strip():
        raise ValueError('confirmed health requires current page evidence')
    try:
        with locked(Path(directory)) as path:
            state = json.loads(path.read_text()) if path.exists() else {
                'version':1,'service':service,'phase':'unknown','pending':None}
            if state.get('version') != 1 or state.get('service') != service or state.get('phase') not in ('unknown','available','maintenance'):
                raise ValueError('invalid persisted state')
            # Unknown/login/network errors neither end maintenance nor consume a pending event.
            if phase == 'unknown':
                return {'status':'not_triggered','transition':None,'phase':state['phase']}
            old = state['phase']
            kind = 'entered' if phase == 'maintenance' and old != 'maintenance' else (
                'recovered' if phase == 'available' and old == 'maintenance' else None)
            if kind:
                # A new observed transition supersedes an obsolete undelivered notification.
                state['pending'] = {'kind':kind,'key':'health-'+secrets.token_hex(16),
                    'time':now(),'delivery':'pending'}
            state.update(phase=phase,last_observed_at=now())
            save(path,state)
            event = state.get('pending')
            if not event:
                return {'status':'not_triggered','transition':None,'phase':phase}
            if event['delivery'] in ('attempting','unknown'):
                return {'status':'unknown','transition':event['kind'],'phase':phase,
                        'error':'prior_delivery_unconfirmed'}
            event['delivery'] = 'attempting'
            save(path,state)  # Interrupted/ambiguous delivery cannot become a second blind send.
            result = sender(event['key'],transition_notice(service,event,page,detail,extra))
            if result.get('status') == 'sent' and not result.get('message_id'):
                result = {'status':'unknown','error':'missing_message_receipt'}
            if result.get('status') == 'sent' and result.get('message_id'):
                state['last_notice'] = {**event,**result,'delivery':'sent'}
                state['pending'] = None
            else:
                event['delivery'] = 'pending' if result.get('status') == 'failed' else 'unknown'
            save(path,state)
            return {**result,'transition':event['kind'],'phase':phase}
    except (OSError,ValueError,KeyError,TypeError,sqlite3.Error):
        # Corrupt/busy state is never treated as a fresh incident; do not spam or reset it.
        return {'status':'failed','transition':None,'error':'health_state_unavailable'}

def main():
    service = Path(__file__).resolve().parents[1].name
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--phase',choices=['maintenance','available','unknown'],required=True)
    parser.add_argument('--page',choices=['closed','preserved','unconfirmed','not_created'],required=True)
    parser.add_argument('--space-id',type=int,help='Actual numeric space ID; required when a space was created')
    parser.add_argument('--evidence',default='',help='Short redacted current visible evidence')
    parser.add_argument('--detail',default='',help='Short actual business result, not model advice')
    parser.add_argument('--chat-id',required=True)
    parser.add_argument('--state-dir',type=Path,default=default_state(service))
    parser.add_argument('--config',type=Path,default=default_config())
    args = parser.parse_args()
    package = Path(__file__).resolve().parents[1]
    if args.state_dir.resolve().is_relative_to(package):
        parser.error('health state must be outside the portable package')
    if args.page != 'not_created' and args.space_id is None:
        parser.error('actual space ID required')
    page = {'closed':'已关闭','preserved':'已保留','unconfirmed':'关闭未确认','not_created':'未创建'}[args.page]
    if args.space_id is not None: page += f'（空间 {args.space_id}）'
    result = observe(args.state_dir,service,args.phase,
        lambda key,notice:send_notice(args.config,args.chat_id,key,notice),
        page=page,evidence=args.evidence,detail=args.detail)
    print(json.dumps(result,ensure_ascii=False))
    return 1 if result['status'] in ('failed','unknown') else 0

if __name__ == '__main__':
    raise SystemExit(main())
