#!/usr/bin/env python3
"""Deterministic, offline lifecycle primitives for document workspaces."""

from __future__ import annotations

import hashlib
import json
import os
import re
import stat
import ctypes
import errno
import sys
from contextlib import contextmanager
from contextvars import ContextVar
from datetime import datetime
from functools import wraps
from pathlib import Path, PurePosixPath, PureWindowsPath
from typing import Any, Iterable

if os.name == "posix":
    import fcntl


SCHEMA_VERSION = 1
IS_WINDOWS = os.name == "nt"

LAYOUT_DIRECTORIES = (
    "control",
    "control/sources",
    "control/artifacts",
    "raw",
    "raw/as-received",
    "work",
    "work/derived",
    "work/drafts",
    "formal",
    "formal/current",
    "archive",
    "archive/versions",
    "conversation",
    "memory",
    "memory/daily",
)

RESERVED_TOP_LEVEL = {
    "index.md",
    "control",
    "raw",
    "work",
    "formal",
    "archive",
    "conversation",
    "memory",
}

FORBIDDEN_ANYWHERE = {
    ".ds_store",
    ".git",
    ".svn",
    "__pycache__",
    "thumbs.db",
    "desktop.ini",
}

BUNDLE_DIRECTORIES = {".key", ".numbers", ".pages"}

TYPE_BY_EXTENSION = {
    ".txt": "text",
    ".md": "text",
    ".rtf": "document",
    ".json": "structured-text",
    ".jsonl": "structured-text",
    ".yaml": "structured-text",
    ".yml": "structured-text",
    ".xml": "structured-text",
    ".html": "structured-text",
    ".htm": "structured-text",
    ".doc": "document",
    ".docx": "document",
    ".odt": "document",
    ".pdf": "pdf",
    ".csv": "spreadsheet",
    ".tsv": "spreadsheet",
    ".xls": "spreadsheet",
    ".xlsx": "spreadsheet",
    ".ods": "spreadsheet",
    ".ppt": "presentation",
    ".pptx": "presentation",
    ".odp": "presentation",
    ".png": "image",
    ".jpg": "image",
    ".jpeg": "image",
    ".gif": "image",
    ".bmp": "image",
    ".tif": "image",
    ".tiff": "image",
    ".webp": "image",
    ".heic": "image",
    ".wav": "audio",
    ".mp3": "audio",
    ".m4a": "audio",
    ".aac": "audio",
    ".flac": "audio",
    ".ogg": "audio",
    ".opus": "audio",
    ".mp4": "video",
    ".mov": "video",
    ".m4v": "video",
    ".avi": "video",
    ".mkv": "video",
    ".webm": "video",
    ".srt": "transcript",
    ".vtt": "transcript",
    ".eml": "message",
    ".msg": "message",
    ".zip": "archive",
    ".7z": "archive",
    ".tar": "archive",
    ".gz": "archive",
    ".tgz": "archive",
}

SOURCE_CLASSES = {
    "chat-attachment",
    "direct-receipt",
    "local-existing",
    "photo-or-scan",
    "recording",
    "upstream-derived",
    "unknown",
}

RELIABILITY_VALUES = {"unknown", "unverified", "user-confirmed", "verified"}
ARTIFACT_KINDS = {"analysis", "asr", "draft", "ocr", "qa", "transformation"}
ARCHIVE_STATUSES = {"rejected", "superseded"}

WINDOWS_RESERVED_NAMES = {
    "con",
    "prn",
    "aux",
    "nul",
    *(f"com{index}" for index in range(1, 10)),
    *(f"lpt{index}" for index in range(1, 10)),
}

VERSION_RE = re.compile(r"^v[0-9]{3,}$")
CONVERSATION_ID_RE = re.compile(r"^[0-9]{2,}-[a-z0-9]+(?:-[a-z0-9]+)*$")
ARTIFACT_ID_RE = re.compile(r"^art-[0-9a-f]{20}$")
SOURCE_ID_RE = re.compile(r"^src-[0-9a-f]{20}$")

_ACTIVE_ROOT: ContextVar[tuple[str, int, int] | None] = ContextVar(
    "document_workspace_active_root",
    default=None,
)


class WorkspaceError(RuntimeError):
    """A visible, structured refusal with no fallback behavior."""

    def __init__(
        self,
        code: str,
        message: str,
        *,
        status: str = "refused",
        details: dict[str, Any] | None = None,
    ) -> None:
        super().__init__(message)
        self.code = code
        self.status = status
        self.details = details or {}

    def as_dict(self) -> dict[str, Any]:
        result: dict[str, Any] = {
            "status": self.status,
            "error": self.code,
            "message": str(self),
        }
        if self.details:
            result["details"] = self.details
        return result


def is_link_like(path: Path) -> bool:
    """Treat both symbolic links and Windows directory junctions as links."""
    if path.is_symlink():
        return True
    junction_check = getattr(path, "is_junction", None)
    if junction_check is None:
        if IS_WINDOWS:
            raise WorkspaceError(
                "unsupported_runtime",
                "Windows requires Python 3.12 or newer for fail-closed junction detection.",
            )
        return False
    return bool(junction_check())


def canonical_json_bytes(value: Any) -> bytes:
    return (
        json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    ).encode("utf-8")


def compact_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value, ensure_ascii=False, separators=(",", ":"), sort_keys=True
    ).encode("utf-8")


def plan_with_token(plan: dict[str, Any]) -> dict[str, Any]:
    result = dict(plan)
    result.pop("plan_token", None)
    workspace = result.get("workspace")
    if isinstance(workspace, str):
        state = inventory_tree(validate_exact_directory(workspace))
        result["workspace_state_sha256"] = hashlib.sha256(
            compact_json_bytes(state)
        ).hexdigest()
    result["plan_token"] = hashlib.sha256(compact_json_bytes(result)).hexdigest()
    return result


def require_plan_token(plan: dict[str, Any], supplied: str | None) -> str:
    expected = plan_with_token(plan)["plan_token"]
    if not supplied:
        raise WorkspaceError(
            "plan_token_required",
            "Apply requires the exact plan_token from a prior dry-run.",
        )
    if supplied != expected:
        raise WorkspaceError(
            "stale_or_mismatched_plan",
            "The workspace or requested operation changed after the dry-run.",
            details={"expected_plan_token": expected},
        )
    return expected


def normalize_timestamp(raw: str, *, allow_unknown: bool = False) -> str:
    if raw == "unknown":
        if allow_unknown:
            return raw
        raise WorkspaceError(
            "timestamp_required",
            "This mutation needs a known timezone-aware timestamp.",
        )
    candidate = raw[:-1] + "+00:00" if raw.endswith("Z") else raw
    try:
        parsed = datetime.fromisoformat(candidate)
    except ValueError as exc:
        raise WorkspaceError(
            "invalid_timestamp",
            "Use an ISO 8601 timestamp with a timezone, such as 2030-01-02T03:04:05Z.",
        ) from exc
    if parsed.tzinfo is None:
        raise WorkspaceError(
            "invalid_timestamp",
            "The timestamp must include Z or an explicit UTC offset.",
        )
    normalized = parsed.isoformat(timespec="seconds")
    if normalized.endswith("+00:00"):
        normalized = normalized[:-6] + "Z"
    return normalized


def validate_portable_component(component: str) -> None:
    if not component or component in {".", ".."}:
        raise WorkspaceError("unsafe_path", "Relative paths cannot contain empty or dot components.")
    if any(ord(character) < 32 for character in component):
        raise WorkspaceError("nonportable_name", f"Control characters are not portable: {component!r}")
    if any(character in '<>:"/\\|?*' for character in component):
        raise WorkspaceError("nonportable_name", f"Unsupported portable filename: {component!r}")
    if component.endswith((" ", ".")):
        raise WorkspaceError("nonportable_name", f"Trailing spaces or dots are not portable: {component!r}")
    if component.split(".", 1)[0].casefold() in WINDOWS_RESERVED_NAMES:
        raise WorkspaceError("nonportable_name", f"Reserved Windows filename: {component!r}")


def normalize_relative_path(raw: str) -> str:
    if not isinstance(raw, str) or not raw.strip():
        raise WorkspaceError("unsafe_path", "A non-empty relative path is required.")
    candidate = raw.replace("\\", "/")
    windows = PureWindowsPath(raw)
    if windows.drive or windows.root:
        raise WorkspaceError("path_escape", f"Absolute or drive-qualified path refused: {raw!r}")
    pure = PurePosixPath(candidate)
    if pure.is_absolute() or any(part == ".." for part in pure.parts):
        raise WorkspaceError("path_escape", f"Path escapes the selected workspace: {raw!r}")
    parts = [part for part in pure.parts if part != "."]
    if not parts:
        raise WorkspaceError("unsafe_path", "A file path, not the workspace root, is required.")
    for part in parts:
        validate_portable_component(part)
    return PurePosixPath(*parts).as_posix()


def _absolute_without_resolving(raw: os.PathLike[str] | str) -> Path:
    return Path(os.path.abspath(os.fspath(raw)))


def _iter_absolute_components(path: Path) -> Iterable[Path]:
    current = Path(path.anchor)
    yield current
    for part in path.parts[1:]:
        current = current / part
        yield current


def validate_exact_directory(
    raw: os.PathLike[str] | str,
    *,
    allow_missing_leaf: bool = False,
) -> Path:
    path = _absolute_without_resolving(raw)
    components = list(_iter_absolute_components(path))
    for index, component in enumerate(components):
        leaf = index == len(components) - 1
        try:
            info = component.lstat()
        except FileNotFoundError:
            if allow_missing_leaf and leaf:
                parent = component.parent
                if not parent.is_dir() or is_link_like(parent):
                    raise WorkspaceError(
                        "invalid_workspace_parent",
                        "The exact workspace parent must be an existing real directory.",
                    )
                return path
            raise WorkspaceError("workspace_missing", f"Selected workspace does not exist: {path}")
        if stat.S_ISLNK(info.st_mode) or is_link_like(component):
            raise WorkspaceError(
                "linked_path_refused",
                f"Linked path components are outside the write boundary: {component}",
            )
        if not leaf and not stat.S_ISDIR(info.st_mode):
            raise WorkspaceError("invalid_path", f"Non-directory path component: {component}")
        if leaf and not stat.S_ISDIR(info.st_mode):
            raise WorkspaceError("workspace_not_directory", f"Selected workspace is not a directory: {path}")
    return path


def path_in_workspace(root: Path, relative: str) -> Path:
    normalized = normalize_relative_path(relative)
    candidate = root.joinpath(*PurePosixPath(normalized).parts)
    if os.path.commonpath((os.fspath(root), os.fspath(candidate))) != os.fspath(root):
        raise WorkspaceError("path_escape", f"Path escapes the selected workspace: {relative!r}")
    current = root
    for part in PurePosixPath(normalized).parts[:-1]:
        current = current / part
        if current.exists() or is_link_like(current):
            info = current.lstat()
            if stat.S_ISLNK(info.st_mode) or is_link_like(current):
                raise WorkspaceError("linked_path_refused", f"Linked intermediate refused: {current}")
            if not stat.S_ISDIR(info.st_mode):
                raise WorkspaceError("invalid_path", f"Non-directory intermediate: {current}")
    return candidate


def classify_file(path_or_relative: os.PathLike[str] | str) -> str:
    suffix = Path(path_or_relative).suffix.casefold()
    result = TYPE_BY_EXTENSION.get(suffix)
    if result is None:
        raise WorkspaceError(
            "unsupported_file_type",
            f"Unsupported file extension {suffix or '<none>'!r}; preserve the conflict and choose an explicit conversion or scope.",
        )
    return result


def _check_readable_mode(info: os.stat_result, path: Path) -> None:
    if info.st_mode & 0o444 == 0:
        raise WorkspaceError("unreadable_file", f"Readable source bytes are required: {path}")


def hash_regular_file(path: Path) -> tuple[int, str]:
    try:
        before = path.lstat()
    except FileNotFoundError as exc:
        raise WorkspaceError("missing_file", f"File is missing: {path}") from exc
    if stat.S_ISLNK(before.st_mode) or is_link_like(path):
        raise WorkspaceError("linked_path_refused", f"Linked files are refused: {path}")
    if not stat.S_ISREG(before.st_mode):
        raise WorkspaceError("unsupported_node", f"Only regular files are supported: {path}")
    _check_readable_mode(before, path)
    digest = hashlib.sha256()
    size = 0
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags)
        with os.fdopen(descriptor, "rb", closefd=True) as handle:
            opened = os.fstat(handle.fileno())
            if not stat.S_ISREG(opened.st_mode):
                raise WorkspaceError("unsupported_node", f"Only regular files are supported: {path}")
            if (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino):
                raise WorkspaceError("source_changed", f"Source changed while it was opened: {path}")
            while True:
                block = handle.read(1024 * 1024)
                if not block:
                    break
                digest.update(block)
                size += len(block)
    except OSError as exc:
        raise WorkspaceError("unreadable_file", f"Cannot read source bytes: {path}") from exc
    after = path.lstat()
    if (after.st_dev, after.st_ino, after.st_size, after.st_mtime_ns) != (
        before.st_dev,
        before.st_ino,
        before.st_size,
        before.st_mtime_ns,
    ):
        raise WorkspaceError("source_changed", f"Source changed during hashing: {path}")
    if size != before.st_size:
        raise WorkspaceError("source_changed", f"Source size changed during hashing: {path}")
    return size, digest.hexdigest()


