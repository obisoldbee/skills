# Result collection and quality review

Use for every execution dispatch, single or multi-lane. Complete portable handoff remains an artifact-only outcome. `dispatch_only` is an exception selected by an explicit user request to send/create and leave follow-up elsewhere; preserve that request and the named next owner. Do not infer it from task count, wording that asks an Agent to do work, or missing scheduling configuration.

## Bind the minimum contract

Before sending, name the Controller/result reader, worker thread or accessible output location, expected result, acceptance criteria, and next observation entry. Include the exact version or source identity in the returned result. Reuse existing project records; one short lane can keep this contract and receipt in the current conversation. Do not require a new state file, extra reviewer task, or user approval just to collect and review an already authorized result.

An executor (`worker`) may develop, research, review, operate a UI, or perform scheduled observation. Return evidence appropriate to that task: implementation uses a diff/version and relevant checks; research uses the complete findings and sources; operations use the observed outcome; scheduled checks use target, observation time/cursor, current evidence, change classification, and next check or stop condition. Files are required only when the task calls for them. A worker's final reply in its own thread is a valid return location. Reverse notification is optional and requires its own messaging authority.

## Choose efficient follow-up

- Optimize total cost per accepted result: actual model/effort, context size, wake-up count, tool work, and review/rework all matter. “Both consume tokens” does not make an Astra polling turn equivalent to a Luna-max check. Assign a capable executor to the bounded work before choosing cadence; no exact billing ratio or measured saving is implied.
- For specified mechanical monitoring, prefer Luna-max under the user's selected monitoring policy, or the corresponding authorized auto route. Give Luna the explicit objective/check contract below. Astra, when selected as Controller, handles decisions and substantive quality review after actionable evidence arrives; it does not need to remain awake checking unchanged progress.
- Reuse an earlier explicit Luna-max policy as route authority for this monitoring responsibility; do not ask the user to repeat the alias at every check or substitute Astra because its chat already exists. Preserve explicit alternative choices. The named policy selects only the observer role; it does not change other task models, grant new task-creation authority, or turn a bare Skill invocation into automatic routing.
- For an expected short wait or a one-off check, bounded `wait_threads` with current cursors may avoid the overhead of another executor. Keep useful independent work local. Do not use this exception to turn a long mechanical wait into repeated high-capability Controller turns.
- For a long, uncertain, unattended, or cross-turn wait, prefer a real host-supported completion trigger or low-frequency scheduled checks. Do not invent an event subscription. When scheduling is selected, use the live automation tools: inspect and reuse/update a matching automation instead of duplicating it; bind the actual target, result reader, check interval, resume action, and stop condition. Reuse existing monitoring authorization rather than asking again at every step.
- After choosing the executor, set cadence from expected duration, responsiveness needs, and any user deadline. Back off after unchanged observations. Batch independent targets where supported, retain cursors, and avoid full-history/context reloads. Give the observer only its bounded materials and compact previous state; load the larger project context for Controller review when needed. Do not keep a foreground wait loop alongside an active observer for the same responsibility.
- Keep unchanged/non-actionable checks quiet. An observer may update its small cursor/status record, but should not notify the user or wake the Controller merely to repeat unchanged state. Return new actionable evidence, completion, failure, or required user action through a verified authorized delivery/continuation route. An explicit periodic-report request overrides silence.
- Before ending the current turn under background coverage, verify the real observer/automation is active, reads the correct target, and can deliver the result or resume the responsible Controller for collection and quality review. Report an interim pending status, not completion. A schedule that never returns results, a prompt, saved next-check time, or unaccepted handoff is not coverage.
- Verify the real automation owner and execution model/effort. A heartbeat inherits its target thread's settings on hosts with that contract: bind it to the verified Luna-max observer when that is the selected policy. A prompt saying “you are Luna” or a fabricated heartbeat model field is not a model switch. Reuse a suitable existing observer and matching automation; new visible chat creation still requires the corresponding user request. Keep other explicit observer choices intact. Do not silently attach routine checks to an Astra Controller heartbeat as a convenience fallback; report a missing observer/capability precisely and continue independent work or a bounded necessary read.
- A normal timeout means work is pending, not failed or accepted. Adjust cadence or hand off to verified background observation rather than repeatedly performing unchanged checks. If scheduling is unavailable or disallowed, keep the feasible bounded wait/read route and independent work; do not drop result collection or claim a background wake-up that does not exist.
- If the user stops work or a real external failure prevents continuation after independent work is exhausted, report the current incomplete state, last result/observation, exact blocker, and resume action. Do not report closure or promise a wake-up that does not exist. An involuntary interruption requires resume from the saved state, not redispatch of an existing worker.

### Bounded Luna-max observation task

Include these fields in the existing handoff; no extra state system is required:

