#!/usr/bin/env python3
"""Filesystem-identity boundary checks and handle-bound Unix consumer links."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import stat
import sys


def identity(path: Path) -> tuple[int, int]:
    observed = path.stat()
    return observed.st_dev, observed.st_ino


def consumer_boundary(repo: Path) -> Path:
    parent = repo.parent
    declaration = parent / "AGENTS.md"
    control = parent / "skills/AGENTS.md"
    conventional_repo = parent / "GitHub"
    # samefile honors the actual volume's case behavior. Merely naming a
    # standalone checkout GitHub does not make its parent a collection.
    if (conventional_repo.is_dir() and repo.samefile(conventional_repo)
            and declaration.is_file() and control.is_file()):
        text = declaration.read_text(encoding="utf-8")
        if ("Project Collection" in text and "obisoldbee/skills" in text
                and "collection-control" in control.read_text(encoding="utf-8")):
            return parent
    return repo


def inspect_target(repo: Path, target: Path) -> tuple[Path, str]:
    repo = repo.resolve(strict=True)
    if not target.is_absolute():
        raise ValueError("target-must-be-absolute")
    resolved = target.resolve(strict=True)
    if not resolved.is_dir():
        raise ValueError("target-parent-missing")
    boundary = consumer_boundary(repo)
    boundary_id = identity(boundary)
    # Both sides matter: an internal outward alias is still not a consumer,
    # while an external inward alias must not hide its physical ancestry.
    for path in (target, resolved):
        for ancestor in (path, *path.parents):
            if identity(ancestor) == boundary_id:
                kind = "repository" if boundary_id == identity(repo) else "collection"
                raise ValueError(f"target-inside-{kind}: {target}")
    token = json.dumps([identity(repo), boundary_id, identity(resolved)], separators=(",", ":"))
    return resolved, token


def require_safe_create() -> None:
    if (os.name != "posix" or not hasattr(os, "O_DIRECTORY")
            or not hasattr(os, "O_NOFOLLOW")
            or os.stat not in os.supports_follow_symlinks
            or any(operation not in os.supports_dir_fd
                   for operation in (os.symlink, os.stat, os.readlink))):
        raise ValueError("safe-consumer-create-unsupported: requires Unix directory-fd symlink creation")


def create_link(repo: Path, target: Path, name: str, source: Path, expected: str) -> None:
    require_safe_create()
    if not re.fullmatch(r"[a-z0-9]+(?:-[a-z0-9]+)*", name):
        raise ValueError("invalid-skill")
    repo = repo.resolve(strict=True)
    source = source.resolve(strict=True)
    if not source.is_relative_to(repo) or source == repo or not (source / "SKILL.md").is_file():
        raise ValueError("source-outside-repository-or-invalid")
    resolved, token = inspect_target(repo, target)
    if token != expected:
        raise ValueError("consumer-target-or-boundary-changed")
    descriptor = os.open(resolved, os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW)
    try:
        opened = os.fstat(descriptor)
        parent_id = (opened.st_dev, opened.st_ino)
        if parent_id != tuple(json.loads(expected)[2]) or inspect_target(repo, target)[1] != expected:
            raise ValueError("consumer-target-or-boundary-changed")
        # symlinkat is exclusive and never treats an existing leaf as a
        # container. The fd binds creation to the verified parent even if its
        # pathname is replaced after the last check.
        os.symlink(str(source), name, dir_fd=descriptor)
        created = os.stat(name, dir_fd=descriptor, follow_symlinks=False)
        if not stat.S_ISLNK(created.st_mode) or os.readlink(name, dir_fd=descriptor) != str(source):
            raise ValueError("apply-verification-failed")
        if inspect_target(repo, target)[1] != expected:
            # Do not remove a concurrent actor's replacement or follow the new
            # path to roll back. Our link may remain in the original directory.
            raise ValueError("consumer-target-or-boundary-changed-after-create")
    finally:
        os.close(descriptor)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("operation", choices=("check", "create", "check-create-support"))
    parser.add_argument("--repository", type=Path)
    parser.add_argument("--target", type=Path)
    parser.add_argument("--name")
    parser.add_argument("--source", type=Path)
    parser.add_argument("--expected")
    args = parser.parse_args()
    try:
        if args.operation == "check-create-support":
            require_safe_create()
        elif args.repository is None or args.target is None:
            parser.error("--repository and --target are required")
        elif args.operation == "check":
            print(inspect_target(args.repository, args.target)[1])
        elif args.name is None or args.source is None or args.expected is None:
            parser.error("create requires --name, --source and --expected")
        else:
            create_link(args.repository, args.target, args.name, args.source, args.expected)
    except (OSError, ValueError, UnicodeError, RuntimeError) as exc:
        print(f"error {exc}", file=sys.stderr)
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
