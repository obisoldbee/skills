#!/usr/bin/env python3
"""Verify only the repository-root files owned by the public root overlay."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit


ROOT_MANIFEST = "ROOT-MANIFEST.sha256"
ROOT_MANAGED_ENTRIES = {
    ".gitattributes",
    ".github",
    ".gitignore",
    "AGENTS.md",
    "README.md",
    "config",
    "scripts",
}
REQUIRED_ROOT_DIRECTORIES = {".github", ".github/workflows", "config", "scripts"}
REQUIRED_ROOT_FILES = {
    ".gitattributes",
    ".github/workflows/verify.yml",
    ".gitignore",
    "AGENTS.md",
    "README.md",
    "config/agent-paths.tsv",
    "config/skill-exports.tsv",
    "scripts/link-macos.sh",
    "scripts/link-windows.ps1",
    "scripts/verify_release.py",
    "scripts/test_repository_refresh.py",
    "scripts/test_consumer_boundaries.py",
    "scripts/consumer_paths.py",
}
MANIFEST_ROW = re.compile(r"^([0-9a-f]{64})  ([^\\]+)$")
FORBIDDEN_NAMES = {".DS_Store", "__pycache__"}
FORBIDDEN_SUFFIXES = {".pyc", ".pyo"}
FORBIDDEN_MARKERS = {
    b"/" + b"Users/": "personal-macos-path",
    b"C:" + b"\\Users\\": "personal-windows-path",
    b"file" + b"://": "local-file-uri",
    b"192" + b".168.": "private-network-address",
    b"BEGIN OPENSSH " + b"PRIVATE KEY": "private-key",
    b"id_" + b"ed25519": "private-key-name",
}
REMOTE_IDENTITY = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
SAFE_COMPONENT = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")


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


def iter_tree_without_following_links(root: Path):
    """Yield descendants while treating links and junctions as leaf entries."""
    pending = [root]
    while pending:
        directory = pending.pop()
        with os.scandir(directory) as scan:
            entries = sorted(scan, key=lambda item: item.name, reverse=True)
        for entry in entries:
            path = Path(entry.path)
            yield path
            if not is_link_or_junction(path) and entry.is_dir(follow_symlinks=False):
                pending.append(path)


def resolve_real_root(root: Path) -> Path:
    raw_root = root.expanduser().absolute()
    if is_link_or_junction(raw_root) or not raw_root.is_dir():
        raise ValueError(f"repository root is missing or linked: {raw_root}")
    return raw_root.resolve()


def root_managed_files(root: Path) -> dict[str, Path]:
    for relative in sorted(REQUIRED_ROOT_DIRECTORIES):
        required = root / relative
        if is_link_or_junction(required):
            raise ValueError(f"required root directory must not be linked: {relative}")
        if not required.is_dir():
            raise ValueError(f"required root directory missing or wrong type: {relative}")
    for relative in sorted(REQUIRED_ROOT_FILES):
        required = root / relative
        if is_link_or_junction(required):
            raise ValueError(f"required root file must not be linked: {relative}")
        if not required.is_file():
            raise ValueError(f"required root file missing or wrong type: {relative}")

    files: dict[str, Path] = {}
    for entry_name in sorted(ROOT_MANAGED_ENTRIES):
        entry = root / entry_name
        if not entry.exists():
            continue
        paths = (
            [entry]
            if entry.is_file()
            else sorted(iter_tree_without_following_links(entry))
        )
        for path in paths:
            relative = path.relative_to(root).as_posix()
            if is_link_or_junction(path):
                raise ValueError(f"link or junction is not publishable: {relative}")
            if path.is_dir() and relative not in REQUIRED_ROOT_DIRECTORIES:
                raise ValueError(f"unlisted root-managed directory: {relative}")
            if path.name in FORBIDDEN_NAMES or path.suffix in FORBIDDEN_SUFFIXES:
                raise ValueError(f"transient path is not publishable: {relative}")
            if path.is_file():
                files[relative] = path
            elif not path.is_dir():
                raise ValueError(f"unsupported root-managed path type: {relative}")
    if set(files) != REQUIRED_ROOT_FILES:
        missing = sorted(REQUIRED_ROOT_FILES - set(files))
        extra = sorted(set(files) - REQUIRED_ROOT_FILES)
        raise ValueError(
            f"root-managed file set differs: missing={missing} extra={extra}"
        )
    return files


def validate_portability(files: dict[str, Path]) -> None:
    for relative, path in files.items():
        data = path.read_bytes()
        if b"\r" in data:
            raise ValueError(f"portability violation non-LF line ending: {relative}")
        for marker, label in FORBIDDEN_MARKERS.items():
            if marker in data:
                raise ValueError(f"portability violation {label}: {relative}")


def rebuild_manifest(root: Path) -> dict[str, object]:
    root = resolve_real_root(root)
    manifest_path = root / ROOT_MANIFEST
    if not manifest_path.is_file():
        raise ValueError(f"root manifest missing: {manifest_path}")
    if is_link_or_junction(manifest_path):
        raise ValueError(f"root manifest must not be linked: {manifest_path}")

    files = root_managed_files(root)
    validate_portability(files)
    manifest = "".join(
        f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {relative}\n"
        for relative, path in sorted(files.items())
    )
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{ROOT_MANIFEST}.", dir=str(root)
    )
    temporary = Path(temporary_name)
    manifest_mode = manifest_path.stat().st_mode
    try:
        with open(
            descriptor, "w", encoding="utf-8", newline="\n", closefd=True
        ) as handle:
            handle.write(manifest)
        temporary.chmod(manifest_mode)
        temporary.replace(manifest_path)
    finally:
        if temporary.exists():
            temporary.unlink()

    return {
        "status": "root_manifest_rebuilt",
        "scope": "repository-root-only",
        "root": str(root),
        "manifest_entries": len(files),
    }


def verify(root: Path) -> dict[str, object]:
    root = resolve_real_root(root)
    manifest_path = root / ROOT_MANIFEST
    if not manifest_path.is_file():
        raise ValueError(f"root manifest missing: {manifest_path}")
    if is_link_or_junction(manifest_path):
        raise ValueError(f"root manifest must not be linked: {manifest_path}")

    expected = root_managed_files(root)
    listed: dict[str, str] = {}
    for line_number, row in enumerate(
        manifest_path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        match = MANIFEST_ROW.fullmatch(row)
        if not match:
            raise ValueError(f"invalid root manifest row {line_number}")
        digest, relative = match.groups()
        path = Path(relative)
        if path.is_absolute() or not path.parts or ".." in path.parts:
            raise ValueError(f"unsafe root manifest path: {relative}")
        if path.parts[0] not in ROOT_MANAGED_ENTRIES:
            raise ValueError(f"member or unmanaged path in root manifest: {relative}")
        if relative in listed:
            raise ValueError(f"duplicate root manifest path: {relative}")
        listed[relative] = digest

    if not listed:
        raise ValueError("root manifest must not be empty")

    if set(listed) != set(expected):
        missing = sorted(set(expected) - set(listed))
        extra = sorted(set(listed) - set(expected))
        raise ValueError(f"root manifest file set differs: missing={missing} extra={extra}")

    validate_portability(expected)
    for relative, path in expected.items():
        data = path.read_bytes()
        observed = hashlib.sha256(data).hexdigest()
        if observed != listed[relative]:
            raise ValueError(f"digest mismatch: {relative}")

    return {
        "status": "verified",
        "scope": "repository-root-only",
        "root": str(root),
        "manifest_entries": len(listed),
    }


def run_command(
    root: Path,
    *arguments: str,
    allow_failure: bool = False,
) -> subprocess.CompletedProcess[str]:
    result = subprocess.run(
        list(arguments),
        cwd=root,
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
        raise ValueError(f"{' '.join(arguments)} failed at {root}: {detail}")
    return result


def git(root: Path, *arguments: str) -> str:
    # A read-only status must not refresh the active index on a failed candidate.
    return run_command(root, "git", "--no-optional-locks", *arguments).stdout.strip()


def safe_component(value: str, label: str) -> str:
    if not SAFE_COMPONENT.fullmatch(value) or value in {".", ".."}:
        raise ValueError(f"unsafe {label}: {value!r}")
    return value


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
    return identity if REMOTE_IDENTITY.fullmatch(identity) else None


def remote_matches(observed: str, expected: str) -> bool:
    normalized = normalize_remote(observed)
    if REMOTE_IDENTITY.fullmatch(expected):
        return normalized is not None and normalized.lower() == expected.lower()
    return observed.strip().rstrip("/") == expected.strip().rstrip("/")


def display_remote(url: str) -> str:
    if REMOTE_IDENTITY.fullmatch(url):
        return url
    return normalize_remote(url) or "<non-GitHub remote>"


def operation_markers(root: Path) -> list[str]:
    names = (
        "MERGE_HEAD",
        "CHERRY_PICK_HEAD",
        "REVERT_HEAD",
        "BISECT_LOG",
        "rebase-apply",
        "rebase-merge",
        "index.lock",
        "shallow.lock",
        "HEAD.lock",
        "packed-refs.lock",
        "sequencer",
    )
    found = []
    for name in names:
        path = Path(git(root, "rev-parse", "--git-path", name))
        if not path.is_absolute():
            path = root / path
        if os.path.lexists(path):
            found.append(name)
    return found


def _index_identity(observed) -> tuple[int, int, int, int, int]:
    """Return index metadata whose meaning agrees across path and handle stats."""
    return (
        observed.st_dev,
        observed.st_ino,
        observed.st_mode,
        observed.st_size,
        observed.st_mtime_ns,
    )


def index_state(root: Path) -> dict[str, object]:
    """Freeze the real index, including flags that porcelain status omits."""
    path = Path(git(root, "rev-parse", "--git-path", "index"))
    if not path.is_absolute():
        path = root / path

    before = path.lstat()
    if not stat.S_ISREG(before.st_mode) or is_link_or_junction(path):
        raise ValueError("checkout index is not a regular file")
    with path.open("rb") as handle:
        opened = os.fstat(handle.fileno())
        digest = hashlib.sha256(handle.read()).hexdigest()
        after = os.fstat(handle.fileno())
    # Logical entries also cover shared-index entries in split-index checkouts.
    entries = git(root, "ls-files", "-v", "--stage", "-z")
    # Windows can expose different creation/change-time semantics for path
    # stat() and fstat() on the same open file.  ctime is not
    # part of Git's index contents, so freeze the stable file identity and
    # metadata here; the byte digest and logical-entry digest below bind the
    # actual index state.
    if not (
        _index_identity(before)
        == _index_identity(opened)
        == _index_identity(after)
        == _index_identity(path.lstat())
    ):
        raise ValueError("checkout index changed while reading state")
    return {"path": str(path), "identity": _index_identity(after), "sha256": digest,
            "entries_sha256": hashlib.sha256(entries.encode("utf-8")).hexdigest()}


def repository_state(
    root: Path,
    *,
    remote_name: str,
    remote_identity: str,
    expected_ref: str,
) -> dict[str, object]:
    observed_root = Path(git(root, "rev-parse", "--show-toplevel")).resolve()
    if observed_root != root:
        raise ValueError(f"Git root differs: expected {root}, observed {observed_root}")

    branch_result = run_command(
        root,
        "git",
        "symbolic-ref",
        "--quiet",
        "--short",
        "HEAD",
        allow_failure=True,
    )
    branch = branch_result.stdout.strip()
    if branch != expected_ref:
        raise ValueError(
            f"checkout branch differs: expected {expected_ref}, observed {branch or 'detached'}"
        )
    upstream = git(
        root,
        "rev-parse",
        "--abbrev-ref",
        "--symbolic-full-name",
        "@{upstream}",
    )
    expected_upstream = f"{remote_name}/{expected_ref}"
    if upstream != expected_upstream:
        raise ValueError(
            f"checkout upstream differs: expected {expected_upstream}, observed {upstream}"
        )
    index = index_state(root)
    if git(root, "status", "--porcelain=v1", "--untracked-files=all"):
        raise ValueError("checkout is dirty; repository refresh stopped")
    markers = operation_markers(root)
    if markers:
        raise ValueError("Git operation or lock is present: " + ", ".join(markers))
    origin = git(root, "config", "--get", f"remote.{remote_name}.url")
    if not remote_matches(origin, remote_identity):
        raise ValueError(
            "checkout remote differs: "
            f"expected {display_remote(remote_identity)}, observed {display_remote(origin)}"
        )

    return {
        "head": git(root, "rev-parse", "--verify", "HEAD^{commit}"),
        "branch": branch,
        "upstream": upstream,
        "origin": origin,
        "transport": git(root, "remote", "get-url", remote_name),
        "index": index,
    }


def extract_candidate_root(root: Path, candidate: str, destination: Path) -> None:
    """Read Git objects directly: no archive attributes, checkout, links or hooks."""
    listing = git(
        root, "ls-tree", "-r", "-t", "-z", candidate, "--",
        *sorted(ROOT_MANAGED_ENTRIES | {ROOT_MANIFEST}),
    )
    entries = []
    seen = set()
    for record in listing.split("\0"):
        if not record:
            continue
        metadata, name = record.split("\t", 1)
        mode, kind, oid = metadata.split()
        relative = PurePosixPath(name)
        # Reject paths which could acquire a different meaning on Windows too.
        if (
            not relative.parts or relative.is_absolute() or relative.as_posix() != name
            or relative.parts[0] not in ROOT_MANAGED_ENTRIES | {ROOT_MANIFEST}
            or any(
                part in {".", ".."} or part.endswith((".", " "))
                or re.search(r'[\\\\:<>"|?*\x00-\x1f]', part)
                or re.fullmatch(r"(?i)(con|prn|aux|nul|com[1-9]|lpt[1-9])(?:\..*)?", part)
                for part in relative.parts
            )
            or name.casefold() in seen
        ):
            raise ValueError(f"unsafe or duplicate candidate path: {name!r}")
        if (mode, kind) not in {("040000", "tree"), ("100644", "blob"), ("100755", "blob")}:
            raise ValueError(f"linked or unsupported candidate path type: {name} ({mode} {kind})")
        seen.add(name.casefold())
        entries.append((name, mode, kind, oid))

    destination.mkdir()
    for name, mode, kind, oid in entries:
        path = destination / name
        if kind == "tree":
            path.mkdir(parents=True, exist_ok=True)
            continue
        content = subprocess.run(
            ["git", "--no-optional-locks", "cat-file", "blob", oid],
            cwd=root, capture_output=True, check=False,
        )
        if content.returncode:
            raise ValueError(f"candidate blob cannot be read: {name}")
        path.parent.mkdir(parents=True, exist_ok=True)
        with path.open("xb") as handle:
            handle.write(content.stdout)
        path.chmod(0o755 if mode == "100755" else 0o644)


def validate_candidate(root: Path, candidate: str) -> None:
    with tempfile.TemporaryDirectory(prefix="skills-root-candidate-") as raw:
        candidate_root = Path(raw) / "tree"
        extract_candidate_root(root, candidate, candidate_root)
        # Treat candidate programs as data, not an authority that can attest to
        # itself. A temporary cwd is not a sandbox: execute no candidate code.
        verify(candidate_root)


def check_candidate_landing(root: Path, before: str, candidate: str) -> None:
    """Reject local untracked/ignored entries in the whole update's write set."""
    tracked = set(git(root, "ls-tree", "-r", "--name-only", "-z", before).split("\0"))
    tracked_directories = {
        parent.as_posix() for name in tracked if name
        for parent in PurePosixPath(name).parents if parent != PurePosixPath(".")
    }
    arriving = git(root, "diff-tree", "--no-commit-id", "--name-only", "-z",
                   "--no-renames", "--diff-filter=ACMT", "-r", before, candidate)
    for name in filter(None, arriving.split("\0")):
        path = root / name
        for ancestor in path.parents:
            if ancestor == root:
                break
            relative = ancestor.relative_to(root).as_posix()
            if os.path.lexists(ancestor) and relative not in tracked:
                if is_link_or_junction(ancestor) or not ancestor.is_dir():
                    raise ValueError(f"untracked landing conflict: {relative}")
        if not os.path.lexists(path) or name in tracked:
            continue
        if name in tracked_directories and path.is_dir() and not is_link_or_junction(path):
            # A tracked directory-to-file change is safe only without local extras.
            for descendant in iter_tree_without_following_links(path):
                relative = descendant.relative_to(root).as_posix()
                if relative not in tracked and relative not in tracked_directories:
                    raise ValueError(f"untracked landing conflict: {relative}")
        else:
            raise ValueError(f"untracked landing conflict: {name}")


