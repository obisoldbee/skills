#!/usr/bin/env python3
"""Build a root-only update overlay for the public Skill repository."""

from __future__ import annotations

import argparse
import hashlib
import json
import shutil
import tempfile
from pathlib import Path


CONTROL_ROOT = Path(__file__).resolve().parents[2]
PUBLIC_ROOT_SOURCE = CONTROL_ROOT / "src" / "public-repo"
RELEASE_ROOT = CONTROL_ROOT / "release"
DEFAULT_OUTPUT = RELEASE_ROOT / "public-root-overlay"
ROOT_MANIFEST = "ROOT-MANIFEST.sha256"
ROOT_MANAGED_ENTRIES = {
    ".gitattributes",
    ".github",
    ".gitignore",
    "AGENTS.md",
    "README.md",
    "config",
    "scripts",
}
FORBIDDEN_NAMES = {".DS_Store", "__pycache__"}
FORBIDDEN_SUFFIXES = {".pyc", ".pyo"}
FORBIDDEN_MARKERS = {
    b"/" + b"Users/": "personal-macos-path",
    b"C:" + b"\\Users\\": "personal-windows-path",
    b"file" + b"://": "local-file-uri",
    b"192.168.": "private-network-address",
    b"BEGIN OPENSSH PRIVATE KEY": "private-key",
    b"id_ed25519": "private-key-name",
}


class BuildError(RuntimeError):
    """Raised when the root overlay cannot be built safely."""


def validate_root_scope(root: Path) -> list[str]:
    violations: list[str] = []
    for entry in sorted(root.iterdir()):
        if entry.name not in ROOT_MANAGED_ENTRIES and entry.name != ROOT_MANIFEST:
            violations.append(f"unmanaged-top-level-entry:{entry.name}")
    return violations


def validate_tree(root: Path, label: str) -> list[str]:
    violations: list[str] = []
    for path in sorted(root.rglob("*")):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            violations.append(f"{label}:{relative}:symlink")
            continue
        if path.name in FORBIDDEN_NAMES or path.suffix in FORBIDDEN_SUFFIXES:
            violations.append(f"{label}:{relative}:transient")
            continue
        if not path.is_file():
            continue
        data = path.read_bytes()
        for marker, rule in FORBIDDEN_MARKERS.items():
            if marker in data:
                violations.append(f"{label}:{relative}:{rule}")
    return violations


def build(output: Path) -> dict[str, object]:
    if not PUBLIC_ROOT_SOURCE.is_dir():
        raise BuildError(f"public root source is missing: {PUBLIC_ROOT_SOURCE}")

    source_violations = validate_root_scope(PUBLIC_ROOT_SOURCE)
    source_violations.extend(validate_tree(PUBLIC_ROOT_SOURCE, "public-root-source"))
    if source_violations:
        raise BuildError("public root source violations:\n" + "\n".join(source_violations))

    if RELEASE_ROOT.is_symlink():
        raise BuildError(f"release root must not be a symlink: {RELEASE_ROOT}")
    release_root = RELEASE_ROOT.resolve()
    output = output.expanduser().resolve()
    try:
        relative_output = output.relative_to(release_root)
    except ValueError as exc:
        raise BuildError(f"output must stay under release root: {release_root}") from exc
    if not relative_output.parts:
        raise BuildError(f"output must be a child of release root: {release_root}")
    if output in {CONTROL_ROOT.resolve(), PUBLIC_ROOT_SOURCE.resolve()}:
        raise BuildError(f"refusing protected output: {output}")
    if output.exists() or output.is_symlink():
        raise BuildError(f"output already exists: {output}")

    output.parent.mkdir(parents=True, exist_ok=True)
    temporary = Path(
        tempfile.mkdtemp(prefix=f".{output.name}.build-", dir=str(output.parent))
    )
    try:
        shutil.copytree(
            PUBLIC_ROOT_SOURCE,
            temporary,
            dirs_exist_ok=True,
            copy_function=shutil.copy2,
        )
        for script in (temporary / "scripts").glob("*"):
            if script.is_file():
                script.chmod(script.stat().st_mode | 0o111)

        candidate_violations = validate_root_scope(temporary)
        candidate_violations.extend(validate_tree(temporary, "root-overlay"))
        if candidate_violations:
            raise BuildError("root overlay violations:\n" + "\n".join(candidate_violations))

        manifest_entries: list[tuple[str, str]] = []
        for path in sorted(temporary.rglob("*")):
            if not path.is_file() or path.name == ROOT_MANIFEST:
                continue
            relative = path.relative_to(temporary).as_posix()
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            manifest_entries.append((relative, digest))
        manifest = "".join(
            f"{digest}  {relative}\n" for relative, digest in manifest_entries
        )
        (temporary / ROOT_MANIFEST).write_text(manifest, encoding="utf-8")
        temporary.rename(output)
    except Exception:
        if temporary.exists():
            shutil.rmtree(temporary)
        raise

    return {
        "status": "root_overlay_built",
        "scope": "repository-root-only",
        "output": str(output),
        "files": len(manifest_entries) + 1,
        "manifest_entries": len(manifest_entries),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        type=Path,
        default=DEFAULT_OUTPUT,
        help="new root-only output directory; it must not already exist",
    )
    arguments = parser.parse_args()
    try:
        result = build(arguments.output)
    except BuildError as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
