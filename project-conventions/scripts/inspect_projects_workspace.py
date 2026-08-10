#!/usr/bin/env python3
"""Offline, read-only inspector for one local Projects Workspace.

The inspector never follows directory links, never writes to the workspace, and
never performs network access. A structural collection row may point to one
member index; safe member paths are expanded for coverage and reporting.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import subprocess
import sys
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


RESERVED = {"_project-catalog"}
IGNORED_WALK_DIRS = {
    ".git",
    ".hg",
    ".svn",
    "node_modules",
    "DerivedData",
    "build",
    "dist",
    ".cache",
    ".venv",
    "venv",
}


@dataclass(frozen=True)
class IndexEntry:
    key: str
    path: str
    category_file: str
    vcs: str = ""
    remote: str = ""
    kind: str = "project"
    members_index: str = ""
    parent_collection: str = ""
    source: str = ""
    repository_root: str = ""
    managed_scope: str = ""
    role: str = ""
    status: str = ""


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description="Inspect one local Projects Workspace without modifying it."
    )
    parser.add_argument("root", help="Projects Workspace root")
    parser.add_argument(
        "--indexes-dir",
        help="Markdown index directory; defaults to _project-catalog/docs/indexes",
    )
    parser.add_argument("--max-depth", type=int, default=5)
    parser.add_argument("--max-entries", type=int, default=10000)
    parser.add_argument("--git-timeout", type=float, default=2.0)
    parser.add_argument("--format", choices=("json", "markdown"), default="json")
    return parser.parse_args()


def relative(path: Path, root: Path) -> str:
    value = path.relative_to(root).as_posix()
    return value if value != "." else ""


def entry_kind(path: Path) -> tuple[str, bool]:
    try:
        is_link = path.is_symlink()
        is_junction = bool(getattr(os.path, "isjunction", lambda _: False)(path))
        if is_link or is_junction:
            return ("junction" if is_junction else "symlink", path.exists())
        if path.is_dir():
            return ("directory", True)
        if path.is_file():
            return ("file", True)
        return ("other", True)
    except OSError:
        return ("unreadable", False)


def scan_top_level(root: Path) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with os.scandir(root) as iterator:
        for raw in iterator:
            path = Path(raw.path)
            kind, target_exists = entry_kind(path)
            rows.append(
                {
                    "name": raw.name,
                    "path": raw.name,
                    "kind": kind,
                    "target_exists": target_exists,
                    "reserved": raw.name in RESERVED,
                    "hidden": raw.name.startswith("."),
                }
            )
    return sorted(rows, key=lambda item: str(item["name"]).casefold())


def iter_paths(
    root: Path, max_depth: int, max_entries: int
) -> tuple[list[Path], list[tuple[Path, bool]], bool]:
    git_markers: list[Path] = []
    links: list[tuple[Path, bool]] = []
    observed = 0
    for current, dirs, files in os.walk(root, topdown=True, followlinks=False):
        current_path = Path(current)
        depth = len(current_path.relative_to(root).parts)
        raw_dirs = sorted(dirs)
        kept_dirs: list[str] = []
        for name in raw_dirs:
            path = current_path / name
            kind, target_exists = entry_kind(path)
            observed += 1
            if name == ".git":
                git_markers.append(path)
            if kind in {"symlink", "junction"}:
                links.append((path, target_exists))
            if observed >= max_entries:
                return git_markers, links, True
            if (
                depth < max_depth
                and name not in IGNORED_WALK_DIRS
                and not (current_path == root and name in RESERVED)
                and kind not in {"symlink", "junction"}
            ):
                kept_dirs.append(name)
        dirs[:] = kept_dirs
        for name in sorted(files):
            path = current_path / name
            kind, target_exists = entry_kind(path)
            observed += 1
            if name == ".git":
                git_markers.append(path)
            if kind in {"symlink", "junction"}:
                links.append((path, target_exists))
            if observed >= max_entries:
                return git_markers, links, True
    return git_markers, links, False


def git_value(directory: Path, arguments: list[str], timeout: float) -> str | None:
    try:
        result = subprocess.run(
            ["git", "-C", str(directory), *arguments],
            check=False,
            capture_output=True,
            text=True,
            timeout=timeout,
        )
    except (OSError, subprocess.TimeoutExpired):
        return None
    if result.returncode != 0:
        return None
    value = result.stdout.strip()
    return value or None


def display_git_path(
    value: str | None, parent: Path, root: Path
) -> str | None:
    if not value:
        return None
    candidate = Path(value)
    candidate = candidate if candidate.is_absolute() else parent / candidate
    try:
        return relative(candidate.resolve(), root)
    except (ValueError, OSError):
        return "outside-workspace"


def normalize_remote_identity(value: str | None) -> str | None:
    if not value or value.strip() in {"", "-"}:
        return None
    remote = value.strip()
    if "://" in remote:
        remote = remote.split("://", 1)[1]
        authority, separator, suffix = remote.partition("/")
        if "@" in authority:
            authority = authority.rsplit("@", 1)[1]
        remote = authority + (separator + suffix if separator else "")
    elif re.match(r"^[^/@]+@[^:]+:", remote):
        remote = remote.split("@", 1)[1].replace(":", "/", 1)
    remote = remote.strip().strip("/")
    if remote.endswith(".git"):
        remote = remote[:-4]
    return remote.casefold() or None


def remotes_equivalent(left: str | None, right: str | None) -> bool:
    a = normalize_remote_identity(left)
    b = normalize_remote_identity(right)
    if not a or not b:
        return True
    return a == b or a.endswith("/" + b) or b.endswith("/" + a)


def inspect_git_roots(
    root: Path, paths: Iterable[Path], timeout: float
) -> list[dict[str, object]]:
    marker_parents = sorted(
        {path.parent for path in paths if path.name == ".git"},
        key=lambda path: str(path),
    )
    results: list[dict[str, object]] = []
    seen: set[str] = set()
    for parent in marker_parents:
        top = git_value(parent, ["rev-parse", "--show-toplevel"], timeout)
        common = git_value(parent, ["rev-parse", "--git-common-dir"], timeout)
        remote = git_value(parent, ["remote", "get-url", "origin"], timeout)
        superproject = git_value(
            parent, ["rev-parse", "--show-superproject-working-tree"], timeout
        )
        if top:
            try:
                top_display = relative(Path(top).resolve(), root)
            except (ValueError, OSError):
                top_display = "outside-workspace"
        else:
            top_display = relative(parent, root)
        if top_display in seen:
            continue
        seen.add(top_display)
        results.append(
            {
                "path": top_display,
                "marker": relative(parent / ".git", root),
                "common_dir": display_git_path(common, parent, root),
                "remote_identity": normalize_remote_identity(remote),
                "superproject": display_git_path(superproject, parent, root),
                "verified": bool(top),
            }
        )
    return results


def table_cells(line: str) -> list[str]:
    stripped = line.strip()
    if not stripped.startswith("|") or not stripped.endswith("|"):
        return []
    return [cell.strip() for cell in stripped[1:-1].split("|")]


def parse_index_file(path: Path, label_base: Path) -> list[IndexEntry]:
    entries: list[IndexEntry] = []
    header: list[str] | None = None
    for line in path.read_text(encoding="utf-8").splitlines():
        cells = table_cells(line)
        lowered = [cell.lower().strip("`") for cell in cells]
        if "key" in lowered and "path" in lowered:
            header = lowered
            continue
        if not header or not cells or len(cells) != len(header):
            continue
        if all(set(cell) <= {"-", ":", " "} for cell in cells):
            continue
        row = dict(zip(header, (cell.strip("`") for cell in cells)))
        key = row.get("key", "").strip()
        local_path = row.get("path", "").strip()
        if not key or not local_path:
            continue
        entries.append(
            IndexEntry(
                key=key,
                path=local_path,
                category_file=path.relative_to(label_base).as_posix(),
                vcs=row.get("vcs", ""),
                remote=row.get("remote", ""),
                kind=row.get("kind", "project") or "project",
                members_index=row.get("members_index", ""),
                source=row.get("source", ""),
                repository_root=row.get("repository_root", ""),
                managed_scope=row.get("managed_scope", ""),
                role=row.get("role", ""),
                status=row.get("status", ""),
            )
        )
    return entries


def is_safe_relative_path(value: str) -> bool:
    normalized = value.replace("\\", "/")
    candidate = Path(normalized)
    if candidate.is_absolute() or re.match(r"^[a-zA-Z]:/", normalized):
        return False
    return bool(candidate.parts) and ".." not in candidate.parts


def load_indexes(
    root: Path, indexes_dir: Path | None
) -> tuple[list[IndexEntry], list[dict[str, str]], list[dict[str, object]]]:
    if indexes_dir is None or not indexes_dir.is_dir():
        return [], [], []
    entries: list[IndexEntry] = []
    errors: list[dict[str, str]] = []
    expansions: list[dict[str, object]] = []
    for path in sorted(indexes_dir.rglob("*.md")):
        if path.is_symlink():
            errors.append(
                {
                    "type": "index_path_link",
                    "path": path.relative_to(indexes_dir).as_posix(),
                }
            )
            continue
        try:
            entries.extend(parse_index_file(path, indexes_dir))
        except (OSError, UnicodeError, ValueError) as exc:
            errors.append(
                {
                    "type": "index_read_error",
                    "path": f"{path.relative_to(indexes_dir).as_posix()}: {exc}",
                }
            )

    collections = [entry for entry in entries if entry.kind == "collection"]
    expanded: list[IndexEntry] = []
    for collection in collections:
        if (
            not is_safe_relative_path(collection.path)
            or not is_safe_relative_path(collection.members_index)
        ):
            errors.append(
                {"type": "collection_index_invalid", "path": collection.key}
            )
            continue
        collection_candidate = root / collection.path
        collection_kind, _ = entry_kind(collection_candidate)
        if collection_kind in {"symlink", "junction"}:
            errors.append(
                {"type": "collection_path_link", "path": collection.path}
            )
            continue
        collection_root = collection_candidate.resolve()
        try:
            collection_root.relative_to(root)
        except ValueError:
            errors.append(
                {"type": "collection_index_invalid", "path": collection.key}
            )
            continue
        member_index_candidate = collection_root / collection.members_index
        member_index_kind, _ = entry_kind(member_index_candidate)
        if member_index_kind in {"symlink", "junction"}:
            errors.append(
                {
                    "type": "index_path_link",
                    "path": f"{collection.path}/{collection.members_index}",
                }
            )
            continue
        member_file = member_index_candidate.resolve()
        try:
            member_file.relative_to(collection_root)
        except ValueError:
            errors.append(
                {"type": "collection_index_invalid", "path": collection.key}
            )
            continue
        if not member_file.is_file():
            errors.append(
                {
                    "type": "collection_index_missing",
                    "path": f"{collection.path}/{collection.members_index}",
                }
            )
            continue
        try:
            member_rows = parse_index_file(member_file, collection_root)
        except (OSError, UnicodeError, ValueError) as exc:
            errors.append(
                {
                    "type": "collection_index_invalid",
                    "path": f"{collection.key}: {exc}",
                }
            )
            continue
        control_roles = [
            member for member in member_rows
            if member.role == "collection-control"
        ]
        if len(control_roles) != 1:
            errors.append(
                {
                    "type": "collection_control_role_invalid",
                    "path": (
                        f"{collection.key}: expected=1, "
                        f"observed={len(control_roles)}"
                    ),
                }
            )
        accepted = 0
        for member in member_rows:
            if not is_safe_relative_path(member.path):
                errors.append(
                    {
                        "type": "collection_member_path_invalid",
                        "path": f"{collection.key}/{member.key}:{member.path}",
                    }
                )
                continue
            if member.status not in {
                "active",
                "inactive",
                "observed",
                "archived",
            }:
                errors.append(
                    {
                        "type": "collection_member_status_invalid",
                        "path": (
                            f"{collection.key}/{member.key}:"
                            f"{member.status or '<empty>'}"
                        ),
                    }
                )
            member_candidate = collection_root / member.path
            member_kind, _ = entry_kind(member_candidate)
            if member_kind in {"symlink", "junction"}:
                errors.append(
                    {
                        "type": "collection_member_path_link",
                        "path": f"{collection.key}/{member.key}:{member.path}",
                    }
                )
                continue
            try:
                member_candidate.resolve().relative_to(collection_root)
            except ValueError:
                errors.append(
                    {
                        "type": "collection_member_path_invalid",
                        "path": f"{collection.key}/{member.key}:{member.path}",
                    }
                )
                continue
            if not is_safe_relative_path(member.source):
                errors.append(
                    {
                        "type": "collection_member_source_invalid",
                        "path": f"{collection.key}/{member.key}:{member.source}",
                    }
                )
            elif member.status in {"active", "inactive", "observed"}:
                source_candidate = member_candidate / member.source
                source_kind, _ = entry_kind(source_candidate)
                repository_relative = member.repository_root.strip().strip("`/")
                scope_relative = member.managed_scope.strip().strip("`/")
                repository_candidate = collection_root / repository_relative
                shared_mapping = False
                if (
                    repository_relative not in {"", "-"}
                    and scope_relative not in {"", "-", "whole repository"}
                    and is_safe_relative_path(repository_relative)
                    and is_safe_relative_path(scope_relative)
                ):
                    try:
                        repository_candidate.resolve().relative_to(
                            member_candidate.resolve()
                        )
                    except ValueError:
                        shared_mapping = True
                if source_kind in {"symlink", "junction"}:
                    if not shared_mapping:
                        errors.append(
                            {
                                "type": "collection_member_source_link",
                                "path": f"{collection.key}/{member.key}:{member.source}",
                            }
                        )
                    else:
                        repository_kind, _ = entry_kind(repository_candidate)
                        if repository_kind in {"symlink", "junction"}:
                            errors.append(
                                {
                                    "type": "collection_repository_root_link",
                                    "path": (
                                        f"{collection.key}/{member.key}:"
                                        f"{repository_relative}"
                                    ),
                                }
                            )
                        elif not repository_candidate.is_dir():
                            errors.append(
                                {
                                    "type": "collection_repository_root_missing",
                                    "path": (
                                        f"{collection.path}/{repository_relative}"
                                    ),
                                }
                            )
                        else:
                            expected_source = repository_candidate / scope_relative
                            try:
                                expected_source.resolve().relative_to(
                                    repository_candidate.resolve()
                                )
                                source_target = source_candidate.resolve(strict=True)
                            except (OSError, ValueError):
                                errors.append(
                                    {
                                        "type": "collection_member_projection_invalid",
                                        "path": (
                                            f"{collection.key}/{member.key}:"
                                            f"{member.source}"
                                        ),
                                    }
                                )
                            else:
                                if source_target != expected_source.resolve():
                                    errors.append(
                                        {
                                            "type": "collection_member_projection_mismatch",
                                            "path": (
                                                f"{collection.key}/{member.key}:"
                                                f"{member.source}"
                                            ),
                                        }
                                    )
                elif shared_mapping:
                    errors.append(
                        {
                            "type": "collection_member_projection_not_link",
                            "path": f"{collection.key}/{member.key}:{member.source}",
                        }
                    )
                else:
                    try:
                        source_candidate.resolve().relative_to(
                            member_candidate.resolve()
                        )
                    except ValueError:
                        errors.append(
                            {
                                "type": "collection_member_source_invalid",
                                "path": f"{collection.key}/{member.key}:{member.source}",
                            }
                        )
                    if not source_candidate.exists():
                        errors.append(
                            {
                                "type": "collection_member_source_missing",
                                "path": (
                                    f"{collection.path}/{member.path}/"
                                    f"{member.source}"
                                ),
                            }
                        )
            expanded.append(
                IndexEntry(
                    key=f"{collection.key}/{member.key}",
                    path=(
                        Path(collection.path) / Path(member.path)
                    ).as_posix(),
                    category_file=(
                        f"{collection.path}/{member.category_file}"
                    ),
                    vcs=member.vcs,
                    remote=member.remote,
                    kind="collection-member",
                    parent_collection=collection.key,
                    source=member.source,
                    role=member.role,
                    status=member.status,
                    repository_root=(
                        (Path(collection.path) / Path(member.repository_root)).as_posix()
                        if member.repository_root.strip() not in {"", "-"}
                        and is_safe_relative_path(member.repository_root.strip())
                        else member.repository_root
                    ),
                    managed_scope=member.managed_scope,
                )
            )
            accepted += 1
        expansions.append(
            {
                "collection": collection.key,
                "members_index": (
                    f"{collection.path}/{collection.members_index}"
                ),
                "members": accepted,
            }
        )
    return entries + expanded, errors, expansions


def findings_for(
    root: Path,
    top: list[dict[str, object]],
    indexes: list[IndexEntry],
    index_errors: list[dict[str, str]],
    indexes_available: bool,
    git_roots: list[dict[str, object]],
    walked_links: list[tuple[Path, bool]],
) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = list(index_errors)
    by_key: dict[str, list[IndexEntry]] = {}
    by_path: dict[str, list[IndexEntry]] = {}
    valid: list[IndexEntry] = []

    for entry in indexes:
        by_key.setdefault(entry.key, []).append(entry)
        by_path.setdefault(entry.path, []).append(entry)
        if not is_safe_relative_path(entry.path):
            findings.append({"type": "invalid_index_path", "path": entry.path})
            continue
        valid.append(entry)
        live = (
            entry.kind != "collection-member"
            or entry.status in {"active", "inactive", "observed"}
        )
        if Path(entry.path).parts[0] in RESERVED:
            findings.append(
                {"type": "reserved_entry_conflict", "path": entry.path}
            )
        if live and not (root / entry.path).exists():
            findings.append({"type": "indexed_path_missing", "path": entry.path})

    for key, items in by_key.items():
        if len(items) > 1:
            findings.append({"type": "duplicate_key", "path": key})
    for local_path, items in by_path.items():
        if len(items) > 1:
            findings.append({"type": "duplicate_path", "path": local_path})

    live_valid = [
        entry
        for entry in valid
        if entry.kind != "collection-member"
        or entry.status in {"active", "inactive", "observed"}
    ]
    indexed_top = {
        Path(entry.path).parts[0]
        for entry in live_valid
        if Path(entry.path).parts
    }
    if indexes_available:
        for item in top:
            if (
                item["kind"] == "directory"
                and not item["reserved"]
                and not item["hidden"]
                and item["name"] not in indexed_top
            ):
                findings.append(
                    {"type": "unindexed_directory", "path": str(item["path"])}
                )

    project_entries = [
        entry for entry in live_valid if entry.kind != "collection"
    ]
    collection_entries = [entry for entry in valid if entry.kind == "collection"]

    for entry in project_entries:
        prefix = entry.path.rstrip("/")
        has_explicit_repository = (
            entry.kind == "collection-member"
            and entry.repository_root.strip() not in {"", "-"}
            and is_safe_relative_path(entry.repository_root)
        )
        repository_prefix = (
            entry.repository_root.rstrip("/")
            if has_explicit_repository
            else prefix
        )
        declared_contained = [
            item
            for item in git_roots
            if item["path"] == repository_prefix
            or str(item["path"]).startswith(repository_prefix + "/")
        ]
        member_contained = [
            item
            for item in git_roots
            if item["path"] == prefix
            or str(item["path"]).startswith(prefix + "/")
        ]
        contained_by_path = {
            str(item["path"]): item
            for item in (*declared_contained, *member_contained)
        }
        contained = list(contained_by_path.values())
        if len(contained) > 1:
            findings.append(
                {"type": "nested_git_detected", "path": entry.path}
            )
        if len(contained) == 1 and entry.remote not in {"", "-"}:
            observed = str(contained[0].get("remote_identity") or "")
            if observed and not remotes_equivalent(entry.remote, observed):
                findings.append(
                    {"type": "remote_mismatch", "path": entry.path}
                )
        if entry.vcs == "none" and contained:
            findings.append(
                {
                    "type": "vcs_state_mismatch",
                    "path": f"{entry.path}: declared=none, observed=git",
                }
            )
        elif entry.vcs in {"git", "local_git"} and not contained:
            findings.append(
                {
                    "type": "vcs_state_mismatch",
                    "path": f"{entry.path}: declared={entry.vcs}, observed=none",
                }
            )
        if (
            entry.kind == "collection-member"
            and entry.vcs in {"git", "local_git"}
            and entry.source
            and contained
            and is_safe_relative_path(entry.source)
        ):
            expected = (
                repository_prefix
                if has_explicit_repository
                else (Path(entry.path) / Path(entry.source)).as_posix().rstrip("/")
            )
            observed_roots = {str(item["path"]) for item in contained}
            if expected not in observed_roots:
                findings.append(
                    {
                        "type": "repository_root_mismatch",
                        "path": (
                            f"{entry.path}: expected={expected}, "
                            f"observed={','.join(sorted(observed_roots))}"
                        ),
                    }
                )

    for collection in collection_entries:
        for item in git_roots:
            if item["path"] == collection.path.rstrip("/"):
                findings.append(
                    {"type": "collection_root_git", "path": collection.path}
                )

    if indexes_available:
        covered_paths = [entry.path.rstrip("/") for entry in project_entries]
        covered_paths.extend(
            entry.repository_root.rstrip("/")
            for entry in project_entries
            if entry.repository_root.strip() not in {"", "-"}
            and is_safe_relative_path(entry.repository_root)
        )
        for item in git_roots:
            git_path = str(item["path"])
            if git_path == "outside-workspace":
                continue
            covered = any(
                git_path == local_path
                or git_path.startswith(local_path + "/")
                for local_path in covered_paths
            )
            if not covered:
                findings.append(
                    {"type": "unindexed_git_root", "path": git_path}
                )

    for item in top:
        if item["kind"] in {"symlink", "junction"} and not item["target_exists"]:
            findings.append(
                {"type": "dangling_link", "path": str(item["path"])}
            )
    for path, target_exists in walked_links:
        if not target_exists:
            findings.append(
                {"type": "dangling_link", "path": relative(path, root)}
            )

    unique = {
        (item["type"], item["path"]): item
        for item in findings
    }
    return sorted(
        unique.values(), key=lambda item: (item["type"], item["path"])
    )


def render_markdown(report: dict[str, object]) -> str:
    def bool_text(value: object) -> str:
        return str(bool(value)).lower()

    def cell(value: object) -> str:
        if value in {None, ""}:
            return "—"
        return str(value).replace("|", "\\|").replace("\n", " ")

    lines = [
        "# Projects Workspace Inspection",
        "",
        f"- Root: `{report['root']}`",
        f"- Observed at: `{report['observed_at']}`",
        f"- Top-level entries: {len(report['top_level'])}",
        f"- Index entries including expanded members: {len(report['index_entries'])}",
        f"- Collections expanded: {len(report['collection_expansions'])}",
        f"- Git roots/markers: {len(report['git_roots'])}",
        f"- Findings: {len(report['findings'])}",
        f"- Traversal truncated: `{str(report['truncated']).lower()}`",
        "",
        "## Collections",
        "",
        "| collection | members index | members |",
        "|---|---|---:|",
    ]
    for item in report["collection_expansions"]:
        lines.append(
            f"| `{item['collection']}` | `{item['members_index']}` | {item['members']} |"
        )
    if not report["collection_expansions"]:
        lines.append("| none | — | 0 |")
    lines.extend(
        [
            "",
            "## Top-level entries",
            "",
            "| path | kind | reserved | target exists |",
            "|---|---|---:|---:|",
        ]
    )
    for item in report["top_level"]:
        lines.append(
            f"| `{item['path']}` | {item['kind']} | "
            f"{bool_text(item['reserved'])} | {bool_text(item['target_exists'])} |"
        )
    lines.extend(
        [
            "",
            "## Index entries",
            "",
            "| key | path | kind | vcs | status | source | repository root | managed scope | remote |",
            "|---|---|---|---|---|---|---|---|---|",
        ]
    )
    for item in report["index_entries"]:
        lines.append(
            f"| `{cell(item['key'])}` | `{cell(item['path'])}` | "
            f"{cell(item['kind'])} | {cell(item['vcs'])} | "
            f"{cell(item['status'])} | `{cell(item['source'])}` | "
            f"`{cell(item['repository_root'])}` | `{cell(item['managed_scope'])}` | "
            f"`{cell(item['remote'])}` |"
        )
    if not report["index_entries"]:
        lines.append("| none | — | — | — | — | — | — | — | — |")
    lines.extend(
        [
            "",
            "## Git roots",
            "",
            "| path | marker | verified | remote |",
            "|---|---|---:|---|",
        ]
    )
    for item in report["git_roots"]:
        lines.append(
            f"| `{cell(item['path'])}` | `{cell(item['marker'])}` | "
            f"{bool_text(item['verified'])} | `{cell(item['remote_identity'])}` |"
        )
    if not report["git_roots"]:
        lines.append("| none | — | false | — |")
    lines.extend(["", "## Findings", "", "| type | path |", "|---|---|"])
    for finding in report["findings"]:
        lines.append(
            f"| `{finding['type']}` | `{finding['path']}` |"
        )
    if not report["findings"]:
        lines.append("| none | — |")
    return "\n".join(lines) + "\n"


def main() -> int:
    args = parse_args()
    if args.max_depth < 1 or args.max_entries < 1 or args.git_timeout <= 0:
        print("limits must be positive", file=sys.stderr)
        return 2

    root = Path(args.root).expanduser().resolve()
    if not root.is_dir() or not os.access(root, os.R_OK):
        print(f"unreadable Projects Workspace root: {root}", file=sys.stderr)
        return 2

    default_indexes = root / "_project-catalog" / "docs" / "indexes"
    indexes_dir = (
        Path(args.indexes_dir).expanduser().resolve()
        if args.indexes_dir
        else default_indexes
    )
    try:
        indexes_dir.relative_to(root)
    except ValueError:
        print(
            f"indexes directory escapes Projects Workspace: {indexes_dir}",
            file=sys.stderr,
        )
        return 2

    try:
        top = scan_top_level(root)
        git_markers, walked_links, truncated = iter_paths(
            root, args.max_depth, args.max_entries
        )
        git_roots = inspect_git_roots(root, git_markers, args.git_timeout)
        indexes_available = indexes_dir.is_dir()
        indexes, index_errors, expansions = load_indexes(
            root, indexes_dir if indexes_available else None
        )
        report: dict[str, object] = {
            "schema": "projects-workspace-inspection/v3",
            "observed_at": datetime.now(timezone.utc).isoformat(),
            "root": str(root),
            "limits": {
                "max_depth": args.max_depth,
                "max_entries": args.max_entries,
                "git_timeout": args.git_timeout,
            },
            "truncated": truncated,
            "top_level": top,
            "git_roots": git_roots,
            "index_entries": [asdict(entry) for entry in indexes],
            "collection_expansions": expansions,
            "findings": findings_for(
                root,
                top,
                indexes,
                index_errors,
                indexes_available,
                git_roots,
                walked_links,
            ),
        }
    except Exception as exc:
        print(f"inspection failed: {exc}", file=sys.stderr)
        return 3

    if args.format == "markdown":
        sys.stdout.write(render_markdown(report))
    else:
        json.dump(
            report,
            sys.stdout,
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
        sys.stdout.write("\n")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
