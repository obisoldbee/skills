#!/usr/bin/env python3
"""Validate manifest/result coverage for a visual model benchmark."""

from __future__ import annotations

import argparse
import json
from pathlib import Path


ALLOWED_STATUS = {"success", "failed", "not_run"}


def load_json(path: Path) -> dict:
    with path.open("r", encoding="utf-8") as handle:
        value = json.load(handle)
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return value


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    parser.add_argument("results", type=Path)
    parser.add_argument("--allow-incomplete", action="store_true")
    args = parser.parse_args()

    manifest = load_json(args.manifest)
    results_doc = load_json(args.results)
    cases = {item["case_id"] for item in manifest.get("cases", [])}
    participants = {item["participant_id"] for item in manifest.get("participants", [])}
    expected = {(participant, case) for participant in participants for case in cases}

    errors: list[str] = []
    seen: set[tuple[str, str]] = set()
    status_counts = {status: 0 for status in sorted(ALLOWED_STATUS)}

    for index, item in enumerate(results_doc.get("results", [])):
        key = (item.get("participant_id"), item.get("case_id"))
        if key in seen:
            errors.append(f"duplicate result at index {index}: {key}")
        seen.add(key)
        if key not in expected:
            errors.append(f"unknown participant-case pair: {key}")
        status = item.get("status")
        if status not in ALLOWED_STATUS:
            errors.append(f"invalid status for {key}: {status!r}")
            continue
        status_counts[status] += 1
        if status == "success" and not str(item.get("output_text", "")).strip():
            errors.append(f"successful result has empty output_text: {key}")
        if status == "failed" and not str(item.get("failure_type", "")).strip():
            errors.append(f"failed result has no failure_type: {key}")

    missing = sorted(expected - seen)
    if missing and not args.allow_incomplete:
        errors.append(f"missing {len(missing)} participant-case pairs")

    report = {
        "status": "pass" if not errors else "fail",
        "expected_pairs": len(expected),
        "seen_pairs": len(seen),
        "missing_pairs": len(missing),
        "status_counts": status_counts,
        "errors": errors,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
