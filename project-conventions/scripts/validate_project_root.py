#!/usr/bin/env python3
"""Validate an initialized ordinary Project Root and its local access entry."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import sys
import unicodedata
from pathlib import Path, PurePosixPath


CONTROL_DIRECTORY = ".project-conventions"
PROTOCOL_VERSION = 1
SKILL_NAME_PATTERN = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MANAGED_START = "<!-- project-conventions:access:start -->"
MANAGED_END = "<!-- project-conventions:access:end -->"
FILE_URI_MARKER = "file" + "://"
PERSONAL_PATHS = (
    re.compile(r"/(?:Users|home|Volumes)/[^/<>{}\s]+/"),
    re.compile(r"[A-Za-z]:[\\/]Users[\\/][^\\/<>{}\s]+[\\/]", re.IGNORECASE),
    re.compile(re.escape(FILE_URI_MARKER), re.IGNORECASE),
)
WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{number}" for number in range(1, 10)),
    *(f"LPT{number}" for number in range(1, 10)),
}


class ProjectValidationError(RuntimeError):
    """Raised when a Project Root does not satisfy the initialized contract."""


def path_identity(value: str | Path) -> str:
    return unicodedata.normalize("NFC", os.path.normpath(str(value))).casefold()


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


def safe_relative(value: object, label: str, allow_none: bool = False) -> str | None:
    if value is None and allow_none:
        return None
    if not isinstance(value, str) or not value or "\\" in value:
        raise ProjectValidationError(f"{label} must be a portable relative path")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise ProjectValidationError(f"{label} must be a normalized relative path")
    for part in path.parts:
        stem = part.split(".", 1)[0].upper()
        if (
            any(ord(character) < 32 or character in '<>:"|?*' for character in part)
            or part.endswith((".", " "))
            or stem in WINDOWS_RESERVED_NAMES
        ):
            raise ProjectValidationError(f"{label} is not portable across supported filesystems")
    return path.as_posix()


def require_real_file(root: Path, relative: str) -> Path:
    path = root / relative
    current = root
    for part in PurePosixPath(relative).parts[:-1]:
        current = current / part
        if is_link_or_junction(current) or not current.is_dir():
            raise ProjectValidationError(f"required path has a linked or missing parent: {relative}")
    if is_link_or_junction(path) or not path.is_file():
        raise ProjectValidationError(f"required real file is missing: {relative}")
    return path


def require_real_directory(root: Path, relative: str) -> Path:
    path = root / relative
    current = root
    for part in PurePosixPath(relative).parts:
        current = current / part
        if is_link_or_junction(current) or not current.is_dir():
            raise ProjectValidationError(f"required real directory is missing: {relative}")
    return path


def validate_existing_path_components(root: Path, relative: str | None, label: str) -> None:
    if relative is None:
        return
    current = root
    for part in PurePosixPath(relative).parts:
        current = current / part
        if is_link_or_junction(current):
            raise ProjectValidationError(f"{label} contains a directory link: {relative}")
        if current.exists() and not current.is_dir():
            raise ProjectValidationError(f"{label} contains a non-directory: {relative}")
        if not current.exists():
            break


def find_misplaced_skill_entries(root: Path, expected_entry: str) -> list[str]:
    observed: list[str] = []
    expected_package = PurePosixPath(expected_entry).parent.as_posix()
    for base_name in ("docs", "src"):
        base = root / base_name
        if is_link_or_junction(base) or not base.is_dir():
            continue
        stack = [base]
        while stack:
            current = stack.pop()
            with os.scandir(current) as entries:
                for entry in entries:
                    path = Path(entry.path)
                    relative = path.relative_to(root).as_posix()
                    if entry.name == "SKILL.md" and (
                        entry.is_file(follow_symlinks=False) or is_link_or_junction(path)
                    ):
                        if relative != expected_entry:
                            observed.append(relative)
                    elif is_link_or_junction(path):
                        linked_entry = path / "SKILL.md"
                        if is_link_or_junction(linked_entry) or linked_entry.is_file():
                            observed.append(relative + "/SKILL.md")
                    elif (
                        entry.is_dir(follow_symlinks=False)
                        and not is_link_or_junction(path)
                        and relative != expected_package
                    ):
                        stack.append(path)
    root_entry = root / "SKILL.md"
    if is_link_or_junction(root_entry) or root_entry.is_file():
        observed.append("SKILL.md")
    return sorted(set(observed))


SKILL_PATH_MENTION = re.compile(
    r"(?i)(?<![A-Za-z0-9_.-])((?:(?:src|docs)[/\\][^\s`|<>\"']*[/\\])?SKILL\.md)"
    r"(?![A-Za-z0-9_.-])"
)


def validate_agent_skill_agents_routes(text: str, expected_entry: str) -> None:
    outside = text
    if text.count(MANAGED_START) == 1 and text.count(MANAGED_END) == 1:
        start = text.index(MANAGED_START)
        end = text.index(MANAGED_END, start) + len(MANAGED_END)
        outside = text[:start] + text[end:]
    mentions = {
        match.group(1).replace("\\", "/")
        for match in SKILL_PATH_MENTION.finditer(outside)
    }
    conflicts = sorted(mention for mention in mentions if mention != expected_entry)
    if conflicts:
        raise ProjectValidationError(
            "AGENTS.md has conflicting Agent Skill source routes: " + ", ".join(conflicts)
        )


def validate(target: Path, run_access_check: bool = True) -> dict[str, object]:
    raw_target = target.expanduser().absolute()
    if is_link_or_junction(raw_target) or not raw_target.is_dir():
        raise ProjectValidationError(f"Project Root is missing or linked: {raw_target}")
    root = raw_target.resolve()

    config_path = require_real_file(root, f"{CONTROL_DIRECTORY}/project.json")
    try:
        config = json.loads(config_path.read_text(encoding="utf-8"))
    except (json.JSONDecodeError, UnicodeError) as exc:
        raise ProjectValidationError(f"invalid project.json: {exc}") from exc
    expected_keys = {
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
    if set(config) != expected_keys:
        raise ProjectValidationError("project.json field set is invalid")
    if config["schema_version"] != PROTOCOL_VERSION:
        raise ProjectValidationError("project.json schema_version is unsupported")
    project_type = config["project_type"]
    if project_type not in {"code", "document", "hybrid"}:
        raise ProjectValidationError("project.json project_type is invalid")
    project_profile = config["project_profile"]
    if project_profile not in {"standard", "agent-skill"}:
        raise ProjectValidationError("project.json project_profile is invalid")
    project_role = config["project_role"]
    if project_role not in {"ordinary", "collection-control", "collection-member"}:
        raise ProjectValidationError("project.json project_role is invalid")
    if project_role != "ordinary" and project_profile != "standard":
        raise ProjectValidationError("shared collection roles require the standard profile")
    skill_package = config["skill_package"]
    if project_profile == "agent-skill":
        if (
            project_type != "code"
            or not isinstance(skill_package, str)
            or len(skill_package) > 64
            or not SKILL_NAME_PATTERN.fullmatch(skill_package)
        ):
            raise ProjectValidationError("project.json Agent Skill package is invalid")
    elif skill_package is not None:
        raise ProjectValidationError("standard Project Root cannot name a Skill package")
    repository_root = safe_relative(config["repository_root"], "repository_root", allow_none=True)
    records_dir = safe_relative(config["records_dir"], "records_dir", allow_none=True)
    validate_existing_path_components(root, repository_root, "repository_root")
    coordination_root = config["coordination_root"]
    coordination_id = config["coordination_id"]
    if config["runtime_backend"] not in {
        "project-local",
        "git-common-dir",
        "collection-control",
    }:
        raise ProjectValidationError("project.json runtime_backend is invalid")
    if coordination_id is not None:
        if not isinstance(coordination_id, str) or not re.fullmatch(
            r"[A-Za-z0-9][A-Za-z0-9._-]{0,127}", coordination_id
        ):
            raise ProjectValidationError("coordination_id is invalid")
        stem = coordination_id.split(".", 1)[0].upper()
        if coordination_id.endswith((".", " ")) or stem in WINDOWS_RESERVED_NAMES:
            raise ProjectValidationError("coordination_id is not portable")
    if project_role == "collection-control":
        if (
            config["runtime_backend"] != "project-local"
            or coordination_root is not None
            or coordination_id is None
            or root.name != coordination_id
        ):
            raise ProjectValidationError("collection-control identity or runtime is invalid")
    elif project_role == "collection-member":
        if (
            config["runtime_backend"] != "collection-control"
            or coordination_id is None
            or coordination_root != f"../{coordination_id}"
        ):
            raise ProjectValidationError("shared-member coordination binding is invalid")
        coordination = root / coordination_root
        if is_link_or_junction(coordination) or not coordination.is_dir():
            raise ProjectValidationError("collection coordination Project Root is missing or linked")
        if path_identity(coordination.resolve().parent) != path_identity(root.parent):
            raise ProjectValidationError("collection coordination Project Root is not a sibling")
        coordination = coordination.resolve()
        coordinator_config_path = require_real_file(
            coordination, f"{CONTROL_DIRECTORY}/project.json"
        )
        try:
            coordinator_config = json.loads(coordinator_config_path.read_text(encoding="utf-8"))
        except (json.JSONDecodeError, UnicodeError) as exc:
            raise ProjectValidationError(f"invalid collection coordinator project.json: {exc}") from exc
        if (
            coordinator_config.get("project_role") != "collection-control"
            or coordinator_config.get("runtime_backend") != "project-local"
            or coordinator_config.get("coordination_id") != coordination_id
            or coordinator_config.get("coordination_root") is not None
        ):
            raise ProjectValidationError("collection coordinator authority or identity differs")
        validate(coordination, run_access_check=False)
    elif (
        coordination_root is not None
        or coordination_id is not None
        or config["runtime_backend"] == "collection-control"
    ):
        raise ProjectValidationError(
            "coordination binding is valid only for shared collection profiles"
        )
    required_files = {
        "AGENTS.md",
        "README.md",
        "conversation/00-initialization.md",
        "memory/MEMORY.md",
        f"{CONTROL_DIRECTORY}/.gitignore",
        f"{CONTROL_DIRECTORY}/ACCESS.md",
        f"{CONTROL_DIRECTORY}/project.json",
        f"{CONTROL_DIRECTORY}/project_access.py",
    }
    required_directories = {
        "docs",
        "conversation",
        "memory",
        CONTROL_DIRECTORY,
    }
    if project_type in {"code", "hybrid"}:
        required_directories.update(
            {"src", "docs/specs", "docs/plans", "docs/reviews", "docs/research"}
        )
    if project_profile == "agent-skill":
        required_directories.add(f"src/{skill_package}")
        required_files.add(f"src/{skill_package}/SKILL.md")
    if project_type == "document" or records_dir is not None:
        required_files.add("INDEX.md")
    if records_dir is not None:
        required_directories.add(records_dir)
        required_files.add(f"{records_dir}/INDEX.md")

    for relative in sorted(required_directories):
        require_real_directory(root, relative)
    for relative in sorted(required_files):
        require_real_file(root, relative)

    helper = root / CONTROL_DIRECTORY / "project_access.py"
    helper_digest = hashlib.sha256(helper.read_bytes()).hexdigest()
    if config["helper_sha256"] != helper_digest:
        raise ProjectValidationError("project_access.py digest differs from project.json")

    agents_text = (root / "AGENTS.md").read_text(encoding="utf-8")
    if agents_text.count(MANAGED_START) != 1 or agents_text.count(MANAGED_END) != 1:
        raise ProjectValidationError("AGENTS.md access block is missing or duplicated")
    start = agents_text.index(MANAGED_START)
    end = agents_text.index(MANAGED_END, start) + len(MANAGED_END)
    managed_block = agents_text[start:end]
    agents_block_digest = hashlib.sha256(managed_block.encode("utf-8")).hexdigest()
    if config["agents_block_sha256"] != agents_block_digest:
        raise ProjectValidationError("AGENTS.md managed access block differs from project.json")
    access_readme = root / CONTROL_DIRECTORY / "ACCESS.md"
    if config["access_readme_sha256"] != hashlib.sha256(access_readme.read_bytes()).hexdigest():
        raise ProjectValidationError("ACCESS.md digest differs from project.json")
    if "$project-handoff" in managed_block or "<skills-dir>" in managed_block:
        raise ProjectValidationError("AGENTS.md access block has an external Skill dependency")
    if any(pattern.search(managed_block) for pattern in PERSONAL_PATHS):
        raise ProjectValidationError("AGENTS.md access block contains a machine-specific path")
    if ".project-conventions/project_access.py status" not in managed_block:
        raise ProjectValidationError("AGENTS.md does not route Agents through the local access helper")
    if project_profile == "agent-skill":
        expected_entry = f"src/{skill_package}/SKILL.md"
        if expected_entry not in managed_block or f"src/{skill_package}/" not in agents_text:
            raise ProjectValidationError("AGENTS.md does not identify the Agent Skill package root")
        validate_agent_skill_agents_routes(agents_text, expected_entry)
        observed_misplaced = find_misplaced_skill_entries(root, expected_entry)
        if observed_misplaced:
            raise ProjectValidationError(
                "Agent Skill package entry is misplaced: " + ", ".join(observed_misplaced)
            )
        skill_text = (root / expected_entry).read_text(encoding="utf-8")
        if not skill_text.startswith("---\n") or "\n---\n" not in skill_text[4:]:
            raise ProjectValidationError("Agent Skill entry has no valid YAML frontmatter boundary")
        frontmatter = skill_text[4 : skill_text.index("\n---\n", 4)]
        observed_name = re.search(r"(?m)^name:\s*([a-z0-9]+(?:-[a-z0-9]+)*)\s*$", frontmatter)
        if observed_name is None or observed_name.group(1) != skill_package:
            raise ProjectValidationError("Agent Skill frontmatter name differs from skill_package")

    access_status: dict[str, object] | None = None
    if run_access_check:
        completed = subprocess.run(
            [sys.executable, "-B", str(helper), "status"],
            capture_output=True,
            text=True,
            check=False,
        )
        if completed.returncode != 0:
            raise ProjectValidationError(
                "project access status failed: " + (completed.stderr.strip() or completed.stdout.strip())
            )
        try:
            access_status = json.loads(completed.stdout)
        except json.JSONDecodeError as exc:
            raise ProjectValidationError("project access status did not return JSON") from exc
        if access_status.get("protocol_version") != PROTOCOL_VERSION:
            raise ProjectValidationError("project access status protocol mismatch")

    repository_state = "not-configured"
    if repository_root is not None:
        repository_path = root / repository_root
        if repository_path.exists():
            completed = subprocess.run(
                ["git", "-C", str(repository_path), "rev-parse", "--show-toplevel"],
                capture_output=True,
                text=True,
                check=False,
            )
            if completed.returncode == 0:
                observed_root = Path(completed.stdout.strip()).expanduser().resolve()
                repository_state = (
                    "git-backed"
                    if os.path.normcase(str(observed_root))
                    == os.path.normcase(str(repository_path.resolve()))
                    else "present-inside-other-git-root"
                )
            else:
                repository_state = "present-not-git"
        else:
            repository_state = "missing"

    return {
        "status": "valid",
        "scope": "ordinary-project-root",
        "project_root": str(root),
        "project_type": project_type,
        "project_profile": project_profile,
        "project_role": project_role,
        "repository_root": repository_root,
        "repository_state": repository_state,
        "runtime_backend": config["runtime_backend"],
        "coordination_id": coordination_id,
        "coordination_root": coordination_root,
        "records_dir": records_dir,
        "skill_package": skill_package,
        "skill_package_state": (
            "scaffold"
            if project_profile == "agent-skill"
            and "structurally valid, non-installed scaffold" in skill_text
            else "authored"
            if project_profile == "agent-skill"
            else None
        ),
        "access_status": access_status,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path)
    parser.add_argument("--skip-access-check", action="store_true")
    arguments = parser.parse_args()
    try:
        result = validate(arguments.target, run_access_check=not arguments.skip_access_check)
    except (ProjectValidationError, OSError, UnicodeError) as exc:
        print(str(exc), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
