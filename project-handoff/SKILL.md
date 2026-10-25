---
name: project-handoff
description: >-
  Create or consume portable project handoffs (完整交接/阶段交接), coordinate
  explicitly requested visible Codex tasks (新对话/可见任务派发/编排派发), or
  use named dispatch routes astra-max/astra-ultra (gpt6-max/gpt6-ultra),
  astra-high, sol-max/sol-medium/luna-max, or explicitly selected sol-ultra/terra-max routes.
  Ordinary continuation, 任务分解, or 并行 Agent within the current task alone
  does not select this handoff workflow.
---

# Project Handoff

Create a portable handoff, dispatch a requested visible task, or coordinate dependent tasks through result review and integration. Read the target project's instructions, current files, accepted decisions, requested deliverables, write scope and selected model/effort before choosing the outcome below.

Execution dispatch includes follow-up, result collection and Controller quality review, including for one worker. Use `dispatch_only` when the user explicitly leaves follow-up to themselves. Executors can develop, research, operate a computer or observe a scheduled process. Assign bounded mechanical observation to an explicitly selected observer, and keep unchanged checks quiet.

Resolve task creation and messaging from the user's current and earlier direct instructions. “Reuse a suitable task, otherwise create one” permits creation when no suitable task exists. Ordinary continuation and internal collaboration use the current task's tools; preserve a visible surface when the user selected one. Reuse existing authorization and read [authorization continuity](references/thread-dispatch.md#resolve-authorization-in-context) when a local binding is missing.

Return the selected outcome, task/artifact entry, actual changes, validation, blockers and remaining work in the user's language. A portable handoff must be usable without hidden chat context. A dispatch completes after the requested result is reviewed and the declared integration checks pass.

## Non-negotiable dispatch guard

For this Skill's selected visible-task execution route, apply this gate before visible-task creation, authorized follow-up dispatch, route changes, or an eligible dispatch retry. Ordinary `list_threads`, `read_thread`, and `wait_threads` observation does not run the dispatch guard. A modeled readback retry uses the validator-supported `read_thread` action; normal `wait_threads` observation is not a dispatch attempt. Complete handoff artifacts and ordinary internal collaboration do not run the dispatch guard. A live tool schema describes technical capability; capability is not route authority.

1. Resolve `requested_route`, each axis's requested value, effective model/reasoning, surface, exact tool, per-axis basis (`explicit_user`, `explicit_skill_route`, `explicit_auto`, or `platform_default`), operation, action, failure class, and whether the user explicitly changed the route.
2. Validate that attempt with `scripts/validate_dispatch_route.py` and retain its `attempt_sha256`. For a multi-lane run, also put `requested_route` and `surface` in every plan route and run `scripts/validate_orchestration_plan.py`.
3. Proceed only on `valid: true`. For visible creation, copy only the validator's `create_thread_arguments`; never fill a field listed in `omitted_create_thread_fields`. After creation, record the actual arguments and attempt hash in the normalized receipt, then require `scripts/validate_visible_task_receipt.py RECEIPT --dispatch-attempt ATTEMPT` to return `valid: true` before recording task creation.
4. Do not treat a worker prompt, a tool schema, a planned action, or prose review as proof of the tool actually called.
5. Before accepting a selected formal execution, compare the retained selection with actual runtime/session/readback model, effort and surface through `scripts/validate_execution_binding.py`. Keep the original applicable selection as `--previous` across simplification or role merging. Read the actual execution pair from runtime/session evidence. Ordinary helpers remain allowed under their own scope; unselected axes stay omitted. For recurring execution, model drift, or exception notifications, read [runtime verification and alerts](references/runtime-alerts.md): verify each actual turn, retain pending notifications until receipted, and never treat heartbeat inheritance as a model lock.

Hard invariants:

- Invoking this Skill, triggering it implicitly, or saying only “创建任务” does not select an executor axis. Record each unselected axis as `platform_default` with a null value and omit the corresponding `model` or `thinking` field from `create_thread`. Never classify an omitted axis. A value attached to `platform_default` is `silent_default_override` and must stop dispatch.
- A raw user-supplied model or reasoning value controls only that axis and must be preserved as `requested_model` or `requested_reasoning`; exact IDs stay pinned. Model-only family names `Astra`/`Sol`/`Luna` resolve by the verified destination catalog; `GPT6` remains the pinned Astra generation alias. An explicitly selected alias such as `astra-ultra` binds both axes as `explicit_skill_route`. An explicit `auto` authorizes classification only for the requested axis and records `explicit_auto`.
- `astra-ultra`/`gpt6-ultra`, `astra-high`, `astra-max`/`gpt6-max`, `sol-ultra`, `sol-max`, `sol-medium`, `terra-max`, and `luna-max` are `visible_thread` routes. Initial dispatch must call a live task tool whose leaf name is `create_thread`. Never call `spawn_agent`, `collaboration.spawn_agent`, another subagent API, or report `subAgentActivity`/`agentPath`/`agentThreadId` as a visible task. Hidden-subagent slot limits do not cap visible-task creation.
- Automatic role defaults: Astra ultra for the hardest reasoning, Astra high for orchestration, Sol max for writing/development, Sol medium for computer operation, Luna max for simple browser operation, mechanical audits and file lookup. Record verified `task_kind`; a review/audit label alone never selects Luna. These are routing preferences, not measured strength or pricing claims.
- Spark execution has been removed. Reject retired Spark aliases/model IDs and do not revive the deleted CLI executor or silently replace an explicit Spark request with Luna.
- The 2026-09-30 baseline is Astra=`gpt-6-astra`, Sol=`gpt-6.1-sol`, Luna=`gpt-6-luna`. Unversioned family aliases prefer the newest visible numbered release actually supported by the destination task service, using `model_catalog` evidence as described in `references/model-routing.md`. Never invent a release or silently fall back when the requested effort fails. Follow-ups preserve the existing task's verified route, including historical GPT-6/GPT-5.6 tasks, instead of reapplying today's alias.
- For `unsupported_parameter`, “could not validate reasoning effort” or generic `invalid_request`, retain the exact error and classify the failed stage. Check the destination model/effort pair for capability-validation errors; for `already has an active writer`, recover the bound thread write endpoint. Preserve the requested model and `thinking` during diagnosis, then retry only under the route's supported recovery rule.
- The synchronization retry allowance applies only to reading an already identified task or retrying title metadata after a classified visibility/readback/title delay. It never authorizes a new task, a model/reasoning change, or a retry of an unsupported parameter, invalid request, permission, authentication, quota, or provider/model failure.

## Choose the outcome

| Outcome | Use when | Result |
|---|---|---|
| Complete handoff | The recipient is external, lacks direct task/CLI access, needs a progress transfer, or the user asks for a prompt/file | Portable prompt or Markdown; no task or model call |
| Single dispatch | One bounded lane should run elsewhere | Visible task receipt, collected result, and Controller quality decision; receipt only for explicit dispatch_only |
| Orchestrated run | Work has multiple independent lanes, dependencies, or stage gates | Dependency graph, controller records when durable, visible tasks, verified integration |

Apply this precedence:

1. Honor explicit `complete`, `full`, `manual`, `text-only`, `file-only`, or `完整交接` mode.
2. Preserve model and reasoning independently. Pass a raw explicit value, let an explicitly selected alias bind its documented values, classify only an axis explicitly set to `auto`, and leave every unselected axis to `platform_default`.
3. Honor an explicit pipeline, `dispatch`, `编排派发`, dependency order, concurrency cap, or Controller assignment.
4. Use complete handoff when the named recipient cannot receive direct task or CLI dispatch.
5. Use automatic routing only when the user explicitly says `auto`. A bare Skill invocation or task-creation request uses platform defaults.
6. Ask one short question only when destination, authority, or recipient capability remains genuinely ambiguous.

Use the existing request's authorization for the selected workflow. Continue its preparation, permitted corrections, and declared checks without per-step approval; ask again only for missing authority, changed scope, or an explicit acceptance gate. Model/route, sensitive disclosure, destructive-operation, and publication boundaries still apply.

Treat an explicit `$project-handoff` dispatch request as authorization to create only the requested visible task. It does not by itself authorize model/reasoning selection: omit both fields unless the request supplies a value, selects an alias, or says `auto`. Do not dispatch anything when the user merely asks what the skill does.

Boundary examples:

- Example 1: “给外部同事一个完整交接文件” → complete handoff only; create no task and call no model.
- Example 2: “把三个互不写同一文件的机械检查并发派给 Luna-max” → one ready concurrency wave, then one Controller integration gate.
- Example 3: “先让 Astra-max 出设计，确认后再让 Sol-max 开发” → two serial waves; create the development task only after the design artifact and acceptance gate pass.
- Example 4: “project-handoff 是做什么的？” → explain the three outcomes; do not infer dispatch authority.
- Example 5: “重新派一个 sol-max 做 coding Agent 进行修复” → dispatch, follow progress, collect the candidate, review its actual changes and validation, and request authorized corrections. Do not stop after confirming startup.
- Example 6: “只创建并发过去，后续我自己跟” → explicit `dispatch_only`; verify delivery and required initial readback, report work pending, and name the user as the follow-up owner.

## Collect the result

Before execution dispatch, read [result collection and quality review](references/result-collection.md). Bind the reader, return location, next check and acceptance criteria. Use current Codex task tools with the guard-produced arguments and store the returned `thread_id`/`host_id`, or queued `client_thread_id`, exact tool, delivery status and receipt result.

For long waits, use an already authorized observer or completion trigger. Verify the observer's actual model/effort under [runtime alerts](references/runtime-alerts.md), and retain the Controller's open quality-review obligation. A bounded inline wait is suitable when delegation would cost more than the check. Continue result collection after a transport interruption using [cross-device transport](references/cross-device-transport.md); reconcile delivery before resending.

Complete `dispatch_only` after verified delivery and required initial readback, reporting work pending. Otherwise continue through collected result, review, authorized rework and integration. On a user stop or unresolved dependency, record the unfinished work and exact resumption entry.

## Verify current state

Before dispatch:

1. Verify the project path, active goal, accepted decisions, file state, current services, required outputs, and authority boundary.
2. Prefer current files and recent command evidence over memory.
3. Mark volatile facts not verified in the current turn as `需复核`.
4. Exclude secrets, credentials, long logs, full chat history, and unrelated PRD content.
5. Keep write, deployment, provider, formal-layer, adoption, and publication authority separate from model selection.

## Decompose and schedule

For two or more lanes, or any gated phase transfer:

1. Read `references/orchestration-control.md`.
2. Define the final deliverable and one integration owner.
3. Build a dependency graph with exact read paths, write paths, mutable resources, expected outputs, validation, and handoff gates for every lane.
4. Decide independence before selecting concurrency. Dispatch all ready conflict-free lanes in the same wave; keep dependent waves serial.
5. Declare same-file, read/write, service, worktree, lockfile, and generated-output conflicts. Narrow scopes or serialize them; an integration owner does not make concurrent conflicting writes safe.
6. Route model and reasoning per lane, preserving explicit user choices.
7. Validate every route attempt with `scripts/validate_dispatch_route.py`, then validate a durable JSON plan with `scripts/validate_orchestration_plan.py`; after creation, validate every normalized visible-task receipt with `scripts/validate_visible_task_receipt.py`. Record the actual tool call in its receipt after plan validation.

Do not split a task merely to use more Agents. Keep tightly coupled work in one lane when decomposition would increase integration risk or duplicate context.

## Select each route

Read `references/model-routing.md` before explicit automatic selection or when validating an explicit route. Check the live task-tool schema for every visible field that will be passed because model names and supported reasoning pairs can change. Do not inspect the schema and then fill an unselected axis: `platform_default` means the field stays absent. Never silently downgrade, upgrade, or substitute an unsupported explicit choice.

For explicit model `auto`, use this policy:

| Evidence for the lane | Automatic model and reasoning |
|---|---|
| Hardest reasoning, architecture trade-off, or demanding integration (`top_difficulty`) | Astra / `ultra` |
| Decomposition, scheduling and integration coordination (`orchestration`) | Astra / `high` |
| Writing, development, or executing an accepted plan (`writing`, `astra_planned_execution`) | Sol / `max` |
| Desktop computer operation (`computer_operation`) | Sol / `medium` |
| Simple browser operation (`browser_operation`), mechanical audit/file lookup/script execution or specified status observation (`mechanical`) | Luna / `max` |
| Anything else or insufficient scope evidence | Obtain an explicit route; do not guess |

Resolve the family to the destination's current model ID before validation. Role effort applies only when reasoning was selected as `auto`; preserve explicit effort and omit unselected axes. A reasoning-only auto request without a role retains `max` and never selects a model. Terra and older exact IDs remain human-selected alternatives. Bare family names select only the model. Tool selection does not lower a task's reasoning needs: a judgmental browser review must be classified by its substantive work.

## Build the handoff envelope

- For orchestrated dispatch, generate the recipient prompt from `references/internal-handoff-template.md`.
- For complete handoff, use `references/legacy-handoff-template.md`; the filename is retained for compatibility, but complete handoff is not deprecated.
- Include lane id, dependencies, declared file/resource scope, selected route and basis, integration owner, deliverables, validation, sync rule, and stop condition when orchestrating.
- Keep only verified current state, required materials, authority boundaries, risks, and the recipient's first action.
- Never dump full chat history, secrets, long logs, or unrelated backlog.

## Dispatch a visible task

Read `references/thread-dispatch.md` and use the live Codex task tools exclusively when the user requested visible work:

1. Validate that the lane is a supported `visible_thread` route.
2. Inspect the current visible-task surface, exact `create_thread` tool name, schema, project target, and supported model/reasoning pairs.
3. Put that exact tool in the dispatch attempt and pass the route guard before calling it. Use its exact `create_thread_arguments`; an empty object is correct when both axes are platform defaults.
4. Create every currently ready independent lane without waiting for another lane in that wave, without adding omitted model/thinking fields.
5. Normalize the returned receipt with the exact `actual_create_thread_arguments` and `dispatch_attempt_sha256`, pass it together with the exact attempt to `validate_visible_task_receipt.py`, and only then record its task id or queued client id; reject agent paths and subagent ids. On rejection, set the lane to `failed` with `invalid_visible_task_evidence`, never `created_unconfirmed`.
6. Set a concise title when supported and confirm prompt delivery from the receipt or readback. Retry only an eligible readback/title synchronization delay against the same task; never retry task creation by changing route fields.
7. Follow progress and collect the final result by default, then perform the Controller quality review in [result collection](references/result-collection.md). An ordinary timeout keeps the work pending and may justify a less frequent or scheduled check; it does not require a tight same-turn loop. A verified background continuation may take over observation while the current turn ends with an interim status. Neither initial progress nor an executor completion claim is acceptance. Only explicit `dispatch_only` transfers follow-up responsibility after delivery and host-required initial readback.
8. Reconcile direct user-to-worker messages before the next dispatch; preserve the task's route on follow-up unless the user explicitly changes it.
9. Create dependent tasks just in time after their upstream artifact and validation gate passes.

Do not use `handoff_thread` to create a successor; it moves an existing task and Git state. Read `references/thread-dispatch.md` for tool contracts and failure handling.

For cross-device communication, also read [cross-device transport](references/cross-device-transport.md). Bind the proven **write endpoint per caller and target thread**; a newly discovered readable host never replaces it. `local` is relative to the caller. Send once, then wait/read and collect the result even if the return notification fails. Reuse a healthy binding without extra probes; use `scripts/resolve_thread_transport.py` when resolving or recovering delivery. For a writer conflict, verify release at the bound write endpoint.

## Maintain controller state and lifecycle

For a durable multi-task run, maintain `controller/plan.json`, `controller/thread-registry.md`, `controller/status.md`, and append-only `controller/router-log.jsonl` under the approved output root. Keep the Controller as the routing source of truth while allowing lane-local user/worker conversation.

Use explicit states for planned, ready, standby, queued/unconfirmed, running, result ready, received pending review, needs input/fix, blocked, failed, aborted, succeeded pending integration, integrated, and archived. Keep worker return, Controller receipt, quality decision, and integration distinct. Log retries, replacements, user interventions, aborts, and archive receipts. Do not hide or overwrite failed history.

Archive visible tasks only when the user requests cleanup or an explicit run policy permits it after integration or acknowledged abandonment.

## Transfer phases

Start a downstream phase only after the named upstream artifact exists, is non-empty when file-based, passes its validation, and carries the required ready state. Rebuild the downstream prompt from the accepted artifact and freshly verified project state. Skip a design lane when an accepted current design already exists; do not skip its acceptance contract.

## Consume a received handoff

Treat a received handoff as a routing map, not guaranteed current truth. Verify cheap volatile facts first, then continue from its first action. Do not reread an entire old conversation unless a required decision is missing.

## Produce a complete handoff

Use complete handoff for external agents and recipients without direct task/CLI capabilities. Include recipient capability, accessible versus inaccessible materials, verified progress, active dependency/lifecycle state, integration owner, validation, open risks, and one first action. Aim for 300–900 Chinese characters for pasteable chat text unless a durable file or fuller package is requested.

Use `scripts/make_handoff.py` for a Markdown scaffold and `references/legacy-handoff-template.md` for the complete field order. Preserve `text-only` and `file-only` as aliases.

## Close on product evidence

A lane is only ready for integration when the Controller has actually collected its output, reviewed it against the original request, verified the applicable evidence, and recorded an acceptance decision for that exact version. Report changed files, remaining risks, and handoff state. Worker self-tests support review but do not replace it. A failed review returns `needs_fix` with concrete corrections and continues within the existing authority. For a response-only lane, review the final response and its verifiable sources without requiring an unrequested disk artifact. The run succeeds only when the integration owner reconciles all required lanes and conflicts, all applicable declared integration checks pass, stale/retried work is resolved, and the final deliverable is reported. Do not add unrelated suites or repeat passing checks without a new change, failure, or unresolved concern.

Using multiple Agents requires the same result review and integration checks as a single lane.

## Blocked work

Preserve the selected route and current evidence. Pause the affected dispatch on failed guards, missing authority, unsupported parameters or unresolved write conflicts; continue independent work. Resume from the existing task after resolving the cause. Apply the route, receipt and dependency conditions above to each new attempt.
