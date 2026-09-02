#!/usr/bin/env python3
"""Safely inventory, plan, clone, and fast-forward a non-Git repository pool."""

from __future__ import annotations

import argparse
import ctypes
import datetime as dt
import errno
import hashlib
import hmac
import json
import os
from pathlib import Path
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from typing import Any
import urllib.error
import urllib.parse
import urllib.request
import uuid


SCHEMA_VERSION = 1
GITHUB_API = "https://api.github.com"
USER_AGENT = "others-manager-skill/1"
SAFE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
LICENSE_NAME = re.compile(r"^(licen[cs]e|copying|notice)(?:[._-].*)?$", re.IGNORECASE)
HEX40 = re.compile(r"^[0-9a-f]{40}$")
OPERATION_MARKERS = (
    "MERGE_HEAD",
    "CHERRY_PICK_HEAD",
    "REVERT_HEAD",
    "BISECT_LOG",
    "rebase-apply",
    "rebase-merge",
    "sequencer",
)
PLAN_ID = re.compile(r"^[0-9a-f]{64}$")
CONTROLLER_SESSION = re.compile(r"^[A-Za-z0-9._-]{1,128}$")
CONTROLLER_TOKEN = re.compile(r"^[0-9a-f]{48}$")
CONTROLLER_TOKEN_ENV = "OTHERS_MANAGER_CONTROLLER_TOKEN"
PROJECT_ACCESS_STDIN_BRIDGE = (
    "import runpy,sys\n"
    "helper,session=sys.argv[1:3]\n"
    "token=sys.stdin.readline().rstrip('\\n')\n"
    "sys.argv=[helper,'check','--session',session,'--token',token]\n"
    "runpy.run_path(helper,run_name='__main__')\n"
)
SAFE_CORE_CONFIG: dict[str, set[str]] = {
    "core.repositoryformatversion": {"0"},
    "core.filemode": {"true", "false"},
    "core.bare": {"false"},
    "core.logallrefupdates": {"true"},
    "core.ignorecase": {"true", "false"},
    "core.precomposeunicode": {"true", "false"},
}
SAFE_ARBITRARY_CONFIG = {"user.name", "user.email"}
BRANCH_CONFIG = re.compile(r"^branch\.([A-Za-z0-9][A-Za-z0-9._/-]*)\.(remote|merge)$", re.IGNORECASE)
TRUSTED_GIT = Path("/usr/bin/git")


class ManagerError(RuntimeError):
    """A contract failure that should be shown without a traceback."""


def runtime_supported() -> bool:
    """Return whether the host supplies the POSIX safety primitives used here."""
    return sys.platform == "darwin" or sys.platform.startswith("linux")


def require_supported_runtime() -> None:
    if not runtime_supported():
        raise ManagerError("others-manager runtime operations require macOS or Linux")


def now_utc() -> str:
    return dt.datetime.now(dt.timezone.utc).replace(microsecond=0).isoformat()


def canonical_json(value: Any) -> str:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def seal_plan(payload: dict[str, Any]) -> dict[str, Any]:
    sealed = dict(payload)
    sealed["plan_id"] = hashlib.sha256(canonical_json(payload).encode("utf-8")).hexdigest()
    return sealed


def verify_plan(plan: dict[str, Any], kind: str) -> None:
    if plan.get("schema_version") != SCHEMA_VERSION:
        raise ManagerError("unsupported plan schema")
    if plan.get("kind") != kind:
        raise ManagerError(f"expected {kind} plan")
    plan_id = plan.get("plan_id")
    if not isinstance(plan_id, str):
        raise ManagerError("plan_id is missing")
    unsigned = dict(plan)
    unsigned.pop("plan_id", None)
    expected = hashlib.sha256(canonical_json(unsigned).encode("utf-8")).hexdigest()
    if not hmac.compare_digest(plan_id, expected):
        raise ManagerError("plan digest mismatch")
    if kind == "others-manager-update-plan":
        validate_update_plan_shape(plan)
    elif kind == "others-manager-clone-plan":
        validate_clone_plan_shape(plan)


def validate_repository_names(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(name, str) for name in value):
        raise ManagerError(f"{field} must be a list of repository names")
    names = [validate_child_name(name) for name in value]
    if len({name.casefold() for name in names}) != len(names):
        raise ManagerError(f"{field} contains duplicate names")
    if names != sorted(names, key=str.casefold):
        raise ManagerError(f"{field} must be sorted")
    return names


def validate_entry_names(value: Any, field: str) -> list[str]:
    if not isinstance(value, list) or not all(isinstance(name, str) and name and "/" not in name for name in value):
        raise ManagerError(f"{field} must be a list of direct entry names")
    if len({name.casefold() for name in value}) != len(value):
        raise ManagerError(f"{field} contains case-folding duplicates")
    if value != sorted(value, key=str.casefold):
        raise ManagerError(f"{field} must be sorted")
    return value


def validate_branch(branch: Any) -> str:
    if not isinstance(branch, str) or not branch:
        raise ManagerError("plan branch is invalid")
    if run_git(["check-ref-format", "--branch", branch], check=False).returncode != 0:
        raise ManagerError("plan branch is unsafe")
    return branch


def validate_update_plan_shape(plan: dict[str, Any]) -> None:
    pool_value = plan.get("pool")
    if not isinstance(pool_value, str) or not Path(pool_value).is_absolute():
        raise ManagerError("plan pool must be an absolute path")
    validate_fingerprint_shape(plan.get("pool_fingerprint"), "pool_fingerprint")
    names = validate_repository_names(plan.get("repository_names"), "repository_names")
    repositories = plan.get("repositories")
    if not isinstance(repositories, list) or len(repositories) != len(names):
        raise ManagerError("plan repositories do not match repository_names")
    for expected_name, item in zip(names, repositories):
        if not isinstance(item, dict) or item.get("name") != expected_name:
            raise ManagerError("plan repository order or name is invalid")
        if item.get("path") != str(Path(pool_value) / expected_name):
            raise ManagerError("plan repository path is outside its direct child")
        validate_fingerprint_shape(item.get("fingerprint"), "repository fingerprint")
        validate_fingerprint_shape(item.get("git_fingerprint"), "repository Git fingerprint")
        blockers = item.get("blockers")
        if not isinstance(blockers, list) or not all(isinstance(reason, str) for reason in blockers):
            raise ManagerError("plan blockers must be a list of strings")
        advisories = item.get("advisories")
        if not isinstance(advisories, list) or not all(isinstance(reason, str) for reason in advisories):
            raise ManagerError("plan advisories must be a list of strings")
        if item.get("action") not in {"blocked", "already_current", "fast_forward_candidate"}:
            raise ManagerError("plan action is invalid")
        if blockers:
            if item.get("action") != "blocked":
                raise ManagerError("blocked repository must have blocked action")
            continue
        if item.get("action") == "blocked":
            raise ManagerError("safe repository cannot have blocked action")
        branch = validate_branch(item.get("branch"))
        canonical_url = item.get("canonical_url")
        identity = item.get("identity")
        if not isinstance(canonical_url, str) or not isinstance(identity, str):
            raise ManagerError("safe plan repository lacks GitHub identity")
        normalized = normalize_github_url(canonical_url)
        if normalized["canonical_url"] != canonical_url or normalized["identity"].casefold() != identity.casefold():
            raise ManagerError("safe plan repository identity is not canonical")
        if item.get("upstream") != f"origin/{branch}" or item.get("clean") is not True:
            raise ManagerError("safe plan repository branch state is invalid")
        if not isinstance(item.get("licenses"), list):
            raise ManagerError("safe plan repository license files must be a list")
        if not HEX40.fullmatch(str(item.get("head", ""))) or not HEX40.fullmatch(str(item.get("remote_head", ""))):
            raise ManagerError("safe plan repository commit evidence is invalid")
        github_snapshot = item.get("github_snapshot")
        validate_update_github_snapshot_shape(github_snapshot)
        if (
            github_snapshot["identity"].casefold() != identity.casefold()
            or github_snapshot["canonical_url"] != canonical_url
            or github_snapshot["default_branch"] != branch
            or github_snapshot["remote_head"] != item["remote_head"]
        ):
            raise ManagerError("safe plan repository contradicts GitHub snapshot")
        expected_action = "already_current" if item["head"] == item["remote_head"] else "fast_forward_candidate"
        if item.get("action") != expected_action:
            raise ManagerError("safe plan repository action contradicts commit evidence")


