#!/usr/bin/env python3
"""Validate observed results, send authorized notices, and render a short report.

Does not perform browser actions. Input is one JSON object on stdin.
"""
import argparse
from datetime import date
import json
from pathlib import Path
import sys
import subprocess
from service_health import default_config, default_state, observe, send_notice

SERVICE = 'minimax-agent-daily-checkin'
RESULTS = {'newly_completed':'签到成功','already_completed':'今日已签到',
           'not_completed':'今日尚未签到','maintenance':'维护中',
           'runtime_unavailable':'未执行（浏览器连接失败）','failure':'未完成'}
PAGES = {'closed':'已关闭','preserved':'已保留','unconfirmed':'关闭未确认','not_created':'未创建'}


def validate(d):
    if date.fromisoformat(d['service_day']).isoformat()!=d['service_day']: raise ValueError('invalid date')
    if d['outcome'] not in RESULTS or d['page'] not in PAGES: raise ValueError('invalid outcome/page')
    for key in ('remaining_points','points_before','reward'):
        v=d.get(key)
        if v is not None and (type(v) is not int or v<0): raise ValueError('points must be integers or null')
    normal=d['outcome'] in ('newly_completed','already_completed','not_completed')
    if normal and d.get('remaining_points') is None: raise ValueError('normal result needs fresh points')
    if normal and not d.get('evidence'): raise ValueError('normal result needs current page evidence')
    if d['outcome']=='newly_completed':
        if d.get('click_attempted') is not True or d.get('points_before') is None or not d.get('reward'):
            raise ValueError('new check-in needs click and points evidence')
        if d['remaining_points']-d['points_before']!=d['reward']: raise ValueError('points delta mismatch')
    elif d.get('reward') is not None: raise ValueError('only a verified new check-in reports earned reward')
    if d['outcome']=='already_completed' and d.get('click_attempted') is not False:
        raise ValueError('already completed requires no check-in click')
    if normal and d['page']=='not_created': raise ValueError('no page cannot confirm normal result')
    if d['outcome']=='maintenance' and not d.get('evidence'): raise ValueError('maintenance needs current evidence')
    for key in ('reason','evidence'):
        if not isinstance(d.get(key,''),str) or len(d.get(key,''))>120 or '\n' in d.get(key,''):
            raise ValueError('reason/evidence must be short redacted single-line text')



def read_task_spaces():
    """Read existing spaces only. Never create, resume, close or claim a space."""
    script = "console.log('MINIMAX_SPACES='+JSON.stringify((await listTaskSpaces()).map(s=>({id:s.id,name:s.name,createdBy:s.createdBy}))));"
    result = subprocess.run(['ego-browser','nodejs','-e',script],
                            capture_output=True,text=True,timeout=20)
    if result.returncode: raise ValueError('space inspection failed')
    for stream in (result.stdout,result.stderr):
        for line in stream.splitlines():
            if line.startswith('MINIMAX_SPACES='):
                spaces=json.loads(line[len('MINIMAX_SPACES='):])
                if not isinstance(spaces,list) or any(not isinstance(s,dict) or type(s.get('id')) is not int for s in spaces):
                    raise ValueError('invalid space list')
                return spaces
    raise ValueError('missing space inspection')


def verify_cleanup(d, inspect_spaces):
    """A model-written closed flag is not a browser receipt."""
    d=dict(d)
    if d['page']!='closed': return d
    ids=d.get('space_ids')
    if not isinstance(ids,list) or not ids or any(type(i) is not int or i<=0 for i in ids) or len(ids)!=len(set(ids)):
        issue='缺少本轮完整空间 ID，不能确认页面已关闭'
    else:
        try:
            spaces=inspect_spaces()
            # Scope cleanup to this invocation. Old user-handoff spaces are not
            # evidence that this round failed, even when their names match.
            pending=[s['id'] for s in spaces if s['id'] in ids]
            issue=('MiniMax 签到空间仍存在（'+','.join(map(str,pending))+'），本轮清理未确认') if pending else ''
        except (OSError,ValueError,TypeError,KeyError,subprocess.TimeoutExpired):
            issue='无法读取当前空间列表，不能确认页面已关闭'
    if issue:
        d['page']='unconfirmed'
        d['reason']=((d.get('reason','')+'；') if d.get('reason') else '')+issue
        d['reason']=d['reason'][:120]
    return d

