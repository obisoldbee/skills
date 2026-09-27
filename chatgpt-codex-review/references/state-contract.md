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
  "followup": null
}
```

示例值不可拿来执行。已有本 Skill state 按原 phase 和原件恢复；已有代码与修复记录但无本 Skill 历史时，Astra 可直接核实材料、建立此 run 并从 `ready_to_submit` 准备复审，不重复初轮调研或默认派 Sol。旧 v2 缺 `controller_thread_id` / `controller_host` / `state_path` 时，用当前宿主真实上下文产生 `bind_controller` 事件补齐，不丢已收回复，也不编造身份。`conversation_url=null` 只适用于尚未发送的首轮或其暂停/阻碍恢复；空白新聊天通常在首条消息发送后才有真实 `/c/id`，届时由 Luna 读回。已有对话必须存实际 URL。`prepared_request` 由 Astra 准备事件写入，`followup` 由真实宿主 `automation_update/view` 回执写入，不能用此示例值冒充配置。

`source_route=github` 需要 `git:` 加完整 40/64 位小写 commit；其 `source_binding` 为经路由核实的 `repository` 和 `commit`。`mcp` 需要 `mcp:` 加 64 位内容快照 SHA，binding 为 route helper 返回的 `server`, `tool`, `version`, `snapshot_sha256`, `manifest_sha256`；`evidence_ref` 另存证据，不进 digest。三个 digest 均是各自对象的 UTF-8 JSON（sorted keys、紧凑分隔符、保留 Unicode）的 SHA-256。验收标准或内容访问工具变化会使旧 review/validation/delivery 失效。`artifact_root` 是本 run 的真实绝对目录。run 记录还应保存原始要求、scope、授权、角色实际 model/effort/任务 host、网页 space/page、调度回执与验收标准。

`artifact_contract.required` 与 `optional` 各列 `{name,kind,sha256?,size?}`；kind 为 `zip/png/json/utf8`。来源有可信预期 SHA/大小则填入，没有时只能声明本次接收计算的 SHA，不得说与原件一致。无附件要求时两个数组为空，附件门槛直接通过。输出附件可以是 Web 审查报告、图或日志；源码 route 不因此改变。`verify_artifacts.py` 只访问 `artifact_root` 内真实文件，检查字节数、SHA、类型与可读性；ZIP 检查 CRC、展开大小、symlink、穿越和路径别名；PNG 需 Pillow 完整解码。依赖缺失/格式无法验证产生 `unverified`，不是 PASS。不会执行附件代码。

Luna 的 `artifact_receipt` 保存完整 JSON 到独立文件，回 Astra 小回执：文件路径、回执 SHA、每项 status、`required_ready` 与异常。Astra 读原始回执及必要正文。建议器检查回执的 validator 标记、run/round/source/token/contract/consumer host/artifact_root 和必需文件状态；回执内容仍需由 Astra 核对真实文件。可选缺件不影响 `required_ready`。

## 事件和转换

所有事件均需与 state 完全一致的 `run_id`, `round`, `source_id`, `source_binding_digest`, `request_token`, `contract_digest`, `acceptance_digest`, `consumer_host`, `artifact_root`，加非空证据路径数组 `evidence`。仅有文件名不证明文件存在。v2 每轮 token 加入 `used_request_tokens`，新 token 不得与 run 中任何旧 token 重复。run/合同/host/source/工具绑定变化使旧审查与验收证据无效；附件还绑定 round/token/root。源码变化后新轮必须重新审查，并在 `validation` 事件提供新的 `next_source_binding`（来自 route helper/实际远端核查），使新源码的本地验证能在下一轮继续引用；同源补充消息也用新 token。

| type | 必需附加字段 | 建议器行为 |
|---|---|
| `bind_controller` | 实际 `controller_thread_id`, `controller_host`, 绝对 `state_path` | 旧 v2 补绑定后继续原阶段，并要求真实定时回读 |
| `prepare_submission` | Astra 保存的 `review_request_path`, `prompt_sha256`, 原始需求、source 读回、检查、逐项处置的引用与 `materials_verified=true`；明确只整理时 `materials_only=true` | 冻结本轮请求，不自动发送；只整理时返回 `deliver_prepared_request`，闭环模式缺定时返回 `ensure_followup` |
| `followup_readback` | `followup` 为真实 heartbeat view 回执 | 记录本 run ACTIVE ID；不同 ID 仅在旧任务已删除/不存在的工具证据与替代 ACTIVE view 齐全时换绑 |
| `submission` | `conversation_url` 可在首次 not_sent 为 null，`status=sent/not_sent/unknown`；sent 还需 `request_present=true`, `user_message_id`, `ui_model_verified=true`, `prompt_sha256` | 未发须准备请求及发送前新鲜 ACTIVE view；已读回才 watch，发送后跟进失效只补跟进，不重发 |
| `adopt_submission` | 实际 URL、user message ID、原文 SHA/路径、源码身份及绑定 digest 的读回；无网页 token 时另记 `local_import_id` 且标明原文没有它 | 原请求绑定后接管观察，未知先 reconcile，绝不因本地导入而重发 |
| `observation` | URL、时区时间、UI 错误/生成状态、请求与新消息身份、正文长度/SHA/保存路径、完成控件 | 两次完整稳定观测相隔 ≥10 秒才 triage；变化正文的观察时间也不可倒退 |
| `artifact_receipt` | `receipt`（helper 原始 JSON） | 绑定且必需文件 ready 后解锁依赖文件的修复或继续验收 |
| `assessment` | `review_message_id`, `coverage_complete`；完整时 `confirmed_findings`, `unresolved_claims`, `file_dependent_findings` | 已确认且可独立的修复先派；争议保留待裁决；必需附件缺时只挡文件依赖修复 |
| `worker_result` | `candidate_source_id`, `delivery_path`；处理文件依赖项时 `addressed_file_findings` | 仅从 repairing 进入 validating；缺文件项仍保留，不因一次局部交付消失 |
| `validation` | `checked_source_id`, `passed`, `required_unverified`；需复审时新 token | 本地失败继续返修，源码变更送新网页轮次 |
| `delivery` | `delivered_source_id`, `complete` | 同一源码约定交付门槛 |
| `external_blocker` | `reason`, `attempts`, `requires_external_change`, `independent_work_remaining` | 先完成独立工作；确需外部改变才 blocked |
| `pause` / `resume` | 用户停止/明确预算指令引用，或阻碍解除证据 | 保留同一 run 的恢复入口 |
| `followup_closed` | 同一 automation ID 的真实 `PAUSED` view | 用户叫停或全局验收后关闭本 run 调度并读回；旧已完成工作无调度不必先建再关 |

`followup` 回执含 `tool="automation_update/view"`, `kind="heartbeat"`, 真实 automation ID、`ACTIVE`/`PAUSED`、owner thread/host、run ID、state 绝对路径、已核实 prompt 绑定、实际 `cadence_minutes`、`checked_at`、`next_check_at` 与证据引用。ACTIVE 要有下次检查时间；PAUSED 可为 null。`followup_readback` 替换旧 ID 时另附 `replacement_of_automation_id`, `prior_automation_status=not_found/deleted`, `prior_automation_evidence_ref`，并保存换绑记录；通常跨轮复用同一 ID。发送前和恢复时要新鲜 `view`，旧回执不能永久放行；已用于发送前核实的同一 view，在有效时间窗内可用于该次 sent 读回，无须立即再 view。建议器只验证声明结构/绑定和时间，不会创建、暂停或查询任务。heartbeat 唤醒的是 Controller，由其读 state 后再派 Luna max；不能把 prompt 写着 Luna 当实际模型配置。调度失效返回 `ensure_followup`，但已发消息及已收原文保留；如果未真的刷新页面，不增加刷新计数。无变化的唤醒静默，完成或用户停止关闭本 run 的实际调度并回读。宿主若不支持建议的五分钟周期，记录实际支持的周期。

`assessment` 确认问题和争议并存时，若有可独立修复项进入 `repairing`，记录争议数，允许随后 `worker_result`。有必需附件且确认问题大于零时，`file_dependent_findings` 必须明确给出，不能靠缺省零漏派。`dispatchable_findings` 与 `pending_file_findings` 分开记录。Luna 在 repairing/validating 期间收到当前绑定的必需文件时，`artifact_receipt` 建议同一 Sol 继续修复，不创建重叠 writer；已交的局部 worker 结果不会清空待处理文件项。Sol 处理后以 `addressed_file_findings` 明确扣除；未扣除项使验证不能进入下一轮。必需文件缺失且全部确认问题依赖它们时建议 `obtain_required_artifacts`；不能以缺件阻止无关文本核实。worker 候选须保持当前 GitHub/MCP 源码路线，换路线要重新初始化。clean review 也要当前附件门槛、同 run/源码/来源工具/附件合同/验收合同/host 的本地检查和交付才可 completed。无隐含一次返修预算。

`next_action.py` 的 `valid=false`/退出码 2 表示旧版本、字段缺失、错轮次/来源/合同/host 或非法转换。退出码 0 仅表示建议计算成功，不证明输入事实或整个 run 完成。浏览器最多三次有退避的连续错误刷新是页面恢复预算，跟修复轮数无关；正常生成不刷新，发送未知不重发。
