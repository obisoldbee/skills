#!/usr/bin/env python3
"""Shared, billing-safe request-state helpers for MiniMax media adapters."""

from __future__ import annotations

import hashlib
import json
import os
import stat
import tempfile
from pathlib import Path
from typing import Any


REQUEST_STATES = {
    "not_sent",
    "rejected",
    "accepted",
    "acceptance_unknown",
    "completed",
}


def canonical_json_bytes(value: Any) -> bytes:
    return json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    ).encode("utf-8")


def operation_fingerprint(endpoint: str, payload: dict[str, Any]) -> str:
    digest = hashlib.sha256()
    digest.update(endpoint.encode("utf-8"))
    digest.update(b"\0")
    digest.update(canonical_json_bytes(payload))
    return digest.hexdigest()


def provider_request_id(body: Any, headers: Any = None) -> str | None:
    if isinstance(body, dict):
        for key in ("request_id", "requestId", "id"):
            value = body.get(key)
            if isinstance(value, str) and value.strip():
                return value.strip()
    if headers is not None:
        for key in ("x-request-id", "x-minimax-request-id", "request-id"):
            value = headers.get(key)
            if value:
                return str(value)
    return None


def classify_response(result: dict[str, Any], text: str) -> tuple[str, str]:
    """Return request state and retry disposition.

    Only an explicit provider rejection can authorize an automatic resend. A
    transport failure after ``urlopen`` starts is acceptance-unknown, even when
    it looks like a connect or read timeout.
    """

    status_code = result.get("status_code")
    if result.get("ok") and isinstance(status_code, int) and 200 <= status_code < 300:
        if text.strip():
            return "completed", "completed_no_retry"
        return "accepted", "provider_accepted_empty_result_no_resubmit"

    if isinstance(status_code, int) and 400 <= status_code < 500:
        if status_code == 429:
            return "rejected", "retry_allowed_proven_not_accepted"
        return "rejected", "rejected_terminal_no_retry"

    if isinstance(status_code, int):
        return "acceptance_unknown", "provider_acceptance_unknown_no_resubmit"

    if result.get("not_sent") is True:
        return "not_sent", "retry_allowed_proven_not_sent"

    return "acceptance_unknown", "provider_acceptance_unknown_no_resubmit"


def atomic_write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    fd, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(fd, "w", encoding="utf-8") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass


def load_operation(path: Path) -> dict[str, Any] | None:
    if not path.is_file():
        return None
    if path.is_symlink():
        raise ValueError(f"operation state must not be a symlink: {path}")
    payload = json.loads(path.read_text(encoding="utf-8"))
    state = payload.get("state")
    if state not in REQUEST_STATES:
        raise ValueError(f"invalid saved request state: {state}")
    return payload


def response_reference(path: Path, operation_dir: Path) -> dict[str, str]:
    if path.parent.resolve() != operation_dir.resolve() or path.is_symlink() or not path.is_file():
        raise ValueError(f"response evidence must be a regular operation-local file: {path}")
    data = path.read_bytes()
    return {"path": path.name, "sha256": hashlib.sha256(data).hexdigest()}


def verified_response_evidence(
    operation_dir: Path,
    reference: object,
    expected_fingerprint: str,
    expected_state: str,
    expected_status_code: int | None = None,
) -> dict[str, Any]:
    """Read one operation-local response once and verify its complete binding."""
    if not isinstance(reference, dict):
        raise ValueError("response evidence reference must be an object")
    relative = reference.get("path")
    digest = reference.get("sha256")
    if (
        not isinstance(relative, str)
        or not relative
        or Path(relative).is_absolute()
        or len(Path(relative).parts) != 1
        or not isinstance(digest, str)
        or len(digest) != 64
    ):
        raise ValueError("response evidence reference is not operation-local and hash-bound")
    operation_dir = operation_dir.resolve()
    candidate = operation_dir / relative
    flags = os.O_RDONLY | getattr(os, "O_NOFOLLOW", 0)
    descriptor = os.open(candidate, flags)
    try:
        info = os.fstat(descriptor)
        if not stat.S_ISREG(info.st_mode):
            raise ValueError("response evidence is not a regular file")
        chunks: list[bytes] = []
        while True:
            chunk = os.read(descriptor, 1024 * 1024)
            if not chunk:
                break
            chunks.append(chunk)
    finally:
        os.close(descriptor)
    data = b"".join(chunks)
    if hashlib.sha256(data).hexdigest() != digest:
        raise ValueError("response evidence hash mismatch")
    try:
        payload = json.loads(data.decode("utf-8"))
    except (UnicodeDecodeError, json.JSONDecodeError) as exc:
        raise ValueError("response evidence is not valid JSON") from exc
    if not isinstance(payload, dict):
        raise ValueError("response evidence must be a JSON object")
    if payload.get("operation_fingerprint") != expected_fingerprint:
        raise ValueError("response evidence operation fingerprint mismatch")
    if payload.get("request_state") != expected_state:
        raise ValueError("response evidence request state mismatch")
    if expected_status_code is not None and payload.get("status_code") != expected_status_code:
        raise ValueError("response evidence status code mismatch")
    return payload


