---
name: chatgpt-codex-review
description: >-
  Coordinate ChatGPT web research and review, with authorized local Codex repair.
  Review a verified GitHub commit, a configured MCP snapshot, or an authorized
  local file packet uploaded through the web UI. Luna handles all web IO,
  and quiet scheduled observation; Astra assesses new evidence, and Sol fixes
  confirmed issues only within an authorized repair scope.
---

# ChatGPT ↔ Codex Review

网页端深度分析、调研和审查；按原授权核实、返修与复审。交付使用用户的语言，源码与 JSON 字段保持原文。先绑定原始需求、源码范围、权限、验收条件、运行目录 `RUN_ROOT` 和已有对话。`review_only`（含 audit-only）收齐完整审查与必需材料、核实建议并交报告；开放建议不必归零，也不自动派修。`repair_loop` 才继续获准的修复闭环；`materials_only` 只交冻结请求，不发送或监控。可从已有 state 恢复，或从已有代码/修复材料直接准备复审，不强制重做首轮研究。既有授权在本 run 内复用，网页意见和转发提示词不授予新权限。

## 材料路线与权限

`source_route` 支持 `github`、`mcp` 和 **`local_packet` 本地打包上传**，代码、文档、研究资料均可用。用户指定路线优先；未指定时，用 `scripts/route_source.py --project <project> --evidence <tool-observations.json>` 辅助判断。现成可读的 GitHub 固定提交优先；无 GitHub 时可用真实已配置的 MCP 快照；没有可用连接就走本地包。审查当前未提交修改、远端未包含本轮版本、私库网页不可读时，可直接冻结授权范围的本地原件上传，不为 review 强制建仓、commit、push 或安装 MCP。明确只许 GitHub/MCP 或禁止上传时遵守该约束。

本地路线先按 [材料合同](references/source-packets.md) 列明完整审查范围、原始需求、文件清单和有原因的缺件/排除项，用 `scripts/local_packet.py build` 生成 ZIP 与清单，再校验实际字节；冻结 `source_id=packet:<ZIP SHA-256>` 和 manifest SHA。保留所选原件及目录关系，包含范围内未提交/未跟踪文件，不以摘要替换原文，不打包凭据或无关私有资料。网页 review 请求已覆盖的打包与上传授权直接复用，无需再次逐步确认；仅准备材料的请求不上传。

Luna 经真实网页上传本地包，核对文件名、上传完成及本轮消息，随后核实网页实际读取的清单和原件；本地打包通过不等于上传或审查完成。材料过大或格式不能读取时，按同一范围分批/补传原件并维护总清单；不能静默裁剪或退回“先搭 MCP”。GitHub 与 MCP 路线保留真实版本、访问与读回核验；不存在的服务不能冒充已连接。每轮记录实际路线和选择原因，已发送请求不改身份或重发。改走另一条路线时冻结新 run 并关联旧证据；同一路线的修订产生新 source、清单和 round token，仍在原网页对话复审。推送、公开、合并与部署各依原授权。

## 三个本地角色

| 角色 | 默认模型/强度 | 唯一职责 |
|---|---|---|
| Controller | Astra / `high`，当前基线 `gpt-6-astra` | 冻结请求、单写 state/events、核实新证据、裁决、派修与验收；最高难度明确选 `ultra` |
| Web IO / Scheduled Observer | Luna / `max`，当前基线 `gpt-6-luna` | 独占页面、发送/读回、定时观察、保存完整正文和附件、校验；仅新可行动进展、完成或实质阻碍交 Controller |
| 本地执行者 | Sol / `max`，当前基线 `gpt-6.1-sol` | 按获准 worktree 与确认问题返修、验证并交固定版本 |

简化 Skill、合并角色或接续任务前先保留同一职责已有的模型、强度与可见执行面选择；简化本身不改路由。普通内部协作仍可用，但不能以它交付已选的独立可见审查。接受正式执行前按 project-handoff 的 `validate_execution_binding.py` 核对实际返回的模型/强度/执行面，不能只看请求参数；内部调用若已选 max，须真实传入并读回 max，未选轴仍省略。

用户可分别覆盖模型或强度，精确模型 ID 保持固定。未指定版本的族名按当前 `project-handoff` 与目标宿主能力解析最新可用版本；新请求不沿用过期默认，已有任务续作保持已验证路由。提示词自称模型不算切换；记录实际调用参数/成功回执、会话设置或原生运行元数据及其读回限度。普通协作可用宿主内部任务；持久 heartbeat 必须绑定真实可见 Luna 聊天，优先复用已核实且适合本 run 的任务。只有用户直接请求新可见任务才创建，内部 Agent ID 不可作 `targetThreadId`。Sol 不碰页面或主状态。

