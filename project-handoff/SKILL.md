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

Route work from verified project state. Preserve complete portable handoff as a first-class result while using one Controller for decomposition, dispatch, synchronization, and integration when execution is requested.

Background: Use this Skill as the single control surface for complete handoff, bounded dispatch, or dependency-aware orchestration. A handoff or task receipt is routing evidence, not authority to deploy, publish, install, or adopt.

Scope: Ordinary continuation or internal subagent collaboration stays within the current task's rules. The visible-task guard prohibits substituting subagents for requested visible tasks; it does not prohibit internal help. For complete handoff, load the portable template; for execution, load only the references required by the selected route and outcome. Reuse current readings until the relevant contract or state changes.

Materials: Read the target project's current instructions, accepted decisions, active goal, file state, authorized read/write roots, required deliverables, validation commands, recipient capabilities, and any explicit model/reasoning/concurrency choices.

Constraints: Preserve explicit user choices and scope; keep secrets and unrelated history out; do not dispatch when the user only asks for an explanation; do not parallelize conflicting lanes or infer deployment/provider/formal-layer authority.

Objective: Select exactly one outcome, verify current state, build a self-contained handoff or safe dependency graph, dispatch only when authorized, synchronize artifacts and task state, and close through the named validation/integration gate.

Output format: Return the selected outcome, route and basis, visible task or artifact receipts, changed/output files, validation, lifecycle/integration state, blockers, and explicit non-authorized actions. For complete handoff, use the portable template.

Success criteria: The recipient can continue from verified materials without hidden context; every requested lane or handoff artifact satisfies its gate; conflicts and stale work are reconciled; no task creation or fluent worker response is mislabeled as integrated success.

## Non-negotiable dispatch guard

For this Skill's selected visible-task execution route, apply this gate before choosing or calling any task, follow-up, retry, or task tool. Complete handoff artifacts and ordinary internal collaboration do not run the dispatch guard. A live tool schema describes technical capability; capability is not route authority.

1. Resolve `requested_route`, each axis's requested value, effective model/reasoning, surface, exact tool, per-axis basis (`explicit_user`, `explicit_skill_route`, `explicit_auto`, or `platform_default`), operation, action, failure class, and whether the user explicitly changed the route.
2. Validate that attempt with `scripts/validate_dispatch_route.py` and retain its `attempt_sha256`. For a multi-lane run, also put `requested_route` and `surface` in every plan route and run `scripts/validate_orchestration_plan.py`.
3. Proceed only on `valid: true`. For visible creation, copy only the validator's `create_thread_arguments`; never fill a field listed in `omitted_create_thread_fields`. After creation, record the actual arguments and attempt hash in the normalized receipt, then require `scripts/validate_visible_task_receipt.py RECEIPT --dispatch-attempt ATTEMPT` to return `valid: true` before recording task creation.
4. Do not treat a worker prompt, a tool schema, a planned action, or prose review as proof of the tool actually called.

Hard invariants:

- Invoking this Skill, triggering it implicitly, or saying only “创建任务” does not select an executor axis. Record each unselected axis as `platform_default` with a null value and omit the corresponding `model` or `thinking` field from `create_thread`. Never classify an omitted axis. A value attached to `platform_default` is `silent_default_override` and must stop dispatch.
- A raw user-supplied model or reasoning value controls only that axis and must be preserved as `requested_model` or `requested_reasoning`; exact IDs stay pinned. Model-only family names `Astra`/`Sol`/`Luna` resolve by the verified destination catalog; `GPT6` remains the pinned Astra generation alias. An explicitly selected alias such as `astra-ultra` binds both axes as `explicit_skill_route`. An explicit `auto` authorizes classification only for the requested axis and records `explicit_auto`.
- `astra-ultra`/`gpt6-ultra`, `astra-high`, `astra-max`/`gpt6-max`, `sol-ultra`, `sol-max`, `sol-medium`, `terra-max`, and `luna-max` are `visible_thread` routes. Initial dispatch must call a live task tool whose leaf name is `create_thread`. Never call `spawn_agent`, `collaboration.spawn_agent`, another subagent API, or report `subAgentActivity`/`agentPath`/`agentThreadId` as a visible task. Hidden-subagent slot limits do not cap visible-task creation.
- Automatic role defaults: Astra ultra for the hardest reasoning, Astra high for orchestration, Sol max for writing/development, Sol medium for computer operation, Luna max for simple browser operation, mechanical audits and file lookup. Record verified `task_kind`; a review/audit label alone never selects Luna. These are routing preferences, not measured strength or pricing claims.
- Spark execution has been removed. Reject retired Spark aliases/model IDs and do not revive the deleted CLI executor or silently replace an explicit Spark request with Luna.
- The 2026-09-30 baseline is Astra=`gpt-6-astra`, Sol=`gpt-6.1-sol`, Luna=`gpt-6-luna`. Unversioned family aliases prefer the newest visible numbered release actually supported by the destination task service, using `model_catalog` evidence as described in `references/model-routing.md`. Never invent a release or silently fall back when the requested effort fails. Follow-ups preserve the existing task's verified route, including historical GPT-6/GPT-5.6 tasks, instead of reapplying today's alias.
- `unsupported_parameter` or “could not validate reasoning effort” indicates a capability-validation failure, not proof the model is unavailable. A generic `invalid_request` also needs the actual error and failed stage: `already has an active writer` is a thread transport conflict, not a model error. Keep the requested model and `thinking`; diagnose the relevant capability or transport. Never downgrade effort, swap models, or use CLI/subagents to pretend visible creation passed.
- The synchronization retry allowance applies only to reading an already identified task or retrying title metadata after a classified visibility/readback/title delay. It never authorizes a new task, a model/reasoning change, or a retry of an unsupported parameter, invalid request, permission, authentication, quota, or provider/model failure.

