#!/usr/bin/env python3
"""Fail closed on project-handoff route, surface, follow-up, and retry drift."""

import argparse
import hashlib
import json
from pathlib import Path
import re
import sys


ROUTE_BASES = {
    "explicit_user",
    "explicit_skill_route",
    "explicit_auto",
    "platform_default",
}
SURFACES = {"visible_thread", "bundled_cli"}
OPERATIONS = {"initial_dispatch", "followup", "sync_retry", "failure_report"}
ACTIONS = {
    "create_visible_task",
    "run_bundled_spark_cli",
    "read_existing_task",
    "set_visible_task_title",
    "send_followup",
    "none",
}
ACTION_TOOL_LEAVES = {
    "create_visible_task": {"create_thread"},
    "run_bundled_spark_cli": {"run-spark-cli.sh"},
    "read_existing_task": {"read_thread"},
    "set_visible_task_title": {"set_thread_title"},
    "send_followup": {"send_message_to_thread"},
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
}
MISSING = object()
REASONING_TIERS = ("low", "medium", "high", "xhigh", "max", "ultra")


def add_error(errors, message):
    if message not in errors:
        errors.append(message)


def required_string(value, field, errors):
    if not isinstance(value, str) or not value.strip():
        add_error(errors, f"{field} must be a non-empty string")
        return ""
    return value.strip()


