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
SURFACES = {"visible_thread"}
OPERATIONS = {"initial_dispatch", "followup", "sync_retry", "failure_report"}
ACTIONS = {
    "create_visible_task",
    "read_existing_task",
    "set_visible_task_title",
    "send_followup",
    "none",
}
ACTION_TOOL_LEAVES = {
    "create_visible_task": {"create_thread"},
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
    "auth",
    "permission",
    "quota",
    "provider_model",
    "unknown",
}

ASTRA_MODEL = "gpt-6-astra"
SOL_MODEL = "gpt-6.1-sol"
LUNA_MODEL = "gpt-6-luna"
MODEL_NAMES = {"astra": ASTRA_MODEL, "gpt6": ASTRA_MODEL, "sol": SOL_MODEL, "luna": LUNA_MODEL}
ROLE_ROUTES = {
    "top_difficulty": ("astra", "ultra"),
    "orchestration": ("astra", "high"),
    "writing": ("sol", "max"),
    "astra_planned_execution": ("sol", "max"),
    "computer_operation": ("sol", "medium"),
    "mechanical": ("luna", "max"),
    "browser_operation": ("luna", "max"),
}
FAMILY_BASELINES = {"astra": ASTRA_MODEL, "sol": SOL_MODEL, "luna": LUNA_MODEL}
AUTO_MODELS = {ASTRA_MODEL, SOL_MODEL, LUNA_MODEL}
# Tombstones prevent old prompts from reviving a removed executor. No fallback.
RETIRED_ROUTES = {"spark", "spark-xhigh", "gpt-5.3-codex-spark"}
KNOWN_EFFORTS = {
    ASTRA_MODEL: {"low", "medium", "high", "xhigh", "max", "ultra"},
    SOL_MODEL: {"low", "medium", "high", "xhigh", "max", "ultra"},
    LUNA_MODEL: {"low", "medium", "high", "xhigh", "max"},
    "gpt-6-sol": {"low", "medium", "high", "xhigh", "max", "ultra"},
}
ALIASES = {
    "astra-high": (ASTRA_MODEL, "high", "visible_thread"),
    "sol-medium": (SOL_MODEL, "medium", "visible_thread"),
    "astra-ultra": (ASTRA_MODEL, "ultra", "visible_thread"),
    "gpt6-ultra": (ASTRA_MODEL, "ultra", "visible_thread"),
    "astra-max": (ASTRA_MODEL, "max", "visible_thread"),
    "gpt6-max": (ASTRA_MODEL, "max", "visible_thread"),
    "sol-ultra": (SOL_MODEL, "ultra", "visible_thread"),
    "sol-max": (SOL_MODEL, "max", "visible_thread"),
    "terra-max": ("gpt-5.6-terra", "max", "visible_thread"),
    "luna-max": (LUNA_MODEL, "max", "visible_thread"),
}
LEGACY_ALIASES = {
    "sol-ultra": ("gpt-5.6-sol", "ultra", "visible_thread"),
    "sol-max": ("gpt-5.6-sol", "max", "visible_thread"),
    "luna-max": ("gpt-5.6-luna", "max", "visible_thread"),
}
LEGACY_AUTO_MODELS = {"gpt-5.6-sol", "gpt-5.6-terra", "gpt-5.6-luna", "gpt-6-sol"}
MISSING = object()
REASONING_TIERS = ("low", "medium", "high", "xhigh", "max", "ultra")


def family_version(model, family):
    """Only numbered family releases; preview/custom/date suffixes are not ordered."""
    match = re.fullmatch(r"gpt-(\d+(?:\.\d+)*)-" + re.escape(family), model)
    if not match:
        return None
    parts = [int(p) for p in match.group(1).split('.')]
    while len(parts) > 1 and parts[-1] == 0:
        parts.pop()
    return tuple(parts)


def catalog_rows(catalog):
    if not isinstance(catalog, dict) or any(
        not isinstance(catalog.get(k), str) or not catalog[k].strip()
        for k in ('source', 'host_id', 'observed_at')
    ) or not isinstance(catalog.get('models'), list):
        raise ValueError('invalid_model_catalog: source, host_id, observed_at and models required')
    ids = set()
    for row in catalog['models']:
        if (not isinstance(row, dict) or not isinstance(row.get('model'), str)
            or type(row.get('hidden')) is not bool
            or not isinstance(row.get('reasoning_efforts'), list)
            or not row['reasoning_efforts']
            or any(not isinstance(x, str) or not x for x in row['reasoning_efforts'])):
            raise ValueError('invalid_model_catalog: malformed model entry')
        if row['model'] in ids:
            raise ValueError('invalid_model_catalog: duplicate model ID')
        ids.add(row['model'])
    return catalog['models']


