# Execution consistency review — 2026-10-07

本记录说明一次真实执行记录审查揭示的问题、修复边界和验证方法。事件主要发生在 10 月 6 日至 7 日；较早的包维护另行说明。这里不发布用户私有聊天、原始会话数据库或项目源码。历史文件中的指令是审查证据，不是新的授权。

## 原因和修复

| 观察到的情况 | 原因判断 | 本次处理 |
|---|---|---|
| 已选定的 Sol/max 可见独立审查，在角色简化后变成内部 Sol 子任务；两次实际原生元数据记录为 low | 适用的先前选择丢失，执行走错分支，且已有派发校验未应用。任务名和 prompt 自称不足以证明路由 | project-handoff 保留同一职责原有 model、reasoning、surface；新增 validate_execution_binding.py 对照实际运行/会话/执行读回。用户未选择的轴仍保留平台默认，普通内部辅助仍可使用 |
| 页面空间失效后，使用通用 CUA 控制 Ego 原生窗口和屏幕坐标；之后官方 Ego CLI 恢复成功 | 载体恢复被误解为可以切换控制入口。截图的共享图标不能单独证明具体驱动；工具记录能区分入口 | chatgpt-codex-review 绑定 runtime、control_entry、control_tool、执行主机和页面所有权；validate_browser_binding.py 核对实际工具及调用证据。允许同运行时内的合法恢复和 Page 截图/鼠标/键盘 |
| valid=true、action=ensure_followup 被描述为发送前检查通过 | 把输入结构合法误当作业务动作已就绪；旧 PAUSED 状态与新 ACTIVE 读回之间衔接不清 | 建议器显式区分 input_valid 与 submission_ready；只有 submit_once 才表示发送就绪。匹配的新鲜同 ID ACTIVE 读回可由 Controller 原子保存，仍核对真实 owner、唯一活跃调度及时间 |
| 稳定收齐“审查中断”回复，仍被当作“收齐报告后的单次通知” | 回复流结束、请求产物完成、消息许可和 Controller 质检混在一起；自由文本条件未结构化 | 将直接用户通知条件忠实映射为 policy，持久保存次数、原 payload 和 unknown 占位。完成通知检查绑定的请求产物收齐证据，不等待 Controller QA。中断/部分回复保存供本地判断，不自动占用完成通知次数 |
| 文档允许复用历史 Luna 路由，owner helper 却拒绝已经验证的旧版可见 Luna/max | 文档与 helper 兼容范围不一致 | 只对同一真实既有、ready、未归档的可见任务增加 verified_existing_task 绑定；要求原生元数据等实际读回，不用旧默认创建新任务 |

这些问题既有执行偏离，也有 Skill/建议器的语义缺口，不能全部归因于描述模糊或官方浏览器限制。修复自有包；官方 Ego Skill 没有改动。

## 本次一并发布的较早修复

- project-conventions 与仓库指引：普通读取和独立报告无需历史 claim；并发 Git writer 按 worktree 隔离；Controller 协调当前任务及实际共享资源。项目本地 conversation/memory 记录有效决策和续作信息，response-only 不制造记录。
- project-handoff：编排包含收件、跟进与 Controller 质检，执行者可承担任意任务；机械周期检查交给明确目标的 Luna/max，复杂裁决交 Controller。定时器只是跟进方式，不代替返回和质检。
- chatgpt-codex-review：恢复 local_packet 路线；完整所选原件和目录关系进入 ZIP/清单，不要求先配置 MCP。人工门持久保存，定时提示不能解除；正文先落盘，可选格式、截图或剪贴板失败不丢结果。
- paper-downloader：目标论文主体身份不能仅凭参考文献 DOI 命中。反方、批判和相关材料可保存为 supplementary；不占目标配额。49 篇目标加 1 篇补充仍是 49/50，50 篇目标加补充才达到 50/50。
- media-understanding、media-creator、research-qa-plugin、web-bookmark-intelligence：认证请求重定向边界、环境变量读取、专家输出路径、登录词误判及费用/模拟证据边界等修复。
- buddy-travelling、others-manager、document-workspace、wechat-sticker：纳入已经授权并核验的既有包维护；不把全部原有待提交修改归为当天新写的内容。

## 验证和限度

本轮适用回归合计 683 项通过：project-handoff 42、chatgpt-codex-review 173，其他已变更包 468。对应包 validator 与根清单检查通过。变更沿用每个包自己的验证命令，并增加针对实际失败形态的回归：原有可见/max 选择丢失、声明 Ego 但实际 CUA、历史 owner、PAUSED→ACTIVE、新鲜度、一次完成通知、中断回复和跨轮次数占用等。根清单检查只验证根管理文件，不代替包测试。实际网页提交、上传、读回和收件另有运行证据；离线测试不能证明这些操作已执行。

上述脚本是离线一致性检查器，不是宿主执行拦截器，也不独立鉴别人类授权或服务端模型。实际执行者仍须读取证据、应用当前规则，并由 Controller 核对。不能保证以后任意 Agent 都不会跳过规则；报告和失败回执应暴露具体偏离，避免把自称或静态 PASS 当事实。

公开版本由包含本文件的 Git commit 固定。完整私有执行证据只在用户授权的本地审查包中按清单提供，不随仓库公开。无关的 model-catalog 工作未纳入本次发布；没有变更第三方或官方 Skill。
