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
  "followup_mode": "durable",
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
  "artifact_receipt": null,
  "artifact_observation": null,
  "awaiting_send": false
}
```

示例值不可执行。`execution_scope` 取 `review_only/repair_loop/materials_only`，从原始用户要求绑定；旧 v2 缺省 repair_loop 是兼容值，恢复时仍须核对真实修复授权。review_only（包括 audit-only）允许网页发送/收取，完整报告可保留确认缺陷与未核实建议，不自动派修。materials_only 只交冻结请求。新网页调研/深度 review 默认 `followup_mode=durable`，要实际 Luna heartbeat 与可执行收件返回入口；用户没说“跨回合”不构成 inline 依据。`followup_mode=inline` 只用于已生成完整回复的短时收取或用户直接限定仅本回合。用户明确要求 durable 时保存 `durable_followup_requested=true`，helper 拒绝改 inline；旧 v2 缺省 durable，不把缺调度自动变成本回合模式。把旧缺省显式补成相同 repair_loop/durable 只确认原语义，保留 ledger 原 binding/key/payload/SHA/状态与预算；真正 scope/mode 改变仍是新业务边界，不能重写旧结果冒充新结果。

已有 state 保留 phase 和原件；无 Skill 历史的已有修复可直接 ready_to_submit，不重做初轮研究或默认派 Sol。缺 Controller 绑定时用 `bind_controller` 补真实 thread/host/绝对 state_path。首条尚未发送可以 URL=null；已发送必须由 UI 读回实际 `/c/id`，不编造。prepared_request 和 followup 都只由 Controller 核实真实事件后写入。

durable 的 `web_io_binding` 为 `{surface:"visible_thread", ready:true, thread_id, host_id, model, reasoning, identity_readback_ref, model_readback_ref, reasoning_readback_ref, runtime_pair_verified:true, verified_at}`。默认是目标宿主核实的最新 Luna/max；精确用户覆盖需 `route_basis="explicit_user"` 与 `user_override_ref`。owner 不得等于 Controller、隐藏 Agent 或 queued clientThreadId。当前模型/强度可由显式 create_thread 参数和成功回执加已运行进展、真实会话设置或原生运行元数据绑定；read_thread 未暴露字段时如实说明证据限度，不以 prompt 自称代替，不伪称独立服务端核实。

已核实的历史 `gpt-5.6-luna/max` 可保留 `route_basis="verified_existing_task"`，增加 `existing_task_readback={operation:"reuse_existing",metadata_source:"runtime_metadata"|"session_settings"|"task_tool_readback",thread_id,host_id,model,reasoning,ready:true,archived:false,agent_path:null,evidence_ref,observed_at}`，各身份/模型字段与 binding 相符、observed_at 等于 verified_at。证据须来自原生元数据/真实会话设置/包含实际字段的任务读回，不能只引用自称 Luna 的问候或请求参数。此兼容只复用同一已存在可见任务，不支持内部 owner、初始旧模型自动创建或替代新任务。

`followup_check` 的 durable 就绪还检查返回入口：已有 `controller_notification_authorization` 绑定直接用户通讯授权与正确 Controller；否则 `controller_result_return={kind:"native_completion_event"|"verified_dispatcher",verified:true,evidence_ref,destination_thread_id,destination_host}` 必须来自宿主实际唤醒/投递证据并匹配 Controller。它是证据归一化字段，不是新工具或可假定存在的能力；只有共享文件、内部 Agent ID、计划以后读取或不匹配的目的地，均返回 ensure_result_return。未取得所缺通讯授权时不得伪填 true。

inline 还须 `inline_policy={basis:"explicit_user",user_instruction_ref}`，或 `{basis:"capture_existing_reply",complete_reply_observed:true,reply_readback_ref}` 且 state 已绑定真实 submitted_user_message_id。前者来自用户直接限定仅本回合的原文；后者须真实完整回复证据。内部 Luna 存在、用户未提定时、估计能等到或缺 owner 均不算依据；没有有效 policy，helper 返回 ensure_durable_followup。

inline 的 `inline_observer_binding` 为 `{surface:"internal_agent"|"current_turn", execution_ref, turn_id, model, reasoning, model_readback_ref, reasoning_readback_ref, runtime_pair_verified:true, verified_at, deadline_at}`，内部执行者另保存运行时真实 `agent_id`（不能把读回文件路径当 Agent 身份），默认 Luna/max，同样尊重显式覆盖；每个收发/观察事件带一致的 `inline_execution_ref/inline_turn_id` 和实际 observed_at。仅仍属于上述 inline 例外时，可用真实执行证据更新过期绑定；准备结束回合或收取超出期限时先运行 followup_check，不能靠续期限无限等待。缺执行证据返回 ensure_inline_luna；普通未完成收取返回 ensure_durable_followup，按调度合同接续。此分支无需可见 owner 或 heartbeat，schedule_action 一律 none。

`source_route=github` 需要 `git:` 加完整 40/64 位小写 commit；其 `source_binding` 为经路由核实的 `repository` 和 `commit`。`mcp` 需要 `mcp:` 加 64 位内容快照 SHA，binding 为 route helper 返回的 `server`, `tool`, `version`, `snapshot_sha256`, `manifest_sha256`；`local_packet` 需要 `packet:` 加 ZIP 的 SHA-256，binding 精确为 `archive_sha256`、`manifest_sha256`，由 local_packet.py/route_source.py 实际读回产生；包路径、清单路径、上传与读取证据另存。`evidence_ref` 另存证据，不进 digest。三个 digest 均是各自对象的 UTF-8 JSON（sorted keys、紧凑分隔符、保留 Unicode）的 SHA-256。验收标准或内容访问工具变化会使旧 review/validation/delivery 失效。`artifact_root` 是本 run 的真实绝对目录。run 记录还应保存原始要求、scope、授权、角色实际 model/effort/任务 host、网页 space/page、调度回执与验收标准。

`artifact_contract.required` 与 `optional` 各列 `{name,kind,sha256?,size?}`；kind 为 `zip/png/json/utf8`。来源有可信预期 SHA/大小则填入，没有时只能声明本次接收计算的 SHA，不得说与原件一致。无附件要求时两个数组为空，附件门槛直接通过。输出附件可以是 Web 审查报告、图或日志；源码 route 不因此改变。`verify_artifacts.py` 只访问 `artifact_root` 内真实文件，检查字节数、SHA、类型与可读性；ZIP 检查 CRC、展开大小、symlink、穿越和路径别名；PNG 需 Pillow 完整解码。依赖缺失/格式无法验证产生 `unverified`，不是 PASS。不会执行附件代码。

Luna 的 `artifact_receipt` 保存完整 JSON 到独立文件，回 Astra 小回执：文件路径、回执 SHA、每项 status、`required_ready` 与异常。Astra 读原始回执及必要正文。建议器检查回执的 validator 标记、run/round/source/token/contract/consumer host/artifact_root 和必需文件状态；回执内容仍需由 Astra 核对真实文件。可选缺件不影响 `required_ready`。

## 事件和转换

所有事件均需与 state 完全一致的 `run_id`, `round`, `source_id`, `source_binding_digest`, `request_token`, `contract_digest`, `acceptance_digest`, `consumer_host`, `artifact_root`，加非空证据路径数组 `evidence`。原通知及 `web_progress` 保留原 `execution_scope/followup_mode`；旧缺省 repair_loop/durable 可按相同默认处理，真正变化不能重绑旧事件，须在写收讫前拒绝。仅有文件名不证明文件存在。v2 每轮 token 加入 `used_request_tokens`，新 token 不得与 run 中任何旧 token 重复。run/合同/host/source/工具绑定变化使旧审查与验收证据无效；附件还绑定 round/token/root。源码变化后新轮必须重新审查，并在 `validation` 事件提供新的 `next_source_binding`（来自 route helper/实际远端核查），使新源码的本地验证能在下一轮继续引用；同源补充消息也用新 token。

| type | 必需附加字段 | 建议器行为 |
|---|---|
| `followup_check` | `checkpoint=before_submit/turn_end/inline_deadline`、实际 observed_at；durable 带新鲜 followup_view，并传最新 observer record | 发送前/回合结束/期限到核对未闭合收件：默认要求真实 Luna 持久跟进；缺口非 terminal，不改已发请求或旧 ledger；正文/文件已齐但未收讫先 receive_saved_result 原样收回，不为收现成结果新建调度；用户明确仅本回合才 report_inline_checkpoint；已收齐继续本地质检 |
| `bind_controller` | 实际 controller_thread_id、controller_host、绝对 state_path | 补绑定后按 inline/durable 选择核实对应观察能力 |
| `bind_web_io` | 真实 `web_io_binding` 的 ready visible Luna 身份与模型/强度证据 | 保存独立 Luna owner，要求该目标的真实调度回读；不创建任务 |
| `prepare_submission` | 保存的 review_request_path/prompt_sha256、原始需求/source 读回/检查/逐项处置引用与 materials_verified=true；只整理时 materials_only=true | 冻结请求不自动发送；materials_only 交文件，其他模式缺相应执行/调度绑定时报告具体缺口 |
| `followup_readback` | `followup` 为真实 heartbeat view 回执 | 记录本 run ACTIVE ID；不同 ID 仅在旧任务已删除/不存在的工具证据与替代 ACTIVE view 齐全时换绑 |
| `submission` | URL 可在首次 not_sent 为 null，status=sent/not_sent/unknown；sent 需 request_present、user_message_id、ui_model_verified、prompt_sha256 | 未发须冻结请求及所选模式门槛：durable 新鲜 ACTIVE view，inline 本 turn 实际执行绑定；已发失效只补观察不重发 |
| `adopt_submission` | 实际 URL、user message ID、原文 SHA/路径、源码身份及绑定 digest 的读回；无网页 token 时另记 `local_import_id` 且标明原文没有它 | 原请求绑定后接管观察，未知先 reconcile，绝不因本地导入而重发 |
| `observation` | URL、时区时间、UI 错误/生成状态、请求与新消息身份、正文长度/SHA/保存路径、完成控件 | waiting_web 两次完整稳定观测相隔 ≥10 秒才 triage；review_ready/repairing/validating 的必需补件也先分类故障/人类门/临时退避，保留原阶段与正文；无错误才正常补件 |
| `browser_fault` | `reason_code=space_missing/space_closed/browser_crash/connection_failed`、实际 observed_at 与 evidence；若同时有真实 auth/user_control/permission_denied 则优先人类门 | 按原任务授权恢复本任务载体/原 URL；连续两次仍失败诊断，不直接 blocked 或重复索取许可 |
| `browser_driver_check` | 当前 `browser_actual` 的真实入口/工具调用/所有权证据；首个已核实绑定另带 `browser_execution_binding` | 核对并保存所选 runtime/control entry/tool/主机/target；错驱动或缺证据只 reload_browser_binding，不改旧绑定/权限，不阻断本地收件/QA |
| `browser_recovered` | 同一 URL、实际 observed_at、old_space_id、browser_context={space_id,page_label,ownership:"agent"}、recovery_evidence_ref、request_status=present/absent/unknown；已发另核对原 user_message_id/prompt_sha256 与已知 assistant_message_id | 保存旧→新映射后继续原收件/发送门；未知/身份不符先 reconcile，不重发；actual 恢复才结束事故预算，不能绕过用户 pause/人类门 |
| `scheduled_observation` / `inline_observation` | 与 observation 同样的原始字段；durable 需新鲜 followup_view，inline 需 turn 执行绑定；错误需 error_fingerprint | Luna 独立去重/稳定性门禁，返回 observer_updates，主 state_updates 为空；无变化静默 |
| `scheduled_artifacts` / `inline_artifacts` | 当前绑定的完整 receipt 与时间、模式回读 | 保存最新实际附件观测与 SHA；必需缺件仅继续 capture，收齐后产生一次 artifact_receipt 小回执；文件重验失败覆盖旧 ready |
| `observer_delivery` | notification_key、实际 attempt_id、delivery_status=delivered/not_delivered/unknown/active_writer、实际 observed_at/delivery_evidence_ref、destination_thread_id/destination_host | 同 Controller 目的地的真实投递回执，仅写 Luna 独立记录；delivered 不等于 received |
| `notification_check` | 实际 observed_at 与模式执行/readback；可带 notification_key、delivery_readback=present/absent/unknown、destination_status=idle/active_writer/unknown、write_endpoint_recovery；稍晚完成的 requested_output_collection 另绑定原 notification_key/notification_receipt_sha256 | 只查收讫/投递，不开已收齐网页；非 unknown 读回及写入口恢复须目标匹配、新鲜且不早于上次投递；idle 不证明可以重发 |
| `controller_received` | 已读 notification_key、notification_receipt_sha256 及真实读取 evidence；传最新 Luna record | 同次记收讫；采集已闭合且原事件尚未处理时 process_saved_result 返回原 payload 供 Controller 本地应用，不能以再启表代替处理 |
| `web_progress` | 当前 URL/请求、原 execution_scope/followup_mode 及 actionable_progress=true、actionable_progress_ref | Controller 核实新可行动证据，真 scope/mode 变化拒绝旧事件，不误报完成或自动派修 |
| `artifact_receipt` | `receipt`（helper 原始 JSON）、本次真实校验后的 observed_at 与证据 | 保存主 state 当前证明；与最新 Luna 证明一致且必需快照已应用才解锁文件依赖步骤；旧无时间回执不覆盖新证明 |
| `assessment` | review_message_id、coverage_complete；完整时 confirmed_findings、unresolved_claims、file_dependent_findings | review_only 保留问题后交报告；repair_loop 才派允许的确认修复，缺件仅挡依赖文件项 |
| `worker_result` | `candidate_source_id`, `delivery_path`；处理文件依赖项时 `addressed_file_findings` | 仅从 repairing 进入 validating；缺文件项仍保留，不因一次局部交付消失 |
| `validation` | `checked_source_id`, `passed`, `required_unverified`；需复审时新 token | repair_loop 失败继续返修；review_only 失败保留 validating/证据并 finish_delivery，报告验收未通过；源码变更送新网页轮次 |
| `delivery` | `delivered_source_id`, `complete` | 同一源码约定交付门槛 |
| `external_blocker` | `reason`, `attempts`, `requires_external_change`, `independent_work_remaining` | 普通空间丢失/崩溃转恢复；其余先完成独立工作，确需外部改变才 blocked |
| `pause` / `resume` | 用户停止/明确预算指令引用，或阻碍解除证据；active browser_gate 另需下文 gate-bound 来源校验 | 保留同一 run 的恢复入口；回执/定时提示不解除人工门 |
| `followup_closed` | 同一 automation ID 的真实 PAUSED view，并传最新 Luna record | 采集和收讫均闭合但尚未处理时返回 process_saved_result，不因旧 waiting_web 再启表；仍需采集/收讫才恢复 Luna，用户停止/阻碍保存检查点，旧无调度不先建再关 |

`followup` 的真实 heartbeat view 回执保留 automation_id、ACTIVE/PAUSED、run_id、state_path、prompt_binding_verified、实际 cadence_minutes、checked_at、next_check_at、evidence_ref。增加 `owner_role="web_io"`、`owner_thread_id/target_thread_id/owner_host/owner_model/owner_reasoning`，均匹配 web_io_binding；`owner_model_readback_ref/owner_reasoning_readback_ref` 匹配其实际证据；另存 `controller_thread_id/controller_host`，不把 Controller 当 owner。宿主调用字段是 targetThreadId；这里只是归一化回执，model/effort 继承目标聊天，不能发明 heartbeat model 参数。

`browser_context` 只记录当前载体和恢复证据，不是服务端会话身份。先恢复可用的本任务空间，确认失效后按 browser-loop 的当前运行时合同恢复，允许重建时才打开原 URL；没有 URL 的未发送首轮不伪造 URL。`browser_recovered` 核对已发原请求；尚未发送需真实 definitive_absence=true 才回原发送门，unknown 不允许补发。可在该事件带当前实际 inline_observer_binding 与匹配的执行/turn 字段续接过期窗口，不能仅在 prompt 自称新执行者。已保存正文/附件和未收讫原 payload/evidence 保留。`browser_recovery_attempts` 最多两次连续载体恢复；各入口读取主 state 与最新同业务 ledger 的已用次数，切换 Controller/observer、owner/turn 或刷新证明不重新计数。`browser_recovery_fault` 保存实际故障时间；成功 `browser_context` 保存 observed_at 与原恢复事件 SHA，只有不早于当前故障的实际新成功才复位。已应用或陈旧成功重放不改载体/预算，改证据文件名也不是新事件；同空间恢复、同一引用下的新实际成功观测仍可用。旧 ledger 的次数按它自己的故障与成功核对，已解决旧事故不能污染后来的新事故。历史缺时间不伪造。旧 blocked 仅在原始阻碍证据已核实为载体故障并记录 blocker_reason_code 时，browser_recovered 或同等恢复字段的 resume 自动续保存阶段；其他或未分类 blocker 保留 blocked/原 marker，仍可独立恢复载体并 continue_independent_work，但恢复浏览器不证明材料主机/源码发布等条件已解除。无法确认原阻碍时读取本 run 原证据或走已有正常 resume+resolution_ref，不新增用户审批。真实 auth/user_control/permission_denied 门先核对下文 browser_gate_resolution 并 resume，保留解除证据后才允许后续普通恢复。显式用户暂停、inactive/unassigned 所有权和真正工具拒绝不可被失效标签遮盖。

`browser_execution_binding` 是独立可选兼容字段，结构与调用证据见 browser-platforms。已经绑定时 browser_recovered 必须带相符 `browser_actual`，换载体另带 `browser_driver_recovery`；实际工具错配不清旧事故预算。旧记录缺绑定先 reload 现行 Skill/本任务证据，不伪造既有驱动，不使已有本地处理失效。browser_driver_check/恢复的合法声明不解除 browser_gate。

以 `schedule_inventory_ref` 绑定本 run 全部实际调度的读取证据；`active_automation_ids` 在 ACTIVE 时必须仅含本 automation_id，PAUSED 时为空。默认建议 10 分钟，宿主实际节奏优先。ACTIVE 要下一次检查；PAUSED next_check_at=null。跨轮保留 ID，换绑需旧 ID 已删除/不存在的工具证据和替代 ACTIVE view。旧 Controller heartbeat 先用宿主工具暂停/删除并保存原始 readback，再迁移绑定并检查去重；不能假称旧 owner 是 Luna 才关它。

durable 发送前新鲜 view 必须在 10 分钟内，`awaiting_send=true` 保持准备→arm→send 的短窗口；正常发送后清零。已用于发送前验证的同一 view，可在有效窗内用于该 sent 读回。无 valid durable owner 返回 ensure_luna_owner，不能自动创建聊天或回退 Controller；有 owner 但调度无效返回 ensure_followup。已发消息/原文均保留，无真实刷新不消费预算。无网页/必需附件和排队收讫义务才 pause_if_active；进入下一轮发送前重新 arm 同一 ID。暂停仅针对本 run；项目级 watcher 仍有开发/构建等待时只解除网页子义务，不关整个 watcher。返回 schedule_action 是建议，仍需实际工具回读；`establish_durable` 表示待补而非已创建。`followup_check` 不自动修改 mode、执行调度或搬迁旧 ledger；inline 接续时先按 orchestration 保存/处理旧原件与通知、继承事故预算，再核实 owner 和 ACTIVE view，不能直接清空 ledger。

同一 ID 的已保存 PAUSED view 可由更晚、不同证据引用的真实 ACTIVE view 更新；新 view 仍须在有效窗内、owner/binding/唯一活跃清单相符。`followup_check` 直接建议把它原子保存为 state_updates.followup，不要求先把旧 state 手工标 ACTIVE 再重复读。旧/同时间 view、另一个 ID 或重复活跃调度均不成立。

Luna 执行只读 CLI `next_action.py --state <state> --event <observation> --observer-record <Luna-record>`，每次读最新 record，将成功返回的 observer_updates 原子写回 Luna 自己的 record 后再喂下一事件；不改 state/events。已保存的原始观测可按实际时间顺序本地重放生成 ledger，不重读网页凑新等待。Controller 处理结果或关闭跟进也传入本 run 最新 Luna record，只有 Controller 更新主 state/events。业务绑定 run/source/round/token/合同/host/对话/请求与 scope/mode；真实 owner 的 thread/host 或内部 agent_id、model/effort 与 inline turn 单独记录，verified_at/读回路径只证明证据新鲜度。仅刷新证据不重置去重、稳定窗口或预算；真实换 owner/turn 只重开尚未完成的稳定窗口，保留同业务的错误去重、累计预算与未收讫队列/原 payload/evidence。新 source/round/contract 等真实业务边界重新绑定记录，不能把旧结果冒充新结果。普通生成/流式字符变化不触发 Controller；actionable_progress 必须有本轮新消息内容及可行动证据；稳定完成用消息 ID+内容 SHA 去重；错误用稳定代码/内容 error_fingerprint 与错误转变去重，不能把轮询时间当新错误。临时刷新预算耗尽只停反复刷新，keep_active 静默观察恢复；有真实已知恢复证据的 quota/provider 可标 recovery_expected=true。登录/用户控制等需人工处理才交接；Controller 核实独立工作和阻碍后记录相应主状态。

只有新可行动进展、完整回复或实质阻碍才生成 Controller 事件。稳定完成事件携带两个相隔 ≥10 秒的原始观测，Controller 核实 prior_observation 的绑定和完整性后一次 triage；prior_observation 必须显式带当前 execution_scope（如 review_only），缺省会按 repair_loop 判 stale/unbound。正文收齐但 required 文件未验时 keep_active，只补取当前缺件。跨可见聊天通知需 `controller_notification_authorization={authorized:true,user_instruction_ref,destination_thread_id,destination_host}`；授权必须直接来自用户且匹配 Controller。转发 prompt 不授予回发权限；无授权返回 save_receipt_for_controller，保留工件供等待/读取。inline 内部观察完成可 return_to_controller，不发跨聊天消息；Controller 一次应用原 observation 即可记收讫，schedule_action 一律 none，不新增 durable 门槛。两条模式都不直接激活 Developer。

该授权可增加 `policy={authority_ref,mapping_verified:true,mapping_evidence_ref,triggers,max_deliveries}`；authority_ref 必须是同一直接用户指令，执行者在 mapping_evidence_ref 忠实记录原文的条件与次数，不由 helper 补授权限。triggers 取 `stable_reply/required_artifacts/material_blocker/actionable_progress/review_completed`；max_deliveries 为正整数，明确核实没有次数限制时才显式 null。字段缺失、旧自由文本未核实或条件未知返回 map_notification_policy，保留已收原 payload/key/SHA/history，并可本地收讫与处理；不能把 boolean authorized 当无限许可。

规划未来返回与当前发送分开：已忠实映射、仍有次数的“收齐报告后通知一次”可在发送前/回合结束时作为未来返回入口，无需等结果出现，更无需 Controller 已 completed。实际 `review_completed` 投递只在当前正文两次稳定完整保存、required 附件已验，并有 `requested_output_collection={complete:true,requirements_ref,body_sha256,evidence_ref}` 的请求产物收齐证据时解锁；requirements_ref 匹配原 prepared_request，body SHA 匹配本消息，原件覆盖由执行者实际核对。已标 response_interrupted/缺件/覆盖未知不触发、不占次数；已存部分回复仍可本地 QA。这是请求输出收齐，不是产品验收，Controller 后续收到、核实 coverage/意见并裁决，尚未收讫/QA 的完整报告也可以按原条件通知一次。

有次数限制时，pending/unknown/已投递的不同 key 占用次数；未知发送保守占位，不因换 round/owner 或重放重新授额。实际明确 not_delivered/active_writer 才释放该未送达占位，同 key 仅在原恢复/冷却/总三次机会门下重试；delivered/unknown 不再发送。同一次投递回执重放幂等。ledger 真业务绑定变化时把旧 notifications 保留在 notification_history 供同 run 授权计数，原 payload 和历史不改；旧缺省补录保留原队列。权限耗尽只禁止发送，新收件仍保存并交 Controller 直接读取、核实和继续获准工作；异步结束回合需另一个实际授权返回入口，共享文件不冒充唤醒。

采集完成、通知投递、Controller 收讫与处理各自核实。notifications 每项保存 key、原 controller_event、receipt_sha256、status、attempts、attempted_at/next_check_at 和实际投递证据；payload SHA 是原事件（含 notification_key）的规范 JSON SHA，排除 notification_receipt_sha256/controller_received_at。pending、not_delivered、unknown、active_writer、delivered 都未结束收讫义务；同内容去重不清掉待交记录。采集已齐时 scheduled_observation 或 notification_check 返回 observe_webpage=false，仅查独立回执和 Controller state，未收讫保持 keep_active，不反复打开原网页。全部已收讫时 Luna 可 pause_followup；Controller 的 controller_received/followup_readback/followup_closed 根据同一最新 ledger 给 process_saved_result 和未改写的原 controller_event，本地应用后仍走正常 triage/附件处理/交付动作，不再启网页表或让 Luna 做裁决。没有完整原 payload 的历史记录给 read_saved_result，从原件核实恢复，不能制造新 key/SHA。处理状态沿用 received_notifications 的同 key/原 payload SHA/业务绑定下的 applied 标记及既有主状态，不建第二套账本；已应用事件重放返回 already_applied_notification，不让旧进展或旧错误抢占完整报告。

附件与正文到达顺序不影响采集就绪。Controller 与 Luna 在各自记录的 `artifact_observation={payload,sha256}` 保存实际校验原事件，按绑定、合同、规范 SHA 与真实 verifier receipt 合并为当前必需文件证明；observed_at 来自本次 verifier 返回后的真实观察，不能用文件 mtime 或补造时间。主 state 较新证明可以覆盖 Luna 较旧证明；最新实际 invalid/missing/unverified 使必需附件重新待采集，不对未经验证的 ready 布尔值取 OR。assessment 的依赖项、worker 文件处置、validation 与最终交付共用同一门：当前证明有效，且主 state 已应用的必需文件快照与其一致。独立修复和可选附件变化不受此门阻断。

新有效必需快照未应用时，Controller 本地处理对应的原 artifact_receipt；队首可选回执不能遮盖后面的必需更新。真实 A→B→A 重验要应用本次快照；历史同 key/SHA 事件仍幂等，不能重写原 key/payload。已有通知不包含本次校验时间时，使用已保存的本次原始附件观测本地应用，不重开网页。Controller 和 Luna 替换各自 artifact_observation 前使用相同的合并规则：相同时间但必需快照冲突时附带一份原 `conflicting_proof={payload,sha256}`，保留主 state 已应用回执；同一 Luna 的旧成功、冲突原事件或第三份同时间观测都不能抹掉失败/必需冲突。必需快照相同而仅 optional 不同，不新增冲突。缺时间的旧直接回执不能覆盖有时间的新证明；未知顺序或同时间冲突用一次真正更新的本地校验消解，不加用户确认或重新下载要求。错误 SHA/绑定不能作为当前证明。

unknown 核对原请求 key/payload 的目的地历史和实际投递回执；即使历史暂未出现，也不能排除仍在途的请求。发现原消息记 delivered；只有取得该次请求明确未追加/已取消的回执，才用 observer_delivery 记 not_delivered。active_writer 仅用于明确发生在追加前的拒绝，否则同样 unknown。`destination_thread_id/destination_host` 绑定 state 的稳定 Controller 身份；实际发送方、工具 hostId 与服务入口另外保存在 handoff 通讯记录和原始证据中，不能把 A 的 local 原样用于 B 回发，也不因修入口改写 Controller 身份或原通知。

已知 not_delivered/active_writer 后按 project-handoff 恢复正确的写入服务；idle/可读都不足以解锁重试。notification_check 的 `write_endpoint_recovery={notification_key,receipt_sha256,attempted_at,evidence_ref}` 须匹配原通知与上次尝试，证据来自实际连接/入口恢复，不能用 idle 截图代替。恢复和非 unknown 读回沿用该事件的 destination 身份、readback_evidence_ref/readback_observed_at，时间在本次 observed_at 前 60 秒内且不早于上次投递。helper 只检查声明，执行者仍按 handoff 核实实际入口与故障类别。缺恢复证据返回 restore_notification_transport，继续低成本收讫核对；有恢复证据、目标未再报告 writer 冲突、冷却至少 60 秒且授权仍有效才 retry_notification。原 key、payload、source/token/原网页请求身份保持不变，总投递机会最多三次；耗尽返回 delivery_recovery_checkpoint。Controller 可主动 wait/read/读保存回执收取，不要求反向消息先成功；未授权发送也不妨碍读取与处理原结果。

原 Controller 事件带 notification_key/notification_receipt_sha256；处理 observation、artifact_receipt、web_progress，或 assessment/worker_result 引用已核对的小回执时，同次 state_updates 可写 received_notifications，保存绑定、原 payload SHA 和实际 evidence。只有实际应用 observation/artifact_receipt/web_progress 才标 applied=true；controller_received 或其他仅引用回执的事件只记收到，不能把未处理事件标成已应用。独立共享读取无额外审批/往返，收讫本身不代表采纳意见或整合通过。Controller 也可据既有 state 已处理相同 reply message/body SHA/原文路径或完整附件回执收敛。旧 luna-observer/v1 通知项仅有 key/status/evidence 时，核对其顶层 completion_observation 与当前 state 的同一绑定/消息/SHA/路径；不能确认的保留待核对，不伪造旧 payload/新回执，不把旧已处理 run 重挂。用户停止/已确认阻碍可暂停并保存未收讫 payload，恢复后核实原 Luna ACTIVE 继续核对。

repair_loop 的 assessment 确认问题与争议并存时先派独立确认修复；file_dependent_findings 在 required 文件存在时必须明确，dispatchable/pending 分开。新当前文件交同一个 Sol 继续，不建重叠 writer；局部交付不清空 pending，处理后明确 addressed_file_findings，未闭合不能下一轮。worker 不可擅换 github/mcp/local_packet 路线；Controller 的显式换路用关联的新 run 保留旧证据。repair_loop completed 要 clean 当前 review、当前 required 附件、绑定本地检查与交付；review_only 要完整 coverage、当前 required 附件和报告交付，开放建议保留，只有验收合同明确要求的检查才需 validation。review_only passed=false 保留当前失败证据与 required_unverified，在 validating 交报告；可 terminal=true 结束报告义务，但 acceptance_passed=false，不能宣称检查通过或派修。scope 变化使旧审查/交付记录失效。无隐含一次返修预算。

`next_action.py` 的 `valid=false/input_valid=false`、退出码 2 表示旧版本、字段缺失、错轮次/来源/合同/host 或非法转换。保留旧 valid/退出码接口；退出码 0 和 input_valid=true 仅表示建议计算成功，不证明输入事实或整个 run 完成。`submission_ready` 只在 `action=submit_once` 时为 true；`followup_ready`、未知发送核对及缺口动作均为 false，跟进就绪不能当发送许可；还须按 browser-platforms/browser-loop 核实实际驱动、UI、上传及发送。终态报告、合法输入与发送就绪不能混称。浏览器最多三次有退避的连续错误刷新是页面恢复预算，跟修复轮数无关；正常生成不刷新，发送未知不重发。

### 投递尝试与稍晚到达的完整性证据

`notify_controller/retry_notification` 返回 `notification_attempt_id`，同时在独立 ledger 写入该通知的 `attempt_id/attempt_history`。实际发送与 `observer_delivery.attempt_id` 使用同一 ID；原 notification_key、controller_event、receipt SHA 保持不变。只对唯一一次历史投递允许省略 attempt ID；多次尝试无法归属时返回 reconcile_notification_attempt，仅核对该回执，原件收取和本地处理继续。每次尝试的实际结果保留，旧尝试失败不能撤销另一尝试 delivered/unknown；一旦有送达事实就占用对应通知额度。迟到 unknown 也不抹掉同一次明确追加前拒绝。unknown 仍不是未投递，不据此新增尝试。

完整正文已经稳定保存后，输出覆盖核对可以稍晚形成。将 requested_output_collection 与原正文 SHA、requirements_ref、evidence_ref 绑定；同一回复的后续 scheduled_observation 可以追加证明，或 notification_check 带原 notification_key/notification_receipt_sha256 在本地追加。证明保存为 output_collection_proofs，原 controller_event/key/payload/SHA 不改写，不新增通知身份。只有原始回复确为完整稳定、非中断且必需附件齐全时，忠实 policy 才能允许第一次通知；不要求先完成 Controller QA，也不重新打开已收齐网页。重复或错正文/要求/receipt 的证明不产生第二次发送。

## 本地包事件

`source_route=local_packet` 适用于已授权的文档、研究和源码上传，source 固定为实际 ZIP hash。
prepare_submission 的 source_readback_ref 可以是本地包校验回执；还未声称网页读取。
submission.status=sent 或 adopt_submission.status=verified 需 source_upload 对象：

```json
{
  "archive_sha256": "本轮 ZIP 的 64 位 SHA-256",
  "manifest_sha256": "本轮清单的 64 位 SHA-256",
  "archive_name": "source.zip",
  "upload_complete": true,
  "evidence_ref": "本轮 UI 上传完成及消息附件的实际读回记录"
}
```

缺失/不同 hash/上传未完成不能被记录为已发送的合格本地包；发送状态未知仍先 reconcile，
不能为满足记录格式重复发送。完整覆盖的 assessment 需 source_readback_id=当前 source_id 和
source_readback_ref 指向 Web 实际读取清单/原件的证据；附件卡片或打包 PASS 不能填充这项。
修复后 worker_result 的 candidate_source_id 仍以 packet: 开头，validation 提供新 next_source_binding；
新一轮清除旧上传记录并冻结新包。上传/读取字段是声明式证据绑定检查，宿主仍须核实原始回执。
显式变更 source_route 使用关联旧证据的新 run，沿用网页对话；不篡改旧 state 或重新发送旧请求。

## 浏览器控制门兼容字段

`browser_gate` 独立于 phase，字段为 `gate_id/run_id/conversation_url/reason_code/observed_at/evidence/error_fingerprint`；Luna 先存 ledger，Controller 应用原事件或收件时同步。真实 gate 保留于同 run 的换 owner/turn/source/round；原事件回执和已有原件不可丢弃。普通故障优先结构化代码，自由文本只兼容明确肯定消息，不按任意子串推断接管。

未解除时，调度结果为 `observe_webpage=false`、durable 的 `schedule_action=pause_if_active`，即使尚有未收讫通知。这是页面动作暂停，不是采集完成；已有文件验证、原件读取、独立本地分析和 Controller 收讫仍可执行。不能用自动化 ACTIVE/投递成功替代解除证明。不要为关闭该网页任务连带暂停项目内其他义务。

`resume` 在 paused/blocked 或存在 active gate 时可用。对应 gate 的 `browser_gate_resolution` 包含 `gate_id/source/observed_at/evidence_ref`，时间须晚于停止且不晚于事件。`source=direct_user` 另需 `user_instruction_ref/author_is_human=true/applies_to_gate=true`；检查原始来源，而非 userMessage 角色/“继续”字样。heartbeat、automation、Controller 转述、历史指令和事后 takeOver 成功均不构成此来源。仅 auth 可用 `source=runtime_readback`、`condition_resolved=true/tool_result_ref` 的真实非页面恢复回执。helper 不鉴别人类身份，只验证这些声明的绑定；执行者必须核对原件。

缺少、错 gate、停止前或未来的解除证据返回 `request_browser_input`；不清 gate。通过后留存 `browser_gate_resolutions[gate_id]`，再核实当前 Luna/调度；未恢复调度时也保留解除证据，不要求重复的人类指示。旧解除不能解除新停止；新 user_control/permission_denied 不能被旧 auth 门或登录恢复回执遮盖。重复同一错误指纹不制造新的停止事件。旧 blocked 记录仍有人类 code 但缺字段时生成可识别 legacy gate，执行者核对原始停止时间和材料后提供新的对应来源，不能盲信旧 resolution_ref。完整 DOM 先独立落盘的顺序和额外格式 required/optional 边界见 browser-loop。
