#!/usr/bin/env python3
"""Generate final reports only after inventory, manifest, and disk readback agree."""

from __future__ import annotations

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import quote, urlsplit


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from build_inventory_download_manifest import build_rows  # noqa: E402
from manifest_contract import (  # noqa: E402
    REPORT_RECEIPT_SCHEMA,
    atomic_write_bytes,
    atomic_write_json,
    canonical_identity,
    declared_output_path,
    declared_output_root,
    exact_status_counts,
    is_within,
    load_manifest,
    relative_output_path,
    require_distinct_paths,
    row_binding_projection,
    rows_binding_sha256,
    sha256_file,
    verify_downloaded_collection,
)


def load_rows(path: Path) -> list[dict[str, Any]]:
    return load_manifest(path)["rows"]


def status_of(row: dict[str, Any]) -> str:
    if "download_status" in row:
        raise ValueError("dual status/download_status is forbidden")
    return str(row.get("status") or "")


def has_identifier(row: dict[str, Any]) -> bool:
    return any(str(row.get(key) or "").strip() for key in ("doi", "pmid", "pmcid", "pdf_url"))


def non_download_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [row for row in rows if status_of(row) != "downloaded"]


def bound_browser_attempts(row: dict[str, Any]) -> list[dict[str, Any]]:
    identity = canonical_identity(row)
    return [
        attempt
        for attempt in row.get("attempts", [])
        if isinstance(attempt, dict)
        and str(attempt.get("attempt_id") or "").strip()
        and attempt.get("row_id") == row.get("row_id")
        and attempt.get("identity") == identity
        and (
            str(attempt.get("route") or "").startswith("browser")
            or str(attempt.get("route") or "").endswith("_browser")
        )
    ]


def browser_attempted_non_download(row: dict[str, Any]) -> bool:
    return bool(bound_browser_attempts(row))


def screenshot_path_valid(value: Any, output_root: Path | None) -> bool:
    value = str(value or "").strip()
    if not value:
        return False
    if output_root is None:
        return True
    if Path(value).is_absolute():
        return False
    try:
        path = declared_output_path(Path(value), output_root)
    except ValueError:
        return False
    return path.is_file() and path.stat().st_size > 0


def screenshot_evidence_valid(row: dict[str, Any], output_root: Path | None) -> bool:
    return screenshot_path_valid(row.get("failure_screenshot_path"), output_root)


def observable_browser_failure(row: dict[str, Any], output_root: Path | None = None) -> bool:
    for attempt in bound_browser_attempts(row):
        if screenshot_path_valid(attempt.get("failure_screenshot_path"), output_root):
            return True
        if str(attempt.get("failure_screenshot_error") or "").strip():
            return True
        observed_url = urlsplit(str(attempt.get("observed_url") or "").strip())
        if observed_url.scheme in {"http", "https"} and observed_url.netloc:
            return True
        if str(attempt.get("observed_title") or "").strip():
            return True
        if (
            isinstance(attempt.get("response_bytes"), int)
            and attempt.get("response_bytes", 0) > 0
            and re.fullmatch(r"[0-9a-f]{64}", str(attempt.get("response_sha256") or ""))
        ):
            return True
    return False


def pubmed_followup_evidenced(row: dict[str, Any]) -> bool:
    return any(
        attempt.get("route") == "pubmed_browser"
        and attempt.get("pubmed_full_text_checked") is True
        for attempt in bound_browser_attempts(row)
    )


def pmcid_followup_evidenced(row: dict[str, Any]) -> bool:
    return any(
        attempt.get("route") == "pmc_browser"
        and attempt.get("pmcid_route_checked") is True
        for attempt in bound_browser_attempts(row)
    )


def completion_blockers(rows: list[dict[str, Any]], output_root: Path | None = None) -> list[str]:
    blockers: list[str] = []
    queued = {"pending", "browser_required", "manual_browser_required", "paywalled_or_no_pdf"}
    observed_terminal = {"paywalled", "access_blocked", "failed"}
    for row in rows:
        row_id = str(row.get("row_id") or "<missing-row-id>")
        status = status_of(row)
        disposition = str(row.get("disposition") or "eligible")
        reason = str(row.get("failure_reason") or "").strip()
        if status in queued:
            blockers.append(f"{row_id}:unresolved_status:{status}")
        if status == "needs_manual_review" and disposition not in {"excluded_do_not_cite"}:
            blockers.append(f"{row_id}:unresolved_status:needs_manual_review")
        if row.get("pubmed_followup_required") is True:
            blockers.append(f"{row_id}:pubmed_followup_required")
        if row.get("pmcid_followup_required") is True:
            blockers.append(f"{row_id}:pmcid_followup_required")
        if status != "downloaded" and not reason:
            blockers.append(f"{row_id}:non_download_failure_reason_missing")
        if status == "downloaded" and reason:
            blockers.append(f"{row_id}:downloaded_row_has_failure_reason")
        if status in observed_terminal and disposition in {"", "eligible"}:
            if not browser_attempted_non_download(row):
                blockers.append(f"{row_id}:terminal_status_without_browser_attempt:{status}")
            if str(row.get("pmid") or "").strip() and not pubmed_followup_evidenced(row):
                blockers.append(f"{row_id}:terminal_status_without_pubmed_followup_evidence")
            if str(row.get("pmcid") or "").strip() and not pmcid_followup_evidenced(row):
                blockers.append(f"{row_id}:terminal_status_without_pmcid_followup_evidence")
        if str(row.get("failure_screenshot_path") or "").strip() and not screenshot_evidence_valid(row, output_root):
            blockers.append(f"{row_id}:failure_screenshot_path_invalid")
        if status != "downloaded" and browser_attempted_non_download(row) and not observable_browser_failure(row, output_root):
            blockers.append(f"{row_id}:browser_failure_observable_evidence_missing")
    return blockers


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


