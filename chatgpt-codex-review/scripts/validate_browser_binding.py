#!/usr/bin/env python3
"""Check the selected browser driver and owned target before UI actions."""

import argparse
import json
from pathlib import Path
import sys


def nonempty(value):
    return isinstance(value, str) and bool(value.strip())


def tool_leaf(value):
    return value.rsplit("__", 1)[-1].rsplit(".", 1)[-1] if isinstance(value, str) else None


def tool_identity(value):
    if not isinstance(value, str):
        return None
    for prefix in ("tools.", "functions."):
        if value.startswith(prefix):
            return value[len(prefix):]
    return value


def validate_binding(binding, actual, recovery=None):
    errors = []
    if not isinstance(binding, dict) or not isinstance(actual, dict):
        return {"valid": False, "next_action": "reload_browser_binding",
                "errors": ["reload the selected runtime, documented control entry and owned target from current evidence"],
                "runtime_verified_by_helper": False, "authority_verified": False}
    keys = ("runtime", "control_entry", "execution_host", "target_id", "page_id", "evidence_ref")
    for label, record in (("binding", binding), ("actual", actual)):
        if any(not nonempty(record.get(key)) for key in keys):
            errors.append(label + " needs runtime, control entry, host, owned target/page and evidence")
    if not nonempty(binding.get("control_tool")):
        errors.append("selected control_tool must come from the documented runtime entry")
    if not nonempty(actual.get("actual_tool")) or not nonempty(actual.get("call_evidence_ref")):
        errors.append("actual call/tool evidence is required; a typed driver label is insufficient")
    elif tool_identity(actual["actual_tool"]) != tool_identity(binding.get("control_tool")):
        errors.append("actual_driver_mismatch: actual_tool")
    ego_cli = (binding.get("runtime") == "ego-browser"
               and any(marker in str(binding.get("control_entry", "")).lower() for marker in ("nodejs", "taskspace/page")))
    if ego_cli and tool_leaf(actual.get("actual_tool")) not in {"exec_command", "write_stdin"}:
        errors.append("selected Ego TaskSpace/Page CLI cannot be executed by generic CUA/native app tools")
    for key in ("runtime", "control_entry", "execution_host"):
        if actual.get(key) != binding.get(key):
            errors.append("actual_driver_mismatch: " + key)
    if actual.get("ownership") != "agent":
        errors.append("current agent ownership is unverified; obey the runtime's takeover/auth/refusal gate")
    if actual.get("conversation_url") != binding.get("conversation_url"):
        errors.append("original conversation identity mismatch")
    target_changed = any(actual.get(key) != binding.get(key) for key in ("target_id", "page_id"))
    if target_changed:
        if (not isinstance(recovery, dict)
                or recovery.get("old_target_id") != binding.get("target_id")
                or recovery.get("old_page_id") != binding.get("page_id")
                or recovery.get("new_target_id") != actual.get("target_id")
                or recovery.get("new_page_id") != actual.get("page_id")
                or recovery.get("runtime_recovery_permitted") is not True
                or not nonempty(recovery.get("recovery_basis_ref"))
                or not nonempty(recovery.get("original_request_readback_ref"))):
            errors.append("changed target needs permitted recovery, old-to-new mapping and original request readback")
    return {"valid": not errors, "next_action": "use_selected_driver" if not errors else "reload_browser_binding",
            "errors": errors, "binding_update": {**binding, **actual, "control_tool": binding["control_tool"]} if not errors and target_changed else None,
            "runtime_verified_by_helper": False, "authority_verified": False}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--binding", required=True, type=Path)
    parser.add_argument("--actual", required=True, type=Path)
    parser.add_argument("--recovery", type=Path)
    args = parser.parse_args()
    try:
        report = validate_binding(json.loads(args.binding.read_text(encoding="utf-8")),
                                  json.loads(args.actual.read_text(encoding="utf-8")),
                                  json.loads(args.recovery.read_text(encoding="utf-8")) if args.recovery else None)
    except (ValueError, OSError) as exc:
        report = {"valid": False, "next_action": "reload_browser_binding", "errors": [str(exc)],
                  "runtime_verified_by_helper": False, "authority_verified": False}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if report["valid"] else 2


if __name__ == "__main__":
    sys.exit(main())
