#!/usr/bin/env python3
"""Create a complete portable Skills collection-control Project Root."""

from __future__ import annotations

import argparse
import json
import os
import re
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path, PurePosixPath

from initialize_project_collection import render_files as render_collection_files


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
TEMPLATE_FILES = (
    "src/scripts/build_public_root_overlay.py",
    "src/scripts/link-macos.sh",
    "src/scripts/link-windows.ps1",
    "src/tests/test_public_root_overlay.py",
)
CONTROL_DIRECTORIES = (
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
    "src/public-repo",
    "src/scripts",
    "src/tests",
)


class ControlInitializationError(RuntimeError):
    """Raised when the control project cannot be created without guessing."""


def validate_name(value: str, label: str) -> str:
    if not SAFE_NAME.fullmatch(value) or value in {".", ".."}:
        raise ControlInitializationError(f"unsafe {label}: {value!r}")
    return value


def validate_relative(value: str, label: str) -> str:
    normalized = value.replace("\\", "/").strip("/")
    path = PurePosixPath(normalized)
    if (
        not normalized
        or path.is_absolute()
        or not path.parts
        or any(part in {"", ".", ".."} for part in path.parts)
    ):
        raise ControlInitializationError(f"unsafe {label}: {value!r}")
    return path.as_posix()


def normalize_remote(url: str) -> str | None:
    value = url.strip().rstrip("/")
    prefixes = (
        "https://github.com/",
        "http://github.com/",
        "ssh://git@github.com/",
        "git@github.com:",
    )
    for prefix in prefixes:
        if value.lower().startswith(prefix.lower()):
            identity = value[len(prefix) :]
            if identity.endswith(".git"):
                identity = identity[:-4]
            return identity
    return None


def run_git(repository_root: Path, *arguments: str) -> str:
    result = subprocess.run(
        ["git", "-C", str(repository_root), *arguments],
        check=False,
        capture_output=True,
        text=True,
    )
    if result.returncode != 0:
        detail = result.stderr.strip() or result.stdout.strip() or "unknown git error"
        raise ControlInitializationError(
            f"git {' '.join(arguments)} failed at {repository_root}: {detail}"
        )
    return result.stdout.strip()


def validate_member(
    collection_root: Path,
    member_project: str,
    repository_root_relative: str,
    package_source_relative: str,
    remote_identity: str,
    expected_ref: str,
) -> dict[str, str]:
    member_root = collection_root / member_project
    if member_root.is_symlink() or not member_root.is_dir():
        raise ControlInitializationError(
            f"member Project Root is missing or not a real directory: {member_root}"
        )

    repository_root = member_root / repository_root_relative
    package_root = member_root / package_source_relative
    if repository_root.is_symlink() or not repository_root.is_dir():
        raise ControlInitializationError(
            f"member Repository Root is missing or not a real directory: {repository_root}"
        )
    if package_root.is_symlink() or not (package_root / "SKILL.md").is_file():
        raise ControlInitializationError(
            f"member Skill package is missing at the declared source: {package_root}"
        )

    observed_root = Path(run_git(repository_root, "rev-parse", "--show-toplevel")).resolve()
    if observed_root != repository_root.resolve():
        raise ControlInitializationError(
            f"declared Repository Root differs from Git readback: {observed_root}"
        )
    branch = run_git(repository_root, "symbolic-ref", "--quiet", "--short", "HEAD")
    if branch != expected_ref:
        raise ControlInitializationError(
            f"member branch differs: expected {expected_ref}, observed {branch or 'detached'}"
        )
    upstream = run_git(
        repository_root,
        "rev-parse",
        "--abbrev-ref",
        "--symbolic-full-name",
        "@{upstream}",
    )
    if upstream != f"origin/{expected_ref}":
        raise ControlInitializationError(
            f"member upstream differs: expected origin/{expected_ref}, observed {upstream}"
        )
    status = run_git(repository_root, "status", "--porcelain=v1")
    if status:
        raise ControlInitializationError("member checkout is not clean")
    origin = run_git(repository_root, "remote", "get-url", "origin")
    observed_identity = normalize_remote(origin)
    if observed_identity is None or observed_identity.lower() != remote_identity.lower():
        raise ControlInitializationError(
            f"member origin differs: expected {remote_identity}, observed {origin}"
        )
    head = run_git(repository_root, "rev-parse", "HEAD")
    remote_head = run_git(repository_root, "rev-parse", f"origin/{expected_ref}")
    if head != remote_head:
        raise ControlInitializationError(
            f"member HEAD differs from origin/{expected_ref}: {head} != {remote_head}"
        )
    return {
        "branch": branch,
        "head": head,
        "origin": origin,
        "upstream": upstream,
        "repository_root": str(repository_root.resolve()),
        "package_root": str(package_root.resolve()),
    }


