#!/usr/bin/env python3
"""Replay the immutable 15-page archive as an offline quality-gate regression test."""

from __future__ import annotations

import argparse
from pathlib import Path

from common import meaningful_char_count, read_json, utc_now, write_json

META_MARKER = "正文取自 meta description"


def body(markdown: str) -> str:
    return markdown.split("\n---\n", 1)[1] if "\n---\n" in markdown else markdown


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, default=Path(__file__).resolve().parents[1] / "fixtures" / "historical-15.json")
    parser.add_argument("--vault-root", type=Path, required=True)
    parser.add_argument("--package-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    fixture = read_json(args.fixture)
    cases = fixture.get("cases", []) if isinstance(fixture, dict) else []
    if len(cases) != 15 or {item.get("id") for item in cases if isinstance(item, dict)} != set(range(1, 16)):
        raise SystemExit("fixture must contain exactly ids 1..15")
    archive_root = args.vault_root.resolve() / str(fixture["archive_root"])
    results: list[dict[str, object]] = []
    for item in cases:
        article = archive_root / str(item["relative_article"])
        result: dict[str, object] = {"id": item["id"], "title": item["title"], "article": str(article), "expected_route": item["expected_route"]}
        if not article.is_file():
            result.update(status="failed", reason="missing_historical_article")
            results.append(result)
            continue
        markdown = article.read_text(encoding="utf-8", errors="replace")
        text = body(markdown)
        count = meaningful_char_count(text)
        has_marker = META_MARKER in markdown
        expects_marker = bool(item["expects_meta_description_marker"])
        minimum = int(item["minimum_meaningful_chars"])
        passed = count >= minimum and has_marker == expects_marker
        if expects_marker and item["expected_route"] == "playwright_then_media_ocr":
            reason = "requires_media_ocr_not_body_pass" if passed else "missing_meta_boundary_or_content"
        elif expects_marker:
            reason = "capture_evidence_conflict_requires_recapture_not_body_pass" if passed else "missing_meta_boundary_or_content"
        else:
            reason = "dom_baseline_preserved" if passed else "description_marker_or_short_body"
        result.update(status="passed" if passed else "failed", meaningful_chars=count, has_meta_description_marker=has_marker, reason=reason)
        results.append(result)
    report = {
        "schema": "web-bookmark-intelligence/historical-replay/v1",
        "created_at": utc_now(),
        "fixture": str(args.fixture),
        "offline_only": True,
        "total_cases": len(results),
        "passed_cases": sum(1 for item in results if item["status"] == "passed"),
        "failed_cases": sum(1 for item in results if item["status"] != "passed"),
        "global_assertion": "No case with the historical meta-description marker is a body-pass baseline.",
        "results": results,
    }
    write_json(args.out, report, args.package_root.resolve())
    print(f"passed={report['passed_cases']} failed={report['failed_cases']}")
    return 0 if report["failed_cases"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
