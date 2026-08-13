#!/usr/bin/env python3
"""Create a serial/resumable multi-URL plan on the same WorkBuddy capture pipeline."""

from __future__ import annotations

import argparse
import subprocess
import sys
from pathlib import Path

from common import ensure_within, read_json, stable_id, utc_now, write_json
from intake_case import canonical_url

TERMINAL_STATES = {"captured", "partial", "blocked", "failed"}
SHARED_CAPTURE_PIPELINE = "workbuddy_v1_5_1_shared"
WORKBUDDY_ADAPTER = "workbuddy_wechat_article_archive"


def load_urls(values: list[str], url_file: Path | None) -> list[str]:
    collected = [value.strip() for value in values if value.strip()]
    if url_file:
        collected.extend(line.strip() for line in url_file.read_text(encoding="utf-8").splitlines() if line.strip() and not line.lstrip().startswith("#"))
    return collected


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
        if existing and existing.get("status") in TERMINAL_STATES:
            cases.append(existing)
            continue
        host_matches = bool(canonical and "chinalowcarb.com" in canonical.split("/", 3)[2].lower())
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
            item["status"] = "captured" if completed.returncode == 0 else "failed"
            item["execution_returncode"] = completed.returncode
    elif execution_blocked:
        for item in cases:
            if item["status"] == "planned":
                item["status"] = "blocked"
                item["blocked_reason"] = "missing_network_authorization_or_workbuddy_script"

    batch = {
        "schema": "web-bookmark-intelligence/batch/v1",
        "created_at": utc_now(),
        "profile": args.profile,
        "capture_pipeline": SHARED_CAPTURE_PIPELINE,
        "workbuddy_adapter": WORKBUDDY_ADAPTER,
        "max_workers": 1,
        "resume_policy": "preserve_terminal_states",
        "formal_write_authorized": False,
        "cases": cases,
    }
    write_json(out_dir / "batch-plan.json", batch, root)
    write_json(state_path, batch, root)
    print(f"cases={len(cases)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
