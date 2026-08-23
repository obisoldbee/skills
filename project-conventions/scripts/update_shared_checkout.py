#!/usr/bin/env python3
"""Safely fast-forward one shared Skills checkout and validate one package.

This is the deterministic update-only entry point. It resolves the Git worktree
from the requested package, refuses dirty/ahead/detached/diverged states, performs
at most one fetch, validates the named package from the frozen candidate commit,
then fast-forwards that exact commit, reports before/after commits, and stops. It never edits
wrappers, indexes, records, or Skill links.
"""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
import subprocess
import sys
import tarfile
import tempfile
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit


SAFE_COMPONENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
REMOTE_IDENTITY = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")


class UpdateError(RuntimeError):
    """Raised when the update-only safety gate fails."""


def is_windows_junction(path: Path) -> bool:
    native = getattr(os.path, "isjunction", None)
    if native is not None:
        try:
            return bool(native(path))
        except OSError:
            return False
    if os.name != "nt":
        return False
    try:
        observed = os.lstat(path)
    except OSError:
        return False
    return getattr(observed, "st_reparse_tag", None) == getattr(
        stat, "IO_REPARSE_TAG_MOUNT_POINT", 0xA0000003
    )


def is_link_or_junction(path: Path) -> bool:
    return path.is_symlink() or is_windows_junction(path)


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
        detail = re.sub(
            r"((?:https?|ssh|git)://)[^/@\s]+@",
            r"\1<redacted>@",
            detail,
            flags=re.IGNORECASE,
        )
        raise UpdateError(f"{' '.join(arguments)} failed at {cwd}: {detail}")
    return result


def git(cwd: Path, *arguments: str) -> str:
    return run(cwd, "git", *arguments).stdout.strip()


def normalize_remote(url: str) -> str | None:
    value = url.strip().rstrip("/")
    scp = re.fullmatch(r"(?:[^@/:]+@)?github\.com:(.+)", value, re.IGNORECASE)
    if scp:
        identity = scp.group(1)
    else:
        parsed = urlsplit(value)
        if parsed.scheme.lower() not in {"http", "https", "ssh", "git"}:
            return None
        if (parsed.hostname or "").lower() != "github.com":
            return None
        identity = parsed.path.lstrip("/")
    if identity.endswith(".git"):
        identity = identity[:-4]
    if REMOTE_IDENTITY.fullmatch(identity):
        return identity
    return None


def display_remote(url: str) -> str:
    """Return a credential-free identity suitable for errors and receipts."""
    bare_identity = url.strip().rstrip("/")
    if REMOTE_IDENTITY.fullmatch(bare_identity):
        return bare_identity
    return normalize_remote(url) or "<non-GitHub remote>"


