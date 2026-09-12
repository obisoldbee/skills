# Buddy 短报告

日常任务的最终报告用于让用户立即看懂这次做了什么，正常为 5–6 行。

## 执行与边界

将 `skill_dir` 绑定为本轮实际读取的 SKILL.md 所在包目录（投影可解析到真源）。将下述当前证据组成一个 JSON 对象，通过标准输入交给：

```text
python3 -B "<skill_dir>/scripts/render_report.py"
```

脚本只解析输入并向 stdout 打印短报告；不联网、不操作浏览器、不发送飞书、不写文件。无需为渲染新建输出目录。按运行流程先完成应做的清理和通知，再填实际回执。脚本不会替你完成这些步骤。

最终回复必须是**一个 text 代码块，内容等于 renderer 的 stdout，块前后没有其他文字**。不得转成普通 Markdown 段落（换行会被合并），也不得附 JSON、helper 代码、执行过程、英文解释、账号/会话 ID、message_id、证据表或建议。原始工具结果留在内部上下文或调用者原有记录；不为本要求新建账本。

- 若 renderer 返回非零退出码：先按实际证据修正输入字段，允许重跑纯渲染，不重跑网站动作。证据缺失则保持未确认，不能补假值凑成功。
- 若脚本本身不可运行：只输出 text 代码块中的三行“任务名称 / 结果：报告生成失败 / 原因：实际错误的简短说明”，不把错误堆栈发给用户，不宣布业务失败或成功。
- 用户明确请求证据/调试过程时才另行提供相关证据；定时任务默认不会收到技术长报告。
- 例子都是离线格式示例，日期、积分和余额不是本轮输入。

## 共用输入字段

| JSON 字段 | 当前证据与取值 |
|---|---|
| `page` | 对象，`status` 为 closed / preserved / failed / unconfirmed / not_created；可附实际数字 `space_id`。closed 必须有真实关闭核验，不能因为调用 finish 就填 closed。 |
| `notifications` | 本轮真实通知尝试数组，无触发用 `[]`。每项含 `kind`（auth / failure / low_traffic / maintenance_entered / maintenance_recovered）、`status`（sent / failed / unknown / needs_configuration）；sent 还必须传实际 `message_id`。 |
| `maintenance_unchanged` | 仅状态脚本明确返回 maintenance 且无变化/未触发时可填 true；脚本失败不能填 true。 |
| `reason` | 可选。仅阻塞/异常时一行简短中文原因，不填正常执行解释，不复制日志。 |
| `action` | 可选。确需用户操作时只写一项必要动作；正常和维护自动等待均省略，不写“结束/无/建议优化”。 |

维护脚本 `transition:entered/recovered` 分别映射 maintenance_entered/maintenance_recovered，status 使用其真实发送结果；无变化不产生通知项。未执行通知、配置缺失、发送失败、回执未知、已送达必须区分。通知情况独立于业务结果：发送失败不抹掉已完成动作，业务正常也不能掩盖收尾或发送异常。

## Buddy 输入

- `receipt`：本轮 canonical helper 的完整返回对象。新派出必须来自 `dispatch_receipt()`；仅已有状态使用对应 helper。渲染器校验 receipt，不接受另行指定成功结论。只领礼物用 status_only_receipt 并附观察到的状态，不伪造新派出。
- `gift`：claimed / not_claimed / unknown。仅本轮点击领取并确认“已领取”才是 claimed，并传整数 `points`；其他状态 points 省略或 null，不能引用历史积分。
- 旅行地点/倒计时来自本轮 receipt。派出未知时不把 expected_destination 当成已到达地点；同日旧回执拦截后，不拿旧倒计时冒充当前值。
- 结果只由 receipt 决定；维护是业务暂停，不是完成领取/派出。关闭、通知仍按各自真实回执。

代表性判定：

| 输入证据 | 应有结果 |
|---|---|
| 本轮已领取，派出 helper 确认成功 | 已完成（本轮已派出），显示本轮积分及旅行 |
| 进入即旅行中，没有领取/派出 | 旅行中（本轮未派出），领取：本轮未领取 |
| 点击派出但目标或倒计时缺失 | 派出结果未确认，不自行覆盖为成功，也不重复派出 |
| 同日旧回执结果未知，阻止再次派出 | 此前结果仍未解决，不能说“今日已完成” |
| 确认维护且持续不变 | 维护中，空间关闭，持续维护未重复提醒 |

正常 stdout 示例（最终回复需包在一个 text 代码块内）：

```text
Buddy｜2026-09-13
结果：已完成（本轮已派出）
领取：10 积分（本轮已领取）
旅行：咖啡馆 · 剩余 03:59:47
页面：已关闭
飞书：未触发
```

旅行中示例：

```text
Buddy｜2026-09-13
结果：旅行中（本轮未派出）
领取：本轮未领取
旅行：剩余 03:05:54
页面：已关闭
飞书：未触发
```
