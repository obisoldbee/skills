# Cross-device task communication

Use this contract for an authorized message between existing Codex tasks, especially when SSH and Remote Control can both read the same thread. The normal path is **reuse the proven write endpoint → send once → wait/read → collect**. No new database, ownership probe or user confirmation is required for every message.

## Bind each direction once

Keep these facts in the existing task receipt or Controller registry:

| Fact | Source and use |
|---|---|
| Caller identity | Stable sender/device context; invalidate its endpoint mapping when that context changes |
| Target `threadId` | Actual ready task; never a queued client id or internal subagent id |
| Write `hostId` | Actual creation receipt, confirmed delivery, explicit user endpoint or completed normal handoff, with evidence reference |
| Read endpoints | Hosts discovered through list/read/wait; useful for collection, never proof of a writable service |
| Result reader | Named reader, next check time/entry and actual result thread or storage host/path |

`hostId="local"` means local to the caller. A Controller on device A cannot hand that value to a worker on B as A's return address. Resolve B→A separately through B's live tools. Neither matching thread ids nor matching filesystem paths establish the same writable service or shared files.

An existing Desktop/Remote Control success remains the send route even if SSH later reads the same thread. A thread created and served through SSH keeps that route instead. Do not hardcode one transport for all tasks. Reuse a healthy binding; after a relevant failure or actual handoff, repair that binding from current evidence. Historical success is a route to try, not a permanent ownership guarantee.

## Send and collect

1. Reuse the original user's communication authority for this task and destination. A worker's request to report back does not itself grant permission. If return messaging is not authorized, save the result and let Controller read it.
2. Include a stable `request_id` in the final self-contained prompt. Save the exact prompt and SHA, target, caller and selected endpoint in the existing run record. Before the tool call, append a unique attempt id with delivery `unknown`. This protects recovery after a caller crash; it is not server-side idempotency.
3. Call the live `send_message_to_thread` once with that `threadId`, `hostId` and `prompt`. Preserve the existing model/effort; ordinary follow-up omits `model` and `thinking`.
4. Record the actual result: `delivered` only with acceptance evidence; `not_delivered` only with an explicit pre-append rejection; timeout, disconnect or uncertain outcome stays `unknown`. An error label alone does not establish whether the prompt was appended.
5. Use bounded `wait_threads` with the last cursor, then focused `read_thread`/artifact reads. Delivery, started work, completed work and Controller receipt are separate observations. If accepted but progress is delayed, inspect the same task; do not resend RUN.
6. The executor saves results/observations before sending an authorized hint. The selected observer collects mechanical evidence; the Controller retains result receipt and [quality review](result-collection.md), even when reverse notification fails or is forbidden. For a chosen Luna-max monitoring policy, verify that the schedule actually executes on the Luna/max owner, retain compact cursors, back off, and stay quiet when unchanged. Wake the Controller for actionable evidence rather than repeating Astra checks; naming Luna in an Astra heartbeat prompt does not change its executor. Verify the authorized result return/resume route before ending the current turn as pending. One timeout is not closure, and a prompt is not a scheduler.

Report delivery/work/receipt state, actual output locations and the next action in the user's language. Write only the assigned run receipt/log and worker outputs; the helper input below stays read-only. Reuse existing records instead of creating a parallel registry for every message.

Cross-device artifacts name the actual storage host and recipient-readable path or Git commit. Transfer only the necessary authorized files and verify the received bytes. Do not synchronize whole chat databases or private runtime directories to communicate.

## Recover the affected delivery

| Actual evidence | Next action |
|---|---|
| Original message already accepted/present | Collect its result; never resend that request |
| `already has an active writer` rejected a send through a different reader endpoint | Restore the original proven write endpoint and send the same rejected request there once |
| Writer conflict at the recorded write endpoint | Restore access to its owning service, or verify a normal release/handoff; idle generation is insufficient |
| Initialize/stream timeout, connection lost | Reconcile the original attempt, restore the recorded connection, then retry only if explicitly not delivered |
| Unknown outcome, including absent recent history | Continue receipt/history reconciliation; absence does not exclude a still-in-flight append |
| Model/effort, permission, login or quota error | Diagnose that exact boundary; transport recovery does not change model or expand permission |

