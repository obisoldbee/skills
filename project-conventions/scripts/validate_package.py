#!/usr/bin/env python3
"""Offline structural and portability validation for project-conventions."""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
import sys
from pathlib import Path


REQUIRED_FILES = {
    "SKILL.md",
    "README.md",
    "agents/openai.yaml",
    "scripts/initialize_project_collection.py",
    "scripts/initialize_project_root.py",
    "scripts/initialize_skills_control_project.py",
    "scripts/inspect_projects_workspace.py",
    "scripts/project_access.py",
    "scripts/test_inspect_projects_workspace.py",
    "scripts/test_lifecycle_workflows.py",
    "scripts/test_project_root_workflows.py",
    "scripts/update_shared_checkout.py",
    "scripts/validate_package.py",
    "scripts/validate_project_root.py",
    "references/project-access.md",
    "references/project-root-initialization.md",
    "references/shared-repository.md",
}
REQUIRED_DIRECTORIES = {"agents", "assets", "references", "scripts"}
TEXT_SUFFIXES = {".json", ".md", ".ps1", ".py", ".sh", ".toml", ".tsv", ".yaml", ".yml"}
FORBIDDEN_NAMES = {".DS_Store", "__pycache__"}
FILE_URI_MARKER = "file" + "://"
PERSONAL_PATTERNS = (
    re.compile(r"/(?:Users|home)/[^/<>{}\s]+/"),
    re.compile(r"[A-Za-z]:[\\/]Users[\\/][^\\/<>{}\s]+[\\/]", re.IGNORECASE),
    re.compile(re.escape(FILE_URI_MARKER), re.IGNORECASE),
)


class ValidationError(RuntimeError):
    """Raised when the package is incomplete or not portable."""


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


def first_link_or_junction(root: Path, relative: str) -> Path | None:
    current = root
    for part in Path(relative).parts:
        current = current / part
        if is_link_or_junction(current):
            return current
    return None


def validate(package_root: Path) -> dict[str, object]:
    raw_package_root = package_root.expanduser().absolute()
    if is_link_or_junction(raw_package_root) or not raw_package_root.is_dir():
        raise ValidationError(f"package root is missing or linked: {raw_package_root}")
    package_root = raw_package_root.resolve()

    linked_required = sorted(
        relative
        for relative in REQUIRED_FILES | REQUIRED_DIRECTORIES
        if first_link_or_junction(package_root, relative) is not None
    )
    if linked_required:
        raise ValidationError(f"required package paths are linked: {linked_required}")
    missing_files = sorted(
        relative for relative in REQUIRED_FILES if not (package_root / relative).is_file()
    )
    missing_directories = sorted(
        relative for relative in REQUIRED_DIRECTORIES if not (package_root / relative).is_dir()
    )
    if missing_files or missing_directories:
        raise ValidationError(
            f"package shape incomplete: files={missing_files}, directories={missing_directories}"
        )

    skill = (package_root / "SKILL.md").read_text(encoding="utf-8")
    if not skill.startswith("---\n") or "\nname: project-conventions\n" not in skill:
        raise ValidationError("SKILL.md frontmatter or name is invalid")
    frontmatter_end = skill.find("\n---\n", 4)
    if frontmatter_end < 0 or "description:" not in skill[4:frontmatter_end]:
        raise ValidationError("SKILL.md description is missing")

    files = 0
    violations: list[str] = []
    for path in sorted(iter_tree_without_following_links(package_root)):
        relative = path.relative_to(package_root).as_posix()
        if is_link_or_junction(path):
            violations.append(f"link:{relative}")
            continue
        if path.name in FORBIDDEN_NAMES or path.suffix == ".pyc":
            violations.append(f"transient:{relative}")
            continue
        if path.is_dir():
            continue
        if not path.is_file():
            violations.append(f"unsupported-type:{relative}")
            continue
        files += 1
        if path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeError:
            violations.append(f"non-utf8:{relative}")
            continue
        if any(pattern.search(text) for pattern in PERSONAL_PATTERNS):
            violations.append(f"personal-path:{relative}")
    if violations:
        raise ValidationError("package portability violations: " + ", ".join(violations))

    return {
        "status": "valid",
        "scope": "project-conventions-package",
        "package_root": str(package_root),
        "files": files,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("package_root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    arguments = parser.parse_args()
    try:
        result = validate(arguments.package_root)
    except (ValidationError, OSError, UnicodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
