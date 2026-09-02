#!/usr/bin/env python3
"""Validate the others-manager Skill package."""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path
import re
import sys


REQUIRED_FILES = (
    "SKILL.md",
    "agents/openai.yaml",
    "references/operations.md",
    "references/luna-task-briefs.md",
    "scripts/manage_others.py",
    "scripts/validate_package.py",
    "scripts/validate_wrapper.py",
    "tests/test_manage_others.py",
)


def validate(root: Path) -> list[str]:
    errors: list[str] = []
    if root.is_symlink() or not root.is_dir():
        return ["package root must be a real directory"]
    for relative in REQUIRED_FILES:
        path = root / relative
        if path.is_symlink() or not path.is_file():
            errors.append(f"missing real file: {relative}")

    text_files = [path for path in root.rglob("*") if path.is_file() and "__pycache__" not in path.parts]
    for path in text_files:
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        relative = path.relative_to(root)
        source_machine_prefix = "/" + "Users" + "/"
        unresolved_marker = "TO" + "DO"
        if source_machine_prefix in text:
            errors.append(f"source-machine absolute path in {relative}")
        if unresolved_marker in text:
            errors.append(f"unresolved marker in {relative}")

    skill_path = root / "SKILL.md"
    if skill_path.is_file():
        skill = skill_path.read_text(encoding="utf-8")
        match = re.match(r"\A---\n(.*?)\n---\n", skill, re.DOTALL)
        if not match:
            errors.append("SKILL.md frontmatter is missing")
        else:
            frontmatter = match.group(1)
            if not re.search(r"^name:\s*others-manager\s*$", frontmatter, re.MULTILINE):
                errors.append("SKILL.md name must be others-manager")
            description = re.search(r"^description:\s*(.+)$", frontmatter, re.MULTILINE)
            if not description or len(description.group(1).strip()) < 80:
                errors.append("SKILL.md description must explain purpose and triggers")
        for target in ("references/operations.md", "references/luna-task-briefs.md"):
            if target not in skill:
                errors.append(f"SKILL.md must route to {target}")

    yaml_path = root / "agents/openai.yaml"
    if yaml_path.is_file():
        yaml = yaml_path.read_text(encoding="utf-8")
        for required in ("display_name:", "short_description:", "default_prompt:", "$others-manager"):
            if required not in yaml:
                errors.append(f"agents/openai.yaml missing {required}")

    manager_path = root / "scripts/manage_others.py"
    if manager_path.is_file():
        source = manager_path.read_text(encoding="utf-8")
        try:
            tree = ast.parse(source, filename=str(manager_path))
        except SyntaxError as exc:
            errors.append(f"manage_others.py syntax error: {exc}")
        else:
            for node in ast.walk(tree):
                if isinstance(node, ast.keyword) and node.arg == "shell":
                    if not isinstance(node.value, ast.Constant) or node.value.value is not False:
                        errors.append("shell execution is forbidden")
                if not isinstance(node, ast.Call):
                    continue
                function_name = node.func.id if isinstance(node.func, ast.Name) else None
                list_index = 0 if function_name == "run_git" else (1 if function_name == "git_text" else None)
                if list_index is None or len(node.args) <= list_index:
                    continue
                command = node.args[list_index]
                if not isinstance(command, ast.List) or not command.elts:
                    continue
                first = command.elts[0]
                if isinstance(first, ast.Constant) and first.value in {
                    "pull",
                    "push",
                    "reset",
                    "rebase",
                    "stash",
                    "clean",
                }:
                    errors.append(f"forbidden git command in manage_others.py: {first.value}")
        if "os." + "system(" in source:
            errors.append("os.system execution is forbidden")

    return sorted(set(errors))


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("root", nargs="?", default=str(Path(__file__).resolve().parents[1]))
    args = parser.parse_args()
    root = Path(args.root).resolve(strict=True)
    errors = validate(root)
    report = {"status": "pass" if not errors else "fail", "package": str(root), "errors": errors}
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    sys.exit(main())
