#!/usr/bin/env python3
"""Validate an external-harness launch/environment receipt against one plan lane."""

import argparse
import json
from pathlib import Path
import re
import sys

from validate_orchestration_plan import validate_plan
from validate_visible_task_receipt import (
    add_error,
    path_is_within,
    paths_equal,
    required_bool,
    required_string,
    validate_absolute_path,
    validate_base_revision,
    validate_environment_evidence,
)


STATUSES = {"verified", "failed"}
FILE_ACCESS_MODES = {"read_only", "write"}
WORKSPACE_MODES = {"shared_checkout", "worktree", "non_git"}
EVIDENCE_SOURCES = {"external_receipt", "controller_disk_readback"}
HARNESS_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
REQUIRED_FIELDS = {
    "run_id",
    "lane_id",
    "harness",
    "status",
    "surface",
    "file_access",
    "workspace_mode",
    "worktree_source",
    "repository_root",
    "workspace_path",
    "base_revision",
    "environment_verified",
    "evidence_source",
    "environment_evidence",
    "failure",
}


def optional_string(value, field, errors):
    if value is None:
        return ""
    if not isinstance(value, str):
        add_error(errors, f"{field} must be a string or null")
        return ""
    return value.strip()


def validate_receipt(receipt, plan):
    errors = []
    if not isinstance(receipt, dict):
        return {
            "valid": False,
            "errors": ["receipt root must be an object"],
            "classification": "invalid_external_environment_evidence",
            "execution_ready": False,
            "plan_bound": False,
        }

    missing = sorted(REQUIRED_FIELDS - set(receipt))
    extra = sorted(set(receipt) - REQUIRED_FIELDS)
    if missing:
        add_error(errors, "receipt is missing fields: " + ", ".join(missing))
    if extra:
        add_error(errors, "receipt contains unsupported fields: " + ", ".join(extra))

    run_id = required_string(receipt.get("run_id"), "run_id", errors)
    lane_id = required_string(receipt.get("lane_id"), "lane_id", errors)
    harness = required_string(receipt.get("harness"), "harness", errors)
    if harness and not HARNESS_ID.fullmatch(harness):
        add_error(errors, "harness must be a lowercase identifier")
    if harness in {"codex", "codex-cli"}:
        add_error(errors, "external environment receipt requires an external harness")
    status = required_string(receipt.get("status"), "status", errors)
    if status and status not in STATUSES:
        add_error(errors, "status must be verified or failed")
    surface = required_string(receipt.get("surface"), "surface", errors)
    if surface and surface != "portable_handoff":
        add_error(errors, "surface must be portable_handoff")
    file_access = required_string(receipt.get("file_access"), "file_access", errors)
    if file_access and file_access not in FILE_ACCESS_MODES:
        add_error(errors, "file_access must be read_only or write")
    workspace_mode = required_string(
        receipt.get("workspace_mode"), "workspace_mode", errors
    )
    if workspace_mode and workspace_mode not in WORKSPACE_MODES:
        add_error(errors, "workspace_mode is invalid")

    worktree_source = validate_absolute_path(
        receipt.get("worktree_source"), "worktree_source", errors
    )
    repository_root = validate_absolute_path(
        receipt.get("repository_root"), "repository_root", errors
    )
    workspace_path = validate_absolute_path(
        receipt.get("workspace_path"), "workspace_path", errors
    )
    base_revision = validate_base_revision(
        receipt.get("base_revision"), "base_revision", errors
    )
    environment_verified = required_bool(
        receipt.get("environment_verified"), "environment_verified", errors
    )
    evidence_source = required_string(
        receipt.get("evidence_source"), "evidence_source", errors
    )
    if evidence_source and evidence_source not in EVIDENCE_SOURCES:
        add_error(errors, "evidence_source is invalid")
    failure = optional_string(receipt.get("failure"), "failure", errors)

    environment_evidence = None
    if status == "verified":
        if not environment_verified:
            add_error(errors, "status=verified requires environment_verified=true")
        if failure:
            add_error(errors, "status=verified must have null failure")
        environment_evidence = validate_environment_evidence(
            receipt.get("environment_evidence"), workspace_mode, errors
        )
        for field, outer in (
            ("worktree_source", worktree_source),
            ("repository_root", repository_root),
            ("workspace_path", workspace_path),
            ("base_revision", base_revision),
        ):
            observed = environment_evidence.get(field)
            if field.endswith("root") or field.endswith("path"):
                matches = (not observed and not outer) or paths_equal(observed, outer)
            else:
                matches = observed == outer
            if not matches:
                add_error(errors, f"environment_evidence.{field} must match receipt {field}")
    elif status == "failed":
        if environment_verified:
            add_error(errors, "status=failed requires environment_verified=false")
        if receipt.get("environment_evidence") is not None:
            add_error(errors, "status=failed must have null environment_evidence")
        if not failure:
            add_error(errors, "status=failed requires failure")

    if status == "verified":
        if workspace_mode == "worktree":
            if not worktree_source or not repository_root or not workspace_path:
                add_error(errors, "verified worktree requires source, actual root, and workspace")
            if paths_equal(worktree_source, repository_root):
                add_error(errors, "worktree repository_root must differ from worktree_source")
        elif worktree_source:
            add_error(errors, f"workspace_mode={workspace_mode} must have null worktree_source")
        if workspace_mode == "shared_checkout":
            if not repository_root or not path_is_within(repository_root, workspace_path):
                add_error(errors, "shared checkout workspace must be inside repository_root")
        elif workspace_mode == "non_git" and repository_root:
            add_error(errors, "non_git receipt must have null repository_root")

    plan_result = validate_plan(plan)
    if not plan_result["valid"]:
        for error in plan_result["errors"]:
            add_error(errors, "plan invalid: " + error)
        lane = None
    else:
        matches = [
            lane for lane in plan.get("lanes", []) if lane.get("id") == lane_id
        ]
        lane = matches[0] if len(matches) == 1 else None
        if plan.get("run_id") != run_id:
            add_error(errors, "receipt run_id must match plan run_id")
        if lane is None:
            add_error(errors, "receipt lane_id must identify exactly one plan lane")

    if lane is not None:
        route = lane.get("route") if isinstance(lane.get("route"), dict) else {}
        for field, observed in (
            ("harness", harness),
            ("file_access", file_access),
            ("workspace_mode", workspace_mode),
        ):
            if lane.get(field) != observed:
                add_error(errors, f"receipt {field} must match plan lane")
        if route.get("surface") != "portable_handoff":
            add_error(errors, "external receipt requires a portable_handoff plan lane")
        if lane_id not in plan_result.get("launch_receipt_required", []):
            add_error(errors, "plan lane does not require an external launch receipt")
        if status == "verified":
            for field, observed in (("base_revision", base_revision),):
                if lane.get(field) != observed:
                    add_error(errors, f"receipt {field} must match plan lane")
            for field, observed in (
                ("worktree_source", worktree_source),
                ("repository_root", repository_root),
                ("workspace_path", workspace_path),
            ):
                planned = lane.get(field) or ""
                if planned or observed:
                    if not paths_equal(planned, observed):
                        add_error(errors, f"receipt {field} must match plan lane")
            if lane_id in plan_result.get("environment_pending", []):
                add_error(errors, "actual external paths must be written back to plan first")
            if lane_id in plan_result.get("base_pending", []):
                add_error(errors, "external launch requires a frozen plan base_revision")
            if file_access == "write" and workspace_mode == "worktree":
                current_group = next(
                    (
                        group
                        for group in plan_result.get("ready_groups", [])
                        if lane_id in group
                    ),
                    [],
                )
                pending_peers = []
                for other in plan.get("lanes", []):
                    other_id = other.get("id")
                    if other_id == lane_id or other_id not in current_group:
                        continue
                    if (
                        other.get("file_access") == "write"
                        and other.get("workspace_mode") == "worktree"
                        and paths_equal(
                            other.get("worktree_source") or "",
                            lane.get("worktree_source") or "",
                        )
                        and other_id in plan_result.get("environment_pending", [])
                    ):
                        pending_peers.append(other_id)
                if pending_peers:
                    add_error(
                        errors,
                        "execution-ready external writer requires actual paths for every "
                        "same-wave writer in the source repository: "
                        + ", ".join(sorted(pending_peers)),
                    )

    valid = not errors
    return {
        "valid": valid,
        "errors": errors,
        "classification": (
            "external_environment_receipt"
            if valid and status == "verified"
            else "external_environment_failure"
            if valid
            else "invalid_external_environment_evidence"
        ),
        "execution_ready": valid and status == "verified",
        "plan_bound": valid,
        "receipt": {
            "run_id": run_id,
            "lane_id": lane_id,
            "harness": harness,
            "status": status,
            "surface": surface,
            "file_access": file_access,
            "workspace_mode": workspace_mode,
            "worktree_source": worktree_source,
            "repository_root": repository_root,
            "workspace_path": workspace_path,
            "base_revision": base_revision,
            "environment_verified": environment_verified,
            "evidence_source": evidence_source,
            "environment_evidence": environment_evidence,
            "failure": failure,
        },
    }


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("receipt_file")
    parser.add_argument("--plan", required=True)
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()
    try:
        receipt = json.loads(Path(args.receipt_file).read_text(encoding="utf-8"))
        plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        result = {
            "valid": False,
            "errors": [f"cannot read input: {exc}"],
            "classification": "invalid_external_environment_evidence",
            "execution_ready": False,
            "plan_bound": False,
        }
    else:
        result = validate_receipt(receipt, plan)
    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print("VALID" if result["valid"] else "INVALID")
        for error in result["errors"]:
            print(f"- {error}")
    return 0 if result["valid"] else 2


if __name__ == "__main__":
    sys.exit(main())