def _check_directory_entries(entries: list[os.DirEntry[str]], directory: Path) -> None:
    seen: dict[str, str] = {}
    for entry in entries:
        validate_portable_component(entry.name)
        folded = entry.name.casefold()
        if folded in seen and seen[folded] != entry.name:
            raise WorkspaceError(
                "case_collision",
                f"Case-only filename collision is not portable in {directory}: {seen[folded]!r}, {entry.name!r}",
            )
        seen[folded] = entry.name
        if folded in FORBIDDEN_ANYWHERE:
            raise WorkspaceError("transient_or_control_path", f"Unsupported transient/control path: {directory / entry.name}")


def inventory_tree(root: Path) -> list[dict[str, Any]]:
    root = validate_exact_directory(root)
    records: list[dict[str, Any]] = []

    def visit(directory: Path, relative_directory: PurePosixPath) -> None:
        try:
            with os.scandir(directory) as iterator:
                entries = sorted(list(iterator), key=lambda item: (item.name.casefold(), item.name))
        except OSError as exc:
            raise WorkspaceError("unreadable_directory", f"Cannot inventory directory: {directory}") from exc
        _check_directory_entries(entries, directory)
        for entry in entries:
            relative = relative_directory / entry.name
            relative_text = relative.as_posix()
            info = entry.stat(follow_symlinks=False)
            if entry.is_symlink() or is_link_like(Path(entry.path)):
                raise WorkspaceError("linked_path_refused", f"Links are refused: {relative_text}")
            if stat.S_ISDIR(info.st_mode):
                if Path(entry.name).suffix.casefold() in BUNDLE_DIRECTORIES:
                    raise WorkspaceError(
                        "unsupported_file_type",
                        f"Package-style document directories need an explicit conversion: {relative_text}",
                    )
                if info.st_mode & 0o555 == 0:
                    raise WorkspaceError("unreadable_directory", f"Unreadable directory: {relative_text}")
                records.append({"node": "directory", "path": relative_text})
                visit(Path(entry.path), relative)
            elif stat.S_ISREG(info.st_mode):
                type_class = classify_file(relative_text)
                size, sha256 = hash_regular_file(Path(entry.path))
                records.append(
                    {
                        "node": "file",
                        "path": relative_text,
                        "type_class": type_class,
                        "byte_size": size,
                        "sha256": sha256,
                    }
                )
            else:
                raise WorkspaceError("unsupported_node", f"Unsupported filesystem node: {relative_text}")

    visit(root, PurePosixPath())
    return records


def inventory_report(root_raw: os.PathLike[str] | str) -> dict[str, Any]:
    root = validate_exact_directory(root_raw)
    entries = inventory_tree(root)
    return {
        "status": "inventoried",
        "workspace": os.fspath(root),
        "entry_count": len(entries),
        "entries": entries,
        "semantic_content_read": False,
        "byte_hashing_performed": True,
        "provider_calls": False,
    }


def _source_identifier(identity: dict[str, Any]) -> str:
    return "src-" + hashlib.sha256(compact_json_bytes(identity)).hexdigest()[:20]


def _artifact_identifier(identity: dict[str, Any]) -> str:
    return "art-" + hashlib.sha256(compact_json_bytes(identity)).hexdigest()[:20]


def _source_record_identity(record: dict[str, Any]) -> dict[str, Any]:
    return {
        key: record[key]
        for key in (
            "original_relative_path",
            "type_class",
            "source_class",
            "source_mode",
            "byte_size",
            "sha256",
            "received_at",
            "event_at",
            "imported_at",
            "reliability",
            "derivation_links",
            "status",
        )
    }


def _artifact_record_identity(record: dict[str, Any]) -> dict[str, Any]:
    return {
        key: record[key]
        for key in (
            "kind",
            "current_relative_path",
            "type_class",
            "byte_size",
            "sha256",
            "created_at",
            "reliability",
            "derivation_links",
            "status",
        )
    }


def _new_source_record(
    *,
    original_relative_path: str,
    current_relative_path: str,
    type_class: str,
    source_class: str,
    byte_size: int,
    sha256: str,
    received_at: str,
    event_at: str,
    imported_at: str,
    reliability: str,
    derivation_links: list[str],
    source_mode: str,
) -> dict[str, Any]:
    record = {
        "schema_version": SCHEMA_VERSION,
        "original_relative_path": original_relative_path,
        "current_relative_path": current_relative_path,
        "type_class": type_class,
        "source_class": source_class,
        "source_mode": source_mode,
        "byte_size": byte_size,
        "sha256": sha256,
        "received_at": received_at,
        "event_at": event_at,
        "imported_at": imported_at,
        "reliability": reliability,
        "derivation_links": derivation_links,
        "status": "preserved",
    }
    record["source_id"] = _source_identifier(_source_record_identity(record))
    return record


def _workspace_index(timestamp: str) -> bytes:
    return f"""# Document Workspace

Initialized: {timestamp}

| Path | Role |
|---|---|
| `control/` | Machine-readable provenance, artifact, and current-version records |
| `raw/as-received/` | Immutable byte-preserved received inputs; not a truth claim |
| `work/derived/` | Rebuildable OCR, ASR, analysis, transformations, and QA artifacts |
| `work/drafts/` | Revisable deliverable drafts; never implicitly approved |
| `formal/current/` | The one explicitly approved current formal version |
| `archive/versions/` | Rejected and superseded versions with complete records |
| `conversation/` | Agent proposals, user corrections, reasons, and decisions |
| `memory/daily/` | Dated work logs |
| `memory/MEMORY.md` | Curated reusable lessons without copied source content |

Initialization is local and structural. Byte hashing is used for integrity; no semantic
content reading, playback, OCR, ASR, provider call, or external upload is authorized here.
""".encode("utf-8")


def _workspace_record(timestamp: str, mode: str) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "workspace_kind": "document-workspace",
        "selection": "exact-root",
        "initialized_at": timestamp,
        "initialization_mode": mode,
        "raw_semantics": "byte-preserved-as-received-not-truth",
        "content_access": "byte-level-integrity-only",
        "provider_calls": False,
        "layout": {
            "navigation": "INDEX.md",
            "control": "control",
            "raw": "raw/as-received",
            "derived": "work/derived",
            "drafts": "work/drafts",
            "current_formal": "formal/current",
            "version_archive": "archive/versions",
            "conversation": "conversation",
            "daily_memory": "memory/daily",
            "curated_memory": "memory/MEMORY.md",
        },
    }


def empty_current_record() -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "none",
        "version_id": "unknown",
        "decided_at": "unknown",
        "conversation_record": "unknown",
        "conversation_sha256": "unknown",
        "outputs": [],
    }


def _initial_conversation(timestamp: str) -> bytes:
    date = timestamp[:10]
    return f"""# 00 Workspace Decision

> Date: {date}
> Status: incomplete

## Agent original proposal

unknown

## User corrections

unknown

## Rejection or modification reasons

unknown

## Final decision

unknown

Complete this record, or create a later complete conversation record with the CLI,
before approving or archiving a version.
""".encode("utf-8")


def _initial_daily_memory(timestamp: str, mode: str) -> bytes:
    return f"""# {timestamp[:10]}

- Time: {timestamp}
- Action: initialized document workspace
- Mode: {mode}
- Semantic content read: false
- Provider calls: false
- Follow-up: record work decisions and unresolved facts without copying source content.
""".encode("utf-8")


def _initial_curated_memory() -> bytes:
    return b"""# Curated Memory

- Keep only reusable decisions, constraints, and lessons.
- Link to source and conversation records instead of copying sensitive source content.
- Preserve unknown facts as `unknown`; do not turn inference into evidence.
"""


def _initial_file_map(timestamp: str, mode: str) -> dict[str, bytes]:
    return {
        "INDEX.md": _workspace_index(timestamp),
        "control/workspace.json": canonical_json_bytes(_workspace_record(timestamp, mode)),
        "control/current.json": canonical_json_bytes(empty_current_record()),
        "conversation/00-workspace-decision.md": _initial_conversation(timestamp),
        f"memory/daily/{timestamp[:10]}.md": _initial_daily_memory(timestamp, mode),
        "memory/MEMORY.md": _initial_curated_memory(),
    }


def _top_level_collisions(entries: list[dict[str, Any]]) -> list[str]:
    collisions = []
    for entry in entries:
        top = PurePosixPath(entry["path"]).parts[0]
        if top.casefold() in RESERVED_TOP_LEVEL:
            collisions.append(entry["path"])
    return sorted(set(collisions), key=lambda value: (value.casefold(), value))


def plan_initialize(
    root_raw: os.PathLike[str] | str,
    *,
    timestamp: str,
    upstream_derived: Iterable[str] = (),
) -> dict[str, Any]:
    timestamp = normalize_timestamp(timestamp)
    root = validate_exact_directory(root_raw)
    upstream_paths = sorted(
        {normalize_relative_path(path) for path in upstream_derived},
        key=lambda value: (value.casefold(), value),
    )
    workspace_record = root / "control" / "workspace.json"
    if workspace_record.exists() or is_link_like(workspace_record):
        validation = validate_workspace(root)
        return {
            "operation": "initialize",
            "status": "already_initialized",
            "workspace": os.fspath(root),
            "timestamp": timestamp,
            "requested_upstream_derived": upstream_paths,
            "actions": [],
            "validation_summary": validation["summary"],
        }

    entries = inventory_tree(root)
    collisions = _top_level_collisions(entries)
    if collisions:
        raise WorkspaceError(
            "reserved_path_collision",
            "Existing paths collide with the managed workspace layout; select a nested work package or preserve the collision for review.",
            details={"paths": collisions},
        )
    mode = "empty" if not entries else "adopt-populated"
    files = [entry for entry in entries if entry["node"] == "file"]
    file_by_path = {entry["path"]: entry for entry in files}
    missing_classifications = [path for path in upstream_paths if path not in file_by_path]
    if missing_classifications:
        raise WorkspaceError(
            "classification_target_missing",
            "Every upstream-derived classification must identify one inventoried regular file.",
            details={"paths": missing_classifications},
        )

    source_records: list[dict[str, Any]] = []
    for entry in files:
        original = entry["path"]
        current = f"raw/as-received/adopted/{original}"
        upstream = original in upstream_paths
        record = _new_source_record(
            original_relative_path=original,
            current_relative_path=current,
            type_class=entry["type_class"],
            source_class="upstream-derived" if upstream else "local-existing",
            byte_size=entry["byte_size"],
            sha256=entry["sha256"],
            received_at="unknown",
            event_at="unknown",
            imported_at=timestamp,
            reliability="unverified" if upstream else "unknown",
            derivation_links=["unknown"] if upstream else [],
            source_mode="adopted",
        )
        source_records.append(record)

    actions: list[dict[str, Any]] = [
        {"action": "create_directory", "path": relative}
        for relative in LAYOUT_DIRECTORIES
    ]
    actions.extend(
        {"action": "write_control", "path": relative, "sha256": hashlib.sha256(content).hexdigest()}
        for relative, content in sorted(_initial_file_map(timestamp, mode).items())
    )
    for record in source_records:
        actions.append(
            {
                "action": "copy_preserved_source",
                "from": record["original_relative_path"],
                "to": record["current_relative_path"],
                "sha256": record["sha256"],
            }
        )
        actions.append(
            {
                "action": "write_source_record",
                "path": f"control/sources/{record['source_id']}.json",
                "sha256": hashlib.sha256(canonical_json_bytes(record)).hexdigest(),
            }
        )

    return {
        "operation": "initialize",
        "status": "would_initialize" if mode == "empty" else "would_adopt",
        "workspace": os.fspath(root),
        "timestamp": timestamp,
        "requested_upstream_derived": upstream_paths,
        "mode": mode,
        "inventory": {
            "entry_count": len(entries),
            "file_count": len(files),
            "semantic_content_read": False,
            "byte_hashing_performed": True,
        },
        "source_records": source_records,
        "actions": actions,
        "provider_calls": False,
    }


