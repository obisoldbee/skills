# Ikuuu 短报告

日常任务的最终报告正常固定 5 行：任务日期、结果、剩余流量、页面、飞书。没有独立“领取”行；有本轮已核验奖励时直接并入结果，未核验则不填奖励。额外原因/需处理只用于实际异常。

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
| `page` | 对象，`status` 为 closed / preserved / failed / unconfirmed / not_created；`space_id` 保留兼容字段名，可附真实 Ego 非负整数或其他浏览器的实际 `runtime:kind:id`，如 `tabbit:tab:42`、`edge:tab:abc`。`not_created` 省略该字段。closed 必须有真实关闭核验，不能因为调用 finish 就填 closed。 |
| `page.keep_reason` | 可选，仅当前用户指定保留的原页面填写 `user_requested`，同时要求 `status: preserved` 和实际 `space_id`。这类正常保留不标成收尾异常；关闭失败、异常交接或自建遗留页面不填此字段。 |
| `notifications` | 本轮真实通知尝试数组，无触发用 `[]`。每项含 `kind`（auth / failure / low_traffic / maintenance_entered / maintenance_recovered）、`status`（sent / failed / unknown / needs_configuration）；sent 还必须传实际 `message_id`。 |
| `maintenance_unchanged` | 仅状态脚本明确返回 maintenance 且无变化/未触发时可填 true；脚本失败不能填 true。 |
| `reason` | 可选。仅阻塞/异常时一行简短中文原因，不填正常执行解释，不复制日志。 |
| `action` | 可选。确需用户操作时只写一项必要动作；正常和维护自动等待均省略，不写“结束/无/建议优化”。 |

维护脚本 `transition:entered/recovered` 分别映射 maintenance_entered/maintenance_recovered，status 使用其真实发送结果；无变化不产生通知项。未执行通知、配置缺失、发送失败、回执未知、已送达必须区分。通知情况独立于业务结果：发送失败不抹掉已完成动作，业务正常也不能掩盖收尾或发送异常。

## Ikuuu 输入

| JSON 字段 | 取值与证据 |
|---|---|
| `service_day` | 本轮日期 YYYY-MM-DD |
| `checkin_evidence` | 必填对象，按下方定义传原始时序证据；scripts/checkin_contract.py 自动判定动作及签到状态 |
| `outcome` | 可省略以采用 helper 判定；余额未确认可用 uncertain，其他实际阻塞用 maintenance / needs_user_action / needs_configuration / runtime_unavailable / site_unreachable / failed / unknown。显式 success / already_checked_in / not_completed 必须与时序 helper 一致，否则拒绝。 |
| `reward_verified`、`reward` | boolean；只有本轮点击后新成功弹窗与该点击关联才 true，reward 格式如 "522 MB"；否则 false 且 reward:null。原已签到一律不得携带本轮奖励。 |
| `balance_verified`、`balance` | boolean；必须通过 read-balance.md 的当前卡片与稳定采样，才 true，balance 格式如 "86.38 GB"；否则 false 且 balance:null。 |

`checkin_evidence` 四个字段只取对应时点的原始观察/调用，不由摘要或结果反推：

- `before`：点击前唯一可用“每日签到”为 available；点击前“明日再来”为 done；缺失或冲突为 unknown。
- `click_attempted`：实际调用签到 click 为 true（即使超时、禁用或可能无效）；明确没调用为 false；原始调用记录取不到为 null。脚本据此生成 checkin_action，不能再传“语义上未点击”覆盖它。
- `after`：最终明确“明日再来”为 done；明确仍未签到为 not_done；无证据为 unknown。
- `reward_popup`：点击前无弹窗且点击后新出现成功奖励为 new；进入时就存在为 preexisting；缺少前后证据为 unknown。

renderer 内部实际调用该 helper，不让模型另写一份相反的状态。已有 click 调用只能保留 attempted，是否成功由前后证据决定；这些动作证据保留在输入中，不另增用户报告字段。证据不足的原因用普通中文一句话（如“该轮签到的前后证据不足”），不把选择器、DOM 猜测或子节点故事塞入短报告。

success 必须有本轮签到点击及点击后完成证据；进入时已经签到且没点击则 already_checked_in。成功/原已签到/正常查询必须有已核验余额，否则用 uncertain。点击记录以原始工具调用为准：实际调用了点击就保留 clicked_once，不能改成“没有有效点击”。没有当时的 DOM/回执就不能编造“图标文字匹配”“禁用按钮触发旧弹窗”“别人已签到”等解释；最后按钮禁用不能反推点击前已禁用。收到点击返回、旧成功弹窗、未稳定数字或历史报告均不能补齐缺失证据。只有完整走完现有路由和恢复分支才可填 site_unreachable，原因概括实际入口，完整轨迹留内部记录。

代表性判定：

| 本轮证据 | 应有报告 |
|---|---|
| 点击前为每日签到 → 本轮点击 → 新弹窗 123 MB 且变成明日再来，余额核验通过 | 结果：签到成功（本轮已签到）；奖励 123 MB，不能改称原已签到 |
| 点击前就明日再来且有旧弹窗 123 MB，没有点击 | 结果：已签到（本轮未重复签到），不另列领取或奖励 |
| 签到完成但余额未读清 | 结果未确认；剩余流量未确认，不报告完整成功 |
| 维护中且状态没有变化 | 维护中；关闭页面；不重复通知 |
| 签到成功但通知失败 | 保留签到成功，同时飞书明确写发送失败 |

以下是假设输入的排版示例，不能用于判定真实轮次属于哪种情形；最终回复必须包在一个 text 代码块内，不能追加通知条件说明：

```text
Ikuuu｜2030-01-01
结果：已签到（本轮未重复签到）
剩余流量：99.00 GB
页面：已关闭
飞书：未触发
```
