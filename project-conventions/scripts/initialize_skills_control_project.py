#!/usr/bin/env python3
"""Initialize one fresh Skills Project Collection from a shared Git checkout.

The caller clones the distribution repository to <collection>/GitHub first.
This script validates that exact checkout, then creates the collection routing
overlay, the complete collection-control project, and a stable member wrapper
whose Skill source projects to GitHub/project-conventions.

Dry-run is the default. The script never clones, fetches, updates a repository,
creates Agent consumer links, or rewrites an existing non-deterministic tree.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
TEMPLATE_ROOT = PACKAGE_ROOT / "assets" / "skills-control"
SAFE_NAME = re.compile(r"^[A-Za-z0-9][A-Za-z0-9._-]*$")
REMOTE_IDENTITY = re.compile(r"^[A-Za-z0-9_.-]+/[A-Za-z0-9_.-]+$")
PUBLIC_ROOT_FILES = (
    ".gitattributes",
    ".github/workflows/verify.yml",
    ".gitignore",
    "AGENTS.md",
    "README.md",
    "config/agent-paths.tsv",
    "config/skill-exports.tsv",
    "scripts/link-macos.sh",
    "scripts/link-windows.ps1",
    "scripts/verify_release.py",
)
PUBLIC_ROOT_DIRECTORIES = (".github", ".github/workflows", "config", "scripts")
WINDOWS_RESERVED_NAMES = {
    "CON",
    "PRN",
    "AUX",
    "NUL",
    *(f"COM{number}" for number in range(1, 10)),
    *(f"LPT{number}" for number in range(1, 10)),
}
TEMPLATE_FILES = (
    "src/scripts/build_public_root_overlay.py",
    "src/scripts/link-macos.sh",
    "src/scripts/link-windows.ps1",
    "src/tests/test_public_root_overlay.py",
)
CONTROL_DIRECTORIES = (
    ".project-conventions",
    "conversation",
    "docs/decisions",
    "docs/indexes",
    "docs/migrations",
    "docs/plans",
    "docs/research",
    "docs/reviews",
    "docs/specs",
    "memory",
    "release",
    "runtime",
    "src/config",
    "src/scripts",
    "src/tests",
)
MEMBER_DIRECTORIES = (
    ".project-conventions",
    "conversation",
    "docs/decisions",
    "docs/indexes",
    "docs/migrations",
    "docs/plans",
    "docs/research",
    "docs/reviews",
    "docs/specs",
    "memory",
    "src",
)


class ControlInitializationError(RuntimeError):
    """Raised when initialization cannot proceed without guessing or overwriting."""


def render_access_block() -> str:
    return """<!-- project-conventions:access:start -->
## Mandatory Agent Entry

