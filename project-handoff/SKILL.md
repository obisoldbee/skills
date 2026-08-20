---
name: project-handoff
description: >-
  Create or consume portable project handoffs; decompose dependency graphs;
  route by explicit or automatic model/reasoning; coordinate user-owned visible
  Codex tasks, bounded Spark CLI audits, and phase artifacts. Use for "handoff",
  "交接", "完整交接", "任务分解", "并行 Agent", "编排派发", "可见任务派发",
  "阶段交接", "新对话", "新任务", "接着做", controller/router workflows,
  cross-harness work, Git worktrees, parallel review, concurrent writers,
  staged design-to-development, sol-ultra, sol-max, terra-max, luna-max, or
  spark. For Sol/Terra/Luna dispatch, call create_thread and validate the real
  thread/client receipt; never substitute spawn_agent, collaboration subagents,
  agent paths, or subAgentActivity. Spark is bundled-CLI-only at xhigh,
  ephemeral, and read-only. Any nonzero Spark CLI exit ends that lane; never
  fall back to an App task or another model without a new explicit user request.
  Preserve every explicit model/reasoning choice.
---

# Project Handoff

Route work from verified project state. Preserve complete portable handoff as a first-class result while using one Controller for decomposition, dispatch, synchronization, and integration when execution is requested.

Background: Use this Skill as the single control surface for complete handoff, bounded dispatch, or dependency-aware orchestration. A handoff or task receipt is routing evidence, not authority to deploy, publish, install, or adopt.

Materials: Read the target project's current instructions, accepted decisions, active goal, file state, authorized read/write roots, required deliverables, validation commands, recipient capabilities, and any explicit model/reasoning/concurrency choices.

Constraints: Preserve explicit user choices and scope; keep secrets and unrelated history out; do not dispatch when the user only asks for an explanation; do not parallelize conflicting lanes or infer deployment/provider/formal-layer authority.

Objective: Select exactly one outcome, verify current state, build a self-contained handoff or safe dependency graph, dispatch only when authorized, synchronize artifacts and task state, and close through the named validation/integration gate.

Output format: Return the selected outcome, route and basis, visible task or artifact receipts, changed/output files, validation, lifecycle/integration state, blockers, and explicit non-authorized actions. For complete handoff, use the portable template.

Success criteria: The recipient can continue from verified materials without hidden context; every requested lane or handoff artifact satisfies its gate; conflicts and stale work are reconciled; no task creation or fluent worker response is mislabeled as integrated success.

## Non-negotiable dispatch guard

Apply this gate before choosing or calling any task, follow-up, retry, or Spark tool. A live tool schema describes technical capability; capability is not route authority.

1. Resolve `requested_route`, model, reasoning, surface, exact tool, field bases, operation, action, failure class, and whether the user explicitly changed the route.
2. Validate that receipt with `scripts/validate_dispatch_route.py`. For a multi-lane run, also put `requested_route` and `surface` in every plan route and run `scripts/validate_orchestration_plan.py`.
3. Proceed only on `valid: true`. After visible creation, normalize the raw tool result and require `scripts/validate_visible_task_receipt.py` to return `valid: true` before recording task creation.
4. Do not treat a worker prompt, a tool schema, a planned action, or prose review as proof of the tool actually called.

Hard invariants:

- `sol-ultra`, `sol-max`, `terra-max`, and `luna-max` are `visible_thread` routes. Initial dispatch must call a live task tool whose leaf name is `create_thread`. Never call `spawn_agent`, `collaboration.spawn_agent`, another subagent API, or report `subAgentActivity`/`agentPath`/`agentThreadId` as a visible task. Hidden-subagent slot limits do not cap visible-task creation.
- `spark` and `spark-xhigh` mean only `scripts/run-spark-cli.sh`, `gpt-5.3-codex-spark`, `xhigh`, `bundled_cli`, ephemeral, and read-only. Never create, fork, hand off, or retry a visible Spark task. Never use `create_thread`, `fork_thread`, `handoff_thread`, or another visible-task API for Spark, even when the API lists that model.
- Any nonzero `run-spark-cli.sh` exit is terminal for that Spark lane. Honor `PROJECT_HANDOFF_SPARK_TERMINAL_FAILURE`: call no task/thread/follow-up/model tool for the lane, do not substitute local or visible model work as if it were the Spark result, and wait for a new explicit user request before changing route.
- `luna-max` means `gpt-5.6-luna` with `max` on `visible_thread`. A later message being small or simple is not permission to use `low`, omit reasoning, or add a different `thinking` value. Follow-ups preserve the existing route unless the user explicitly requests a route change.
- `unsupported_parameter`, `invalid_request`, or rejection of `reasoning.summary` on a Desktop/visible-task request proves that request or surface is wrong. It is not evidence that Spark is unavailable. Stop that visible attempt; do not create a second task by deleting, omitting, or changing the reasoning field.
- Report Spark itself unavailable only when a correctly validated bundled-CLI attempt returns a provider/model route failure and the validator reports `spark_unavailable_supported: true`. A missing wrapper or CLI means the executor is unavailable, not that the Spark model is unavailable.
- The synchronization retry allowance applies only to reading an already identified task or retrying title metadata after a classified visibility/readback/title delay. It never authorizes a new task, a model/reasoning change, or a retry of an unsupported parameter, invalid request, permission, authentication, quota, or provider/model failure.

