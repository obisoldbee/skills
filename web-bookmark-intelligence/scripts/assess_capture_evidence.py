#!/usr/bin/env python3
"""Fuse case-bound DOM and media evidence into one conservative final state."""

from __future__ import annotations

import argparse
from pathlib import Path

from common import (
    ensure_within,
    package_relative,
    read_json,
    resolve_declared_path,
    sha256_file,
    utc_now,
    write_json,
)
from capture_pipeline import decide_gate, dom_media_inventory


MEDIA_SUCCESS_STATES = {"completed", "success", "succeeded", "available"}
MEDIA_RESULT_KINDS = {"ocr", "visual"}
MEDIA_INVENTORY_CLASSES = {
    "claim_bearing",
    "non_claim_content",
    "cover_or_ui",
    "tracking",
    "unavailable",
}
QUALITY_BINDING_FIELDS = {
    "status",
    "next_route",
    "body_provenance",
    "body_evidence_state",
    "body_text",
    "body_meaningful_chars",
    "paragraph_count",
    "dom_noise_or_placeholder",
    "meta_description",
    "meta_description_as_body",
    "image_count",
    "has_canvas",
    "media_inventory_required",
    "final_evidence_status",
}


def mapping(value: object) -> dict[str, object]:
    return value if isinstance(value, dict) else {}


def media_is_available(media: dict[str, object]) -> bool:
    status = str(media.get("status") or media.get("media_evidence_status") or "").lower()
    return status in MEDIA_SUCCESS_STATES


def media_inventory_completed(media: dict[str, object]) -> bool:
    return media.get("inventory_status") == "completed" and media_is_available(media)


def same_declared_path(value: object, expected: Path, package_root: Path) -> bool:
    try:
        return resolve_declared_path(value, package_root) == expected.resolve()
    except (TypeError, ValueError):
        return False


def declared_case_root(record: dict[str, object], package_root: Path) -> Path | None:
    try:
        return resolve_declared_path(record.get("case_root"), package_root)
    except (TypeError, ValueError):
        return None


def bound_regular_file(
    reference: object,
    package_root: Path,
    case_root: Path,
) -> Path | None:
    ref = mapping(reference)
    try:
        path = resolve_declared_path(ref.get("path"), package_root)
        ensure_within(path, case_root)
    except (TypeError, ValueError):
        return None
    if not path.is_file() or path.is_symlink() or ref.get("sha256") != sha256_file(path):
        return None
    return path


