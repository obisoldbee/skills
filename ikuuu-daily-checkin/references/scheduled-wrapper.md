# 单轮自动化

## 任务

在支持本地命令和当前所选浏览器控制工具的 Agent 自动化中执行一轮 Ikuuu 签到。本模式不依赖 Mavis，不创建提醒、不用 sleep 等待下一轮、不修改主任务、不写磁盘重试状态。主任务只负责触发；流程、停止规则、通知和报告由 Skill 完成。

## 配置与授权

自动化 prompt 只需调用本 Skill 的 scheduled 模式，提供 `lark_chat_id`，授权签到及按本规则使用飞书 CLI、`--as bot` 发消息。会话 ID 不得写入 Skill、脚本或默认值。缺少目标/授权则在网站操作前返回 `needs_configuration`。运行日期从当前系统时间按 `Asia/Shanghai` 计算，不从旧对话日期推断。

## 服务维护

每轮先读 [service-maintenance.md](service-maintenance.md) 判定状态，确认维护时按所选路线关闭本轮自建页面。正常、维护和未知轮都在下列第 3 步调用一次状态脚本。该脚本持久保存维护转变与送达回执。

## 顺序

1. 执行 SKILL.md 规定的一轮浏览器流程，保留奖励、余额、失败原因和本轮实际页面标识。Ego 使用真实数字 Space ID；其他路线保留工具实际返回的 `runtime:kind:id`，例如 `tabbit:tab:<实际ID>`。
2. 执行 [task-space-cleanup.md](task-space-cleanup.md)：正常结果和确认维护必须按路线完成清理并读回结果，未解决异常才保留/交接。Ego 核验整个 Space 消失，其他路线关闭本轮自建对象并保留用户指定原页。该步骤不可因“原已完成”“无需通知”而跳过。先固定业务结果，清理失败单独记录，不抢占用户页面、不重开网站。
3. 按下表判断本轮业务提醒，把 `low_traffic` 或 `failure` 作为 `--business-notice` 交给维护脚本，无业务提醒时省略。维护脚本返回 `transition=entered/recovered` 时，按 `notification_kind` 记录它实际处理的提醒和送达结果，本轮通知结束。脚本确认没有维护转变时，按下表发送到期的业务提醒一次。
4. 按 [result-report.md](result-report.md) 调用 renderer，把中文短报告原样放在一个 text 代码块中，直接结束。不要附通知条件推理、执行摘要或“30 分钟后重试”。

## 通知条件

- 成功且刷新余额 >= 20 GB：不推送。
- 刷新后明确余额严格低于 20 GB：推送流量不足提醒；MB/GB/TB 按 1024 换算。未知/歧义单位不判断阈值。
- 排除已确认维护，本轮业务未完成、需人工处理或运行环境失败：推送失败提醒。若同时有低流量证据，只发失败提醒，避免重复通知。
- 仅页面清理异常时只记本地结果。已知关闭失败传 `--page failed`，关闭结果待核实时传 `unconfirmed`，两者均附实际页面标识。
- 失败正文固定为 `Ikuuu 签到异常。`；仅低流量时固定为 `Ikuuu 流量不足。`。只发这一句，不附日期、原因、奖励、未知余额、空间 ID、链接、操作说明或签名。发送脚本只接受这两种正文。
- 幂等键：`ikuuu-{YYYYMMDD}-failure` 或仅低流量时 `ikuuu-{YYYYMMDD}-low-traffic`。

## 飞书发送

读取当前可用的 lark-shared、lark-im 及 messages-send 指引。固定调用包内独立机器人发送脚本，不直接使用宿主插件 PATH 中的 lark-cli。宿主可能注入 user-only 外部 OAuth；脚本仅在独立子进程中使用部署者配置好的本地机器人CLI/profile，验证 identity=bot/available=true 后单次发送，不改插件、全局strict-mode或钥匙串。`config/lark-bot.local.json` 仅有 CLI 路径/profile，属于不入Git的本机接入配置；会话ID仍只来自自动化prompt。配置缺失才需要部署者处理，运行时不能改配置。用参数数组或正确 shell 引号传正文：

```text
python3 <本Skill目录>/scripts/send-bot.py --config <本Skill目录>/config/lark-bot.local.json --chat-id <caller_lark_chat_id> --text <rendered_message> --idempotency-key <key>
```

成功必须有退出码 0、JSON `ok: true` 和消息 ID；保留 ID 作为回执，不把“准备发送”当成送达。CLI 不可用、失败或不明确时，在任务结果中写“通知失败/未确认”，不改配置、不换身份、不再次发送。CLI 幂等窗口有限，不宣称跨天或无限期去重。

## 输出

唯一最终输出合同见 [result-report.md](result-report.md)。只输出 renderer 的短报告；命令回执、通知条件判断、实际尝试的完整轨迹保留在内部上下文或调用者已有日志。未完成时原因只概括实际失败入口；不能声称未尝试入口都失败。本轮可恢复的站点尝试属于一次执行内的正常流程，不是额外调度重试。

旧 MiniMaxCode 十轮自提醒合同保存在 [minimaxcode-retry.md](minimaxcode-retry.md) 供旧平台维护，不用于本模式，不需要加载。
