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
EXPECTED_CONTROL_GITIGNORE = b"/runtime/\n*.sqlite3\n*.sqlite3-journal\n"
HARNESS_ENTRIES = {
    ".agents",
    ".claude",
    ".codex",
    ".minimax",
    ".qoder",
    ".qoderworkcn",
    ".trae",
    ".workbuddy",
}
RESERVED_OPTIONAL_PATH_PARTS = {".git", CONTROL_DIRECTORY, *HARNESS_ENTRIES}
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


def portable_text_sha256(content: bytes) -> str:
    """Hash text after canonicalizing checkout-dependent line endings."""
    normalized = content.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(normalized).hexdigest()


def path_identity(value: str | Path) -> str:
    return unicodedata.normalize("NFC", os.path.normpath(str(value))).casefold()


def is_link_or_junction(path: Path) -> bool:
    return path.is_symlink() or is_junction(path)


def is_junction(path: Path) -> bool:
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
    return junction


def safe_relative(value: object, label: str, allow_none: bool = False) -> str | None:
    if value is None and allow_none:
        return None
    if not isinstance(value, str) or not value or value != value.strip() or "\\" in value:
        raise ProjectValidationError(f"{label} must be a portable relative path")
    value = unicodedata.normalize("NFC", value)
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or not path.parts
        or path.as_posix() != value
        or path.as_posix() == "."
        or any(part in {"", ".", ".."} for part in path.parts)
    ):
        raise ProjectValidationError(f"{label} must be a normalized relative path")
    for part in path.parts:
        stem = part.split(".", 1)[0].upper()
        if (
            any(ord(character) < 32 or character in '<>:"|?*' for character in part)
            or part.endswith((".", " "))
            or stem in WINDOWS_RESERVED_NAMES
        ):
            raise ProjectValidationError(f"{label} is not portable across supported filesystems")
        if part.casefold() in {entry.casefold() for entry in RESERVED_OPTIONAL_PATH_PARTS}:
            raise ProjectValidationError(f"{label} enters a reserved project boundary")
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
    r"(?i)([^\s`|<>\"'()\[\]{}*,;]+SKILL\.md)(?![A-Za-z0-9_.-])"
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


def validate_planned_topology(
    directories: set[str], files: set[str], optional_directories: set[str]
) -> None:
    file_paths = {PurePosixPath(relative) for relative in files}
    directory_paths = {
        PurePosixPath(relative) for relative in directories | optional_directories
    }
    for directory in directory_paths:
        if directory in file_paths or any(parent in file_paths for parent in directory.parents):
            raise ProjectValidationError(
                f"configured directory conflicts with a managed file: {directory.as_posix()}"
            )
    for file_path in file_paths:
        if any(parent in file_paths for parent in file_path.parents):
            raise ProjectValidationError(
                f"configured file has a managed-file parent: {file_path.as_posix()}"
            )


