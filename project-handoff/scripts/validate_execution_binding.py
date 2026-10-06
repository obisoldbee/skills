#!/usr/bin/env python3
"""Check retained route choices against actual execution metadata, offline."""

import argparse
import json
from pathlib import Path
import sys


BASES = {"explicit_user", "explicit_skill_route", "explicit_auto", "platform_default"}
SURFACES = {"visible_thread", "internal_agent", "current_turn"}
METADATA_SOURCES = {"runtime_metadata", "session_settings", "execution_readback"}


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def validate_binding(selection, actual, previous=None):
    errors = []
    if not isinstance(selection, dict) or not isinstance(actual, dict):
        return {"valid": False, "execution_verified": False,
                "errors": ["selection and actual must be objects"],
                "authority_verified": False, "runtime_verified_by_helper": False}
    if not nonempty(selection.get("scope_id")) or not nonempty(selection.get("selection_ref")):
        errors.append("selection needs the applicable scope_id and original selection_ref")
    selected = {}
    for axis in ("model", "reasoning"):
        basis = selection.get(axis + "_basis", "platform_default")
        value = selection.get(axis)
        if basis not in BASES:
            errors.append("invalid " + axis + "_basis")
        elif basis == "platform_default":
            if value is not None:
                errors.append("silent_default_override: " + axis)
        elif not nonempty(value):
            errors.append("selected " + axis + " needs a value")
        else:
            selected[axis] = value
    surface = selection.get("surface")
    if surface is not None:
        if surface not in SURFACES:
            errors.append("invalid selected surface")
        else:
            selected["surface"] = surface
    if previous is not None:
        if not isinstance(previous, dict) or previous.get("scope_id") != selection.get("scope_id"):
            errors.append("previous selection must belong to this same applicable scope")
        else:
            change = selection.get("user_route_change") or {}
            changed = (isinstance(change, dict) and change.get("author_is_human") is True
                       and nonempty(change.get("user_instruction_ref"))
                       and isinstance(change.get("axes"), list))
            for axis in ("model", "reasoning", "surface"):
                prior = previous.get(axis)
                prior_selected = (prior is not None and (axis == "surface"
                                  or previous.get(axis + "_basis") != "platform_default"))
                if prior_selected and selection.get(axis) != prior:
                    if not changed or axis not in change["axes"]:
                        errors.append("selection_lost_or_changed: " + axis)
    if actual.get("scope_id") != selection.get("scope_id"):
        errors.append("actual metadata belongs to a different scope")
    if (actual.get("metadata_source") not in METADATA_SOURCES
            or not nonempty(actual.get("evidence_ref"))
            or not nonempty(actual.get("execution_id"))):
        errors.append("actual runtime/session/readback evidence is required; prompts and requested arguments are insufficient")
    if actual.get("surface") not in SURFACES:
        errors.append("actual surface is missing or unsupported")
    for axis, expected in selected.items():
        if actual.get(axis) != expected:
            errors.append("actual_" + axis + "_mismatch")
    tool = actual.get("actual_tool")
    if not nonempty(tool):
        errors.append("actual_tool is required")
    elif actual.get("surface") == "visible_thread" and any(
            marker in tool.lower() for marker in ("spawn_agent", "collaboration", "subagent")):
        errors.append("hidden tool cannot prove visible execution")
    if actual.get("surface") == "visible_thread" and (
            str(actual.get("execution_id", "")).startswith("/root/")
            or any(actual.get(key) not in (None, "") for key in ("agentPath", "agentThreadId", "agent_path", "agent_thread_id", "subAgentActivity"))):
        errors.append("hidden agent identity cannot prove visible execution")
    return {"valid": not errors, "execution_verified": not errors,
            "selected_axes": selected, "errors": errors,
            "authority_verified": False, "runtime_verified_by_helper": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("selection", type=Path)
    parser.add_argument("--actual", required=True, type=Path)
    parser.add_argument("--previous", type=Path, help="original applicable choices retained before simplification")
    args = parser.parse_args()
    try:
        report = validate_binding(json.loads(args.selection.read_text(encoding="utf-8")),
                                  json.loads(args.actual.read_text(encoding="utf-8")),
                                  json.loads(args.previous.read_text(encoding="utf-8")) if args.previous else None)
    except (ValueError, OSError) as exc:
        report = {"valid": False, "execution_verified": False, "errors": [str(exc)],
                  "authority_verified": False, "runtime_verified_by_helper": False}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["valid"] else 2


if __name__ == "__main__":
    sys.exit(main())
