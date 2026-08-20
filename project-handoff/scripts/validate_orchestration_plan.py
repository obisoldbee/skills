#!/usr/bin/env python3
"""Validate a declared project-handoff orchestration plan without model calls."""

import argparse
import json
import ntpath
from pathlib import Path
import posixpath
import re
import sys

from validate_dispatch_route import validate_route

LANE_FIELDS = (
    "id",
    "goal",
    "depends_on",
    "read_paths",
    "write_paths",
    "mutable_resources",
    "harness",
    "file_access",
    "workspace_mode",
    "worktree_source",
    "repository_root",
    "workspace_path",
    "base_revision",
    "expected_outputs",
    "validation",
    "route",
)
PLAN_FIELDS = {"run_id", "integration_owner", "lanes"}
WINDOWS_ABSOLUTE_PATH = re.compile(r"^(?:[A-Za-z]:[\\/]|\\\\)")
HARNESS_ID = re.compile(r"^[a-z0-9][a-z0-9._-]{0,63}$")
GIT_REVISION = re.compile(r"^(?:[0-9a-f]{40}|[0-9a-f]{64})$", re.IGNORECASE)
CONTENT_REVISION = re.compile(
    r"^(?:snapshot|working-tree):sha256:[0-9a-f]{64}$", re.IGNORECASE
)
FILE_ACCESS_MODES = {"read_only", "write"}
WORKSPACE_MODES = {"shared_checkout", "worktree", "non_git"}


def add_error(errors, message):
    if message not in errors:
        errors.append(message)


def string_list(value, field, errors, allow_empty=True, preserve_items=False):
    if not isinstance(value, list):
        add_error(errors, f"{field} must be a list")
        return []
    result = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            add_error(errors, f"{field}[{index}] must be a non-empty string")
            continue
        result.append(item if preserve_items else item.strip())
    if not allow_empty and not result:
        add_error(errors, f"{field} must contain at least one item")
    return result


def optional_string(value, field, errors):
    if value is None:
        return ""
    if not isinstance(value, str):
        add_error(errors, f"{field} must be a string or null")
        return ""
    return value.strip()


def absolute_path(value, field, errors, allow_pending=False):
    if value is None:
        normalized = ""
    elif not isinstance(value, str):
        add_error(errors, f"{field} must be a string or null")
        normalized = ""
    else:
        normalized = value
        if normalized != normalized.strip():
            add_error(errors, f"{field} must not start or end with whitespace")
    if not normalized:
        if not allow_pending:
            add_error(errors, f"{field} must be an absolute path")
        return ""
    style = path_style(normalized)
    if style == "relative":
        add_error(errors, f"{field} must be an absolute path")
        return ""
    if style == "windows":
        if has_windows_ambiguous_component(normalized):
            add_error(errors, f"{field} has a Windows component ending in dot or space")
        return ntpath.normpath(normalized.replace("/", "\\"))
    return posixpath.normpath(normalized.replace("\\", "/"))


def normalize_paths(values, field, errors):
    normalized = []
    for index, value in enumerate(values):
        if value != value.strip():
            add_error(
                errors,
                f"{field}[{index}] must not start or end with whitespace: {value!r}",
            )
            continue
        if any(marker in value for marker in ("*", "?", "[", "]")):
            add_error(
                errors,
                f"{field}[{index}] must be a literal path, not a glob: {value}",
            )
            continue
        drive_relative = bool(re.match(r"^[A-Za-z]:", value))
        rooted = value.startswith(("/", "\\"))
        if path_style(value) != "relative" or drive_relative or rooted:
            add_error(
                errors,
                f"{field}[{index}] must be relative to workspace_path: {value}",
            )
            continue
        candidate = posixpath.normpath(value.replace("\\", "/"))
        if candidate.startswith("/"):
            add_error(
                errors,
                f"{field}[{index}] must be relative to workspace_path: {value}",
            )
            continue
        if candidate == ".." or candidate.startswith("../"):
            add_error(
                errors,
                f"{field}[{index}] must not escape workspace_path: {value}",
            )
            continue
        normalized.append(candidate)
    return normalized


