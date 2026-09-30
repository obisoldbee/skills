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


def web_capture_required(state):
    return (state["phase"] == "waiting_web"
            or (state["phase"] in {"review_ready", "repairing", "validating"}
                and nonempty(state.get("raw_reply_path")) and not artifact_ready(state)))


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
                  artifact_contract=contract, contract_digest=digest, artifact_receipt=None,
                  acceptance_contract=acceptance, acceptance_digest=acceptance_hash,
                  prepared_request=None, review=None, review_message_id=None, last_completion=None,
                  submitted_user_message_id=None, submitted_prompt_sha256=None,
                  adopted_without_web_token=False, send_authorized_view_ref=None,
                  awaiting_send=False,
                  pending_file_findings=0, dispatchable_findings=0,
                  refresh_count=0, next_refresh_at=None)


def completion(state):
    review = state.get("review") or {}
    checks = state.get("validation") or {}
    delivery = state.get("delivery") or {}
    if state.get("pending_file_findings", 0):
        return result(state, "obtain_required_artifacts" if not artifact_ready(state)
                      else "continue_repair_with_files",
                      "File-dependent confirmed findings remain open.")
    if not artifact_ready(state):
        return result(state, "obtain_required_artifacts", "Required saved artifacts need current verification.")
    review_only = state.get("execution_scope") == "review_only"
    if not (bound(review, state, token=True)
            and (review.get("coverage_complete") is True if review_only else review.get("clean") is True)
            and evidence(review.get("evidence"))):
        return result(state, "obtain_current_review", "This source has no accepted complete review.")
    checks_required = not review_only or bool(state["acceptance_contract"]["required_checks"])
    if checks_required and not (bound(checks, state) and checks.get("passed") is True
            and checks.get("required_unverified") == [] and evidence(checks.get("evidence"))):
        return result(state, "run_local_checks", "Review alone cannot satisfy local acceptance.",
                      phase="validating")
    if not (bound(delivery, state) and delivery.get("complete") is True
            and evidence(delivery.get("evidence"))):
        return result(state, "finish_delivery", "Finish all agreed delivery items for this source.",
                      phase="validating")
    if followup_binding(state, state.get("followup")) and state["followup"]["status"] == "ACTIVE":
        return result(state, "disable_followup", "Pause this run's actual heartbeat and read back its state.")
    return result(state, "complete", "Current review, required checks and delivery all passed.",
                  phase="completed")


def observe(state, event):
    require(state["phase"] == "waiting_web", "observations require waiting_web")
    require(event.get("conversation_url") == state["conversation_url"], "wrong conversation URL")
    now = timestamp(event.get("observed_at"))
    error = event.get("ui_error")
    generation = event.get("generation")
    require(error in {"none", "transient", "auth", "user_control", "quota", "provider"}, "unknown ui_error")
    require(generation in {"idle", "generating", "unknown"}, "unknown generation state")
    if error in {"auth", "user_control", "quota", "provider"}:
        return result(state, "request_browser_input", "Hand off the browser; assess independent work before blocking the run.",
                      last_completion=None)
    if generation == "generating":
        return result(state, "wait", "Normal generation is not a refresh trigger.", last_completion=None)
    if error == "transient":
        count = state.get("refresh_count", 0)
        require(type(count) is int and 0 <= count <= 3, "invalid refresh_count")
        if count == 3:
            return result(state, "backoff_and_diagnose", "Page recovery budget is not a repair budget.",
                          last_completion=None)
        due = state.get("next_refresh_at")
        if due is None:
            return result(state, "wait", "Preserve evidence, then wait before refreshing.",
                          next_refresh_at=stamp(now + timedelta(seconds=30)), last_completion=None)
        if now < timestamp(due):
            return result(state, "wait", "Refresh cooldown has not elapsed.", last_completion=None)
        return result(state, "reload_same_conversation", "Reload once, then reconcile the original request.",
                      refresh_count=count + 1, last_completion=None,
                      next_refresh_at=stamp(now + timedelta(seconds=(60, 120, 120)[count])))
    reset = {"refresh_count": 0, "next_refresh_at": None}
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
    return {key: state.get(key) for key in (
        "run_id", "round", "source_id", "source_binding_digest", "request_token", "contract_digest",
        "acceptance_digest", "consumer_host", "artifact_root", "conversation_url",
        "submitted_user_message_id", "execution_scope", "followup_mode", "web_io_binding", "inline_observer_binding")}


