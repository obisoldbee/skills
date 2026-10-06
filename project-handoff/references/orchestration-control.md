# Orchestration Control

Use this contract for requested handoff or visible-task orchestration with multiple lanes or a gated phase transfer. Ordinary task decomposition or internal subagent collaboration alone does not select this visible-task workflow. The current task remains the Controller unless the user explicitly assigns that role elsewhere.

In a visible-task run, `worker` means a separate user-owned Codex task created through `create_thread`. It never means `spawn_agent`, a collaboration subagent, or an agent path.

`Executor` describes the task role, not a developer job title: workers may implement, research, review, operate tools, or perform scheduled observation. Apply result collection and quality criteria to the actual work; a recurring observer also has an ongoing monitoring responsibility beyond any one observation.

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
- Execution includes result collection and Controller quality review, even for a single lane. Use [result collection](result-collection.md) to choose short inline waits or verified event/scheduled follow-up. Only the user's explicit dispatch-only instruction transfers follow-up responsibility; a verified observer may take over waiting without closing the run.

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

Also bind the result reader, return location, next observation entry, and Controller acceptance criteria in the handoff and current record. The lane's executor validation does not replace Controller review. Assign mechanical checks to the selected capable observation executor first, then tune cadence; prefer the user's Luna-max monitoring policy over repeated Astra status checks. Record the exact check objective, real observer model/effort and automation binding, escalation conditions, and result return path. Short inline waits remain useful; neither a timer nor a separate reviewer is universally mandatory.

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
        "requested_route": "astra-max",
        "model": "gpt-6-astra",
        "reasoning": "max",
        "surface": "visible_thread",
        "model_basis": "explicit_skill_route",
        "reasoning_basis": "explicit_skill_route"
      }
    }
  ]
}
~~~

Allowed route bases are `explicit_user`, `explicit_skill_route`, `explicit_auto`, and `platform_default`. Record model and reasoning bases separately, and retain raw values as `requested_model` or `requested_reasoning`. Exact model IDs stay pinned; family names and aliases use the destination-catalog policy in `model-routing.md`. An alias binds both axes; explicit `auto` classifies only that axis; an unselected axis stays null and is omitted from `create_thread`. A bare Skill trigger or task-creation request uses `requested_route=platform-default`. Automatic model selection records verified `task_kind`: hardest reasoning uses Astra ultra, orchestration Astra high, writing/development Sol max, desktop operation Sol medium, simple browser/mechanical tasks Luna max. Current baseline Sol is GPT-6.1; keep the resolved catalog evidence in each lane route and preserve existing task pairs on continuation.

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

The integration owner is the only actor allowed to reconcile cross-lane changes, resolve collisions, run the declared integration validation applicable to the final deliverable, and declare the integrated result. When the owner is a worker lane, that lane must depend on every lane whose output it integrates. Otherwise keep the Controller as owner.

## 5. Controller records

For a durable multi-task run, create these files under the user-approved output root, not under read-only source or input trees:

- `controller/plan.json` — dependency graph, scopes, routes, expected outputs, and integration owner.
- `controller/thread-registry.md` — lane, visible task id, title, status, dependencies, route, expected outputs, result reader/return location, last sync cursor/time, and caller-specific write endpoint with its creation/delivery evidence. Record each direction separately; readable hosts are discovery hints, not replacement write endpoints.
- `controller/status.md` — current wave, ready queue, running lanes, received versions, pending quality reviews, acceptance evidence/decisions, blockers, invalidated gates, next action, and integration state.
- `controller/router-log.jsonl` — append-only dispatch, message, retry, user intervention, gate, abort, archive, and integration events.

Normalize the actual `create_thread` result and require `scripts/validate_visible_task_receipt.py RECEIPT --dispatch-attempt ATTEMPT` to pass before recording creation. Record the exact `actual_tool`, `actual_create_thread_arguments`, `dispatch_attempt_sha256`, `thread_id` plus `host_id`, or queued `client_thread_id`; never record `/root/<agent>`, `agentPath`, `agentThreadId`, or subagent activity. Never pass a queued client id to a tool that requires a ready task id.

Each router-log line should contain at least:

~~~json
{"at":"2026-08-07T12:00:00+08:00","run_id":"sync-v2","lane":"design","event":"dispatch","attempt":1,"result":"created_confirmed","receipt":{"actual_tool":"codex_app__create_thread","thread_id":"019...","host_id":"local","receipt_guard_valid":true}}
~~~

Append events; do not rewrite history to make a retry or failure disappear. `status.md` is the current snapshot, while the log is the event record.

## 6. Worker and user synchronization

Controller to worker:

- Send one self-contained RUN envelope with exact inputs, outputs, authority, route, validation, and stop rules.
- Name the result reader, return location, next check entry, and quality gate. Follow [result collection](result-collection.md): give a selected Luna-max observer a concrete mechanical goal and bounded inputs; leave substantive decisions and quality acceptance to the Controller. Verify the actual model/effort, automation owner, and result return/resume route. Avoid repeated unchanged reads, preserve cursors, back off, and keep unchanged checks quiet without waking Astra. Short waits may stay inline; a verified observer can take over long waits while the Controller ends the current turn as pending. Preserve explicit routes and task-creation authority.
- Send a correction only after reading the latest worker state. Do not duplicate an uncertain RUN or correction.
- When the global goal changes, pause or abort affected lanes, invalidate stale downstream gates, update the graph, and then send scoped replacements.

