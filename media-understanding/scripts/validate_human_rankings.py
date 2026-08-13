#!/usr/bin/env python3
"""Validate and recompute a 3/2/1 human-ranking export."""

from __future__ import annotations

import argparse
import json
from collections import defaultdict
from pathlib import Path


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("rankings", type=Path)
    parser.add_argument("--expected-cases", type=int)
    args = parser.parse_args()

    with args.rankings.open("r", encoding="utf-8") as handle:
        document = json.load(handle)

    errors: list[str] = []
    allowed_schemas = {
        "akashic-visual-output-review-rankings/v1",
        "visual-model-human-ranking/v1",
    }
    if document.get("schema_version") not in allowed_schemas:
        errors.append("unexpected schema_version")
    case_rankings = document.get("case_rankings")
    if not isinstance(case_rankings, dict):
        errors.append("case_rankings must be an object")
        case_rankings = {}
    if args.expected_cases is not None and len(case_rankings) != args.expected_cases:
        errors.append(
            f"expected {args.expected_cases} case entries, found {len(case_rankings)}"
        )

    stats: dict[str, dict[str, int]] = defaultdict(
        lambda: {"points": 0, "first": 0, "second": 0, "third": 0, "ranked_cases": 0}
    )
    weights = (3, 2, 1)
    labels = ("first", "second", "third")
    completed_cases = 0

    for case_id, ranking in sorted(case_rankings.items()):
        if not isinstance(ranking, list) or len(ranking) > 3:
            errors.append(f"{case_id}: ranking must be an array with at most three IDs")
            continue
        participant_ids: list[str] = []
        for index, item in enumerate(ranking):
            if isinstance(item, str):
                participant_ids.append(item)
            elif isinstance(item, dict):
                participant_ids.append(item.get("participant_id", ""))
                expected_rank = index + 1
                if item.get("rank") not in (None, expected_rank):
                    errors.append(f"{case_id}: rank field does not match array order")
                if item.get("points") not in (None, weights[index]):
                    errors.append(f"{case_id}: points field does not match 3/2/1 scoring")
            else:
                participant_ids.append("")
        if len(participant_ids) != len(set(participant_ids)):
            errors.append(f"{case_id}: duplicate participant IDs")
            continue
        if len(ranking) == 3:
            completed_cases += 1
        for index, participant_id in enumerate(participant_ids):
            if not isinstance(participant_id, str) or not participant_id:
                errors.append(f"{case_id}: invalid participant ID at rank {index + 1}")
                continue
            row = stats[participant_id]
            row["points"] += weights[index]
            row[labels[index]] += 1
            row["ranked_cases"] += 1

    leaderboard = [
        {"participant_id": participant_id, **values}
        for participant_id, values in stats.items()
    ]
    leaderboard.sort(
        key=lambda row: (
            -row["points"],
            -row["first"],
            -row["second"],
            -row["third"],
            row["participant_id"],
        )
    )

    report = {
        "status": "pass" if not errors else "fail",
        "case_entries": len(case_rankings),
        "completed_cases": completed_cases,
        "leaderboard": leaderboard,
        "errors": errors,
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))
    return 0 if not errors else 1


if __name__ == "__main__":
    raise SystemExit(main())
