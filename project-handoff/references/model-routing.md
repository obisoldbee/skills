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
2. Treat an explicit `auto` for that field as authorization to classify it.
3. Classify a field only when it is omitted or set to `auto`.
4. Use a runtime default only when classification remains ambiguous and the user did not make that field explicit.

If the user specifies a model but not reasoning, keep the model and select only a compatible reasoning level. If the user specifies reasoning but not a model, keep that reasoning and select only a compatible model. Validate visible-task pairs against the current task-tool schema before dispatch; validate Spark against the bundled wrapper contract, never the visible-task schema.

An explicit ordered pipeline, lane-to-model mapping, or concurrency cap also wins over automatic planning. Never silently downgrade, upgrade, or substitute an unsupported explicit value; report the unsupported pair and ask for a new choice only when no exact route is possible.

Record each field's basis as `explicit_user`, `auto_requested`, or `auto_unspecified`.

## Aliases

| Alias | Model | Reasoning | Surface |
|---|---|---|---|
| `sol-ultra` | `gpt-5.6-sol` | `ultra` | visible Codex task/controller |
| `sol-max` | `gpt-5.6-sol` | `max` | visible Codex task |
| `terra-max` | `gpt-5.6-terra` | `max` | visible Codex task |
| `luna-max` | `gpt-5.6-luna` | `max` | visible Codex task |
| `spark` / `spark-xhigh` | `gpt-5.3-codex-spark` | `xhigh` | bundled CLI workflow |
| `portable-handoff` | `none` | `none` | external harness handoff |

Normalize alias casing. Check the live tool declaration before creating a visible task because supported model/reasoning combinations can change. Tool capability is not route authority: an advertised Spark model does not authorize `create_thread`, fork, handoff, or any visible task. `spark` is an atomic CLI-only route, and a nonzero wrapper exit terminates that lane until a new explicit user request changes route. `luna-max` is an atomic max route unless the user explicitly replaces that alias with another route; a later follow-up does not implicitly replace it.

Treat every non-Spark alias above as a visible-task contract, not merely a model selection. Initial dispatch must use the live `create_thread` tool. `spawn_agent`, collaboration subagents, agent paths, and subagent activity receipts never satisfy these aliases.

When the user explicitly names another live-supported reasoning tier such as `low`, `medium`, `high`, `xhigh`, `max`, or `ultra`, preserve it and record a non-alias `requested_route` when it replaces an alias contract. Do not copy a Controller's reasoning tier to workers automatically. Reserve automatic `ultra` for an explicitly requested Controller or a separately documented runtime policy; established worker aliases above remain the default automatic choices.

## Mandatory route preflight

Before any dispatch, follow-up, retry, or availability claim, serialize the attempt and run `scripts/validate_dispatch_route.py`. A multi-lane plan must also carry `requested_route` and `surface` for every lane so `scripts/validate_orchestration_plan.py` can enforce the same alias boundary.

The attempt receipt requires:

~~~yaml
operation: initial_dispatch | followup | sync_retry | failure_report
action: create_visible_task | run_bundled_spark_cli | produce_portable_handoff | read_existing_task | set_visible_task_title | send_followup | none
tool: <exact live tool or bundled wrapper>
failure_class: none | creation_visibility_delay | prompt_readback_delay | title_metadata_delay | unsupported_parameter | invalid_request | unsupported_route | wrapper_missing | codex_cli_missing | auth | permission | quota | provider_model | unknown
route_changed: false
explicit_user_route_change: false
route:
  requested_route: spark | luna-max | sol-max | terra-max | portable-handoff | model-id
  model:
  reasoning:
  surface: visible_thread | bundled_cli | portable_handoff
  model_basis: explicit_user | auto_requested | auto_unspecified
  reasoning_basis: explicit_user | auto_requested | auto_unspecified
~~~

For `operation: followup` only, also provide `prior_file_access`, `requested_file_access`, `plan_guard_valid`, and `environment_guard_valid`. Do not add those four fields to other operations. An external harness initial attempt uses `portable-handoff`, `produce_portable_handoff`, `tool: none`, and `portable_handoff`.

Proceed only when the validator returns `valid: true`. Obey its `terminal`, `next_action`, `visible_task_allowed`, and `route_change_requires_new_user_request` fields. An `unsupported_parameter`, `invalid_request`, or `reasoning.summary` rejection on the visible/Desktop surface is classified as `wrong_surface_or_request`, cannot support a Spark-unavailable claim, and must not be retried by changing or omitting reasoning.

