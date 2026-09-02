#!/usr/bin/env python3
"""Create a runtime-neutral serial/resumable multi-URL evidence plan."""

from __future__ import annotations

import argparse
from pathlib import Path
from urllib.parse import urlparse

from common import ensure_within, file_reference_matches, package_relative, read_json, resolve_declared_path, sha256_file, stable_id, utc_now, write_json
from assess_capture_evidence import validate_persisted_assessment
from intake_case import canonical_url

TERMINAL_STATES = {"captured", "blocked", "failed"}
PASSING_ASSESSMENT_STATES = {"full_body", "full_body_with_media_supplement", "needs_image_supplement"}
SHARED_CAPTURE_PIPELINE = "runtime_browser_or_case_local_html"
LEGACY_BATCH_SCHEMA = "web-bookmark-intelligence/batch/v2"
LEGACY_ADAPTER_ONLY_BLOCKERS = {
    "missing_network_authorization_or_workbuddy_script",
    "missing_network_authorization",
    "missing_workbuddy_script",
    "unrecognized_workbuddy_implementation_hash",
    "executor_does_not_prove_redirect_rebind_protection",
    "executor_does_not_prove_per_hop_dns_revalidation_or_ip_pinning",
}
LEGACY_ATTEMPT_FIELDS = (
    "status",
    "blocked_reason",
    "capture_pipeline",
    "capture_adapter",
    "workbuddy_adapter",
    "capture_mode",
    "capture_receipt",
    "execution_receipt",
    "execution_returncode",
    "network_executed",
    "required_implementation",
    "observed_implementation",
)


def load_urls(values: list[str], url_file: Path | None) -> list[str]:
    collected = [value.strip() for value in values if value.strip()]
    if url_file:
        collected.extend(line.strip() for line in url_file.read_text(encoding="utf-8").splitlines() if line.strip() and not line.lstrip().startswith("#"))
    return collected


def is_legacy_adapter_item(batch_schema: object, item: dict[str, object]) -> bool:
    pipeline = str(item.get("capture_pipeline") or "")
    return (
        batch_schema == LEGACY_BATCH_SCHEMA
        or "workbuddy_adapter" in item
        or pipeline.startswith("workbuddy_")
    )


def is_legacy_adapter_only_blocker(item: dict[str, object]) -> bool:
    reason = item.get("blocked_reason")
    return isinstance(reason, str) and (
        reason in LEGACY_ADAPTER_ONLY_BLOCKERS
        or reason.startswith("implementation_unreadable:")
    )


def previous_legacy_attempt(batch_schema: object, item: dict[str, object]) -> dict[str, object]:
    snapshot = {key: item[key] for key in LEGACY_ATTEMPT_FIELDS if key in item}
    snapshot["batch_schema"] = batch_schema
    return snapshot