def resolve_family(family, catalog=None):
    """Resolve a declared destination snapshot, not a live availability claim."""
    baseline = FAMILY_BASELINES[family]
    if catalog is None:
        return baseline
    candidates = []
    for row in catalog_rows(catalog):
        version = family_version(row['model'], family)
        if version is not None and not row['hidden']:
            candidates.append((version, row['model']))
    if not candidates:
        raise ValueError('model_catalog_unavailable: no visible ' + family)
    version, selected = max(candidates)
    if version < family_version(baseline, family):
        raise ValueError('model_catalog_stale: refresh destination; do not silently downgrade')
    if sum(v == version for v, _ in candidates) > 1:
        raise ValueError('invalid_model_catalog: ambiguous equal version')
    return selected


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
    if leaf == "none":
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


def validate_route(route, field="route", allow_legacy_continuation=False):
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
    if requested_route in RETIRED_ROUTES or model in RETIRED_ROUTES:
        add_error(errors, "retired_route: Spark execution has been removed; request a supported route explicitly")

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
    catalog = route.get('model_catalog')
    kind = route.get('task_kind')
    if kind is not None and (not isinstance(kind, str) or kind not in ROLE_ROUTES):
        add_error(errors, 'unknown task_kind')
        kind = None
    if kind in ROLE_ROUTES:
        result['task_kind'] = kind
    if catalog is not None:
        result['model_catalog'] = catalog
        try:
            catalog_rows(catalog)
        except ValueError as exc:
            add_error(errors, str(exc))
    if model_basis == 'explicit_auto' and kind is None and not allow_legacy_continuation:
        add_error(errors, 'automatic_role_required: record task_kind from verified scope')

    def family_model(family):
        try:
            return resolve_family(family, catalog)
        except ValueError as exc:
            add_error(errors, str(exc))
            return FAMILY_BASELINES[family]

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
                expected_value = (
                    MODEL_NAMES.get(requested.lower(), requested)
                    if axis == "model" else requested
                )
                if axis == 'model' and requested.lower() in FAMILY_BASELINES:
                    family = requested.lower()
                    expected_value = (value if allow_legacy_continuation and
                                      family_version(value or '', family) else family_model(family))
                if value != expected_value:
                    add_error(
                        errors,
                        f"axis_authority_mismatch: {field}.{axis} must equal "
                        f"{field}.{requested_field} (or its documented model name)",
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
    alias_family = requested_route.split('-')[0]
    if expected and alias_family in FAMILY_BASELINES:
        selected = (model if allow_legacy_continuation and family_version(model or '', alias_family)
                    else family_model(alias_family))
        expected = (selected, expected[1], expected[2])
    if allow_legacy_continuation and actual == LEGACY_ALIASES.get(requested_route):
        expected = actual
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

    retired_continuation = allow_legacy_continuation and model in LEGACY_AUTO_MODELS
    recommended = ROLE_ROUTES.get(kind)
    auto_effort = recommended[1] if recommended else 'max'
    if reasoning_basis == "explicit_auto" and reasoning != auto_effort and not allow_legacy_continuation:
        add_error(errors, f"automatic_reasoning_not_allowed: expected {auto_effort} for declared role")
    if model in KNOWN_EFFORTS and reasoning is not None and reasoning not in KNOWN_EFFORTS[model]:
        add_error(errors, f"unsupported_reasoning: {model} does not support {reasoning}; verify the destination capability")
    # Optional observed destination state checks inherited defaults too, without
    # turning them into explicit overrides in the emitted tool arguments.
    destination = route.get("destination_state")
    if destination is not None:
        if not isinstance(destination, dict):
            add_error(errors, f"{field}.destination_state must be an object")
        else:
            observed = {}
            for axis in ("model", "reasoning"):
                value = destination.get(axis)
                if value is not None and (not isinstance(value, str) or not value.strip()):
                    add_error(errors, f"{field}.destination_state.{axis} must be a nonempty string")
                else:
                    observed[axis] = value
            effective_model = model or observed.get("model")
            effective_reasoning = reasoning or observed.get("reasoning")
            if effective_model in KNOWN_EFFORTS and effective_reasoning is not None and effective_reasoning not in KNOWN_EFFORTS[effective_model]:
                add_error(errors, "unsupported_inherited_reasoning: destination effort must be repaired before sending")
            supported = destination.get("supported_reasoning")
            if supported is not None:
                if not isinstance(supported, list) or not supported or any(not isinstance(x, str) for x in supported):
                    add_error(errors, "destination_state.supported_reasoning must be a nonempty string list")
                elif destination.get("model") == effective_model and effective_reasoning is not None and effective_reasoning not in supported:
                    add_error(errors, "unsupported_reasoning: effective effort is absent from the destination capability evidence")
    auto_models = AUTO_MODELS
    if recommended and model_basis == 'explicit_auto':
        if allow_legacy_continuation and family_version(model or '', recommended[0]):
            auto_models = {model}
        else:
            auto_models = {family_model(recommended[0])}
    elif catalog is not None and model_basis == 'explicit_auto':
        family = next((f for f in FAMILY_BASELINES if family_version(model or '', f)), None)
        auto_models = {family_model(family)} if family else set()
    if model_basis == "explicit_auto" and model not in auto_models and not retired_continuation:
        add_error(
            errors,
            f"automatic_model_not_allowed: {field}.model must be one of: "
            + ", ".join(sorted(auto_models)),
        )
    if catalog is not None and not errors and model is not None and reasoning is not None:
        entries = catalog.get('models', []) if isinstance(catalog, dict) else []
        row = next((r for r in entries if isinstance(r, dict) and r.get('model') == model), None)
        if row is None or reasoning not in row.get('reasoning_efforts', []):
            add_error(errors, 'unsupported_reasoning: pair absent from destination model_catalog')

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

    alias_names = "(" + "|".join(
        re.escape(alias) for alias in sorted(set(ALIASES) | RETIRED_ROUTES, key=len, reverse=True)
    ) + ")"
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
        if re.search(
            r"模型用|推理(?:档位)?用|模型自动|推理(?:档位)?自动|模型和推理都自动选",
            lowered,
        ):
            raise ValueError("alias plus separate axis selection requires a resolved route")
        alias = alias_match.group(1)
        if alias in RETIRED_ROUTES:
            raise ValueError("retired_route: Spark execution has been removed")
        model, reasoning, surface = ALIASES[alias]
        family = alias.split('-')[0]
        if family in FAMILY_BASELINES:
            model = resolve_family(family, context.get('model_catalog'))
        return _decision_from_route(
            {
                "requested_route": alias,
                "model": model,
                "reasoning": reasoning,
                "surface": surface,
                "model_basis": "explicit_skill_route",
                "reasoning_basis": "explicit_skill_route",
                **({'model_catalog': context['model_catalog']} if 'model_catalog' in context else {}),
            }
        )

    model_matches = list(re.finditer(
        r"模型用\s*(gpt-[a-z0-9.-]+|(?:astra|sol|luna|gpt6)(?![a-z0-9.-]))",
        lowered,
    ))
    model_name_pattern = r"(astra|sol|luna|gpt6)(?![a-z0-9.-])"
    name_match = re.search(
        r"(?:用|使用)\s*" + model_name_pattern + r"\s*(?:创建|派发|dispatch|create)",
        lowered,
    ) or re.search(
        r"(?:^|\s)use\s+" + model_name_pattern + r"(?:\s+to)?\s+(?:创建|派发|dispatch|create)",
        lowered,
    ) or re.search(
        r"^(?:\$project-handoff\s+)?" + model_name_pattern + r"\s+(?:创建|派发|dispatch|create)",
        lowered,
    )
    if name_match and all(match.span(1) != name_match.span(1) for match in model_matches):
        model_matches.append(name_match)
    reasoning_matches = list(re.finditer(
        r"推理(?:档位)?用\s*(" + "|".join(REASONING_TIERS) + r")(?![a-z0-9.-])",
        lowered,
    ))
    if len(model_matches) > 1 or len(reasoning_matches) > 1:
        raise ValueError("multiple explicit selections require a resolved axis")
    model_match = model_matches[0] if model_matches else None
    reasoning_match = reasoning_matches[0] if reasoning_matches else None

    auto_both = "模型和推理都自动选" in text
    model_auto = auto_both or bool(
        re.search(r"模型(?:用)?\s*(?:自动选?|auto)\b", lowered)
    )
    reasoning_auto = auto_both or bool(
        re.search(r"推理(?:档位)?(?:用)?\s*(?:自动选?|auto)\b", lowered)
    )
    if "模型用" in lowered and not (model_match or model_auto) and not re.search(
        r"模型用\s*平台默认", lowered
    ):
        raise ValueError("unrecognized explicit model selection")
    if re.search(r"推理(?:档位)?用", lowered) and not (reasoning_match or reasoning_auto) and not re.search(
        r"推理(?:档位)?用\s*平台默认", lowered
    ):
        raise ValueError("unrecognized explicit reasoning selection")
    if (model_match and model_auto) or (reasoning_match and reasoning_auto):
        raise ValueError("conflicting explicit and auto values require a resolved axis")
    if model_match or reasoning_match or model_auto or reasoning_auto:
        if model_auto and reasoning_auto and "先设计" in text and "验收后" in text:
            if context.get("task_kind") != "top_difficulty" and context.get("lane_difficulty") != "high":
                raise ValueError("needs_explicit_route: verify top-difficulty design before an automatic Astra/Sol pipeline")
            return {
                "surface": "visible_thread_pipeline",
                "requested_route": "auto",
                "model_basis": "explicit_auto",
                "reasoning_basis": "explicit_auto",
                "sequence": [
                    {"model": resolve_family('astra', context.get('model_catalog')), "reasoning": "ultra"},
                    {"model": resolve_family('sol', context.get('model_catalog')), "reasoning": "max"},
                ],
            }

        classified_model = None
        kind = context.get("task_kind")
        if model_auto or reasoning_auto:
            if kind == "top_difficulty" or context.get("lane_difficulty") == "high":
                kind = 'top_difficulty'
            elif kind == "mechanical" or (
                any(marker in text for marker in ("manifest", "YAML", "SHA", "找文件", "查找文件", "已有脚本"))
                and any(marker in text for marker in ("只读", "不判断", "无需判断"))
            ):
                kind = 'mechanical'
            elif kind == "astra_planned_execution" or (
                context.get("plan_owner") == "astra"
                and any(marker in text for marker in ("已批准", "已验收", "已编排"))
            ):
                kind = 'astra_planned_execution'
            elif kind not in ROLE_ROUTES and model_auto:
                raise ValueError("needs_explicit_route: establish role and scope before automatic model selection")
            if kind in ROLE_ROUTES and model_auto:
                classified_model = resolve_family(ROLE_ROUTES[kind][0], context.get('model_catalog'))

        requested_model = model_match.group(1) if model_match else None
        model = (
            MODEL_NAMES.get(requested_model, requested_model)
            if model_match else classified_model if model_auto else None
        )
        if requested_model in FAMILY_BASELINES:
            model = resolve_family(requested_model, context.get('model_catalog'))
        reasoning = (
            reasoning_match.group(1) if reasoning_match
            else ROLE_ROUTES.get(kind, (None, 'max'))[1] if reasoning_auto
            else None
        )
        surface = "visible_thread"
        route = {
            "requested_route": "auto" if model_auto or reasoning_auto
            else requested_model if model_match else "reasoning-only",
            "model": model,
            "reasoning": reasoning,
            "surface": surface,
            "model_basis": "explicit_user" if model_match else "explicit_auto" if model_auto else "platform_default",
            "reasoning_basis": "explicit_user" if reasoning_match else "explicit_auto" if reasoning_auto else "platform_default",
        }
        if model_match:
            route["requested_model"] = requested_model
        if reasoning_match:
            route["requested_reasoning"] = reasoning_match.group(1)
        if kind in ROLE_ROUTES:
            route['task_kind'] = kind
        if 'model_catalog' in context:
            route['model_catalog'] = context['model_catalog']

        return _decision_from_route(route)

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
    elif failure_class in {"unsupported_route", "provider_model"}:
        classification = "runtime_route_unavailable"
    elif failure_class in {"auth", "permission", "quota"}:
        classification = "runtime_access_blocked"
    elif failure_class == "none":
        classification = "none"
    else:
        classification = "unknown"

    if route_errors:
        next_action = "correct_invalid_attempt"
    elif failure_class in SYNC_FAILURES:
        next_action = "retry_existing_task_metadata"
    elif failure_class in {"unsupported_parameter", "invalid_request"}:
        next_action = "inspect_model_effort_capabilities"
    elif failure_class == "none":
        next_action = "proceed"
    else:
        next_action = "stop_or_follow_declared_worker_failure_policy"

    return {
        "classification": classification,
        "terminal": failure_class != "none" and failure_class not in SYNC_FAILURES,
        "next_action": next_action,
        "visible_task_allowed": not route_errors,
        "same_lane_retry_allowed": failure_class in SYNC_FAILURES and not route_errors,
        "automatic_fallback_allowed": False,
        "route_change_requires_new_user_request": failure_class != "none",
        "sync_retry_allowed": failure_class in SYNC_FAILURES and not route_errors,
        "model_unavailable_supported": not route_errors and failure_class in {"unsupported_route", "provider_model"},
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

    route, route_errors = validate_route(
        attempt.get("route"),
        allow_legacy_continuation=(
            operation in {"followup", "sync_retry", "failure_report"}
            and not route_changed
        ),
    )
    for error in route_errors:
        add_error(errors, error)

    if route_changed and not explicit_user_route_change:
        add_error(errors, "route_changed requires an explicit user route change")

    if operation == "initial_dispatch":
        if failure_class != "none":
            add_error(errors, "initial_dispatch requires failure_class=none")
        if route_changed:
            add_error(errors, "initial_dispatch cannot be a route-changing retry")
        expected_action = "create_visible_task"
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
            "model_unavailable_supported: "
            + str(disposition["model_unavailable_supported"]).lower()
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
