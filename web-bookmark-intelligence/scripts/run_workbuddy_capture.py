#!/usr/bin/env python3
"""Plan or execute the one WorkBuddy capture route with auditable TLS receipts."""

from __future__ import annotations

import argparse
import os
import subprocess
import sys
import time
from pathlib import Path

from common import ensure_within, sha256_file, utc_now, write_json, write_text
from intake_case import canonical_url


def certifi_bundle() -> str | None:
    try:
        import certifi  # type: ignore

        return certifi.where()
    except Exception:
        return None


def child_ssl_environment(strategy: str) -> tuple[dict[str, str], str]:
    """Return a verified TLS child environment; no unverified mode exists."""
    environment = os.environ.copy()
    bundle = certifi_bundle()
    if strategy == "certifi":
        if not bundle:
            raise RuntimeError("certifi_not_available")
        environment["SSL_CERT_FILE"] = bundle
        environment["REQUESTS_CA_BUNDLE"] = bundle
        return environment, "certifi_bundle"
    environment.pop("SSL_CERT_FILE", None)
    environment.pop("REQUESTS_CA_BUNDLE", None)
    return environment, "system_trust_store"


def is_certificate_failure(text: str) -> bool:
    normalized = text.lower()
    signals = (
        "certificate_verify_failed",
        "certificate verify failed",
        "ssl certificate problem",
        "unable to get local issuer certificate",
        "[ssl: cert",
    )
    return any(signal in normalized for signal in signals)


def text_value(value: object) -> str:
    if isinstance(value, bytes):
        return value.decode("utf-8", errors="replace")
    return str(value or "")