def _require_secure_mutation_runtime() -> None:
    required = ("O_DIRECTORY", "O_NOFOLLOW")
    if os.name != "posix" or any(not hasattr(os, name) for name in required):
        raise WorkspaceError(
            "unsupported_mutation_runtime",
            "Apply requires POSIX directory descriptors, no-follow opens, and advisory locking; dry-run and validation remain available.",
        )
    if sys.platform != "darwin" and not sys.platform.startswith("linux"):
        raise WorkspaceError(
            "unsupported_mutation_runtime",
            "Apply requires Darwin guarded opens or Linux openat2; dry-run and validation remain available.",
        )


def _directory_open_flags() -> int:
    _require_secure_mutation_runtime()
    return os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW


class _OpenHow(ctypes.Structure):
    _fields_ = [
        ("flags", ctypes.c_ulonglong),
        ("mode", ctypes.c_ulonglong),
        ("resolve", ctypes.c_ulonglong),
    ]


def _guarded_open_beneath(
    root_descriptor: int,
    relative: str,
    flags: int,
    *,
    mode: int = 0o600,
) -> int:
    """Open one root-relative path with kernel-enforced no-link containment."""
    normalized = normalize_relative_path(relative)
    try:
        if sys.platform == "darwin":
            nofollow_any = getattr(os, "O_NOFOLLOW_ANY", None)
            if nofollow_any is None:
                raise WorkspaceError(
                    "unsupported_mutation_runtime",
                    "This Darwin runtime lacks O_NOFOLLOW_ANY.",
                )
            return os.open(
                normalized,
                flags | nofollow_any | 0x00001000,
                mode,
                dir_fd=root_descriptor,
            )
        if sys.platform.startswith("linux"):
            libc = ctypes.CDLL(None, use_errno=True)
            syscall = getattr(libc, "syscall", None)
            if syscall is None:
                raise WorkspaceError(
                    "unsupported_mutation_runtime",
                    "This Linux runtime lacks the openat2 syscall entry point.",
                )
            how = _OpenHow(
                flags=flags,
                mode=mode if flags & os.O_CREAT else 0,
                resolve=0x02 | 0x04 | 0x08,
            )
            result = syscall(
                437,
                root_descriptor,
                os.fsencode(normalized),
                ctypes.byref(how),
                ctypes.sizeof(how),
            )
            if result < 0:
                error = ctypes.get_errno()
                if error in {errno.ENOSYS, errno.EINVAL}:
                    raise WorkspaceError(
                        "unsupported_mutation_runtime",
                        "This Linux kernel does not provide the required openat2 containment.",
                    )
                raise OSError(error, os.strerror(error), normalized)
            return int(result)
    except OSError as exc:
        if exc.errno in {errno.ELOOP, errno.EXDEV}:
            raise WorkspaceError(
                "linked_path_refused",
                f"A link or root escape appeared during apply: {normalized}",
            ) from exc
        raise
    raise WorkspaceError(
        "unsupported_mutation_runtime",
        "No guarded root-relative open implementation is available.",
    )


def _root_descriptor(root: Path) -> int:
    before = root.lstat()
    try:
        descriptor = os.open(root, _directory_open_flags())
    except OSError as exc:
        raise WorkspaceError("workspace_boundary_changed", f"Cannot anchor the exact workspace root: {root}") from exc
    opened = os.fstat(descriptor)
    if not stat.S_ISDIR(opened.st_mode) or (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino):
        os.close(descriptor)
        raise WorkspaceError("workspace_boundary_changed", f"Workspace root changed while it was being anchored: {root}")
    active = _ACTIVE_ROOT.get()
    identity = (os.fspath(root), opened.st_dev, opened.st_ino)
    if active is not None and identity != active:
        os.close(descriptor)
        raise WorkspaceError("workspace_boundary_changed", "The locked exact workspace root was replaced during apply.")
    return descriptor


@contextmanager
def _workspace_mutation_lock(root: Path):
    """Serialize package writers and keep the exact root inode anchored."""
    descriptor = _root_descriptor(root)
    opened = os.fstat(descriptor)
    token = None
    try:
        try:
            fcntl.flock(descriptor, fcntl.LOCK_EX | fcntl.LOCK_NB)
        except OSError as exc:
            raise WorkspaceError("workspace_busy", "Another mutation already holds the exact workspace lock.") from exc
        token = _ACTIVE_ROOT.set((os.fspath(root), opened.st_dev, opened.st_ino))
        yield
        after = root.lstat()
        if is_link_like(root) or (after.st_dev, after.st_ino) != (opened.st_dev, opened.st_ino):
            raise WorkspaceError("workspace_boundary_changed", "The exact workspace root changed during apply.")
    finally:
        if token is not None:
            _ACTIVE_ROOT.reset(token)
        try:
            fcntl.flock(descriptor, fcntl.LOCK_UN)
        finally:
            os.close(descriptor)


def _serialized_apply(function):
    @wraps(function)
    def wrapped(root_raw, *args, **kwargs):
        root = validate_exact_directory(root_raw)
        with _workspace_mutation_lock(root):
            return function(root, *args, **kwargs)

    return wrapped


@contextmanager
def _open_parent_descriptor(root: Path, relative_file: str, *, create: bool):
    normalized = normalize_relative_path(relative_file)
    parts = PurePosixPath(normalized).parts
    if not parts:
        raise WorkspaceError("invalid_relative_path", "A file path must name a final component.")
    descriptor = _root_descriptor(root)
    try:
        for part in parts[:-1]:
            try:
                child = os.open(part, _directory_open_flags(), dir_fd=descriptor)
            except FileNotFoundError:
                if not create:
                    raise WorkspaceError("missing_parent", f"Required directory is missing: {part}")
                try:
                    os.mkdir(part, mode=0o755, dir_fd=descriptor)
                except FileExistsError:
                    pass
                try:
                    child = os.open(part, _directory_open_flags(), dir_fd=descriptor)
                except OSError as exc:
                    raise WorkspaceError("path_collision", f"Created parent is not a real directory: {part}") from exc
            except OSError as exc:
                if exc.errno in {errno.ELOOP, errno.ENOTDIR}:
                    raise WorkspaceError("path_collision", f"File parent is linked or not a directory: {part}") from exc
                raise
            os.close(descriptor)
            descriptor = child
        yield descriptor, parts[-1]
    finally:
        os.close(descriptor)


def _descriptor_bytes(descriptor: int) -> bytes:
    os.lseek(descriptor, 0, os.SEEK_SET)
    chunks: list[bytes] = []
    while True:
        chunk = os.read(descriptor, 1024 * 1024)
        if not chunk:
            return b"".join(chunks)
        chunks.append(chunk)


def _descriptor_size_hash(descriptor: int) -> tuple[int, str]:
    os.lseek(descriptor, 0, os.SEEK_SET)
    digest = hashlib.sha256()
    size = 0
    while True:
        chunk = os.read(descriptor, 1024 * 1024)
        if not chunk:
            return size, digest.hexdigest()
        digest.update(chunk)
        size += len(chunk)


def _guarded_open_absolute(source: Path, flags: int) -> int:
    absolute = _absolute_without_resolving(source)
    if absolute.anchor != os.sep:
        raise WorkspaceError(
            "unsupported_mutation_runtime",
            "Secure source opening currently requires a POSIX absolute path.",
        )
    relative = PurePosixPath(*absolute.parts[1:]).as_posix()
    filesystem_root = Path(os.sep)
    before = filesystem_root.lstat()
    root_descriptor = os.open(filesystem_root, _directory_open_flags())
    try:
        opened = os.fstat(root_descriptor)
        if (opened.st_dev, opened.st_ino) != (before.st_dev, before.st_ino):
            raise WorkspaceError("source_changed", "The filesystem source anchor changed during apply.")
        return _guarded_open_beneath(root_descriptor, relative, flags)
    finally:
        os.close(root_descriptor)


def _open_regular_at(parent: int, name: str, flags: int) -> int:
    try:
        descriptor = os.open(name, flags | os.O_NOFOLLOW, dir_fd=parent)
    except OSError as exc:
        if exc.errno in {errno.ELOOP, errno.ENOTDIR}:
            raise WorkspaceError("path_collision", f"Managed file is linked or has an invalid parent: {name}") from exc
        raise
    info = os.fstat(descriptor)
    if not stat.S_ISREG(info.st_mode):
        os.close(descriptor)
        raise WorkspaceError("path_collision", f"Managed file is not a regular file: {name}")
    return descriptor


def _secure_ensure_directory(root: Path, relative: str) -> None:
    normalized = normalize_relative_path(relative)
    descriptor = _root_descriptor(root)
    try:
        for part in PurePosixPath(normalized).parts:
            try:
                child = os.open(part, _directory_open_flags(), dir_fd=descriptor)
            except FileNotFoundError:
                try:
                    os.mkdir(part, mode=0o755, dir_fd=descriptor)
                except FileExistsError:
                    pass
                try:
                    child = os.open(part, _directory_open_flags(), dir_fd=descriptor)
                except OSError as exc:
                    raise WorkspaceError("path_collision", f"Required directory collides with another node: {relative}") from exc
            except OSError as exc:
                raise WorkspaceError("path_collision", f"Required directory is linked or invalid: {relative}") from exc
            os.close(descriptor)
            descriptor = child
    finally:
        os.close(descriptor)


def _secure_make_directory(root: Path, relative: str) -> None:
    with _open_parent_descriptor(root, relative, create=True) as (parent, name):
        try:
            os.mkdir(name, mode=0o755, dir_fd=parent)
        except FileExistsError as exc:
            raise WorkspaceError("path_collision", f"Directory collision evidence already exists: {relative}") from exc


def _secure_write_exclusive_or_same(root: Path, relative: str, content: bytes) -> str:
    with _open_parent_descriptor(root, relative, create=True):
        pass
    root_descriptor = _root_descriptor(root)
    try:
        try:
            descriptor = _guarded_open_beneath(
                root_descriptor,
                relative,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            )
        except FileExistsError:
            try:
                descriptor = _guarded_open_beneath(root_descriptor, relative, os.O_RDONLY)
            except OSError as exc:
                raise WorkspaceError("path_collision", f"Target collision: {relative}") from exc
            try:
                if not stat.S_ISREG(os.fstat(descriptor).st_mode):
                    raise WorkspaceError("path_collision", f"Target is not a regular file: {relative}")
                if _descriptor_bytes(descriptor) != content:
                    raise WorkspaceError("no_clobber", f"Refusing to overwrite different existing content: {relative}")
            finally:
                os.close(descriptor)
            return "unchanged"
        try:
            view = memoryview(content)
            while view:
                written = os.write(descriptor, view)
                view = view[written:]
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
        readback = _guarded_open_beneath(root_descriptor, relative, os.O_RDONLY)
        try:
            if not stat.S_ISREG(os.fstat(readback).st_mode):
                raise WorkspaceError("path_collision", f"Written target is not a regular file: {relative}")
            if _descriptor_bytes(readback) != content:
                raise WorkspaceError("readback_failed", f"Written bytes failed readback: {relative}")
        finally:
            os.close(readback)
    finally:
        os.close(root_descriptor)
    return "created"


def _secure_write_exclusive(root: Path, relative: str, content: bytes) -> None:
    with _open_parent_descriptor(root, relative, create=True):
        pass
    root_descriptor = _root_descriptor(root)
    try:
        try:
            descriptor = _guarded_open_beneath(
                root_descriptor,
                relative,
                os.O_WRONLY | os.O_CREAT | os.O_EXCL,
            )
        except FileExistsError as exc:
            raise WorkspaceError(
                "collision_evidence",
                f"Preserved mutation evidence already exists: {relative}",
            ) from exc
        try:
            view = memoryview(content)
            while view:
                written = os.write(descriptor, view)
                view = view[written:]
            os.fsync(descriptor)
        finally:
            os.close(descriptor)
    finally:
        os.close(root_descriptor)