def validate_operation_chain(
    operation: dict[str, Any], operation_dir: Path
) -> list[dict[str, Any]]:
    attempts = operation.get("attempts")
    references = operation.get("response_evidence")
    if (
        not isinstance(attempts, list)
        or not attempts
        or not isinstance(references, list)
        or len(references) != len(attempts)
    ):
        raise ValueError("operation has no response evidence")
    fingerprint = operation.get("operation_fingerprint")
    if not isinstance(fingerprint, str):
        raise ValueError("operation fingerprint missing")
    verified: list[dict[str, Any]] = []
    for number, (attempt, reference) in enumerate(zip(attempts, references), 1):
        if not isinstance(attempt, dict) or attempt.get("attempt") != number:
            raise ValueError("operation attempt numbering is not contiguous")
        if attempt.get("response_evidence") != reference:
            raise ValueError("operation attempt and response evidence disagree")
        expected_path = f"attempt_{number:02d}.json"
        if not isinstance(reference, dict) or reference.get("path") != expected_path:
            raise ValueError("operation response path does not match attempt number")
        if attempt.get("expected_operation_fingerprint") != fingerprint:
            raise ValueError("operation attempt fingerprint binding mismatch")
        state = attempt.get("state")
        if state not in REQUEST_STATES:
            raise ValueError("operation attempt state is invalid")
        payload = verified_response_evidence(
            operation_dir,
            reference,
            fingerprint,
            str(state),
            attempt.get("status_code") if isinstance(attempt.get("status_code"), int) else None,
        )
        if (
            payload.get("status_code") != attempt.get("status_code")
            or payload.get("retry_disposition") != attempt.get("retry_disposition")
            or payload.get("provider_request_id") != attempt.get("provider_request_id")
        ):
            raise ValueError("operation attempt metadata does not match response evidence")
        verified.append(payload)
    return verified


def last_verified_response(
    operation: dict[str, Any],
    operation_dir: Path,
    expected_state: str,
    expected_status_code: int | None = None,
) -> dict[str, Any]:
    attempts = operation.get("attempts")
    verified = validate_operation_chain(operation, operation_dir)
    attempt = attempts[-1]
    if attempt.get("state") != expected_state:
        raise ValueError("operation attempt state mismatch")
    if expected_status_code is not None and attempt.get("status_code") != expected_status_code:
        raise ValueError("operation attempt status mismatch")
    return verified[-1]


def resume_disposition(operation: dict[str, Any] | None, operation_dir: Path) -> str:
    if not operation:
        return "new_operation"
    state = operation["state"]
    if state == "completed":
        try:
            response = last_verified_response(operation, operation_dir, "completed")
        except (OSError, ValueError):
            return "resume_terminal_without_resubmit"
        status_code = response.get("status_code")
        return "reuse_completed" if isinstance(status_code, int) and 200 <= status_code < 300 else "resume_terminal_without_resubmit"
    if state in {"accepted", "acceptance_unknown"}:
        return "resume_without_resubmit"
    if state == "rejected" and operation.get("retry_disposition") == "retry_allowed_proven_not_accepted":
        try:
            response = last_verified_response(operation, operation_dir, "rejected", 429)
        except (OSError, ValueError):
            return "resume_terminal_without_resubmit"
        if response.get("retry_disposition") == "retry_allowed_proven_not_accepted":
            return "retry_proven_safe"
    return "resume_terminal_without_resubmit"