## Choose the outcome

| Outcome | Use when | Result |
|---|---|---|
| Complete handoff | The recipient is external, lacks direct task/CLI access, needs a progress transfer, or the user asks for a prompt/file | Portable prompt or Markdown; no task or model call |
| Single dispatch | One bounded lane should run elsewhere | One visible Codex task receipt |
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

## Dispatch tool contract

Purpose: Use the current Codex task tools to deliver one authorized lane to a capable recipient and preserve a verifiable receipt.

Use when: The user explicitly requests visible dispatch/orchestration, and the target project, lane scope, route, dependencies, outputs, validation, and authority are known.

Do not use when: The user asks only for a complete text/file handoff or explanation; task tooling is unavailable; a requested explicit route is unsupported; dependencies or write conflicts are unresolved; or the action would exceed granted authority.

Parameters: Project/host target, lane id and goal, self-contained prompt, exact read/write paths, mutable resources, dependencies, expected outputs, validation, requested/effective model/reasoning axes with separate bases, the validator-produced `create_thread_arguments` and `attempt_sha256`, concurrency cap, integration owner, retry budget, and archive policy.

For completion or coordination work, bind the result reader, next check time/entry, and Controller receipt responsibility before dispatch. Initial delivery is not result receipt. The current Controller can use bounded `wait_threads`/`read_thread`; cross-turn waiting requires an actual verified observer and resumable schedule. An already selected Luna monitoring policy (for example chatgpt-codex-review or an explicit user choice) uses a verified Luna owner; respect explicit other model/effort choices, and ordinary handoff does not select or modify an unrequested axis. Reuse a suitable visible owner; creating another visible task still requires a direct user request. Do not use a Controller heartbeat or claim background follow-up from a prompt. Web capture and development/build waiting remain separate obligations.

Returns: A confirmed `thread_id` plus `host_id`, a queued `client_thread_id`, exact `actual_tool`, prompt-delivery/readback state, receipt-guard result, current cursor/status, artifact/validation receipts, or an exact structured failure.

Failure handling: Classify the exact failure with the dispatch guard. Metadata synchronization retries and message transport recovery are separate. For a writer conflict or connection failure, follow [cross-device transport](references/cross-device-transport.md): retain the original request, reconcile delivery, restore its verified write endpoint and continue result collection. A transport failure leaves that delivery pending; it does not stop the project. Never silently change route, scope, authority, executor, or create a second task by stripping a rejected parameter.

Tool stop rule: End dispatch-only after verified delivery; end a lane or run at its declared gate, user stop or genuine unresolved external dependency. An exhausted communication retry budget ends immediate resends only: keep the pending receipt, next check and independent work. For requested completion/coordination, collect the actual results; a send failure or successful dispatch does not close that obligation.

