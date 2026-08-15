#!/usr/bin/env python3
"""Validate the portable project-handoff Skill package without network calls."""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import re
import stat
import sys


PACKAGE_NAME = "project-handoff"
EXPECTED_TOP_LEVEL = {"SKILL.md", "agents", "references", "scripts", "tests"}
EXPECTED_DIRECTORIES = {"agents", "references", "scripts", "tests", "tests/fixtures"}
REQUIRED_FILES = {
    "SKILL.md",
    "agents/openai.yaml",
    "references/internal-handoff-template.md",
    "references/legacy-handoff-template.md",
    "references/model-routing.md",
    "references/orchestration-control.md",
    "references/spark-cli-route.md",
    "references/thread-dispatch.md",
    "scripts/make_handoff.py",
    "scripts/run-spark-cli.sh",
    "scripts/validate_dispatch_route.py",
    "scripts/validate_orchestration_plan.py",
    "scripts/validate_package.py",
    "scripts/validate_visible_task_receipt.py",
    "tests/dispatch-route-cases.json",
    "tests/fixtures/internal-handoff-prompt.txt",
    "tests/orchestration-cases.json",
    "tests/routing-cases.json",
    "tests/test_skill_contract.py",
    "tests/visible-task-receipt-cases.json",
}
FORBIDDEN_NAMES = {".DS_Store", "__pycache__"}
FORBIDDEN_SUFFIXES = {".pyc", ".pyo"}
FORBIDDEN_SENSITIVE_NAMES = {
    ".env",
    "auth.json",
    "credentials.json",
    "id_ed25519",
    "id_rsa",
}
FORBIDDEN_MARKERS = {
    b"/" + b"Users/": "personal-macos-path",
    b"file" + b"://": "local-file-uri",
    b"BEGIN OPENSSH " + b"PRIVATE KEY": "private-key",
}
FORBIDDEN_PATTERNS = (
    (re.compile(b"/" + b"home/" + rb"[^/\s]+/"), "personal-linux-path"),
    (
        re.compile(b"C:" + rb"[/\\]" + b"Users" + rb"[/\\]", re.IGNORECASE),
        "personal-windows-path",
    ),
    (
        re.compile(rb"\b" + b"10" + rb"(?:\.\d{1,3}){3}\b"),
        "private-network-address",
    ),
    (
        re.compile(rb"\b" + b"172" + rb"\.(?:1[6-9]|2\d|3[01])(?:\.\d{1,3}){2}\b"),
        "private-network-address",
    ),
    (
        re.compile(rb"\b" + b"192" + rb"\.168(?:\.\d{1,3}){2}\b"),
        "private-network-address",
    ),
    (re.compile(b"AKIA" + rb"[0-9A-Z]{16}"), "access-key"),
    (re.compile(b"gh" + rb"[pousr]_[A-Za-z0-9_]{20,}"), "github-token"),
    (re.compile(b"sk" + rb"-[A-Za-z0-9]{20,}"), "api-key"),
)
TEXT_SUFFIXES = {".json", ".md", ".py", ".sh", ".txt", ".yaml", ".yml"}


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


def iter_tree(root: Path):
    pending = [root]
    while pending:
        directory = pending.pop()
        with os.scandir(directory) as scan:
            entries = sorted(scan, key=lambda entry: entry.name, reverse=True)
        for entry in entries:
            path = Path(entry.path)
            yield path
            if not is_link_or_junction(path) and entry.is_dir(follow_symlinks=False):
                pending.append(path)


def resolve_package(root: Path) -> Path:
    raw = root.expanduser().absolute()
    if is_link_or_junction(raw) or not raw.is_dir():
        raise ValueError(f"package root is missing or linked: {raw}")
    resolved = raw.resolve()
    if resolved.name != PACKAGE_NAME:
        raise ValueError(f"package directory must be named {PACKAGE_NAME}: {resolved}")
    return resolved


def parse_frontmatter(skill_text: str) -> dict[str, str]:
    if not skill_text.startswith("---\n"):
        raise ValueError("SKILL.md must start with YAML frontmatter")
    parts = skill_text.split("---", 2)
    if len(parts) != 3:
        raise ValueError("SKILL.md frontmatter is not closed")
    values: dict[str, str] = {}
    for line in parts[1].splitlines():
        if not line or line[0].isspace() or ":" not in line:
            continue
        key, value = line.split(":", 1)
        values[key.strip()] = value.strip()
    if set(values) != {"name", "description"}:
        raise ValueError(
            "SKILL.md frontmatter must contain exactly name and description"
        )
    if values["name"] != PACKAGE_NAME:
        raise ValueError(f"SKILL.md name must be {PACKAGE_NAME}")
    if not values["description"]:
        raise ValueError("SKILL.md description must not be empty")
    return values