def refresh_repository(
    root: Path,
    *,
    update: bool,
    remote_name: str,
    remote_identity: str,
    expected_ref: str,
) -> dict[str, object]:
    root = resolve_real_root(root)
    remote_name = safe_component(remote_name, "remote name")
    expected_ref = safe_component(expected_ref, "ref")
    gate = dict(remote_name=remote_name, remote_identity=remote_identity, expected_ref=expected_ref)
    initial = repository_state(root, **gate)
    verify(root)
    before = initial["head"]
    upstream = initial["upstream"]
    if update:
        fetched = run_command(
            root,
            "git",
            "fetch",
            "--prune",
            remote_name,
            allow_failure=True,
        )
        if fetched.returncode != 0:
            raise ValueError(f"git fetch failed for configured remote {remote_name}")

    candidate = git(root, "rev-parse", "--verify", f"{upstream}^{{commit}}")
    if not re.fullmatch(r"(?:[0-9a-f]{40}|[0-9a-f]{64})", candidate):
        raise ValueError("upstream did not resolve to a full commit id")
    counts = git(
        root,
        "rev-list",
        "--left-right",
        "--count",
        f"{before}...{candidate}",
    ).split()
    if len(counts) != 2:
        raise ValueError(f"unexpected ahead/behind output: {' '.join(counts)}")
    ahead, behind = (int(counts[0]), int(counts[1]))
    if ahead:
        state = "diverged" if behind else "ahead"
        raise ValueError(
            f"checkout is {state}: ahead={ahead}, behind={behind}; no local commit was changed"
        )
    ancestor = run_command(
        root,
        "git",
        "merge-base",
        "--is-ancestor",
        before,
        candidate,
        allow_failure=True,
    )
    if ancestor.returncode != 0:
        raise ValueError("checkout cannot fast-forward to its upstream")
    if update:
        try:
            validate_candidate(root, candidate)
        except (ValueError, OSError, UnicodeError) as exc:
            raise ValueError(f"candidate {candidate} validation failed before fast-forward: {exc}") from exc
        check_candidate_landing(root, before, candidate)
        if repository_state(root, **gate) != initial:
            raise ValueError("checkout state changed during candidate validation")
        if git(root, "rev-parse", "--verify", f"{upstream}^{{commit}}") != candidate:
            raise ValueError("upstream changed during candidate validation")
        if behind:
            git(root, "merge", "--ff-only", "--no-overwrite-ignore", candidate)

    after = git(root, "rev-parse", "HEAD")
    if update:
        final = repository_state(root, **gate)
        expected_final = dict(initial, head=candidate)
        if behind:
            # A successful checkout necessarily replaces its index. No-op updates
            # must still retain the original index identity and bytes.
            expected_final["index"] = final["index"]
        if final != expected_final or after != candidate:
            raise ValueError(
                "checkout state differs from validated candidate during final readback"
            )
        if git(root, "rev-parse", "--verify", f"{upstream}^{{commit}}") != candidate:
            raise ValueError("upstream changed during final update readback")

    return {
        "status": "ready" if not update else ("updated" if before != after else "already_current"),
        "operation": "repository-device-refresh",
        "mode": "check-only" if not update else "apply",
        "repository_root": str(root),
        "remote": display_remote(initial["origin"]),
        "branch": initial["branch"],
        "upstream": upstream,
        "before": before,
        "after": after,
        "candidate": candidate,
        "ahead": ahead,
        "behind": behind if not update else 0,
        "validation": "scripts/verify_release.py",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).parents[1])
    operation = parser.add_mutually_exclusive_group()
    operation.add_argument(
        "--rebuild-root-manifest",
        action="store_true",
        help="atomically rewrite only ROOT-MANIFEST.sha256 from the exact root-managed file set",
    )
    operation.add_argument(
        "--check-repository",
        action="store_true",
        help="validate Git state and root files without fetching or writing",
    )
    operation.add_argument(
        "--update-repository",
        action="store_true",
        help="fetch, validate isolated candidate root files, then fast-forward that exact commit",
    )
    parser.add_argument("--remote", default="origin")
    parser.add_argument("--remote-identity", default="obisoldbee/skills")
    parser.add_argument("--ref", default="main")
    arguments = parser.parse_args()
    try:
        if arguments.rebuild_root_manifest:
            result = rebuild_manifest(arguments.root)
        elif arguments.check_repository or arguments.update_repository:
            result = refresh_repository(
                arguments.root,
                update=arguments.update_repository,
                remote_name=arguments.remote,
                remote_identity=arguments.remote_identity,
                expected_ref=arguments.ref,
            )
        else:
            result = verify(arguments.root)
    except (ValueError, OSError, UnicodeError) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
