# Thread Dispatch Contract

Use these contracts when creating or coordinating visible Codex tasks. In this reference, a visible-task worker is a separate user-owned Codex task created through `create_thread`; it never means a collaboration subagent.

## Contents

1. Live surface and project target
2. Create, title, read, wait, message, and archive tools
3. Single-task and multi-lane lifecycles
4. Failure and replacement rules
5. Receipt binding and shape

## Resolve the live surface and project target

Inspect the current task-tool names and schemas before planning dispatch. Tool names, project-target shapes, model ids, reasoning fields, host ids, and readiness receipts may change.

Validate the route attempt with `scripts/validate_dispatch_route.py` before selecting a tool.

- Use `list_projects` before project-scoped creation when that tool exists.
- If the live `create_thread` schema resolves a verified workspace/project target directly, follow that schema instead of inventing an obsolete lookup step.
- Match the user-provided or currently verified path unambiguously. Never guess a project id, host, checkout, or worktree.
- Do not create a projectless task as a fallback unless the user authorized projectless execution.
- If the surface lacks visible-task creation, produce a complete portable handoff. Do not silently substitute a hidden subagent.

## Visible-task exclusivity

- For any supported model initial dispatch, call the live tool whose leaf name is `create_thread`.
- Never call `spawn_agent`, `collaboration.spawn_agent`, or another hidden-subagent API for a `visible_thread` route. Never treat `subAgentActivity`, `/root/<agent>`, `agentPath`, or `agentThreadId` as task creation evidence.
- Do not apply a hidden-subagent concurrency-slot limit to visible tasks. Use only the live visible-task capacity and the user's cap.
- Put the exact planned tool name in the route attempt before calling it and retain the route validator's `attempt_sha256`. After the call, put the exact actual tool name, actual route-sensitive arguments, and attempt hash in a normalized receipt, then run `scripts/validate_visible_task_receipt.py RECEIPT --dispatch-attempt ATTEMPT`.
- If either guard fails, set the lane to `failed` with classification `invalid_visible_task_evidence`, record the exact evidence, and stop that dispatch. Do not use `created_confirmed`, `created_unconfirmed`, or `queued`.

Visible-task authority and field authority are separate. A user who only invokes `$project-handoff`, triggers it implicitly, or says “创建任务” authorizes no model/reasoning override. Validate `requested_route=platform-default`, then omit both `model` and `thinking`. A raw explicit value controls only its axis and is retained in `requested_model` or `requested_reasoning`; the documented model-only names Astra/GPT6 resolve to `gpt-6-astra` without selecting reasoning; an explicit alias binds both documented axes; explicit `auto` authorizes classification only on the named axis.

## `create_thread`

- **Purpose**: Create a separate, user-owned Codex task.
- **Use when**: The user explicitly asks for a new/visible task, names a dispatch pipeline, or invokes a documented `$project-handoff` dispatch mode.
- **Do not use when**: The user asks only for an explanation, complete handoff artifact, or current-task answer.
- **Parameters**:
  - `prompt`: generated internal handoff envelope;
  - `target`: resolved project/projectless target and allowed environment;
  - `model` and `thinking`: include only fields present in the route validator's `create_thread_arguments`. Omit each field whose basis is `platform_default`; never substitute a Skill-selected value for an omitted axis.
- **Return**:
  - ready creation: `threadId` and `hostId`;
  - queued worktree setup: `clientThreadId`.
- **Postcondition**: Normalize the raw return as the receipt shape below, bind it to the exact attempt file, and require `scripts/validate_visible_task_receipt.py RECEIPT --dispatch-attempt ATTEMPT` to report `valid: true` before registration.
- **Failure handling**: An unsupported parameter, invalid request, permission/auth/quota failure, or provider/model failure is not a synchronization delay and must not be retried by stripping or changing route fields. When creation returns an ambiguous result, inspect current task state before considering any new create call. Do not silently use a hidden subagent.
- **Stop rules**:
  - Do not pass a `clientThreadId` to tools requiring a `threadId`.
  - Do not claim prompt acceptance from creation alone when the receipt does not cover delivery and readback is available.
  - Treat every created task as user-owned and visible in the task list.

## `set_thread_title`

- **Purpose**: Give the visible task a concise, user-scannable title.
- **Use when**: A ready `threadId` exists.
- **Do not use when**: Only a queued `clientThreadId` exists.
- **Failure handling**: Preserve the created task and report the title failure; title failure does not erase creation.

## `read_thread`

- **Purpose**: Confirm the task exists, inspect recent state, and verify that it received the initial prompt.
- **Use when**: Focused readback is needed after ready creation, after a direct user-to-worker intervention, or during a dependency/failure check.
- **Return**: Recent task status and turn summaries.
- **Failure handling**: Retry one likely synchronization delay once.
- **Stop rule**: Keep state `created_unconfirmed` when readback still fails.

## `wait_threads`

