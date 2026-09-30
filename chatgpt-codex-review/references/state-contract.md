# v2 状态、附件与建议器

`next_action.py` 只读 JSON，输出建议动作和 `state_updates`；它不联网、不写 state、不核实 UI 真伪。Astra 是 `state.json` 唯一写入者：核对事件证据，写临时文件并同目录原子替换 state，再向 `events.jsonl` 追加该 run 的事件/动作/证据路径。Luna/Sol 只写各自回执文件；单 Controller 即可，不引入全项目 claim/锁。

v1 没有附件门槛，helper 明确拒绝 `schema_version=1`。迁移时读取旧事件与真实文件，建立新 v2 合同、重新验证并记录迁移来源；绝不把旧 PASS、旧附件状态或旧 round token 自动当已验。

## 最小 state

```json
{
  "schema_version": 2,
  "run_id": "example-run",
  "round": 1,
  "phase": "ready_to_submit",
  "execution_scope": "review_only",
  "followup_mode": "inline",
  "durable_followup_requested": false,
  "controller_thread_id": "observed-controller-thread",
  "controller_host": "observed-controller-host",
  "state_path": "/absolute/run/state.json",
  "source_route": "github",
  "source_id": "git:aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa",
  "source_binding": {"repository": "owner/project", "commit": "aaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaaa"},
  "source_binding_digest": "SHA-256-of-canonical-source-binding",
  "request_token": "example-run-r1",
  "used_request_tokens": ["example-run-r1"],
  "consumer_host": "observed-host-id",
  "artifact_root": "/absolute/run/artifacts",
  "artifact_contract": {"required": [], "optional": []},
  "contract_digest": "SHA-256-of-canonical-artifact-contract",
  "acceptance_contract": {"required_checks": ["local tests"], "delivery_items": ["review report"]},
  "acceptance_digest": "SHA-256-of-canonical-acceptance-contract",
  "conversation_url": null,
  "prepared_request": null,
  "followup": null,
  "web_io_binding": null,
  "inline_observer_binding": null,
  "controller_notification_authorization": null,
  "awaiting_send": false
}
```

示例值不可执行。`execution_scope` 取 `review_only/repair_loop/materials_only`，从原始用户要求绑定；旧 v2 缺省 repair_loop 是兼容值，恢复时仍须核对真实修复授权。review_only（包括 audit-only）允许网页发送/收取，完整报告可保留确认缺陷与未核实建议，不自动派修。materials_only 只交冻结请求。`followup_mode=inline` 只在当前 turn 有界收取；`durable` 要实际 Luna heartbeat。用户明确要求 durable 时保存 `durable_followup_requested=true`，helper 拒绝改 inline；旧 v2 缺省 durable，不把缺调度自动变成本回合模式。

已有 state 保留 phase 和原件；无 Skill 历史的已有修复可直接 ready_to_submit，不重做初轮研究或默认派 Sol。缺 Controller 绑定时用 `bind_controller` 补真实 thread/host/绝对 state_path。首条尚未发送可以 URL=null；已发送必须由 UI 读回实际 `/c/id`，不编造。prepared_request 和 followup 都只由 Controller 核实真实事件后写入。

durable 的 `web_io_binding` 为 `{surface:"visible_thread", ready:true, thread_id, host_id, model, reasoning, identity_readback_ref, model_readback_ref, reasoning_readback_ref, runtime_pair_verified:true, verified_at}`。默认是目标宿主核实的最新 Luna/max；精确用户覆盖需 `route_basis="explicit_user"` 与 `user_override_ref`。owner 不得等于 Controller、隐藏 Agent 或 queued clientThreadId。当前模型/强度可由显式 create_thread 参数和成功回执加已运行进展、真实会话设置或原生运行元数据绑定；read_thread 未暴露字段时如实说明证据限度，不以 prompt 自称代替，不伪称独立服务端核实。

inline 的 `inline_observer_binding` 为 `{surface:"internal_agent"|"current_turn", execution_ref, turn_id, model, reasoning, model_readback_ref, reasoning_readback_ref, runtime_pair_verified:true, verified_at, deadline_at}`，内部执行者另保存运行时真实 `agent_id`（不能把读回文件路径当 Agent 身份），默认 Luna/max，同样尊重显式覆盖；每个收发/观察事件带一致的 `inline_execution_ref/inline_turn_id` 和实际 observed_at。过期或换 turn 后由当前真实 Luna 执行证据更新绑定/期限，保持原模型/强度和业务，不要求用户配置后台；缺口返回 ensure_inline_luna，不声称有后台任务。此分支无需可见 owner 或 heartbeat，schedule_action 一律 none。

