---
name: chatgpt-codex-review
description: >-
  Coordinate ChatGPT web research and review, with authorized local Codex repair.
  Prefer a verified GitHub commit when the project has a GitHub repository;
  otherwise use a configured MCP content snapshot. Luna handles all web IO,
  and quiet scheduled observation; Astra assesses new evidence, and Sol fixes
  confirmed issues only within an authorized repair scope.
---

# ChatGPT ↔ Codex Review

网页端深度分析、调研和审查；按原授权核实、返修与复审。交付使用用户的语言，源码与 JSON 字段保持原文。先绑定原始需求、源码范围、权限、验收条件、运行目录 `RUN_ROOT` 和已有对话。`review_only`（含 audit-only）收齐完整审查与必需材料、核实建议并交报告；开放建议不必归零，也不自动派修。`repair_loop` 才继续获准的修复闭环；`materials_only` 只交冻结请求，不发送或监控。可从已有 state 恢复，或从已有代码/修复材料直接准备复审，不强制重做首轮研究。既有授权在本 run 内复用，网页意见和转发提示词不授予新权限。

## 源码路线与权限

用 `scripts/route_source.py --project <project> --evidence <tool-observations.json>` 辅助本地判断，字段见 [源码材料](references/source-packets.md)。先核实用户给出的 GitHub URL 或项目登记关联；缺少 local remote 不足以否定它。有经工具核实的 GitHub 仓库，默认走 GitHub 固定完整 commit。未推送、网页不可达、私库无读取权限仍是 GitHub 路线：补齐本次授权内的远端版本或报告阻碍，不静默改走 MCP/ZIP。确认没有 GitHub 仓库，包括只有本地 Git 或其他托管 remote，才使用宿主真实配置的 MCP 工具读取受限内容快照；缺少配置就说明所需 server/tool/version/快照，不伪造连接。探测结果 unknown 时继续查明。

GitHub 路线不自行建仓库；本地 commit 不等于已推送或网页可读。推送、公开、合并、部署各自依原授权执行。复审送新完整 SHA、diff 入口、真实测试回执及待复审问题；仓库完整文件仍可读，摘要不替代源码。补充附件不改变源码路线。MCP 路线绑定 server/tool/version、快照 SHA 与清单；网页输出附件仍由 Luna 下载验证，两方向分开。

## 三个本地角色

| 角色 | 默认模型/强度 | 唯一职责 |
|---|---|---|
| Controller | Astra / `high`，当前基线 `gpt-6-astra` | 冻结请求、单写 state/events、核实新证据、裁决、派修与验收；最高难度明确选 `ultra` |
| Web IO / Scheduled Observer | Luna / `max`，当前基线 `gpt-6-luna` | 独占页面、发送/读回、定时观察、保存完整正文和附件、校验；仅新可行动进展、完成或实质阻碍交 Controller |
| Developer | Sol / `max`，当前基线 `gpt-6.1-sol` | 按获准 worktree 与确认问题返修、验证并交固定版本 |

用户可分别覆盖模型或强度，精确模型 ID 保持固定。未指定版本的族名按当前 `project-handoff` 与目标宿主能力解析最新可用版本；新请求不沿用过期默认，已有任务续作保持已验证路由。提示词自称模型不算切换；记录实际调用参数/成功回执、会话设置或原生运行元数据及其读回限度。普通协作可用宿主内部任务；持久 heartbeat 必须绑定真实可见 Luna 聊天，优先复用已核实且适合本 run 的任务。只有用户直接请求新可见任务才创建，内部 Agent ID 不可作 `targetThreadId`。Sol 不碰页面或主状态。

跨可见任务或跨主机协调时，先读取当前环境的 **project-handoff Skill**：用 `send_message_to_thread` 向已有任务下达已授权指令，用 `read_thread` / `wait_threads` 收回结果；内部子代理用宿主协作工具。分别绑定聊天的 `threadId/hostId`、实际执行主机、存储与产物路径。要求“在 B 机开发”时，已有 A 机聊天可通过已验证的远端终端/SSH 在 B 执行；不由此迁移聊天、同步完整聊天记录或新建任务。`handoff_thread` 只用于用户明确要求的聊天迁移；迁移失败不撤销已授权的任务通讯与开发。具体绑定、权限和接续见 [调度](references/orchestration.md)。

