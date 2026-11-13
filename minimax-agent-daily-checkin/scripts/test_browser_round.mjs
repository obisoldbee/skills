import test from 'node:test';
import assert from 'node:assert/strict';
import {runRound,MiniMaxPage,isInformationalPopup} from './browser_round.mjs';

function fixture(options={}) {
  const events=[], checkpoints=[];
  let balance=1000, claimed=false, exists=true, owner='agent', cardReads=0;
  const task={spaceId:71,
    async finish() { events.push('finish'); if(options.finishFails) throw Error('finish failed'); exists=!!options.residue; return {closedSpace:!options.residue}; },
    async handOff() { events.push('handoff'); owner='agentDelegatedToUser'; }};
  const ui={
    async open() {events.push('open'); if(options.takeover) {owner='user';throw Error('user took over');}},
    async inspect() {return {authenticated:!options.loggedOut,maintenance:!!options.maintenance};},
    async login() {events.push('login');},
    async card() {cardReads++; return {completed:!!options.completed || claimed || (options.changed && cardReads>1),reward:400};},
    async points() {events.push('points'); return options.noPoints?null:balance;},
    async claim() {events.push('claim'); if(options.claimFails) throw Error('click result unknown'); claimed=true;balance+=options.wrongDelta?200:400;},
    async wait() {}
  };
  let staleReads=options.staleClose?2:0;
  const api={async create() {events.push('create'); if(options.createFails) throw Error('unavailable');return task;},
    ui:()=>ui,async wait() {},async list() {
      if(!exists && staleReads-->0) return [{id:71,ownership:owner}];
      return exists?[{id:71,ownership:owner}]:[];
    }};
  return {events,checkpoints,async run(mode='scheduled') {
    return runRound(api,{service_day:'2026-09-25',run_id:'fixture',mode},r=>checkpoints.push(structuredClone(r)));
  }};
}

