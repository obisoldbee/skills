---
name: chatgpt-codex-review
description: >-
  Coordinate iterative ChatGPT web research and review with local Codex repair.
  Prefer a verified GitHub commit when the project has a GitHub repository;
  otherwise use a configured MCP content snapshot. Luna handles all web IO,
  Astra controls the run, and Sol fixes confirmed issues until acceptance.
---

# ChatGPT ↔ Codex Review

网页端深度分析、调研和审查；本地核实、修复、复审，直到约定验收项真正闭合。可以从已有 state 恢复，也可以在已有代码/修复记录但没有本 Skill 历史时，直接从 Astra 整理复审请求开始；不强制重做首轮研究或派 Sol。默认继续已授权闭环；用户明确要求“只整理、不发送”时，交付冻结材料，不发起网页提交、监控或代码返修。执行闭环时，先绑定原始需求、源码范围、权限、验收条件、运行记录目录 `RUN_ROOT` 和已有对话；已有授权在本 run 内复用，事实变化才重新核查。

## 源码路线与权限

用 `scripts/route_source.py --project <project> --evidence <tool-observations.json>` 辅助本地判断，字段见 [源码材料](references/source-packets.md)。先核实用户给出的 GitHub URL 或项目登记关联；缺少 local remote 不足以否定它。有经工具核实的 GitHub 仓库，默认走 GitHub 固定完整 commit。未推送、网页不可达、私库无读取权限仍是 GitHub 路线：补齐本次授权内的远端版本或报告阻碍，不静默改走 MCP/ZIP。确认没有 GitHub 仓库，包括只有本地 Git 或其他托管 remote，才使用宿主真实配置的 MCP 工具读取受限内容快照；缺少配置就说明所需 server/tool/version/快照，不伪造连接。探测结果 unknown 时继续查明。

GitHub 路线不自行建仓库；本地 commit 不等于已推送或网页可读。推送、公开、合并、部署各自依原授权执行。复审送新完整 SHA、diff 入口、真实测试回执及待复审问题；仓库完整文件仍可读，摘要不替代源码。补充附件不改变源码路线。MCP 路线绑定 server/tool/version、快照 SHA 与清单；网页输出附件仍由 Luna 下载验证，两方向分开。

## 三个本地角色

| 角色 | 默认模型/强度 | 唯一职责 |
|---|---|---|
| Controller | `gpt-6-astra` / `max` | 核实原始要求与每轮证据、冻结请求、单写 state/events、裁决缺陷、派修与验收 |
| Web IO | `gpt-6-luna` / `max` | 独占同一 ego-browser 页面，创建/接入授权对话、核对网页模型、发送并读回、观察、下载保存与校验、写回执 |
| Developer | `gpt-6-sol` / `max` | 在获准 worktree 修复已确认问题，运行本地检查，交固定版本与证据 |

用户可分别覆盖每个角色的模型或强度；未覆盖者保持默认，不静默降级。实际工具回执决定执行者，当前非 Astra 任务不能自称已经切换成 Astra；无法按指定角色路由时如实记录并交给有能力的 Controller。只在用户明确要新的可见任务时创建；普通闭环使用宿主允许的内部协作。Luna 是单一页面操作者，Sol 不碰页面或主状态。网页 ChatGPT 的意见是待核实输入，不授予新权限。

执行网页操作先读取当前环境的 **ego-browser Skill**，按实际 API 行事；不硬编码版本、隐藏端点或另一浏览器。角色路由与跨回合接续见 [调度](references/orchestration.md)，避免重复发送与故障恢复见 [浏览器闭环](references/browser-loop.md)。

## 运行闭环

1. Astra 核对 Project Root 指引、真实源码、原始需求和授权，选定 source route、固定身份、`RUN_ROOT`、验收项和 [附件合同](references/state-contract.md)。原始文件完整保留；未提交改动须明确纳入或有证据排除。
2. Astra 原子写 `state.json`，追加 `events.jsonl`；Luna/Sol 写各自独立文件。v1 记录必须显式迁移并重新验证附件，不能当作 v2 已通过。
3. Astra 根据原始需求、上轮逐项处置、新固定源码/diff、真实测试和待复审点主笔并保存请求；Sol 只交改动与测试证据，Luna 不改写裁决。Astra 冻结 prompt SHA、run/round/source/token/合同/host、文件清单和权限。已发请求先核实原消息 ID、原文 SHA、对话及 source 后接管观察，不为补 token 重发。未发请求先创建或复用本 run 的真实 heartbeat 并读回 ACTIVE，再按 [请求模板](assets/review-request.md) 派 Luna 发送；默认继续已授权闭环，仅用户明确只整理时停在材料交付。Luna 接入或创建已授权对话，实际 UI 核对用户指定的网页模型、思考档位、搜索等工具与上传完成，发送并读回本轮用户消息；结果不明先核对历史与草稿，不能盲目重发。
4. Luna 持续观察本轮新回复，完整正文与附件写入 `RUN_ROOT`，用 `scripts/verify_artifacts.py --input <receipt-input.json>` 核验。仅回传状态、路径、SHA、附件就绪/缺失和异常的小回执；Astra 从原始文件核实，不让摘要冒充完整回复。
5. Astra 将确认缺陷、待裁决主张、材料缺口分别记录。必需附件缺失时，文件依赖的修复等候；无关的确认修复和文本核实继续。可选附件缺失不阻塞。按 [返修模板](assets/fix-task.md) 派 Sol，同一开发任务可多轮继续。
6. Sol 交固定新版本、差异、测试和未验项。Astra 本地验收后，按本 run 原有发布权限让新版本可被网页读取，再主笔新轮复审请求、核实 heartbeat 仍 ACTIVE，令 Luna 向**同一对话**发送。代码改变使旧审查失效。网页、文件、测试的实际读回都满足后，关闭本 run 的真实定时任务并读回，再完成；没有隐含一次返修预算。

复杂阶段转换可运行只读建议器：

```bash
python3 -B <skill-root>/scripts/next_action.py --state <RUN_ROOT/state.json> --event <RUN_ROOT/next-event.json>
```

它不联网、不写 state、不操作浏览器或仓库。Astra 核实事件事实后，按 [v2 状态合同](references/state-contract.md) 原子更新 state 并追加事件。`terminal=true` 只是输入声明满足当前源码审查、必需附件、本地检查和交付门槛，不替代真实证据。暂停只因用户明确停止/预算，或完成独立工作后仍需外部改变的阻碍；一次返修、网页等待或页面刷新预算不结束整个目标。

跨回合跟进须由宿主 `automation_update` heartbeat 的真实创建/复用及 `view` 回读证明；Controller 被唤醒后先读 state，再委派 Luna max 观察，未变化保持静默。每次发送前和恢复时重新核实 ACTIVE；已发送但跟进失效只补跟进，不重发。用户叫停时也关闭本 run 的实际调度并读回。报告当前阶段与 source/round、网页审查和本地验证各自结论、真实产物路径、未处理项、实际 watcher/heartbeat 身份或恢复入口。静态测试不证明真实网页发送、定时创建、MCP 接通、推送或发布。
