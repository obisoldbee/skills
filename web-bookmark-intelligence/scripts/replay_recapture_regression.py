#!/usr/bin/env python3
"""Verify five retained real-capture receipts offline without rerunning a URL."""

from __future__ import annotations

import argparse
from pathlib import Path

from common import meaningful_char_count, read_json, sha256_file, utc_now, write_json


META_MARKER = "正文取自 meta description"


def mapping(value: object) -> dict[str, object]:
    return value if isinstance(value, dict) else {}


def source_path(source_root: Path, relative: str) -> Path:
    path = (source_root / relative).resolve()
    try:
        path.relative_to(source_root)
    except ValueError as exc:
        raise ValueError(f"fixture source escapes source package: {relative}") from exc
    return path


def receipt_path(value: object, source_root: Path, legacy_package_id: str) -> Path:
    """Bind receipt evidence to the relocated source package without editing history.

    Current relative paths resolve from source_root. Historical absolute paths are
    accepted only when they name the same legacy package immediately below a
    `12-agent-submissions` component; only the suffix after that package id is
    reused. All reads therefore remain inside the current source package.
    """
    source_root = source_root.resolve()
    raw = Path(str(value))
    if not raw.is_absolute():
        return source_path(source_root, str(raw))
    path = raw.resolve()
    try:
        path.relative_to(source_root)
        return path
    except ValueError:
        pass

    parts = raw.parts
    indexes = [
        index
        for index, part in enumerate(parts)
        if part == legacy_package_id and index > 0 and parts[index - 1] == "12-agent-submissions"
    ]
    if source_root.name != legacy_package_id or len(indexes) != 1:
        raise ValueError(f"receipt evidence is outside source package: {path}")
    suffix = parts[indexes[0] + 1 :]
    if not suffix:
        raise ValueError(f"receipt evidence has no package-relative suffix: {path}")
    rebound = (source_root / Path(*suffix)).resolve()
    try:
        rebound.relative_to(source_root)
    except ValueError as exc:
        raise ValueError(f"rebased receipt evidence escapes source package: {path}") from exc
    return rebound


def article_body(markdown: str) -> str:
    return markdown.split("\n---\n", 1)[1] if "\n---\n" in markdown else markdown


