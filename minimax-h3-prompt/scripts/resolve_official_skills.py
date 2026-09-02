#!/usr/bin/env python3
"""Resolve a reviewed MiniMax-H3 upstream Skill checkout without mutating it."""

from __future__ import annotations

import argparse
import json
import os
import stat
import subprocess
from pathlib import Path


EXPECTED_IDENTITY = "github.com/minimax-ai/minimax-h3"
EXPECTED_HEAD = "d21241f0a4b3acbb34c97dae47fa417b7065e438"

STYLE_ROUTES = {
    "minimalist-product-ad-generator",
    "3d-animation-short-generator",
    "papercraft-stop-motion-explainer",
    "brand-promo-video-generator",
    "music-video-subtitle-generator",
    "co-op-game-intro-generator",
    "paper-collage-explainer-generator",
    "handdrawn-live-video-generator",
}

ROUTES = {"h3-base", "h3-ref", *STYLE_ROUTES}

GIT_TIMEOUT_SECONDS = 10


def _git_bytes(repo: Path, *args: str) -> bytes:
    env = os.environ.copy()
    for key in tuple(env):
        if key.startswith("GIT_"):
            env.pop(key, None)
    env.update(
        {
            "GIT_ATTR_NOSYSTEM": "1",
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_NO_LAZY_FETCH": "1",
            "GIT_NO_REPLACE_OBJECTS": "1",
            "GIT_OPTIONAL_LOCKS": "0",
            "GIT_TERMINAL_PROMPT": "0",
            "LC_ALL": "C",
        }
    )
    try:
        result = subprocess.run(
            [
                "git",
                "-c",
                "core.fsmonitor=false",
                "-c",
                "core.untrackedCache=false",
                "-c",
                f"core.hooksPath={os.devnull}",
                "-C",
                str(repo),
                *args,
            ],
            check=False,
            capture_output=True,
            env=env,
            timeout=GIT_TIMEOUT_SECONDS,
        )
    except subprocess.TimeoutExpired as exc:
        raise RuntimeError("git command timed out") from exc
    if result.returncode != 0:
        detail_bytes = result.stderr.strip() or result.stdout.strip()
        detail = detail_bytes.decode("utf-8", errors="replace") or "git command failed"
        raise RuntimeError(detail)
    return result.stdout


def _git(repo: Path, *args: str) -> str:
    return _git_bytes(repo, *args).decode("utf-8", errors="surrogateescape").strip()


def _remote_identity(remote: str) -> str:
    value = remote.strip().rstrip("/")
    if value.endswith(".git"):
        value = value[:-4]
    if value.startswith("git@github.com:"):
        value = "github.com/" + value.removeprefix("git@github.com:")
    elif value.startswith("ssh://git@github.com/"):
        value = "github.com/" + value.removeprefix("ssh://git@github.com/")
    elif value.startswith("https://github.com/"):
        value = "github.com/" + value.removeprefix("https://github.com/")
    return value.lower()


def _default_repo() -> Path:
    package_root = Path(__file__).resolve().parents[1]
    return package_root.parent.parent / "GitHub-others" / "MiniMax-H3"


def _route_root(route: str) -> str:
    if route in {"h3-base", "h3-ref"}:
        return "skills/h3-prompt-writing"
    return f"skills/{route}"


def _reviewed_tree(repo: Path, route_root: str) -> dict[str, str]:
    output = _git_bytes(
        repo,
        "ls-tree",
        "-r",
        "-z",
        "--full-tree",
        "HEAD",
        "--",
        route_root,
    )
    entries: dict[str, str] = {}
    prefix = route_root.rstrip("/") + "/"
    for record in output.split(b"\0"):
        if not record:
            continue
        try:
            header, raw_path = record.split(b"\t", 1)
            mode, object_type, object_id = header.decode("ascii").split()
        except (UnicodeDecodeError, ValueError) as exc:
            raise RuntimeError("invalid entry in reviewed Git tree") from exc
        path = os.fsdecode(raw_path)
        if not path.startswith(prefix) or "/../" in f"/{path}/":
            raise RuntimeError("reviewed Git tree contains an invalid route path")
        if object_type != "blob" or mode not in {"100644", "100755"}:
            raise RuntimeError(f"reviewed route contains a non-file entry: {path}")
        entries[path] = object_id
    if not entries:
        raise RuntimeError("reviewed route is absent from upstream HEAD")
    return entries


def _disk_tree(repo: Path, route_root: str) -> tuple[set[str], set[str]]:
    root = repo / route_root
    current = repo
    for part in Path(route_root).parts:
        current /= part
        info = current.lstat()
        if not stat.S_ISDIR(info.st_mode):
            raise RuntimeError(f"official route directory is not a plain directory: {current}")

    files: set[str] = set()
    special: set[str] = set()

    def walk(directory: Path) -> None:
        with os.scandir(directory) as children:
            for child in children:
                path = Path(child.path)
                relative = path.relative_to(repo).as_posix()
                if child.is_symlink():
                    special.add(relative)
                elif child.is_dir(follow_symlinks=False):
                    walk(path)
                elif child.is_file(follow_symlinks=False):
                    files.add(relative)
                else:
                    special.add(relative)

    walk(root)
    return files, special


