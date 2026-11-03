# 读取稳定的剩余流量

## 原因

2026-09-08 的现场复现中，同一 `/user` 页面“剩余流量”卡片在加载后从 `7.29 GB` 逐步增长到 `104.13 GB`。这是可见 DOM `.counter` 的数字动画；页面已加载、URL 正确和新鲜 snapshot 都不能证明数字已经稳定。不得将该现象解释成账号切换而没有额外证据。

## 规则

通过所选浏览器读取可见页面。绑定标题精确为“剩余流量”的唯一卡片及其 `.card-body`，不从整页任意数字、今日已用、钱包余额或图表百分比取值。选择器失效时以当前可见 DOM 重新定位同一语义卡片，不猜值。

每次页面加载/刷新后先留出至少 8 秒动画时间，再以 1 秒间隔读取；至少连续 3 次完全一致才接受。整个检查最多 30 秒，不重新刷新。若数值仍变化、卡片歧义、单位不明、认证丢失或截图冲突，返回 `uncertain`，余额为“未确认”，不触发低流量报警。

使用 Ego 时，在一次 ego-browser heredoc 内执行以下只读采样。其他浏览器按同样采样间隔和稳定性要求使用其页面读取接口。数字 task ID 使用当前轮次已有的 ID，不创建第二空间；调用前已有页面认证证据。

```js
const task = await taskSpace(TASK_ID);
const page = task.page("p1");
await page.waitForTimeout(8000);
let previous = null, streak = 0, accepted = null;
const samples = [];
for (let i = 0; i < 22; i++) {
  const result = await page.evaluate(() => {
    const visible = e => e.getClientRects().length > 0;
    const headings = [...document.querySelectorAll('h4')]
      .filter(e => visible(e) && e.textContent.trim() === '剩余流量');
    if (headings.length !== 1) return null;
    const card = headings[0].closest('.card-wrap');
    const bodies = card ? [...card.querySelectorAll('.card-body')].filter(visible) : [];
    return bodies.length === 1 ? bodies[0].innerText.trim() : null;
  });
  if (!result || !/^\d+(?:\.\d+)?\s*(?:MB|GB|TB)$/.test(result)) {
    previous = null; streak = 0;
    await page.waitForTimeout(1000);
    continue; // 暂时空值先等待，不在第一帧判失败
  }
  samples.push(result);
  streak = result === previous ? streak + 1 : 1;
  previous = result;
  if (streak >= 3) { accepted = result; break; }
  await page.waitForTimeout(1000);
}
console.log({balance: accepted, stable: accepted !== null, samples});
```

报告前用当前截图核对该卡片一次（不对截图猜测不清晰的小字）。仅稳定、语义卡片绑定和视觉核对一致的数值可用于报告及 `<20 GB` 阈值判断。不要执行新的签到或登录来修复余额读取失败。
