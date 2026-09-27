# 角色调度与持续复审

Astra Controller 单写 `RUN_ROOT/state.json` 和 `events.jsonl`，核实 Luna 原始网页证据与 Sol 交付。Luna max 是唯一页面操作者：接入/创建获准的原对话、模型 UI 核对、上传、发送、读回、防重发、观察、真实下载和文件核验都在同一角色内。Sol max 只在指定 worktree 修复，不能操作网页或主状态。默认模型分别为 `gpt-6-astra/max`、`gpt-6-luna/max`、`gpt-6-sol/max`；各自可被用户单独覆盖。用当前宿主真实工具字段与回执核实实际执行者，不因提示词写着某模型就冒充已切换。

普通执行用宿主内部协作，只有用户明确要求新可见任务才创建。复用已有 Luna 与 Sol 任务和同一浏览器 TaskSpace；替换故障任务前保存产物、未完成项与实际身份。非 Astra 当前任务应把控制委派给可用的 Astra 角色，或记录实际 Controller 与模型能力缺口，不自称已切换。

`RUN_ROOT` 至少保存：原始需求、权限/披露范围、验收合同、source route 及证据、state/events、每轮冻结 prompt、Luna 完整正文/附件/观测与小回执、Astra 逐项裁决、Sol 固定交付和本地检查。文件按 run/round 命名，不覆盖旧轮。Astra 用同目录临时文件原子替换 state，再追加事件；Luna/Sol 不追加主事件流。压缩上下文后先读取实际 state、当前 round 和原始资料。

已有本 Skill state 时按真实 phase、事件及原件恢复，不把旧回执当新事实。若已有代码/修复记录而没有本 Skill 历史，Astra 核实原始要求、现有源码/diff、逐项处置与实际测试后建立本 run，可直接 `ready_to_submit` 并发出 `prepare_submission`；缺失或失效的检查才补跑，不强行从初次研究或 Sol 返修开始。Astra 主笔并保存 review-request，明确原始需求、上轮逐项处置、新固定源码/diff、真实测试、待复审点及未验项；Sol 交改动和检查证据，Luna 只按冻结原文收发，不自行改写判断。用户明确只要材料时，准备后停在交付，不由准备动作自动发送。已在网页发送的旧请求须由 Luna 核对真实对话、user message ID、原文 SHA、source 读回，再由 Astra 记录 `adopt_submission`；网页原文没有 token 时，本地导入标识与网页原文分开记。绑定不清先 reconcile，不能为接管而重发。

Astra 给 Luna 的输入是冻结的 run/round/source/token、prompt SHA、合同 digest、consumer host、精确网页对话和文件清单、实际权限。Luna 的常态回执只含状态、原文/附件路径、字节数/SHA、下载验证状态、消息 ID 与异常；正文和页面快照不反复粘给 Astra。Astra 必要时读原文件裁决，不把 Luna 总结当完整审查。新一轮沿用已核准的路由、模型和权限；只有身份/范围/权限变化才复核。GitHub 复审用新完整 SHA、diff 入口、测试回执、待复审点，完整源码仍可取；Luna 不重传整个源码 ZIP。

完整回复后，Astra 将发现分成确认缺陷、待裁决主张、已证据反驳、范围外建议和必需未验项。若必需附件缺失，先推进与文件无关的确认修复及文本核实；`pending_file_findings` 保留待处理数量。Luna 在 repairing/validating 期间补取文件后，Astra把当前验证回执交给同一个 Sol 继续，不创建重叠 writer；局部 worker 交付不消除缺件义务。Sol 的输入含精确写入范围、原始需求、确认问题和依赖附件、完成标准；文件依赖项完成时明确计入 `addressed_file_findings`。每次返修交固定新身份/差异/检查记录。一次 worker 完成只进入本地验证，失败继续诊断与返修；没有默认一次反馈预算。网页意见不授权需求扩大或外部写入。

即时监测用宿主协作等待；普通等待/sleep 不是跨回合定时。跨回合先查并复用本 run 的 `automation_update` heartbeat，默认建议每 5 分钟，若宿主只支持其他节奏则记录真实节奏。Controller 用真实工具创建或更新，然后 `view` 回读，记录 automation ID、`ACTIVE`、owner thread/host、run ID、state 绝对路径、prompt 绑定、周期、下次检查与证据；提示词写“定时”不算创建。首条网页消息发送前可以还没有 `/c/id`，heartbeat 先绑定 run/state/owner，发送后补记真实对话 URL。每次发送前和跨回合恢复时重新核实 ACTIVE；已发送但缺或暂停的跟进优先补建/恢复，保留原消息，不重发。正常情况跨轮复用同一 ID；旧 ID 经工具证据确认不存在或已删除时，记录旧 ID、失败证据与替代 ID 的 ACTIVE view，才可换绑。不为每轮造新任务，不用 raw cron 或假脚本代替。内部子代理不自动拥有独立可见 thread；heartbeat 唤醒的是 Controller，再委派 Luna max，不能宣称纯 Luna 常驻或免费唤醒。

每次 heartbeat 唤醒先读 state：`waiting_web` 才派 Luna 观察；完整正文/附件交 Astra 核实后，按授权继续 Sol 修复与下一轮复审。无变化静默，不重复发送或逐次通知。临时失败保留原安排及 URL/space/page 恢复入口；模型/host 绑定不可验证时只做本 turn 有界观察并报告能力缺口。用户叫停或整体验收完成时暂停**本 run 已存在的** heartbeat，再 `view` 读回 `PAUSED`；暂停状态不需伪造下次检查时间。旧工作已收齐且无调度时直接验收，不为了关闭而新建一个任务。真正的定时任务创建/回读必须在运行时执行，本包离线测试只能验证回执决策。

最后门槛：最新源码的完整网页审查及所需附件已验；确认缺陷与待裁决主张为零；同一验收合同下本地必需检查和交付完成。测试宿主错误不冒充产品缺陷，网页测试不冒充原生/设备检查。新源码或合同变更使旧证据失效。发布、合并和安装仍按原授权；未获推送许可时保留本地成果，不改走 MCP，也不用旧远端版本冒充复审。