def validate_media_content(
    media: dict[str, object],
    package_root: Path,
    case_root: Path,
    source_asset_path: Path | None,
    source_asset_sha256: object,
    capture_inventory: object,
) -> tuple[bool, bool, bool, list[str]]:
    """Validate inventory and any claim-bearing result artifacts.

    A success label alone is not evidence. Inventory entries bind the capture
    asset; claim-bearing media additionally binds nonempty OCR/visual output
    and the executor receipt that names those exact results.
    """
    failures: list[str] = []
    claims_value = media.get("media_claims_required")
    claims_required = claims_value is True
    if media.get("inventory_status") != "completed":
        failures.append("media_inventory_incomplete")
    if not isinstance(claims_value, bool):
        failures.append("media_claims_requirement_missing")

    inventory_items = media.get("inventory_items")
    if not isinstance(inventory_items, list) or not inventory_items:
        failures.append("media_inventory_items_missing")
        inventory_items = []
    capture_items = capture_inventory if isinstance(capture_inventory, list) else []
    expected_items = {
        str(item.get("dom_id")): mapping(item)
        for item in capture_items
        if isinstance(item, dict)
        and isinstance(item.get("dom_id"), str)
    }
    observed_ids: list[str] = []
    matching_classes: list[str] = []
    for item in inventory_items:
        item_map = mapping(item)
        dom_id = item_map.get("dom_id")
        source_ref = mapping(item_map.get("source_asset"))
        classification = item_map.get("classification")
        if not isinstance(dom_id, str):
            failures.append("media_inventory_dom_id_missing")
            continue
        observed_ids.append(dom_id)
        if classification not in MEDIA_INVENTORY_CLASSES:
            failures.append("media_inventory_classification_invalid")
        expected = expected_items.get(dom_id)
        if expected is None:
            failures.append("media_inventory_dom_id_not_declared")
            continue
        expected_source = mapping(expected.get("source_asset"))
        if expected.get("availability") != "captured":
            failures.append("media_inventory_capture_asset_unavailable")
        elif (
            source_ref.get("path") != expected_source.get("path")
            or source_ref.get("sha256") != expected_source.get("sha256")
        ):
            failures.append("media_inventory_source_asset_mismatch")
        matching_classes.append(str(classification))
    if len(observed_ids) != len(set(observed_ids)):
        failures.append("media_inventory_duplicate_dom_id")
    if set(observed_ids) != set(expected_items) or len(observed_ids) != len(expected_items):
        failures.append("media_inventory_dom_set_mismatch")
    if claims_required and "claim_bearing" not in matching_classes:
        failures.append("media_claim_bearing_inventory_item_missing")
    if not claims_required and "claim_bearing" in matching_classes:
        failures.append("media_claim_requirement_contradicts_inventory")

    result_references = media.get("result_artifacts")
    result_references = result_references if isinstance(result_references, list) else []
    valid_results: list[dict[str, object]] = []
    if claims_required and not result_references:
        failures.append("media_result_artifacts_missing")
    for result in result_references:
        result_ref = mapping(result)
        if result_ref.get("kind") not in MEDIA_RESULT_KINDS:
            failures.append("media_result_kind_invalid")
            continue
        result_path = bound_regular_file(result_ref, package_root, case_root)
        if result_path is None:
            failures.append("media_result_artifact_binding_mismatch")
            continue
        if not result_path.read_text(encoding="utf-8", errors="replace").strip():
            failures.append("media_result_artifact_empty")
            continue
        valid_results.append(
            {
                "kind": result_ref.get("kind"),
                "path": package_relative(result_path, package_root),
                "sha256": sha256_file(result_path),
            }
        )

    if claims_required:
        executor_path = bound_regular_file(media.get("executor_receipt"), package_root, case_root)
        if executor_path is None:
            failures.append("media_executor_receipt_binding_mismatch")
        else:
            try:
                executor = mapping(read_json(executor_path))
            except (OSError, ValueError):
                executor = {}
            executor_asset = mapping(executor.get("source_asset"))
            if (
                executor.get("schema") != "media-understanding/operation-receipt/v1"
                or executor.get("status") != "completed"
                or executor.get("case_id") != media.get("case_id")
                or declared_case_root(executor, package_root) != case_root.resolve()
                or source_asset_path is None
                or not same_declared_path(executor_asset.get("path"), source_asset_path, package_root)
                or executor_asset.get("sha256") != source_asset_sha256
                or executor.get("result_artifacts") != valid_results
            ):
                failures.append("media_executor_receipt_content_mismatch")

    inventory_completed = media_is_available(media) and not any(
        failure.startswith("media_inventory") or failure == "media_claims_requirement_missing"
        for failure in failures
    )
    supplement_available = claims_required and inventory_completed and not failures
    return inventory_completed, claims_required, supplement_available, failures


