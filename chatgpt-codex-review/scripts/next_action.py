#!/usr/bin/env python3
"""Read declared review-cycle evidence and suggest one action. No side effects."""

import argparse
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import re
import sys
from urllib.parse import urlsplit


PHASES = {
    "ready_to_submit", "submitting", "waiting_web", "review_ready",
    "repairing", "validating", "completed", "blocked", "paused",
}
SOURCE = re.compile(r"(?:git:(?:[0-9a-f]{40}|[0-9a-f]{64})|mcp:[0-9a-f]{64})\Z")
SHA256 = re.compile(r"[0-9a-f]{64}\Z")
ARTIFACT_NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\Z")
GITHUB_REPOSITORY = re.compile(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+\Z")
LUNA_MODEL = re.compile(r"gpt-(\d+(?:\.\d+)*)-luna\Z")
SCOPES = {"repair_loop", "review_only", "materials_only"}
BROWSER_FAULTS = {"space_missing", "space_closed", "browser_crash", "connection_failed"}
HUMAN_BROWSER_GATES = {"auth", "user_control", "permission_denied"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def evidence(value):
    return isinstance(value, list) and bool(value) and all(nonempty(x) for x in value)


def timestamp(value):
    require(nonempty(value), "observed_at must be an ISO timestamp with timezone")
    try:
        parsed = datetime.fromisoformat(value.replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError("invalid ISO timestamp") from exc
    require(parsed.tzinfo is not None, "timestamp needs a timezone")
    return parsed


def stamp(value):
    return value.astimezone(timezone.utc).isoformat()


def source(value):
    return isinstance(value, str) and SOURCE.fullmatch(value) is not None


def conversation_url(value):
    if not isinstance(value, str):
        return False
    url = urlsplit(value)
    return (url.scheme == "https" and url.hostname in {"chatgpt.com", "chat.openai.com"}
            and re.search(r"/c/[^/]+/?$", url.path) is not None
            and not url.username and not url.password)


def contract_digest(contract):
    require(isinstance(contract, dict) and set(contract) == {"required", "optional"},
            "artifact_contract needs required and optional lists")
    names = set()
    for category in ("required", "optional"):
        require(isinstance(contract[category], list), "invalid artifact list")
        for item in contract[category]:
            require(isinstance(item, dict) and isinstance(item.get("name"), str)
                    and ARTIFACT_NAME.fullmatch(item["name"]) is not None
                    and isinstance(item.get("kind"), str)
                    and item["kind"] in {"zip", "png", "json", "utf8"}, "invalid artifact item")
            require(item["name"].casefold() not in names, "duplicate artifact name")
            names.add(item["name"].casefold())
    return hashlib.sha256(json.dumps(contract, sort_keys=True, ensure_ascii=False,
                                    separators=(",", ":")).encode("utf-8")).hexdigest()


def acceptance_digest(contract):
    require(isinstance(contract, dict) and set(contract) == {"required_checks", "delivery_items"},
            "acceptance_contract needs required_checks and delivery_items")
    for key in ("required_checks", "delivery_items"):
        require(isinstance(contract[key], list) and all(nonempty(x) for x in contract[key]),
                "invalid acceptance_contract " + key)
    return hashlib.sha256(json.dumps(contract, sort_keys=True, ensure_ascii=False,
                                    separators=(",", ":")).encode("utf-8")).hexdigest()


def source_binding_digest(route, source_id, binding):
    require(isinstance(binding, dict), "source_binding must be an object")
    if route == "github":
        require(set(binding) == {"repository", "commit"}
                and isinstance(binding["repository"], str)
                and GITHUB_REPOSITORY.fullmatch(binding["repository"]) is not None
                and binding["commit"] == source_id.removeprefix("git:"),
                "GitHub source binding mismatch")
    else:
        require(set(binding) == {"server", "tool", "version", "snapshot_sha256", "manifest_sha256"}
                and all(nonempty(binding[k]) for k in ("server", "tool", "version"))
                and binding["snapshot_sha256"] == source_id.removeprefix("mcp:")
                and isinstance(binding["manifest_sha256"], str)
                and SHA256.fullmatch(binding["manifest_sha256"]) is not None,
                "MCP source binding mismatch")
    return hashlib.sha256(json.dumps(binding, sort_keys=True, ensure_ascii=False,
                                    separators=(",", ":")).encode("utf-8")).hexdigest()


def bound(record, state, *, token=False):
    return (isinstance(record, dict) and record.get("run_id") == state["run_id"]
            and record.get("source_id") == state["source_id"]
            and record.get("source_binding_digest") == state["source_binding_digest"]
            and record.get("contract_digest") == state["contract_digest"]
            and record.get("acceptance_digest") == state["acceptance_digest"]
            and record.get("consumer_host") == state["consumer_host"]
            and record.get("execution_scope", "repair_loop") == state.get("execution_scope", "repair_loop")
            and (not token or (record.get("round") == state["round"]
                               and record.get("request_token") == state["request_token"])))


def receipt_bound(state, receipt):
    if not isinstance(receipt, dict):
        return False
    binding = receipt.get("binding") or {}
    if receipt.get("validator") != "verify_artifacts/v2" or receipt.get("contract_digest") != state["contract_digest"]:
        return False
    for key in ("run_id", "round", "source_id", "request_token", "consumer_host", "artifact_root"):
        if binding.get(key) != state[key]:
            return False
    reports = receipt.get("files") or {}
    names = {item["name"] for category in ("required", "optional")
             for item in state["artifact_contract"][category]}
    return isinstance(reports, dict) and set(reports) == names and all(
        isinstance(reports[name], dict)
        and reports[name].get("status") in {"verified", "missing", "invalid", "unverified"}
        for name in names)


def artifact_ready(state):
    required = {item["name"] for item in state["artifact_contract"]["required"]}
    if not required:
        return True
    receipt = state.get("artifact_receipt") or {}
    if not receipt_bound(state, receipt):
        return False
    reports = receipt["files"]
    return receipt.get("required_ready") is True and all(
        isinstance(reports.get(name), dict) and reports[name].get("status") == "verified"
        for name in required)


def record(state, event, **fields):
    return {"run_id": state["run_id"], "source_id": state["source_id"],
            "source_binding_digest": state["source_binding_digest"],
            "contract_digest": state["contract_digest"],
            "acceptance_digest": state["acceptance_digest"],
            "consumer_host": state["consumer_host"], "round": state["round"],
            "execution_scope": state.get("execution_scope", "repair_loop"),
            "request_token": state["request_token"], "evidence": event["evidence"], **fields}


def prepared_request(state):
    prepared = state.get("prepared_request") or {}
    return (bound(prepared, state, token=True)
            and nonempty(prepared.get("path"))
            and isinstance(prepared.get("sha256"), str)
            and SHA256.fullmatch(prepared["sha256"]) is not None)


def luna_pair(binding):
    match = LUNA_MODEL.fullmatch(str(binding.get("model", "")))
    return ((match is not None and int(match[1].split(".")[0]) >= 6 and binding.get("reasoning") == "max")
            or (binding.get("route_basis") == "explicit_user" and nonempty(binding.get("user_override_ref"))))


def web_io_binding(state, binding=None):
    """Validate a declared ready visible owner, never an internal agent identity."""
    binding = state.get("web_io_binding") if binding is None else binding
    if not isinstance(binding, dict):
        return False
    keys = ("thread_id", "host_id", "model", "reasoning", "identity_readback_ref",
            "model_readback_ref", "reasoning_readback_ref")
    if (binding.get("surface") != "visible_thread" or binding.get("ready") is not True
            or any(not nonempty(binding.get(key)) for key in keys)
            or binding["thread_id"].startswith("/root/")
            or any(key in binding for key in ("agentPath", "agentThreadId", "client_thread_id", "subAgentActivity"))
            or binding["thread_id"] == state.get("controller_thread_id")
            or binding.get("runtime_pair_verified") is not True):
        return False
    # Exact user choices stay pinned. A role name or forwarded prompt is not an override.
    if not luna_pair(binding):
        return False
    try:
        timestamp(binding.get("verified_at"))
    except ValueError:
        return False
    return True


def followup_binding(state, receipt):
    if not isinstance(receipt, dict):
        return False
    keys = ("automation_id", "owner_thread_id", "owner_host", "run_id", "state_path", "evidence_ref")
    owner = state.get("web_io_binding") or {}
    if (not web_io_binding(state)
            or receipt.get("tool") != "automation_update/view" or receipt.get("kind") != "heartbeat"
            or receipt.get("status") not in {"ACTIVE", "PAUSED"}
            or any(not nonempty(receipt.get(key)) for key in keys)
            or receipt.get("owner_role") != "web_io"
            or receipt.get("owner_thread_id") != owner.get("thread_id")
            or receipt.get("target_thread_id") != owner.get("thread_id")
            or receipt.get("owner_host") != owner.get("host_id")
            or receipt.get("owner_model") != owner.get("model")
            or receipt.get("owner_reasoning") != owner.get("reasoning")
            or receipt.get("owner_model_readback_ref") != owner.get("model_readback_ref")
            or receipt.get("owner_reasoning_readback_ref") != owner.get("reasoning_readback_ref")
            or receipt.get("controller_thread_id") != state.get("controller_thread_id")
            or receipt.get("controller_host") != state.get("controller_host")
            or not nonempty(state.get("controller_thread_id"))
            or not nonempty(state.get("controller_host"))
            or receipt.get("run_id") != state["run_id"]
            or receipt.get("state_path") != state.get("state_path")
            or receipt.get("prompt_binding_verified") is not True
            or not nonempty(receipt.get("schedule_inventory_ref"))
            or receipt.get("active_automation_ids") != (
                [receipt.get("automation_id")] if receipt.get("status") == "ACTIVE" else [])
            or type(receipt.get("cadence_minutes")) is not int
            or not 1 <= receipt["cadence_minutes"] <= 1440):
        return False
    try:
        checked = timestamp(receipt.get("checked_at"))
    except ValueError:
        return False
    if receipt["status"] == "PAUSED":
        return receipt.get("next_check_at") is None
    try:
        next_check = timestamp(receipt.get("next_check_at"))
    except ValueError:
        return False
    return next_check >= checked


def current_followup(state, event, *, fresh_view=False):
    saved = state.get("followup")
    view = event.get("followup_view") if fresh_view else event.get("followup_view", saved)
    if (not followup_binding(state, saved) or saved["status"] != "ACTIVE"
            or not followup_binding(state, view) or view["status"] != "ACTIVE"
            or view["automation_id"] != saved["automation_id"]):
        return None
    if fresh_view and view.get("evidence_ref") == saved.get("evidence_ref"):
        return None
    try:
        when = timestamp(event.get("observed_at"))
        checked = timestamp(view["checked_at"])
        prior = timestamp(saved["checked_at"])
    except ValueError:
        return None
    if checked < prior or not 0 <= (when - checked).total_seconds() <= 600:
        return None
    return view


def inline_execution(state, event):
    binding = state.get("inline_observer_binding") or {}
    if (binding.get("surface") not in {"internal_agent", "current_turn"}
            or binding.get("runtime_pair_verified") is not True or not luna_pair(binding)
            or any(not nonempty(binding.get(key)) for key in (
                "execution_ref", "turn_id", "model", "reasoning", "model_readback_ref", "reasoning_readback_ref"))
            or event.get("inline_execution_ref") != binding.get("execution_ref")
            or event.get("inline_turn_id") != binding.get("turn_id")):
        return None
    try:
        when = timestamp(event.get("observed_at"))
        if not timestamp(binding.get("verified_at")) <= when <= timestamp(binding.get("deadline_at")):
            return None
    except ValueError:
        return None
    return {"mode": "inline", "evidence_ref": binding["execution_ref"]}


def submission_observer(state, event, *, fresh_view=False):
    if state.get("followup_mode", "durable") == "inline":
        return inline_execution(state, event)
    return current_followup(state, event, fresh_view=fresh_view)


def observer_readback_updates(view):
    return {"inline_execution_ref": view["evidence_ref"]} if view.get("mode") == "inline" else {"followup": view}


def ensure_followup(state, reason, **updates):
    if state.get("followup_mode", "durable") == "inline":
        return result(state, "ensure_inline_luna", "Bind a verified Luna execution in this turn; "
                      "capture within its bound or report the remaining wait without claiming background follow-up. " + reason,
                      **updates)
    if not web_io_binding(state):
        return result(state, "ensure_luna_owner",
                      "Reuse a verified ready Luna visible thread with model/effort readback; "
                      "new visible-task creation needs a direct user request. " + reason, **updates)
    return result(state, "ensure_followup", reason, **updates)


def result(state, action, reason, **updates):
    phase = updates.get("phase", state["phase"])
    candidate = {**state, **updates}
    schedule_action = ("none" if state.get("followup_mode", "durable") == "inline"
                       else "keep_active" if web_capture_required(candidate) or (
                           candidate.get("awaiting_send") is True and phase in {"ready_to_submit", "submitting"})
                       else "pause_if_active")
    return {"action": action, "reason": reason, "phase": phase, "schedule_action": schedule_action,
            "terminal": phase == "completed", "state_updates": updates}


def web_capture_required(state, observer_record=None):
    if (observer_record and observer_record.get("validator") == "luna-observer/v1"
            and observer_binding(observer_record.get("binding") or {}) == observer_binding(state)
            and observer_record.get("text_complete") is True
            and captured_artifacts_ready(state, observer_record)):
        return False
    return (state["phase"] == "waiting_web"
            or (state["phase"] in {"review_ready", "repairing", "validating"}
                and nonempty(state.get("raw_reply_path")) and not captured_artifacts_ready(state, observer_record)))


def captured_artifacts_ready(state, ledger):
    proof = current_artifact_observation(state, ledger)
    return (artifact_ready(state) if proof is None else bool(proof)
            and artifact_ready({**state, "artifact_receipt": proof["payload"].get("receipt")}))


def event_followup_mode(event):
    return event.get("followup_mode", "inline" if event.get("inline_execution_ref")
                     or event.get("type") in {"inline_observation", "inline_artifacts"} else "durable")


def artifact_observation(state, event):
    payload = dict(event)
    # Unsigned Controller inputs inherit this invocation's scope; an original
    # notification's payload/SHA is never rewritten.
    if not payload.get("notification_key"):
        payload.setdefault("execution_scope", state.get("execution_scope", "repair_loop"))
        payload.setdefault("followup_mode", state.get("followup_mode", "durable"))
    return {"payload": payload, "sha256": notification_digest(payload)}


def required_artifact_snapshot(state, receipt):
    return ({item["name"]: receipt["files"][item["name"]]
             for item in state["artifact_contract"]["required"]} if receipt_bound(state, receipt) else None)


def current_artifact_observation(state, ledger):
    """One current proof across both writers; absence retains legacy receipts."""
    candidates = [state.get("artifact_observation")]
    if ledger and observer_binding(ledger.get("binding") or {}) == observer_binding(state):
        latest = ledger.get("artifact_observation")
        if latest is None:
            # Old ledgers have original notifications but no current snapshot.
            for item in reversed(ledger.get("notifications", [])):
                payload = item.get("controller_event") or {}
                if isinstance(payload, dict) and payload.get("type") == "artifact_receipt":
                    if (notification_digest(payload) != item.get("receipt_sha256")
                            or payload.get("notification_receipt_sha256") != item.get("receipt_sha256")
                            or notification_key(ledger["binding"], {"kind": "artifacts", "receipt": payload.get("receipt")}) != item.get("key")):
                        return {}
                    latest = {"payload": payload, "sha256": item["receipt_sha256"]}
                    break
        candidates.append(latest)
    proofs = []
    for proof in candidates:
        if proof is None:
            continue
        proofs.append(proof)
        if isinstance(proof, dict) and "conflicting_proof" in proof:
            proofs.append(proof["conflicting_proof"])
    verified = []
    for proof in proofs:
        payload = proof.get("payload") if isinstance(proof, dict) else None
        if not (isinstance(payload, dict) and payload.get("type") in {"scheduled_artifacts", "inline_artifacts", "artifact_receipt"}
                and bound(payload, state, token=True) and payload.get("artifact_root") == state["artifact_root"]
                and event_followup_mode(payload) == state.get("followup_mode", "durable")
                and evidence(payload.get("evidence")) and notification_digest(payload) == proof.get("sha256")
                and receipt_bound(state, payload.get("receipt"))):
            return {}
        when = timestamp(payload["observed_at"]) if payload.get("observed_at") else None
        verified.append((when, proof))
    if not verified:
        return None
    dated = [when for when, _ in verified if when is not None]
    latest = max(dated) if dated else None
    current = next(proof for when, proof in verified if when == latest)
    required = required_artifact_snapshot(state, current["payload"]["receipt"])
    if any((when is None or when == latest)
           and required_artifact_snapshot(state, proof["payload"]["receipt"]) != required
           for when, proof in verified):
        return {}  # Unknown order or same-time conflicts need fresh real proof.
    return current


def current_artifacts_applied(state, ledger):
    if not state["artifact_contract"]["required"]:
        return True
    proof = current_artifact_observation(state, ledger)
    return (artifact_ready(state) and captured_artifacts_ready(state, ledger)
            and (proof is None or required_artifact_snapshot(state, state.get("artifact_receipt"))
                 == required_artifact_snapshot(state, proof["payload"]["receipt"])))


def artifact_gate(state, ledger):
    proof = current_artifact_observation(state, ledger)
    if proof and captured_artifacts_ready(state, ledger) and not current_artifacts_applied(state, ledger):
        latest = proof["payload"]
        for item in (ledger or {}).get("notifications", []):
            payload = item.get("controller_event") or {}
            if (isinstance(payload, dict) and payload.get("type") == "artifact_receipt"
                    and payload.get("receipt") == latest.get("receipt")
                    and payload.get("observed_at") == latest.get("observed_at")
                    and bound(payload, state, token=True) and payload.get("artifact_root") == state["artifact_root"]
                    and event_followup_mode(payload) == state.get("followup_mode", "durable")
                    and payload.get("notification_key") == item.get("key")
                    and notification_digest(payload) == item.get("receipt_sha256") == payload.get("notification_receipt_sha256")
                    and not notification_applied(state, item.get("key"), item.get("receipt_sha256"))):
                latest = payload
                break
        if not latest.get("notification_key"):
            latest = {**latest, "type": "artifact_receipt"}
        if not notification_applied(state, latest.get("notification_key"), latest.get("notification_receipt_sha256")):
            answer = result(state, "process_saved_result", "Apply the current verified required snapshot locally; historical event receipt is not the current applied file set.")
            answer["controller_event"] = latest
            return answer
    return result(state, "obtain_required_artifacts", "Required files need current verification and an applied matching snapshot.")


def next_round(state, event, next_source):
    token = event.get("next_request_token")
    require(nonempty(token) and token not in state["used_request_tokens"],
            "a resubmission needs a never-used next_request_token")
    contract = event.get("next_artifact_contract", state["artifact_contract"])
    digest = contract_digest(contract)
    if "next_contract_digest" in event:
        require(event["next_contract_digest"] == digest, "next artifact contract digest mismatch")
    acceptance = event.get("next_acceptance_contract", state["acceptance_contract"])
    acceptance_hash = acceptance_digest(acceptance)
    if "next_acceptance_digest" in event:
        require(event["next_acceptance_digest"] == acceptance_hash, "next acceptance digest mismatch")
    if next_source != state["source_id"]:
        require("next_source_binding" in event, "new source needs next_source_binding")
    source_binding = event.get("next_source_binding", state["source_binding"])
    source_hash = source_binding_digest(state["source_route"], next_source, source_binding)
    return result(state, "prepare_review_request", "Astra must freeze this round's review request before Luna submits.",
                  phase="ready_to_submit", round=state["round"] + 1,
                  source_id=next_source, request_token=token, candidate_source_id=None,
                  source_binding=source_binding, source_binding_digest=source_hash,
                  used_request_tokens=[*state["used_request_tokens"], token],
                  artifact_contract=contract, contract_digest=digest, artifact_receipt=None, artifact_observation=None,
                  acceptance_contract=acceptance, acceptance_digest=acceptance_hash,
                  prepared_request=None, review=None, review_message_id=None, last_completion=None,
                  submitted_user_message_id=None, submitted_prompt_sha256=None,
                  adopted_without_web_token=False, send_authorized_view_ref=None,
                  awaiting_send=False,
                  pending_file_findings=0, dispatchable_findings=0,
                  refresh_count=0, next_refresh_at=None)


def completion(state, observer_record=None):
    review = state.get("review") or {}
    checks = state.get("validation") or {}
    delivery = state.get("delivery") or {}
    files_ready = current_artifacts_applied(state, observer_record)
    if state.get("pending_file_findings", 0):
        return (artifact_gate(state, observer_record) if not files_ready else result(state, "continue_repair_with_files",
                      "File-dependent confirmed findings remain open."))
    if not files_ready:
        return artifact_gate(state, observer_record)
    review_only = state.get("execution_scope") == "review_only"
    if not (bound(review, state, token=True)
            and (review.get("coverage_complete") is True if review_only else review.get("clean") is True)
            and evidence(review.get("evidence"))):
        return result(state, "obtain_current_review", "This source has no accepted complete review.")
    checks_required = not review_only or bool(state["acceptance_contract"]["required_checks"])
    failed_review_checks = (review_only and bound(checks, state) and checks.get("passed") is False
                            and evidence(checks.get("evidence")))
    if checks_required and not (bound(checks, state) and checks.get("passed") is True
            and checks.get("required_unverified") == [] and evidence(checks.get("evidence"))) and not failed_review_checks:
        return result(state, "run_local_checks", "Review alone cannot satisfy local acceptance.",
                      phase="validating")
    if not (bound(delivery, state) and delivery.get("complete") is True
            and evidence(delivery.get("evidence"))):
        return result(state, "finish_delivery", "Finish all agreed delivery items for this source.",
                      phase="validating")
    if followup_binding(state, state.get("followup")) and state["followup"]["status"] == "ACTIVE":
        return result(state, "disable_followup", "Pause this run's actual heartbeat and read back its state.")
    return result(state, "complete", "Review report delivered with failed-check evidence; acceptance did not pass."
                  if failed_review_checks else "Current review, required checks and delivery all passed.",
                  phase="completed", acceptance_passed=not failed_review_checks)


def browser_fault_code(event):
    codes = (event.get("ui_error"), event.get("reason_code"))
    for code in codes:
        if code in HUMAN_BROWSER_GATES:
            return code
    # Narrow compatibility for old free-text blockers, not a grant of permission.
    reason = str(event.get("reason", "")).casefold()
    if any(word in reason for word in ("login", "captcha", "permission denied", "approval rejected", "登录", "验证码", "权限拒绝")):
        return "auth" if "permission" not in reason and "拒绝" not in reason else "permission_denied"
    if any(word in reason for word in ("user control", "inactive", "unassigned", "用户接管")):
        return "user_control"
    for code in codes:
        if code in BROWSER_FAULTS:
            return code
    if any(word in reason for word in ("space missing", "space not found", "space disappeared", "空间丢失", "空间消失")):
        return "space_missing"
    if "browser crash" in reason or "浏览器崩溃" in reason:
        return "browser_crash"
    return event.get("reason_code") or event.get("ui_error")


def browser_fault_record(state, observer_record=None):
    candidates = [state.get("browser_recovery_fault")]
    if observer_record and observer_binding(observer_record.get("binding") or {}) == observer_binding(state):
        candidates.append(observer_record.get("browser_recovery_fault"))
    current = [item for item in candidates if bound(item, state, token=True)
               and evidence(item.get("evidence")) and item.get("reason_code") in BROWSER_FAULTS]
    return max(current, key=lambda item: timestamp(item["observed_at"]) if item.get("observed_at")
               else datetime.min.replace(tzinfo=timezone.utc), default=None)


def recovery_attempts(state, observer_record=None):
    count = state.get("browser_recovery_attempts", 0)
    require(type(count) is int and 0 <= count <= 2, "invalid browser recovery attempts")
    if observer_record and observer_binding(observer_record.get("binding") or {}) == observer_binding(state):
        prior = observer_record.get("browser_recovery_attempts", 0)
        require(type(prior) is int and 0 <= prior <= 2, "invalid observer browser recovery attempts")
        context = state.get("browser_context") or {}
        fault = observer_record.get("browser_recovery_fault") or {}
        recovered = (bound(context, state, token=True) and evidence(context.get("evidence"))
                     and nonempty(context.get("recovery_event_sha256"))
                     and context["recovery_event_sha256"] != observer_record.get("browser_recovery_event_sha256")
                     and (not fault.get("observed_at") or context.get("observed_at")
                          and timestamp(context["observed_at"]) >= timestamp(fault["observed_at"])))
        if not recovered:
            count = max(count, prior)
    return count


def browser_resume_phase(state):
    return (state.get("resume_phase") if state["phase"] == "blocked"
            and state.get("blocker_reason_code") in BROWSER_FAULTS else state["phase"])


def recover_browser(state, event, code, observer_record=None):
    require(code in BROWSER_FAULTS | HUMAN_BROWSER_GATES, "unclassified browser fault")
    if code in HUMAN_BROWSER_GATES or state.get("blocker_reason_code") in HUMAN_BROWSER_GATES:
        return result(state, "request_browser_input", "Respect actual login, user control or permission denial; do not rebuild to bypass it.")
    if state["phase"] == "paused":
        return result(state, "pause", "An explicit user pause still applies.")
    phase = browser_resume_phase(state)
    require(phase in PHASES - {"paused", "completed"}, "missing resumable browser phase")
    count = recovery_attempts(state, observer_record)
    pending = browser_fault_record(state, observer_record) or {}
    observed = event.get("observed_at") or pending.get("observed_at")
    if observed:
        when = timestamp(observed)
        require(not pending.get("observed_at") or when >= timestamp(pending["observed_at"]),
                "browser fault observations moved backwards")
    fault = record(state, event, reason_code=code, observed_at=observed)
    if count == 2:
        return result(state, "diagnose_browser_recovery", "Stop repeated restarts; diagnose the actual tool/app condition and reuse saved material.",
                      phase=phase, browser_recovery_attempts=count, browser_recovery_fault=fault)
    return result(state, "recover_browser_context", "Reuse task authority: restore the owned space, then rebuild it if confirmed lost; reopen the same URL and reconcile the original request. Never resend or replace the server conversation.",
                  phase=phase, browser_recovery_attempts=count + 1, browser_recovery_fault=fault)


def browser_recovered(state, event, observer_record=None):
    code = browser_fault_code(event)
    require(code in BROWSER_FAULTS, "browser recovery needs the actual recoverable fault classification")
    require(state["phase"] != "paused" and state.get("blocker_reason_code") not in HUMAN_BROWSER_GATES,
            "browser recovery cannot bypass user pause or a human browser gate")
    require(event.get("conversation_url") == state.get("conversation_url"), "recovery changed the server conversation")
    when = timestamp(event.get("observed_at"))
    context = event.get("browser_context") or {}
    space_ids = (context.get("space_id"), event.get("old_space_id"))
    require(context.get("ownership") == "agent" and all(nonempty(value) or type(value) is int and value > 0 for value in space_ids)
            and nonempty(context.get("page_label"))
            and nonempty(event.get("recovery_evidence_ref")), "recovery needs owned old/new space mapping and actual evidence")
    prior = state.get("browser_context") or {}
    require(not prior or prior.get("space_id") == event["old_space_id"], "wrong prior browser space")
    if bound(prior, state, token=True) and prior.get("recovery_evidence_ref"):
        if (notification_digest(event) == prior.get("recovery_event_sha256")
                or prior.get("observed_at") and when <= timestamp(prior["observed_at"])):
            return result(state, "ignore_replayed_browser_recovery", "This success is already recorded or stale; preserve the current context and incident budget.")
    fault = browser_fault_record(state, observer_record) or {}
    require(not fault.get("observed_at") or when >= timestamp(fault["observed_at"]),
            "browser recovery success predates the current fault")
    phase = browser_resume_phase(state)
    require(phase in PHASES - {"paused", "completed"}, "missing browser recovery phase")
    updates = {"phase": phase, "browser_recovery_attempts": 0,
               "blocker_reason_code": state.get("blocker_reason_code") if phase == "blocked" else None,
               "browser_context": record(state, event, **context, old_space_id=event["old_space_id"],
                                                        observed_at=stamp(when),
                                                        recovery_event_sha256=notification_digest(event),
                                                        recovery_evidence_ref=event["recovery_evidence_ref"])}
    candidate = {**state, **updates}
    renewed = event.get("inline_observer_binding")
    if renewed is not None:
        require(state.get("followup_mode") == "inline", "inline renewal requires inline mode")
        old = state.get("inline_observer_binding") or {}
        require(not old or all(renewed.get(key) == old.get(key) for key in ("model", "reasoning")), "recovery must preserve the selected model/effort")
        candidate["inline_observer_binding"] = renewed
        require(inline_execution(candidate, event) is not None, "inline renewal needs actual current execution evidence")
        updates["inline_observer_binding"] = renewed
    status = event.get("request_status")
    require(status in {"present", "absent", "unknown"}, "recovery needs original request readback")
    submitted = state.get("submitted_user_message_id")
    if status == "unknown" or (submitted and (status != "present"
            or event.get("user_message_id") != submitted or event.get("prompt_sha256") != state.get("submitted_prompt_sha256"))):
        return result(state, "reconcile_submission", "Recovery preserves the original request; unknown or mismatched readback never authorizes resend.", **updates)
    if not submitted and not (status == "absent" and event.get("definitive_absence") is True):
        return result(state, "reconcile_submission", "Check original history/draft before the normal send gate.", **updates)
    known_reply = state.get("review_message_id") or (state.get("last_completion") or {}).get("assistant_message_id")
    if known_reply and event.get("assistant_message_id") != known_reply:
        return result(state, "reconcile_submission", "Recover the known response identity without generating another response.", **updates)
    if phase == "blocked":
        return result(state, "continue_independent_work", "Browser restored; the unrelated or unclassified business blocker still needs its own resolution evidence.", **updates)
    view = submission_observer(candidate, event)
    if (web_capture_required(candidate) or not submitted) and view is None:
        return ensure_followup(candidate, "Renew the actual current execution/readback and continue recovery; no user scheduler configuration is needed for inline.", **updates)
    if view:
        updates.update(observer_readback_updates(view))
    action = "watch" if submitted and web_capture_required(candidate) else "continue_current_step" if submitted else "verify_before_submit" if prepared_request(candidate) else "prepare_review_request"
    return result(state, action, "Original conversation/request/source and saved files are preserved; continue the existing capture or send gate.", **updates)


def observe(state, event, observer_record=None):
    require(state["phase"] == "waiting_web" or web_capture_required(state, observer_record),
            "observations require a current reply or required artifact wait")
    require(event.get("conversation_url") == state["conversation_url"], "wrong conversation URL")
    now = timestamp(event.get("observed_at"))
    code = browser_fault_code(event)
    error = code if code in BROWSER_FAULTS | HUMAN_BROWSER_GATES else event.get("ui_error")
    generation = event.get("generation")
    require(error in {"none", "transient", "auth", "user_control", "quota", "provider", "permission_denied"} | BROWSER_FAULTS, "unknown ui_error")
    require(generation in {"idle", "generating", "unknown"}, "unknown generation state")
    pending = {"last_completion": None} if state["phase"] == "waiting_web" else {}
    if error in BROWSER_FAULTS:
        return recover_browser(state, event, error, observer_record)
    if error in {"auth", "user_control", "permission_denied", "quota", "provider"}:
        return result(state, "request_browser_input", "Hand off the browser; assess independent work before blocking the run.",
                      **pending)
    if generation == "generating":
        return result(state, "wait", "Normal generation is not a refresh trigger.", **pending)
    if error == "transient":
        count = state.get("refresh_count", 0)
        require(type(count) is int and 0 <= count <= 3, "invalid refresh_count")
        if count == 3:
            return result(state, "backoff_and_diagnose", "Page recovery budget is not a repair budget.",
                          **pending)
        due = state.get("next_refresh_at")
        if due is None:
            return result(state, "wait", "Preserve evidence, then wait before refreshing.",
                          next_refresh_at=stamp(now + timedelta(seconds=30)), **pending)
        if now < timestamp(due):
            return result(state, "wait", "Refresh cooldown has not elapsed.", **pending)
        return result(state, "reload_same_conversation", "Reload once, then reconcile the original request.",
                      refresh_count=count + 1, **pending,
                      next_refresh_at=stamp(now + timedelta(seconds=(60, 120, 120)[count])))
    reset = {"refresh_count": 0, "next_refresh_at": None}
    if state["phase"] != "waiting_web":
        return result(state, "capture_required_artifacts", "Preserve the collected reply; continue only the outstanding required artifacts.", **reset)
    if event.get("request_present") is not True:
        return result(state, "reconcile_submission", "Missing or unknown is not permission to resend.",
                      last_completion=None, **reset)
    complete = (
        event.get("after_request") is True and generation == "idle"
        and event.get("completion_controls") is True
        and nonempty(event.get("assistant_message_id"))
        and type(event.get("body_chars")) is int and event["body_chars"] > 0
        and isinstance(event.get("body_sha256"), str)
        and SHA256.fullmatch(event["body_sha256"]) is not None
        and nonempty(event.get("raw_reply_path"))
        and event.get("full_body_saved") is True
    )
    if not complete:
        return result(state, "wait", "A full, current, completed response is not yet established.",
                      last_completion=None, **reset)
    current = {k: event[k] for k in ("assistant_message_id", "body_sha256", "body_chars", "observed_at")}
    previous = state.get("last_completion") or {}
    if previous:
        require(now >= timestamp(previous.get("observed_at")), "observation timestamps moved backwards")
    stable = all(previous.get(k) == current[k] for k in ("assistant_message_id", "body_sha256", "body_chars"))
    if stable:
        delta = (now - timestamp(previous.get("observed_at"))).total_seconds()
        if delta >= 10:
            return result(state, "triage_review", "Stable full reply observed; contents still need assessment.",
                          phase="review_ready", review_message_id=event["assistant_message_id"],
                          raw_reply_path=event["raw_reply_path"], last_completion=current, **reset)
        # Preserve the first eligible observation, so frequent polls can reach ten seconds.
        return result(state, "wait", "Require at least ten seconds of stable completed content.", **reset)
    return result(state, "wait", "Confirm this completed message again after at least ten seconds.",
                  last_completion=current, **reset)


def observer_binding(state):
    return {**{key: state.get(key) for key in (
        "run_id", "round", "source_id", "source_binding_digest", "request_token", "contract_digest",
        "acceptance_digest", "consumer_host", "artifact_root", "conversation_url",
        "submitted_user_message_id")}, "execution_scope": state.get("execution_scope") or "repair_loop",
            "followup_mode": state.get("followup_mode") or "durable"}


def observer_identity(state):
    owner = state.get("web_io_binding") or state.get("inline_observer_binding") or {}
    return {key: owner.get(key) for key in ("surface", "thread_id", "host_id", "agent_id", "model", "reasoning")}


def notification_authorized(state):
    permission = state.get("controller_notification_authorization") or {}
    return (permission.get("authorized") is True and nonempty(permission.get("user_instruction_ref"))
            and permission.get("destination_thread_id") == state.get("controller_thread_id")
            and permission.get("destination_host") == state.get("controller_host"))


def notification_digest(payload):
    content = {key: value for key, value in payload.items() if key not in {
        "notification_receipt_sha256", "controller_received_at"}}
    return hashlib.sha256(json.dumps(content, sort_keys=True, ensure_ascii=False,
                                    separators=(",", ":")).encode()).hexdigest()


def notification_key(binding, change):
    return hashlib.sha256(json.dumps({"binding": binding, "change": change}, sort_keys=True,
                                    ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()


def notification_applied(state, key, digest):
    saved = (state.get("received_notifications") or {}).get(key) or {}
    return (saved.get("applied") is True and saved.get("receipt_sha256") == digest
            and saved.get("artifact_root") == state["artifact_root"]
            and saved.get("followup_mode") == state.get("followup_mode", "durable")
            and bound(saved, state, token=True) and evidence(saved.get("evidence")))


def notification_received(state, item, ledger):
    payload = item.get("controller_event") or {}
    saved = (state.get("received_notifications") or {}).get(item["key"]) or {}
    if (saved.get("receipt_sha256") == item.get("receipt_sha256")
            and bound(saved, state, token=True) and evidence(saved.get("evidence"))):
        return True
    # Existing Controller-owned processing state is also a receipt. Never revive
    # a finished old run merely because its observer predates explicit receipts.
    if not payload:
        # v1 observer records kept the completed observation and notification key,
        # but not the whole delivery payload. Match that exact processed result.
        completed = ledger.get("completion_observation") or {}
        reply = {"kind": "reply", "message": completed.get("assistant_message_id"),
                 "sha256": completed.get("body_sha256")}
        if notification_key(ledger["binding"], reply) == item["key"]:
            payload = {**completed, "type": "observation"}
        elif artifact_ready(state) and notification_key(ledger["binding"], {
                "kind": "artifacts", "receipt": state.get("artifact_receipt")}) == item["key"]:
            return True
    if not bound(payload, state, token=True):
        return False
    if payload.get("type") == "observation":
        completed = state.get("last_completion") or {}
        return (state["phase"] != "waiting_web" and state.get("review_message_id") == payload.get("assistant_message_id")
                and completed.get("body_sha256") == payload.get("body_sha256")
                and state.get("raw_reply_path") == payload.get("raw_reply_path"))
    if payload.get("type") == "artifact_receipt":
        return state.get("artifact_receipt") == payload.get("receipt") and artifact_ready(state)
    progress = state.get("web_progress") or {}
    return (payload.get("type") == "web_progress" and bound(progress, state, token=True)
            and progress.get("evidence_ref") == payload.get("actionable_progress_ref"))


def saved_result(state, ledger):
    for item in ledger.get("notifications", []):
        payload = item.get("controller_event")
        if (not isinstance(payload, dict) or notification_digest(payload) != item.get("receipt_sha256")
                or not bound(payload, state, token=True) or payload.get("artifact_root") != state["artifact_root"]
                or notification_applied(state, item["key"], item.get("receipt_sha256"))
                or not notification_received(state, item, ledger)):
            continue
        kind = payload.get("type")
        # Browser-input notifications are observations too. Only the original
        # completed-reply key identifies an unprocessed reply, not an old error.
        reply = notification_key(ledger["binding"], {"kind": "reply",
                                 "message": payload.get("assistant_message_id"),
                                 "sha256": payload.get("body_sha256")})
        if (kind == "observation" and state["phase"] == "waiting_web"
                and item["key"] == reply
                or kind == "artifact_receipt" and state.get("artifact_receipt") != payload.get("receipt")
                or kind == "web_progress" and state["phase"] == "waiting_web"
                and (state.get("web_progress") or {}).get("evidence_ref") != payload.get("actionable_progress_ref")):
            return payload
    return None


def scheduled_observation(state, event, saved):
    """Luna's independent ledger; never return updates for Controller state/events."""
    binding = observer_binding(state)
    ledger = dict(saved or {})
    if observer_binding(ledger.get("binding") or {}) != binding:
        ledger = {"validator": "luna-observer/v1", "binding": binding, "notifications": [],
                  "error_transition": 0}
    require(ledger.get("validator") == "luna-observer/v1"
            and isinstance(ledger.get("notifications"), list)
            and all(isinstance(item, dict) and nonempty(item.get("key"))
                    for item in ledger["notifications"]), "invalid Luna observer record")
    owner = observer_identity(state)
    turn = (state.get("inline_observer_binding") or {}).get("turn_id")
    changed = ledger.get("observer_identity", observer_identity(ledger["binding"])) != owner or ledger.get("inline_turn_id", turn) != turn
    if changed and not ledger.get("text_complete"):
        ledger["last_completion"] = ledger["completion_observation"] = None
    ledger.update(observer_identity=owner, inline_turn_id=turn)
    ledger["browser_recovery_attempts"] = recovery_attempts(state, ledger)
    ledger["browser_recovery_fault"] = browser_fault_record(state, ledger)
    recovery = (state.get("browser_context") or {}).get("recovery_evidence_ref")
    if recovery and recovery != ledger.get("browser_recovery_evidence_ref"):
        ledger["browser_recovery_evidence_ref"] = recovery
    recovery_event = (state.get("browser_context") or {}).get("recovery_event_sha256")
    if recovery_event:
        ledger["browser_recovery_event_sha256"] = recovery_event
    when = timestamp(event.get("observed_at"))
    previous_time = ledger.get("last_observed_at")
    require(previous_time is None or when >= timestamp(previous_time), "observer timestamps moved backwards")
    ledger["last_observed_at"] = stamp(when)

    def answer(action, reason, *, controller_event=None, schedule_action="keep_active", key=None, observe_webpage=False):
        outstanding = any(item.get("status") != "received" for item in ledger["notifications"])
        if outstanding and state["phase"] not in {"paused", "blocked"}:
            schedule_action = "keep_active"
        return {"action": action, "reason": reason, "phase": state["phase"], "terminal": False,
                "activate_controller": action in {"notify_controller", "retry_notification", "return_to_controller"},
                "activate_developer": False, "observe_webpage": observe_webpage,
                "schedule_action": "none" if state.get("followup_mode", "durable") == "inline" else schedule_action,
                "state_updates": {},
                "observer_updates": ledger, "notification_key": key, "controller_event": controller_event}

    kind = event["type"]
    inline = state.get("followup_mode", "durable") == "inline"
    require(kind in {"observer_delivery", "notification_check"}
            or inline == (kind in {"inline_observation", "inline_artifacts"}), "observer surface disagrees with followup_mode")
    if kind in {"scheduled_artifacts", "inline_artifacts"}:
        require(receipt_bound(state, event.get("receipt")), "scheduled artifacts have stale or invalid binding")
        ledger["artifact_observation"] = artifact_observation(state, event)
    ledger["required_artifacts_ready"] = captured_artifacts_ready(state, ledger)
    ledger["notifications"] = [({**item, "status": "received"} if notification_received(state, item, ledger) else item)
                               for item in ledger["notifications"]]
    if kind == "observer_delivery":
        key = event.get("notification_key")
        pending = next((item for item in ledger["notifications"] if item.get("key") == key), None)
        require(pending is not None, "delivery has no pending observer notification")
        require(event.get("delivery_status") in {"delivered", "not_delivered", "unknown", "active_writer"}
                and nonempty(event.get("delivery_evidence_ref")), "notification delivery needs actual evidence")
        require(event.get("destination_thread_id") == state.get("controller_thread_id")
                and event.get("destination_host") == state.get("controller_host"), "delivery destination mismatch")
        if event["delivery_status"] == "delivered":
            require(notification_authorized(state),
                    "delivered notification lacks direct user communication authority or destination binding")
        ledger["notifications"] = [({**item, "status": event["delivery_status"] if item.get("status") != "received" else "received",
                                     "evidence_ref": event["delivery_evidence_ref"], "delivery_observed_at": stamp(when),
                                     "destination_thread_id": event["destination_thread_id"], "destination_host": event["destination_host"],
                                     "next_check_at": stamp(when + timedelta(seconds=60))}
                                    if item.get("key") == key else item)
                                   for item in ledger["notifications"]]
        return answer("record_notification_delivery", "Delivery and Controller receipt are distinct; retain receipt checks without reopening the webpage.")

    outstanding = next((item for item in ledger["notifications"] if item.get("status") != "received"), None)
    if state["phase"] in {"paused", "blocked"}:
        return answer("pause_followup", "Preserve unreceived results and their checkpoint while this run is stopped or blocked.",
                      schedule_action="pause_if_active")
    if kind == "notification_check" or (kind not in {"scheduled_artifacts", "inline_artifacts"} and
            (not web_capture_required(state, ledger) or
            (ledger.get("text_complete") and ledger.get("required_artifacts_ready"))) and outstanding):
        if outstanding is None:
            capture = web_capture_required(state, ledger)
            armed = state.get("awaiting_send") is True and state["phase"] in {"ready_to_submit", "submitting"}
            if capture or armed:
                if submission_observer(state, event) is None:
                    action = "ensure_inline_luna" if inline else "ensure_followup" if web_io_binding(state) else "ensure_luna_owner"
                    return answer(action, "Receipts are closed, but capture or the armed send still needs the verified observer.")
                if capture:
                    action = "capture_required_artifacts" if ledger.get("text_complete") or state["phase"] != "waiting_web" else "keep_quiet"
                    return answer(action, "Receipts are closed; continue the unfinished reply or required artifact capture.",
                                  observe_webpage=True)
                return answer("keep_quiet", "Receipts are closed; preserve the same observer's armed send window.")
            return answer("finish_inline_capture" if inline else "pause_followup", "Controller has received all queued results.",
                          schedule_action="pause_if_active")
        if submission_observer(state, event) is None:
            action = "ensure_inline_luna" if inline else "ensure_followup" if web_io_binding(state) else "ensure_luna_owner"
            return answer(action, "Preserve the unreceived result; restore the actual Luna receipt checker, never a Controller heartbeat.")
        key = event.get("notification_key", outstanding["key"])
        pending = next((item for item in ledger["notifications"] if item["key"] == key), None)
        require(pending is not None, "unknown notification checkpoint")
        if pending.get("status") == "received":
            return answer("check_controller_receipt", "This receipt is closed; check the remaining unreceived result.", key=outstanding["key"])
        readback = event.get("delivery_readback", "unknown")
        require(readback in {"present", "absent", "unknown"}, "invalid delivery readback")
        destination = event.get("destination_status", "unknown")
        require(destination in {"idle", "active_writer", "unknown"}, "invalid destination status")
        if readback != "unknown" or destination != "unknown":
            require(nonempty(event.get("readback_evidence_ref"))
                    and event.get("destination_thread_id") == state.get("controller_thread_id")
                    and event.get("destination_host") == state.get("controller_host"),
                    "delivery readback requires evidence bound to the Controller destination")
            checked = timestamp(event.get("readback_observed_at"))
            attempted = pending.get("delivery_observed_at") or pending.get("attempted_at")
            require(0 <= (when - checked).total_seconds() <= 60
                    and (attempted is None or checked >= timestamp(attempted)),
                    "delivery readback is stale or predates the last delivery attempt")
        if readback == "present":
            pending = {**pending, "status": "delivered", "readback_evidence_ref": event["readback_evidence_ref"]}
            ledger["notifications"] = [pending if item["key"] == key else item for item in ledger["notifications"]]
        if (pending.get("status") in {"not_delivered", "active_writer"} or
                (pending.get("status") in {"pending", "unknown"} and readback == "absent")):
            due = pending.get("next_check_at")
            if (destination == "idle"
                    and (due is None or when >= timestamp(due)) and notification_authorized(state)):
                if pending.get("attempts", 1) >= 3:
                    return answer("delivery_recovery_checkpoint", "Delivery attempt budget is exhausted; retain receipt checks and let Controller read the saved result directly.", key=key)
                payload = pending.get("controller_event")
                require(isinstance(payload, dict) and notification_digest(payload) == pending.get("receipt_sha256"),
                        "retry needs the original saved payload and its receipt SHA")
                pending = {**pending, "status": "pending", "attempts": pending.get("attempts", 1) + 1,
                           "attempted_at": stamp(when), "next_check_at": stamp(when + timedelta(seconds=60))}
                ledger["notifications"] = [pending if item["key"] == key else item for item in ledger["notifications"]]
                return answer("retry_notification", "Confirmed non-delivery and an idle destination permit one same-payload authorized retry.",
                              controller_event=payload, key=key)
        return answer("check_controller_receipt", "Read delivery history, Controller state or the shared receipt; unknown is not non-delivery and delivered is not received.", key=key)

    if (kind not in {"scheduled_artifacts", "inline_artifacts"} or state["phase"] == "completed") and not web_capture_required(state, ledger):
        if state.get("awaiting_send") is True and state["phase"] in {"ready_to_submit", "submitting"}:
            if submission_observer(state, event) is not None:
                return answer("keep_quiet", "The same observer is armed for the imminent send; Luna must reconcile before sending.")
        return answer("finish_inline_capture" if inline else "pause_followup",
                      "No current webpage wait or required capture remains; finish inline capture or pause the same heartbeat and read back.",
                      schedule_action="none" if inline else "pause_if_active")
    if submission_observer(state, event) is None:
        action = "ensure_inline_luna" if inline else "ensure_followup" if web_io_binding(state) else "ensure_luna_owner"
        return answer(action, "Durable polling needs a verified Luna visible owner and fresh ACTIVE readback; "
                      "preserve the existing message. Bounded in-turn observation is not a durable schedule.")

    schedule_action = "keep_active"
    controller_event = None
    notification_material = None
    if kind in {"scheduled_artifacts", "inline_artifacts"}:
        receipt = event.get("receipt")
        require(receipt_bound(state, receipt), "scheduled artifacts have stale or invalid binding")
        proof = current_artifact_observation(state, ledger)
        if (proof and proof["payload"].get("observed_at")
                and timestamp(proof["payload"]["observed_at"]) > when):
            return answer("keep_quiet", "A newer actual verification is already current; preserve the older raw observation without restarting capture.",
                          schedule_action="keep_active" if web_capture_required(state, ledger) else "pause_if_active",
                          observe_webpage=web_capture_required(state, ledger))
        if not artifact_ready({**state, "artifact_receipt": receipt}):
            return answer("capture_required_artifacts", "Required attachments remain; preserve capture obligations without waking Controller.",
                          observe_webpage=True)
        ledger["required_artifacts_ready"] = captured_artifacts_ready(state, ledger)
        schedule_action = "pause_if_active" if ledger["required_artifacts_ready"] and (state["phase"] != "waiting_web" or ledger.get("text_complete")) else "keep_active"
        controller_event = {**event, "type": "artifact_receipt"}
        notification_material = {"kind": "artifacts", "receipt": receipt}
    else:
        require(event.get("request_user_message_id") == state.get("submitted_user_message_id"),
                "observer does not follow the submitted user message")
        prior_completion = ledger.get("completion_observation")
        local = {**state, **{key: ledger.get(key) for key in ("last_completion", "next_refresh_at")},
                 "refresh_count": ledger.get("refresh_count", 0),
                 "browser_recovery_attempts": ledger["browser_recovery_attempts"]}
        observed = observe(local, event, ledger)
        ledger.update({key: value for key, value in observed["state_updates"].items()
                       if key in {"last_completion", "refresh_count", "next_refresh_at", "browser_recovery_attempts", "browser_recovery_fault"}})
        if observed["state_updates"].get("last_completion"):
            ledger["completion_observation"] = {**event, "execution_scope": state.get("execution_scope", "repair_loop")}
        elif "last_completion" in observed["state_updates"]:
            ledger["completion_observation"] = None
        code = browser_fault_code(event)
        error = code if code in BROWSER_FAULTS | HUMAN_BROWSER_GATES else event.get("ui_error")
        error_id = event.get("error_fingerprint") if error != "none" else None
        if error != "none":
            require(nonempty(error_id), "UI errors need a stable content/code fingerprint, not a polling timestamp")
        transition = (error, error_id)
        if list(transition) != ledger.get("last_error_transition"):
            ledger["error_transition"] += 1
            ledger["last_error_transition"] = list(transition)
        if observed["action"] in {"recover_browser_context", "diagnose_browser_recovery"}:
            return answer(observed["action"], observed["reason"])
        if observed["action"] == "capture_required_artifacts":
            return answer(observed["action"], observed["reason"], observe_webpage=True)
        if observed["action"] == "triage_review":
            controller_event = {**event, "type": "observation", "prior_observation": prior_completion}
            notification_material = {"kind": "reply", "message": event["assistant_message_id"],
                                     "sha256": event["body_sha256"]}
            schedule_action = "pause_if_active" if ledger["required_artifacts_ready"] else "keep_active"
            ledger["text_complete"] = True
        elif observed["action"] == "backoff_and_diagnose" or (
                error in {"quota", "provider"} and event.get("recovery_expected") is True):
            return answer("keep_quiet", "Stop repeated refreshes; keep low-cost observation for recovery without waking Controller.")
        elif observed["action"] == "request_browser_input":
            controller_event = {**event, "type": "observation"}
            notification_material = {"kind": "blocker", "transition": ledger["error_transition"],
                                     "error": error, "fingerprint": error_id}
            schedule_action = "pause_if_active" if error in HUMAN_BROWSER_GATES else "keep_active"
        elif event.get("actionable_progress") is True and error == "none":
            require(event.get("after_request") is True and nonempty(event.get("assistant_message_id"))
                    and isinstance(event.get("body_sha256"), str) and SHA256.fullmatch(event["body_sha256"])
                    and nonempty(event.get("raw_reply_path")) and nonempty(event.get("actionable_progress_ref")),
                    "actionable progress needs new message content and evidence for the actionable change")
            controller_event = {**event, "type": "web_progress"}
            notification_material = {"kind": "progress", "message": event["assistant_message_id"],
                                     "sha256": event["body_sha256"]}
        else:
            action = observed["action"] if observed["action"] == "reload_same_conversation" else "keep_quiet"
            return answer(action, observed["reason"], observe_webpage=True)

    key = notification_key(ledger["binding"], notification_material)
    if any(item.get("key") == key for item in ledger["notifications"]):
        return answer("keep_quiet", "This reply/content or error transition already has a receipt; do not wake Controller again.",
                      schedule_action=schedule_action, key=key,
                      observe_webpage=web_capture_required(state) and not (ledger.get("text_complete") and ledger.get("required_artifacts_ready")))
    controller_event = {**controller_event, "execution_scope": state.get("execution_scope", "repair_loop"),
                        "followup_mode": state.get("followup_mode", "durable"), "notification_key": key}
    digest = notification_digest(controller_event)
    controller_event["notification_receipt_sha256"] = digest
    ledger["notifications"] = [*ledger["notifications"], {"key": key, "status": "pending",
                "receipt_sha256": digest, "controller_event": controller_event,
                "attempts": 1 if not inline and notification_authorized(state) else 0, "attempted_at": stamp(when),
                "next_check_at": stamp(when + timedelta(seconds=60)), "evidence": event["evidence"]}]
    action = "return_to_controller" if inline else "notify_controller" if notification_authorized(state) else "save_receipt_for_controller"
    return answer(action, "One new actionable receipt is ready; Controller verifies it before any authorized developer work.",
                  controller_event=controller_event, schedule_action=schedule_action, key=key)


def _decide(state, event, observer_record=None):
    require(isinstance(state, dict) and isinstance(event, dict), "state/event must be JSON objects")
    require(type(state.get("schema_version")) is int and state["schema_version"] == 2,
            "unsupported schema_version; migrate v1 with a new artifact contract and reverify files")
    require(state.get("phase") in PHASES, "invalid phase")
    require(type(state.get("round")) is int and state["round"] > 0, "round must be a positive integer")
    require(nonempty(state.get("run_id")) and nonempty(state.get("request_token")), "missing run identity")
    if state.get("state_path") is not None:
        require(isinstance(state["state_path"], str) and Path(state["state_path"]).is_absolute(),
                "state_path must be absolute")
    require(source(state.get("source_id")), "source_id must pin a full Git hash or MCP content SHA-256")
    require(state.get("source_route") in {"github", "mcp"}, "invalid source_route")
    require(state["source_id"].startswith("git:" if state["source_route"] == "github" else "mcp:"),
            "source_id disagrees with source_route")
    require(state.get("source_binding_digest") == source_binding_digest(
        state["source_route"], state["source_id"], state.get("source_binding")),
        "source binding digest mismatch")
    require(nonempty(state.get("consumer_host")), "missing consumer_host")
    require(isinstance(state.get("artifact_root"), str) and Path(state["artifact_root"]).is_absolute(),
            "artifact_root must be an absolute run directory")
    require(state.get("contract_digest") == contract_digest(state.get("artifact_contract")),
            "artifact contract digest mismatch")
    require(state.get("acceptance_digest") == acceptance_digest(state.get("acceptance_contract")),
            "acceptance contract digest mismatch")
    tokens = state.get("used_request_tokens")
    require(isinstance(tokens, list) and tokens and all(nonempty(x) for x in tokens)
            and len(set(tokens)) == len(tokens) and tokens[-1] == state["request_token"],
            "used_request_tokens must contain unique run history ending in current token")
    candidate = state.get("candidate_source_id")
    require(candidate is None or (source(candidate)
            and candidate.startswith("git:" if state["source_route"] == "github" else "mcp:")),
            "candidate source route mismatch")
    require(type(state.get("pending_file_findings", 0)) is int
            and state.get("pending_file_findings", 0) >= 0, "invalid pending_file_findings")
    require(state.get("execution_scope", "repair_loop") in SCOPES, "invalid execution_scope")
    require(state.get("followup_mode", "durable") in {"durable", "inline"}, "invalid followup_mode")
    require(not (state.get("durable_followup_requested") is True and state.get("followup_mode") == "inline"),
            "explicit durable follow-up cannot silently become inline")
    conversation = state.get("conversation_url")
    if conversation is None:
        resumable_unsent = (state["phase"] in {"paused", "blocked"}
                            and state.get("resume_phase") in {"ready_to_submit", "submitting"})
        require(state["phase"] in {"ready_to_submit", "submitting"} or resumable_unsent,
                "only an unsent initial round may lack a conversation URL")
    else:
        require(conversation_url(conversation),
                "conversation_url must be an observed ChatGPT conversation URL")
    require(evidence(event.get("evidence")), "event needs evidence references")
    for key in ("run_id", "round", "source_id", "source_binding_digest", "request_token",
                "contract_digest", "acceptance_digest",
                "consumer_host", "artifact_root"):
        require(event.get(key) == state[key], "stale or mismatched " + key)
    kind = event.get("type")
    if kind in {"observation", "artifact_receipt", "web_progress"}:
        if kind == "web_progress" or "execution_scope" in event or event.get("notification_key"):
            require(event.get("execution_scope", "repair_loop") == state.get("execution_scope", "repair_loop"),
                    "stale or mismatched execution_scope")
        if (kind == "web_progress" or "followup_mode" in event or event.get("notification_key")
                or event.get("inline_execution_ref") or event.get("followup_view")):
            require(event_followup_mode(event) == state.get("followup_mode", "durable"),
                    "stale or mismatched followup_mode")
    if kind in {"observation", "artifact_receipt", "web_progress"} and event.get("notification_key"):
        require(event.get("notification_receipt_sha256") == notification_digest(event), "Controller receipt payload SHA mismatch")
        if notification_applied(state, event["notification_key"], event["notification_receipt_sha256"]):
            return result(state, "already_applied_notification", "This exact bound original event is already applied; preserve current work.")
    if kind in {"scheduled_observation", "scheduled_artifacts", "inline_observation", "inline_artifacts", "observer_delivery", "notification_check"}:
        return scheduled_observation(state, event, observer_record)
    if kind == "controller_received":
        require(SHA256.fullmatch(str(event.get("notification_key", "")))
                and SHA256.fullmatch(str(event.get("notification_receipt_sha256", ""))), "receipt needs notification identity and payload SHA")
        return result(state, "record_controller_receipt", "Controller read the saved result; receipt alone does not assess or integrate it.")
    if state["phase"] == "completed":
        return result(state, "already_complete", "Start a separately authorized run for new work.")
    if kind == "browser_fault":
        return recover_browser(state, event, browser_fault_code(event), observer_record)
    if kind == "browser_recovered":
        return browser_recovered(state, event, observer_record)
    if kind == "external_blocker" and browser_fault_code(event) in BROWSER_FAULTS:
        return recover_browser(state, event, browser_fault_code(event), observer_record)
    if kind == "bind_controller":
        require(nonempty(event.get("controller_thread_id")) and nonempty(event.get("controller_host"))
                and isinstance(event.get("state_path"), str)
                and Path(event["state_path"]).is_absolute(),
                "bind_controller needs observed thread, host and absolute state path")
        for key in ("controller_thread_id", "controller_host", "state_path"):
            require(not state.get(key) or state[key] == event[key],
                    "existing Controller binding conflicts with " + key)
        return ensure_followup(state, "Controller identity is restored; view or establish the run heartbeat.",
                               controller_thread_id=event["controller_thread_id"],
                               controller_host=event["controller_host"], state_path=event["state_path"])
    if kind == "bind_web_io":
        binding = event.get("web_io_binding")
        require(web_io_binding(state, binding), "bind_web_io needs a verified ready visible Luna owner and actual model/effort readback")
        return ensure_followup({**state, "web_io_binding": binding}, "View the heartbeat targeted to this existing Luna owner.",
                               web_io_binding=binding)
    if kind == "followup_readback":
        receipt = event.get("followup")
        if not followup_binding(state, receipt):
            return ensure_followup(state, "A real, run-bound heartbeat view readback is required.")
        prior = state.get("followup") or {}
        if prior and receipt["automation_id"] != prior.get("automation_id"):
            replaced = (event.get("replacement_of_automation_id") == prior.get("automation_id")
                        and event.get("prior_automation_status") in {"not_found", "deleted"}
                        and nonempty(event.get("prior_automation_evidence_ref"))
                        and receipt["status"] == "ACTIVE")
            if not replaced:
                return ensure_followup(state, "Reuse this run's existing automation ID; verify old-ID removal before replacement.")
            return result(state, "record_followup", "Old automation absence and replacement ACTIVE view are recorded.",
                          followup=receipt,
                          followup_replacement={"old_automation_id": prior["automation_id"],
                                                "old_status": event["prior_automation_status"],
                                                "old_evidence_ref": event["prior_automation_evidence_ref"],
                                                "new_automation_id": receipt["automation_id"]})
        if receipt["status"] != "ACTIVE" and web_capture_required(state, observer_record):
            return ensure_followup(state, "Heartbeat is paused; reactivate and view it before continuing.",
                                   followup=receipt)
        return result(state, "record_followup", "The host view confirms this run's Luna heartbeat state.",
                      followup=receipt, awaiting_send=(receipt["status"] == "ACTIVE"
                          and state["phase"] in {"ready_to_submit", "submitting"} and prepared_request(state)))
    if kind == "followup_closed":
        prior = state.get("followup") or {}
        receipt = event.get("followup")
        require(followup_binding(state, prior) and prior["status"] == "ACTIVE",
                "no active run heartbeat to close")
        require(followup_binding(state, receipt) and receipt["automation_id"] == prior["automation_id"]
                and receipt["status"] == "PAUSED", "closing needs same heartbeat PAUSED view readback")
        if state["phase"] in {"paused", "blocked"}:
            return result(state, "pause", "User pause and heartbeat shutdown are both recorded.",
                          followup=receipt, awaiting_send=False)
        if not web_capture_required(state, observer_record):
            candidate = {**state, "followup": receipt}
            if state["phase"] == "validating":
                answer = completion(candidate, observer_record)
                answer["state_updates"]["followup"] = receipt
                return answer
            return result(state, "continue_current_step", "Polling is paused outside webpage wait; preserve this phase and re-arm before the next send.",
                          followup=receipt)
        answer = completion({**state, "followup": receipt}, observer_record)
        answer["state_updates"]["followup"] = receipt
        if answer["action"] != "complete":
            answer["action"] = "ensure_followup"
            answer["reason"] = "Run remains open; restore the heartbeat before unattended waiting."
        return answer
    if kind == "pause":
        require(event.get("reason") in {"user_stop", "explicit_user_budget"}
                and nonempty(event.get("user_instruction_ref")), "pause requires an explicit user instruction")
        require(state["phase"] not in {"paused", "blocked"}, "already paused/blocked")
        action = ("disable_followup" if followup_binding(state, state.get("followup"))
                  and state["followup"]["status"] == "ACTIVE" else "pause")
        return result(state, action, event["reason"], phase="paused", resume_phase=state["phase"])
    if kind == "resume":
        require(state["phase"] in {"paused", "blocked"}, "resume requires paused/blocked")
        phase = state.get("resume_phase")
        require(phase in PHASES - {"completed", "paused", "blocked"}, "missing resumable phase")
        if browser_fault_code(event) in BROWSER_FAULTS:
            return browser_recovered(state, event, observer_record) if event.get("recovery_evidence_ref") else recover_browser(state, event, browser_fault_code(event), observer_record)
        require(nonempty(event.get("resolution_ref")), "resume needs user resumption or resolved-condition evidence")
        view = submission_observer(state, event, fresh_view=True)
        if view is None and web_capture_required({**state, "phase": phase}):
            return ensure_followup(state, "View this run's ACTIVE heartbeat before restoring unattended work.")
        return result(state, "resume_saved_step", "Continue the saved run, not a duplicate workflow.",
                      phase=phase, blocker_reason_code=None, **(observer_readback_updates(view) if view else {}))
    require(state["phase"] not in {"paused", "blocked"}, "resume the run before other events")
    if kind == "prepare_submission":
        require(state["phase"] == "ready_to_submit", "prepare_submission requires ready_to_submit")
        require("materials_only" not in event or type(event["materials_only"]) is bool,
                "materials_only must be a boolean")
        require(nonempty(event.get("review_request_path"))
                and isinstance(event.get("prompt_sha256"), str)
                and SHA256.fullmatch(event["prompt_sha256"]) is not None
                and nonempty(event.get("requirements_ref"))
                and nonempty(event.get("source_readback_ref"))
                and nonempty(event.get("checks_ref"))
                and nonempty(event.get("dispositions_ref"))
                and event.get("materials_verified") is True,
                "Astra must freeze the request, source, original requirements, checks and dispositions")
        prepared = record(state, event, path=event["review_request_path"], sha256=event["prompt_sha256"],
                          requirements_ref=event["requirements_ref"],
                          source_readback_ref=event["source_readback_ref"],
                          checks_ref=event["checks_ref"],
                          dispositions_ref=event["dispositions_ref"])
        if event.get("materials_only") is True:
            return result(state, "deliver_prepared_request", "Explicit materials-only scope stops before submission.",
                          prepared_request=prepared)
        if state.get("execution_scope") == "materials_only" or event.get("materials_only") is True:
            return result(state, "deliver_prepared_request", "Materials-only scope stops before submission.",
                          prepared_request=prepared)
        if submission_observer(state, event) is None:
            return ensure_followup(state, "Prepare is saved; verify the selected observation mode before sending.",
                                   prepared_request=prepared)
        return result(state, "verify_before_submit", "Request is frozen; verify the selected observer binding before sending.",
                      prepared_request=prepared, awaiting_send=True)
    if kind == "external_blocker":
        code = browser_fault_code(event)
        require(nonempty(event.get("reason")) and evidence(event.get("attempts"))
                and nonempty(event.get("requires_external_change")), "blocker needs attempts and an external change")
        require(type(event.get("independent_work_remaining")) is bool, "declare independent work remaining")
        if event["independent_work_remaining"]:
            return result(state, "continue_independent_work", "Complete authorized work that does not need this condition.")
        return result(state, "request_external_input", event["reason"], phase="blocked", resume_phase=state["phase"], blocker_reason_code=code)
    if kind == "submission":
        require(state.get("execution_scope") != "materials_only", "materials-only scope cannot submit")
        require(state["phase"] in {"ready_to_submit", "submitting", "waiting_web"}, "unexpected submission receipt")
        known_url = state.get("conversation_url")
        event_url = event.get("conversation_url")
        require(event_url == known_url or (known_url is None and
                (event_url is None or conversation_url(event_url))), "wrong conversation URL")
        status = event.get("status")
        if status == "sent":
            require(event.get("request_present") is True, "sent needs user-message readback")
            require(nonempty(event.get("user_message_id")) and event.get("ui_model_verified") is True
                    and SHA256.fullmatch(str(event.get("prompt_sha256", ""))),
                    "sent needs Luna UI model, prompt hash and user-message readback")
            require(conversation_url(event_url), "sent needs actual conversation URL readback")
            require(prepared_request(state) and event["prompt_sha256"] == state["prepared_request"]["sha256"],
                    "sent prompt does not match Astra's frozen review request")
            updates = {"phase": "waiting_web", "conversation_url": event_url,
                       "submitted_user_message_id": event["user_message_id"],
                       "submitted_prompt_sha256": event["prompt_sha256"], "last_completion": None,
                       "awaiting_send": False}
            sent_view = event.get("followup_view") or {}
            reuse_send_view = (nonempty(state.get("send_authorized_view_ref"))
                               and sent_view.get("evidence_ref") == state["send_authorized_view_ref"])
            view = submission_observer(state, event, fresh_view=not reuse_send_view)
            if view is None:
                return ensure_followup(state, "Request is already sent; re-view or establish heartbeat, never resend.",
                                       send_authorized_view_ref=None, **updates)
            return result(state, "watch", "Observe the request already present; never send it again.",
                          send_authorized_view_ref=None, **observer_readback_updates(view), **updates)
        if status == "not_sent":
            require(event.get("definitive_absence") is True, "resend needs definitive absence evidence")
            require(prepared_request(state), "prepare Astra's review request before sending")
            view = submission_observer(state, event, fresh_view=True)
            if view is None:
                return ensure_followup(state, "A fresh ACTIVE heartbeat view is required before submission.",
                                       phase="ready_to_submit", last_completion=None)
            return result(state, "submit_once", "Controller may submit after proving the original request absent.",
                          phase="ready_to_submit", last_completion=None, **observer_readback_updates(view),
                          awaiting_send=True,
                          send_authorized_view_ref=view["evidence_ref"])
        require(status == "unknown", "unknown submission status")
        return result(state, "reconcile_submission", "Inspect history, draft and attachments before any resend.",
                      phase="submitting", last_completion=None, awaiting_send=False)
    if kind == "adopt_submission":
        require(state.get("execution_scope") != "materials_only", "materials-only scope cannot adopt webpage work")
        require(state["phase"] in {"ready_to_submit", "submitting"},
                "adopt_submission requires an unconfirmed initial request")
        if event.get("status") != "verified":
            require(event.get("status") == "unknown", "unknown adoption status")
            return result(state, "reconcile_submission", "Cannot bind the original message; inspect it, do not resend.",
                          phase="submitting")
        event_url = event.get("conversation_url")
        bound_message = (conversation_url(event_url)
                         and (state.get("conversation_url") is None or event_url == state["conversation_url"])
                         and nonempty(event.get("user_message_id"))
                         and isinstance(event.get("prompt_sha256"), str)
                         and SHA256.fullmatch(event["prompt_sha256"]) is not None
                         and nonempty(event.get("raw_user_message_path"))
                         and event.get("source_readback_id") == state["source_id"]
                         and event.get("source_binding_digest_observed") == state["source_binding_digest"]
                         and nonempty(event.get("source_readback_ref"))
                         and type(event.get("web_token_present")) is bool)
        if bound_message:
            if event["web_token_present"]:
                bound_message = event.get("web_request_token") == state["request_token"]
            else:
                bound_message = (event.get("local_import_id") == state["request_token"]
                                 and event.get("web_request_token") is None
                                 and event.get("local_import_id_present_in_web") is False)
        if not bound_message:
            return result(state, "reconcile_submission", "Message identity, prompt, source or local import label is unbound.",
                          phase="submitting")
        updates = {"phase": "waiting_web", "conversation_url": event_url,
                   "submitted_user_message_id": event["user_message_id"],
                   "submitted_prompt_sha256": event["prompt_sha256"],
                   "adopted_without_web_token": not event["web_token_present"],
                   "raw_user_message_path": event["raw_user_message_path"], "last_completion": None,
                   "awaiting_send": False}
        view = submission_observer(state, event, fresh_view=True)
        if view is None:
            return ensure_followup(state, "Existing request is preserved; establish heartbeat before unattended waiting.",
                                   **updates)
        return result(state, "watch", "Observe the adopted user message without resending it.",
                      **observer_readback_updates(view), **updates)
    if kind == "observation":
        submitted = state.get("submitted_user_message_id")
        if submitted:
            require(event.get("request_user_message_id") == submitted,
                    "observation does not follow the submitted user message")
        prior = event.get("prior_observation")
        observed_state = state
        if prior is not None:
            require(bound(prior, state, token=True) and prior.get("artifact_root") == state["artifact_root"]
                    and evidence(prior.get("evidence")) and prior.get("request_user_message_id") == submitted,
                    "stable prior observation is stale or unbound")
            first = observe(state, prior, observer_record)
            require(first["state_updates"].get("last_completion") is not None,
                    "prior observation is not a complete current reply")
            observed_state = {**state, **first["state_updates"]}
        answer = observe(observed_state, event, observer_record)
        if answer["action"] in {"wait", "reconcile_submission", "reload_same_conversation",
                                "backoff_and_diagnose"} and submission_observer(state, event) is None:
            if answer["action"] == "reload_same_conversation":
                answer["state_updates"].pop("refresh_count", None)
                answer["state_updates"].pop("next_refresh_at", None)
            answer = ensure_followup(state, "Preserve the observation; verify the selected observation mode before waiting.",
                                     **answer["state_updates"])
        return answer
    if kind == "web_progress":
        require(state["phase"] == "waiting_web" and event.get("conversation_url") == state["conversation_url"]
                and event.get("request_user_message_id") == state.get("submitted_user_message_id")
                and event.get("actionable_progress") is True and nonempty(event.get("actionable_progress_ref")),
                "web progress needs bound current actionable evidence")
        return result(state, "assess_web_progress", "Inspect the new actionable evidence without assuming reply completion or repair authority.",
                      web_progress=record(state, event, evidence_ref=event["actionable_progress_ref"]))
    if kind == "artifact_receipt":
        require(state["phase"] in {"waiting_web", "review_ready", "repairing", "validating"},
                "artifact receipt requires a current webpage round")
        receipt = event.get("receipt")
        require(isinstance(receipt, dict), "missing artifact receipt")
        proof = artifact_observation(state, event)
        previous_proof = state.get("artifact_observation") or {}
        previous = previous_proof.get("payload") or {}
        if bound(previous, state, token=True) and previous.get("observed_at") and not event.get("observed_at"):
            return result(state, "ignore_stale_artifact_receipt", "An undated legacy receipt cannot replace a newer applied proof; verify the current files locally if reconciliation is needed.")
        if event.get("observed_at"):
            when = timestamp(event["observed_at"])
            if bound(previous, state, token=True) and previous.get("observed_at"):
                before = timestamp(previous["observed_at"])
                if when < before:
                    return result(state, "ignore_stale_artifact_receipt", "Preserve the newer applied verification; read the current original proof.")
                if when == before and (previous_proof.get("conflicting_proof")
                        or required_artifact_snapshot(state, receipt) != required_artifact_snapshot(state, previous.get("receipt"))):
                    require(receipt_bound(state, receipt), "artifacts are mismatched")
                    proof["conflicting_proof"] = (previous_proof["conflicting_proof"]
                        if required_artifact_snapshot(state, receipt) == required_artifact_snapshot(state, previous.get("receipt"))
                        else {"payload": previous, "sha256": previous_proof.get("sha256")})
                    return result(state, "reconcile_artifact_verification", "Preserve the actual same-time conflict until fresh local verification resolves it; do not invent an order.",
                                  artifact_observation=proof)
        candidate = {**state, "artifact_receipt": receipt, "artifact_observation": proof}
        require(receipt_bound(candidate, receipt) and artifact_ready(candidate),
                "artifacts are missing, invalid or mismatched")
        current = current_artifact_observation(candidate, observer_record)
        if current and current["payload"].get("receipt") == receipt:
            proof = current  # This same saved receipt may have fresher actual verification.
            candidate["artifact_observation"] = proof
        updates = {"artifact_receipt": receipt, "artifact_observation": proof}
        if state["phase"] == "waiting_web":
            return result(state, "watch", "Files verified; the complete reply still needs stable observation.",
                          **updates)
        if state.get("execution_scope") == "review_only":
            answer = completion(candidate, observer_record)
            answer["state_updates"].update(updates)
            return answer
        if not current_artifacts_applied(candidate, observer_record):
            answer = artifact_gate(candidate, observer_record)
            answer["state_updates"].update(updates)
            return answer
        if state["phase"] in {"repairing", "validating"}:
            if state.get("pending_file_findings", 0):
                return result(state, "continue_repair_with_files",
                              "Continue the same developer with newly verified files and open findings.",
                              phase="repairing", **updates)
            return result(state, "continue_current_step", "Files verified; preserve current work.",
                          **updates)
        review = state.get("review") or {}
        if review.get("confirmed_findings", 0):
            return result(state, "dispatch_repair", "Verified files now permit dependent repair.",
                          phase="repairing", **updates)
        if review.get("clean") is True:
            answer = completion(candidate, observer_record)
            answer["state_updates"].update(updates)
            return answer
        return result(state, "investigate_review", "Files are ready; resolve remaining claims.",
                      **updates)
    if kind == "assessment":
        require(state["phase"] == "review_ready", "assessment requires review_ready")
        require(nonempty(state.get("review_message_id"))
                and event.get("review_message_id") == state["review_message_id"], "wrong review message")
        require(type(event.get("coverage_complete")) is bool, "declare full review coverage")
        if not event["coverage_complete"]:
            return next_round(state, event, state["source_id"])
        for key in ("confirmed_findings", "unresolved_claims"):
            require(type(event.get(key)) is int and event[key] >= 0, "invalid " + key)
        dependent = event.get("file_dependent_findings", 0)
        if event["confirmed_findings"] and state["artifact_contract"]["required"]:
            require("file_dependent_findings" in event,
                    "assessment must classify file-dependent findings when required artifacts exist")
        require(type(dependent) is int and 0 <= dependent <= event["confirmed_findings"],
                "invalid file_dependent_findings")
        review = record(state, event, clean=not (event["confirmed_findings"] or event["unresolved_claims"]),
                        coverage_complete=True,
                        confirmed_findings=event["confirmed_findings"],
                        unresolved_claims=event["unresolved_claims"], file_dependent_findings=dependent)
        if state.get("execution_scope") == "review_only":
            answer = completion({**state, "review": review, "pending_file_findings": 0}, observer_record)
            answer["state_updates"].update(review=review, pending_file_findings=0, dispatchable_findings=0)
            return answer
        if event["confirmed_findings"]:
            ready = current_artifacts_applied(state, observer_record)
            dispatchable = event["confirmed_findings"] if ready else event["confirmed_findings"] - dependent
            if dispatchable:
                return result(state, "dispatch_repair", "Dispatch verified independent fixes; preserve disputed claims.",
                              phase="repairing", review=review, dispatchable_findings=dispatchable,
                              pending_file_findings=dependent)
            answer = artifact_gate(state, observer_record)
            answer["state_updates"].update(review=review, dispatchable_findings=0, pending_file_findings=dependent)
            return answer
        if event["unresolved_claims"]:
            return result(state, "investigate_review", "Resolve disputed claims with evidence.",
                          review=review, pending_file_findings=0, dispatchable_findings=0)
        answer = completion({**state, "review": review, "pending_file_findings": 0}, observer_record)
        answer["state_updates"]["review"] = review
        answer["state_updates"]["pending_file_findings"] = 0
        answer["state_updates"]["dispatchable_findings"] = 0
        return answer
    if kind == "worker_result":
        require(state.get("execution_scope", "repair_loop") == "repair_loop", "review-only scope cannot accept developer work")
        require(state["phase"] == "repairing", "worker result requires repairing")
        require(source(event.get("candidate_source_id"))
                and event["candidate_source_id"].startswith("git:" if state["source_route"] == "github" else "mcp:")
                and nonempty(event.get("delivery_path")),
                "worker must identify its fixed source and delivery")
        pending = state.get("pending_file_findings", 0)
        addressed = event.get("addressed_file_findings", 0)
        require(type(pending) is int and pending >= 0 and type(addressed) is int
                and 0 <= addressed <= pending, "invalid addressed_file_findings")
        require(addressed == 0 or current_artifacts_applied(state, observer_record),
                "file-dependent findings cannot be addressed before required artifacts verify")
        return result(state, "run_local_checks", "Worker completion is not goal completion.",
                      phase="validating", candidate_source_id=event["candidate_source_id"],
                      pending_file_findings=pending - addressed, review=None)
    if kind == "validation":
        require(state["phase"] == "validating", "validation requires validating")
        checked = state.get("candidate_source_id") or state["source_id"]
        require(event.get("checked_source_id") == checked, "validation checked the wrong source")
        require(type(event.get("passed")) is bool, "passed must be boolean")
        missing = event.get("required_unverified")
        require(isinstance(missing, list) and all(nonempty(x) for x in missing), "list required_unverified checks")
        validation = {**record(state, event), "source_id": checked, "passed": event["passed"],
                      "required_unverified": missing}
        if checked != state["source_id"] and "next_source_binding" in event:
            validation["source_binding_digest"] = source_binding_digest(
                state["source_route"], checked, event["next_source_binding"])
        if not event["passed"]:
            if state.get("execution_scope") == "review_only":
                return result(state, "finish_delivery", "Deliver the review report with failed-check evidence; this scope does not authorize repair.",
                              validation=validation, acceptance_passed=False)
            return result(state, "diagnose_or_repair", "Use the failure evidence; no implicit repair-round limit.",
                          phase="repairing", validation=validation)
        if missing:
            return result(state, "complete_missing_checks", "Required unverified checks still block acceptance.",
                          validation=validation)
        if state.get("pending_file_findings", 0):
            if current_artifacts_applied(state, observer_record):
                return result(state, "continue_repair_with_files",
                              "Open file-dependent findings stay with this developer before resubmission.",
                              phase="repairing", validation=validation)
            answer = artifact_gate(state, observer_record)
            answer["state_updates"]["validation"] = validation
            return answer
        review = state.get("review") or {}
        current_review = (bound(review, state, token=True) and review.get("source_id") == checked
                          and (review.get("coverage_complete") is True if state.get("execution_scope") == "review_only"
                               else review.get("clean") is True)
                          and evidence(review.get("evidence")))
        if checked != state["source_id"] or not current_review:
            answer = next_round(state, event, checked)
        else:
            answer = completion({**state, "validation": validation}, observer_record)
        answer["state_updates"]["validation"] = validation
        return answer
    if kind == "delivery":
        require(state["phase"] == "validating", "delivery gate requires validating")
        require(event.get("delivered_source_id") == state["source_id"], "delivery source mismatch")
        require(type(event.get("complete")) is bool, "declare delivery completion")
        delivery = record(state, event, complete=event["complete"])
        answer = completion({**state, "delivery": delivery}, observer_record)
        answer["state_updates"]["delivery"] = delivery
        return answer
    raise ValueError("unsupported event type")


def decide(state, event, observer_record=None):
    answer = _decide(state, event, observer_record)
    if (event.get("type") in {"controller_received", "observation", "artifact_receipt", "assessment", "worker_result", "web_progress"}
            and event.get("notification_key")):
        key, digest = event["notification_key"], event.get("notification_receipt_sha256")
        require(SHA256.fullmatch(str(key)) and SHA256.fullmatch(str(digest)), "invalid Controller notification receipt")
        previous = (state.get("received_notifications") or {}).get(key) or {}
        require(not bound(previous, state, token=True) or previous.get("receipt_sha256") == digest,
                "notification key already has a different payload SHA")
        if event["type"] in {"observation", "artifact_receipt", "web_progress"}:
            require(digest == notification_digest(event), "Controller receipt payload SHA mismatch")
        received = record(state, event, receipt_sha256=digest, received_at=event.get("controller_received_at"),
                          artifact_root=state["artifact_root"], followup_mode=state.get("followup_mode", "durable"))
        received["applied"] = (event["type"] in {"observation", "artifact_receipt", "web_progress"}
                               and answer["action"] != "reconcile_artifact_verification"
                               or notification_applied(state, key, digest))
        answer["state_updates"]["received_notifications"] = {**(state.get("received_notifications") or {}), key: received}
    # Controller reads the independent observer record before closing its own
    # Web follow-up. Processing a primary event can acknowledge it in this update.
    candidate = {**state, **answer["state_updates"]}
    if ("observer_updates" not in answer and observer_record
            and observer_binding(observer_record.get("binding") or {}) == observer_binding(candidate)
            and candidate["phase"] not in {"paused", "blocked"}
            and web_capture_required(candidate, observer_record)):
        answer["schedule_action"] = "none" if candidate.get("followup_mode") == "inline" else "keep_active"
    if (observer_record and observer_binding(observer_record.get("binding") or {}) == observer_binding(candidate)
            and candidate["phase"] not in {"paused", "blocked"}
            and any(item.get("status") != "received" and not notification_received(candidate, item, observer_record)
                    for item in observer_record.get("notifications", []))):
        answer["schedule_action"] = "none" if state.get("followup_mode", "durable") == "inline" else "keep_active"
        if event["type"] == "followup_closed" or answer["action"] in {"complete", "disable_followup"}:
            answer["action"] = "ensure_followup" if event["type"] == "followup_closed" else "await_controller_receipt"
            answer["reason"] = "Controller receipt remains open; read the saved result before closing this run's Luna follow-up."
            answer["terminal"] = False
            if candidate["phase"] == "completed":
                answer["state_updates"]["phase"] = state["phase"]
                answer["phase"] = state["phase"]
    elif ("observer_updates" not in answer and observer_record
            and observer_binding(observer_record.get("binding") or {}) == observer_binding(candidate)
            and candidate["phase"] in {"waiting_web", "review_ready", "repairing", "validating"}
            and not web_capture_required(candidate, observer_record)):
        answer["schedule_action"] = "none" if candidate.get("followup_mode") == "inline" else "pause_if_active"
        payload = saved_result(candidate, observer_record)
        if payload and event["type"] in {"controller_received", "followup_closed", "followup_readback"}:
            answer.update(action="process_saved_result", reason="Capture and receipt are closed; apply this original saved event locally without rearming or reopening the webpage.",
                          controller_event=payload)
        elif candidate["phase"] == "waiting_web" and event["type"] in {"controller_received", "followup_closed", "followup_readback"}:
            answer.update(action="read_saved_result", reason="Capture is closed; recover the original saved event from its evidence without fabricating a payload or rearming webpage polling.")
    return answer


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--state", required=True, type=Path)
    parser.add_argument("--event", required=True, type=Path)
    parser.add_argument("--observer-record", type=Path, help="Luna-owned ledger input; output contains observer_updates only")
    args = parser.parse_args()
    try:
        answer = decide(json.loads(args.state.read_text(encoding="utf-8")),
                        json.loads(args.event.read_text(encoding="utf-8")),
                        json.loads(args.observer_record.read_text(encoding="utf-8")) if args.observer_record else None)
    except (ValueError, TypeError, OSError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps({"valid": True, **answer}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
