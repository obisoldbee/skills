#!/usr/bin/env python3
"""Validate the actual portable package, without changing or copying it."""

import argparse
import ast
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlsplit


REQUIRED = {
    "SKILL.md", "agents/openai.yaml", "references/source-packets.md",
    "references/browser-loop.md", "references/orchestration.md", "references/state-contract.md",
    "assets/review-request.md", "assets/fix-task.md", "assets/watcher-task.md",
    "scripts/next_action.py", "scripts/route_source.py", "scripts/verify_artifacts.py",
    "scripts/validate_package.py", "tests/test_review_cycle.py",
    "tests/test_source_and_artifacts.py",
    "tests/test_scheduler.py",
}


def validate(root):
    errors = []
    actual = set()
    root = root.resolve()
    if not root.is_dir():
        return ["package directory does not exist"]
    for path in sorted(root.rglob("*")):
        rel = path.relative_to(root).as_posix()
        if path.is_symlink():
            errors.append("symlink is not portable package source: " + rel)
            continue
        if path.is_dir():
            if path.name in {"__pycache__", "node_modules", ".git"}:
                errors.append("runtime/cache directory: " + rel)
            continue
        actual.add(rel)
        if rel not in REQUIRED:
            errors.append("unexpected package file: " + rel)
            continue
        try:
            body = path.read_text(encoding="utf-8")
            if not body.strip():
                errors.append("empty file: " + rel)
            if path.suffix == ".py":
                ast.parse(body, filename=rel)
            # A generic check, not a substitute for a secret review.
            if re.search(r"/(?:Users|home)/[\w.-]+/|[A-Z]:\\Users\\[\w.-]+\\", body):
                errors.append("machine-specific home path: " + rel)
            if path.suffix == ".md":
                for target in re.findall(r"\[[^\]]*\]\(([^\s)]+)\)", body):
                    if urlsplit(target).scheme or target.startswith("#"):
                        continue
                    dest = (path.parent / unquote(target.split("#", 1)[0])).resolve()
                    if not dest.is_relative_to(root) or not dest.is_file():
                        errors.append("missing or escaping document link: " + rel + " -> " + target)
        except (OSError, UnicodeError, SyntaxError) as exc:
            errors.append(rel + ": " + str(exc))
    for missing in sorted(REQUIRED - actual):
        errors.append("missing required file: " + missing)
    skill = root / "SKILL.md"
    if skill.is_file():
        body = skill.read_text(encoding="utf-8")
        if not body.startswith("---\nname: chatgpt-codex-review\ndescription:"):
            errors.append("unexpected skill metadata")
        if len(body.splitlines()) > 250:
            errors.append("move extended guidance into references: SKILL.md exceeds 250 lines")
    return errors


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1])
    args = parser.parse_args()
    errors = validate(args.root)
    print(json.dumps({"valid": not errors, "errors": errors}, ensure_ascii=False, indent=2))
    return 1 if errors else 0


if __name__ == "__main__":
    sys.exit(main())
