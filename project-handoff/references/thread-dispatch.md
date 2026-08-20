# Thread Dispatch Contract

Use these contracts when creating or coordinating visible Codex tasks. In this reference, a visible-task worker is a separate user-owned Codex task created through `create_thread`; it never means a collaboration subagent. Spark is outside this surface and must use the bundled CLI route.

## Contents

1. Live surface and project target
2. Create, title, read, wait, message, and archive tools
3. Single-task and multi-lane lifecycles
4. Failure and replacement rules
5. Receipt binding and shape

## Resolve the live surface and project target

Inspect the current task-tool names and schemas before planning dispatch. Tool names, project-target shapes, model ids, reasoning fields, host ids, and readiness receipts may change.

A tool advertising `gpt-5.3-codex-spark` describes capability, not authorization. Never create, fork, hand off, message, or retry a visible Spark task. Validate the route attempt with `scripts/validate_dispatch_route.py` before selecting a tool.

- Use `list_projects` before project-scoped creation when that tool exists.
- If the live `create_thread` schema resolves a verified workspace/project target directly, follow that schema instead of inventing an obsolete lookup step.
- Match the user-provided or currently verified path unambiguously. Never guess a project id, host, checkout, or worktree.
- Match the lane's validated `file_access` and `workspace_mode`. For unordered writers in one Git repository, request worktrees; for shared read-only reviewers, local execution is allowed only on the one frozen base recorded in the plan.
- Do not create a projectless task as a fallback unless the user authorized projectless execution.
- If the surface lacks visible-task creation, produce a complete portable handoff. Do not silently substitute a hidden subagent.
- External harnesses do not use this visible-task receipt. Keep them on `portable_handoff` and require `scripts/validate_external_environment_receipt.py --plan` before `running`.

## Visible-task exclusivity

- For Sol, Terra, and Luna initial dispatch, call the live tool whose leaf name is `create_thread`.
- Never call `spawn_agent`, `collaboration.spawn_agent`, or another hidden-subagent API for a `visible_thread` route. Never treat `subAgentActivity`, `/root/<agent>`, `agentPath`, or `agentThreadId` as task creation evidence.
- Do not apply a hidden-subagent concurrency-slot limit to visible tasks. Use only the live visible-task capacity and the user's cap.
- Put the exact planned tool name in the route attempt before calling it. After the call, put the exact actual tool name and normalized raw receipt in a receipt file and run `scripts/validate_visible_task_receipt.py`.
- If either guard fails, set the lane to `failed` with classification `invalid_visible_task_evidence`, record the exact evidence, and stop that dispatch. Do not use `created_confirmed`, `created_unconfirmed`, or `queued`.

## `create_thread`

- **Purpose**: Create a separate, user-owned Codex task.
- **Use when**: The user explicitly asks for a new/visible task, names a dispatch pipeline, or invokes a documented `$project-handoff` dispatch mode.
- **Do not use when**: The user asks only for an explanation, complete handoff artifact, or current-task answer; or the route is Spark.
- **Parameters**:
  - `prompt`: generated internal handoff envelope;
  - `target`: resolved project/projectless target and allowed environment;
  - `model` and `thinking`: explicit or authorized automatic route.
- **Return**:
  - ready creation: `threadId` and `hostId`;
  - queued worktree setup: `clientThreadId`.
- **Postcondition**: Normalize the raw return as the receipt shape below and require `scripts/validate_visible_task_receipt.py` to report `valid: true` before registration.
- **Environment postcondition**: A queued worktree may be registered but is not execution-ready. Before a lane writes, read back the task and Git state; require the normalized receipt to prove `worktree_source`, the linked worktree's own Repository Root, workspace path, frozen base, clean pre-write status, and distinct Git/common directories. For a same-source concurrency wave, update the plan with every writer's actual paths and rerun plan validation before authorizing any writer in that wave.
- **Failure handling**: An unsupported parameter, invalid request, permission/auth/quota failure, or provider/model failure is not a synchronization delay and must not be retried by stripping or changing route fields. When creation returns an ambiguous result, inspect current task state before considering any new create call. Do not silently use a hidden subagent.
- **Stop rules**:
  - Do not pass a `clientThreadId` to tools requiring a `threadId`.
  - Do not claim prompt acceptance from creation alone when the receipt does not cover delivery and readback is available.
  - Do not mark a task `running` or send a write instruction while `environment_verified` is false.
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
- **Execution rule**: A follow-up that changes `file_access=read_only` into file repair is not an ordinary continuation. Re-plan write paths and mutable resources, wait for other readers or move to a verified worktree, then validate the revised environment before sending repair instructions. The dispatch-attempt receipt must include `prior_file_access`, `requested_file_access`, `plan_guard_valid`, and `environment_guard_valid`; unsupported fields are rejected rather than ignored.

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
3. Select the route, write its dispatch-attempt receipt, and require `valid: true` from `scripts/validate_dispatch_route.py`.
4. Generate internal prompt.
5. Create task.
6. Normalize and validate the real creation receipt, including requested file access, workspace mode, and environment.
7. Set title.
8. Confirm prompt delivery and read back actual environment. Keep the task non-running when the environment remains unverified.
9. For a Git write lane, verify the worktree path and base revision before authorizing writes.
10. Return task receipt.