def parse_openai_metadata(metadata: str) -> dict[str, str]:
    lines = metadata.splitlines()
    if len(lines) != 4 or lines[0] != "interface:":
        raise ValueError(
            "agents/openai.yaml must contain only interface and three fields"
        )

    fields: dict[str, str] = {}
    pattern = re.compile(r'^  (display_name|short_description|default_prompt): "([^"]+)"$')
    for line in lines[1:]:
        match = pattern.fullmatch(line)
        if match is None:
            raise ValueError(
                "agents/openai.yaml fields must be supported and double-quoted"
            )
        key, value = match.groups()
        if key in fields:
            raise ValueError(f"agents/openai.yaml repeats field: {key}")
        fields[key] = value

    expected = {"display_name", "short_description", "default_prompt"}
    if set(fields) != expected:
        raise ValueError("agents/openai.yaml interface fields are incomplete")
    if not 25 <= len(fields["short_description"]) <= 64:
        raise ValueError(
            "agents/openai.yaml short_description must be 25-64 characters"
        )
    if "$project-handoff" not in fields["default_prompt"]:
        raise ValueError(
            "agents/openai.yaml default_prompt must invoke $project-handoff"
        )
    return fields


def validate(root: Path) -> dict[str, object]:
    root = resolve_package(root)
    observed_top_level = {path.name for path in root.iterdir()}
    if observed_top_level != EXPECTED_TOP_LEVEL:
        missing = sorted(EXPECTED_TOP_LEVEL - observed_top_level)
        extra = sorted(observed_top_level - EXPECTED_TOP_LEVEL)
        raise ValueError(f"top-level entries differ: missing={missing} extra={extra}")

    files: dict[str, Path] = {}
    directories = set()
    for path in iter_tree(root):
        relative = path.relative_to(root).as_posix()
        if is_link_or_junction(path):
            raise ValueError(f"link or junction is not publishable: {relative}")
        if path.name in FORBIDDEN_NAMES or path.suffix in FORBIDDEN_SUFFIXES:
            raise ValueError(f"transient path is not publishable: {relative}")
        if (
            path.name in FORBIDDEN_SENSITIVE_NAMES
            or path.suffix.lower() in {".key", ".pem", ".p12", ".pfx"}
        ):
            raise ValueError(f"credential-shaped path is not publishable: {relative}")
        if path.is_file():
            files[relative] = path
        elif path.is_dir():
            directories.add(relative)
        else:
            raise ValueError(f"unsupported path type: {relative}")

    missing_files = sorted(REQUIRED_FILES - set(files))
    extra_files = sorted(set(files) - REQUIRED_FILES)
    if missing_files or extra_files:
        raise ValueError(
            f"package files differ: missing={missing_files} extra={extra_files}"
        )
    if directories != EXPECTED_DIRECTORIES:
        missing = sorted(EXPECTED_DIRECTORIES - directories)
        extra = sorted(directories - EXPECTED_DIRECTORIES)
        raise ValueError(f"package directories differ: missing={missing} extra={extra}")

    for relative, path in files.items():
        data = path.read_bytes()
        for marker, label in FORBIDDEN_MARKERS.items():
            if marker in data:
                raise ValueError(f"portability violation {label}: {relative}")
        for pattern, label in FORBIDDEN_PATTERNS:
            if pattern.search(data):
                raise ValueError(f"portability violation {label}: {relative}")
        if path.suffix in TEXT_SUFFIXES or path.name == "SKILL.md":
            try:
                text = data.decode("utf-8")
            except UnicodeDecodeError as exc:
                raise ValueError(f"text file is not UTF-8: {relative}") from exc
            if path.suffix == ".py":
                try:
                    compile(text, relative, "exec")
                except SyntaxError as exc:
                    raise ValueError(f"Python syntax error in {relative}: {exc}") from exc
            if path.suffix == ".json":
                try:
                    json.loads(text)
                except json.JSONDecodeError as exc:
                    raise ValueError(f"invalid JSON in {relative}: {exc}") from exc

    skill_text = files["SKILL.md"].read_text(encoding="utf-8")
    parse_frontmatter(skill_text)
    if len(skill_text.splitlines()) > 500:
        raise ValueError("SKILL.md must remain at or below 500 lines")

    metadata = files["agents/openai.yaml"].read_text(encoding="utf-8")
    parse_openai_metadata(metadata)

    for relative, path in files.items():
        if not relative.startswith("references/"):
            continue
        text = path.read_text(encoding="utf-8")
        lines = text.splitlines()
        if len(lines) > 100 and "## Contents" not in lines[:30]:
            raise ValueError(f"long reference is missing a Contents section: {relative}")

    for relative in sorted(REQUIRED_FILES):
        if relative.startswith("scripts/") and not os.access(files[relative], os.X_OK):
            raise ValueError(f"script must be executable: {relative}")

    return {
        "status": "validated",
        "package": PACKAGE_NAME,
        "root": str(root),
        "files": len(files),
        "skill_lines": len(skill_text.splitlines()),
        "provider_calls": False,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "root", nargs="?", type=Path, default=Path(__file__).resolve().parents[1]
    )
    arguments = parser.parse_args()
    try:
        result = validate(arguments.root)
    except ValueError as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