- Before substantive work, run `python3 -B .project-conventions/project_access.py status`.
- Response-only inspection enters `read-only`; any possible side effect enters `writer`. Do not write until the JSON receipt says `status: entered`.
- Save the returned `session_id` and `token`, re-read current state, run `check` before write batches, and finish project records before `finish`.
- A blocked Agent writes nothing. Never auto-clear another claim; recovery requires explicit user authorization, a reason, dry-run, then `--apply --token <recovery-token>` with the same reason.
- The entry is project-local and works from any cooperating Harness; no dispatcher or Agent messaging is required.
<!-- project-conventions:access:end -->
"""


def render_access_files(
    project_type: str = "code",
    project_role: str = "ordinary",
    coordination_id: str | None = None,
    runtime_backend: str = "project-local",
    coordination_root: str | None = None,
) -> dict[str, str]:
    helper_path = PACKAGE_ROOT / "scripts" / "project_access.py"
    validate_source_file(helper_path, "project access helper")
    helper = helper_path.read_text(encoding="utf-8")
    access_block = render_access_block().rstrip("\n")
    access_readme = (
        "# Project Access\n\n"
        "Use `project_access.py status`, then obtain `read-only` or exclusive `writer` "
        "admission before substantive work. Save the returned session and token. "
        "Claims never expire automatically. Recovery requires explicit user authorization: "
        "run a dry-run with the reason, then repeat with `--apply`, the same reason, and "
        "the returned one-time `--token`.\n"
    )
    config = {
        "access_readme_sha256": hashlib.sha256(access_readme.encode("utf-8")).hexdigest(),
        "agents_block_sha256": hashlib.sha256(access_block.encode("utf-8")).hexdigest(),
        "coordination_id": coordination_id,
        "coordination_root": coordination_root,
        "helper_sha256": hashlib.sha256(helper.encode("utf-8")).hexdigest(),
        "project_profile": "standard",
        "project_role": project_role,
        "project_type": project_type,
        "records_dir": None,
        "repository_root": None,
        "runtime_backend": runtime_backend,
        "schema_version": 1,
        "skill_package": None,
    }
    files = {
        ".project-conventions/.gitignore": "/runtime/\n*.sqlite3\n*.sqlite3-journal\n",
        ".project-conventions/ACCESS.md": access_readme,
        ".project-conventions/project.json": (
            json.dumps(config, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
        ),
        ".project-conventions/project_access.py": helper,
    }
    return files


def validate_name(value: str, label: str) -> str:
    stem = value.split(".", 1)[0].upper()
    if (
        not SAFE_NAME.fullmatch(value)
        or value in {".", ".."}
        or value.endswith((".", " "))
        or stem in WINDOWS_RESERVED_NAMES
    ):
        raise ControlInitializationError(f"unsafe {label}: {value!r}")
    return value


def validate_relative(value: str, label: str) -> str:
    if "\\" in value or value != value.strip("/"):
        raise ControlInitializationError(f"unsafe {label}: {value!r}")
    normalized = value
    path = PurePosixPath(normalized)
    if (
        not normalized
        or path.is_absolute()
        or not path.parts
        or any(part in {"", ".", ".."} for part in path.parts)
    ):
        raise ControlInitializationError(f"unsafe {label}: {value!r}")
    for part in path.parts:
        stem = part.split(".", 1)[0].upper()
        if (
            any(ord(character) < 32 or character in '<>:"|?*' for character in part)
            or part.endswith((".", " "))
            or stem in WINDOWS_RESERVED_NAMES
        ):
            raise ControlInitializationError(f"unsafe {label}: {value!r}")
    return path.as_posix()


def normalize_remote(url: str) -> str | None:
    value = url.strip().rstrip("/")
    scp = re.fullmatch(r"(?:[^@/:]+@)?github\.com:(.+)", value, re.IGNORECASE)
    if scp:
        identity = scp.group(1)
    else:
        parsed = urlsplit(value)
        if parsed.scheme.lower() not in {"http", "https", "ssh", "git"}:
            return None
        if (parsed.hostname or "").lower() != "github.com":
            return None
        identity = parsed.path.lstrip("/")
    if identity.endswith(".git"):
        identity = identity[:-4]
    if REMOTE_IDENTITY.fullmatch(identity):
        return identity
    return None


def display_remote(url: str) -> str:
    """Return a credential-free identity suitable for errors and receipts."""
    return normalize_remote(url) or "<unrecognized remote URL>"


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
    try:
        return path.is_symlink() or is_windows_junction(path)
    except OSError:
        return False


def run_git(repository_root: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repository_root), *arguments],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "unknown git error"
        detail = re.sub(
            r"((?:https?|ssh|git)://)[^/@\s]+@",
            r"\1<redacted>@",
            detail,
            flags=re.IGNORECASE,
        )
        raise ControlInitializationError(
            f"git {' '.join(arguments)} failed at {repository_root}: {detail}"
        )
    return result.stdout.strip()


def git_operation_markers(repository_root: Path) -> list[str]:
    git_dir = Path(run_git(repository_root, "rev-parse", "--git-dir"))
    if not git_dir.is_absolute():
        git_dir = repository_root / git_dir
    markers = (
        "MERGE_HEAD",
        "CHERRY_PICK_HEAD",
        "REVERT_HEAD",
        "BISECT_LOG",
        "rebase-apply",
        "rebase-merge",
        "index.lock",
        "shallow.lock",
    )
    return [marker for marker in markers if (git_dir / marker).exists()]


def validate_source_file(path: Path, label: str) -> None:
    if is_link_or_junction(path) or not path.is_file():
        raise ControlInitializationError(f"required {label} file is missing: {path}")


def validate_distribution(
    collection_root: Path,
    distribution_root: Path,
    repository_project: str,
    package_subpath: str,
    remote_identity: str,
    expected_ref: str,
) -> dict[str, str]:
    expected_root = collection_root / repository_project
    if is_link_or_junction(distribution_root) or not distribution_root.is_dir():
        raise ControlInitializationError(
            f"shared Repository Root is missing or linked: {distribution_root}"
        )
    if distribution_root.resolve() != expected_root.resolve():
        raise ControlInitializationError(
            "distribution root must be the collection-local shared checkout at "
            f"{expected_root}"
        )

    observed_root = Path(
        run_git(distribution_root, "rev-parse", "--show-toplevel")
    ).resolve()
    if observed_root != distribution_root.resolve():
        raise ControlInitializationError(
            f"declared shared Repository Root differs from Git readback: {observed_root}"
        )
    branch_result = subprocess.run(
        ["git", "-C", str(distribution_root), "symbolic-ref", "--quiet", "--short", "HEAD"],
        check=False,
        capture_output=True,
        text=True,
    )
    branch = branch_result.stdout.strip()
    if branch != expected_ref:
        raise ControlInitializationError(
            f"shared checkout branch differs: expected {expected_ref}, observed {branch or 'detached'}"
        )
    upstream = run_git(
        distribution_root,
        "rev-parse",
        "--abbrev-ref",
        "--symbolic-full-name",
        "@{upstream}",
    )
    if upstream != f"origin/{expected_ref}":
        raise ControlInitializationError(
            f"shared checkout upstream differs: expected origin/{expected_ref}, observed {upstream}"
        )
    if run_git(distribution_root, "status", "--porcelain=v1", "--untracked-files=all"):
        raise ControlInitializationError("shared checkout is not clean")
    operations = git_operation_markers(distribution_root)
    if operations:
        raise ControlInitializationError(
            "shared checkout has a Git operation or lock: " + ", ".join(operations)
        )
    origin = run_git(distribution_root, "remote", "get-url", "origin")
    observed_identity = normalize_remote(origin)
    if observed_identity is None or observed_identity.lower() != remote_identity.lower():
        raise ControlInitializationError(
            "shared checkout origin differs: "
            f"expected {remote_identity}, observed {display_remote(origin)}"
        )
    head = run_git(distribution_root, "rev-parse", "HEAD")
    remote_head = run_git(distribution_root, "rev-parse", f"origin/{expected_ref}")
    if head != remote_head:
        raise ControlInitializationError(
            f"shared checkout HEAD differs from origin/{expected_ref}: {head} != {remote_head}"
        )

    validate_source_file(distribution_root / "ROOT-MANIFEST.sha256", "distribution")
    package_root = distribution_root / package_subpath
    if is_link_or_junction(package_root) or not package_root.is_dir():
        raise ControlInitializationError(
            f"managed package root is missing or linked: {package_root}"
        )
    validate_source_file(package_root / "SKILL.md", "package entry")
    package_scripts = package_root / "scripts"
    if is_link_or_junction(package_scripts) or not package_scripts.is_dir():
        raise ControlInitializationError(
            f"package scripts directory is missing or linked: {package_scripts}"
        )
    validate_source_file(
        package_scripts / "validate_package.py", "package validator"
    )
    if PACKAGE_ROOT.resolve() != package_root.resolve():
        raise ControlInitializationError(
            "initializer must run from the managed package inside the declared "
            f"shared checkout: {package_root}"
        )
    for relative in PUBLIC_ROOT_DIRECTORIES:
        directory = distribution_root / relative
        if is_link_or_junction(directory) or not directory.is_dir():
            raise ControlInitializationError(
                f"required public-root directory is missing or linked: {directory}"
            )
    for relative in PUBLIC_ROOT_FILES:
        validate_source_file(distribution_root / relative, "public-root")
    for relative in TEMPLATE_FILES:
        validate_source_file(TEMPLATE_ROOT / relative, "control template")

    verification = subprocess.run(
        [
            sys.executable,
            "-B",
            str(distribution_root / "scripts" / "verify_release.py"),
            str(distribution_root),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if verification.returncode != 0:
        detail = verification.stderr.strip() or verification.stdout.strip()
        raise ControlInitializationError(
            f"distribution root verification failed: {detail}"
        )

    package_verification = subprocess.run(
        [
            sys.executable,
            "-B",
            str(package_scripts / "validate_package.py"),
            str(package_root),
        ],
        check=False,
        capture_output=True,
        text=True,
    )
    if package_verification.returncode != 0:
        detail = package_verification.stderr.strip() or package_verification.stdout.strip()
        raise ControlInitializationError(f"package verification failed: {detail}")

    return {
        "branch": branch,
        "head": head,
        "origin": observed_identity,
        "upstream": upstream,
        "repository_root": str(distribution_root.resolve()),
        "package_root": str(package_root.resolve()),
    }


def render_members(
    control_project: str,
    repository_project: str,
    member_project: str,
    package_subpath: str,
    remote_identity: str,
    member_category: str,
) -> str:
    return f"""# Canonical Collection Member Index