def _secure_copy_verified(
    source: Path,
    root: Path,
    destination_relative: str,
    *,
    expected_size: int,
    expected_sha256: str,
    make_read_only: bool,
) -> str:
    source_before = source.lstat()
    try:
        source_descriptor = _guarded_open_absolute(source, os.O_RDONLY)
    except OSError as exc:
        raise WorkspaceError("source_changed", f"Cannot securely open the planned source: {source}") from exc
    try:
        opened = os.fstat(source_descriptor)
        if not stat.S_ISREG(opened.st_mode) or (opened.st_dev, opened.st_ino) != (source_before.st_dev, source_before.st_ino):
            raise WorkspaceError("source_changed", f"Source changed before copying: {source}")
        if _descriptor_size_hash(source_descriptor) != (expected_size, expected_sha256):
            raise WorkspaceError("source_changed", f"Source no longer matches the dry-run: {source}")
        with _open_parent_descriptor(root, destination_relative, create=True):
            pass
        root_descriptor = _root_descriptor(root)
        try:
            try:
                destination_descriptor = _guarded_open_beneath(
                    root_descriptor,
                    destination_relative,
                    os.O_WRONLY | os.O_CREAT | os.O_EXCL,
                )
            except FileExistsError:
                destination_descriptor = _guarded_open_beneath(
                    root_descriptor,
                    destination_relative,
                    os.O_RDONLY,
                )
                try:
                    if not stat.S_ISREG(os.fstat(destination_descriptor).st_mode):
                        raise WorkspaceError("path_collision", f"Destination is not a regular file: {destination_relative}")
                    if _descriptor_size_hash(destination_descriptor) != (expected_size, expected_sha256):
                        raise WorkspaceError("no_clobber", f"Destination contains different bytes: {destination_relative}")
                finally:
                    os.close(destination_descriptor)
                return "unchanged"
            try:
                os.lseek(source_descriptor, 0, os.SEEK_SET)
                while True:
                    chunk = os.read(source_descriptor, 1024 * 1024)
                    if not chunk:
                        break
                    view = memoryview(chunk)
                    while view:
                        written = os.write(destination_descriptor, view)
                        view = view[written:]
                os.fsync(destination_descriptor)
                if make_read_only:
                    os.fchmod(destination_descriptor, stat.S_IRUSR | stat.S_IRGRP | stat.S_IROTH)
            finally:
                os.close(destination_descriptor)
            readback = _guarded_open_beneath(
                root_descriptor,
                destination_relative,
                os.O_RDONLY,
            )
            try:
                if not stat.S_ISREG(os.fstat(readback).st_mode):
                    raise WorkspaceError("path_collision", f"Copied target is not a regular file: {destination_relative}")
                if _descriptor_size_hash(readback) != (expected_size, expected_sha256):
                    raise WorkspaceError("copy_verification_failed", f"Copied bytes failed verification: {destination_relative}")
            finally:
                os.close(readback)
        finally:
            os.close(root_descriptor)
        source_after = source.lstat()
        if (source_after.st_dev, source_after.st_ino) != (opened.st_dev, opened.st_ino):
            raise WorkspaceError("source_changed", f"Source path changed during copying: {source}")
    finally:
        os.close(source_descriptor)
    return "created"


def _renameat_flags(source_parent: int, source: str, target_parent: int, target: str, flags: int) -> None:
    libc = ctypes.CDLL(None, use_errno=True)
    encoded_source = os.fsencode(source)
    encoded_target = os.fsencode(target)
    if hasattr(libc, "renameatx_np"):
        result = libc.renameatx_np(
            source_parent,
            encoded_source,
            target_parent,
            encoded_target,
            flags | 0x00000010 | 0x00000020,
        )
    elif hasattr(libc, "renameat2"):
        result = libc.renameat2(source_parent, encoded_source, target_parent, encoded_target, flags)
    else:
        raise WorkspaceError("unsupported_mutation_runtime", "Atomic no-clobber rename primitives are unavailable on this platform.")
    if result != 0:
        error = ctypes.get_errno()
        raise OSError(error, os.strerror(error))


def _secure_rename_noreplace(root: Path, source_relative: str, target_relative: str) -> None:
    source_relative = normalize_relative_path(source_relative)
    target_relative = normalize_relative_path(target_relative)
    if sys.platform == "darwin":
        root_descriptor = _root_descriptor(root)
        try:
            _renameat_flags(
                root_descriptor,
                source_relative,
                root_descriptor,
                target_relative,
                4,
            )
        except OSError as exc:
            raise WorkspaceError("no_clobber", f"Atomic move refused a collision: {target_relative}") from exc
        finally:
            os.close(root_descriptor)
        return
    with _open_parent_descriptor(root, source_relative, create=False) as (source_parent, source_name):
        with _open_parent_descriptor(root, target_relative, create=True) as (target_parent, target_name):
            try:
                _renameat_flags(source_parent, source_name, target_parent, target_name, 1)
            except OSError as exc:
                raise WorkspaceError("no_clobber", f"Atomic move refused a collision: {target_relative}") from exc


def _secure_exchange_names(root: Path, left_relative: str, right_relative: str) -> None:
    left_relative = normalize_relative_path(left_relative)
    right_relative = normalize_relative_path(right_relative)
    if sys.platform == "darwin":
        root_descriptor = _root_descriptor(root)
        try:
            _renameat_flags(
                root_descriptor,
                left_relative,
                root_descriptor,
                right_relative,
                2,
            )
        finally:
            os.close(root_descriptor)
        return
    with _open_parent_descriptor(root, left_relative, create=False) as (left_parent, left_name):
        with _open_parent_descriptor(root, right_relative, create=False) as (right_parent, right_name):
            _renameat_flags(left_parent, left_name, right_parent, right_name, 2)


def _secure_remove_empty_directory(root: Path, relative: str) -> None:
    with _open_parent_descriptor(root, relative, create=False) as (parent, name):
        try:
            os.rmdir(name, dir_fd=parent)
        except OSError as exc:
            raise WorkspaceError(
                "directory_not_empty",
                f"Refusing to remove a non-empty or changed managed directory: {relative}",
            ) from exc


def _secure_exchange_claim(root: Path, relative: str, expected: bytes, replacement: bytes) -> str:
    temp_relative = str(PurePosixPath(relative).with_name(f".{PurePosixPath(relative).name}.document-workspace.displaced"))
    root_descriptor = _root_descriptor(root)
    try:
        current = _guarded_open_beneath(root_descriptor, relative, os.O_RDONLY)
        try:
            if not stat.S_ISREG(os.fstat(current).st_mode):
                raise WorkspaceError("path_collision", f"Managed control is not a regular file: {relative}")
            if _descriptor_bytes(current) != expected:
                raise WorkspaceError("control_changed", f"Managed control file changed after planning: {relative}")
        finally:
            os.close(current)
    finally:
        os.close(root_descriptor)
    _secure_write_exclusive(root, temp_relative, replacement)
    temp_descriptor = _root_descriptor(root)
    try:
        replacement_handle = _guarded_open_beneath(temp_descriptor, temp_relative, os.O_RDONLY)
        try:
            replacement_identity = os.fstat(replacement_handle)
        finally:
            os.close(replacement_handle)
    finally:
        os.close(temp_descriptor)
    try:
        _secure_exchange_names(root, temp_relative, relative)
    except OSError as exc:
        raise WorkspaceError(
            "control_exchange_failed",
            f"Atomic control exchange failed; replacement remains as collision evidence: {temp_relative}",
        ) from exc
    with _open_parent_descriptor(root, relative, create=False) as (parent, name):
        temp_name = PurePosixPath(temp_relative).name
        displaced = _open_regular_at(parent, temp_name, os.O_RDONLY)
        try:
            displaced_bytes = _descriptor_bytes(displaced)
        finally:
            os.close(displaced)
        current = _open_regular_at(parent, name, os.O_RDONLY)
        try:
            current_identity = os.fstat(current)
            current_bytes = _descriptor_bytes(current)
        finally:
            os.close(current)
        current_is_replacement = (
            current_identity.st_dev,
            current_identity.st_ino,
        ) == (
            replacement_identity.st_dev,
            replacement_identity.st_ino,
        )
        if displaced_bytes != expected:
            if current_is_replacement and current_bytes == replacement:
                try:
                    _secure_exchange_names(root, temp_relative, relative)
                except OSError as exc:
                    raise WorkspaceError(
                        "control_transition_collision",
                        "Concurrent control bytes and the proposed replacement were preserved, but rollback failed.",
                    ) from exc
            raise WorkspaceError(
                "control_changed",
                f"Concurrent control bytes were preserved; review current and collision evidence: {temp_relative}",
            )
        if not current_is_replacement or current_bytes != replacement:
            raise WorkspaceError(
                "control_transition_collision",
                f"Control changed after the atomic exchange; prior managed bytes remain at {temp_relative}",
            )
        return temp_relative


def _secure_exchange_commit(root: Path, relative: str, evidence_relative: str, replacement: bytes) -> None:
    with _open_parent_descriptor(root, relative, create=False) as (parent, name):
        evidence_name = PurePosixPath(evidence_relative).name
        current = _open_regular_at(parent, name, os.O_RDONLY)
        try:
            current_bytes = _descriptor_bytes(current)
        finally:
            os.close(current)
        if current_bytes != replacement:
            raise WorkspaceError(
                "control_transition_collision",
                f"Control changed after it was claimed; prior managed bytes remain at {evidence_relative}",
            )
        os.unlink(evidence_name, dir_fd=parent)
        os.fsync(parent)


def _secure_exchange_abort(root: Path, relative: str, evidence_relative: str, replacement: bytes) -> None:
    with _open_parent_descriptor(root, relative, create=False) as (parent, name):
        current = _open_regular_at(parent, name, os.O_RDONLY)
        try:
            current_bytes = _descriptor_bytes(current)
        finally:
            os.close(current)
    if current_bytes != replacement:
        raise WorkspaceError(
            "control_transition_collision",
            f"Control changed after it was claimed; rollback evidence remains at {evidence_relative}",
        )
    _secure_exchange_names(root, evidence_relative, relative)


def _secure_exchange_expected(root: Path, relative: str, expected: bytes, replacement: bytes) -> None:
    evidence = _secure_exchange_claim(root, relative, expected, replacement)
    _secure_exchange_commit(root, relative, evidence, replacement)


@_serialized_apply
def apply_initialize(
    root_raw: os.PathLike[str] | str,
    *,
    timestamp: str,
    upstream_derived: Iterable[str] = (),
    plan_token: str | None,
) -> dict[str, Any]:
    plan = plan_initialize(root_raw, timestamp=timestamp, upstream_derived=upstream_derived)
    token = require_plan_token(plan, plan_token)
    if plan["status"] == "already_initialized":
        return {**plan, "status": "already_initialized", "plan_token": token}
    root = validate_exact_directory(root_raw)
    for relative in LAYOUT_DIRECTORIES:
        _secure_ensure_directory(root, relative)
    files = _initial_file_map(plan["timestamp"], plan["mode"])
    for relative, content in sorted(files.items()):
        _secure_write_exclusive_or_same(root, relative, content)
    for record in plan["source_records"]:
        source = path_in_workspace(root, record["original_relative_path"])
        _secure_copy_verified(
            source,
            root,
            record["current_relative_path"],
            expected_size=record["byte_size"],
            expected_sha256=record["sha256"],
            make_read_only=True,
        )
        _secure_write_exclusive_or_same(
            root,
            f"control/sources/{record['source_id']}.json",
            canonical_json_bytes(record),
        )
    validation = validate_workspace(root)
    return {
        "operation": "initialize",
        "status": "initialized" if plan["mode"] == "empty" else "adopted",
        "workspace": os.fspath(root),
        "mode": plan["mode"],
        "preserved_source_count": len(plan["source_records"]),
        "plan_token": token,
        "validation_summary": validation["summary"],
        "provider_calls": False,
    }


def _validate_source_options(source_class: str, reliability: str) -> None:
    if source_class not in SOURCE_CLASSES:
        raise WorkspaceError("invalid_source_class", f"Unsupported source class: {source_class}")
    if reliability not in RELIABILITY_VALUES:
        raise WorkspaceError("invalid_reliability", f"Unsupported reliability value: {reliability}")
    if source_class == "upstream-derived" and reliability != "unverified":
        raise WorkspaceError(
            "upstream_reliability_mismatch",
            "Upstream-derived material must remain unverified when preserved as received.",
        )


def _validate_explicit_source(source_raw: os.PathLike[str] | str) -> Path:
    source = _absolute_without_resolving(source_raw)
    if not source.exists() and not is_link_like(source):
        raise WorkspaceError(
            "missing_attachment",
            "A UI-visible attachment is not durable evidence without a real readable file.",
            status="not_preserved",
        )
    for component in _iter_absolute_components(source):
        try:
            info = component.lstat()
        except FileNotFoundError as exc:
            raise WorkspaceError(
                "missing_attachment",
                "The attachment path is incomplete or missing.",
                status="not_preserved",
            ) from exc
        if stat.S_ISLNK(info.st_mode) or is_link_like(component):
            raise WorkspaceError(
                "linked_attachment_refused",
                "Linked attachments are not copied because their boundary is uncertain.",
                status="not_preserved",
            )
    info = source.lstat()
    if not stat.S_ISREG(info.st_mode):
        raise WorkspaceError(
            "unsupported_attachment",
            "The attachment must be one readable regular file.",
            status="not_preserved",
        )
    try:
        classify_file(source)
        hash_regular_file(source)
    except WorkspaceError as exc:
        if exc.status == "not_preserved":
            raise
        raise WorkspaceError(
            exc.code,
            str(exc),
            status="not_preserved",
            details=exc.details,
        ) from exc
    return source


