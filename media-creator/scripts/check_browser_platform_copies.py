#!/usr/bin/env python3
"""Maintenance-only check of duplicated browser policy; no runtime package dependency."""
import argparse
import hashlib
import json
from pathlib import Path

COPIES = ("media-creator/references/browser-platforms.md",
          "chatgpt-codex-review/references/browser-platforms.md")


def check(repository_root):
    hashes = {}
    for relative in COPIES:
        path = repository_root / relative
        hashes[relative] = hashlib.sha256(path.read_bytes()).hexdigest() if path.is_file() else None
    return {"valid": None not in hashes.values() and len(set(hashes.values())) == 1,
            "sha256": hashes, "scope": "maintenance_only_exact_shared_reference_copies"}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("repository_root", type=Path)
    args = parser.parse_args()
    result = check(args.repository_root)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0 if result["valid"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