def check_case(
    item: dict[str, object],
    source_root: Path,
    expected_workbuddy_hash: str,
    legacy_package_id: str,
) -> dict[str, object]:
    case_id = item["id"]
    failures: list[str] = []
    receipt = mapping(read_json(source_path(source_root, str(item["execution_receipt"]))))
    first = mapping(item["first_execution"])
    source = mapping(receipt.get("source_of_truth"))
    tls = mapping(receipt.get("tls"))
    if receipt.get("execution_kind") != "first_successful_authorized_capture_execution":
        failures.append("execution_receipt_not_first_successful_authorized_capture")
    if receipt.get("replay_or_reexecution") is not False:
        failures.append("execution_receipt_marked_replay_or_reexecution")
    for key in ("observed_completion_at", "mode_duration_seconds", "returncode", "successful_attempt_index"):
        if receipt.get(key) != first.get(key):
            failures.append(f"first_execution_{key}_mismatch")
    if tls.get("verification_disabled") is not False:
        failures.append("tls_verification_disabled")
    expected_prior = bool(first.get("prior_tls_failure_preserved"))
    actual_prior = receipt.get("prior_failed_attempt_preserved")
    if bool(actual_prior) != expected_prior:
        failures.append("prior_tls_failure_presence_mismatch")
    elif actual_prior and not receipt_path(actual_prior, source_root, legacy_package_id).is_file():
        failures.append("prior_tls_failure_artifact_missing")

    stderr_path = receipt_path(source.get("workbuddy_stderr"), source_root, legacy_package_id)
    article_path = receipt_path(source.get("workbuddy_article"), source_root, legacy_package_id)
    if not stderr_path.is_file() or sha256_file(stderr_path) != first.get("stderr_sha256"):
        failures.append("stderr_hash_mismatch_or_missing")
    if not article_path.is_file() or sha256_file(article_path) != first.get("article_sha256"):
        failures.append("article_hash_mismatch_or_missing")
    if source.get("workbuddy_script_sha256") != expected_workbuddy_hash:
        failures.append("workbuddy_script_hash_inconsistent")

    dom = mapping(read_json(source_path(source_root, str(item["dom_evidence_source"]))))
    metrics = mapping(dom.get("article_metrics"))
    expected_dom = mapping(item["expected_dom"])
    if metrics.get("body_meaningful_chars") != expected_dom.get("meaningful_chars"):
        failures.append("dom_meaningful_char_count_mismatch")
    if metrics.get("image_count") != expected_dom.get("image_count"):
        failures.append("dom_image_count_mismatch")
    if metrics.get("has_meta_description_marker") != expected_dom.get("meta_description_marker"):
        failures.append("meta_description_marker_mismatch")
    markdown = article_path.read_text(encoding="utf-8", errors="replace") if article_path.is_file() else ""
    if META_MARKER in markdown:
        failures.append("meta_description_body_marker_present")
    preview = str(metrics.get("body_preview") or "")
    is_noise = meaningful_char_count(preview) < 120 and "-" in preview
    if is_noise != expected_dom.get("noise_or_placeholder"):
        failures.append("placeholder_noise_boundary_mismatch")

    final = mapping(read_json(source_path(source_root, str(item["final_status_source"]))))
    final_status = final.get("actual_status")
    if final_status != item.get("expected_final_status"):
        failures.append("final_status_mismatch")
    final_role = final.get("artifact_role")
    if final_role and final_role != "reconciliation_only_not_execution_receipt":
        failures.append("unexpected_final_reconciliation_role")

    media_summary: dict[str, object] | None = None
    if item.get("media_result"):
        media = mapping(read_json(source_path(source_root, str(item["media_result"]))))
        expected_media = mapping(item["expected_media"])
        media_source = mapping(media.get("source"))
        if media.get("status") != expected_media.get("status"):
            failures.append("media_status_mismatch")
        if media_source.get("image_count_sent_to_ocr") != expected_media.get("images_sent_to_ocr"):
            failures.append("media_ocr_image_count_mismatch")
        if media_source.get("tracking_pixels_retained_but_not_sent") != expected_media.get("tracking_pixels_not_sent"):
            failures.append("media_tracking_pixel_count_mismatch")
        image_evidence = [mapping(value) for value in item.get("image_level_evidence", []) if isinstance(value, dict)]
        for proof in image_evidence:
            proof_path = source_path(source_root, str(proof.get("path")))
            if not proof_path.is_file() or sha256_file(proof_path) != proof.get("sha256"):
                failures.append("image_level_evidence_hash_mismatch_or_missing")
                continue
            phrase = str(proof.get("required_phrase") or "")
            if phrase and phrase not in proof_path.read_text(encoding="utf-8", errors="replace"):
                failures.append("image_level_evidence_phrase_missing")
        media_summary = {
            "status": media.get("status"),
            "images_sent_to_ocr": media_source.get("image_count_sent_to_ocr"),
            "tracking_pixels_not_sent": media_source.get("tracking_pixels_retained_but_not_sent"),
            "image_level_evidence_count": len(image_evidence),
        }

    return {
        "id": case_id,
        "status": "passed" if not failures else "failed",
        "expected_final_status": item.get("expected_final_status"),
        "actual_final_status": final_status,
        "first_execution": {
            "observed_completion_at": receipt.get("observed_completion_at"),
            "mode_duration_seconds": receipt.get("mode_duration_seconds"),
            "returncode": receipt.get("returncode"),
            "successful_attempt_index": receipt.get("successful_attempt_index"),
            "prior_tls_failure_preserved": bool(actual_prior),
            "tls_verification_disabled": tls.get("verification_disabled"),
        },
        "dom": {
            "meaningful_chars": metrics.get("body_meaningful_chars"),
            "image_count": metrics.get("image_count"),
            "meta_description_marker": metrics.get("has_meta_description_marker"),
            "noise_or_placeholder": is_noise,
        },
        "media": media_summary,
        "reconciliation_used_only_for_final_state": final_role == "reconciliation_only_not_execution_receipt",
        "failures": failures,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--fixture", type=Path, default=Path(__file__).resolve().parents[1] / "fixtures" / "recapture-regression.json")
    parser.add_argument("--vault-root", type=Path, required=True)
    parser.add_argument("--package-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    args = parser.parse_args()

    fixture = mapping(read_json(args.fixture))
    cases = [mapping(item) for item in fixture.get("cases", []) if isinstance(item, dict)]
    ids = {item.get("id") for item in cases}
    if len(cases) != 5 or ids != {2, 5, 8, 14, 15}:
        raise SystemExit("fixture must contain exactly real-capture ids 2, 5, 8, 14, 15")
    source_root = source_path(args.vault_root.resolve(), str(fixture["source_package"]))
    binding = mapping(fixture.get("receipt_path_binding"))
    if binding.get("mode") != "source_package_relative_with_legacy_package_id_rebase":
        raise SystemExit("fixture must declare the source-package-relative legacy receipt binding")
    legacy_package_id = str(binding.get("legacy_package_id") or "")
    if not legacy_package_id or legacy_package_id != source_root.name:
        raise SystemExit("fixture legacy package id must match the resolved source package")
    expected_workbuddy_hash = str(mapping(fixture.get("workbuddy")).get("script_sha256") or "")
    results = [check_case(item, source_root, expected_workbuddy_hash, legacy_package_id) for item in cases]
    report = {
        "schema": "web-bookmark-intelligence/recapture-regression-report/v1",
        "created_at": utc_now(),
        "offline_only": True,
        "network_calls": 0,
        "fixture": str(args.fixture),
        "source_package": fixture["source_package"],
        "receipt_path_binding": binding,
        "source_execution_receipt_used": fixture["source_execution_receipts"],
        "reconciliation_not_used_as_execution_receipt": True,
        "total_cases": len(results),
        "passed_cases": sum(1 for result in results if result["status"] == "passed"),
        "failed_cases": sum(1 for result in results if result["status"] != "passed"),
        "results": results,
    }
    write_json(args.out, report, args.package_root.resolve())
    print(f"passed={report['passed_cases']} failed={report['failed_cases']}")
    return 0 if report["failed_cases"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