def path_style(value):
    if WINDOWS_ABSOLUTE_PATH.match(value) or value.startswith("//"):
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
    style = path_style(value)
    if style == "windows":
        return style, ntpath.normcase(ntpath.normpath(value.replace("/", "\\")))
    return style, posixpath.normpath(value.replace("\\", "/"))


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


def paths_overlap(left, right, left_scope, right_scope):
    left_style = path_style(left)
    right_style = path_style(right)
    if left_style != right_style:
        return False
    if left_style == "relative" and not paths_equal(left_scope, right_scope):
        return False

    if left_style == "relative":
        separator = "/"
        left_key = posixpath.normpath(left.replace("\\", "/"))
        right_key = posixpath.normpath(right.replace("\\", "/"))
        if path_style(left_scope) == "windows":
            left_key = left_key.casefold()
            right_key = right_key.casefold()
    elif left_style == "windows":
        separator = "\\"
        left_key = ntpath.normcase(left)
        right_key = ntpath.normcase(right)
    else:
        separator = "/"
        left_key = left
        right_key = right

    if left_key == right_key:
        return True
    if left_style == "relative" and (left_key == "." or right_key == "."):
        return True

    left_prefix = left_key.rstrip(separator) + separator
    right_prefix = right_key.rstrip(separator) + separator
    return left_key.startswith(right_prefix) or right_key.startswith(left_prefix)


def overlapping_pairs(left_paths, right_paths, left_scope, right_scope):
    overlaps = []
    for left in left_paths:
        for right in right_paths:
            if paths_overlap(left, right, left_scope, right_scope):
                pair = [left, right]
                if pair not in overlaps:
                    overlaps.append(pair)
    return overlaps


def is_reserved_shared_record(relative, path_scope):
    parts = [part for part in relative.replace("\\", "/").split("/") if part not in {"", "."}]
    if not parts:
        return False
    windows_scope = path_style(path_scope) == "windows"
    comparison = [part.casefold() for part in parts] if windows_scope else parts
    if comparison[0] in {"conversation", "memory", "controller"}:
        return True
    if comparison[:2] == ["docs", "indexes"]:
        return True
    reserved_names = {"index.md", "members.md"} if windows_scope else {"INDEX.md", "MEMBERS.md"}
    return comparison[-1] in reserved_names


def write_scope_reaches_reserved(relative, path_scope):
    if is_reserved_shared_record(relative, path_scope):
        return True
    return any(
        paths_overlap(relative, protected, path_scope, path_scope)
        for protected in ("conversation", "memory", "controller", "docs/indexes")
    )


def route_contract(route, lane_id, errors):
    field = f"lane {lane_id} route"
    result, route_errors = validate_route(route, field)
    for error in route_errors:
        add_error(errors, error)
    return result


def topological_waves(lane_ids, dependencies, errors):
    indegree = {lane_id: len(dependencies.get(lane_id, [])) for lane_id in lane_ids}
    dependents = {lane_id: [] for lane_id in lane_ids}
    for lane_id, prerequisites in dependencies.items():
        for prerequisite in prerequisites:
            if prerequisite in dependents:
                dependents[prerequisite].append(lane_id)

    order = {lane_id: index for index, lane_id in enumerate(lane_ids)}
    ready = [lane_id for lane_id in lane_ids if indegree[lane_id] == 0]
    waves = []
    visited = 0

    while ready:
        wave = sorted(ready, key=order.get)
        waves.append(wave)
        visited += len(wave)
        next_ready = []
        for lane_id in wave:
            for dependent in dependents[lane_id]:
                indegree[dependent] -= 1
                if indegree[dependent] == 0:
                    next_ready.append(dependent)
        ready = next_ready

    if visited != len(lane_ids):
        cyclic = [lane_id for lane_id in lane_ids if indegree[lane_id] > 0]
        add_error(errors, f"dependency graph contains a cycle involving: {', '.join(cyclic)}")
        return []
    return waves


def ancestors_for(lane_id, dependencies, cache):
    if lane_id in cache:
        return cache[lane_id]
    ancestors = set()
    for prerequisite in dependencies.get(lane_id, []):
        ancestors.add(prerequisite)
        ancestors.update(ancestors_for(prerequisite, dependencies, cache))
    cache[lane_id] = ancestors
    return ancestors