def passing_case_assessment(case_dir: Path, item: dict[str, object], root: Path) -> dict[str, object] | None:
    """Return a bound assessment receipt only when it closes the quality gate."""
    assessment_path = case_dir / "evidence-assessment.json"
    if not assessment_path.is_file() or assessment_path.is_symlink():
        return None
    assessment = read_json(assessment_path)
    if not isinstance(assessment, dict):
        return None
    binding = assessment.get("case_binding")
    try:
        declared_root = resolve_declared_path(assessment.get("case_root"), root)
    except (TypeError, ValueError):
        return None
    if (
        assessment.get("schema") != "web-bookmark-intelligence/evidence-assessment/v2"
        or assessment.get("case_id") != item.get("case_id")
        or declared_root != case_dir.resolve()
        or not isinstance(binding, dict)
        or binding.get("valid") is not True
        or assessment.get("page_purpose_ready") is not True
        or assessment.get("final_status") not in PASSING_ASSESSMENT_STATES
    ):
        return None
    intake = assessment.get("intake")
    dom = assessment.get("dom")
    media = assessment.get("media")
    dom_reference = {
        "path": dom.get("capture_path") if isinstance(dom, dict) else None,
        "sha256": dom.get("sha256") if isinstance(dom, dict) else None,
    }
    if not file_reference_matches(intake, root, case_dir) or not file_reference_matches(dom_reference, root, case_dir):
        return None
    if isinstance(media, dict) and media.get("provided") is True and not file_reference_matches(media, root, case_dir):
        return None
    if validate_persisted_assessment(
        assessment_path,
        root,
        case_dir,
        str(item.get("case_id") or ""),
        str(item.get("source_url") or ""),
    ):
        return None
    return {
        "path": package_relative(assessment_path, root),
        "sha256": sha256_file(assessment_path),
        "final_status": assessment.get("final_status"),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--urls", nargs="*", default=[])
    parser.add_argument("--url-file", type=Path)
    parser.add_argument("--profile", choices=["generic", "shoulong"], default="generic")
    parser.add_argument("--package-root", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--state", type=Path)
    args = parser.parse_args()

    urls = load_urls(args.urls, args.url_file)
    if not urls:
        raise SystemExit("provide --urls or --url-file")
    root = args.package_root.resolve()
    out_dir = ensure_within(args.out_dir, root)
    out_dir.mkdir(parents=True, exist_ok=True)
    state_path = ensure_within(args.state or out_dir / "batch-state.json", root)
    prior = read_json(state_path) if state_path.exists() else {"cases": []}
    prior_by_url = {item.get("source_url"): item for item in prior.get("cases", []) if isinstance(item, dict)}
    prior_schema = prior.get("schema")

    cases: list[dict[str, object]] = []
    for raw_url in urls:
        canonical, unsafe_reason = canonical_url(raw_url)
        source_url = canonical or raw_url
        existing = prior_by_url.get(source_url)
        recovered_legacy_attempt: dict[str, object] | None = None
        if existing:
            existing = dict(existing)
            case_dir = out_dir / "cases" / str(existing.get("case_id"))
            prior_status = existing.get("status")
            batch_identity_valid = existing.get("case_id") == stable_id("case", source_url)
            recoverable_legacy_block = (
                prior_status in {"blocked", "needs_compatible_executor"}
                and is_legacy_adapter_item(prior_schema, existing)
                and is_legacy_adapter_only_blocker(existing)
            )
            assessment = (
                passing_case_assessment(case_dir, existing, root)
                if batch_identity_valid and prior_status in {"pending_quality", "captured"}
                else None
            )
            if assessment:
                existing["status"] = "captured"
                existing["quality_assessment"] = assessment
                existing["blocked_reason"] = None
            elif prior_status in {"pending_quality", "captured"}:
                existing["status"] = "pending_quality"
                existing.pop("quality_assessment", None)
                existing["blocked_reason"] = "stale_or_invalid_quality_assessment"
            if recoverable_legacy_block:
                recovered_legacy_attempt = previous_legacy_attempt(prior_schema, existing)
            elif existing.get("status") in TERMINAL_STATES or existing.get("status") in {
                "pending_quality",
                "needs_compatible_executor",
            }:
                cases.append(existing)
                continue
        host = (urlparse(canonical).hostname or "").lower() if canonical else ""
        host_matches = host == "chinalowcarb.com" or host.endswith(".chinalowcarb.com")
        status = "planned"
        blocked_reason = unsafe_reason
        if args.profile == "shoulong" and not host_matches:
            status, blocked_reason = "blocked", "shoulong_profile_host_mismatch"
        elif unsafe_reason:
            status = "blocked"
        planned_case: dict[str, object] = {
            "case_id": stable_id("case", source_url),
            "source_url": source_url,
            "status": status,
            "blocked_reason": blocked_reason,
            "profile": args.profile,
            "capture_pipeline": SHARED_CAPTURE_PIPELINE,
            "capture_adapter": "runtime_selected",
            "capture_mode": "rendered_browser_or_case_local_html",
            "quality_gate": "capture_pipeline.py",
            "media_route_on_text_failure": "media_understanding_then_ocr",
            "continuity_key": stable_id("batch", source_url) if args.profile == "shoulong" else None,
            "quality_assessment_required": True,
        }
        if recovered_legacy_attempt:
            planned_case["previous_legacy_capture_attempt"] = recovered_legacy_attempt
        cases.append(planned_case)

    batch = {
        "schema": "web-bookmark-intelligence/batch/v3",
        "created_at": utc_now(),
        "profile": args.profile,
        "capture_pipeline": SHARED_CAPTURE_PIPELINE,
        "capture_adapter": "runtime_selected",
        "max_workers": 1,
        "resume_policy": "preserve_terminal_states_except_legacy_adapter_only_blockers",
        "capture_completion_gate": "case-bound evidence-assessment/v2 with a passing final_status",
        "formal_write_authorized": False,
        "cases": cases,
    }
    write_json(out_dir / "batch-plan.json", batch, root)
    write_json(state_path, batch, root)
    print(f"cases={len(cases)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