def optional_route_value(value, field, errors):
    """Normalize an optional model/reasoning axis recorded in a route receipt."""
    if value is None:
        return None
    if not isinstance(value, str) or not value.strip():
        add_error(errors, f"{field} must be a non-empty string or null")
        return None
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

    requested_route = required_string(
        route.get("requested_route"), f"{field}.requested_route", errors
    ).lower()
    model = optional_route_value(route.get("model"), f"{field}.model", errors)
    reasoning = optional_route_value(
        route.get("reasoning"), f"{field}.reasoning", errors
    )
    surface = required_string(route.get("surface"), f"{field}.surface", errors)

    result = {
        "requested_route": requested_route,
        "model": model,
        "reasoning": reasoning,
        "surface": surface,
    }

    if surface and surface not in SURFACES:
        add_error(errors, f"{field}.surface must be one of: {', '.join(sorted(SURFACES))}")

    bases = {}
    for key in ("model_basis", "reasoning_basis"):
        value = route.get(key)
        if value not in ROUTE_BASES:
            add_error(
                errors,
                f"{field}.{key} must be one of: {', '.join(sorted(ROUTE_BASES))}",
            )
        else:
            result[key] = value
            bases[key] = value

    for axis, value in (("model", model), ("reasoning", reasoning)):
        basis = bases.get(f"{axis}_basis")
        if basis == "platform_default" and value is not None:
            add_error(
                errors,
                f"silent_default_override: {field}.{axis} must be null or omitted "
                "when its basis is platform_default",
            )
        elif basis in {"explicit_user", "explicit_skill_route", "explicit_auto"}:
            if value is None:
                add_error(
                    errors,
                    f"{field}.{axis} must be present when its basis is {basis}",
                )

    model_basis = bases.get("model_basis")
    reasoning_basis = bases.get("reasoning_basis")

    requested_axes = {}
    for axis, value, basis in (
        ("model", model, model_basis),
        ("reasoning", reasoning, reasoning_basis),
    ):
        requested_field = f"requested_{axis}"
        raw_requested = route.get(requested_field, MISSING)
        requested = (
            MISSING
            if raw_requested is MISSING
            else optional_route_value(raw_requested, f"{field}.{requested_field}", errors)
        )

        if basis == "explicit_user":
            if requested is MISSING or requested is None:
                add_error(
                    errors,
                    f"{field}.{requested_field} must record the explicit user value",
                )
                normalized_requested = None
            else:
                normalized_requested = requested
                if value != requested:
                    add_error(
                        errors,
                        f"axis_authority_mismatch: {field}.{axis} must equal "
                        f"{field}.{requested_field}",
                    )
        elif basis == "explicit_skill_route":
            normalized_requested = requested_route or None
            if requested is not MISSING and (
                requested is None or requested.lower() != requested_route
            ):
                add_error(
                    errors,
                    f"{field}.{requested_field} must equal alias {requested_route}",
                )
        elif basis == "explicit_auto":
            normalized_requested = "auto"
            if requested is not MISSING and (
                requested is None or requested.lower() != "auto"
            ):
                add_error(errors, f"{field}.{requested_field} must be auto")
        else:
            normalized_requested = None
            if requested is not MISSING and requested is not None:
                add_error(
                    errors,
                    f"{field}.{requested_field} must be null or omitted for platform_default",
                )

        requested_axes[axis] = {
            "basis": basis,
            "requested": normalized_requested,
            "effective": value,
        }

    result["requested_axes"] = requested_axes

    if "explicit_auto" not in {model_basis, reasoning_basis}:
        requested_model = requested_axes["model"]["requested"]
        if model_basis == "explicit_user" and (
            not requested_model or requested_route != requested_model.lower()
        ):
            add_error(
                errors,
                f"{field}.requested_route must equal the explicit requested_model",
            )
        if (
            model_basis == "platform_default"
            and reasoning_basis == "explicit_user"
            and requested_route != "reasoning-only"
        ):
            add_error(
                errors,
                f"{field}.requested_route must be reasoning-only for a raw "
                "reasoning-only request",
            )

    expected = ALIASES.get(requested_route)
    actual = (model, reasoning, surface)
    if expected and actual != expected:
        add_error(
            errors,
            f"{field} alias {requested_route} requires model={expected[0]}, "
            f"reasoning={expected[1]}, surface={expected[2]}",
        )

    if expected and (
        model_basis != "explicit_skill_route"
        or reasoning_basis != "explicit_skill_route"
    ):
        add_error(
            errors,
            f"{field} explicit alias {requested_route} requires "
            "model_basis=explicit_skill_route and "
            "reasoning_basis=explicit_skill_route",
        )

    if "explicit_skill_route" in {model_basis, reasoning_basis} and not expected:
        add_error(
            errors,
            f"{field} explicit_skill_route is valid only for a named Skill alias",
        )

    if requested_route == "platform-default":
        if surface != "visible_thread":
            add_error(errors, f"{field} platform-default requires surface=visible_thread")
        if model_basis != "platform_default" or reasoning_basis != "platform_default":
            add_error(
                errors,
                f"{field} platform-default requires both axes to use "
                "platform_default",
            )

    if (
        model_basis == "platform_default"
        and reasoning_basis == "platform_default"
        and requested_route != "platform-default"
    ):
        add_error(
            errors,
            f"{field} two platform-default axes require requested_route=platform-default",
        )

    if requested_route == "auto" and "explicit_auto" not in {
        model_basis,
        reasoning_basis,
    }:
        add_error(errors, f"{field} requested_route=auto requires an explicit_auto axis")
    if "explicit_auto" in {model_basis, reasoning_basis} and requested_route != "auto":
        add_error(
            errors,
            f"{field} explicit_auto requires requested_route=auto",
        )

    if model == SPARK_MODEL and actual != SPARK_ROUTE:
        add_error(
            errors,
            f"{field} Spark model requires reasoning=xhigh and surface=bundled_cli",
        )
    if surface == "bundled_cli" and model != SPARK_MODEL:
        add_error(errors, f"{field} bundled_cli is reserved for {SPARK_MODEL}")

    create_thread_arguments = {}
    omitted_create_thread_fields = []
    if surface == "visible_thread":
        if model_basis == "platform_default":
            omitted_create_thread_fields.append("model")
        elif model is not None:
            create_thread_arguments["model"] = model
        if reasoning_basis == "platform_default":
            omitted_create_thread_fields.append("thinking")
        elif reasoning is not None:
            create_thread_arguments["thinking"] = reasoning
    result["create_thread_arguments"] = create_thread_arguments
    result["omitted_create_thread_fields"] = omitted_create_thread_fields

    return result, errors