`source_route=github` 需要 `git:` 加完整 40/64 位小写 commit；其 `source_binding` 为经路由核实的 `repository` 和 `commit`。`mcp` 需要 `mcp:` 加 64 位内容快照 SHA，binding 为 route helper 返回的 `server`, `tool`, `version`, `snapshot_sha256`, `manifest_sha256`；`evidence_ref` 另存证据，不进 digest。三个 digest 均是各自对象的 UTF-8 JSON（sorted keys、紧凑分隔符、保留 Unicode）的 SHA-256。验收标准或内容访问工具变化会使旧 review/validation/delivery 失效。`artifact_root` 是本 run 的真实绝对目录。run 记录还应保存原始要求、scope、授权、角色实际 model/effort/任务 host、网页 space/page、调度回执与验收标准。

`artifact_contract.required` 与 `optional` 各列 `{name,kind,sha256?,size?}`；kind 为 `zip/png/json/utf8`。来源有可信预期 SHA/大小则填入，没有时只能声明本次接收计算的 SHA，不得说与原件一致。无附件要求时两个数组为空，附件门槛直接通过。输出附件可以是 Web 审查报告、图或日志；源码 route 不因此改变。`verify_artifacts.py` 只访问 `artifact_root` 内真实文件，检查字节数、SHA、类型与可读性；ZIP 检查 CRC、展开大小、symlink、穿越和路径别名；PNG 需 Pillow 完整解码。依赖缺失/格式无法验证产生 `unverified`，不是 PASS。不会执行附件代码。

Luna 的 `artifact_receipt` 保存完整 JSON 到独立文件，回 Astra 小回执：文件路径、回执 SHA、每项 status、`required_ready` 与异常。Astra 读原始回执及必要正文。建议器检查回执的 validator 标记、run/round/source/token/contract/consumer host/artifact_root 和必需文件状态；回执内容仍需由 Astra 核对真实文件。可选缺件不影响 `required_ready`。

## 事件和转换

所有事件均需与 state 完全一致的 `run_id`, `round`, `source_id`, `source_binding_digest`, `request_token`, `contract_digest`, `acceptance_digest`, `consumer_host`, `artifact_root`，加非空证据路径数组 `evidence`。仅有文件名不证明文件存在。v2 每轮 token 加入 `used_request_tokens`，新 token 不得与 run 中任何旧 token 重复。run/合同/host/source/工具绑定变化使旧审查与验收证据无效；附件还绑定 round/token/root。源码变化后新轮必须重新审查，并在 `validation` 事件提供新的 `next_source_binding`（来自 route helper/实际远端核查），使新源码的本地验证能在下一轮继续引用；同源补充消息也用新 token。

