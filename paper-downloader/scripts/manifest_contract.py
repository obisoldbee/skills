#!/usr/bin/env python3
"""Canonical manifest, path, PDF, and atomic-write contracts."""

from __future__ import annotations

import hashlib
import json
import os
import re
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import unquote, urlsplit


SCHEMA = "paper-downloader/download-manifest/v2"
JOURNAL_SCHEMA = "paper-downloader/browser-result-journal/v1"
REPORT_RECEIPT_SCHEMA = "paper-downloader/final-report-receipt/v1"
PDF_MIN_BYTES = 5120
PACKAGE_ROOT = Path(__file__).resolve().parents[1]

ALLOWED_STATUSES = {
    "pending",
    "downloaded",
    "verified_abstract",
    "browser_required",
    "manual_browser_required",
    "paywalled",
    "paywalled_or_no_pdf",
    "access_blocked",
    "unverified_citation",
    "duplicate",
    "needs_manual_review",
    "failed",
}
TERMINAL_NON_DOWNLOAD_STATUSES = {
    "verified_abstract",
    "paywalled",
    "access_blocked",
    "unverified_citation",
    "duplicate",
    "needs_manual_review",
    "failed",
}
IDENTITY_METHODS = {
    "pdf_bytes_doi",
    "pdf_bytes_pmid",
    "pdf_bytes_pmcid",
    "pdf_title_metadata",
}
ROW_BINDING_FIELDS = (
    "row_id",
    "source_row_id",
    "source_coordinate",
    "source_row",
    "title",
    "doi",
    "pmid",
    "pmcid",
    "pdf_url",
    "source_origin",
    "input_url",
    "original_publication_url",
    "disposition",
    "duplicate_of",
)


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def is_within(path: Path, root: Path) -> bool:
    try:
        path.relative_to(root)
    except ValueError:
        return False
    return True


def declared_output_root(value: Path) -> Path:
    root = value.expanduser().resolve()
    if (
        root == PACKAGE_ROOT
        or is_within(root, PACKAGE_ROOT)
        or is_within(PACKAGE_ROOT, root)
    ):
        raise ValueError(
            "declared output root must not be the Skill package/source root "
            "or one of its ancestors"
        )
    return root


def declared_output_path(value: Path, output_root: Path, *, allow_root: bool = False) -> Path:
    root = declared_output_root(output_root)
    path = value.expanduser()
    path = (root / path).resolve() if not path.is_absolute() else path.resolve()
    if is_within(path, PACKAGE_ROOT):
        raise ValueError(f"output path resolves inside the Skill package/source root: {value}")
    if not is_within(path, root) or (path == root and not allow_root):
        raise ValueError(f"output path escapes declared output root: {value}")
    return path


def relative_output_path(path: Path, output_root: Path) -> str:
    return declared_output_path(path, output_root).relative_to(declared_output_root(output_root)).as_posix()


def require_distinct_paths(**paths: Path) -> None:
    """Reject aliases among named paths after resolving symlinks and relatives."""

    seen: dict[Path, str] = {}
    for name, value in paths.items():
        resolved = value.expanduser().resolve()
        previous = seen.get(resolved)
        if previous is not None:
            raise ValueError(f"path alias is forbidden: {previous} == {name}: {resolved}")
        seen[resolved] = name


def atomic_write_bytes(path: Path, data: bytes) -> dict[str, Any]:
    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        os.replace(temporary, path)
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
    reread = path.read_bytes()
    if reread != data:
        raise RuntimeError(f"atomic write readback mismatch: {path}")
    return {"bytes": len(reread), "sha256": sha256_bytes(reread)}


def atomic_create_bytes(path: Path, data: bytes) -> dict[str, Any]:
    """Persist complete bytes without ever replacing an existing target."""

    path.parent.mkdir(parents=True, exist_ok=True)
    descriptor, temporary = tempfile.mkstemp(prefix=f".{path.name}.", dir=path.parent)
    try:
        with os.fdopen(descriptor, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())
        try:
            os.link(temporary, path)
        except FileExistsError as exc:
            raise ValueError(f"target CAS failed; path already exists: {path.name}") from exc
    finally:
        try:
            os.unlink(temporary)
        except FileNotFoundError:
            pass
    reread = path.read_bytes()
    if reread != data:
        raise RuntimeError(f"exclusive create readback mismatch: {path}")
    return {"bytes": len(reread), "sha256": sha256_bytes(reread)}