def ordering_for(left, right, dependencies, acyclic):
    if not acyclic:
        return "unknown_cycle"
    cache = {}
    if right in ancestors_for(left, dependencies, cache):
        return f"{right}_before_{left}"
    if left in ancestors_for(right, dependencies, cache):
        return f"{left}_before_{right}"
    return "unordered"


def validate_plan(plan):
    errors = []
    conflicts = []
    environment_pending = []
    base_pending = []
    launch_receipt_required = []

    if not isinstance(plan, dict):
        return {
            "valid": False,
            "errors": ["plan root must be an object"],
            "ready_groups": [],
            "resource_conflicts": [],
            "environment_pending": [],
            "base_pending": [],
            "launch_receipt_required": [],
            "integration_owner": None,
            "execution_contract_complete": False,
        }

    run_id = plan.get("run_id")
    unknown_plan_fields = sorted(set(plan) - PLAN_FIELDS)
    if unknown_plan_fields:
        add_error(
            errors,
            "plan contains unsupported fields: " + ", ".join(unknown_plan_fields),
        )
    if not isinstance(run_id, str) or not run_id.strip():
        add_error(errors, "run_id must be a non-empty string")

    lanes_value = plan.get("lanes")
    if not isinstance(lanes_value, list) or not lanes_value:
        add_error(errors, "lanes must be a non-empty list")
        lanes_value = []

    lanes = {}
    lane_ids = []
    dependencies = {}

    for index, lane in enumerate(lanes_value):
        if not isinstance(lane, dict):
            add_error(errors, f"lanes[{index}] must be an object")
            continue
        for field in LANE_FIELDS:
            if field not in lane:
                add_error(errors, f"lanes[{index}] is missing required field: {field}")
        unknown_lane_fields = sorted(set(lane) - set(LANE_FIELDS))
        if unknown_lane_fields:
            add_error(
                errors,
                f"lanes[{index}] contains unsupported fields: "
                + ", ".join(unknown_lane_fields),
            )

        lane_id = lane.get("id")
        if not isinstance(lane_id, str) or not lane_id.strip():
            add_error(errors, f"lanes[{index}].id must be a non-empty string")
            continue
        lane_id = lane_id.strip()
        if lane_id in lanes:
            add_error(errors, f"duplicate lane id: {lane_id}")
            continue

        goal = lane.get("goal")
        if not isinstance(goal, str) or not goal.strip():
            add_error(errors, f"lane {lane_id} goal must be a non-empty string")
        validation = lane.get("validation")
        if not isinstance(validation, str) or not validation.strip():
            add_error(errors, f"lane {lane_id} validation must be a non-empty string")

        depends_on = string_list(
            lane.get("depends_on"), f"lane {lane_id} depends_on", errors
        )
        read_paths = normalize_paths(
            string_list(
                lane.get("read_paths"),
                f"lane {lane_id} read_paths",
                errors,
                preserve_items=True,
            ),
            f"lane {lane_id} read_paths",
            errors,
        )
        write_paths = normalize_paths(
            string_list(
                lane.get("write_paths"),
                f"lane {lane_id} write_paths",
                errors,
                preserve_items=True,
            ),
            f"lane {lane_id} write_paths",
            errors,
        )
        mutable_resources = string_list(
            lane.get("mutable_resources"),
            f"lane {lane_id} mutable_resources",
            errors,
        )
        expected_outputs = string_list(
            lane.get("expected_outputs"),
            f"lane {lane_id} expected_outputs",
            errors,
            allow_empty=False,
        )

        harness = optional_string(lane.get("harness"), f"lane {lane_id} harness", errors)
        if not harness:
            add_error(errors, f"lane {lane_id} harness must be a non-empty string")
        elif not HARNESS_ID.fullmatch(harness):
            add_error(
                errors,
                f"lane {lane_id} harness must be a lowercase identifier",
            )

        file_access = optional_string(
            lane.get("file_access"), f"lane {lane_id} file_access", errors
        )
        if file_access and file_access not in FILE_ACCESS_MODES:
            add_error(
                errors,
                f"lane {lane_id} file_access must be one of: "
                + ", ".join(sorted(FILE_ACCESS_MODES)),
            )
        workspace_mode = optional_string(
            lane.get("workspace_mode"), f"lane {lane_id} workspace_mode", errors
        )
        if workspace_mode and workspace_mode not in WORKSPACE_MODES:
            add_error(
                errors,
                f"lane {lane_id} workspace_mode must be one of: "
                + ", ".join(sorted(WORKSPACE_MODES)),
            )

        route = route_contract(lane.get("route"), lane_id, errors)
        surface = route.get("surface")
        if surface == "visible_thread" and harness != "codex":
            add_error(errors, f"lane {lane_id} visible_thread requires harness=codex")
        if surface == "bundled_cli" and harness != "codex-cli":
            add_error(errors, f"lane {lane_id} bundled_cli requires harness=codex-cli")
        if surface == "portable_handoff":
            launch_receipt_required.append(lane_id)

        worktree_source = absolute_path(
            lane.get("worktree_source"),
            f"lane {lane_id} worktree_source",
            errors,
            allow_pending=workspace_mode != "worktree",
        )
        repository_root = absolute_path(
            lane.get("repository_root"),
            f"lane {lane_id} repository_root",
            errors,
            allow_pending=workspace_mode in {"worktree", "non_git"},
        )
        workspace_pending_allowed = workspace_mode == "worktree" and surface == "visible_thread"
        workspace_path = absolute_path(
            lane.get("workspace_path"),
            f"lane {lane_id} workspace_path",
            errors,
            allow_pending=workspace_pending_allowed,
        )
        base_revision = optional_string(
            lane.get("base_revision"), f"lane {lane_id} base_revision", errors
        )
        if not base_revision:
            if depends_on:
                base_pending.append(lane_id)
            else:
                add_error(
                    errors,
                    f"lane {lane_id} base_revision is required for a dependency-free lane",
                )
        elif workspace_mode == "non_git" and not CONTENT_REVISION.fullmatch(base_revision):
            add_error(errors, f"lane {lane_id} non_git base_revision must be a verified content-state digest")
        elif workspace_mode != "non_git" and not GIT_REVISION.fullmatch(base_revision):
            add_error(errors, f"lane {lane_id} Git base_revision must be a full commit")

        if file_access == "read_only":
            if write_paths:
                add_error(errors, f"lane {lane_id} file_access=read_only must have empty write_paths")
        elif file_access == "write" and not write_paths and not mutable_resources:
            add_error(
                errors,
                f"lane {lane_id} file_access=write requires write_paths or mutable_resources",
            )

        if workspace_mode == "shared_checkout":
            if worktree_source:
                add_error(
                    errors,
                    f"lane {lane_id} shared_checkout must have null worktree_source",
                )
            if not repository_root:
                add_error(errors, f"lane {lane_id} shared_checkout requires repository_root")
            if repository_root and workspace_path and not path_is_within(repository_root, workspace_path):
                add_error(errors, f"lane {lane_id} workspace_path must be inside repository_root")
        elif workspace_mode == "worktree":
            if not worktree_source:
                add_error(errors, f"lane {lane_id} worktree requires worktree_source")
            if repository_root and paths_equal(repository_root, worktree_source):
                add_error(errors, f"lane {lane_id} worktree repository_root must differ from worktree_source")
            if bool(repository_root) != bool(workspace_path):
                add_error(errors, f"lane {lane_id} worktree repository_root and workspace_path must become known together")
            if repository_root and workspace_path and not path_is_within(repository_root, workspace_path):
                add_error(errors, f"lane {lane_id} workspace_path must be inside repository_root")
            if not repository_root or not workspace_path:
                environment_pending.append(lane_id)
        elif workspace_mode == "non_git":
            if worktree_source or repository_root:
                add_error(errors, f"lane {lane_id} non_git must not declare Git roots")
        if workspace_mode != "worktree" and not workspace_path:
            add_error(errors, f"lane {lane_id} workspace_mode={workspace_mode or 'unknown'} requires workspace_path")

        lanes[lane_id] = {
            "read_paths": read_paths,
            "write_paths": write_paths,
            "mutable_resources": mutable_resources,
            "expected_outputs": expected_outputs,
            "harness": harness,
            "file_access": file_access,
            "workspace_mode": workspace_mode,
            "worktree_source": worktree_source,
            "repository_root": repository_root,
            "workspace_path": workspace_path,
            "base_revision": base_revision,
            "path_scope": worktree_source or repository_root or workspace_path,
            "route": route,
        }
        if path_style(lanes[lane_id]["path_scope"]) == "windows":
            for field_name, paths in (("read_paths", read_paths), ("write_paths", write_paths)):
                for path in paths:
                    if has_windows_ambiguous_component(path):
                        add_error(
                            errors,
                            f"lane {lane_id} {field_name} has a Windows component ending in dot or space: {path}",
                        )
        lane_ids.append(lane_id)
        dependencies[lane_id] = depends_on

    lane_id_set = set(lane_ids)
    for lane_id, prerequisites in dependencies.items():
        if lane_id in prerequisites:
            add_error(errors, f"lane {lane_id} cannot depend on itself")
        for prerequisite in prerequisites:
            if prerequisite not in lane_id_set:
                add_error(errors, f"lane {lane_id} depends on unknown lane: {prerequisite}")

    graph_errors_before = len(errors)
    ready_groups = topological_waves(lane_ids, dependencies, errors)
    acyclic = bool(lane_ids) and ready_groups != [] and not any(
        "contains a cycle" in error for error in errors[graph_errors_before:]
    )

    for left_index, left_id in enumerate(lane_ids):
        for right_id in lane_ids[left_index + 1 :]:
            left = lanes[left_id]
            right = lanes[right_id]
            ordering = ordering_for(left_id, right_id, dependencies, acyclic)
            same_scope = paths_equal(left["path_scope"], right["path_scope"])
            unordered_writers = (
                ordering == "unordered"
                and left["file_access"] == "write"
                and right["file_access"] == "write"
                and same_scope
            )
            if unordered_writers:
                if left["workspace_mode"] != "worktree" or right["workspace_mode"] != "worktree":
                    add_error(
                        errors,
                        "unordered writers in one logical repository must each use workspace_mode=worktree "
                        f"or be serialized: {left_id}, {right_id}",
                    )
                elif (
                    left["repository_root"]
                    and right["repository_root"]
                    and paths_equal(left["repository_root"], right["repository_root"])
                ):
                    add_error(
                        errors,
                        "unordered worktree lanes must use distinct repository_root values: "
                        f"{left_id}, {right_id}",
                    )
                if (
                    left["base_revision"]
                    and right["base_revision"]
                    and left["base_revision"] != right["base_revision"]
                ):
                    add_error(
                        errors,
                        "unordered worktree lanes in one repository must share one base_revision: "
                        f"{left_id}, {right_id}",
                    )
            if (
                ordering == "unordered"
                and left["workspace_path"]
                and right["workspace_path"]
                and paths_equal(left["workspace_path"], right["workspace_path"])
                and left["base_revision"]
                and right["base_revision"]
                and left["base_revision"] != right["base_revision"]
            ):
                add_error(
                    errors,
                    "unordered lanes in one physical workspace must share one base_revision: "
                    f"{left_id}, {right_id}",
                )
            checks = (
                (
                    "write/write",
                    overlapping_pairs(
                        left["write_paths"], right["write_paths"],
                        left["path_scope"], right["path_scope"],
                    ),
                ),
                (
                    "write/read",
                    overlapping_pairs(
                        left["write_paths"], right["read_paths"],
                        left["path_scope"], right["path_scope"],
                    )
                    + overlapping_pairs(
                        right["write_paths"], left["read_paths"],
                        right["path_scope"], left["path_scope"],
                    ),
                ),
            )
            for kind, resources in checks:
                if not resources:
                    continue
                conflict = {
                    "lanes": [left_id, right_id],
                    "kind": kind,
                    "resources": resources,
                    "ordering": ordering,
                }
                conflicts.append(conflict)
                if ordering == "unordered":
                    add_error(
                        errors,
                        f"unordered {kind} conflict between {left_id} and {right_id}",
                    )

            shared_mutable = sorted(
                set(left["mutable_resources"]) & set(right["mutable_resources"])
            )
            if shared_mutable:
                conflicts.append(
                    {
                        "lanes": [left_id, right_id],
                        "kind": "mutable_resource",
                        "resources": shared_mutable,
                        "ordering": ordering,
                    }
                )
                if ordering == "unordered":
                    add_error(
                        errors,
                        "unordered mutable_resource conflict between "
                        f"{left_id} and {right_id}: {', '.join(shared_mutable)}",
                    )

    integration_owner = plan.get("integration_owner")
    if integration_owner != "controller" and integration_owner not in lane_id_set:
        add_error(
            errors,
            "integration_owner must be 'controller' or an existing lane id",
        )
    elif integration_owner in lane_id_set and acyclic:
        owner_ancestors = ancestors_for(integration_owner, dependencies, {})
        missing = [
            lane_id
            for lane_id in lane_ids
            if lane_id != integration_owner and lane_id not in owner_ancestors
        ]
        if missing:
            add_error(
                errors,
                f"integration owner lane {integration_owner} must depend on all other lanes; missing: {', '.join(missing)}",
            )

    for lane_id, lane in lanes.items():
        if lane_id == integration_owner:
            continue
        reserved = sorted(
            path
            for path in lane["write_paths"]
            if write_scope_reaches_reserved(path, lane["path_scope"])
        )
        if reserved:
            add_error(
                errors,
                f"lane {lane_id} writes integration-owner-only shared records: {', '.join(reserved)}",
            )

    pending_lanes = set(environment_pending) | set(base_pending) | set(launch_receipt_required)
    initial_group = ready_groups[0] if ready_groups else []

    return {
        "valid": not errors,
        "errors": errors,
        "ready_groups": ready_groups if not errors else [],
        "resource_conflicts": conflicts,
        "environment_pending": sorted(set(environment_pending)),
        "base_pending": sorted(set(base_pending)),
        "launch_receipt_required": sorted(set(launch_receipt_required)),
        "initial_execution_ready": [
            lane_id for lane_id in initial_group if lane_id not in pending_lanes
        ] if not errors else [],
        "integration_owner": integration_owner,
        "execution_contract_complete": not errors and not pending_lanes,
    }


