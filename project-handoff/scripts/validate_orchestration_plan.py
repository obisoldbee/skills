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
    "expected_outputs",
    "validation",
    "route",
)
WINDOWS_ABSOLUTE_PATH = re.compile(r"^(?:[A-Za-z]:[\\/]|\\\\)")


def add_error(errors, message):
    if message not in errors:
        errors.append(message)


def string_list(value, field, errors, allow_empty=True):
    if not isinstance(value, list):
        add_error(errors, f"{field} must be a list")
        return []
    result = []
    for index, item in enumerate(value):
        if not isinstance(item, str) or not item.strip():
            add_error(errors, f"{field}[{index}] must be a non-empty string")
            continue
        result.append(item.strip())
    if not allow_empty and not result:
        add_error(errors, f"{field} must contain at least one item")
    return result


def normalize_paths(values, field, errors):
    normalized = []
    for index, value in enumerate(values):
        if any(marker in value for marker in ("*", "?", "[", "]")):
            add_error(
                errors,
                f"{field}[{index}] must be a literal path, not a glob: {value}",
            )
            continue
        if WINDOWS_ABSOLUTE_PATH.match(value):
            normalized.append(ntpath.normpath(value.replace("/", "\\")))
        else:
            normalized.append(posixpath.normpath(value.replace("\\", "/")))
    return normalized


def path_style(value):
    if WINDOWS_ABSOLUTE_PATH.match(value):
        return "windows"
    if value.startswith("/"):
        return "posix"
    return "relative"


def paths_overlap(left, right):
    left_style = path_style(left)
    right_style = path_style(right)
    if left_style != right_style:
        return False

    if left_style == "windows":
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


def overlapping_pairs(left_paths, right_paths):
    overlaps = []
    for left in left_paths:
        for right in right_paths:
            if paths_overlap(left, right):
                pair = [left, right]
                if pair not in overlaps:
                    overlaps.append(pair)
    return overlaps


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

    if not isinstance(plan, dict):
        return {
            "valid": False,
            "errors": ["plan root must be an object"],
            "ready_groups": [],
            "resource_conflicts": [],
            "integration_owner": None,
        }

    run_id = plan.get("run_id")
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
            string_list(lane.get("read_paths"), f"lane {lane_id} read_paths", errors),
            f"lane {lane_id} read_paths",
            errors,
        )
        write_paths = normalize_paths(
            string_list(
                lane.get("write_paths"), f"lane {lane_id} write_paths", errors
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

        lanes[lane_id] = {
            "read_paths": read_paths,
            "write_paths": write_paths,
            "mutable_resources": mutable_resources,
            "expected_outputs": expected_outputs,
            "route": route_contract(lane.get("route"), lane_id, errors),
        }
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
            checks = (
                (
                    "write/write",
                    overlapping_pairs(left["write_paths"], right["write_paths"]),
                ),
                (
                    "write/read",
                    overlapping_pairs(left["write_paths"], right["read_paths"])
                    + overlapping_pairs(right["write_paths"], left["read_paths"]),
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

    return {
        "valid": not errors,
        "errors": errors,
        "ready_groups": ready_groups if not errors else [],
        "resource_conflicts": conflicts,
        "integration_owner": integration_owner,
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
            "integration_owner": None,
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