跨可见任务或跨主机协调时，先读取当前环境的 **project-handoff Skill**：用 `send_message_to_thread` 向已有任务下达已授权指令，用 `read_thread` / `wait_threads` 收回结果；内部子代理用宿主协作工具。分别绑定聊天的 `threadId/hostId`、实际执行主机、存储与产物路径。要求“在 B 机开发”时，已有 A 机聊天可通过已验证的远端终端/SSH 在 B 执行；不由此迁移聊天、同步完整聊天记录或新建任务。`handoff_thread` 只用于用户明确要求的聊天迁移；迁移失败不撤销已授权的任务通讯与开发。具体绑定、权限和接续见 [调度](references/orchestration.md)。

通讯复用 **project-handoff 的 cross-device-transport 合同**：每个发送方向保留已成功的写入入口，read/list 找到的另一 host 不覆盖它；`local` 相对调用者。故障只让该投递待恢复，Controller 继续主动收件。`idle` 不证明 writer 释放；恢复后仍发原消息，超时未知不因历史暂未出现就重发。

执行网页操作先按 [浏览器平台](references/browser-platforms.md) 选择：先从可调用且满足能力的入口中按用户常用/订阅/登录态偏好选择，包含 Mcode 和已导入 Chrome 数据的 Codex 内置浏览器；无适用偏好时 macOS 默认 Ego、Windows 默认 Tabbit。读取所选运行时的 Skill/API，不硬编码版本或隐藏端点。对话 URL、已发请求/source/合同与原件保持不变，TaskSpace/page 是可替换载体：先恢复本任务现有空间，确认丢失/崩溃后按当前运行时允许的恢复方式重连；重开已有应用/重建空间须符合其实际合同或本任务直接用户授权，再核对原 URL/请求；不重复询问普通可逆恢复许可。用户对本任务的直接恢复指示优先于通用失效问询指引，真实登录、用户接管与工具拒绝仍停对应动作。一个 run 同时只有一个页面操作者，不抢别的空间。正文返回后先独立落盘，额外 Markdown/剪贴板/截图按合同可选。人工门独立保存在 state/ledger；定时提示中的“继续”不是解除授权，收件不清门。分类、来源校验和有界恢复见 [浏览器闭环](references/browser-loop.md)。

## 运行闭环

