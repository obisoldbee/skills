#!/usr/bin/env python3
"""Fuse local DOM and media evidence into one conservative final capture state."""

from __future__ import annotations

import argparse
from pathlib import Path

from common import read_json, sha256_file, utc_now, write_json


MEDIA_SUCCESS_STATES = {"completed", "success", "succeeded", "available"}


def mapping(value: object) -> dict[str, object]:
    return value if isinstance(value, dict) else {}


def media_is_available(media: dict[str, object]) -> bool:
    status = str(media.get("status") or media.get("media_evidence_status") or "").lower()
    return status in MEDIA_SUCCESS_STATES


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--capture", type=Path, required=True)
    parser.add_argument("--package-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--media", type=Path)
    parser.add_argument("--media-claims-required", action="store_true")
    args = parser.parse_args()

    capture = mapping(read_json(args.capture))
    quality = mapping(capture.get("quality_gate"))
    media = mapping(read_json(args.media)) if args.media else {}
    body_state = str(quality.get("body_evidence_state") or "not_available")
    meta_as_body = bool(quality.get("meta_description_as_body")) or quality.get("body_provenance") == "meta_description"
    media_required = args.media_claims_required or bool(media.get("media_claims_required"))
    media_available = media_is_available(media)

    if meta_as_body:
        final_status, reason = "failed", "meta_description_cannot_be_promoted_to_body_evidence"
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
        "schema": "web-bookmark-intelligence/evidence-assessment/v1",
        "created_at": utc_now(),
        "case_id": capture.get("case_id"),
        "final_status": final_status,
        "reason": reason,
        "dom": {
            "capture_path": str(args.capture),
            "sha256": sha256_file(args.capture),
            "body_evidence_state": body_state,
            "body_provenance": quality.get("body_provenance"),
            "body_meaningful_chars": quality.get("body_meaningful_chars"),
            "dom_noise_or_placeholder": quality.get("dom_noise_or_placeholder"),
            "meta_description_as_body": meta_as_body,
        },
        "media": {
            "provided": bool(args.media),
            "path": str(args.media) if args.media else None,
            "sha256": sha256_file(args.media) if args.media else None,
            "available": media_available,
            "claims_required": media_required,
        },
        "page_purpose_ready": final_status != "failed",
        "formal_write_authorized": False,
        "adoption_authorized": False,
    }
    write_json(args.out, result, args.package_root.resolve())
    print(final_status)
    return 0 if final_status != "failed" else 1


if __name__ == "__main__":
    raise SystemExit(main())
