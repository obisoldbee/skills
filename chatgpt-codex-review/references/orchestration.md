# 角色调度与持续复审

Astra Controller 单写 `RUN_ROOT/state.json` 和 `events.jsonl`，核实 Luna 原始网页证据与获准的 Sol 交付。Luna max 独占页面和定时观察，Sol max 只在指定 worktree 修复。角色默认采用当前 `project-handoff`：Astra high（最高难度明确选 ultra）、Luna max、Sol max；2026-09-30 基线为 `gpt-6-astra`、`gpt-6-luna`、`gpt-6.1-sol`。新族名按目标宿主的真实能力解析最新版，已有任务保持验证过的路由，用户精确覆盖优先。实际参数/成功回执、会话设置或原生元数据决定可证明的模型/强度，不以提示词自称作为证据。

普通执行可用宿主内部协作，只有用户直接要求新可见任务才创建。durable heartbeat 必须有 ready 的真实 Luna 可见聊天，先查可复用任务和当前可用的本任务 Agent 空间；内部 Agent、排队中的 clientThreadId 不能作 owner。服务端对话/请求/source/合同保持原身份，浏览器空间是可替换载体：恢复现有空间，确认丢失/崩溃后按 browser-loop 的当前运行时恢复合同处理，允许重开/重建时再恢复原 URL，记录旧→新映射；不重复索取普通恢复许可，不绕过真实登录/用户接管/工具拒绝。替换故障任务前保存产物、未收讫队列与实际身份。无持久 owner 时如实记录所缺能力与选择，不把定时器放到 Astra 聊天上。

角色合并或简化保留同一职责此前选定的模型/强度/可见面，实际执行读回仍须相符；允许的内部助手不替代已选可见 reviewer。复用历史 `gpt-5.6-luna/max` owner 仅限 state-contract 的 `verified_existing_task` 证据绑定，同一个 ready、未归档的真实可见任务；不为新自动创建选旧模型，不让 prompt 自称成为读回。

## 任务通讯与执行主机

协调已有可见任务或跨主机工作时，读取当前环境的 `project-handoff` Skill，并按它的调度、路由和回执合同操作。先以任务工具核实已有角色的身份，再绑定下面三类位置；角色叫 Astra/Sol/Luna 不决定它在哪台机器。

| 绑定 | 核实与用途 |
|---|---|
| 聊天身份与读取入口 | 实际 `threadId` 与可读 host；用于读/等，同一聊天可能经多个服务可读 |
| 消息写入入口 | 按发送方分别保存目标 thread、成功创建/发送使用的 `hostId` 和证据；按 project-handoff 的 cross-device-transport 合同复用，不被新的读回覆盖 |
| 执行位置 | 实际运行源码编辑、构建、测试或浏览器的物理主机与终端/工具；按项目规则验证，不从聊天位置或路径猜测 |
| 材料位置 | 源码 worktree、`RUN_ROOT`、附件和回执的存储主机、挂载与接收方可读路径；跨机传材料后读回字节数/SHA |

在用户已授权协调的现有任务之间，用 `send_message_to_thread` 发送本轮自包含指令，用 `wait_threads` 等待进展，必要时 `read_thread` 有界读取。传该发送方已验证的写入 `hostId`，不能以新发现的读入口或代码执行主机代替；`local` 相对调用者，A→B 与 B→A 分别绑定。state 的 Controller 身份不因读入口改变，实际发送入口由 handoff 记录解析。普通续作保留原模型/强度，遵守 `project-handoff` 的逐轴权限与 route guard。内部子代理用实际父子协作工具，不把子代理 ID 当可见任务 ID。每次派 Sol 都明确结果读取者、下一次检查时间/入口及 Controller 收讫责任；开发/构建等待另记，网页子义务结束不结束整条开发链。缺少向其他聊天发消息的用户授权时，由 Controller 等待/读取交付；不能因没有主动回报权限而丢弃成果或阻塞独立工作。反向消息失败时 Controller 直接 wait/read 读取结果；当前 turn 结束或 idle 不是写入权释放证明。

指令只传当前 run/round、角色、原始要求与现行决策、已授权读写范围、固定源码身份、实际执行/材料位置、原件与回执路径、验收项和剩余动作。接收方先核对本轮指令和当前材料，再继续本轮任务；历史任务只作背景，不从旧上下文恢复过期写入。缺少决策时定向读取相关历史；不复制整段聊天、会话数据库或私有运行时目录，也不要求两机先同步聊天记录。路径在接收方不可读时，只补传授权内的必要工件并校验，保留完整原件而不以摘要替代。