| type | 必需附加字段 | 建议器行为 |
|---|---|
| `bind_controller` | 实际 controller_thread_id、controller_host、绝对 state_path | 补绑定后按 inline/durable 选择核实对应观察能力 |
| `bind_web_io` | 真实 `web_io_binding` 的 ready visible Luna 身份与模型/强度证据 | 保存独立 Luna owner，要求该目标的真实调度回读；不创建任务 |
| `prepare_submission` | 保存的 review_request_path/prompt_sha256、原始需求/source 读回/检查/逐项处置引用与 materials_verified=true；只整理时 materials_only=true | 冻结请求不自动发送；materials_only 交文件，其他模式缺相应执行/调度绑定时报告具体缺口 |
| `followup_readback` | `followup` 为真实 heartbeat view 回执 | 记录本 run ACTIVE ID；不同 ID 仅在旧任务已删除/不存在的工具证据与替代 ACTIVE view 齐全时换绑 |
| `submission` | URL 可在首次 not_sent 为 null，status=sent/not_sent/unknown；sent 需 request_present、user_message_id、ui_model_verified、prompt_sha256 | 未发须冻结请求及所选模式门槛：durable 新鲜 ACTIVE view，inline 本 turn 实际执行绑定；已发失效只补观察不重发 |
| `adopt_submission` | 实际 URL、user message ID、原文 SHA/路径、源码身份及绑定 digest 的读回；无网页 token 时另记 `local_import_id` 且标明原文没有它 | 原请求绑定后接管观察，未知先 reconcile，绝不因本地导入而重发 |
| `observation` | URL、时区时间、UI 错误/生成状态、请求与新消息身份、正文长度/SHA/保存路径、完成控件 | 两次完整稳定观测相隔 ≥10 秒才 triage；变化正文的观察时间也不可倒退；普通空间故障返回恢复动作 |
| `browser_fault` | `reason_code=space_missing/space_closed/browser_crash/connection_failed` 与实际 evidence；若同时有真实 auth/user_control/permission_denied 则优先人类门 | 按原任务授权恢复本任务载体/原 URL；连续两次仍失败诊断，不直接 blocked 或重复索取许可 |
| `browser_recovered` | 同一 URL、实际 observed_at、old_space_id、browser_context={space_id,page_label,ownership:"agent"}、recovery_evidence_ref、request_status=present/absent/unknown；已发另核对原 user_message_id/prompt_sha256 与已知 assistant_message_id | 保存旧→新映射后继续原收件/发送门；未知/身份不符先 reconcile，不重发；actual 恢复才结束事故预算，不能绕过用户 pause/人类门 |
| `scheduled_observation` / `inline_observation` | 与 observation 同样的原始字段；durable 需新鲜 followup_view，inline 需 turn 执行绑定；错误需 error_fingerprint | Luna 独立去重/稳定性门禁，返回 observer_updates，主 state_updates 为空；无变化静默 |
| `scheduled_artifacts` / `inline_artifacts` | 当前绑定的完整 receipt 与时间、模式回读 | 必需缺件仅继续 capture；收齐后产生一次 artifact_receipt 小回执 |
| `observer_delivery` | notification_key、delivery_status=delivered/not_delivered/unknown/active_writer、实际 observed_at/delivery_evidence_ref、destination_thread_id/destination_host | 同 Controller 目的地的真实投递回执，仅写 Luna 独立记录；delivered 不等于 received |
| `notification_check` | 实际 observed_at 与模式执行/readback；可带 notification_key、delivery_readback=present/absent/unknown、destination_status=idle/active_writer/unknown | 只查收讫/投递，不开已收齐网页；非 unknown 的读回须目标匹配、readback_evidence_ref/readback_observed_at 新鲜且不早于上次投递 |
| `controller_received` | 已读 notification_key、notification_receipt_sha256 及真实读取 evidence | Controller 同次 state 更新记录收讫，不代替内容裁决/整合 |
| `web_progress` | 当前 URL/请求及 actionable_progress=true、actionable_progress_ref | Controller 核实新可行动证据，不误报完成或自动派修 |
| `artifact_receipt` | `receipt`（helper 原始 JSON） | 绑定且必需文件 ready 后解锁依赖文件的修复或继续验收 |
| `assessment` | review_message_id、coverage_complete；完整时 confirmed_findings、unresolved_claims、file_dependent_findings | review_only 保留问题后交报告；repair_loop 才派允许的确认修复，缺件仅挡依赖文件项 |
| `worker_result` | `candidate_source_id`, `delivery_path`；处理文件依赖项时 `addressed_file_findings` | 仅从 repairing 进入 validating；缺文件项仍保留，不因一次局部交付消失 |
| `validation` | `checked_source_id`, `passed`, `required_unverified`；需复审时新 token | repair_loop 失败继续返修；review_only 失败保留 validating/证据并 finish_delivery，报告验收未通过；源码变更送新网页轮次 |
| `delivery` | `delivered_source_id`, `complete` | 同一源码约定交付门槛 |
| `external_blocker` | `reason`, `attempts`, `requires_external_change`, `independent_work_remaining` | 普通空间丢失/崩溃转恢复；其余先完成独立工作，确需外部改变才 blocked |
| `pause` / `resume` | 用户停止/明确预算指令引用，或阻碍解除证据 | 保留同一 run 的恢复入口 |
| `followup_closed` | 同一 automation ID 的真实 PAUSED view，并传最新 Luna record | 采集和已排队收讫均闭合才继续；仍未收讫则恢复 Luna 跟进；用户停止/阻碍保存检查点，旧无调度不先建再关 |