If an older incorrect visible Spark attempt already exists, preserve it as invalid-route evidence and do not continue it. Before any bundled-CLI attempt has failed, the original authorized Spark lane may make one fresh, validated bundled-CLI attempt; this corrects the surface rather than retrying the visible task. After a bundled-CLI failure, the lane is terminal.

## Choose the outcome

| Outcome | Use when | Result |
|---|---|---|
| Complete handoff | The recipient is external, lacks direct task/CLI access, needs a progress transfer, or the user asks for a prompt/file | Portable prompt or Markdown; no task or model call |
| Single dispatch | One bounded lane should run elsewhere | One visible Codex task receipt or approved Spark result |
| Orchestrated run | Work has multiple independent lanes, dependencies, or stage gates | Dependency graph, controller records when durable, visible tasks, verified integration |

Apply this precedence:

1. Honor explicit `complete`, `full`, `manual`, `text-only`, `file-only`, or `完整交接` mode.
2. Preserve an explicit model and reasoning independently. Auto-select only the component the user omitted or set to `auto`.
3. Honor an explicit pipeline, `dispatch`, `编排派发`, dependency order, concurrency cap, or Controller assignment.
4. Use complete handoff when the named recipient cannot receive direct task or CLI dispatch.
5. Use automatic routing only when the user says `auto` or explicitly requests dispatch without selecting an executor component.
6. Ask one short question only when destination, authority, or recipient capability remains genuinely ambiguous.

Treat an explicit `$project-handoff` dispatch request as authorization to create only the requested visible task or bounded Spark run. Do not dispatch anything when the user merely asks what the skill does.

Boundary examples:

- Example 1: “给外部同事一个完整交接文件” → complete handoff only; create no task and call no model.
- Example 2: “把三个互不写同一文件的只读审计并发派给 Luna” → one ready concurrency wave, then one Controller integration gate.
- Example 3: “先让 Sol 出设计，确认后再让 Terra 开发” → two serial waves; create the development task only after the design artifact and acceptance gate pass.
- Example 4: “project-handoff 是做什么的？” → explain the three outcomes; do not infer dispatch authority.

## Dispatch tool contract

Purpose: Use the current Codex task tools or the bundled Spark wrapper to deliver one authorized lane to a capable recipient and preserve a verifiable receipt.

Use when: The user explicitly requests visible dispatch/orchestration or an approved bounded Spark run, and the target project, lane scope, route, dependencies, outputs, validation, and authority are known.

Do not use when: The user asks only for a complete text/file handoff or explanation; task tooling is unavailable; a requested explicit route is unsupported; dependencies or write conflicts are unresolved; or the action would exceed granted authority.

Parameters: Project/host target, lane id and goal, self-contained prompt, exact read/write paths, mutable resources, dependencies, expected outputs, validation, selected model and reasoning with separate bases, concurrency cap, integration owner, retry budget, and archive policy.

Returns: A confirmed `thread_id` plus `host_id`, a queued `client_thread_id`, exact `actual_tool`, prompt-delivery/readback state, receipt-guard result, current cursor/status, artifact/validation receipts, or an exact structured failure. Spark returns bounded CLI output and no visible task.

Failure handling: Classify the exact failure with the dispatch guard. Retry only an eligible readback/title synchronization delay against the already identified non-Spark task; preserve every other failure receipt and stop or replace only under the declared worker-failure policy. A nonzero Spark wrapper exit overrides replacement policy and terminates that lane until a new explicit user request changes route. Never silently change route, scope, authority, executor, or create a second task by stripping a rejected parameter.

