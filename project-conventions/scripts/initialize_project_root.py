#!/usr/bin/env python3
"""Initialize or adopt one ordinary Project Root without moving user content."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import stat
import subprocess
import tempfile
from pathlib import Path, PurePosixPath


CONTROL_DIRECTORY = ".project-conventions"
PROTOCOL_VERSION = 1
MANAGED_START = "<!-- project-conventions:access:start -->"
MANAGED_END = "<!-- project-conventions:access:end -->"
HARNESS_ENTRIES = {
    ".claude",
    ".codex",
    ".minimax",
    ".qoder",
    ".qoderworkcn",
    ".trae",
    ".workbuddy",
}
PROJECT_NAME = re.compile(r"^[^/\\\x00]{1,160}$")
SKILL_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{number}" for number in range(1, 10)),
    *(f"LPT{number}" for number in range(1, 10)),
}


class ProjectInitializationError(RuntimeError):
    """Raised when initialization cannot preserve the target safely."""


def portable_text_sha256(content: bytes) -> str:
    """Hash text after canonicalizing checkout-dependent line endings."""
    normalized = content.replace(b"\r\n", b"\n").replace(b"\r", b"\n")
    return hashlib.sha256(normalized).hexdigest()


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


def safe_relative(value: str | None, label: str, allow_none: bool = True) -> str | None:
    if value is None and allow_none:
        return None
    if value is None or not value or "\\" in value:
        raise ProjectInitializationError(f"{label} must be a portable relative path")
    path = PurePosixPath(value)
    if path.is_absolute() or any(part in {"", ".", ".."} for part in path.parts):
        raise ProjectInitializationError(f"{label} must be a normalized relative path")
    for part in path.parts:
        stem = part.split(".", 1)[0].upper()
        if (
            any(ord(character) < 32 or character in '<>:"|?*' for character in part)
            or part.endswith((".", " "))
            or stem in WINDOWS_RESERVED_NAMES
        ):
            raise ProjectInitializationError(f"{label} is not portable across supported filesystems")
    return path.as_posix()


def validate_existing_path_components(target: Path, relative: str | None, label: str) -> None:
    if relative is None:
        return
    current = target
    for part in PurePosixPath(relative).parts:
        current = current / part
        if is_link_or_junction(current):
            raise ProjectInitializationError(f"{label} contains a directory link: {relative}")
        if current.exists() and not current.is_dir():
            raise ProjectInitializationError(f"{label} contains a non-directory: {relative}")
        if not current.exists():
            break


def render_access_block(project_profile: str, skill_name: str | None) -> str:
    skill_rules = (
        f"""
- This is an Agent Skill Code Project. Its true package root is `src/{skill_name}/`, even when most package files are Markdown or YAML.
- Create and edit the entry only at `src/{skill_name}/SKILL.md`; keep `agents/`, `scripts/`, `references/`, and package assets under the same package root.
- `docs/` is project governance, never the Skill package. `src/SKILL.md` and `docs/{skill_name}/SKILL.md` are invalid placements.
- Agent-specific Skill directories are consumers, not source. Installation/linking is a separate explicitly authorized action and must never move the true package.
"""
        if project_profile == "agent-skill"
        else ""
    )
    return f"""{MANAGED_START}
## Mandatory Agent Entry