test('one space and fresh points precede the only claim; finish and absence prove cleanup',async()=>{
  const f=fixture(),r=await f.run();
  assert.equal(r.outcome,'newly_completed');assert.equal(r.reward,400);
  assert.deepEqual(r.space_ids,[71]);assert.equal(r.page,'closed');
  assert.deepEqual(f.events,['create','open','points','claim','points','finish']);
  const beforeClick=f.checkpoints.find(r=>r.actions.at(-1).action==='checkin_attempted');
  assert.equal(beforeClick.points_before,1000);assert.equal(beforeClick.click_attempted,true);
  assert.equal(beforeClick.outcome,'failure');assert.equal(beforeClick.reward,null);
  assert.equal(beforeClick.remaining_points,null);
  const afterClick=f.checkpoints.find(r=>r.actions.at(-1).action==='points_after');
  assert.equal(afterClick.remaining_points,1400);
});
test('already completed reads fresh points and closes without claiming',async()=>{
  const f=fixture({completed:true}),r=await f.run();
  assert.equal(r.outcome,'already_completed');assert.equal(r.remaining_points,1000);
  assert.equal(r.click_attempted,false);assert.equal(r.page,'closed');assert(!f.events.includes('claim'));
});
test('missing baseline hands off the original space without clicking or finishing',async()=>{
  const f=fixture({noPoints:true}),r=await f.run();
  assert.equal(r.outcome,'failure');assert.equal(r.page,'preserved');
  assert.deepEqual(f.events,['create','open','points','handoff']);assert.deepEqual(r.space_ids,[71]);
});
test('unknown click result never retries or rewrites it to already-completed',async()=>{
  const f=fixture({claimFails:true}),r=await f.run();
  assert.equal(r.outcome,'failure');assert.equal(r.click_attempted,true);assert.equal(r.reward,null);
  assert.equal(r.points_before,1000);assert.equal(r.remaining_points,null);
  assert.equal(r.page,'preserved');assert.equal(f.events.filter(v=>v==='claim').length,1);
  assert.equal(f.events.filter(v=>v==='create').length,1);assert(!f.events.includes('finish'));
});
test('mismatched delta rereads once, then hands off without another claim',async()=>{
  const f=fixture({wrongDelta:true}),r=await f.run();
  assert.equal(r.outcome,'failure');assert.equal(r.remaining_points,1200);assert.equal(r.reward,null);
  assert.equal(f.events.filter(v=>v==='claim').length,1);assert.equal(f.events.filter(v=>v==='points').length,3);
  assert.equal(r.page,'preserved');
});
test('state changed before click does not claim',async()=>{
  const f=fixture({changed:true}),r=await f.run();
  assert.equal(r.outcome,'already_completed');assert(!f.events.includes('claim'));
});
test('query mode cannot claim, even when reward is available',async()=>{
  const f=fixture(),r=await f.run('query-only');
  assert.equal(r.outcome,'not_completed');assert.equal(r.page,'closed');assert(!f.events.includes('claim'));
});
test('logged-out query hands off without login',async()=>{
  const f=fixture({loggedOut:true}),r=await f.run('query-only');
  assert.equal(r.page,'preserved');assert(!f.events.includes('login'));assert(!f.events.includes('claim'));
});
test('failed automatic login is one attempt then handoff',async()=>{
  const f=fixture({loggedOut:true}),r=await f.run();
  assert.equal(r.page,'preserved');assert.equal(f.events.filter(v=>v==='login').length,1);assert(!f.events.includes('claim'));
});
test('cleanup exception retains verified business result and does not retry finish',async()=>{
  const f=fixture({finishFails:true}),r=await f.run();
  assert.equal(r.outcome,'newly_completed');assert.equal(r.reward,400);assert.equal(r.page,'unconfirmed');
  assert.equal(f.events.filter(v=>v==='finish').length,1);assert(!f.events.includes('handoff'));
});
test('finish without disappearance cannot report closed',async()=>{
  const f=fixture({residue:true}),r=await f.run();assert.equal(r.page,'unconfirmed');
});
test('delayed native list removal is observed without another finish or space',async()=>{
  const f=fixture({staleClose:true}),r=await f.run();
  assert.equal(r.page,'closed');assert.equal(f.events.filter(v=>v==='create').length,1);
  assert.equal(f.events.filter(v=>v==='finish').length,1);
});
test('user takeover is not reclaimed, handed off again or finished',async()=>{
  const f=fixture({takeover:true}),r=await f.run();
  assert.equal(r.page,'preserved');assert.deepEqual(f.events,['create','open']);
});
test('failed creation never creates a replacement space',async()=>{
  const f=fixture({createFails:true}),r=await f.run();
  assert.equal(r.page,'unconfirmed');assert.deepEqual(r.space_ids,[]);assert.deepEqual(f.events,['create']);
});
test('confirmed maintenance closes without a login or claim',async()=>{
  const f=fixture({maintenance:true,loggedOut:true}),r=await f.run();
  assert.equal(r.outcome,'maintenance');assert.equal(r.page,'closed');assert.deepEqual(f.events,['create','open','finish']);
});

