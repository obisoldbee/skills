# Model Routing

Use this reference for automatic selection and for validating that an explicit route was preserved and is supported by the correct runtime surface.

## Contents

1. Field-level precedence
2. Aliases
3. Per-lane classifier
4. Mixed work and Controller routing
5. Route receipt
6. Evaluation examples

## Field-level precedence

Resolve `model` and `reasoning` independently:

1. Preserve an explicit user value for that field.
2. When the user explicitly selects a Skill alias such as `sol-ultra`, let that alias bind both fields.
3. Treat an explicit `auto` for that field as authorization to classify it and pass the selected value.
4. When the user did not select that field, leave it to the platform default and omit it from `create_thread`.

Merely invoking `$project-handoff`, triggering the Skill implicitly with “创建任务”, or asking to create a task does not authorize model classification. If neither axis was selected, record `requested_route=platform-default`, set both values to `null`, use `platform_default` for both bases, and call `create_thread` without `model` or `thinking`. This preserves the live platform defaults.

If the user specifies a model but not reasoning, pass only `model`; omit `thinking`. If the user specifies reasoning but not a model, pass only `thinking`; omit `model`. An explicit `auto` applies only to the axis on which it was requested. Validate every value that will be passed against the current task-tool schema before dispatch; validate Spark against the bundled wrapper contract, never the visible-task schema.

An explicit ordered pipeline, lane-to-model mapping, or concurrency cap also wins over automatic planning. Never silently downgrade, upgrade, or substitute an unsupported explicit value; report the unsupported pair and ask for a new choice only when no exact route is possible.

Record each field's basis as exactly one of:

- `explicit_user` — the user supplied that raw model or reasoning value;
- `explicit_skill_route` — the user explicitly selected a Skill alias that binds that axis;
- `explicit_auto` — the user explicitly asked the Skill to select that axis;
- `platform_default` — the user did not select that axis, so the corresponding tool field must be absent.

The route validator returns `requested_axes` with each axis's basis, requested value, and effective value, plus `create_thread_arguments` using tool field names (`model`, `thinking`) and `omitted_create_thread_fields`. A raw explicit axis must carry `requested_model` or `requested_reasoning`, and its effective value must match. The only model-name normalization is documented below: retain `astra` or `gpt6` as the requested name and resolve it to `gpt-6-astra`; this does not select reasoning. Use the exact argument projection. Supplying a value while its basis is `platform_default` is `silent_default_override` and must fail before dispatch.

## Aliases

| Alias | Model | Reasoning | Surface |
|---|---|---|---|
| `astra-ultra` / `gpt6-ultra` | `gpt-6-astra` | `ultra` | visible Codex task/controller |
| `astra-max` / `gpt6-max` | `gpt-6-astra` | `max` | visible Codex task |
| `sol-ultra` | `gpt-5.6-sol` | `ultra` | visible Codex task/controller |
| `sol-max` | `gpt-5.6-sol` | `max` | visible Codex task |
| `terra-max` | `gpt-5.6-terra` | `max` | visible Codex task |
| `luna-max` | `gpt-5.6-luna` | `max` | visible Codex task |
| `spark` / `spark-xhigh` | `gpt-5.3-codex-spark` | `xhigh` | bundled CLI workflow |

An alias is a shortcut for the complete model/reasoning/surface pair, not a new model. Bare `Astra` and `GPT6` are model-only names for `gpt-6-astra`; record `model_basis=explicit_user` and leave reasoning unselected unless the user names it or requests `auto`. For example, “模型用 GPT6，推理用平台默认” passes only `model=gpt-6-astra`. These spellings refer specifically to Astra, not every future GPT-6 variant. Existing `sol-ultra`, `sol-max`, and `terra-max` keep their original meanings. Terra remains available by explicit model or alias, but is never selected by model `auto` for new dispatch.

Do not migrate already-created Terra tasks as a side effect of this policy update. An unchanged historical automatic Terra route may continue only for existing-task follow-up, eligible synchronization, or failure reporting with `route_changed=false` and a verified existing task. Before using that exception, the caller must bind the operation to an existing task id and verify its original effective route from task readback and the historical receipt. The offline guard checks declared operation/route fields only; it does not query the task or prove this continuity evidence. New initial dispatch and new plans reject model `auto` selecting Terra. Historical receipts remain evidence of the original call and policy; a current initial-dispatch validator is not a retroactive acceptance test for those receipts.