def execute_attempt(
    command_prefix: list[str],
    root: Path,
    out_dir: Path,
    attempt_number: int,
    strategy: str,
    timeout_seconds: int,
) -> dict[str, object]:
    attempt_root = ensure_within(out_dir / "workbuddy-output" / f"attempt-{attempt_number:02d}", root)
    attempt_root.mkdir(parents=True, exist_ok=True)
    environment, strategy_name = child_ssl_environment(strategy)
    command = [*command_prefix, "--out", str(attempt_root)]
    logs = ensure_within(out_dir / "logs", root)
    started_at = utc_now()
    monotonic_started = time.monotonic()
    stdout = ""
    stderr = ""
    returncode: int | None = None
    timed_out = False
    try:
        completed = subprocess.run(
            command,
            cwd=str(attempt_root),
            env=environment,
            capture_output=True,
            text=True,
            timeout=timeout_seconds,
            check=False,
        )
        stdout, stderr, returncode = completed.stdout, completed.stderr, completed.returncode
    except subprocess.TimeoutExpired as exc:
        stdout, stderr, timed_out = text_value(exc.stdout), text_value(exc.stderr), True
    finished_at = utc_now()
    stdout_path = logs / f"attempt-{attempt_number:02d}.stdout.txt"
    stderr_path = logs / f"attempt-{attempt_number:02d}.stderr.txt"
    write_text(stdout_path, stdout, root)
    write_text(stderr_path, stderr, root)
    article_candidates = [str(item.relative_to(root)) for item in attempt_root.rglob("article.md")]
    return {
        "attempt": attempt_number,
        "started_at": started_at,
        "finished_at": finished_at,
        "elapsed_seconds": round(time.monotonic() - monotonic_started, 3),
        "tls_strategy": strategy_name,
        "tls_verification_disabled": False,
        "returncode": returncode,
        "timed_out": timed_out,
        "certificate_failure_detected": is_certificate_failure(f"{stdout}\n{stderr}"),
        "stdout": {"path": str(stdout_path.relative_to(root)), "sha256": sha256_file(stdout_path)},
        "stderr": {"path": str(stderr_path.relative_to(root)), "sha256": sha256_file(stderr_path)},
        "article_candidates": article_candidates,
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--url", required=True)
    parser.add_argument("--package-root", type=Path, required=True)
    parser.add_argument("--out-dir", type=Path, required=True)
    parser.add_argument("--mode", choices=["auto", "static", "textblock", "playwright", "playwright-ocr"], default="auto")
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--network-authorized", action="store_true")
    parser.add_argument("--workbuddy-script", type=Path)
    parser.add_argument("--timeout-seconds", type=int, default=120)
    parser.add_argument("--tls-strategy", choices=["auto", "system", "certifi"], default="auto")
    args = parser.parse_args()

    root = args.package_root.resolve()
    out_dir = ensure_within(args.out_dir, root)
    url, blocked_reason = canonical_url(args.url)
    effective_mode = "playwright" if args.mode == "auto" else args.mode
    bundle_available = certifi_bundle() is not None
    record: dict[str, object] = {
        "schema": "web-bookmark-intelligence/workbuddy-capture/v2",
        "created_at": utc_now(),
        "source_url": url or args.url,
        "capture_implementation": "workbuddy_wechat_article_archive",
        "baseline_version": "v1.5.1",
        "mode": effective_mode,
        "network_executed": False,
        "status": "planned",
        "blocked_reason": blocked_reason,
        "quality_gate_required_after_capture": True,
        "meta_description_is_never_body_pass": True,
        "tls_verification_disabled": False,
        "tls_retry_policy": {
            "maximum_retry_count": 1,
            "eligible_only": "initial system-trust certificate verification failure with certifi available",
            "never_retry": ["success", "timeout", "non_tls_error", "certifi_attempt_failure"],
        },
        "formal_write_authorized": False,
    }
    if blocked_reason:
        record["status"] = "blocked"
        write_json(out_dir / "capture-plan.json", record, root)
        print("blocked")
        return 0

    if not args.execute:
        record["planned_initial_tls_strategy"] = "system_trust_store" if args.tls_strategy == "auto" else f"{args.tls_strategy}_trust_store"
        write_json(out_dir / "capture-plan.json", record, root)
        print("planned")
        return 0

    if not args.network_authorized:
        record["status"] = "blocked"
        record["blocked_reason"] = "missing_network_authorization"
        write_json(out_dir / "capture-plan.json", record, root)
        print("blocked")
        return 2
    if not args.workbuddy_script or not args.workbuddy_script.is_file():
        record["status"] = "blocked"
        record["blocked_reason"] = "missing_workbuddy_script"
        write_json(out_dir / "capture-plan.json", record, root)
        print("blocked")
        return 2

    initial_strategy = "system" if args.tls_strategy == "auto" else args.tls_strategy
    command_prefix = [sys.executable, str(args.workbuddy_script.resolve()), url, "--mode", effective_mode]
    attempts: list[dict[str, object]] = []
    try:
        attempts.append(execute_attempt(command_prefix, root, out_dir, 1, initial_strategy, args.timeout_seconds))
    except RuntimeError as exc:
        record.update(status="failed", blocked_reason=str(exc), attempts=attempts)
        write_json(out_dir / "capture-execution-receipt.json", record, root)
        print("failed")
        return 1

    first = attempts[0]
    eligible_retry = (
        first["returncode"] not in {0, None}
        and first["timed_out"] is False
        and first["tls_strategy"] == "system_trust_store"
        and first["certificate_failure_detected"] is True
        and bundle_available
    )
    if eligible_retry:
        attempts.append(execute_attempt(command_prefix, root, out_dir, 2, "certifi", args.timeout_seconds))

    final = attempts[-1]
    success = final["returncode"] == 0 and final["timed_out"] is False
    record.update(
        network_executed=True,
        status="captured_pending_quality_gate" if success else "failed",
        attempts=attempts,
        limited_tls_retry_performed=len(attempts) == 2,
        article_candidates=final["article_candidates"],
    )
    if not success:
        record["blocked_reason"] = "workbuddy_timeout" if final["timed_out"] else "workbuddy_execution_failed"
    write_json(out_dir / "capture-execution-receipt.json", record, root)
    print(record["status"])
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
