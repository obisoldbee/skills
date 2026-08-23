#!/usr/bin/env python3
"""Produce deterministic, user-gated action-card scaffolding from supplied evidence."""

from __future__ import annotations

import argparse
from pathlib import Path

from common import ensure_within, file_reference_matches, package_relative, read_json, resolve_declared_path, sha256_file, utc_now, write_json
from assess_capture_evidence import validate_persisted_assessment


CURRENT_AUTHORITIES = {"formal_current", "formal_verified_event"}
ACTIONABLE_CAPTURE_STATES = {"full_body", "full_body_with_media_supplement", "needs_image_supplement"}


def list_from_payload(payload: object, key: str) -> list[dict[str, object]]:
    if isinstance(payload, list):
        return [item for item in payload if isinstance(item, dict)]
    if isinstance(payload, dict):
        value = payload.get(key, [])
        return [item for item in value if isinstance(item, dict)] if isinstance(value, list) else []
    return []


def repository_name(unit: dict[str, object]) -> str | None:
    for key in ("repository", "repo", "repo_id"):
        value = unit.get(key)
        if isinstance(value, str) and value:
            return value.removeprefix("github:")
    return None


def same_declared_path(value: object, expected: Path, package_root: Path) -> bool:
    try:
        return resolve_declared_path(value, package_root) == expected.resolve()
    except (TypeError, ValueError):
        return False


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--case", type=Path, required=True)
    parser.add_argument("--capture", type=Path, required=True)
    parser.add_argument("--purpose", type=Path)
    parser.add_argument("--content-units", type=Path)
    parser.add_argument("--context", type=Path)
    parser.add_argument("--repos", type=Path)
    parser.add_argument("--package-root", type=Path, required=True)
    parser.add_argument("--case-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    root = args.package_root.resolve()
    case_root = ensure_within(args.case_root, root)
    case_path = ensure_within(args.case, case_root)
    capture_path = ensure_within(args.capture, case_root)
    purpose_path = ensure_within(args.purpose, case_root) if args.purpose else None
    units_path = ensure_within(args.content_units, case_root) if args.content_units else None
    context_path = ensure_within(args.context, case_root) if args.context else None
    repos_path = ensure_within(args.repos, case_root) if args.repos else None
    out_path = ensure_within(args.out, case_root)
    case = read_json(case_path)
    capture = read_json(capture_path)
    purpose = read_json(purpose_path) if purpose_path else {}
    units_payload = read_json(units_path) if units_path else {}
    units = list_from_payload(units_payload, "content_units")
    snapshot = read_json(context_path) if context_path else {}
    contexts = list_from_payload(snapshot, "records")
    permitted_contexts = [
        item
        for item in contexts
        if item.get("authority_class") in CURRENT_AUTHORITIES and item.get("allowed_use") != "blocked"
    ]
    repos = list_from_payload(read_json(repos_path), "repositories") if repos_path else []
    repo_by_name = {
        str(item.get("repository") or item.get("repo_id", "")).removeprefix("github:"): item
        for item in repos
        if item.get("repository") or item.get("repo_id")
    }

    case_mapping = case if isinstance(case, dict) else {}
    capture_mapping = capture if isinstance(capture, dict) else {}
    purpose_mapping = purpose if isinstance(purpose, dict) else {}
    capture_binding = capture_mapping.get("case_binding") if isinstance(capture_mapping.get("case_binding"), dict) else {}
    try:
        case_declared_root = resolve_declared_path(case_mapping.get("case_root"), root)
        capture_declared_root = resolve_declared_path(capture_mapping.get("case_root"), root)
        purpose_declared_root = resolve_declared_path(purpose_mapping.get("case_root"), root) if purpose_path else None
    except (TypeError, ValueError):
        case_declared_root = capture_declared_root = purpose_declared_root = None
    case_id = case_mapping.get("case_id")
    capture_status = capture_mapping.get("final_status")
    action_gate_failures: list[str] = []
    if case_mapping.get("schema") != "web-bookmark-intelligence/intake/v2" or capture_mapping.get("schema") != "web-bookmark-intelligence/evidence-assessment/v2":
        action_gate_failures.append("case_or_assessment_schema_mismatch")
    if not case_id or capture_mapping.get("case_id") != case_id or (purpose_path and purpose_mapping.get("case_id") != case_id):
        action_gate_failures.append("case_id_mismatch")
    if case_declared_root != case_root or capture_declared_root != case_root or (purpose_path and purpose_declared_root != case_root):
        action_gate_failures.append("case_root_mismatch")
    if capture_binding.get("valid") is not True:
        action_gate_failures.append("capture_case_binding_not_valid")
    if capture_status not in ACTIONABLE_CAPTURE_STATES or capture_mapping.get("page_purpose_ready") is not True:
        action_gate_failures.append("capture_evidence_not_actionable")
    capture_dom = capture_mapping.get("dom") if isinstance(capture_mapping.get("dom"), dict) else {}
    capture_dom_reference = {"path": capture_dom.get("capture_path"), "sha256": capture_dom.get("sha256")}
    capture_media = capture_mapping.get("media") if isinstance(capture_mapping.get("media"), dict) else {}
    if not file_reference_matches(capture_mapping.get("intake"), root, case_root) or not file_reference_matches(capture_dom_reference, root, case_root):
        action_gate_failures.append("capture_evidence_file_binding_mismatch")
    if capture_media.get("provided") is True and not file_reference_matches(capture_media, root, case_root):
        action_gate_failures.append("capture_media_file_binding_mismatch")
    if validate_persisted_assessment(
        capture_path,
        root,
        case_root,
        str(case_id or ""),
    ):
        action_gate_failures.append("capture_live_evidence_revalidation_failed")
    if not purpose_path or purpose_mapping.get("page_purpose_status") != "ready_for_semantic_interpretation" or purpose_mapping.get("case_binding_valid") is not True:
        action_gate_failures.append("page_purpose_not_ready")
    if purpose_mapping.get("schema") != "web-bookmark-intelligence/page-purpose-request/v2":
        action_gate_failures.append("page_purpose_schema_mismatch")
    purpose_evidence = purpose_mapping.get("evidence_assessment") if isinstance(purpose_mapping.get("evidence_assessment"), dict) else {}
    if not same_declared_path(purpose_evidence.get("path"), capture_path, root) or purpose_evidence.get("sha256") != sha256_file(capture_path):
        action_gate_failures.append("page_purpose_assessment_binding_mismatch")
    units_mapping = units_payload if isinstance(units_payload, dict) else {}
    units_evidence = units_mapping.get("evidence_assessment") if isinstance(units_mapping.get("evidence_assessment"), dict) else {}
    try:
        units_declared_root = resolve_declared_path(units_mapping.get("case_root"), root)
    except (TypeError, ValueError):
        units_declared_root = None
    if units_path and (
        units_mapping.get("schema") != "web-bookmark-intelligence/content-units/v2"
        or units_mapping.get("case_id") != case_id
        or units_declared_root != case_root
        or not same_declared_path(units_evidence.get("path"), capture_path, root)
        or units_evidence.get("sha256") != sha256_file(capture_path)
    ):
        action_gate_failures.append("content_units_assessment_binding_mismatch")

    action_cards: list[dict[str, object]] = []
    eligible_units = units if not action_gate_failures else []
    for index, unit in enumerate(eligible_units, 1):
        name = repository_name(unit)
        matched_repo = repo_by_name.get(name) if name else None
        freshness = matched_repo.get("freshness_state", "unknown") if matched_repo else "unknown"
        recommendation = "research_refresh" if name and freshness in {"unknown", "aging", "stale"} else "catalog_only"
        action_cards.append(
            {
                "action_id": unit.get("unit_id") or f"action-{index}",
                "content_unit_id": unit.get("unit_id"),
                "recommendation": recommendation,
                "reason": "repository_metrics_or_current_decision_need_refresh" if recommendation == "research_refresh" else "candidate_requires_human_review",
                "same_as_existing": [matched_repo.get("repo_id")] if matched_repo else [],
                "new_vs_existing": "requires_semantic_review",
                "matched_context_ids": [item.get("record_id") or item.get("affair_id") for item in permitted_contexts],
                "matched_repo_ids": [matched_repo.get("repo_id")] if matched_repo else [],
                "evidence_refs": unit.get("evidence_refs", []),
                "freshness_state": freshness,
                "user_decision_required": True,
                "formal_write_authorized": False,
                "adoption_authorized": False,
            }
        )

    result = {
        "schema": "web-bookmark-intelligence/action-cards/v2",
        "created_at": utc_now(),
        "case_id": case_id,
        "case_root": package_relative(case_root, root),
        "capture_status": capture_status,
        "page_purpose": purpose_mapping.get("page_purpose_status", "requires_evidence_backed_semantic_interpretation"),
        "page_purpose_request_used": bool(args.purpose),
        "action_card_status": "ready_for_user_decision" if not action_gate_failures else "blocked_evidence_gate",
        "action_gate_failures": action_gate_failures,
        "context_status": "provided" if permitted_contexts else "context_insufficient",
        "context_records_used": [item.get("record_id") or item.get("affair_id") for item in permitted_contexts],
        "github_snapshots": repos,
        "action_cards": action_cards,
        "uncertainties": [
            "No semantic conclusion is generated by this deterministic scaffold.",
            "Repository stars/forks/watchers and updated_at remain source snapshots, not live values.",
        ],
        "formal_write_authorized": False,
        "install_authorized": False,
        "adoption_authorized": False,
    }
    write_json(out_path, result, root)
    print(f"action_cards={len(action_cards)}")
    return 0 if not action_gate_failures else 1


if __name__ == "__main__":
    raise SystemExit(main())
