#!/usr/bin/env python3
"""Validate that a visible-task claim is backed by a create_thread receipt."""

import argparse
import json
import ntpath
from pathlib import Path
import posixpath
import re
import sys

from validate_orchestration_plan import validate_plan


STATUSES = {"created_confirmed", "created_unconfirmed", "queued", "failed"}
PROMPT_STATES = {"receipt", "readback", "false"}
FILE_ACCESS_MODES = {"read_only", "write"}
WORKSPACE_MODES = {"shared_checkout", "worktree", "non_git"}
REQUESTED_ENVIRONMENTS = {"local", "worktree"}
ACTUAL_ENVIRONMENTS = {"local", "worktree", "pending", "unknown"}
ENVIRONMENT_STATES = {"receipt", "readback", "false"}
FORBIDDEN_FIELDS = {"agent_path", "agent_thread_id", "agentPath", "agentThreadId"}
RECEIPT_FIELDS = {
    "actual_tool",
    "status",
    "surface",
    "requested_route",
    "task_kind",
    "run_id",
    "lane_id",
    "harness",
    "file_access",
    "workspace_mode",
    "requested_environment",
    "actual_environment",
    "environment_verified",
    "worktree_source",
    "repository_root",
    "workspace_path",
    "base_revision",
    "environment_evidence",
    "thread_id",
    "client_thread_id",
    "host_id",
    "prompt_verified",
    "failure",
}
FORBIDDEN_TOOL_MARKERS = ("spawn_agent", "subagent", "collaboration")
ID_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._:-]{7,}$")
HARNESS_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
ABSOLUTE_PATH = re.compile(r"^(?:/|[A-Za-z]:[\\/]|\\\\)")
GIT_REVISION = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$", re.IGNORECASE)
BASE_REVISION = re.compile(
    r"^(?:[0-9a-f]{40}|[0-9a-f]{64}|(?:snapshot|working-tree):sha256:[0-9a-f]{64})$",
    re.IGNORECASE,
)


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


def validate_absolute_path(value, field, errors, required=False):
    if value is None:
        result = ""
    elif not isinstance(value, str):
        add_error(errors, f"{field} must be a string or null")
        result = ""
    else:
        result = value
        if result != result.strip():
            add_error(errors, f"{field} must not start or end with whitespace")
    if required and not result:
        add_error(errors, f"{field} must be an absolute path")
    elif result and not ABSOLUTE_PATH.match(result):
        add_error(errors, f"{field} must be an absolute path")
    elif result and path_style(result) == "windows" and has_windows_ambiguous_component(result):
        add_error(errors, f"{field} has a Windows component ending in dot or space")
    return result


def validate_base_revision(value, field, errors, required=False, git_only=False):
    result = optional_string(value, field, errors)
    if required and not result:
        add_error(errors, f"{field} must be a verified base revision")
    elif result and not (GIT_REVISION if git_only else BASE_REVISION).fullmatch(result):
        add_error(errors, f"{field} has an invalid revision shape")
    return result


def path_style(value):
    if re.match(r"^(?:[A-Za-z]:[\\/]|\\\\)", value) or value.startswith("//"):
        return "windows"
    if value.startswith("/"):
        return "posix"
    return "relative"


def has_windows_ambiguous_component(value):
    _, tail = ntpath.splitdrive(value.replace("/", "\\"))
    return any(
        part not in {"", ".", ".."} and part.endswith((".", " "))
        for part in tail.split("\\")
    )


def path_identity(value):
    if path_style(value) == "windows":
        return "windows", ntpath.normcase(ntpath.normpath(value.replace("/", "\\")))
    return path_style(value), posixpath.normpath(value.replace("\\", "/"))


def paths_equal(left, right):
    return bool(left and right) and path_identity(left) == path_identity(right)