def atomic_write_json(path: Path, payload: Any) -> dict[str, Any]:
    data = (json.dumps(payload, ensure_ascii=False, indent=2) + "\n").encode("utf-8")
    receipt = atomic_write_bytes(path, data)
    if json.loads(path.read_text(encoding="utf-8")) != payload:
        raise RuntimeError(f"JSON readback mismatch: {path}")
    return receipt


def normalized_identifier(kind: str, value: Any) -> str:
    text = unquote(str(value or "").strip())
    if kind == "doi":
        text = re.sub(r"^doi\s*:\s*", "", text, flags=re.IGNORECASE)
        parsed = urlsplit(text)
        if parsed.scheme.lower() in {"http", "https"} and parsed.netloc.lower() in {
            "doi.org",
            "dx.doi.org",
            "www.doi.org",
        }:
            text = parsed.path.lstrip("/")
        text = text.strip().rstrip(".,;)\"'").lower()
        if re.fullmatch(r"10\.\d{4,9}/[^\s]+", text):
            return text
        return ""
    if kind == "pmcid":
        text = re.sub(r"(?i)^pmcid\s*:?\s*", "", text).strip()
        parsed = urlsplit(text)
        if parsed.scheme.lower() in {"http", "https"} and parsed.netloc.lower() in {
            "pmc.ncbi.nlm.nih.gov",
            "www.pmc.ncbi.nlm.nih.gov",
            "www.ncbi.nlm.nih.gov",
        }:
            path_match = re.fullmatch(r"(?i)/(?:pmc/)?articles/(PMC\d+)/?", parsed.path)
            text = path_match.group(1) if path_match else ""
        text = text.strip().rstrip(".,;")
        text = re.sub(r"^[\[(]\s*|\s*[\])]$", "", text).strip().rstrip(".,;")
        match = re.fullmatch(r"(?i)PMC\d+", text)
        return match.group(0).upper() if match else ""
    if kind == "pmid":
        text = re.sub(r"(?i)^pmid\s*:?\s*", "", text).strip()
        parsed = urlsplit(text)
        if parsed.scheme.lower() in {"http", "https"} and parsed.netloc.lower() in {
            "pubmed.ncbi.nlm.nih.gov",
            "www.pubmed.ncbi.nlm.nih.gov",
        }:
            path_match = re.fullmatch(r"/(\d+)/?", parsed.path)
            text = path_match.group(1) if path_match else ""
        text = text.strip().rstrip(".,;")
        text = re.sub(r"^[\[(]\s*|\s*[\])]$", "", text).strip().rstrip(".,;")
        match = re.fullmatch(r"\d+", text)
        return match.group(0) if match else ""
    return ""


def canonical_identity(row: dict[str, Any]) -> dict[str, str] | None:
    for kind in ("pmcid", "pmid", "doi"):
        value = normalized_identifier(kind, row.get(kind))
        if value:
            return {"kind": kind, "value": value}
    return None


def identity_key(row: dict[str, Any]) -> str:
    identity = canonical_identity(row)
    if identity:
        return f"{identity['kind']}:{identity['value']}"
    title = re.sub(r"\s+", " ", str(row.get("title") or "").strip().lower())
    return f"title:{title}" if title else ""


def row_binding_projection(row: dict[str, Any]) -> dict[str, Any]:
    return {field: row.get(field) for field in ROW_BINDING_FIELDS}


def rows_binding_sha256(rows: Iterable[dict[str, Any]]) -> str:
    payload = [row_binding_projection(row) for row in rows]
    data = json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return sha256_bytes(data)


def _normalize_title(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "").strip())


def _decode_pdf_literal(value: bytes) -> str:
    value = re.sub(rb"\\([()\\])", rb"\1", value)
    value = value.replace(b"\\n", b"\n").replace(b"\\r", b"\r").replace(b"\\t", b"\t")
    return value.decode("utf-8", errors="replace")