- **Purpose**: Wait for one or more visible tasks to complete or request attention.
- **Use when**: One or more dispatched lanes are running or a pipeline must wait for upstream results.
- **Do not use when**: No task is running and no downstream dependency exists.
- **Parameters**: Use the live target shape, including host id and an up-to-date cursor when required. Prefer one bounded wait for the current ready wave over repeated full task reads.
- **Failure handling**: Preserve each target's last cursor and report target-specific failures.
- **Stop rule**: Do not interpret commentary or a timeout snapshot as completion; verify final task state and required artifacts.

## `send_message_to_thread`

- **Purpose**: Continue or correct an existing visible task.
- **Use when**: The worker needs a scoped correction, user intervention must be synchronized, a downstream gate failed, or a running lane must pause/abort.
- **Do not use when**: Creating the initial task.
- **Failure handling**: Do not duplicate the same follow-up after an uncertain send without checking the task.
- **Route rule**: Preserve the task's effective model/reasoning route. Do not pass a new model or `thinking` value unless the user explicitly requested that route change; in particular, keep `luna-max` at `max`.
- **Retired automatic route**: For an existing GPT-5.6 Sol/Luna/Terra task, verify the task id and original effective route from readback and its historical receipt before declaring `route_changed=false`. The offline guard's compatibility allowance validates that declaration only; it does not establish task existence or original routing. Use its original effective model/effort, including when its historical alias has since changed meaning. This exception never authorizes new automatic GPT-5.6 creation or migration to GPT-6.

## `set_thread_archived`

- **Purpose**: Archive a visible task without deleting its evidence.
- **Use when**: The user requests cleanup or an explicit run policy permits archival after integration or acknowledged abandonment.
- **Do not use when**: A failure is unresolved, evidence is still needed, or cleanup authority is absent.
- **Failure handling**: Record the failure; archival failure does not change the lane's substantive state.

## Do not use `handoff_thread` for creation

`handoff_thread` moves another existing task and its Git state between a checkout, worktree, or host. It does not create a successor conversation.

## Single-task lifecycle

1. Verify state and authority.
2. Resolve the live project target.
3. Select the route, write its dispatch-attempt receipt, and require `valid: true` from `scripts/validate_dispatch_route.py`. Preserve its exact `create_thread_arguments` and omitted-field list.
4. Generate internal prompt.
5. Create the task without adding any omitted model/thinking field.
6. Normalize and validate the real creation receipt against the exact pre-dispatch attempt and argument projection.
7. Set title.
8. Confirm delivery from the receipt or read back once.
9. Return task receipt.

Before closing dispatch-only, also satisfy any initial progress wait/readback required by the live host. This ends the dispatch request, not the worker's substantive work. If the user requested completion, monitoring, or integration, continue bounded waits and verify the lane's declared outputs and checks before reporting that result complete.

## Multi-lane lifecycle

1. Build and validate the dependency graph, scopes, conflict declarations, routes, and integration owner.
2. Create all currently ready, conflict-free lanes in one wave, within the live concurrency cap.
3. Validate every real creation receipt, then immediately record each ready task id or queued client id, actual tool, role, dependencies, route, expected outputs, and last cursor/time.
4. Wait on the wave with bounded calls while keeping target-specific cursors.
5. Reconcile final task state, direct user-to-worker changes, output artifacts, and lane validation.
6. Mark a passed lane `succeeded_pending_integration`; keep missing or failed gates in `needs_fix`, `blocked`, `failed`, or `aborted`.
7. Create each dependent lane just in time from freshly verified upstream artifacts.
8. Let only the integration owner reconcile cross-lane changes, run all declared integration checks applicable to the final deliverable, and mark work `integrated`.
9. Archive only under the explicit lifecycle rule above.

## Failure and replacement rules

- The one synchronization retry is a whitelist, not a general second attempt. It covers only reading an already identified task after a classified creation-visibility or prompt-readback delay, or retrying title metadata after a title delay.
- `unsupported_parameter`, `invalid_request`, unsupported model/reasoning, permission, authentication, quota, and provider/model failures must not be retried under that allowance.
- Never create a second task because the first request rejected `reasoning.summary`, `thinking`, or another parameter. Removing or changing the parameter is a route mutation, not synchronization recovery.
- Before a worker retry, record the failure, artifacts, validation, attempted correction, and remaining retry budget.
- Continue the existing task when its context and outputs remain safe; otherwise create a replacement only after marking the old task superseded and its unintegrated outputs stale.
- Never change model, reasoning, scope, project target, or authority silently to make a retry pass.
- On abort, stop downstream dispatch, notify running lanes when possible, preserve receipts/artifacts, and invalidate dependent gates.
- Do not claim success because task creation, messaging, or multi-Agent usage succeeded.

## Receipt binding and shape

Write one normalized JSON receipt from the actual `create_thread` result and validate it together with the exact pre-dispatch attempt before updating registry/status/log. The validator rejects hidden-subagent tools and fields, path-like ids, missing ready ids, false confirmation states, a changed tool/route/attempt hash, and any actual argument that differs from the route validator's exact projection. That exact comparison also rejects injection of a field listed in `omitted_create_thread_fields`. This syntactic guard does not replace app readback when readback is available.

Required creation-receipt fields:

