#!/usr/bin/env python3
"""Prepare a message on its recorded write endpoint; no network or state writes.

Input and recovery evidence are caller declarations, not a live ownership probe.
The caller must record an attempt before sending and inspect the actual receipt.
"""

import argparse
import hashlib
import json
from pathlib import Path

from validate_dispatch_route import classify_failure


WRITE_BASES = {"created", "confirmed_delivery", "explicit_user_endpoint", "normal_handoff"}


def require(condition, message):
    if not condition:
        raise ValueError(message)


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def resolve(document):
    require(isinstance(document, dict), "input must be an object")
    for key in ("caller_id", "target_thread_id", "request_id", "prompt"):
        require(nonempty(document.get(key)), "missing " + key)
    digest = hashlib.sha256(document["prompt"].encode("utf-8")).hexdigest()
    identity = {key: document[key] for key in ("caller_id", "target_thread_id", "request_id")}
    identity["payload_sha256"] = digest

    def answer(action, reason, **extra):
        return {"valid": True, **identity, "action": action, "reason": reason,
                "terminal": False, "send_arguments": None, **extra}

    last = document.get("last_delivery")
    if last is not None:
        require(isinstance(last, dict), "last_delivery must be an object")
        require(all(last.get(key) == value for key, value in identity.items()),
                "last delivery must bind the same caller, thread, request and exact prompt")
        require(nonempty(last.get("attempt_id")) and nonempty(last.get("evidence_ref"))
                and nonempty(last.get("host_id")), "last delivery needs its actual attempt and endpoint receipt")
        require(last.get("status") in {"delivered", "not_delivered", "unknown"}, "invalid delivery status")
        if last["status"] == "delivered":
            return answer("collect_result", "Message was delivered; read the task/result instead of sending again.")
        readback = document.get("delivery_readback") or {}
        if readback:
            require(isinstance(readback, dict) and all(readback.get(k) == v for k, v in identity.items())
                    and readback.get("attempt_id") == last["attempt_id"]
                    and nonempty(readback.get("evidence_ref")), "readback must match the original request and attempt")
            require(readback.get("status") in {"present", "absent", "unknown"}, "invalid readback status")
            if readback["status"] == "present":
                return answer("collect_result", "The exact original message is present; do not resend.")
        if last["status"] == "unknown":
            return answer("reconcile_delivery", "Resolve the original attempt through history/receipt; absence in a read is not proof a timed-out send was rejected.")

    binding = document.get("write_binding") or {}
    if not (isinstance(binding, dict) and binding.get("basis") in WRITE_BASES
            and binding.get("caller_id") == document["caller_id"]
            and binding.get("thread_id") == document["target_thread_id"]
            and nonempty(binding.get("host_id")) and nonempty(binding.get("evidence_ref"))):
        return answer("resolve_write_endpoint", "Reuse the caller's creation/success receipt or explicit target; read/list discovery cannot establish a write endpoint.")
    host = binding["host_id"]
    if last:
        failure = classify_failure(last.get("failure_class", "unknown"), last.get("error"))
        if failure not in {"thread_writer_conflict", "transport_timeout", "transport_unavailable"}:
            return answer("inspect_send_failure", "Diagnose the actual rejection; transport recovery does not change model, permissions or scope.")
        recovered = document.get("recovery") or {}
        recovery_bound = (isinstance(recovered, dict)
                           and recovered.get("caller_id") == document["caller_id"]
                           and recovered.get("thread_id") == document["target_thread_id"]
                           and recovered.get("host_id") == host
                           and recovered.get("after_attempt_id") == last["attempt_id"]
                           and nonempty(recovered.get("evidence_ref")))
        # A known original endpoint can repair an explicitly rejected send that
        # used a different reader endpoint. Idle alone never repairs ownership.
        original_endpoint = (host != last["host_id"] and binding["basis"] in
                             {"created", "confirmed_delivery", "normal_handoff"})
        if failure == "thread_writer_conflict":
            if not original_endpoint and not (recovery_bound and recovered.get("kind") == "writer_endpoint_restored"):
                return answer("restore_write_endpoint", "Reconnect to the owning service or verify normal release/handoff; an idle thread is insufficient.")
        elif not original_endpoint and not (recovery_bound and recovered.get("kind") == "same_endpoint_reconnected"):
            return answer("restore_connection", "Restore this recorded connection; do not switch to another readable service.")
    return answer("prepare_send", "Record an unknown/pending attempt, then send this exact message once under existing user authority.",
                  send_arguments={"threadId": document["target_thread_id"], "hostId": host,
                                  "prompt": document["prompt"]})


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("input", type=Path)
    args = parser.parse_args()
    try:
        result = resolve(json.loads(args.input.read_text(encoding="utf-8")))
    except (OSError, ValueError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