def _validate_derivation_links(root: Path, links: Iterable[str]) -> list[str]:
    if isinstance(links, (str, bytes)):
        raise WorkspaceError("invalid_derivation", "Derivation links must be a list of record IDs.")
    supplied = list(links)
    if any(not isinstance(link, str) for link in supplied):
        raise WorkspaceError("invalid_derivation", "Derivation links must be string record IDs.")
    normalized = list(dict.fromkeys(supplied))
    if not normalized:
        return []
    if "unknown" in normalized and len(normalized) != 1:
        raise WorkspaceError("invalid_derivation", "Use either explicit derivation record IDs or only `unknown`.")
    if normalized == ["unknown"]:
        return normalized
    for link in normalized:
        if SOURCE_ID_RE.fullmatch(link):
            record = root / "control" / "sources" / f"{link}.json"
        elif ARTIFACT_ID_RE.fullmatch(link):
            record = root / "control" / "artifacts" / f"{link}.json"
        else:
            raise WorkspaceError("invalid_derivation", f"Unknown derivation record ID: {link}")
        if not record.is_file() or is_link_like(record):
            raise WorkspaceError("missing_derivation", f"Derivation record is missing: {link}")
    return normalized


def _validate_derivation_acyclic(root: Path, start_id: str) -> None:
    visited: set[str] = set()
    active: set[str] = set()

    def links_for(record_id: str) -> list[str]:
        if SOURCE_ID_RE.fullmatch(record_id):
            path = root / "control" / "sources" / f"{record_id}.json"
        elif ARTIFACT_ID_RE.fullmatch(record_id):
            path = root / "control" / "artifacts" / f"{record_id}.json"
        else:
            raise WorkspaceError("invalid_derivation", f"Invalid derivation ID in graph: {record_id}")
        record = _load_json(path)
        links = record.get("derivation_links")
        if not isinstance(links, list):
            raise WorkspaceError("invalid_derivation", f"Derivation links are not a list: {record_id}")
        return [link for link in links if link != "unknown"]

    def visit(record_id: str) -> None:
        if record_id in active:
            raise WorkspaceError("derivation_cycle", f"Derivation cycle detected at {record_id}")
        if record_id in visited:
            return
        active.add(record_id)
        for linked_id in links_for(record_id):
            visit(linked_id)
        active.remove(record_id)
        visited.add(record_id)

    visit(start_id)


def plan_preserve(
    root_raw: os.PathLike[str] | str,
    *,
    source_raw: os.PathLike[str] | str,
    original_relative_path: str,
    source_class: str,
    reliability: str,
    received_at: str,
    event_at: str,
    timestamp: str,
    derivation_links: Iterable[str] = (),
) -> dict[str, Any]:
    root = validate_exact_directory(root_raw)
    source = _validate_explicit_source(source_raw)
    source_relative: str | None = None
    try:
        candidate_relative = source.relative_to(root).as_posix()
    except ValueError:
        pass
    else:
        source_relative = normalize_relative_path(candidate_relative)
    validate_workspace(root, allow_one_unpreserved_relative=source_relative)
    original = normalize_relative_path(original_relative_path)
    if source_relative is not None and original != source_relative:
        raise WorkspaceError(
            "in_workspace_source_label_mismatch",
            "An in-workspace arrival must record its exact current relative path as original_relative_path.",
        )
    imported_at = normalize_timestamp(timestamp)
    received = normalize_timestamp(received_at, allow_unknown=True)
    event = normalize_timestamp(event_at, allow_unknown=True)
    _validate_source_options(source_class, reliability)
    links = _validate_derivation_links(root, derivation_links)
    size, sha256 = hash_regular_file(source)
    type_class = classify_file(source)
    record = _new_source_record(
        original_relative_path=original,
        current_relative_path=f"raw/as-received/imported/pending/{source.name}",
        type_class=type_class,
        source_class=source_class,
        byte_size=size,
        sha256=sha256,
        received_at=received,
        event_at=event,
        imported_at=imported_at,
        reliability=reliability,
        derivation_links=links,
        source_mode="explicit-in-workspace" if source_relative is not None else "explicit-attachment",
    )
    source_id = record["source_id"]
    destination_relative = f"raw/as-received/imported/{source_id}/{source.name}"
    record["current_relative_path"] = destination_relative
    record_relative = f"control/sources/{source_id}.json"
    destination = path_in_workspace(root, destination_relative)
    record_path = path_in_workspace(root, record_relative)
    already = False
    if destination.exists() or record_path.exists() or is_link_like(destination) or is_link_like(record_path):
        if not destination.is_file() or is_link_like(destination) or not record_path.is_file() or is_link_like(record_path):
            raise WorkspaceError("path_collision", "Existing source destination or record is not the expected regular file pair.")
        existing = json.loads(record_path.read_text(encoding="utf-8"))
        existing_size, existing_sha = hash_regular_file(destination)
        if existing != record or (existing_size, existing_sha) != (size, sha256):
            raise WorkspaceError("no_clobber", "A different source or record already occupies the deterministic destination.")
        already = True
    return {
        "operation": "preserve",
        "status": "already_preserved" if already else "would_preserve",
        "workspace": os.fspath(root),
        "source": os.fspath(source),
        "source_name": source.name,
        "source_record": record,
        "actions": []
        if already
        else [
            {"action": "copy_preserved_source", "to": destination_relative, "sha256": sha256},
            {"action": "write_source_record", "path": record_relative},
        ],
        "provider_calls": False,
    }


@_serialized_apply
def apply_preserve(
    root_raw: os.PathLike[str] | str,
    *,
    source_raw: os.PathLike[str] | str,
    original_relative_path: str,
    source_class: str,
    reliability: str,
    received_at: str,
    event_at: str,
    timestamp: str,
    derivation_links: Iterable[str] = (),
    plan_token: str | None,
) -> dict[str, Any]:
    plan = plan_preserve(
        root_raw,
        source_raw=source_raw,
        original_relative_path=original_relative_path,
        source_class=source_class,
        reliability=reliability,
        received_at=received_at,
        event_at=event_at,
        timestamp=timestamp,
        derivation_links=derivation_links,
    )
    token = require_plan_token(plan, plan_token)
    if plan["status"] == "already_preserved":
        return {**plan, "plan_token": token}
    root = validate_exact_directory(root_raw)
    source = _validate_explicit_source(source_raw)
    record = plan["source_record"]
    _secure_copy_verified(
        source,
        root,
        record["current_relative_path"],
        expected_size=record["byte_size"],
        expected_sha256=record["sha256"],
        make_read_only=True,
    )
    _secure_write_exclusive_or_same(
        root,
        f"control/sources/{record['source_id']}.json",
        canonical_json_bytes(record),
    )
    validation = validate_workspace(root)
    return {
        "operation": "preserve",
        "status": "preserved",
        "workspace": os.fspath(root),
        "source_id": record["source_id"],
        "current_relative_path": record["current_relative_path"],
        "sha256": record["sha256"],
        "plan_token": token,
        "validation_summary": validation["summary"],
        "provider_calls": False,
    }


def _conversation_content(
    *,
    conversation_id: str,
    timestamp: str,
    proposal: str,
    user_correction: str,
    reason: str,
    final_decision: str,
) -> bytes:
    title = conversation_id.split("-", 1)[1].replace("-", " ").title()
    return f"""# {conversation_id.split('-', 1)[0]} {title}

> Date: {timestamp[:10]}
> Time: {timestamp}
> Status: complete

## Agent original proposal

{proposal.strip()}

## User corrections

{user_correction.strip()}

## Rejection or modification reasons

{reason.strip()}

## Final decision

{final_decision.strip()}
""".encode("utf-8")


def _require_nonempty_text(label: str, value: str) -> str:
    normalized = value.strip()
    if not normalized:
        raise WorkspaceError("missing_record_field", f"Conversation field {label!r} cannot be empty.")
    return normalized


def plan_conversation(
    root_raw: os.PathLike[str] | str,
    *,
    conversation_id: str,
    timestamp: str,
    proposal: str,
    user_correction: str,
    reason: str,
    final_decision: str,
) -> dict[str, Any]:
    root = validate_exact_directory(root_raw)
    validate_workspace(root)
    if not CONVERSATION_ID_RE.fullmatch(conversation_id):
        raise WorkspaceError("invalid_conversation_id", "Use NN-kebab-topic for conversation IDs.")
    timestamp = normalize_timestamp(timestamp)
    content = _conversation_content(
        conversation_id=conversation_id,
        timestamp=timestamp,
        proposal=_require_nonempty_text("proposal", proposal),
        user_correction=_require_nonempty_text("user_correction", user_correction),
        reason=_require_nonempty_text("reason", reason),
        final_decision=_require_nonempty_text("final_decision", final_decision),
    )
    relative = f"conversation/{conversation_id}.md"
    target = path_in_workspace(root, relative)
    status_value = "would_record"
    if target.exists() or is_link_like(target):
        if is_link_like(target) or not target.is_file():
            raise WorkspaceError("path_collision", f"Conversation path collision: {relative}")
        if target.read_bytes() != content:
            raise WorkspaceError("no_clobber", f"Conversation record already exists with different content: {relative}")
        status_value = "already_recorded"
    return {
        "operation": "conversation",
        "status": status_value,
        "workspace": os.fspath(root),
        "conversation_record": relative,
        "sha256": hashlib.sha256(content).hexdigest(),
        "actions": [] if status_value == "already_recorded" else [{"action": "write_conversation", "path": relative}],
        "provider_calls": False,
    }


@_serialized_apply
def apply_conversation(
    root_raw: os.PathLike[str] | str,
    *,
    conversation_id: str,
    timestamp: str,
    proposal: str,
    user_correction: str,
    reason: str,
    final_decision: str,
    plan_token: str | None,
) -> dict[str, Any]:
    plan = plan_conversation(
        root_raw,
        conversation_id=conversation_id,
        timestamp=timestamp,
        proposal=proposal,
        user_correction=user_correction,
        reason=reason,
        final_decision=final_decision,
    )
    token = require_plan_token(plan, plan_token)
    if plan["status"] == "already_recorded":
        return {**plan, "plan_token": token}
    root = validate_exact_directory(root_raw)
    content = _conversation_content(
        conversation_id=conversation_id,
        timestamp=normalize_timestamp(timestamp),
        proposal=_require_nonempty_text("proposal", proposal),
        user_correction=_require_nonempty_text("user_correction", user_correction),
        reason=_require_nonempty_text("reason", reason),
        final_decision=_require_nonempty_text("final_decision", final_decision),
    )
    _secure_write_exclusive_or_same(root, plan["conversation_record"], content)
    validate_workspace(root)
    return {**plan, "status": "recorded", "plan_token": token}


def _load_json(path: Path) -> dict[str, Any]:
    if is_link_like(path) or not path.is_file():
        raise WorkspaceError("missing_record", f"Required JSON record is missing or linked: {path}")
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        raise WorkspaceError("invalid_json", f"Invalid JSON record: {path}") from exc
    if not isinstance(value, dict):
        raise WorkspaceError("invalid_json", f"JSON record must be an object: {path}")
    return value


def _artifact_records(root: Path) -> list[dict[str, Any]]:
    directory = root / "control" / "artifacts"
    records = []
    for path in sorted(directory.glob("*.json"), key=lambda item: (item.name.casefold(), item.name)):
        records.append(_load_json(path))
    return records


def _artifact_for_path(root: Path, relative: str) -> dict[str, Any] | None:
    for record in _artifact_records(root):
        if record.get("current_relative_path") == relative:
            return record
    return None


