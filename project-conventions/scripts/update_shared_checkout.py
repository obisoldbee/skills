#!/usr/bin/env python3
"""Safely fast-forward one shared Skills checkout and validate one package.

This is the deterministic update-only entry point. It resolves the Git worktree
from the requested package, refuses dirty/ahead/detached/diverged states, performs
at most one fetch plus fast-forward, validates the distribution root and the
named package tests, reports before/after commits, and stops. It never edits
wrappers, indexes, records, or Skill links.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
import sys
from pathlib import Path


SAFE_COMPONENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


class UpdateError(RuntimeError):
    """Raised when the update-only safety gate fails."""


def run(
    cwd: Path,
    *arguments: str,
    allow_failure: bool = False,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        list(arguments),
        cwd=cwd,
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0 and not allow_failure:
        detail = result.stderr.strip() or result.stdout.strip() or "unknown error"
        raise UpdateError(f"{' '.join(arguments)} failed at {cwd}: {detail}")
    return result


def git(cwd: Path, *arguments: str) -> str:
    return run(cwd, "git", *arguments).stdout.strip()


def normalize_remote(url: str) -> str | None:
    value = url.strip().rstrip("/")
    prefixes = (
        "https://github.com/",
        "http://github.com/",
        "ssh://git@github.com/",
        "git@github.com:",
    )
    for prefix in prefixes:
        if value.lower().startswith(prefix.lower()):
            identity = value[len(prefix) :]
            if identity.endswith(".git"):
                identity = identity[:-4]
            return identity
    return None


def remote_matches(observed: str, expected: str) -> bool:
    normalized = normalize_remote(observed)
    if SAFE_COMPONENT.fullmatch(expected.split("/", 1)[0]) and "/" in expected:
        return normalized is not None and normalized.lower() == expected.lower()
    return observed.strip().rstrip("/") == expected.strip().rstrip("/")


def operation_in_progress(repository_root: Path) -> list[str]:
    git_dir_raw = git(repository_root, "rev-parse", "--git-dir")
    git_dir = Path(git_dir_raw)
    if not git_dir.is_absolute():
        git_dir = repository_root / git_dir
    markers = (
        "MERGE_HEAD",
        "CHERRY_PICK_HEAD",
        "REVERT_HEAD",
        "BISECT_LOG",
        "rebase-apply",
        "rebase-merge",
        "index.lock",
        "shallow.lock",
    )
    return [marker for marker in markers if (git_dir / marker).exists()]


def validate_package_name(value: str) -> str:
    if not SAFE_COMPONENT.fullmatch(value) or value in {".", ".."}:
        raise UpdateError(f"unsafe package name: {value!r}")
    return value


def validate_after_update(repository_root: Path, package_root: Path) -> list[str]:
    commands = [
        [
            sys.executable,
            "-B",
            str(repository_root / "scripts" / "verify_release.py"),
            str(repository_root),
        ],
        [
            sys.executable,
            "-B",
            str(package_root / "scripts" / "validate_package.py"),
            str(package_root),
        ],
    ]
    completed: list[str] = []
    for command in commands:
        result = run(repository_root, *command)
        completed.append(" ".join(command[1:]))
        if result.stderr and "FAILED" in result.stderr:
            raise UpdateError(f"package validation reported failure: {result.stderr.strip()}")
    return completed


def update(
    package_root: Path,
    package_name: str,
    remote_name: str,
    remote_identity: str,
    expected_ref: str,
) -> dict[str, object]:
    package_name = validate_package_name(package_name)
    remote_name = validate_package_name(remote_name)
    expected_ref = validate_package_name(expected_ref)
    package_root = package_root.expanduser().resolve()
    if package_root.name != package_name or not (package_root / "SKILL.md").is_file():
        raise UpdateError(
            f"requested package entry is missing or mismatched: {package_root}"
        )

    repository_root = Path(
        git(package_root, "rev-parse", "--show-toplevel")
    ).resolve()
    try:
        relative_package = package_root.relative_to(repository_root).as_posix()
    except ValueError as exc:
        raise UpdateError("package path escapes the resolved Git worktree") from exc
    if relative_package != package_name:
        raise UpdateError(
            f"managed package path differs: expected {package_name}, observed {relative_package}"
        )

    branch = git(repository_root, "symbolic-ref", "--quiet", "--short", "HEAD")
    if branch != expected_ref:
        raise UpdateError(
            f"checkout branch differs: expected {expected_ref}, observed {branch or 'detached'}"
        )
    upstream = git(
        repository_root,
        "rev-parse",
        "--abbrev-ref",
        "--symbolic-full-name",
        "@{upstream}",
    )
    expected_upstream = f"{remote_name}/{expected_ref}"
    if upstream != expected_upstream:
        raise UpdateError(
            f"checkout upstream differs: expected {expected_upstream}, observed {upstream}"
        )
    status = git(
        repository_root,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
    )
    if status:
        raise UpdateError("checkout is dirty; update-only stopped before fetch")
    operations = operation_in_progress(repository_root)
    if operations:
        raise UpdateError(
            "Git operation or lock is present: " + ", ".join(operations)
        )
    origin = git(repository_root, "remote", "get-url", remote_name)
    if not remote_matches(origin, remote_identity):
        raise UpdateError(
            f"checkout remote differs: expected {remote_identity}, observed {origin}"
        )

    before = git(repository_root, "rev-parse", "HEAD")
    git(repository_root, "fetch", "--prune", remote_name)
    counts = git(
        repository_root,
        "rev-list",
        "--left-right",
        "--count",
        f"HEAD...{upstream}",
    ).split()
    if len(counts) != 2:
        raise UpdateError(f"unexpected ahead/behind output: {' '.join(counts)}")
    ahead, behind = (int(counts[0]), int(counts[1]))
    if ahead:
        state = "diverged" if behind else "ahead"
        raise UpdateError(
            f"checkout is {state}: ahead={ahead}, behind={behind}; no local commit was changed"
        )
    ancestor = run(
        repository_root,
        "git",
        "merge-base",
        "--is-ancestor",
        "HEAD",
        upstream,
        allow_failure=True,
    )
    if ancestor.returncode != 0:
        raise UpdateError("checkout cannot fast-forward to its upstream")
    if behind:
        git(repository_root, "merge", "--ff-only", upstream)

    after = git(repository_root, "rev-parse", "HEAD")
    upstream_head = git(repository_root, "rev-parse", upstream)
    if after != upstream_head:
        raise UpdateError(f"post-update HEAD differs from upstream: {after} != {upstream_head}")
    if git(
        repository_root,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
    ):
        raise UpdateError("checkout became dirty during update")

    try:
        validations = validate_after_update(repository_root, package_root)
    except UpdateError as exc:
        raise UpdateError(
            f"checkout state after update is {after}; validation failed after "
            f"{before} -> {after}: {exc}"
        ) from exc
    return {
        "status": "updated" if before != after else "already_current",
        "lifecycle": "update-only",
        "package": package_name,
        "package_root": str(package_root),
        "repository_root": str(repository_root),
        "remote": origin,
        "branch": branch,
        "upstream": upstream,
        "before": before,
        "after": after,
        "ahead": 0,
        "behind": 0,
        "validations": validations,
        "stop_boundary": "no wrapper, index, record, or link work",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "package_root",
        nargs="?",
        type=Path,
        default=Path(__file__).resolve().parents[1],
    )
    parser.add_argument("--package", default="project-conventions")
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--remote-identity", default="obisoldbee/skills")
    parser.add_argument("--ref", default="main")
    arguments = parser.parse_args()
    try:
        result = update(
            arguments.package_root,
            arguments.package,
            arguments.remote,
            arguments.remote_identity,
            arguments.ref,
        )
    except (UpdateError, OSError, UnicodeError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