def _pdf_info_object(data: bytes) -> bytes:
    info_reference: tuple[bytes, bytes] | None = None
    for trailer in reversed(list(re.finditer(rb"\btrailer\s*<<(.*?)>>", data, flags=re.DOTALL))):
        match = re.search(rb"/Info\s+(\d+)\s+(\d+)\s+R\b", trailer.group(1))
        if match:
            info_reference = (match.group(1), match.group(2))
            break
    if info_reference is None:
        return b""
    object_pattern = (
        rb"(?m)(?<!\d)"
        + re.escape(info_reference[0])
        + rb"\s+"
        + re.escape(info_reference[1])
        + rb"\s+obj\b(.*?)\bendobj\b"
    )
    match = re.search(object_pattern, data, flags=re.DOTALL)
    return match.group(1) if match else b""


def _pdf_title(data: bytes) -> str:
    info = _pdf_info_object(data)
    if not info:
        return ""
    literal = re.search(rb"/Title\s*\(((?:\\.|[^\\)])*)\)", info, flags=re.DOTALL)
    if literal:
        return _decode_pdf_literal(literal.group(1))
    hexadecimal = re.search(rb"/Title\s*<([0-9A-Fa-f]+)>", info)
    if not hexadecimal:
        return ""
    try:
        raw = bytes.fromhex(hexadecimal.group(1).decode("ascii"))
    except ValueError:
        return ""
    if raw.startswith(b"\xfe\xff"):
        return raw[2:].decode("utf-16-be", errors="replace")
    return raw.decode("utf-8", errors="replace")


def _strict_identifier_in_pdf(data: bytes, kind: str, value: str) -> bool:
    text = data.decode("latin-1", errors="ignore")
    escaped = re.escape(value)
    if kind == "doi":
        pattern = (
            rf"(?i)(?<![A-Za-z0-9])"
            rf"(?:doi\s*:\s*|https?://(?:dx\.)?doi\.org/)?"
            rf"{escaped}(?=$|\s|[<>\]\[\"']|[.,;)](?=$|\s|[<>\]\[\"']))"
        )
    elif kind == "pmcid":
        pattern = rf"(?i)(?<![A-Za-z0-9]){escaped}(?![A-Za-z0-9])"
    else:
        pattern = rf"(?i)(?<![A-Za-z0-9])PMID\s*:\s*{escaped}(?![0-9])"
    return re.search(pattern, text) is not None


def _identity_matches(
    row: dict[str, Any],
    data: bytes,
) -> tuple[bool, str | None, str | None, str]:
    for kind in ("pmcid", "pmid", "doi"):
        value = normalized_identifier(kind, row.get(kind))
        if value and _strict_identifier_in_pdf(data, kind, value):
            return True, f"pdf_bytes_{kind}", value, "identifier_found_in_pdf_bytes"
    expected_title = _normalize_title(row.get("title"))
    observed_title = _pdf_title(data)
    if expected_title and _normalize_title(observed_title) == expected_title:
        return True, "pdf_title_metadata", observed_title, "pdf_title_metadata_exact"
    return False, None, None, "identifier_or_exact_title_not_found_in_pdf_bytes"


def verify_pdf(
    path: Path,
    output_root: Path,
    row: dict[str, Any],
    *,
    identity_match_method: str | None,
    identity_match_evidence: str | None,
) -> dict[str, Any]:
    root = declared_output_root(output_root)
    try:
        resolved = declared_output_path(path, root)
    except ValueError as exc:
        return {
            "validated": False,
            "path": str(path),
            "failure_reason": "path_escape",
            "detail": str(exc),
            "bytes": 0,
            "sha256": "",
            "magic": "",
            "identity_match": {"method": identity_match_method, "evidence": identity_match_evidence, "matched": False},
        }
    if not resolved.is_file():
        return {
            "validated": False,
            "path": resolved.relative_to(root).as_posix(),
            "failure_reason": "pdf_missing",
            "bytes": 0,
            "sha256": "",
            "magic": "",
            "identity_match": {"method": identity_match_method, "evidence": identity_match_evidence, "matched": False},
        }
    data = resolved.read_bytes()
    magic = data[:4].decode("latin-1", "replace")
    identity_matched, derived_method, derived_evidence, identity_reason = _identity_matches(row, data)
    failure_reason = ""
    if len(data) <= PDF_MIN_BYTES:
        failure_reason = "pdf_not_larger_than_5120_bytes"
    elif data[:4] != b"%PDF":
        failure_reason = "pdf_magic_mismatch"
    elif not identity_matched:
        failure_reason = "identity_needs_manual_review"
    return {
        "validated": not failure_reason,
        "path": resolved.relative_to(root).as_posix(),
        "bytes": len(data),
        "sha256": sha256_bytes(data),
        "magic": magic,
        "failure_reason": failure_reason,
        "identity_match": {
            "method": derived_method,
            "evidence": derived_evidence,
            "matched": identity_matched,
            "reason": identity_reason,
            "claimed_method": identity_match_method,
            "claimed_evidence": identity_match_evidence,
        },
    }


