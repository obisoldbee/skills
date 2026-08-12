#!/usr/bin/env python3
"""Offline, package-local validator for the public document-workspace Skill."""

from __future__ import annotations

import ast
import json
import os
import re
import stat
import sys
from pathlib import Path


REQUIRED_FILES = {
    "SKILL.md",
    "agents/openai.yaml",
    "references/operations.md",
    "references/workspace-contract.md",
    "scripts/document_workspace.py",
    "scripts/validate_package.py",
    "scripts/workspace_core.py",
    "tests/test_document_workspace.py",
    "tests/test_package.py",
}

REQUIRED_DIRECTORIES = {"agents", "references", "scripts", "tests"}
ALLOWED_SUFFIXES = {".md", ".py", ".yaml"}
TRANSIENT_NAMES = {".DS_Store", "__pycache__", ".pytest_cache", ".mypy_cache"}
IS_WINDOWS = os.name == "nt"
FORBIDDEN_FILE_PATTERNS = (
    re.compile(r"(^|/)\.env($|\.)", re.IGNORECASE),
    re.compile(r"\.(?:pem|key|p12|pfx|cer|crt)$", re.IGNORECASE),
    re.compile(r"\.(?:png|jpe?g|gif|heic|pdf|docx?|xlsx?|mp[34]|mov|wav)$", re.IGNORECASE),
)
FORBIDDEN_TEXT_PATTERNS = {
    "macOS user-home path": re.compile(r"/Users/[A-Za-z0-9._-]+/"),
    "Linux user-home path": re.compile(r"/home/[A-Za-z0-9._-]+/"),
    "Windows user-home path": re.compile(r"[A-Za-z]:\\Users\\[^\\\s]+\\", re.IGNORECASE),
    "local file URI": re.compile(r"file:/" r"/", re.IGNORECASE),
    "private IPv4 address": re.compile(
        r"(?<![0-9])(?:10\.(?:[0-9]{1,3}\.){2}[0-9]{1,3}|192\.168\.(?:[0-9]{1,3}\.)[0-9]{1,3}|172\.(?:1[6-9]|2[0-9]|3[01])\.(?:[0-9]{1,3}\.)[0-9]{1,3})(?![0-9])"
    ),
    "credential assignment": re.compile(
        r"(?im)^\s*(?:api[_-]?key|access[_-]?token|password|secret)\s*[:=]\s*[^<\s][^\n]*$"
    ),
    "unfinished placeholder": re.compile(r"\bTO" r"DO\b|\[TO" r"DO", re.IGNORECASE),
}


class ValidationError(RuntimeError):
    pass


def fail(message: str) -> None:
    raise ValidationError(message)


def is_link_like(path: Path) -> bool:
    if path.is_symlink():
        return True
    junction_check = getattr(path, "is_junction", None)
    if junction_check is None:
        if IS_WINDOWS:
            fail("Windows requires Python 3.12 or newer for fail-closed junction detection")
        return False
    return bool(junction_check())


def walk_real_files(root: Path) -> list[Path]:
    files: list[Path] = []

    def visit(directory: Path) -> None:
        try:
            entries = sorted(os.scandir(directory), key=lambda entry: (entry.name.casefold(), entry.name))
        except OSError as exc:
            fail(f"cannot scan {directory}: {exc}")
        for entry in entries:
            relative = Path(entry.path).relative_to(root).as_posix()
            if entry.name in TRANSIENT_NAMES or entry.name.endswith((".pyc", ".pyo", "~")):
                fail(f"transient file refused: {relative}")
            info = entry.stat(follow_symlinks=False)
            if entry.is_symlink() or is_link_like(Path(entry.path)):
                fail(f"linked package node refused: {relative}")
            if stat.S_ISDIR(info.st_mode):
                visit(Path(entry.path))
            elif stat.S_ISREG(info.st_mode):
                files.append(Path(entry.path))
            else:
                fail(f"unsupported package node: {relative}")

    visit(root)
    return files


def parse_skill_frontmatter(text: str) -> dict[str, str]:
    match = re.match(r"^---\n(.*?)\n---\n", text, re.DOTALL)
    if not match:
        fail("SKILL.md has invalid frontmatter delimiters")
    lines = match.group(1).splitlines()
    result: dict[str, str] = {}
    for line in lines:
        if ":" not in line:
            fail("SKILL.md frontmatter must contain simple key/value lines")
        key, value = line.split(":", 1)
        result[key.strip()] = value.strip().strip('"')
    if set(result) != {"name", "description"}:
        fail("SKILL.md frontmatter must contain only name and description")
    if result["name"] != "document-workspace":
        fail("SKILL.md name must be document-workspace")
    if not result["description"] or len(result["description"]) > 1024:
        fail("SKILL.md description is missing or too long")
    return result


