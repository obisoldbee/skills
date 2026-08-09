#!/usr/bin/env python3
"""Create the minimal routing overlay for one Project Collection."""

from __future__ import annotations

import argparse
import json
import os
import re
import tempfile
from pathlib import Path


SAFE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
ROOT_FILES = ("AGENTS.md", "README.md", "MEMBERS.md")


class InitializationError(RuntimeError):
    """Raised when collection initialization would be unsafe."""


def validate_name(value: str, label: str) -> str:
    if not SAFE_NAME.fullmatch(value) or value in {".", ".."}:
        raise InitializationError(f"unsafe {label}: {value!r}")
    return value


def render_files(control_project: str, reserved: tuple[str, ...]) -> dict[str, str]:
    reserved_text = ", ".join(f"`{name}/`" for name in reserved)
    return {
        "AGENTS.md": f"""# Project Collection

> Routing entry for related, independently governed Project Roots.

## Mandatory Rules

- This directory is a Project Collection, not a Project Root or Git repository.
- Do not initialize Git at this collection root.
- `{control_project}/` is the collection-control Project Root and owns the canonical member index.
- Keep every member's source, documents, conversation, and memory inside that member Project Root.
- Incoming member names reserved by initialization: {reserved_text}.
- Do not create, move, link, or initialize unnamed members.

## Entry Points

| Path | Purpose |
|---|---|
| `README.md` | Human overview and current initialization state |
| `MEMBERS.md` | Readable member view; regenerate from the canonical index after migration |
| `{control_project}/docs/indexes/members.md` | Canonical member index after the control project arrives |
""",
        "README.md": f"""# Project Collection

This directory groups related, independently governed Project Roots. It is a routing overlay, not a Git super-repository.

## Initialization state

- Collection root overlay: initialized
- Collection-control project: `{control_project}/` (reserved or present after migration)
- Reserved incoming member names: {reserved_text}
- Member migration and final index readback: pending until verified from disk

## Navigation

| Path | Purpose |
|---|---|
| `AGENTS.md` | Agent routing and safety rules |
| `MEMBERS.md` | Readable member view |
| `{control_project}/` | Collection-control Project Root after migration |
""",
        "MEMBERS.md": f"""# Members

The collection root has been initialized. Regenerate this view from `{control_project}/docs/indexes/members.md` only after the approved member directories have arrived and their paths have been read back from disk.
""",
    }


def inspect_target(target: Path, expected: dict[str, str]) -> tuple[list[str], list[str]]:
    if target.is_symlink():
        raise InitializationError(f"target must not be a symlink: {target}")
    if target.exists() and not target.is_dir():
        raise InitializationError(f"target is not a directory: {target}")
    if not target.parent.is_dir():
        raise InitializationError(f"target parent does not exist: {target.parent}")

    created: list[str] = []
    unchanged: list[str] = []
    if target.exists():
        allowed = set(ROOT_FILES)
        unexpected = sorted(path.name for path in target.iterdir() if path.name not in allowed)
        if unexpected:
            raise InitializationError(
                "target contains entries outside the minimal collection overlay: "
                + ", ".join(unexpected)
            )

    for name, content in expected.items():
        path = target / name
        if path.is_symlink() or (path.exists() and not path.is_file()):
            raise InitializationError(f"root entry is not a regular file: {path}")
        if path.exists():
            if path.read_text(encoding="utf-8") != content:
                raise InitializationError(f"existing root file differs: {path}")
            unchanged.append(name)
        else:
            created.append(name)
    return created, unchanged


def write_atomic(path: Path, content: str) -> None:
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "w", encoding="utf-8", newline="\n") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def initialize(
    target: Path,
    control_project: str,
    reserved_names: list[str],
    apply: bool,
) -> dict[str, object]:
    control_project = validate_name(control_project, "control-project name")
    reserved = tuple(
        sorted({validate_name(value, "reserved name") for value in reserved_names} | {control_project})
    )
    target = target.expanduser().resolve(strict=False)
    expected = render_files(control_project, reserved)
    created, unchanged = inspect_target(target, expected)

    if apply and created:
        target.mkdir(exist_ok=True)
        for name in created:
            write_atomic(target / name, expected[name])
        verified_created, verified_unchanged = inspect_target(target, expected)
        if verified_created:
            raise InitializationError(
                "post-write readback is incomplete: " + ", ".join(verified_created)
            )
        unchanged = verified_unchanged

    return {
        "status": (
            "would_initialize"
            if not apply and created
            else "initialized"
            if apply and created
            else "already_initialized"
        ),
        "target": str(target),
        "created": created if apply else [],
        "would_create": created if not apply else [],
        "verified": unchanged,
        "reserved_names": list(reserved),
        "created_member_directories": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path)
    parser.add_argument("--control-project", required=True)
    parser.add_argument("--reserve", action="append", default=[])
    parser.add_argument("--apply", action="store_true")
    arguments = parser.parse_args()
    try:
        result = initialize(
            arguments.target,
            arguments.control_project,
            arguments.reserve,
            arguments.apply,
        )
    except (InitializationError, OSError, UnicodeError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