def empty_pdf_receipt() -> dict[str, Any]:
    return {
        "validated": False,
        "path": "",
        "bytes": 0,
        "sha256": "",
        "magic": "",
        "failure_reason": "not_downloaded",
        "identity_match": {"method": None, "evidence": None, "matched": False, "reason": "not_checked"},
    }


def validate_manifest(payload: Any, *, output_root: Path | None = None) -> dict[str, Any]:
    if not isinstance(payload, dict) or payload.get("schema") != SCHEMA:
        raise ValueError(f"manifest must use schema {SCHEMA}")
    inventory = payload.get("inventory")
    rows = payload.get("rows")
    if not isinstance(inventory, dict) or not isinstance(rows, list):
        raise ValueError("manifest must contain inventory object and rows array")
    row_ids = [str(row.get("row_id") or "") for row in rows if isinstance(row, dict)]
    if len(row_ids) != len(rows) or any(not row_id for row_id in row_ids):
        raise ValueError("every manifest row requires a canonical row_id")
    if len(row_ids) != len(set(row_ids)):
        raise ValueError("canonical row_id values must be unique")
    if inventory.get("row_count") != len(rows):
        raise ValueError("inventory row_count does not match manifest rows")
    if inventory.get("row_ids") != row_ids:
        raise ValueError("inventory row_ids do not exactly match manifest row order")
    if inventory.get("format") not in {"markdown", "csv"}:
        raise ValueError("inventory format must be exactly markdown or csv")
    sha = str(inventory.get("sha256") or "")
    if not re.fullmatch(r"[0-9a-f]{64}", sha):
        raise ValueError("inventory sha256 is missing or invalid")
    rows_sha = str(inventory.get("rows_sha256") or "")
    if not re.fullmatch(r"[0-9a-f]{64}", rows_sha):
        raise ValueError("inventory rows_sha256 is missing or invalid")
    if rows_sha != rows_binding_sha256(rows):
        raise ValueError("inventory rows_sha256 does not match frozen row bindings")
    global_attempt_ids: set[str] = set()
    root: Path | None = None
    paper_root: Path | None = None
    if output_root is not None:
        root = declared_output_root(output_root)
        paper_root_text = str(payload.get("paper_root") or "")
        if not paper_root_text or Path(paper_root_text).is_absolute():
            raise ValueError("manifest paper_root must be a non-empty relative output-root path")
        paper_root = declared_output_path(Path(paper_root_text), root)
        if paper_root.relative_to(root).as_posix() != paper_root_text:
            raise ValueError("manifest paper_root must be normalized relative POSIX path")
    for row in rows:
        status = row.get("status")
        if status not in ALLOWED_STATUSES:
            raise ValueError(f"invalid exact status {status!r} for {row.get('row_id')}")
        if "download_status" in row:
            raise ValueError(f"dual status/download_status fields are forbidden: {row.get('row_id')}")
        pdf = row.get("pdf")
        if not isinstance(pdf, dict):
            raise ValueError(f"row pdf receipt missing: {row.get('row_id')}")
        attempts = row.get("attempts")
        if not isinstance(attempts, list):
            raise ValueError(f"row attempts must be an array: {row.get('row_id')}")
        row_identity = canonical_identity(row)
        for attempt in attempts:
            if not isinstance(attempt, dict):
                raise ValueError(f"row attempt must be an object: {row.get('row_id')}")
            route = str(attempt.get("route") or "")
            is_browser_attempt = route.startswith("browser") or route.endswith("_browser")
            attempt_id = str(attempt.get("attempt_id") or "").strip()
            if is_browser_attempt and not attempt_id:
                raise ValueError(f"browser attempt lacks attempt_id: {row.get('row_id')}")
            if attempt_id:
                if attempt_id in global_attempt_ids:
                    raise ValueError(f"global manifest attempt_id collision: {attempt_id}")
                global_attempt_ids.add(attempt_id)
                if attempt.get("row_id") != row.get("row_id") or attempt.get("identity") != row_identity:
                    raise ValueError(
                        f"manifest attempt row/identity binding mismatch: {row.get('row_id')}:{attempt_id}"
                    )
        if "file_size_kb" in row or "file_size_bytes" in row:
            raise ValueError(f"split/ambiguous size fields are forbidden: {row.get('row_id')}")
        for kind in ("doi", "pmid", "pmcid"):
            value = str(row.get(kind) or "")
            if value and normalized_identifier(kind, value) != value:
                raise ValueError(f"row {kind} is not canonical: {row.get('row_id')}")
        recorded_pdf_path = str(pdf.get("path") or "")
        if recorded_pdf_path:
            if not isinstance(pdf.get("bytes"), int) or pdf.get("bytes", 0) < 0:
                raise ValueError(f"PDF receipt bytes must be a non-negative integer: {row.get('row_id')}")
            if not re.fullmatch(r"[0-9a-f]{64}", str(pdf.get("sha256") or "")):
                raise ValueError(f"PDF receipt sha256 is missing or invalid: {row.get('row_id')}")
            if pdf.get("bytes", 0) <= PDF_MIN_BYTES or pdf.get("magic") != "%PDF":
                raise ValueError(f"recorded PDF receipt is not structurally valid: {row.get('row_id')}")
            if root is not None:
                if Path(recorded_pdf_path).is_absolute():
                    raise ValueError(f"PDF receipt path must be output-root relative: {row.get('row_id')}")
                resolved_pdf = declared_output_path(Path(recorded_pdf_path), root)
                if resolved_pdf.relative_to(root).as_posix() != recorded_pdf_path:
                    raise ValueError(f"PDF receipt path must be normalized: {row.get('row_id')}")
                if paper_root is not None and not is_within(resolved_pdf, paper_root):
                    raise ValueError(f"PDF receipt path is outside paper_root: {row.get('row_id')}")
        elif (
            pdf.get("validated") is True
            or pdf.get("bytes") not in {None, 0}
            or str(pdf.get("sha256") or "")
            or str(pdf.get("magic") or "")
        ):
            raise ValueError(f"pathless PDF receipt contains claimed disk evidence: {row.get('row_id')}")
        if status == "downloaded" and pdf.get("validated") is not True:
            raise ValueError(f"downloaded row lacks a validated PDF receipt: {row.get('row_id')}")
        if status == "downloaded":
            if not recorded_pdf_path:
                raise ValueError(f"downloaded row lacks a PDF path: {row.get('row_id')}")
            if str(row.get("failure_reason") or ""):
                raise ValueError(f"downloaded row must not retain a failure reason: {row.get('row_id')}")
            identity = pdf.get("identity_match") if isinstance(pdf.get("identity_match"), dict) else {}
            if identity.get("matched") is not True or identity.get("method") not in IDENTITY_METHODS:
                raise ValueError(f"downloaded row lacks actual PDF identity evidence: {row.get('row_id')}")
        if status == "duplicate":
            duplicate_of = str(row.get("duplicate_of") or "")
            if not duplicate_of or duplicate_of == row.get("row_id") or duplicate_of not in row_ids:
                raise ValueError(f"duplicate row lacks valid canonical lineage: {row.get('row_id')}")
        if status == "unverified_citation" and canonical_identity(row) is not None:
            raise ValueError(
                f"unverified_citation row retains a stable canonical identity: {row.get('row_id')}"
            )
    if root is not None:
        recorded = Path(str(payload.get("declared_output_root") or "")).expanduser().resolve()
        if recorded != root:
            raise ValueError("manifest declared_output_root does not match the CLI output root")
    return payload


