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
import tarfile
import tempfile
import xml.etree.ElementTree as ET
from pathlib import Path
from typing import Any


PDF_MIN_BYTES = 5 * 1024
USER_AGENT = "Mozilla/5.0 Akashic paper-downloader; public OA route"


def load_rows(path: Path) -> list[dict[str, Any]]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and isinstance(data.get("rows"), list):
        return data["rows"]
    raise SystemExit(f"unsupported manifest shape: {path}")


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
    for key in ("local_path", "local_download_path", "local_source_path", "local_or_download_path"):
        value = clean_path_hint(row.get(key))
        if not value or not value.lower().endswith(".pdf"):
            continue
        raw = Path(value)
        candidates = [raw] if raw.is_absolute() else []
        for root in roots:
            candidates.append(root / value)
            if value.startswith("12-agent-submissions/"):
                candidates.extend(root.glob(f"12-agent-submissions/已处理/*/**/{Path(value).name}"))
        for candidate in candidates:
            if valid_pdf_file(candidate):
                paths.append(candidate)
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
        if not root.exists():
            continue
        for dirpath, _, filenames in os.walk(root):
            for filename in filenames:
                if not filename.lower().endswith(".pdf"):
                    continue
                path = Path(dirpath) / filename
                low = str(path).lower()
                if any(identifier in low for identifier in identifiers) and valid_pdf_file(path):
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
    path.write_bytes(data)
    return path


def process_row(row: dict[str, Any], args: argparse.Namespace, local_roots: list[Path]) -> dict[str, Any]:
    attempted: list[str] = []
    existing = scan_local_pdf(row, local_roots, recursive=not args.skip_recursive_local_scan)
    result = {
        "row_id": row.get("row_id", ""),
        "title": row.get("title", ""),
        "pmcid": row.get("pmcid", ""),
        "pmid": row.get("pmid", ""),
        "doi": row.get("doi", ""),
        "status": "failed",
        "local_path": "",
        "source_existing_path": "",
        "attempted_routes": attempted,
        "failure_reason": "",
        "file_size_bytes": 0,
        "sha256": "",
        "validated": False,
        "original_status": row.get("status", ""),
        "original_failure_reason": row.get("failure_reason", ""),
    }
    if existing:
        result.update(
            {
                "status": "already_local_pdf",
                "source_existing_path": str(existing),
                "failure_reason": "local_pdf_found_by_identifier_precheck",
                "file_size_bytes": existing.stat().st_size,
                "sha256": hashlib.sha256(existing.read_bytes()).hexdigest(),
                "validated": True,
            }
        )
        return result

    errors: list[str] = []

    for label, url in route_urls(row):
        if label == "doi_landing" and args.skip_doi_landing:
            continue
        attempted.append(url)
        data, final_url, meta = curl_bytes(url, args.timeout)
        if data and valid_pdf_bytes(data):
            path = write_pdf(args.paper_dir, row, data, label)
            attempted.append(f"final_url:{final_url}")
            result.update(
                {
                    "status": "downloaded",
                    "local_path": str(path),
                    "failure_reason": "",
                    "file_size_bytes": len(data),
                    "sha256": sha256(data),
                    "validated": True,
                }
            )
            return result
        if data:
            errors.append(f"{label}:not_pdf_or_too_small:{len(data)}:{meta}")
        else:
            errors.append(f"{label}:{meta}")

        if label == "europepmc_render" and data is None and "timed out" in meta.lower() and args.europepmc_timeout > args.timeout:
            attempted.append(f"{url}#retry_timeout_{args.europepmc_timeout}")
            data, final_url, meta = curl_bytes(url, args.europepmc_timeout)
            if data and valid_pdf_bytes(data):
                path = write_pdf(args.paper_dir, row, data, label)
                attempted.append(f"final_url:{final_url}")
                result.update(
                    {
                        "status": "downloaded",
                        "local_path": str(path),
                        "failure_reason": "",
                        "file_size_bytes": len(data),
                        "sha256": sha256(data),
                        "validated": True,
                    }
                )
                return result
            if data:
                errors.append(f"{label}_retry:not_pdf_or_too_small:{len(data)}:{meta}")
            else:
                errors.append(f"{label}_retry:{meta}")

    pmcid = str(row.get("pmcid") or "").strip()
    if pmcid and not args.skip_oa_package:
        routes, pdf, error = oa_package_routes(pmcid, args.timeout)
        attempted.extend(routes)
        if pdf:
            path = write_pdf(args.paper_dir, row, pdf, "ncbi_oa")
            result.update(
                {
                    "status": "downloaded",
                    "local_path": str(path),
                    "failure_reason": "",
                    "file_size_bytes": len(pdf),
                    "sha256": sha256(pdf),
                    "validated": True,
                }
            )
            return result
        errors.append(error)

    result["failure_reason"] = "; ".join(error for error in errors if error) or "no_route_succeeded"
    if "403" in result["failure_reason"] or "Just a moment" in result["failure_reason"]:
        result["status"] = "browser_required"
        result["failure_reason"] = (
            "browser_required_after_command_line_block: "
            + result["failure_reason"]
        )
    elif "idIsNotOpenAccess" in result["failure_reason"] or "no valid pdf" in result["failure_reason"].lower():
        result["status"] = "paywalled_or_no_pdf"
    return result


def write_status(path: Path, rows: list[dict[str, Any]]) -> None:
    counts: dict[str, int] = {}
    for row in rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    lines = [
        "# Download Status",
        "",
        "## Counts",
        "",
        *[f"- {key}: {value}" for key, value in sorted(counts.items())],
        "",
        "## Rows",
        "",
        "| row_id | status | local_path | source_existing_path | failure_reason |",
        "|---|---|---|---|---|",
    ]
    for row in rows:
        reason = str(row.get("failure_reason") or "").replace("|", "/")
        lines.append(
            f"| {row.get('row_id','')} | {row.get('status','')} | {row.get('local_path','')} | "
            f"{row.get('source_existing_path','')} | {reason} |"
        )
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
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

    args.paper_dir.mkdir(parents=True, exist_ok=True)
    args.manifest_out.parent.mkdir(parents=True, exist_ok=True)
    args.status_out.parent.mkdir(parents=True, exist_ok=True)

    rows = load_rows(args.input)
    if args.limit:
        rows = rows[: args.limit]

    local_roots = [root for root in args.local_root if root.exists()]
    out_rows = [process_row(row, args, local_roots) for row in rows]
    args.manifest_out.write_text(json.dumps(out_rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    write_status(args.status_out, out_rows)

    counts: dict[str, int] = {}
    for row in out_rows:
        counts[row["status"]] = counts.get(row["status"], 0) + 1
    print(json.dumps({"rows": len(out_rows), "counts": counts}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
