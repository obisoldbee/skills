#!/usr/bin/env python3
"""Flatten the obsolete project-conventions/src/skills checkout without copying."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


class RepairError(RuntimeError):
    """Raised when checkout layout repair is not provably safe."""


EXPECTED_REMOTE = "https://github.com/obisoldbee/skills"


def normalize_remote(value: str) -> str:
    value = value.strip().replace("git@github.com:", "https://github.com/")
    if value.endswith(".git"):
        value = value[:-4]
    return value.rstrip("/").lower()


def git(checkout: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(checkout), *arguments],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip()
        raise RepairError(f"git {' '.join(arguments)} failed: {detail}")
    return result.stdout.replace("\r\n", "\n").rstrip("\n")


def snapshot(checkout: Path) -> dict[str, str]:
    root = Path(git(checkout, "rev-parse", "--show-toplevel")).resolve()
    if root != checkout.resolve():
        raise RepairError(f"unexpected Git worktree root: {root}")
    git_dir_value = Path(git(checkout, "rev-parse", "--git-dir"))
    git_dir = (
        git_dir_value
        if git_dir_value.is_absolute()
        else (checkout / git_dir_value).resolve()
    )
    locks = sorted(path.relative_to(git_dir).as_posix() for path in git_dir.rglob("*.lock"))
    if locks:
        raise RepairError("Git operation lock exists: " + ", ".join(locks))
    status = git(checkout, "status", "--porcelain=v1")
    if status:
        raise RepairError("obsolete checkout worktree is not clean")
    origin = git(checkout, "remote", "get-url", "origin")
    if normalize_remote(origin) != EXPECTED_REMOTE:
        raise RepairError(f"unexpected origin remote: {origin}")
    return {
        "head": git(checkout, "rev-parse", "HEAD"),
        "ref": git(checkout, "symbolic-ref", "--quiet", "--short", "HEAD"),
        "remotes": git(checkout, "remote", "-v"),
        "stashes": git(checkout, "stash", "list"),
        "status": status,
    }


def validate_layout(bootstrap_root: Path) -> tuple[Path, Path, Path]:
    if bootstrap_root.is_symlink() or not bootstrap_root.is_dir():
        raise RepairError(f"bootstrap root must be a real directory: {bootstrap_root}")
    src = bootstrap_root / "src"
    old_checkout = src / "skills"
    stage = bootstrap_root / ".src-layout-repair"
    if src.is_symlink() or not src.is_dir():
        raise RepairError(f"obsolete src directory is missing or unsafe: {src}")
    try:
        Path.cwd().resolve().relative_to(src.resolve())
    except ValueError:
        pass
    else:
        raise RepairError("run layout repair from the bootstrap root or its parent, not inside src")
    entries = sorted(path.name for path in src.iterdir())
    if entries != ["skills"]:
        raise RepairError(
            "src must contain exactly the obsolete skills checkout; observed: "
            + ", ".join(entries)
        )
    if old_checkout.is_symlink() or not old_checkout.is_dir():
        raise RepairError(f"obsolete checkout is missing or unsafe: {old_checkout}")
    if not (old_checkout / "project-conventions" / "SKILL.md").is_file():
        raise RepairError("project-conventions package is missing from obsolete checkout")
    if stage.exists() or stage.is_symlink():
        raise RepairError(f"repair staging path already exists: {stage}")
    return src, old_checkout, stage


def rollback(src: Path, stage: Path) -> None:
    if stage.is_dir() and not src.exists():
        stage.rename(src)
        return
    staged_checkout = stage / "skills"
    if stage.is_dir() and src.is_dir() and not any(stage.iterdir()):
        src.rename(staged_checkout)
        stage.rename(src)


def repair(bootstrap_root: Path, apply: bool) -> dict[str, object]:
    bootstrap_root = bootstrap_root.expanduser().resolve()
    src, old_checkout, stage = validate_layout(bootstrap_root)
    before = snapshot(old_checkout)
    if not apply:
        return {
            "status": "would_repair",
            "bootstrap_root": str(bootstrap_root),
            "old_repository_root": str(old_checkout),
            "new_repository_root": str(src),
            "head": before["head"],
        }

    try:
        src.rename(stage)
        (stage / "skills").rename(src)
        if any(stage.iterdir()):
            raise RepairError("repair staging directory is not empty after checkout move")
        stage.rmdir()
        after = snapshot(src)
        if after != before:
            raise RepairError("Git snapshot changed during layout repair")
        if not (src / "project-conventions" / "SKILL.md").is_file():
            raise RepairError("package is missing at src/project-conventions/SKILL.md")
    except Exception as exc:
        try:
            rollback(src, stage)
        except Exception as rollback_exc:
            raise RepairError(
                f"layout repair failed and rollback also failed: {exc}; {rollback_exc}"
            ) from rollback_exc
        if isinstance(exc, RepairError):
            raise
        raise RepairError(f"layout repair failed and was rolled back: {exc}") from exc

    return {
        "status": "repaired",
        "bootstrap_root": str(bootstrap_root),
        "repository_root": str(src),
        "package": str(src / "project-conventions"),
        "head": after["head"],
        "git_snapshot_preserved": True,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("bootstrap_root", type=Path)
    parser.add_argument("--apply", action="store_true")
    arguments = parser.parse_args()
    try:
        result = repair(arguments.bootstrap_root, arguments.apply)
    except (RepairError, OSError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
