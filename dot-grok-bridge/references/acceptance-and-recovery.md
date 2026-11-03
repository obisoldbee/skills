# 验收与恢复

## 逐层记录

给每个目标 bot 记录独立结果。服务启动、表单保存、身份校验、投递、claim、实际任务执行、回复/产物展示、complete 各是一项证据。报告使用“已观察/待验证/阻塞”，不把所有层压成一个“接通”。

本包的离线测试证明参考实现的特定分支，不能证明目标账户、客户端或当前会话运行正确。真实验收由原始双方实际执行，部署/调试 agent 只观察和协调，不代 claim、complete 或伪装另一身份。

## 真实协作验收

先检查用户正在进行的工作、服务健康和在途记录。每次新验收使用新的稳定 CID/MID 和明确属于用户交办的任务，不能重放 stopped/expired/final 会话。以下按依赖完成，可在同一用户任务内组合，不额外派无关工作。

1. Dot 向一个 bot 发用户范围内的实际子任务。原 bot 领取、使用自身工具执行，回传有用结果。先确认独立 bot 和路由正确，再扩展其余目标。
2. 在该任务内让一问产生两段独立回复，首段 end_of_turn=false，末段 true，均 final=false。通过 send_message 或主动 `/messages` 同方续发时，第二段 reply_to 指第一段出站 MID，第一段保持 end_of_turn=false，不 claim 自己消息；作用域 callback 按 part_index 递增。Dot 自动领取、展示并 complete 每段，收到末段才继续。缓存验收同时核对三层 send_message 描述全文，见 [界面与缓存](ui-and-cache.md)。
3. Dot 给出实际追问或审阅意见，对方修订并交付产物。核对任务的输入、执行及产物，不只核对暗号或自报“完成”。
4. 核对同一个已登记 bot 持久保存的主动 helper、README、本方唯一 secret 变量与发现规则，分别从 DM、群聊确认可发现。首次运行先在实际 runtime 做 hash-only 预检，对比本方预期 SHA256，匹配后该 bot 才使用自己的 helper 主动向 Dot 发一次用户任务内的实际问题/子任务。检查 send 返回的 sender 等于本 bot 的稳定 slug，再验证当前事件订阅和接收规则；Dot 执行或回答后，bot 接收结果。配置已保存或只有 Webhook 可用时，主动协作继续待验证。
5. 成果交付并确认后发单条 final=true。原接收方处理并 complete，核对之前各段完成及会话 completed。

多 bot 扩展至少逐个验证身份、Dot 发起、主动入口的持久发现和该 bot 主动发起。完整多轮、分段和产物流程先做一个代表目标，再按用户任务覆盖有差异的例程；未跑过的目标与渠道明确列出。任务需要跨 bot 时由 Dot 开独立子会话，使用已存在 parent_task_id 和稳定 delegation_id 汇总。

群聊发起时保留原群与原参与方，由发起 bot 使用自己的 helper 直接向 Dot 建立双边会话，接收并处理 Dot 的结果后交付回原群。验收同时核对桥内真实消息/领取/完成记录与原群的实际交付界面；不以新聊天替代原群交付。

验收记录使用脱敏 CID/MID、actor、sent_at/received_at/processed_at、status、final/end_of_turn、attempts、代码版本、双方真实行为和产物的授权位置。原始正文、个人文件链接、secret、callback URL、delivery URL 不进公开 Skill。当前实例的详细记录留在其私密交付范围。

## 主动发送身份错配

出现 sender 错配时，先对照服务端登记身份与 key 指纹，再在实际发送 runtime 对本方绑定变量做 hash-only 核对。曾有同名 `GROK_BRIDGE_KEY` 跨 bot 覆盖，使原聊天的 helper 实际使用另一 bot 的 key；聊天标题、UUID 和 registry 中各 key 不同都没有核实 runtime 的实际取值。

原始 bot 和新增 bot 均改用各自唯一变量，helper 与原例程固定引用本方变量、只读自身 secret、无通用 fallback。例如原始黑布丁使用 `GROK_BRIDGE_KEY_BLACK_PUDDING`，继续按其原绑定 actor 验证 sender。已有正确原 key 可经 native 安全卡改存，无需重生成。

安全卡保存、bot 自报匹配、实际 runtime 指纹回读与真实协作分别记录。发送前比对将用于请求的同一值，发送后回读 sender；具体会话结果及验收证据存放 Skill 树外。

发生身份误认时，仅停止本次自有验收 CID 并保留失败证据，不续发。后续验收在状态核对与本方指纹预检完成后使用新的稳定 CID/MID，不复活已停止会话。

## 故障分层