~~~yaml
actual_tool: codex_app__create_thread
status: created_confirmed | created_unconfirmed | queued | failed
surface: visible_thread
requested_route: astra-high | astra-max | astra-ultra | sol-max | sol-medium | terra-max | luna-max | <supported visible route>
dispatch_attempt_sha256: <64 lowercase hex from the route validator>
actual_create_thread_arguments: <exact arguments actually passed; may be {}>
task_kind: codex
thread_id: <ready task id or null>
client_thread_id: <queued client id or null>
host_id: <ready host id or null>
prompt_verified: receipt | readback | false
failure: <message or null>
~~~

Do not include `agentPath`, `agentThreadId`, `agent_path`, or `agent_thread_id`.

Controller registry/receipt fields:

~~~yaml
run_id:
lane_id:
status: created_confirmed | created_unconfirmed | queued | failed | aborted | archived
actual_tool:
task_kind: codex
thread_id:
client_thread_id:
host_id:
title:
project_id:
requested_route:
requested_model: <raw explicit model or null>
requested_reasoning: <raw explicit reasoning or null>
model:
reasoning:
surface:
model_basis: explicit_user | explicit_skill_route | explicit_auto | platform_default
reasoning_basis: explicit_user | explicit_skill_route | explicit_auto | platform_default
create_thread_arguments:
omitted_create_thread_fields:
dispatch_attempt_sha256:
actual_create_thread_arguments:
dispatch_guard_valid:
receipt_guard_valid:
prompt_verified: receipt | readback | false
attempt:
last_cursor:
next_gate:
failure:
failure_class:
failure_disposition:
~~~

## Verify effective reasoning before sending

A generic tool parameter enum is not evidence that every listed effort works with every model. The currently observed GPT-6 Astra, Sol, and Luna pairs reject `none` and `minimal`; Luna also excludes `ultra`. When a destination task is known, read its current model/effort before forwarding, particularly after switching models or receiving an unsupported-value error. Global configuration does not prove a task override is compatible. Record observed state in the route's optional `destination_state` object (`model`, `reasoning`, and a model-specific `supported_reasoning` list when actually observed). The validator checks inherited values as well as explicit overrides without converting platform-default axes into tool arguments. If destination state is unavailable, record that compatibility is unverified; do not claim the route guard checked a hidden default.

For a provider error, retain its actual supported list: it takes precedence over a broader tool advertisement for that destination. For example, an Astra destination advertising only low/medium/high/xhigh/max cannot accept ultra even if a generic tool schema lists it. Do not silently rewrite an explicitly requested alias.

If the user asks to fix an invalid inherited effort, restore that task's last verified supported effort (for example medium), keeping the model and substantive request unchanged. This targeted repair is authorized by the repair request; do not change all tasks or global defaults. Verify the corrected effective turn from task readback. An erroring turn that never ran is not evidence its business action was completed. Before resuming externally visible actions, reread their actual state to avoid duplicates. Ordinary unsupported-parameter errors still do not authorize repeated new tasks or silent route changes.

ChatGPT-to-Codex built-in forwarding is outside this repository. Updating this Skill guards callers that use it; it cannot patch the app's internal forwarding implementation. If that bridge injects an invalid effort, pass a supported explicit effort through an available authorized task API or correct the destination UI setting. Report app-layer recurrence separately instead of claiming a Skill edit repaired the bridge.


## Diagnose a GPT-6 max validation error

`create_thread` uses `model` and **`thinking`**. Pass `thinking="max"` for the three max aliases; do not translate this to `effort` or `reasoning.effort` on this tool. Those names belong to other interfaces. The installed standalone CLI and the Desktop task service can use different binaries, versions, and model catalogs.

1. Preserve the exact error, tool name, target host, attempted model/thinking, and current schema. A “could not validate reasoning effort max” error is `unsupported_parameter` (request/capability validation), not a demonstrated unavailable model.
2. Check the selected host's actual task-service runtime and model-specific capability evidence. Use local code/version/catalog inspection first; do not infer Desktop support from the standalone `codex --version`, an unrelated CLI success, UI selection, a generic effort enum, or a model's self-description.
3. If the current tool advertises the exact pair, an authorized smoke test may create one minimal task with that unchanged pair, then verify creation, prompt delivery, and completed output separately. A live rejection takes precedence over the static advertisement for that attempt.
4. Diagnose mismatched/outdated metadata or unavailable capability evidence. Do not patch installed app internals, update/restart the app, or change global defaults as a side effect of editing this Skill. Follow the user's separate authority for runtime repair.
5. Stop repeated creation on a parameter error. After a verified relevant runtime fix and authorization to retest, check whether any task was created before making one new test with the same exact model/thinking. Record it as a post-fix test, not a synchronization retry. Without that fix, report the unresolved tool validation boundary; never silently swap models, omit `thinking`, or substitute a subagent/CLI.

A successful creation receipt proves the tool accepted the request. A completed marker from the task additionally proves the turn ran. Neither proves arbitrary complex work quality. If the runtime does not expose its effective model/effort, report the accepted requested pair and that readback limit rather than claiming independent server-model verification.
