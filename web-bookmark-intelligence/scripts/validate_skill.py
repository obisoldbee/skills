#!/usr/bin/env python3
"""Run package-local, offline behavior checks for the candidate skill."""

from __future__ import annotations

import argparse
import base64
import importlib.util
import json
import os
import subprocess
import sys
import tempfile
from pathlib import Path

from common import utc_now, write_json


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
        "evidence_fusion_requires_media_for_image_led_claims",
        "screenshot_and_video_page_intake_use_single_flow",
        "shoulong_batch_uses_workbuddy_pipeline_serially",
        "action_cards_preserve_repository_metrics_and_user_gate",
        "limited_tls_certifi_retry_preserves_both_local_attempt_receipts",
    ]
    with tempfile.TemporaryDirectory(prefix="web-bookmark-intelligence-") as temporary:
        root = Path(temporary)
        rich = root / "rich.html"
        rich.write_text(
            "<html><head><title>Rich</title><meta name='description' content='short summary only'></head>"
            "<body><article><p>" + "真实正文内容 " * 80 + "</p><p>" + "第二段正文证据 " * 80 + "</p></article></body></html>",
            encoding="utf-8",
        )
        meta_only = root / "meta-only.html"
        meta_only.write_text("<html><head><meta name='description' content='" + "摘要 " * 180 + "'></head><body><div>分享</div></body></html>", encoding="utf-8")
        canvas = root / "canvas.html"
        canvas.write_text("<html><head><meta name='description' content='image summary'></head><body><article><p>短说明</p><canvas></canvas><img src='a.png'><img src='b.png'></article></body></html>", encoding="utf-8")
        rich_out, meta_out, canvas_out = root / "rich.json", root / "meta.json", root / "canvas.json"
        run(str(SCRIPT_DIR / "capture_pipeline.py"), "--html", str(rich), "--package-root", str(root), "--out", str(rich_out), "--rendered")
        run(str(SCRIPT_DIR / "capture_pipeline.py"), "--html", str(meta_only), "--package-root", str(root), "--out", str(meta_out))
        run(str(SCRIPT_DIR / "capture_pipeline.py"), "--html", str(canvas), "--package-root", str(root), "--out", str(canvas_out), "--rendered")
        rich_record, meta_record, canvas_record = load(rich_out), load(meta_out), load(canvas_out)
        assert rich_record["quality_gate"]["status"] == "pass"
        assert rich_record["quality_gate"]["meta_description_as_body"] is False
        assert meta_record["quality_gate"]["status"] == "needs_playwright"
        assert meta_record["quality_gate"]["body_text"] != meta_record["quality_gate"]["meta_description"]
        assert canvas_record["quality_gate"]["status"] == "needs_media_understanding"
        assert canvas_record["quality_gate"]["dom_noise_or_placeholder"] is True

        media = root / "media.json"
        media.write_text(json.dumps({"status": "success", "media_claims_required": True}), encoding="utf-8")
        rich_assessment = root / "rich-assessment.json"
        canvas_assessment = root / "canvas-assessment.json"
        run(str(SCRIPT_DIR / "assess_capture_evidence.py"), "--capture", str(rich_out), "--media", str(media), "--media-claims-required", "--package-root", str(root), "--out", str(rich_assessment))
        run(str(SCRIPT_DIR / "assess_capture_evidence.py"), "--capture", str(canvas_out), "--media", str(media), "--package-root", str(root), "--out", str(canvas_assessment))
        assert load(rich_assessment)["final_status"] == "full_body_with_media_supplement"
        assert load(canvas_assessment)["final_status"] == "needs_image_supplement"

        image = root / "one.gif"
        image.write_bytes(base64.b64decode("R0lGODlhAQABAIAAAAAAAP///ywAAAAAAQABAAACAUwAOw=="))
        intake_out, video_intake_out = root / "intake.json", root / "video-intake.json"
        run(str(SCRIPT_DIR / "intake_case.py"), "--image", str(image), "--package-root", str(root), "--out", str(intake_out))
        run(str(SCRIPT_DIR / "intake_case.py"), "--url", "https://example.com/video", "--url-kind", "video_page", "--package-root", str(root), "--out", str(video_intake_out))
        intake, video_intake = load(intake_out), load(video_intake_out)
        assert intake["route_request"] == "media_understanding_with_optional_ocr"
        assert video_intake["route_request"] == "video_page_capture_then_media_access_check"

        urls = root / "urls.txt"
        urls.write_text("https://chinalowcarb.com/example\n", encoding="utf-8")
        run(str(SCRIPT_DIR / "plan_batch.py"), "--url-file", str(urls), "--profile", "shoulong", "--package-root", str(root), "--out-dir", str(root / "batch"))
        batch = load(root / "batch" / "batch-plan.json")
        assert batch["capture_pipeline"] == "workbuddy_v1_5_1_shared"
        assert batch["workbuddy_adapter"] == "workbuddy_wechat_article_archive"
        assert batch["max_workers"] == 1
        assert batch["cases"][0]["status"] == "planned"

        purpose_out = root / "purpose.json"
        run(str(SCRIPT_DIR / "prepare_page_purpose.py"), "--case", str(intake_out), "--evidence", str(rich_assessment), "--package-root", str(root), "--out", str(purpose_out))
        context, repos, units = root / "context.json", root / "repos.json", root / "units.json"
        context.write_text(json.dumps({"records": [{"record_id": "affair-1", "authority_class": "formal_current", "allowed_use": "compare_only"}]}), encoding="utf-8")
        repos.write_text(json.dumps([{"repo_id": "github:example/tool", "repository": "example/tool", "source": {"url": "https://github.com/example/tool", "observed_at": "2026-07-29T00:00:00Z"}, "purpose": "fixture", "discussion_conclusion": {"status": "researched_candidate"}, "metrics_snapshot": {"stars": 1, "forks": 2, "watchers": 3, "observed_at": "2026-07-29T00:00:00Z"}, "updated_at": "2026-07-28T00:00:00Z", "freshness_state": "aging"}]), encoding="utf-8")
        units.write_text(json.dumps([{"unit_id": "repo-1", "type": "repo", "repository": "example/tool", "evidence_refs": ["span-1"]}]), encoding="utf-8")
        cards_out = root / "cards.json"
        run(str(SCRIPT_DIR / "build_action_cards.py"), "--case", str(intake_out), "--capture", str(rich_assessment), "--purpose", str(purpose_out), "--content-units", str(units), "--context", str(context), "--repos", str(repos), "--package-root", str(root), "--out", str(cards_out))
        cards = load(cards_out)
        assert cards["capture_status"] == "full_body_with_media_supplement"
        assert cards["page_purpose"] == "ready_for_semantic_interpretation"
        assert cards["github_snapshots"][0]["metrics_snapshot"]["watchers"] == 3
        assert cards["action_cards"][0]["recommendation"] == "research_refresh"
        assert cards["action_cards"][0]["user_decision_required"] is True
        assert cards["adoption_authorized"] is False

        if importlib.util.find_spec("certifi") is None:
            raise RuntimeError("certifi is required to validate the bounded local TLS retry")
        fake_workbuddy = root / "fake_workbuddy.py"
        fake_workbuddy.write_text(
            "import os, sys\nfrom pathlib import Path\n"
            "if not os.environ.get('SSL_CERT_FILE'):\n"
            "    print('CERTIFICATE_VERIFY_FAILED', file=sys.stderr)\n"
            "    raise SystemExit(7)\n"
            "out = Path(sys.argv[sys.argv.index('--out') + 1])\n"
            "out.mkdir(parents=True, exist_ok=True)\n"
            "(out / 'article.md').write_text('local fixture body', encoding='utf-8')\n"
            "print('[ok]', file=sys.stderr)\n",
            encoding="utf-8",
        )
        retry_dir = root / "tls-retry"
        run(str(SCRIPT_DIR / "run_workbuddy_capture.py"), "--url", "https://example.com/", "--package-root", str(root), "--out-dir", str(retry_dir), "--execute", "--network-authorized", "--workbuddy-script", str(fake_workbuddy), "--tls-strategy", "system")
        retry_receipt = load(retry_dir / "capture-execution-receipt.json")
        assert retry_receipt["status"] == "captured_pending_quality_gate"
        assert retry_receipt["limited_tls_retry_performed"] is True
        assert len(retry_receipt["attempts"]) == 2
        assert retry_receipt["attempts"][0]["certificate_failure_detected"] is True
        assert retry_receipt["attempts"][1]["tls_strategy"] == "certifi_bundle"
        assert all(item["tls_verification_disabled"] is False for item in retry_receipt["attempts"])
        assert all((root / item[key]["path"]).is_file() for item in retry_receipt["attempts"] for key in ("stdout", "stderr"))

    if args.out:
        write_json(
            args.out,
            {
                "schema": "web-bookmark-intelligence/candidate-validation/v2",
                "created_at": utc_now(),
                "offline_only": True,
                "network_calls": 0,
                "status": "passed",
                "checks": checks,
            },
            args.package_root.resolve(),
        )
    print("candidate_behavior=pass")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
