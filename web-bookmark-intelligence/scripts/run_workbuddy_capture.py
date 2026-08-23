#!/usr/bin/env python3
"""Plan or execute one hash-bound WorkBuddy route with fail-closed DNS policy."""

from __future__ import annotations

import argparse
import hashlib
import ipaddress
import os
import socket
import subprocess
import sys
import time
from pathlib import Path
from urllib.parse import urlparse

from common import ensure_within, package_relative, sha256_file, sha256_json, utc_now, write_json, write_text
from intake_case import canonical_url


WORKBUDDY_V1_5_1_SHA256 = "bb6f11eab11de44882b6563b012424ddd6b631197be4874fc1c4b7c0e29737df"
KNOWN_IMPLEMENTATIONS: dict[str, dict[str, str]] = {
    WORKBUDDY_V1_5_1_SHA256: {
        "implementation": "workbuddy_wechat_article_archive",
        "version": "v1.5.1",
        # The retained package proves capture output, not per-redirect DNS checks or IP pinning.
        "redirect_rebind_protection": "unproven",
    }
}
COMPATIBLE_REDIRECT_POLICIES = {"per_hop_dns_revalidation", "destination_ip_pinning"}


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


def normalized_ip(value: str) -> tuple[str, bool]:
    address = ipaddress.ip_address(value.split("%", 1)[0])
    if isinstance(address, ipaddress.IPv6Address) and address.ipv4_mapped is not None:
        address = address.ipv4_mapped
    return str(address), bool(address.is_global)


def resolve_dns_snapshot(hostname: str, resolver=socket.getaddrinfo) -> dict[str, object]:
    """Resolve A and AAAA records and reject empty, mixed, or non-public answers."""
    try:
        answers = resolver(hostname, None, socket.AF_UNSPEC, socket.SOCK_STREAM)
    except socket.gaierror as exc:
        return {
            "status": "blocked",
            "reason": "dns_nxdomain_or_failure",
            "error_code": exc.errno,
            "public_addresses": [],
            "blocked_addresses": [],
        }

    public: set[str] = set()
    blocked: set[str] = set()
    families: set[str] = set()
    for family, _socktype, _protocol, _canonname, sockaddr in answers:
        if family not in {socket.AF_INET, socket.AF_INET6} or not sockaddr:
            continue
        families.add("A" if family == socket.AF_INET else "AAAA")
        try:
            address, is_public = normalized_ip(str(sockaddr[0]))
        except ValueError:
            blocked.add(str(sockaddr[0]))
            continue
        (public if is_public else blocked).add(address)
    if not public and not blocked:
        reason = "dns_no_a_or_aaaa_records"
    elif blocked:
        reason = "dns_contains_non_public_or_mixed_addresses"
    else:
        reason = None
    return {
        "status": "passed" if reason is None else "blocked",
        "reason": reason,
        "families": sorted(families),
        "public_addresses": sorted(public),
        "blocked_addresses": sorted(blocked),
    }


def dns_rebinding_gate(hostname: str, resolver=socket.getaddrinfo) -> dict[str, object]:
    """Require two identical public snapshots before a compatible executor starts."""
    first = resolve_dns_snapshot(hostname, resolver)
    if first["status"] != "passed":
        return {"status": "blocked", "reason": first["reason"], "initial": first, "pre_dispatch": None}
    second = resolve_dns_snapshot(hostname, resolver)
    if second["status"] != "passed":
        return {"status": "blocked", "reason": second["reason"], "initial": first, "pre_dispatch": second}
    if first["public_addresses"] != second["public_addresses"]:
        return {"status": "blocked", "reason": "dns_resolution_changed", "initial": first, "pre_dispatch": second}
    return {
        "status": "passed",
        "reason": None,
        "initial": first,
        "pre_dispatch": second,
        "redirect_requirement": "executor must revalidate every hop or pin destination IPs",
    }


def identify_implementation(script: Path) -> dict[str, object]:
    resolved = script.resolve(strict=True)
    digest = sha256_file(resolved)
    known = KNOWN_IMPLEMENTATIONS.get(digest)
    return {
        "supplied_path": str(script),
        "resolved_path": str(resolved),
        "sha256_before": digest,
        "sha256_after": None,
        "recognized": known is not None,
        "implementation": known.get("implementation") if known else "unknown",
        "version": known.get("version") if known else None,
        "redirect_rebind_protection": known.get("redirect_rebind_protection") if known else "unknown",
    }


def artifact_inventory(attempt_root: Path, package_root: Path) -> list[dict[str, object]]:
    artifacts: list[dict[str, object]] = []
    for item in sorted(attempt_root.rglob("*")):
        if item.is_symlink():
            raise ValueError(f"workbuddy artifact symlink is not allowed: {item}")
        if item.is_file():
            ensure_within(item, attempt_root)
            artifacts.append(
                {
                    "path": package_relative(item, package_root),
                    "sha256": sha256_file(item),
                    "bytes": item.stat().st_size,
                }
            )
    return artifacts


