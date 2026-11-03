// One invocation owns one space, the observations, and its terminal disposition.
export async function runRound(api, input, checkpoint = () => {}) {
  const r = {service_day:input.service_day, outcome:'failure', remaining_points:null,
    points_before:null, reward:null, click_attempted:false, page:'not_created',
    space_ids:[], evidence:'', actions:[]};
  let task, ui, finishAttempted=false;
  const record = (action, facts={}) => { r.actions.push({action,at:new Date().toISOString(),...facts}); checkpoint(r); };
  const fail = reason => { throw new Error(reason); };
  try {
    r.page='unconfirmed'; record('create_attempted');
    task=await api.create(input.run_id);
    r.space_ids=[task.spaceId]; record('created',{space_id:task.spaceId});
    ui=api.ui(task);
    ui.onDismiss=()=>record('informational_popup_dismissed');
    await ui.open();
    let state=await ui.inspect(); record('opened',state);
    if (state.maintenance) {
      await ui.wait(2000);
      if (!(await ui.inspect()).maintenance) fail('维护状态不稳定，未执行签到');
      r.outcome='maintenance'; r.evidence='当前服务维护公告阻断签到，两次观察一致';
    } else {
      if (!state.authenticated) {
        if (input.mode==='query-only') fail('当前未登录，查询模式不提交登录');
        record('login_started');
        await ui.login();
        state=await ui.inspect(); record('login_observed',state);
        if (!state.authenticated) fail('自动登录未成功，需要在保留页面完成登录或验证');
      }
      let card=await ui.card(); record('card_before',card);
      const before=await ui.points();
      if (!Number.isSafeInteger(before) || before<0) fail('未读到本轮积分基线，未提交签到');
      r.remaining_points=before; record('points_before',{points:before});
      card=await ui.card(); record('card_after_points',card);
      if (card.completed) {
        r.outcome='already_completed'; r.evidence='当前签到按钮显示今日已签到';
      } else if (input.mode==='query-only') {
        if (!card.reward) fail('未确认当前签到状态');
        r.outcome='not_completed'; r.evidence='当前签到按钮显示可签到';
      } else {
        // Reopen the card after leaving it to read points. Never use yesterday's balance.
        card=await ui.card(); record('card_preclick',card);
        if (card.completed) {
          r.outcome='already_completed'; r.evidence='点击前观察到今日已签到，未重复提交';
        } else {
          if (!Number.isSafeInteger(card.reward) || card.reward<=0) fail('未读到唯一可领取奖励');
          r.points_before=before; r.click_attempted=true;
          record('checkin_attempted',{reward:card.reward}); // Persist before sending the click.
          await ui.claim(card.reward);
          await ui.wait(3000);
          const afterCard=await ui.card(); record('card_after',afterCard);
          let after=await ui.points(); record('points_after',{points:after});
          if (!afterCard.completed) fail('已提交签到，但完成状态未确认；不能重复领取');
          if (after-before!==card.reward) {
            await ui.wait(5000); after=await ui.points(); record('points_recheck',{points:after});
          }
          r.remaining_points=Number.isSafeInteger(after)?after:null;
          if (after-before!==card.reward) fail('已提交签到，但积分增量未核验；不能重复领取');
          r.outcome='newly_completed'; r.reward=card.reward;
          r.evidence='本轮点击后显示今日已签到，且积分增量与奖励一致';
        }
      }
    }
    record('business_complete');
    finishAttempted=true; record('finish_attempted');
    const receipt=await task.finish({keep:[]});
    record('finish_receipt',{closedSpace:receipt.closedSpace===true});
    let spaces=await api.list();
    // finish() acknowledges the close before the native space index settles.
    // Poll only the original id; never call finish again or create a replacement.
    for(let poll=0;receipt.closedSpace===true && spaces.some(s=>s.id===task.spaceId) && poll<10;poll++) {
      await (api.wait || (ms=>new Promise(resolve=>setTimeout(resolve,ms))))(300);
      spaces=await api.list();
    }
    const absent=!spaces.some(s=>s.id===task.spaceId);
    r.page=receipt.closedSpace===true && absent?'closed':'unconfirmed';
    record('space_verified',{absent});
    if (r.page!=='closed') r.reason='本轮空间关闭未确认';
  } catch (error) {
    // Do not copy page/account text or engine errors to the receipt.
    r.reason=/^[\u4e00-\u9fff]/.test(error.message||'')?error.message.slice(0,120):
      (finishAttempted?'本轮空间收尾失败，业务结果保留':'浏览器操作失败，本轮未完成；请查看保留空间');
    if (!finishAttempted && task) {
      const spaces=await api.list().catch(()=>null);
      const current=spaces?.find(s=>s.id===task.spaceId);
      // A user takeover is terminal. Never reclaim or close it.
      if (current?.ownership==='agent') {
        try {
          await task.handOff();
          const handed=(await api.list()).find(s=>s.id===task.spaceId);
          r.page=handed && handed.ownership!=='agent'?'preserved':'unconfirmed';
        } catch { r.page='unconfirmed'; }
      } else r.page=current?'preserved':'unconfirmed';
      record('handed_off',{page:r.page});
    }
  }
  checkpoint(r);
  return r;
}