- This protocol is project-local and applies to Codex, WorkBuddy, Qoder, Trae, and any other cooperating Agent.
- Before substantive work, run `python3 -B .project-conventions/project_access.py status`.
- Response-only inspection requires `enter --mode read-only --actor <harness-or-task-label>`; any filesystem, Git, cache, database, service, or project-record side effect requires `enter --mode writer --actor <harness-or-task-label>` by default.
- Only a clean linked Git worktree with exact disjoint `--write-path` values may use `isolated-writer`; canonical project records still require the exclusive `writer`.
- Do not modify anything until `enter` returns `status: entered`. Save its `session_id` and `token`, re-read current disk/Git state, and run `check` before each write batch.
- A blocked Agent writes nothing, including `conversation/`, `memory/`, indexes, reviews, or status files. It reports the active claim and stops or waits.
- Finish canonical records before `finish --session <id> --token <token> --outcome <success|failed|aborted>`.
- Never auto-clear another claim. `recover` requires explicit user authorization, a reason, a dry-run, and then `--apply`.
- If this helper is missing or fails, remain read-only. Separate Harness conversations are not separate filesystems.
{skill_rules.rstrip()}
{MANAGED_END}"""


def render_agents(
    project_name: str,
    project_type: str,
    repository_root: str | None,
    project_profile: str,
    skill_name: str | None,
) -> str:
    repository = f"`{repository_root}` (verify with Git before use)" if repository_root else "not configured"
    src_row = "| `src/` | Source and repository entry |\n" if project_type in {"code", "hybrid"} else ""
    index_row = "| `INDEX.md` | Document navigation |\n" if project_type == "document" else ""
    skill_row = (
        f"| `src/{skill_name}/` | Agent Skill package true source |\n"
        if project_profile == "agent-skill"
        else ""
    )
    skill_mapping = (
        f"| Skill Package Root | `src/{skill_name}` |\n"
        "| Agent consumer | separate installation target; never source |\n"
        if project_profile == "agent-skill"
        else ""
    )
    skill_routing = (
        f"- This is an Agent Skill Code Project: its only package entry is `src/{skill_name}/SKILL.md`; every other placement is invalid.\n"
        if project_profile == "agent-skill"
        else ""
    )
    return f"""# AGENTS.md

> Portable Agent entry point for this Project Root.

## Project

{project_name} — {project_type.title()} Project Root.

{render_access_block(project_profile, skill_name)}

## Directory Index

| Path | Purpose |
|---|---|
| `README.md` | Human overview |
{index_row}| `docs/` | Formal project documents |
| `conversation/` | Decisions and collaboration history |
| `memory/` | Project-owned continuity |
{src_row}| `.project-conventions/` | Harness-neutral access protocol; runtime state is local and ignored |
{skill_row}

## Source Mapping

| Field | Value |
|---|---|
| Project Root | `.` |
| Repository Root | {repository} |
{skill_mapping}

## Routing Rules

- Use Project-Root-relative paths in active files; never copy a source machine's absolute path into current routing.
- Preserve existing user material. Generated specs go to `docs/specs/`, research to `docs/research/`, and runnable implementation to `src/` when present.
- Harness-owned hidden directories are opaque and never replace project `conversation/` or `memory/`.
{skill_routing}- Do not initialize Git, move material, publish, or create worktrees unless the user separately authorizes that action.
"""


def render_readme(
    project_name: str, project_type: str, project_profile: str, skill_name: str | None
) -> str:
    skill_row = (
        f"| `src/{skill_name}/` | Agent Skill package true source |\n"
        if project_profile == "agent-skill"
        else ""
    )
    return f"""# {project_name}

This is an initialized {project_type.title()} Project Root.

## Navigation

| Path | Purpose |
|---|---|
| `AGENTS.md` | Mandatory Agent entry and routing rules |
| `.project-conventions/ACCESS.md` | Cross-Harness reader/writer admission protocol |
| `docs/` | Formal documents |
| `conversation/` | Decision and collaboration records |
| `memory/` | Project continuity |
{skill_row}
"""


def render_access_readme() -> str:
    return """# Project Access

This directory is project-owned coordination infrastructure, not a Harness directory.

Every cooperating Agent uses the same local helper before substantive work:

```bash
python3 -B .project-conventions/project_access.py status
python3 -B .project-conventions/project_access.py enter --mode read-only --actor <label>
python3 -B .project-conventions/project_access.py enter --mode writer --actor <label>
python3 -B .project-conventions/project_access.py enter --mode isolated-writer \
  --actor <label> --workspace <linked-worktree> --write-path <repo-relative-path>
python3 -B .project-conventions/project_access.py check --session <id> --token <token>
python3 -B .project-conventions/project_access.py finish \
  --session <id> --token <token> --outcome <success|failed|aborted>
```

Multiple readers may coexist. A writer is exclusive against every reader and writer. `isolated-writer` is only for an existing clean linked Git worktree with exact disjoint paths; it cannot write `.git/`, `.project-conventions/`, `conversation/`, `memory/`, indexes, or other canonical records. It may edit/test declared paths and commit on its admitted branch; fetch, Git config/ref/worktree maintenance, merge, and integration require the exclusive writer. The returned `session_id` and `token` are required by `check` and `finish`. A read-only Agent that becomes a writer must finish its reader claim and enter again as a writer.

