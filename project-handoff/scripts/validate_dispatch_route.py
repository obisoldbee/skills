#!/usr/bin/env python3
"""Fail closed on project-handoff route, surface, follow-up, and retry drift."""

import argparse
import json
from pathlib import Path
import sys


ROUTE_BASES = {"explicit_user", "auto_requested", "auto_unspecified"}
SURFACES = {"visible_thread", "bundled_cli", "portable_handoff"}
OPERATIONS = {"initial_dispatch", "followup", "sync_retry", "failure_report"}
FILE_ACCESS_MODES = {"read_only", "write"}
ROUTE_FIELDS = {
    "requested_route",
    "model",
    "reasoning",
    "surface",
    "model_basis",
    "reasoning_basis",
}
ATTEMPT_FIELDS = {
    "operation",
    "action",
    "tool",
    "failure_class",
    "route_changed",
    "explicit_user_route_change",
    "route",
    "prior_file_access",
    "requested_file_access",
    "plan_guard_valid",
    "environment_guard_valid",
}
ACTIONS = {
    "create_visible_task",
    "run_bundled_spark_cli",
    "read_existing_task",
    "set_visible_task_title",
    "send_followup",
    "produce_portable_handoff",
    "none",
}
ACTION_TOOL_LEAVES = {
    "create_visible_task": {"create_thread"},
    "run_bundled_spark_cli": {"run-spark-cli.sh"},
    "read_existing_task": {"read_thread"},
    "set_visible_task_title": {"set_thread_title"},
    "send_followup": {"send_message_to_thread"},
    "produce_portable_handoff": {"none"},
    "none": {"none"},
}
FORBIDDEN_TOOL_MARKERS = ("spawn_agent", "subagent", "collaboration")
SYNC_RETRY_ACTIONS = {"read_existing_task", "set_visible_task_title"}
SYNC_FAILURES = {"creation_visibility_delay", "prompt_readback_delay", "title_metadata_delay"}
FAILURE_CLASSES = {
    "none",
    *SYNC_FAILURES,
    "unsupported_parameter",
    "invalid_request",
    "unsupported_route",
    "wrapper_missing",
    "codex_cli_missing",
    "auth",
    "permission",
    "quota",
    "provider_model",
    "unknown",
}

SPARK_MODEL = "gpt-5.3-codex-spark"
SPARK_ROUTE = (SPARK_MODEL, "xhigh", "bundled_cli")
ALIASES = {
    "sol-ultra": ("gpt-5.6-sol", "ultra", "visible_thread"),
    "sol-max": ("gpt-5.6-sol", "max", "visible_thread"),
    "terra-max": ("gpt-5.6-terra", "max", "visible_thread"),
    "luna-max": ("gpt-5.6-luna", "max", "visible_thread"),
    "spark": SPARK_ROUTE,
    "spark-xhigh": SPARK_ROUTE,
    "portable-handoff": ("none", "none", "portable_handoff"),
}


def add_error(errors, message):
    if message not in errors:
        errors.append(message)


def required_string(value, field, errors):
    if not isinstance(value, str) or not value.strip():
        add_error(errors, f"{field} must be a non-empty string")
        return ""
    return value.strip()


def required_bool(value, field, errors):
    if not isinstance(value, bool):
        add_error(errors, f"{field} must be a boolean")
        return False
    return value


def tool_leaf(tool):
    """Return a stable leaf for namespaced app tools or script paths."""
    leaf = tool.replace("\\", "/").rsplit("/", 1)[-1]
    if "__" in leaf:
        return leaf.rsplit("__", 1)[-1]
    if leaf in {"run-spark-cli.sh", "none"}:
        return leaf
    return leaf.rsplit(".", 1)[-1]


def validate_tool(action, tool, errors):
    lowered = tool.lower()
    if any(marker in lowered for marker in FORBIDDEN_TOOL_MARKERS):
        add_error(
            errors,
            "tool must not use spawn_agent, collaboration, or subagent surfaces",
        )
        return

    allowed = ACTION_TOOL_LEAVES.get(action)
    if allowed and tool_leaf(tool) not in allowed:
        add_error(
            errors,
            f"action={action} requires tool leaf in: {', '.join(sorted(allowed))}",
        )