`followup` 的真实 heartbeat view 回执保留 automation_id、ACTIVE/PAUSED、run_id、state_path、prompt_binding_verified、实际 cadence_minutes、checked_at、next_check_at、evidence_ref。增加 `owner_role="web_io"`、`owner_thread_id/target_thread_id/owner_host/owner_model/owner_reasoning`，均匹配 web_io_binding；`owner_model_readback_ref/owner_reasoning_readback_ref` 匹配其实际证据；另存 `controller_thread_id/controller_host`，不把 Controller 当 owner。宿主调用字段是 targetThreadId；这里只是归一化回执，model/effort 继承目标聊天，不能发明 heartbeat model 参数。

`browser_context` 只记录当前载体和恢复证据，不是服务端会话身份。先恢复可用的本任务空间，确认失效后重建并打开原 URL；没有 URL 的未发送首轮不伪造 URL。`browser_recovered` 核对已发原请求；尚未发送需真实 definitive_absence=true 才回原发送门，unknown 不允许补发。可在该事件带当前实际 inline_observer_binding 与匹配的执行/turn 字段续接过期窗口，不能仅在 prompt 自称新执行者。已保存正文/附件和未收讫原 payload/evidence 保留。`browser_recovery_attempts` 最多两次连续载体恢复，实际成功的 recovery_evidence_ref 才清零；换 turn/verified_at/读回路径不会清预算。旧 missing-space blocked 可用 browser_recovered，或带同等恢复字段的 resume 续保存阶段；真实 auth/user_control/permission_denied 门先实际解除并走正常 resume，清除 blocker_reason_code 后才允许后续普通恢复。显式用户暂停、inactive/unassigned 所有权和真正工具拒绝不可被失效标签遮盖。

以 `schedule_inventory_ref` 绑定本 run 全部实际调度的读取证据；`active_automation_ids` 在 ACTIVE 时必须仅含本 automation_id，PAUSED 时为空。默认建议 10 分钟，宿主实际节奏优先。ACTIVE 要下一次检查；PAUSED next_check_at=null。跨轮保留 ID，换绑需旧 ID 已删除/不存在的工具证据和替代 ACTIVE view。旧 Controller heartbeat 先用宿主工具暂停/删除并保存原始 readback，再迁移绑定并检查去重；不能假称旧 owner 是 Luna 才关它。

durable 发送前新鲜 view 必须在 10 分钟内，`awaiting_send=true` 保持准备→arm→send 的短窗口；正常发送后清零。已用于发送前验证的同一 view，可在有效窗内用于该 sent 读回。无 valid durable owner 返回 ensure_luna_owner，不能自动创建聊天或回退 Controller；有 owner 但调度无效返回 ensure_followup。已发消息/原文均保留，无真实刷新不消费预算。无网页/必需附件和排队收讫义务才 pause_if_active；进入下一轮发送前重新 arm 同一 ID。暂停仅针对本 run；项目级 watcher 仍有开发/构建等待时只解除网页子义务，不关整个 watcher。返回 schedule_action 是建议，仍需实际工具回读。

Luna 执行只读 CLI `next_action.py --state <state> --event <observation> --observer-record <Luna-record>`，将 observer_updates 保存到本轮独立文件；不改 state/events。Controller 处理结果或关闭跟进也传入本 run 最新 Luna record，只有 Controller 更新主 state/events。业务绑定 run/source/round/token/合同/host/对话/请求与 scope/mode；真实 owner 的 thread/host 或内部 agent_id、model/effort 与 inline turn 单独记录，verified_at/读回路径只证明证据新鲜度。仅刷新证据不重置去重、稳定窗口或预算；真实换 owner/turn 只重开尚未完成的稳定窗口，保留同业务的错误去重、累计预算与未收讫队列/原 payload/evidence。新 source/round/contract 等真实业务边界重新绑定记录，不能把旧结果冒充新结果。普通生成/流式字符变化不触发 Controller；actionable_progress 必须有本轮新消息内容及可行动证据；稳定完成用消息 ID+内容 SHA 去重；错误用稳定代码/内容 error_fingerprint 与错误转变去重，不能把轮询时间当新错误。临时刷新预算耗尽只停反复刷新，keep_active 静默观察恢复；有真实已知恢复证据的 quota/provider 可标 recovery_expected=true。登录/用户控制等需人工处理才交接；Controller 核实独立工作和阻碍后记录相应主状态。

