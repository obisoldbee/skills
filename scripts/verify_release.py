#!/usr/bin/env python3
"""Verify only the repository-root files owned by the public root overlay."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
import tempfile
from pathlib import Path


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
}
MANIFEST_ROW = re.compile(r"^([0-9a-f]{64})  ([^\\]+)$")
FORBIDDEN_NAMES = {".DS_Store", "__pycache__"}
FORBIDDEN_SUFFIXES = {".pyc", ".pyo"}
FORBIDDEN_MARKERS = {
    b"/" + b"Users/": "personal-macos-path",
    b"file" + b"://": "local-file-uri",
    b"192" + b".168.": "private-network-address",
    b"BEGIN OPENSSH " + b"PRIVATE KEY": "private-key",
    b"id_" + b"ed25519": "private-key-name",
}


def root_managed_files(root: Path) -> dict[str, Path]:
    for relative in sorted(REQUIRED_ROOT_DIRECTORIES):
        required = root / relative
        if required.is_symlink():
            raise ValueError(f"required root directory must not be a symlink: {relative}")
        if not required.is_dir():
            raise ValueError(f"required root directory missing or wrong type: {relative}")
    for relative in sorted(REQUIRED_ROOT_FILES):
        required = root / relative
        if required.is_symlink():
            raise ValueError(f"required root file must not be a symlink: {relative}")
        if not required.is_file():
            raise ValueError(f"required root file missing or wrong type: {relative}")

    files: dict[str, Path] = {}
    for entry_name in sorted(ROOT_MANAGED_ENTRIES):
        entry = root / entry_name
        if not entry.exists():
            continue
        paths = [entry] if entry.is_file() else sorted(entry.rglob("*"))
        for path in paths:
            relative = path.relative_to(root).as_posix()
            if path.is_symlink():
                raise ValueError(f"symlink is not publishable: {relative}")
            if path.is_dir() and relative not in REQUIRED_ROOT_DIRECTORIES:
                raise ValueError(f"unlisted root-managed directory: {relative}")
            if path.name in FORBIDDEN_NAMES or path.suffix in FORBIDDEN_SUFFIXES:
                raise ValueError(f"transient path is not publishable: {relative}")
            if path.is_file():
                files[relative] = path
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
        for marker, label in FORBIDDEN_MARKERS.items():
            if marker in data:
                raise ValueError(f"portability violation {label}: {relative}")


def rebuild_manifest(root: Path) -> dict[str, object]:
    root = root.expanduser().resolve()
    manifest_path = root / ROOT_MANIFEST
    if not manifest_path.is_file():
        raise ValueError(f"root manifest missing: {manifest_path}")
    if manifest_path.is_symlink():
        raise ValueError(f"root manifest must not be a symlink: {manifest_path}")

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
    root = root.expanduser().resolve()
    manifest_path = root / ROOT_MANIFEST
    if not manifest_path.is_file():
        raise ValueError(f"root manifest missing: {manifest_path}")
    if manifest_path.is_symlink():
        raise ValueError(f"root manifest must not be a symlink: {manifest_path}")

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


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).parents[1])
    parser.add_argument(
        "--rebuild-root-manifest",
        action="store_true",
        help="atomically rewrite only ROOT-MANIFEST.sha256 from the exact root-managed file set",
    )
    arguments = parser.parse_args()
    try:
        if arguments.rebuild_root_manifest:
            result = rebuild_manifest(arguments.root)
        else:
            result = verify(arguments.root)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