| Field | Concrete content |
|---|---|
| Objective | Which task/result/condition is being monitored and what makes it ready for Controller attention |
| Inputs | Exact thread/host or allowed artifact paths, expected source/version, and last cursor or observation identity |
| Checks | Bounded status reads, file/receipt checks, or already authorized deterministic commands; no open-ended redesign or final product acceptance |
| Execution | Verified Luna/max owner, actual automation binding, cadence/backoff, and applicable permission limits |
| Return | Target/source, observation time/cursor, change since last check, evidence references, and current condition |
| Wake condition | New completion/result, failure, material deviation, evidence conflict, or a decision requiring the Controller; unchanged state stays quiet |
| Delivery | Verified authorized result delivery/resume route, stable event identity, and Controller receipt; do not dump full history into each notification |
| Stop | The named monitoring obligation's completion/receipt condition, user stop, or real unresolved capability/authority boundary |

Luna's “result ready” means that evidence is ready for review, not that the product passed. If judgment exceeds the specified checks, return the evidence and precise question to the Controller. A failed or forbidden reverse notification does not lose the result: retain it and the pending receipt, use the authorized collection route, and avoid duplicate escalation. Observing completion alone does not satisfy the Controller's outstanding receipt/quality gate or stop unrelated monitors.

## Receive, review, and act

1. **Receive.** On a returned result, read the executor's reply/observation and required artifacts at their real locations. Reconcile direct user changes and bind receipt to the current candidate revision, file hashes, response message, or observation cursor/time. Mark `received_pending_review`. Do this even when the executor was told not to send a reverse message or its notification failed; scheduling changes when collection occurs, not who owns it.
2. **Review.** The Controller inspects the actual result against the original request and declared acceptance criteria. For code, inspect the relevant diff and credible validation evidence, then run focused independent checks where necessary to establish the changed behavior. For documents, research, or UI work, inspect the corresponding content, sources, or actual product evidence. Reuse applicable current checks; do not repeat an entire suite or demand disk artifacts merely to look rigorous. Worker prose and self-tests alone are not a Controller quality decision.
3. **Decide.** Record the reviewed version, criteria checked, evidence actually read, verdict, and remaining issues. Pass only when the applicable gate is met. Missing evidence remains unverified; identified defects become `needs_fix`, with expected correction and acceptance evidence. An honest blocked/failed result is collected and assessed but is not a passed deliverable. An interrupted or partial review can be received and quality checked, but the requested review remains incomplete; UI generation stopping or a worker's final message does not establish coverage.
4. **Correct.** Read the current worker state, then send concrete in-scope corrections to the same task when the user's delegation authorizes continuation. Reuse the existing route and messaging authority; the route guard still applies to dispatch, not ordinary reads. If a boundary needs new authority, finish independent authorized work and report that exact gap. Neither a failed notification nor an arbitrary one-repair budget ends the repair loop.
5. **Recheck and integrate.** Collect the corrected version and review affected criteria again. Only a passed Controller review permits `succeeded_pending_integration`. The integration owner then performs the already authorized integration and its applicable checks, or reports the genuine remaining acceptance/authority gate. Acceptance of a candidate does not itself authorize commit, merge, install, restart, publish, or deploy.

An existing self-report labeled `succeeded_pending_integration` is still an unreviewed candidate until the Controller performs these checks. Do not edit old receipts to make review appear to have happened earlier. A changed candidate or direct user scope change invalidates the affected acceptance evidence.

For a recurring observer, distinguish one checked observation from completion of the monitoring responsibility. Quality review verifies the right target, fresh evidence, correct change classification, and actionable result delivery; it does not require a full Controller review on every unchanged tick. Stop/pause only the named monitoring obligation when its completion condition or user stop is met, verify that state, and retain unrelated monitoring. An active timer alone does not prove it performed a check, returned a result, or passed quality review.

## Minimum closeout

For each required lane, report these facts in the existing status or final response:

| Fact | Required evidence |
|---|---|
| Executor returned | Actual result/observation and requested artifacts, bound to a version or observation identity |
| Controller received | What the Controller read and which version was received |
| Quality decision | Criteria, inspected evidence, accepted/needs_fix/blocked verdict, and unresolved issues |
| Integration/delivery | Actual authorized result and relevant checks, or its remaining gate and owner |

Keep the states distinct: `running -> result_ready -> received_pending_review -> needs_fix | succeeded_pending_integration -> integrated`. A returned result has reached `result_ready`; it has not passed quality review. Failed or blocked work retains its factual state and resume action.

For explicit `dispatch_only`, close only the routing obligation after verified delivery and any live-host initial progress requirement. Report the executor's result and quality review as pending under the user-designated owner. For normal execution, “started; I will review later” without a verified continuation leaves an unowned gap. With verified background follow-up, the current turn may end with an interim status naming the actual observer, next check/trigger, and collection/review owner; the run remains pending until those obligations pass.