| 现象 | 查什么、怎么处理 |
| --- | --- |
| HTTP400，旧会话已 final | 读实际 conversation state；开关联新会话，不复活旧 CID |
| 参数不识别或旧轮数限制 | 核对代码、插件目录、Dot 运行工具三层及实例环境限制 |
| 原 Dot 依旧描述让第二段复用 q1 被拒绝 | 回读三层 send_message 描述全文；第二段应指自己上一条 end_of_turn=false 出站 MID，不 claim 自己消息；修正描述和指针，保留服务端校验 |
| 完整请求设置 end_of_turn=false，对方等待后续 | 由原发送方在同 CID 的消息链上，引用自己上一条 end_of_turn=false 出站 MID，使用稳定新 MID 补 end_of_turn=true、final=false 收尾；修正 helper，使常规完整请求显式 end_of_turn=true，保留既有消息不改写 |
| HTTP401、主动发送失败 | 核对发送 key 的 bot 身份及用途，安全卡保存状态；不在聊天重贴 key |
| 本方变量缺失或 SHA256 与预期不符 | 停止 hash-only 预检，不发请求；核对本方唯一变量与 helper 固定引用，不读取其他 bot secret 或回退通用变量 |
| send 返回 sender 缺失或错配 | 本次验收失败；仅停止本次自有验收 CID，保留实际 sender、CID/MID、预检结果与脱敏响应，不继续向误认 bot 回复；服务器保持按凭据认身份 |
| DM 或群聊找不到主动发送入口 | 核对该 bot 的持久 helper、README 与发现规则，分别回读两个入口；不只补一次聊天提示 |
| 入口迁移后不触发或 SID 不一致 | 对照宿主 list 与服务端新 SID，检查旧 source 停用、原 task 的新 trigger 和同一 owner/Dot 绑定；按 deployment.md 的迁移前提处理 |
| HTTP400，route unavailable/changed | 读配置 epoch 与消息 fingerprint，禁用/轮换后先核对在途工作，不回落旧目标 |
| webhook 2xx 但无回复 | 分别查 routine_accepted、received_at、执行阻塞和 processed_at；不盲目重触发 |
| Grok 400 | 保存脱敏响应摘要和对应运行记录；错误原因未知就标 unknown，不凭状态码猜原因 |
| delivery_unknown/processing_unknown | 查上游运行记录、原始聊天和已有产物，按下文原接收方证据恢复条件处理；不自动改 ID 重做或直接修改数据库 |
| 自动审核拒绝 | 查实际动作、主动 /messages 规则和自行追加的公开/覆盖操作，读 ui-and-cache.md |
| 本人确认要求 | 准确转达已有用户授权与代办身份，仍拒绝则交还指定原会话确认，记录具体门槛 |
| Automation run rate limit exceeded | 记录提供方实际 automation 错误和时间；其余额度含义 unknown，不推成聊天周额度或五小时限额 |

参考实现对非 Dot 投递不盲重试。Dot 事件投递在部分暂时失败时有限重试，规则见当前代码；消息处理未知时更不重做。provider 限流后不换账号、换路径或重放绕过，是否再试由真实解除情况和用户要求决定。不自行建定时任务。

完整请求误设 end_of_turn=false 时，对方会按协议等待后续。让原发送方修正 helper 与原例程的常规完整请求规则，显式设置 end_of_turn=true，再沿同 CID 的自身上一段补收尾；既有消息保持原记录。补段后的对方领取、处理与完成继续按真实记录验收。

stop 只阻止队列投递和后续回复，不能强制取消已在对方电脑执行的任务。仅停止本次自有失败测试会话，避免停止用户其他任务。

## 恢复和回滚

改路由、换凭据、重启前先读在途状态。系统维护重启后先核对重启来源、服务稳定状态及受影响的会话/消息记录，再判断恢复路径，不因 unknown 直接修改数据库。新验收使用新且稳定的 CID/MID；当前 active 会话按以下条件恢复原工作，保留原失败与恢复证据。

重启使入站处理进入 unknown 时，由原接收方凭自身上下文及持久产物确认该入站已实际处理，并核对会话仍 active、最新入站仍为这条消息，且预定交付的 v2 稳定 MID 尚未入库。条件满足后，原接收方可以本人 complete 该入站，再按协议继续原产物交付，保持既定 v2 MID，不重新执行已有产物的任务。

若 v2 MID 已入库，先查询并对照该消息的正文、路由、任务字段与处理状态，沿既有记录继续，不换 ID 重派。上下文、产物或当前状态证据不足时保持 unknown；部署方不能代原接收方确认或 complete。恢复原入站和提交产物分别记录，仍须对方实际领取、处理并完成，且产物通过验收后，才能把会话记为通过。

退回旧两主体版本前，停止新派活、禁用新增路由、识别并隔离新增 recipient 的队列与回调，再使用明确只消费 dot/grok 队列的兼容版本。旧原始实现可能把未知 recipient 分支当成 Dot；未检查队列保护的旧代码禁止直接消费新库。

保留追加列/表和部署后的真实消息，不用旧数据库覆盖新记录。没有兼容回滚代码时，先保持当前版本并关闭受影响新路由，修复或准备受检保护版本，不能靠丢记录回滚。同入口恢复核对原 OAuth/订阅；公共入口迁移核对原 OAuth client、同一 owner/Dot、原接收 task 的新 source/trigger/SID，以及旧 source 已停用且无并行 receiver。两种情形均检查旧两主体路由及新增消息未误投。