Normalize alias casing. Check the live tool declaration before creating a visible task because supported model/reasoning combinations can change. Tool capability is not route authority: an advertised Spark model does not authorize `create_thread`, fork, handoff, or any visible task. `spark` is an atomic CLI-only route, and a nonzero wrapper exit terminates that lane until a new explicit user request changes route. `luna-max` is an atomic max route unless the user explicitly replaces that alias with another route; a later follow-up does not implicitly replace it.

Treat every non-Spark alias above as a visible-task contract, not merely a model selection. Initial dispatch must use the live `create_thread` tool. `spawn_agent`, collaboration subagents, agent paths, and subagent activity receipts never satisfy these aliases.

An explicitly selected alias records both axes as `explicit_skill_route`. If the user instead says `auto`, record `requested_route=auto` and the classified axes as `explicit_auto`; do not relabel an automatic choice as a user-selected alias. A raw model or reasoning value uses `explicit_user` and does not silently bind the other axis.

When the user explicitly names another live-supported reasoning tier such as `low`, `medium`, `high`, `xhigh`, `max`, or `ultra`, preserve it and record a non-alias `requested_route` when it replaces an alias contract. Do not copy a Controller's reasoning tier to workers automatically. Automatic reasoning uses `max` for visible tasks and `xhigh` for the atomic Spark CLI route. Use `ultra` only when explicitly requested, including through an `*-ultra` alias. An automatic choice is recorded as `requested_route=auto`, never relabeled as a user-selected alias.

The current task-tool schema observed on 2026-09-06 lists `gpt-6-astra` with `low`, `medium`, `high`, `xhigh`, `max`, and `ultra`. This is a compatibility observation, not a permanent support guarantee or runtime dispatch test; recheck the selected host at execution time.

## Mandatory route preflight

Before any dispatch, follow-up, retry, or availability claim, serialize the attempt and run `scripts/validate_dispatch_route.py`. A multi-lane plan must also carry `requested_route` and `surface` for every lane so `scripts/validate_orchestration_plan.py` can enforce the same alias boundary.

The attempt receipt requires:

~~~yaml
operation: initial_dispatch | followup | sync_retry | failure_report
action: create_visible_task | run_bundled_spark_cli | read_existing_task | set_visible_task_title | send_followup | none
tool: <exact live tool or bundled wrapper>
failure_class: none | creation_visibility_delay | prompt_readback_delay | title_metadata_delay | unsupported_parameter | invalid_request | unsupported_route | wrapper_missing | codex_cli_missing | auth | permission | quota | provider_model | unknown
route_changed: false
explicit_user_route_change: false
route:
  requested_route: spark | luna-max | astra-max | astra-ultra | sol-max | terra-max | model-id
  requested_model: <required for an explicit raw model; otherwise omit>
  requested_reasoning: <required for an explicit raw reasoning value; otherwise omit>
  model: <selected value or null for platform default>
  reasoning: <selected value or null for platform default>
  surface: visible_thread | bundled_cli
  model_basis: explicit_user | explicit_skill_route | explicit_auto | platform_default
  reasoning_basis: explicit_user | explicit_skill_route | explicit_auto | platform_default
~~~

Proceed only when the validator returns `valid: true`. Retain its `attempt_sha256`. For visible creation, copy only its returned `create_thread_arguments` into the live tool call; do not fill any returned `omitted_create_thread_fields`. Obey its `terminal`, `next_action`, `visible_task_allowed`, and `route_change_requires_new_user_request` fields. An `unsupported_parameter`, `invalid_request`, or `reasoning.summary` rejection on the visible/Desktop surface is classified as `wrong_surface_or_request`, cannot support a Spark-unavailable claim, and must not be retried by changing or omitting reasoning.

After visible creation, normalize the actual `create_thread` return, exact arguments, and attempt hash, then run `scripts/validate_visible_task_receipt.py RECEIPT --dispatch-attempt ATTEMPT`. Do not register a lane until that validator accepts both the binding and a real ready `thread_id`/`host_id` or queued `client_thread_id`.

## Per-lane classifier

Build the dependency graph and lane scope first, then classify each lane. One run may legitimately use different routes for design, implementation, audit, and integration. Keep deterministic local work local when an LLM adds no material value.

### Route to Astra-max

Use for:

