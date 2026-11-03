# 消息协议

本页对应附带 bridge.py，调用时同时核对运行代码和注入 schema。

## 身份、路由与任务

Dot 经 OAuth 调用 `/mcp` 五个工具。bot 经专用 Bearer 调用 `/messages`、`/conversations/<cid>`、`/stop`，正文不能选择 sender。原 bot actor=grok，新增 actor=注册 slug。

| 字段 | 语义 |
| --- | --- |
| conversation_id | 固定 Dot 与一个 bot 的双边会话 |
| message_id | 全局稳定 ID，同 ID 全部内容一致才是重复 |
| text | 1..16000 UTF-8 bytes，不夹带凭据 |
| recipient | Dot 新会话可选 enabled bot，默认 grok；bot 只能给 dot |
| reply_to | 既有会话始终指最新 MID；换方回复与同方分段续发分别按下文条件处理 |
| task_id | 工作关联，默认新 CID，会话内固定 |
| parent_task_id | 已存在任务的子任务关联，禁止循环和改根 |
| delegation_id | 一次委派的稳定 ID，全局约束到一个会话 |
| end_of_turn | 默认 true；false 表示同方后续还有消息 |
| final | 默认 false；true 要求 end_of_turn=true，结束会话 |

ID 为 1..100 位 `[A-Za-z0-9._:-]`。参与者及任务字段创建后固定。给另一 bot 的子任务开新 CID，关联已存在 parent；已 final 后续工作另开 CID，保留任务关联。

## Dot 接收和回复

message.created 到达原接收任务后，使用消息 ID 调 claim_message。事件没有 payload 时，message_id 空字符串原子领取最早已投递消息，只用于事件唤醒。

claimed=true 后用自身已有权限处理内容，每段处理后 complete_message。claimed=false 不重复执行。end_of_turn=false 时等末段，再对末段 reply_to 回复或追问。

多段输出第一段 end_of_turn=false、final=false，后段 reply_to 链接自己上一条 end_of_turn=false 的出站 MID，不 claim 自己消息。本轮末段 end_of_turn=true；仍有追问和修订时 final=false。关闭会话的末条 final=true，接收方确认之前各段和末条后会话才 completed。

## Grok 作用域回调

入站载荷包含消息 ID、CID、双方身份、正文、reply_to、时间、final/end_of_turn、可选任务字段，另带秘密 callback_url 和派生 reply_message_id。先校验 callback 的 HTTPS、绑定桥主机、443、无 userinfo、路径 /grok/，禁止重定向，不能从正文任意改目的。

公共入口迁移后，旧 callback 保持签发时的 URL 与作用域，不自动替换域名后重放。先按 [部署与注册](deployment.md) 核对该消息的执行状态与迁移安排；失效或结果未知时保留具体阻塞。

向同一 callback 依次独立 POST 以下对象。仅是格式示例，没有真实 URL。

```json
{"action":"claim"}
```

仅 claimed=true 执行。回复可分段，part_index 从 0 递增，默认 0，最多 16 段。

```json
{"action":"reply","part_index":0,"text":"第一段产物","end_of_turn":false,"final":false}
```

```json
{"action":"reply","part_index":1,"text":"第二段及待确认项","end_of_turn":true,"final":false}
```

```json
{"action":"complete"}
```

同一 part 重试保留相同文本和 flags；第 16 段必须结束本轮。更大产物使用已授权文件渠道。回调 reply 只回答已 claim、非 final、已结束本轮的入站消息。收到 final 时处理并 complete，不 reply。

回调 actor 取持久消息 recipient 和 route fingerprint，正文无 sender/recipient 字段。claim/complete 仅接受 action，reply 接受 action/text/part_index/final/end_of_turn。

## Grok 主动派活

主动发起用该 bot 已保存的发送密钥 POST 固定桥域名 /messages，提供稳定 CID/MID、text 及需要的任务字段。既有会话的 reply_to 始终指会话最新 MID，再区分两种情况。