def write_coverage(args: argparse.Namespace, rows: list[dict[str, Any]]) -> dict[str, Any]:
    counts = exact_status_counts(rows)
    missing_reason = [
        row for row in non_download_rows(rows)
        if not str(row.get("failure_reason") or "").strip()
    ]
    missing_browser_evidence = [
        row for row in non_download_rows(rows)
        if browser_attempted_non_download(row)
        and not observable_browser_failure(row, args.output_root)
    ]
    lines = [
        "# Download Coverage",
        "",
        f"- manifest_sha256: `{args.manifest_sha256}`",
        f"- source_inventory_sha256: `{args.inventory_sha256}`",
        f"- source_inventory_rows: {args.inventory_rows}",
        f"- manifest_rows: {len(rows)}",
        f"- rows_with_identifier: {sum(1 for row in rows if has_identifier(row))}",
        f"- rows_missing_failure_reason: {len(missing_reason)}",
        f"- browser_non_download_rows_missing_observable_evidence: {len(missing_browser_evidence)}",
        "",
        "## Exact Status Counts",
        "",
        *[f"- {status}: {count}" for status, count in sorted(counts.items())],
        "",
        "## Coverage Boundary",
        "",
        args.note or "Complete frozen inventory; downloaded claims passed disk readback.",
        "",
    ]
    if missing_reason:
        lines.extend(["## Rows Missing Failure Reason", ""])
        lines.extend(f"- `{row['row_id']}`: {row.get('title', '')}" for row in missing_reason)
        lines.append("")
    if missing_browser_evidence:
        lines.extend(["## Browser Rows Missing Observable Evidence", ""])
        lines.extend(f"- `{row['row_id']}`: {row.get('title', '')}" for row in missing_browser_evidence)
        lines.append("")
    return atomic_write_bytes(args.coverage_out, ("\n".join(lines) + "\n").encode("utf-8"))


def write_failed(args: argparse.Namespace, rows: list[dict[str, Any]]) -> dict[str, Any]:
    lines = [
        "# Failed Downloads",
        "",
        "| row_id | status | pmcid | pmid | doi | source_links | failure_reason | observed_url | observed_title | attempts |",
        "|---|---|---|---|---|---|---|---|---|---|",
    ]
    for row in non_download_rows(rows):
        attempts = "; ".join(
            f"{attempt.get('route', '')}:{attempt.get('outcome', '')}"
            for attempt in row.get("attempts", [])
            if isinstance(attempt, dict)
        )
        values = [
            row.get("row_id", ""), status_of(row), row.get("pmcid", ""),
            row.get("pmid", ""), row.get("doi", ""), reference_links(row),
            row.get("failure_reason", ""), row.get("observed_url", ""),
            row.get("observed_title", ""), attempts,
        ]
        lines.append("| " + " | ".join(str(value).replace("|", "/") for value in values) + " |")
    return atomic_write_bytes(args.failed_out, ("\n".join(lines) + "\n").encode("utf-8"))


def verify_inventory(manifest: dict[str, Any], inventory_path: Path) -> list[dict[str, Any]]:
    observed_sha = sha256_file(inventory_path)
    if observed_sha != manifest["inventory"]["sha256"]:
        raise ValueError("inventory SHA does not match canonical manifest")
    inventory_format = str(manifest["inventory"].get("format") or "")
    if inventory_format not in {"markdown", "csv"}:
        raise ValueError("canonical manifest inventory format is missing or invalid")
    observed_rows = build_rows(inventory_path, inventory_format=inventory_format)
    observed_ids = [row["row_id"] for row in observed_rows]
    if observed_ids != manifest["inventory"]["row_ids"]:
        raise ValueError("inventory canonical row-id set/order does not match manifest")
    observed_projection = [row_binding_projection(row) for row in observed_rows]
    manifest_projection = [row_binding_projection(row) for row in manifest["rows"]]
    if observed_projection != manifest_projection:
        raise ValueError("inventory frozen row bindings do not exactly match manifest rows")
    observed_rows_sha = rows_binding_sha256(observed_rows)
    if observed_rows_sha != manifest["inventory"]["rows_sha256"]:
        raise ValueError("inventory frozen row binding SHA does not match manifest")
    return observed_rows