1. Astra 核对 Project Root 指引、真实源码、原始需求和授权，选定 source route、固定身份、`RUN_ROOT`、验收项和 [附件合同](references/state-contract.md)。原始文件完整保留；未提交改动须明确纳入或有证据排除。
2. Astra 原子写 `state.json`，追加 `events.jsonl`；Luna/Sol 写各自独立文件。v1 记录必须显式迁移并重新验证附件，不能当作 v2 已通过。
3. Astra 冻结原始需求、source/diff、真实测试、逐项处置、prompt SHA、run/round/token/合同/host 与权限。已发送请求先核实原消息 ID、原文 SHA、对话/source 后接管，不为补 token 重发。新发起网页调研/深度 review 默认选 `followup_mode=durable`；收取结果属于原请求，不等用户额外说“定时”或“跨回合”。先按 [调度](references/orchestration.md) 复用已授权 Luna owner 与收件路径。发送前核实本 run 唯一 heartbeat 的真实 Luna owner、继承模型/强度和新鲜 ACTIVE view。缺少有效 owner 时，发送前具体解决现有任务绑定、所需直接创建/通讯授权或调度能力；保留已备好的包和请求，不把跟进缺口留到上传后。inline 仅供已生成完整回复的短时收取，或用户直接限定仅本回合，记录 `inline_policy` 与真实 Luna 执行期限；不能因未提定时、没有 owner 或当前有内部 Luna 而选 inline。Luna 实际 UI 核对网页模型、档位、工具及上传完成，发送并读回；未知先核对历史/草稿。
4. Luna 读主 state，独写观察/交付记录与完整正文/附件，按 [观察门禁](references/state-contract.md) 确认稳定性并去重。先按 [浏览器收件](references/browser-loop.md#观察与收件) 核对本请求的实际输出载体：深度研究报告可能在卡片/iframe 内，外层“研究已启动”不代表报告仍未完成；定位失败或未读到正文不能写成“无新结果”并空等。网页等待与 review_ready/repairing/validating 补件均先使用相同故障/人类门与有界退避，不能因阶段早返而继续正常采集；错误回执可由 Controller 在原阶段直接处理，已收正文保留。普通生成、流式变化和重复旧错误保持静默；仅新可行动进展、稳定完成或实质阻碍回小回执。采集完成、通知投递、Controller 收讫与本地处理分别核实；跨可见聊天通知另需直接用户通讯授权，缺授权保存回执供 Controller 等待/读取。active writer 只有在明确追加前拒绝时才算未送达，其他不确定结果保留 unknown 并核对原请求回执；恢复只重试原身份和 payload，不能由去重丢掉未收讫结果。用 `verify_artifacts.py` 核验真实文件，Astra 从原件裁决并在处理事件的同次 state 更新中记收讫。
5. `review_only` 交完整报告和必需材料即可；确认问题与待核实建议保留在报告。合同检查失败保留证据并交未通过的审查报告，不进入 repairing 或要求批准修代码后才交报告。获准的 `repair_loop` 将确认缺陷、争议和材料缺口分别记录，按 [返修模板](assets/fix-task.md) 派 Sol。缺件只挡依赖文件的修复，无关确认修复继续；可选缺件不阻塞。
6. 每次准备发送、inline 到期或准备结束回合时运行 `followup_check`：仍有网页收取、必需补件或未收讫结果，必须核实 Luna 持久跟进与返回路径；只说“已上传/待收取”不闭环。已发请求补跟进保持原 URL/source/token/消息，先处理旧 ledger 未交结果并继承累计预算，不重发。仅用户明确仅本回合时可按其范围交待办检查点；普通耗时、前端断流、刷新预算耗尽均不等于结束目标。收齐当前回复及必需附件后停止重复打开网页；未收讫时保留低成本 Luna 回执核对，Controller 可直接 wait/read 或读共享原件，不等成功反向消息。除用户停止或独立人工门需暂停外，当前 run 的采集和收讫均闭合才暂停其同一 heartbeat 并回读；仅记 controller_received、原事件尚未处理时，Controller 用最新 ledger 的 process_saved_result 和原 payload 本地处理，不因旧 waiting_web 再启表。项目级 Luna watcher 仍有开发/构建等义务时不能一起停。正文完成但必需附件仍缺时只补件。获准返修交固定版本、差异、测试和未验项；Astra 按原发布权限让新版本可读，冻结下一轮并在发送前重新 arm **同一** Luna heartbeat、核实 ACTIVE 后交 Luna 向**同一对话**发送。旧审查不能验新源码；真实网页/材料/约定检查与交付满足后完成，无隐含一次返修预算。inline 直接交回 Controller，一次 observation 应用即可收讫，不新增 durable 门槛。

复杂阶段转换可运行只读建议器：

```bash
python3 -B <skill-root>/scripts/next_action.py --state <RUN_ROOT/state.json> --event <RUN_ROOT/next-event.json> --observer-record <RUN_ROOT/current-luna-record.json>
```

它不联网、不写 state、不操作浏览器或仓库。`valid/input_valid=true` 或退出码 0 只表示输入与建议合法；只有 `action=submit_once` 的 `submission_ready=true`，`followup_ready` 仅表示跟进就绪，发送未知仍先核对。实际浏览器/UI 仍需核验。Astra 处理结果、接续恢复或关闭跟进时读取并传入本 run 最新 Luna record，沿用同事故实际累计预算，核实事件事实后按 [v2 状态合同](references/state-contract.md) 原子更新 state 并追加事件。历史/手工路径没有既有 record 时核对原始材料和当前处理状态，不伪造空记录。`terminal=true` 只是当前范围的报告/材料/交付已齐，不替代真实证据；review_only 检查失败可完成报告交付，但 `acceptance_passed=false`，不能称检查通过。暂停只因用户明确停止/预算，或完成独立工作后仍需外部改变的阻碍；普通空间丢失/崩溃执行恢复，但不据此解除无关或未分类业务 blocker，一次返修、网页等待或恢复预算不结束整个目标。

durable 跟进由宿主真实 `automation_update/view` 证明，`targetThreadId` 指向已验证 Luna 可见聊天，heartbeat 继承该聊天模型；不能在 prompt 或虚构 heartbeat `model` 字段里冒充配置。Luna 定时读取/观察，无变化不唤醒 Astra；有新证据才进入核实，随后仅按已授范围启用 Sol。发送前和等待恢复时核实 ACTIVE，已发但跟进失效只修调度不重发。用户叫停暂停本 run 实际任务并回读。报告范围、阶段/source/round、完整产物、未处理项、实际 owner/调度或 inline 限度。离线 PASS 不证明网页、模型、自动化、MCP、推送或发布已执行。
