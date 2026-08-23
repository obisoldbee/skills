#!/usr/bin/env python3
"""Prepare a bounded semantic handoff from fused evidence without calling a provider."""

from __future__ import annotations

import argparse
from pathlib import Path

from common import ensure_within, file_reference_matches, package_relative, read_json, resolve_declared_path, sha256_file, utc_now, write_json


def mapping(value: object) -> dict[str, object]:
    return value if isinstance(value, dict) else {}


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", type=Path, required=True)
    parser.add_argument("--evidence", type=Path, required=True)
    parser.add_argument("--package-root", type=Path, required=True)
    parser.add_argument("--case-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    root = args.package_root.resolve()
    case_root = ensure_within(args.case_root, root)
    case_path = ensure_within(args.case, case_root)
    evidence_path = ensure_within(args.evidence, case_root)
    out_path = ensure_within(args.out, case_root)
    case = mapping(read_json(case_path))
    evidence = mapping(read_json(evidence_path))
    final_status = str(evidence.get("final_status") or "failed")
    binding = mapping(evidence.get("case_binding"))
    try:
        case_declared_root = resolve_declared_path(case.get("case_root"), root)
        evidence_declared_root = resolve_declared_path(evidence.get("case_root"), root)
    except (TypeError, ValueError):
        case_declared_root = evidence_declared_root = None
    evidence_dom = mapping(evidence.get("dom"))
    dom_reference = {"path": evidence_dom.get("capture_path"), "sha256": evidence_dom.get("sha256")}
    evidence_media = mapping(evidence.get("media"))
    file_binding_valid = (
        file_reference_matches(evidence.get("intake"), root, case_root)
        and file_reference_matches(dom_reference, root, case_root)
        and (evidence_media.get("provided") is not True or file_reference_matches(evidence_media, root, case_root))
    )
    same_case = (
        bool(case.get("case_id"))
        and case.get("schema") == "web-bookmark-intelligence/intake/v2"
        and evidence.get("schema") == "web-bookmark-intelligence/evidence-assessment/v2"
        and case.get("case_id") == evidence.get("case_id")
        and case_declared_root == case_root
        and evidence_declared_root == case_root
        and binding.get("valid") is True
        and file_binding_valid
    )
    ready = final_status != "failed" and bool(evidence.get("page_purpose_ready")) and same_case
    result = {
        "schema": "web-bookmark-intelligence/page-purpose-request/v2",
        "created_at": utc_now(),
        "case_id": case.get("case_id"),
        "case_root": package_relative(case_root, root),
        "input_kind": case.get("input_kind"),
        "source_locator": case.get("source_locator"),
        "case_binding_valid": same_case,
        "evidence_assessment": {
            "path": package_relative(evidence_path, root),
            "sha256": sha256_file(evidence_path),
            "final_status": final_status,
        },
        "page_purpose_status": "ready_for_semantic_interpretation" if ready else "blocked_insufficient_evidence",
        "required_evidence_classes": ["dom_body_or_ocr", "media_when_claims_depend_on_media", "permitted_context_for_comparison"],
        "semantic_provider_called": False,
        "allowed_conclusion": "candidate page-purpose notes only; no adoption, installation, or formal writeback",
        "formal_write_authorized": False,
        "adoption_authorized": False,
    }
    write_json(out_path, result, root)
    print(result["page_purpose_status"])
    return 0 if ready else 1


if __name__ == "__main__":
    raise SystemExit(main())
