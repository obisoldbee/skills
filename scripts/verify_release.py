#!/usr/bin/env python3
"""Verify the published tree against its manifest and portability boundary."""

from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path


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


def release_files(root: Path) -> dict[str, Path]:
    files: dict[str, Path] = {}
    for path in sorted(root.rglob("*")):
        relative_path = path.relative_to(root)
        if ".git" in relative_path.parts:
            continue
        relative = relative_path.as_posix()
        if path.is_symlink():
            raise ValueError(f"symlink is not publishable: {relative}")
        if path.name in FORBIDDEN_NAMES or path.suffix in FORBIDDEN_SUFFIXES:
            raise ValueError(f"transient path is not publishable: {relative}")
        if path.is_file() and relative != "MANIFEST.sha256":
            files[relative] = path
    return files


def verify(root: Path) -> dict[str, object]:
    root = root.expanduser().resolve()
    manifest_path = root / "MANIFEST.sha256"
    if not manifest_path.is_file():
        raise ValueError(f"manifest missing: {manifest_path}")

    expected = release_files(root)
    listed: dict[str, str] = {}
    for line_number, row in enumerate(
        manifest_path.read_text(encoding="utf-8").splitlines(), start=1
    ):
        match = MANIFEST_ROW.fullmatch(row)
        if not match:
            raise ValueError(f"invalid manifest row {line_number}")
        digest, relative = match.groups()
        path = Path(relative)
        if path.is_absolute() or not path.parts or ".." in path.parts:
            raise ValueError(f"unsafe manifest path: {relative}")
        if relative in listed:
            raise ValueError(f"duplicate manifest path: {relative}")
        listed[relative] = digest

    if set(listed) != set(expected):
        missing = sorted(set(expected) - set(listed))
        extra = sorted(set(listed) - set(expected))
        raise ValueError(f"manifest file set differs: missing={missing} extra={extra}")

    for relative, path in expected.items():
        data = path.read_bytes()
        observed = hashlib.sha256(data).hexdigest()
        if observed != listed[relative]:
            raise ValueError(f"digest mismatch: {relative}")
        for marker, label in FORBIDDEN_MARKERS.items():
            if marker in data:
                raise ValueError(f"portability violation {label}: {relative}")

    skill_file = root / "project-conventions" / "SKILL.md"
    if not skill_file.is_file() or "name: project-conventions" not in skill_file.read_text(
        encoding="utf-8"
    ):
        raise ValueError("project-conventions package entry is invalid")

    return {
        "status": "verified",
        "root": str(root),
        "manifest_entries": len(listed),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).parents[1])
    arguments = parser.parse_args()
    try:
        result = verify(arguments.root)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