def path_is_within(root, candidate):
    if not root or not candidate or path_style(root) != path_style(candidate):
        return False
    try:
        if path_style(root) == "windows":
            normalized_root = ntpath.normcase(ntpath.normpath(root))
            normalized_candidate = ntpath.normcase(ntpath.normpath(candidate))
            return ntpath.commonpath([normalized_root, normalized_candidate]) == normalized_root
        normalized_root = posixpath.normpath(root)
        normalized_candidate = posixpath.normpath(candidate)
        return posixpath.commonpath([normalized_root, normalized_candidate]) == normalized_root
    except ValueError:
        return False


def required_bool(value, field, errors):
    if not isinstance(value, bool):
        add_error(errors, f"{field} must be a boolean")
        return False
    return value


def validate_environment_evidence(value, workspace_mode, errors):
    if not isinstance(value, dict):
        add_error(errors, "environment_evidence must be an object")
        return {}

    common_fields = {
        "verified_by",
        "worktree_source",
        "repository_root",
        "workspace_path",
        "base_revision",
    }
    if workspace_mode == "non_git":
        expected_fields = common_fields | {"content_state_verified"}
    elif workspace_mode in {"shared_checkout", "worktree"}:
        expected_fields = common_fields | {
            "git_dir",
            "git_common_dir",
            "head_revision",
            "working_tree_clean",
        }
    else:
        expected_fields = set(value)
    missing = sorted(expected_fields - set(value))
    extra = sorted(set(value) - expected_fields)
    if missing:
        add_error(errors, "environment_evidence is missing fields: " + ", ".join(missing))
    if extra:
        add_error(errors, "environment_evidence contains unsupported fields: " + ", ".join(extra))

    verified_by = required_string(
        value.get("verified_by"), "environment_evidence.verified_by", errors
    )
    expected_verifier = "snapshot_readback" if workspace_mode == "non_git" else "git_readback"
    if verified_by and verified_by != expected_verifier:
        add_error(
            errors,
            f"environment_evidence.verified_by must be {expected_verifier}",
        )
    worktree_source = validate_absolute_path(
        value.get("worktree_source"),
        "environment_evidence.worktree_source",
        errors,
        required=workspace_mode == "worktree",
    )
    repository_root = validate_absolute_path(
        value.get("repository_root"),
        "environment_evidence.repository_root",
        errors,
        required=workspace_mode != "non_git",
    )
    workspace_path = validate_absolute_path(
        value.get("workspace_path"),
        "environment_evidence.workspace_path",
        errors,
        required=True,
    )
    base_revision = validate_base_revision(
        value.get("base_revision"),
        "environment_evidence.base_revision",
        errors,
        required=True,
        git_only=workspace_mode != "non_git",
    )
    git_dir = ""
    git_common_dir = ""
    head_revision = ""
    working_tree_clean = False
    content_state_verified = False
    if workspace_mode == "non_git":
        if worktree_source or repository_root:
            add_error(errors, "non_git environment evidence must not declare Git roots")
        content_state_verified = required_bool(
            value.get("content_state_verified"),
            "environment_evidence.content_state_verified",
            errors,
        )
        if not content_state_verified:
            add_error(errors, "non_git environment evidence requires verified content state")
    else:
        git_dir = validate_absolute_path(
            value.get("git_dir"),
            "environment_evidence.git_dir",
            errors,
            required=True,
        )
        git_common_dir = validate_absolute_path(
            value.get("git_common_dir"),
            "environment_evidence.git_common_dir",
            errors,
            required=True,
        )
        head_revision = validate_base_revision(
            value.get("head_revision"),
            "environment_evidence.head_revision",
            errors,
            required=True,
            git_only=True,
        )
        working_tree_clean = required_bool(
            value.get("working_tree_clean"),
            "environment_evidence.working_tree_clean",
            errors,
        )
        if not working_tree_clean:
            add_error(errors, "Git environment evidence requires a clean pre-write worktree")
        if base_revision and head_revision and base_revision != head_revision:
            add_error(errors, "environment head_revision must equal base_revision before writes")
        if repository_root and workspace_path and not path_is_within(repository_root, workspace_path):
            add_error(errors, "environment workspace_path must be inside repository_root")
        if workspace_mode == "worktree":
            if repository_root and worktree_source and paths_equal(repository_root, worktree_source):
                add_error(errors, "worktree repository_root must differ from worktree_source")
            if git_dir and git_common_dir and paths_equal(git_dir, git_common_dir):
                add_error(errors, "worktree git_dir must differ from git_common_dir")
        else:
            if worktree_source:
                add_error(errors, "shared_checkout environment must have null worktree_source")
            if git_dir and git_common_dir and not paths_equal(git_dir, git_common_dir):
                add_error(errors, "shared_checkout git_dir must equal git_common_dir")
    result = {
        "verified_by": verified_by,
        "worktree_source": worktree_source,
        "repository_root": repository_root,
        "workspace_path": workspace_path,
        "base_revision": base_revision,
    }
    if workspace_mode == "non_git":
        result["content_state_verified"] = content_state_verified
    else:
        result.update(
            {
                "git_dir": git_dir,
                "git_common_dir": git_common_dir,
                "head_revision": head_revision,
                "working_tree_clean": working_tree_clean,
            }
        )
    return result