def plan_artifact(
    root_raw: os.PathLike[str] | str,
    *,
    relative_path: str,
    kind: str,
    timestamp: str,
    reliability: str,
    derivation_links: Iterable[str],
) -> dict[str, Any]:
    root = validate_exact_directory(root_raw)
    validate_workspace(root, allow_unregistered_work=True)
    relative = normalize_relative_path(relative_path)
    if kind not in ARTIFACT_KINDS:
        raise WorkspaceError("invalid_artifact_kind", f"Unsupported artifact kind: {kind}")
    if reliability not in RELIABILITY_VALUES:
        raise WorkspaceError("invalid_reliability", f"Unsupported reliability value: {reliability}")
    required_prefix = "work/drafts/" if kind == "draft" else "work/derived/"
    if not relative.startswith(required_prefix):
        raise WorkspaceError("artifact_boundary", f"Artifact kind {kind!r} must live under {required_prefix}")
    target = path_in_workspace(root, relative)
    classify_file(target)
    size, sha256 = hash_regular_file(target)
    registered_paths = {
        record.get("current_relative_path") for record in _artifact_records(root)
    }
    work_entries = inventory_tree(root / "work")
    unregistered_paths = {
        f"work/{entry['path']}"
        for entry in work_entries
        if entry["node"] == "file"
        and f"work/{entry['path']}" not in registered_paths
    }
    if unregistered_paths - {relative}:
        raise WorkspaceError(
            "unregistered_work_collision",
            "Register one exact work artifact at a time; other unregistered files are collision evidence.",
            details={"paths": sorted(unregistered_paths - {relative})},
        )
    links = _validate_derivation_links(root, derivation_links)
    if not links:
        links = ["unknown"]
    timestamp = normalize_timestamp(timestamp)
    record = {
        "schema_version": SCHEMA_VERSION,
        "kind": kind,
        "current_relative_path": relative,
        "type_class": classify_file(target),
        "byte_size": size,
        "sha256": sha256,
        "created_at": timestamp,
        "reliability": reliability,
        "derivation_links": links,
        "status": "draft" if kind == "draft" else "working",
    }
    artifact_id = _artifact_identifier(_artifact_record_identity(record))
    record["artifact_id"] = artifact_id
    record_relative = f"control/artifacts/{artifact_id}.json"
    record_path = path_in_workspace(root, record_relative)
    existing_for_path = _artifact_for_path(root, relative)
    if existing_for_path and existing_for_path != record:
        raise WorkspaceError("artifact_changed", "The work artifact changed after it was registered; create a new path or version.")
    status_value = "would_record"
    if record_path.exists() or is_link_like(record_path):
        if is_link_like(record_path) or not record_path.is_file() or _load_json(record_path) != record:
            raise WorkspaceError("no_clobber", f"Artifact record collision: {record_relative}")
        status_value = "already_recorded"
    return {
        "operation": "artifact",
        "status": status_value,
        "workspace": os.fspath(root),
        "artifact_record": record,
        "record_path": record_relative,
        "actions": [] if status_value == "already_recorded" else [{"action": "write_artifact_record", "path": record_relative}],
        "provider_calls": False,
    }


@_serialized_apply
def apply_artifact(
    root_raw: os.PathLike[str] | str,
    *,
    relative_path: str,
    kind: str,
    timestamp: str,
    reliability: str,
    derivation_links: Iterable[str],
    plan_token: str | None,
) -> dict[str, Any]:
    plan = plan_artifact(
        root_raw,
        relative_path=relative_path,
        kind=kind,
        timestamp=timestamp,
        reliability=reliability,
        derivation_links=derivation_links,
    )
    token = require_plan_token(plan, plan_token)
    if plan["status"] == "already_recorded":
        return {**plan, "plan_token": token}
    root = validate_exact_directory(root_raw)
    _secure_write_exclusive_or_same(
        root,
        plan["record_path"],
        canonical_json_bytes(plan["artifact_record"]),
    )
    validate_workspace(root)
    return {**plan, "status": "recorded", "plan_token": token}


def _validate_version_id(version_id: str) -> str:
    if not VERSION_RE.fullmatch(version_id):
        raise WorkspaceError("invalid_version_id", "Use a stable zero-padded version ID such as v001.")
    return version_id


def _complete_conversation(root: Path, relative: str) -> tuple[int, str]:
    normalized = normalize_relative_path(relative)
    if not normalized.startswith("conversation/") or not normalized.endswith(".md"):
        raise WorkspaceError("conversation_boundary", "Conversation evidence must be a Markdown file under conversation/.")
    path = path_in_workspace(root, normalized)
    size, sha256 = hash_regular_file(path)
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeError as exc:
        raise WorkspaceError("invalid_conversation", "Conversation evidence must be UTF-8 text.") from exc
    if "> Status: complete" not in text:
        raise WorkspaceError("incomplete_conversation", "Conversation evidence is missing required proposal/correction/reason/decision fields.")
    headings = (
        "## Agent original proposal",
        "## User corrections",
        "## Rejection or modification reasons",
        "## Final decision",
    )
    positions = [text.find(heading) for heading in headings]
    if any(position < 0 for position in positions) or positions != sorted(positions):
        raise WorkspaceError("incomplete_conversation", "Conversation evidence is missing required proposal/correction/reason/decision fields.")
    for index, heading in enumerate(headings):
        start = positions[index] + len(heading)
        end = positions[index + 1] if index + 1 < len(headings) else len(text)
        body = text[start:end].strip()
        if not body or body == "unknown":
            raise WorkspaceError("incomplete_conversation", f"Conversation section is empty or unknown: {heading}")
    return size, sha256


def plan_approve(
    root_raw: os.PathLike[str] | str,
    *,
    version_id: str,
    files: Iterable[str],
    conversation_relative: str,
    timestamp: str,
) -> dict[str, Any]:
    root = validate_exact_directory(root_raw)
    validate_workspace(root)
    version_id = _validate_version_id(version_id)
    archived_version = root / "archive" / "versions" / version_id
    if archived_version.exists() or is_link_like(archived_version):
        raise WorkspaceError(
            "archived_version_exists",
            "An archived version ID is immutable and cannot become current again.",
        )
    timestamp = normalize_timestamp(timestamp)
    conversation = normalize_relative_path(conversation_relative)
    _, conversation_sha = _complete_conversation(root, conversation)
    normalized_files = sorted(
        {normalize_relative_path(value) for value in files},
        key=lambda value: (value.casefold(), value),
    )
    if not normalized_files:
        raise WorkspaceError("missing_outputs", "Approval requires at least one registered draft file.")
    outputs: list[dict[str, Any]] = []
    for relative in normalized_files:
        if not relative.startswith("work/drafts/"):
            raise WorkspaceError("draft_boundary", f"Only files under work/drafts can be approved: {relative}")
        artifact = _artifact_for_path(root, relative)
        if artifact is None or artifact.get("kind") != "draft":
            raise WorkspaceError("unregistered_draft", f"Draft must be registered before approval: {relative}")
        source = path_in_workspace(root, relative)
        size, sha256 = hash_regular_file(source)
        if (size, sha256) != (artifact.get("byte_size"), artifact.get("sha256")):
            raise WorkspaceError("artifact_changed", f"Draft bytes changed after registration: {relative}")
        suffix = relative[len("work/drafts/") :]
        current = f"formal/current/{version_id}/{suffix}"
        outputs.append(
            {
                "artifact_id": artifact["artifact_id"],
                "draft_relative_path": relative,
                "current_relative_path": current,
                "type_class": artifact["type_class"],
                "byte_size": size,
                "sha256": sha256,
            }
        )
    current_path = root / "control" / "current.json"
    existing_current = _load_json(current_path)
    new_current = {
        "schema_version": SCHEMA_VERSION,
        "status": "approved",
        "version_id": version_id,
        "decided_at": timestamp,
        "conversation_record": conversation,
        "conversation_sha256": conversation_sha,
        "outputs": outputs,
    }
    if existing_current == new_current:
        for output in outputs:
            size, sha256 = hash_regular_file(path_in_workspace(root, output["current_relative_path"]))
            if (size, sha256) != (output["byte_size"], output["sha256"]):
                raise WorkspaceError("current_output_changed", "Approved current bytes no longer match their record.")
        status_value = "already_approved"
        actions: list[dict[str, Any]] = []
    else:
        if existing_current != empty_current_record():
            raise WorkspaceError(
                "current_version_exists",
                "Archive the exact current version as superseded before approving a replacement.",
            )
        current_entries = inventory_tree(root / "formal" / "current")
        existing_files = [entry["path"] for entry in current_entries if entry["node"] == "file"]
        allowed_existing = {PurePosixPath(output["current_relative_path"]).relative_to("formal/current").as_posix() for output in outputs}
        if any(path not in allowed_existing for path in existing_files):
            raise WorkspaceError("current_output_collision", "formal/current contains untracked collision evidence.")
        for output in outputs:
            target = path_in_workspace(root, output["current_relative_path"])
            if target.exists() or is_link_like(target):
                if is_link_like(target) or not target.is_file():
                    raise WorkspaceError("path_collision", f"Current output collision: {output['current_relative_path']}")
                size, sha256 = hash_regular_file(target)
                if (size, sha256) != (output["byte_size"], output["sha256"]):
                    raise WorkspaceError("no_clobber", f"Different current output bytes already exist: {output['current_relative_path']}")
        status_value = "would_approve"
        actions = [
            {"action": "copy_current_output", "from": item["draft_relative_path"], "to": item["current_relative_path"], "sha256": item["sha256"]}
            for item in outputs
        ] + [{"action": "set_current_record", "path": "control/current.json"}]
    return {
        "operation": "approve",
        "status": status_value,
        "workspace": os.fspath(root),
        "current_record": new_current,
        "actions": actions,
        "provider_calls": False,
    }


@_serialized_apply
def apply_approve(
    root_raw: os.PathLike[str] | str,
    *,
    version_id: str,
    files: Iterable[str],
    conversation_relative: str,
    timestamp: str,
    plan_token: str | None,
) -> dict[str, Any]:
    plan = plan_approve(
        root_raw,
        version_id=version_id,
        files=files,
        conversation_relative=conversation_relative,
        timestamp=timestamp,
    )
    token = require_plan_token(plan, plan_token)
    if plan["status"] == "already_approved":
        return {**plan, "plan_token": token}
    root = validate_exact_directory(root_raw)
    for output in plan["current_record"]["outputs"]:
        source = path_in_workspace(root, output["draft_relative_path"])
        _secure_copy_verified(
            source,
            root,
            output["current_relative_path"],
            expected_size=output["byte_size"],
            expected_sha256=output["sha256"],
            make_read_only=False,
        )
    _secure_exchange_expected(
        root,
        "control/current.json",
        canonical_json_bytes(empty_current_record()),
        canonical_json_bytes(plan["current_record"]),
    )
    validation = validate_workspace(root)
    return {
        **plan,
        "status": "approved",
        "plan_token": token,
        "validation_summary": validation["summary"],
    }


def _archive_existing_matches(
    root: Path,
    version_id: str,
    *,
    status_value: str,
    reason: str,
    replacement: str,
    conversation: str,
    timestamp: str,
    requested_sources: set[str] | None,
) -> dict[str, Any] | None:
    record_path = root / "archive" / "versions" / version_id / "record.json"
    if not record_path.exists() and not is_link_like(record_path):
        return None
    record = _load_json(record_path)
    expected_fields = {
        "version_id": version_id,
        "status": status_value,
        "reason": reason,
        "replacement": replacement,
        "timestamp": timestamp,
        "conversation_record": conversation,
    }
    if any(record.get(key) != value for key, value in expected_fields.items()):
        raise WorkspaceError("archive_collision", f"Archive version already exists with different metadata: {version_id}")
    if requested_sources is not None:
        recorded_sources = {
            item.get("source_relative_path")
            for item in record.get("files", [])
            if isinstance(item, dict)
        }
        if recorded_sources != requested_sources:
            raise WorkspaceError(
                "archive_collision",
                f"Archive version already exists for a different file set: {version_id}",
            )
    _validate_archive_record(root, record_path, record)
    return record


