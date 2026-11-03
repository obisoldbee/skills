#!/usr/bin/env python3
"""One complete MiniMax check-in invocation; no model-authored result JSON."""
import argparse
from datetime import datetime
import fcntl
import json
import os
from pathlib import Path
import secrets
import shutil
import subprocess
import sys
from zoneinfo import ZoneInfo
from finish_round import complete, SERVICE
from service_health import default_config, default_state, observe, save, send_notice

SCRIPTS=Path(__file__).resolve().parent

def browser_script(data, checkpoint):
    return f'''
const {{runRound,MiniMaxPage}}=await import({json.dumps((SCRIPTS/'browser_round.mjs').as_uri())});
const fs=await import('node:fs');
const input={json.dumps(data)};
const path={json.dumps(str(checkpoint))};
function checkpoint(value) {{
  fs.writeFileSync(path+'.tmp',JSON.stringify(value),{{mode:0o600}});
  fs.renameSync(path+'.tmp',path);
}}
const api={{
  create:async runId=>{{
    if(input.resume_space_id) {{
      const s=(await listTaskSpaces()).find(s=>s.id===input.resume_space_id);
      if(!s || s.ownership!=='agent') throw new Error('指定测试空间已不可用，未接管或创建其他空间');
      return taskSpace(input.resume_space_id);
    }}
    const task=await taskSpace('MiniMax daily checkin '+runId);
    console.log('MINIMAX_SPACE_ID='+task.spaceId);
    return task;
  }},
  ui:task=>new MiniMaxPage(task.page('p1')),
  list:()=>listTaskSpaces()
}};
const result=await runRound(api,input,checkpoint);
checkpoint(result);
console.log('MINIMAX_ROUND_DONE');
'''

def interrupted_report(receipt, day):
    d=receipt.get('browser',{})
    ids=d.get('space_ids',[])
    attempted=d.get('click_attempted')
    deliveries=[]
    for n in receipt.get('notifications',[]):
        deliveries.append('已发送' if n.get('status')=='sent' and n.get('message_id') else
                          '发送失败' if n.get('status')=='failed' else '送达未确认')
    notification='；'.join(deliveries) or ('此前发送状态待核查' if receipt.get('phase')=='reporting' else '未触发')
    return '\n'.join([f'MiniMax｜{day}',
        '结果：已尝试签到，结果待核查' if attempted else '结果：上一轮中断，需核查原空间',
        '页面：'+('空间 '+','.join(map(str,ids))+'，状态待核查' if ids else '创建状态未确认'),
        '飞书：'+notification,
        '原因：本日已有执行记录，未重新建空间或领取'])

def run_once(args, directory, day, browser=None, render=complete):
    directory.mkdir(parents=True,exist_ok=True)
    receipt_path=directory/'receipt.json'
    checkpoint=directory/'browser.json'
    with (directory/'run.lock').open('a') as lock:
        try: fcntl.flock(lock,fcntl.LOCK_EX|fcntl.LOCK_NB)
        except BlockingIOError:
            return 'MiniMax｜'+day+'\n结果：本轮正在运行，请等待原命令结束',1
        if receipt_path.exists():
            receipt=json.loads(receipt_path.read_text())
            if receipt.get('report_text'): return receipt['report_text'],receipt['exit_code']
            if checkpoint.exists(): receipt['browser']=json.loads(checkpoint.read_text())
            return interrupted_report(receipt,day),1
        receipt={'service_day':day,'run_id':directory.name,'phase':'browser_running','notifications':[]}
        save(receipt_path,receipt)
        data={'service_day':day,'run_id':directory.name,'mode':args.mode,
              'resume_space_id':getattr(args,'resume_space_id',None)}
        if browser:
            result=browser(data,checkpoint)
        else:
            cli=shutil.which('ego-browser')
            if not cli and (Path.home()/'.local/bin/ego-browser').is_file(): cli=str(Path.home()/'.local/bin/ego-browser')
            result=None
            if cli:
                try:
                    process=subprocess.run([cli,'nodejs'],input=browser_script(data,checkpoint),
                        capture_output=True,text=True,timeout=180)
                    if process.returncode==0 and 'MINIMAX_ROUND_DONE' in process.stdout+process.stderr:
                        result=json.loads(checkpoint.read_text())
                except (OSError,ValueError,subprocess.TimeoutExpired): pass
            if result is None:
                result=json.loads(checkpoint.read_text()) if checkpoint.exists() else {
                    'service_day':day,'outcome':'runtime_unavailable','remaining_points':None,
                    'click_attempted':False,'points_before':None,'reward':None,'space_ids':[],
                    'evidence':'','page':'not_created' if not cli else 'unconfirmed'}
                # A killed command has no trustworthy final disposition. Do not launch a replacement.
                if result.get('page')!='closed':
                    result.update(page='unconfirmed' if result.get('space_ids') or cli else 'not_created',
                                  outcome='failure' if result.get('space_ids') else 'runtime_unavailable',
                                  reward=None,reason='浏览器命令未完整结束；未重开空间或重复签到')
        receipt.update(phase='reporting',browser=result)
        save(receipt_path,receipt)
        def sender(key,notice):
            entry={'status':'unknown','key':key}
            receipt['notifications'].append(entry); save(receipt_path,receipt)
            response=send_notice(args.config,args.chat_id,key,notice)
            entry.update(response); save(receipt_path,receipt)
            return response
        def health(phase,page,evidence,detail,notice):
            value=observe(args.state_dir,SERVICE,phase,sender,page=page,evidence=evidence,detail=detail,extra=notice)
            receipt['health']=value; save(receipt_path,receipt)
            return value
        # The same browser invocation recorded finish and disappearance; no bootstrap/probe rerun.
        verified=result.get('page')=='closed' and any(a.get('action')=='space_verified' and a.get('absent') is True for a in result.get('actions',[]))
        if result.get('page')=='closed' and not verified: result['page']='unconfirmed'
        text=render(result,args.mode,sender,health,lambda:[])
        code=0 if result['outcome'] in ('already_completed','newly_completed','not_completed','maintenance') and result['page']=='closed' else 1
        if any(n.get('status') in ('failed','unknown') for n in receipt['notifications']) or receipt.get('health',{}).get('status') in ('failed','unknown'): code=1
        receipt.update(phase='finished',report_text=text,exit_code=code)
        save(receipt_path,receipt)
        return text,code

def main():
    p=argparse.ArgumentParser(description=__doc__)
    p.add_argument('--mode',choices=['scheduled','manual','query-only'],required=True)
    p.add_argument('--chat-id')
    p.add_argument('--config',type=Path,default=default_config())
    p.add_argument('--state-dir',type=Path,default=default_state(SERVICE))
    p.add_argument('--resume-space-id',type=int,help='Explicit repair only: resume a verified agent-owned test space')
    args=p.parse_args()
    if args.mode=='scheduled' and (not args.chat_id or not args.chat_id.startswith('oc_')): p.error('scheduled requires caller chat-id')
    if args.mode=='scheduled' and args.resume_space_id: p.error('scheduled does not resume arbitrary spaces')
    if args.state_dir.resolve().is_relative_to(SCRIPTS.parent): p.error('state must be outside package')
    os.umask(0o077)
    day=datetime.now(ZoneInfo('Asia/Shanghai')).date().isoformat()
    key=day+'-scheduled' if args.mode=='scheduled' else day+'-'+args.mode+'-'+secrets.token_hex(4)
    text,code=run_once(args,args.state_dir/'runs'/key,day)
    print(text)
    return code

if __name__=='__main__': raise SystemExit(main())
