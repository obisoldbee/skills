#!/usr/bin/env python3
"""Resolve a reviewed MiniMax-H3 upstream Skill checkout without mutating it."""

from __future__ import annotations

import argparse
import json
import os
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


def _git(repo: Path, *args: str) -> str:
    env = os.environ.copy()
    env.update(
        {
            "GIT_CONFIG_NOSYSTEM": "1",
            "GIT_CONFIG_GLOBAL": os.devnull,
            "GIT_TERMINAL_PROMPT": "0",
            "LC_ALL": "C",
        }
    )
    result = subprocess.run(
        ["git", "-C", str(repo), *args],
        check=False,
        capture_output=True,
        text=True,
        env=env,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "git command failed"
        raise RuntimeError(detail)
    return result.stdout.strip()


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


def _route_files(repo: Path, route: str) -> list[Path]:
    skills = repo / "skills"
    if route == "h3-base":
        return [
            skills / "h3-prompt-writing" / "SKILL.md",
            skills / "h3-prompt-writing" / "references" / "base-en.txt",
        ]
    if route == "h3-ref":
        return [
            skills / "h3-prompt-writing" / "SKILL.md",
            skills / "h3-prompt-writing" / "references" / "ref-en.txt",
        ]

    skill_root = skills / route
    files = [skill_root / "SKILL.cn.md"]
    references = skill_root / "references"
    if references.is_dir():
        files.extend(sorted(path for path in references.rglob("*") if path.is_file()))
    return files


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
        if _git(repo, "status", "--porcelain=v1"):
            raise RuntimeError("upstream checkout is dirty")

        sparse_paths = [line for line in _git(repo, "sparse-checkout", "list").splitlines() if line]
        if sparse_paths != ["skills"]:
            raise RuntimeError("sparse checkout must select exactly skills")

        files = _route_files(repo, route)
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