- product or architecture design;
- ambiguous requirements;
- cross-system trade-offs;
- migration strategy;
- high-consequence design review;
- selecting among multiple viable approaches.

Require decisions, alternatives, risks, interfaces, acceptance criteria, and a clear handoff state.

### Route to Sol-max

Use for:

- implementing an accepted plan;
- multi-file development;
- debugging and integration;
- tests and verification;
- converting a stable design into working artifacts.

This is the ordinary implementation default and the bounded execution support for an Astra Controller. If the design is missing or materially unresolved, run Astra-max first unless a small implementation can be safely specified within the current lane. An explicit user route always wins.

### Route demanding development to Astra-max

Use Astra-max instead of Sol-max when the lane is verified to require high-intensity development or integration, for example:

- unresolved cross-system interfaces or architectural decisions;
- multiple coordinated workstreams with substantial collision risk;
- large or super-large scope with an unusually demanding integration and verification surface;
- a high-consequence review requiring the same depth of judgment as architecture work.

The Astra/Sol split replaces the former Sol/Terra automatic split: Astra takes the former design and highest-difficulty work; Sol takes accepted-plan implementation. Preserve the current or explicitly assigned Controller. Its model alone does not promote every helper to Astra or copy `ultra` to workers. Mechanical checks and ordinary bounded support retain their own route even inside a large run.

Use only verified lane scope and runtime/user-provided metadata; never infer a Controller model from writing style. If difficulty or project scope is ambiguous, keep ordinary implementation on Sol-max. Do not replace an explicit Sol or Terra choice just because the task is difficult.

### Route to Luna-max

Use for:

- judgmental audits;
- comparing evidence and claims;
- risk prioritization;
- focused research review;
- deciding whether a report supports an engineering conclusion.

Luna may produce visible review artifacts, but it does not inherit authority beyond the assigned scope.

Keep `max` on creation and every follow-up. Do not add `thinking: low`, omit the reasoning field to accept a default, or downgrade because a correction is short. Only an explicit user route change authorizes a different effective route.

### Route to Spark CLI

Use for bounded read-only work such as:

- parsing and classifying structured files;
- checking frontmatter, JSONL, YAML, hashes, names, paths, and counts;
- grouping deterministic validator failures;
- producing a candidate table from explicit files;
- summarizing mechanical command output.

Do not use Spark for product decisions, semantic truth, user-position handling, medical conclusions, formal writes, deployment, or final acceptance.

Spark has no visible-task branch in this Skill. Use only the bundled wrapper at `xhigh`; never test Spark availability through a task-creation API. On `PROJECT_HANDOFF_SPARK_TERMINAL_FAILURE`, stop the lane and wait for a new explicit user request rather than selecting an App model.

### Keep local

Do not create a model task when a single deterministic command fully answers the request and an independent LLM reading adds no value. Run the local validator, preserve exact output, and report it.

## Mixed work and Controller routing

For design plus implementation:

1. Route design to Astra-max.
2. Require a named, non-empty artifact and explicit ready state.
3. Verify the artifact and current repository state.
4. Route implementation just in time: Sol-max ordinarily, or Astra-max for a verified demanding lane as above.

Do not create both tasks simultaneously unless the user explicitly asks for speculative work and accepts that the implementation cannot pass its real integration gate until design is accepted. Other graph-independent lanes should still be dispatched concurrently.

For multiple ready lanes:

1. classify each lane separately;
2. preserve every explicit lane route;
3. dispatch the full ready, conflict-free wave within the live concurrency cap;
4. keep the current task or explicitly named Controller responsible for route changes and final integration.

## Route decision receipt

Record:

~~~yaml
lane_id:
requested_route:
requested_model:
requested_reasoning:
operation:
action:
selected_executor:
planned_tool:
actual_tool:
model:
reasoning:
model_basis: explicit_user | explicit_skill_route | explicit_auto | platform_default
reasoning_basis: explicit_user | explicit_skill_route | explicit_auto | platform_default
create_thread_arguments: <exact validator projection; omit platform-default axes>
omitted_create_thread_fields:
dispatch_attempt_sha256:
actual_create_thread_arguments:
surface:
selection_basis:
runtime_pair_verified:
dispatch_guard_valid:
receipt_guard_valid:
failure_class:
spark_unavailable_supported:
dependencies:
fallback: none | explicit-user-authorized alternative
authority_boundary:
~~~