def validate_clone_plan_shape(plan: dict[str, Any]) -> None:
    pool_value = plan.get("pool")
    if not isinstance(pool_value, str) or not Path(pool_value).is_absolute():
        raise ManagerError("plan pool must be an absolute path")
    validate_fingerprint_shape(plan.get("pool_fingerprint"), "pool_fingerprint")
    names = validate_repository_names(plan.get("repository_names_before"), "repository_names_before")
    entry_names = validate_entry_names(plan.get("entry_names_before"), "entry_names_before")
    destination = validate_child_name(plan.get("destination")) if isinstance(plan.get("destination"), str) else None
    if destination is None or destination.casefold() in {name.casefold() for name in entry_names}:
        raise ManagerError("clone destination conflicts with the planned repository set")
    repository = plan.get("repository")
    if not isinstance(repository, dict):
        raise ManagerError("clone plan repository is invalid")
    canonical_url = repository.get("canonical_url")
    identity = repository.get("identity")
    identity_key = repository.get("identity_key")
    if not all(isinstance(value, str) for value in (canonical_url, identity, identity_key)):
        raise ManagerError("clone plan GitHub identity is incomplete")
    normalized = normalize_github_url(canonical_url)
    if (
        normalized["canonical_url"] != canonical_url
        or normalized["identity"].casefold() != identity.casefold()
        or normalized["identity_key"] != identity_key
    ):
        raise ManagerError("clone plan GitHub identity is not canonical")
    validate_branch(repository.get("default_branch"))
    if not HEX40.fullmatch(str(repository.get("remote_head", ""))):
        raise ManagerError("clone plan remote head is invalid")
    validate_license_snapshot_shape(repository.get("license"), "clone plan license")


def validate_fingerprint_shape(value: Any, field: str) -> None:
    if not isinstance(value, dict) or set(value) != {"device", "inode", "mode"}:
        raise ManagerError(f"{field} is invalid")
    if not all(isinstance(value[key], int) and value[key] >= 0 for key in value):
        raise ManagerError(f"{field} is invalid")


def validate_github_snapshot_shape(repository: Any) -> None:
    if not isinstance(repository, dict):
        raise ManagerError("GitHub snapshot is invalid")
    canonical_url = repository.get("canonical_url")
    identity = repository.get("identity")
    identity_key = repository.get("identity_key")
    if not all(isinstance(value, str) for value in (canonical_url, identity, identity_key)):
        raise ManagerError("GitHub snapshot identity is incomplete")
    normalized = normalize_github_url(canonical_url)
    if (
        normalized["canonical_url"] != canonical_url
        or normalized["identity"].casefold() != identity.casefold()
        or normalized["identity_key"] != identity_key
    ):
        raise ManagerError("GitHub snapshot identity is not canonical")
    validate_branch(repository.get("default_branch"))
    if not HEX40.fullmatch(str(repository.get("remote_head", ""))):
        raise ManagerError("GitHub snapshot remote head is invalid")
    validate_license_snapshot_shape(repository.get("license"), "GitHub snapshot license")


def validate_update_github_snapshot_shape(repository: Any) -> None:
    if not isinstance(repository, dict):
        raise ManagerError("GitHub update snapshot is invalid")
    canonical_url = repository.get("canonical_url")
    identity = repository.get("identity")
    identity_key = repository.get("identity_key")
    if not all(isinstance(value, str) for value in (canonical_url, identity, identity_key)):
        raise ManagerError("GitHub update snapshot identity is incomplete")
    normalized = normalize_github_url(canonical_url)
    if (
        normalized["canonical_url"] != canonical_url
        or normalized["identity"].casefold() != identity.casefold()
        or normalized["identity_key"] != identity_key
    ):
        raise ManagerError("GitHub update snapshot identity is not canonical")
    validate_branch(repository.get("default_branch"))
    if not HEX40.fullmatch(str(repository.get("remote_head", ""))):
        raise ManagerError("GitHub update snapshot remote head is invalid")
    validate_license_snapshot_shape(repository.get("license"), "GitHub update snapshot license")


def validate_license_snapshot_shape(value: Any, field: str) -> None:
    if not isinstance(value, dict):
        raise ManagerError(f"{field} evidence is invalid")
    status = value.get("status")
    spdx = value.get("spdx_id")
    license_path = value.get("path")
    blob_sha = value.get("blob_sha")
    reason = value.get("reason")
    if status == "verified":
        if not isinstance(spdx, str) or spdx.upper() in {"", "NOASSERTION", "OTHER"}:
            raise ManagerError(f"{field} SPDX evidence is invalid")
        if not isinstance(license_path, str) or "/" in license_path or not LICENSE_NAME.fullmatch(license_path):
            raise ManagerError(f"{field} path is invalid")
        if not HEX40.fullmatch(str(blob_sha)) or reason is not None:
            raise ManagerError(f"{field} blob evidence is invalid")
        return
    if status == "unverified":
        if any(value is not None for value in (spdx, license_path, blob_sha)):
            raise ManagerError(f"{field} unverified evidence is contradictory")
        if not isinstance(reason, str) or not reason:
            raise ManagerError(f"{field} unverified reason is missing")
        return
    raise ManagerError(f"{field} status is invalid")


def normalized_system_temp_path(path_value: str) -> Path:
    path = Path(path_value)
    if not path.is_absolute():
        raise ManagerError("plan and report paths must be absolute")
    parent = path.parent
    if parent.is_symlink() or not parent.is_dir():
        raise ManagerError("plan and report parent must be an existing real directory")
    candidate = parent.resolve(strict=True) / path.name
    if path != candidate:
        raise ManagerError("plan and report paths must be exact normalized real paths")
    allowed_roots: list[Path] = []
    for root_value in (tempfile.gettempdir(), "/private/tmp", "/tmp"):
        root = Path(root_value)
        if root.exists():
            resolved = root.resolve(strict=True)
            if resolved not in allowed_roots:
                allowed_roots.append(resolved)
    if candidate.parent not in allowed_roots:
        raise ManagerError("plan and report paths must be direct files in a system temporary directory")
    return path


def load_plan(path_value: str, kind: str, expected_plan_id: str) -> dict[str, Any]:
    if not PLAN_ID.fullmatch(expected_plan_id):
        raise ManagerError("expected plan ID must be a lowercase SHA-256 digest")
    path = normalized_system_temp_path(path_value)
    flags = os.O_RDONLY
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    try:
        descriptor = os.open(path, flags)
    except OSError as exc:
        raise ManagerError(f"cannot open plan safely: {exc}") from exc
    try:
        metadata = os.fstat(descriptor)
        if not stat.S_ISREG(metadata.st_mode) or metadata.st_size > 16 * 1024 * 1024:
            raise ManagerError("plan must be a bounded real regular file")
        with os.fdopen(descriptor, "r", encoding="utf-8") as handle:
            descriptor = -1
            value = json.load(handle)
        current = path.lstat()
        if path.is_symlink() or (current.st_dev, current.st_ino) != (metadata.st_dev, metadata.st_ino):
            raise ManagerError("plan path identity changed while it was opened")
    except (OSError, json.JSONDecodeError) as exc:
        raise ManagerError(f"cannot read plan: {exc}") from exc
    finally:
        if descriptor >= 0:
            os.close(descriptor)
    if not isinstance(value, dict):
        raise ManagerError("plan root must be an object")
    verify_plan(value, kind)
    if not hmac.compare_digest(value["plan_id"], expected_plan_id):
        raise ManagerError("reviewed plan ID does not match the opened plan")
    return value


def ensure_output_available(path_value: str) -> Path:
    path = normalized_system_temp_path(path_value)
    if path.exists() or path.is_symlink():
        raise ManagerError(f"refusing to overwrite output: {path}")
    return path


def path_fingerprint(path: Path, *, require_directory: bool = True) -> dict[str, int]:
    try:
        metadata = path.lstat()
    except OSError as exc:
        raise ManagerError(f"cannot fingerprint path: {path.name}") from exc
    if path.is_symlink() or (require_directory and not stat.S_ISDIR(metadata.st_mode)):
        raise ManagerError(f"path is not a real directory: {path.name}")
    return {"device": metadata.st_dev, "inode": metadata.st_ino, "mode": stat.S_IFMT(metadata.st_mode)}


def same_fingerprint(path: Path, expected: dict[str, int]) -> bool:
    try:
        return path_fingerprint(path) == expected
    except ManagerError:
        return False