def validate_openai_yaml(text: str) -> None:
    expected_prefixes = (
        "interface:\n",
        '  display_name: "文书工作区（Document Workspace）"\n',
        "  short_description: \"",
        "  default_prompt: \"",
    )
    if not text.startswith(expected_prefixes[0] + expected_prefixes[1]):
        fail("agents/openai.yaml has the wrong interface/display name")
    lines = text.splitlines()
    if len(lines) != 4 or [line.split(":", 1)[0].strip() for line in lines] != [
        "interface",
        "display_name",
        "short_description",
        "default_prompt",
    ]:
        fail("agents/openai.yaml must contain only the three requested interface fields")
    for line in lines[1:]:
        value = line.split(":", 1)[1].strip()
        if not (value.startswith('"') and value.endswith('"')):
            fail("all agents/openai.yaml strings must be quoted")
    short_description = lines[2].split(":", 1)[1].strip()[1:-1]
    if not 25 <= len(short_description) <= 64:
        fail("short_description must contain 25-64 characters")
    prompt = lines[3].split(":", 1)[1].strip()[1:-1]
    if "$document-workspace" not in prompt:
        fail("default_prompt must explicitly mention $document-workspace")


def validate_package(root_raw: str | os.PathLike[str]) -> dict[str, object]:
    root = Path(os.path.abspath(os.fspath(root_raw)))
    if is_link_like(root) or not root.is_dir():
        fail("package root must be one real directory")
    if root.name != "document-workspace":
        fail("package directory must be named document-workspace")
    for directory in REQUIRED_DIRECTORIES:
        path = root / directory
        if is_link_like(path) or not path.is_dir():
            fail(f"required real directory missing: {directory}")
    files = walk_real_files(root)
    relative_files = {path.relative_to(root).as_posix() for path in files}
    missing = sorted(REQUIRED_FILES - relative_files)
    if missing:
        fail(f"required files missing: {', '.join(missing)}")
    extra_top_level = sorted(
        path.name
        for path in root.iterdir()
        if path.name not in {"SKILL.md", *REQUIRED_DIRECTORIES}
    )
    if extra_top_level:
        fail(f"unsupported top-level package paths: {', '.join(extra_top_level)}")
    for relative in sorted(relative_files):
        if any(pattern.search(relative) for pattern in FORBIDDEN_FILE_PATTERNS):
            fail(f"public package contains unsupported artifact/credential file: {relative}")
        path = root / relative
        if path.suffix not in ALLOWED_SUFFIXES:
            fail(f"unsupported package file type: {relative}")
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeError as exc:
            fail(f"non-UTF-8 package text: {relative}: {exc}")
        for label, pattern in FORBIDDEN_TEXT_PATTERNS.items():
            if pattern.search(text):
                fail(f"{label} found in {relative}")
        if path.suffix == ".py":
            try:
                ast.parse(text, filename=relative)
            except SyntaxError as exc:
                fail(f"Python syntax error in {relative}: {exc}")
    skill_text = (root / "SKILL.md").read_text(encoding="utf-8")
    parse_skill_frontmatter(skill_text)
    validate_openai_yaml((root / "agents" / "openai.yaml").read_text(encoding="utf-8"))
    for reference in re.findall(r"\((references/[^)]+\.md)\)", skill_text):
        target = root / reference
        if is_link_like(target) or not target.is_file():
            fail(f"SKILL.md reference is missing or linked: {reference}")
    return {
        "status": "valid",
        "package": "document-workspace",
        "file_count": len(relative_files),
        "provider_calls": False,
        "network_calls": False,
        "machine_specific_paths": False,
        "linked_nodes": False,
    }


def main(argv: list[str]) -> int:
    if len(argv) != 2:
        print("Usage: python validate_package.py <document-workspace-package>", file=sys.stderr)
        return 2
    try:
        print(json.dumps(validate_package(argv[1]), ensure_ascii=False, indent=2, sort_keys=True))
        return 0
    except ValidationError as exc:
        print(f"INVALID: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main(sys.argv))
