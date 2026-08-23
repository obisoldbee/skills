#!/usr/bin/env python3
"""Create the minimal routing overlay for one Project Collection."""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
from pathlib import Path


SAFE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
ROOT_FILES = ("AGENTS.md", "README.md", "MEMBERS.md")


class InitializationError(RuntimeError):
    """Raised when collection initialization would be unsafe."""


def is_link_or_junction(path: Path) -> bool:
    native = getattr(os.path, "isjunction", None)
    junction = False
    if native is not None:
        try:
            junction = bool(native(path))
        except OSError:
            junction = False
    elif os.name == "nt":
        try:
            observed = os.lstat(path)
            junction = getattr(observed, "st_reparse_tag", None) == getattr(
                stat, "IO_REPARSE_TAG_MOUNT_POINT", 0xA0000003
            )
        except OSError:
            junction = False
    return path.is_symlink() or junction


def target_identity(path: Path) -> tuple[int, int]:
    if is_link_or_junction(path) or not path.is_dir():
        raise InitializationError(f"target must be a real directory: {path}")
    observed = path.stat(follow_symlinks=False)
    return observed.st_dev, observed.st_ino


def validate_target_path(target: Path) -> None:
    for current in [*reversed(target.parents), target]:
        if is_link_or_junction(current):
            raise InitializationError(f"target path contains a symlink or junction: {current}")
        if current.exists():
            if not current.is_dir():
                raise InitializationError(f"target path component is not a directory: {current}")


def same_file(path: Path, receipt: tuple[int, int, int, bytes]) -> bool:
    try:
        observed = path.stat(follow_symlinks=False)
        return (
            not is_link_or_junction(path)
            and path.is_file()
            and (observed.st_dev, observed.st_ino, stat.S_IMODE(observed.st_mode), path.read_bytes())
            == receipt
        )
    except OSError:
        return False


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
    validate_target_path(target)
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
        if is_link_or_junction(path) or (path.exists() and not path.is_file()):
            raise InitializationError(f"root entry is not a regular file: {path}")
        if path.exists():
            if path.read_text(encoding="utf-8") != content:
                raise InitializationError(f"existing root file differs: {path}")
            unchanged.append(name)
        else:
            created.append(name)
    return created, unchanged


def write_exclusive(path: Path, content: str) -> tuple[int, int, int, bytes]:
    encoded = content.encode("utf-8")
    descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
    created = os.fstat(descriptor)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            if hasattr(os, "fchmod"):
                os.fchmod(handle.fileno(), 0o644)
            handle.write(encoded)
            handle.flush()
            os.fsync(handle.fileno())
            final = os.fstat(handle.fileno())
        if not hasattr(os, "fchmod"):
            os.chmod(path, 0o644)
            final = path.stat(follow_symlinks=False)
        return final.st_dev, final.st_ino, stat.S_IMODE(final.st_mode), encoded
    except Exception:
        try:
            observed = path.stat(follow_symlinks=False)
            if observed.st_dev == created.st_dev and observed.st_ino == created.st_ino:
                path.unlink()
        except OSError:
            pass
        raise


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
    target = target.expanduser()
    if ".." in target.parts:
        raise InitializationError("target path must not contain '..'")
    target = target.absolute()
    validate_target_path(target)
    expected = render_files(control_project, reserved)
    planned_target = target_identity(target) if target.exists() else None
    created, unchanged = inspect_target(target, expected)

    if apply and created:
        created_target: tuple[int, int] | None = None
        written: list[tuple[Path, tuple[int, int, int, bytes]]] = []
        try:
            if planned_target is None:
                target.mkdir()
                created_target = target_identity(target)
            elif target_identity(target) != planned_target:
                raise InitializationError("target changed after planning")
            active_target = created_target or planned_target
            for name in created:
                if target_identity(target) != active_target:
                    raise InitializationError("target changed during apply")
                path = target / name
                written.append((path, write_exclusive(path, expected[name])))
            verified_created, verified_unchanged = inspect_target(target, expected)
            if verified_created:
                raise InitializationError(
                    "post-write readback is incomplete: " + ", ".join(verified_created)
                )
            unchanged = verified_unchanged
        except Exception as exc:
            unresolved: list[str] = []
            for path, receipt in reversed(written):
                try:
                    if same_file(path, receipt):
                        path.unlink()
                    else:
                        unresolved.append(str(path))
                except OSError:
                    unresolved.append(str(path))
            if created_target is not None:
                try:
                    if target_identity(target) == created_target:
                        target.rmdir()
                    else:
                        unresolved.append(str(target))
                except OSError:
                    unresolved.append(str(target))
            if unresolved:
                raise InitializationError(
                    f"{exc}; rollback preserved changed or unrecoverable paths: "
                    + ", ".join(sorted(set(unresolved)))
                ) from exc
            raise

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
