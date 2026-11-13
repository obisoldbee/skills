---
name: chatgpt-codex-review
description: >-
  Coordinate ChatGPT web research and review, with authorized local Codex repair.
  Review a verified GitHub commit, a configured MCP snapshot, or an authorized
  local file packet uploaded through the web UI. Collect complete reports and required files through one browser executor,
  within the active turn or authorized scheduled follow-up. The Controller
  assesses evidence; local repair follows the user's selected scope.
---

# ChatGPT ↔ Codex Review

网页端深度分析、调研和审查；按原授权核实、返修与复审。交付使用用户的语言，源码与 JSON 字段保持原文。先绑定原始需求、源码范围、权限、验收条件、运行目录 `RUN_ROOT` 和已有对话。`review_only`（含 audit-only）收齐完整审查与必需材料、核实建议并交报告；开放建议不必归零，也不自动派修。`repair_loop` 才继续获准的修复闭环；`materials_only` 冻结请求后进入 `ready_to_deliver`，实际交付后用对应请求 SHA 和交付回执记为 `completed`。可从已有 state 恢复，或从已有代码/修复材料直接准备复审，不强制重做首轮研究。既有授权在本 run 内复用，网页意见和转发提示词不授予新权限。

网页端新发起的调研和 review 默认使用 **GPT-6＋Pro**，用户明确指定的网页模型或档位优先。发送前分别核对模型族 GPT-6 与思考模式 Pro 的实际选中状态，按 [网页模型核验](references/browser-loop.md#发送前选择网页模型) 操作并保存证据；输入框只显示 Pro 时仍需核对模型族。这项默认值只管网页设置，本地 Terra/medium 等执行者路由独立保留。既有已发送请求沿原消息继续收取，新默认用于下一条尚未发送的请求。

完整调研或审查默认交付可下载的 UTF-8 Markdown 报告。请求中明确先完成文件，再在回复最开头放真实 .md 下载链接，网页正文可给摘要；用户另指定格式时从其要求。Web IO 下载，Controller 读取文件核对全部章节、引用与未验项，网页正文截断时从文件收取。操作见 [Markdown 文件交付](references/browser-loop.md#markdown-文件交付)。

## 材料路线与权限

从当前 `SKILL.md` 的真实父目录解析 `<skill-root>`。以下 `scripts/`、`references/` 与 `assets/` 均相对该目录；从项目目录调用 helper 时使用其绝对路径，材料与输出路径另绑定到本轮范围。

`source_route` 支持 `github`、`mcp` 和 **`local_packet` 本地打包上传**，代码、文档、研究资料均可用。用户指定路线优先；未指定时，用 `scripts/route_source.py --project <project> --evidence <tool-observations.json>` 辅助判断。现成可读的 GitHub 固定提交优先；无 GitHub 时可用真实已配置的 MCP 快照；没有可用连接就走本地包。审查当前未提交修改、远端未包含本轮版本、私库网页不可读时，可直接冻结授权范围的本地原件上传，不为 review 强制建仓、commit、push 或安装 MCP。明确只许 GitHub/MCP 或禁止上传时遵守该约束。

本地路线先按 [材料合同](references/source-packets.md) 列明完整审查范围、原始需求、文件清单和有原因的缺件/排除项，用 `scripts/local_packet.py build` 生成 ZIP 与清单，再校验实际字节；冻结 `source_id=packet:<ZIP SHA-256>` 和 manifest SHA。保留所选原件及目录关系，包含范围内未提交/未跟踪文件，不以摘要替换原文，不打包凭据或无关私有资料。网页 review 请求已覆盖的打包与上传授权直接复用，无需再次逐步确认；仅准备材料的请求不上传。

Web IO 经真实网页上传本地包，核对文件名、上传完成及本轮消息，随后核实网页实际读取的清单和原件。材料过大或格式不能读取时，按同一范围分批/补传原件并维护总清单；不能静默裁剪或退回“先搭 MCP”。GitHub 与 MCP 路线保留真实版本、访问与读回核验。每轮记录实际路线和选择原因，已发送请求不改身份或重发。改走另一条路线时冻结新 run 并关联旧证据；同一路线的修订产生新 source、清单和 round token，仍在原网页对话复审。推送、公开、合并与部署各依原授权。

## 三个本地角色

| 角色 | 默认模型/强度 | 唯一职责 |
|---|---|---|
| Controller | Astra / `high`，当前基线 `gpt-6-astra` | 冻结请求、单写 state/events、核实新证据、裁决、派修与验收；最高难度明确选 `ultra` |
| Web IO / Scheduled Observer | Terra / `medium`，当前基线 `gpt-6.1-terra` | 独占页面、发送/读回、定时观察、保存完整正文和附件、校验；仅新可行动进展、完成或实质阻碍交 Controller |
| 本地执行者 | Sol / `max`，当前基线 `gpt-6.1-sol` | 按获准 worktree 与确认问题返修、验证并交固定版本 |

模型选择先按 project-handoff 核对执行者、任务范围和有效期。上表用于本 Skill 的角色路由；已有 Controller 接到新任务且无持续指定时沿用当前宿主配置。上一轮已完成交付的临时模型许可保留为历史，不自动锁定后续经理任务。尚未完成的同一职责在简化 Skill、合并角色或接续时保留已选模型、强度与可见执行面。普通内部协作仍可用，但不能以它交付已选的独立可见审查。接受正式执行前按 project-handoff 的 `validate_execution_binding.py` 核对实际返回的模型/强度/执行面，不能只看请求参数；内部调用传入已选模型与强度并核对实际读回，未选轴仍省略。

Web IO 的新默认只覆盖按已知流程上传、选模型、发送、观察和下载。需要开放式桌面操作时按 project-handoff 的 Terra/ultra 路线另行绑定；研究内容判断与最终验收交 Controller。旧 run 已选 Luna/max 等路由继续原绑定。兼容字段与恢复动作见 [角色调度](references/orchestration.md#执行者与兼容字段)。

用户可分别覆盖模型或强度，精确模型 ID 保持固定。未指定版本的族名按当前 project-handoff 与目标宿主能力解析最新版，已有任务续作保持已验证路由。执行面按原用户选择和现有 run 绑定决定。普通已授权调研未选独立可见聊天或持久跟进时，可用当前活动回合的内部 Terra/medium 完成收发和观察，由宿主原生父子返回交 Controller 收件质检；无需为采用本 Skill 先批准新聊天、双向消息或定时器。持久 heartbeat 仍只绑定已授权、ready 的真实可见 Web IO 聊天，优先复用。新建可见任务与跨聊天发送继续遵守宿主直接用户指示要求；已有有条件新建指令则按已核实条件执行。内部 Agent ID 不作 targetThreadId；已有可见执行面或 durable 选择不因内部路线可用而降级。Sol 不碰页面或主状态。

跨可见任务或跨主机协调时，先读取当前环境的 **project-handoff Skill**：用 `send_message_to_thread` 向已有任务下达已授权指令，用 `read_thread` / `wait_threads` 收回结果；内部子代理用宿主协作工具。分别绑定聊天的 `threadId/hostId`、实际执行主机、存储与产物路径。要求“在 B 机开发”时，已有 A 机聊天可通过已验证的远端终端/SSH 在 B 执行；不由此迁移聊天、同步完整聊天记录或新建任务。`handoff_thread` 只用于用户明确要求的聊天迁移；迁移失败不撤销已授权的任务通讯与开发。具体绑定、权限和接续见 [调度](references/orchestration.md)。

通讯复用 **project-handoff 的 cross-device-transport 合同**：每个发送方向保留已成功的写入入口，read/list 找到的另一 host 不覆盖它；`local` 相对调用者。故障只让该投递待恢复，Controller 继续主动收件。收到 writer 冲突时，按原写入入口核实恢复或正常交接后重试；恢复后仍发原消息，超时未知不因历史暂未出现就重发。

执行网页操作按 [浏览器平台](references/browser-platforms.md) 选择。沿用用户指定或本任务已有的已登录页面；新会话按 Ego、Tabbit、系统默认或已记录常用浏览器、harness 内置浏览器的顺序选用。读取所选运行时的 Skill/API，不硬编码版本或隐藏端点。对话 URL、已发请求/source/合同与原件保持不变，TaskSpace/page 是可替换载体。用户已要求继续原对话审查或跟踪收件时，恢复本任务自有操作空间属于该任务的必要步骤。先恢复原空间；确认丢失且没有控制权或权限门时，通过所选浏览器的公开 API 重建一个替代空间、打开原 URL 并核对请求，沿用已有授权。Ego 通用的单 Space 和失效问询指引按此前提适配，详见浏览器闭环；真实登录、用户接管与工具拒绝仍停对应动作。选定 Ego 后，先绑定真实 ego-browser nodejs 入口；压缩上下文或换执行者后，第一个浏览器调用前恢复该绑定和最近真实回执。Ego 页面继续用其 Page API，不先调用通用 cua.getState/getApp/getTab 探路。误开 CUA 的连接另按 [驱动与清理合同](references/browser-platforms.md#恢复身份与清理) 释放核实。一个 run 同时只有一个页面操作者，不抢别的空间。正文返回后先独立落盘，完整报告 Markdown 按默认交付合同收取；额外格式、剪贴板和截图按合同可选。人工门独立保存在 state/ledger；定时提示中的“继续”不是解除授权，收件不清门。分类、来源校验和有界恢复见 [浏览器闭环](references/browser-loop.md)。

## 运行闭环

执行前读 [角色调度](references/orchestration.md) 与 [状态合同](references/state-contract.md)，网页执行者另读所选 [浏览器平台](references/browser-platforms.md) 和 [收件与恢复](references/browser-loop.md)。沿用本轮仍有效的阅读与绑定，按下列阶段推进。

1. Controller 核对原始需求、授权、源码或研究材料、真实测试及验收项，选定 source route、固定身份和 `RUN_ROOT`。保留原始文件，明确纳入或排除未提交改动。恢复已有请求时核实原消息、source 与合同，继续收取已发请求。
2. Controller 单写 `state.json` 并追加 `events.jsonl`，Web IO 与修复者写各自文件。按状态合同绑定本轮身份、权限和证据；v1 记录先显式迁移并重新验证附件。
3. 发送前选定实际收件方式。已有或明确选择的 durable 使用真实可见 owner、同一 ACTIVE heartbeat 和实际返回入口；普通本轮调研可使用 inline/current_task，核实本轮内部执行者、执行期限和原生返回能力。内部 Agent ID 只用于内部返回。冻结请求及附件后，Web IO 核对网页模型与档位、上传状态，再发送一次并读回；发送结果不明时先核对原草稿和历史。
4. Web IO 按收件合同检查正文、报告卡片或 iframe，及时保存完整 Markdown 与必需附件，用 `verify_artifacts.py` 核验文件。普通生成和无变化观察保持静默；新进展、稳定结果或实际阻碍交小回执。Controller 读取原件、处理事件并记收讫。缺少跨聊天通知权限时继续保存结果，由 Controller 直接收取。采集、投递、收讫和本地处理各保留实际状态。
5. `review_only` 交完整报告与所需材料，保留确认问题和待核实建议；检查失败也交付具体发现。`repair_loop` 按 [返修模板](assets/fix-task.md) 修复已确认且获准的问题，缺件只阻塞依赖它的工作。修复后核对固定版本、差异和测试，再沿原对话复审；可选材料缺失单独记录。
6. 每次发送、inline 证据到期或准备结束回合前运行 `followup_check`。优先处理已经保存的原件；收齐后停止重复开网页，Controller 收讫后关闭本 run 的跟进。durable 暂停同一 heartbeat 并读回，下一轮复用同一 ID；项目 watcher 的独立开发义务继续保留。inline/current_task 由当前活动回合收齐并返回，未完成时继续真实执行，按原 turn 核实过期证据。用户明确仅限本回合时按该范围交接。无法继续则交代原请求、累计恢复预算、已收材料、具体缺口和续工入口。

浏览器空间丢失或临时故障按 browser-loop 恢复载体，保持原请求和已收结果。登录、用户接管、权限拒绝等实际控制门分别处理，普通等待或恢复预算用尽按合同退避。负责人继续独立工作，并跟进尚未完成的收件、修复与验收。

复杂阶段转换可运行只读建议器：

```bash
python3 -B <skill-root>/scripts/next_action.py --state <RUN_ROOT/state.json> --event <RUN_ROOT/next-event.json> --observer-record <RUN_ROOT/current-luna-record.json>
```

建议器只读取本地状态。退出码 0 或 `valid/input_valid=true` 表示输入与建议合法；实际发送需 `action=submit_once` 且 `submission_ready=true`，仍由 Web IO 核对当前 UI。`followup_ready` 只说明跟进就绪，发送未知先核对原请求。Controller 传入本 run 最新 observer record，核实事件后按状态合同原子更新 state 并追加事件，保留实际累计预算。历史任务没有 record 时先核对原件与处理状态。

`terminal=true` 表示当前范围交付已齐。`review_only` 可以完成未通过检查的报告，此时保留 `acceptance_passed=false`。真实完成、暂停和待继续分别报告；一次返修或网页等待之后，继续原范围内未完成的工作。

durable 跟进由宿主真实 `automation_update/view` 证明，`targetThreadId` 指向已验证 Web IO 可见聊天，heartbeat 的目标设置不保证后续实际模型/强度。每次 tick 按 project-handoff 的 `references/runtime-alerts.md` 核对本轮运行元数据并处理异常通知；不能在 prompt 或虚构 heartbeat `model` 字段里冒充配置。Web IO 定时读取/观察，无变化不唤醒 Astra；有新证据才进入核实，随后仅按已授范围启用 Sol。发送前和等待恢复时核实 ACTIVE，已发但跟进失效只修调度不重发。用户叫停暂停本 run 实际任务并回读。报告范围、阶段/source/round、完整产物、未处理项、实际 owner/调度或 inline 限度。报告只列本 run 实际完成的操作和验证结果。