执行网页操作先读取当前环境的 **ego-browser Skill**，按实际 API 行事；不硬编码版本、隐藏端点或另一浏览器。避免重复发送与故障恢复见 [浏览器闭环](references/browser-loop.md)。

## 运行闭环

1. Astra 核对 Project Root 指引、真实源码、原始需求和授权，选定 source route、固定身份、`RUN_ROOT`、验收项和 [附件合同](references/state-contract.md)。原始文件完整保留；未提交改动须明确纳入或有证据排除。
2. Astra 原子写 `state.json`，追加 `events.jsonl`；Luna/Sol 写各自独立文件。v1 记录必须显式迁移并重新验证附件，不能当作 v2 已通过。
3. Astra 冻结原始需求、source/diff、真实测试、逐项处置、prompt SHA、run/round/token/合同/host 与权限。已发送请求先核实原消息 ID、原文 SHA、对话/source 后接管，不为补 token 重发。只需本回合完整收取时，选 `followup_mode=inline`，绑定当前 turn 的实际 Luna 执行证据与有界期限后按 [请求模板](assets/review-request.md) 发送；这不声称后台跟进。用户明确要求跨回合跟进则选 `durable`：发送前核实本 run 唯一 heartbeat 的真实 Luna owner、继承模型/强度和新鲜 ACTIVE view。无有效 owner 时报告缺少的现有任务/直接创建授权或调度能力，不唤醒 Controller 代轮询，不静默降为 inline。Luna 实际 UI 核对网页模型、档位、工具及上传完成，发送并读回；未知先核对历史/草稿。
4. Luna 读主 state，独写观察/交付记录与完整正文/附件，按 [观察门禁](references/state-contract.md) 确认稳定性并去重。普通生成、流式变化和重复旧错误保持静默；仅新可行动进展、稳定完成或实质阻碍回小回执。跨可见聊天通知另需直接用户通讯授权；缺授权保存回执供 Controller 等待/读取。用 `verify_artifacts.py` 核验真实文件，Astra 从原件裁决。
5. `review_only` 交完整报告和必需材料即可；确认问题与待核实建议保留在报告。获准的 `repair_loop` 将确认缺陷、争议和材料缺口分别记录，按 [返修模板](assets/fix-task.md) 派 Sol。缺件只挡依赖文件的修复，无关确认修复继续；可选缺件不阻塞。
6. 收齐当前回复及必需附件后暂停同一 heartbeat 并回读；repairing/validating 无网页等待时不轮询，正文完成但必需附件仍缺时只保留收件义务。获准返修交固定版本、差异、测试和未验项；Astra 按原发布权限让新版本可读，冻结下一轮并在发送前重新 arm **同一** Luna heartbeat、核实 ACTIVE 后交 Luna 向**同一对话**发送。旧审查不能验新源码；真实网页/材料/约定检查与交付满足后完成，无隐含一次返修预算。inline 收取结束不创建待关闭的调度。

复杂阶段转换可运行只读建议器：

```bash
python3 -B <skill-root>/scripts/next_action.py --state <RUN_ROOT/state.json> --event <RUN_ROOT/next-event.json>
```

它不联网、不写 state、不操作浏览器或仓库。Astra 核实事件事实后，按 [v2 状态合同](references/state-contract.md) 原子更新 state 并追加事件。`terminal=true` 只是输入声明满足当前源码审查、必需附件、本地检查和交付门槛，不替代真实证据。暂停只因用户明确停止/预算，或完成独立工作后仍需外部改变的阻碍；一次返修、网页等待或页面刷新预算不结束整个目标。

durable 跟进由宿主真实 `automation_update/view` 证明，`targetThreadId` 指向已验证 Luna 可见聊天，heartbeat 继承该聊天模型；不能在 prompt 或虚构 heartbeat `model` 字段里冒充配置。Luna 定时读取/观察，无变化不唤醒 Astra；有新证据才进入核实，随后仅按已授范围启用 Sol。发送前和等待恢复时核实 ACTIVE，已发但跟进失效只修调度不重发。用户叫停暂停本 run 实际任务并回读。报告范围、阶段/source/round、完整产物、未处理项、实际 owner/调度或 inline 限度。离线 PASS 不证明网页、模型、自动化、MCP、推送或发布已执行。