Keep the raw error and failed stage. JSON-RPC `invalid_request` is too broad: `already has an active writer` is `thread_writer_conflict`; an initialize handshake or stream-pong timeout is transport failure. A provider timeout remains a provider failure. `read_thread` succeeding or reporting `idle`/`notLoaded` does not prove writer ownership was released. The task tools do not expose a universal `writerOwner` probe; do not invent one.

Ordinary reconnection through available task/app tools is part of the authorized coordination work. Carry it out without asking the user to repeat permission. Reconnect the existing endpoint; do not bounce between SSH and Remote Control to see which accepts a duplicate. Do not delete writer locks, copy session databases, kill app-server processes or change `CODEX_HOME` as an automatic workaround. If normal ownership transfer is needed, use a supported, appropriately authorized release/handoff and verify its result.

Per incident, allow at most two additional immediate sends, only after a relevant route/connection repair and confirmed non-delivery. An unchanged error ends immediate retries, not the project: keep the pending receipt and next low-cost check, continue independent work, and let Controller pull available outputs. A later real connection recovery can resume the same incident/request; merely renaming an attempt or reaching the next timer tick does not reset the budget. Respect any stricter explicit user budget. Only an actual missing external capability or authority needs user input.

## Offline decision helper

Use `scripts/resolve_thread_transport.py` when a binding is missing or a delivery needs recovery. It reads declared evidence and emits a next action; it does not contact a host, acquire ownership, send a message or prove a receipt is true. The route guard still validates model/tool choices separately. After transport repair, the actual send is an unchanged `followup`, not a metadata `sync_retry`.

Minimal input (illustrative ids, replace with observed values):

```json
{
  "caller_id": "device-a",
  "target_thread_id": "task-b",
  "request_id": "run-1-command-1",
  "prompt": "Continue the accepted task once. request_id=run-1-command-1",
  "write_binding": {
    "caller_id": "device-a",
    "thread_id": "task-b",
    "host_id": "observed-write-host",
    "basis": "confirmed_delivery",
    "evidence_ref": "receipts/previous-send.json"
  }
}
```

```sh
python3 -B <skill-root>/scripts/resolve_thread_transport.py <run-root>/transport-attempt.json
```

On `prepare_send`, persist the pending attempt, then copy `send_arguments` into the real tool. On `collect_result`, wait/read instead. On any restore/reconcile action, do that operation and update the same record; do not report a global `blocked` just because no send arguments were returned.

Optional recovery fields reuse the existing attempt record:

- `last_delivery`: `caller_id`, `target_thread_id`, `request_id`, `payload_sha256`, unique `attempt_id`, actual `host_id`, `status`, `failure_class`, optional raw `error` (`message`, `stage`), and `evidence_ref`.
- `delivery_readback`: the same caller/thread/request/hash and `attempt_id`, `status=present|absent|unknown`, and `evidence_ref`. Presence must identify the exact original message. Unknown stays unknown despite absence; resolve it to `not_delivered` only from a definitive rejection/cancellation receipt for that attempt.
- `recovery`: `caller_id`, `thread_id`, selected `host_id`, `after_attempt_id`, `kind=same_endpoint_reconnected|writer_endpoint_restored`, and `evidence_ref`. A writer conflict needs restoration of the writable service, not merely a live socket.

The helper checks identity and endpoint selection, not the user's authority, authenticity of evidence or the run's persisted retry budget. The caller enforces those existing boundaries. It deliberately ignores `read_endpoints` for choosing a writer. Use [transport regression tests](../tests/test_thread_transport.py) for offline examples; a PASS does not prove live cross-device availability.