def write_json_exclusive(path: Path, value: dict[str, Any]) -> None:
    flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
    if hasattr(os, "O_NOFOLLOW"):
        flags |= os.O_NOFOLLOW
    data = (json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    try:
        fd = os.open(path, flags, 0o600)
    except OSError as exc:
        raise ManagerError(f"cannot create output exclusively: {path}: {exc}") from exc
    try:
        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
    except Exception:
        try:
            path.unlink()
        except OSError:
            pass
        raise


def reserve_operation_receipt(path_value: str, operation: str, pool: Path, plan_id: str) -> dict[str, Any]:
    path = ensure_output_available(path_value)
    nonce = uuid.uuid4().hex
    initial = {
        "schema_version": SCHEMA_VERSION,
        "kind": "others-manager-operation-receipt",
        "status": "in_progress",
        "operation": operation,
        "pool": str(pool),
        "plan_id": plan_id,
        "receipt_nonce": nonce,
        "started_at": now_utc(),
    }
    write_json_exclusive(path, initial)
    metadata = path.lstat()
    return {"path": path, "inode": metadata.st_ino, "device": metadata.st_dev, "nonce": nonce, "initial": initial}


def receipt_is_owned(receipt: dict[str, Any]) -> bool:
    path: Path = receipt["path"]
    try:
        metadata = path.lstat()
        if path.is_symlink() or not stat.S_ISREG(metadata.st_mode):
            return False
        if (metadata.st_dev, metadata.st_ino) != (receipt["device"], receipt["inode"]):
            return False
        current = json.loads(path.read_text(encoding="utf-8"))
        return current.get("receipt_nonce") == receipt["nonce"] and current.get("status") == "in_progress"
    except (OSError, json.JSONDecodeError, AttributeError):
        return False


def finalize_operation_receipt(receipt: dict[str, Any], value: dict[str, Any]) -> None:
    if not receipt_is_owned(receipt):
        raise ManagerError("operation receipt ownership changed before finalization")
    path: Path = receipt["path"]
    completed = dict(value)
    completed["receipt_nonce"] = receipt["nonce"]
    completed["receipt_status"] = "complete" if completed.get("status") != "failed" else "failed"
    temporary = path.with_name(f".{path.name}.others-manager-{uuid.uuid4().hex}.tmp")
    write_json_exclusive(temporary, completed)
    try:
        if not receipt_is_owned(receipt):
            raise ManagerError("operation receipt ownership changed during finalization")
        os.replace(temporary, path)
        directory_fd = os.open(path.parent, os.O_RDONLY)
        try:
            os.fsync(directory_fd)
        finally:
            os.close(directory_fd)
    finally:
        if temporary.exists() and not temporary.is_symlink():
            temporary.unlink()


def failed_operation_receipt(receipt: dict[str, Any], error: str) -> dict[str, Any]:
    initial = receipt["initial"]
    return {
        "schema_version": SCHEMA_VERSION,
        "kind": "others-manager-operation-receipt",
        "status": "failed",
        "operation": initial["operation"],
        "pool": initial["pool"],
        "plan_id": initial["plan_id"],
        "started_at": initial["started_at"],
        "finished_at": now_utc(),
        "error": error,
    }


def finalize_lock_cleanup_receipt(
    receipt: dict[str, Any],
    lock: dict[str, Any] | None,
) -> tuple[bool, list[str]]:
    released = lock is not None and release_operation_lock(lock)
    if lock is None:
        release_result = "not_acquired"
        blockers: list[str] = []
        lock_path = None
    elif released:
        release_result = "released"
        blockers = []
        lock_path = str(lock["path"])
    else:
        release_result = "retained_requires_review"
        blockers = ["controller operation lock cleanup requires review"]
        lock_path = str(lock["path"])
    initial = receipt["initial"]
    finalize_operation_receipt(
        receipt,
        {
            "schema_version": SCHEMA_VERSION,
            "kind": "others-manager-lock-cleanup-report",
            "status": "complete",
            "operation": initial["operation"],
            "pool": initial["pool"],
            "plan_id": initial["plan_id"],
            "started_at": initial["started_at"],
            "finished_at": now_utc(),
            "release_result": release_result,
            "lock_path": lock_path,
            "blockers": blockers,
        },
    )
    return released, blockers


def operation_lock_root() -> Path:
    for candidate in (Path("/private/tmp"), Path(tempfile.gettempdir()), Path("/tmp")):
        if candidate.exists() and not candidate.is_symlink() and candidate.is_dir():
            return candidate.resolve(strict=True)
    raise ManagerError("no real system temporary root is available for the operation lock")


def acquire_operation_lock(pool: Path, plan_id: str) -> dict[str, Any]:
    digest = hashlib.sha256(str(pool).encode("utf-8")).hexdigest()[:24]
    path = operation_lock_root() / f".others-manager-lock-{digest}"
    try:
        os.mkdir(path, 0o700)
    except FileExistsError as exc:
        raise ManagerError(f"another controller operation holds the pool lock: {path}") from exc
    except OSError as exc:
        raise ManagerError("cannot acquire the controller operation lock") from exc
    token = uuid.uuid4().hex
    marker = path / "owner.json"
    try:
        write_json_exclusive(
            marker,
            {
                "schema_version": SCHEMA_VERSION,
                "kind": "others-manager-operation-lock",
                "pool": str(pool),
                "plan_id": plan_id,
                "token": token,
                "acquired_at": now_utc(),
            },
        )
        metadata = path.lstat()
    except Exception:
        try:
            if marker.exists() and not marker.is_symlink():
                marker.unlink()
            path.rmdir()
        except OSError:
            pass
        raise
    return {"path": path, "inode": metadata.st_ino, "device": metadata.st_dev, "token": token, "marker": marker}


def release_operation_lock(lock: dict[str, Any]) -> bool:
    path: Path = lock["path"]
    marker: Path = lock["marker"]
    try:
        metadata = path.lstat()
        if path.is_symlink() or not path.is_dir():
            return False
        if (metadata.st_dev, metadata.st_ino) != (lock["device"], lock["inode"]):
            return False
        if marker.is_symlink():
            return False
        value = json.loads(marker.read_text(encoding="utf-8"))
        if value.get("token") != lock["token"]:
            return False
        marker.unlink()
        path.rmdir()
        return True
    except (OSError, json.JSONDecodeError, AttributeError):
        return False


def emit(value: dict[str, Any], output: str | None = None) -> None:
    if output is not None:
        write_json_exclusive(ensure_output_available(output), value)
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def git_environment() -> dict[str, str]:
    return {
        "PATH": "/usr/bin:/bin",
        "HOME": "/var/empty" if Path("/var/empty").is_dir() else "/",
        "LANG": "C",
        "LC_ALL": "C",
        "GIT_TERMINAL_PROMPT": "0",
        "GIT_OPTIONAL_LOCKS": "0",
        "GIT_ASKPASS": "/usr/bin/false",
        "SSH_ASKPASS": "/usr/bin/false",
        "GIT_CONFIG_NOSYSTEM": "1",
        "GIT_CONFIG_GLOBAL": os.devnull,
    }


def trusted_git() -> str:
    try:
        metadata = TRUSTED_GIT.lstat()
    except OSError as exc:
        raise ManagerError("trusted system Git is unavailable") from exc
    if TRUSTED_GIT.is_symlink() or not stat.S_ISREG(metadata.st_mode):
        raise ManagerError("trusted system Git path is not a regular file")
    if metadata.st_uid != 0 or metadata.st_mode & 0o022:
        raise ManagerError("trusted system Git permissions are unsafe")
    return str(TRUSTED_GIT)


def run_git(
    args: list[str],
    *,
    cwd: Path | None = None,
    timeout: int = 120,
    check: bool = True,
) -> subprocess.CompletedProcess[str]:
    require_supported_runtime()
    environment = git_environment()
    if cwd is None:
        # Remote probes and clones must not inherit the caller's repository config.
        cwd = Path(environment["HOME"]).resolve(strict=True)
        if (cwd / ".git").exists() or (cwd / ".git").is_symlink():
            raise ManagerError("repository-independent Git directory contains .git")
        environment["GIT_CEILING_DIRECTORIES"] = str(cwd.parent)
    command = [
        trusted_git(),
        "-c",
        "core.hooksPath=/dev/null",
        "-c",
        "core.fsmonitor=false",
        "-c",
        "core.alternateRefsCommand=",
        "-c",
        "core.sshCommand=/usr/bin/false",
        "-c",
        "submodule.recurse=false",
        "-c",
        "credential.helper=",
        "-c",
        "http.extraHeader=",
        "-c",
        "http.cookieFile=",
        "-c",
        "http.proxy=",
        "-c",
        # Leave client cert/key paths unset; empty values are not a disable switch.
        "http.sslVerify=true",
        "-c",
        "protocol.ext.allow=never",
        "-c",
        "protocol.file.allow=never",
        *args,
    ]
    try:
        result = subprocess.run(
            command,
            cwd=cwd,
            env=environment,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=timeout,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ManagerError(f"git command could not run: {args[0]}") from exc
    if check and result.returncode != 0:
        raise ManagerError(f"git command failed: {args[0]} (exit {result.returncode})")
    return result


def git_text(repo: Path, args: list[str]) -> str:
    return run_git(args, cwd=repo).stdout.strip()


def validate_pool(path_value: str) -> Path:
    supplied = Path(path_value)
    if not supplied.is_absolute():
        raise ManagerError("pool path must be absolute")
    if supplied.is_symlink() or not supplied.is_dir():
        raise ManagerError("pool must be an existing real directory")
    pool = supplied.resolve(strict=True)
    if supplied != pool:
        raise ManagerError("pool path must be the exact normalized real path")
    if (pool / ".git").exists() or (pool / ".git").is_symlink():
        raise ManagerError("pool root must not contain .git")
    return pool


def validate_controller_capability(
    controller_project_value: str,
    controller_session: str,
    pool: Path,
) -> dict[str, str]:
    require_supported_runtime()
    token = os.environ.get(CONTROLLER_TOKEN_ENV, "")
    if not CONTROLLER_SESSION.fullmatch(controller_session):
        raise ManagerError("controller session has an invalid format")
    if not CONTROLLER_TOKEN.fullmatch(token):
        raise ManagerError(f"controller writer token is missing from {CONTROLLER_TOKEN_ENV}")

    supplied = Path(controller_project_value)
    if not supplied.is_absolute() or supplied.is_symlink() or not supplied.is_dir():
        raise ManagerError("controller project must be an exact real absolute directory")
    controller_project = supplied.resolve(strict=True)
    expected_controller = pool.parent / "others-manager"
    if supplied != controller_project or controller_project != expected_controller:
        raise ManagerError("controller project does not match the pool's exact others-manager wrapper")

    package_root = Path(__file__).resolve(strict=True).parents[1]
    expected_package = pool.parent / "GitHub" / "others-manager"
    if package_root != expected_package.resolve(strict=True):
        raise ManagerError("running Skill source does not match the pool's public package topology")
    projection = controller_project / "src" / "others-manager"
    try:
        projection_target = os.readlink(projection)
        projection_resolved = projection.resolve(strict=True)
    except OSError as exc:
        raise ManagerError("controller project lacks the exact Skill source projection") from exc
    if projection_target != "../../GitHub/others-manager" or projection_resolved != package_root:
        raise ManagerError("controller project Skill projection does not match the running package")

    helper = controller_project / ".project-conventions" / "project_access.py"
    try:
        helper_metadata = helper.lstat()
    except OSError as exc:
        raise ManagerError("controller project access helper is unavailable") from exc
    if (
        helper.is_symlink()
        or not stat.S_ISREG(helper_metadata.st_mode)
        or helper_metadata.st_uid != os.getuid()
        or helper_metadata.st_mode & 0o022
    ):
        raise ManagerError("controller project access helper permissions are unsafe")

    try:
        result = subprocess.run(
            [
                sys.executable,
                "-I",
                "-B",
                "-c",
                PROJECT_ACCESS_STDIN_BRIDGE,
                str(helper),
                controller_session,
            ],
            cwd=controller_project,
            env={
                "PATH": "/usr/bin:/bin",
                "HOME": "/var/empty" if Path("/var/empty").is_dir() else "/",
                "LANG": "C",
                "LC_ALL": "C",
            },
            text=True,
            input=token + "\n",
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            timeout=15,
            check=False,
        )
    except (OSError, subprocess.TimeoutExpired) as exc:
        raise ManagerError("controller writer capability check could not run") from exc
    if result.returncode != 0:
        raise ManagerError("controller writer capability is not active")
    try:
        evidence = json.loads(result.stdout)
    except json.JSONDecodeError as exc:
        raise ManagerError("controller writer capability returned invalid evidence") from exc
    expected = {
        "status": "active",
        "project_root": str(controller_project),
        "session_id": controller_session,
        "mode": "writer",
        "workspace": str(controller_project),
    }
    if not isinstance(evidence, dict) or any(evidence.get(key) != value for key, value in expected.items()):
        raise ManagerError("controller capability is not an exclusive writer for this wrapper")
    return {
        "project_root": str(controller_project),
        "session_id": controller_session,
        "mode": "writer",
    }


def validate_child_name(name: str) -> str:
    if not SAFE_NAME.fullmatch(name) or name in {".", ".."} or name.startswith(".others-manager-"):
        raise ManagerError(f"unsafe destination name: {name}")
    return name


def normalize_github_url(value: str) -> dict[str, str]:
    raw = value.strip()
    owner: str | None = None
    repo: str | None = None
    scp = re.fullmatch(r"git@github\.com:([^/]+)/([^/]+)", raw, re.IGNORECASE)
    if scp:
        owner, repo = scp.groups()
    else:
        parsed = urllib.parse.urlsplit(raw)
        if parsed.scheme not in {"https", "http", "ssh", "git"}:
            raise ManagerError("repository URL must use an explicit supported scheme")
        if (parsed.hostname or "").casefold() != "github.com":
            raise ManagerError("repository origin must be github.com")
        if parsed.password is not None or (parsed.username not in {None, "git"}):
            raise ManagerError("credential-bearing repository URLs are not allowed")
        if parsed.query or parsed.fragment:
            raise ManagerError("repository URL must not contain query or fragment data")
        parts = [urllib.parse.unquote(item) for item in parsed.path.split("/") if item]
        if len(parts) != 2:
            raise ManagerError("GitHub repository URL must contain exactly owner/repository")
        owner, repo = parts
    assert owner is not None and repo is not None
    if repo.casefold().endswith(".git"):
        repo = repo[:-4]
    if not SAFE_NAME.fullmatch(owner) or not SAFE_NAME.fullmatch(repo):
        raise ManagerError("GitHub owner or repository name is unsafe")
    identity = f"{owner}/{repo}"
    return {
        "owner": owner,
        "repo": repo,
        "identity": identity,
        "identity_key": identity.casefold(),
        "canonical_url": f"https://github.com/{owner}/{repo}.git",
    }


def top_level_licenses(repo: Path) -> list[str]:
    names: list[str] = []
    try:
        children = list(repo.iterdir())
    except OSError:
        return names
    for child in children:
        if child.is_symlink() or not child.is_file():
            continue
        if LICENSE_NAME.fullmatch(child.name):
            names.append(child.name)
    return sorted(names, key=str.casefold)


def git_dir_for(repo: Path) -> Path:
    value = git_text(repo, ["rev-parse", "--git-dir"])
    path = Path(value)
    if not path.is_absolute():
        path = repo / path
    return path.resolve(strict=True)


def operation_markers(repo: Path) -> list[str]:
    try:
        git_dir = git_dir_for(repo)
    except ManagerError:
        return ["unreadable-git-dir"]
    return [name for name in OPERATION_MARKERS if (git_dir / name).exists()]


def executable_local_config(repo: Path) -> list[str]:
    result = run_git(
        ["config", "--local", "--no-includes", "--null", "--list"],
        cwd=repo,
        check=False,
    )
    if result.returncode != 0:
        return ["unreadable-local-config"]
    categories: set[str] = set()
    entries: dict[str, list[tuple[str, str]]] = {}
    for record in result.stdout.split("\0"):
        if not record:
            continue
        if "\n" not in record:
            categories.add("malformed-local-config")
            continue
        key, value = record.split("\n", 1)
        entries.setdefault(key.casefold(), []).append((key, value))

    for folded_key, values in entries.items():
        if len(values) != 1:
            categories.add("duplicate-local-config-key")
            continue
        key, value = values[0]
        if folded_key in SAFE_CORE_CONFIG:
            if value.casefold() not in SAFE_CORE_CONFIG[folded_key]:
                categories.add("unsafe-core-config-value")
        elif folded_key in SAFE_ARBITRARY_CONFIG:
            if "\0" in value or "\n" in value:
                categories.add("unsafe-user-config-value")
        elif folded_key == "remote.origin.url":
            try:
                normalize_github_url(value)
            except ManagerError:
                categories.add("unsafe-origin-url")
        elif folded_key == "remote.origin.fetch":
            if value != "+refs/heads/*:refs/remotes/origin/*":
                categories.add("unsafe-origin-fetch")
        elif folded_key == "remote.origin.tagopt":
            if value != "--no-tags":
                categories.add("unsafe-origin-tag-policy")
        else:
            branch_match = BRANCH_CONFIG.fullmatch(key)
            if branch_match is None:
                categories.add("unsupported-local-config-key")
                continue
            branch, field = branch_match.groups()
            if field.casefold() == "remote" and value != "origin":
                categories.add("unsafe-branch-config")
            elif field.casefold() == "merge" and value != f"refs/heads/{branch}":
                categories.add("unsafe-branch-config")
    return sorted(categories)


def discover_repositories(pool: Path) -> tuple[list[Path], list[dict[str, str]]]:
    repositories: list[Path] = []
    ignored: list[dict[str, str]] = []
    for child in sorted(pool.iterdir(), key=lambda item: item.name.casefold()):
        if child.is_symlink():
            ignored.append({"name": child.name, "reason": "symlink_not_followed"})
            continue
        if not child.is_dir():
            continue
        git_entry = child / ".git"
        if git_entry.exists() or git_entry.is_symlink():
            repositories.append(child)
    return repositories, ignored


def inspect_repository(repo: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "name": repo.name,
        "path": str(repo),
        "fingerprint": None,
        "git_fingerprint": None,
        "identity": None,
        "canonical_url": None,
        "branch": None,
        "upstream": None,
        "head": None,
        "clean": None,
        "ahead": None,
        "behind": None,
        "licenses": top_level_licenses(repo),
        "advisories": [],
        "operation_markers": [],
        "executable_local_config": [],
        "blockers": [],
    }
    blockers: list[str] = result["blockers"]
    try:
        result["fingerprint"] = path_fingerprint(repo)
        if repo != repo.resolve(strict=True):
            blockers.append("repository_path_is_not_exact_real_path")
            return result
        result["git_fingerprint"] = path_fingerprint(repo / ".git")
    except (ManagerError, OSError):
        blockers.append("unreadable_repository_root")
        return result

    if (repo / ".git").is_symlink() or not (repo / ".git").is_dir():
        blockers.append("linked_worktree_not_allowed")

    risky_config = executable_local_config(repo)
    result["executable_local_config"] = risky_config
    if risky_config:
        blockers.append("unsupported_or_unsafe_local_git_config")
        return result

    try:
        root = Path(git_text(repo, ["rev-parse", "--show-toplevel"])).resolve(strict=True)
        if root != repo:
            blockers.append("not_exact_repository_root")
            return result
    except (ManagerError, OSError):
        blockers.append("unreadable_repository_root")
        return result

    markers = operation_markers(repo)
    result["operation_markers"] = markers
    if markers:
        blockers.append("git_operation_in_progress")

    branch_result = run_git(["symbolic-ref", "--quiet", "--short", "HEAD"], cwd=repo, check=False)
    if branch_result.returncode == 0:
        result["branch"] = branch_result.stdout.strip()
    else:
        blockers.append("detached_head")

    try:
        result["head"] = git_text(repo, ["rev-parse", "HEAD"])
    except ManagerError:
        blockers.append("unreadable_head")

    origin = run_git(["remote", "get-url", "origin"], cwd=repo, check=False)
    if origin.returncode != 0:
        blockers.append("missing_origin")
    else:
        try:
            normalized = normalize_github_url(origin.stdout.strip())
            result["identity"] = normalized["identity"]
            result["canonical_url"] = normalized["canonical_url"]
        except ManagerError as exc:
            blockers.append(str(exc).replace(" ", "_"))

    upstream_result = run_git(
        ["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"],
        cwd=repo,
        check=False,
    )
    if upstream_result.returncode == 0:
        result["upstream"] = upstream_result.stdout.strip()
    else:
        blockers.append("missing_upstream")

    if result["branch"] and result["upstream"] != f"origin/{result['branch']}":
        blockers.append("upstream_must_match_origin_branch")

    if not risky_config:
        status = run_git(["status", "--porcelain=v1", "--untracked-files=all"], cwd=repo, check=False)
        if status.returncode != 0:
            blockers.append("unreadable_worktree_status")
        else:
            result["clean"] = not bool(status.stdout)
            if not result["clean"]:
                blockers.append("dirty_worktree")

    if not result["licenses"]:
        result["advisories"].append("license_unverified")

    if result["upstream"]:
        counts = run_git(
            ["rev-list", "--left-right", "--count", "HEAD...@{upstream}"],
            cwd=repo,
            check=False,
        )
        if counts.returncode == 0:
            parts = counts.stdout.split()
            if len(parts) == 2 and all(part.isdigit() for part in parts):
                result["ahead"], result["behind"] = (int(parts[0]), int(parts[1]))
                if result["ahead"] and result["behind"]:
                    blockers.append("diverged_from_upstream")
                elif result["ahead"]:
                    blockers.append("ahead_of_upstream")
            else:
                blockers.append("unreadable_ahead_behind")
        else:
            blockers.append("unreadable_ahead_behind")

    result["blockers"] = sorted(set(blockers))
    return result


def add_duplicate_blockers(repositories: list[dict[str, Any]]) -> None:
    by_identity: dict[str, list[dict[str, Any]]] = {}
    for repo in repositories:
        identity = repo.get("identity")
        if isinstance(identity, str):
            by_identity.setdefault(identity.casefold(), []).append(repo)
    for duplicates in by_identity.values():
        if len(duplicates) > 1:
            for repo in duplicates:
                repo["blockers"] = sorted(set([*repo["blockers"], "duplicate_origin_identity"]))


def inventory(pool: Path) -> dict[str, Any]:
    paths, ignored = discover_repositories(pool)
    repositories = [inspect_repository(path) for path in paths]
    add_duplicate_blockers(repositories)
    clean = sum(repo.get("clean") is True for repo in repositories)
    dirty = sum(repo.get("clean") is False for repo in repositories)
    blocked = sum(bool(repo["blockers"]) for repo in repositories)
    return {
        "schema_version": SCHEMA_VERSION,
        "kind": "inventory",
        "generated_at": now_utc(),
        "pool": str(pool),
        "pool_fingerprint": path_fingerprint(pool),
        "repositories_total": len(repositories),
        "counts": {
            "clean": clean,
            "dirty": dirty,
            "unknown_clean_state": len(repositories) - clean - dirty,
            "blocked": blocked,
        },
        "repositories": repositories,
        "ignored_entries": ignored,
    }


def plan_update(pool: Path) -> dict[str, Any]:
    snapshot = inventory(pool)
    planned: list[dict[str, Any]] = []
    for repo in snapshot["repositories"]:
        item = dict(repo)
        item["remote_head"] = None
        item["github_snapshot"] = None
        if not item["blockers"]:
            try:
                github_snapshot = github_update_snapshot(item["canonical_url"])
                if github_snapshot["identity"].casefold() != item["identity"].casefold():
                    raise ManagerError("GitHub canonical identity changed")
                if github_snapshot["default_branch"] != item["branch"]:
                    raise ManagerError("checked-out branch is not the GitHub default branch")
                item["github_snapshot"] = github_snapshot
                item["remote_head"] = github_snapshot["remote_head"]
            except ManagerError as exc:
                item["blockers"] = [f"remote_check_failed:{exc}"]
        item["action"] = (
            "blocked"
            if item["blockers"]
            else ("already_current" if item["head"] == item["remote_head"] else "fast_forward_candidate")
        )
        planned.append(item)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "kind": "others-manager-update-plan",
        "created_at": now_utc(),
        "pool": str(pool),
        "pool_fingerprint": snapshot["pool_fingerprint"],
        "repository_names": [repo["name"] for repo in planned],
        "repositories": planned,
        "ignored_entries": snapshot["ignored_entries"],
    }
    return seal_plan(payload)


def same_local_snapshot(current: dict[str, Any], planned: dict[str, Any]) -> bool:
    fields = (
        "name",
        "identity",
        "canonical_url",
        "branch",
        "upstream",
        "head",
        "fingerprint",
        "git_fingerprint",
        "clean",
        "licenses",
        "advisories",
        "operation_markers",
        "executable_local_config",
        "blockers",
    )
    return all(current.get(field) == planned.get(field) for field in fields)


def candidate_license_blob(repo: Path, commit: str, license_path: str) -> str:
    value = git_text(repo, ["rev-parse", f"{commit}:{license_path}"])
    if not HEX40.fullmatch(value):
        raise ManagerError("candidate license blob is invalid")
    return value


def candidate_license_evidence(repo: Path, commit: str) -> list[dict[str, str]]:
    tree = run_git(["ls-tree", "-z", commit], cwd=repo)
    evidence: list[dict[str, str]] = []
    for entry in tree.stdout.split("\0"):
        if not entry or "\t" not in entry:
            continue
        metadata, name = entry.split("\t", 1)
        parts = metadata.split()
        if len(parts) != 3:
            continue
        mode, object_type, object_id = parts
        if mode not in {"100644", "100755"} or object_type != "blob":
            continue
        if LICENSE_NAME.fullmatch(name) and HEX40.fullmatch(object_id):
            evidence.append({"path": name, "blob_sha": object_id})
    return sorted(evidence, key=lambda item: item["path"].casefold())


def require_remote_tracking_fast_forward(repo: Path, old_tracking: str, fetched: str) -> None:
    tracking_ancestor = run_git(
        ["merge-base", "--is-ancestor", old_tracking, fetched],
        cwd=repo,
        check=False,
    )
    if tracking_ancestor.returncode != 0:
        raise ManagerError("remote tracking ref would require non-fast-forward movement")


def apply_update(pool: Path, plan: dict[str, Any]) -> dict[str, Any]:
    if plan.get("pool") != str(pool):
        raise ManagerError("plan pool does not match exact resolved pool")
    if not same_fingerprint(pool, plan["pool_fingerprint"]):
        raise ManagerError("pool identity changed after planning")
    paths, ignored = discover_repositories(pool)
    names = [path.name for path in paths]
    if names != plan.get("repository_names"):
        raise ManagerError("repository set changed after planning")

    path_by_name = {path.name: path for path in paths}
    results: list[dict[str, Any]] = []
    for planned in plan["repositories"]:
        name = planned["name"]
        planned_advisories = list(planned.get("advisories", []))
        planned_github_snapshot = planned.get("github_snapshot")
        if (
            isinstance(planned_github_snapshot, dict)
            and isinstance(planned_github_snapshot.get("license"), dict)
            and planned_github_snapshot["license"].get("status") == "unverified"
        ):
            planned_advisories.append("license_unverified")
        result: dict[str, Any] = {
            "name": name,
            "identity": planned.get("identity"),
            "old_head": planned.get("head"),
            "new_head": None,
            "result": None,
            "blockers": [],
            "remote_tracking_updated": False,
            "branch_moved": False,
            "candidate_licenses": [],
            "advisories": sorted(set(planned_advisories)),
        }
        if planned.get("blockers"):
            result["result"] = "blocked"
            result["blockers"] = [f"planned:{reason}" for reason in planned["blockers"]]
            results.append(result)
            continue

        repo = path_by_name[name]
        current = inspect_repository(repo)
        if not same_fingerprint(pool, plan["pool_fingerprint"]) or not same_local_snapshot(current, planned):
            result["result"] = "blocked"
            result["blockers"] = ["local_state_changed_after_planning"]
            results.append(result)
            continue

        try:
            current_remote = github_update_snapshot(planned["canonical_url"])
        except ManagerError as exc:
            result["result"] = "blocked"
            result["blockers"] = [f"remote_recheck_failed:{exc}"]
            results.append(result)
            continue
        if not same_repository_snapshot(current_remote, planned["github_snapshot"]):
            result["result"] = "blocked"
            result["blockers"] = ["GitHub_metadata_or_head_changed_after_planning"]
            results.append(result)
            continue

        branch = planned["branch"]
        remote_ref = f"refs/remotes/origin/{branch}"
        tracking_updated = False
        branch_moved = False
        try:
            if not same_fingerprint(pool, plan["pool_fingerprint"]) or not same_local_snapshot(
                inspect_repository(repo), planned
            ):
                raise ManagerError("local identity changed before fetch")
            run_git(
                [
                    "fetch",
                    "--no-tags",
                    "--no-recurse-submodules",
                    planned["canonical_url"],
                    f"refs/heads/{branch}",
                ],
                cwd=repo,
                timeout=300,
            )
            fetched = git_text(repo, ["rev-parse", "FETCH_HEAD"])
            if fetched != planned["remote_head"]:
                raise ManagerError("fetched candidate head does not match plan")
            if not same_fingerprint(pool, plan["pool_fingerprint"]) or not same_local_snapshot(
                inspect_repository(repo), planned
            ):
                raise ManagerError("local identity changed during fetch")
            ancestor = run_git(["merge-base", "--is-ancestor", "HEAD", fetched], cwd=repo, check=False)
            if ancestor.returncode != 0:
                raise ManagerError("candidate is not a fast-forward descendant")
            candidate_licenses = candidate_license_evidence(repo, fetched)
            result["candidate_licenses"] = candidate_licenses
            if not same_fingerprint(pool, plan["pool_fingerprint"]) or not same_local_snapshot(
                inspect_repository(repo), planned
            ):
                raise ManagerError("local identity changed before commit point")

            old_tracking = git_text(repo, ["rev-parse", remote_ref])
            require_remote_tracking_fast_forward(repo, old_tracking, fetched)
            run_git(["update-ref", remote_ref, fetched, old_tracking], cwd=repo)
            tracking_updated = True
            result["remote_tracking_updated"] = True
            before_merge = inspect_repository(repo)
            expected_premerge_fields = (
                "name",
                "identity",
                "canonical_url",
                "branch",
                "upstream",
                "head",
                "fingerprint",
                "git_fingerprint",
                "clean",
                "licenses",
                "advisories",
                "operation_markers",
                "executable_local_config",
            )
            if not same_fingerprint(pool, plan["pool_fingerprint"]) or not all(
                before_merge.get(field) == planned.get(field) for field in expected_premerge_fields
            ):
                raise ManagerError("local identity changed before fast-forward")

            if planned["head"] != fetched:
                run_git(["merge", "--ff-only", "--no-edit", fetched], cwd=repo, timeout=300)
                branch_moved = True
                result["branch_moved"] = True
                outcome = "updated"
            else:
                outcome = "already_current"
            final = inspect_repository(repo)
            expected_final = {
                "name": planned["name"],
                "identity": planned["identity"],
                "canonical_url": planned["canonical_url"],
                "branch": planned["branch"],
                "upstream": planned["upstream"],
                "head": planned["remote_head"],
                "fingerprint": planned["fingerprint"],
                "git_fingerprint": planned["git_fingerprint"],
                "clean": True,
            }
            if (
                final["blockers"]
                or not same_fingerprint(pool, plan["pool_fingerprint"])
                or any(final.get(field) != value for field, value in expected_final.items())
                or candidate_license_evidence(repo, final["head"]) != candidate_licenses
            ):
                raise ManagerError("final repository validation failed")
            result["result"] = outcome
            result["new_head"] = final["head"]
            result["advisories"] = sorted(
                set([*result["advisories"], *final["advisories"]])
            )
        except ManagerError as exc:
            result["result"] = "changed_with_blocker" if branch_moved else "blocked"
            result["blockers"] = [str(exc)]
            result["remote_tracking_updated"] = tracking_updated
            result["branch_moved"] = branch_moved
            try:
                result["new_head"] = git_text(repo, ["rev-parse", "HEAD"])
            except ManagerError:
                result["new_head"] = None
        results.append(result)

    blocked = sum(item["result"] in {"blocked", "changed_with_blocker"} for item in results)
    return {
        "schema_version": SCHEMA_VERSION,
        "kind": "others-manager-update-report",
        "generated_at": now_utc(),
        "pool": str(pool),
        "plan_id": plan["plan_id"],
        "repositories_total": len(results),
        "counts": {
            "updated": sum(item["result"] == "updated" for item in results),
            "already_current": sum(item["result"] == "already_current" for item in results),
            "blocked": blocked,
            "changed_with_blocker": sum(item["result"] == "changed_with_blocker" for item in results),
        },
        "repositories": results,
        "ignored_entries": ignored,
        "complete_without_blockers": blocked == 0,
    }


def github_json(path: str) -> dict[str, Any]:
    request = urllib.request.Request(
        f"{GITHUB_API}{path}",
        headers={"Accept": "application/vnd.github+json", "User-Agent": USER_AGENT},
        method="GET",
    )
    try:
        opener = urllib.request.build_opener(urllib.request.ProxyHandler({}))
        with opener.open(request, timeout=30) as response:
            value = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        raise ManagerError(f"GitHub API request failed with HTTP {exc.code}") from exc
    except (urllib.error.URLError, TimeoutError, json.JSONDecodeError) as exc:
        raise ManagerError("GitHub API request failed") from exc
    if not isinstance(value, dict):
        raise ManagerError("GitHub API returned an unexpected response")
    return value


def remote_default_head(canonical_url: str, default_branch: str) -> str:
    ref = f"refs/heads/{default_branch}"
    result = run_git(["ls-remote", "--symref", "--exit-code", canonical_url, "HEAD", ref], timeout=60)
    head_ref: str | None = None
    head_oid: str | None = None
    branch_oid: str | None = None
    for line in result.stdout.splitlines():
        parts = line.split()
        if len(parts) == 3 and parts[0] == "ref:" and parts[2] == "HEAD":
            head_ref = parts[1]
        elif len(parts) == 2 and parts[1] == "HEAD":
            head_oid = parts[0]
        elif len(parts) == 2 and parts[1] == ref:
            branch_oid = parts[0]
    if head_ref != ref or not head_oid or head_oid != branch_oid or not HEX40.fullmatch(head_oid):
        raise ManagerError("remote default branch or head is ambiguous")
    return head_oid


def github_license_snapshot(canonical: dict[str, str]) -> dict[str, Any]:
    try:
        license_data = github_json(f"/repos/{canonical['owner']}/{canonical['repo']}/license")
    except ManagerError:
        return {
            "status": "unverified",
            "spdx_id": None,
            "path": None,
            "blob_sha": None,
            "reason": "license_metadata_unavailable",
        }
    license_meta = license_data.get("license")
    spdx = license_meta.get("spdx_id") if isinstance(license_meta, dict) else None
    license_path = license_data.get("path")
    license_sha = license_data.get("sha")
    if not isinstance(spdx, str) or spdx.upper() in {"", "NOASSERTION", "OTHER"}:
        reason = "spdx_unrecognized"
    elif not isinstance(license_path, str) or "/" in license_path or not LICENSE_NAME.fullmatch(license_path):
        reason = "top_level_license_unrecognized"
    elif not isinstance(license_sha, str) or not HEX40.fullmatch(license_sha):
        reason = "license_blob_unavailable"
    else:
        return {
            "status": "verified",
            "spdx_id": spdx,
            "path": license_path,
            "blob_sha": license_sha,
            "reason": None,
        }
    return {
        "status": "unverified",
        "spdx_id": None,
        "path": None,
        "blob_sha": None,
        "reason": reason,
    }


def github_update_snapshot(url: str) -> dict[str, Any]:
    requested = normalize_github_url(url)
    metadata = github_json(f"/repos/{requested['owner']}/{requested['repo']}")
    full_name = metadata.get("full_name")
    if not isinstance(full_name, str) or "/" not in full_name:
        raise ManagerError("GitHub metadata lacks a canonical repository identity")
    canonical = normalize_github_url(f"https://github.com/{full_name}")
    if metadata.get("private") is not False:
        raise ManagerError("repository must be public")
    if metadata.get("archived") is not False:
        raise ManagerError("archived repositories are not admitted")
    if metadata.get("disabled") is not False:
        raise ManagerError("disabled repositories are not admitted")
    default_branch = metadata.get("default_branch")
    if not isinstance(default_branch, str) or not default_branch:
        raise ManagerError("repository lacks a default branch")
    if run_git(["check-ref-format", "--branch", default_branch], check=False).returncode != 0:
        raise ManagerError("repository default branch is unsafe")
    remote_head = remote_default_head(canonical["canonical_url"], default_branch)
    return {
        "identity": canonical["identity"],
        "identity_key": canonical["identity_key"],
        "canonical_url": canonical["canonical_url"],
        "default_branch": default_branch,
        "remote_head": remote_head,
        "license": github_license_snapshot(canonical),
    }


def github_repository_snapshot(url: str) -> dict[str, Any]:
    requested = normalize_github_url(url)
    metadata = github_json(f"/repos/{requested['owner']}/{requested['repo']}")
    full_name = metadata.get("full_name")
    if not isinstance(full_name, str) or "/" not in full_name:
        raise ManagerError("GitHub metadata lacks a canonical repository identity")
    canonical = normalize_github_url(f"https://github.com/{full_name}")
    if metadata.get("private") is not False:
        raise ManagerError("repository must be public")
    if metadata.get("archived") is not False:
        raise ManagerError("archived repositories are not admitted")
    if metadata.get("disabled") is not False:
        raise ManagerError("disabled repositories are not admitted")
    default_branch = metadata.get("default_branch")
    if not isinstance(default_branch, str) or not default_branch:
        raise ManagerError("repository lacks a default branch")
    check_ref = run_git(["check-ref-format", "--branch", default_branch], check=False)
    if check_ref.returncode != 0:
        raise ManagerError("repository default branch is unsafe")

    remote_head = remote_default_head(canonical["canonical_url"], default_branch)
    return {
        "identity": canonical["identity"],
        "identity_key": canonical["identity_key"],
        "canonical_url": canonical["canonical_url"],
        "default_branch": default_branch,
        "remote_head": remote_head,
        "license": github_license_snapshot(canonical),
    }


def existing_identity_map(pool: Path) -> dict[str, list[str]]:
    paths, _ = discover_repositories(pool)
    identities: dict[str, list[str]] = {}
    unknown: list[str] = []
    for path in paths:
        state = inspect_repository(path)
        identity = state.get("identity")
        if isinstance(identity, str):
            identities.setdefault(identity.casefold(), []).append(path.name)
        else:
            unknown.append(path.name)
    if unknown:
        raise ManagerError("cannot prove origin uniqueness for: " + ",".join(sorted(unknown)))
    return identities


def plan_clone(pool: Path, url: str, name: str | None) -> dict[str, Any]:
    snapshot = github_repository_snapshot(url)
    destination = validate_child_name(name or snapshot["identity"].split("/", 1)[1])
    existing_names = {child.name.casefold() for child in pool.iterdir()}
    if destination.casefold() in existing_names:
        raise ManagerError("destination already exists")
    identities = existing_identity_map(pool)
    if snapshot["identity_key"] in identities:
        raise ManagerError("repository origin is already present in: " + ",".join(identities[snapshot["identity_key"]]))
    paths, ignored = discover_repositories(pool)
    payload = {
        "schema_version": SCHEMA_VERSION,
        "kind": "others-manager-clone-plan",
        "created_at": now_utc(),
        "pool": str(pool),
        "pool_fingerprint": path_fingerprint(pool),
        "repository_names_before": [path.name for path in paths],
        "entry_names_before": sorted((child.name for child in pool.iterdir()), key=str.casefold),
        "ignored_entries": ignored,
        "destination": destination,
        "repository": snapshot,
    }
    return seal_plan(payload)


def same_repository_snapshot(current: dict[str, Any], planned: dict[str, Any]) -> bool:
    return all(
        current.get(field) == planned.get(field)
        for field in ("identity", "identity_key", "canonical_url", "default_branch", "remote_head", "license")
    )


def atomic_rename_noreplace(source: Path, destination: Path) -> None:
    require_supported_runtime()
    if source.parent.parent != destination.parent:
        raise ManagerError("clone staging and destination must share the pool filesystem")
    if destination.exists() or destination.is_symlink():
        raise ManagerError("clone destination exists at commit point")
    library = ctypes.CDLL(None, use_errno=True)
    source_bytes = os.fsencode(source)
    destination_bytes = os.fsencode(destination)
    if sys.platform == "darwin" and hasattr(library, "renamex_np"):
        rename = library.renamex_np
        rename.argtypes = [ctypes.c_char_p, ctypes.c_char_p, ctypes.c_uint]
        rename.restype = ctypes.c_int
        result = rename(source_bytes, destination_bytes, 0x00000004)
    elif sys.platform.startswith("linux") and hasattr(library, "renameat2"):
        rename = library.renameat2
        rename.argtypes = [ctypes.c_int, ctypes.c_char_p, ctypes.c_int, ctypes.c_char_p, ctypes.c_uint]
        rename.restype = ctypes.c_int
        result = rename(-100, source_bytes, -100, destination_bytes, 0x00000001)
    else:
        raise ManagerError("atomic no-replace directory rename is unavailable on this platform")
    if result != 0:
        error_number = ctypes.get_errno()
        if error_number in {errno.EEXIST, errno.ENOTEMPTY}:
            raise ManagerError("clone destination appeared at commit point")
        raise ManagerError(f"atomic clone commit failed with errno {error_number}")


def safe_cleanup_stage(
    stage: Path,
    pool: Path,
    expected_device: int,
    expected_inode: int,
    marker_token: str,
) -> bool:
    try:
        stat = stage.lstat()
        marker = stage / ".others-manager-owned"
        if (
            stage.parent != pool
            or not stage.name.startswith(".others-manager-clone-")
            or stage.is_symlink()
            or not stage.is_dir()
            or (stat.st_dev, stat.st_ino) != (expected_device, expected_inode)
        ):
            return False
        if marker.is_symlink() or marker.read_text(encoding="utf-8") != marker_token:
            return False
        shutil.rmtree(stage)
        return True
    except OSError:
        return False


def validate_unchecked_clone(checkout: Path, planned_repo: dict[str, Any]) -> None:
    if checkout != checkout.resolve(strict=True):
        raise ManagerError("staged clone path is not exact and real")
    path_fingerprint(checkout)
    path_fingerprint(checkout / ".git")
    root = Path(git_text(checkout, ["rev-parse", "--show-toplevel"])).resolve(strict=True)
    if root != checkout:
        raise ManagerError("staged clone is not an exact repository root")
    if operation_markers(checkout):
        raise ManagerError("staged clone has a Git operation marker")
    if executable_local_config(checkout):
        raise ManagerError("staged clone has unsupported or unsafe local Git config")
    origin_result = run_git(["remote", "get-url", "origin"], cwd=checkout, check=False)
    if origin_result.returncode != 0:
        raise ManagerError("staged clone lacks origin")
    origin = normalize_github_url(origin_result.stdout.strip())
    if origin["identity_key"] != planned_repo["identity_key"]:
        raise ManagerError("staged clone origin identity does not match plan")
    branch = git_text(checkout, ["symbolic-ref", "--quiet", "--short", "HEAD"])
    upstream = git_text(checkout, ["rev-parse", "--abbrev-ref", "--symbolic-full-name", "@{upstream}"])
    head = git_text(checkout, ["rev-parse", "HEAD"])
    if branch != planned_repo["default_branch"] or upstream != f"origin/{branch}":
        raise ManagerError("staged clone branch or upstream does not match plan")
    if head != planned_repo["remote_head"]:
        raise ManagerError("staged clone head does not match plan")
    license_data = planned_repo["license"]
    if license_data["status"] == "verified":
        if candidate_license_blob(checkout, head, license_data["path"]) != license_data["blob_sha"]:
            raise ManagerError("staged clone license blob does not match plan")


def apply_clone(pool: Path, plan: dict[str, Any]) -> dict[str, Any]:
    if plan.get("pool") != str(pool):
        raise ManagerError("plan pool does not match exact resolved pool")
    if not same_fingerprint(pool, plan["pool_fingerprint"]):
        raise ManagerError("pool identity changed after planning")
    paths, _ = discover_repositories(pool)
    names = [path.name for path in paths]
    if names != plan.get("repository_names_before"):
        raise ManagerError("repository set changed after planning")
    entry_names = sorted((child.name for child in pool.iterdir()), key=str.casefold)
    if entry_names != plan.get("entry_names_before"):
        raise ManagerError("pool entry set changed after planning")
    destination = validate_child_name(plan["destination"])
    destination_path = pool / destination
    identities = existing_identity_map(pool)
    planned_repo = plan["repository"]
    if planned_repo["identity_key"] in identities:
        raise ManagerError("repository origin appeared after planning")
    current = github_repository_snapshot(planned_repo["canonical_url"])
    if not same_repository_snapshot(current, planned_repo):
        raise ManagerError("repository metadata or remote head changed after planning")

    marker_token = uuid.uuid4().hex
    stage = Path(tempfile.mkdtemp(prefix=".others-manager-clone-", dir=pool))
    stage_metadata = stage.lstat()
    marker = stage / ".others-manager-owned"
    try:
        flags = os.O_WRONLY | os.O_CREAT | os.O_EXCL
        if hasattr(os, "O_NOFOLLOW"):
            flags |= os.O_NOFOLLOW
        marker_fd = os.open(marker, flags, 0o600)
        with os.fdopen(marker_fd, "w", encoding="utf-8") as handle:
            handle.write(marker_token)
            handle.flush()
            os.fsync(handle.fileno())
    except Exception as exc:
        try:
            if stage.lstat().st_ino == stage_metadata.st_ino and not any(stage.iterdir()):
                stage.rmdir()
        except OSError:
            pass
        raise ManagerError("cannot initialize owned clone staging") from exc
    checkout = stage / "checkout"
    committed = False
    warnings: list[str] = []
    advisories: list[str] = []
    try:
        run_git(
            [
                "clone",
                "--origin",
                "origin",
                "--branch",
                planned_repo["default_branch"],
                "--no-checkout",
                "--no-tags",
                "--no-recurse-submodules",
                planned_repo["canonical_url"],
                str(checkout),
            ],
            timeout=900,
        )
        validate_unchecked_clone(checkout, planned_repo)
        run_git(["checkout", "--force", planned_repo["default_branch"]], cwd=checkout, timeout=300)
        state = inspect_repository(checkout)
        expected_upstream = f"origin/{planned_repo['default_branch']}"
        if state["identity"].casefold() != planned_repo["identity_key"]:
            raise ManagerError("cloned origin identity does not match plan")
        if state["branch"] != planned_repo["default_branch"] or state["upstream"] != expected_upstream:
            raise ManagerError("cloned branch or upstream does not match plan")
        if state["head"] != planned_repo["remote_head"] or state["clean"] is not True:
            raise ManagerError("cloned head or worktree does not match plan")
        license_data = planned_repo["license"]
        if license_data["status"] == "verified":
            if license_data["path"] not in state["licenses"]:
                raise ManagerError("planned top-level license is absent after clone")
            license_blob = git_text(checkout, ["rev-parse", f"HEAD:{license_data['path']}"])
            if license_blob != license_data["blob_sha"]:
                raise ManagerError("cloned license blob does not match GitHub evidence")
        else:
            advisories.append("license_unverified")
        if state["blockers"]:
            raise ManagerError("cloned repository validation failed: " + ",".join(state["blockers"]))
        latest = github_repository_snapshot(planned_repo["canonical_url"])
        if not same_repository_snapshot(latest, planned_repo):
            raise ManagerError("repository metadata or remote head changed during clone")
        current_entries = sorted((child.name for child in pool.iterdir() if child != stage), key=str.casefold)
        if (
            not same_fingerprint(pool, plan["pool_fingerprint"])
            or current_entries != plan["entry_names_before"]
            or destination_path.exists()
            or destination_path.is_symlink()
        ):
            raise ManagerError("pool identity or entry set changed before clone commit")
        atomic_rename_noreplace(checkout, destination_path)
        committed = True
    except Exception as exc:
        cleaned = safe_cleanup_stage(
            stage,
            pool,
            stage_metadata.st_dev,
            stage_metadata.st_ino,
            marker_token,
        )
        if isinstance(exc, ManagerError):
            suffix = "" if cleaned else f"; owned staging retained for review: {stage}"
            raise ManagerError(f"{exc}{suffix}") from exc
        suffix = "" if cleaned else f"; owned staging retained for review: {stage}"
        raise ManagerError(f"clone apply failed{suffix}") from exc

    if committed:
        try:
            marker.unlink()
            stage.rmdir()
        except OSError:
            warnings.append(f"owned staging cleanup requires review: {stage}")

    return {
        "schema_version": SCHEMA_VERSION,
        "kind": "others-manager-clone-report",
        "generated_at": now_utc(),
        "pool": str(pool),
        "plan_id": plan["plan_id"],
        "result": "cloned",
        "destination": str(destination_path),
        "repository": planned_repo,
        "blockers": [],
        "warnings": warnings,
        "advisories": advisories,
    }


def execute_controller_apply(
    *,
    pool: Path,
    plan: dict[str, Any],
    output: str,
    cleanup_output: str,
    operation: str,
    apply_function: Any,
    capability_check: Any,
) -> dict[str, Any]:
    require_supported_runtime()
    capability_check()
    receipt = reserve_operation_receipt(output, operation, pool, plan["plan_id"])
    try:
        cleanup_receipt = reserve_operation_receipt(
            cleanup_output,
            f"{operation}-lock-cleanup",
            pool,
            plan["plan_id"],
        )
    except Exception as exc:
        error = "cannot reserve the independent lock cleanup receipt"
        finalize_operation_receipt(receipt, failed_operation_receipt(receipt, error))
        raise ManagerError(error) from exc
    lock: dict[str, Any] | None = None
    try:
        lock = acquire_operation_lock(pool, plan["plan_id"])
        capability_check()
        report = apply_function(pool, plan)
    except Exception as exc:
        error = str(exc) if isinstance(exc, ManagerError) else "unexpected controller apply failure"
        try:
            finalize_operation_receipt(receipt, failed_operation_receipt(receipt, error))
        except ManagerError as receipt_error:
            suffix = f"; operation lock retained for safety: {lock['path']}" if lock is not None else ""
            raise ManagerError(f"{error}; {receipt_error}{suffix}") from exc
        try:
            _, cleanup_blockers = finalize_lock_cleanup_receipt(cleanup_receipt, lock)
        except ManagerError as cleanup_error:
            raise ManagerError(f"{error}; {cleanup_error}") from exc
        if cleanup_blockers:
            error += "; " + "; ".join(cleanup_blockers)
        raise ManagerError(error) from exc

    report["operation_lock_state_at_receipt_commit"] = "held"
    report["lock_cleanup_receipt"] = str(cleanup_receipt["path"])
    finalize_operation_receipt(receipt, report)
    released, cleanup_blockers = finalize_lock_cleanup_receipt(cleanup_receipt, lock)
    if cleanup_blockers:
        report["cleanup_blockers"] = cleanup_blockers
        if "complete_without_blockers" in report:
            report["complete_without_blockers"] = False
    print(
        json.dumps(
            {**report, "receipt_status": "complete", "operation_lock_released": released},
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
    return report


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="command", required=True)

    inventory_parser = subparsers.add_parser("inventory", help="inspect local repository state only")
    inventory_parser.add_argument("--pool", required=True)
    inventory_parser.add_argument("--output")

    plan_update_parser = subparsers.add_parser("plan-update", help="freeze local and remote update facts")
    plan_update_parser.add_argument("--pool", required=True)
    plan_update_parser.add_argument("--output", required=True)

    apply_update_parser = subparsers.add_parser("apply-update", help="apply a reviewed update plan")
    apply_update_parser.add_argument("--pool", required=True)
    apply_update_parser.add_argument("--plan", required=True)
    apply_update_parser.add_argument("--output", required=True)
    apply_update_parser.add_argument("--cleanup-output", required=True)
    apply_update_parser.add_argument("--expected-plan-id", required=True)
    apply_update_parser.add_argument("--controller-project", required=True)
    apply_update_parser.add_argument("--controller-session", required=True)
    apply_update_parser.add_argument("--controller-confirm-reviewed-plan", action="store_true")

    plan_clone_parser = subparsers.add_parser("plan-clone", help="freeze GitHub clone admission facts")
    plan_clone_parser.add_argument("--pool", required=True)
    plan_clone_parser.add_argument("--url", required=True)
    plan_clone_parser.add_argument("--name")
    plan_clone_parser.add_argument("--output", required=True)

    apply_clone_parser = subparsers.add_parser("apply-clone", help="apply a reviewed clone plan")
    apply_clone_parser.add_argument("--pool", required=True)
    apply_clone_parser.add_argument("--plan", required=True)
    apply_clone_parser.add_argument("--output", required=True)
    apply_clone_parser.add_argument("--cleanup-output", required=True)
    apply_clone_parser.add_argument("--expected-plan-id", required=True)
    apply_clone_parser.add_argument("--controller-project", required=True)
    apply_clone_parser.add_argument("--controller-session", required=True)
    apply_clone_parser.add_argument("--controller-confirm-reviewed-plan", action="store_true")
    return parser


def main(argv: list[str] | None = None) -> int:
    args = build_parser().parse_args(argv)
    try:
        require_supported_runtime()
        pool = validate_pool(args.pool)
        if args.command == "inventory":
            report = inventory(pool)
            emit(report, args.output)
            return 2 if report["counts"]["blocked"] else 0
        if args.command == "plan-update":
            ensure_output_available(args.output)
            plan = plan_update(pool)
            emit(plan, args.output)
            return 2 if any(repo["blockers"] for repo in plan["repositories"]) else 0
        if args.command == "apply-update":
            if not args.controller_confirm_reviewed_plan:
                raise ManagerError("apply-update requires reviewed-plan confirmation")
            capability_check = lambda: validate_controller_capability(
                args.controller_project,
                args.controller_session,
                pool,
            )
            capability_check()
            plan = load_plan(args.plan, "others-manager-update-plan", args.expected_plan_id)
            report = execute_controller_apply(
                pool=pool,
                plan=plan,
                output=args.output,
                cleanup_output=args.cleanup_output,
                operation="apply-update",
                apply_function=apply_update,
                capability_check=capability_check,
            )
            return 2 if report["counts"]["blocked"] or report.get("cleanup_blockers") else 0
        if args.command == "plan-clone":
            ensure_output_available(args.output)
            plan = plan_clone(pool, args.url, args.name)
            emit(plan, args.output)
            return 0
        if args.command == "apply-clone":
            if not args.controller_confirm_reviewed_plan:
                raise ManagerError("apply-clone requires reviewed-plan confirmation")
            capability_check = lambda: validate_controller_capability(
                args.controller_project,
                args.controller_session,
                pool,
            )
            capability_check()
            plan = load_plan(args.plan, "others-manager-clone-plan", args.expected_plan_id)
            report = execute_controller_apply(
                pool=pool,
                plan=plan,
                output=args.output,
                cleanup_output=args.cleanup_output,
                operation="apply-clone",
                apply_function=apply_clone,
                capability_check=capability_check,
            )
            return 2 if report.get("warnings") or report.get("cleanup_blockers") else 0
        raise ManagerError("unknown command")
    except ManagerError as exc:
        print(json.dumps({"status": "error", "error": str(exc)}, ensure_ascii=False), file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
