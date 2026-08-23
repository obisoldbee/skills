#!/usr/bin/env python3
"""Create a serial/resumable multi-URL plan on the same WorkBuddy capture pipeline."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path
from urllib.parse import urlparse

from common import ensure_within, file_reference_matches, package_relative, read_json, resolve_declared_path, sha256_file, stable_id, utc_now, write_json
from assess_capture_evidence import validate_persisted_assessment
from intake_case import canonical_url

TERMINAL_STATES = {"captured", "blocked", "failed"}
PASSING_ASSESSMENT_STATES = {"full_body", "full_body_with_media_supplement", "needs_image_supplement"}
SHARED_CAPTURE_PIPELINE = "workbuddy_shared_pending_quality"
WORKBUDDY_ADAPTER = "workbuddy_wechat_article_archive"


def load_urls(values: list[str], url_file: Path | None) -> list[str]:
    collected = [value.strip() for value in values if value.strip()]
    if url_file:
        collected.extend(line.strip() for line in url_file.read_text(encoding="utf-8").splitlines() if line.strip() and not line.lstrip().startswith("#"))
    return collected


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
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--network-authorized", action="store_true")
    parser.add_argument("--workbuddy-script", type=Path)
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

    cases: list[dict[str, object]] = []
    for raw_url in urls:
        canonical, unsafe_reason = canonical_url(raw_url)
        source_url = canonical or raw_url
        existing = prior_by_url.get(source_url)
        if existing:
            existing = dict(existing)
            case_dir = out_dir / "cases" / str(existing.get("case_id"))
            prior_status = existing.get("status")
            batch_identity_valid = existing.get("case_id") == stable_id("case", source_url)
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
            if existing.get("status") in TERMINAL_STATES or existing.get("status") == "pending_quality":
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
        cases.append(
            {
                "case_id": stable_id("case", source_url),
                "source_url": source_url,
                "status": status,
                "blocked_reason": blocked_reason,
                "profile": args.profile,
                "capture_pipeline": SHARED_CAPTURE_PIPELINE,
                "workbuddy_adapter": WORKBUDDY_ADAPTER,
                "capture_mode": "playwright",
                "quality_gate": "capture_pipeline.py",
                "media_route_on_text_failure": "media_understanding_then_ocr",
                "continuity_key": stable_id("batch", source_url) if args.profile == "shoulong" else None,
                "quality_assessment_required": True,
            }
        )

    execution_blocked = args.execute and (not args.network_authorized or not args.workbuddy_script)
    if args.execute and not execution_blocked:
        wrapper = Path(__file__).with_name("run_workbuddy_capture.py")
        for item in cases:
            if item["status"] != "planned":
                continue
            case_dir = out_dir / "cases" / str(item["case_id"])
            command = [
                sys.executable,
                str(wrapper),
                "--url",
                str(item["source_url"]),
                "--package-root",
                str(root),
                "--out-dir",
                str(case_dir),
                "--execute",
                "--network-authorized",
                "--workbuddy-script",
                str(args.workbuddy_script.resolve()),
            ]
            completed = subprocess.run(command, capture_output=True, text=True, check=False)
            receipt_path = case_dir / "capture-execution-receipt.json"
            receipt = read_json(receipt_path) if receipt_path.is_file() else {}
            receipt_status = receipt.get("status") if isinstance(receipt, dict) else None
            if completed.returncode == 0 and receipt_status == "captured_pending_quality_gate":
                item["status"] = "pending_quality"
                item["blocked_reason"] = None
            elif receipt_status == "needs_compatible_executor":
                item["status"] = "blocked"
                item["blocked_reason"] = receipt.get("blocked_reason")
            else:
                item["status"] = "failed"
                item["blocked_reason"] = receipt.get("blocked_reason") if isinstance(receipt, dict) else "capture_execution_failed"
            item["execution_returncode"] = completed.returncode
            if receipt_path.is_file():
                item["capture_receipt"] = {
                    "path": package_relative(receipt_path, root),
                    "sha256": sha256_file(receipt_path),
                }
    elif execution_blocked:
        for item in cases:
            if item["status"] == "planned":
                item["status"] = "blocked"
                item["blocked_reason"] = "missing_network_authorization_or_workbuddy_script"

    batch = {
        "schema": "web-bookmark-intelligence/batch/v2",
        "created_at": utc_now(),
        "profile": args.profile,
        "capture_pipeline": SHARED_CAPTURE_PIPELINE,
        "workbuddy_adapter": WORKBUDDY_ADAPTER,
        "max_workers": 1,
        "resume_policy": "preserve_terminal_states",
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