> Paths are relative to this Project Collection. `repository_root` records the shared Git worktree independently from each stable member source.

| key | name | path | role | source | repository_root | vcs | remote | managed_scope | category | status | tags |
|---|---|---|---|---|---|---|---|---|---|---|---|
| {control_project} | Skills Collection Control | {control_project} | collection-control | src | - | none | - | local control files | local-only | active | collection,links |
| {member_project} | Project Conventions | {member_project} | member | src/{member_project} | {repository_project} | git | {remote_identity} | {package_subpath}/ | {member_category} | active | skill,governance |
"""


def render_control_files(
    control_project: str,
    repository_project: str,
    member_project: str,
    package_subpath: str,
    remote_identity: str,
    member_category: str,
) -> dict[str, str]:
    members = render_members(
        control_project,
        repository_project,
        member_project,
        package_subpath,
        remote_identity,
        member_category,
    )
    files = {
        ".gitignore": ".DS_Store\nruntime/\nrelease/*/\n*.tmp\n__pycache__/\n*.py[cod]\n",
        "AGENTS.md": f"""# AGENTS.md

> Agent entry point for the `{control_project}` collection-control Project Root.

## Project

`{control_project}` owns device-local membership, explicit Skill exports, safe link utilities, and a root-overlay builder that reads the shared checkout directly. It does not own member source or a second root-file copy.

