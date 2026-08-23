#!/usr/bin/env python3
"""Run package-local, offline behavior checks for the candidate skill."""

from __future__ import annotations

import argparse
import base64
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from common import package_relative, sha256_file, utc_now, write_json


SCRIPT_DIR = Path(__file__).resolve().parent


def run(*args: str, allow_failure: bool = False) -> subprocess.CompletedProcess[str]:
    environment = os.environ.copy()
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    completed = subprocess.run([sys.executable, "-B", *args], capture_output=True, text=True, check=False, env=environment)
    if completed.returncode != 0 and not allow_failure:
        raise RuntimeError(f"command failed: {' '.join(args)}\n{completed.stdout}\n{completed.stderr}")
    return completed


def load(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def create_url_intake(root: Path, case_root: Path, case_id: str, url: str) -> Path:
    case_root.mkdir(parents=True, exist_ok=True)
    intake = case_root / "intake.json"
    run(
        str(SCRIPT_DIR / "intake_case.py"),
        "--url",
        url,
        "--case-id",
        case_id,
        "--package-root",
        str(root),
        "--case-root",
        str(case_root),
        "--out",
        str(intake),
    )
    return intake


def capture_html(root: Path, case_root: Path, intake: Path, html_path: Path, out: Path, url: str, *extra: str) -> None:
    run(
        str(SCRIPT_DIR / "capture_pipeline.py"),
        "--html",
        str(html_path),
        "--intake",
        str(intake),
        "--source-url",
        url,
        "--package-root",
        str(root),
        "--case-root",
        str(case_root),
        "--out",
        str(out),
        *extra,
    )


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--package-root", type=Path)
    parser.add_argument("--out", type=Path)
    args = parser.parse_args()
    if bool(args.package_root) != bool(args.out):
        raise SystemExit("pass --package-root and --out together when persisting a validation report")
    checks = [
        "rich_dom_body_passes_without_promoting_meta_description",
        "meta_only_html_routes_to_playwright",
        "canvas_and_placeholder_dom_route_to_media_understanding",
        "evidence_fusion_requires_same_case_hash_lineage",
        "cross_case_media_is_rejected",
        "screenshot_and_video_page_intake_use_single_flow",
        "shoulong_batch_starts_planned_and_requires_pending_quality",
        "action_cards_require_bound_passing_assessment",
        "unknown_exit_zero_script_cannot_claim_workbuddy_v1_5_1",
    ]
    with tempfile.TemporaryDirectory(prefix="web-bookmark-intelligence-") as temporary:
        root = Path(temporary)
        rich_case = root / "cases" / "rich"
        rich_url = "https://example.com/rich"
        rich_intake = create_url_intake(root, rich_case, "rich", rich_url)
        rich = rich_case / "rich.html"
        rich.write_text(
            "<html><head><title>Rich</title><meta name='description' content='short summary only'></head>"
            "<body><article><p>" + "真实正文内容 " * 80 + "</p><p>" + "第二段正文证据 " * 80 + "</p><img src='asset.png'></article></body></html>",
            encoding="utf-8",
        )
        rich_asset = rich_case / "asset.png"
        rich_asset.write_bytes(base64.b64decode("iVBORw0KGgoAAAANSUhEUgAAAAEAAAABCAQAAAC1HAwCAAAAC0lEQVR42mNk+A8AAQUBAScY42YAAAAASUVORK5CYII="))
        rich_out = rich_case / "capture.json"
        capture_html(root, rich_case, rich_intake, rich, rich_out, rich_url, "--rendered", "--media-asset", str(rich_asset))
        rich_record = load(rich_out)
        assert rich_record["quality_gate"]["status"] == "pass"
        assert rich_record["quality_gate"]["meta_description_as_body"] is False

        meta_case = root / "cases" / "meta"
        meta_url = "https://example.com/meta"
        meta_intake = create_url_intake(root, meta_case, "meta", meta_url)
        meta_only = meta_case / "meta-only.html"
        meta_only.write_text("<html><head><meta name='description' content='" + "摘要 " * 180 + "'></head><body><div>分享</div></body></html>", encoding="utf-8")
        meta_out = meta_case / "capture.json"
        capture_html(root, meta_case, meta_intake, meta_only, meta_out, meta_url)
        meta_record = load(meta_out)
        assert meta_record["quality_gate"]["status"] == "needs_playwright"
        assert meta_record["quality_gate"]["body_text"] != meta_record["quality_gate"]["meta_description"]

        canvas_case = root / "cases" / "canvas"
        canvas_url = "https://example.com/canvas"
        canvas_intake = create_url_intake(root, canvas_case, "canvas", canvas_url)
        canvas = canvas_case / "canvas.html"
        canvas.write_text("<html><body><article><p>短说明</p><canvas></canvas><img src='a.png'></article></body></html>", encoding="utf-8")
        canvas_asset = canvas_case / "asset.png"
        canvas_asset.write_bytes(rich_asset.read_bytes())
        canvas_out = canvas_case / "capture.json"
        capture_html(root, canvas_case, canvas_intake, canvas, canvas_out, canvas_url, "--rendered", "--media-asset", str(canvas_asset))
        canvas_record = load(canvas_out)
        assert canvas_record["quality_gate"]["status"] == "needs_media_understanding"
        assert canvas_record["quality_gate"]["dom_noise_or_placeholder"] is True

        visual_result = rich_case / "visual-result.txt"
        visual_result.write_text(
            "The case-local source image contains a substantive claim; uncertainty: fixture-only visual result.",
            encoding="utf-8",
        )
        result_artifacts = [
            {
                "kind": "visual",
                "path": package_relative(visual_result, root),
                "sha256": sha256_file(visual_result),
            }
        ]
        executor_receipt = rich_case / "media-executor-receipt.json"
        executor_receipt.write_text(
            json.dumps(
                {
                    "schema": "media-understanding/operation-receipt/v1",
                    "status": "completed",
                    "case_id": "rich",
                    "case_root": package_relative(rich_case, root),
                    "source_asset": {
                        "path": package_relative(rich_asset, root),
                        "sha256": sha256_file(rich_asset),
                    },
                    "result_artifacts": result_artifacts,
                }
            ),
            encoding="utf-8",
        )
        media = rich_case / "media.json"
        media.write_text(
            json.dumps(
                {
                    "schema": "web-bookmark-intelligence/media-evidence/v2",
                    "status": "success",
                    "inventory_status": "completed",
                    "case_id": "rich",
                    "case_root": package_relative(rich_case, root),
                    "media_claims_required": True,
                    "inventory_items": [
                        {
                            "dom_id": rich_record["dom_media_inventory"][0]["dom_id"],
                            "source_asset": {
                                "path": package_relative(rich_asset, root),
                                "sha256": sha256_file(rich_asset),
                            },
                            "classification": "claim_bearing",
                        }
                    ],
                    "result_artifacts": result_artifacts,
                    "executor_receipt": {
                        "path": package_relative(executor_receipt, root),
                        "sha256": sha256_file(executor_receipt),
                    },
                    "lineage": {
                        "intake": {"path": package_relative(rich_intake, root), "sha256": sha256_file(rich_intake)},
                        "capture": {"path": package_relative(rich_out, root), "sha256": sha256_file(rich_out)},
                        "source_asset": {"path": package_relative(rich_asset, root), "sha256": sha256_file(rich_asset)},
                    },
                }
            ),
            encoding="utf-8",
        )
        rich_assessment = rich_case / "evidence-assessment.json"
        run(
            str(SCRIPT_DIR / "assess_capture_evidence.py"),
            "--intake",
            str(rich_intake),
            "--capture",
            str(rich_out),
            "--media",
            str(media),
            "--media-claims-required",
            "--package-root",
            str(root),
            "--case-root",
            str(rich_case),
            "--out",
            str(rich_assessment),
        )
        assessment = load(rich_assessment)
        assert assessment["final_status"] == "full_body_with_media_supplement"
        assert assessment["case_binding"]["valid"] is True

        empty_media = rich_case / "empty-media.json"
        empty_payload = load(media)
        empty_payload["inventory_items"] = []
        empty_payload["result_artifacts"] = []
        empty_payload.pop("executor_receipt")
        empty_media.write_text(json.dumps(empty_payload), encoding="utf-8")
        empty_assessment = rich_case / "empty-media-assessment.json"
        empty_result = run(
            str(SCRIPT_DIR / "assess_capture_evidence.py"),
            "--intake",
            str(rich_intake),
            "--capture",
            str(rich_out),
            "--media",
            str(empty_media),
            "--package-root",
            str(root),
            "--case-root",
            str(rich_case),
            "--out",
            str(empty_assessment),
            allow_failure=True,
        )
        assert empty_result.returncode == 1
        assert load(empty_assessment)["final_status"] == "failed"

        cross_case_media = rich_case / "cross-case-media.json"
        cross_case_media.write_text(media.read_text(encoding="utf-8"), encoding="utf-8")
        cross_payload = load(cross_case_media)
        cross_payload["case_id"] = "canvas"
        cross_payload["case_root"] = package_relative(canvas_case, root)
        cross_payload["lineage"]["source_asset"] = {
            "path": package_relative(canvas_asset, root),
            "sha256": sha256_file(canvas_asset),
        }
        cross_case_media.write_text(json.dumps(cross_payload), encoding="utf-8")
        rejected_assessment = rich_case / "rejected-assessment.json"
        rejected = run(
            str(SCRIPT_DIR / "assess_capture_evidence.py"),
            "--intake",
            str(rich_intake),
            "--capture",
            str(rich_out),
            "--media",
            str(cross_case_media),
            "--package-root",
            str(root),
            "--case-root",
            str(rich_case),
            "--out",
            str(rejected_assessment),
            allow_failure=True,
        )
        assert rejected.returncode == 1
        assert load(rejected_assessment)["reason"] == "case_lineage_mismatch"

        image_case = root / "cases" / "image"
        image_case.mkdir(parents=True)
        image = root / "input.gif"
        image.write_bytes(base64.b64decode("R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw=="))
        intake_out = image_case / "intake.json"
        run(str(SCRIPT_DIR / "intake_case.py"), "--image", str(image), "--package-root", str(root), "--case-root", str(image_case), "--out", str(intake_out))
        video_case = root / "cases" / "video"
        video_intake = create_url_intake(root, video_case, "video", "https://example.com/video")
        video_payload = load(video_intake)
        assert load(intake_out)["route_request"] == "media_understanding_with_optional_ocr"
        assert video_payload["route_request"] == "html_capture_pipeline"
        video_out = video_case / "video-intake.json"
        run(str(SCRIPT_DIR / "intake_case.py"), "--url", "https://example.com/video", "--url-kind", "video_page", "--package-root", str(root), "--case-root", str(video_case), "--out", str(video_out), "--case-id", "video")
        assert load(video_out)["route_request"] == "video_page_capture_then_media_access_check"

        urls = root / "urls.txt"
        urls.write_text("https://chinalowcarb.com/example\n", encoding="utf-8")
        run(str(SCRIPT_DIR / "plan_batch.py"), "--url-file", str(urls), "--profile", "shoulong", "--package-root", str(root), "--out-dir", str(root / "batch"))
        batch = load(root / "batch" / "batch-plan.json")
        assert batch["capture_pipeline"] == "workbuddy_shared_pending_quality"
        assert batch["cases"][0]["status"] == "planned"
        assert batch["cases"][0]["quality_assessment_required"] is True

        purpose_out = rich_case / "purpose.json"
        run(str(SCRIPT_DIR / "prepare_page_purpose.py"), "--case", str(rich_intake), "--evidence", str(rich_assessment), "--package-root", str(root), "--case-root", str(rich_case), "--out", str(purpose_out))
        context, repos, units = rich_case / "context.json", rich_case / "repos.json", rich_case / "units.json"
        context.write_text(json.dumps({"records": [{"record_id": "affair-1", "authority_class": "formal_current", "allowed_use": "compare_only"}]}), encoding="utf-8")
        repos.write_text(json.dumps([{"repo_id": "github:example/tool", "repository": "example/tool", "metrics_snapshot": {"watchers": 3}, "freshness_state": "aging"}]), encoding="utf-8")
        units.write_text(
            json.dumps(
                {
                    "schema": "web-bookmark-intelligence/content-units/v2",
                    "case_id": "rich",
                    "case_root": package_relative(rich_case, root),
                    "evidence_assessment": {
                        "path": package_relative(rich_assessment, root),
                        "sha256": sha256_file(rich_assessment),
                    },
                    "content_units": [{"unit_id": "repo-1", "repository": "example/tool", "evidence_refs": ["span-1"]}],
                }
            ),
            encoding="utf-8",
        )
        cards_out = rich_case / "cards.json"
        run(str(SCRIPT_DIR / "build_action_cards.py"), "--case", str(rich_intake), "--capture", str(rich_assessment), "--purpose", str(purpose_out), "--content-units", str(units), "--context", str(context), "--repos", str(repos), "--package-root", str(root), "--case-root", str(rich_case), "--out", str(cards_out))
        cards = load(cards_out)
        assert cards["action_card_status"] == "ready_for_user_decision"
        assert len(cards["action_cards"]) == 1

        blocked_cards = rich_case / "blocked-cards.json"
        blocked = run(str(SCRIPT_DIR / "build_action_cards.py"), "--case", str(rich_intake), "--capture", str(rejected_assessment), "--purpose", str(purpose_out), "--content-units", str(units), "--package-root", str(root), "--case-root", str(rich_case), "--out", str(blocked_cards), allow_failure=True)
        assert blocked.returncode == 1
        assert load(blocked_cards)["action_cards"] == []

        fake_workbuddy = root / "fake_workbuddy.py"
        sentinel = root / "fake-was-executed"
        fake_workbuddy.write_text(f"from pathlib import Path\nPath({str(sentinel)!r}).write_text('bad')\n", encoding="utf-8")
        unknown_dir = root / "unknown-workbuddy"
        unknown = run(str(SCRIPT_DIR / "run_workbuddy_capture.py"), "--url", "https://example.com/", "--package-root", str(root), "--out-dir", str(unknown_dir), "--execute", "--network-authorized", "--workbuddy-script", str(fake_workbuddy), allow_failure=True)
        unknown_receipt = load(unknown_dir / "capture-execution-receipt.json")
        assert unknown.returncode == 2
        assert unknown_receipt["status"] == "needs_compatible_executor"
        assert unknown_receipt["observed_implementation"]["version"] is None
        assert unknown_receipt["network_executed"] is False
        assert not sentinel.exists()

    if args.out:
        write_json(
            args.out,
            {
                "schema": "web-bookmark-intelligence/candidate-validation/v3",
                "created_at": utc_now(),
                "offline_only": True,
                "network_calls": 0,
                "status": "passed",
                "checks": checks,
            },
            args.package_root.resolve(),
        )
    print(f"candidate_behavior=pass checks={len(checks)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