test('release/promotion semantics survive new titles without clicking the promotional CTA',()=>{
  for(const title of ['MiniMax Code 产品焕新','本周更新已来','新功能介绍','限时活动','What’s new']) {
    assert(isInformationalPopup({title,text:'M Plan 全新推出，首月5折。立即体验'}));
  }
  assert(isInformationalPopup({text:'新手引导：使用指引'}));
});
test('forms, verification, consent, payments, maintenance and unknown dialogs are not advertisements',()=>{
  for(const text of ['请输入验证码','安全验证','请同意用户协议','隐私政策','确认支付','确认删除','服务维护中']) {
    assert(!isInformationalPopup({title:'新功能介绍',text}));
  }
  assert(!isInformationalPopup({title:'优惠活动',hasForm:true}));
  assert(!isInformationalPopup({title:'操作失败',text:'请稍后重试'}));
});
function popupFixture(options={}) {
  const events=[];
  let remaining=options.count ?? 1;
  const popup={title:'MiniMax Code 产品焕新',text:'立即体验',selector:'div:nth-of-type(2)',
    closeSelectors:options.closes ?? ['div:nth-of-type(2) > button:nth-of-type(1)']};
  const page={
    async evaluate() {return remaining ? [popup] : [];},
    async click(selector) {events.push(['click',selector]);remaining--;},
    async waitForFunction(fn,previous,options_) {
      events.push(['wait','dialog_gone']);
      assert.equal(options_.timeout,3000);
      // A visible unrelated node reusing the old DOM position is not the modal.
      globalThis.document={querySelectorAll:()=>options.stuck?[{
        getBoundingClientRect:()=>({width:800,height:400}),getAttribute:()=>previous.title,innerText:previous.text
      }]:[],getElementById:()=>null};
      globalThis.getComputedStyle=()=>({visibility:'visible'});
      try {if(!fn(previous)) throw Error('timeout');}
      finally {delete globalThis.document;delete globalThis.getComputedStyle;}
    },
    async snapshot() {events.push(['snapshot']);}
  };
  const ui=new MiniMaxPage(page);
  ui.onDismiss=()=>events.push(['dismissed']);
  return {ui,events,popup};
}
test('dismisses only the observed close button then verifies and reobserves',async()=>{
  const f=popupFixture();await f.ui.dismissInformationalPopups();
  assert.deepEqual(f.events,[['click','loc=css:'+f.popup.closeSelectors[0]],['wait','dialog_gone'],['dismissed'],['snapshot']]);
  await f.ui.dismissInformationalPopups();assert.equal(f.ui.dismissals,1);
});
test('missing/ambiguous close controls stop without clicking arbitrary buttons',async()=>{
  for(const closes of [[],['button.a','button.b']]) {
    const f=popupFixture({closes});
    await assert.rejects(f.ui.dismissInformationalPopups(),/入口不明确/);
    assert.deepEqual(f.events,[]);
  }
});
test('unclosed or repeated overlays are bounded, never blindly clicked again',async()=>{
  const stuck=popupFixture({stuck:true});
  await assert.rejects(stuck.ui.dismissInformationalPopups(),/仍遮挡/);
  assert.equal(stuck.events.filter(e=>e[0]==='click').length,1);
  const repeating=popupFixture({count:4});
  await assert.rejects(repeating.ui.dismissInformationalPopups(),/反复遮挡/);
  assert.equal(repeating.ui.dismissals,3);
});
test('popup close failure hands off and never claims or reports success',async()=>{
  const f=popupFixture({stuck:true});
  let handed=false;
  const r=await runRound({
    async create(){return {spaceId:71,async handOff(){handed=true;}};},
    ui(){return {async open(){},async inspect(){await f.ui.dismissInformationalPopups();},async claim(){assert.fail('claim forbidden');}};},
    async list(){return [{id:71,ownership:handed?'agentDelegatedToUser':'agent'}];}
  },{service_day:'2026-10-01',run_id:'test',mode:'scheduled'});
  assert.equal(r.outcome,'failure');assert.equal(r.click_attempted,false);assert.equal(r.page,'preserved');
});