def input_descriptor(path: Path, root: Path) -> dict[str, Any]:
    resolved = path.expanduser().resolve()
    descriptor: dict[str, Any] = {
        "bytes": resolved.stat().st_size,
        "sha256": sha256_file(resolved),
    }
    if is_within(resolved, root):
        descriptor["path"] = resolved.relative_to(root).as_posix()
    else:
        descriptor["source_name"] = resolved.name
        descriptor["external_input"] = True
    return descriptor


def verify_written_artifact(path: Path, receipt: dict[str, Any]) -> None:
    data = path.read_bytes()
    if len(data) != receipt["bytes"] or sha256_file(path) != receipt["sha256"]:
        raise RuntimeError(f"written artifact readback mismatch: {path}")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--inventory", required=True, type=Path)
    parser.add_argument("--coverage-out", required=True, type=Path)
    parser.add_argument("--failed-out", required=True, type=Path)
    parser.add_argument("--receipt-out", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--note", default="")
    args = parser.parse_args()

    root = declared_output_root(args.output_root)
    args.output_root = root
    args.manifest = declared_output_path(args.manifest, root)
    args.inventory = args.inventory.expanduser().resolve()
    if not args.inventory.is_file():
        parser.error(f"inventory input not found: {args.inventory}")
    args.coverage_out = declared_output_path(args.coverage_out, root)
    args.failed_out = declared_output_path(args.failed_out, root)
    args.receipt_out = declared_output_path(args.receipt_out, root)
    require_distinct_paths(
        manifest=args.manifest,
        inventory=args.inventory,
        coverage_out=args.coverage_out,
        failed_out=args.failed_out,
        receipt_out=args.receipt_out,
    )

    manifest = load_manifest(args.manifest, output_root=root)
    paper_root = declared_output_path(Path(str(manifest.get("paper_root") or "papers")), root, allow_root=True)
    if is_within(args.manifest, paper_root) or is_within(args.inventory, paper_root):
        raise ValueError("manifest and inventory inputs must be outside the declared paper root")
    for label, output in (
        ("coverage", args.coverage_out),
        ("failed", args.failed_out),
        ("receipt", args.receipt_out),
    ):
        if is_within(output, paper_root):
            raise ValueError(f"{label} output must not be inside the declared paper root")
    verify_inventory(manifest, args.inventory)
    disk = verify_downloaded_collection(manifest, root)
    blockers = completion_blockers(manifest["rows"], root)
    if blockers:
        raise ValueError("final completion gate failed: " + "; ".join(blockers))
    args.manifest_sha256 = sha256_file(args.manifest)
    args.inventory_sha256 = sha256_file(args.inventory)
    args.inventory_rows = manifest["inventory"]["row_count"]
    manifest_descriptor = input_descriptor(args.manifest, root)
    inventory_descriptor = input_descriptor(args.inventory, root)
    coverage_receipt = write_coverage(args, manifest["rows"])
    failed_receipt = write_failed(args, manifest["rows"])
    verify_written_artifact(args.coverage_out, coverage_receipt)
    verify_written_artifact(args.failed_out, failed_receipt)
    receipt = {
        "schema": REPORT_RECEIPT_SCHEMA,
        "completion_state": "complete",
        "manifest": manifest_descriptor,
        "inventory": inventory_descriptor,
        "inventory_rows_sha256": manifest["inventory"]["rows_sha256"],
        "inventory_row_ids": manifest["inventory"]["row_ids"],
        "status_counts": exact_status_counts(manifest["rows"]),
        "disk": disk,
        "coverage_report": {"path": relative_output_path(args.coverage_out, root), **coverage_receipt},
        "failed_report": {"path": relative_output_path(args.failed_out, root), **failed_receipt},
    }
    receipt_write = atomic_write_json(args.receipt_out, receipt)
    if json.loads(args.receipt_out.read_text(encoding="utf-8")) != receipt:
        raise RuntimeError("final report receipt readback mismatch")
    # The final check deliberately rereads all three authorities after every
    # output has been persisted.  The receipt does not contain its own hash.
    reread_manifest = load_manifest(args.manifest, output_root=root)
    verify_inventory(reread_manifest, args.inventory)
    if input_descriptor(args.manifest, root) != manifest_descriptor:
        raise RuntimeError("manifest changed during final report persistence")
    if input_descriptor(args.inventory, root) != inventory_descriptor:
        raise RuntimeError("inventory changed during final report persistence")
    verify_downloaded_collection(reread_manifest, root)
    verify_written_artifact(args.coverage_out, coverage_receipt)
    verify_written_artifact(args.failed_out, failed_receipt)
    print(
        json.dumps(
            {
                **receipt,
                "receipt": {
                    "path": relative_output_path(args.receipt_out, root),
                    **receipt_write,
                },
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