Runtime state is local and ignored by Git. Claims never expire automatically: after a crashed or abandoned Agent, inspect `status`, obtain explicit user authorization, run `recover` without `--apply`, then repeat with `--apply`, the same reason, and the returned one-time recovery token. This protocol coordinates cooperating processes that share this physical Project Root; it cannot lock independent devices or an Agent that ignores `AGENTS.md`.
"""


def render_index(project_name: str, records_dir: str | None) -> str:
    records_row = (
        f"| `{records_dir}/` | Versioned submissions and their ledger |\n"
        if records_dir is not None
        else ""
    )
    return f"""# {project_name} Index

| Path | Purpose |
|---|---|
| `docs/` | Current formal documents |
{records_row}| `conversation/` | Decisions and working history |
| `memory/` | Project continuity |
"""


def render_records_index() -> str:
    return """# Versioned Records

No versioned record has been registered yet. Add entries only when an actual submission or version cycle begins.
"""


def render_memory() -> str:
    return """# Project Memory

Project-wide durable facts belong here after substantive work. Harness-private memory does not replace this file.
"""


def render_skill_scaffold(skill_name: str) -> str:
    title = " ".join(part.capitalize() for part in skill_name.split("-"))
    return f"""---
name: {skill_name}
description: "Develop and maintain the {skill_name} Agent Skill package. Use when working on its behavior, references, scripts, tests, or installation preparation."
---

# {title}

This is a structurally valid, non-installed scaffold—not completed Skill behavior. Replace this section with the real workflow before validation, installation, discovery, or execution claims.
"""


def validate_skill_entry_name(path: Path, skill_name: str) -> None:
    if is_link_or_junction(path) or not path.is_file():
        raise ProjectInitializationError(f"Agent Skill entry must be a real file: {path}")
    try:
        text = path.read_text(encoding="utf-8")
    except UnicodeError as exc:
        raise ProjectInitializationError("Agent Skill entry is not UTF-8") from exc
    if not text.startswith("---\n") or "\n---\n" not in text[4:]:
        raise ProjectInitializationError("Agent Skill entry has no valid YAML frontmatter boundary")
    frontmatter = text[4 : text.index("\n---\n", 4)]
    observed = re.search(r"(?m)^name:\s*([a-z0-9]+(?:-[a-z0-9]+)*)\s*$", frontmatter)
    if observed is None or observed.group(1) != skill_name:
        raise ProjectInitializationError("Agent Skill frontmatter name differs from --skill-name")


def find_misplaced_skill_entries(target: Path, expected_relative: str) -> list[str]:
    if not target.is_dir():
        return []
    observed: list[str] = []
    expected_package = PurePosixPath(expected_relative).parent.as_posix()
    for base_name in ("docs", "src"):
        base = target / base_name
        if is_link_or_junction(base) or not base.is_dir():
            continue
        stack = [base]
        while stack:
            current = stack.pop()
            with os.scandir(current) as entries:
                for entry in entries:
                    path = Path(entry.path)
                    relative = path.relative_to(target).as_posix()
                    if entry.name == "SKILL.md" and (
                        entry.is_file(follow_symlinks=False) or is_link_or_junction(path)
                    ):
                        if relative != expected_relative:
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
    root_entry = target / "SKILL.md"
    if is_link_or_junction(root_entry) or root_entry.is_file():
        observed.append("SKILL.md")
    return sorted(set(observed))


SKILL_PATH_MENTION = re.compile(
    r"(?i)(?<![A-Za-z0-9_.-])((?:(?:src|docs)[/\\][^\s`|<>\"']*[/\\])?SKILL\.md)"
    r"(?![A-Za-z0-9_.-])"
)


def validate_agent_skill_agents_routes(text: str, expected_entry: str) -> None:
    """Reject active AGENTS routing that competes with the managed Skill source."""
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
        raise ProjectInitializationError(
            "existing AGENTS.md has conflicting Agent Skill source routes; manual merge required: "
            + ", ".join(conflicts)
        )


def render_initial_conversation(project_type: str, mode: str) -> str:
    return f"""# Project Initialization

## Decision

- Project type: `{project_type}`
- Initialization mode: `{mode}`
- Existing user and Harness content: preserved in place
- Files moved: none
- Git/worktrees/remote actions: none

## Agent entry