def validate_receipt(receipt):
    errors = []
    if not isinstance(receipt, dict):
        return {
            "valid": False,
            "errors": ["receipt root must be an object"],
            "classification": "invalid_visible_task_evidence",
            "registerable": False,
            "execution_ready": False,
        }

    missing_fields = sorted(RECEIPT_FIELDS - set(receipt))
    extra_fields = sorted(set(receipt) - RECEIPT_FIELDS)
    if missing_fields:
        add_error(errors, "receipt is missing fields: " + ", ".join(missing_fields))
    if extra_fields:
        add_error(errors, "receipt contains unsupported fields: " + ", ".join(extra_fields))

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

    run_id = required_string(receipt.get("run_id"), "run_id", errors)
    lane_id = required_string(receipt.get("lane_id"), "lane_id", errors)
    harness = required_string(receipt.get("harness"), "harness", errors)
    if harness and harness != "codex":
        add_error(errors, "visible-task receipt requires harness=codex")
    if harness and not HARNESS_ID.fullmatch(harness):
        add_error(errors, "harness must be a lowercase identifier")

    file_access = required_string(
        receipt.get("file_access"), "file_access", errors
    )
    if file_access and file_access not in FILE_ACCESS_MODES:
        add_error(
            errors,
            f"file_access must be one of: {', '.join(sorted(FILE_ACCESS_MODES))}",
        )
    workspace_mode = required_string(
        receipt.get("workspace_mode"), "workspace_mode", errors
    )
    if workspace_mode and workspace_mode not in WORKSPACE_MODES:
        add_error(
            errors,
            f"workspace_mode must be one of: {', '.join(sorted(WORKSPACE_MODES))}",
        )
    requested_environment = required_string(
        receipt.get("requested_environment"), "requested_environment", errors
    )
    if requested_environment and requested_environment not in REQUESTED_ENVIRONMENTS:
        add_error(
            errors,
            "requested_environment must be one of: "
            + ", ".join(sorted(REQUESTED_ENVIRONMENTS)),
        )
    actual_environment = required_string(
        receipt.get("actual_environment"), "actual_environment", errors
    )
    if actual_environment and actual_environment not in ACTUAL_ENVIRONMENTS:
        add_error(
            errors,
            "actual_environment must be one of: "
            + ", ".join(sorted(ACTUAL_ENVIRONMENTS)),
        )
    environment_value = receipt.get("environment_verified")
    if environment_value is False:
        environment_verified = "false"
    else:
        environment_verified = required_string(
            environment_value, "environment_verified", errors
        )
    if environment_verified and environment_verified not in ENVIRONMENT_STATES:
        add_error(
            errors,
            "environment_verified must be one of: "
            + ", ".join(sorted(ENVIRONMENT_STATES)),
        )

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
    evidence_value = receipt.get("environment_evidence")
    environment_evidence = None
    if evidence_value is not None:
        environment_evidence = validate_environment_evidence(
            evidence_value, workspace_mode, errors
        )

    if workspace_mode == "worktree" and requested_environment != "worktree":
        add_error(errors, "workspace_mode=worktree requires requested_environment=worktree")
    if workspace_mode in {"shared_checkout", "non_git"} and requested_environment != "local":
        add_error(
            errors,
            f"workspace_mode={workspace_mode} requires requested_environment=local",
        )

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

    if status == "created_confirmed":
        if actual_environment not in {"local", "worktree"}:
            add_error(
                errors,
                "status=created_confirmed requires actual_environment=local or worktree",
            )
        if actual_environment and actual_environment != requested_environment:
            add_error(errors, "actual_environment must match requested_environment")
        if environment_verified != "readback":
            add_error(
                errors,
                "status=created_confirmed requires environment_verified=readback",
            )
        if not workspace_path:
            add_error(errors, "status=created_confirmed requires workspace_path")
        if not base_revision:
            add_error(errors, "status=created_confirmed requires base_revision")
        if environment_evidence is None:
            add_error(errors, "status=created_confirmed requires environment_evidence")
    elif status == "created_unconfirmed":
        if actual_environment != "unknown":
            add_error(
                errors,
                "status=created_unconfirmed requires actual_environment=unknown",
            )
        if environment_verified != "false":
            add_error(
                errors,
                "status=created_unconfirmed requires environment_verified=false",
            )
    elif status == "queued":
        if actual_environment != "pending":
            add_error(errors, "status=queued requires actual_environment=pending")
        if environment_verified != "false":
            add_error(errors, "status=queued requires environment_verified=false")
    elif status == "failed":
        if actual_environment != "unknown":
            add_error(errors, "status=failed requires actual_environment=unknown")
        if environment_verified != "false":
            add_error(errors, "status=failed requires environment_verified=false")

    if status != "created_confirmed" and environment_evidence is not None:
        add_error(errors, f"status={status} must not include environment_evidence")

    if environment_evidence is not None:
        for key, outer in (
            ("worktree_source", worktree_source),
            ("repository_root", repository_root),
            ("workspace_path", workspace_path),
            ("base_revision", base_revision),
        ):
            observed = environment_evidence.get(key)
            if outer or observed:
                if key.endswith("root") or key.endswith("path"):
                    matches = paths_equal(observed, outer)
                else:
                    matches = observed == outer
                if not matches:
                    add_error(
                        errors,
                        f"environment_evidence.{key} must match receipt {key}",
                    )

    if workspace_mode == "worktree":
        if not worktree_source:
            add_error(errors, "workspace_mode=worktree requires worktree_source")
        if status == "created_confirmed" and not repository_root:
            add_error(errors, "confirmed worktree requires repository_root")
        if repository_root and worktree_source and paths_equal(repository_root, worktree_source):
            add_error(errors, "worktree repository_root must differ from worktree_source")
    elif worktree_source:
        add_error(errors, f"workspace_mode={workspace_mode} must have null worktree_source")

    if workspace_mode == "shared_checkout":
        if status == "created_confirmed" and not repository_root:
            add_error(errors, "confirmed shared_checkout requires repository_root")
        if repository_root and workspace_path and not path_is_within(repository_root, workspace_path):
            add_error(errors, "workspace_path must be inside repository_root")
    elif workspace_mode == "non_git" and repository_root:
        add_error(errors, "workspace_mode=non_git must have null repository_root")

    if actual_environment == "local" and workspace_mode == "worktree":
        add_error(errors, "worktree execution must not resolve to local environment")
    if actual_environment == "worktree" and workspace_mode != "worktree":
        add_error(errors, "actual worktree requires workspace_mode=worktree")

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
    execution_ready = not errors and status == "created_confirmed"

    return {
        "valid": not errors,
        "errors": errors,
        "classification": classification,
        "registerable": registerable,
        "execution_ready": execution_ready,
        "receipt": {
            "actual_tool": actual_tool,
            "status": status,
            "surface": surface,
            "requested_route": requested_route,
            "task_kind": task_kind,
            "run_id": run_id,
            "lane_id": lane_id,
            "harness": harness,
            "file_access": file_access,
            "workspace_mode": workspace_mode,
            "requested_environment": requested_environment,
            "actual_environment": actual_environment,
            "environment_verified": environment_verified,
            "worktree_source": worktree_source,
            "repository_root": repository_root,
            "workspace_path": workspace_path,
            "base_revision": base_revision,
            "environment_evidence": environment_evidence,
            "thread_id": thread_id,
            "client_thread_id": client_thread_id,
            "host_id": host_id,
            "prompt_verified": prompt_verified,
            "failure": failure,
        },
    }