function readinessFixture(states) {
  let index=0;
  const events=[];
  const visibleNode={getBoundingClientRect:()=>({width:100,height:20}),innerText:''};
  const page={
    async evaluate(fn) {
      const state=states[index];
      globalThis.document={querySelectorAll:selector=>{
        if(selector==='.mavis-dropdown.flex-1.cursor-pointer') return state.account?[visibleNode]:[];
        if(selector==='button[aria-label="今日已签到"],button[aria-label^="签到得"]') return state.card?[visibleNode]:[];
        if(selector==='button') return state.login?[{...visibleNode,innerText:'登录'}]:[];
        return [];
      }};
      globalThis.getComputedStyle=()=>({visibility:'visible',display:'block'});
      try { return fn(); }
      finally {delete globalThis.document;delete globalThis.getComputedStyle;}
    },
    async waitForTimeout() {events.push('wait');index=Math.min(index+1,states.length-1);},
    async snapshot() {},
    async click() {events.push('click');throw Error('unexpected click');},
    mouse:{async click(){events.push('click');throw Error('unexpected login');}}
  };
  return {ui:new MiniMaxPage(page),events};
}
test('loading without account or login controls waits for the authenticated page',async()=>{
  const f=readinessFixture([{}, {}, {account:true}]);
  assert.deepEqual(await f.ui.inspect(),{authenticated:true,maintenance:false});
  assert(f.events.includes('wait'));
  assert(!f.events.includes('click'));
});
test('loading resolves to logged out only after the login entry appears',async()=>{
  const f=readinessFixture([{}, {login:true}]);
  assert.deepEqual(await f.ui.inspect(),{authenticated:false,maintenance:false});
  assert(f.events.includes('wait'));
  assert(!f.events.includes('click'));
});
test('unresolved page readiness is bounded and never submits login',async()=>{
  const f=readinessFixture([{}]);
  await assert.rejects(f.ui.inspect(),/页面尚未就绪/);
  assert(f.events.length>0 && f.events.length<=30);
  assert(!f.events.includes('click'));
});
test('authentication appearing before login is rechecked without opening a login form',async()=>{
  const f=readinessFixture([{account:true}]);
  await f.ui.login();
  assert(!f.events.includes('click'));
});

function closingMenuFixture({stuck=false}={}) {
  let menu='open', cardVisible=false;
  const events=[];
  const withDocument=fn=>{
    globalThis.document={querySelectorAll:selector=>selector==='[role="menuitem"]' && menu!=='closed'
      ? [{innerText:'用量',getBoundingClientRect:()=>({width:234,height:25})}] : []};
    try {return fn();} finally {delete globalThis.document;}
  };
  const page={
    async evaluate(fn) {return withDocument(fn);},
    keyboard:{async press(key) {assert.equal(key,'Escape');events.push('escape');menu='closing';}},
    async waitForFunction(fn,arg,options) {
      assert.equal(options.timeout,5000);events.push('wait for menu to close');
      assert.equal(withDocument(fn),false); // closing menu still has a bounding box
      if(stuck) throw Error('menu did not close');
      menu='closed';assert.equal(withDocument(fn),true);
    },
    async click(selector) {
      if(selector==='loc=css:.mavis-dropdown.flex-1.cursor-pointer') {
        assert.equal(menu,'closed');events.push('open menu');menu='open';
      } else {
        assert.equal(selector,'loc=role:menuitem[name="每日签到"]');
        assert.equal(menu,'open');events.push('open card');cardVisible=true;
      }
    },
    async waitForSelector(selector) {events.push('wait '+selector);}
  };
  const ui=new MiniMaxPage(page);
  ui.dismissInformationalPopups=async()=>{};
  ui.readCard=async()=>({completed:false,reward:cardVisible?400:null,label:cardVisible?'签到得 400':null});
  return {ui,events};
}

test('waits for the old menu to finish closing before reopening the check-in card',async()=>{
  const f=closingMenuFixture();
  assert.equal((await f.ui.card()).reward,400);
  assert.deepEqual(f.events.slice(0,4),['escape','wait for menu to close','open menu','wait loc=role:menuitem[name="用量"]']);
  assert(f.events.indexOf('wait loc=role:menuitem[name="每日签到"]')<f.events.indexOf('open card'));
});

test('a menu that cannot close stops before opening or claiming anything',async()=>{
  const f=closingMenuFixture({stuck:true});
  await assert.rejects(f.ui.card(),/menu did not close/);
  assert.deepEqual(f.events,['escape','wait for menu to close']);
});