def exact_git_root(repository: Path) -> None:
    if is_link_or_junction(repository) or not repository.is_dir():
        raise ProjectValidationError("shared Repository Root is missing or linked")
    completed = subprocess.run(
        ["git", "-C", str(repository), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        raise ProjectValidationError("shared Repository Root is not a verified Git worktree")
    observed = Path(completed.stdout.strip()).expanduser().resolve()
    if path_identity(observed) != path_identity(repository.resolve()):
        raise ProjectValidationError("shared Repository Root is not the exact Git worktree root")


def validate_ordinary_git_boundary(root: Path) -> None:
    completed = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        return
    observed = Path(completed.stdout.strip()).expanduser().resolve()
    if path_identity(observed) != path_identity(root):
        raise ProjectValidationError(
            "ordinary Project Root is nested inside another Git worktree"
        )
    git_dir = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--git-dir"],
        capture_output=True,
        text=True,
        check=False,
    )
    common_dir = subprocess.run(
        ["git", "-C", str(root), "rev-parse", "--git-common-dir"],
        capture_output=True,
        text=True,
        check=False,
    )
    if git_dir.returncode != 0 or common_dir.returncode != 0:
        raise ProjectValidationError("ordinary Git worktree identity could not be verified")
    git_path = Path(git_dir.stdout.strip())
    common_path = Path(common_dir.stdout.strip())
    if not git_path.is_absolute():
        git_path = root / git_path
    if not common_path.is_absolute():
        common_path = root / common_path
    if path_identity(git_path.resolve()) != path_identity(common_path.resolve()):
        raise ProjectValidationError(
            "linked Git worktree is an execution workspace, not an ordinary Project Root"
        )


def validate_projection(projection: Path, target: Path, directory: bool) -> None:
    if not target.exists() or is_link_or_junction(target):
        raise ProjectValidationError(f"projection target is missing or linked: {target}")
    if directory and not target.is_dir():
        raise ProjectValidationError(f"projection target is not a directory: {target}")
    if not directory and not target.is_file():
        raise ProjectValidationError(f"projection target is not a file: {target}")
    if os.name == "nt":
        junction = is_junction(projection)
        if directory:
            if not junction or projection.is_symlink():
                raise ProjectValidationError(f"directory projection is not a Windows junction: {projection}")
        elif junction or not projection.is_symlink():
            raise ProjectValidationError(f"file projection is not a Windows symbolic link: {projection}")
    else:
        if not projection.is_symlink():
            raise ProjectValidationError(f"projection is not a Unix symbolic link: {projection}")
        raw = os.readlink(projection)
        expected_raw = Path(os.path.relpath(target, projection.parent)).as_posix()
        if os.path.isabs(raw) or raw.replace("\\", "/") != expected_raw:
            raise ProjectValidationError(f"projection does not use the exact relative target: {projection}")
    try:
        observed = projection.resolve(strict=True)
    except OSError as exc:
        raise ProjectValidationError(f"projection is dangling: {projection}") from exc
    if path_identity(observed) != path_identity(target.resolve()):
        raise ProjectValidationError(f"projection target differs: {projection}")


def validate_collection_control_shape(root: Path) -> None:
    members = require_real_file(root, "docs/indexes/members.md")
    if not members.read_bytes():
        raise ProjectValidationError("collection-control members index is empty")
    source = require_real_directory(root, "src")
    expected_entries = {"AGENTS.md", "README.md", "config", "scripts"}
    observed_entries = {entry.name for entry in source.iterdir()}
    if observed_entries != expected_entries:
        raise ProjectValidationError("collection-control src must contain exactly four projections")
    repository_roots: set[str] = set()
    resolved_repository: Path | None = None
    for name in sorted(expected_entries):
        projection = source / name
        try:
            resolved = projection.resolve(strict=True)
        except OSError as exc:
            raise ProjectValidationError(f"collection-control projection is dangling: {name}") from exc
        repository = resolved.parent
        if (
            path_identity(repository.parent.resolve()) != path_identity(root.parent.resolve())
            or path_identity(repository.resolve()) == path_identity(root.resolve())
        ):
            raise ProjectValidationError("collection-control projections do not target one real sibling")
        validate_projection(projection, repository / name, directory=name in {"config", "scripts"})
        repository_roots.add(path_identity(repository.resolve()))
        resolved_repository = repository
    if len(repository_roots) != 1 or resolved_repository is None:
        raise ProjectValidationError("collection-control projections do not share one Repository Root")
    exact_git_root(resolved_repository)


def validate_collection_member_shape(root: Path) -> None:
    source_root = require_real_directory(root, "src")
    if {entry.name for entry in source_root.iterdir()} != {root.name}:
        raise ProjectValidationError("collection-member src must contain only its package projection")
    projection = source_root / root.name
    if not (projection.exists() or is_link_or_junction(projection)):
        raise ProjectValidationError("collection-member package projection is missing")
    try:
        package = projection.resolve(strict=True)
    except OSError as exc:
        raise ProjectValidationError("collection-member package projection is dangling") from exc
    repository = package.parent
    if (
        package.name != root.name
        or path_identity(repository.parent.resolve()) != path_identity(root.parent.resolve())
    ):
        raise ProjectValidationError("collection-member projection does not target a same-name sibling package")
    validate_projection(projection, repository / root.name, directory=True)
    exact_git_root(repository)
    require_real_file(package, "SKILL.md")


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
    validate_existing_path_components(root, records_dir, "records_dir")
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
    if project_role == "ordinary":
        validate_ordinary_git_boundary(root)
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
    else:
        required_directories.update({"docs/reviews", "docs/research"})
    if project_profile == "agent-skill":
        required_directories.add(f"src/{skill_package}")
        required_files.add(f"src/{skill_package}/SKILL.md")
    if project_type == "document" or records_dir is not None:
        required_files.add("INDEX.md")
    if records_dir is not None:
        required_directories.add(records_dir)
        required_files.add(f"{records_dir}/INDEX.md")

    validate_planned_topology(
        required_directories,
        required_files,
        {
            relative
            for relative in (repository_root, records_dir)
            if relative is not None
        },
    )

    for relative in sorted(required_directories):
        require_real_directory(root, relative)
    for relative in sorted(required_files):
        require_real_file(root, relative)

    helper = root / CONTROL_DIRECTORY / "project_access.py"
    helper_digest = portable_text_sha256(helper.read_bytes())
    if config["helper_sha256"] != helper_digest:
        raise ProjectValidationError("project_access.py digest differs from project.json")
    control_gitignore = root / CONTROL_DIRECTORY / ".gitignore"
    if portable_text_sha256(control_gitignore.read_bytes()) != portable_text_sha256(
        EXPECTED_CONTROL_GITIGNORE
    ):
        raise ProjectValidationError(".project-conventions/.gitignore differs from the managed contract")

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
    if config["access_readme_sha256"] != portable_text_sha256(access_readme.read_bytes()):
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
        name_keys = re.findall(r"(?m)^name\s*:", frontmatter)
        observed_names = re.findall(r"(?m)^name:\s*([^\r\n]*?)\s*$", frontmatter)
        if len(name_keys) != 1 or len(observed_names) != 1 or observed_names[0] != skill_package:
            raise ProjectValidationError("Agent Skill frontmatter name differs from skill_package")

    if project_role == "collection-control":
        validate_collection_control_shape(root)
    elif project_role == "collection-member":
        validate_collection_member_shape(root)

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
