#!/usr/bin/env python3
"""Validate a local others-manager wrapper, source projection, and pool boundary."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import stat
import subprocess
import sys


EXPECTED_LINK = "../../GitHub/others-manager"


def is_junction(path: Path) -> bool:
    native = getattr(os.path, "isjunction", None)
    if native is not None:
        return bool(native(path))
    # Python 3.11 has no isjunction; lstat still exposes the reparse tag.
    return getattr(os.lstat(path), "st_reparse_tag", None) == getattr(
        stat, "IO_REPARSE_TAG_MOUNT_POINT", 0xA0000003)


def is_projection_link(path: Path) -> bool:
    try:
        return is_junction(path) if os.name == "nt" else path.is_symlink()
    except OSError:
        return False


def git_root(path: Path) -> Path | None:
    result = subprocess.run(
        ["git", "-C", str(path), "rev-parse", "--show-toplevel"],
        text=True,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        check=False,
    )
    if result.returncode != 0:
        return None
    return Path(result.stdout.strip()).resolve(strict=True)


def validate(wrapper: Path, package: Path, pool: Path) -> list[str]:
    errors: list[str] = []
    required_wrapper = (
        "AGENTS.md",
        "README.md",
        ".project-conventions/project.json",
        ".project-conventions/project_access.py",
        "conversation/00-initialization.md",
        "memory/MEMORY.md",
        "docs/specs/2026-08-24-others-manager-spec.md",
    )
    if wrapper.is_symlink() or is_projection_link(wrapper) or not wrapper.is_dir():
        return ["wrapper must be a real directory"]
    if (wrapper / ".git").exists() or (wrapper / ".git").is_symlink():
        errors.append("wrapper must not be a Git repository")
    for relative in required_wrapper:
        path = wrapper / relative
        if path.is_symlink() or not path.is_file():
            errors.append(f"missing wrapper file: {relative}")

    if package.is_symlink() or is_projection_link(package) or not package.is_dir() or not (package / "SKILL.md").is_file():
        errors.append("public package source is invalid")
    else:
        root = git_root(package)
        if root is None or package.parent.resolve(strict=True) != root:
            errors.append("package must be a direct child of its exact public Git root")

    projection = wrapper / "src/others-manager"
    if not is_projection_link(projection):
        errors.append("src/others-manager must be a directory junction" if os.name == "nt"
                      else "src/others-manager must be a symbolic link")
    else:
        raw = os.readlink(projection)
        if os.name != "nt" and raw != EXPECTED_LINK:
            errors.append(f"projection must use exact relative target {EXPECTED_LINK}")
        try:
            resolved = projection.resolve(strict=True)
        except OSError:
            errors.append("projection target does not resolve")
        else:
            if resolved != package.resolve(strict=True):
                errors.append("projection does not resolve to exact public package source")

    if pool.is_symlink() or is_projection_link(pool) or not pool.is_dir():
        errors.append("managed pool must be a real directory")
    elif (pool / ".git").exists() or (pool / ".git").is_symlink():
        errors.append("managed pool root must not contain .git")

    agents = wrapper / "AGENTS.md"
    if agents.is_file():
        text = agents.read_text(encoding="utf-8")
        for phrase in (
            "current user-authorized workspace integrator",
            "Delegated Luna workers may only inventory",
            "active exclusive writer capability",
            "fast-forward-only",
            "host filesystem sandbox",
        ):
            if phrase not in text:
                errors.append(f"AGENTS.md missing boundary phrase: {phrase}")
    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--wrapper", required=True)
    parser.add_argument("--package", required=True)
    parser.add_argument("--pool", required=True)
    args = parser.parse_args()
    # Keep the supplied entry's link identity for validate's boundary checks.
    wrapper = Path(args.wrapper).expanduser().absolute()
    package = Path(args.package).expanduser().absolute()
    pool = Path(args.pool).expanduser().absolute()
    errors = validate(wrapper, package, pool)
    report = {
        "status": "pass" if not errors else "fail",
        "wrapper": str(wrapper),
        "package": str(package),
        "pool": str(pool),
        "errors": errors,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