只有新可行动进展、完整回复或实质阻碍才生成 Controller 事件。稳定完成事件携带两个相隔 ≥10 秒的原始观测，Controller 核实 prior_observation 的绑定和完整性后一次 triage；prior_observation 必须显式带当前 execution_scope（如 review_only），缺省会按 repair_loop 判 stale/unbound。正文收齐但 required 文件未验时 keep_active，只补取当前缺件。跨可见聊天通知需 `controller_notification_authorization={authorized:true,user_instruction_ref,destination_thread_id,destination_host}`；授权必须直接来自用户且匹配 Controller。转发 prompt 不授予回发权限；无授权返回 save_receipt_for_controller，保留工件供等待/读取。inline 内部观察完成可 return_to_controller，不发跨聊天消息；Controller 一次应用原 observation 即可记收讫，schedule_action 一律 none，不新增 durable 门槛。两条模式都不直接激活 Developer。

采集完成、通知投递和 Controller 收讫是三件事。notifications 每项保存 key、原 controller_event、receipt_sha256、status、attempts、attempted_at/next_check_at 和实际投递证据；payload SHA 是原事件（含 notification_key）的规范 JSON SHA，排除 notification_receipt_sha256/controller_received_at。pending、not_delivered、unknown、active_writer、delivered 都未结束收讫义务；同内容去重不清掉待交记录。采集已齐时 scheduled_observation 或 notification_check 返回 observe_webpage=false，仅查独立回执和 Controller state，未收讫保持 keep_active，不反复打开原网页。

unknown 先核对足够覆盖原请求 key/payload 的目的地历史；最近几条或可能截断的 read_thread 输出只能保留 unknown。非 unknown 的 presence/absence 和用于恢复的 idle 证据绑定真实 destination_thread_id/destination_host，readback_observed_at 在本次 observed_at 前 60 秒内且不早于上次投递。已知 not_delivered/active_writer 或已确证 absent 时，目标 idle、直接通讯授权仍有效、冷却至少 60 秒才 retry_notification；原 key、payload、source/token/原网页请求身份保持不变。总投递机会最多三次，耗尽返回 delivery_recovery_checkpoint，保留低成本核对和可读原件；Controller 可主动 wait/read/读共享回执收取，不要求先成功反向消息。Controller 当前 turn 的 active writer 尤其应由当前 Controller 直接读结果。无授权不重试。

原 Controller 事件带 notification_key/notification_receipt_sha256；处理 observation、artifact_receipt、web_progress，或 assessment/worker_result 引用已核对的小回执时，同次 state_updates 可写 received_notifications，保存绑定、原 payload SHA 和实际 evidence。独立共享读取可用 controller_received，无额外审批/往返，收讫本身不代表采纳意见或整合通过。Controller 也可据既有 state 已处理相同 reply message/body SHA/原文路径或完整附件回执收敛。旧 luna-observer/v1 通知项仅有 key/status/evidence 时，核对其顶层 completion_observation 与当前 state 的同一绑定/消息/SHA/路径；不能确认的保留待核对，不伪造旧 payload/新回执，不把旧已处理 run 重挂。用户停止/已确认阻碍可暂停并保存未收讫 payload，恢复后核实原 Luna ACTIVE 继续核对。

repair_loop 的 assessment 确认问题与争议并存时先派独立确认修复；file_dependent_findings 在 required 文件存在时必须明确，dispatchable/pending 分开。新当前文件交同一个 Sol 继续，不建重叠 writer；局部交付不清空 pending，处理后明确 addressed_file_findings，未闭合不能下一轮。worker 不可换 GitHub/MCP 路线。repair_loop completed 要 clean 当前 review、当前 required 附件、绑定本地检查与交付；review_only 要完整 coverage、当前 required 附件和报告交付，开放建议保留，只有验收合同明确要求的检查才需 validation。review_only passed=false 保留当前失败证据与 required_unverified，在 validating 交报告；可 terminal=true 结束报告义务，但 acceptance_passed=false，不能宣称检查通过或派修。scope 变化使旧审查/交付记录失效。无隐含一次返修预算。

`next_action.py` 的 `valid=false`/退出码 2 表示旧版本、字段缺失、错轮次/来源/合同/host 或非法转换。退出码 0 仅表示建议计算成功，不证明输入事实或整个 run 完成。浏览器最多三次有退避的连续错误刷新是页面恢复预算，跟修复轮数无关；正常生成不刷新，发送未知不重发。