## Multi-lane lifecycle

1. Build and validate the dependency graph, scopes, conflict declarations, routes, and integration owner.
2. Create all currently ready, conflict-free lanes in one wave, within the live concurrency cap.
3. Validate every real creation receipt, then immediately record each ready task id or queued client id, actual tool, harness, planned and actual environment, dependencies, route, expected outputs, and last cursor/time.
4. Wait on the wave with bounded calls while keeping target-specific cursors.
5. Reconcile final task state, direct user-to-worker changes, output artifacts, and lane validation.
6. Mark a passed lane `succeeded_pending_integration`; keep missing or failed gates in `needs_fix`, `blocked`, `failed`, or `aborted`.
7. Create each dependent lane just in time from freshly verified upstream artifacts.
8. Let only the integration owner reconcile cross-lane changes, run full validation, and mark work `integrated`.
9. Archive only under the explicit lifecycle rule above.

## Failure and replacement rules

- The one synchronization retry is a whitelist, not a general second attempt. It covers only reading an already identified task after a classified creation-visibility or prompt-readback delay, or retrying title metadata after a title delay.
- `unsupported_parameter`, `invalid_request`, unsupported model/reasoning, permission, authentication, quota, and provider/model failures must not be retried under that allowance.
- Never create a second task because the first request rejected `reasoning.summary`, `thinking`, or another parameter. Removing or changing the parameter is a route mutation, not synchronization recovery.
- Before a worker retry, record the failure, artifacts, validation, attempted correction, and remaining retry budget.
- Continue the existing task when its context and outputs remain safe; otherwise create a replacement only after marking the old task superseded and its unintegrated outputs stale.
- Never change model, reasoning, scope, project target, or authority silently to make a retry pass.
- A replacement policy for a worker failure does not legalize an invalid route. An incorrect visible Spark attempt is preserved as invalid-route evidence; any still-authorized Spark work starts once through the validated bundled CLI, never as a visible replacement.
- On abort, stop downstream dispatch, notify running lanes when possible, preserve receipts/artifacts, and invalidate dependent gates.
- Do not claim success because task creation, messaging, or multi-Agent usage succeeded.

## Receipt binding and shape

Write one normalized JSON receipt from the actual `create_thread` result and validate it before updating registry/status/log. The validator rejects hidden-subagent tools and fields, path-like ids, missing ready ids, and false confirmation states; rejected evidence is `failed / invalid_visible_task_evidence`. This syntactic guard does not replace app readback when readback is available.

Required creation-receipt fields:

~~~yaml
actual_tool: codex_app__create_thread
run_id: <controller run id>
lane_id: <lane id>
harness: codex
status: created_confirmed | created_unconfirmed | queued | failed
surface: visible_thread
requested_route: sol-max | terra-max | luna-max | <supported visible route>
task_kind: codex
file_access: read_only | write
workspace_mode: shared_checkout | worktree | non_git
requested_environment: local | worktree
actual_environment: local | worktree | pending | unknown
environment_verified: receipt | readback | false
worktree_source: <source Repository Root or null>
repository_root: <absolute path or null>
workspace_path: <absolute path or null>
base_revision: <full commit for Git, verified content-state digest for non-Git, or null>
environment_evidence: <null, or exactly one mode-specific shape below>
thread_id: <ready task id or null>
client_thread_id: <queued client id or null>
host_id: <ready host id or null>
prompt_verified: receipt | readback | false
failure: <message or null>
~~~

For a confirmed Git worktree, use exactly this evidence shape; a shared checkout uses the same fields with `worktree_source: null` and equal `git_dir` / `git_common_dir`:

~~~yaml
environment_evidence:
  verified_by: git_readback
  worktree_source: <absolute source Repository Root>
  repository_root: <actual linked-worktree Git top-level>
  workspace_path: <actual execution directory inside that root>
  base_revision: <full commit>
  git_dir: <absolute per-worktree Git directory>
  git_common_dir: <absolute shared Git directory>
  head_revision: <same full commit before writes>
  working_tree_clean: true
~~~

For confirmed non-Git execution, use exactly:

~~~yaml
environment_evidence:
  verified_by: snapshot_readback
  worktree_source: null
  repository_root: null
  workspace_path: <absolute execution directory>
  base_revision: <snapshot:sha256 digest>
  content_state_verified: true
~~~

Do not include `agentPath`, `agentThreadId`, `agent_path`, or `agent_thread_id`.

Controller registry fields only (do not pass this superset to the receipt validator):

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
model:
reasoning:
surface:
file_access:
workspace_mode:
requested_environment:
actual_environment:
environment_verified:
worktree_source:
repository_root:
workspace_path:
base_revision:
environment_evidence:
model_basis:
reasoning_basis:
dispatch_guard_valid:
receipt_guard_valid:
prompt_verified: receipt | readback | false
attempt:
last_cursor:
next_gate:
failure:
failure_class:
failure_disposition:
spark_unavailable_supported:
~~~