{render_access_block()}

## Mandatory Rules

- Canonical membership lives at `docs/indexes/members.md`; collection-root `MEMBERS.md` is its readable mirror.
- `{repository_project}/` is the one shared Repository Root for `{remote_identity}`. It is infrastructure, not another Project Root.
- `{member_project}/src/{member_project}` is only a stable projection to `{repository_project}/{package_subpath}`.
- Link sources come only from `src/config/skill-exports.tsv` and point directly into `{repository_project}/`, never through a member projection.
- The public-root builder reads allowlisted files directly from `../{repository_project}`; do not recreate `src/public-repo`.
- Link scripts require an explicit Agent/target and Skill for apply, never create target parents, and never replace conflicts.
- Updating `{member_project}` means running its update-only helper against `{repository_project}/{package_subpath}` and stopping after validation. Do not regenerate indexes or links.
- Do not clone, pull, push, publish, or apply links without authorization for that exact action.

## Directory Index

| Path | Purpose |
|---|---|
| `docs/indexes/members.md` | Canonical device-local member index |
| `src/config/` | Explicit Skill exports and Agent path candidates |
| `src/scripts/` | Collection-aware link and publication utilities |
| `src/tests/` | Deterministic control-project tests |
| `conversation/`, `memory/` | Collection-control continuity records |
| `release/`, `runtime/` | Generated and ignored local output |
""",
        "README.md": f"""# Skills Collection Control

This is the complete portable collection-control Project Root for its parent Project Collection.

The Git source of truth is `../{repository_project}`. Stable member wrappers and Agent consumers do not contain copies: they project or link directly to named packages in that checkout.

## Validation

```text
python -B src/tests/test_public_root_overlay.py
```

Initialization creates no Agent links. Linking is a later, separately authorized action using one exact Agent/target and Skill.

## Navigation

| Path | Purpose |
|---|---|
| `docs/indexes/members.md` | Canonical member and Repository Root mapping |
| `src/config/` | Direct exports from `{repository_project}/` plus Agent candidates |
| `src/scripts/` | Link and public-root overlay tools |
| `src/tests/` | Deterministic validation |
| `conversation/`, `memory/` | Initially empty device-local records |
| `release/`, `runtime/` | Initially empty generated output |

Updating one Skill is update-only: refresh `../{repository_project}` safely, validate the named package, and stop. It does not reinitialize this collection or relink consumers.
""",
        "docs/indexes/members.md": members,
        "conversation/00-initialization.md": (
            "# Collection-Control Initialization\n\n"
            "This Project Root was created by the deterministic shared-Skills initializer. "
            "No Agent links, Git history changes, or member migrations were performed.\n"
        ),
        "memory/MEMORY.md": (
            "# Project Memory\n\n"
            "Durable collection-control facts belong here after substantive work.\n"
        ),
        "src/README.md": f"""# Collection-Control Source

This directory contains deterministic control assets only. Member source is not copied here.

`src/config/skill-exports.tsv` exports `{repository_project}/{package_subpath}` directly, so every Agent consumer has one true source and does not depend on a wrapper-link chain.
""",
        "src/config/skill-exports.tsv": (
            "skill_name\tsource\tconsumers\n"
            f"project-conventions\t{repository_project}/{package_subpath}\tall\n"
        ),
    }
    files.update(
        render_access_files(
            project_role="collection-control",
            coordination_id=control_project,
        )
    )
    return files


def render_member_files(
    control_project: str,
    repository_project: str,
    member_project: str,
    package_subpath: str,
    remote_identity: str,
) -> dict[str, str]:
    files = {
        "AGENTS.md": f"""# AGENTS.md

> Agent entry point for the `{member_project}` Project Root.

## Project

This wrapper owns project documents, conversation, and memory. Its loadable Skill source is the stable projection `src/{member_project}`; the one Git source of truth is `../{repository_project}/{package_subpath}`.

{render_access_block()}

## Mandatory Rules

