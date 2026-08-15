# Orchestration Control

Use this contract when a handoff contains multiple lanes, visible tasks, parallel work, or a gated phase transfer. The current task remains the Controller unless the user explicitly assigns that role elsewhere.

In a visible-task run, `worker` means a separate user-owned Codex task created through `create_thread`. It never means `spawn_agent`, a collaboration subagent, or an agent path.

## Contents

1. Run boundary
2. Dependency graph and lane contract
3. Independence and concurrency
4. Write conflicts and integration ownership
5. Controller records
6. Worker and user synchronization
7. Failure, retry, abort, and archive lifecycle
8. Completion and integration gates
9. Boundary examples
10. Deterministic plan validation

## 1. Run boundary

- Keep one Controller responsible for global routing, dependency changes, route changes, reconciliation, and final integration.
- Give each worker one bounded lane. A worker may report lane-local facts and request clarification, but must not create unrelated lanes or declare the whole run successful.
- Treat visible Codex tasks as user-owned tasks. Create them only when the user explicitly requests dispatch or invokes a documented dispatch mode.
- Create visible workers only through the live `create_thread` tool and validate the real creation receipt. Hidden-subagent capacity, activity, paths, and ids are outside this lifecycle.
- Keep model choice separate from file-write, provider-call, deployment, publication, installation, and formal-adoption authority.
- Use a single-task receipt instead of controller files when the run has only one short-lived lane and no later handoff.

## 2. Dependency graph and lane contract

Build the graph before dispatching workers. An edge `B depends_on A` means B cannot start until A's named artifact and gate are verified. Declare one run-level `integration_owner` as either the Controller or one final integration lane.

For every lane, declare:

| Field | Meaning |
|---|---|
| `id` | Stable lane identifier |
| `goal` | One current result, not a backlog |
| `depends_on` | Hard prerequisite lane ids |
| `read_paths` | Exact read-only inputs |
| `write_paths` | Exact writable files or narrow directories |
| `mutable_resources` | Shared ports, databases, devices, worktrees, services, or build state |
| `expected_outputs` | Artifacts or receipts needed by the gate |
| `validation` | Exact command or evidence rule |
| `route` | Requested route, selected model, reasoning, surface, and the basis for each field |

Route each lane after its scope and dependencies are known. Do not select one executor for an entire mixed run merely because the first lane fits it.

Use this machine-checkable shape when a durable plan is useful:

~~~json
{
  "run_id": "sync-v2",
  "integration_owner": "controller",
  "lanes": [
    {
      "id": "design",
      "goal": "Produce the accepted protocol design.",
      "depends_on": [],
      "read_paths": ["docs/requirements.md"],
      "write_paths": ["docs/specs/protocol-v2.md"],
      "mutable_resources": [],
      "expected_outputs": ["docs/specs/protocol-v2.md"],
      "validation": "test -s docs/specs/protocol-v2.md",
      "route": {
        "requested_route": "sol-max",
        "model": "gpt-5.6-sol",
        "reasoning": "max",
        "surface": "visible_thread",
        "model_basis": "auto_unspecified",
        "reasoning_basis": "auto_unspecified"
      }
    }
  ]
}
~~~

Allowed route bases are `explicit_user`, `auto_requested`, and `auto_unspecified`. Record model and reasoning bases separately so a user-selected model is never replaced merely because reasoning was left automatic, and vice versa. `requested_route` binds alias semantics: `spark` requires the bundled CLI at `xhigh`, while `luna-max` requires a visible Luna task at `max`.

## 3. Independence and concurrency

Two lanes are independent only when all of these are true:

1. Neither consumes an output or decision from the other.
2. Their declared writes do not overlap.
3. Neither reads a path while the other may mutate the same path unless a dependency orders them.
4. They do not share mutable resources such as one port, test database, device, worktree, lockfile, generated tree, or mutable service.
5. Each can succeed from a self-contained prompt without learning the other worker's intermediate reasoning.

