#!/usr/bin/env python3
"""Build a root-only update overlay for the public Skill repository."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import tempfile
from pathlib import Path
from urllib.parse import urlsplit


CONTROL_ROOT = Path(__file__).resolve().parents[2]
SHARED_REPOSITORY_ROOT = CONTROL_ROOT.parent / "GitHub"
RELEASE_ROOT = CONTROL_ROOT / "release"
DEFAULT_OUTPUT = RELEASE_ROOT / "public-root-overlay"
ROOT_MANIFEST = "ROOT-MANIFEST.sha256"
EXPECTED_REMOTE_IDENTITY = "obisoldbee/skills"
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
}
REQUIRED_ROOT_DIRECTORIES = {".github", ".github/workflows", "config", "scripts"}
ROOT_MANAGED_ENTRIES = {
    ".gitattributes",
    ".github",
    ".gitignore",
    "AGENTS.md",
    "README.md",
    "config",
    "scripts",
}
FORBIDDEN_NAMES = {".DS_Store", "__pycache__"}
FORBIDDEN_SUFFIXES = {".pyc", ".pyo"}
FORBIDDEN_MARKERS = {
    b"/" + b"Users/": "personal-macos-path",
    b"C:" + b"\\Users\\": "personal-windows-path",
    b"file" + b"://": "local-file-uri",
    b"192.168.": "private-network-address",
    b"BEGIN OPENSSH PRIVATE KEY": "private-key",
    b"id_ed25519": "private-key-name",
}


class BuildError(RuntimeError):
    """Raised when the root overlay cannot be built safely."""


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


def root_managed_paths(root: Path):
    for name in sorted(ROOT_MANAGED_ENTRIES):
        entry = root / name
        linked = is_link_or_junction(entry)
        if not linked and not entry.exists():
            continue
        yield entry
        if not linked and entry.is_dir():
            yield from iter_tree_without_following_links(entry)


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
    if re.fullmatch(r"[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+", identity):
        return identity
    return None


def git_value(repository_root: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repository_root), *arguments],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        raise BuildError(
            f"shared Repository Root Git verification failed: {' '.join(arguments)}"
        )
    return result.stdout.strip()


def validate_shared_repository() -> None:
    if is_link_or_junction(SHARED_REPOSITORY_ROOT) or not SHARED_REPOSITORY_ROOT.is_dir():
        raise BuildError(
            f"shared Repository Root is missing or linked: {SHARED_REPOSITORY_ROOT}"
        )
    observed_root = Path(
        git_value(SHARED_REPOSITORY_ROOT, "rev-parse", "--show-toplevel")
    ).resolve()
    if observed_root != SHARED_REPOSITORY_ROOT.resolve():
        raise BuildError(
            f"shared Repository Root differs from Git readback: {observed_root}"
        )
    observed_remote = normalize_remote(
        git_value(SHARED_REPOSITORY_ROOT, "remote", "get-url", "origin")
    )
    if observed_remote is None or observed_remote.lower() != EXPECTED_REMOTE_IDENTITY:
        raise BuildError(
            "shared Repository Root remote differs: "
            f"expected {EXPECTED_REMOTE_IDENTITY}, observed "
            f"{observed_remote or '<unrecognized remote URL>'}"
        )


def validate_real_path_components(root: Path, child: Path) -> None:
    try:
        relative = child.relative_to(root)
    except ValueError as exc:
        raise BuildError(f"output must stay under release root: {root}") from exc
    current = root
    for part in relative.parts:
        current = current / part
        if is_link_or_junction(current):
            raise BuildError(f"output path contains a link/junction: {current}")


def validate_root_scope(root: Path) -> list[str]:
    violations: list[str] = []
    for entry in sorted(root.iterdir()):
        if entry.name not in ROOT_MANAGED_ENTRIES and entry.name != ROOT_MANIFEST:
            violations.append(f"unmanaged-top-level-entry:{entry.name}")
    return violations


def validate_exact_root_files(root: Path, label: str) -> list[str]:
    managed_paths = list(root_managed_paths(root))
    observed: set[str] = set()
    observed_directories: set[str] = set()
    for path in managed_paths:
        if is_link_or_junction(path):
            continue
        relative = path.relative_to(root).as_posix()
        if path.is_file():
            observed.add(relative)
        elif path.is_dir():
            observed_directories.add(relative)
    violations: list[str] = []
    missing = sorted(REQUIRED_ROOT_FILES - observed)
    extra = sorted(observed - REQUIRED_ROOT_FILES)
    missing_directories = sorted(REQUIRED_ROOT_DIRECTORIES - observed_directories)
    extra_directories = sorted(observed_directories - REQUIRED_ROOT_DIRECTORIES)
    if missing:
        violations.append(f"{label}:missing-root-files:{missing}")
    if extra:
        violations.append(f"{label}:extra-root-files:{extra}")
    if missing_directories:
        violations.append(f"{label}:missing-root-directories:{missing_directories}")
    if extra_directories:
        violations.append(f"{label}:extra-root-directories:{extra_directories}")
    return violations


def validate_tree(root: Path, label: str) -> list[str]:
    violations: list[str] = []
    for path in sorted(iter_tree_without_following_links(root)):
        relative = path.relative_to(root).as_posix()
        if is_link_or_junction(path):
            violations.append(f"{label}:{relative}:link-or-junction")
            continue
        if path.name in FORBIDDEN_NAMES or path.suffix in FORBIDDEN_SUFFIXES:
            violations.append(f"{label}:{relative}:transient")
            continue
        if path.is_dir():
            continue
        if not path.is_file():
            violations.append(f"{label}:{relative}:unsupported-type")
            continue
        data = path.read_bytes()
        for marker, rule in FORBIDDEN_MARKERS.items():
            if marker in data:
                violations.append(f"{label}:{relative}:{rule}")
    return violations


def validate_root_file(path: Path, label: str) -> list[str]:
    violations: list[str] = []
    if path.name in FORBIDDEN_NAMES or path.suffix in FORBIDDEN_SUFFIXES:
        violations.append(f"{label}:{path.name}:transient")
        return violations
    data = path.read_bytes()
    for marker, rule in FORBIDDEN_MARKERS.items():
        if marker in data:
            violations.append(f"{label}:{path.name}:{rule}")
    return violations


def build(output: Path) -> dict[str, object]:
    validate_shared_repository()
    source_violations: list[str] = []
    for name in sorted(ROOT_MANAGED_ENTRIES):
        source = SHARED_REPOSITORY_ROOT / name
        if not source.exists() or is_link_or_junction(source):
            source_violations.append(f"shared-repository:{name}:missing-or-linked")
        elif source.is_dir():
            source_violations.extend(validate_tree(source, f"shared-repository:{name}"))
        elif source.is_file():
            source_violations.extend(validate_root_file(source, "shared-repository"))
        else:
            source_violations.append(
                f"shared-repository:{name}:missing-or-wrong-type"
            )
    source_violations.extend(
        validate_exact_root_files(SHARED_REPOSITORY_ROOT, "shared-repository")
    )
    if source_violations:
        raise BuildError("shared repository violations:\n" + "\n".join(source_violations))

    if is_link_or_junction(RELEASE_ROOT):
        raise BuildError(f"release root must not be linked: {RELEASE_ROOT}")
    release_root = RELEASE_ROOT.absolute()
    expanded_output = output.expanduser()
    if ".." in expanded_output.parts:
        raise BuildError(f"output path contains parent traversal: {expanded_output}")
    output = expanded_output.absolute()
    try:
        relative_output = output.relative_to(release_root)
    except ValueError as exc:
        raise BuildError(f"output must stay under release root: {release_root}") from exc
    if not relative_output.parts:
        raise BuildError(f"output must be a child of release root: {release_root}")
    validate_real_path_components(release_root, output.parent)
    if output in {CONTROL_ROOT.absolute(), SHARED_REPOSITORY_ROOT.absolute()}:
        raise BuildError(f"refusing protected output: {output}")
    if output.exists() or is_link_or_junction(output):
        raise BuildError(f"output already exists: {output}")

    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(
        tempfile.mkdtemp(prefix=f".{output.name}.build-", dir=str(output.parent))
    )
    try:
        for name in sorted(ROOT_MANAGED_ENTRIES):
            source = SHARED_REPOSITORY_ROOT / name
            destination = temporary / name
            if source.is_dir():
                shutil.copytree(source, destination, copy_function=shutil.copy2)
            elif source.is_file():
                destination.parent.mkdir(parents=True, exist_ok=True)
                shutil.copy2(source, destination)
            else:
                raise BuildError(f"shared repository source type changed: {source}")
        for script in (temporary / "scripts").glob("*"):
            if script.is_file():
                script.chmod(script.stat().st_mode | 0o111)

        candidate_violations = validate_root_scope(temporary)
        candidate_violations.extend(validate_tree(temporary, "root-overlay"))
        candidate_violations.extend(
            validate_exact_root_files(temporary, "root-overlay")
        )
        if candidate_violations:
            raise BuildError("root overlay violations:\n" + "\n".join(candidate_violations))

        manifest_entries: list[tuple[str, str]] = []
        for path in sorted(iter_tree_without_following_links(temporary)):
            if not path.is_file() or path.name == ROOT_MANIFEST:
                continue
            relative = path.relative_to(temporary).as_posix()
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            manifest_entries.append((relative, digest))
        manifest = "".join(
            f"{digest}  {relative}\n" for relative, digest in manifest_entries
        )
        (temporary / ROOT_MANIFEST).write_text(manifest, encoding="utf-8")
        temporary.rename(output)
    except Exception:
        if temporary.exists():
            shutil.rmtree(temporary)
        raise

    return {
        "status": "root_overlay_built",
        "scope": "repository-root-only",
        "output": str(output),
        "files": len(manifest_entries) + 1,
        "manifest_entries": len(manifest_entries),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="new root-only output directory; it must not already exist",
    )
    arguments = parser.parse_args()
    try:
        result = build(arguments.output)
    except BuildError as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
