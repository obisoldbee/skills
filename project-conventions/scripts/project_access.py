#!/usr/bin/env python3
"""Harness-neutral reader/writer admission for one initialized Project Root."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import platform
import re
import secrets
import sqlite3
import stat
import subprocess
import sys
import unicodedata
from datetime import datetime, timezone
from pathlib import Path, PurePosixPath


PROTOCOL_VERSION = 1
SESSION_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]{0,127}$")
SKILL_NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
CONTROL_DIRECTORY = ".project-conventions"
CONFIG_FILE = "project.json"
DATABASE_FILE = "access.sqlite3"
MANAGED_START = "<!-- project-conventions:access:start -->"
MANAGED_END = "<!-- project-conventions:access:end -->"
RESERVED_SHARED_PATHS = (
    ".project-conventions",
    ".git",
    "conversation",
    "controller",
    "docs/indexes",
    "INDEX.md",
    "MEMBERS.md",
    "memory",
)
WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{number}" for number in range(1, 10)),
    *(f"LPT{number}" for number in range(1, 10)),
}
CONFIG_KEYS = {
    "access_readme_sha256",
    "agents_block_sha256",
    "coordination_id",
    "coordination_root",
    "helper_sha256",
    "project_profile",
    "project_role",
    "project_type",
    "records_dir",
    "repository_root",
    "runtime_backend",
    "schema_version",
    "skill_package",
}


class AccessError(RuntimeError):
    """Raised when the admission protocol cannot be applied safely."""


class AccessConflict(AccessError):
    """Raised when an active claim blocks the requested mode."""


def portable_text_sha256(content: bytes) -> str:
    """Hash text after canonicalizing checkout-dependent line endings."""
    normalized = content.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(normalized).hexdigest()


def safe_config_relative(value: object, label: str) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not value or "\\" in value:
        raise AccessError(f"{label} must be a portable relative path")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise AccessError(f"{label} must be a normalized relative path")
    for part in path.parts:
        stem = part.split(".", 1)[0].upper()
        if (
            any(ord(character) < 32 or character in '<>:"|?*' for character in part)
            or part.endswith((".", " "))
            or stem in WINDOWS_RESERVED_NAMES
        ):
            raise AccessError(f"{label} is not portable across supported filesystems")
    return path.as_posix()


def safe_coordination_root(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or "\\" in value:
        raise AccessError("coordination_root must be one portable sibling path")
    path = PurePosixPath(value)
    sibling = path.parts[1] if len(path.parts) == 2 else ""
    stem = sibling.split(".", 1)[0].upper()
    if (
        len(path.parts) != 2
        or path.parts[0] != ".."
        or not SESSION_PATTERN.fullmatch(sibling)
        or sibling.endswith((".", " "))
        or stem in WINDOWS_RESERVED_NAMES
    ):
        raise AccessError("coordination_root must be exactly ../<sibling-project>")
    return path.as_posix()


def safe_coordination_id(value: object) -> str | None:
    if value is None:
        return None
    if not isinstance(value, str) or not SESSION_PATTERN.fullmatch(value):
        raise AccessError("coordination_id must be one portable project name")
    stem = value.split(".", 1)[0].upper()
    if value.endswith((".", " ")) or stem in WINDOWS_RESERVED_NAMES:
        raise AccessError("coordination_id must be one portable project name")
    return value


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat()


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


def resolve_control(script_path: Path) -> tuple[Path, Path, dict[str, object]]:
    if is_link_or_junction(script_path) or not script_path.is_file():
        raise AccessError(f"invalid project access helper: {script_path}")
    control = script_path.expanduser().absolute().parent
    if control.name != CONTROL_DIRECTORY or is_link_or_junction(control):
        raise AccessError(f"invalid project control directory: {control}")
    project_root = control.parent
    if is_link_or_junction(project_root) or not project_root.is_dir():
        raise AccessError(f"invalid Project Root: {project_root}")
    config_path = control / CONFIG_FILE
    if is_link_or_junction(config_path) or not config_path.is_file():
        raise AccessError(f"missing real project configuration: {config_path}")
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise AccessError(f"invalid project configuration: {exc}") from exc
    if config.get("schema_version") != PROTOCOL_VERSION:
        raise AccessError("unsupported project coordination schema")
    if set(config) != CONFIG_KEYS:
        raise AccessError("project configuration field set is invalid")
    if config.get("project_type") not in {"code", "document", "hybrid"}:
        raise AccessError("invalid project_type in project configuration")
    if config.get("project_profile") not in {"standard", "agent-skill"}:
        raise AccessError("invalid project_profile in project configuration")
    if config.get("project_role") not in {
        "ordinary",
        "collection-control",
        "collection-member",
    }:
        raise AccessError("invalid project_role in project configuration")
    if config.get("project_role") != "ordinary" and config.get("project_profile") != "standard":
        raise AccessError("shared collection roles require the standard project profile")
    skill_package = config.get("skill_package")
    if config.get("project_profile") == "agent-skill":
        if (
            config.get("project_type") != "code"
            or not isinstance(skill_package, str)
            or len(skill_package) > 64
            or not SKILL_NAME_PATTERN.fullmatch(skill_package)
        ):
            raise AccessError("invalid agent-skill package configuration")
    elif skill_package is not None:
        raise AccessError("standard project configuration cannot name a Skill package")
    config["repository_root"] = safe_config_relative(
        config.get("repository_root"), "repository_root"
    )
    config["records_dir"] = safe_config_relative(config.get("records_dir"), "records_dir")
    config["coordination_id"] = safe_coordination_id(config.get("coordination_id"))
    config["coordination_root"] = safe_coordination_root(config.get("coordination_root"))
    if config.get("runtime_backend") not in {
        "project-local",
        "git-common-dir",
        "collection-control",
    }:
        raise AccessError("invalid runtime_backend in project configuration")
    role = config.get("project_role")
    coordination_id = config.get("coordination_id")
    coordination_root = config.get("coordination_root")
    backend = config.get("runtime_backend")
    if role == "collection-control":
        if (
            backend != "project-local"
            or coordination_root is not None
            or coordination_id is None
            or project_root.name != coordination_id
        ):
            raise AccessError("collection-control identity or runtime configuration is invalid")
    elif role == "collection-member":
        if (
            backend != "collection-control"
            or coordination_id is None
            or coordination_root != f"../{coordination_id}"
        ):
            raise AccessError("shared-member coordination binding is invalid")
    elif coordination_id is not None or coordination_root is not None or backend == "collection-control":
        raise AccessError("coordination binding is valid only for shared collection profiles")
    helper_digest = config.get("helper_sha256")
    if not isinstance(helper_digest, str) or not secrets.compare_digest(
        helper_digest, portable_text_sha256(script_path.read_bytes())
    ):
        raise AccessError("project access helper digest differs from project configuration")
    agents_path = project_root / "AGENTS.md"
    access_path = control / "ACCESS.md"
    if is_link_or_junction(agents_path) or not agents_path.is_file():
        raise AccessError("project AGENTS.md is missing or linked")
    if is_link_or_junction(access_path) or not access_path.is_file():
        raise AccessError("project ACCESS.md is missing or linked")
    agents_text = agents_path.read_text(encoding="utf-8")
    if agents_text.count(MANAGED_START) != 1 or agents_text.count(MANAGED_END) != 1:
        raise AccessError("project AGENTS.md managed access block is missing or duplicated")
    start = agents_text.index(MANAGED_START)
    end = agents_text.index(MANAGED_END, start) + len(MANAGED_END)
    managed_block = agents_text[start:end]
    if config.get("agents_block_sha256") != hashlib.sha256(
        managed_block.encode("utf-8")
    ).hexdigest():
        raise AccessError("project AGENTS.md managed access block digest differs")
    if config.get("access_readme_sha256") != portable_text_sha256(access_path.read_bytes()):
        raise AccessError("project ACCESS.md digest differs from project configuration")
    return project_root.resolve(), control.resolve(), config


def run_git(project_root: Path, *arguments: str) -> str | None:
    completed = subprocess.run(
        ["git", "-C", str(project_root), *arguments],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        return None
    return completed.stdout.strip()


def path_identity(value: str | Path) -> str:
    return unicodedata.normalize("NFC", os.path.normpath(str(value))).casefold()


def runtime_root(
    project_root: Path, control: Path, config: dict[str, object]
) -> tuple[Path, str]:
    backend = config.get("runtime_backend")
    if backend == "project-local":
        return control / "runtime", "project-local"
    if backend == "collection-control":
        coordination_relative = str(config.get("coordination_root"))
        coordination_id = str(config.get("coordination_id"))
        coordination = project_root / coordination_relative
        if is_link_or_junction(coordination) or not coordination.is_dir():
            raise AccessError("collection coordination Project Root is missing or linked")
        coordination = coordination.resolve()
        if path_identity(coordination.parent) != path_identity(project_root.parent):
            raise AccessError("collection coordination Project Root is not an exact sibling")
        coordination_control = coordination / CONTROL_DIRECTORY
        if is_link_or_junction(coordination_control) or not coordination_control.is_dir():
            raise AccessError("collection coordination control directory is missing or linked")
        coordinator_root, verified_control, coordinator = resolve_control(
            coordination_control / "project_access.py"
        )
        if (
            path_identity(coordinator_root) != path_identity(coordination)
            or path_identity(verified_control) != path_identity(coordination_control)
            or coordinator.get("project_role") != "collection-control"
            or coordinator.get("runtime_backend") != "project-local"
            or coordinator.get("coordination_id") != coordination_id
            or coordinator.get("coordination_root") is not None
        ):
            raise AccessError("collection coordinator authority or identity differs")
        return verified_control / "runtime", "collection-control"
    if backend != "git-common-dir":
        raise AccessError("project configuration has an invalid runtime_backend")
    repository_relative = config.get("repository_root")
    repository_root = (
        project_root / str(repository_relative) if repository_relative is not None else project_root
    )
    current = project_root
    for part in repository_root.relative_to(project_root).parts:
        current = current / part
        if is_link_or_junction(current):
            raise AccessError("configured Repository Root contains a directory link")
    top = run_git(repository_root, "rev-parse", "--show-toplevel")
    common = run_git(repository_root, "rev-parse", "--git-common-dir") if top else None
    if top and common:
        top_path = Path(top).expanduser().resolve()
        if path_identity(top_path) == path_identity(repository_root.resolve()):
            common_path = Path(common)
            if not common_path.is_absolute():
                common_path = repository_root / common_path
            return common_path.resolve() / "project-conventions-access", "git-common-dir"
    raise AccessError("git-common-dir runtime requires this Project Root to be a Git worktree root")


def git_evidence(project_root: Path) -> dict[str, object]:
    top = run_git(project_root, "rev-parse", "--show-toplevel")
    if not top or path_identity(Path(top).resolve()) != path_identity(project_root):
        return {"git_backed": False}
    head = run_git(project_root, "rev-parse", "HEAD")
    branch = run_git(project_root, "symbolic-ref", "--short", "-q", "HEAD")
    git_dir_raw = run_git(project_root, "rev-parse", "--git-dir")
    common_dir_raw = run_git(project_root, "rev-parse", "--git-common-dir")
    if git_dir_raw is None or common_dir_raw is None:
        return {"git_backed": False}
    git_dir = Path(git_dir_raw)
    common_dir = Path(common_dir_raw)
    if not git_dir.is_absolute():
        git_dir = project_root / git_dir
    if not common_dir.is_absolute():
        common_dir = project_root / common_dir
    git_dir = git_dir.resolve()
    common_dir = common_dir.resolve()
    status = run_git(project_root, "status", "--porcelain=v1", "--untracked-files=normal")
    status_text = status if status is not None else "<git-status-unavailable>"
    return {
        "git_backed": True,
        "head": head or "unborn",
        "branch": branch or "detached",
        "git_dir": str(git_dir),
        "git_common_dir": str(common_dir),
        "linked_worktree": path_identity(git_dir) != path_identity(common_dir),
        "status_sha256": hashlib.sha256(status_text.encode("utf-8")).hexdigest(),
        "clean": status_text == "",
    }


def connect(database: Path) -> sqlite3.Connection:
    database.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(database, timeout=5.0, isolation_level=None)
    connection.execute("PRAGMA busy_timeout = 5000")
    connection.execute("PRAGMA journal_mode = DELETE")
    connection.execute("PRAGMA synchronous = FULL")
    connection.executescript(
        """
        CREATE TABLE IF NOT EXISTS meta (
            key TEXT PRIMARY KEY,
            value TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS claims (
            session_id TEXT PRIMARY KEY,
            mode TEXT NOT NULL CHECK (mode IN ('read-only', 'writer', 'isolated-writer')),
            token_hash TEXT NOT NULL,
            actor TEXT NOT NULL,
            workspace TEXT NOT NULL,
            acquired_at TEXT NOT NULL,
            write_paths_json TEXT NOT NULL,
            evidence_json TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS history (
            event_id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_id TEXT NOT NULL,
            mode TEXT NOT NULL,
            actor TEXT NOT NULL,
            event TEXT NOT NULL,
            occurred_at TEXT NOT NULL,
            reason TEXT NOT NULL,
            evidence_json TEXT NOT NULL
        );
        CREATE TABLE IF NOT EXISTS recovery_plans (
            session_id TEXT PRIMARY KEY,
            token_hash TEXT NOT NULL,
            claim_token_hash TEXT NOT NULL,
            reason TEXT NOT NULL,
            planned_at TEXT NOT NULL
        );
        """
    )
    connection.execute(
        "INSERT OR IGNORE INTO meta(key, value) VALUES('protocol_version', ?)",
        (str(PROTOCOL_VERSION),),
    )
    observed = connection.execute(
        "SELECT value FROM meta WHERE key = 'protocol_version'"
    ).fetchone()
    if observed is None or observed[0] != str(PROTOCOL_VERSION):
        connection.close()
        raise AccessError("runtime database uses an unsupported protocol version")
    return connection


def public_claims(connection: sqlite3.Connection) -> list[dict[str, object]]:
    rows = connection.execute(
        "SELECT session_id, mode, actor, workspace, acquired_at, write_paths_json, evidence_json "
        "FROM claims ORDER BY acquired_at, session_id"
    ).fetchall()
    return [
        {
            "session_id": row[0],
            "mode": row[1],
            "actor": row[2],
            "workspace": row[3],
            "acquired_at": row[4],
            "write_paths": json.loads(row[5]),
            "evidence": json.loads(row[6]),
        }
        for row in rows
    ]


def validate_session(value: str | None) -> str:
    if value is None:
        return secrets.token_hex(12)
    if not SESSION_PATTERN.fullmatch(value):
        raise AccessError("session must use 1-128 letters, digits, dot, underscore, or hyphen")
    return value


def token_digest(token: str) -> str:
    return hashlib.sha256(token.encode("utf-8")).hexdigest()


def normalize_write_paths(values: list[str]) -> list[str]:
    normalized: list[str] = []
    for value in values:
        if not value or value != value.strip() or "\\" in value:
            raise AccessError("write paths must be normalized workspace-relative Git paths")
        value = unicodedata.normalize("NFC", value)
        path = PurePosixPath(value)
        if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
            raise AccessError("write paths must be normalized workspace-relative Git paths")
        for part in path.parts:
            stem = part.split(".", 1)[0].upper()
            if (
                any(ord(character) < 32 or character in '<>:"|?*' for character in part)
                or part.endswith((".", " "))
                or stem in WINDOWS_RESERVED_NAMES
            ):
                raise AccessError("write paths must be portable across supported filesystems")
        candidate = path.as_posix()
        if candidate not in normalized:
            normalized.append(candidate)
    return sorted(normalized)


def path_overlap(left: str, right: str) -> bool:
    # Declared paths are a portable logical scope. Compare conservatively so a
    # plan created on a case-sensitive host cannot bypass canonical paths when
    # the same repository is used on common case-insensitive hosts.
    left = unicodedata.normalize("NFC", left).casefold()
    right = unicodedata.normalize("NFC", right).casefold()
    return left == right or left.startswith(right + "/") or right.startswith(left + "/")


def reaches_reserved(path: str) -> bool:
    return any(path_overlap(path, reserved) for reserved in RESERVED_SHARED_PATHS)


def reject_linked_write_paths(workspace: Path, write_paths: list[str]) -> None:
    for relative in write_paths:
        current = workspace
        parts = PurePosixPath(relative).parts
        for index, part in enumerate(parts):
            current = current / part
            if is_link_or_junction(current):
                raise AccessError(f"write path contains a directory/file link: {relative}")
            if current.exists() and not current.is_dir() and index < len(parts) - 1:
                raise AccessError(f"write path contains a non-directory component: {relative}")
            if not current.exists():
                break


def status(project_root: Path, database: Path, storage: str) -> dict[str, object]:
    if not database.exists():
        claims: list[dict[str, object]] = []
    else:
        with connect(database) as connection:
            claims = public_claims(connection)
    modes = [claim["mode"] for claim in claims]
    return {
        "status": "available" if "writer" not in modes else "writer_active",
        "protocol_version": PROTOCOL_VERSION,
        "project_root": str(project_root),
        "runtime_storage": storage,
        "claims": claims,
        "read_only_allowed": "writer" not in modes,
        "writer_allowed": not claims,
    }


def enter(
    project_root: Path,
    database: Path,
    storage: str,
    mode: str,
    session_id: str | None,
    actor: str,
    write_paths: list[str],
    workspace: Path | None,
) -> dict[str, object]:
    session_id = validate_session(session_id)
    actor = actor.strip()
    if not actor or len(actor) > 160:
        raise AccessError("actor must be a non-empty label of at most 160 characters")
    write_paths = normalize_write_paths(write_paths)
    if mode == "isolated-writer":
        if not write_paths:
            raise AccessError("isolated-writer requires at least one --write-path")
        reserved = [path for path in write_paths if reaches_reserved(path)]
        if reserved:
            raise AccessError(
                "isolated writers cannot claim canonical shared records: " + ", ".join(reserved)
            )
    elif write_paths:
        raise AccessError("--write-path is valid only with isolated-writer")
    if mode == "isolated-writer":
        actual_workspace = (workspace or project_root).expanduser().absolute()
        if is_link_or_junction(actual_workspace) or not actual_workspace.is_dir():
            raise AccessError("isolated-writer workspace must be a real directory")
        actual_workspace = actual_workspace.resolve()
        reject_linked_write_paths(actual_workspace, write_paths)
    else:
        if workspace is not None:
            raise AccessError("--workspace is valid only with isolated-writer")
        actual_workspace = project_root
    token = secrets.token_hex(24)
    evidence = git_evidence(actual_workspace)
    if mode == "isolated-writer":
        if not evidence.get("git_backed") or not evidence.get("linked_worktree"):
            raise AccessError("isolated-writer requires a real linked Git worktree")
        if not evidence.get("clean"):
            raise AccessError("isolated-writer worktree must be clean before admission")
        if storage != "git-common-dir":
            raise AccessError("isolated-writer requires a Git-common coordination backend")
        expected_common = database.parent.parent.resolve()
        observed_common = Path(str(evidence["git_common_dir"])).resolve()
        if path_identity(expected_common) != path_identity(observed_common):
            raise AccessError("isolated-writer belongs to a different source repository")
    acquired_at = utc_now()
    connection = connect(database)
    try:
        connection.execute("BEGIN IMMEDIATE")
        existing = connection.execute(
            "SELECT mode, actor FROM claims WHERE session_id = ?", (session_id,)
        ).fetchone()
        if existing is not None:
            connection.execute("ROLLBACK")
            raise AccessError(
                f"session already has an active {existing[0]} claim for actor {existing[1]!r}"
            )
        claims = public_claims(connection)
        conflict = mode == "writer" and bool(claims)
        if mode == "read-only" and any(claim["mode"] == "writer" for claim in claims):
            conflict = True
        if mode == "isolated-writer":
            for claim in claims:
                if claim["mode"] == "writer":
                    conflict = True
                    break
                if claim["mode"] != "isolated-writer":
                    continue
                same_workspace = path_identity(str(claim["workspace"])) == path_identity(
                    actual_workspace
                )
                overlapping = any(
                    path_overlap(left, right)
                    for left in write_paths
                    for right in claim["write_paths"]
                )
                if same_workspace or overlapping:
                    conflict = True
                    break
        if conflict:
            connection.execute("ROLLBACK")
            raise AccessConflict(json.dumps(claims, ensure_ascii=False, sort_keys=True))
        connection.execute(
            "INSERT INTO claims(session_id, mode, token_hash, actor, workspace, acquired_at, write_paths_json, evidence_json) "
            "VALUES(?, ?, ?, ?, ?, ?, ?, ?)",
            (
                session_id,
                mode,
                token_digest(token),
                actor,
                str(actual_workspace),
                acquired_at,
                json.dumps(write_paths, ensure_ascii=False, sort_keys=True),
                json.dumps(evidence, ensure_ascii=False, sort_keys=True),
            ),
        )
        connection.execute("COMMIT")
    except Exception:
        if connection.in_transaction:
            connection.execute("ROLLBACK")
        raise
    finally:
        connection.close()
    return {
        "status": "entered",
        "protocol_version": PROTOCOL_VERSION,
        "project_root": str(project_root),
        "workspace": str(actual_workspace),
        "runtime_storage": storage,
        "session_id": session_id,
        "token": token,
        "mode": mode,
        "actor": actor,
        "write_paths": write_paths,
        "acquired_at": acquired_at,
        "evidence": evidence,
        "next_action": "re-read current project and Git state before continuing",
    }


def require_claim(
    connection: sqlite3.Connection, session_id: str, token: str
) -> dict[str, object]:
    row = connection.execute(
        "SELECT mode, actor, token_hash, workspace, write_paths_json, evidence_json "
        "FROM claims WHERE session_id = ?",
        (session_id,),
    ).fetchone()
    if row is None:
        raise AccessError("active claim not found")
    if not secrets.compare_digest(row[2], token_digest(token)):
        raise AccessError("claim token does not match")
    return {
        "mode": row[0],
        "actor": row[1],
        "token_hash": row[2],
        "workspace": row[3],
        "write_paths": json.loads(row[4]),
        "evidence": json.loads(row[5]),
    }


def check_claim(
    project_root: Path, database: Path, session_id: str, token: str
) -> dict[str, object]:
    session_id = validate_session(session_id)
    if not database.exists():
        raise AccessError("runtime database does not exist")
    with connect(database) as connection:
        claim = require_claim(connection, session_id, token)
    workspace = Path(str(claim["workspace"]))
    evidence = git_evidence(workspace)
    if claim["mode"] == "isolated-writer":
        if is_link_or_junction(workspace) or not workspace.is_dir():
            raise AccessError("isolated-writer workspace no longer exists as a real directory")
        reject_linked_write_paths(workspace, list(claim["write_paths"]))
        original = dict(claim["evidence"])
        if not evidence.get("git_backed") or not evidence.get("linked_worktree"):
            raise AccessError("isolated-writer workspace is no longer a linked Git worktree")
        if (
            path_identity(str(evidence.get("git_dir")))
            != path_identity(str(original.get("git_dir")))
            or path_identity(str(evidence.get("git_common_dir")))
            != path_identity(str(original.get("git_common_dir")))
            or evidence.get("branch") != original.get("branch")
        ):
            raise AccessError("isolated-writer Git identity or branch changed after admission")
    return {
        "status": "active",
        "project_root": str(project_root),
        "session_id": session_id,
        "mode": claim["mode"],
        "actor": claim["actor"],
        "workspace": str(workspace),
        "evidence": evidence,
    }


def finish(
    project_root: Path,
    database: Path,
    session_id: str,
    token: str,
    outcome: str,
) -> dict[str, object]:
    session_id = validate_session(session_id)
    if not database.exists():
        raise AccessError("runtime database does not exist")
    connection = connect(database)
    try:
        connection.execute("BEGIN IMMEDIATE")
        claim = require_claim(connection, session_id, token)
        mode = str(claim["mode"])
        actor = str(claim["actor"])
        workspace = str(claim["workspace"])
        evidence = git_evidence(Path(workspace))
        now = utc_now()
        connection.execute(
            "INSERT INTO history(session_id, mode, actor, event, occurred_at, reason, evidence_json) "
            "VALUES(?, ?, ?, 'finished', ?, ?, ?)",
            (
                session_id,
                mode,
                actor,
                now,
                outcome,
                json.dumps(evidence, ensure_ascii=False, sort_keys=True),
            ),
        )
        connection.execute("DELETE FROM claims WHERE session_id = ?", (session_id,))
        connection.execute("DELETE FROM recovery_plans WHERE session_id = ?", (session_id,))
        connection.execute("COMMIT")
    except Exception:
        if connection.in_transaction:
            connection.execute("ROLLBACK")
        raise
    finally:
        connection.close()
    return {
        "status": "finished",
        "project_root": str(project_root),
        "session_id": session_id,
        "mode": mode,
        "outcome": outcome,
    }


def recover(
    project_root: Path,
    database: Path,
    session_id: str,
    reason: str,
    apply: bool,
    token: str | None,
) -> dict[str, object]:
    session_id = validate_session(session_id)
    reason = reason.strip()
    if not reason:
        raise AccessError("recovery requires a non-empty reason")
    if not database.exists():
        raise AccessError("runtime database does not exist")
    connection = connect(database)
    try:
        connection.execute("BEGIN IMMEDIATE")
        row = connection.execute(
            "SELECT mode, actor, evidence_json, token_hash FROM claims WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        if row is None:
            connection.execute("ROLLBACK")
            raise AccessError("active claim not found")
        if not apply:
            if token is not None:
                connection.execute("ROLLBACK")
                raise AccessError("recovery dry-run does not accept --token")
            recovery_token = secrets.token_hex(24)
            planned_at = utc_now()
            connection.execute(
                "INSERT OR REPLACE INTO recovery_plans(session_id, token_hash, claim_token_hash, reason, planned_at) "
                "VALUES(?, ?, ?, ?, ?)",
                (session_id, token_digest(recovery_token), row[3], reason, planned_at),
            )
            connection.execute("COMMIT")
            return {
                "status": "would_recover",
                "project_root": str(project_root),
                "session_id": session_id,
                "mode": row[0],
                "actor": row[1],
                "reason": reason,
                "recovery_token": recovery_token,
                "planned_at": planned_at,
            }
        if token is None:
            connection.execute("ROLLBACK")
            raise AccessError("recovery --apply requires the token from its dry-run")
        plan = connection.execute(
            "SELECT token_hash, claim_token_hash, reason FROM recovery_plans WHERE session_id = ?",
            (session_id,),
        ).fetchone()
        if (
            plan is None
            or not secrets.compare_digest(plan[0], token_digest(token))
            or not secrets.compare_digest(plan[1], row[3])
            or plan[2] != reason
        ):
            connection.execute("ROLLBACK")
            raise AccessError("recovery plan/token does not match the active claim and reason")
        now = utc_now()
        connection.execute(
            "INSERT INTO history(session_id, mode, actor, event, occurred_at, reason, evidence_json) "
            "VALUES(?, ?, ?, 'recovered', ?, ?, ?)",
            (session_id, row[0], row[1], now, reason, row[2]),
        )
        connection.execute("DELETE FROM claims WHERE session_id = ?", (session_id,))
        connection.execute("DELETE FROM recovery_plans WHERE session_id = ?", (session_id,))
        connection.execute("COMMIT")
    except Exception:
        if connection.in_transaction:
            connection.execute("ROLLBACK")
        raise
    finally:
        connection.close()
    return {
        "status": "recovered",
        "project_root": str(project_root),
        "session_id": session_id,
        "reason": reason,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)
    subparsers.add_parser("status")

    enter_parser = subparsers.add_parser("enter")
    enter_parser.add_argument(
        "--mode", choices=("read-only", "writer", "isolated-writer"), required=True
    )
    enter_parser.add_argument("--session")
    enter_parser.add_argument("--actor", required=True)
    enter_parser.add_argument("--write-path", action="append", default=[])
    enter_parser.add_argument("--workspace", type=Path)

    check_parser = subparsers.add_parser("check")
    check_parser.add_argument("--session", required=True)
    check_parser.add_argument("--token", required=True)

    finish_parser = subparsers.add_parser("finish")
    finish_parser.add_argument("--session", required=True)
    finish_parser.add_argument("--token", required=True)
    finish_parser.add_argument("--outcome", choices=("success", "failed", "aborted"), required=True)

    recover_parser = subparsers.add_parser("recover")
    recover_parser.add_argument("--session", required=True)
    recover_parser.add_argument("--reason", required=True)
    recover_parser.add_argument("--apply", action="store_true")
    recover_parser.add_argument("--token")

    arguments = parser.parse_args()
    try:
        project_root, control, config = resolve_control(Path(__file__))
        runtime, storage = runtime_root(project_root, control, config)
        database = runtime / DATABASE_FILE
        if arguments.command == "status":
            result = status(project_root, database, storage)
        elif arguments.command == "enter":
            result = enter(
                project_root,
                database,
                storage,
                arguments.mode,
                arguments.session,
                arguments.actor,
                arguments.write_path,
                arguments.workspace,
            )
        elif arguments.command == "check":
            result = check_claim(project_root, database, arguments.session, arguments.token)
        elif arguments.command == "finish":
            result = finish(
                project_root,
                database,
                arguments.session,
                arguments.token,
                arguments.outcome,
            )
        else:
            result = recover(
                project_root,
                database,
                arguments.session,
                arguments.reason,
                arguments.apply,
                arguments.token,
            )
    except AccessConflict as exc:
        print(
            json.dumps(
                {"status": "blocked", "reason": "active_claim_conflict", "claims": json.loads(str(exc))},
                ensure_ascii=False,
                sort_keys=True,
            )
        )
        return 2
    except (AccessError, OSError, sqlite3.Error, UnicodeError) as exc:
        print(
            json.dumps({"status": "error", "reason": str(exc)}, ensure_ascii=False, sort_keys=True),
            file=sys.stderr,
        )
        return 3
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
