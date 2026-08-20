#!/usr/bin/env python3
"""Validate that a visible-task claim is backed by a create_thread receipt."""

import argparse
import json
from pathlib import Path
import re
import sys


STATUSES = {"created_confirmed", "created_unconfirmed", "queued", "failed"}
PROMPT_STATES = {"receipt", "readback", "false"}
FORBIDDEN_FIELDS = {"agent_path", "agent_thread_id", "agentPath", "agentThreadId"}
FORBIDDEN_TOOL_MARKERS = ("spawn_agent", "subagent", "collaboration")
ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{7,}$")


def add_error(errors, message):
    if message not in errors:
        errors.append(message)


def optional_string(value, field, errors):
    if value is None:
        return ""
    if not isinstance(value, str):
        add_error(errors, f"{field} must be a string or null")
        return ""
    return value.strip()


def required_string(value, field, errors):
    result = optional_string(value, field, errors)
    if not result:
        add_error(errors, f"{field} must be a non-empty string")
    return result


def tool_leaf(tool):
    leaf = tool.replace("\\", "/").rsplit("/", 1)[-1]
    if "__" in leaf:
        return leaf.rsplit("__", 1)[-1]
    return leaf.rsplit(".", 1)[-1]


def validate_identifier(value, field, errors):
    if not value:
        return
    if value.startswith("/") or "/root/" in value or "\\" in value:
        add_error(errors, f"{field} must be a task identifier, not an agent path")
    elif not ID_PATTERN.fullmatch(value):
        add_error(errors, f"{field} has an invalid identifier shape")


def validate_receipt(receipt):
    errors = []
    if not isinstance(receipt, dict):
        return {
            "valid": False,
            "errors": ["receipt root must be an object"],
            "classification": "invalid_visible_task_evidence",
            "registerable": False,
        }

    for field in FORBIDDEN_FIELDS.intersection(receipt):
        add_error(errors, f"{field} is a hidden-subagent field and is forbidden")

    actual_tool = required_string(receipt.get("actual_tool"), "actual_tool", errors)
    lowered_tool = actual_tool.lower()
    if any(marker in lowered_tool for marker in FORBIDDEN_TOOL_MARKERS):
        add_error(errors, "actual_tool must not use a collaboration or subagent surface")
    elif actual_tool and tool_leaf(actual_tool) != "create_thread":
        add_error(errors, "actual_tool must have leaf name create_thread")

    status = required_string(receipt.get("status"), "status", errors)
    if status and status not in STATUSES:
        add_error(errors, f"status must be one of: {', '.join(sorted(STATUSES))}")

    surface = required_string(receipt.get("surface"), "surface", errors)
    if surface and surface != "visible_thread":
        add_error(errors, "surface must be visible_thread")

    requested_route = required_string(
        receipt.get("requested_route"), "requested_route", errors
    ).lower()
    if requested_route in {"spark", "spark-xhigh"}:
        add_error(errors, "Spark cannot produce a visible-task receipt")

    task_kind = required_string(receipt.get("task_kind"), "task_kind", errors)
    if task_kind and task_kind != "codex":
        add_error(errors, "task_kind must be codex")

    prompt_verified_value = receipt.get("prompt_verified")
    if prompt_verified_value is False:
        prompt_verified = "false"
    else:
        prompt_verified = required_string(
            prompt_verified_value, "prompt_verified", errors
        )
    if prompt_verified and prompt_verified not in PROMPT_STATES:
        add_error(
            errors,
            f"prompt_verified must be one of: {', '.join(sorted(PROMPT_STATES))}",
        )

    thread_id = optional_string(receipt.get("thread_id"), "thread_id", errors)
    client_thread_id = optional_string(
        receipt.get("client_thread_id"), "client_thread_id", errors
    )
    host_id = optional_string(receipt.get("host_id"), "host_id", errors)
    validate_identifier(thread_id, "thread_id", errors)
    validate_identifier(client_thread_id, "client_thread_id", errors)

    failure = optional_string(receipt.get("failure"), "failure", errors)

    if status in {"created_confirmed", "created_unconfirmed"}:
        if not thread_id:
            add_error(errors, f"status={status} requires thread_id")
        if client_thread_id:
            add_error(errors, f"status={status} must not include client_thread_id")
        if not host_id:
            add_error(errors, f"status={status} requires host_id")
    elif status == "queued":
        if not client_thread_id:
            add_error(errors, "status=queued requires client_thread_id")
        if thread_id:
            add_error(errors, "status=queued must not include thread_id")
    elif status == "failed":
        if thread_id or client_thread_id:
            add_error(errors, "status=failed must not include task identifiers")
        if not failure:
            add_error(errors, "status=failed requires failure")

    if status == "created_confirmed" and prompt_verified not in {"receipt", "readback"}:
        add_error(
            errors,
            "status=created_confirmed requires prompt_verified=receipt or readback",
        )
    if status in {"created_unconfirmed", "queued", "failed"} and prompt_verified != "false":
        add_error(errors, f"status={status} requires prompt_verified=false")

    classification = (
        "invalid_visible_task_evidence"
        if errors
        else "creation_failure"
        if status == "failed"
        else "visible_task_receipt"
    )
    registerable = not errors and status in {
        "created_confirmed",
        "created_unconfirmed",
        "queued",
    }

    return {
        "valid": not errors,
        "errors": errors,
        "classification": classification,
        "registerable": registerable,
        "receipt": {
            "actual_tool": actual_tool,
            "status": status,
            "surface": surface,
            "requested_route": requested_route,
            "task_kind": task_kind,
            "thread_id": thread_id,
            "client_thread_id": client_thread_id,
            "host_id": host_id,
            "prompt_verified": prompt_verified,
            "failure": failure,
        },
    }


def main():
    parser = argparse.ArgumentParser(
        description="Validate a normalized create_thread receipt before task registration."
    )
    parser.add_argument("receipt_file", help="JSON receipt path.")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()

    try:
        receipt = json.loads(Path(args.receipt_file).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        result = {
            "valid": False,
            "errors": [f"cannot read receipt: {exc}"],
            "classification": "invalid_visible_task_evidence",
            "registerable": False,
        }
    else:
        result = validate_receipt(receipt)

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print("VALID" if result["valid"] else "INVALID")
        for error in result["errors"]:
            print(f"- {error}")
    return 0 if result["valid"] else 2


if __name__ == "__main__":
    sys.exit(main())