def load_manifest(path: Path, *, output_root: Path | None = None) -> dict[str, Any]:
    return validate_manifest(json.loads(path.read_text(encoding="utf-8")), output_root=output_root)


def save_manifest(path: Path, payload: dict[str, Any], output_root: Path) -> dict[str, Any]:
    root = declared_output_root(output_root)
    target = declared_output_path(path, root)
    validate_manifest(payload, output_root=root)
    receipt = atomic_write_json(target, payload)
    load_manifest(target, output_root=root)
    return receipt


def pdf_files(root: Path) -> list[str]:
    if not root.exists():
        return []
    return sorted(
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() == ".pdf"
    )


def verify_downloaded_collection(manifest: dict[str, Any], output_root: Path) -> dict[str, Any]:
    root = declared_output_root(output_root)
    paper_root = declared_output_path(Path(str(manifest.get("paper_root") or "papers")), root, allow_root=True)
    expected: set[str] = set()
    failures: list[str] = []
    claimed_by_path: dict[str, str] = {}
    claimed_by_sha: dict[str, str] = {}
    for row in manifest["rows"]:
        recorded = row["pdf"]
        recorded_path = str(recorded.get("path") or "")
        if not recorded_path:
            if row["status"] == "downloaded":
                failures.append(f"{row['row_id']}:downloaded_pdf_path_missing")
            continue
        receipt = verify_pdf(
            root / recorded_path,
            root,
            row,
            identity_match_method=recorded.get("identity_match", {}).get("method"),
            identity_match_evidence=recorded.get("identity_match", {}).get("evidence"),
        )
        identity_only_failure = receipt["failure_reason"] == "identity_needs_manual_review"
        candidate_allowed = row["status"] == "needs_manual_review" and identity_only_failure
        if not receipt["validated"] and not candidate_allowed:
            failures.append(f"{row['row_id']}:{receipt['failure_reason']}")
            continue
        if receipt["bytes"] != recorded.get("bytes") or receipt["sha256"] != recorded.get("sha256"):
            failures.append(f"{row['row_id']}:pdf_receipt_mismatch")
        if row["status"] == "downloaded" and recorded.get("validated") is not True:
            failures.append(f"{row['row_id']}:downloaded_receipt_not_validated")
        if row["status"] != "downloaded" and not candidate_allowed:
            failures.append(f"{row['row_id']}:pdf_claim_requires_downloaded_or_identity_review_status")
        previous = claimed_by_path.get(receipt["path"])
        if previous and previous != row["row_id"]:
            failures.append(
                f"{row['row_id']}:pdf_path_already_claimed_by:{previous}"
            )
        else:
            claimed_by_path[receipt["path"]] = row["row_id"]
        previous_sha = claimed_by_sha.get(receipt["sha256"])
        if previous_sha and previous_sha != row["row_id"]:
            failures.append(
                f"{row['row_id']}:pdf_sha_already_claimed_by:{previous_sha}"
            )
        else:
            claimed_by_sha[receipt["sha256"]] = row["row_id"]
        try:
            expected.add(
                Path(receipt["path"])
                .relative_to(paper_root.relative_to(root))
                .as_posix()
            )
        except ValueError:
            failures.append(f"{row['row_id']}:pdf_outside_declared_paper_root")
    actual = set(pdf_files(paper_root))
    missing = sorted(expected - actual)
    extra = sorted(actual - expected)
    if missing:
        failures.extend(f"missing_pdf:{path}" for path in missing)
    if extra:
        failures.extend(f"extra_pdf:{path}" for path in extra)
    if failures:
        raise ValueError("; ".join(failures))
    return {"expected_pdf_files": sorted(expected), "actual_pdf_files": sorted(actual)}


def exact_status_counts(rows: Iterable[dict[str, Any]]) -> dict[str, int]:
    counts = {status: 0 for status in sorted(ALLOWED_STATUSES)}
    for row in rows:
        status = row.get("status")
        if status not in ALLOWED_STATUSES:
            raise ValueError(f"invalid exact status: {status}")
        counts[status] += 1
    return {status: count for status, count in counts.items() if count}