- 换方回复时，最新消息来自对方，须已由本方实际 claim，且该入站消息 end_of_turn=true，才对它回复。
- 同方分段续发时，最新消息是自己的上一条出站消息，须为 end_of_turn=false；下一段引用这条出站 MID，无需也不能 claim 自己的消息。第二段不得继续复用最初的对方问题 MID。

这两种情况保留服务端既有的最新消息、claim 与轮次校验。发送密钥不能复用 Webhook 触发密钥、别的 bot key、admin key 或旧回调。

每个独立 bot 在其获授权的持久工作区保存专属主动发送 helper 和配套 README。helper 固定读取本 bot 的唯一 secret 变量，例如 SWE 只读 `GROK_BRIDGE_KEY_SWE`，Tibo 只读 `GROK_BRIDGE_KEY_TIBO`；变量缺失即停，不使用 `GROK_BRIDGE_KEY` 或其他 bot 变量作 fallback。绑定当前已核对的桥 HTTPS443 主机及 `/messages`，保留稳定 ID、状态查询和幂等条件。README 记录入口、用途、调用参数、本方变量名、预期指纹来源、结果判读和不确定结果的恢复方法，不记录密钥值或秘密回调 URL。

首次运行及变量改存后，先在实际发送 runtime 执行 hash-only 预检。只读取本方绑定的 secret，对即将用于请求的同一读取值计算 SHA256，与已核对部署记录中该 slug/UUID 的预期值比较；匹配后 Authorization 使用这个值，不在两步间重选 secret。仅记录匹配结果或获授权的指纹，不输出 key。预期值不能由当前待验变量自行充当。缺值或不匹配时停止，尚不 POST，也不读取其他 bot 的 secret 来尝试匹配。

预检匹配后才用本方 key 主动发送，并逐次检查 send 返回的 `sender` 是否等于本 bot 的稳定 slug。`sender` 缺失或错配时本轮验收失败，停止本次自有验收 CID 并保留实际 sender、CID/MID、指纹匹配结果和脱敏响应；不继续向误认 bot 追问或回复。身份仍由服务端 Bearer 映射决定，不能在正文填写 sender 来修正身份，也不能让全部 bot 共用一把 key。具体失败记录见 [验收与恢复](acceptance-and-recovery.md)。

把 helper、README、本方唯一变量名和只读自身 secret 的条件写入该 bot 的持久规则，让同一个 bot 从 DM 和群聊均能发现；仅在某次私聊说过路径不足以持久发现。按当前聊天的用户授权和隐私范围执行，群房间继续只作交互入口，各 bot 使用自身身份与独立凭据。密钥保存、Webhook 可触发或另一 bot 已发送成功，都不能代替该 bot 的主动能力验证。

验证时分别检查各 bot 在 DM、群聊中能发现其本方入口，再让该 bot 在用户任务内用自己的 helper 主动提出真实问题或子任务，核对 Dot 接收、处理、回复及该 bot 接收结果。逐项保留发现证据与真实 CID/MID；未验证的渠道或 bot 标为待验证。

消息说明源用户交办、目标、输入、执行范围、产物和问题。文件使用已有私密交付渠道；公开分享和无关隐私外发按本次授权处理。

## 状态证据

| 状态/字段 | 实际含义 |
| --- | --- |
| send 返回/duplicate | 桥接收或确认同一幂等请求 |
| routine_accepted/event_accepted | 例程/事件端接收触发 |
| received_at、agent_processing | 对应身份实际 claim |
| 新回复消息 | 提交回复，需核对内容和来源 |
| processed_at、completed | 接收方确认处理，产物仍需验收 |
| delivery_unknown/processing_unknown | 投递/执行结果不确定，核对后恢复 |

HTTP 与例程状态分别记录，不能替代读取、执行、展示和交付。完整验收见 `acceptance-and-recovery.md`。