## Evaluation examples

The offline `resolve_request_case` regression grammar is deliberately bounded, not a general runtime intent parser. It consumes the fixture forms for Chinese `模型和推理都自动选`, per-axis `模型自动选`/`推理自动选` (also `auto`), `模型用`/`推理用` values, Chinese `用`/`使用` aliases, a leading naked alias, or English `use <alias> ... create`. Model-only `Astra`/`GPT6` use the same leading/Chinese/English forms or follow `模型用`. Context fields describe verified lane facts, not hidden defaults: `lane_difficulty=bounded` prevents a large overall project from promoting ordinary implementation support. Multiple or conflicting explicit selections require a resolved route; unsupported fixture forms are not a license to override an axis. Runtime routing must still resolve the full live request. A bare `$project-handoff` or “创建任务” form is tested separately and never counts as an alias.

An explicit model plus reasoning `auto` preserves that model; model `auto` plus explicit reasoning preserves that reasoning. An omitted axis stays omitted. If a model-only automatic choice would require the atomic Spark route while reasoning is unselected, stop that proposed route rather than silently filling `xhigh` or substituting another model.

### Example 1 — Architecture design

Input: “创建新任务，模型和推理都自动选；为一个跨设备 Repo Hub 设计控制面、数据模型和迁移方案。”

Expected: `gpt-6-astra`, `max`, visible task.

Reason: The task requires architecture and trade-offs rather than implementation.

### Example 2 — Accepted-plan implementation

Input: “创建新任务，模型和推理都自动选；方案已经批准，按 `docs/specs/api-v2.md` 实现并跑测试。”

Expected: `gpt-5.6-sol`, `max`, visible task.

Reason: A current accepted design already defines the implementation contract.

### Example 3 — Design then build

Input: “模型和推理都自动选；先设计新的同步协议，方案验收后再开发。”

Expected: `gpt-6-astra max -> gpt-5.6-sol max`, sequential visible tasks.

Reason: The user explicitly requires a design gate before implementation.

### Example 4 — Judgmental audit

Input: “创建新任务，模型和推理都自动选；核验三份研究报告的证据是否真的支持工程结论，并标出风险。”

Expected: `gpt-5.6-luna`, `max`, visible task.

Reason: The work requires evidence interpretation and risk judgment.

### Example 5 — Mechanical audit

Input: “创建新任务，模型和推理都自动选；只读检查 80 个 manifest 的 YAML、字段、路径和 SHA，输出异常表，不判断内容价值。”

Expected: `gpt-5.3-codex-spark`, `xhigh`, bundled CLI.

Reason: The scope is bounded, structural, read-only, and non-authoritative.

### Example 6 — Demanding development under an Astra Controller

Input: The verified source Controller is `gpt-6-astra` with `ultra` reasoning; the user asks to auto-select both worker axes for a lane integrating several workstreams across a super-large project.

Expected: `gpt-6-astra`, `max`, visible task.

Reason: The lane's demanding integration scope selects Astra-max; the Controller stays in place. An ordinary bounded implementation helper under the same Controller would use Sol-max.

### Example 7 — Partial explicit route

Input: “实现这个已验收方案，用 `gpt-5.6-terra`；推理档位用平台默认。”

Expected: `create_thread_arguments={"model":"gpt-5.6-terra"}`; omit `thinking`.

Reason: A raw explicit model does not authorize the Skill to override the other axis.

### Example 8 — Independent mixed lanes

Input: “并行做两件事：Sol-max 设计迁移方案；Luna-max 独立审核现有证据。两者都完成后由当前任务集成。”

Expected: dispatch both visible tasks in one ready wave with their explicit routes; current task remains integration owner.

Reason: The lanes have no data dependency or shared writes, and both explicit routes must be preserved.

### Example 9 — Skill trigger only

Input: “帮我创建一个新任务继续处理。” or “`$project-handoff` 创建任务。”

Expected: `requested_route=platform-default`; `create_thread_arguments={}`; omit both `model` and `thinking`.

Reason: Skill discovery or invocation is task-creation authority only; it is not model-selection authority.

### Example 10 — Explicit auto

Input: “创建新任务，模型和推理都自动选。”

Expected: classify both axes, record both as `explicit_auto`, validate the live pair, and pass both returned fields.

Reason: The user explicitly authorized model/reasoning selection rather than leaving either axis to the platform.