def notification_authorized(state):
    permission = state.get("controller_notification_authorization") or {}
    return (permission.get("authorized") is True and nonempty(permission.get("user_instruction_ref"))
            and permission.get("destination_thread_id") == state.get("controller_thread_id")
            and permission.get("destination_host") == state.get("controller_host"))


def scheduled_observation(state, event, saved):
    """Luna's independent ledger; never return updates for Controller state/events."""
    binding = observer_binding(state)
    ledger = dict(saved or {})
    if ledger.get("binding") != binding:
        ledger = {"validator": "luna-observer/v1", "binding": binding, "notifications": [],
                  "error_transition": 0}
    require(ledger.get("validator") == "luna-observer/v1"
            and isinstance(ledger.get("notifications"), list)
            and all(isinstance(item, dict) and nonempty(item.get("key"))
                    for item in ledger["notifications"]), "invalid Luna observer record")
    when = timestamp(event.get("observed_at"))
    previous_time = ledger.get("last_observed_at")
    require(previous_time is None or when >= timestamp(previous_time), "observer timestamps moved backwards")
    ledger["last_observed_at"] = stamp(when)

    def answer(action, reason, *, controller_event=None, schedule_action="keep_active", key=None):
        return {"action": action, "reason": reason, "phase": state["phase"], "terminal": False,
                "activate_controller": action in {"notify_controller", "return_to_controller"}, "activate_developer": False,
                "schedule_action": "none" if state.get("followup_mode", "durable") == "inline" else schedule_action,
                "state_updates": {},
                "observer_updates": ledger, "notification_key": key, "controller_event": controller_event}

    kind = event["type"]
    inline = state.get("followup_mode", "durable") == "inline"
    require(inline == (kind in {"inline_observation", "inline_artifacts", "observer_delivery"})
            or kind == "observer_delivery", "observer surface disagrees with followup_mode")
    if kind == "observer_delivery":
        key = event.get("notification_key")
        pending = next((item for item in ledger["notifications"] if item.get("key") == key), None)
        require(pending is not None, "delivery has no pending observer notification")
        require(event.get("delivery_status") in {"delivered", "not_delivered", "unknown"}
                and nonempty(event.get("delivery_evidence_ref")), "notification delivery needs actual evidence")
        if event["delivery_status"] == "delivered":
            require(notification_authorized(state)
                    and event.get("destination_thread_id") == state.get("controller_thread_id")
                    and event.get("destination_host") == state.get("controller_host"),
                    "delivered notification lacks direct user communication authority or destination binding")
        ledger["notifications"] = [({**item, "status": event["delivery_status"],
                                     "evidence_ref": event["delivery_evidence_ref"]} if item.get("key") == key else item)
                                   for item in ledger["notifications"]]
        return answer("record_notification_delivery", "Receipt records delivery; unknown or failed sends never trigger blind retries.")

    if not web_capture_required(state) or (ledger.get("text_complete") and ledger.get("required_artifacts_ready")):
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
        if not artifact_ready({**state, "artifact_receipt": receipt}):
            return answer("capture_required_artifacts", "Required attachments remain; preserve capture obligations without waking Controller.")
        ledger["required_artifacts_ready"] = True
        schedule_action = "pause_if_active" if state["phase"] != "waiting_web" or ledger.get("text_complete") else "keep_active"
        controller_event = {**event, "type": "artifact_receipt"}
        notification_material = {"kind": "artifacts", "receipt": receipt}
    elif state["phase"] != "waiting_web":
        return answer("capture_required_artifacts", "Text is collected; only the outstanding required attachments need observation.")
    else:
        require(event.get("request_user_message_id") == state.get("submitted_user_message_id"),
                "observer does not follow the submitted user message")
        prior_completion = ledger.get("completion_observation")
        local = {**state, **{key: ledger.get(key) for key in ("last_completion", "next_refresh_at")},
                 "refresh_count": ledger.get("refresh_count", 0)}
        observed = observe(local, event)
        ledger.update({key: value for key, value in observed["state_updates"].items()
                       if key in {"last_completion", "refresh_count", "next_refresh_at"}})
        if observed["state_updates"].get("last_completion"):
            ledger["completion_observation"] = {**event, "execution_scope": state.get("execution_scope", "repair_loop")}
        elif "last_completion" in observed["state_updates"]:
            ledger["completion_observation"] = None
        error = event.get("ui_error")
        error_id = event.get("error_fingerprint") if error != "none" else None
        if error != "none":
            require(nonempty(error_id), "UI errors need a stable content/code fingerprint, not a polling timestamp")
        transition = (error, error_id)
        if list(transition) != ledger.get("last_error_transition"):
            ledger["error_transition"] += 1
            ledger["last_error_transition"] = list(transition)
        if observed["action"] == "triage_review":
            controller_event = {**event, "type": "observation", "prior_observation": prior_completion}
            notification_material = {"kind": "reply", "message": event["assistant_message_id"],
                                     "sha256": event["body_sha256"]}
            schedule_action = "pause_if_active" if artifact_ready(state) else "keep_active"
            ledger["text_complete"] = True
            ledger["required_artifacts_ready"] = artifact_ready(state)
        elif observed["action"] == "backoff_and_diagnose" or (
                error in {"quota", "provider"} and event.get("recovery_expected") is True):
            return answer("keep_quiet", "Stop repeated refreshes; keep low-cost observation for recovery without waking Controller.")
        elif observed["action"] == "request_browser_input":
            controller_event = {**event, "type": "observation"}
            notification_material = {"kind": "blocker", "transition": ledger["error_transition"],
                                     "error": error, "fingerprint": error_id}
            schedule_action = "pause_if_active" if error in {"auth", "user_control"} else "keep_active"
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
            return answer(action, observed["reason"])

    key = hashlib.sha256(json.dumps({"binding": binding, "change": notification_material},
                                   sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()
    if any(item.get("key") == key for item in ledger["notifications"]):
        return answer("keep_quiet", "This reply/content or error transition already has a receipt; do not wake Controller again.",
                      schedule_action=schedule_action, key=key)
    ledger["notifications"] = [*ledger["notifications"], {"key": key, "status": "pending",
                                                          "evidence": event["evidence"]}]
    action = "return_to_controller" if inline else "notify_controller" if notification_authorized(state) else "save_receipt_for_controller"
    return answer(action, "One new actionable receipt is ready; Controller verifies it before any authorized developer work.",
                  controller_event=controller_event, schedule_action=schedule_action, key=key)


def decide(state, event, observer_record=None):
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
    if kind in {"scheduled_observation", "scheduled_artifacts", "inline_observation", "inline_artifacts", "observer_delivery"}:
        return scheduled_observation(state, event, observer_record)
    if state["phase"] == "completed":
        return result(state, "already_complete", "Start a separately authorized run for new work.")
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
        if receipt["status"] != "ACTIVE" and web_capture_required(state):
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
        if not web_capture_required(state):
            candidate = {**state, "followup": receipt}
            if state["phase"] == "validating":
                answer = completion(candidate)
                answer["state_updates"]["followup"] = receipt
                return answer
            return result(state, "continue_current_step", "Polling is paused outside webpage wait; preserve this phase and re-arm before the next send.",
                          followup=receipt)
        answer = completion({**state, "followup": receipt})
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
        require(nonempty(event.get("resolution_ref")), "resume needs user resumption or resolved-condition evidence")
        view = submission_observer(state, event, fresh_view=True)
        if view is None and web_capture_required({**state, "phase": phase}):
            return ensure_followup(state, "View this run's ACTIVE heartbeat before restoring unattended work.")
        return result(state, "resume_saved_step", "Continue the saved run, not a duplicate workflow.",
                      phase=phase, **(observer_readback_updates(view) if view else {}))
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
        require(nonempty(event.get("reason")) and evidence(event.get("attempts"))
                and nonempty(event.get("requires_external_change")), "blocker needs attempts and an external change")
        require(type(event.get("independent_work_remaining")) is bool, "declare independent work remaining")
        if event["independent_work_remaining"]:
            return result(state, "continue_independent_work", "Complete authorized work that does not need this condition.")
        return result(state, "request_external_input", event["reason"], phase="blocked", resume_phase=state["phase"])
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
            first = observe(state, prior)
            require(first["state_updates"].get("last_completion") is not None,
                    "prior observation is not a complete current reply")
            observed_state = {**state, **first["state_updates"]}
        answer = observe(observed_state, event)
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
        candidate = {**state, "artifact_receipt": receipt}
        require(receipt_bound(candidate, receipt) and artifact_ready(candidate),
                "artifacts are missing, invalid or mismatched")
        if state["phase"] == "waiting_web":
            return result(state, "watch", "Files verified; the complete reply still needs stable observation.",
                          artifact_receipt=receipt)
        if state.get("execution_scope") == "review_only":
            answer = completion(candidate)
            answer["state_updates"]["artifact_receipt"] = receipt
            return answer
        if state["phase"] in {"repairing", "validating"}:
            if state.get("pending_file_findings", 0):
                return result(state, "continue_repair_with_files",
                              "Continue the same developer with newly verified files and open findings.",
                              phase="repairing", artifact_receipt=receipt)
            return result(state, "continue_current_step", "Files verified; preserve current work.",
                          artifact_receipt=receipt)
        review = state.get("review") or {}
        if review.get("confirmed_findings", 0):
            return result(state, "dispatch_repair", "Verified files now permit dependent repair.",
                          phase="repairing", artifact_receipt=receipt)
        if review.get("clean") is True:
            answer = completion(candidate)
            answer["state_updates"]["artifact_receipt"] = receipt
            return answer
        return result(state, "investigate_review", "Files are ready; resolve remaining claims.",
                      artifact_receipt=receipt)
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
            answer = completion({**state, "review": review, "pending_file_findings": 0})
            answer["state_updates"].update(review=review, pending_file_findings=0, dispatchable_findings=0)
            return answer
        if event["confirmed_findings"]:
            ready = artifact_ready(state)
            dispatchable = event["confirmed_findings"] if ready else event["confirmed_findings"] - dependent
            if dispatchable:
                return result(state, "dispatch_repair", "Dispatch verified independent fixes; preserve disputed claims.",
                              phase="repairing", review=review, dispatchable_findings=dispatchable,
                              pending_file_findings=dependent)
            return result(state, "obtain_required_artifacts", "File-dependent repairs await verified required files.",
                          review=review, dispatchable_findings=0, pending_file_findings=dependent)
        if event["unresolved_claims"]:
            return result(state, "investigate_review", "Resolve disputed claims with evidence.",
                          review=review, pending_file_findings=0, dispatchable_findings=0)
        answer = completion({**state, "review": review, "pending_file_findings": 0})
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
        require(addressed == 0 or artifact_ready(state),
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
            return result(state, "diagnose_or_repair", "Use the failure evidence; no implicit repair-round limit.",
                          phase="repairing", validation=validation)
        if missing:
            return result(state, "complete_missing_checks", "Required unverified checks still block acceptance.",
                          validation=validation)
        if state.get("pending_file_findings", 0):
            return result(state, "continue_repair_with_files" if artifact_ready(state)
                          else "obtain_required_artifacts",
                          "Open file-dependent findings stay with this developer before resubmission.",
                          phase="repairing" if artifact_ready(state) else "validating",
                          validation=validation)
        review = state.get("review") or {}
        current_review = (bound(review, state, token=True) and review.get("source_id") == checked
                          and (review.get("coverage_complete") is True if state.get("execution_scope") == "review_only"
                               else review.get("clean") is True)
                          and evidence(review.get("evidence")))
        if checked != state["source_id"] or not current_review:
            answer = next_round(state, event, checked)
        else:
            answer = completion({**state, "validation": validation})
        answer["state_updates"]["validation"] = validation
        return answer
    if kind == "delivery":
        require(state["phase"] == "validating", "delivery gate requires validating")
        require(event.get("delivered_source_id") == state["source_id"], "delivery source mismatch")
        require(type(event.get("complete")) is bool, "declare delivery completion")
        delivery = record(state, event, complete=event["complete"])
        answer = completion({**state, "delivery": delivery})
        answer["state_updates"]["delivery"] = delivery
        return answer
    raise ValueError("unsupported event type")


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