def execute_attempt(
    command_prefix: list[str],
    implementation_path: Path,
    implementation_sha256: str,
    root: Path,
    out_dir: Path,
    attempt_number: int,
    strategy: str,
    timeout_seconds: int,
) -> dict[str, object]:
    implementation_bytes = implementation_path.read_bytes()
    if hashlib.sha256(implementation_bytes).hexdigest() != implementation_sha256:
        raise RuntimeError("implementation_changed_before_execution")
    attempt_root = ensure_within(out_dir / "workbuddy-output" / f"attempt-{attempt_number:02d}", root)
    attempt_root.mkdir(parents=True, exist_ok=True)
    environment, strategy_name = child_ssl_environment(strategy)
    logs = ensure_within(out_dir / "logs", root)
    logs.mkdir(parents=True, exist_ok=True)
    if len(command_prefix) < 2 or Path(command_prefix[1]).resolve() != implementation_path.resolve():
        raise RuntimeError("command_prefix_does_not_bind_resolved_implementation")
    # A same-owner attacker can replace even an O_EXCL/0500 path between our
    # hash check and the interpreter opening it. Execute the exact bytes already
    # read and hashed through Python's standard-input script mode instead.
    execution_sha256_before = hashlib.sha256(implementation_bytes).hexdigest()
    command = [
        command_prefix[0],
        "-",
        *command_prefix[2:],
        "--out",
        str(attempt_root),
    ]
    started_at = utc_now()
    monotonic_started = time.monotonic()
    stdout = ""
    stderr = ""
    returncode: int | None = None
    timed_out = False
    try:
        completed = subprocess.run(
            command,
            input=implementation_bytes,
            cwd=str(attempt_root),
            env=environment,
            capture_output=True,
            timeout=timeout_seconds,
            check=False,
        )
        stdout, stderr, returncode = (
            text_value(completed.stdout),
            text_value(completed.stderr),
            completed.returncode,
        )
    except subprocess.TimeoutExpired as exc:
        stdout, stderr, timed_out = text_value(exc.stdout), text_value(exc.stderr), True
    finished_at = utc_now()
    try:
        implementation_after = sha256_file(implementation_path)
    except OSError:
        implementation_after = None
    execution_sha256_after = hashlib.sha256(implementation_bytes).hexdigest()
    stdout_path = logs / f"attempt-{attempt_number:02d}.stdout.txt"
    stderr_path = logs / f"attempt-{attempt_number:02d}.stderr.txt"
    write_text(stdout_path, stdout, root)
    write_text(stderr_path, stderr, root)
    artifact_error: str | None = None
    try:
        artifacts = artifact_inventory(attempt_root, root)
    except ValueError as exc:
        artifacts = []
        artifact_error = str(exc)
    article_candidates = [item for item in artifacts if str(item["path"]).endswith("/article.md")]
    return {
        "attempt": attempt_number,
        "started_at": started_at,
        "finished_at": finished_at,
        "elapsed_seconds": round(time.monotonic() - monotonic_started, 3),
        "tls_strategy": strategy_name,
        "tls_verification_disabled": False,
        "command": command,
        "command_sha256": sha256_json(
            {"argv": command, "stdin_sha256": execution_sha256_before}
        ),
        "execution_input": {
            "transport": "python_stdin",
            "bytes": len(implementation_bytes),
            "sha256_before": execution_sha256_before,
            "sha256_after": execution_sha256_after,
            "unchanged": execution_sha256_after == execution_sha256_before,
            "matches_verified_source": execution_sha256_before == implementation_sha256,
        },
        "implementation_sha256_before": implementation_sha256,
        "implementation_sha256_after": implementation_after,
        "implementation_unchanged": implementation_after == implementation_sha256,
        "returncode": returncode,
        "timed_out": timed_out,
        "certificate_failure_detected": is_certificate_failure(f"{stdout}\n{stderr}"),
        "stdout": {"path": package_relative(stdout_path, root), "sha256": sha256_file(stdout_path)},
        "stderr": {"path": package_relative(stderr_path, root), "sha256": sha256_file(stderr_path)},
        "artifacts": artifacts,
        "artifact_inventory_sha256": sha256_json(artifacts),
        "artifact_error": artifact_error,
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
    record: dict[str, object] = {
        "schema": "web-bookmark-intelligence/workbuddy-capture/v3",
        "created_at": utc_now(),
        "source_url": url or args.url,
        "required_implementation": {
            "implementation": "workbuddy_wechat_article_archive",
            "version": "v1.5.1",
            "sha256": WORKBUDDY_V1_5_1_SHA256,
        },
        "observed_implementation": None,
        "mode": effective_mode,
        "network_executed": False,
        "status": "planned",
        "blocked_reason": blocked_reason,
        "quality_gate_required_after_capture": True,
        "meta_description_is_never_body_pass": True,
        "tls_verification_disabled": False,
        "dns_gate": {"status": "not_run"},
        "tls_retry_policy": {
            "maximum_retry_count": 1,
            "eligible_only": "initial system-trust certificate verification failure with certifi available",
            "never_retry": ["success", "timeout", "non_tls_error", "certifi_attempt_failure", "implementation_drift"],
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
        record["status"] = "planned_needs_implementation_and_network_safety_proof"
        write_json(out_dir / "capture-plan.json", record, root)
        print("planned")
        return 0

    if not args.network_authorized:
        record["status"] = "blocked"
        record["blocked_reason"] = "missing_network_authorization"
        write_json(out_dir / "capture-execution-receipt.json", record, root)
        print("blocked")
        return 2
    if not args.workbuddy_script or not args.workbuddy_script.is_file():
        record["status"] = "needs_compatible_executor"
        record["blocked_reason"] = "missing_workbuddy_script"
        write_json(out_dir / "capture-execution-receipt.json", record, root)
        print("needs_compatible_executor")
        return 2

    try:
        implementation = identify_implementation(args.workbuddy_script)
    except (OSError, ValueError) as exc:
        record["status"] = "needs_compatible_executor"
        record["blocked_reason"] = f"implementation_unreadable:{exc}"
        write_json(out_dir / "capture-execution-receipt.json", record, root)
        print("needs_compatible_executor")
        return 2
    record["observed_implementation"] = implementation
    if implementation["recognized"] is not True:
        record["status"] = "needs_compatible_executor"
        record["blocked_reason"] = "unrecognized_workbuddy_implementation_hash"
        write_json(out_dir / "capture-execution-receipt.json", record, root)
        print("needs_compatible_executor")
        return 2
    if implementation["redirect_rebind_protection"] not in COMPATIBLE_REDIRECT_POLICIES:
        record["status"] = "needs_compatible_executor"
        record["blocked_reason"] = "executor_does_not_prove_per_hop_dns_revalidation_or_ip_pinning"
        write_json(out_dir / "capture-execution-receipt.json", record, root)
        print("needs_compatible_executor")
        return 2

    hostname = urlparse(url).hostname or ""
    dns_gate = dns_rebinding_gate(hostname)
    record["dns_gate"] = dns_gate
    if dns_gate["status"] != "passed":
        record["status"] = "blocked"
        record["blocked_reason"] = dns_gate["reason"]
        write_json(out_dir / "capture-execution-receipt.json", record, root)
        print("blocked")
        return 2

    implementation_path = Path(str(implementation["resolved_path"]))
    implementation_sha = str(implementation["sha256_before"])
    initial_strategy = "system" if args.tls_strategy == "auto" else args.tls_strategy
    command_prefix = [sys.executable, str(implementation_path), url, "--mode", effective_mode]
    attempts: list[dict[str, object]] = []
    try:
        attempts.append(
            execute_attempt(
                command_prefix,
                implementation_path,
                implementation_sha,
                root,
                out_dir,
                1,
                initial_strategy,
                args.timeout_seconds,
            )
        )
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
        and first["implementation_unchanged"] is True
        and first["artifact_error"] is None
        and certifi_bundle() is not None
    )
    if eligible_retry:
        try:
            attempts.append(
                execute_attempt(
                    command_prefix,
                    implementation_path,
                    implementation_sha,
                    root,
                    out_dir,
                    2,
                    "certifi",
                    args.timeout_seconds,
                )
            )
        except RuntimeError as exc:
            record.update(status="failed", blocked_reason=str(exc), attempts=attempts)
            write_json(out_dir / "capture-execution-receipt.json", record, root)
            print("failed")
            return 1

    final = attempts[-1]
    implementation["sha256_after"] = final["implementation_sha256_after"]
    success = (
        final["returncode"] == 0
        and final["timed_out"] is False
        and final["implementation_unchanged"] is True
        and final["execution_input"]["unchanged"] is True
        and final["execution_input"]["matches_verified_source"] is True
        and final["artifact_error"] is None
        and bool(final["article_candidates"])
    )
    record.update(
        network_executed=True,
        status="captured_pending_quality_gate" if success else "failed",
        observed_implementation=implementation,
        command_prefix=command_prefix,
        command_prefix_sha256=sha256_json(command_prefix),
        attempts=attempts,
        limited_tls_retry_performed=len(attempts) == 2,
        article_candidates=final["article_candidates"],
        final_artifact_inventory_sha256=final["artifact_inventory_sha256"],
    )
    if not success:
        if final["implementation_unchanged"] is not True:
            record["blocked_reason"] = "implementation_changed_during_execution"
        elif final["artifact_error"]:
            record["blocked_reason"] = "unsafe_or_unreadable_workbuddy_artifact"
        elif not final["article_candidates"]:
            record["blocked_reason"] = "workbuddy_exit_zero_without_article_artifact" if final["returncode"] == 0 else "workbuddy_execution_failed"
        else:
            record["blocked_reason"] = "workbuddy_timeout" if final["timed_out"] else "workbuddy_execution_failed"
    write_json(out_dir / "capture-execution-receipt.json", record, root)
    print(record["status"])
    return 0 if success else 1


if __name__ == "__main__":
    raise SystemExit(main())