def remote_matches(observed: str, expected: str) -> bool:
    normalized = normalize_remote(observed)
    if REMOTE_IDENTITY.fullmatch(expected):
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
    if package_root.parent != repository_root or is_link_or_junction(package_root):
        raise UpdateError(
            f"managed package root is outside its exact real path or linked: {package_root}"
        )
    if not package_root.is_dir():
        raise UpdateError(f"managed package root is missing: {package_root}")
    scripts_root = package_root / "scripts"
    validator = scripts_root / "validate_package.py"
    if is_link_or_junction(scripts_root) or not scripts_root.is_dir():
        raise UpdateError(f"package scripts directory is missing or linked: {scripts_root}")
    if is_link_or_junction(validator) or not validator.is_file():
        raise UpdateError(f"package validator is missing or linked: {validator}")
    commands = [
        [
            sys.executable,
            "-B",
            str(validator),
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


def extract_candidate_archive(archive: Path, destination: Path, package_name: str) -> None:
    destination.mkdir()
    with tarfile.open(archive, mode="r:") as bundle:
        members: list[tuple[tarfile.TarInfo, str]] = []
        observed: set[str] = set()
        for member in bundle.getmembers():
            raw_name = member.name.rstrip("/")
            relative = PurePosixPath(raw_name)
            if (
                not raw_name
                or "\\" in raw_name
                or relative.is_absolute()
                or not relative.parts
                or any(part in {"", ".", ".."} for part in relative.parts)
                or relative.as_posix() != raw_name
                or relative.parts[0] != package_name
                or raw_name in observed
            ):
                raise UpdateError(f"unsafe or duplicate candidate archive path: {member.name!r}")
            if not (member.isdir() or member.isreg()):
                raise UpdateError(f"candidate package contains a linked path: {raw_name}")
            observed.add(raw_name)
            members.append((member, raw_name))

        for member, raw_name in members:
            if member.isdir():
                (destination / raw_name).mkdir(parents=True, exist_ok=True)
        for member, raw_name in members:
            if not member.isreg():
                continue
            path = destination / raw_name
            path.parent.mkdir(parents=True, exist_ok=True)
            source = bundle.extractfile(member)
            if source is None:
                raise UpdateError(f"candidate archive file cannot be read: {raw_name}")
            descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
            try:
                with os.fdopen(descriptor, "wb") as handle:
                    while chunk := source.read(1024 * 1024):
                        handle.write(chunk)
                    if hasattr(os, "fchmod"):
                        os.fchmod(handle.fileno(), 0o755 if member.mode & 0o111 else 0o644)
                if not hasattr(os, "fchmod"):
                    os.chmod(path, 0o755 if member.mode & 0o111 else 0o644)
            except Exception:
                try:
                    path.unlink()
                except OSError:
                    pass
                raise


def validate_candidate(
    repository_root: Path,
    candidate: str,
    package_name: str,
) -> list[str]:
    with tempfile.TemporaryDirectory(prefix="project-conventions-candidate-") as raw:
        temporary = Path(raw)
        archive = temporary / "candidate.tar"
        run(
            repository_root,
            "git",
            "archive",
            "--format=tar",
            f"--output={archive}",
            candidate,
            "--",
            package_name,
        )
        candidate_root = temporary / "tree"
        extract_candidate_archive(archive, candidate_root, package_name)
        validate_after_update(candidate_root, candidate_root / package_name)
    return [f"validate_package.py {package_name} at {candidate}"]


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

    branch_result = run(
        repository_root,
        "git",
        "symbolic-ref",
        "--quiet",
        "--short",
        "HEAD",
        allow_failure=True,
    )
    branch = branch_result.stdout.strip()
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
            "checkout remote differs: "
            f"expected {display_remote(remote_identity)}, observed {display_remote(origin)}"
        )

    before = git(repository_root, "rev-parse", "HEAD")
    fetch = run(
        repository_root,
        "git",
        "fetch",
        "--prune",
        remote_name,
        allow_failure=True,
    )
    if fetch.returncode != 0:
        raise UpdateError(f"git fetch failed for configured remote {remote_name}")
    candidate = git(repository_root, "rev-parse", upstream)
    counts = git(
        repository_root,
        "rev-list",
        "--left-right",
        "--count",
        f"{before}...{candidate}",
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
        before,
        candidate,
        allow_failure=True,
    )
    if ancestor.returncode != 0:
        raise UpdateError("checkout cannot fast-forward to its upstream")
    try:
        validations = validate_candidate(repository_root, candidate, package_name)
    except UpdateError as exc:
        raise UpdateError(
            f"candidate {candidate} validation failed before fast-forward: {exc}"
        ) from exc

    current_head = git(repository_root, "rev-parse", "HEAD")
    if current_head != before:
        raise UpdateError(f"checkout HEAD changed during candidate validation: {current_head}")
    current_branch = run(
        repository_root,
        "git",
        "symbolic-ref",
        "--quiet",
        "--short",
        "HEAD",
        allow_failure=True,
    ).stdout.strip()
    if current_branch != branch:
        raise UpdateError("checkout branch changed during candidate validation")
    current_upstream = git(
        repository_root,
        "rev-parse",
        "--abbrev-ref",
        "--symbolic-full-name",
        "@{upstream}",
    )
    if current_upstream != upstream:
        raise UpdateError("checkout upstream changed during candidate validation")
    if git(
        repository_root,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
    ):
        raise UpdateError("checkout became dirty during candidate validation")
    current_operations = operation_in_progress(repository_root)
    if current_operations:
        raise UpdateError(
            "Git operation or lock appeared during candidate validation: "
            + ", ".join(current_operations)
        )
    current_origin = git(repository_root, "remote", "get-url", remote_name)
    if current_origin != origin or not remote_matches(current_origin, remote_identity):
        raise UpdateError("checkout remote changed during candidate validation")
    current_candidate = git(repository_root, "rev-parse", upstream)
    if current_candidate != candidate:
        raise UpdateError(
            f"upstream changed during candidate validation: {candidate} -> {current_candidate}"
        )

    if behind:
        git(repository_root, "merge", "--ff-only", candidate)

    after = git(repository_root, "rev-parse", "HEAD")
    if after != candidate:
        raise UpdateError(f"post-update HEAD differs from validated candidate: {after} != {candidate}")
    final_branch = run(
        repository_root,
        "git",
        "symbolic-ref",
        "--quiet",
        "--short",
        "HEAD",
        allow_failure=True,
    ).stdout.strip()
    final_upstream = git(
        repository_root,
        "rev-parse",
        "--abbrev-ref",
        "--symbolic-full-name",
        "@{upstream}",
    )
    final_upstream_head = git(repository_root, "rev-parse", final_upstream)
    final_origin = git(repository_root, "remote", "get-url", remote_name)
    final_status = git(
        repository_root,
        "status",
        "--porcelain=v1",
        "--untracked-files=all",
    )
    final_operations = operation_in_progress(repository_root)
    if (
        final_branch != branch
        or final_upstream != upstream
        or final_upstream_head != candidate
        or final_origin != origin
        or final_status
        or final_operations
    ):
        raise UpdateError("checkout state changed during final update readback")
    return {
        "status": "updated" if before != after else "already_current",
        "lifecycle": "update-only",
        "package": package_name,
        "package_root": str(package_root),
        "repository_root": str(repository_root),
        "remote": display_remote(origin),
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