- This member's local helper stores claims in `../{control_project}/.project-conventions/runtime`, so one local `enter` automatically shares the collection-wide gate used by every member and the control project. Do not bypass it by entering `../{repository_project}` directly.
- Edit Skill content through `src/{member_project}` or directly at `../{repository_project}/{package_subpath}`; both resolve to the same bytes.
- `SKILL.md` is package source even though it is Markdown; never move the package under this wrapper's `docs/` or into an Agent consumer directory.
- Run Git only at `../{repository_project}` after verifying the worktree root, remote, branch, and status.
- An update request runs `src/{member_project}/scripts/update_shared_checkout.py`, validates the named package, reports the before/after commit, and stops.
- Update-only never rewrites this wrapper, collection indexes, other members, or Agent links.
- Put project records under `docs/`, collaboration under `conversation/`, and local continuity under `memory/`.

## Source Mapping

| Field | Value |
|---|---|
| Project Root | `.` |
| Stable Skill source | `src/{member_project}` |
| Repository Root | `../{repository_project}` |
| Remote | `{remote_identity}` |
| Default ref | `main` |
| Managed scope | `{package_subpath}/` |
""",
        "README.md": f"""# {member_project}

This Project Root is the stable local wrapper for the `{member_project}` Skill.

```text
src/{member_project}  ->  ../../{repository_project}/{package_subpath}
```

The wrapper keeps project-local documents and continuity records. The shared Git checkout at `../{repository_project}` is the only code source of truth. Agent consumer links should point directly to `../{repository_project}/{package_subpath}`, avoiding a link-to-link chain.

To update this Skill only, run its `scripts/update_shared_checkout.py` entry. It may fast-forward the shared repository, validates this named package, and then stops without rebuilding the collection or links.
""",
        "conversation/00-initialization.md": (
            "# Member Wrapper Initialization\n\n"
            "This wrapper was created around the verified shared package source. "
            "No second checkout or source copy was created.\n"
        ),
        "memory/MEMORY.md": (
            "# Project Memory\n\n"
            "Durable wrapper facts belong here after substantive work.\n"
        ),
    }
    files.update(
        render_access_files(
            project_role="collection-member",
            coordination_id=control_project,
            runtime_backend="collection-control",
            coordination_root=f"../{control_project}",
        )
    )
    return files


def render_root_files(
    control_project: str,
    repository_project: str,
    member_project: str,
    package_subpath: str,
    remote_identity: str,
    member_category: str,
) -> dict[str, str]:
    members = render_members(
        control_project,
        repository_project,
        member_project,
        package_subpath,
        remote_identity,
        member_category,
    )
    table = "\n".join(members.splitlines()[4:]) + "\n"
    return {
        "AGENTS.md": f"""# Project Collection

> Routing entry for related, independently governed Skill Project Roots.

## Mandatory Rules

- This directory is a Project Collection, not a Git repository or monorepo.
- `{repository_project}/` is the single shared Repository Root for `{remote_identity}`; it is infrastructure, not a Project Root.
- `{control_project}/` owns local membership and link utilities, not member source.
- `{member_project}/src/{member_project}` projects to `{repository_project}/{package_subpath}`.
- Agent consumers link directly to `{repository_project}/{package_subpath}`.
- Updating `{member_project}` only refreshes `{repository_project}` with the package update helper, validates the named package, and stops. Do not regenerate wrappers, indexes, records, or links.
- Never create a second checkout or package copy to update one Skill.

## Entry Points

| Path | Purpose |
|---|---|
| `{repository_project}/` | Shared Git source of truth |
| `{member_project}/` | Stable Project Root and package projection |
| `{control_project}/` | Collection-control Project Root |
| `{control_project}/docs/indexes/members.md` | Canonical member and Repository Root index |
| `MEMBERS.md` | Readable mirror |
""",
        "README.md": f"""# Skills Project Collection

This collection separates stable project organization from one shared Git source:

```text
{repository_project}/                              # one Git checkout
{repository_project}/{package_subpath}/            # true Skill source
{member_project}/src/{member_project}              # stable projection
{control_project}/                                 # local index and link tools
```

Clone `https://github.com/{remote_identity}.git` exactly once as `{repository_project}/`. The collection root and member wrapper are not Git repositories.

