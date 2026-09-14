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
import unicodedata
from dataclasses import dataclass
from pathlib import Path, PurePosixPath


CONTROL_DIRECTORY = ".project-conventions"
CONFIG_SCHEMA_VERSION = 1
MANAGED_START = "<!-- project-conventions:access:start -->"
MANAGED_END = "<!-- project-conventions:access:end -->"
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
RESERVED_OPTIONAL_PATH_PARTS = {
    ".git",
    CONTROL_DIRECTORY,
    *HARNESS_ENTRIES,
}
PROJECT_NAME = re.compile(r"^[^/\\\x00-\x1f\x7f]{1,160}$")
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


@dataclass(frozen=True)
class FileSnapshot:
    content: bytes
    mode: int
    device: int
    inode: int


@dataclass(frozen=True)
class PathIdentity:
    device: int
    inode: int


@dataclass(frozen=True)
class AppliedFile:
    path: Path
    snapshot: FileSnapshot
    previous: FileSnapshot | None


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
    if value is None or not value or value != value.strip() or "\\" in value:
        raise ProjectInitializationError(f"{label} must be a portable relative path")
    value = unicodedata.normalize("NFC", value)
    path = PurePosixPath(value)
    if (
        path.is_absolute()
        or not path.parts
        or path.as_posix() != value
        or path.as_posix() == "."
        or any(part in {"", ".", ".."} for part in path.parts)
    ):
        raise ProjectInitializationError(f"{label} must be a normalized relative path")
    for part in path.parts:
        stem = part.split(".", 1)[0].upper()
        if (
            any(ord(character) < 32 or character in '<>:"|?*' for character in part)
            or part.endswith((".", " "))
            or stem in WINDOWS_RESERVED_NAMES
        ):
            raise ProjectInitializationError(f"{label} is not portable across supported filesystems")
        if part.casefold() in {entry.casefold() for entry in RESERVED_OPTIONAL_PATH_PARTS}:
            raise ProjectInitializationError(f"{label} enters a reserved project boundary")
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