例如：开发聊天留在 A、用户要求开发在 B，就向 A 上该聊天发消息，让其用已验证的 B 远端会话/SSH 执行；开发聊天本就在 B 且终端身份已核实，则直接在 B 执行。用户明确要求新建 B 机聊天时，才按 `project-handoff` 核实该主机真实项目并创建；用户明确要求搬迁现有聊天时，才使用 `handoff_thread`。该工具移动聊天及其 Git 状态，不是消息通道。Project Root 非 Git 或聊天迁移失败，不阻断现有任务通讯，也不把原本获准的开发自动降为只读；只有实际执行能力、必要材料或授权缺口才阻塞相应动作，独立工作继续。

项目规定的开发/构建/验收主机始终有效。相同绝对路径可能经共享挂载指向同一批文件；不同主机或聊天不构成文件隔离，仍需各写入者的独立 worktree 与输出目录。收到消息、任务创建或聊天迁移成功只证明对应操作，最终以指定主机的执行回执和产物核验为准。

## 默认收取与结束门槛

新发起的网页调研/深度 review 默认 `durable`：用户要求完成审查已包含收取结果，不能因未出现“定时”“跨回合”就改为 inline。先选承担检查的实际 Luna/max，再设节奏；常态检查只读指定 state、原对话和回执，无变化静默退出。Astra 负责新证据的裁决与质检，不替代 Luna 周期检查。已有选定的 Luna 路由与收件授权直接复用。创建新的可见聊天及跨聊天发消息仍按宿主所需的直接用户授权；若缺少，先把固定请求、Luna 任务目标、约十分钟的宿主可用节奏、收件对象与停止条件准备好，在发送前解决这一具体前提。不要先发送再放弃跟进。

发送前、inline 期限到或当前回合结束前，Controller 以 `followup_check` 和最新 observer record 核对：原请求是否已发送；正文/必需文件是否收齐；结果是否收讫；若仍未齐，实际 Luna owner、唯一 ACTIVE heartbeat、下一次检查和可执行返回入口是否齐备。工具拒绝、缺创建/通讯授权时报告具体未满足项，不把本地待办或内部 Agent 当运行中的后台。普通生成慢、前端断流、固定刷新预算耗尽只改变检查/恢复动作，不解除收件责任。仅已确认登录/用户接管等人工前提、用户明确停止或完成收取与收讫时，才按原暂停合同停止对应跟进。

Controller 结束当前回合后，不能只留下“以后主动 read”而没有实际唤醒入口。优先使用已获授权的 Luna→Controller 结果通知；缺反向消息权限时，发送前绑定另一条实际可用的收件唤醒入口或取得所缺通讯授权。共享文件只证明结果可读，不证明接收者会醒来。Luna 保存完整结果及小回执，Controller 收讫后做质检；定时器 tick 成功、上传成功、Luna 收集完各是不同阶段。

通讯授权中的一次消息、收齐报告后通知等条件按原人类指令映射为 state-contract 的可选结构化 policy；建议器不制造授权。仍有次数的完成通知可覆盖未来返回，不等 Controller QA/completed 才允许后台等待；实际发送核对请求产物收齐的绑定证据，稳定中断回复不触发。条件不符、次数用尽或旧自由文本尚未忠实映射时，只停止该发送，保留 payload/history；Controller 仍主动读取、QA、收取和继续同范围已授权 review。请求输出收齐、Controller 收讫、质检 coverage 和产品验收分别核实。回合结束时仍要核实实际获准返回入口；通知用尽不把本地收件工作变成待批准工作。

已有 inline 长审查要补 durable 时，先保存原消息与完整旧 ledger；仍有未收讫/未处理的原 payload，先按原 mode 本地收讫并应用，不重写旧 key/payload/SHA。再核实可见 owner、唯一 ACTIVE view 与返回入口，将同事故已用刷新/恢复次数及时间、已有正文/附件证明带入 Controller state，留旧 ledger 归档引用后切换模式，不能因新 observer binding 清零预算或遗失成果。只改跟进执行方式，保留 run/source/round/token/合同/URL/已发消息；本步骤不产生新 review 请求。建议器的 `ensure_durable_followup` 只报告待补的跟进，不伪造创建成功或自动重绑历史。

## 运行材料与接续