def render_text(result):
    lines = ["VALID" if result["valid"] else "INVALID"]
    if result["errors"]:
        lines.append("errors:")
        lines.extend(f"- {error}" for error in result["errors"])
    if result["ready_groups"]:
        lines.append("ready_groups:")
        lines.extend(
            f"- {', '.join(group)}" for group in result["ready_groups"]
        )
    if result["resource_conflicts"]:
        lines.append("resource_conflicts:")
        for conflict in result["resource_conflicts"]:
            lines.append(
                "- "
                + "/".join(conflict["lanes"])
                + f": {conflict['kind']} ({conflict['ordering']})"
            )
    if result.get("environment_pending"):
        lines.append("environment_pending:")
        lines.extend(f"- {lane_id}" for lane_id in result["environment_pending"])
    if result.get("base_pending"):
        lines.append("base_pending:")
        lines.extend(f"- {lane_id}" for lane_id in result["base_pending"])
    if result.get("launch_receipt_required"):
        lines.append("launch_receipt_required:")
        lines.extend(f"- {lane_id}" for lane_id in result["launch_receipt_required"])
    if result.get("initial_execution_ready"):
        lines.append("initial_execution_ready:")
        lines.extend(f"- {lane_id}" for lane_id in result["initial_execution_ready"])
    return "\n".join(lines)


def main():
    parser = argparse.ArgumentParser(
        description="Validate a project-handoff orchestration plan."
    )
    parser.add_argument("plan_file", help="JSON plan path.")
    parser.add_argument("--format", choices=("text", "json"), default="text")
    args = parser.parse_args()

    try:
        plan = json.loads(Path(args.plan_file).read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        result = {
            "valid": False,
            "errors": [f"cannot read plan: {exc}"],
            "ready_groups": [],
            "resource_conflicts": [],
            "environment_pending": [],
            "base_pending": [],
            "launch_receipt_required": [],
            "initial_execution_ready": [],
            "integration_owner": None,
            "execution_contract_complete": False,
        }
    else:
        result = validate_plan(plan)

    if args.format == "json":
        print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    else:
        print(render_text(result))
    return 0 if result["valid"] else 2


if __name__ == "__main__":
    sys.exit(main())