def complete(d, mode, sender, health, inspect_spaces=read_task_spaces):
    validate(d)
    if mode=='query-only' and (d.get('click_attempted') or d['outcome']=='newly_completed'):
        raise ValueError('query cannot claim points')
    d=verify_cleanup(d,inspect_spaces)
    outcome=d['outcome']
    normal=outcome in ('newly_completed','already_completed','not_completed')
    phase='available' if normal else ('maintenance' if outcome=='maintenance' else 'unknown')
    page=PAGES[d['page']]
    if d['page'] in ('preserved','unconfirmed') and d.get('space_ids'):
        page+='（空间 '+','.join(map(str,d['space_ids']))+'）'
    result=RESULTS[outcome]
    if d.get('reward') is not None: result+=f"（+{d['reward']} 积分）"
    cleanup_issue=(normal or outcome=='maintenance') and d['page']!='closed'
    if cleanup_issue: result+='，页面清理未完成'
    notice=None
    # Browser housekeeping is the executor's responsibility. Keep any cleanup
    # defect in its local report/receipt; it is not a user-action notification.
    if (not normal and outcome!='maintenance') or (mode=='scheduled' and outcome=='not_completed'):
        notice=('MiniMax 签到异常。',[])
    deliveries=[]
    if mode=='scheduled':
        h=health(phase,page,d.get('evidence',''),result,notice)
        if h.get('transition') or h.get('status') in ('failed','unknown'): deliveries.append(h)
        if notice and (not h.get('transition') or h.get('status')=='failed'):
            deliveries.append(sender('minimax-'+d['service_day'].replace('-','')+'-failure',notice))
    statuses={'sent':'已发送','failed':'发送失败','unknown':'送达未确认'}
    delivery='；'.join(statuses.get(v.get('status'),'送达未确认') for v in deliveries) or '未触发'
    if any(v.get('status')=='sent' and not v.get('message_id') for v in deliveries): delivery='送达未确认'
    lines=[f"MiniMax｜{d['service_day']}",'结果：'+result,
           '剩余积分：'+str(d['remaining_points'] if d.get('remaining_points') is not None else '未确认'),
           '页面：'+page,'飞书：'+delivery]
    if d.get('reason') and (not normal or cleanup_issue): lines.append('原因：'+d['reason'])
    return '\n'.join(lines)


def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mode',choices=['scheduled','manual','query-only'],required=True)
    p.add_argument('--chat-id')
    p.add_argument('--config',type=Path,default=default_config())
    p.add_argument('--state-dir',type=Path,default=default_state(SERVICE))
    a=p.parse_args()
    if a.mode=='scheduled': p.error('scheduled 模式请调用 run_checkin.py；报告和通知由执行器统一生成，不接收手填结果')
    if a.state_dir.resolve().is_relative_to(Path(__file__).resolve().parents[1]): p.error('state must be outside package')
    sender=lambda key,notice:send_notice(a.config,a.chat_id,key,notice)
    health=lambda phase,page,evidence,detail,notice:observe(a.state_dir,SERVICE,phase,sender,
        page=page,evidence=evidence,detail=detail,extra=notice)
    try: print(complete(json.load(sys.stdin),a.mode,sender,health))
    except (ValueError,KeyError,TypeError):
        print('报告输入与证据不一致；请按真实工具结果修正输入，不重跑签到。',file=sys.stderr)
        return 2
    return 0


if __name__=='__main__': raise SystemExit(main())