// Classify visible dialog semantics, not one release title or screen coordinates.
// Page text remains in memory only; the receipt records the dismissal, not its contents.
export function isInformationalPopup(dialog) {
  const {title='',text='',hasForm=false}=dialog;
  if (hasForm || /验证码|安全验证|身份验证|验证身份|滑动验证|人机验证|登录|登入|同意|隐私|用户协议|服务条款|确认支付|确认购买|确认删除|系统维护|服务维护|平台维护|captcha|sign.?in|log.?in|consent|privacy|terms|checkout|confirm.*(?:payment|delete)|maintenance/i.test(title+'\n'+text)) return false;
  return /产品焕新|版本更新|更新已来|更新公告|新功能|新特性|功能介绍|产品介绍|活动公告|限时活动|优惠活动|福利|新手引导|使用指引|what.s new|release notes|product update|promotion|onboarding/i.test(title+'\n'+text);
}

export class MiniMaxPage {
  constructor(page) { this.page=page; this.dismissals=0; this.onDismiss=()=>{}; }
  wait(ms) { return this.page.waitForTimeout(ms); }
  async dismissInformationalPopups() {
    for (;;) {
      const dialogs=await this.page.evaluate(()=>{
        const visible=e=>!!(e && e.getBoundingClientRect().width && e.getBoundingClientRect().height && getComputedStyle(e).visibility!=='hidden' && getComputedStyle(e).display!=='none');
        const path=e=>{
          const parts=[];
          for(let n=e;n && n.nodeType===1;n=n.parentElement) {
            const siblings=n.parentElement?[...n.parentElement.children].filter(s=>s.tagName===n.tagName):[n];
            parts.unshift(n.tagName.toLowerCase()+':nth-of-type('+(siblings.indexOf(n)+1)+')');
          }
          return parts.join(' > ');
        };
        // Keep outer dialog only if a framework also marks its nested content.
        const roots=[...document.querySelectorAll('[role="dialog"],[aria-modal="true"],.ant-modal-content')].filter(visible);
        return roots.filter(e=>!roots.some(other=>other!==e && other.contains(e))).map(e=>{
          const title=e.getAttribute('aria-label') || document.getElementById(e.getAttribute('aria-labelledby'))?.innerText || e.querySelector('h1,h2,h3,[role="heading"]')?.innerText || '';
          const closes=[...e.querySelectorAll('button,[role="button"]')].filter(b=>visible(b) && !b.disabled && b.getAttribute('aria-disabled')!=='true')
            .filter(b=>/^(关闭|关闭弹窗|关闭公告|暂不|稍后|稍后再说|以后再说|跳过|close|dismiss|not now|maybe later|skip)$/i.test((b.getAttribute('aria-label') || b.getAttribute('title') || b.innerText || '').trim()))
            .filter(b=>{const r=b.getBoundingClientRect(),hit=document.elementFromPoint(r.x+r.width/2,r.y+r.height/2);return hit && (hit===b || b.contains(hit));});
          return {title,text:e.innerText,hasForm:[...e.querySelectorAll('input,select,textarea,[role="checkbox"],[role="textbox"],iframe')].some(visible),
            selector:path(e),closeSelectors:closes.map(path)};
        });
      });
      const candidates=dialogs.filter(isInformationalPopup);
      if (!candidates.length) return;
      if (this.dismissals>=3) throw new Error('公告反复遮挡，已停止自动关闭并保留原空间');
      const actionable=candidates.filter(d=>d.closeSelectors.length===1);
      if(actionable.length!==1) throw new Error('公告关闭入口不明确，已保留原空间');
      const dialog=actionable[0];
      await this.page.click('loc=css:'+dialog.closeSelectors[0]);
      this.dismissals++;
      try { await this.page.waitForFunction(previous=>{
        // DOM positions can be reused by the page after closing an overlay.
        // Verify the observed dialog's identity, not its former nth-of-type path.
        return ![...document.querySelectorAll('[role="dialog"],[aria-modal="true"],.ant-modal-content')].some(e=>{
          if(!e.getBoundingClientRect().width || !e.getBoundingClientRect().height || getComputedStyle(e).visibility==='hidden') return false;
          const title=e.getAttribute('aria-label') || document.getElementById(e.getAttribute('aria-labelledby'))?.innerText || e.querySelector('h1,h2,h3,[role="heading"]')?.innerText || '';
          return title===previous.title && e.innerText===previous.text;
        });
      },{title:dialog.title,text:dialog.text},{timeout:3000}); }
      catch { throw new Error('公告关闭后仍遮挡页面，已保留原空间'); }
      this.onDismiss();
      await this.page.snapshot();
    }
  }
  async open() {
    try { await this.page.goto('https://agent.minimaxi.com/',{waitUntil:'domcontentloaded',timeout:30000}); }
    catch(e) { if (!/navigation.*(timeout|timed out|abort)/i.test(e.message)) throw e; }
    await this.wait(10000);
    await this.page.snapshot(); // Ground selectors in the current page; never persist the account snapshot.
  }
  async inspect() {
    // A hydrated shell can precede both account and login controls. Their
    // absence is a loading state, not evidence that the user is logged out.
    for(let attempt=0;attempt<30;attempt++) {
      await this.dismissInformationalPopups();
      const state=await this.page.evaluate(()=>{
        const visible=e=>!!(e && e.getBoundingClientRect().width && e.getBoundingClientRect().height && getComputedStyle(e).visibility!=='hidden');
        const account=[...document.querySelectorAll('.mavis-dropdown.flex-1.cursor-pointer')].some(visible);
        const card=[...document.querySelectorAll('button[aria-label="今日已签到"],button[aria-label^="签到得"]')].some(visible);
        const login=[...document.querySelectorAll('button')].some(e=>visible(e) && e.innerText.trim()==='登录');
        // Restrict maintenance to an actual blocking dialog, not task/chat text.
        const blocking=[...document.querySelectorAll('[role="dialog"],.ant-modal-content')].filter(visible);
        const maintenance=blocking.some(e=>/^(系统维护中|服务维护中|平台维护中|系统正在维护|服务正在维护)[。！\s]*$/.test(e.innerText.trim()));
        return {authenticated:account||card,maintenance,login};
      });
      if(state.authenticated || state.maintenance || state.login)
        return {authenticated:state.authenticated,maintenance:state.maintenance};
      if(attempt<29) await this.wait(1000);
    }
    throw new Error('页面尚未就绪，账号和登录入口均未出现；未提交登录或签到');
  }
  async menu() {
    await this.dismissInformationalPopups();
    const has=await this.page.evaluate(()=>[...document.querySelectorAll('[role="menuitem"]')]
      .some(e=>e.getBoundingClientRect().width>0 && e.innerText.trim()==='用量'));
    if (!has) {
      await this.page.click('loc=css:.mavis-dropdown.flex-1.cursor-pointer');
      await this.page.waitForSelector('loc=role:menuitem[name="用量"]',{state:'visible',timeout:5000});
    }
  }
  async card() {
    await this.dismissInformationalPopups();
    const menuOpen=await this.page.evaluate(()=>[...document.querySelectorAll('[role="menuitem"]')]
      .some(e=>e.getBoundingClientRect().width>0 && e.innerText.trim()==='用量'));
    if(menuOpen) {
      await this.page.keyboard.press('Escape');
      // The dropdown remains measurable during its closing animation. Wait
      // for the same condition used by menu() to clear before reopening it.
      await this.page.waitForFunction(()=>![...document.querySelectorAll('[role="menuitem"]')]
        .some(e=>e.getBoundingClientRect().width>0 && e.innerText.trim()==='用量'),
        undefined,{timeout:5000});
    }
    let value=await this.readCard();
    if (value.completed || value.reward) return value;
    await this.menu();
    await this.page.waitForSelector('loc=role:menuitem[name="每日签到"]',{state:'visible',timeout:5000});
    await this.page.click('loc=role:menuitem[name="每日签到"]');
    await this.page.waitForSelector('loc=css:button[aria-label="今日已签到"],button[aria-label^="签到得"]',{state:'visible',timeout:5000});
    return this.readCard();
  }
  readCard() {
    return this.page.evaluate(()=>{
      const buttons=[...document.querySelectorAll('button')].filter(e=>e.getBoundingClientRect().width>0);
      const completed=buttons.some(e=>e.getAttribute('aria-label')==='今日已签到' && e.disabled);
      const available=buttons.filter(e=>/^签到得\s*[\d,]+$/.test(e.getAttribute('aria-label')||'') && !e.disabled);
      const label=available.length===1?available[0].getAttribute('aria-label'):null;
      return {completed,reward:label?Number(label.replace(/[^\d]/g,'')):null,label};
    });
  }
  async points() {
    await this.menu();
    await this.page.hover('loc=role:menuitem[name="用量"]');
    for(let attempt=0;attempt<5;attempt++) {
      await this.wait(1000);
      const points=await this.page.evaluate(()=>{
        const labels=[...document.querySelectorAll('span')].filter(e=>e.getBoundingClientRect().width>0 && e.innerText.trim()==='积分');
        const values=labels.map(e=>e.parentElement.innerText.trim().match(/^积分\s+([\d,]+)$/)?.[1]).filter(Boolean);
        return values.length===1?Number(values[0].replaceAll(',','')):null;
      });
      if (Number.isSafeInteger(points)) return points;
    }
    return null;
  }
  async claim(reward) {
    await this.dismissInformationalPopups();
    const card=await this.readCard();
    if(card.completed || card.reward!==reward) throw new Error('签到状态已变化，未提交领取');
    await this.page.click(`loc=css:button[aria-label=${JSON.stringify(card.label)}]`);
  }
  async login() {
    // Only the ordinary existing-account route; never read credential values.
    if((await this.inspect()).authenticated) return;
    await this.dismissInformationalPopups();
    await this.page.snapshot();
    const blocked=await this.page.evaluate(()=>!![...document.querySelectorAll('[role="dialog"],.ant-modal-content')]
      .find(e=>e.getBoundingClientRect().width>0 && /验证码|验证身份|安全验证/.test(e.innerText)));
    if(blocked) throw new Error('登录入口被验证或公告遮挡，需要在保留页面处理');
    const top=await this.page.evaluate(()=>[...document.querySelectorAll('button')]
      .filter(e=>e.getBoundingClientRect().width>0 && e.innerText.trim()==='登录')
      .map(e=>({x:e.getBoundingClientRect().x+e.getBoundingClientRect().width/2,y:e.getBoundingClientRect().y+e.getBoundingClientRect().height/2}))
      .sort((a,b)=>a.y-b.y)[0]);
    if(!top) throw new Error('未找到登录入口，需要人工处理');
    await this.page.mouse.click(top.x,top.y,{label:'打开普通登录入口'});
    await this.wait(1000);
    await this.page.snapshot();
    await this.page.click('text="密码登录"');
    await this.wait(10000);
    const normal=await this.page.evaluate(()=>{
      const visible=e=>e.getBoundingClientRect().width>0;
      return [...document.querySelectorAll('input[type="password"]')].some(visible) &&
        ![...document.querySelectorAll('[role="dialog"],.ant-modal-content')].filter(visible).some(e=>/安全验证|图形验证码|滑动验证/.test(e.innerText)) &&
        ![...document.querySelectorAll('input[type="checkbox"],[role="checkbox"]')].filter(visible)
          .some(e=>e.matches('input')?!e.checked:e.getAttribute('aria-checked')==='false');
    });
    if(!normal) throw new Error('登录需要人工验证或确认协议，已保留页面');
    await this.page.click('text="立即登录"');
    await this.wait(10000);
  }
}