def plan_archive(
    root_raw: os.PathLike[str] | str,
    *,
    version_id: str,
    status_value: str,
    files: Iterable[str],
    reason: str,
    replacement: str,
    conversation_relative: str,
    timestamp: str,
) -> dict[str, Any]:
    root = validate_exact_directory(root_raw)
    validate_workspace(root)
    version_id = _validate_version_id(version_id)
    if status_value not in ARCHIVE_STATUSES:
        raise WorkspaceError("invalid_archive_status", "Archive status must be rejected or superseded.")
    reason = _require_nonempty_text("reason", reason)
    replacement = replacement.strip() or "unknown"
    if replacement != "unknown":
        _validate_version_id(replacement)
        if replacement == version_id:
            raise WorkspaceError("invalid_replacement", "An archive replacement cannot equal the archived version.")
    timestamp = normalize_timestamp(timestamp)
    conversation = normalize_relative_path(conversation_relative)
    _, conversation_sha = _complete_conversation(root, conversation)
    file_values = list(files)
    normalized_files: list[str] = []
    if status_value == "rejected":
        normalized_files = sorted(
            {normalize_relative_path(value) for value in file_values},
            key=lambda value: (value.casefold(), value),
        )
        if not normalized_files:
            raise WorkspaceError("missing_outputs", "Rejected archive requires at least one registered draft.")
        current = _load_json(root / "control" / "current.json")
        if current.get("status") == "approved" and current.get("version_id") == version_id:
            raise WorkspaceError(
                "version_state_conflict",
                "The approved current version cannot also be archived as rejected.",
            )
        requested_sources: set[str] | None = set(normalized_files)
    else:
        if file_values:
            raise WorkspaceError("unexpected_files", "Superseded archive uses the complete current record; do not pass --file.")
        requested_sources = None
    existing = _archive_existing_matches(
        root,
        version_id,
        status_value=status_value,
        reason=reason,
        replacement=replacement,
        conversation=conversation,
        timestamp=timestamp,
        requested_sources=requested_sources,
    )
    if existing is not None:
        return {
            "operation": "archive",
            "status": "already_archived",
            "workspace": os.fspath(root),
            "archive_record": existing,
            "actions": [],
            "provider_calls": False,
        }

    file_records: list[dict[str, Any]] = []
    expected_current_record: dict[str, Any] | None = None
    if status_value == "rejected":
        for relative in normalized_files:
            if not relative.startswith("work/drafts/"):
                raise WorkspaceError("draft_boundary", f"Rejected versions must come from work/drafts: {relative}")
            artifact = _artifact_for_path(root, relative)
            if artifact is None or artifact.get("kind") != "draft":
                raise WorkspaceError("unregistered_draft", f"Draft must be registered before archive: {relative}")
            size, sha256 = hash_regular_file(path_in_workspace(root, relative))
            if (size, sha256) != (artifact["byte_size"], artifact["sha256"]):
                raise WorkspaceError("artifact_changed", f"Draft bytes changed after registration: {relative}")
            suffix = relative[len("work/drafts/") :]
            file_records.append(
                {
                    "source_relative_path": relative,
                    "archive_relative_path": f"archive/versions/{version_id}/files/{suffix}",
                    "artifact_id": artifact["artifact_id"],
                    "byte_size": size,
                    "sha256": sha256,
                    "archive_method": "copy-preserve-draft",
                }
            )
    else:
        current = _load_json(root / "control" / "current.json")
        if current.get("status") != "approved" or current.get("version_id") != version_id:
            raise WorkspaceError("current_version_mismatch", "The superseded version must be the exact approved current version.")
        for output in current.get("outputs", []):
            source_relative = output["current_relative_path"]
            size, sha256 = hash_regular_file(path_in_workspace(root, source_relative))
            if (size, sha256) != (output["byte_size"], output["sha256"]):
                raise WorkspaceError("current_output_changed", f"Current output bytes changed: {source_relative}")
            prefix = f"formal/current/{version_id}/"
            if not source_relative.startswith(prefix):
                raise WorkspaceError("current_record_invalid", f"Current output is outside its version directory: {source_relative}")
            suffix = source_relative[len(prefix) :]
            file_records.append(
                {
                    "source_relative_path": source_relative,
                    "archive_relative_path": f"archive/versions/{version_id}/files/{suffix}",
                    "artifact_id": output["artifact_id"],
                    "byte_size": size,
                    "sha256": sha256,
                    "archive_method": "move-current",
                }
            )
        expected_current_record = current
    archive_record = {
        "schema_version": SCHEMA_VERSION,
        "version_id": version_id,
        "status": status_value,
        "reason": reason,
        "replacement": replacement,
        "timestamp": timestamp,
        "conversation_record": conversation,
        "conversation_sha256": conversation_sha,
        "files": file_records,
    }
    actions = [
        {
            "action": "archive_file",
            "method": item["archive_method"],
            "from": item["source_relative_path"],
            "to": item["archive_relative_path"],
            "sha256": item["sha256"],
        }
        for item in file_records
    ]
    actions.append({"action": "write_archive_record", "path": f"archive/versions/{version_id}/record.json"})
    if status_value == "superseded":
        actions.append({"action": "clear_current_record", "path": "control/current.json"})
    result = {
        "operation": "archive",
        "status": "would_archive",
        "workspace": os.fspath(root),
        "archive_record": archive_record,
        "actions": actions,
        "provider_calls": False,
    }
    if expected_current_record is not None:
        result["expected_current_record"] = expected_current_record
    return result


@_serialized_apply
def apply_archive(
    root_raw: os.PathLike[str] | str,
    *,
    version_id: str,
    status_value: str,
    files: Iterable[str],
    reason: str,
    replacement: str,
    conversation_relative: str,
    timestamp: str,
    plan_token: str | None,
) -> dict[str, Any]:
    file_values = list(files)
    plan = plan_archive(
        root_raw,
        version_id=version_id,
        status_value=status_value,
        files=file_values,
        reason=reason,
        replacement=replacement,
        conversation_relative=conversation_relative,
        timestamp=timestamp,
    )
    token = require_plan_token(plan, plan_token)
    if plan["status"] == "already_archived":
        return {**plan, "plan_token": token}
    root = validate_exact_directory(root_raw)
    record = plan["archive_record"]
    final_relative = f"archive/versions/{record['version_id']}"
    temp_relative = f"archive/versions/.{record['version_id']}.document-workspace.tmp"
    final = path_in_workspace(root, final_relative)
    temp = path_in_workspace(root, temp_relative)
    if final.exists() or is_link_like(final) or temp.exists() or is_link_like(temp):
        raise WorkspaceError("archive_collision", "Archive destination or preserved temporary collision already exists.")
    cleared_current = canonical_json_bytes(empty_current_record())
    current_evidence: str | None = None
    if record["status"] == "superseded":
        current_evidence = _secure_exchange_claim(
            root,
            "control/current.json",
            canonical_json_bytes(plan["expected_current_record"]),
            cleared_current,
        )
    _secure_make_directory(root, temp_relative)
    _secure_ensure_directory(root, f"{temp_relative}/files")
    emptied_current_directories: set[str] = set()
    for item in record["files"]:
        source = path_in_workspace(root, item["source_relative_path"])
        suffix = PurePosixPath(item["archive_relative_path"]).relative_to(
            f"archive/versions/{record['version_id']}/files"
        )
        destination_relative = f"{temp_relative}/files/{suffix.as_posix()}"
        if item["archive_method"] == "copy-preserve-draft":
            _secure_copy_verified(
                source,
                root,
                destination_relative,
                expected_size=item["byte_size"],
                expected_sha256=item["sha256"],
                make_read_only=False,
            )
        else:
            _secure_rename_noreplace(root, item["source_relative_path"], destination_relative)
            parent = PurePosixPath(item["source_relative_path"]).parent
            stop = PurePosixPath("formal/current")
            while parent != stop:
                emptied_current_directories.add(parent.as_posix())
                parent = parent.parent
            size, sha256 = hash_regular_file(path_in_workspace(root, destination_relative))
            if (size, sha256) != (item["byte_size"], item["sha256"]):
                raise WorkspaceError("archive_verification_failed", f"Moved current output failed verification: {destination_relative}")
    for relative in sorted(
        emptied_current_directories,
        key=lambda value: len(PurePosixPath(value).parts),
        reverse=True,
    ):
        _secure_remove_empty_directory(root, relative)
    _secure_write_exclusive_or_same(root, f"{temp_relative}/record.json", canonical_json_bytes(record))
    _secure_rename_noreplace(root, temp_relative, final_relative)
    if current_evidence is not None:
        _secure_exchange_commit(
            root,
            "control/current.json",
            current_evidence,
            cleared_current,
        )
    validation = validate_workspace(root)
    return {
        **plan,
        "status": "archived",
        "plan_token": token,
        "validation_summary": validation["summary"],
    }


def _require_fields(record: dict[str, Any], fields: Iterable[str], label: str) -> None:
    missing = [field for field in fields if field not in record]
    if missing:
        raise WorkspaceError("record_schema_error", f"{label} is missing fields: {', '.join(missing)}")


def _validate_source_record(root: Path, record_path: Path, record: dict[str, Any]) -> str:
    fields = (
        "schema_version",
        "source_id",
        "original_relative_path",
        "current_relative_path",
        "type_class",
        "source_class",
        "source_mode",
        "byte_size",
        "sha256",
        "received_at",
        "event_at",
        "imported_at",
        "reliability",
        "derivation_links",
        "status",
    )
    _require_fields(record, fields, f"source record {record_path.name}")
    if record["schema_version"] != SCHEMA_VERSION:
        raise WorkspaceError("record_schema_error", f"Unsupported source record schema version: {record_path}")
    source_id = record["source_id"]
    if not SOURCE_ID_RE.fullmatch(source_id) or record_path.name != f"{source_id}.json":
        raise WorkspaceError("record_schema_error", f"Source ID/path mismatch: {record_path}")
    expected_source_id = _source_identifier(_source_record_identity(record))
    if source_id != expected_source_id:
        raise WorkspaceError("record_identity_mismatch", f"Source record identity was reclassified or fabricated: {record_path}")
    current = normalize_relative_path(record["current_relative_path"])
    normalize_relative_path(record["original_relative_path"])
    if not current.startswith("raw/as-received/"):
        raise WorkspaceError("raw_boundary", f"Source record points outside raw/as-received: {current}")
    if record["source_class"] not in SOURCE_CLASSES or record["reliability"] not in RELIABILITY_VALUES:
        raise WorkspaceError("record_schema_error", f"Invalid source class or reliability: {record_path}")
    if record["source_mode"] not in {"adopted", "explicit-attachment", "explicit-in-workspace"}:
        raise WorkspaceError("record_schema_error", f"Invalid source mode: {record_path}")
    if record["source_mode"] == "adopted":
        expected_current = f"raw/as-received/adopted/{record['original_relative_path']}"
        if current != expected_current:
            raise WorkspaceError("record_identity_mismatch", f"Adopted raw path differs from its original path: {record_path}")
    elif not current.startswith(f"raw/as-received/imported/{source_id}/"):
        raise WorkspaceError("record_identity_mismatch", f"Explicit raw path is not bound to its source ID: {record_path}")
    if record["source_class"] == "upstream-derived" and record["reliability"] != "unverified":
        raise WorkspaceError("upstream_reliability_mismatch", f"Upstream-derived record must be unverified: {record_path}")
    normalize_timestamp(record["received_at"], allow_unknown=True)
    normalize_timestamp(record["event_at"], allow_unknown=True)
    normalize_timestamp(record["imported_at"])
    _validate_derivation_links(root, record["derivation_links"])
    _validate_derivation_acyclic(root, source_id)
    if record["status"] != "preserved":
        raise WorkspaceError("record_schema_error", f"Raw source status must remain preserved: {record_path}")
    file_path = path_in_workspace(root, current)
    size, sha256 = hash_regular_file(file_path)
    if (size, sha256) != (record["byte_size"], record["sha256"]):
        raise WorkspaceError("raw_immutability_violation", f"Raw bytes changed after preservation: {current}")
    if classify_file(file_path) != record["type_class"]:
        raise WorkspaceError("record_schema_error", f"Source type-class mismatch: {record_path}")
    return current


def _validate_artifact_record(root: Path, record_path: Path, record: dict[str, Any]) -> str:
    fields = (
        "schema_version",
        "artifact_id",
        "kind",
        "current_relative_path",
        "type_class",
        "byte_size",
        "sha256",
        "created_at",
        "reliability",
        "derivation_links",
        "status",
    )
    _require_fields(record, fields, f"artifact record {record_path.name}")
    if record["schema_version"] != SCHEMA_VERSION:
        raise WorkspaceError("record_schema_error", f"Unsupported artifact record schema version: {record_path}")
    artifact_id = record["artifact_id"]
    if not ARTIFACT_ID_RE.fullmatch(artifact_id) or record_path.name != f"{artifact_id}.json":
        raise WorkspaceError("record_schema_error", f"Artifact ID/path mismatch: {record_path}")
    expected_artifact_id = _artifact_identifier(_artifact_record_identity(record))
    if artifact_id != expected_artifact_id:
        raise WorkspaceError("record_identity_mismatch", f"Artifact record identity was reclassified or fabricated: {record_path}")
    relative = normalize_relative_path(record["current_relative_path"])
    expected_prefix = "work/drafts/" if record["kind"] == "draft" else "work/derived/"
    if record["kind"] not in ARTIFACT_KINDS or not relative.startswith(expected_prefix):
        raise WorkspaceError("artifact_boundary", f"Artifact record path/kind mismatch: {record_path}")
    if record["reliability"] not in RELIABILITY_VALUES:
        raise WorkspaceError("record_schema_error", f"Invalid artifact reliability: {record_path}")
    expected_status = "draft" if record["kind"] == "draft" else "working"
    if record["status"] != expected_status:
        raise WorkspaceError("record_schema_error", f"Invalid artifact status: {record_path}")
    normalize_timestamp(record["created_at"])
    _validate_derivation_links(root, record["derivation_links"])
    _validate_derivation_acyclic(root, artifact_id)
    target = path_in_workspace(root, relative)
    size, sha256 = hash_regular_file(target)
    if (size, sha256) != (record["byte_size"], record["sha256"]):
        raise WorkspaceError("artifact_changed", f"Work artifact changed after registration: {relative}")
    if classify_file(target) != record["type_class"]:
        raise WorkspaceError("record_schema_error", f"Artifact type-class mismatch: {record_path}")
    return relative


