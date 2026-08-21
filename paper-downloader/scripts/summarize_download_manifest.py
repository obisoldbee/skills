#!/usr/bin/env python3
"""Write download coverage and failed-download reports from downloader outputs."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlsplit


def load_rows(path: Path) -> list[dict[str, Any]]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(payload, list):
        return [row for row in payload if isinstance(row, dict)]
    if isinstance(payload, dict) and isinstance(payload.get("rows"), list):
        return [row for row in payload["rows"] if isinstance(row, dict)]
    raise SystemExit(f"unsupported manifest shape: {path}")


def status_of(row: dict[str, Any]) -> str:
    return str(row.get("status") or row.get("download_status") or "unknown")


def has_identifier(row: dict[str, Any]) -> bool:
    return any(str(row.get(key) or "").strip() for key in ("doi", "pmid", "pmcid", "pdf_url"))


def non_download_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    out = []
    for row in rows:
        status = status_of(row).lower()
        if status in {"downloaded", "already_local_pdf", "local_existing", "verified_fulltext"}:
            continue
        if "downloaded" in status:
            continue
        out.append(row)
    return out


def browser_attempted_non_download(row: dict[str, Any]) -> bool:
    status = status_of(row).lower()
    reason = str(row.get("failure_reason") or "").lower()
    routes = " ".join(str(x).lower() for x in row.get("attempted_routes") or [])
    browser_statuses = {
        "failed",
        "manual_browser_required",
        "paywalled",
        "paywalled_or_no_pdf",
        "needs_manual_review",
    }
    return (
        status in browser_statuses
        or "browser" in status
        or "browser" in reason
        or "doi.org" in routes
        or "publisher" in routes
    )


def _http_link(label: str, url: str) -> str:
    parsed = urlsplit(url)
    if parsed.scheme not in {"http", "https"} or not parsed.netloc:
        return ""
    encoded = quote(url, safe=":/?&=#%+@;,$!'*-._~")
    return f"[{label}]({encoded})"


def reference_links(row: dict[str, Any]) -> str:
    links: list[str] = []
    doi = str(row.get("doi") or "").strip()
    pmid = str(row.get("pmid") or "").strip()
    pmcid = str(row.get("pmcid") or "").strip().upper()

    if doi:
        links.append(_http_link("DOI", f"https://doi.org/{doi}"))
    if re.fullmatch(r"\d+", pmid):
        links.append(_http_link("PubMed", f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/"))
    if re.fullmatch(r"PMC\d+", pmcid):
        links.append(_http_link("PMC", f"https://pmc.ncbi.nlm.nih.gov/articles/{pmcid}/"))

    observed = _http_link("observed", str(row.get("observed_url") or "").strip())
    if observed:
        links.append(observed)
    return " / ".join(link for link in links if link)


def write_coverage(args: argparse.Namespace, rows: list[dict[str, Any]]) -> None:
    counts = Counter(status_of(row) for row in rows)
    identifier_count = sum(1 for row in rows if has_identifier(row))
    missing_reason = [
        row
        for row in non_download_rows(rows)
        if not str(row.get("failure_reason") or "").strip()
    ]
    missing_screenshot = [
        row
        for row in non_download_rows(rows)
        if browser_attempted_non_download(row)
        and not str(row.get("failure_screenshot_path") or row.get("failure_screenshot_error") or "").strip()
    ]
    lines = [
        "# Download Coverage",
        "",
        f"- manifest: `{args.manifest}`",
        f"- source_inventory: `{args.inventory}`" if args.inventory else "- source_inventory: not_provided",
        f"- source_inventory_rows: {args.inventory_rows if args.inventory_rows is not None else 'unknown'}",
        f"- downloader_rows: {len(rows)}",
        f"- rows_with_identifier: {identifier_count}",
        f"- rows_missing_failure_reason: {len(missing_reason)}",
        f"- browser_non_download_rows_missing_screenshot_or_error: {len(missing_screenshot)}",
        "",
        "## Status Counts",
        "",
    ]
    for status, count in sorted(counts.items()):
        lines.append(f"- {status}: {count}")
    lines.extend(
        [
            "",
            "## Coverage Boundary",
            "",
            args.note or "No extra coverage note supplied.",
            "",
        ]
    )
    if missing_reason:
        lines.extend(["## Rows Missing Failure Reason", ""])
        for row in missing_reason:
            lines.append(f"- `{row.get('row_id') or row.get('id') or 'unknown'}`: {row.get('title','')}")
        lines.append("")
    if missing_screenshot:
        lines.extend(["## Browser Rows Missing Failure Screenshot", ""])
        for row in missing_screenshot:
            lines.append(f"- `{row.get('row_id') or row.get('id') or 'unknown'}`: {row.get('title','')}")
        lines.append("")
    args.coverage_out.parent.mkdir(parents=True, exist_ok=True)
    args.coverage_out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def write_failed(args: argparse.Namespace, rows: list[dict[str, Any]]) -> None:
    failed = non_download_rows(rows)
    lines = [
        "# Failed Downloads",
        "",
        "| row_id | status | pmcid | pmid | doi | source_links | failure_reason | screenshot | observed_url | observed_title | attempted_routes |",
        "|---|---|---|---|---|---|---|---|---|---|---|",
    ]
    for row in failed:
        reason = str(row.get("failure_reason") or "").replace("|", "/")
        screenshot = str(row.get("failure_screenshot_path") or row.get("failure_screenshot_error") or "").replace("|", "/")
        observed_url = str(row.get("observed_url") or "").replace("|", "/")
        observed_title = str(row.get("observed_title") or "").replace("|", "/")
        routes = "; ".join(str(x) for x in row.get("attempted_routes") or [])
        routes = routes.replace("|", "/")
        lines.append(
            f"| {row.get('row_id') or row.get('id') or ''} | {status_of(row)} | "
            f"{row.get('pmcid','')} | {row.get('pmid','')} | {row.get('doi','')} | "
            f"{reference_links(row)} | {reason} | {screenshot} | {observed_url} | {observed_title} | {routes} |"
        )
    args.failed_out.parent.mkdir(parents=True, exist_ok=True)
    args.failed_out.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--coverage-out", required=True, type=Path)
    parser.add_argument("--failed-out", required=True, type=Path)
    parser.add_argument("--inventory", type=Path)
    parser.add_argument("--inventory-rows", type=int)
    parser.add_argument("--note", default="")
    args = parser.parse_args()

    rows = load_rows(args.manifest)
    write_coverage(args, rows)
    write_failed(args, rows)
    print(json.dumps({"rows": len(rows), "non_download_rows": len(non_download_rows(rows))}, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