After visible creation, normalize the actual `create_thread` return and run `scripts/validate_visible_task_receipt.py`. Do not register a lane until that validator accepts a real ready `thread_id`/`host_id` or queued `client_thread_id`.

## Per-lane classifier

Build the dependency graph and lane scope first, then classify each lane. One run may legitimately use different routes for design, implementation, audit, and integration. Keep deterministic local work local when an LLM adds no material value.

### Route to Sol-max

Use for:

- product or architecture design;
- ambiguous requirements;
- cross-system trade-offs;
- migration strategy;
- high-consequence design review;
- selecting among multiple viable approaches.

Require decisions, alternatives, risks, interfaces, acceptance criteria, and a clear handoff state.

### Route to Terra-max

Use for:

- implementing an accepted plan;
- multi-file development;
- debugging and integration;
- tests and verification;
- converting a stable design into working artifacts.

This is the ordinary implementation default. If the design is missing or materially unresolved, run Sol-max first unless the implementation is small and the user explicitly requests Terra directly.

### Route large-project development to Sol-max

Use Sol-max instead of Terra-max for development when either signal is verified:

- the source Controller is `gpt-5.6-sol` with `ultra` reasoning; or
- the project is clearly high-intensity at large or super-large scale, with multiple coordinated workstreams, cross-system interfaces, substantial collision risk, or an unusually demanding integration and verification surface.

Treat a verified Sol-ultra Controller as a strong orchestration signal: keep that Controller coordinating the work and assign bounded development lanes to Sol-max. Do not automatically copy `ultra` reasoning to workers.

Use only controller metadata exposed by the current runtime or explicitly stated by the user. Do not infer the Controller model from writing style. If controller metadata is unavailable and project scale is ambiguous, keep the ordinary Terra-max implementation route. An explicit user route always overrides these defaults.

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

1. Route design to Sol-max.
2. Require a named, non-empty artifact and explicit ready state.
3. Verify the artifact and current repository state.
4. Route implementation just in time: Terra-max ordinarily, or Sol-max under the verified large-project/controller rule above.

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
operation:
action:
selected_executor:
planned_tool:
actual_tool:
model:
reasoning:
model_basis: explicit_user | auto_requested | auto_unspecified
reasoning_basis: explicit_user | auto_requested | auto_unspecified
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

### Example 1 — Architecture design

Input: “为一个跨设备 Repo Hub 设计控制面、数据模型和迁移方案。”

Expected: `gpt-5.6-sol`, `max`, visible task.

Reason: The task requires architecture and trade-offs rather than implementation.

### Example 2 — Accepted-plan implementation

Input: “方案已经批准，按 `docs/specs/api-v2.md` 实现并跑测试。”

Expected: `gpt-5.6-terra`, `max`, visible task.

Reason: A current accepted design already defines the implementation contract.

### Example 3 — Design then build

Input: “先设计新的同步协议，方案验收后再开发。”

Expected: `gpt-5.6-sol max -> gpt-5.6-terra max`, sequential visible tasks.

Reason: The user explicitly requires a design gate before implementation.

### Example 4 — Judgmental audit

Input: “核验三份研究报告的证据是否真的支持工程结论，并标出风险。”

Expected: `gpt-5.6-luna`, `max`, visible task.

Reason: The work requires evidence interpretation and risk judgment.

### Example 5 — Mechanical audit

Input: “只读检查 80 个 manifest 的 YAML、字段、路径和 SHA，输出异常表，不判断内容价值。”

Expected: `gpt-5.3-codex-spark`, `xhigh`, bundled CLI.

Reason: The scope is bounded, structural, read-only, and non-authoritative.

### Example 6 — Sol-ultra Controller development

Input: The verified source Controller is `gpt-5.6-sol` with `ultra` reasoning and is orchestrating a super-large multi-workstream project; hand off an accepted implementation lane without naming a worker.

Expected: `gpt-5.6-sol`, `max`, visible task.

Reason: Sol-ultra is retained as the orchestration Controller while Sol-max performs the high-intensity development lane.

### Example 7 — Partial explicit route

Input: “实现这个已验收方案，用 Terra，推理档位 auto。”

Expected: preserve `gpt-5.6-terra`; auto-select only a live-compatible reasoning level, ordinarily the alias default `max`.

Reason: Model and reasoning precedence are field-specific.

### Example 8 — Independent mixed lanes

Input: “并行做两件事：Sol-max 设计迁移方案；Luna-max 独立审核现有证据。两者都完成后由当前任务集成。”

Expected: dispatch both visible tasks in one ready wave with their explicit routes; current task remains integration owner.

Reason: The lanes have no data dependency or shared writes, and both explicit routes must be preserved.