def render_access_block(project_profile: str, skill_name: str | None, coordination_policy: str = "worktree-first") -> str:
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
    if coordination_policy == "worktree-first":
        return f"""{MANAGED_START}
## Worktree-first collaboration

- Coordination policy: `worktree-first`. Read `.project-conventions/ACCESS.md` for the complete workflow.
- Read-only work needs no admission or runtime writes. Use a fixed revision or recheck changed inputs.
- Code changes use one task-specific branch and linked Git worktree per concurrent writer. Bind the actual repository, base commit, unique branch, and absent destination first. Existing dirty work stays in place; a new worktree starts from committed content only.
- Reports use distinct exact output files or task-owned directories, with no-clobber creation. Different files in one folder may coexist. For existing shared files, use separate worktrees or one agreed integrator; do not overwrite concurrent edits.
- Merge validated commits through one integrator after checking the destination and preserving unrelated work. Shared build outputs, databases and ports require their own isolation. A different chat is not an isolated filesystem.
- Do not run `enter/check/finish/recover` or request claim cleanup for ordinary work. Legacy SQLite claims are historical metadata, not admission authority under this policy. Do not delete the old database or infer that old processes have stopped.
- Record meaningful work in a unique task record; the integrator updates canonical logs and indexes. Do not hold a project-wide claim for records or number allocation.
- A copied directory is not automatically a linked worktree. Verify its Git root/common directory before using Git; preserve existing content and copied runtime metadata.
{skill_rules.rstrip()}
{MANAGED_END}"""
    return f"""{MANAGED_START}
## Mandatory Agent Entry

- This protocol is project-local and applies to Codex, WorkBuddy, Qoder, Trae, and any other cooperating Agent.
- Before substantive work, run `python3 -B .project-conventions/project_access.py status`.
- Response-only inspection uses `enter --mode read-only --actor <label>` and may coexist with every writer. An active writer is not a read denial; use a fixed snapshot or recheck changing inputs before concluding.
- For reports and bounded file edits, use `enter --mode scoped-writer --actor <label> --write-file <relative-file>` or `--write-dir <dedicated-relative-directory>`. Repeat flags for all outputs, caches and required records. Different files in the same directory may coexist; claiming a directory reserves its entire subtree. Never claim the parent merely because the output file is inside it.
- For code implementation, prefer a task-specific branch and linked Git worktree, then `isolated-writer --workspace <path> --write-path <repo-relative-scope>`. Different worktrees may edit the same logical path; one physical worktree has one writer. Reconcile overlap during integration.
- Use the exclusive `writer` only for short maintenance/integration in this physical workspace. It excludes overlapping writers, not readers or disjoint external worktrees. Only actual repository-wide Git/protocol maintenance uses `writer --registry-maintenance`, which excludes all other writers until released; a workspace claim alone does not protect shared refs/config. Reserve shared record files briefly with `scoped-writer`; release the worktree claim before updating canonical records.
- Do not modify anything until `enter` returns `status: entered`. Save its `session_id` and `token`, re-read current disk/Git state, and run `check` before each write batch.
- A blocked Agent writes nothing under the denied claim. Continue permitted reading or request a fresh claim for an independently authorized nonconflicting output; do not wait merely because another Agent is active. Create new reports without overwriting an existing file.
- Finish required in-scope work and records before `finish --session <id> --token <token> --outcome <success|failed|aborted>`. Response-only tasks create no project records; admission metadata still follows this adopted protocol.
- For a bounded foreground command, prefer `run --actor <label> --write-dir <output> -- <command>`; declare every write path and keep child processes in the foreground. It releases on normal completion, command failure and start failure. Do not hold an entire-project writer across a whole conversation.
- Never auto-clear another claim. `recover` requires explicit user authorization, a reason, a dry-run, and then `--apply`.
- This managed block adopts the helper for this Project Root: if it is missing or fails, remain read-only. Absence in another legacy project does not authorize installing governance or block unrelated work by itself. Separate Harness conversations are not separate filesystems.
{skill_rules.rstrip()}
{MANAGED_END}"""


