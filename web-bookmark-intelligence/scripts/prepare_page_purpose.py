#!/usr/bin/env python3
"""Prepare a bounded semantic handoff from fused evidence without calling a provider."""

from __future__ import annotations

import argparse
from pathlib import Path

from common import read_json, sha256_file, utc_now, write_json


def mapping(value: object) -> dict[str, object]:
    return value if isinstance(value, dict) else {}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--package-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    case = mapping(read_json(args.case))
    evidence = mapping(read_json(args.evidence))
    final_status = str(evidence.get("final_status") or "failed")
    ready = final_status != "failed" and bool(evidence.get("page_purpose_ready"))
    result = {
        "schema": "web-bookmark-intelligence/page-purpose-request/v1",
        "created_at": utc_now(),
        "case_id": case.get("case_id"),
        "input_kind": case.get("input_kind"),
        "source_locator": case.get("source_locator"),
        "evidence_assessment": {"path": str(args.evidence), "sha256": sha256_file(args.evidence), "final_status": final_status},
        "page_purpose_status": "ready_for_semantic_interpretation" if ready else "blocked_insufficient_evidence",
        "required_evidence_classes": ["dom_body_or_ocr", "media_when_claims_depend_on_media", "permitted_context_for_comparison"],
        "semantic_provider_called": False,
        "allowed_conclusion": "candidate page-purpose notes only; no adoption, installation, or formal writeback",
        "formal_write_authorized": False,
        "adoption_authorized": False,
    }
    write_json(args.out, result, args.package_root.resolve())
    print(result["page_purpose_status"])
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