`RUN_ROOT` 至少保存：原始需求、权限/披露范围、验收合同、各角色的通讯/执行/材料位置绑定、source route 及证据、state/events、每轮冻结 prompt、Luna 完整正文/附件/观测与小回执、Astra 逐项裁决、Sol 固定交付和本地检查。文件按 run/round 命名，不覆盖旧轮。Astra 用同目录临时文件原子替换 state，再追加事件；Luna/Sol 不追加主事件流。压缩上下文后先读取实际 state、当前 round 和原始资料。

已有 state 按真实 phase、原件和当前授权恢复；旧 v2 的缺省 `repair_loop/durable` 是兼容解释，不替代用户原始范围，接续前补录实际 scope/mode。补成相同默认语义保留旧 ledger/key/payload/SHA/状态与预算，真实 scope/mode 改变才按新业务绑定。Controller 接续恢复同样传最新 Luna record，沿用已用事故预算；载体恢复只解除证据已确认的载体 blocker，无关或未分类业务条件保留，独立恢复仍可做。已有代码/修复记录但无 Skill 历史时可直接 `ready_to_submit`，只补缺失/失效检查，不强行初次研究或派 Sol。Astra 保存请求与原始要求、逐项处置、固定源码/diff、真实测试、未验项；Luna 原样收发。`materials_only` 只交冻结材料；`review_only` 可真实发送并收取，但结束于完整审查报告、核实建议及所需材料，不自动采纳建议或要求开放建议归零。只有 `repair_loop` 且原授权包含返修才派 Sol。旧网页请求须核对真实对话、user message ID、原文 SHA 与 source，再记录 `adopt_submission`；本地 token 与网页原文分开，绑定不清先 reconcile，不为接管重发。

Astra 给 Luna 的输入是冻结的 run/round/source/token、prompt SHA、合同 digest、consumer host、精确网页对话和文件清单、实际权限。Luna 的常态回执只含状态、原文/附件路径、字节数/SHA、下载验证状态、消息 ID 与异常；正文和页面快照不反复粘给 Astra。Astra 必要时读原文件裁决，不把 Luna 总结当完整审查。新一轮沿用已核准的路由、模型和权限；只有身份/范围/权限变化才复核。GitHub 复审用新完整 SHA、diff 入口、测试回执、待复审点，完整源码仍可取；Luna 不重传整个源码 ZIP。

完整回复后，Astra 将发现分成确认缺陷、待裁决主张、已证据反驳、范围外建议和必需未验项。若必需附件缺失，先推进与文件无关的确认修复及文本核实；`pending_file_findings` 保留待处理数量。Luna 在 repairing/validating 期间补取文件后，Astra把当前验证回执交给同一个 Sol 继续，不创建重叠 writer；局部 worker 交付不消除缺件义务。Sol 的输入含精确写入范围、原始需求、确认问题和依赖附件、完成标准；文件依赖项完成时明确计入 `addressed_file_findings`。每次返修交固定新身份/差异/检查记录。一次 worker 完成只进入本地验证，失败继续诊断与返修；没有默认一次反馈预算。网页意见不授权需求扩大或外部写入。

`followup_mode=inline` 仅用于已经观察到完整回复、可短时收取的 `capture_existing_reply`，或用户直接限定仅本回合的 `explicit_user`；绑定 `inline_policy` 的实际依据、本 turn 的 Luna model/effort、执行回执和有界期限。新深度审查时长未知，不属于已完成回复收取。inline 无后台；到期仍未收齐则走上述 durable 接续，不能反复续期限让 Astra 留守。用户明确禁止后台或限定本回合时遵从其范围，交未完成检查点并说明尚未收到结果，不把该例外推广到普通 review。仅执行证据过期但仍是获准的短时收取时，可更新真实绑定；更换执行者/turn 只重开未完成稳定窗口，保留错误去重、预算和未收讫原 payload/evidence。普通 wait/sleep 不是持久调度。

跨回合采用 `durable`：先查本 run 的真实 `automation_update` heartbeat 与现有 Luna owner，默认建议每 10 分钟并记录宿主实际节奏。使用支持的 `targetThreadId` 绑定 Luna 的真实 threadId；它继承目标聊天模型/强度，heartbeat prompt 不配置模型，也没有本 Skill 发明的 model 参数。核实 owner 的聊天 host、实际 model/effort、证据限度，另绑 Controller 目的地与直接用户通讯授权。`read_thread` 不一定给模型字段：显式 create_thread 参数和成功原始回执连同已运行进展、真实会话设置或原生运行元数据可作为可接受证据；仅接受请求不能冒充独立服务端模型核实。缺适合的现有 owner 且用户未要求创建时，报告缺少的 owner/创建选择或调度能力，允许在本回合准备/有界观察，不偷建可见任务、Controller heartbeat、standalone cron 或睡眠常驻。

