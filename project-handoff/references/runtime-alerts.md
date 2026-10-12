# Runtime verification and exception delivery

## Contents

- [Verify the actual turn](#verify-the-actual-turn)
- [Local detector and outbox](#local-detector-and-outbox)
- [Connect a dot without inventing an endpoint](#connect-a-dot-without-inventing-an-endpoint)

Use for a selected model/effort responsibility that continues across turns, or
when the user requests anomaly notifications. A model choice is a contract, not
a scheduler lock. A heartbeat may fall back; an ordinary user turn may also
change effort. Do not attribute both to the same cause without execution logs.

## Verify the actual turn

1. Retain the applicable human/Skill selection, scope, session and each selected
   axis independently. Never derive the expected pair from already drifted
   settings, a task title, or the latest observed value. Unselected axes remain
   `platform_default` with null values; don't freeze them accidentally.
2. Bind actual metadata to this session and turn. Requested parameters, creation
   receipts and session settings prove request/configuration only. Previous
   runtime values do not prove a later heartbeat. Preserve observed `low` and
   missing fields rather than replacing them with requested `max`. For recurring
   execution pass `--turn-id <current-turn>` to `validate_execution_binding.py`
   with the retained selection and actual evidence. It rejects old-turn evidence
   and configuration-only `session_settings` for that check.
3. Compare before route-dependent work when current runtime metadata is
   available, and again before accepting its result. A missing field is
   `route_unverified`; a conflicting observed field is `route_mismatch`.
   Continue bounded metadata diagnosis and independent authorized work. Do not
   restart or block the whole project for a missing optional display field.
4. A confirmed mismatch suspends only the affected formal execution/recurrence,
   preserving artifacts and collection responsibility. Record the actual
   automation pause readback where supported. Notify once through an authorized
   route. Diagnose scheduler/default/catalog versus an explicit user change;
   do not rewrite app databases or silently substitute another executor.
5. Resume under the retained route after fresh actual execution evidence, or an
   explicit human route change recorded with its source. A new prompt, unchanged
   ACTIVE timer, or manually relabeled receipt does not clear the incident.

## Local detector and outbox

`scripts/runtime_alerts.py` is a deterministic, standard-library adapter for
Codex `Stop` and `PermissionRequest` command hooks. It performs no network or
model calls and never changes model settings, pauses timers, or trusts hooks.
The Stop check is after-the-fact detection, not prevention of first-turn cost.
PermissionRequest detects an actual tool approval request, not arbitrary prose
asking a question. Other blockers must be reported by the responsible executor.

When installing the detector, bind its registry and state-directory paths in the
local dispatch record; add each selected recurring session before dispatch and
update it only for a verified scope/route change. It does not automatically
cover every chat. Explain alerts in the user's language.

Create a local registry outside the public package. Enroll only known sessions
with their retained selection; no wildcard enrollment from task titles:

```json
{
  "transcript_root": "<Codex sessions directory>",
  "sessions": {
    "<actual session id>": {
      "selection_ref": "<original instruction or accepted route record>",
      "model_basis": "explicit_skill_route",
      "model": "gpt-6-luna",
      "reasoning_basis": "explicit_skill_route",
      "reasoning": "max"
    }
  }
}
```

Current hook input provides `model` and `turn_id`. Effort is read only from the
newest matching session/turn/model transcript context, within a bounded 4 MiB
tail. The transcript format is not stable: missing, out-of-root, conflicting or
unreadable evidence stays unknown. No global-config fallback proves effort.
The helper checks supplied evidence, not the authenticity of human authority.

Install a reviewed command for each event using absolute, shell-quoted paths:
`python3 -B <script> --state-dir <local-state> hook --registry <registry>`.
Use a short timeout, for example 5 seconds. Merge with existing hook sources;
never replace other handlers or write trust hashes. Hook definitions require
the host's trust flow; configured, trusted, actually fired, and delivered are
separate states. Never pass a trust bypass to make a test succeed.

The private SQLite outbox serializes concurrent events, deduplicates unchanged
conditions across ticks, and retains pending alerts across process restarts.
Only a fully matched observation resets deduplication for a later recurrence.
Old pending alerts remain deliverable even after recovery; verify current state
before wording a delayed alert. Run:

```text
python3 -B <script> --state-dir <local-state> pending
python3 -B <script> --state-dir <local-state> ack --id <alert-id> --receipt <actual-message-reference>
```

The consumer delivers the compact incident, then acknowledges with the actual
destination message reference. A send error or unknown delivery leaves it
pending; reconcile the stable alert ID before retrying. The helper records a
receipt string but cannot independently authenticate delivery. Never acknowledge
on queue insertion, successful hook exit, or a proposed integration.

## Connect a dot without inventing an endpoint

Bind the user's selected dot/channel and authorized access to the outbox. Use a
supported dot capability or an already-authorized channel integration. A dot
name, web link or Computers connection alone is not an event subscription. If a
dot needs a recurring pickup, confirm its actual recurring task, cadence, read
scope, quiet behavior and receipt path. Do not create expensive model polling
merely to detect a model switch; detection is local and event driven. A chosen
dot pickup may still consume resources and needs its own bounded cadence.

Send only alert ID, task/session link, expected and observed pair, evidence
status, impact and required action. Never forward raw transcripts, commands,
prompts, credentials or unrelated tasks. Notification to the user is not
authorization to message unrelated tasks or approve the underlying operation.

Verify one clearly labeled test from hook firing through pending queue,
destination-visible message and receipt; then verify duplicate suppression.
Until all stages pass, report the exact unconnected stage. Missing dot delivery
must not silently discard incidents or be reported as successful notification.
Do not use `Stop` output `decision: block` or exit code 2 for notifications: that
requests another model continuation. A human prerequisite with no independent
work left should notify once and suspend the affected poller, not wake it every
few minutes to repeat the blocker. Keep the resume condition and pending result.

Official contracts: [Hooks](https://learn.chatgpt.com/docs/hooks),
[dot channels](https://learn.chatgpt.com/docs/dots/channels), and
[dot computer access](https://learn.chatgpt.com/docs/dots/computers-and-apps).
Recheck the host's supported interface when installing or changing an adapter.