def dispatch_attempt_sha256(attempt):
    """Bind a post-create receipt to the exact pre-dispatch record."""
    canonical = json.dumps(
        attempt,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")
    return hashlib.sha256(canonical).hexdigest()


def _decision_from_route(route):
    normalized, errors = validate_route(route)
    if errors:
        raise ValueError("; ".join(errors))
    return normalized


def resolve_request_case(request, context=None):
    """Resolve only the documented natural-language grammar used by fixtures.

    This is not a general intent parser. An unrecognized or ambiguous fixture fails
    instead of inventing authority. Runtime callers still resolve the live request
    and verify tool capability.
    """
    if not isinstance(request, str) or not request.strip():
        raise ValueError("request must be a non-empty string")
    context = context if isinstance(context, dict) else {}
    text = request.strip()
    lowered = text.lower()

    if (
        context.get("recipient_create_thread") is False
        and context.get("recipient_cli") is False
    ):
        return {"surface": "portable_prompt_or_file", "mode": "complete_handoff"}

    alias_names = r"(sol-ultra|sol-max|terra-max|luna-max|spark(?:-xhigh)?)"
    alias_match = re.search(
        r"(?:用|使用)\s*" + alias_names + r"\s*(?:创建|派发|dispatch|create)",
        lowered,
    ) or re.search(
        r"(?:^|\s)use\s+" + alias_names + r"(?:\s+to)?\s+(?:创建|派发|dispatch|create)",
        lowered,
    ) or re.search(
        r"^(?:\$project-handoff\s+)?" + alias_names + r"\s+(?:创建|派发|dispatch|create)",
        lowered,
    )
    if alias_match:
        alias = alias_match.group(1)
        model, reasoning, surface = ALIASES[alias]
        return _decision_from_route(
            {
                "requested_route": alias,
                "model": model,
                "reasoning": reasoning,
                "surface": surface,
                "model_basis": "explicit_skill_route",
                "reasoning_basis": "explicit_skill_route",
            }
        )

    model_match = re.search(r"模型用\s*(gpt-[a-z0-9.-]+)", lowered)
    reasoning_match = re.search(
        r"推理(?:档位)?用\s*(" + "|".join(REASONING_TIERS) + r")",
        lowered,
    )
    if model_match and reasoning_match:
        model = model_match.group(1)
        reasoning = reasoning_match.group(1)
        return _decision_from_route(
            {
                "requested_route": model,
                "requested_model": model,
                "requested_reasoning": reasoning,
                "model": model,
                "reasoning": reasoning,
                "surface": "visible_thread",
                "model_basis": "explicit_user",
                "reasoning_basis": "explicit_user",
            }
        )
    if model_match and not reasoning_match:
        model = model_match.group(1)
        return _decision_from_route(
            {
                "requested_route": model,
                "requested_model": model,
                "model": model,
                "reasoning": None,
                "surface": "visible_thread",
                "model_basis": "explicit_user",
                "reasoning_basis": "platform_default",
            }
        )
    if reasoning_match and not model_match:
        reasoning = reasoning_match.group(1)
        return _decision_from_route(
            {
                "requested_route": "reasoning-only",
                "requested_reasoning": reasoning,
                "model": None,
                "reasoning": reasoning,
                "surface": "visible_thread",
                "model_basis": "platform_default",
                "reasoning_basis": "explicit_user",
            }
        )

    auto_both = "自动" in text and "模型" in text and "推理" in text
    if auto_both:
        if "先设计" in text and "验收后" in text:
            return {
                "surface": "visible_thread_pipeline",
                "requested_route": "auto",
                "model_basis": "explicit_auto",
                "reasoning_basis": "explicit_auto",
                "sequence": [
                    {"model": "gpt-5.6-sol", "reasoning": "max"},
                    {"model": "gpt-5.6-terra", "reasoning": "max"},
                ],
            }

        if (
            context.get("controller_model") == "gpt-5.6-sol"
            and context.get("controller_reasoning") == "ultra"
            and context.get("project_scale") in {"large", "super-large"}
        ):
            model, reasoning, surface = "gpt-5.6-sol", "max", "visible_thread"
        elif any(marker in text for marker in ("manifest", "YAML", "SHA")) and any(
            marker in text for marker in ("只读", "不判断")
        ):
            model, reasoning, surface = SPARK_ROUTE
        elif any(marker in text for marker in ("核验", "审核", "风险优先级")):
            model, reasoning, surface = "gpt-5.6-luna", "max", "visible_thread"
        elif any(marker in text for marker in ("设计", "架构", "迁移方案")):
            model, reasoning, surface = "gpt-5.6-sol", "max", "visible_thread"
        else:
            model, reasoning, surface = "gpt-5.6-terra", "max", "visible_thread"

        return _decision_from_route(
            {
                "requested_route": "auto",
                "model": model,
                "reasoning": reasoning,
                "surface": surface,
                "model_basis": "explicit_auto",
                "reasoning_basis": "explicit_auto",
            }
        )

    if any(marker in text for marker in ("创建一个新任务", "创建任务", "创建一个任务")):
        return _decision_from_route(
            {
                "requested_route": "platform-default",
                "model": None,
                "reasoning": None,
                "surface": "visible_thread",
                "model_basis": "platform_default",
                "reasoning_basis": "platform_default",
            }
        )

    raise ValueError("automatic routing requires an explicit auto request")


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
        "visible_task_allowed": not spark_lane,
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

    if operation == "initial_dispatch":
        if failure_class != "none":
            add_error(errors, "initial_dispatch requires failure_class=none")
        if route_changed:
            add_error(errors, "initial_dispatch cannot be a route-changing retry")
        expected_action = (
            "run_bundled_spark_cli"
            if route.get("surface") == "bundled_cli"
            else "create_visible_task"
        )
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
        "attempt_sha256": dispatch_attempt_sha256(attempt),
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