Dispatch every currently ready, conflict-free lane as one concurrency wave, limited only by the user's cap and the live visible-task surface's safe capacity. Do not import a separate hidden-subagent slot limit. Do not wait for one independent lane before creating the next. Keep dependent waves serial and create downstream tasks just in time from freshly verified upstream artifacts.

Read-only access to the same immutable inputs is normally safe in parallel. Shared working directories are not proof of safety: declared file scopes and mutable resources decide.

## 4. Write conflicts and integration ownership

Treat the following as conflicts unless an explicit dependency serializes them:

- the same file or one path containing another lane's write path;
- a writer and reader of the same generated or mutable path;
- shared lockfiles, manifests, indexes, migrations, snapshots, or generated outputs;
- the same database, local service, port, simulator, device, or non-isolated build state.

For every conflict, record the affected lanes, paths/resources, chosen order, and integration owner. Resolve it by narrowing scopes, serializing lanes, or using an explicitly authorized isolated worktree/environment. Never assume that naming an integration owner makes concurrent same-file writes safe.

The integration owner is the only actor allowed to reconcile cross-lane changes, resolve collisions, run the full validation surface, and declare the integrated result. When the owner is a worker lane, that lane must depend on every lane whose output it integrates. Otherwise keep the Controller as owner.

## 5. Controller records

For a durable multi-task run, create these files under the user-approved output root, not under read-only source or input trees:

- `controller/plan.json` — dependency graph, scopes, routes, expected outputs, and integration owner.
- `controller/thread-registry.md` — lane, visible task id, title, host, status, dependencies, route, expected outputs, and last sync cursor/time.
- `controller/status.md` — current wave, ready queue, running lanes, blockers, invalidated gates, next action, and integration state.
- `controller/router-log.jsonl` — append-only dispatch, message, retry, user intervention, gate, abort, archive, and integration events.

Normalize the actual `create_thread` result and require `scripts/validate_visible_task_receipt.py` to pass before recording creation. Record the exact `actual_tool`, `thread_id` plus `host_id`, or queued `client_thread_id`; never record `/root/<agent>`, `agentPath`, `agentThreadId`, or subagent activity. Never pass a queued client id to a tool that requires a ready task id.

Each router-log line should contain at least:

~~~json
{"at":"2026-08-07T12:00:00+08:00","run_id":"sync-v2","lane":"design","event":"dispatch","attempt":1,"result":"created_confirmed","receipt":{"actual_tool":"codex_app__create_thread","thread_id":"019...","host_id":"local","receipt_guard_valid":true}}
~~~

Append events; do not rewrite history to make a retry or failure disappear. `status.md` is the current snapshot, while the log is the event record.

## 6. Worker and user synchronization

Controller to worker:

- Send one self-contained RUN envelope with exact inputs, outputs, authority, route, validation, and stop rules.
- Send a correction only after reading the latest worker state. Do not duplicate an uncertain RUN or correction.
- When the global goal changes, pause or abort affected lanes, invalidate stale downstream gates, update the graph, and then send scoped replacements.

Worker to Controller:

- Reconcile task state and filesystem artifacts; chat text alone is not completion evidence.
- Record changed files, validation, risks, and the lane's requested next state.
- Carry forward only verified outputs. Mark replaced or superseded outputs stale until revalidated.

User to either side:

- The user may message the Controller or a worker directly.
- Before the next dispatch, read every directly changed worker since its last cursor/time, record the intervention, update registry/status, and re-evaluate affected gates.
- A worker-side user message may change that lane, but it does not silently change global routing, other lanes, or integration authority.

## 7. Failure, retry, abort, and archive lifecycle

Use explicit states:

`planned -> ready|standby -> queued|created_unconfirmed|running -> needs_input|needs_fix|blocked|failed|aborted|succeeded_pending_integration -> integrated -> archived`