def render_agents(
    project_name: str,
    project_type: str,
    repository_root: str | None,
    project_profile: str,
    skill_name: str | None,
    coordination_policy: str = "worktree-first",
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

{render_access_block(project_profile, skill_name, coordination_policy)}

## Directory Index

| Path | Purpose |
|---|---|
| `README.md` | Human overview |
{index_row}| `docs/` | Formal project documents |
| `conversation/` | Decisions and collaboration history |
| `memory/` | Project-owned continuity |
{src_row}| `.project-conventions/` | Worktree-first collaboration entry; legacy runtime stays local and ignored |
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
- Read the instructions and materials needed for the selected task; reuse complete current readings. Run checks for the changed contract or behavior and preserve required acceptance gates, without unrelated suites or repeated passing checks.
- Record significant decisions and substantive work that adds useful continuity; update indexes only when their represented facts change. Response-only tasks create no project records. Use separate task records and one integrator for canonical logs and sequence numbers.
- Complete the authorized deliverable, inspect it, fix failures caused by the change, and rerun affected checks without per-step approval. Report any unresolved blocker and the actual completion boundary.
{skill_routing}- Do not initialize Git, move material, or publish without task authorization. A temporary task-specific worktree can support authorized code changes; choose its exact repository, base, branch and path before creating it. Initialization itself creates no worktree.
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
| `.project-conventions/ACCESS.md` | Worktree-first collaboration policy and legacy compatibility |
| `docs/` | Formal documents |
| `conversation/` | Decision and collaboration records |
| `memory/` | Project continuity |
{skill_row}
"""


def render_access_readme(coordination_policy: str = "worktree-first") -> str:
    if coordination_policy == "worktree-first":
        return (Path(__file__).resolve().parents[1] / "references" / "worktree-collaboration.md").read_text(encoding="utf-8")
    return """# Project Access — Protocol 2

This directory is project-owned coordination infrastructure, not a Harness directory.

Every cooperating Agent uses the same local helper. Select the smallest scope covering the actual task effects:

| Task | Admission | Concurrency |
|---|---|---|
| Response-only reading | read-only | Coexists with every writer; does not freeze inputs |
| One report or bounded file edits | scoped-writer + --write-file | Different files in one directory can run together |
| A task-owned output subtree | scoped-writer + --write-dir | Reserves the directory and everything below it |
| Code implementation | isolated-writer in a linked worktree | Separate branches/worktrees; same logical filenames allowed |
| Unbounded/shared maintenance or integration | writer | Excludes other writers, not readers |

```bash
python3 -B .project-conventions/project_access.py status
python3 -B .project-conventions/project_access.py enter --mode read-only --actor <label>
python3 -B .project-conventions/project_access.py enter --mode scoped-writer --actor reviewer-a --write-file docs/reviews/a.md
python3 -B .project-conventions/project_access.py enter --mode scoped-writer --actor reviewer-b --write-file docs/reviews/b.md
python3 -B .project-conventions/project_access.py enter --mode scoped-writer --actor researcher --write-dir docs/research/task-c
python3 -B .project-conventions/project_access.py enter --mode isolated-writer --actor <label> --workspace <linked-worktree> --write-path <repo-relative-path>
python3 -B .project-conventions/project_access.py enter --mode writer --actor <maintenance-label>
python3 -B .project-conventions/project_access.py check --session <id> --token <token>
python3 -B .project-conventions/project_access.py finish --session <id> --token <token> --outcome <success|failed|aborted>
```

In the examples, a.md and b.md can be written concurrently. A second claim for a.md, or a directory claim for docs/reviews, conflicts with a.md. Paths are project-relative, literal, normalized and contain no wildcards; use forward slashes, including on Windows. Repeat --write-file and/or --write-dir to cover every output. File claims do not reserve the parent: creating missing parent directories with mkdir(exist_ok=True) is allowed, but renaming/deleting the parent or changing siblings is not. File versus directory is explicit even before the target exists. Case/Unicode aliases are compared conservatively; symlink/junction paths and hard-linked file targets are rejected. Within a claimed directory, do not follow links or mutate reserved Git, protocol or Harness metadata.

Save the returned session_id and token privately. Re-read current state after entering; run check before each write batch and finish afterward. New reports use no-clobber creation (for example Python open(path, 'x')); an existing filename is a conflict, not permission to overwrite. On collision, select a new authorized name and obtain a claim covering it before writing. A denied write claim does not prohibit read-only entry or a fresh nonconflicting claim. A reader becoming an editor obtains a writing claim first; never silently upgrade its reader claim.

Read-only admission does not freeze files. For a consistent review, use a fixed commit/snapshot or compare input hashes before and after and reread changed inputs. The helper coordinates cooperating Harnesses; it is not a filesystem lock and does not intercept writes from Agents that ignore the protocol.

For code, prefer an existing clean linked Git worktree on a task-specific branch. Only one writer uses a physical worktree; different worktrees may change the same logical path and must resolve merge conflicts later. The helper validates but never creates worktrees. An isolated writer may edit/test its declared paths and commit on its admitted branch. Canonical records are updated in their owning Project Root under a short scoped claim after releasing the worktree claim. Git common-state maintenance, fetch, worktree add/remove and final integration use writer. Databases, ports, devices, services and build outputs need actual isolation; a file claim cannot reserve an external service. Use writer for shared effects not covered by a proven independent boundary.

Record significant decisions and substantive work only when they add useful continuity; update indexes only when their represented facts change. Claim exact record files for the short write batch, reread and merge concurrent additions before saving, then release. For allocating conversation/NN-topic.md, briefly claim conversation/ so numbering is unique. Do not hold a record claim throughout research. Response-only tasks create no project records; the helper's own admission/release metadata remains part of this adopted protocol. Reuse existing exact work authorization rather than asking at every check or finish step.

Runtime state is local and ignored by Git. Claims never expire automatically: after a crashed or abandoned Agent, inspect status, obtain explicit user authorization, run recover without --apply, then repeat with --apply, the same reason, and the returned one-time recovery token. This protocol coordinates cooperating processes that share this physical Project Root; it cannot lock independent devices or an Agent that ignores AGENTS.md.
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
    keys = re.findall(r"(?m)^name\s*:", frontmatter)
    observed = re.findall(r"(?m)^name:\s*([^\r\n]*?)\s*$", frontmatter)
    if len(keys) != 1 or len(observed) != 1 or observed[0] != skill_name:
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
    r"(?i)([^\s`|<>\"'()\[\]{}*,;]+SKILL\.md)(?![A-Za-z0-9_.-])"
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

Follow the coordination policy in AGENTS.md and .project-conventions/ACCESS.md. Worktree-first is the default; legacy claims require explicit selection.
"""


def validate_project_root_git_boundary(target: Path) -> None:
    probe = target if target.is_dir() else target.parent
    completed = subprocess.run(
        ["git", "-C", str(probe), "rev-parse", "--show-toplevel"],
        capture_output=True,
        text=True,
        check=False,
    )
    if completed.returncode != 0:
        return
    observed = Path(completed.stdout.strip()).expanduser().resolve()
    if not target.is_dir() or os.path.normcase(str(observed)) != os.path.normcase(
        str(target.resolve())
    ):
        raise ProjectInitializationError(
            "ordinary Project Root must not be nested inside another Git worktree"
        )
    git_dir = subprocess.run(
        ["git", "-C", str(target), "rev-parse", "--git-dir"],
        capture_output=True,
        text=True,
        check=False,
    )
    common_dir = subprocess.run(
        ["git", "-C", str(target), "rev-parse", "--git-common-dir"],
        capture_output=True,
        text=True,
        check=False,
    )
    if git_dir.returncode != 0 or common_dir.returncode != 0:
        raise ProjectInitializationError("Git worktree identity could not be verified")
    git_path = Path(git_dir.stdout.strip())
    common_path = Path(common_dir.stdout.strip())
    if not git_path.is_absolute():
        git_path = target / git_path
    if not common_path.is_absolute():
        common_path = target / common_path
    if os.path.normcase(str(git_path.resolve())) != os.path.normcase(str(common_path.resolve())):
        raise ProjectInitializationError(
            "ordinary initialization must run at the canonical Git worktree, not a linked worktree"
        )


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


def canonical_text(content: bytes) -> bytes:
    return content.replace(b"\r\n", b"\n").replace(b"\r", b"\n")


def preferred_newline(content: bytes) -> bytes:
    crlf_count = content.count(b"\r\n")
    lone_lf_count = content.count(b"\n") - crlf_count
    return b"\r\n" if crlf_count and not lone_lf_count else b"\n"


def managed_agents(existing: bytes, expected_block: str) -> tuple[bytes, str]:
    try:
        existing.decode("utf-8")
    except UnicodeError as exc:
        raise ProjectInitializationError("AGENTS.md is not UTF-8") from exc
    start_marker = MANAGED_START.encode("utf-8")
    end_marker = MANAGED_END.encode("utf-8")
    start_count = existing.count(start_marker)
    end_count = existing.count(end_marker)
    if start_count == 0 and end_count == 0:
        newline = preferred_newline(existing)
        block = expected_block.encode("utf-8").replace(b"\n", newline)
        if not existing:
            separator = b""
        elif existing.endswith(newline * 2):
            separator = b""
        elif existing.endswith(newline):
            separator = newline
        else:
            separator = newline * 2
        return existing + separator + block + newline, "append"
    if start_count != 1 or end_count != 1:
        raise ProjectInitializationError("AGENTS.md has malformed project-conventions access markers")
    start = existing.index(start_marker)
    end = existing.index(end_marker, start) + len(end_marker)
    observed = existing[start:end]
    if canonical_text(observed) != expected_block.encode("utf-8"):
        raise ProjectInitializationError("existing AGENTS.md access block differs; manual merge required")
    return existing, "preserve"


def file_snapshot(path: Path) -> FileSnapshot:
    if is_link_or_junction(path) or not path.is_file():
        raise ProjectInitializationError(f"required real file changed: {path}")
    observed = path.stat(follow_symlinks=False)
    return FileSnapshot(
        content=path.read_bytes(),
        mode=stat.S_IMODE(observed.st_mode),
        device=observed.st_dev,
        inode=observed.st_ino,
    )


def directory_identity(path: Path) -> PathIdentity:
    if is_link_or_junction(path) or not path.is_dir():
        raise ProjectInitializationError(f"required real directory changed: {path}")
    observed = path.stat(follow_symlinks=False)
    return PathIdentity(device=observed.st_dev, inode=observed.st_ino)


def same_file_snapshot(path: Path, expected: FileSnapshot) -> bool:
    try:
        return file_snapshot(path) == expected
    except (OSError, ProjectInitializationError):
        return False


def same_directory(path: Path, expected: PathIdentity) -> bool:
    try:
        return directory_identity(path) == expected
    except (OSError, ProjectInitializationError):
        return False


def create_directory(path: Path) -> PathIdentity:
    path.mkdir()
    try:
        return directory_identity(path)
    except Exception:
        try:
            if not is_link_or_junction(path) and path.is_dir():
                path.rmdir()
        except OSError:
            pass
        raise


def inspect_target(
    target: Path,
    mode: str,
    directories: set[str],
    expected_files: dict[str, bytes],
    managed_block: str,
) -> tuple[
    list[str],
    list[str],
    list[str],
    dict[str, FileSnapshot | None],
    dict[str, PathIdentity | None],
]:
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
    preconditions: dict[str, FileSnapshot | None] = {}
    directory_preconditions: dict[str, PathIdentity | None] = {
        ".": directory_identity(target) if target.exists() else None
    }
    for relative in sorted(directories):
        path = target / relative
        if is_link_or_junction(path) or (path.exists() and not path.is_dir()):
            raise ProjectInitializationError(f"required directory conflicts: {relative}")
        if path.exists():
            preserves.append(relative + "/")
            directory_preconditions[relative] = directory_identity(path)
        else:
            creates.append(relative + "/")
            directory_preconditions[relative] = None

    for relative, expected in sorted(expected_files.items()):
        path = target / relative
        if is_link_or_junction(path) or (path.exists() and not path.is_file()):
            raise ProjectInitializationError(f"required file conflicts: {relative}")
        if not path.exists():
            creates.append(relative)
            preconditions[relative] = None
            continue
        observed = file_snapshot(path)
        preconditions[relative] = observed
        if relative == "AGENTS.md":
            updated, action = managed_agents(observed.content, managed_block)
            expected_files[relative] = updated
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
        elif observed.content == expected:
            preserves.append(relative)
        else:
            raise ProjectInitializationError(f"managed file differs: {relative}")
    return creates, edits, preserves, preconditions, directory_preconditions


def validate_planned_topology(
    directories: set[str], expected_files: dict[str, bytes], optional_directories: set[str]
) -> None:
    file_paths = {PurePosixPath(relative) for relative in expected_files}
    directory_paths = {
        PurePosixPath(relative) for relative in directories | optional_directories
    }
    for directory in directory_paths:
        if directory in file_paths or any(parent in file_paths for parent in directory.parents):
            raise ProjectInitializationError(
                f"planned directory conflicts with a managed file: {directory.as_posix()}"
            )
    for file_path in file_paths:
        if any(parent in file_paths for parent in file_path.parents):
            raise ProjectInitializationError(
                f"planned file has a managed-file parent: {file_path.as_posix()}"
            )


def write_atomic(
    path: Path, content: bytes, expected_existing: FileSnapshot | None
) -> AppliedFile:
    if expected_existing is None:
        descriptor = os.open(path, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o644)
        created = os.fstat(descriptor)
        try:
            with os.fdopen(descriptor, "wb") as handle:
                if hasattr(os, "fchmod"):
                    os.fchmod(handle.fileno(), 0o644)
                handle.write(content)
                handle.flush()
                os.fsync(handle.fileno())
                created_final = os.fstat(handle.fileno())
            if not hasattr(os, "fchmod"):
                os.chmod(path, 0o644)
        except Exception:
            try:
                observed = path.stat(follow_symlinks=False)
                if observed.st_dev == created.st_dev and observed.st_ino == created.st_ino:
                    path.unlink()
            except OSError:
                pass
            raise
        return AppliedFile(
            path=path,
            snapshot=FileSnapshot(
                content=content,
                mode=stat.S_IMODE(created_final.st_mode),
                device=created_final.st_dev,
                inode=created_final.st_ino,
            ),
            previous=None,
        )
    if not same_file_snapshot(path, expected_existing):
        raise ProjectInitializationError(f"file changed after planning: {path}")
    descriptor, temporary_name = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(content)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, expected_existing.mode)
        installed = temporary.stat(follow_symlinks=False)
        if not same_file_snapshot(path, expected_existing):
            raise ProjectInitializationError(f"file changed during apply: {path}")
        os.replace(temporary, path)
    finally:
        if temporary.exists():
            temporary.unlink()
    return AppliedFile(
        path=path,
        snapshot=FileSnapshot(
            content=content,
            mode=expected_existing.mode,
            device=installed.st_dev,
            inode=installed.st_ino,
        ),
        previous=expected_existing,
    )


def restore_file(applied: AppliedFile) -> bool:
    if not same_file_snapshot(applied.path, applied.snapshot):
        return False
    if applied.previous is None:
        applied.path.unlink()
        return True
    descriptor, temporary_name = tempfile.mkstemp(
        prefix=f".{applied.path.name}.rollback.", dir=applied.path.parent
    )
    temporary = Path(temporary_name)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(applied.previous.content)
            handle.flush()
            os.fsync(handle.fileno())
        os.chmod(temporary, applied.previous.mode)
        if same_file_snapshot(applied.path, applied.snapshot):
            os.replace(temporary, applied.path)
            return True
    finally:
        if temporary.exists():
            temporary.unlink()
    return False


def rollback_apply(
    applied_files: list[AppliedFile], created_directories: list[tuple[Path, PathIdentity]]
) -> list[str]:
    unresolved: list[str] = []
    for applied in reversed(applied_files):
        try:
            if not restore_file(applied):
                unresolved.append(str(applied.path))
        except OSError:
            unresolved.append(str(applied.path))
    for path, identity in reversed(created_directories):
        try:
            if same_directory(path, identity):
                path.rmdir()
            elif path.exists() or is_link_or_junction(path):
                unresolved.append(str(path))
        except OSError:
            unresolved.append(str(path))
    return unresolved


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
    coordination_policy: str = "worktree-first",
) -> dict[str, object]:
    if coordination_policy not in {"worktree-first", "legacy-claims"}:
        raise ProjectInitializationError("unsupported coordination policy")
    raw_target = target.expanduser().absolute()
    project_name = project_name or raw_target.name
    if (
        not PROJECT_NAME.fullmatch(project_name)
        or MANAGED_START in project_name
        or MANAGED_END in project_name
    ):
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
    validate_existing_path_components(raw_target, records_dir, "records_dir")
    validate_project_root_git_boundary(raw_target)
    helper_source = Path(__file__).resolve().with_name("project_access.py")
    if is_link_or_junction(helper_source) or not helper_source.is_file():
        raise ProjectInitializationError("packaged project_access.py is missing or linked")
    helper = helper_source.read_bytes()
    helper_digest = portable_text_sha256(helper)
    managed_block = render_access_block(project_profile, skill_name, coordination_policy)
    access_readme = render_access_readme(coordination_policy)
    config = {
        "coordination_policy": coordination_policy,
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
        "schema_version": CONFIG_SCHEMA_VERSION,
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
            project_name, project_type, repository_root, project_profile, skill_name, coordination_policy
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

    optional_directories = {
        relative for relative in (repository_root, records_dir) if relative is not None
    }
    validate_planned_topology(directories, expected_files, optional_directories)

    creates, edits, preserves, preconditions, directory_preconditions = inspect_target(
        raw_target, mode, directories, expected_files, managed_block
    )
    if apply and (creates or edits):
        created_directories: list[tuple[Path, PathIdentity]] = []
        applied_files: list[AppliedFile] = []
        directory_states: dict[str, PathIdentity] = {}
        try:
            planned_root = directory_preconditions["."]
            if planned_root is None:
                identity = create_directory(raw_target)
                directory_states["."] = identity
                created_directories.append((raw_target, identity))
            elif same_directory(raw_target, planned_root):
                directory_states["."] = planned_root
            else:
                raise ProjectInitializationError("target changed after planning")

            for relative in sorted(directories, key=lambda item: (item.count("/"), item)):
                path = raw_target / relative
                parent = PurePosixPath(relative).parent.as_posix()
                parent_key = "." if parent == "." else parent
                parent_identity = directory_states.get(parent_key)
                if parent_identity is None or not same_directory(path.parent, parent_identity):
                    raise ProjectInitializationError(
                        f"directory parent changed after planning: {relative}"
                    )
                planned_directory = directory_preconditions[relative]
                if planned_directory is None:
                    identity = create_directory(path)
                    created_directories.append((path, identity))
                    directory_states[relative] = identity
                elif same_directory(path, planned_directory):
                    directory_states[relative] = planned_directory
                else:
                    raise ProjectInitializationError(
                        f"required directory changed after planning: {relative}"
                    )

            files_to_write = {
                relative for relative in creates + edits if not relative.endswith("/")
            }
            ordered_files = sorted(
                files_to_write,
                key=lambda item: (item == "AGENTS.md", item),
            )
            for relative in ordered_files:
                path = raw_target / relative
                parent = PurePosixPath(relative).parent.as_posix()
                parent_key = "." if parent == "." else parent
                parent_identity = directory_states.get(parent_key)
                if parent_identity is None or not same_directory(path.parent, parent_identity):
                    raise ProjectInitializationError(
                        f"file parent changed after planning: {relative}"
                    )
                applied_files.append(
                    write_atomic(path, expected_files[relative], preconditions[relative])
                )
            # Re-read inside the transaction. A failed readback rolls back this run.
            verified_create, verified_edit, _, _, _ = inspect_target(
                raw_target, "adopt-existing", directories, expected_files, managed_block
            )
            if verified_create or verified_edit:
                raise ProjectInitializationError(
                    "post-write readback failed: " + ", ".join(verified_create + verified_edit)
                )
        except Exception as exc:
            unresolved = rollback_apply(applied_files, created_directories)
            if unresolved:
                raise ProjectInitializationError(
                    f"{exc}; rollback preserved changed or unrecoverable paths: "
                    + ", ".join(sorted(set(unresolved)))
                ) from exc
            raise

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
    parser.add_argument("--coordination-policy", choices=("worktree-first", "legacy-claims"), default="worktree-first")
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
            arguments.coordination_policy,
        )
    except (ProjectInitializationError, OSError, UnicodeError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