def validate_capture_dom_inventory(
    capture: dict[str, object],
    document: str,
    package_root: Path,
    case_root: Path,
) -> tuple[list[dict[str, object]], list[str]]:
    observed = dom_media_inventory(document)
    declared_value = capture.get("dom_media_inventory")
    if not isinstance(declared_value, list):
        return [], ["capture_dom_media_inventory_missing"]
    declared = [mapping(item) for item in declared_value]
    failures: list[str] = []
    if len(declared) != len(observed):
        failures.append("capture_dom_media_inventory_count_mismatch")
    for index, expected in enumerate(observed):
        if index >= len(declared):
            break
        item = declared[index]
        for field in ("dom_id", "kind", "locator", "duplicate_of"):
            if item.get(field) != expected.get(field):
                failures.append(f"capture_dom_media_inventory_mismatch:{field}")
        availability = item.get("availability")
        source_ref = mapping(item.get("source_asset"))
        if availability == "captured":
            source_path = bound_regular_file(source_ref, package_root, case_root)
            if source_path is None or source_ref.get("bytes") != source_path.stat().st_size:
                failures.append("capture_dom_media_source_binding_mismatch")
        elif availability == "unavailable":
            if item.get("source_asset") is not None:
                failures.append("capture_unavailable_dom_media_has_source")
        else:
            failures.append("capture_dom_media_availability_invalid")
        duplicate_of = item.get("duplicate_of")
        if isinstance(duplicate_of, str):
            prior = next(
                (candidate for candidate in declared[:index] if candidate.get("dom_id") == duplicate_of),
                None,
            )
            if prior is None or prior.get("source_asset") != item.get("source_asset"):
                failures.append("capture_duplicate_dom_media_binding_mismatch")

    declared_assets = capture.get("source_assets")
    if not isinstance(declared_assets, list):
        failures.append("capture_source_assets_missing")
        declared_assets = []
    expected_by_ref: dict[tuple[object, object], list[str]] = {}
    for item in declared:
        source_ref = mapping(item.get("source_asset"))
        if item.get("availability") == "captured":
            key = (source_ref.get("path"), source_ref.get("sha256"))
            expected_by_ref.setdefault(key, []).append(str(item.get("dom_id")))
    observed_keys: list[tuple[object, object]] = []
    for source_asset in declared_assets:
        asset = mapping(source_asset)
        key = (asset.get("path"), asset.get("sha256"))
        observed_keys.append(key)
        source_path = bound_regular_file(asset, package_root, case_root)
        if (
            source_path is None
            or asset.get("bytes") != source_path.stat().st_size
            or asset.get("dom_ids") != expected_by_ref.get(key)
        ):
            failures.append("capture_source_asset_set_binding_mismatch")
    if len(observed_keys) != len(set(observed_keys)) or set(observed_keys) != set(expected_by_ref):
        failures.append("capture_source_asset_set_mismatch")
    if any(
        item.get("duplicate_of") is None and item.get("availability") != "captured"
        for item in declared
    ):
        failures.append("capture_unique_dom_media_asset_unavailable")
    return declared, failures


def recompute_capture_quality(
    capture: dict[str, object], local_html: Path, package_root: Path, case_root: Path
) -> tuple[dict[str, object], list[str]]:
    """Bind declared quality fields to a fresh read of the captured HTML."""
    adapter = capture.get("capture_adapter")
    if adapter == "static_html_probe":
        rendered = False
    elif adapter == "rendered_html_probe":
        rendered = True
    else:
        return {}, ["capture_adapter_unrecognized"]
    document = local_html.read_text(encoding="utf-8", errors="replace")
    observed = decide_gate(document, rendered)
    declared = mapping(capture.get("quality_gate"))
    failures = [
        f"capture_quality_gate_mismatch:{field}"
        for field in sorted(QUALITY_BINDING_FIELDS)
        if declared.get(field) != observed.get(field)
    ]
    _, inventory_failures = validate_capture_dom_inventory(
        capture, document, package_root, case_root
    )
    failures.extend(inventory_failures)
    return observed, failures


