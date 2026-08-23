#!/usr/bin/env python3
"""Offline structural validator for the candidate research QA plugin and runs."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import zlib
from datetime import date, datetime
from pathlib import Path, PurePosixPath
from typing import Any, Iterable
from urllib.parse import urlsplit, urlunsplit


PLUGIN_SCHEMA = "https://agent-plugins.org/schemas/1.0.0/plugin.schema.json"
PLUGIN_NAME = "research-qa-plugin"
PLUGIN_VERSION = "0.2.0"
SKILL_NAME = "research-qa-orchestrator"
PAPER_DOWNLOADER_NAME = "paper-downloader"
BUNDLED_SCHEMA = "research-qa-orchestrator/bundled-source-manifest/v1"
PLUGIN_RECEIPT_SCHEMA = "research-qa-orchestrator/plugin-validation-receipt/v2"
RUNTIME_OPERATION_SCHEMA = "research-qa-orchestrator/runtime-operation-receipt/v1"
SKILL_DISCOVERY_SCHEMA = "research-qa-orchestrator/skill-discovery-receipt/v1"
ACQUISITION_OPERATION_SCHEMA = (
    "research-qa-orchestrator/acquisition-operation-receipt/v1"
)
TREE_HASH_ALGORITHM = (
    "sha256(concat(sorted_utf8(relative_path) + NUL + "
    "sha256(content)_hex + LF))"
)
AKASHIC_ROOT = Path.home() / "Documents" / "Akashic"
LIVE_RULE = AKASHIC_ROOT / "90-project-rules" / "current" / "05-文献分级与创作.md"
AKASHIC_REGISTRY_ROOT = AKASHIC_ROOT / "03-metadata" / "registry"
AKASHIC_SUBMISSIONS_ROOT = AKASHIC_ROOT / "12-agent-submissions"
DEFAULT_PLUGIN_ROOT = Path(__file__).resolve().parents[3]
SKILL_RELATIVE = Path("skills") / SKILL_NAME
BUNDLED_RELATIVE = SKILL_RELATIVE / "bundled"
SOURCE_MANIFEST_RELATIVE = BUNDLED_RELATIVE / "source-manifest.json"
VALIDATOR_RELATIVE = SKILL_RELATIVE / "scripts" / "validate_research_qa.py"
CRITICAL_RUNTIME_RELATIVES = (
    Path("plugin.json"),
    SKILL_RELATIVE / "SKILL.md",
    SKILL_RELATIVE / "references" / "workflow-contract.md",
    SKILL_RELATIVE / "references" / "executor-and-audit-contract.md",
    SKILL_RELATIVE / "references" / "artifact-contract.md",
    SKILL_RELATIVE / "references" / "external-executors.md",
    VALIDATOR_RELATIVE,
    SOURCE_MANIFEST_RELATIVE,
    BUNDLED_RELATIVE / "verify_bundled.py",
)
ALLOWED_PLUGIN_FIELDS = {
    "$schema",
    "name",
    "version",
    "description",
    "author",
    "homepage",
    "repository",
    "license",
    "keywords",
    "extensions",
}
EXCLUDED_BUNDLED_NAMES = {".DS_Store", ".git", "__pycache__"}
HEX64 = re.compile(r"\A[0-9a-f]{64}\Z")
RUNTIME_ID_PATTERN = re.compile(r"\A[A-Za-z0-9][A-Za-z0-9._:-]{7,}\Z")
PLUGIN_NAME_PATTERN = re.compile(
    r"\A(?!.*(?:--|\.\.))[a-z0-9](?:[a-z0-9.-]*[a-z0-9])?\Z"
)
COMPONENT_ID_PATTERN = re.compile(r"\A[a-z0-9][a-z0-9-]*\Z")
PACKAGE_ID_PATTERN = re.compile(r"\A[a-zA-Z0-9][a-zA-Z0-9._-]{0,127}\Z")
PACKAGE_YEAR_PATTERN = re.compile(r"\A[0-9]{4}\Z")
PACKAGE_MONTH_DAY_PATTERN = re.compile(r"\A[0-9]{2}\Z")
ATTEMPT_PATTERN = re.compile(r"\Aattempt-(\d{2})\.md\Z")
MAX_ATTEMPTS = 4
MIN_REVIEWABLE = 30
MIN_PDF_BYTES = 5 * 1024
MIN_EXPERT_NONSPACE = 400
MIN_SYNTHESIS_NONSPACE = 800
ALLOWED_DOCUMENT_KINDS = {
    "paper",
    "randomized_trial",
    "controlled_trial",
    "cohort_study",
    "case_control_study",
    "cross_sectional_study",
    "case_report",
    "mechanistic_study",
    "systematic_review",
    "meta_analysis",
    "narrative_review",
    "clinical_guideline",
    "consensus_statement",
    "preprint",
}
REVIEWABLE_ACCESS_STATUSES = {"downloaded", "akashic_reused", "verified_abstract"}
ALLOWED_ACCESS_STATUSES = REVIEWABLE_ACCESS_STATUSES | {
    "browser_required",
    "manual_browser_required",
    "paywalled",
    "paywalled_or_no_pdf",
    "access_blocked",
    "unverified_citation",
    "duplicate",
    "needs_manual_review",
    "failed",
}
EXPERT_COMPONENTS = (
    ("persona-01", "Nick Norwitz"),
    ("persona-02", "Anthony Chaffee"),
    ("persona-03", "PeterAttia"),
    ("persona-04", "Dr Eric Berg"),
    ("persona-05", "Steak and Butter Gal"),
    ("persona-06", "Dr Stan Ekberg"),
    ("persona-07", "Dr Robert"),
    ("persona-08", "ShawnBaker"),
)
FUXI_COMPONENT = ("fuxi-skill", "fuxi-skill")
REQUIRED_SOURCE_FIELDS = {
    "source_id",
    "title",
    "authors",
    "year",
    "source_type",
    "document_kind",
    "publication_identity",
    "doi",
    "pmid",
    "pmcid",
    "original_publication_url",
    "source_origin",
    "local_source_path",
    "online_source_url",
    "access_depth",
    "access_status",
    "download_attempted",
    "local_payload_path",
    "payload_sha256",
    "payload_bytes",
    "acquisition_receipt_path",
    "akashic_registry_path",
    "failure_reason",
    "duplicate_of",
    "on_scope",
    "identifier_verified",
    "reviewable",
    "evidence_quality",
    "usage_role",
    "review_depth",
    "local_grade",
    "method_flags",
    "funding_flags",
    "diet_flags",
    "record_sha256",
}
TERMINAL_FAILURE_EVENTS = {
    "plugin_invalid",
    "bundled_manifest_invalid",
    "rule_missing",
    "rule_drift",
    "collection_not_ready",
    "material_audit_rejected",
    "auditor_unavailable",
    "expert_exhausted",
    "synthesis_exhausted",
    "receipt_chain_invalid",
    "unsafe_request",
    "package_calendar_path",
    "invalid_package_date",
    "package_exists",
    "package_escape",
    "output_boundary_invalid",
    "acquisition_executor_unavailable",
}
FORBIDDEN_RUNTIME_FIELDS = {
    "agent_path",
    "agent_thread_id",
    "agentPath",
    "agentThreadId",
    "subAgentActivity",
    "subagent_activity",
}
FORBIDDEN_RUNTIME_TOOL_MARKERS = ("spawn_agent", "subagent", "collaboration")
PACKAGE_LOCAL_ATTESTATION_FIELDS = {
    "host_attestation",
    "independent_host_attestation",
}
STRUCTURAL_RUN_STATUS = "structurally_complete_runtime_unverified"
RUNTIME_NOT_VERIFIED = "runtime_not_verified"


class ValidationError(Exception):
    """Stable contract error returned as JSON by the CLI."""

    def __init__(self, code: str, message: str, **details: Any) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.details = details


def fail(code: str, message: str, **details: Any) -> None:
    raise ValidationError(code, message, **details)


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def canonical_without(record: dict[str, Any], key: str) -> bytes:
    material = {name: value for name, value in record.items() if name != key}
    return (
        json.dumps(
            material,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ).encode("utf-8")
        + b"\n"
    )


def parse_time(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        fail("invalid_timestamp", f"{field} must be a non-empty RFC3339 timestamp")
    candidate = value.replace("Z", "+00:00")
    try:
        datetime.fromisoformat(candidate)
    except ValueError:
        fail("invalid_timestamp", f"{field} is not RFC3339-compatible", value=value)
    return value


def parsed_time(value: Any, field: str) -> datetime:
    parsed = parse_time(value, field)
    return datetime.fromisoformat(parsed.replace("Z", "+00:00"))


def require_hex(value: Any, field: str) -> str:
    if not isinstance(value, str) or not HEX64.fullmatch(value):
        fail("invalid_sha256", f"{field} must be 64 lowercase hex characters")
    return value


def require_object(value: Any, field: str) -> dict[str, Any]:
    if not isinstance(value, dict):
        fail("invalid_object", f"{field} must be an object")
    return value


def require_list(value: Any, field: str) -> list[Any]:
    if not isinstance(value, list):
        fail("invalid_array", f"{field} must be an array")
    return value


def require_nonempty_string(value: Any, field: str) -> str:
    if not isinstance(value, str) or not value.strip():
        fail("invalid_string", f"{field} must be a non-empty string")
    return value


def require_runtime_identifier(value: Any, field: str) -> str:
    identifier = require_nonempty_string(value, field).strip()
    if (
        identifier.startswith("/")
        or "/root/" in identifier
        or "\\" in identifier
        or not RUNTIME_ID_PATTERN.fullmatch(identifier)
    ):
        fail(
            "invalid_runtime_identifier",
            f"{field} must be a runtime identifier, not an agent path",
            value=identifier,
        )
    return identifier


def tool_leaf(tool: str) -> str:
    leaf = tool.replace("\\", "/").rsplit("/", 1)[-1]
    if "__" in leaf:
        return leaf.rsplit("__", 1)[-1]
    return leaf.rsplit(".", 1)[-1]


def reject_hidden_runtime_evidence(value: Any, field: str) -> None:
    if isinstance(value, dict):
        forbidden = sorted(FORBIDDEN_RUNTIME_FIELDS.intersection(value))
        if forbidden:
            fail(
                "hidden_subagent_evidence",
                f"{field} contains hidden-subagent fields",
                fields=forbidden,
            )
        attestation_fields = sorted(
            PACKAGE_LOCAL_ATTESTATION_FIELDS.intersection(value)
        )
        success_overclaims = sorted(
            key
            for key in ("runtime_execution_verified", "run_success_verified")
            if value.get(key) is True
        )
        if attestation_fields or success_overclaims:
            fail(
                "runtime_attestation_boundary",
                f"{field} contains a package-local runtime attestation claim",
                fields=attestation_fields + success_overclaims,
            )
        for key, child in value.items():
            reject_hidden_runtime_evidence(child, f"{field}.{key}")
    elif isinstance(value, list):
        for index, child in enumerate(value):
            reject_hidden_runtime_evidence(child, f"{field}[{index}]")


def normalized_root(path: Path, label: str) -> Path:
    absolute = path.expanduser().absolute()
    if absolute.is_symlink():
        fail("symlink_forbidden", f"{label} cannot be a symlink", path=str(absolute))
    if not absolute.is_dir():
        fail("missing_directory", f"{label} is not a directory", path=str(absolute))
    try:
        return absolute.resolve(strict=True)
    except OSError as error:
        fail("unresolvable_path", f"cannot resolve {label}", path=str(absolute), error=str(error))


def absolute_lexical_path(path: Path, field: str) -> Path:
    expanded = path.expanduser()
    if not expanded.is_absolute():
        fail("package_path_not_absolute", f"{field} must be absolute", path=str(path))
    return Path(os.path.abspath(os.fspath(expanded)))


def validate_package_location(
    submissions_root_input: Path,
    package_input: Path,
    *,
    must_exist: bool,
) -> dict[str, str]:
    """Validate the strict YYYY/MM/DD/package_id boundary without writing."""

    submissions_root_lexical = absolute_lexical_path(
        submissions_root_input,
        "Akashic 12-agent-submissions root",
    )
    submissions_root = normalized_root(
        submissions_root_input,
        "Akashic 12-agent-submissions root",
    )
    package_input_lexical = absolute_lexical_path(package_input, "package path")
    try:
        relative = package_input_lexical.relative_to(submissions_root_lexical)
    except ValueError:
        try:
            relative = package_input_lexical.relative_to(submissions_root)
        except ValueError:
            fail(
                "package_escape",
                "package path escapes 12-agent-submissions",
                path=str(package_input_lexical),
            )
    package_lexical = submissions_root / relative
    if len(relative.parts) != 4:
        fail(
            "package_calendar_path",
            "package path must be exactly YYYY/MM/DD/<package_id>",
            relative_path=relative.as_posix(),
        )
    year, month, day, package_id = relative.parts
    if (
        not PACKAGE_YEAR_PATTERN.fullmatch(year)
        or not PACKAGE_MONTH_DAY_PATTERN.fullmatch(month)
        or not PACKAGE_MONTH_DAY_PATTERN.fullmatch(day)
    ):
        fail(
            "package_calendar_path",
            "YYYY must have four digits and MM/DD must each have two digits",
            relative_path=relative.as_posix(),
        )
    try:
        package_date = date(int(year), int(month), int(day))
    except ValueError as error:
        fail(
            "invalid_package_date",
            "package calendar path is not a real Gregorian date",
            relative_path=relative.as_posix(),
            error=str(error),
        )
    if not PACKAGE_ID_PATTERN.fullmatch(package_id):
        fail(
            "invalid_package_id",
            "package directory name is not a safe package ID",
            package_id=package_id,
        )

    day_lexical = submissions_root / year / month / day
    current = submissions_root
    for label, component in (("year", year), ("month", month), ("day", day)):
        current = current / component
        if current.is_symlink():
            fail(
                "symlink_forbidden",
                f"package {label} directory cannot be a symlink",
                path=str(current),
            )
        if current.exists() and not current.is_dir():
            fail(
                "invalid_package_parent",
                f"package {label} path is not a directory",
                path=str(current),
            )
        if current.exists():
            resolved = current.resolve(strict=True)
            if not within(submissions_root, resolved):
                fail("package_escape", "package calendar parent escapes its root", path=str(current))

    if package_lexical.parent != day_lexical:
        fail(
            "package_boundary",
            "package must be the immediate child of its day directory",
            path=str(package_lexical),
        )
    if must_exist:
        if package_lexical.is_symlink():
            fail("symlink_forbidden", "run package cannot be a symlink", path=str(package_lexical))
        if not package_lexical.is_dir():
            fail("missing_package", "run package must be an existing directory", path=str(package_lexical))
        package = package_lexical.resolve(strict=True)
        if package.parent != day_lexical.resolve(strict=True):
            fail(
                "package_boundary",
                "package must resolve as the immediate child of its day directory",
                path=str(package),
            )
    else:
        if package_lexical.exists() or package_lexical.is_symlink():
            fail(
                "package_exists",
                "package destination already exists; overwrite and reuse are forbidden",
                path=str(package_lexical),
            )
        package = package_lexical

    return {
        "submissions_root": str(submissions_root),
        "package": str(package),
        "package_id": package_id,
        "package_date": package_date.isoformat(),
        "package_relative_path": relative.as_posix(),
    }


def validate_new_package_destination(
    package_input: Path,
    *,
    submissions_root_input: Path = AKASHIC_SUBMISSIONS_ROOT,
) -> dict[str, Any]:
    location = validate_package_location(
        submissions_root_input,
        package_input,
        must_exist=False,
    )
    return {
        "ok": True,
        "mode": "destination",
        **location,
        "destination_preexisted": False,
        "creation_mode": "exclusive",
    }


def relative_posix(value: Any, field: str) -> PurePosixPath:
    text = require_nonempty_string(value, field)
    path = PurePosixPath(text)
    if path.is_absolute() or not path.parts or any(part in {"", ".", ".."} for part in path.parts):
        fail("invalid_relative_path", f"{field} must be a confined POSIX relative path", path=text)
    return path


def within(root: Path, candidate: Path) -> bool:
    try:
        return os.path.commonpath([str(root), str(candidate)]) == str(root)
    except ValueError:
        return False


def confined(
    root: Path,
    relative: str | PurePosixPath | Path,
    *,
    kind: str = "file",
    field: str = "path",
) -> Path:
    if isinstance(relative, str):
        rel = relative_posix(relative, field)
    else:
        rel = PurePosixPath(relative.as_posix())
        if rel.is_absolute() or any(part in {"", ".", ".."} for part in rel.parts):
            fail("invalid_relative_path", f"{field} must be confined", path=str(relative))
    current = root
    for part in rel.parts:
        current = current / part
        if current.is_symlink():
            fail("symlink_forbidden", f"symlink in {field}", path=str(current))
    if kind == "file" and not current.is_file():
        fail("missing_file", f"missing required file for {field}", path=str(current))
    if kind == "directory" and not current.is_dir():
        fail("missing_directory", f"missing required directory for {field}", path=str(current))
    try:
        resolved = current.resolve(strict=True)
    except OSError as error:
        fail("unresolvable_path", f"cannot resolve {field}", path=str(current), error=str(error))
    if not within(root, resolved):
        fail("path_escape", f"{field} escapes its root", path=str(current))
    return resolved


def assert_no_symlinks(root: Path) -> None:
    if root.is_symlink():
        fail("symlink_forbidden", "root cannot be a symlink", path=str(root))
    for current, directories, files in os.walk(root, followlinks=False):
        current_path = Path(current)
        for name in directories + files:
            path = current_path / name
            if path.is_symlink():
                fail("symlink_forbidden", "plugin/package tree contains a symlink", path=str(path))


def load_json(path: Path, field: str) -> dict[str, Any]:
    try:
        value = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, UnicodeError, json.JSONDecodeError) as error:
        fail("invalid_json", f"cannot parse {field}", path=str(path), error=str(error))
    return require_object(value, field)


def load_simple_yaml_mapping(path: Path, field: str) -> dict[str, Any]:
    """Read the scalar top-level fields used by Akashic v2 package manifests."""

    if not path.is_file() or path.is_symlink():
        fail("missing_file", f"{field} is missing", path=str(path))
    result: dict[str, Any] = {}
    for line_number, raw_line in enumerate(path.read_text(encoding="utf-8").splitlines(), 1):
        if not raw_line.strip() or raw_line.lstrip().startswith("#"):
            continue
        if raw_line[:1].isspace() or ":" not in raw_line:
            fail("manifest_yaml_shape", f"{field} must contain only scalar top-level fields", line=line_number)
        key, raw_value = raw_line.split(":", 1)
        key = key.strip()
        value = raw_value.strip()
        if not key or not value:
            fail("manifest_yaml_shape", f"{field} contains an empty key or value", line=line_number)
        if value in {"true", "false"}:
            parsed: Any = value == "true"
        elif re.fullmatch(r"[0-9]+", value):
            parsed = int(value)
        elif len(value) >= 2 and value[0] == value[-1] and value[0] in {"'", '"'}:
            parsed = value[1:-1]
        else:
            parsed = value
        result[key] = parsed
    return result


def validate_reserved_package(
    package_root: Path,
    package: Path,
    package_relative_path: str,
) -> dict[str, str]:
    reservation_path = package_path(package_root, package, ".reservation.json")
    reservation = load_json(reservation_path, "Akashic reservation")
    expected_path = f"12-agent-submissions/{package_relative_path}"
    if (
        reservation.get("schema") != "akashic-package-reservation/v2"
        or reservation.get("package_id") != package.name
        or reservation.get("path") != expected_path
        or reservation.get("lifecycle_state") != "pending"
    ):
        fail("akashic_reservation_binding", "package reservation does not match the run destination")
    manifest_path = package_path(package_root, package, "manifest.yaml")
    manifest = load_simple_yaml_mapping(manifest_path, "Akashic manifest.yaml")
    if (
        manifest.get("schema_version") != 2
        or manifest.get("package_id") != package.name
        or manifest.get("status") != "pending"
        or manifest.get("formal_absorption") is not False
    ):
        fail("akashic_manifest_boundary", "Akashic root manifest must remain pending and unabsorbed")
    package_path(package_root, package, "submission.md")
    return {
        "reservation_path": ".reservation.json",
        "reservation_sha256": sha256_file(reservation_path),
        "manifest_path": "manifest.yaml",
        "manifest_sha256": sha256_file(manifest_path),
    }


def load_jsonl(path: Path, field: str) -> tuple[list[dict[str, Any]], list[bytes]]:
    raw = path.read_bytes()
    if raw and not raw.endswith(b"\n"):
        fail("invalid_jsonl", f"{field} must end with LF", path=str(path))
    rows: list[dict[str, Any]] = []
    lines = raw.splitlines(keepends=True)
    for index, line in enumerate(lines, 1):
        if not line.strip():
            fail("invalid_jsonl", f"{field} contains a blank line", line=index)
        try:
            value = json.loads(line.decode("utf-8"))
        except (UnicodeError, json.JSONDecodeError) as error:
            fail("invalid_jsonl", f"cannot parse {field} line", line=index, error=str(error))
        rows.append(require_object(value, f"{field}[{index}]"))
    return rows, lines


def inventory_tree(
    root: Path,
    *,
    exclude_names: set[str] | None = None,
    exclude_relatives: set[str] | None = None,
) -> tuple[dict[str, str], int]:
    excluded_names = exclude_names or set()
    excluded_relatives = exclude_relatives or set()
    files_by_path: dict[str, str] = {}
    total_bytes = 0
    for current, directories, files in os.walk(root, followlinks=False):
        current_path = Path(current)
        kept_directories: list[str] = []
        for name in sorted(directories, key=lambda item: item.encode("utf-8")):
            path = current_path / name
            if path.is_symlink():
                fail("symlink_forbidden", "tree inventory found a symlink", path=str(path))
            if name not in excluded_names:
                kept_directories.append(name)
        directories[:] = kept_directories
        for name in sorted(files, key=lambda item: item.encode("utf-8")):
            path = current_path / name
            relative = path.relative_to(root).as_posix()
            if name in excluded_names or path.suffix == ".pyc" or relative in excluded_relatives:
                continue
            if path.is_symlink():
                fail("symlink_forbidden", "tree inventory found a symlink", path=str(path))
            if not path.is_file():
                fail("non_regular_file", "tree inventory requires regular files", path=str(path))
            data = path.read_bytes()
            files_by_path[relative] = sha256_bytes(data)
            total_bytes += len(data)
    return files_by_path, total_bytes


def tree_sha256(files_by_path: dict[str, str]) -> str:
    digest = hashlib.sha256()
    for relative in sorted(files_by_path, key=lambda value: value.encode("utf-8")):
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(files_by_path[relative].encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def plugin_runtime_inventory(plugin_root: Path) -> tuple[dict[str, str], int]:
    """Inventory exactly the runtime-bearing plugin manifest and Skill tree."""

    plugin_path = confined(plugin_root, "plugin.json", field="plugin manifest")
    skill_root = confined(
        plugin_root,
        SKILL_RELATIVE,
        kind="directory",
        field="orchestrator Skill root",
    )
    skill_files, skill_bytes = inventory_tree(
        skill_root,
        exclude_names=EXCLUDED_BUNDLED_NAMES,
    )
    files = {"plugin.json": sha256_file(plugin_path)}
    files.update(
        {
            (SKILL_RELATIVE / relative).as_posix(): digest
            for relative, digest in skill_files.items()
        }
    )
    return files, plugin_path.stat().st_size + skill_bytes


def observe_git_state(plugin_root: Path, runtime_paths: set[str]) -> dict[str, Any]:
    """Return independent current Git observations, or explicit nulls off Git."""

    def run_git_at(
        directory: Path,
        *arguments: str,
    ) -> subprocess.CompletedProcess[bytes] | None:
        try:
            return subprocess.run(
                ["git", "-C", str(directory), *arguments],
                check=False,
                capture_output=True,
            )
        except OSError:
            return None

    root_result = run_git_at(plugin_root, "rev-parse", "--show-toplevel")
    if root_result is None or root_result.returncode != 0:
        return {
            "repository_present": False,
            "repository_root": None,
            "head_commit": None,
            "runtime_tree_tracked": None,
            "package_dirty": None,
        }
    try:
        repository_root = Path(root_result.stdout.decode("utf-8").strip()).resolve()
        plugin_relative = plugin_root.relative_to(repository_root).as_posix()
    except (UnicodeError, OSError, ValueError):
        return {
            "repository_present": False,
            "repository_root": None,
            "head_commit": None,
            "runtime_tree_tracked": None,
            "package_dirty": None,
        }

    head_result = run_git_at(repository_root, "rev-parse", "--verify", "HEAD")
    head_commit: str | None = None
    if head_result is not None and head_result.returncode == 0:
        candidate = head_result.stdout.decode("ascii", errors="ignore").strip()
        if re.fullmatch(r"[0-9a-f]{40,64}", candidate):
            head_commit = candidate

    tracked_result = run_git_at(
        repository_root,
        "ls-files",
        "-z",
        "--",
        plugin_relative,
    )
    runtime_tree_tracked: bool | None = None
    if tracked_result is not None and tracked_result.returncode == 0:
        tracked = {
            item.decode("utf-8")
            for item in tracked_result.stdout.split(b"\0")
            if item
        }
        expected = {
            (PurePosixPath(plugin_relative) / PurePosixPath(relative)).as_posix()
            for relative in runtime_paths
        }
        runtime_tree_tracked = expected.issubset(tracked)

    dirty_result = run_git_at(
        repository_root,
        "status",
        "--porcelain=v1",
        "-z",
        "--",
        plugin_relative,
    )
    package_dirty: bool | None = None
    if dirty_result is not None and dirty_result.returncode == 0:
        package_dirty = bool(dirty_result.stdout)

    return {
        "repository_present": True,
        "repository_root": str(repository_root),
        "head_commit": head_commit,
        "runtime_tree_tracked": runtime_tree_tracked,
        "package_dirty": package_dirty,
    }


def plugin_evidence(plugin_root: Path) -> dict[str, Any]:
    runtime_files, runtime_bytes = plugin_runtime_inventory(plugin_root)
    bundled_root = confined(
        plugin_root,
        BUNDLED_RELATIVE,
        kind="directory",
        field="bundled runtime tree",
    )
    bundled_files, bundled_bytes = inventory_tree(
        bundled_root,
        exclude_names=EXCLUDED_BUNDLED_NAMES,
    )
    critical_files: dict[str, str] = {}
    for relative in CRITICAL_RUNTIME_RELATIVES:
        path = confined(plugin_root, relative, field=f"critical runtime file {relative}")
        critical_files[relative.as_posix()] = sha256_file(path)
    return {
        "runtime_tree": {
            "file_count": len(runtime_files),
            "total_bytes": runtime_bytes,
            "tree_sha256": tree_sha256(runtime_files),
        },
        "critical_files": critical_files,
        "bundled_tree": {
            "file_count": len(bundled_files),
            "total_bytes": bundled_bytes,
            "tree_sha256": tree_sha256(bundled_files),
        },
        "git_observation": observe_git_state(plugin_root, set(runtime_files)),
    }


def validate_skill_frontmatter(path: Path) -> None:
    try:
        text = path.read_text(encoding="utf-8")
    except (OSError, UnicodeError) as error:
        fail("invalid_skill", "cannot read SKILL.md", path=str(path), error=str(error))
    lines = text.splitlines()
    if not lines or lines[0] != "---":
        fail("invalid_skill", "SKILL.md must start with YAML frontmatter", path=str(path))
    try:
        end = lines.index("---", 1)
    except ValueError:
        fail("invalid_skill", "SKILL.md frontmatter is not closed", path=str(path))
    fields: dict[str, str] = {}
    for line in lines[1:end]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip('"').strip("'")
    if fields.get("name") != SKILL_NAME:
        fail("invalid_skill", "unexpected Skill name", observed=fields.get("name"))
    if not fields.get("description"):
        fail("invalid_skill", "Skill description is required")


def validate_bundled_skill_frontmatter(path: Path, component_id: str) -> str:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except (OSError, UnicodeError) as error:
        fail("invalid_bundled_skill", "cannot read bundled SKILL.md", component=component_id, error=str(error))
    if not lines or lines[0] != "---":
        fail("invalid_bundled_skill", "bundled SKILL.md lacks frontmatter", component=component_id)
    try:
        end = lines.index("---", 1)
    except ValueError:
        fail("invalid_bundled_skill", "bundled SKILL.md frontmatter is not closed", component=component_id)
    fields: dict[str, str] = {}
    for line in lines[1:end]:
        if ":" not in line:
            continue
        key, value = line.split(":", 1)
        fields[key.strip()] = value.strip().strip('"').strip("'")
    name = fields.get("name")
    if not isinstance(name, str) or not name or not COMPONENT_ID_PATTERN.fullmatch(name):
        fail("invalid_bundled_skill", "bundled Skill name is invalid", component=component_id, name=name)
    if not fields.get("description"):
        fail("invalid_bundled_skill", "bundled Skill description is missing", component=component_id)
    return name


def validate_plugin_manifest(path: Path) -> dict[str, Any]:
    manifest = load_json(path, "plugin.json")
    unknown = sorted(set(manifest) - ALLOWED_PLUGIN_FIELDS)
    if unknown:
        fail("unknown_plugin_fields", "plugin.json has unknown top-level fields", fields=unknown)
    if manifest.get("$schema") != PLUGIN_SCHEMA:
        fail("plugin_schema_mismatch", "plugin.json targets the wrong schema")
    name = manifest.get("name")
    if not isinstance(name, str) or not 1 <= len(name) <= 64 or not PLUGIN_NAME_PATTERN.fullmatch(name):
        fail("invalid_plugin_name", "plugin.json name is invalid", observed=name)
    if name != PLUGIN_NAME:
        fail("plugin_name_mismatch", "unexpected plugin name", observed=name)
    if manifest.get("version") != PLUGIN_VERSION:
        fail("plugin_version_mismatch", "unexpected plugin version", observed=manifest.get("version"))
    if "description" in manifest and not isinstance(manifest["description"], str):
        fail("invalid_plugin_description", "plugin description must be a string")
    keywords = manifest.get("keywords", [])
    if not isinstance(keywords, list) or not all(isinstance(item, str) for item in keywords):
        fail("invalid_plugin_keywords", "plugin keywords must be strings")
    return manifest


def validate_bundled_manifest(
    plugin_root: Path, manifest_path: Path
) -> tuple[dict[str, Any], dict[str, dict[str, Any]]]:
    manifest = load_json(manifest_path, "bundled/source-manifest.json")
    if manifest.get("schema") != BUNDLED_SCHEMA:
        fail("bundled_schema_mismatch", "unexpected bundled source-manifest schema")
    if manifest.get("portable") is not True:
        fail("bundled_not_portable", "bundled source manifest must declare portable true")
    if manifest.get("absolute_source_paths_persisted") is not False:
        fail("absolute_source_paths", "bundled manifest must forbid persisted absolute source paths")
    if manifest.get("symlinks_allowed") is not False:
        fail("bundled_symlink_policy", "bundled manifest must declare symlinks_allowed false")
    if manifest.get("tree_hash_algorithm") != TREE_HASH_ALGORITHM:
        fail("tree_hash_algorithm_mismatch", "unexpected bundled tree hash algorithm")
    components = require_list(manifest.get("components"), "bundled.components")
    expected = list(EXPERT_COMPONENTS) + [FUXI_COMPONENT]
    if len(components) != len(expected):
        fail("component_count", "bundled manifest must contain eight experts and Fuxi", observed=len(components))
    records: dict[str, dict[str, Any]] = {}
    targets: set[str] = set()
    bundled_root = confined(plugin_root, BUNDLED_RELATIVE, kind="directory", field="bundled root")
    for index, ((expected_id, expected_name), value) in enumerate(zip(expected, components), 1):
        component = require_object(value, f"bundled.components[{index}]")
        component_id = component.get("id")
        if component_id != expected_id or not isinstance(component_id, str) or not COMPONENT_ID_PATTERN.fullmatch(component_id):
            fail(
                "component_identity_mismatch",
                "bundled component ID/order is not the fixed roster",
                expected=expected_id,
                observed=component_id,
            )
        if component.get("source_name") != expected_name:
            fail(
                "component_identity_mismatch",
                "bundled source_name does not match fixed roster",
                component=component_id,
                expected=expected_name,
                observed=component.get("source_name"),
            )
        expected_scope = "claude-user-skills" if component_id == "fuxi-skill" else "minimax-user-skills"
        if component.get("source_scope") != expected_scope:
            fail("component_scope_mismatch", "unexpected source_scope", component=component_id)
        target = relative_posix(component.get("target"), f"component {component_id} target").as_posix()
        if target in targets:
            fail("duplicate_component_target", "component target is duplicated", target=target)
        targets.add(target)
        component_root = confined(bundled_root, target, kind="directory", field=f"component {component_id}")
        skill_path = confined(component_root, "SKILL.md", field=f"component {component_id} SKILL.md")
        bundled_skill_name = validate_bundled_skill_frontmatter(skill_path, component_id)
        declared_skill_sha = require_hex(component.get("skill_md_sha256"), f"{component_id}.skill_md_sha256")
        if sha256_file(skill_path) != declared_skill_sha:
            fail("component_skill_hash_mismatch", "component SKILL.md hash mismatch", component=component_id)
        files_by_path, total_bytes = inventory_tree(component_root, exclude_names=EXCLUDED_BUNDLED_NAMES)
        actual_tree_sha = tree_sha256(files_by_path)
        if component.get("file_count") != len(files_by_path):
            fail("component_file_count_mismatch", "component file count mismatch", component=component_id)
        if component.get("total_bytes") != total_bytes:
            fail("component_byte_count_mismatch", "component byte count mismatch", component=component_id)
        if require_hex(component.get("tree_sha256"), f"{component_id}.tree_sha256") != actual_tree_sha:
            fail("component_tree_hash_mismatch", "component tree hash mismatch", component=component_id)
        records[component_id] = {
            **component,
            "bundled_skill_name": bundled_skill_name,
            "skill_path": (Path("bundled") / target / "SKILL.md").as_posix(),
        }
    return manifest, records


def validate_plugin(plugin_root_input: Path) -> dict[str, Any]:
    plugin_root = normalized_root(plugin_root_input, "plugin root")
    assert_no_symlinks(plugin_root)
    plugin_path = confined(plugin_root, "plugin.json", field="plugin manifest")
    plugin_manifest = validate_plugin_manifest(plugin_path)
    if (plugin_root / "mcp.json").exists() or (plugin_root / "mcp.json").is_symlink():
        fail("unexpected_mcp", "mcp.json is forbidden for this skills-only plugin")
    skills_root = confined(plugin_root, "skills", kind="directory", field="skills root")
    discovered: list[str] = []
    for child in sorted(skills_root.iterdir(), key=lambda item: item.name.encode("utf-8")):
        if child.is_symlink():
            fail("symlink_forbidden", "skills immediate child is a symlink", path=str(child))
        if child.is_dir() and (child / "SKILL.md").is_file():
            discovered.append(child.name)
    if discovered != [SKILL_NAME]:
        fail(
            "skill_discovery_mismatch",
            "Agent Plugins v1 layout must expose exactly one immediate Skill",
            discoverable=discovered,
        )
    skill_path = confined(plugin_root, SKILL_RELATIVE / "SKILL.md", field="orchestrator SKILL.md")
    validate_skill_frontmatter(skill_path)
    source_manifest_path = confined(plugin_root, SOURCE_MANIFEST_RELATIVE, field="bundled source manifest")
    bundled_manifest, components = validate_bundled_manifest(plugin_root, source_manifest_path)
    evidence = plugin_evidence(plugin_root)
    return {
        "ok": True,
        "mode": "plugin",
        "plugin_root": str(plugin_root),
        "plugin": {
            "name": plugin_manifest["name"],
            "version": plugin_manifest["version"],
            "schema": plugin_manifest["$schema"],
        },
        "discoverable_skills": discovered,
        "runtime_discovery_state": "not_evaluated",
        "mcp_present": False,
        "bundled_manifest_sha256": sha256_file(source_manifest_path),
        "bundled_schema": bundled_manifest["schema"],
        "expert_components": [item[0] for item in EXPERT_COMPONENTS],
        "fuxi_component": FUXI_COMPONENT[0],
        "component_count": len(components),
        "symlinks": False,
        "candidate_only": True,
        **evidence,
    }


def package_path(package_root: Path, package: Path, relative: str, *, kind: str = "file") -> Path:
    return confined(package, relative, kind=kind, field=relative)


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


def normalize_windows_link_target(raw_target: str) -> str:
    """Remove the NT namespace prefix returned by os.readlink on Windows."""
    for unc_prefix in ("\\\\?\\UNC\\", "\\??\\UNC\\"):
        if raw_target.startswith(unc_prefix):
            return "\\\\" + raw_target[len(unc_prefix) :]
    for device_prefix in ("\\\\?\\", "\\??\\"):
        if raw_target.startswith(device_prefix):
            return raw_target[len(device_prefix) :]
    return raw_target


def validate_runtime_operation_receipt(
    package: Path,
    receipt_relative_value: Any,
    *,
    runtime_kind: str,
    role: str,
    context_id: str,
    artifact_relative: str,
    artifact_sha256: str,
    field: str,
) -> dict[str, Any]:
    try:
        receipt_relative = relative_posix(
            receipt_relative_value,
            f"{field}.operation_receipt_path",
        ).as_posix()
    except ValidationError as error:
        fail(
            "execution_receipt_missing",
            f"{field} requires a confined runtime operation receipt",
            cause=error.code,
        )
    if not receipt_relative.startswith("payload/runtime-receipts/"):
        fail(
            "execution_receipt_binding",
            f"{field} operation receipt must live below payload/runtime-receipts",
            path=receipt_relative,
        )
    receipt_path = package / receipt_relative
    if receipt_path.is_symlink() or not receipt_path.is_file():
        fail(
            "execution_receipt_missing",
            f"{field} runtime operation receipt is missing",
            path=receipt_relative,
        )
    receipt_path = confined(
        package,
        receipt_relative,
        field=f"{field}.operation_receipt_path",
    )
    receipt = load_json(receipt_path, f"{field} runtime operation receipt")
    reject_hidden_runtime_evidence(receipt, field)
    if (
        receipt.get("schema") != RUNTIME_OPERATION_SCHEMA
        or receipt.get("evidence_origin") != "runtime_tool_result"
        or receipt.get("runtime") != runtime_kind
        or receipt.get("role") != role
        or receipt.get("status") != "succeeded"
        or receipt.get("context_id") != context_id
        or receipt.get("artifact_path") != artifact_relative
        or receipt.get("artifact_sha256") != artifact_sha256
    ):
        fail(
            "execution_receipt_binding",
            f"{field} runtime operation receipt does not bind the completed artifact",
            path=receipt_relative,
        )
    require_runtime_identifier(receipt.get("operation_id"), f"{field}.operation_id")
    started = parsed_time(receipt.get("started_at"), f"{field}.started_at")
    completed = parsed_time(receipt.get("completed_at"), f"{field}.completed_at")
    if completed < started:
        fail("execution_receipt_order", f"{field} completion precedes its start")

    if runtime_kind == "codex":
        creation = require_object(receipt.get("create_thread"), f"{field}.create_thread")
        actual_tool = require_nonempty_string(
            creation.get("actual_tool"),
            f"{field}.create_thread.actual_tool",
        )
        lowered_tool = actual_tool.lower()
        if (
            any(marker in lowered_tool for marker in FORBIDDEN_RUNTIME_TOOL_MARKERS)
            or tool_leaf(actual_tool) != "create_thread"
        ):
            fail(
                "invalid_visible_task_evidence",
                f"{field} Codex execution must come from create_thread",
                actual_tool=actual_tool,
            )
        if (
            creation.get("status") != "created_confirmed"
            or creation.get("surface") != "visible_thread"
            or creation.get("task_kind") != "codex"
            or creation.get("thread_id") != context_id
            or creation.get("client_thread_id") is not None
            or not isinstance(creation.get("host_id"), str)
            or not creation["host_id"].strip()
            or creation.get("prompt_verified") not in {"receipt", "readback"}
            or creation.get("failure") is not None
        ):
            fail(
                "invalid_visible_task_evidence",
                f"{field} lacks a confirmed visible create_thread receipt",
            )
        require_runtime_identifier(context_id, f"{field}.context_id")
        readback = require_object(
            receipt.get("result_readback"),
            f"{field}.result_readback",
        )
        if (
            readback.get("status") != "succeeded"
            or readback.get("thread_id") != context_id
            or readback.get("host_id") != creation.get("host_id")
            or readback.get("artifact_path") != artifact_relative
            or readback.get("artifact_sha256") != artifact_sha256
        ):
            fail(
                "execution_readback_binding",
                f"{field} visible task result readback does not bind the artifact",
            )
        parse_time(readback.get("read_at"), f"{field}.result_readback.read_at")
    else:
        operation = require_object(
            receipt.get("provider_operation"),
            f"{field}.provider_operation",
        )
        actual_tool = require_nonempty_string(
            operation.get("actual_tool"),
            f"{field}.provider_operation.actual_tool",
        )
        if any(
            marker in actual_tool.lower()
            for marker in FORBIDDEN_RUNTIME_TOOL_MARKERS
        ):
            fail(
                "hidden_subagent_evidence",
                f"{field} provider operation cannot be hidden-subagent evidence",
            )
        require_runtime_identifier(
            operation.get("receipt_id"),
            f"{field}.provider_operation.receipt_id",
        )
        if operation.get("result_state") != "succeeded":
            fail(
                "execution_readback_binding",
                f"{field} provider operation has no successful result readback",
            )
    return {
        "path": receipt_relative,
        "sha256": sha256_file(receipt_path),
        "context_id": context_id,
    }


def validate_executor_binding(
    value: Any,
    *,
    package: Path,
    runtime: dict[str, Any],
    expected_kind: str,
    role: str,
    artifact_relative: str,
    artifact_sha256: str,
    field: str,
) -> tuple[str, dict[str, Any]]:
    executor = require_object(value, field)
    reject_hidden_runtime_evidence(executor, field)
    if executor.get("runtime") != runtime["kind"] or executor.get("kind") != expected_kind:
        fail(
            "executor_identity_mismatch",
            f"{field} used the wrong runtime executor",
            role=role,
        )
    context_id = require_runtime_identifier(
        executor.get("context_id"),
        f"{field}.context_id",
    )
    operation = validate_runtime_operation_receipt(
        package,
        executor.get("operation_receipt_path"),
        runtime_kind=runtime["kind"],
        role=role,
        context_id=context_id,
        artifact_relative=artifact_relative,
        artifact_sha256=artifact_sha256,
        field=field,
    )
    return context_id, operation


def validate_runtime(runtime_value: Any) -> dict[str, Any]:
    runtime = require_object(runtime_value, "manifest.runtime")
    kind = require_nonempty_string(runtime.get("kind"), "manifest.runtime.kind")
    auditor_kind = require_nonempty_string(runtime.get("auditor_kind"), "manifest.runtime.auditor_kind")
    if kind == "minimax-code" and auditor_kind != "minimax-default-verifier":
        fail("verifier_route_mismatch", "MiniMaxCode must use its default Verifier")
    if kind == "codex" and auditor_kind != "codex-independent":
        fail("verifier_route_mismatch", "Codex must use an independent Codex auditor")
    if kind not in {"minimax-code", "codex"} and auditor_kind == "minimax-default-verifier":
        fail("verifier_route_mismatch", "non-MiniMax runtime cannot default to MiniMax Verifier")
    return runtime


def plugin_validation_command(plugin_root: Path) -> list[str]:
    return [
        "python3",
        "-B",
        VALIDATOR_RELATIVE.as_posix(),
        "plugin",
        "--plugin-root",
        str(plugin_root),
    ]


def validate_plugin_validation_receipt(
    package: Path,
    plugin_root: Path,
    plugin_report: dict[str, Any],
) -> dict[str, Any]:
    relative = "payload/receipts/plugin-validation.json"
    path = confined(package, relative, field="plugin-validation receipt")
    receipt = load_json(path, "plugin-validation receipt")
    expected_fields = {
        "schema",
        "schema_version",
        "ok",
        "plugin",
        "runtime_tree",
        "critical_files",
        "bundled",
        "validator",
        "validator_result",
        "git_observation",
        "validated_at",
    }
    expected_bundled = {
        "manifest_path": SOURCE_MANIFEST_RELATIVE.as_posix(),
        "manifest_sha256": plugin_report["bundled_manifest_sha256"],
        "tree": plugin_report["bundled_tree"],
    }
    expected_validator = {
        "path": VALIDATOR_RELATIVE.as_posix(),
        "sha256": plugin_report["critical_files"][VALIDATOR_RELATIVE.as_posix()],
        "command": plugin_validation_command(plugin_root),
    }
    if (
        set(receipt) != expected_fields
        or receipt.get("schema") != PLUGIN_RECEIPT_SCHEMA
        or receipt.get("schema_version") != 2
        or receipt.get("ok") is not True
        or receipt.get("plugin") != plugin_report["plugin"]
        or receipt.get("runtime_tree") != plugin_report["runtime_tree"]
        or receipt.get("critical_files") != plugin_report["critical_files"]
        or receipt.get("bundled") != expected_bundled
        or receipt.get("validator") != expected_validator
        or receipt.get("git_observation") != plugin_report["git_observation"]
    ):
        fail(
            "plugin_validation_binding",
            "plugin-validation receipt v2 does not bind the current runtime tree and validator",
        )
    result_ref = require_object(
        receipt.get("validator_result"),
        "plugin-validation.validator_result",
    )
    result_relative = relative_posix(
        result_ref.get("path"),
        "plugin-validation.validator_result.path",
    ).as_posix()
    if result_relative != "payload/validation/plugin-validator-result.json":
        fail(
            "plugin_validation_binding",
            "plugin validator result must use the declared validation path",
            path=result_relative,
        )
    result_path = confined(package, result_relative, field="plugin validator result")
    if require_hex(
        result_ref.get("sha256"),
        "plugin-validation.validator_result.sha256",
    ) != sha256_file(result_path):
        fail("plugin_validation_binding", "plugin validator result hash is stale")
    result = load_json(result_path, "plugin validator result")
    if result != plugin_report:
        fail(
            "plugin_validation_binding",
            "recorded plugin validator result differs from current validation",
        )
    parse_time(receipt.get("validated_at"), "plugin-validation.validated_at")
    return {
        "path": relative,
        "sha256": sha256_file(path),
        "schema": PLUGIN_RECEIPT_SCHEMA,
        "runtime_tree_sha256": plugin_report["runtime_tree"]["tree_sha256"],
        "git_observation": plugin_report["git_observation"],
    }


def validate_skill_discovery_receipt(
    package: Path,
    binding: dict[str, Any],
    *,
    runtime: dict[str, Any],
    registered_skill: Path,
    canonical_realpath: Path,
    skill_sha256: str,
) -> dict[str, Any]:
    relative = relative_posix(
        binding.get("discovery_receipt_path"),
        "run-init.acquisition_executor.discovery_receipt_path",
    ).as_posix()
    if not relative.startswith("payload/runtime-receipts/"):
        fail(
            "acquisition_executor_discovery_unverified",
            "Paper Downloader discovery receipt must live below payload/runtime-receipts",
        )
    path = package / relative
    if path.is_symlink() or not path.is_file():
        fail(
            "acquisition_executor_discovery_unverified",
            "Paper Downloader link exists but runtime discovery is not receipted",
            path=relative,
        )
    path = confined(package, relative, field="Paper Downloader discovery receipt")
    expected_sha = require_hex(
        binding.get("discovery_receipt_sha256"),
        "run-init.acquisition_executor.discovery_receipt_sha256",
    )
    if sha256_file(path) != expected_sha:
        fail(
            "acquisition_executor_discovery_unverified",
            "Paper Downloader discovery receipt hash is stale",
        )
    receipt = load_json(path, "Paper Downloader discovery receipt")
    reject_hidden_runtime_evidence(receipt, "Paper Downloader discovery receipt")
    if (
        receipt.get("schema") != SKILL_DISCOVERY_SCHEMA
        or receipt.get("evidence_origin") != "runtime_skill_catalog"
        or receipt.get("runtime") != runtime["kind"]
        or receipt.get("status") != "discovered"
        or receipt.get("consumer_skill_path") != str(registered_skill)
        or receipt.get("canonical_realpath") != str(canonical_realpath)
        or receipt.get("skill_sha256") != skill_sha256
    ):
        fail(
            "acquisition_executor_discovery_unverified",
            "Paper Downloader discovery receipt does not bind the linked consumer and canonical source",
        )
    require_runtime_identifier(receipt.get("receipt_id"), "skill-discovery.receipt_id")
    parse_time(receipt.get("observed_at"), "skill-discovery.observed_at")
    return {
        "path": relative,
        "sha256": expected_sha,
        "receipt_structurally_validated": True,
        "runtime_state": RUNTIME_NOT_VERIFIED,
    }


def validate_acquisition_executor(
    value: Any,
    plugin_root: Path,
    package: Path,
    runtime: dict[str, Any],
) -> dict[str, Any]:
    binding = require_object(value, "run-init.acquisition_executor")
    required = {
        "name",
        "registered_skill_path",
        "canonical_realpath",
        "skill_sha256",
        "verified_at",
        "consumer_link_state",
        "discovery_receipt_path",
        "discovery_receipt_sha256",
    }
    if (
        set(binding) != required
        or binding.get("name") != PAPER_DOWNLOADER_NAME
        or binding.get("consumer_link_state") != "linked"
    ):
        fail(
            "acquisition_executor_binding",
            "run-init must separate Paper Downloader source, linked consumer, and discovery evidence",
        )

    canonical_root = plugin_root.parent / PAPER_DOWNLOADER_NAME
    if canonical_root.is_symlink() or not canonical_root.is_dir():
        fail(
            "acquisition_executor_unavailable",
            "canonical Paper Downloader package is missing or is not a real directory",
            path=str(canonical_root),
        )
    canonical_skill = canonical_root / "SKILL.md"
    if canonical_skill.is_symlink() or not canonical_skill.is_file():
        fail(
            "acquisition_executor_unavailable",
            "canonical Paper Downloader SKILL.md is missing or symlinked",
            path=str(canonical_skill),
        )

    registered_skill = Path(
        require_nonempty_string(
            binding.get("registered_skill_path"),
            "run-init.acquisition_executor.registered_skill_path",
        )
    ).expanduser()
    if not registered_skill.is_absolute():
        fail(
            "acquisition_executor_binding",
            "registered Paper Downloader Skill path must be absolute",
        )
    collection_root = Path(os.path.abspath(plugin_root.parent.parent))
    registered_lexical_path = Path(os.path.abspath(registered_skill))
    try:
        registered_lexical_path.relative_to(collection_root)
    except ValueError:
        pass
    else:
        fail(
            "acquisition_executor_unavailable",
            "registered Paper Downloader Skill must be an external Agent consumer, not a collection source or wrapper projection",
            path=str(registered_lexical_path),
        )
    expected_realpath = canonical_root.resolve()
    registered_package = registered_lexical_path.parent
    try:
        raw_target = Path(
            normalize_windows_link_target(os.readlink(registered_package))
        )
    except OSError as error:
        fail(
            "acquisition_executor_unavailable",
            "registered Paper Downloader consumer must be a direct package link",
            path=str(registered_package),
            error=str(error),
        )
    if not raw_target.is_absolute():
        raw_target = registered_package.parent / raw_target
    direct_target = Path(os.path.abspath(raw_target))
    if (
        is_link_or_junction(direct_target)
        or not direct_target.is_dir()
        or direct_target.resolve() != expected_realpath
    ):
        fail(
            "acquisition_executor_unavailable",
            "registered Paper Downloader consumer does not link directly to the canonical package",
            path=str(registered_package),
            target=str(direct_target),
        )
    try:
        registered_realpath = registered_skill.resolve(strict=True)
    except OSError as error:
        fail(
            "acquisition_executor_unavailable",
            "registered Paper Downloader Skill is unreadable",
            path=str(registered_skill),
            error=str(error),
        )

    expected_skill = canonical_skill.resolve()
    if registered_realpath != expected_skill:
        fail(
            "acquisition_executor_unavailable",
            "registered Paper Downloader Skill does not resolve directly to the canonical package",
            registered_realpath=str(registered_realpath),
            expected=str(expected_skill),
        )
    if binding.get("canonical_realpath") != str(expected_realpath):
        fail(
            "acquisition_executor_binding",
            "recorded Paper Downloader canonical realpath is stale or incorrect",
            expected=str(expected_realpath),
        )
    expected_sha = sha256_file(canonical_skill)
    if require_hex(
        binding.get("skill_sha256"),
        "run-init.acquisition_executor.skill_sha256",
    ) != expected_sha:
        fail(
            "acquisition_executor_hash_mismatch",
            "recorded Paper Downloader SKILL.md hash differs from the canonical source",
            expected=expected_sha,
        )
    parse_time(
        binding.get("verified_at"),
        "run-init.acquisition_executor.verified_at",
    )
    discovery = validate_skill_discovery_receipt(
        package,
        binding,
        runtime=runtime,
        registered_skill=registered_skill,
        canonical_realpath=expected_realpath,
        skill_sha256=expected_sha,
    )
    return {
        "name": PAPER_DOWNLOADER_NAME,
        "registered_skill_path": str(registered_skill),
        "canonical_realpath": str(expected_realpath),
        "skill_sha256": expected_sha,
        "source_state": "validated",
        "consumer_link_state": "linked",
        "runtime_discovery_state": discovery["runtime_state"],
        "discovery_receipt_structurally_validated": discovery[
            "receipt_structurally_validated"
        ],
        "runtime_execution_verified": False,
        "discovery_receipt": discovery,
    }


def validate_rule_binding(
    value: Any,
    expected_sha: str,
    field: str,
    *,
    expected_bytes: int | None = None,
) -> dict[str, Any]:
    rule = require_object(value, field)
    if rule.get("path") != str(LIVE_RULE):
        fail("rule_path_mismatch", f"{field}.path must be the live Akashic rule")
    if require_hex(rule.get("sha256"), f"{field}.sha256") != expected_sha:
        fail("rule_hash_mismatch", f"{field}.sha256 differs from the run baseline")
    if not isinstance(rule.get("bytes"), int) or rule["bytes"] <= 0:
        fail("invalid_rule_receipt", f"{field}.bytes must be positive")
    if expected_bytes is not None and rule["bytes"] != expected_bytes:
        fail("invalid_rule_receipt", f"{field}.bytes differs from live rule readback")
    parse_time(rule.get("read_at"), f"{field}.read_at")
    return rule


def normalize_publication_identity(row: dict[str, Any], field: str) -> str:
    doi = row.get("doi")
    if isinstance(doi, str) and doi.strip():
        value = doi.strip().lower()
        for prefix in ("https://doi.org/", "http://doi.org/", "doi:"):
            if value.startswith(prefix):
                value = value[len(prefix) :]
                break
        return f"doi:{value}"
    pmid = row.get("pmid")
    if isinstance(pmid, (str, int)) and str(pmid).strip():
        return f"pmid:{str(pmid).strip()}"
    pmcid = row.get("pmcid")
    if isinstance(pmcid, str) and pmcid.strip():
        return f"pmcid:{pmcid.strip().upper()}"
    url = row.get("original_publication_url")
    if isinstance(url, str) and url.strip():
        parsed = urlsplit(url.strip())
        if parsed.scheme not in {"http", "https"} or not parsed.netloc:
            fail("invalid_publication_url", f"{field} must be an HTTP(S) URL")
        path = parsed.path.rstrip("/") or "/"
        normalized = urlunsplit(
            (parsed.scheme.lower(), parsed.netloc.lower(), path, parsed.query, "")
        )
        return f"url:{normalized}"
    fail("publication_identity_missing", f"{field} has no stable publication identity")


def source_ids_sha256(source_ids: Iterable[str]) -> str:
    data = "".join(f"{source_id}\n" for source_id in sorted(source_ids)).encode("utf-8")
    return sha256_bytes(data)


def validate_candidate_text(path: Path, artifact_type: str, artifact_id: str) -> None:
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        fail("candidate_not_utf8", "candidate report must be UTF-8 text", artifact_id=artifact_id)
    nonspace = sum(not character.isspace() for character in text)
    minimum = MIN_EXPERT_NONSPACE if artifact_type == "expert" else MIN_SYNTHESIS_NONSPACE
    nonempty_lines = sum(bool(line.strip()) for line in text.splitlines())
    if nonspace < minimum or nonempty_lines < 5:
        fail(
            "candidate_too_thin",
            "candidate report is empty or obviously incomplete",
            artifact_id=artifact_id,
            nonspace=nonspace,
            nonempty_lines=nonempty_lines,
            minimum=minimum,
        )


PDF_WHITESPACE = b" \t\r\n\f\x00"
PDF_HEADER_PATTERN = re.compile(br"\A%PDF-(?:1\.[0-7]|2\.0)(?:\r\n|\r|\n)")
PDF_TERMINAL_PATTERN = re.compile(
    br"startxref[ \t]*(?:\r\n|\r|\n)+(\d+)[ \t]*"
    br"(?:\r\n|\r|\n)+%%EOF[ \t\r\n\f\x00]*\Z"
)


def invalid_pdf(source_id: str, message: str, **details: Any) -> None:
    fail("invalid_downloaded_pdf", message, source_id=source_id, **details)


def skip_pdf_whitespace(data: bytes, position: int, limit: int) -> int:
    while position < limit and data[position] in PDF_WHITESPACE:
        position += 1
    return position


def read_pdf_line(
    data: bytes,
    position: int,
    limit: int,
    source_id: str,
) -> tuple[bytes, int]:
    if position >= limit:
        invalid_pdf(source_id, "PDF cross-reference table ended unexpectedly")
    end = position
    while end < limit and data[end] not in b"\r\n":
        end += 1
    if end == limit:
        invalid_pdf(source_id, "PDF cross-reference line has no line ending")
    next_position = end + 1
    if data[end : end + 2] == b"\r\n":
        next_position = end + 2
    return data[position:end], next_position


def extract_pdf_dictionary(
    data: bytes,
    position: int,
    limit: int,
    source_id: str,
) -> tuple[bytes, int]:
    position = skip_pdf_whitespace(data, position, limit)
    if data[position : position + 2] != b"<<":
        invalid_pdf(source_id, "PDF cross-reference data has no trailer dictionary")
    start = position
    depth = 0
    literal_depth = 0
    while position < limit:
        if literal_depth:
            byte = data[position]
            if byte == 0x5C:  # backslash escape inside a literal string
                position += 2
                continue
            if byte == 0x28:
                literal_depth += 1
            elif byte == 0x29:
                literal_depth -= 1
            position += 1
            continue
        if data[position] == 0x25:  # comment
            while position < limit and data[position] not in b"\r\n":
                position += 1
            continue
        if data[position] == 0x28:
            literal_depth = 1
            position += 1
            continue
        if data[position : position + 2] == b"<<":
            depth += 1
            position += 2
            continue
        if data[position : position + 2] == b">>":
            depth -= 1
            position += 2
            if depth == 0:
                return data[start:position], position
            if depth < 0:
                break
            continue
        if data[position] == 0x3C:  # hexadecimal string, not a dictionary
            end = data.find(b">", position + 1, limit)
            if end < 0:
                invalid_pdf(source_id, "PDF trailer contains an unterminated hex string")
            position = end + 1
            continue
        position += 1
    invalid_pdf(source_id, "PDF trailer dictionary is unterminated")


def pdf_dictionary_integer(
    dictionary: bytes,
    name: bytes,
    source_id: str,
) -> int:
    match = re.search(
        br"/" + re.escape(name) + br"(?![A-Za-z0-9#])"
        br"[ \t\r\n\f\x00]+(\d+)(?!\d)",
        dictionary,
    )
    if match is None:
        invalid_pdf(source_id, f"PDF cross-reference dictionary lacks /{name.decode('ascii')}")
    return int(match.group(1))


def pdf_dictionary_reference(
    dictionary: bytes,
    name: bytes,
    source_id: str,
) -> tuple[int, int]:
    match = re.search(
        br"/" + re.escape(name) + br"(?![A-Za-z0-9#])"
        br"[ \t\r\n\f\x00]+(\d+)[ \t\r\n\f\x00]+"
        br"(\d+)[ \t\r\n\f\x00]+R(?![A-Za-z0-9])",
        dictionary,
    )
    if match is None:
        invalid_pdf(source_id, f"PDF cross-reference dictionary lacks /{name.decode('ascii')} reference")
    return int(match.group(1)), int(match.group(2))


def validate_pdf_object_offset(
    data: bytes,
    object_number: int,
    generation: int,
    offset: int,
    xref_offset: int,
    source_id: str,
) -> None:
    if offset <= 0 or offset > xref_offset:
        invalid_pdf(
            source_id,
            "PDF cross-reference entry points outside the object body",
            object_number=object_number,
            offset=offset,
        )
    marker = f"{object_number} {generation} obj".encode("ascii")
    if data[offset : offset + len(marker)] != marker:
        invalid_pdf(
            source_id,
            "PDF cross-reference entry does not match its indirect object",
            object_number=object_number,
            offset=offset,
        )
    following = offset + len(marker)
    if following >= len(data) or data[following] not in PDF_WHITESPACE:
        invalid_pdf(source_id, "PDF indirect object header has no token boundary")


def validate_classic_pdf_xref(
    data: bytes,
    xref_offset: int,
    startxref_position: int,
    source_id: str,
) -> None:
    if not data.startswith(b"xref", xref_offset):
        invalid_pdf(source_id, "PDF startxref does not point to an xref table")
    boundary = xref_offset + 4
    if boundary >= len(data) or data[boundary] not in PDF_WHITESPACE:
        invalid_pdf(source_id, "PDF xref token has no boundary")
    position = boundary
    entries: dict[int, tuple[int, int, bytes]] = {}
    saw_section = False
    while position < startxref_position:
        line, position = read_pdf_line(data, position, startxref_position, source_id)
        stripped = line.strip(PDF_WHITESPACE)
        if not stripped:
            continue
        if stripped == b"trailer":
            break
        section = re.fullmatch(br"(\d+)[ \t]+(\d+)", stripped)
        if section is None:
            invalid_pdf(source_id, "PDF xref subsection header is malformed")
        first_object = int(section.group(1))
        count = int(section.group(2))
        if count <= 0:
            invalid_pdf(source_id, "PDF xref subsection cannot be empty")
        saw_section = True
        for index in range(count):
            entry_line, position = read_pdf_line(
                data,
                position,
                startxref_position,
                source_id,
            )
            entry = re.fullmatch(
                br"(\d{10})[ \t]+(\d{5})[ \t]+([nf])[ \t]*",
                entry_line,
            )
            if entry is None:
                invalid_pdf(source_id, "PDF xref entry is malformed")
            object_number = first_object + index
            if object_number in entries:
                invalid_pdf(source_id, "PDF xref table repeats an object entry")
            entries[object_number] = (
                int(entry.group(1)),
                int(entry.group(2)),
                entry.group(3),
            )
    else:
        invalid_pdf(source_id, "PDF xref table has no trailer")
    if not saw_section or 0 not in entries or entries[0][2] != b"f":
        invalid_pdf(source_id, "PDF xref table lacks the required free object zero")

    dictionary, dictionary_end = extract_pdf_dictionary(
        data,
        position,
        startxref_position,
        source_id,
    )
    if data[dictionary_end:startxref_position].strip(PDF_WHITESPACE):
        invalid_pdf(source_id, "PDF has unexpected bytes between trailer and startxref")
    size = pdf_dictionary_integer(dictionary, b"Size", source_id)
    root_object, root_generation = pdf_dictionary_reference(
        dictionary,
        b"Root",
        source_id,
    )
    if size <= max(entries):
        invalid_pdf(source_id, "PDF trailer /Size does not cover the xref table")
    root_entry = entries.get(root_object)
    if root_entry is None or root_entry[2] != b"n" or root_entry[1] != root_generation:
        invalid_pdf(source_id, "PDF trailer /Root is not an in-use xref object")
    for object_number, (offset, generation, state) in entries.items():
        if state == b"n":
            validate_pdf_object_offset(
                data,
                object_number,
                generation,
                offset,
                xref_offset,
                source_id,
            )


def validate_pdf_xref_stream(
    data: bytes,
    xref_offset: int,
    startxref_position: int,
    source_id: str,
) -> None:
    header = re.match(
        br"(\d+)[ \t\r\n\f\x00]+(\d+)[ \t\r\n\f\x00]+obj"
        br"(?=[ \t\r\n\f\x00])",
        data[xref_offset:startxref_position],
    )
    if header is None:
        invalid_pdf(source_id, "PDF startxref points to neither xref nor an xref stream")
    position = xref_offset + header.end()
    dictionary, dictionary_end = extract_pdf_dictionary(
        data,
        position,
        startxref_position,
        source_id,
    )
    if not re.search(br"/Type[ \t\r\n\f\x00]+/XRef(?![A-Za-z0-9#])", dictionary):
        invalid_pdf(source_id, "PDF startxref object is not an /XRef stream")
    size = pdf_dictionary_integer(dictionary, b"Size", source_id)
    root_object, _ = pdf_dictionary_reference(dictionary, b"Root", source_id)
    length = pdf_dictionary_integer(dictionary, b"Length", source_id)
    widths_match = re.search(br"/W[ \t\r\n\f\x00]*\[([^]]+)\]", dictionary)
    if widths_match is None:
        invalid_pdf(source_id, "PDF xref stream lacks /W")
    widths = [int(value) for value in re.findall(br"\d+", widths_match.group(1))]
    if len(widths) != 3 or sum(widths) <= 0:
        invalid_pdf(source_id, "PDF xref stream /W must contain three widths")
    index_match = re.search(br"/Index[ \t\r\n\f\x00]*\[([^]]+)\]", dictionary)
    indexes = (
        [int(value) for value in re.findall(br"\d+", index_match.group(1))]
        if index_match is not None
        else [0, size]
    )
    if len(indexes) % 2 or not indexes:
        invalid_pdf(source_id, "PDF xref stream /Index is malformed")
    indexed_objects: list[int] = []
    for first, count in zip(indexes[0::2], indexes[1::2]):
        if count <= 0:
            invalid_pdf(source_id, "PDF xref stream /Index contains an empty range")
        indexed_objects.extend(range(first, first + count))
    if size <= max(indexed_objects):
        invalid_pdf(source_id, "PDF xref stream /Size does not cover /Index")

    position = skip_pdf_whitespace(data, dictionary_end, startxref_position)
    if not data.startswith(b"stream", position):
        invalid_pdf(source_id, "PDF xref stream dictionary has no stream body")
    position += len(b"stream")
    if data[position : position + 2] == b"\r\n":
        position += 2
    elif data[position : position + 1] in {b"\r", b"\n"}:
        position += 1
    else:
        invalid_pdf(source_id, "PDF xref stream keyword has no line ending")
    stream_end = position + length
    if stream_end > startxref_position:
        invalid_pdf(source_id, "PDF xref stream /Length exceeds the file body")
    stream_data = data[position:stream_end]
    tail = skip_pdf_whitespace(data, stream_end, startxref_position)
    if not data.startswith(b"endstream", tail):
        invalid_pdf(source_id, "PDF xref stream length does not end at endstream")
    endstream = tail + len(b"endstream")
    endobj = skip_pdf_whitespace(data, endstream, startxref_position)
    if not data.startswith(b"endobj", endobj):
        invalid_pdf(source_id, "PDF xref stream object has no endobj")

    filter_match = re.search(br"/Filter[ \t\r\n\f\x00]+/([A-Za-z0-9]+)", dictionary)
    if b"/Filter" in dictionary and filter_match is None:
        invalid_pdf(source_id, "PDF xref stream uses an unsupported filter form")
    if filter_match is None:
        decoded = stream_data
    elif filter_match.group(1) == b"FlateDecode":
        try:
            decoded = zlib.decompress(stream_data)
        except zlib.error as error:
            invalid_pdf(source_id, "PDF xref stream Flate data is invalid", error=str(error))
    else:
        invalid_pdf(
            source_id,
            "PDF xref stream filter is unsupported by the strict structural gate",
            filter=filter_match.group(1).decode("ascii", errors="replace"),
        )
    entry_width = sum(widths)
    if len(decoded) != len(indexed_objects) * entry_width:
        invalid_pdf(source_id, "PDF xref stream byte count does not match /W and /Index")
    entries: dict[int, tuple[int, int, int]] = {}
    cursor = 0
    for object_number in indexed_objects:
        fields: list[int] = []
        for width in widths:
            raw = decoded[cursor : cursor + width]
            cursor += width
            fields.append(int.from_bytes(raw, "big") if width else 0)
        entry_type = fields[0] if widths[0] else 1
        if entry_type not in {0, 1, 2}:
            invalid_pdf(source_id, "PDF xref stream contains an unknown entry type")
        entries[object_number] = (entry_type, fields[1], fields[2])
    root_entry = entries.get(root_object)
    if root_entry is None or root_entry[0] not in {1, 2}:
        invalid_pdf(source_id, "PDF xref stream /Root is not an in-use object")
    for object_number, (entry_type, field_two, field_three) in entries.items():
        if entry_type == 1:
            validate_pdf_object_offset(
                data,
                object_number,
                field_three,
                field_two,
                xref_offset,
                source_id,
            )
        elif entry_type == 2:
            object_stream = entries.get(field_two)
            if object_stream is None or object_stream[0] != 1:
                invalid_pdf(source_id, "PDF compressed object references no object stream")


def validate_pdf_structure(path: Path, source_id: str) -> None:
    data = path.read_bytes()
    if PDF_HEADER_PATTERN.match(data) is None:
        invalid_pdf(source_id, "downloaded payload lacks a valid PDF header")
    terminal = PDF_TERMINAL_PATTERN.search(data)
    if terminal is None:
        invalid_pdf(source_id, "downloaded PDF lacks terminal startxref and %%EOF")
    xref_offset = int(terminal.group(1))
    if xref_offset <= 0 or xref_offset >= terminal.start():
        invalid_pdf(source_id, "PDF startxref offset is outside the document body")
    if data.startswith(b"xref", xref_offset):
        validate_classic_pdf_xref(
            data,
            xref_offset,
            terminal.start(),
            source_id,
        )
    else:
        validate_pdf_xref_stream(
            data,
            xref_offset,
            terminal.start(),
            source_id,
        )


def validate_acquisition_operation_receipt(
    row: dict[str, Any],
    acquisition_receipt: dict[str, Any],
    *,
    package: Path,
    executor_skill_sha256: str,
) -> bool:
    source_id = str(row.get("source_id"))
    relative_value = acquisition_receipt.get("executor_operation_receipt_path")
    if row.get("download_attempted") is not True:
        if relative_value is not None:
            fail(
                "unexpected_acquisition_operation",
                "a non-download row cannot claim a Paper Downloader operation",
                source_id=source_id,
            )
        return False
    try:
        relative = relative_posix(
            relative_value,
            "acquisition.executor_operation_receipt_path",
        ).as_posix()
    except ValidationError as error:
        fail(
            "acquisition_operation_missing",
            "download_attempted=true requires a Paper Downloader runtime operation receipt",
            source_id=source_id,
            cause=error.code,
        )
    if not relative.startswith("payload/runtime-receipts/acquisition/"):
        fail(
            "acquisition_operation_binding",
            "Paper Downloader operation receipt must use the acquisition receipt directory",
            source_id=source_id,
        )
    path = package / relative
    if path.is_symlink() or not path.is_file():
        fail(
            "acquisition_operation_missing",
            "downloaded bytes alone do not prove Paper Downloader execution",
            source_id=source_id,
            path=relative,
        )
    path = confined(package, relative, field="Paper Downloader operation receipt")
    operation = load_json(path, "Paper Downloader operation receipt")
    reject_hidden_runtime_evidence(operation, "Paper Downloader operation receipt")
    result = require_object(operation.get("result"), "acquisition-operation.result")
    if (
        operation.get("schema") != ACQUISITION_OPERATION_SCHEMA
        or operation.get("evidence_origin") != "runtime_tool_result"
        or operation.get("executor_name") != PAPER_DOWNLOADER_NAME
        or operation.get("executor_skill_sha256") != executor_skill_sha256
        or operation.get("status") != "completed"
        or operation.get("source_id") != source_id
        or operation.get("publication_identity") != row.get("publication_identity")
        or result.get("access_status") != row.get("access_status")
        or result.get("local_payload_path") != row.get("local_payload_path")
        or result.get("payload_sha256") != row.get("payload_sha256")
        or result.get("payload_bytes") != row.get("payload_bytes")
    ):
        fail(
            "acquisition_operation_binding",
            "Paper Downloader operation receipt does not bind the source result",
            source_id=source_id,
        )
    actual_tool = require_nonempty_string(
        operation.get("actual_tool"),
        "acquisition-operation.actual_tool",
    )
    if (
        any(marker in actual_tool.lower() for marker in FORBIDDEN_RUNTIME_TOOL_MARKERS)
        or tool_leaf(actual_tool) != PAPER_DOWNLOADER_NAME
    ):
        fail(
            "acquisition_operation_binding",
            "acquisition operation did not use Paper Downloader",
            source_id=source_id,
            actual_tool=actual_tool,
        )
    require_runtime_identifier(
        operation.get("operation_id"),
        "acquisition-operation.operation_id",
    )
    started = parsed_time(
        operation.get("started_at"),
        "acquisition-operation.started_at",
    )
    completed = parsed_time(
        operation.get("completed_at"),
        "acquisition-operation.completed_at",
    )
    if completed < started:
        fail(
            "acquisition_operation_order",
            "Paper Downloader operation completed before it started",
            source_id=source_id,
        )
    return True


def validate_acquisition_receipt(
    row: dict[str, Any],
    *,
    index: int,
    package_root: Path,
    package: Path,
    akashic_root: Path,
    executor_skill_sha256: str,
) -> tuple[Path | None, dict[str, Any], bool]:
    source_id = require_nonempty_string(row.get("source_id"), f"source[{index}].source_id")
    receipt_relative = relative_posix(
        row.get("acquisition_receipt_path"),
        f"source[{index}].acquisition_receipt_path",
    ).as_posix()
    receipt_path = package_path(package_root, package, receipt_relative)
    receipt = load_json(receipt_path, receipt_relative)
    if (
        receipt.get("schema_version") != 1
        or "executor_operation_receipt_path" not in receipt
        or receipt.get("source_id") != source_id
        or receipt.get("publication_identity") != row.get("publication_identity")
        or receipt.get("status") != row.get("access_status")
        or receipt.get("download_attempted") is not row.get("download_attempted")
        or receipt.get("local_payload_path") != row.get("local_payload_path")
        or receipt.get("payload_sha256") != row.get("payload_sha256")
        or receipt.get("payload_bytes") != row.get("payload_bytes")
    ):
        fail("acquisition_receipt_binding", "acquisition receipt does not bind its source row", source_id=source_id)
    lookup = require_object(receipt.get("akashic_lookup"), "acquisition.akashic_lookup")
    if lookup.get("performed") is not True or lookup.get("result") not in {"miss", "reused"}:
        fail("akashic_lookup_missing", "every source must be checked against Akashic before download", source_id=source_id)
    lookup_time = parsed_time(lookup.get("checked_at"), "acquisition.akashic_lookup.checked_at")
    attempted = row.get("download_attempted") is True
    if attempted:
        if lookup.get("result") != "miss":
            fail("akashic_redownload", "an Akashic match must never enter a download attempt", source_id=source_id)
        started = parsed_time(receipt.get("download_started_at"), "acquisition.download_started_at")
        completed = parsed_time(receipt.get("download_completed_at"), "acquisition.download_completed_at")
        if not lookup_time <= started <= completed:
            fail("acquisition_event_order", "Akashic lookup must finish before download", source_id=source_id)
    elif receipt.get("download_started_at") is not None or receipt.get("download_completed_at") is not None:
        fail("false_download_timestamps", "non-download receipt cannot contain download timestamps", source_id=source_id)

    operation_verified = validate_acquisition_operation_receipt(
        row,
        receipt,
        package=package,
        executor_skill_sha256=executor_skill_sha256,
    )

    payload_path: Path | None = None
    payload_relative = row.get("local_payload_path")
    if payload_relative not in {None, ""}:
        payload_path = package_path(
            package_root,
            package,
            relative_posix(payload_relative, f"source[{index}].local_payload_path").as_posix(),
        )
        payload_sha = require_hex(row.get("payload_sha256"), f"source[{index}].payload_sha256")
        payload_bytes = row.get("payload_bytes")
        if not isinstance(payload_bytes, int) or payload_bytes <= 0:
            fail("invalid_payload_bytes", "payload_bytes must be positive", source_id=source_id)
        if payload_path.stat().st_size != payload_bytes or sha256_file(payload_path) != payload_sha:
            fail("payload_readback_mismatch", "local payload bytes or SHA-256 do not match disk", source_id=source_id)
    elif row.get("payload_sha256") is not None or row.get("payload_bytes") is not None:
        fail("payload_binding_incomplete", "payload hash and bytes require local_payload_path", source_id=source_id)

    status = row.get("access_status")
    validation = require_object(receipt.get("validation"), "acquisition.validation")
    if status == "downloaded":
        if not attempted or payload_path is None:
            fail("false_download_claim", "downloaded requires a real local payload and download attempt", source_id=source_id)
        if payload_path.stat().st_size <= MIN_PDF_BYTES:
            fail("invalid_downloaded_pdf", "downloaded payload must be larger than 5 KiB", source_id=source_id)
        validate_pdf_structure(payload_path, source_id)
        if validation.get("exists") is not True or validation.get("kind") != "pdf" or validation.get("magic") != "%PDF":
            fail("false_download_claim", "download validation receipt is incomplete", source_id=source_id)
    elif status == "verified_abstract":
        if not attempted or payload_path is None or payload_path.stat().st_size < 80:
            fail("invalid_abstract_payload", "verified abstract requires a retained non-trivial payload", source_id=source_id)
        if validation.get("exists") is not True or validation.get("kind") != "abstract":
            fail("invalid_abstract_payload", "abstract validation receipt is incomplete", source_id=source_id)
    elif status == "akashic_reused":
        if attempted or lookup.get("result") != "reused" or payload_path is None:
            fail("akashic_redownload", "Akashic reuse requires a payload and download_attempted=false", source_id=source_id)
        registry_value = row.get("akashic_registry_path")
        if not isinstance(registry_value, str) or not registry_value:
            fail("akashic_registry_binding", "Akashic reuse requires a registry path", source_id=source_id)
        registry_path = absolute_lexical_path(Path(registry_value), "akashic_registry_path")
        registry_root = (akashic_root / "03-metadata" / "registry").absolute()
        if not within(registry_root, registry_path) or not registry_path.is_file() or registry_path.is_symlink():
            fail("akashic_registry_binding", "registry path is missing or outside Akashic registry", source_id=source_id)
        registry = load_json(registry_path, "Akashic registry record")
        akashic_source_id = require_nonempty_string(lookup.get("source_id"), "acquisition.akashic_lookup.source_id")
        if registry.get("source_id") != akashic_source_id:
            fail("akashic_registry_binding", "registry source_id does not match reuse receipt", source_id=source_id)
        local_source_value = row.get("local_source_path")
        if not isinstance(local_source_value, str) or not local_source_value:
            fail("akashic_source_binding", "Akashic reuse requires local_source_path", source_id=source_id)
        local_source = absolute_lexical_path(Path(local_source_value), "local_source_path")
        if not within(akashic_root.absolute(), local_source) or not local_source.is_file() or local_source.is_symlink():
            fail("akashic_source_binding", "reused source is unavailable or outside Akashic", source_id=source_id)
        registry_relative = registry.get("source_file_path")
        if not isinstance(registry_relative, str) or (akashic_root / registry_relative).absolute() != local_source:
            fail("akashic_source_binding", "registry does not bind the reused source path", source_id=source_id)
        if sha256_file(local_source) != sha256_file(payload_path):
            fail("akashic_source_binding", "materialized payload differs from the Akashic source", source_id=source_id)
        if validation.get("exists") is not True or validation.get("kind") != "akashic_reuse":
            fail("akashic_source_binding", "Akashic reuse validation receipt is incomplete", source_id=source_id)
    parse_time(receipt.get("recorded_at"), "acquisition.recorded_at")
    return payload_path, receipt, operation_verified


def validate_source_row(
    row: dict[str, Any],
    index: int,
    *,
    package_root: Path,
    package: Path,
    akashic_root: Path,
    executor_skill_sha256: str,
) -> tuple[bool, str, str, bool]:
    missing = sorted(REQUIRED_SOURCE_FIELDS - set(row))
    if missing:
        fail("source_fields_missing", "source inventory row is incomplete", line=index, missing=missing)
    source_id = require_nonempty_string(row.get("source_id"), f"source[{index}].source_id")
    require_nonempty_string(row.get("title"), f"source[{index}].title")
    authors = row.get("authors")
    if not (
        isinstance(authors, str)
        and authors.strip()
        or isinstance(authors, list)
        and authors
        and all(isinstance(item, str) and item.strip() for item in authors)
    ):
        fail("invalid_source_authors", "source authors must be non-empty", source_id=source_id)
    if row.get("source_origin") not in {"local", "online"}:
        fail("invalid_source_origin", "source_origin must be local or online", source_id=source_id)
    if row["source_origin"] == "local" and not row.get("local_source_path"):
        fail("missing_source_route", "local source requires local_source_path", source_id=source_id)
    if row["source_origin"] == "online" and not row.get("online_source_url"):
        fail("missing_source_route", "online source requires online_source_url", source_id=source_id)
    if row.get("document_kind") not in ALLOWED_DOCUMENT_KINDS:
        fail("invalid_document_kind", "source is not an eligible scholarly publication", source_id=source_id)
    identity = normalize_publication_identity(row, f"source[{index}]")
    if row.get("publication_identity") != identity:
        fail("publication_identity_mismatch", "publication_identity is not canonical", source_id=source_id, expected=identity)
    if row.get("access_status") not in ALLOWED_ACCESS_STATUSES:
        fail("invalid_access_status", "access_status is not recognized", source_id=source_id)
    if not isinstance(row.get("download_attempted"), bool):
        fail("invalid_download_attempted", "download_attempted must be boolean", source_id=source_id)
    if row.get("evidence_quality") not in {"high", "medium", "low", "unknown"}:
        fail("invalid_akashic_field", "invalid evidence_quality", source_id=source_id)
    if row.get("usage_role") not in {"support", "context", "counterargument", "avoid"}:
        fail("invalid_akashic_field", "invalid usage_role", source_id=source_id)
    if row.get("review_depth") not in {"unreviewed", "screened", "deep_reviewed"}:
        fail("invalid_akashic_field", "invalid review_depth", source_id=source_id)
    if row.get("local_grade") not in {"A", "B", "C", "X", "unknown"}:
        fail("invalid_akashic_field", "invalid local_grade", source_id=source_id)
    for flag_field in ("method_flags", "funding_flags", "diet_flags"):
        flags = row.get(flag_field)
        if not isinstance(flags, list) or not all(isinstance(item, str) for item in flags):
            fail("invalid_akashic_field", f"{flag_field} must be an array of strings", source_id=source_id)
    declared_record_sha = require_hex(row.get("record_sha256"), f"source[{index}].record_sha256")
    if declared_record_sha != sha256_bytes(canonical_without(row, "record_sha256")):
        fail("source_record_hash_mismatch", "source record self-hash mismatch", source_id=source_id)
    _, _, operation_verified = validate_acquisition_receipt(
        row,
        index=index,
        package_root=package_root,
        package=package,
        akashic_root=akashic_root,
        executor_skill_sha256=executor_skill_sha256,
    )
    reviewable = row.get("reviewable") is True
    if reviewable:
        route_verified = bool(
            row.get("original_publication_url")
            or row.get("doi")
            or row.get("pmid")
            or row.get("pmcid")
        )
        if row.get("duplicate_of") not in {None, ""}:
            fail("invalid_reviewable_source", "duplicate cannot be reviewable", source_id=source_id)
        if row.get("on_scope") is not True or row.get("identifier_verified") is not True:
            fail("invalid_reviewable_source", "reviewable source must be on-scope and verified", source_id=source_id)
        if row.get("access_depth") not in {"fulltext", "abstract_only"}:
            fail("invalid_reviewable_source", "reviewable source has insufficient access depth", source_id=source_id)
        if row.get("access_status") not in REVIEWABLE_ACCESS_STATUSES:
            fail("invalid_reviewable_source", "failed or unresolved access status cannot be reviewable", source_id=source_id)
        if row.get("access_status") in {"downloaded", "akashic_reused"} and row.get("access_depth") != "fulltext":
            fail("invalid_reviewable_source", "full-text status requires fulltext access_depth", source_id=source_id)
        if row.get("access_status") == "verified_abstract" and row.get("access_depth") != "abstract_only":
            fail("invalid_reviewable_source", "verified_abstract requires abstract_only access_depth", source_id=source_id)
        if row.get("local_payload_path") in {None, ""}:
            fail("invalid_reviewable_source", "reviewable source requires a retained local payload", source_id=source_id)
        if not route_verified:
            fail("invalid_reviewable_source", "reviewable source lacks a verified publication route", source_id=source_id)
    return reviewable, identity, source_id, operation_verified


def nonempty_string_list(value: Any, field: str) -> list[str]:
    items = require_list(value, field)
    if not items or not all(isinstance(item, str) and item.strip() for item in items):
        fail("invalid_string_list", f"{field} must contain non-empty strings")
    return items


def validate_topic_stage(
    package_root: Path,
    package: Path,
    components: dict[str, dict[str, Any]],
    runtime: dict[str, Any],
) -> dict[str, Any]:
    question_relative = "payload/topic/question.json"
    question_path = package_path(package_root, package, question_relative)
    question = load_json(question_path, "topic question")
    if question.get("schema_version") != 1 or question.get("initiated_by") != "user":
        fail("topic_question_binding", "topic question must be a user-initiated schema v1 record")
    require_nonempty_string(question.get("question"), "topic.question")
    require_nonempty_string(question.get("output_language"), "topic.output_language")
    require_list(question.get("exclusions"), "topic.exclusions")
    parse_time(question.get("locked_at"), "topic.locked_at")

    contributions_root = package_path(
        package_root,
        package,
        "payload/topic/contributions",
        kind="directory",
    )
    expected_names = sorted(f"{component_id}.json" for component_id, _ in EXPERT_COMPONENTS)
    observed_names = sorted(path.name for path in contributions_root.iterdir() if path.is_file())
    if observed_names != expected_names:
        fail("topic_contribution_roster", "topic expansion requires exactly eight manifest experts", observed=observed_names)
    contribution_bindings: list[dict[str, str]] = []
    contexts: list[str] = []
    for component_id, _ in EXPERT_COMPONENTS:
        relative = f"payload/topic/contributions/{component_id}.json"
        path = package_path(package_root, package, relative)
        contribution = load_json(path, relative)
        if contribution.get("schema_version") != 1 or contribution.get("artifact_id") != component_id:
            fail("topic_contribution_binding", "topic contribution identity mismatch", artifact_id=component_id)
        component = components[component_id]
        bundled = require_object(contribution.get("bundled_skill"), "topic.bundled_skill")
        if any(
            bundled.get(key) != expected
            for key, expected in {
                "manifest_component_id": component_id,
                "source_name": component["source_name"],
                "path": component["skill_path"],
                "skill_md_sha256": component["skill_md_sha256"],
                "tree_sha256": component["tree_sha256"],
            }.items()
        ):
            fail("topic_skill_binding", "topic contribution does not bind its manifest Skill", artifact_id=component_id)
        context_id, _ = validate_executor_binding(
            contribution.get("executor"),
            package=package,
            runtime=runtime,
            expected_kind="author",
            role="topic_expert",
            artifact_relative=relative,
            artifact_sha256=sha256_file(path),
            field=f"topic contribution {component_id} executor",
        )
        contexts.append(context_id)
        nonempty_string_list(contribution.get("research_angles"), "topic.research_angles")
        nonempty_string_list(contribution.get("search_terms"), "topic.search_terms")
        require_list(contribution.get("candidate_exclusions"), "topic.candidate_exclusions")
        parse_time(contribution.get("created_at"), "topic.created_at")
        contribution_bindings.append(
            {"artifact_id": component_id, "path": relative, "sha256": sha256_file(path)}
        )
    if len(set(contexts)) != len(EXPERT_COMPONENTS):
        fail("topic_context_reuse", "the eight topic experts require eight distinct contexts")

    brief_relative = "payload/topic/research-brief.json"
    brief_path = package_path(package_root, package, brief_relative)
    brief = load_json(brief_path, "research brief")
    if (
        brief.get("schema_version") != 1
        or brief.get("question_path") != question_relative
        or brief.get("question_sha256") != sha256_file(question_path)
        or brief.get("contributions") != contribution_bindings
    ):
        fail("research_brief_binding", "research brief does not bind the question and all eight contributions")
    brief_context, _ = validate_executor_binding(
        brief.get("executor"),
        package=package,
        runtime=runtime,
        expected_kind="integrator",
        role="topic_integrator",
        artifact_relative=brief_relative,
        artifact_sha256=sha256_file(brief_path),
        field="research brief executor",
    )
    if brief.get("author_context_id") != brief_context:
        fail(
            "research_brief_binding",
            "research brief author_context_id must match its runtime operation receipt",
        )
    if brief_context in contexts:
        fail("research_brief_context_reuse", "research brief author must be separate from topic expert contexts")
    nonempty_string_list(brief.get("search_queries"), "research-brief.search_queries")
    nonempty_string_list(brief.get("inclusion_criteria"), "research-brief.inclusion_criteria")
    nonempty_string_list(brief.get("exclusion_criteria"), "research-brief.exclusion_criteria")
    parse_time(brief.get("frozen_at"), "research-brief.frozen_at")
    return {
        "question_path": question_relative,
        "question_sha256": sha256_file(question_path),
        "brief_path": brief_relative,
        "brief_sha256": sha256_file(brief_path),
        "expert_contexts": contexts,
        "brief_context": brief_context,
    }


def validate_acquisition_summary(
    package_root: Path,
    package: Path,
    rows: list[dict[str, Any]],
    *,
    reviewable_count: int,
    unique_publication_count: int,
    runtime: dict[str, Any],
    acquisition_operation_receipts_structurally_validated: int,
) -> tuple[dict[str, Any], str]:
    relative = "payload/sources/acquisition-summary.json"
    path = package_path(package_root, package, relative)
    summary = load_json(path, "acquisition summary")
    status_counts: dict[str, int] = {}
    for row in rows:
        status = str(row.get("access_status"))
        status_counts[status] = status_counts.get(status, 0) + 1
    if (
        summary.get("schema_version") != 1
        or summary.get("total_source_rows") != len(rows)
        or summary.get("reviewable_source_count") != reviewable_count
        or summary.get("unique_publication_count") != unique_publication_count
        or summary.get("status_counts") != status_counts
        or summary.get("all_akashic_lookups_completed") is not True
        or summary.get("download_payloads_structurally_validated") is not True
        or summary.get("executor_operation_receipts_structurally_validated")
        != acquisition_operation_receipts_structurally_validated
        or summary.get("runtime_execution_verified") is not False
    ):
        fail("acquisition_summary_binding", "acquisition summary does not match the validated source inventory")
    collector_context, _ = validate_executor_binding(
        summary.get("executor"),
        package=package,
        runtime=runtime,
        expected_kind="collector",
        role="source_collector",
        artifact_relative=relative,
        artifact_sha256=sha256_file(path),
        field="acquisition summary executor",
    )
    if summary.get("collector_context_id") != collector_context:
        fail(
            "acquisition_summary_binding",
            "collector_context_id must match the source collection operation receipt",
        )
    parse_time(summary.get("completed_at"), "acquisition-summary.completed_at")
    return summary, sha256_file(path)


def validate_audit(
    audit: dict[str, Any],
    *,
    package: Path,
    audit_relative: str,
    artifact_type: str,
    artifact_id: str,
    attempt: int,
    candidate_sha: str,
    receipt_sha: str,
    runtime: dict[str, Any],
    author_context: str,
    rule_sha: str,
    rule_bytes: int,
) -> tuple[str, str]:
    if audit.get("schema_version") != 1:
        fail("audit_schema", "audit schema_version must be 1", artifact_id=artifact_id, attempt=attempt)
    if audit.get("artifact_type") != artifact_type or audit.get("artifact_id") != artifact_id or audit.get("attempt") != attempt:
        fail("audit_binding_mismatch", "audit identity does not match attempt", artifact_id=artifact_id, attempt=attempt)
    decision = audit.get("decision")
    if decision not in {"pass", "reject"}:
        fail("invalid_audit_decision", "audit decision must be pass or reject", artifact_id=artifact_id, attempt=attempt)
    findings = require_list(audit.get("findings"), "audit.findings")
    required_changes = require_list(audit.get("required_changes"), "audit.required_changes")
    evidence_refs = require_list(audit.get("evidence_refs"), "audit.evidence_refs")
    if decision == "pass" and required_changes:
        fail("invalid_pass_audit", "passing audit cannot require changes", artifact_id=artifact_id, attempt=attempt)
    if decision == "reject" and (not findings or not required_changes):
        fail("invalid_reject_audit", "rejection requires findings and required changes", artifact_id=artifact_id, attempt=attempt)
    if decision == "pass":
        if not evidence_refs:
            fail("invalid_pass_audit", "passing audit requires traceable evidence references", artifact_id=artifact_id, attempt=attempt)
        quality = require_object(audit.get("quality_checks"), "audit.quality_checks")
        required_quality = {
            "nonempty",
            "substantive",
            "citations_traceable",
            "counterevidence_addressed",
            "uncertainty_stated",
            "medical_boundary_observed",
        }
        required_quality.add(
            "source_coverage_complete" if artifact_type == "expert" else "expert_roster_complete"
        )
        failed_checks = sorted(key for key in required_quality if quality.get(key) is not True)
        if failed_checks:
            fail(
                "audit_quality_gate",
                "passing audit has missing or failed quality checks",
                artifact_id=artifact_id,
                attempt=attempt,
                failed=failed_checks,
            )
    audit_path = confined(package, audit_relative, field="audit artifact")
    auditor_context, _ = validate_executor_binding(
        audit.get("auditor"),
        package=package,
        runtime=runtime,
        expected_kind=runtime["auditor_kind"],
        role=f"{artifact_type}_auditor",
        artifact_relative=audit_relative,
        artifact_sha256=sha256_file(audit_path),
        field=f"{artifact_type} audit executor",
    )
    if auditor_context == author_context:
        fail("auditor_not_independent", "author and auditor contexts must differ", artifact_id=artifact_id, attempt=attempt)
    if require_hex(audit.get("input_sha256"), "audit.input_sha256") != receipt_sha:
        fail("audit_input_hash_mismatch", "audit input receipt hash mismatch", artifact_id=artifact_id, attempt=attempt)
    if require_hex(audit.get("artifact_sha256"), "audit.artifact_sha256") != candidate_sha:
        fail("audit_artifact_hash_mismatch", "audit candidate hash mismatch", artifact_id=artifact_id, attempt=attempt)
    validate_rule_binding(
        audit.get("akashic_rule"),
        rule_sha,
        "audit.akashic_rule",
        expected_bytes=rule_bytes,
    )
    parse_time(audit.get("decided_at"), "audit.decided_at")
    return decision, auditor_context


def validate_attempt_chain(
    package: Path,
    lane_dir: Path,
    *,
    artifact_type: str,
    artifact_id: str,
    runtime: dict[str, Any],
    source_set_sha: str,
    frozen_set_sha: str,
    reviewable_source_ids: list[str],
    reviewable_source_ids_sha: str,
    rule_sha: str,
    rule_bytes: int,
    component: dict[str, Any] | None,
    accepted_experts: dict[str, dict[str, Any]] | None = None,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    attempt_numbers = sorted(
        int(match.group(1))
        for path in lane_dir.iterdir()
        if path.is_file() and (match := ATTEMPT_PATTERN.fullmatch(path.name))
    )
    if not attempt_numbers or attempt_numbers != list(range(1, len(attempt_numbers) + 1)):
        fail("attempt_sequence", "attempts must start at 01 and be contiguous", artifact_id=artifact_id, attempts=attempt_numbers)
    if attempt_numbers[-1] > MAX_ATTEMPTS:
        fail("attempt_limit", "attempt number exceeds initial plus three reworks", artifact_id=artifact_id)
    previous_audit_sha: str | None = None
    previous_decision: str | None = None
    audit_records: list[dict[str, Any]] = []
    pass_count = 0
    last_binding: dict[str, Any] | None = None
    for attempt in attempt_numbers:
        prefix = f"attempt-{attempt:02d}"
        candidate_rel = (lane_dir / f"{prefix}.md").relative_to(package).as_posix()
        receipt_rel = (lane_dir / f"{prefix}.receipt.json").relative_to(package).as_posix()
        audit_rel = (lane_dir / f"{prefix}.audit.json").relative_to(package).as_posix()
        candidate_path = package_path(package.parent, package, candidate_rel)
        receipt_path = package_path(package.parent, package, receipt_rel)
        audit_path = package_path(package.parent, package, audit_rel)
        validate_candidate_text(candidate_path, artifact_type, artifact_id)
        candidate_sha = sha256_file(candidate_path)
        receipt = load_json(receipt_path, receipt_rel)
        if receipt.get("schema_version") != 1:
            fail("attempt_schema", "attempt receipt schema_version must be 1", artifact_id=artifact_id, attempt=attempt)
        if receipt.get("artifact_type") != artifact_type or receipt.get("artifact_id") != artifact_id or receipt.get("attempt") != attempt:
            fail("attempt_binding_mismatch", "attempt receipt identity mismatch", artifact_id=artifact_id, attempt=attempt)
        if receipt.get("candidate_path") != candidate_rel:
            fail("attempt_path_mismatch", "candidate_path does not bind the attempt file", artifact_id=artifact_id, attempt=attempt)
        if require_hex(receipt.get("candidate_sha256"), "receipt.candidate_sha256") != candidate_sha:
            fail("candidate_hash_mismatch", "candidate hash mismatch", artifact_id=artifact_id, attempt=attempt)
        if require_hex(receipt.get("source_set_sha256"), "receipt.source_set_sha256") != source_set_sha:
            fail("source_set_hash_mismatch", "attempt uses a different frozen source set", artifact_id=artifact_id, attempt=attempt)
        delivery = require_object(receipt.get("corpus_delivery"), "receipt.corpus_delivery")
        if (
            delivery.get("frozen_set_path") != "payload/sources/frozen-set.json"
            or delivery.get("frozen_set_sha256") != frozen_set_sha
            or delivery.get("source_set_sha256") != source_set_sha
            or delivery.get("reviewable_source_count") != len(reviewable_source_ids)
            or delivery.get("reviewable_source_ids_sha256") != reviewable_source_ids_sha
        ):
            fail("corpus_delivery_binding", "attempt did not bind the complete frozen corpus", artifact_id=artifact_id, attempt=attempt)
        parse_time(delivery.get("delivered_at"), "receipt.corpus_delivery.delivered_at")
        validate_rule_binding(
            receipt.get("akashic_rule"),
            rule_sha,
            "receipt.akashic_rule",
            expected_bytes=rule_bytes,
        )
        author_context, _ = validate_executor_binding(
            receipt.get("executor"),
            package=package,
            runtime=runtime,
            expected_kind="author",
            role=f"{artifact_type}_author",
            artifact_relative=candidate_rel,
            artifact_sha256=candidate_sha,
            field=f"{artifact_type} {artifact_id} attempt {attempt} executor",
        )
        retry_of = receipt.get("retry_of_audit_sha256")
        if attempt == 1:
            if retry_of is not None:
                fail("unexpected_retry_binding", "attempt 01 cannot be a retry", artifact_id=artifact_id)
        else:
            if previous_decision != "reject" or retry_of != previous_audit_sha:
                fail("retry_chain_mismatch", "retry must bind the immediately preceding rejection", artifact_id=artifact_id, attempt=attempt)
        if artifact_type == "expert":
            bundled = require_object(receipt.get("bundled_skill"), "receipt.bundled_skill")
            assert component is not None
            expected_skill_path = component["skill_path"]
            if (
                bundled.get("manifest_component_id") != artifact_id
                or bundled.get("source_name") != component["source_name"]
                or bundled.get("path") != expected_skill_path
                or bundled.get("skill_md_sha256") != component["skill_md_sha256"]
                or bundled.get("tree_sha256") != component["tree_sha256"]
            ):
                fail("bundled_skill_binding_mismatch", "expert receipt does not bind its manifest Skill", artifact_id=artifact_id, attempt=attempt)
            coverage_relative = relative_posix(
                receipt.get("source_coverage_path"),
                "receipt.source_coverage_path",
            ).as_posix()
            coverage_path = package_path(package.parent, package, coverage_relative)
            if require_hex(receipt.get("source_coverage_sha256"), "receipt.source_coverage_sha256") != sha256_file(coverage_path):
                fail("source_coverage_binding", "expert coverage hash mismatch", artifact_id=artifact_id, attempt=attempt)
            coverage = load_json(coverage_path, "expert source coverage")
            if (
                coverage.get("schema_version") != 1
                or coverage.get("artifact_id") != artifact_id
                or coverage.get("attempt") != attempt
                or coverage.get("source_set_sha256") != source_set_sha
                or coverage.get("reviewed_source_ids") != reviewable_source_ids
            ):
                fail("source_coverage_incomplete", "expert did not review the full frozen corpus", artifact_id=artifact_id, attempt=attempt)
            parse_time(coverage.get("completed_at"), "source-coverage.completed_at")
        else:
            inputs = require_list(receipt.get("accepted_expert_inputs"), "receipt.accepted_expert_inputs")
            assert accepted_experts is not None
            if [item.get("artifact_id") if isinstance(item, dict) else None for item in inputs] != [item[0] for item in EXPERT_COMPONENTS]:
                fail("synthesis_input_roster", "synthesis must bind exactly eight accepted experts in manifest order")
            for item in inputs:
                input_record = require_object(item, "accepted_expert_input")
                expected = accepted_experts.get(str(input_record.get("artifact_id")))
                if expected is None or any(
                    input_record.get(key) != expected[key]
                    for key in ("artifact_id", "candidate_path", "candidate_sha256", "audit_path", "audit_sha256")
                ):
                    fail("synthesis_input_binding", "synthesis input does not match an accepted expert", input=input_record.get("artifact_id"))
        parse_time(receipt.get("created_at"), "receipt.created_at")
        receipt_sha = sha256_file(receipt_path)
        audit = load_json(audit_path, audit_rel)
        decision, auditor_context = validate_audit(
            audit,
            package=package,
            audit_relative=audit_rel,
            artifact_type=artifact_type,
            artifact_id=artifact_id,
            attempt=attempt,
            candidate_sha=candidate_sha,
            receipt_sha=receipt_sha,
            runtime=runtime,
            author_context=author_context,
            rule_sha=rule_sha,
            rule_bytes=rule_bytes,
        )
        audit_sha = sha256_file(audit_path)
        if decision == "pass":
            pass_count += 1
            if attempt != attempt_numbers[-1]:
                fail("attempt_after_pass", "no attempt may follow a passing audit", artifact_id=artifact_id, attempt=attempt)
        audit_records.append(
            {
                "attempt": attempt,
                "decision": decision,
                "receipt_path": receipt_rel,
                "receipt_sha256": receipt_sha,
                "audit_path": audit_rel,
                "audit_sha256": audit_sha,
                "author_context": author_context,
                "auditor_context": auditor_context,
            }
        )
        previous_decision = decision
        previous_audit_sha = audit_sha
        last_binding = {
            "artifact_id": artifact_id,
            "attempt": attempt,
            "candidate_path": candidate_rel,
            "candidate_sha256": candidate_sha,
            "audit_path": audit_rel,
            "audit_sha256": audit_sha,
        }
    if pass_count != 1 or previous_decision != "pass" or last_binding is None:
        fail("artifact_not_accepted", "successful run requires one terminal passing attempt", artifact_id=artifact_id)
    accepted_path = package_path(
        package.parent,
        package,
        (lane_dir / "accepted.json").relative_to(package).as_posix(),
    )
    accepted = load_json(accepted_path, "accepted.json")
    if accepted.get("schema_version") != 1 or any(accepted.get(key) != value for key, value in last_binding.items()):
        fail("accepted_binding_mismatch", "accepted.json does not bind the terminal passing attempt", artifact_id=artifact_id)
    return last_binding, audit_records


def validate_events(
    package: Path,
    expert_audits: dict[str, list[dict[str, Any]]],
    synthesis_audits: list[dict[str, Any]],
    required_artifact_bindings: dict[str, str],
) -> str:
    events_path = package_path(package.parent, package, "payload/events.jsonl")
    events, raw_lines = load_jsonl(events_path, "events.jsonl")
    if not events:
        fail("empty_event_chain", "events.jsonl cannot be empty")
    previous_line_sha: str | None = None
    previous_state: Any = None
    event_ids: set[str] = set()
    observed_bindings: set[tuple[str, str | None]] = set()
    observed_types: list[str] = []
    for index, (event, raw_line) in enumerate(zip(events, raw_lines), 1):
        if event.get("sequence") != index:
            fail("event_sequence", "event sequence must be contiguous", line=index)
        event_id = require_nonempty_string(event.get("event_id"), f"events[{index}].event_id")
        if event_id in event_ids:
            fail("duplicate_event_id", "event_id must be unique", event_id=event_id)
        event_ids.add(event_id)
        event_type = require_nonempty_string(event.get("event_type"), f"events[{index}].event_type")
        if event.get("previous_event_sha256") != previous_line_sha:
            fail("event_hash_chain", "previous_event_sha256 mismatch", line=index)
        if event.get("state_from") != previous_state:
            fail("event_state_chain", "state_from does not match previous state_to", line=index)
        previous_state = require_nonempty_string(event.get("state_to"), f"events[{index}].state_to")
        artifact_rel = event.get("artifact_path")
        artifact_sha = event.get("artifact_sha256")
        if artifact_rel is None:
            if artifact_sha is not None:
                fail("event_artifact_binding", "artifact hash requires artifact path", line=index)
        else:
            artifact_rel = relative_posix(artifact_rel, f"events[{index}].artifact_path").as_posix()
            artifact_path = package_path(package.parent, package, artifact_rel)
            if require_hex(artifact_sha, f"events[{index}].artifact_sha256") != sha256_file(artifact_path):
                fail("event_artifact_binding", "event artifact hash mismatch", line=index)
        parse_time(event.get("recorded_at"), f"events[{index}].recorded_at")
        observed_bindings.add((event_type, artifact_rel))
        observed_types.append(event_type)
        previous_line_sha = sha256_bytes(raw_line)
    if events[0].get("event_type") != "run_initialized" or events[0].get("state_from") is not None or events[0].get("state_to") != "initialized":
        fail("event_chain_start", "event chain must begin with run_initialized -> initialized")
    if (
        events[-1].get("event_type") != "structure_validated_runtime_unverified"
        or events[-1].get("state_to") != RUNTIME_NOT_VERIFIED
    ):
        fail(
            "event_chain_terminal",
            "offline event chain must terminate without claiming runtime success",
        )
    if any(event_type in TERMINAL_FAILURE_EVENTS for event_type in observed_types):
        fail("contradictory_success_chain", "success event chain contains a terminal failure")
    for required in (
        "plugin_validated",
        "live_rule_pinned",
        "topic_locked",
        "topic_experts_completed",
        "research_brief_frozen",
        "collection_started",
        "akashic_reuse_checked",
        "collection_completed",
        "material_audit_passed",
        "sources_frozen",
        "experts_8_of_8_passed",
        "synthesis_passed",
        "chain_validated",
        "structure_validated_runtime_unverified",
    ):
        if required not in observed_types:
            fail("event_missing", "required event is absent", event_type=required)
    for event_type, artifact_path in required_artifact_bindings.items():
        if (event_type, artifact_path) not in observed_bindings:
            fail("event_missing", "required event does not bind the expected artifact", event_type=event_type, artifact=artifact_path)

    first_position = {event_type: observed_types.index(event_type) for event_type in set(observed_types)}
    ordered = (
        "run_initialized",
        "plugin_validated",
        "live_rule_pinned",
        "topic_locked",
        "topic_experts_completed",
        "research_brief_frozen",
        "collection_started",
        "akashic_reuse_checked",
        "collection_completed",
        "material_audit_passed",
        "sources_frozen",
        "experts_8_of_8_passed",
        "synthesis_passed",
        "chain_validated",
        "structure_validated_runtime_unverified",
    )
    positions = [first_position[event_type] for event_type in ordered]
    if positions != sorted(positions) or len(set(positions)) != len(positions):
        fail("event_stage_order", "five-stage event order is invalid", order=list(ordered))
    frozen_position = first_position["sources_frozen"]
    expert_terminal_position = first_position["experts_8_of_8_passed"]
    for index, event_type in enumerate(observed_types):
        if event_type.startswith("expert_") and event_type != "experts_8_of_8_passed":
            if index <= frozen_position or index >= expert_terminal_position:
                fail("event_stage_order", "expert events must occur after freeze and before the 8/8 gate", event_type=event_type)
        if event_type.startswith("synthesis_") and index <= expert_terminal_position:
            fail("event_stage_order", "synthesis cannot start before the 8/8 expert gate", event_type=event_type)
    for records in expert_audits.values():
        for position, record in enumerate(records):
            expected_type = "expert_passed" if record["decision"] == "pass" else "expert_attempt_rejected"
            if (expected_type, record["audit_path"]) not in observed_bindings:
                fail("event_missing", "expert audit event is absent", artifact=record["audit_path"])
            if record["decision"] == "reject":
                next_record = records[position + 1]
                if ("expert_retry_dispatched", next_record["receipt_path"]) not in observed_bindings:
                    fail("event_missing", "expert retry event is absent", artifact=next_record["receipt_path"])
    for position, record in enumerate(synthesis_audits):
        expected_type = "synthesis_passed" if record["decision"] == "pass" else "synthesis_attempt_rejected"
        if (expected_type, record["audit_path"]) not in observed_bindings:
            fail("event_missing", "synthesis audit event is absent", artifact=record["audit_path"])
        if record["decision"] == "reject":
            next_record = synthesis_audits[position + 1]
            if ("synthesis_retry_dispatched", next_record["receipt_path"]) not in observed_bindings:
                fail("event_missing", "synthesis retry event is absent", artifact=next_record["receipt_path"])
    assert previous_line_sha is not None
    return previous_line_sha


def validate_run(
    plugin_root_input: Path,
    package_input: Path,
    *,
    submissions_root_input: Path = AKASHIC_SUBMISSIONS_ROOT,
    live_rule_input: Path = LIVE_RULE,
    akashic_root_input: Path = AKASHIC_ROOT,
) -> dict[str, Any]:
    plugin_report = validate_plugin(plugin_root_input)
    plugin_root = Path(plugin_report["plugin_root"])
    source_manifest_path = confined(plugin_root, SOURCE_MANIFEST_RELATIVE, field="bundled source manifest")
    _, components = validate_bundled_manifest(plugin_root, source_manifest_path)
    location = validate_package_location(
        submissions_root_input,
        package_input,
        must_exist=True,
    )
    package_root = Path(location["submissions_root"])
    package = Path(location["package"])
    package_date = location["package_date"]
    package_relative_path = location["package_relative_path"]
    assert_no_symlinks(package)
    reservation = validate_reserved_package(package_root, package, package_relative_path)
    manifest_path = package_path(
        package_root,
        package,
        "payload/receipts/run-manifest.json",
    )
    manifest = load_json(manifest_path, "run manifest")
    if (
        manifest.get("schema_version") != 1
        or manifest.get("package_id") != package.name
        or manifest.get("package_date") != package_date
        or manifest.get("package_relative_path") != package_relative_path
    ):
        fail("run_manifest_identity", "run manifest identity mismatch")
    if manifest.get("status") != STRUCTURAL_RUN_STATUS:
        fail(
            "runtime_success_overclaim",
            "package-local evidence cannot declare candidate or runtime success",
            status=manifest.get("status"),
        )
    expected_runtime_attestation = {
        "evidence_scope": "package_local_only",
        "independent_host_attestation": "not_provided",
        "runtime_execution_verified": False,
        "run_success_verified": False,
    }
    if manifest.get("runtime_attestation") != expected_runtime_attestation:
        fail(
            "runtime_attestation_boundary",
            "run manifest must record that independent host attestation is absent",
        )
    task_id = require_nonempty_string(manifest.get("task_id"), "manifest.task_id")
    runtime = validate_runtime(manifest.get("runtime"))
    topic = validate_topic_stage(package_root, package, components, runtime)
    if manifest.get("research_brief") != {
        "path": topic["brief_path"],
        "sha256": topic["brief_sha256"],
    }:
        fail("research_brief_binding", "run manifest does not bind the frozen research brief")
    plugin_binding = require_object(manifest.get("plugin"), "manifest.plugin")
    if plugin_binding != {"name": PLUGIN_NAME, "version": PLUGIN_VERSION}:
        fail("run_plugin_binding", "run manifest binds the wrong plugin")
    if manifest.get("formal_absorption") != "not_authorized" or manifest.get("plugin_installation") != "not_performed":
        fail("authority_boundary", "run must remain uninstalled and not formally absorbed")
    if manifest.get("fuxi") != "available_not_invoked":
        fail("fuxi_boundary", "Fuxi must be available_not_invoked")
    rule_manifest = require_object(manifest.get("akashic_rule"), "manifest.akashic_rule")
    if rule_manifest.get("path") != str(LIVE_RULE):
        fail("rule_path_mismatch", "run manifest must bind the live Akashic rule")
    rule_sha = require_hex(rule_manifest.get("sha256"), "manifest.akashic_rule.sha256")
    live_rule = live_rule_input.expanduser().absolute()
    if live_rule.is_symlink() or not live_rule.is_file():
        fail("rule_missing", "live Akashic rule is unavailable", path=str(live_rule))
    if str(live_rule) != str(LIVE_RULE):
        # Test injection may supply a fixture, but its receipt still uses the canonical business path.
        actual_rule_sha = sha256_file(live_rule)
    else:
        actual_rule_sha = sha256_file(LIVE_RULE)
    if actual_rule_sha != rule_sha:
        fail("rule_drift", "live Akashic rule hash differs from the run baseline")
    rule_bytes = live_rule.stat().st_size

    run_init_path = package_path(package_root, package, "payload/receipts/run-init.json")
    run_init = load_json(run_init_path, "run-init receipt")
    if (
        run_init.get("schema_version") != 1
        or run_init.get("task_id") != task_id
        or run_init.get("package_id") != package.name
        or run_init.get("package_date") != package_date
        or run_init.get("package_relative_path") != package_relative_path
        or run_init.get("package_path") != str(package)
        or run_init.get("creation_mode") != "akashic_v2_reserved"
        or run_init.get("reservation_path") != reservation["reservation_path"]
        or run_init.get("reservation_sha256") != reservation["reservation_sha256"]
        or run_init.get("akashic_manifest_path") != reservation["manifest_path"]
        or run_init.get("akashic_manifest_sha256") != reservation["manifest_sha256"]
        or run_init.get("runtime") != runtime
    ):
        fail("run_init_binding", "run-init receipt does not match the run manifest")
    parse_time(run_init.get("initialized_at"), "run-init.initialized_at")
    acquisition_executor = validate_acquisition_executor(
        run_init.get("acquisition_executor"),
        plugin_root,
        package,
        runtime,
    )

    plugin_validation = validate_plugin_validation_receipt(
        package,
        plugin_root,
        plugin_report,
    )
    if manifest.get("plugin_validation") != plugin_validation:
        fail(
            "plugin_validation_binding",
            "run manifest does not bind plugin-validation receipt v2",
        )

    live_receipt_path = package_path(package_root, package, "payload/receipts/live-rule.json")
    live_receipt = load_json(live_receipt_path, "live-rule receipt")
    if live_receipt.get("schema_version") != 1:
        fail("rule_receipt_schema", "live-rule receipt schema_version must be 1")
    validate_rule_binding(
        live_receipt,
        rule_sha,
        "live-rule receipt",
        expected_bytes=rule_bytes,
    )

    inventory_path = package_path(package_root, package, "payload/sources/inventory.jsonl")
    source_rows, _ = load_jsonl(inventory_path, "source inventory")
    source_ids: set[str] = set()
    publication_identities: dict[str, str] = {}
    reviewable_source_ids: list[str] = []
    reviewable_count = 0
    acquisition_operation_receipts_structurally_validated = 0
    akashic_root = akashic_root_input.expanduser().absolute()
    for index, row in enumerate(source_rows, 1):
        source_id = str(row.get("source_id"))
        if source_id in source_ids:
            fail("duplicate_source_id", "source_id is duplicated", source_id=source_id)
        source_ids.add(source_id)
        identity = normalize_publication_identity(row, f"source[{index}]")
        canonical_source_id = publication_identities.get(identity)
        if canonical_source_id is not None:
            if row.get("duplicate_of") != canonical_source_id or row.get("reviewable") is True:
                fail(
                    "duplicate_publication_identity",
                    "duplicate DOI/PMID/PMCID/URL cannot count as another publication",
                    source_id=source_id,
                    canonical_source_id=canonical_source_id,
                    publication_identity=identity,
                )
        else:
            publication_identities[identity] = source_id
        reviewable, validated_identity, validated_source_id, operation_verified = validate_source_row(
            row,
            index,
            package_root=package_root,
            package=package,
            akashic_root=akashic_root,
            executor_skill_sha256=acquisition_executor["skill_sha256"],
        )
        if validated_identity != identity or validated_source_id != source_id:
            fail("source_identity_drift", "source identity changed during validation", source_id=source_id)
        reviewable_count += int(reviewable)
        acquisition_operation_receipts_structurally_validated += int(
            operation_verified
        )
        if reviewable:
            reviewable_source_ids.append(source_id)
    if reviewable_count < MIN_REVIEWABLE:
        fail("collection_not_ready", "fewer than 30 publications are reviewable", reviewable=reviewable_count)
    reviewable_source_ids = sorted(reviewable_source_ids)
    reviewable_ids_sha = source_ids_sha256(reviewable_source_ids)
    if manifest.get("reviewable_source_count") != reviewable_count:
        fail("reviewable_count_mismatch", "manifest reviewable count does not match inventory")
    if manifest.get("reviewable_source_ids_sha256") != reviewable_ids_sha:
        fail("reviewable_source_ids_mismatch", "manifest reviewable source roster is stale")
    expected_acquisition_evidence = {
        "source_state": "validated",
        "consumer_link_state": "linked",
        "runtime_discovery_state": RUNTIME_NOT_VERIFIED,
        "discovery_receipt_structurally_validated": True,
        "operation_receipts_structurally_validated": (
            acquisition_operation_receipts_structurally_validated
        ),
        "runtime_execution_verified": False,
    }
    if manifest.get("acquisition_executor_evidence") != expected_acquisition_evidence:
        fail(
            "acquisition_executor_evidence",
            "run manifest must keep source, link, discovery, and execution axes separate",
        )
    package_path(package_root, package, "payload/sources/search-log.md")
    package_path(package_root, package, "payload/sources/access-log.jsonl")
    acquisition_summary, acquisition_summary_sha = validate_acquisition_summary(
        package_root,
        package,
        source_rows,
        reviewable_count=reviewable_count,
        unique_publication_count=len(publication_identities),
        runtime=runtime,
        acquisition_operation_receipts_structurally_validated=(
            acquisition_operation_receipts_structurally_validated
        ),
    )
    sources_root = package_path(package_root, package, "payload/sources", kind="directory")
    frozen_path = package_path(package_root, package, "payload/sources/frozen-set.json")
    frozen = load_json(frozen_path, "frozen source set")
    source_files, _ = inventory_tree(sources_root, exclude_relatives={"frozen-set.json"})
    source_set_sha = tree_sha256(source_files)
    if (
        frozen.get("schema_version") != 1
        or frozen.get("inventory_path") != "payload/sources/inventory.jsonl"
        or frozen.get("inventory_sha256") != sha256_file(inventory_path)
        or frozen.get("tree_hash_algorithm") != TREE_HASH_ALGORITHM
        or frozen.get("source_set_sha256") != source_set_sha
        or frozen.get("reviewable_source_count") != reviewable_count
        or frozen.get("reviewable_source_ids_sha256") != reviewable_ids_sha
        or frozen.get("acquisition_summary_sha256") != acquisition_summary_sha
    ):
        fail("frozen_source_binding", "frozen source-set receipt does not match source files")
    parse_time(frozen.get("frozen_at"), "frozen-set.frozen_at")
    if manifest.get("source_set_sha256") != source_set_sha:
        fail("source_set_hash_mismatch", "manifest source-set hash mismatch")

    material_ref = require_object(manifest.get("material_audit"), "manifest.material_audit")
    if material_ref != {"decision": "pass", "receipt": "payload/receipts/material-audit.json"}:
        fail("material_audit_reference", "run manifest must bind the passing material audit")
    material_path = package_path(package_root, package, material_ref["receipt"])
    material = load_json(material_path, "material audit")
    if (
        material.get("schema_version") != 1
        or material.get("artifact_type") != "materials"
        or material.get("decision") != "pass"
        or material.get("source_set_sha256") != source_set_sha
        or material.get("reviewable_source_count") != reviewable_count
        or material.get("reviewable_source_ids_sha256") != reviewable_ids_sha
        or material.get("acquisition_summary_sha256") != acquisition_summary_sha
    ):
        fail("material_audit_binding", "material audit does not pass the frozen source set")
    material_checks = require_object(material.get("quality_checks"), "material-audit.quality_checks")
    required_material_checks = {
        "akashic_reuse_verified",
        "download_claims_verified",
        "publication_identities_unique",
        "reviewable_threshold_met",
        "corpus_complete",
    }
    failed_material_checks = sorted(
        key for key in required_material_checks if material_checks.get(key) is not True
    )
    if failed_material_checks:
        fail("material_audit_quality_gate", "material audit quality checks did not all pass", failed=failed_material_checks)
    if not require_list(material.get("evidence_refs"), "material-audit.evidence_refs"):
        fail("material_audit_quality_gate", "material audit requires evidence references")
    validate_rule_binding(
        material.get("akashic_rule"),
        rule_sha,
        "material-audit.akashic_rule",
        expected_bytes=rule_bytes,
    )
    material_author_context = require_nonempty_string(material.get("author_context_id"), "material-audit.author_context_id")
    if material_author_context != acquisition_summary.get("collector_context_id"):
        fail("material_audit_binding", "material audit author must be the recorded collector context")
    material_auditor_context, _ = validate_executor_binding(
        material.get("auditor"),
        package=package,
        runtime=runtime,
        expected_kind=runtime["auditor_kind"],
        role="material_auditor",
        artifact_relative=material_ref["receipt"],
        artifact_sha256=sha256_file(material_path),
        field="material audit executor",
    )
    if material_auditor_context == material_author_context:
        fail("auditor_not_independent", "material author and auditor contexts must differ")
    topic_contexts = set(topic["expert_contexts"] + [topic["brief_context"]])
    if material_author_context in topic_contexts or material_auditor_context in topic_contexts:
        fail("stage_context_reuse", "material collection/audit contexts must be separate from topic contexts")
    parse_time(material.get("decided_at"), "material-audit.decided_at")

    experts_root = package_path(package_root, package, "payload/experts", kind="directory")
    observed_expert_dirs = sorted(path.name for path in experts_root.iterdir() if path.is_dir())
    expected_expert_dirs = sorted(item[0] for item in EXPERT_COMPONENTS)
    if observed_expert_dirs != expected_expert_dirs:
        fail("expert_roster_mismatch", "run must contain exactly the eight manifest experts", observed=observed_expert_dirs)
    accepted_experts: dict[str, dict[str, Any]] = {}
    expert_audits: dict[str, list[dict[str, Any]]] = {}
    for component_id, _ in EXPERT_COMPONENTS:
        lane_dir = package_path(package_root, package, f"payload/experts/{component_id}", kind="directory")
        accepted, audits = validate_attempt_chain(
            package,
            lane_dir,
            artifact_type="expert",
            artifact_id=component_id,
            runtime=runtime,
            source_set_sha=source_set_sha,
            frozen_set_sha=sha256_file(frozen_path),
            reviewable_source_ids=reviewable_source_ids,
            reviewable_source_ids_sha=reviewable_ids_sha,
            rule_sha=rule_sha,
            rule_bytes=rule_bytes,
            component=components[component_id],
        )
        accepted_experts[component_id] = accepted
        expert_audits[component_id] = audits
    if manifest.get("experts_passed") != len(accepted_experts):
        fail("expert_pass_count", "manifest must report 8/8 expert passes")
    initial_expert_contexts = [expert_audits[component_id][0]["author_context"] for component_id, _ in EXPERT_COMPONENTS]
    if len(set(initial_expert_contexts)) != len(EXPERT_COMPONENTS):
        fail("expert_context_reuse", "the eight experts require eight distinct initial author contexts")
    if set(initial_expert_contexts) & topic_contexts:
        fail("stage_context_reuse", "expert review contexts must be clean and separate from topic expansion contexts")
    all_expert_author_contexts = {
        record["author_context"] for records in expert_audits.values() for record in records
    }
    all_expert_auditor_contexts = {
        record["auditor_context"] for records in expert_audits.values() for record in records
    }
    reserved_stage_contexts = topic_contexts | {material_author_context, material_auditor_context}
    if all_expert_author_contexts & reserved_stage_contexts:
        fail("stage_context_reuse", "expert author contexts overlap earlier stages")
    if all_expert_auditor_contexts & (reserved_stage_contexts | all_expert_author_contexts):
        fail("auditor_not_independent", "expert auditor context overlaps an author or earlier-stage context")

    synthesis_root = package_path(package_root, package, "payload/synthesis", kind="directory")
    accepted_synthesis, synthesis_audits = validate_attempt_chain(
        package,
        synthesis_root,
        artifact_type="synthesis",
        artifact_id="final-synthesis",
        runtime=runtime,
        source_set_sha=source_set_sha,
        frozen_set_sha=sha256_file(frozen_path),
        reviewable_source_ids=reviewable_source_ids,
        reviewable_source_ids_sha=reviewable_ids_sha,
        rule_sha=rule_sha,
        rule_bytes=rule_bytes,
        component=None,
        accepted_experts=accepted_experts,
    )
    synthesis_author_contexts = {record["author_context"] for record in synthesis_audits}
    synthesis_auditor_contexts = {record["auditor_context"] for record in synthesis_audits}
    occupied_contexts = reserved_stage_contexts | all_expert_author_contexts | all_expert_auditor_contexts
    if synthesis_author_contexts & occupied_contexts:
        fail("stage_context_reuse", "synthesis author context overlaps a prior stage")
    if synthesis_auditor_contexts & (occupied_contexts | synthesis_author_contexts):
        fail("auditor_not_independent", "synthesis auditor context overlaps an author or prior stage")
    synthesis_ref = require_object(manifest.get("synthesis_audit"), "manifest.synthesis_audit")
    if synthesis_ref.get("decision") != "pass" or synthesis_ref.get("accepted_attempt") != accepted_synthesis["attempt"]:
        fail("synthesis_manifest_binding", "manifest does not bind the accepted synthesis")
    submission_path = package_path(package_root, package, "submission.md")
    if sha256_file(submission_path) != accepted_synthesis["candidate_sha256"]:
        fail("submission_binding", "submission.md must be byte-identical to accepted synthesis")

    runtime_operation_receipts_structurally_validated = (
        8
        + 1  # topic integrator
        + 1  # source collector
        + 1  # material auditor
        + 2 * sum(len(records) for records in expert_audits.values())
        + 2 * len(synthesis_audits)
    )
    if (
        manifest.get("runtime_operation_receipts_structurally_validated")
        != runtime_operation_receipts_structurally_validated
    ):
        fail(
            "execution_receipt_count",
            "run manifest does not bind every structurally validated operation receipt",
        )

    event_head_sha = validate_events(
        package,
        expert_audits,
        synthesis_audits,
        {
            "run_initialized": "payload/receipts/run-init.json",
            "plugin_validated": plugin_validation["path"],
            "live_rule_pinned": "payload/receipts/live-rule.json",
            "topic_locked": topic["question_path"],
            "research_brief_frozen": topic["brief_path"],
            "akashic_reuse_checked": "payload/sources/acquisition-summary.json",
            "collection_completed": "payload/sources/acquisition-summary.json",
            "material_audit_passed": material_ref["receipt"],
            "sources_frozen": "payload/sources/frozen-set.json",
        },
    )
    completion_path = package_path(package_root, package, "payload/receipts/completion.json")
    completion = load_json(completion_path, "completion receipt")
    if (
        completion.get("schema_version") != 1
        or completion.get("status") != STRUCTURAL_RUN_STATUS
        or completion.get("reviewable_source_count") != reviewable_count
        or completion.get("reviewable_source_ids_sha256") != reviewable_ids_sha
        or completion.get("topic_experts_completed") != 8
        or completion.get("akashic_lookup_complete") is not True
        or completion.get("download_payloads_structurally_validated") is not True
        or completion.get("acquisition_operation_receipts_structurally_validated")
        != acquisition_operation_receipts_structurally_validated
        or completion.get("experts_passed") != 8
        or completion.get("synthesis_passed") is not True
        or completion.get("runtime_operation_receipts_structurally_validated")
        != runtime_operation_receipts_structurally_validated
        or completion.get("runtime_execution_verified") is not False
        or completion.get("run_success_verified") is not False
        or completion.get("event_chain_head_sha256") != event_head_sha
    ):
        fail(
            "completion_binding",
            "completion receipt does not bind the structural and runtime-unverified axes",
        )
    parse_time(completion.get("completed_at"), "completion.completed_at")
    if manifest.get("receipt_chain_complete") is not True:
        fail("receipt_chain_incomplete", "manifest must declare a complete receipt chain")
    structural_path = package / "payload/validation/structural-result.json"
    if structural_path.exists():
        structural = load_json(confined(package, "payload/validation/structural-result.json"), "structural result")
        if structural.get("ok") is not True:
            fail("stale_structural_result", "recorded structural result is not passing")

    return {
        "ok": False,
        "mode": "run",
        "status": RUNTIME_NOT_VERIFIED,
        "structural_validation_ok": True,
        "runtime_execution_verified": False,
        "run_success_verified": False,
        "runtime_attestation": {
            "required_source": "independent_host",
            "provided": False,
            "verified": False,
            "status": RUNTIME_NOT_VERIFIED,
            "reason": (
                "package-local normalized receipts are structurally valid but are "
                "not independent host attestation"
            ),
        },
        "package": str(package),
        "package_id": package.name,
        "package_date": package_date,
        "package_relative_path": package_relative_path,
        "task_id": task_id,
        "runtime": runtime,
        "acquisition_executor": acquisition_executor,
        "reviewable_source_count": reviewable_count,
        "reviewable_source_ids_sha256": reviewable_ids_sha,
        "topic_experts_completed": 8,
        "akashic_lookup_complete": True,
        "download_payloads_structurally_validated": True,
        "acquisition_operation_receipts_structurally_validated": (
            acquisition_operation_receipts_structurally_validated
        ),
        "material_audit_receipt_structurally_validated": True,
        "expert_pass_receipts_structurally_validated": len(accepted_experts),
        "expert_attempts": {
            component_id: len(expert_audits[component_id]) for component_id, _ in EXPERT_COMPONENTS
        },
        "synthesis_attempts": len(synthesis_audits),
        "synthesis_audit_receipt_structurally_validated": True,
        "runtime_operation_receipts_structurally_validated": (
            runtime_operation_receipts_structurally_validated
        ),
        "rule_path": str(LIVE_RULE),
        "rule_sha256": rule_sha,
        "source_set_sha256": source_set_sha,
        "receipt_chain_structurally_validated": True,
        "formal_absorption": "not_authorized",
        "plugin_installation": "not_performed",
        "fuxi": "available_not_invoked",
    }


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    subparsers = root.add_subparsers(dest="command", required=True)
    plugin_parser = subparsers.add_parser("plugin", help="validate plugin layout and bundled bindings")
    plugin_parser.add_argument("--plugin-root", type=Path, default=DEFAULT_PLUGIN_ROOT)
    destination_parser = subparsers.add_parser(
        "destination",
        help="preflight a new strict calendar package destination without writing",
    )
    destination_parser.add_argument("--package", type=Path, required=True)
    run_parser = subparsers.add_parser(
        "run",
        help="validate a run package structurally; host execution remains unverified",
    )
    run_parser.add_argument("--plugin-root", type=Path, default=DEFAULT_PLUGIN_ROOT)
    run_parser.add_argument("--package", type=Path, required=True)
    return root


def main(argv: Iterable[str] | None = None) -> int:
    args = parser().parse_args(list(argv) if argv is not None else None)
    try:
        if args.command == "plugin":
            report = validate_plugin(args.plugin_root)
        elif args.command == "destination":
            report = validate_new_package_destination(args.package)
        else:
            report = validate_run(args.plugin_root, args.package)
        print(json.dumps(report, ensure_ascii=False, sort_keys=True))
        return 0 if report.get("ok") is True else 3
    except ValidationError as error:
        payload = {
            "ok": False,
            "error": {
                "code": error.code,
                "message": error.message,
                "details": error.details,
            },
        }
        print(json.dumps(payload, ensure_ascii=False, sort_keys=True), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
