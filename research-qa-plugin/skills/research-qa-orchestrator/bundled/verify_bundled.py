#!/usr/bin/env python3
"""Create and verify the portable manifest for bundled QA expert Skills."""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import stat


ROOT = Path(__file__).resolve().parent
MANIFEST = ROOT / "source-manifest.json"
EXCLUDED_NAMES = {".DS_Store", ".git", "__pycache__"}
PERSONAS = (
    "Nick Norwitz",
    "Anthony Chaffee",
    "PeterAttia",
    "Dr Eric Berg",
    "Steak and Butter Gal",
    "Dr Stan Ekberg",
    "Dr Robert",
    "ShawnBaker",
)
COMPONENTS = [
    {
        "id": f"persona-{index:02d}",
        "source_scope": "minimax-user-skills",
        "source_name": name,
        "target": f"personas/{name}",
    }
    for index, name in enumerate(PERSONAS, 1)
] + [
    {
        "id": "fuxi-skill",
        "source_scope": "claude-user-skills",
        "source_name": "fuxi-skill",
        "target": "fuxi-skill",
    }
]


def excluded(path: Path) -> bool:
    return any(part in EXCLUDED_NAMES for part in path.parts) or path.suffix == ".pyc"


def link_like(path: Path) -> bool:
    if path.is_symlink():
        return True
    is_junction = getattr(os.path, "isjunction", None)
    if is_junction is not None:
        try:
            return bool(is_junction(path))
        except OSError as exc:
            raise ValueError(f"cannot inspect link boundary: {path}") from exc
    if os.name != "nt":
        return False
    try:
        observed = os.lstat(path)
    except OSError as exc:
        raise ValueError(f"cannot inspect link boundary: {path}") from exc
    return getattr(observed, "st_reparse_tag", None) == getattr(
        stat, "IO_REPARSE_TAG_MOUNT_POINT", 0xA0000003
    )


def inventory(root: Path) -> tuple[dict[str, str], int]:
    if link_like(root):
        raise ValueError(f"symlink is forbidden: {root}")
    if not root.is_dir():
        raise ValueError(f"missing directory: {root}")
    result: dict[str, str] = {}
    total_bytes = 0
    for current, directories, files in os.walk(root, followlinks=False):
        current_path = Path(current)
        kept_directories: list[str] = []
        for name in sorted(directories):
            path = current_path / name
            if link_like(path):
                raise ValueError(f"symlink is forbidden: {path}")
            if name not in EXCLUDED_NAMES:
                kept_directories.append(name)
        directories[:] = kept_directories
        for name in sorted(files):
            path = current_path / name
            relative = path.relative_to(root)
            if excluded(relative):
                continue
            if link_like(path):
                raise ValueError(f"symlink is forbidden: {path}")
            if not path.is_file():
                raise ValueError(f"non-regular payload entry: {path}")
            data = path.read_bytes()
            result[relative.as_posix()] = hashlib.sha256(data).hexdigest()
            total_bytes += len(data)
    return result, total_bytes


def tree_sha256(files: dict[str, str]) -> str:
    digest = hashlib.sha256()
    for relative in sorted(files, key=lambda value: value.encode("utf-8")):
        digest.update(relative.encode("utf-8"))
        digest.update(b"\0")
        digest.update(files[relative].encode("ascii"))
        digest.update(b"\n")
    return digest.hexdigest()


def component_record(component: dict[str, str], root: Path) -> dict[str, object]:
    files, total_bytes = inventory(root)
    skill_sha = files.get("SKILL.md")
    if not skill_sha:
        raise ValueError(f"missing SKILL.md: {root}")
    return {
        **component,
        "file_count": len(files),
        "total_bytes": total_bytes,
        "skill_md_sha256": skill_sha,
        "tree_sha256": tree_sha256(files),
    }


def build_manifest() -> dict[str, object]:
    records = [component_record(component, ROOT / component["target"]) for component in COMPONENTS]
    return {
        "schema": "research-qa-orchestrator/bundled-source-manifest/v1",
        "portable": True,
        "absolute_source_paths_persisted": False,
        "symlinks_allowed": False,
        "payload_excludes": [".DS_Store", ".git", "__pycache__", "*.pyc"],
        "tree_hash_algorithm": "sha256(concat(sorted_utf8(relative_path) + NUL + sha256(content)_hex + LF))",
        "components": records,
    }


def compare_sources(minimax_root: Path, claude_root: Path) -> list[dict[str, object]]:
    comparisons: list[dict[str, object]] = []
    for component in COMPONENTS:
        if component["source_scope"] == "minimax-user-skills":
            source = minimax_root / component["source_name"]
        else:
            source = claude_root / component["source_name"]
        target = ROOT / component["target"]
        source_files, _ = inventory(source)
        target_files, _ = inventory(target)
        source_names = set(source_files)
        target_names = set(target_files)
        mismatches = sorted(
            name for name in source_names & target_names if source_files[name] != target_files[name]
        )
        comparisons.append(
            {
                "id": component["id"],
                "missing": sorted(source_names - target_names),
                "extra": sorted(target_names - source_names),
                "content_mismatch": mismatches,
            }
        )
    return comparisons


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--write-manifest", action="store_true")
    parser.add_argument("--minimax-root", type=Path)
    parser.add_argument("--claude-root", type=Path)
    parser.add_argument(
        "--require-source-match",
        action="store_true",
        help="require both upstream roots and complete byte-for-byte source equality",
    )
    args = parser.parse_args()

    actual = build_manifest()
    if args.write_manifest:
        temporary = MANIFEST.with_suffix(".json.tmp")
        temporary.write_text(json.dumps(actual, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        os.replace(temporary, MANIFEST)

    if not MANIFEST.is_file():
        raise SystemExit("missing source-manifest.json; run with --write-manifest")
    expected = json.loads(MANIFEST.read_text(encoding="utf-8"))
    manifest_ok = expected == actual

    source_comparisons: list[dict[str, object]] = []
    if bool(args.minimax_root) != bool(args.claude_root):
        raise SystemExit("pass both --minimax-root and --claude-root")
    if args.minimax_root and args.claude_root:
        source_comparisons = compare_sources(args.minimax_root, args.claude_root)
        sources_ok: bool | None = all(
            not item["missing"] and not item["extra"] and not item["content_mismatch"]
            for item in source_comparisons
        )
        source_comparison = "matched" if sources_ok else "mismatched"
    else:
        sources_ok = None
        source_comparison = "not_compared"

    strict_roots_missing = args.require_source_match and sources_ok is None
    report = {
        "manifest_ok": manifest_ok,
        "component_count": len(actual["components"]),
        "source_comparison": source_comparison,
        "source_comparisons": source_comparisons,
        "sources_ok": sources_ok,
        "source_match_required": args.require_source_match,
    }
    if strict_roots_missing:
        report["error"] = (
            "--require-source-match requires both --minimax-root and --claude-root"
        )
    print(json.dumps(report, ensure_ascii=False, indent=2))
    comparison_failed = sources_ok is False or strict_roots_missing
    return 0 if manifest_ok and not comparison_failed else 1


if __name__ == "__main__":
    raise SystemExit(main())
