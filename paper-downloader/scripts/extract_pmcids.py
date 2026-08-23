#!/usr/bin/env python3
"""Export PMCID browser inputs from the canonical manifest without side effects."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from build_browser_followup_inputs import (  # noqa: E402
    DEFAULT_FOLLOWUP_STATUSES,
    pmc_item,
    pmc_followup_required,
    should_follow,
)
from manifest_contract import (  # noqa: E402
    atomic_write_json,
    declared_output_path,
    declared_output_root,
    is_within,
    load_manifest,
    relative_output_path,
    require_distinct_paths,
)


def extract_rows(manifest: dict) -> list[dict]:
    return [
        item
        for row in manifest["rows"]
        if should_follow(row, DEFAULT_FOLLOWUP_STATUSES)
        if pmc_followup_required(row)
        if (item := pmc_item(row)) is not None
    ]


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    args = parser.parse_args()
    root = declared_output_root(args.output_root)
    manifest_path = declared_output_path(args.manifest, root)
    output = declared_output_path(args.output, root)
    require_distinct_paths(manifest=manifest_path, output=output)
    manifest = load_manifest(manifest_path, output_root=root)
    paper_root = declared_output_path(Path(str(manifest.get("paper_root") or "papers")), root)
    if is_within(output, paper_root):
        raise ValueError("extract output must not be inside manifest paper_root")
    rows = extract_rows(manifest)
    receipt = atomic_write_json(output, rows)
    print(json.dumps({"rows": len(rows), "output": {"path": relative_output_path(output, root), **receipt}}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