def validate_source_file(path: Path, label: str) -> None:
    if path.is_symlink() or not path.is_file():
        raise ControlInitializationError(f"required {label} file is missing: {path}")


def validate_distribution(distribution_root: Path) -> None:
    if distribution_root.is_symlink() or not distribution_root.is_dir():
        raise ControlInitializationError(
            f"distribution root is missing or not a real directory: {distribution_root}"
        )
    validate_source_file(distribution_root / "ROOT-MANIFEST.sha256", "distribution")
    validate_source_file(
        distribution_root / "project-conventions" / "SKILL.md", "package entry"
    )
    expected_package_root = (distribution_root / "project-conventions").resolve()
    if PACKAGE_ROOT.resolve() != expected_package_root:
        raise ControlInitializationError(
            "initializer must run from the project-conventions package inside the "
            f"declared distribution root: {expected_package_root}"
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


def render_members(
    control_project: str,
    member_project: str,
    member_source: str,
    remote_identity: str,
    member_category: str,
) -> str:
    return f"""# Canonical Collection Member Index

> Paths are relative to this Project Collection. This table is the canonical member fact source for the current computer.

| key | name | path | role | source | vcs | remote | managed_scope | category | status | tags |
|---|---|---|---|---|---|---|---|---|---|---|
| {control_project} | Skills Collection Control | {control_project} | collection-control | src | none | - | local control files | local-only | active | collection,links |
| {member_project} | Project Conventions | {member_project} | member | {member_source} | git | {remote_identity} | project-conventions/ | {member_category} | active | skill,governance |
"""


def render_control_files(
    control_project: str,
    member_project: str,
    member_repository_root: str,
    member_source: str,
    remote_identity: str,
    member_category: str,
) -> dict[str, str]:
    collection_source = f"{member_project}/{member_source}"
    members = render_members(
        control_project,
        member_project,
        member_source,
        remote_identity,
        member_category,
    )
    return {
        ".gitignore": ".DS_Store\nruntime/\nrelease/*/\n*.tmp\n__pycache__/\n*.py[cod]\n",
        "AGENTS.md": f"""# AGENTS.md

> Agent entry point for the `{control_project}` collection-control Project Root.

## Project

`{control_project}` owns the canonical member index, explicit Skill exports, known Agent target-path candidates, safe local link utilities, and the portable public-repository root overlay. It never owns member source.

## Mandatory Rules

- Canonical membership lives at `docs/indexes/members.md`; the collection root `MEMBERS.md` is only its readable mirror.
- Member source remains inside each member Project Root. Never place `{member_project}` source under this project's `src/`.
- Link sources come only from `src/config/skill-exports.tsv`.
- Link scripts require an explicit Agent/target and Skill for apply, default to scan, never create target parents, and never replace conflicts.
- Public-root publication reads only `src/public-repo/` and writes candidates only under `release/`.
- A request to update `{member_project}` operates only on `../{member_project}/{member_repository_root}` using the member's update-only rules, validates that checkout, and stops. It must not edit this project, collection files, indexes, records, or links.
- Do not initialize Git, clone, pull, push, publish, or apply links here without explicit authorization for that exact action.

## Directory Index

| Path | Purpose |
|---|---|
| `README.md` | Human overview and validation commands |
| `docs/indexes/members.md` | Canonical device-local member index |
| `docs/` | Collection-level plans, decisions, reviews, and research |
| `conversation/` | Collection-control decisions |
| `memory/` | Project-local continuity notes |
| `src/config/` | Explicit Skill exports and Agent path candidates |
| `src/scripts/` | Collection-aware link and publication utilities |
| `src/public-repo/` | Portable source set for files owned at the public repository root |
| `src/tests/` | Deterministic control-project tests |
| `release/` | Generated candidates; not proof of publication |
| `runtime/` | Ignored observations and temporary output |
""",
        "README.md": f"""# Skills Collection Control

This is the complete portable collection-control Project Root for its parent Project Collection.

It manages the canonical device-local member index, explicit Skill exports, known Agent target candidates, scan-first link utilities, and the public repository's root-file overlay. It does not contain or own member Skill source.

## Validation

Run from this Project Root:

```text
python -B src/tests/test_public_root_overlay.py
```

Linking is a later, separately approved action. Scan one exact target and Skill first; do not apply links during initialization.

## Navigation

| Path | Purpose |
|---|---|
| `AGENTS.md` | Agent routing and lifecycle boundaries |
| `docs/indexes/members.md` | Canonical member index |
| `src/config/` | Device-local exports plus portable Agent path candidates |
| `src/scripts/` | Collection-aware link and root-overlay tools |
| `src/public-repo/` | Public repository root-file source |
| `src/tests/` | Deterministic validation |
| `conversation/`, `memory/` | Device-local records; initially empty |
| `release/`, `runtime/` | Generated and ignored local output; initially empty |

Updating `{member_project}` is a separate update-only lifecycle confined to that member's existing Git checkout. It does not regenerate this control project.
""",
        "docs/indexes/members.md": members,
        "src/README.md": f"""# Collection-Control Source

This directory contains only deterministic control assets for the parent Project Collection:

```text
src/
├── README.md
├── config/
├── public-repo/
├── scripts/
└── tests/
```

Member Skill source remains at `../../{member_project}/{member_source}/` and is referenced only through the explicit export allowlist.
""",
        "src/config/skill-exports.tsv": (
            "skill_name\tsource\tconsumers\n"
            f"project-conventions\t{collection_source}\tall\n"
        ),
    }


def render_final_root_files(
    control_project: str,
    member_project: str,
    member_repository_root: str,
    member_source: str,
    remote_identity: str,
    member_category: str,
) -> dict[str, str]:
    members = render_members(
        control_project,
        member_project,
        member_source,
        remote_identity,
        member_category,
    )
    rows = "\n".join(members.splitlines()[4:]) + "\n"
    return {
        "AGENTS.md": f"""# Project Collection

> Routing entry for related, independently governed Project Roots.

## Mandatory Rules

- This directory is a Project Collection, not a Project Root, Git super-repository, or monorepo.
- Do not initialize Git at this collection root.
- `{control_project}/` is the collection-control Project Root and owns the canonical member index.
- `{member_project}/` is an independent member Project Root; its Repository Root is `{member_project}/{member_repository_root}`.
- Keep every member's source, documents, conversation, and memory inside that member Project Root.
- Updating `{member_project}` means a clean fast-forward-only update and validation inside its existing Repository Root, then stopping. Do not edit the collection root, `{control_project}/`, indexes, records, or links.
- Do not create or apply a Skill link without separate approval for one exact consumer and Skill.

## Entry Points

| Path | Purpose |
|---|---|
| `README.md` | Human overview and lifecycle boundaries |
| `MEMBERS.md` | Readable mirror of the canonical member index |
| `{control_project}/docs/indexes/members.md` | Canonical member index |
| `{control_project}/` | Collection-control Project Root |
| `{member_project}/` | Project Conventions member Project Root |
""",
        "README.md": f"""# Project Collection

This directory groups independently governed Project Roots. It is a routing overlay, not a Git repository.

## Members

- `{control_project}/` manages only device-local collection indexes and deterministic control assets.
- `{member_project}/` owns the `project-conventions` Skill package at `{member_source}` and the Git remote `{remote_identity}`.

## Update boundary

A request to update `project-conventions` acts only on `{member_project}/{member_repository_root}`, performs a clean fast-forward-only update plus validation, and stops. It does not reinitialize this collection, rewrite the control project, scan other projects, or recreate links.

See `{control_project}/docs/indexes/members.md` for canonical membership and `MEMBERS.md` for its readable mirror.
""",
        "MEMBERS.md": "# Members\n\nReadable mirror of the canonical index at "
        f"`{control_project}/docs/indexes/members.md`.\n\n{rows}",
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
    expected.update(f"src/public-repo/{relative}" for relative in PUBLIC_ROOT_FILES)
    return expected


def verify_control_tree(control_root: Path, dynamic: dict[str, str]) -> None:
    for relative in CONTROL_DIRECTORIES:
        path = control_root / relative
        if path.is_symlink() or not path.is_dir():
            raise ControlInitializationError(f"control directory readback failed: {path}")
    for relative, content in dynamic.items():
        path = control_root / relative
        validate_source_file(path, "generated control")
        if path.read_text(encoding="utf-8") != content:
            raise ControlInitializationError(f"generated control file differs: {path}")
    observed = {
        path.relative_to(control_root).as_posix()
        for path in control_root.rglob("*")
        if path.is_file()
    }
    expected = expected_control_files(dynamic)
    if observed != expected:
        raise ControlInitializationError(
            f"control file set differs: missing={sorted(expected - observed)} "
            f"extra={sorted(observed - expected)}"
        )


def initialize(
    collection_root: Path,
    distribution_root: Path,
    control_project: str,
    member_project: str,
    repository_root_relative: str,
    package_source_relative: str,
    remote_identity: str,
    expected_ref: str,
    member_category: str,
    apply: bool,
) -> dict[str, object]:
    control_project = validate_name(control_project, "control-project name")
    member_project = validate_name(member_project, "member-project name")
    repository_root_relative = validate_relative(
        repository_root_relative, "repository-root path"
    )
    package_source_relative = validate_relative(
        package_source_relative, "package-source path"
    )
    if not REMOTE_IDENTITY.fullmatch(remote_identity):
        raise ControlInitializationError(f"unsafe remote identity: {remote_identity!r}")
    expected_ref = validate_name(expected_ref, "member ref")
    if member_category not in {
        "personal-open",
        "personal-private",
        "local-only",
        "upstream-open",
    }:
        raise ControlInitializationError(f"unsupported member category: {member_category}")

    collection_root = collection_root.expanduser().resolve()
    distribution_root = distribution_root.expanduser().resolve()
    if collection_root.is_symlink() or not collection_root.is_dir():
        raise ControlInitializationError(
            f"collection root is missing or not a real directory: {collection_root}"
        )
    allowed_entries = {
        "AGENTS.md",
        "README.md",
        "MEMBERS.md",
        control_project,
        member_project,
    }
    unexpected_entries = sorted(
        path.name for path in collection_root.iterdir() if path.name not in allowed_entries
    )
    if unexpected_entries:
        raise ControlInitializationError(
            "collection root contains unnamed entries: " + ", ".join(unexpected_entries)
        )
    validate_distribution(distribution_root)
    member_state = validate_member(
        collection_root,
        member_project,
        repository_root_relative,
        package_source_relative,
        remote_identity,
        expected_ref,
    )

    reserved = tuple(sorted({control_project, member_project}))
    pending_root = render_collection_files(control_project, reserved)
    final_root = render_final_root_files(
        control_project,
        member_project,
        repository_root_relative,
        package_source_relative,
        remote_identity,
        member_category,
    )
    dynamic = render_control_files(
        control_project,
        member_project,
        repository_root_relative,
        package_source_relative,
        remote_identity,
        member_category,
    )
    root_names = ("AGENTS.md", "README.md", "MEMBERS.md")
    root_state = {
        name: (collection_root / name).read_text(encoding="utf-8")
        for name in root_names
        if (collection_root / name).is_file() and not (collection_root / name).is_symlink()
    }
    root_forms_valid = set(root_state) == set(root_names) and all(
        root_state[name] in {pending_root[name], final_root[name]} for name in root_names
    )
    if not root_forms_valid:
        raise ControlInitializationError(
            "collection root files are missing or differ from the deterministic pending/final forms"
        )

    control_root = collection_root / control_project
    if control_root.exists() or control_root.is_symlink():
        if control_root.is_symlink() or not control_root.is_dir():
            raise ControlInitializationError(f"control path is not a real directory: {control_root}")
        verify_control_tree(control_root, dynamic)
        if root_state != final_root:
            if not apply:
                return {
                    "status": "would_finalize_existing_control",
                    "collection_root": str(collection_root),
                    "control_root": str(control_root),
                    "would_finalize_root_files": list(root_names),
                    "member": member_state,
                }
            for name, content in final_root.items():
                write_atomic(collection_root / name, content)
            for name, content in final_root.items():
                if (collection_root / name).read_text(encoding="utf-8") != content:
                    raise ControlInitializationError(
                        f"collection root recovery readback failed: {name}"
                    )
            return {
                "status": "finalized_existing_control",
                "collection_root": str(collection_root),
                "control_root": str(control_root),
                "finalized_root_files": list(root_names),
                "member": member_state,
            }
        return {
            "status": "already_initialized",
            "collection_root": str(collection_root),
            "control_root": str(control_root),
            "created": [],
            "member": member_state,
        }

    if root_state != pending_root:
        raise ControlInitializationError(
            "collection root is finalized or partially finalized but the control project is absent"
        )

    planned_files = sorted(expected_control_files(dynamic))
    if not apply:
        return {
            "status": "would_initialize",
            "collection_root": str(collection_root),
            "control_root": str(control_root),
            "would_create_directories": list(CONTROL_DIRECTORIES),
            "would_create_files": planned_files,
            "would_finalize_root_files": ["AGENTS.md", "README.md", "MEMBERS.md"],
            "member": member_state,
        }

    staging = Path(tempfile.mkdtemp(prefix=f".{control_project}.initialize-", dir=collection_root))
    try:
        for relative in CONTROL_DIRECTORIES:
            (staging / relative).mkdir(parents=True, exist_ok=True)
        copy_required(TEMPLATE_ROOT, staging, TEMPLATE_FILES)
        copy_required(
            distribution_root,
            staging / "src" / "public-repo",
            PUBLIC_ROOT_FILES,
        )
        shutil.copy2(
            distribution_root / "config" / "agent-paths.tsv",
            staging / "src" / "config" / "agent-paths.tsv",
        )
        for relative, content in dynamic.items():
            write_text(staging / relative, content)
        verify_control_tree(staging, dynamic)
        staging.rename(control_root)
        for name, content in final_root.items():
            write_atomic(collection_root / name, content)
    finally:
        if staging.exists():
            shutil.rmtree(staging)

    verify_control_tree(control_root, dynamic)
    for name, content in final_root.items():
        if (collection_root / name).read_text(encoding="utf-8") != content:
            raise ControlInitializationError(f"collection root readback failed: {name}")

    return {
        "status": "initialized",
        "collection_root": str(collection_root),
        "control_root": str(control_root),
        "created": planned_files,
        "created_directories": list(CONTROL_DIRECTORIES),
        "finalized_root_files": ["AGENTS.md", "README.md", "MEMBERS.md"],
        "member": member_state,
        "links_created": [],
        "git_roots_created": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("collection_root", type=Path)
    parser.add_argument("--distribution-root", required=True, type=Path)
    parser.add_argument("--control-project", default="skills")
    parser.add_argument("--member-project", default="project-conventions")
    parser.add_argument("--member-repository-root", default="src")
    parser.add_argument("--member-package-source", default="src/project-conventions")
    parser.add_argument("--member-remote", default="obisoldbee/skills")
    parser.add_argument("--member-ref", default="main")
    parser.add_argument("--member-category", default="personal-open")
    parser.add_argument("--apply", action="store_true")
    arguments = parser.parse_args()
    try:
        result = initialize(
            arguments.collection_root,
            arguments.distribution_root,
            arguments.control_project,
            arguments.member_project,
            arguments.member_repository_root,
            arguments.member_package_source,
            arguments.member_remote,
            arguments.member_ref,
            arguments.member_category,
            arguments.apply,
        )
    except (ControlInitializationError, OSError, UnicodeError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