def bind_receipt_to_plan(result, plan):
    errors = list(result.get("errors", []))
    plan_result = validate_plan(plan)
    if not plan_result["valid"]:
        for error in plan_result["errors"]:
            add_error(errors, "plan invalid: " + error)
        lane = None
    else:
        receipt = result.get("receipt", {})
        if plan.get("run_id") != receipt.get("run_id"):
            add_error(errors, "receipt run_id must match plan run_id")
        matches = [
            lane for lane in plan.get("lanes", [])
            if lane.get("id") == receipt.get("lane_id")
        ]
        lane = matches[0] if len(matches) == 1 else None
        if lane is None:
            add_error(errors, "receipt lane_id must identify exactly one plan lane")

    if lane is not None:
        receipt = result["receipt"]
        route = lane.get("route") if isinstance(lane.get("route"), dict) else {}
        for field in ("harness", "file_access", "workspace_mode", "base_revision"):
            if lane.get(field) != receipt.get(field):
                add_error(errors, f"receipt {field} must match plan lane")
        for field in ("worktree_source", "repository_root", "workspace_path"):
            planned = lane.get(field) or ""
            observed = receipt.get(field) or ""
            if planned or observed:
                if not paths_equal(planned, observed):
                    add_error(errors, f"receipt {field} must match plan lane")
        if route.get("requested_route", "").lower() != receipt.get("requested_route"):
            add_error(errors, "receipt requested_route must match plan lane route")
        if route.get("surface") != "visible_thread":
            add_error(errors, "visible-task receipt requires a visible_thread plan lane")
        if result.get("execution_ready"):
            lane_id = receipt.get("lane_id")
            if lane_id in plan_result.get("environment_pending", []):
                add_error(errors, "execution-ready receipt requires actual paths written back to plan")
            if lane_id in plan_result.get("base_pending", []):
                add_error(errors, "execution-ready receipt requires a frozen plan base_revision")
            if receipt.get("file_access") == "write" and receipt.get("workspace_mode") == "worktree":
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
                        "execution-ready worktree writer requires actual paths for every "
                        "same-wave writer in the source repository: "
                        + ", ".join(sorted(pending_peers)),
                    )

    if errors:
        result["valid"] = False
        result["errors"] = errors
        result["classification"] = "invalid_visible_task_evidence"
        result["registerable"] = False
        result["execution_ready"] = False
    result["plan_bound"] = not errors
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Validate a normalized create_thread receipt before task registration."
    )
    parser.add_argument("receipt_file", help="JSON receipt path.")
    parser.add_argument(
        "--plan",
        help="Optional orchestration plan to bind run, lane, route, and environment fields.",
    )
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
            "execution_ready": False,
        }
    else:
        result = validate_receipt(receipt)
        if args.plan:
            try:
                plan = json.loads(Path(args.plan).read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError) as exc:
                result["valid"] = False
                result["errors"].append(f"cannot read plan: {exc}")
                result["classification"] = "invalid_visible_task_evidence"
                result["registerable"] = False
                result["execution_ready"] = False
                result["plan_bound"] = False
            else:
                result = bind_receipt_to_plan(result, plan)

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print("VALID" if result["valid"] else "INVALID")
        for error in result["errors"]:
            print(f"- {error}")
    return 0 if result["valid"] else 2


if __name__ == "__main__":
    sys.exit(main())