def validate_route(route, field="route"):
    """Validate a route receipt and return its normalized fields plus errors."""
    errors = []
    if not isinstance(route, dict):
        return {}, [f"{field} must be an object"]

    unknown_fields = sorted(set(route) - ROUTE_FIELDS)
    if unknown_fields:
        add_error(
            errors,
            f"{field} contains unsupported fields: {', '.join(unknown_fields)}",
        )

    requested_route = required_string(
        route.get("requested_route"), f"{field}.requested_route", errors
    ).lower()
    model = required_string(route.get("model"), f"{field}.model", errors)
    reasoning = required_string(route.get("reasoning"), f"{field}.reasoning", errors)
    surface = required_string(route.get("surface"), f"{field}.surface", errors)

    result = {
        "requested_route": requested_route,
        "model": model,
        "reasoning": reasoning,
        "surface": surface,
    }

    if surface and surface not in SURFACES:
        add_error(errors, f"{field}.surface must be one of: {', '.join(sorted(SURFACES))}")

    for key in ("model_basis", "reasoning_basis"):
        value = route.get(key)
        if value not in ROUTE_BASES:
            add_error(
                errors,
                f"{field}.{key} must be one of: {', '.join(sorted(ROUTE_BASES))}",
            )
        else:
            result[key] = value

    expected = ALIASES.get(requested_route)
    actual = (model, reasoning, surface)
    if expected and actual != expected:
        add_error(
            errors,
            f"{field} alias {requested_route} requires model={expected[0]}, "
            f"reasoning={expected[1]}, surface={expected[2]}",
        )

    if model == SPARK_MODEL and actual != SPARK_ROUTE:
        add_error(
            errors,
            f"{field} Spark model requires reasoning=xhigh and surface=bundled_cli",
        )
    if surface == "bundled_cli" and model != SPARK_MODEL:
        add_error(errors, f"{field} bundled_cli is reserved for {SPARK_MODEL}")
    if surface == "portable_handoff" and actual != ("none", "none", "portable_handoff"):
        add_error(
            errors,
            f"{field} portable_handoff requires model=none and reasoning=none",
        )

    return result, errors


def failure_disposition(failure_class, route, route_errors):
    if failure_class in SYNC_FAILURES:
        classification = "synchronization_delay"
    elif failure_class in {"unsupported_parameter", "invalid_request"}:
        classification = "wrong_surface_or_request"
    elif failure_class in {"wrapper_missing", "codex_cli_missing"}:
        classification = "executor_unavailable"
    elif failure_class in {"unsupported_route", "provider_model"}:
        classification = "runtime_route_unavailable"
    elif failure_class in {"auth", "permission", "quota"}:
        classification = "runtime_access_blocked"
    elif failure_class == "none":
        classification = "none"
    else:
        classification = "unknown"

    spark_lane = (
        route.get("requested_route") in {"spark", "spark-xhigh"}
        or route.get("model") == SPARK_MODEL
    )
    portable_lane = route.get("surface") == "portable_handoff"
    spark_unavailable_supported = (
        not route_errors
        and route.get("model") == SPARK_MODEL
        and route.get("surface") == "bundled_cli"
        and failure_class in {"unsupported_route", "provider_model"}
    )

    if spark_lane and failure_class != "none":
        next_action = "stop_spark_lane"
    elif spark_lane and route_errors:
        next_action = "correct_to_bundled_cli_before_execution"
    elif spark_lane:
        next_action = "run_bundled_spark_cli"
    elif portable_lane and failure_class == "none":
        next_action = "produce_portable_handoff"
    elif portable_lane:
        next_action = "stop_or_rebuild_portable_handoff"
    elif failure_class in SYNC_FAILURES:
        next_action = "retry_existing_task_metadata"
    elif failure_class == "none":
        next_action = "proceed"
    else:
        next_action = "stop_or_follow_declared_worker_failure_policy"

    return {
        "classification": classification,
        "terminal": spark_lane and failure_class != "none",
        "next_action": next_action,
        "visible_task_allowed": not spark_lane and not portable_lane,
        "portable_handoff_allowed": portable_lane,
        "same_lane_retry_allowed": failure_class in SYNC_FAILURES and not spark_lane,
        "automatic_fallback_allowed": False,
        "route_change_requires_new_user_request": (
            spark_lane and failure_class != "none"
        ),
        "sync_retry_allowed": failure_class in SYNC_FAILURES and not spark_lane,
        "spark_unavailable_supported": spark_unavailable_supported,
    }