Task: Apply the verified materials, selected outcome, route basis, authority boundary, dependency/conflict analysis, tool contract, and stop rules above to produce the requested complete handoff or close the authorized dispatch through its artifact and integration gates.

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
7. Validate every route attempt with `scripts/validate_dispatch_route.py`, then validate a durable JSON plan with `scripts/validate_orchestration_plan.py`; after creation, validate every normalized visible-task receipt with `scripts/validate_visible_task_receipt.py`. Treat plan validation as declared-state checking, not proof of the tool actually called.

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
| Simple browser operation (`browser_operation`), mechanical audit/file lookup/script execution (`mechanical`) | Luna / `max` |
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
7. If the request includes completing or coordinating the worker's result, monitor with bounded task waits/readback and the declared artifact/evidence checks. Before closing dispatch-only, verify creation and delivery and satisfy any initial progress wait/readback required by the live host; report the worker's work as pending. This does not require waiting for worker completion. Commentary alone is not completion.
8. Reconcile direct user-to-worker messages before the next dispatch; preserve the task's route on follow-up unless the user explicitly changes it.
9. Create dependent tasks just in time after their upstream artifact and validation gate passes.

Do not use `handoff_thread` to create a successor; it moves an existing task and Git state. Read `references/thread-dispatch.md` for tool contracts and failure handling.

For cross-device communication, also read [cross-device transport](references/cross-device-transport.md). Bind the proven **write endpoint per caller and target thread**; a newly discovered readable host never replaces it. `local` is relative to the caller. Send once, then wait/read and collect the result even if the return notification fails. Reuse a healthy binding without extra probes; use `scripts/resolve_thread_transport.py` when resolving or recovering delivery. `idle` does not prove that a writer was released.

## Maintain controller state and lifecycle

For a durable multi-task run, maintain `controller/plan.json`, `controller/thread-registry.md`, `controller/status.md`, and append-only `controller/router-log.jsonl` under the approved output root. Keep the Controller as the routing source of truth while allowing lane-local user/worker conversation.

Use explicit states for planned, ready, standby, queued/unconfirmed, running, needs input/fix, blocked, failed, aborted, succeeded pending integration, integrated, and archived. Log retries, replacements, user interventions, aborts, and archive receipts. Do not hide or overwrite failed history.

Archive visible tasks only when the user requests cleanup or an explicit run policy permits it after integration or acknowledged abandonment.

## Transfer phases

Start a downstream phase only after the named upstream artifact exists, is non-empty when file-based, passes its validation, and carries the required ready state. Rebuild the downstream prompt from the accepted artifact and freshly verified project state. Skip a design lane when an accepted current design already exists; do not skip its acceptance contract.

## Consume a received handoff

Treat a received handoff as a routing map, not guaranteed current truth. Verify cheap volatile facts first, then continue from its first action. Do not reread an entire old conversation unless a required decision is missing.

## Produce a complete handoff

Use complete handoff for external agents and recipients without direct task/CLI capabilities. Include recipient capability, accessible versus inaccessible materials, verified progress, active dependency/lifecycle state, integration owner, validation, open risks, and one first action. Aim for 300–900 Chinese characters for pasteable chat text unless a durable file or fuller package is requested.

Use `scripts/make_handoff.py` for a Markdown scaffold and `references/legacy-handoff-template.md` for the complete field order. Preserve `text-only` and `file-only` as aliases.

## Close on product evidence

A lane is only ready for integration when its required output/receipt exists, lane validation passes, changed files and risks are reported, and its handoff state is explicit. For a response-only lane, the requested final response and its verifiable source evidence are the output; do not require an unrequested disk artifact. The run succeeds only when the integration owner reconciles all required lanes and conflicts, all applicable declared integration checks pass, stale/retried work is resolved, and the final deliverable is reported. Do not add unrelated suites or repeat passing checks without a new change, failure, or unresolved concern.

Using multiple Agents, creating tasks, or receiving plausible worker prose is never a success condition.

## Stop rules

- Do not silently replace an explicit executor or reasoning level.
- Do not turn Skill invocation, implicit triggering, or a bare task-creation request into automatic model/reasoning selection. Never pass a value for an axis recorded as `platform_default`.
- Do not dispatch, follow up, retry, or make model-availability claims without the matching guard/evidence.
- Do not revive retired routes or downgrade a max route on follow-up.
- Do not create a hidden subagent when a visible task was requested.
- Do not write `created_confirmed`, `created_unconfirmed`, or `queued` without a valid create-thread receipt containing the required real task identifier.
- Do not claim a task received work until readback or a creation receipt supports it.
- Do not call a model when complete handoff was requested.
- Do not parallelize lanes with undeclared or unresolved shared mutable state.
- Do not start downstream work before its upstream artifact gate passes.
- Do not mark a lane complete from an unsupported self-report or mark a run complete before its declared integration validation. Evaluate response-only outputs against their requested evidence gate.
- Do not turn a candidate, audit, or handoff into installation, deployment, adoption, or publication authority.