def _validate_current(root: Path, current: dict[str, Any]) -> set[str]:
    _require_fields(
        current,
        ("schema_version", "status", "version_id", "decided_at", "conversation_record", "conversation_sha256", "outputs"),
        "current record",
    )
    if current["schema_version"] != SCHEMA_VERSION:
        raise WorkspaceError("current_record_invalid", "Unsupported current record schema version.")
    expected: set[str] = set()
    if current["status"] == "none":
        if current != empty_current_record():
            raise WorkspaceError("current_record_invalid", "Empty current record contains unsupported state.")
        return expected
    if current["status"] != "approved":
        raise WorkspaceError("current_record_invalid", "Current status must be none or approved.")
    version_id = _validate_version_id(current["version_id"])
    normalize_timestamp(current["decided_at"])
    _, conversation_sha = _complete_conversation(root, current["conversation_record"])
    if conversation_sha != current["conversation_sha256"]:
        raise WorkspaceError("conversation_changed", "Approval conversation changed after the current decision.")
    if not isinstance(current["outputs"], list) or not current["outputs"]:
        raise WorkspaceError("current_record_invalid", "Approved current record needs outputs.")
    for output in current["outputs"]:
        _require_fields(
            output,
            ("artifact_id", "draft_relative_path", "current_relative_path", "type_class", "byte_size", "sha256"),
            "current output",
        )
        relative = normalize_relative_path(output["current_relative_path"])
        draft_relative = normalize_relative_path(output["draft_relative_path"])
        if not draft_relative.startswith("work/drafts/"):
            raise WorkspaceError("current_record_invalid", f"Current output draft source is outside work/drafts: {draft_relative}")
        artifact_record_path = root / "control" / "artifacts" / f"{output['artifact_id']}.json"
        artifact = _load_json(artifact_record_path)
        _validate_artifact_record(root, artifact_record_path, artifact)
        if artifact.get("kind") != "draft" or artifact.get("current_relative_path") != draft_relative:
            raise WorkspaceError("current_record_invalid", f"Current output is not bound to its registered draft: {relative}")
        if (output["byte_size"], output["sha256"], output["type_class"]) != (
            artifact["byte_size"],
            artifact["sha256"],
            artifact["type_class"],
        ):
            raise WorkspaceError("current_record_invalid", f"Current output metadata differs from its draft artifact: {relative}")
        if not relative.startswith(f"formal/current/{version_id}/"):
            raise WorkspaceError("current_record_invalid", f"Current output is outside its version directory: {relative}")
        size, sha256 = hash_regular_file(path_in_workspace(root, relative))
        if (size, sha256) != (output["byte_size"], output["sha256"]):
            raise WorkspaceError("current_output_changed", f"Current output changed: {relative}")
        expected.add(relative)
    return expected


def _validate_archive_record(root: Path, record_path: Path, record: dict[str, Any]) -> set[str]:
    fields = (
        "schema_version",
        "version_id",
        "status",
        "reason",
        "replacement",
        "timestamp",
        "conversation_record",
        "conversation_sha256",
        "files",
    )
    _require_fields(record, fields, f"archive record {record_path}")
    if record["schema_version"] != SCHEMA_VERSION:
        raise WorkspaceError("archive_record_invalid", f"Unsupported archive schema version: {record_path}")
    version_id = _validate_version_id(record["version_id"])
    if record_path.parent.name != version_id or record["status"] not in ARCHIVE_STATUSES:
        raise WorkspaceError("archive_record_invalid", f"Archive version/status mismatch: {record_path}")
    if not isinstance(record["reason"], str) or not record["reason"].strip():
        raise WorkspaceError("archive_record_invalid", f"Archive reason is required: {record_path}")
    if record["replacement"] != "unknown":
        _validate_version_id(record["replacement"])
        if record["replacement"] == version_id:
            raise WorkspaceError("archive_record_invalid", f"Archive replacement cannot equal its version: {record_path}")
    normalize_timestamp(record["timestamp"])
    _, conversation_sha = _complete_conversation(root, record["conversation_record"])
    if conversation_sha != record["conversation_sha256"]:
        raise WorkspaceError("conversation_changed", f"Archive conversation changed: {record_path}")
    if not isinstance(record["files"], list) or not record["files"]:
        raise WorkspaceError("archive_record_invalid", f"Archive record needs files: {record_path}")
    expected = {f"archive/versions/{version_id}/record.json"}
    for item in record["files"]:
        _require_fields(
            item,
            ("source_relative_path", "archive_relative_path", "artifact_id", "byte_size", "sha256", "archive_method"),
            "archive file",
        )
        relative = normalize_relative_path(item["archive_relative_path"])
        source_relative = normalize_relative_path(item["source_relative_path"])
        if not ARTIFACT_ID_RE.fullmatch(item["artifact_id"]):
            raise WorkspaceError("archive_record_invalid", f"Archive artifact ID is invalid: {record_path}")
        artifact_path = root / "control" / "artifacts" / f"{item['artifact_id']}.json"
        artifact = _load_json(artifact_path)
        _validate_artifact_record(root, artifact_path, artifact)
        if artifact.get("kind") != "draft":
            raise WorkspaceError("archive_record_invalid", f"Archive file is not derived from a registered draft: {relative}")
        expected_method = "copy-preserve-draft" if record["status"] == "rejected" else "move-current"
        if item["archive_method"] != expected_method:
            raise WorkspaceError("archive_record_invalid", f"Archive method/status mismatch: {record_path}")
        if record["status"] == "rejected":
            if source_relative != artifact["current_relative_path"]:
                raise WorkspaceError("archive_record_invalid", f"Rejected archive source differs from its draft artifact: {relative}")
        elif not source_relative.startswith(f"formal/current/{version_id}/"):
            raise WorkspaceError("archive_record_invalid", f"Superseded archive source is outside its former current version: {relative}")
        if (item["byte_size"], item["sha256"]) != (
            artifact["byte_size"],
            artifact["sha256"],
        ):
            raise WorkspaceError("archive_record_invalid", f"Archive metadata differs from its artifact: {relative}")
        if not relative.startswith(f"archive/versions/{version_id}/files/"):
            raise WorkspaceError("archive_record_invalid", f"Archive file is outside its version: {relative}")
        size, sha256 = hash_regular_file(path_in_workspace(root, relative))
        if (size, sha256) != (item["byte_size"], item["sha256"]):
            raise WorkspaceError("archive_changed", f"Archived bytes changed: {relative}")
        expected.add(relative)
    return expected


def _file_paths_under(entries: list[dict[str, Any]], prefix: str) -> set[str]:
    normalized = prefix.rstrip("/") + "/"
    return {
        entry["path"]
        for entry in entries
        if entry["node"] == "file" and entry["path"].startswith(normalized)
    }


def validate_workspace(
    root_raw: os.PathLike[str] | str,
    *,
    allow_unregistered_work: bool = False,
    allow_one_unpreserved_relative: str | None = None,
) -> dict[str, Any]:
    root = validate_exact_directory(root_raw)
    for relative in LAYOUT_DIRECTORIES:
        path = path_in_workspace(root, relative)
        if is_link_like(path) or not path.is_dir():
            raise WorkspaceError("layout_invalid", f"Required real directory is missing: {relative}")
    required_files = (
        "INDEX.md",
        "control/workspace.json",
        "control/current.json",
        "conversation/00-workspace-decision.md",
        "memory/MEMORY.md",
    )
    for relative in required_files:
        path = path_in_workspace(root, relative)
        if is_link_like(path) or not path.is_file():
            raise WorkspaceError("layout_invalid", f"Required real file is missing: {relative}")
    workspace = _load_json(root / "control" / "workspace.json")
    if workspace.get("schema_version") != SCHEMA_VERSION or workspace.get("workspace_kind") != "document-workspace":
        raise WorkspaceError("workspace_record_invalid", "control/workspace.json is not this schema/version.")
    if workspace.get("selection") != "exact-root" or workspace.get("provider_calls") is not False:
        raise WorkspaceError("workspace_record_invalid", "Workspace selection/provider boundary changed.")
    daily = list((root / "memory" / "daily").glob("????-??-??.md"))
    if not daily:
        raise WorkspaceError("memory_invalid", "At least one dated daily memory scaffold is required.")

    entries = inventory_tree(root)
    source_records: list[dict[str, Any]] = []
    expected_raw: set[str] = set()
    source_dir = root / "control" / "sources"
    for record_path in sorted(source_dir.glob("*.json"), key=lambda item: (item.name.casefold(), item.name)):
        record = _load_json(record_path)
        current_raw = _validate_source_record(root, record_path, record)
        if current_raw in expected_raw:
            raise WorkspaceError("duplicate_source_path", f"Multiple source records point to the same raw file: {current_raw}")
        expected_raw.add(current_raw)
        source_records.append(record)
    actual_raw = _file_paths_under(entries, "raw")
    if actual_raw != expected_raw:
        raise WorkspaceError(
            "raw_inventory_mismatch",
            "Every raw file must have exactly one source record; agent-produced or unrecorded files are refused.",
            details={"unrecorded": sorted(actual_raw - expected_raw), "missing": sorted(expected_raw - actual_raw)},
        )

    artifact_records: list[dict[str, Any]] = []
    expected_work: set[str] = set()
    artifact_dir = root / "control" / "artifacts"
    for record_path in sorted(artifact_dir.glob("*.json"), key=lambda item: (item.name.casefold(), item.name)):
        record = _load_json(record_path)
        current_work = _validate_artifact_record(root, record_path, record)
        if current_work in expected_work:
            raise WorkspaceError("duplicate_artifact_path", f"Multiple artifact records point to the same work file: {current_work}")
        expected_work.add(current_work)
        artifact_records.append(record)
    actual_work = _file_paths_under(entries, "work/derived") | _file_paths_under(entries, "work/drafts")
    if not allow_unregistered_work and actual_work != expected_work:
        raise WorkspaceError(
            "work_inventory_mismatch",
            "Every work product must have an artifact record before downstream use.",
            details={"unregistered": sorted(actual_work - expected_work), "missing": sorted(expected_work - actual_work)},
        )

    current = _load_json(root / "control" / "current.json")
    expected_current = _validate_current(root, current)
    actual_current = _file_paths_under(entries, "formal/current")
    if actual_current != expected_current:
        raise WorkspaceError(
            "current_inventory_mismatch",
            "formal/current must contain only outputs in the explicit approved current record.",
            details={"unrecorded": sorted(actual_current - expected_current), "missing": sorted(expected_current - actual_current)},
        )

    expected_archive: set[str] = set()
    version_count = 0
    versions_dir = root / "archive" / "versions"
    for child in sorted(versions_dir.iterdir(), key=lambda item: (item.name.casefold(), item.name)):
        if is_link_like(child) or not child.is_dir() or not VERSION_RE.fullmatch(child.name):
            raise WorkspaceError("archive_collision", f"Unexpected archive node or collision evidence: {child}")
        record_path = child / "record.json"
        record = _load_json(record_path)
        expected_archive |= _validate_archive_record(root, record_path, record)
        version_count += 1
    actual_archive = _file_paths_under(entries, "archive/versions")
    if actual_archive != expected_archive:
        raise WorkspaceError(
            "archive_inventory_mismatch",
            "Archive contains unrecorded or missing files.",
            details={"unrecorded": sorted(actual_archive - expected_archive), "missing": sorted(expected_archive - actual_archive)},
        )

    managed_top = RESERVED_TOP_LEVEL
    preserved_originals: set[str] = set()
    for record in source_records:
        mode = record.get("source_mode")
        if mode == "adopted":
            preserved_originals.add(record["original_relative_path"])
        elif mode == "explicit-in-workspace":
            original_relative = normalize_relative_path(record["original_relative_path"])
            original_size, original_sha = hash_regular_file(path_in_workspace(root, original_relative))
            if (original_size, original_sha) != (record["byte_size"], record["sha256"]):
                raise WorkspaceError(
                    "received_original_changed",
                    f"The preserved in-workspace received file changed after receipt: {original_relative}",
                )
            preserved_originals.add(original_relative)
    unmanaged_files = {
        entry["path"]
        for entry in entries
        if entry["node"] == "file" and PurePosixPath(entry["path"]).parts[0].casefold() not in managed_top
    }
    allowed_unpreserved: set[str] = set()
    if allow_one_unpreserved_relative is not None:
        allowed_unpreserved.add(normalize_relative_path(allow_one_unpreserved_relative))
    unpreserved = unmanaged_files - preserved_originals
    if unpreserved - allowed_unpreserved:
        raise WorkspaceError(
            "unpreserved_workspace_file",
            "Files added outside managed paths are not preserved sources; use the preserve workflow or select another exact root.",
            details={"paths": sorted(unpreserved - allowed_unpreserved)},
        )
    if allowed_unpreserved - unpreserved:
        raise WorkspaceError(
            "preserve_source_boundary_mismatch",
            "The allowed in-workspace source is not exactly one unpreserved file at the named relative path.",
        )

    return {
        "operation": "validate",
        "status": "valid",
        "workspace": os.fspath(root),
        "summary": {
            "source_records": len(source_records),
            "artifact_records": len(artifact_records),
            "archive_versions": version_count,
            "current_status": current["status"],
            "current_version": current["version_id"],
        },
        "semantic_content_read": False,
        "byte_hashing_performed": True,
        "provider_calls": False,
    }