Tool stop rule: Stop after the requested handoff is delivered, the lane reaches its declared gate, a non-repairable blocker appears, the retry budget is exhausted, the user aborts, or the integrated run closes.

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
2. Read `references/execution-isolation.md` when lanes may overlap in time, use different harnesses, write files, run mutable tests, or transition from review to repair.
3. Define the final deliverable and one integration owner.
4. Build a dependency graph with exact read paths, write paths, mutable resources, file access, workspace mode, harness, workspace identity, base revision, expected outputs, validation, and handoff gates for every lane.
5. Decide independence before selecting concurrency. Dispatch all ready conflict-free lanes in the same wave; keep dependent waves serial.
6. Declare same-file, read/write, service, worktree, lockfile, and generated-output conflicts. Narrow scopes or serialize them; an integration owner does not make concurrent conflicting writes safe.
7. Route model and reasoning per lane, preserving explicit user choices.
8. Validate every route attempt with `scripts/validate_dispatch_route.py`, then validate a durable JSON plan with `scripts/validate_orchestration_plan.py`; after creation, bind every normalized visible-task receipt with `scripts/validate_visible_task_receipt.py --plan`, and validate each external launch with `scripts/validate_external_environment_receipt.py --plan`. Treat plan validation as declared-state checking, not proof of the tool actually called or the environment actually used.

Do not allocate workers from a fixed role list. Define lanes from the current goal and side effects. Multiple response-only reviewers may share one frozen input, while every unordered Git-backed writer needs a separately verified worktree. A reviewer becoming a writer is a new execution decision: re-plan its write scope and environment before sending any repair instruction.

Do not split a task merely to use more Agents. Keep tightly coupled work in one lane when decomposition would increase integration risk or duplicate context.

## Select each route

Read `references/model-routing.md` before automatic selection or when validating an explicit route. Check the live task-tool schema for visible routes because model names and supported reasoning pairs can change, but never let advertised Spark task capability override its bundled-CLI-only contract. Never silently downgrade, upgrade, or substitute an unsupported explicit choice.

## Build the handoff envelope

- For orchestrated dispatch, generate the recipient prompt from `references/internal-handoff-template.md`.
- For complete handoff, use `references/legacy-handoff-template.md`; the filename is retained for compatibility, but complete handoff is not deprecated.
- Include lane id, dependencies, declared file/resource scope, selected route and basis, integration owner, deliverables, validation, sync rule, and stop condition when orchestrating.
- Keep only verified current state, required materials, authority boundaries, risks, and the recipient's first action.
- Never dump full chat history, secrets, long logs, or unrelated backlog.

## Dispatch a visible task

Read `references/thread-dispatch.md` and use the live Codex task tools exclusively when the user requested visible work:

1. Validate that the lane is a `visible_thread` route; Spark fails this check and must go to the bundled CLI section.
2. Inspect the current visible-task surface, exact `create_thread` tool name, schema, project target, and supported model/reasoning pairs.
3. Put that exact tool in the dispatch attempt and pass the route guard before calling it.
4. Create every currently ready independent lane without waiting for another lane in that wave.
5. Normalize the returned receipt, pass `validate_visible_task_receipt.py`, and only then record its task id or queued client id; reject agent paths and subagent ids. On rejection, set the lane to `failed` with `invalid_visible_task_evidence`, never `created_unconfirmed`.
6. Set a concise title when supported and confirm prompt delivery from the receipt or readback. Retry only an eligible readback/title synchronization delay against the same task; never retry task creation by changing route fields.
7. Monitor with bounded task waits/readback and filesystem or artifact checks. Commentary alone is not completion.
8. Reconcile direct user-to-worker messages before the next dispatch; preserve the task's route on follow-up unless the user explicitly changes it.
9. Create dependent tasks just in time after their upstream artifact and validation gate passes.

Do not use `handoff_thread` to create a successor; it moves an existing task and Git state. Read `references/thread-dispatch.md` for tool contracts and failure handling.

## Maintain controller state and lifecycle

For a durable multi-task run, maintain `controller/plan.json`, `controller/thread-registry.md`, `controller/status.md`, and append-only `controller/router-log.jsonl` under the approved output root. Keep the Controller as the routing source of truth while allowing lane-local user/worker conversation.