def _verify_route_tree(repo: Path, route_root: str) -> dict[str, str]:
    reviewed = _reviewed_tree(repo, route_root)
    disk_files, special = _disk_tree(repo, route_root)
    reviewed_files = set(reviewed)

    if special:
        raise RuntimeError(f"official route contains a symlink or special path: {min(special)}")
    extra = disk_files - reviewed_files
    if extra:
        raise RuntimeError(f"official route contains a file absent from reviewed HEAD: {min(extra)}")
    missing = reviewed_files - disk_files
    if missing:
        raise RuntimeError(f"official route is missing a reviewed file: {min(missing)}")

    for relative, object_id in sorted(reviewed.items()):
        disk_bytes = (repo / relative).read_bytes()
        reviewed_bytes = _git_bytes(repo, "cat-file", "blob", object_id)
        if disk_bytes != reviewed_bytes:
            raise RuntimeError(f"official route file differs from reviewed HEAD: {relative}")
    return reviewed


def _route_files(repo: Path, route: str, reviewed: dict[str, str]) -> list[Path]:
    root = _route_root(route)
    if route == "h3-base":
        selected = [
            f"{root}/SKILL.md",
            f"{root}/references/base-en.txt",
        ]
    elif route == "h3-ref":
        selected = [
            f"{root}/SKILL.md",
            f"{root}/references/ref-en.txt",
        ]
    else:
        selected = [f"{root}/SKILL.cn.md"]
        selected.extend(sorted(path for path in reviewed if path.startswith(f"{root}/references/")))

    missing = [path for path in selected if path not in reviewed]
    if missing:
        raise RuntimeError(f"official route is missing a required reviewed file: {missing[0]}")
    return [repo / path for path in selected]


def resolve(
    repo: Path,
    route: str,
    *,
    expected_head: str = EXPECTED_HEAD,
) -> dict[str, object]:
    base = {
        "route": route,
        "expected_head": expected_head,
        "license_status": "NEEDS_LICENSE_CLARIFICATION",
    }
    try:
        if route not in ROUTES:
            raise RuntimeError("unsupported official Skill route")
        repo = repo.expanduser().resolve(strict=True)
        if not repo.is_dir():
            raise RuntimeError("official checkout is not a directory")

        top = Path(_git(repo, "rev-parse", "--show-toplevel")).resolve(strict=True)
        if top != repo:
            raise RuntimeError("path is not the exact Git worktree root")

        remote = _git(repo, "remote", "get-url", "origin")
        push_remote = _git(repo, "remote", "get-url", "--push", "origin")
        if _remote_identity(remote) != EXPECTED_IDENTITY:
            raise RuntimeError("origin fetch URL is not MiniMax-AI/MiniMax-H3")
        if _remote_identity(push_remote) != EXPECTED_IDENTITY:
            raise RuntimeError("origin push URL is not MiniMax-AI/MiniMax-H3")

        branch = _git(repo, "symbolic-ref", "--quiet", "--short", "HEAD")
        upstream = _git(repo, "rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}")
        head = _git(repo, "rev-parse", "HEAD")
        if branch != "main" or upstream != "origin/main":
            raise RuntimeError("checkout must be main tracking origin/main")
        if head != expected_head:
            raise RuntimeError("upstream HEAD differs from the reviewed snapshot")
        if _git(repo, "status", "--porcelain=v1", "--untracked-files=all"):
            raise RuntimeError("upstream checkout is dirty")

        sparse_paths = [line for line in _git(repo, "sparse-checkout", "list").splitlines() if line]
        if sparse_paths != ["skills"]:
            raise RuntimeError("sparse checkout must select exactly skills")

        route_root = _route_root(route)
        reviewed = _verify_route_tree(repo, route_root)
        files = _route_files(repo, route, reviewed)
        skills_root = (repo / "skills").resolve(strict=True)
        resolved_files: list[str] = []
        for path in files:
            resolved = path.resolve(strict=True)
            if not resolved.is_file() or not resolved.is_relative_to(skills_root):
                raise RuntimeError("resolved route file escapes the official skills tree")
            resolved_files.append(str(resolved))

        return {
            **base,
            "status": "available",
            "reason": None,
            "repo_root": str(repo),
            "skills_root": str(skills_root),
            "remote": remote,
            "branch": branch,
            "upstream": upstream,
            "head": head,
            "sparse_paths": sparse_paths,
            "reviewed_tree": route_root,
            "tree_verified_files": len(reviewed),
            "files": resolved_files,
        }
    except (OSError, RuntimeError) as exc:
        return {
            **base,
            "status": "unavailable",
            "reason": str(exc),
            "repo_root": str(repo),
            "files": [],
        }


def main() -> int:
    parser = argparse.ArgumentParser(
        description="Resolve files from the reviewed MiniMax-H3 official skills checkout."
    )
    parser.add_argument("--route", required=True, choices=sorted(ROUTES))
    parser.add_argument(
        "--repo",
        type=Path,
        default=None,
        help="Exact MiniMax-H3 Git worktree root; defaults to the managed collection checkout.",
    )
    args = parser.parse_args()

    result = resolve(args.repo or _default_repo(), args.route)
    print(json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
