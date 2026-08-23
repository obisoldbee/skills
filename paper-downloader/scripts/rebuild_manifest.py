#!/usr/bin/env python3
"""Reconcile the canonical manifest against declared on-disk PDFs."""

from __future__ import annotations

import argparse
import copy
import json
import re
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from manifest_contract import (  # noqa: E402
    atomic_write_json,
    declared_output_path,
    declared_output_root,
    empty_pdf_receipt,
    is_within,
    load_manifest,
    pdf_files,
    relative_output_path,
    require_distinct_paths,
    save_manifest,
    sha256_file,
    utc_now,
    verify_downloaded_collection,
    verify_pdf,
)


def identifier_tokens(row: dict[str, Any]) -> list[str]:
    tokens: list[str] = []
    for key in ("pmcid", "pmid", "doi"):
        value = re.sub(r"[^a-z0-9]+", "", str(row.get(key) or "").lower())
        if value:
            tokens.append(value)
    return tokens


def filename_candidate_paths(row: dict[str, Any], paper_root: Path) -> list[Path]:
    tokens = identifier_tokens(row)
    if not tokens or not paper_root.exists():
        return []
    matches: list[Path] = []
    for path in paper_root.rglob("*"):
        if not path.is_file() or path.suffix.lower() != ".pdf":
            continue
        compact = re.sub(r"[^a-z0-9]+", "", path.name.lower())
        if any(token in compact for token in tokens):
            matches.append(path)
    return sorted(matches)


def all_pdf_paths(paper_root: Path) -> list[Path]:
    if not paper_root.exists():
        return []
    return sorted(
        path.resolve()
        for path in paper_root.rglob("*")
        if path.is_file() and path.suffix.lower() == ".pdf"
    )


def eligible_for_reconciliation(row: dict[str, Any]) -> bool:
    if row.get("disposition") not in {None, "", "eligible"}:
        return False
    return row.get("status") not in {"duplicate", "unverified_citation", "verified_abstract"}


def candidate_for_row(
    row: dict[str, Any],
    root: Path,
    paper_root: Path,
    disk_paths: list[Path],
) -> tuple[Path | None, dict[str, Any] | None, str]:
    recorded = row.get("pdf") if isinstance(row.get("pdf"), dict) else {}
    recorded_path = str(recorded.get("path") or "")
    if recorded_path:
        try:
            resolved = declared_output_path(Path(recorded_path), root)
        except ValueError:
            return None, None, "recorded_pdf_path_escape"
        if not is_within(resolved, paper_root):
            return None, None, "recorded_pdf_outside_declared_paper_root"
        if resolved.is_file():
            receipt = verify_pdf(
                resolved,
                root,
                row,
                identity_match_method=recorded.get("identity_match", {}).get("claimed_method"),
                identity_match_evidence=recorded.get("identity_match", {}).get("claimed_evidence"),
            )
            return resolved, receipt, "recorded_pdf_readback"

    # A missing recorded path may have been renamed.  First search every PDF by
    # actual PDF identity; only then use a unique filename hint as a manual-review
    # candidate.  A filename never proves identity.
    identity_matches: list[tuple[Path, dict[str, Any]]] = []
    for path in disk_paths:
        receipt = verify_pdf(
            path,
            root,
            row,
            identity_match_method=None,
            identity_match_evidence=None,
        )
        if receipt["validated"]:
            identity_matches.append((path, receipt))
    if len(identity_matches) == 1:
        path, receipt = identity_matches[0]
        return path, receipt, "renamed_pdf_identity_readback"
    if len(identity_matches) > 1:
        return None, None, "ambiguous_identity_pdf_candidates"

    filename_matches = filename_candidate_paths(row, paper_root)
    if len(filename_matches) == 1:
        path = filename_matches[0].resolve()
        receipt = verify_pdf(
            path,
            root,
            row,
            identity_match_method="filename_hint_only",
            identity_match_evidence=path.name,
        )
        return path, receipt, "filename_candidate_needs_identity_review"
    if len(filename_matches) > 1:
        return None, None, "ambiguous_filename_pdf_candidates"
    return None, None, "recorded_pdf_missing" if recorded_path else "no_pdf_candidate"