Worker to Controller:

- Reconcile task state and the required artifacts or response evidence; an unsupported self-report is not completion evidence. A response-only audit is assessed against its requested findings and verifiable sources, without creating unrequested files.
- Record changed files or response evidence, the exact candidate version, validation, risks, and the lane's requested next state. Return `result_ready` for a completed candidate; Controller receipt and quality acceptance are later facts.
- Save results before sending a hint. Distinguish collected, delivered and Controller received; message success is not receipt. Controller directly waits/reads the worker or saved result even when a reverse send fails. Follow [cross-device transport](cross-device-transport.md): unknown delivery remains unresolved until the original attempt is reconciled; a confirmed rejection requires the correct write endpoint before retry. `idle` does not release ownership. Exhausted immediate retries preserve the readable result and the next low-cost receipt check.
- Carry forward only verified outputs. Mark replaced or superseded outputs stale until revalidated.

Controller records actual receipt and its quality decision for that version in the existing state/log; no separate approval or round trip is required. Read the actual output and applicable validation evidence before accepting it. Return concrete defects or missing evidence for authorized rework and recheck the revised candidate. A forbidden or failed reverse notification increases the importance of Controller pull; it never transfers collection to the user. The selected observer owns observation/delivery records, while Controller remains the sole main-state writer. Web capture ending cannot stop a project watcher that still owns development/build waits. Dots may be the sole coordinator only when the user explicitly assigns it and its actual target and permissions are verified; local task access does not establish arbitrary cross-host chat access or bypass active-writer constraints. It is not a default dependency.

User to either side:

- The user may message the Controller or a worker directly.
- Before the next dispatch, read every directly changed worker since its last cursor/time, record the intervention, update registry/status, and re-evaluate affected gates.
- A worker-side user message may change that lane, but it does not silently change global routing, other lanes, or integration authority.

## 7. Failure, retry, abort, and archive lifecycle

Use explicit states:

`planned -> ready|standby -> queued|created_unconfirmed|running -> result_ready -> received_pending_review -> needs_fix|succeeded_pending_integration -> integrated -> archived`

`needs_input`, `blocked`, `failed`, and `aborted` remain available when their actual conditions occur; they are not successful acceptance.

- `created_unconfirmed`: creation returned an id but prompt/task readback is not yet available.
- `result_ready`: the worker returned a candidate; it has not yet been accepted by the Controller.
- `received_pending_review`: the Controller read the returned version; quality review is still open.
- `needs_fix`: the worker stopped, but an expected artifact or validation gate failed.
- `succeeded_pending_integration`: the Controller reviewed and accepted the actual candidate against the lane gate, but the integration owner has not closed the run gate. A worker self-report using this label is still pending review.
- `integrated`: the integration owner reconciled the lane into the required product and reran the integration validation.

Retry rules:

1. Retry only a classified creation-visibility, prompt-readback, or title-metadata delay, and only by reading the already identified task or retrying its title metadata. Validate the retry receipt with `scripts/validate_dispatch_route.py`.
2. Honor an explicit run budget. Otherwise continue scoped corrections while new evidence or a relevant fix makes progress; do not stop after an arbitrary single repair or repeat an unchanged failing attempt. For communications, keep delivery state separate from lane work state and use the bounded transport recovery procedure; pending delivery does not cancel independent work or result collection.
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

1. the executor has returned the result required by this lane; a recurring monitor reaches its overall completion gate only when its declared monitoring obligation ends, not after one successful check;
2. every required artifact/receipt exists and is non-empty when file output is required;
3. the Controller has received that exact version, inspected the actual output and applicable validation evidence, and recorded a passing quality decision against the original request;
4. changed files and remaining risks are reported;
5. the handoff state required by downstream lanes is explicit.

The run succeeds only when:

1. every required lane is integrated, or an omitted/aborted lane is explicitly accepted by the user;
2. the integration owner has reconciled all changes and write conflicts;
3. all declared integration checks applicable to the final deliverable pass; unrelated suites and repeated passing runs require a concrete new concern;
4. no required dependency, retry, user intervention, or stale output remains unresolved;
5. the final deliverable, task receipts, Controller quality decisions, and actual integration/delivery state are reported.

Creating many tasks, receiving fluent worker responses, or saying “used multiple Agents” satisfies none of these gates by itself.

Choose efficient observation rather than keeping the Controller in a repeated wait loop. Once actual scheduled/event follow-up and result return are verified, the current turn may end with pending work and a named next check/trigger; this is not run completion. “Executor started” or “will review later” alone is insufficient. An explicit dispatch-only request or user stop changes the obligation; a genuine unresolved external blocker leaves the run incomplete with a precise resume action.

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