All later substantive work uses the project-local `.project-conventions/project_access.py` admission protocol before reading mutable state or writing project files.
"""


def detect_runtime_backend(target: Path, repository_root: str | None) -> str:
    repository = target / repository_root if repository_root is not None else target
    if not repository.is_dir():
        return "project-local"
    completed = subprocess.run(
        ["git", "-C", str(repository), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        return "project-local"
    observed = Path(completed.stdout.strip()).expanduser().resolve()
    return (
        "git-common-dir"
        if os.path.normcase(str(observed)) == os.path.normcase(str(repository.resolve()))
        else "project-local"
    )


def managed_agents(existing: str, expected_block: str) -> tuple[str, str]:
    start_count = existing.count(MANAGED_START)
    end_count = existing.count(MANAGED_END)
    if start_count == 0 and end_count == 0:
        prefix = existing.rstrip()
        return (prefix + "\n\n" + expected_block + "\n" if prefix else expected_block + "\n"), "append"
    if start_count != 1 or end_count != 1:
        raise ProjectInitializationError("AGENTS.md has malformed project-conventions access markers")
    start = existing.index(MANAGED_START)
    end = existing.index(MANAGED_END, start) + len(MANAGED_END)
    observed = existing[start:end]
    if observed != expected_block:
        raise ProjectInitializationError("existing AGENTS.md access block differs; manual merge required")
    return existing, "preserve"


def inspect_target(
    target: Path,
    mode: str,
    directories: set[str],
    expected_files: dict[str, bytes],
    managed_block: str,
) -> tuple[list[str], list[str], list[str], dict[str, bytes | None]]:
    if is_link_or_junction(target):
        raise ProjectInitializationError(f"target must be a real directory: {target}")
    if target.exists() and not target.is_dir():
        raise ProjectInitializationError(f"target is not a directory: {target}")
    if not target.parent.is_dir():
        raise ProjectInitializationError(f"target parent does not exist: {target.parent}")
    if mode == "fresh-empty" and target.exists():
        initialized_marker = target / CONTROL_DIRECTORY / "project.json"
        managed_top_level = (
            {
                PurePosixPath(relative).parts[0]
                for relative in directories | set(expected_files)
            }
            if initialized_marker.is_file() and not is_link_or_junction(initialized_marker)
            else set()
        )
        unexpected = sorted(
            path.name
            for path in target.iterdir()
            if path.name not in HARNESS_ENTRIES | managed_top_level
        )
        if unexpected:
            raise ProjectInitializationError(
                "fresh-empty target contains user entries; use --mode adopt-existing: "
                + ", ".join(unexpected)
            )

    creates: list[str] = []
    edits: list[str] = []
    preserves: list[str] = []
    preconditions: dict[str, bytes | None] = {}
    for relative in sorted(directories):
        path = target / relative
        if is_link_or_junction(path) or (path.exists() and not path.is_dir()):
            raise ProjectInitializationError(f"required directory conflicts: {relative}")
        if path.exists():
            preserves.append(relative + "/")
        else:
            creates.append(relative + "/")

    for relative, expected in sorted(expected_files.items()):
        path = target / relative
        if is_link_or_junction(path) or (path.exists() and not path.is_file()):
            raise ProjectInitializationError(f"required file conflicts: {relative}")
        if not path.exists():
            creates.append(relative)
            preconditions[relative] = None
            continue
        observed = path.read_bytes()
        preconditions[relative] = observed
        if relative == "AGENTS.md":
            try:
                updated, action = managed_agents(observed.decode("utf-8"), managed_block)
            except UnicodeError as exc:
                raise ProjectInitializationError("AGENTS.md is not UTF-8") from exc
            expected_files[relative] = updated.encode("utf-8")
            (edits if action == "append" else preserves).append(relative)
        elif relative in {
            "README.md",
            "INDEX.md",
            "conversation/00-initialization.md",
            "memory/MEMORY.md",
        } or relative.endswith("/INDEX.md") or (
            relative.startswith("src/") and relative.endswith("/SKILL.md")
        ):
            preserves.append(relative)
        elif observed == expected:
            preserves.append(relative)
        else:
            raise ProjectInitializationError(f"managed file differs: {relative}")
    return creates, edits, preserves, preconditions


def write_atomic(path: Path, content: bytes, expected_existing: bytes | None) -> None:
    if expected_existing is None:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        try:
            with os.fdopen(descriptor, "wb") as handle:
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
        except Exception:
            if path.exists():
                path.unlink()
            raise
        return
    if not path.is_file() or path.read_bytes() != expected_existing:
        raise ProjectInitializationError(f"file changed after planning: {path}")
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        if path.read_bytes() != expected_existing:
            raise ProjectInitializationError(f"file changed during apply: {path}")
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()


def initialize(
    target: Path,
    project_type: str,
    mode: str,
    project_name: str | None,
    repository_root: str | None,
    records_dir: str | None,
    project_profile: str,
    skill_name: str | None,
    apply: bool,
) -> dict[str, object]:
    raw_target = target.expanduser().absolute()
    project_name = project_name or raw_target.name
    if not PROJECT_NAME.fullmatch(project_name):
        raise ProjectInitializationError("project name is empty or contains a path separator")
    repository_root = safe_relative(repository_root, "repository_root")
    records_dir = safe_relative(records_dir, "records_dir")
    if project_profile == "agent-skill":
        if project_type != "code":
            raise ProjectInitializationError("agent-skill profile requires --type code")
        if skill_name is None or len(skill_name) > 64 or not SKILL_NAME.fullmatch(skill_name):
            raise ProjectInitializationError(
                "agent-skill profile requires --skill-name in lowercase hyphen-case"
            )
    elif skill_name is not None:
        raise ProjectInitializationError("--skill-name is valid only with --profile agent-skill")
    validate_existing_path_components(raw_target, repository_root, "repository_root")
    helper_source = Path(__file__).resolve().with_name("project_access.py")
    if is_link_or_junction(helper_source) or not helper_source.is_file():
        raise ProjectInitializationError("packaged project_access.py is missing or linked")
    helper = helper_source.read_bytes()
    helper_digest = portable_text_sha256(helper)
    managed_block = render_access_block(project_profile, skill_name)
    access_readme = render_access_readme()
    config = {
        "access_readme_sha256": portable_text_sha256(access_readme.encode("utf-8")),
        "agents_block_sha256": hashlib.sha256(managed_block.encode("utf-8")).hexdigest(),
        "coordination_id": None,
        "coordination_root": None,
        "helper_sha256": helper_digest,
        "project_type": project_type,
        "project_profile": project_profile,
        "project_role": "ordinary",
        "records_dir": records_dir,
        "repository_root": repository_root,
        "runtime_backend": detect_runtime_backend(raw_target, repository_root),
        "schema_version": PROTOCOL_VERSION,
        "skill_package": skill_name,
    }
    directories = {
        CONTROL_DIRECTORY,
        "conversation",
        "docs",
        "memory",
    }
    if project_type in {"code", "hybrid"}:
        directories.update({"src", "docs/specs", "docs/plans", "docs/reviews", "docs/research"})
    else:
        directories.update({"docs/reviews", "docs/research"})
    if project_profile == "agent-skill":
        directories.add(f"src/{skill_name}")
    if records_dir is not None:
        directories.add(records_dir)

    # Optional paths may be nested. Validate and create every parent explicitly so
    # apply cannot partially fail on a missing intermediate directory.
    for relative in tuple(directories):
        for parent in PurePosixPath(relative).parents:
            if parent != PurePosixPath("."):
                directories.add(parent.as_posix())

    expected_files: dict[str, bytes] = {
        "AGENTS.md": render_agents(
            project_name, project_type, repository_root, project_profile, skill_name
        ).encode("utf-8"),
        "README.md": render_readme(
            project_name, project_type, project_profile, skill_name
        ).encode("utf-8"),
        "conversation/00-initialization.md": render_initial_conversation(
            project_type, mode
        ).encode("utf-8"),
        "memory/MEMORY.md": render_memory().encode("utf-8"),
        f"{CONTROL_DIRECTORY}/.gitignore": b"/runtime/\n*.sqlite3\n*.sqlite3-journal\n",
        f"{CONTROL_DIRECTORY}/ACCESS.md": access_readme.encode("utf-8"),
        f"{CONTROL_DIRECTORY}/project.json": (
            json.dumps(config, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        ).encode("utf-8"),
        f"{CONTROL_DIRECTORY}/project_access.py": helper,
    }
    if project_profile == "agent-skill":
        skill_entry = f"src/{skill_name}/SKILL.md"
        misplaced = find_misplaced_skill_entries(raw_target, skill_entry)
        if misplaced:
            raise ProjectInitializationError(
                f"Agent Skill entry must be {skill_entry}; authorize a separate exact migration for: "
                + ", ".join(misplaced)
            )
        existing_skill = raw_target / skill_entry
        if existing_skill.exists() or is_link_or_junction(existing_skill):
            validate_skill_entry_name(existing_skill, skill_name)
        existing_agents = raw_target / "AGENTS.md"
        if existing_agents.is_file() and not is_link_or_junction(existing_agents):
            try:
                validate_agent_skill_agents_routes(
                    existing_agents.read_text(encoding="utf-8"), skill_entry
                )
            except UnicodeError as exc:
                raise ProjectInitializationError("AGENTS.md is not UTF-8") from exc
        expected_files[skill_entry] = render_skill_scaffold(skill_name).encode("utf-8")
    if project_type == "document" or records_dir is not None:
        expected_files["INDEX.md"] = render_index(project_name, records_dir).encode("utf-8")
    if records_dir is not None:
        expected_files[f"{records_dir}/INDEX.md"] = render_records_index().encode("utf-8")

    creates, edits, preserves, preconditions = inspect_target(
        raw_target, mode, directories, expected_files, managed_block
    )
    if apply and (creates or edits):
        raw_target.mkdir(exist_ok=True)
        for relative in sorted(directories, key=lambda item: (item.count("/"), item)):
            (raw_target / relative).mkdir(exist_ok=True)
        files_to_write = {
            relative for relative in creates + edits if not relative.endswith("/")
        }
        ordered_files = sorted(
            files_to_write,
            key=lambda item: (item == "AGENTS.md", item),
        )
        for relative in ordered_files:
            path = raw_target / relative
            expected_existing = preconditions[relative]
            if expected_existing is not None and path.read_bytes() == expected_files[relative]:
                continue
            write_atomic(path, expected_files[relative], expected_existing)
        # Re-read with the same contract. Any remaining create/edit is a failed apply.
        verified_create, verified_edit, _, _ = inspect_target(
            raw_target, "adopt-existing", directories, expected_files, managed_block
        )
        if verified_create or verified_edit:
            raise ProjectInitializationError(
                "post-write readback failed: " + ", ".join(verified_create + verified_edit)
            )

    return {
        "status": (
            "would_initialize"
            if not apply and (creates or edits)
            else "initialized"
            if apply and (creates or edits)
            else "already_initialized"
        ),
        "project_root": str(raw_target.resolve(strict=False)),
        "project_type": project_type,
        "project_profile": project_profile,
        "skill_package": skill_name,
        "skill_package_state": (
            None
            if project_profile != "agent-skill"
            else "would-create-scaffold"
            if not (raw_target / f"src/{skill_name}/SKILL.md").is_file()
            else "scaffold"
            if (raw_target / f"src/{skill_name}/SKILL.md").read_bytes()
            == render_skill_scaffold(str(skill_name)).encode("utf-8")
            else "authored"
        ),
        "mode": mode,
        "would_create": creates if not apply else [],
        "would_edit": edits if not apply else [],
        "created": creates if apply else [],
        "edited": edits if apply else [],
        "preserved": sorted(set(preserves)),
        "moved": [],
        "git_initialized": False,
        "agent_entry": f"{CONTROL_DIRECTORY}/project_access.py",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("target", type=Path)
    parser.add_argument("--type", choices=("code", "document", "hybrid"), required=True)
    parser.add_argument("--mode", choices=("fresh-empty", "adopt-existing"), required=True)
    parser.add_argument("--name")
    parser.add_argument("--repository-root")
    parser.add_argument("--records-dir")
    parser.add_argument("--profile", choices=("standard", "agent-skill"), default="standard")
    parser.add_argument("--skill-name")
    parser.add_argument("--apply", action="store_true")
    arguments = parser.parse_args()
    try:
        result = initialize(
            arguments.target,
            arguments.type,
            arguments.mode,
            arguments.name,
            arguments.repository_root,
            arguments.records_dir,
            arguments.profile,
            arguments.skill_name,
            arguments.apply,
        )
    except (ProjectInitializationError, OSError, UnicodeError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
