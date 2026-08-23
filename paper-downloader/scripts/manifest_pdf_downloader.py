#!/usr/bin/env python3
"""Download PDFs for a manifest with local precheck and public OA routes.

This script is intentionally dependency-light: it uses the system `curl`
instead of Python TLS stacks or Playwright so it can run in Codex environments
where Python certificates or browser modules are not aligned.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import re
import subprocess
import sys
import tarfile
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any

SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from manifest_contract import (  # noqa: E402
    PDF_MIN_BYTES,
    atomic_create_bytes,
    atomic_write_bytes,
    declared_output_path,
    declared_output_root,
    empty_pdf_receipt,
    exact_status_counts,
    is_within,
    load_manifest,
    relative_output_path,
    require_distinct_paths,
    save_manifest,
    sha256_file,
    utc_now,
    verify_downloaded_collection,
    verify_pdf,
)

USER_AGENT = "Mozilla/5.0 Akashic paper-downloader; public OA route"


def load_rows(path: Path) -> list[dict[str, Any]]:
    return load_manifest(path)["rows"]


def safe_name(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())
    return re.sub(r"_+", "_", value).strip("_")[:180] or "paper"


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def valid_pdf_bytes(data: bytes) -> bool:
    return len(data) > PDF_MIN_BYTES and data[:4] == b"%PDF"


def valid_pdf_file(path: Path) -> bool:
    try:
        if not path.is_file() or path.stat().st_size <= PDF_MIN_BYTES:
            return False
        with path.open("rb") as stream:
            return stream.read(4) == b"%PDF"
    except OSError:
        return False


def clean_path_hint(value: Any) -> str:
    text = str(value or "").strip().strip("`")
    if not text or text in {"-", "none", "None", "null"}:
        return ""
    return text


def hinted_local_paths(row: dict[str, Any], roots: list[Path]) -> list[Path]:
    paths: list[Path] = []
    approved_roots = [root.expanduser().resolve() for root in roots]
    for key in ("local_path", "local_download_path", "local_source_path", "local_or_download_path"):
        value = clean_path_hint(row.get(key))
        if not value or not value.lower().endswith(".pdf"):
            continue
        raw = Path(value)
        candidates: list[Path] = []
        for root in approved_roots:
            candidates.append(root / value)
            if value.startswith("12-agent-submissions/"):
                candidates.extend(root.glob(f"12-agent-submissions/已处理/*/**/{Path(value).name}"))
        for candidate in candidates:
            resolved = candidate.expanduser().resolve()
            if any(is_within(resolved, root) for root in approved_roots) and valid_pdf_file(resolved):
                paths.append(resolved)
    return paths


def curl_bytes(url: str, timeout: int) -> tuple[bytes | None, str, str]:
    cmd = [
        "curl",
        "-L",
        "--fail",
        "--silent",
        "--show-error",
        "--max-time",
        str(timeout),
        "--connect-timeout",
        str(min(15, max(5, timeout // 2))),
        "-A",
        USER_AGENT,
        "-w",
        "\\n%{url_effective}\\n%{content_type}\\n%{http_code}",
        url,
    ]
    proc = subprocess.run(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, check=False)
    if proc.returncode != 0:
        err = proc.stderr.decode("utf-8", errors="replace").strip()
        return None, "", f"curl_exit_{proc.returncode}:{err}"

    raw = proc.stdout
    parts = raw.rsplit(b"\n", 3)
    if len(parts) != 4:
        return raw, url, "content_type_unknown"
    body, final_url, content_type, http_code = parts
    meta = f"{content_type.decode(errors='replace')} http={http_code.decode(errors='replace')}"
    return body, final_url.decode("utf-8", errors="replace"), meta


def doi_variants(doi: str) -> list[str]:
    doi = doi.lower().strip()
    if not doi:
        return []
    variants = [
        doi,
        doi.replace("/", "_").replace(".", "-"),
        re.sub(r"[^a-z0-9]+", "-", doi).strip("-"),
        re.sub(r"[^a-z0-9]+", "_", doi).strip("_"),
        re.sub(r"[^a-z0-9]+", "", doi),
    ]
    return list(dict.fromkeys(variants))


def row_identifiers(row: dict[str, Any]) -> list[str]:
    values: list[str] = []
    for key in ("pmcid", "pmid"):
        value = str(row.get(key) or "").strip()
        if value:
            values.append(value.lower())
    values.extend(doi_variants(str(row.get("doi") or "")))
    return [v for v in dict.fromkeys(values) if len(v) >= 5]


def scan_local_pdf(row: dict[str, Any], roots: list[Path], recursive: bool = True) -> Path | None:
    hints = hinted_local_paths(row, roots)
    if hints:
        return hints[0]

    if not recursive:
        return None

    identifiers = row_identifiers(row)
    if not identifiers:
        return None
    for root in roots:
        approved_root = root.expanduser().resolve()
        if not approved_root.exists():
            continue
        for dirpath, _, filenames in os.walk(approved_root):
            for filename in filenames:
                if not filename.lower().endswith(".pdf"):
                    continue
                path = (Path(dirpath) / filename).resolve()
                low = str(path).lower()
                if (
                    is_within(path, approved_root)
                    and any(identifier in low for identifier in identifiers)
                    and valid_pdf_file(path)
                ):
                    return path
    return None


def extract_pdf_from_tgz(data: bytes) -> tuple[bytes | None, str]:
    try:
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:gz") as archive:
            members = [
                member
                for member in archive.getmembers()
                if member.isfile() and member.name.lower().endswith(".pdf")
            ]
            members.sort(key=lambda member: ("/" in member.name.strip("/"), len(member.name)))
            for member in members:
                f = archive.extractfile(member)
                if not f:
                    continue
                pdf = f.read()
                if valid_pdf_bytes(pdf):
                    return pdf, member.name
    except Exception as exc:  # noqa: BLE001
        return None, f"tgz_extract_error:{type(exc).__name__}:{exc}"
    return None, "tgz_contains_no_valid_pdf"


def oa_package_routes(pmcid: str, timeout: int) -> tuple[list[str], bytes | None, str]:
    routes = [f"https://www.ncbi.nlm.nih.gov/pmc/utils/oa/oa.fcgi?id={pmcid}"]
    xml_bytes, _, meta = curl_bytes(routes[0], timeout)
    if not xml_bytes:
        return routes, None, f"oa_api_error:{meta}"
    try:
        root = ET.fromstring(xml_bytes)
    except ET.ParseError as exc:
        return routes, None, f"oa_api_parse_error:{exc}"
    error = root.find(".//error")
    if error is not None:
        code = error.get("code") or "unknown"
        text = (error.text or "").strip()
        return routes, None, f"oa_api_error:{code}:{text}"
    link = root.find(".//link[@format='tgz']")
    if link is None:
        return routes, None, "oa_api_no_tgz_link"
    href = link.get("href") or ""
    if href.startswith("ftp://ftp.ncbi.nlm.nih.gov/"):
        href = "https://ftp.ncbi.nlm.nih.gov/" + href[len("ftp://ftp.ncbi.nlm.nih.gov/") :]
    routes.append(href)
    tgz, final_url, tgz_meta = curl_bytes(href, timeout * 2)
    if not tgz:
        return routes, None, f"oa_tgz_error:{tgz_meta}"
    pdf, member_or_error = extract_pdf_from_tgz(tgz)
    if pdf:
        routes.append(f"oa_member:{member_or_error}")
        routes.append(f"oa_final_url:{final_url}")
        return routes, pdf, ""
    return routes, None, f"oa_tgz_extract_failed:{member_or_error}"


def route_urls(row: dict[str, Any]) -> list[tuple[str, str]]:
    urls: list[tuple[str, str]] = []
    pmcid = str(row.get("pmcid") or "").strip()
    if pmcid:
        urls.extend(
            [
                ("europepmc_render", f"https://europepmc.org/articles/{pmcid}?pdf=render"),
                ("pmc_pdf", f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/pdf/"),
            ]
        )
    pdf_url = str(row.get("pdf_url") or "").strip()
    if pdf_url:
        urls.append(("provided_pdf_url", pdf_url))
    doi = str(row.get("doi") or "").strip()
    if doi:
        urls.append(("doi_landing", f"https://doi.org/{doi}"))
    return urls


def write_pdf(out_dir: Path, row: dict[str, Any], data: bytes, suffix: str) -> Path:
    row_id = safe_name(str(row.get("row_id") or "row"))
    ident = safe_name(str(row.get("pmcid") or row.get("pmid") or row.get("doi") or row_id))
    path = out_dir / f"{row_id}__{ident}__{suffix}.pdf"
    atomic_create_bytes(path, data)
    return path


def identity_for_route(label: str, row: dict[str, Any], evidence: str) -> tuple[str | None, str]:
    if label in {"europepmc_render", "pmc_pdf", "ncbi_oa"} and row.get("pmcid"):
        return "pmcid_route", evidence
    if label == "doi_landing" and row.get("doi"):
        return "doi_route", evidence
    if label == "provided_pdf_url":
        compact = re.sub(r"[^a-z0-9]+", "", evidence.lower())
        for kind in ("pmcid", "pmid", "doi"):
            value = re.sub(r"[^a-z0-9]+", "", str(row.get(kind) or "").lower())
            if value and value in compact:
                return f"{kind}_route", evidence
    return None, evidence


def bind_pdf_result(result: dict[str, Any], receipt: dict[str, Any]) -> None:
    result["pdf"] = receipt
    if receipt["validated"]:
        result["status"] = "downloaded"
        result["failure_reason"] = ""
        result["pubmed_followup_required"] = False
        result["pmcid_followup_required"] = False
    else:
        result["status"] = "needs_manual_review"
        result["failure_reason"] = receipt["failure_reason"]


def process_row(row: dict[str, Any], args: argparse.Namespace, local_roots: list[Path]) -> dict[str, Any]:
    output_root = declared_output_root(args.output_root)
    result = dict(row)
    result.setdefault("attempts", [])
    result.setdefault("pdf", empty_pdf_receipt())
    result.setdefault("pubmed_full_text_checked", False)
    result.setdefault("pubmed_full_text_links", [])
    result.setdefault("pubmed_followup_required", False)
    result.setdefault("pmcid_followup_required", False)
    if result.get("disposition") not in {None, "", "eligible"}:
        return result
    if result.get("status") in {"duplicate", "unverified_citation", "verified_abstract"}:
        return result

    recorded = result.get("pdf") if isinstance(result.get("pdf"), dict) else {}
    recorded_path = str(recorded.get("path") or "")
    if recorded_path:
        resume_receipt = verify_pdf(
            output_root / recorded_path,
            output_root,
            result,
            identity_match_method=recorded.get("identity_match", {}).get("claimed_method"),
            identity_match_evidence=recorded.get("identity_match", {}).get("claimed_evidence"),
        )
        if resume_receipt["validated"]:
            if (
                resume_receipt["bytes"] != recorded.get("bytes")
                or resume_receipt["sha256"] != recorded.get("sha256")
            ):
                result["status"] = "needs_manual_review"
                result["failure_reason"] = "recorded_pdf_receipt_mismatch"
            else:
                bind_pdf_result(result, resume_receipt)
            return result
        if Path(recorded_path).suffix.lower() == ".pdf":
            result["pdf"] = resume_receipt
            result["status"] = "needs_manual_review"
            result["failure_reason"] = resume_receipt["failure_reason"]
            return result

    existing = scan_local_pdf(row, local_roots, recursive=not args.skip_recursive_local_scan)
    if existing:
        existing_data = existing.read_bytes()
        resolved_paper_dir = args.paper_dir.expanduser().resolve()
        destination = (
            existing
            if is_within(existing.resolve(), resolved_paper_dir)
            else write_pdf(args.paper_dir, row, existing_data, "local")
        )
        receipt = verify_pdf(
            destination,
            output_root,
            result,
            identity_match_method="local_file_readback",
            identity_match_evidence=None,
        )
        result["attempts"].append(
            {
                "route": "local_identifier_precheck",
                "outcome": "downloaded" if receipt["validated"] else "needs_manual_review",
                "source_name": existing.name,
                "source_sha256": sha256(existing_data),
                "pdf": receipt,
            }
        )
        bind_pdf_result(result, receipt)
        return result

    # A non-pending row has already completed or exited the first-pass lane.
    # Reruns may recover disk evidence above, but must not repeat network routes
    # or downgrade its exact queue/terminal outcome.
    if result.get("status") != "pending":
        return result

    errors: list[str] = []

    for label, url in route_urls(row):
        if label == "doi_landing" and args.skip_doi_landing:
            continue
        attempt: dict[str, Any] = {"route": label, "url": url}
        data, final_url, meta = curl_bytes(url, args.timeout)
        if data and valid_pdf_bytes(data):
            path = write_pdf(args.paper_dir, row, data, label)
            method, evidence = identity_for_route(label, result, final_url or url)
            receipt = verify_pdf(
                path,
                output_root,
                result,
                identity_match_method=method,
                identity_match_evidence=evidence,
            )
            attempt.update({"final_url": final_url, "outcome": "downloaded" if receipt["validated"] else "needs_manual_review", "pdf": receipt})
            result["attempts"].append(attempt)
            bind_pdf_result(result, receipt)
            return result
        if data:
            errors.append(f"{label}:not_pdf_or_too_small:{len(data)}:{meta}")
            attempt.update({"outcome": "not_pdf_or_too_small", "response_bytes": len(data), "detail": meta})
        else:
            errors.append(f"{label}:{meta}")
            attempt.update({"outcome": "request_failed", "detail": meta})
        result["attempts"].append(attempt)

        if label == "europepmc_render" and data is None and "timed out" in meta.lower() and args.europepmc_timeout > args.timeout:
            retry_attempt: dict[str, Any] = {"route": label, "url": url, "retry_reason": "proven_no_response_timeout"}
            data, final_url, meta = curl_bytes(url, args.europepmc_timeout)
            if data and valid_pdf_bytes(data):
                path = write_pdf(args.paper_dir, row, data, label)
                receipt = verify_pdf(
                    path,
                    output_root,
                    result,
                    identity_match_method="pmcid_route",
                    identity_match_evidence=final_url or url,
                )
                retry_attempt.update({"final_url": final_url, "outcome": "downloaded" if receipt["validated"] else "needs_manual_review", "pdf": receipt})
                result["attempts"].append(retry_attempt)
                bind_pdf_result(result, receipt)
                return result
            if data:
                errors.append(f"{label}_retry:not_pdf_or_too_small:{len(data)}:{meta}")
                retry_attempt.update({"outcome": "not_pdf_or_too_small", "response_bytes": len(data), "detail": meta})
            else:
                errors.append(f"{label}_retry:{meta}")
                retry_attempt.update({"outcome": "request_failed", "detail": meta})
            result["attempts"].append(retry_attempt)

    pmcid = str(row.get("pmcid") or "").strip()
    if pmcid and not args.skip_oa_package:
        routes, pdf, error = oa_package_routes(pmcid, args.timeout)
        attempt = {"route": "ncbi_oa", "route_evidence": routes}
        if pdf:
            path = write_pdf(args.paper_dir, row, pdf, "ncbi_oa")
            receipt = verify_pdf(
                path,
                output_root,
                result,
                identity_match_method="pmcid_route",
                identity_match_evidence=" ".join(routes),
            )
            attempt.update({"outcome": "downloaded" if receipt["validated"] else "needs_manual_review", "pdf": receipt})
            result["attempts"].append(attempt)
            bind_pdf_result(result, receipt)
            return result
        attempt.update({"outcome": "request_failed", "detail": error})
        result["attempts"].append(attempt)
        errors.append(error)

    result["failure_reason"] = "; ".join(error for error in errors if error) or "no_route_succeeded"
    result["status"] = "browser_required"
    result["failure_reason"] = "browser_followup_required_after_first_pass: " + result["failure_reason"]
    if str(result.get("pmcid") or "").strip() and result["status"] != "downloaded":
        result["pmcid_followup_required"] = True
        if result["status"] not in {"manual_browser_required", "browser_required"}:
            result["status"] = "browser_required"
            result["failure_reason"] = "pmcid_followup_required: " + result["failure_reason"]
    if (
        str(result.get("pmid") or "").strip()
        and result["status"] != "downloaded"
        and result.get("pubmed_full_text_checked") is not True
    ):
        result["pubmed_followup_required"] = True
        if result["status"] not in {"manual_browser_required", "browser_required"}:
            result["status"] = "browser_required"
            result["failure_reason"] = "pubmed_full_text_followup_required: " + result["failure_reason"]
    return result


def write_status(path: Path, rows: list[dict[str, Any]]) -> dict[str, Any]:
    counts = exact_status_counts(rows)
    lines = [
        "# Download Status",
        "",
        "## Counts",
        "",
        *[f"- {key}: {value}" for key, value in sorted(counts.items())],
        "",
        "## Rows",
        "",
        "| row_id | status | pdf_path | pdf_bytes | failure_reason |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        reason = str(row.get("failure_reason") or "").replace("|", "/")
        lines.append(
            f"| {row.get('row_id','')} | {row.get('status','')} | {row.get('pdf',{}).get('path','')} | "
            f"{row.get('pdf',{}).get('bytes',0)} | {reason} |"
        )
    return atomic_write_bytes(path, ("\n".join(lines) + "\n").encode("utf-8"))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--paper-dir", required=True, type=Path)
    parser.add_argument("--manifest-out", required=True, type=Path)
    parser.add_argument("--status-out", required=True, type=Path)
    parser.add_argument("--local-root", action="append", default=[], type=Path)
    parser.add_argument("--timeout", default=60, type=int)
    parser.add_argument("--europepmc-timeout", default=75, type=int)
    parser.add_argument("--limit", default=0, type=int)
    parser.add_argument(
        "--workers",
        default=1,
        type=int,
        help="Network acquisition is serialized; this value must be 1.",
    )
    parser.add_argument("--skip-doi-landing", action="store_true")
    parser.add_argument("--skip-oa-package", action="store_true")
    parser.add_argument("--skip-recursive-local-scan", action="store_true")
    args = parser.parse_args()

    if args.workers != 1:
        parser.error(
            "--workers must be 1 because paper acquisition is serialized through "
            "the shared egress IP"
        )
    if args.limit:
        parser.error("--limit would violate frozen inventory coverage; build a separate frozen inventory instead")

    args.output_root = declared_output_root(args.output_root)
    args.input = declared_output_path(args.input, args.output_root)
    args.paper_dir = declared_output_path(args.paper_dir, args.output_root)
    args.manifest_out = declared_output_path(args.manifest_out, args.output_root)
    args.status_out = declared_output_path(args.status_out, args.output_root)
    require_distinct_paths(
        input_manifest=args.input,
        manifest_out=args.manifest_out,
        status_out=args.status_out,
    )
    for label, path in (
        ("input manifest", args.input),
        ("manifest output", args.manifest_out),
        ("status output", args.status_out),
    ):
        if is_within(path, args.paper_dir):
            parser.error(f"{label} must not be inside --paper-dir")
    manifest = load_manifest(args.input, output_root=args.output_root)
    source_manifest_sha = sha256_file(args.input)
    rows = manifest["rows"]

    local_roots = [args.paper_dir, *[root for root in args.local_root if root.exists()]]
    out_rows = [process_row(row, args, local_roots) for row in rows]
    manifest["rows"] = out_rows
    manifest["paper_root"] = args.paper_dir.relative_to(args.output_root).as_posix()
    manifest["reconciled_at"] = utc_now()
    verify_downloaded_collection(manifest, args.output_root)
    if sha256_file(args.input) != source_manifest_sha:
        raise ValueError("source manifest changed before first-pass manifest write")
    manifest_receipt = save_manifest(args.manifest_out, manifest, args.output_root)
    status_receipt = write_status(args.status_out, out_rows)
    reread = load_manifest(args.manifest_out, output_root=args.output_root)
    disk = verify_downloaded_collection(reread, args.output_root)

    counts = exact_status_counts(out_rows)
    print(
        json.dumps(
            {
                "rows": len(out_rows),
                "counts": counts,
                "manifest": {
                    "path": relative_output_path(args.manifest_out, args.output_root),
                    **manifest_receipt,
                },
                "status": {
                    "path": relative_output_path(args.status_out, args.output_root),
                    **status_receipt,
                },
                "disk": disk,
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