def reconcile_manifest(
    manifest: dict[str, Any], output_root: Path, paper_root: Path
) -> tuple[dict[str, Any], dict[str, Any]]:
    root = declared_output_root(output_root)
    paper_root = declared_output_path(paper_root, root)
    rebuilt = copy.deepcopy(manifest)
    rebuilt["paper_root"] = paper_root.relative_to(root).as_posix() or "."
    disk_paths = all_pdf_paths(paper_root)
    proposals: dict[str, tuple[Path | None, dict[str, Any] | None, str]] = {}
    claims: dict[str, list[str]] = {}
    ambiguous: list[str] = []

    # Bind every candidate before mutating any row.  This makes the path-to-row
    # relationship a true bijection and catches cross-row claims pre-write.
    for row in rebuilt["rows"]:
        if not eligible_for_reconciliation(row):
            continue
        proposal = candidate_for_row(row, root, paper_root, disk_paths)
        proposals[row["row_id"]] = proposal
        path, receipt, reason = proposal
        if path is not None and receipt is not None:
            relative = path.relative_to(root).as_posix()
            claims.setdefault(relative, []).append(row["row_id"])
        if reason.startswith("ambiguous_"):
            ambiguous.append(row["row_id"])

    collisions = {path: rows for path, rows in claims.items() if len(rows) > 1}
    if collisions:
        detail = ", ".join(f"{path}=>{','.join(rows)}" for path, rows in sorted(collisions.items()))
        raise ValueError("PDF path-to-row bijection violation: " + detail)

    assigned: set[str] = set()
    for row in rebuilt["rows"]:
        if not eligible_for_reconciliation(row):
            continue
        path, receipt, reason = proposals[row["row_id"]]
        if path is not None and receipt is not None:
            row["pdf"] = receipt
            assigned.add(receipt["path"])
            if receipt["validated"]:
                row["status"] = "downloaded"
                row["failure_reason"] = ""
            elif receipt["failure_reason"] == "identity_needs_manual_review":
                row["status"] = "needs_manual_review"
                row["failure_reason"] = "identity_needs_manual_review"
            else:
                row["status"] = "needs_manual_review"
                row["failure_reason"] = receipt["failure_reason"]
        elif reason.startswith("ambiguous_"):
            row["status"] = "needs_manual_review"
            row["failure_reason"] = reason
            row["pdf"] = empty_pdf_receipt()
        elif row.get("status") == "downloaded" or str((row.get("pdf") or {}).get("path") or ""):
            row["status"] = "needs_manual_review"
            row["failure_reason"] = reason
            row["pdf"] = empty_pdf_receipt()

    actual = {
        (paper_root / relative).relative_to(root).as_posix()
        for relative in pdf_files(paper_root)
    }
    extra = sorted(actual - assigned)
    if extra:
        raise ValueError("unassigned PDFs in declared paper root: " + ", ".join(extra))

    rebuilt["reconciled_at"] = utc_now()
    disk = verify_downloaded_collection(rebuilt, root)
    return rebuilt, {
        "assigned_pdf_files": sorted(assigned),
        "actual_pdf_files": sorted(actual),
        "ambiguous_rows": ambiguous,
        "extra_pdf_files": extra,
        "disk": disk,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--manifest-out", required=True, type=Path)
    parser.add_argument("--paper-dir", required=True, type=Path)
    parser.add_argument("--receipt-out", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    args = parser.parse_args()

    root = declared_output_root(args.output_root)
    manifest_path = declared_output_path(args.manifest, root)
    manifest_out = declared_output_path(args.manifest_out, root)
    paper_dir = declared_output_path(args.paper_dir, root)
    receipt_out = declared_output_path(args.receipt_out, root)
    require_distinct_paths(
        source_manifest=manifest_path,
        manifest_out=manifest_out,
        paper_dir=paper_dir,
        receipt_out=receipt_out,
    )
    for label, path in (
        ("source manifest", manifest_path),
        ("manifest output", manifest_out),
        ("receipt output", receipt_out),
    ):
        if is_within(path, paper_dir):
            parser.error(f"{label} must not be inside --paper-dir")
    manifest = load_manifest(manifest_path, output_root=root)
    source_sha = sha256_file(manifest_path)
    source_bytes = manifest_path.stat().st_size
    manifest, reconciliation = reconcile_manifest(manifest, root, paper_dir)
    verify_downloaded_collection(manifest, root)
    if sha256_file(manifest_path) != source_sha:
        raise ValueError("source manifest changed before rebuild write")
    manifest_receipt = save_manifest(manifest_out, manifest, root)
    reread_manifest = load_manifest(manifest_out, output_root=root)
    disk = verify_downloaded_collection(reread_manifest, root)
    receipt = {
        "schema": "paper-downloader/rebuild-receipt/v1",
        "source_manifest": {
            "path": relative_output_path(manifest_path, root),
            "bytes": source_bytes,
            "sha256": source_sha,
        },
        "inventory_sha256": manifest["inventory"]["sha256"],
        "reconciled_at": manifest["reconciled_at"],
        "manifest": {
            "path": relative_output_path(manifest_out, root),
            **manifest_receipt,
        },
        "disk": disk,
        **reconciliation,
    }
    receipt_write = atomic_write_json(receipt_out, receipt)
    if json.loads(receipt_out.read_text(encoding="utf-8")) != receipt:
        raise RuntimeError("rebuild receipt readback mismatch")
    load_manifest(manifest_out, output_root=root)
    verify_downloaded_collection(reread_manifest, root)
    print(json.dumps({**receipt, "receipt": {"path": relative_output_path(receipt_out, root), **receipt_write}}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