def validate_persisted_assessment(
    assessment_path: Path,
    package_root: Path,
    case_root: Path,
    expected_case_id: str | None = None,
    expected_source_locator: str | None = None,
) -> list[str]:
    """Revalidate intake -> capture -> HTML -> assessment from current bytes."""
    root = package_root.resolve()
    case_dir = ensure_within(case_root, root)
    failures: list[str] = []
    if not assessment_path.is_file() or assessment_path.is_symlink():
        return ["assessment_file_missing_or_linked"]
    assessment = mapping(read_json(assessment_path))
    case_id = str(assessment.get("case_id") or "")
    if assessment.get("schema") != "web-bookmark-intelligence/evidence-assessment/v2":
        failures.append("assessment_schema_mismatch")
    if not case_id or (expected_case_id is not None and case_id != expected_case_id):
        failures.append("assessment_case_id_mismatch")
    if declared_case_root(assessment, root) != case_dir:
        failures.append("assessment_case_root_mismatch")

    intake_ref = mapping(assessment.get("intake"))
    dom_ref = mapping(assessment.get("dom"))
    try:
        intake_path = resolve_declared_path(intake_ref.get("path"), root)
        capture_path = resolve_declared_path(dom_ref.get("capture_path"), root)
        ensure_within(intake_path, case_dir)
        ensure_within(capture_path, case_dir)
    except (TypeError, ValueError):
        return failures + ["assessment_input_path_mismatch"]
    if (
        not intake_path.is_file()
        or intake_path.is_symlink()
        or intake_ref.get("sha256") != sha256_file(intake_path)
    ):
        failures.append("assessment_intake_file_binding_mismatch")
    if (
        not capture_path.is_file()
        or capture_path.is_symlink()
        or dom_ref.get("sha256") != sha256_file(capture_path)
    ):
        failures.append("assessment_capture_file_binding_mismatch")
    if failures:
        return failures

    intake = mapping(read_json(intake_path))
    capture = mapping(read_json(capture_path))
    if intake.get("schema") != "web-bookmark-intelligence/intake/v2":
        failures.append("intake_schema_mismatch")
    if capture.get("schema") != "web-bookmark-intelligence/capture-record/v3":
        failures.append("capture_schema_mismatch")
    if intake.get("case_id") != case_id or capture.get("case_id") != case_id:
        failures.append("assessment_live_case_id_mismatch")
    if (
        expected_source_locator is not None
        and intake.get("input_kind") in {"web_page", "video_page"}
        and intake.get("source_locator") != expected_source_locator
    ):
        failures.append("assessment_source_locator_mismatch")
    if declared_case_root(intake, root) != case_dir or declared_case_root(capture, root) != case_dir:
        failures.append("assessment_live_case_root_mismatch")
    capture_intake = mapping(capture.get("intake"))
    if (
        not same_declared_path(capture_intake.get("path"), intake_path, root)
        or capture_intake.get("sha256") != sha256_file(intake_path)
    ):
        failures.append("capture_intake_binding_mismatch")

    capture_source = mapping(capture.get("source"))
    try:
        local_html = resolve_declared_path(capture_source.get("local_html"), root)
        ensure_within(local_html, case_dir)
    except (TypeError, ValueError):
        local_html = None
        failures.append("capture_source_asset_path_mismatch")
    if (
        local_html is None
        or not local_html.is_file()
        or local_html.is_symlink()
        or capture_source.get("sha256") != sha256_file(local_html)
    ):
        failures.append("capture_source_asset_binding_mismatch")
        observed_quality: dict[str, object] = {}
    else:
        observed_quality, quality_failures = recompute_capture_quality(
            capture, local_html, root, case_dir
        )
        failures.extend(quality_failures)
    if (
        intake.get("input_kind") in {"web_page", "video_page"}
        and capture_source.get("url") != intake.get("source_locator")
    ):
        failures.append("capture_source_url_mismatch")
    for field in (
        "body_evidence_state",
        "body_provenance",
        "body_meaningful_chars",
        "dom_noise_or_placeholder",
        "meta_description_as_body",
    ):
        if dom_ref.get(field) != observed_quality.get(field):
            failures.append(f"assessment_dom_mismatch:{field}")

    media_ref = mapping(assessment.get("media"))
    media: dict[str, object] = {}
    inventory_completed = False
    media_available = False
    media_claims_required = False
    if media_ref.get("provided") is True:
        try:
            media_path = resolve_declared_path(media_ref.get("path"), root)
            ensure_within(media_path, case_dir)
        except (TypeError, ValueError):
            media_path = None
            failures.append("assessment_media_path_mismatch")
        if (
            media_path is None
            or not media_path.is_file()
            or media_path.is_symlink()
            or media_ref.get("sha256") != sha256_file(media_path)
        ):
            failures.append("assessment_media_file_binding_mismatch")
        else:
            media = mapping(read_json(media_path))
            if (
                media.get("schema") != "web-bookmark-intelligence/media-evidence/v2"
                or media.get("case_id") != case_id
                or declared_case_root(media, root) != case_dir
            ):
                failures.append("assessment_media_case_binding_mismatch")
            lineage = mapping(media.get("lineage"))
            media_intake = mapping(lineage.get("intake"))
            media_capture = mapping(lineage.get("capture"))
            source_asset = mapping(lineage.get("source_asset"))
            if (
                not same_declared_path(media_intake.get("path"), intake_path, root)
                or media_intake.get("sha256") != sha256_file(intake_path)
                or not same_declared_path(media_capture.get("path"), capture_path, root)
                or media_capture.get("sha256") != sha256_file(capture_path)
            ):
                failures.append("assessment_media_lineage_mismatch")
            try:
                asset_path = resolve_declared_path(source_asset.get("path"), root)
                ensure_within(asset_path, case_dir)
            except (TypeError, ValueError):
                asset_path = None
                failures.append("assessment_media_source_asset_path_mismatch")
            asset_sha = source_asset.get("sha256")
            declared_assets = [
                mapping(item)
                for item in capture.get("source_assets", [])
                if isinstance(item, dict)
            ]
            if (
                asset_path is None
                or not asset_path.is_file()
                or asset_path.is_symlink()
                or asset_sha != sha256_file(asset_path)
                or not any(
                    same_declared_path(item.get("path"), asset_path, root)
                    and item.get("sha256") == asset_sha
                    for item in declared_assets
                )
            ):
                failures.append("assessment_media_source_asset_binding_mismatch")
            (
                inventory_completed,
                media_claims_required,
                media_available,
                media_content_failures,
            ) = validate_media_content(
                media,
                root,
                case_dir,
                asset_path,
                asset_sha,
                capture.get("dom_media_inventory"),
            )
            failures.extend(media_content_failures)
    elif media_ref.get("path") is not None or media_ref.get("sha256") is not None:
        failures.append("assessment_media_absence_mismatch")

    body_state = str(observed_quality.get("body_evidence_state") or "not_available")
    meta_as_body = bool(observed_quality.get("meta_description_as_body")) or observed_quality.get("body_provenance") == "meta_description"
    inventory_required = bool(observed_quality.get("media_inventory_required"))
    media_required = media_claims_required
    if failures or meta_as_body:
        expected_status = "failed"
    elif inventory_required and not inventory_completed:
        expected_status = "failed"
    elif body_state == "substantive" and media_required and media_available:
        expected_status = "full_body_with_media_supplement"
    elif body_state == "substantive" and media_required:
        expected_status = "failed"
    elif body_state == "substantive":
        expected_status = "full_body"
    elif media_available:
        expected_status = "needs_image_supplement"
    else:
        expected_status = "failed"
    binding = mapping(assessment.get("case_binding"))
    if (
        failures
        or binding.get("valid") is not True
        or binding.get("failures") != []
        or assessment.get("final_status") != expected_status
        or assessment.get("page_purpose_ready") is not (expected_status != "failed")
        or media_ref.get("inventory_required") is not inventory_required
        or media_ref.get("inventory_completed") is not (inventory_completed and not failures)
        or media_ref.get("claims_required") is not media_required
        or media_ref.get("available") is not (media_available and not failures)
    ):
        failures.append("assessment_projection_mismatch")
    return failures


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--intake", type=Path, required=True)
    parser.add_argument("--capture", type=Path, required=True)
    parser.add_argument("--package-root", type=Path, required=True)
    parser.add_argument("--case-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--media", type=Path)
    parser.add_argument("--media-claims-required", action="store_true")
    args = parser.parse_args()

    root = args.package_root.resolve()
    case_root = ensure_within(args.case_root, root)
    intake_path = ensure_within(args.intake, case_root)
    capture_path = ensure_within(args.capture, case_root)
    out_path = ensure_within(args.out, case_root)
    media_path = ensure_within(args.media, case_root) if args.media else None
    for label, path in (("intake", intake_path), ("capture", capture_path), ("media", media_path)):
        if path is not None and (not path.is_file() or path.is_symlink()):
            raise SystemExit(f"{label} must be a regular case-local file: {path}")

    intake = mapping(read_json(intake_path))
    capture = mapping(read_json(capture_path))
    quality = mapping(capture.get("quality_gate"))
    media = mapping(read_json(media_path)) if media_path else {}
    case_id = str(intake.get("case_id") or "")
    failures: list[str] = []

    if intake.get("schema") != "web-bookmark-intelligence/intake/v2":
        failures.append("intake_schema_mismatch")
    if capture.get("schema") != "web-bookmark-intelligence/capture-record/v3":
        failures.append("capture_schema_mismatch")
    if not case_id:
        failures.append("intake_case_id_missing")
    if capture.get("case_id") != case_id:
        failures.append("capture_case_id_mismatch")
    if declared_case_root(intake, root) != case_root:
        failures.append("intake_case_root_mismatch")
    if declared_case_root(capture, root) != case_root:
        failures.append("capture_case_root_mismatch")

    capture_intake = mapping(capture.get("intake"))
    if not same_declared_path(capture_intake.get("path"), intake_path, root):
        failures.append("capture_intake_path_mismatch")
    if capture_intake.get("sha256") != sha256_file(intake_path):
        failures.append("capture_intake_hash_mismatch")

    capture_source = mapping(capture.get("source"))
    try:
        local_html = resolve_declared_path(capture_source.get("local_html"), root)
        ensure_within(local_html, case_root)
    except (TypeError, ValueError):
        local_html = None
        failures.append("capture_source_asset_path_mismatch")
    if local_html is None or not local_html.is_file() or local_html.is_symlink():
        failures.append("capture_source_asset_missing")
    elif capture_source.get("sha256") != sha256_file(local_html):
        failures.append("capture_source_asset_hash_mismatch")
    else:
        quality, quality_failures = recompute_capture_quality(
            capture, local_html, root, case_root
        )
        failures.extend(quality_failures)
    if intake.get("input_kind") in {"web_page", "video_page"} and capture_source.get("url") != intake.get("source_locator"):
        failures.append("capture_source_url_mismatch")

    inventory_required = bool(quality.get("media_inventory_required"))
    media_required = args.media_claims_required or media.get("media_claims_required") is True
    inventory_completed = False
    media_available = False
    if media_path:
        if media.get("schema") != "web-bookmark-intelligence/media-evidence/v2":
            failures.append("media_schema_mismatch")
        if media.get("case_id") != case_id:
            failures.append("media_case_id_mismatch")
        if declared_case_root(media, root) != case_root:
            failures.append("media_case_root_mismatch")
        lineage = mapping(media.get("lineage"))
        intake_lineage = mapping(lineage.get("intake"))
        capture_lineage = mapping(lineage.get("capture"))
        source_asset_lineage = mapping(lineage.get("source_asset"))
        if not same_declared_path(intake_lineage.get("path"), intake_path, root):
            failures.append("media_intake_path_mismatch")
        if intake_lineage.get("sha256") != sha256_file(intake_path):
            failures.append("media_intake_hash_mismatch")
        if not same_declared_path(capture_lineage.get("path"), capture_path, root):
            failures.append("media_capture_path_mismatch")
        if capture_lineage.get("sha256") != sha256_file(capture_path):
            failures.append("media_capture_hash_mismatch")
        try:
            source_asset_path = resolve_declared_path(source_asset_lineage.get("path"), root)
            ensure_within(source_asset_path, case_root)
        except (TypeError, ValueError):
            source_asset_path = None
            failures.append("media_source_asset_path_mismatch")
        source_asset_sha = source_asset_lineage.get("sha256")
        if source_asset_path is None or not source_asset_path.is_file() or source_asset_path.is_symlink():
            failures.append("media_source_asset_missing")
        elif source_asset_sha != sha256_file(source_asset_path):
            failures.append("media_source_asset_hash_mismatch")
        declared_assets = [mapping(item) for item in capture.get("source_assets", []) if isinstance(item, dict)]
        asset_declared = any(
            same_declared_path(item.get("path"), source_asset_path, root)
            and item.get("sha256") == source_asset_sha
            for item in declared_assets
            if source_asset_path is not None
        )
        if not asset_declared:
            failures.append("media_source_asset_not_declared_by_capture")
        (
            inventory_completed,
            receipt_claims_required,
            media_available,
            media_content_failures,
        ) = validate_media_content(
            media,
            root,
            case_root,
            source_asset_path,
            source_asset_sha,
            capture.get("dom_media_inventory"),
        )
        failures.extend(media_content_failures)
        if args.media_claims_required and not receipt_claims_required:
            failures.append("media_claims_requirement_conflicts_with_cli")
        media_required = args.media_claims_required or receipt_claims_required

    body_state = str(quality.get("body_evidence_state") or "not_available")
    meta_as_body = bool(quality.get("meta_description_as_body")) or quality.get("body_provenance") == "meta_description"
    if failures:
        final_status, reason = "failed", "case_lineage_mismatch"
    elif meta_as_body:
        final_status, reason = "failed", "meta_description_cannot_be_promoted_to_body_evidence"
    elif inventory_required and not inventory_completed:
        final_status, reason = "failed", "required_media_inventory_missing"
    elif body_state == "substantive" and media_required and media_available:
        final_status, reason = "full_body_with_media_supplement", "substantive_dom_and_required_media_evidence_available"
    elif body_state == "substantive" and media_required:
        final_status, reason = "failed", "required_media_evidence_missing"
    elif body_state == "substantive":
        final_status, reason = "full_body", "substantive_dom_evidence_available"
    elif media_available:
        final_status, reason = "needs_image_supplement", "dom_is_weak_or_placeholder_but_media_evidence_is_available"
    else:
        final_status, reason = "failed", "no_substantive_body_or_media_evidence"

    result = {
        "schema": "web-bookmark-intelligence/evidence-assessment/v2",
        "created_at": utc_now(),
        "case_id": case_id or None,
        "case_root": package_relative(case_root, root),
        "case_binding": {"valid": not failures, "failures": failures},
        "final_status": final_status,
        "reason": reason,
        "intake": {"path": package_relative(intake_path, root), "sha256": sha256_file(intake_path)},
        "dom": {
            "capture_path": package_relative(capture_path, root),
            "sha256": sha256_file(capture_path),
            "body_evidence_state": body_state,
            "body_provenance": quality.get("body_provenance"),
            "body_meaningful_chars": quality.get("body_meaningful_chars"),
            "dom_noise_or_placeholder": quality.get("dom_noise_or_placeholder"),
            "meta_description_as_body": meta_as_body,
        },
        "media": {
            "provided": bool(media_path),
            "path": package_relative(media_path, root) if media_path else None,
            "sha256": sha256_file(media_path) if media_path else None,
            "inventory_required": inventory_required,
            "inventory_completed": inventory_completed and not failures,
            "available": media_available and not failures,
            "claims_required": media_required,
        },
        "page_purpose_ready": final_status != "failed" and not failures,
        "formal_write_authorized": False,
        "adoption_authorized": False,
    }
    write_json(out_path, result, root)
    print(final_status)
    return 0 if final_status != "failed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
