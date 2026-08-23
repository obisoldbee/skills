#!/usr/bin/env python3
"""Validate a media-creator browser envelope without executing it."""

from __future__ import annotations

import argparse
import json
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any


SCHEMA = "media-creator-browser-envelope/v1"
EXECUTION_MODES = {"execute"}
NON_EXECUTION_MODES = {"prompt", "planning", "preview", "dry_run"}
ROUTES = {"chatgpt-web-image", "minimax-web-music"}
BASE_FIELDS = {
    "schema",
    "mode",
    "request_authority",
    "execution_role",
    "handoff_depth",
    "project",
    "route",
    "authority",
    "execution_location",
    "executor",
    "payload_author",
    "worker_creative_rewrite",
    "final_provider_payload",
    "submission_limit",
    "provider_switch_after_submission",
    "download_retry",
    "recursive_dispatch",
}
VISIBLE_FIELDS = {"orchestrator", "created_and_validated_by", "luna"}
SIDE_EFFECT_FIELDS = {"open_browser", "provider_call", "create_thread"}
LUNA_FIELDS = {"route", "model", "reasoning", "thread", "surface"}


def add_error(errors: list[str], message: str) -> None:
    if message not in errors:
        errors.append(message)


def exact_fields(
    value: Any, expected: set[str], field: str, errors: list[str]
) -> bool:
    if not isinstance(value, dict):
        add_error(errors, f"{field} must be an object")
        return False
    observed = set(value)
    if observed != expected:
        add_error(
            errors,
            f"{field} fields must be exactly {sorted(expected)}; "
            f"missing={sorted(expected - observed)} extra={sorted(observed - expected)}",
        )
        return False
    return True


def required_string(
    value: Any, field: str, errors: list[str], *, allow_empty: bool = False
) -> str:
    if not isinstance(value, str) or (not allow_empty and not value.strip()):
        qualifier = "a string" if allow_empty else "a non-empty string"
        add_error(errors, f"{field} must be {qualifier}")
        return ""
    return value if allow_empty else value.strip()


def required_bool(value: Any, field: str, errors: list[str]) -> bool | None:
    if type(value) is not bool:
        add_error(errors, f"{field} must be a boolean")
        return None
    return value


def is_absolute_path(value: str) -> bool:
    return PurePosixPath(value).is_absolute() or PureWindowsPath(value).is_absolute()


def validate_output_path(value: Any, field: str, errors: list[str]) -> None:
    normalized = required_string(value, field, errors)
    if normalized and not is_absolute_path(normalized):
        add_error(errors, f"{field} must be an absolute caller-authorized path")


def validate_payload(route: str, payload: Any, errors: list[str]) -> None:
    if route == "chatgpt-web-image":
        expected = {"final_image_prompt", "inputs", "output_path"}
        if not exact_fields(payload, expected, "final_provider_payload", errors):
            return
        required_string(
            payload.get("final_image_prompt"),
            "final_provider_payload.final_image_prompt",
            errors,
        )
        inputs = payload.get("inputs")
        if not isinstance(inputs, list):
            add_error(errors, "final_provider_payload.inputs must be a list")
        else:
            for index, item in enumerate(inputs):
                normalized = required_string(
                    item, f"final_provider_payload.inputs[{index}]", errors
                )
                if normalized and not is_absolute_path(normalized):
                    add_error(
                        errors,
                        f"final_provider_payload.inputs[{index}] must be an absolute path",
                    )
        validate_output_path(
            payload.get("output_path"),
            "final_provider_payload.output_path",
            errors,
        )
    elif route == "minimax-web-music":
        expected = {"title", "mode", "style_prompt", "lyrics", "count", "output_path"}
        if not exact_fields(payload, expected, "final_provider_payload", errors):
            return
        required_string(payload.get("title"), "final_provider_payload.title", errors)
        mode = required_string(payload.get("mode"), "final_provider_payload.mode", errors)
        if mode and mode not in {"instrumental", "vocal"}:
            add_error(errors, "final_provider_payload.mode must be instrumental or vocal")
        required_string(
            payload.get("style_prompt"),
            "final_provider_payload.style_prompt",
            errors,
        )
        required_string(
            payload.get("lyrics"),
            "final_provider_payload.lyrics",
            errors,
            allow_empty=True,
        )
        if type(payload.get("count")) is not int or payload.get("count") != 1:
            add_error(errors, "final_provider_payload.count must be exactly 1")
        validate_output_path(
            payload.get("output_path"),
            "final_provider_payload.output_path",
            errors,
        )