发送前冻结请求、核实同一 heartbeat 的 ACTIVE view 与本 run 活跃 ID 清单，进入 `awaiting_send` 的短发送窗口；首次 `/c/id` 尚未产生时先绑定 run/state/owner，发送读回后补 URL。每轮发送前重新 arm 同一 ID，等待恢复也核实 ACTIVE；已发送但调度失效只修跟进，不重发。正常跨轮保留 ID；旧 ID 确认已删除/不存在且有原始工具证据才换绑，禁止同一 run 重复活跃调度。旧 v2 的 Controller heartbeat 先按宿主工具暂停/删除并保存真实 readback，再绑定 Luna；新门禁会拒绝旧 owner，不能为关闭旧任务而伪造 Luna。检查旧/新任务去重；不假定宿主能原位改 owner。

每次 heartbeat 直接唤醒 Luna：先读主 state，再写独立 observer record。`waiting_web` 只观察本轮新回复；正文稳定后若必需附件仍缺，只继续 capture，repairing/validating 也只补该轮缺件。无变化、普通流式变化、同一旧错误保持静默，不激活 Astra。新可行动进展、稳定回复或实质错误转变由门禁产生一条小回执；去重绑定 source/round/message+内容 SHA 或错误转变。先保存原 payload、通知 key/SHA 与待交记录，再按直接用户通讯授权通知。投递成功不等于 Controller 收讫；采集后只核对独立回执/Controller state，不重开已收齐页面。unknown 核对原请求；即使历史暂未出现，也不代表超时请求不会稍后落地。明确未送达后，按 handoff 恢复原写入入口，保存绑定本条通知/上次尝试的 write_endpoint_recovery；idle 本身不能解锁重试。冷却及有效授权仍适用，原 payload 不变。预算耗尽留可读检查点和低成本收讫核对，Controller 主动读取即可收敛。无通讯授权也保留原件供读取。

Astra 处理 observation、artifact_receipt 或 assessment 时可在同次 state 更新记收讫，无需额外往返/审批；直接读取共享回执也可记 controller_received。采集和收讫已闭合但尚未应用原事件时，Controller 从最新 ledger 的 process_saved_result 取得原 payload 本地处理；Luna 只 pause_followup，不承担裁决，不因旧 waiting_web 再启网页轮询。处理后正常 triage/附件处理/交付动作保持。既有 state 已核实处理同一 message/body SHA 或相同附件回执时，亦是收讫证据。处理结果、接续恢复和关闭本 run 跟进时将最新 Luna record 传给 helper；缺旧 record 不伪造空记录，按原件核对。消息仅提示，Controller 仍负责核实原件、收件和获准 repair_loop 的后续派修。

本 run 的正文/必需文件和已排队收讫义务均闭合、用户停止或已确认必须人工处理时，暂停**同一现有** heartbeat 并 view 读回 PAUSED；暂时忙碌、额度恢复等待和刷新预算耗尽不取消低成本观察。Luna 可执行已获准的本 run 暂停并写独立 readback，Controller 后续核对并更新主 state。项目级 Luna watcher 尚有开发/构建等待时仅关闭网页子义务，不能暂停整个 watcher。暂停保存未收讫 payload/检查点；真实人工停止先按 browser-loop/state-contract 核对对应 browser_gate 的解除来源（定时 prompt 的“继续”不算），再核实同一 Luna owner 的 ACTIVE 状态后继续核对，不改用 Controller heartbeat。下一次发送前 re-arm。模型/host 无法验证时保留恢复入口并报告能力缺口；durable 请求仍待满足。旧工作无调度则直接验收，不先建再关。离线 helper 只校验声明结构与决策，不证明真实调度/模型/browser 执行。

最后门槛按 scope：review_only 要当前源码的完整审查、所需附件和约定报告交付，保留确认问题/待核实建议；约定检查失败也保留证据并交未通过报告，acceptance_passed=false，不派修或要求先批准修复。repair_loop 还需确认缺陷和待裁决主张归零、同一合同的本地必需检查与交付通过。不为纯审查添加原生构建/修复门槛。测试宿主错误不冒充产品缺陷，网页检查不冒充设备验收；新源码/合同使旧证据失效。发布、合并和安装各按原授权，未获推送许可不冒用旧版本。自动选路或用户选择 local_packet 时，将本次获授权原件打包上传即可，不要求先推送；已发 run 若换路线则另冻新 run 并关联旧证据。