Use explicit states for planned, ready, standby, queued/unconfirmed, running, needs input/fix, blocked, failed, aborted, succeeded pending integration, integrated, and archived. Log retries, replacements, user interventions, aborts, and archive receipts. Do not hide or overwrite failed history.

Archive visible tasks only when the user requests cleanup or an explicit run policy permits it after integration or acknowledged abandonment.

## Transfer phases

Start a downstream phase only after the named upstream artifact exists, is non-empty when file-based, passes its validation, and carries the required ready state. Rebuild the downstream prompt from the accepted artifact and freshly verified project state. Skip a design lane when an accepted current design already exists; do not skip its acceptance contract.

## Route Spark through the bundled CLI

Use Spark for bounded, mechanical, read-only work that benefits from independent classification or summarization but does not need final judgment.

- Execute the bundled `scripts/run-spark-cli.sh`; do not require the user or recipient to locate another skill.
- Fix the route to `gpt-5.3-codex-spark`, `xhigh`, ephemeral, and read-only.
- Let the wrapper isolate writable CLI runtime state in a private temporary `CODEX_HOME`; never grant the project or live user state database extra write access.
- Treat an explicit request to use Spark on named materials as authority for one minimally scoped provider call; request separate disclosure approval only when current project rules require it, the scope is ambiguous, or sensitive data would be sent. A pending or denied platform approval is a pre-dispatch stop, not a started Spark failure.
- Pass the bounded-input gate in `references/spark-cli-route.md` before provider execution. For large or minified records, prepare a compact structured evidence packet locally; never let Spark discover candidates by echoing whole JSON/JSONL records or by relying on a line-only `head` limit. The wrapper's per-tool output cap is a backstop, not a substitute for prefiltering; on success it returns only the final message, and on failure only bounded diagnostics plus the terminal marker.
- Disclose that this route creates no visible task.
- Do not call any visible-task create/fork/handoff API for Spark, regardless of what its schema advertises.
- Require the main agent to review findings and make all writes and final judgments.
- Stop on every nonzero wrapper exit and report the exact executor boundary accurately. The terminal marker forbids App fallback, model substitution, reasoning changes, and same-lane retry; only a new explicit user request may select another route. Do not add writable flags.

Read `references/spark-cli-route.md` before invoking Spark; it contains the integrated execution contract and portable applicability patterns.

## Consume a received handoff

Treat a received handoff as a routing map, not guaranteed current truth. Verify cheap volatile facts first, then continue from its first action. Do not reread an entire old conversation unless a required decision is missing.

## Produce a complete handoff

Use complete handoff for external agents and recipients without direct task/CLI capabilities. Include recipient capability, accessible versus inaccessible materials, verified progress, active dependency/lifecycle state, integration owner, validation, open risks, and one first action. Aim for 300–900 Chinese characters for pasteable chat text unless a durable file or fuller package is requested.

Use `scripts/make_handoff.py` for a Markdown scaffold and `references/legacy-handoff-template.md` for the complete field order. Preserve `text-only` and `file-only` as aliases.

## Close on product evidence

A lane is only ready for integration when its required output/receipt exists, lane validation passes, changed files and risks are reported, and its handoff state is explicit. The run succeeds only when the integration owner reconciles all required lanes and conflicts, full validation passes, stale/retried work is resolved, and the final deliverable is reported.

Using multiple Agents, creating tasks, or receiving plausible worker prose is never a success condition.

## Stop rules

- Do not silently replace an explicit executor or reasoning level.
- Do not dispatch, follow up, retry, or report Spark unavailable without a valid dispatch-guard receipt.
- Do not create a visible Spark task or downgrade `luna-max` on a follow-up.
- After `PROJECT_HANDOFF_SPARK_TERMINAL_FAILURE`, stop that lane and call no App task or model tool until the user explicitly requests a new route.
- Do not create a hidden subagent when a visible task was requested.
- Do not write `created_confirmed`, `created_unconfirmed`, or `queued` without a valid create-thread receipt containing the required real task identifier.
- Do not claim a task received work until readback or a creation receipt supports it.
- Do not call a model when complete handoff was requested.
- Do not parallelize lanes with undeclared or unresolved shared mutable state.
- Do not start downstream work before its upstream artifact gate passes.
- Do not mark a lane complete from chat text alone or mark a run complete before integration validation.
- Do not turn a candidate, audit, or handoff into installation, deployment, adoption, or publication authority.