def validate_authority(
    authority: Any,
    expected_provider: bool,
    expected_visible: bool,
    errors: list[str],
) -> None:
    expected_fields = {
        "provider_execution_authority",
        "visible_task_creation_authority",
    }
    if not exact_fields(authority, expected_fields, "authority", errors):
        return
    provider = required_bool(
        authority.get("provider_execution_authority"),
        "authority.provider_execution_authority",
        errors,
    )
    visible = required_bool(
        authority.get("visible_task_creation_authority"),
        "authority.visible_task_creation_authority",
        errors,
    )
    if provider is not None and provider is not expected_provider:
        add_error(
            errors,
            f"authority.provider_execution_authority must be {str(expected_provider).lower()}",
        )
    if visible is not None and visible is not expected_visible:
        add_error(
            errors,
            f"authority.visible_task_creation_authority must be {str(expected_visible).lower()}",
        )


def validate_envelope(envelope: Any) -> dict[str, Any]:
    errors: list[str] = []
    if not isinstance(envelope, dict):
        return {
            "valid": False,
            "errors": ["envelope root must be an object"],
            "provider_calls": False,
            "secrets_read": False,
        }

    mode = required_string(envelope.get("mode"), "mode", errors)
    non_execution = mode in NON_EXECUTION_MODES
    visible_execution = (
        mode in EXECUTION_MODES
        and envelope.get("request_authority") == "explicit_visible_task"
    )
    expected_fields = set(BASE_FIELDS)
    if non_execution:
        expected_fields.add("side_effects")
    if visible_execution:
        expected_fields.update(VISIBLE_FIELDS)
    exact_fields(envelope, expected_fields, "envelope", errors)

    if envelope.get("schema") != SCHEMA:
        add_error(errors, f"schema must be {SCHEMA}")
    if mode not in EXECUTION_MODES | NON_EXECUTION_MODES:
        add_error(
            errors,
            "mode must be execute, prompt, planning, preview, or dry_run",
        )

    route = required_string(envelope.get("route"), "route", errors)
    if route and route not in ROUTES:
        add_error(errors, f"route must be one of: {', '.join(sorted(ROUTES))}")
    required_string(envelope.get("project"), "project", errors)
    if envelope.get("payload_author") != "originating_main_task":
        add_error(errors, "payload_author must be originating_main_task")
    if envelope.get("worker_creative_rewrite") is not False:
        add_error(errors, "worker_creative_rewrite must be false")
    if envelope.get("provider_switch_after_submission") is not False:
        add_error(errors, "provider_switch_after_submission must be false")
    if envelope.get("recursive_dispatch") is not False:
        add_error(errors, "recursive_dispatch must be false")
    validate_payload(route, envelope.get("final_provider_payload"), errors)

    if non_execution:
        if envelope.get("request_authority") != "non_execution":
            add_error(errors, "non-execution mode requires request_authority=non_execution")
        validate_authority(envelope.get("authority"), False, False, errors)
        if envelope.get("execution_role") != "planner":
            add_error(errors, "non-execution mode requires execution_role=planner")
        if type(envelope.get("handoff_depth")) is not int or envelope.get(
            "handoff_depth"
        ) != 0:
            add_error(errors, "non-execution mode requires handoff_depth=0")
        if envelope.get("execution_location") != "none":
            add_error(errors, "non-execution mode requires execution_location=none")
        if envelope.get("executor") is not None:
            add_error(errors, "non-execution mode must not select an executor")
        if type(envelope.get("submission_limit")) is not int or envelope.get(
            "submission_limit"
        ) != 0:
            add_error(errors, "non-execution mode requires submission_limit=0")
        if envelope.get("download_retry") != "not_applicable":
            add_error(errors, "non-execution mode requires download_retry=not_applicable")
        side_effects = envelope.get("side_effects")
        if exact_fields(side_effects, SIDE_EFFECT_FIELDS, "side_effects", errors):
            for field in sorted(SIDE_EFFECT_FIELDS):
                if side_effects.get(field) is not False:
                    add_error(errors, f"side_effects.{field} must be false")
    elif mode == "execute":
        if type(envelope.get("submission_limit")) is not int or envelope.get(
            "submission_limit"
        ) != 1:
            add_error(errors, "execute mode requires submission_limit=1")
        if envelope.get("download_retry") != "same_submitted_result_only":
            add_error(
                errors,
                "execute mode requires download_retry=same_submitted_result_only",
            )

        request_authority = envelope.get("request_authority")
        if request_authority == "ordinary_browser_generation":
            validate_authority(envelope.get("authority"), True, False, errors)
            if envelope.get("execution_role") != "browser_executor":
                add_error(errors, "current-task execution requires execution_role=browser_executor")
            if type(envelope.get("handoff_depth")) is not int or envelope.get(
                "handoff_depth"
            ) != 0:
                add_error(errors, "current-task execution requires handoff_depth=0")
            if envelope.get("execution_location") != "current_task":
                add_error(errors, "ordinary browser generation must execute in current_task")
            if envelope.get("executor") != "ego-browser":
                add_error(errors, "current-task execution requires executor=ego-browser")
        elif request_authority == "explicit_visible_task":
            validate_authority(envelope.get("authority"), True, True, errors)
            if envelope.get("execution_role") != "browser_worker":
                add_error(errors, "visible execution requires execution_role=browser_worker")
            if type(envelope.get("handoff_depth")) is not int or envelope.get(
                "handoff_depth"
            ) != 1:
                add_error(errors, "visible execution requires handoff_depth=1")
            if envelope.get("execution_location") != "luna_visible_task":
                add_error(errors, "visible execution requires execution_location=luna_visible_task")
            if envelope.get("executor") != "ego-browser":
                add_error(errors, "visible execution requires executor=ego-browser")
            if envelope.get("orchestrator") != "project-handoff":
                add_error(errors, "visible execution requires orchestrator=project-handoff")
            if envelope.get("created_and_validated_by") != "originating_main_task":
                add_error(
                    errors,
                    "visible execution must be created_and_validated_by=originating_main_task",
                )
            luna = envelope.get("luna")
            expected_luna = {
                "route": "luna-max",
                "model": "gpt-5.6-luna",
                "reasoning": "max",
                "thread": "visible",
                "surface": "visible_thread",
            }
            if exact_fields(luna, LUNA_FIELDS, "luna", errors) and luna != expected_luna:
                add_error(errors, "luna must exactly match the luna-max visible-thread route")
        else:
            add_error(
                errors,
                "execute mode request_authority must be ordinary_browser_generation "
                "or explicit_visible_task",
            )

    return {
        "valid": not errors,
        "errors": errors,
        "provider_calls": False,
        "secrets_read": False,
        "envelope": envelope,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("envelope_file", type=Path)
    parser.add_argument("--format", choices=("json", "text"), default="json")
    args = parser.parse_args()

    try:
        envelope = json.loads(args.envelope_file.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        result = {
            "valid": False,
            "errors": [f"cannot read envelope: {exc}"],
            "provider_calls": False,
            "secrets_read": False,
        }
    else:
        result = validate_envelope(envelope)

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print("VALID" if result["valid"] else "INVALID")
        for error in result["errors"]:
            print(f"- {error}")
    return 0 if result["valid"] else 2


if __name__ == "__main__":
    raise SystemExit(main())