- `created_unconfirmed`: creation returned an id but prompt/task readback is not yet available.
- `needs_fix`: the worker stopped, but an expected artifact or validation gate failed.
- `succeeded_pending_integration`: the lane gate passed, but the integration owner has not closed the run gate.
- `integrated`: the integration owner reconciled the lane into the required product and reran the integration validation.

Retry rules:

1. Retry only a classified creation-visibility, prompt-readback, or title-metadata delay, and only by reading the already identified task or retrying its title metadata. Validate the retry receipt with `scripts/validate_dispatch_route.py`.
2. Set a run-specific retry budget for worker failures. When none is stated, allow one scoped correction for a plausibly repairable failure; do not loop on the same failure class.
3. Before retrying, capture the failure, current artifacts, attempted fix, and whether the existing task can continue safely.
4. If a replacement task is required, mark the old task superseded and its unintegrated outputs stale; give the replacement a fresh prompt from current state.
5. Never change model, reasoning, scope, or authority silently as a retry tactic.
6. `unsupported_parameter`, `invalid_request`, unsupported route, permission, authentication, quota, and provider/model failures are not synchronization delays. Do not create a second task by omitting or changing reasoning.

Abort rules:

- Stop new dispatches, notify running workers when the tool supports it, mark affected lanes `aborted`, and invalidate their downstream gates.
- Preserve artifacts and receipts for review. Abort is not success and does not imply deletion.

Archive rules:

- Archive visible tasks only when the user requests cleanup or an explicit run policy permits it after integration or acknowledged abandonment.
- Record the archive result. A failed archive does not change the task's substantive status.
- Do not archive away evidence needed to understand an unresolved failure.

## 8. Completion and integration gates

A lane reaches `succeeded_pending_integration` only when:

1. the worker has stopped or returned a final lane result;
2. every required artifact/receipt exists and is non-empty when file output is required;
3. lane validation passes;
4. changed files and remaining risks are reported;
5. the handoff state required by downstream lanes is explicit.

The run succeeds only when:

1. every required lane is integrated, or an omitted/aborted lane is explicitly accepted by the user;
2. the integration owner has reconciled all changes and write conflicts;
3. full integration validation passes;
4. no required dependency, retry, user intervention, or stale output remains unresolved;
5. the final deliverable and task receipts are reported.

Creating many tasks, receiving fluent worker responses, or saying “used multiple Agents” satisfies none of these gates by itself.

## 9. Boundary examples

| Situation | Decision |
|---|---|
| Two read-only audits inspect the same frozen inputs and write separate reports | Parallel; shared immutable reads are safe |
| Implementation consumes an accepted design artifact | Serial; implementation depends on the design gate |
| Two workers both edit `src/app.py` | Conflict; narrow scopes or serialize, with one integration owner |
| Frontend and backend edits are disjoint but both may rewrite one lockfile | Not independent until lockfile ownership is separated or ordered |
| Two reviewers return response-only findings while one Controller later writes the decision | Parallel reviewers; Controller owns synthesis and all writes |

## 10. Deterministic plan validation

Use both bundled validators after semantic decomposition and before dispatch. Validate each single dispatch/follow-up/retry receipt first:

~~~sh
python3 <skill-root>/scripts/validate_dispatch_route.py /absolute/path/to/dispatch-attempt.json --format json
~~~

Then validate the full plan:

~~~sh
python3 <skill-root>/scripts/validate_orchestration_plan.py /absolute/path/to/controller/plan.json --format json
~~~

The plan validator checks required fields, lane ids, dependency existence, cycles, requested-route/model/reasoning/surface compatibility, route-basis recording, integration ownership, read/write overlap, write/write overlap, and shared mutable resources. It returns topological concurrency waves for a valid plan and exits nonzero for an unsafe or malformed plan.

The validator can only check declared state. The Controller remains responsible for discovering omitted dependencies, implicit shared resources, semantic coupling, actual tool capacity, and whether the proposed lanes are useful.
