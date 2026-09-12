# 必经收尾：正常关闭 space 后才结束

读取当前 ego-browser Skill，以其 API 和控制权规则为准。本文只管理本轮空间，不清理历史同名空间或其他任务。

## 分支

- **确认维护**：按 [service-maintenance.md](service-maintenance.md) 判断后，与正常结果共用下方关闭步骤；每轮关闭空间，首次维护和恢复各通知一次，持续维护静默。不能因为本轮没签到/没旅行就保留维护页。

- 正常结果：completed_cycle、already_travelling、daily_limit_reached、无待领礼物、只领礼物已完成以及正常只读查询。只停止业务操作，**不能直接 return、输出最终报告或结束任务**；必须走下方关闭步骤。
- 发生问题：未登录、验证码/人工确认、未确认为维护的网络或页面异常、业务证据不确定、用户接管。停止业务操作，遵守 ego-browser 停止规则；需要用户处理时 `await task.handOff()` 并核验，保留空间并报告原因。不调用 finish 伪装正常结束，不夺回用户控制。
- 未创建空间：记 `not_created`，不为收尾新建空间。业务门槛在开网页前结束时也不创建空间；若同轮已经创建，则按真实正常/异常结果收尾。

## 正常关闭步骤（所有正常分支共用）

1. 只创建本轮一个 TaskSpace，创建时记录数字 `task.spaceId`，使用其初始 p1。后续 heredoc 只按该 ID 恢复，不按名字猜选，不新建空间恢复错误。保存已取得的业务证据后停止网站操作。
2. 同一 heredoc 用已有 task；跨 heredoc 用 `const task = await taskSpace(TASK_ID)`，TASK_ID 必须替换为本轮实际数字。只调用一次 `const receipt = await task.finish({ keep: [] })` 并等待返回，输出脱敏回执。禁止省略 keep、保留 p1、`keep:"all"`、旧布尔参数和旧完成/交接辅助接口。
3. 不要通过导航 about:blank、逐个关标签页、输出“已完成”来代替 finish。成功 toast、脚本退出码或旧 `done:true` 不能证明 space 已关闭。若实际回执未明确证明整个空间关闭，只读调用 `listTaskSpaces()`，可间隔 2 秒观察最多 10 秒等待列表同步，按本轮数字 ID 核验空间不存在；不重新打开空间来验证。
4. 确认关闭后才走适用的飞书规则和最终报告。正常不需要请用户关闭浏览器；后续通知失败也不重建空间。
5. 关闭报错、只完成但仍保留受保护标签、或核验不明：改记 `cleanup_failed` / `cleanup_unconfirmed`，报告实际原因或“原因未确认”；不宣称整轮正常完成，不重新领取/派出、不重试 finish、不擅自关闭用户创建或 unmanaged 标签。按原有通知规则处理异常，不能借此新增通知场景。

## 收尾记录与报告

内部保留原始关闭/交接回执；最终回复只按 [result-report.md](result-report.md) 的 page 字段呈现，不另附技术回执。closed → closed；handed_off / retained_due_to_error → preserved；cleanup_failed → failed；cleanup_unconfirmed → unconfirmed；not_created → not_created。异常时附真实空间 ID 和一行原因，正常关闭不展示冗余 ID。

业务结果与清理结果分别报告：关闭失败不抹去已经核验的签到/领取/派出结果，更不授权重复操作。仅有未解决的网页异常才保留页面；已确认维护必须关闭；业务正常却无法关闭属于明确的清理异常，不能静默留空白 space。没有核验就写未确认，不把“已完成”徽标当作关闭证据。