Agent consumer links point directly to `{repository_project}/{package_subpath}`. Updating a Skill fast-forwards the shared checkout and validates the named package; it does not trigger initialization, migration, cataloging, or relinking.
""",
        "MEMBERS.md": (
            "# Members\n\nReadable mirror of the canonical index at "
            f"`{control_project}/docs/indexes/members.md`.\n\n{table}"
        ),
    }


def write_text(path: Path, content: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", encoding="utf-8", newline="\n") as handle:
        handle.write(content)


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


def copy_required(source_root: Path, target_root: Path, relatives: tuple[str, ...]) -> None:
    for relative in relatives:
        source = source_root / relative
        validate_source_file(source, "copy source")
        destination = target_root / relative
        destination.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source, destination)


def expected_control_files(dynamic: dict[str, str]) -> set[str]:
    expected = set(dynamic)
    expected.add("src/config/agent-paths.tsv")
    expected.update(TEMPLATE_FILES)
    return expected


def observed_files(
    root: Path,
    ignored_links: set[str] | None = None,
    ignored_directories: set[str] | None = None,
) -> set[str]:
    """List files without ever descending through a link or junction."""
    ignored_links = ignored_links or set()
    ignored_directories = ignored_directories or set()
    observed: set[str] = set()
    pending = [root]
    while pending:
        directory = pending.pop()
        with os.scandir(directory) as entries:
            for entry in entries:
                path = Path(entry.path)
                relative = path.relative_to(root).as_posix()
                if is_link_or_junction(path):
                    if relative not in ignored_links:
                        observed.add(relative)
                    continue
                if entry.is_dir(follow_symlinks=False):
                    if relative not in ignored_directories:
                        pending.append(path)
                elif entry.is_file(follow_symlinks=False):
                    observed.add(relative)
                else:
                    observed.add(relative)
    return observed


def verify_control_tree(control_root: Path, dynamic: dict[str, str]) -> None:
    if is_link_or_junction(control_root) or not control_root.is_dir():
        raise ControlInitializationError(f"control path is not a real directory: {control_root}")
    for relative in CONTROL_DIRECTORIES:
        path = control_root / relative
        if is_link_or_junction(path) or not path.is_dir():
            raise ControlInitializationError(f"control directory readback failed: {path}")
    for relative, content in dynamic.items():
        path = control_root / relative
        validate_source_file(path, "generated control")
        if path.read_text(encoding="utf-8") != content:
            raise ControlInitializationError(f"generated control file differs: {path}")
    expected = expected_control_files(dynamic)
    runtime = control_root / ".project-conventions" / "runtime"
    if is_link_or_junction(runtime) or (runtime.exists() and not runtime.is_dir()):
        raise ControlInitializationError(f"control runtime path is not a real directory: {runtime}")
    ignored_runtime = {".project-conventions/runtime"} if runtime.is_dir() else set()
    observed = observed_files(control_root, ignored_directories=ignored_runtime)
    if observed != expected:
        raise ControlInitializationError(
            f"control file set differs: missing={sorted(expected - observed)} "
            f"extra={sorted(observed - expected)}"
        )


def create_member_projection(link_path: Path, target: Path, raw_posix_target: str) -> None:
    if os.name == "nt":
        result = subprocess.run(
            ["cmd", "/d", "/c", "mklink", "/J", str(link_path), str(target)],
            check=False,
            capture_output=True,
            text=True,
        )
        if result.returncode != 0:
            detail = result.stderr.strip() or result.stdout.strip()
            raise ControlInitializationError(f"junction creation failed: {detail}")
    else:
        os.symlink(raw_posix_target, link_path, target_is_directory=True)


def verify_member_tree(
    member_root: Path,
    dynamic: dict[str, str],
    package_root: Path,
    member_project: str,
) -> None:
    if is_link_or_junction(member_root) or not member_root.is_dir():
        raise ControlInitializationError(f"member path is not a real directory: {member_root}")
    for relative in MEMBER_DIRECTORIES:
        path = member_root / relative
        if is_link_or_junction(path) or not path.is_dir():
            raise ControlInitializationError(f"member directory readback failed: {path}")
    for relative, content in dynamic.items():
        path = member_root / relative
        validate_source_file(path, "generated member")
        if path.read_text(encoding="utf-8") != content:
            raise ControlInitializationError(f"generated member file differs: {path}")
    projection = member_root / "src" / member_project
    if os.name == "nt":
        if not is_windows_junction(projection):
            raise ControlInitializationError(
                f"member projection is not a Windows directory junction: {projection}"
            )
    else:
        if not projection.is_symlink():
            raise ControlInitializationError(
                f"member projection is not a Unix symlink: {projection}"
            )
        expected_raw_target = os.path.relpath(
            package_root.resolve(), projection.parent.resolve()
        ).replace(os.sep, "/")
        observed_raw_target = os.readlink(projection).replace(os.sep, "/")
        if observed_raw_target != expected_raw_target:
            raise ControlInitializationError(
                "member projection raw target differs: "
                f"expected {expected_raw_target}, observed {observed_raw_target}"
            )
    if not projection.exists() or projection.resolve() != package_root.resolve():
        raise ControlInitializationError(
            f"member projection target differs: {projection} -> {projection.resolve()}"
        )
    if not (projection / "SKILL.md").is_file():
        raise ControlInitializationError(f"member projection package entry is missing: {projection}")
    runtime = member_root / ".project-conventions" / "runtime"
    if is_link_or_junction(runtime) or (runtime.exists() and not runtime.is_dir()):
        raise ControlInitializationError(f"member runtime path is not a real directory: {runtime}")
    ignored_runtime = {".project-conventions/runtime"} if runtime.is_dir() else set()
    observed = observed_files(
        member_root,
        {f"src/{member_project}"},
        ignored_directories=ignored_runtime,
    )
    expected = set(dynamic)
    if observed != expected:
        raise ControlInitializationError(
            f"member file set differs: missing={sorted(expected - observed)} "
            f"extra={sorted(observed - expected)}"
        )


def remove_created_tree(path: Path) -> None:
    if path.exists() or is_link_or_junction(path):
        shutil.rmtree(path)


def initialize(
    collection_root: Path,
    distribution_root: Path,
    control_project: str,
    repository_project: str,
    member_project: str,
    package_subpath: str,
    remote_identity: str,
    expected_ref: str,
    member_category: str,
    apply: bool,
) -> dict[str, object]:
    control_project = validate_name(control_project, "control-project name")
    repository_project = validate_name(repository_project, "repository-project name")
    member_project = validate_name(member_project, "member-project name")
    package_subpath = validate_relative(package_subpath, "package subpath")
    if package_subpath != member_project:
        raise ControlInitializationError(
            "this initializer requires package subpath to match the stable member name"
        )
    if not REMOTE_IDENTITY.fullmatch(remote_identity):
        raise ControlInitializationError(f"unsafe remote identity: {remote_identity!r}")
    expected_ref = validate_name(expected_ref, "repository ref")
    if member_category not in {
        "personal-open",
        "personal-private",
        "local-only",
        "upstream-open",
    }:
        raise ControlInitializationError(f"unsupported member category: {member_category}")

    raw_collection_root = collection_root.expanduser().absolute()
    raw_distribution_root = distribution_root.expanduser().absolute()
    if is_link_or_junction(raw_collection_root) or not raw_collection_root.is_dir():
        raise ControlInitializationError(
            f"collection root is missing or linked: {raw_collection_root}"
        )
    expected_distribution_root = raw_collection_root / repository_project
    if os.path.normcase(os.path.abspath(raw_distribution_root)) != os.path.normcase(
        os.path.abspath(expected_distribution_root)
    ):
        raise ControlInitializationError(
            "distribution root must be the exact collection-local path at "
            f"{expected_distribution_root}"
        )
    if is_link_or_junction(raw_distribution_root) or not raw_distribution_root.is_dir():
        raise ControlInitializationError(
            f"shared Repository Root is missing or linked: {raw_distribution_root}"
        )
    collection_root = raw_collection_root.resolve()
    distribution_root = raw_distribution_root.resolve()
    if (collection_root / ".git").exists() or is_link_or_junction(
        collection_root / ".git"
    ):
        raise ControlInitializationError("collection root must not be a Git worktree")

    allowed_entries = {
        repository_project,
        control_project,
        member_project,
        "AGENTS.md",
        "README.md",
        "MEMBERS.md",
    }
    unexpected_entries = sorted(
        path.name
        for path in collection_root.iterdir()
        if path.name not in allowed_entries
    )
    if unexpected_entries:
        raise ControlInitializationError(
            "fresh collection contains unnamed entries: " + ", ".join(unexpected_entries)
        )

    repository_state = validate_distribution(
        collection_root,
        distribution_root,
        repository_project,
        package_subpath,
        remote_identity,
        expected_ref,
    )
    package_root = distribution_root / package_subpath
    root_files = render_root_files(
        control_project,
        repository_project,
        member_project,
        package_subpath,
        remote_identity,
        member_category,
    )
    control_files = render_control_files(
        control_project,
        repository_project,
        member_project,
        package_subpath,
        remote_identity,
        member_category,
    )
    member_files = render_member_files(
        control_project,
        repository_project,
        member_project,
        package_subpath,
        remote_identity,
    )

    root_state: dict[str, str] = {}
    for name in root_files:
        path = collection_root / name
        if is_link_or_junction(path):
            raise ControlInitializationError(
                f"collection routing path must not be linked: {path}"
            )
        if path.exists() and not path.is_file():
            raise ControlInitializationError(
                f"collection routing path is not a file: {path}"
            )
        if path.is_file():
            root_state[name] = path.read_text(encoding="utf-8")
    if root_state and root_state != root_files:
        raise ControlInitializationError(
            "collection root files are partial or differ from the deterministic shared layout"
        )

    control_root = collection_root / control_project
    member_root = collection_root / member_project
    control_exists = control_root.exists() or is_link_or_junction(control_root)
    member_exists = member_root.exists() or is_link_or_junction(member_root)
    if control_exists != member_exists:
        raise ControlInitializationError(
            "control and member paths must both be absent or both match the initialized layout"
        )
    if control_exists:
        if root_state != root_files:
            raise ControlInitializationError("initialized paths exist but root routing files do not match")
        verify_control_tree(control_root, control_files)
        verify_member_tree(member_root, member_files, package_root, member_project)
        return {
            "status": "already_initialized",
            "collection_root": str(collection_root),
            "repository": repository_state,
            "control_root": str(control_root),
            "member_root": str(member_root),
            "member_projection": str(member_root / "src" / member_project),
            "created": [],
        }

    if root_state:
        raise ControlInitializationError(
            "root routing files exist while control and member paths are absent"
        )

    planned_control_files = sorted(expected_control_files(control_files))
    planned_member_files = sorted(member_files)
    projection = member_root / "src" / member_project
    if not apply:
        return {
            "status": "would_initialize",
            "collection_root": str(collection_root),
            "repository": repository_state,
            "would_create_root_files": sorted(root_files),
            "would_create_control_directories": list(CONTROL_DIRECTORIES),
            "would_create_control_files": planned_control_files,
            "would_create_member_directories": list(MEMBER_DIRECTORIES),
            "would_create_member_files": planned_member_files,
            "would_create_member_projection": {
                "path": str(projection),
                "target": str(package_root.resolve()),
                "kind": "junction" if os.name == "nt" else "symlink",
            },
            "agent_links_created": [],
        }

    control_staging = Path(
        tempfile.mkdtemp(prefix=f".{control_project}.initialize-", dir=collection_root)
    )
    member_staging = Path(
        tempfile.mkdtemp(prefix=f".{member_project}.initialize-", dir=collection_root)
    )
    created_control = False
    created_member = False
    created_root_files: list[Path] = []
    try:
        for relative in CONTROL_DIRECTORIES:
            (control_staging / relative).mkdir(parents=True, exist_ok=True)
        copy_required(TEMPLATE_ROOT, control_staging, TEMPLATE_FILES)
        shutil.copy2(
            distribution_root / "config" / "agent-paths.tsv",
            control_staging / "src" / "config" / "agent-paths.tsv",
        )
        for relative, content in control_files.items():
            write_text(control_staging / relative, content)
        verify_control_tree(control_staging, control_files)

        for relative in MEMBER_DIRECTORIES:
            (member_staging / relative).mkdir(parents=True, exist_ok=True)
        for relative, content in member_files.items():
            write_text(member_staging / relative, content)
        raw_target = f"../../{repository_project}/{package_subpath}"
        create_member_projection(
            member_staging / "src" / member_project,
            package_root.resolve(),
            raw_target,
        )
        verify_member_tree(member_staging, member_files, package_root, member_project)

        control_staging.rename(control_root)
        created_control = True
        member_staging.rename(member_root)
        created_member = True
        for name, content in root_files.items():
            write_atomic(collection_root / name, content)
            created_root_files.append(collection_root / name)
    except Exception:
        for path in reversed(created_root_files):
            if path.exists() and path.is_file():
                path.unlink()
        if created_member:
            remove_created_tree(member_root)
        if created_control:
            remove_created_tree(control_root)
        raise
    finally:
        if member_staging.exists():
            shutil.rmtree(member_staging)
        if control_staging.exists():
            shutil.rmtree(control_staging)

    verify_control_tree(control_root, control_files)
    verify_member_tree(member_root, member_files, package_root, member_project)
    for name, content in root_files.items():
        if (collection_root / name).read_text(encoding="utf-8") != content:
            raise ControlInitializationError(f"collection root readback failed: {name}")

    return {
        "status": "initialized",
        "collection_root": str(collection_root),
        "repository": repository_state,
        "control_root": str(control_root),
        "member_root": str(member_root),
        "member_projection": {
            "path": str(projection),
            "target": str(projection.resolve()),
            "kind": "junction" if os.name == "nt" else "symlink",
        },
        "created_control_files": planned_control_files,
        "created_member_files": planned_member_files,
        "created_root_files": sorted(root_files),
        "agent_links_created": [],
        "git_roots_created": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("collection_root", type=Path)
    parser.add_argument("--distribution-root", required=True, type=Path)
    parser.add_argument("--control-project", default="skills")
    parser.add_argument("--repository-project", default="GitHub")
    parser.add_argument("--member-project", default="project-conventions")
    parser.add_argument("--package-subpath", default="project-conventions")
    parser.add_argument("--member-remote", default="obisoldbee/skills")
    parser.add_argument("--repository-ref", default="main")
    parser.add_argument("--member-category", default="personal-open")
    parser.add_argument("--apply", action="store_true")
    arguments = parser.parse_args()
    try:
        result = initialize(
            arguments.collection_root,
            arguments.distribution_root,
            arguments.control_project,
            arguments.repository_project,
            arguments.member_project,
            arguments.package_subpath,
            arguments.member_remote,
            arguments.repository_ref,
            arguments.member_category,
            arguments.apply,
        )
    except (ControlInitializationError, OSError, UnicodeError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