def validate_attempt(attempt):
    errors = []
    if not isinstance(attempt, dict):
        return {
            "valid": False,
            "errors": ["attempt root must be an object"],
            "route": {},
            "failure_disposition": failure_disposition("unknown", {}, ["invalid"]),
        }

    unknown_fields = sorted(set(attempt) - ATTEMPT_FIELDS)
    if unknown_fields:
        add_error(errors, "attempt contains unsupported fields: " + ", ".join(unknown_fields))

    operation = required_string(attempt.get("operation"), "operation", errors)
    action = required_string(attempt.get("action"), "action", errors)
    tool = required_string(attempt.get("tool"), "tool", errors)
    failure_class = required_string(
        attempt.get("failure_class"), "failure_class", errors
    )
    route_changed = required_bool(attempt.get("route_changed"), "route_changed", errors)
    explicit_user_route_change = required_bool(
        attempt.get("explicit_user_route_change"),
        "explicit_user_route_change",
        errors,
    )

    if operation and operation not in OPERATIONS:
        add_error(errors, f"operation must be one of: {', '.join(sorted(OPERATIONS))}")
    if action and action not in ACTIONS:
        add_error(errors, f"action must be one of: {', '.join(sorted(ACTIONS))}")
    if action in ACTIONS and tool:
        validate_tool(action, tool, errors)
    if failure_class and failure_class not in FAILURE_CLASSES:
        add_error(
            errors,
            f"failure_class must be one of: {', '.join(sorted(FAILURE_CLASSES))}",
        )

    route, route_errors = validate_route(attempt.get("route"))
    for error in route_errors:
        add_error(errors, error)

    if route_changed and not explicit_user_route_change:
        add_error(errors, "route_changed requires an explicit user route change")
    if operation != "followup" and any(
        field in attempt
        for field in (
            "prior_file_access",
            "requested_file_access",
            "plan_guard_valid",
            "environment_guard_valid",
        )
    ):
        add_error(errors, "execution transition fields are allowed only for followup")

    if operation == "initial_dispatch":
        if failure_class != "none":
            add_error(errors, "initial_dispatch requires failure_class=none")
        if route_changed:
            add_error(errors, "initial_dispatch cannot be a route-changing retry")
        expected_action = {
            "bundled_cli": "run_bundled_spark_cli",
            "portable_handoff": "produce_portable_handoff",
        }.get(route.get("surface"), "create_visible_task")
        if action != expected_action:
            add_error(
                errors,
                f"initial_dispatch on {route.get('surface') or 'unknown surface'} "
                f"requires action={expected_action}",
            )

    elif operation == "followup":
        if action != "send_followup":
            add_error(errors, "followup requires action=send_followup")
        if failure_class != "none":
            add_error(errors, "followup requires failure_class=none")
        if route.get("surface") != "visible_thread":
            add_error(errors, "followup is available only for a visible_thread route")
        prior_file_access = required_string(
            attempt.get("prior_file_access"), "prior_file_access", errors
        )
        requested_file_access = required_string(
            attempt.get("requested_file_access"), "requested_file_access", errors
        )
        if prior_file_access and prior_file_access not in FILE_ACCESS_MODES:
            add_error(errors, "prior_file_access must be read_only or write")
        if requested_file_access and requested_file_access not in FILE_ACCESS_MODES:
            add_error(errors, "requested_file_access must be read_only or write")
        plan_guard_valid = required_bool(
            attempt.get("plan_guard_valid"), "plan_guard_valid", errors
        )
        environment_guard_valid = required_bool(
            attempt.get("environment_guard_valid"),
            "environment_guard_valid",
            errors,
        )
        if not plan_guard_valid:
            add_error(errors, "followup requires a validated current lane plan")
        if requested_file_access == "write" and not environment_guard_valid:
            add_error(errors, "write followup requires a validated current environment")
        if prior_file_access == "read_only" and requested_file_access == "write":
            if not plan_guard_valid or not environment_guard_valid:
                add_error(
                    errors,
                    "read_only-to-write followup requires replanned scope and environment",
                )

    elif operation == "sync_retry":
        if action not in SYNC_RETRY_ACTIONS:
            add_error(
                errors,
                "sync_retry may only read an existing task or retry title metadata; "
                "it must not create a replacement task",
            )
        if failure_class not in SYNC_FAILURES:
            add_error(errors, "sync_retry requires an eligible synchronization failure")
        if route.get("surface") != "visible_thread":
            add_error(errors, "sync_retry is available only for an existing visible_thread")
        if route_changed:
            add_error(errors, "sync_retry must preserve the original route")

    elif operation == "failure_report":
        if action != "none":
            add_error(errors, "failure_report requires action=none")
        if failure_class == "none":
            add_error(errors, "failure_report requires a non-none failure_class")
        if route_changed:
            add_error(errors, "failure_report cannot change the attempted route")

    disposition = failure_disposition(failure_class, route, route_errors)
    return {
        "valid": not errors,
        "errors": errors,
        "route": route,
        "operation": operation,
        "action": action,
        "tool": tool,
        "failure_class": failure_class,
        "failure_disposition": disposition,
    }


def main():
    parser = argparse.ArgumentParser(
        description="Validate a project-handoff dispatch, follow-up, retry, or failure receipt."
    )
    parser.add_argument("attempt_file", help="JSON attempt path.")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()

    try:
        attempt = json.loads(Path(args.attempt_file).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        result = {
            "valid": False,
            "errors": [f"cannot read attempt: {exc}"],
            "route": {},
            "failure_disposition": failure_disposition("unknown", {}, ["invalid"]),
        }
    else:
        result = validate_attempt(attempt)

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print("VALID" if result["valid"] else "INVALID")
        for error in result["errors"]:
            print(f"- {error}")
        disposition = result["failure_disposition"]
        print(f"classification: {disposition['classification']}")
        print(
            "spark_unavailable_supported: "
            + str(disposition["spark_unavailable_supported"]).lower()
        )
        print(f"next_action: {disposition['next_action']}")
        print(f"terminal: {str(disposition['terminal']).lower()}")
        print(
            "visible_task_allowed: "
            + str(disposition["visible_task_allowed"]).lower()
        )
    return 0 if result["valid"] else 2


if __name__ == "__main__":
    sys.exit(main())
