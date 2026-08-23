#!/usr/bin/env python3
"""Idempotently apply case-bound browser result attempts to the v2 manifest."""

from __future__ import annotations

import argparse
import copy
import json
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from manifest_contract import (  # noqa: E402
    JOURNAL_SCHEMA,
    atomic_write_json,
    canonical_identity,
    declared_output_path,
    declared_output_root,
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


BROWSER_OUTCOMES = {
    "downloaded",
    "needs_manual_review",
    "browser_required",
    "manual_browser_required",
    "paywalled",
    "access_blocked",
    "failed",
}


def load_journal(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict) or payload.get("schema") != JOURNAL_SCHEMA:
        raise ValueError(f"journal must use schema {JOURNAL_SCHEMA}")
    if not isinstance(payload.get("rows"), list):
        raise ValueError("journal rows must be an array")
    return payload


def applied_attempt_ids(row: dict[str, Any]) -> set[str]:
    return {
        str(attempt.get("attempt_id"))
        for attempt in row.get("attempts", [])
        if isinstance(attempt, dict) and attempt.get("attempt_id")
    }


def canonical_attempt(attempt: dict[str, Any]) -> str:
    payload = {
        key: value
        for key, value in attempt.items()
        if key not in {"manifest_disposition"}
    }
    return json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":"))


def global_attempt_index(rows: list[dict[str, Any]], *, source: str) -> dict[str, tuple[str, str]]:
    index: dict[str, tuple[str, str]] = {}
    for row in rows:
        row_id = str(row.get("row_id") or "")
        attempts = row.get("attempts")
        if not isinstance(attempts, list):
            raise ValueError(f"{source} attempts must be an array: {row_id}")
        for attempt in attempts:
            if not isinstance(attempt, dict):
                raise ValueError(f"{source} attempt must be an object: {row_id}")
            attempt_id = str(attempt.get("attempt_id") or "").strip()
            if not attempt_id:
                continue
            if attempt_id in index:
                raise ValueError(f"global {source} attempt_id collision: {attempt_id}")
            index[attempt_id] = (row_id, canonical_attempt(attempt))
    return index


def validate_replay_bindings(manifest: dict[str, Any], journal: dict[str, Any]) -> int:
    manifest_index = global_attempt_index(manifest["rows"], source="manifest")
    journal_index = global_attempt_index(journal["rows"], source="journal")
    new_attempts = 0
    for attempt_id, journal_binding in journal_index.items():
        existing = manifest_index.get(attempt_id)
        if existing is None:
            new_attempts += 1
        elif existing != journal_binding:
            raise ValueError(f"attempt_id replay content changed: {attempt_id}")
    return new_attempts


def validate_entry(entry: dict[str, Any], row: dict[str, Any]) -> None:
    if entry.get("row_id") != row.get("row_id"):
        raise ValueError(f"journal row id mismatch: {entry.get('row_id')}")
    if entry.get("identity") != canonical_identity(row):
        raise ValueError(f"journal identity mismatch for {row.get('row_id')}")
    if not isinstance(entry.get("attempts"), list):
        raise ValueError(f"journal attempts must be an array: {row.get('row_id')}")


def validate_claimed_pdf_receipt(attempt: dict[str, Any], receipt: dict[str, Any]) -> None:
    claimed = attempt.get("pdf") or attempt.get("candidate_pdf")
    if not isinstance(claimed, dict):
        return
    for field in ("path", "bytes", "sha256", "magic", "validated", "failure_reason"):
        if claimed.get(field) != receipt.get(field):
            raise ValueError(f"journal PDF receipt does not match disk readback: {field}")


def apply_attempt(row: dict[str, Any], entry: dict[str, Any], attempt: dict[str, Any], output_root: Path) -> bool:
    attempt_id = str(attempt.get("attempt_id") or "").strip()
    if not attempt_id:
        raise ValueError(f"attempt_id missing for {row['row_id']}")
    if attempt.get("row_id") != row["row_id"] or attempt.get("identity") != entry["identity"]:
        raise ValueError(f"attempt row/identity binding mismatch: {row['row_id']}:{attempt_id}")
    if attempt_id in applied_attempt_ids(row):
        existing = next(
            item for item in row.get("attempts", [])
            if isinstance(item, dict) and str(item.get("attempt_id") or "") == attempt_id
        )
        if canonical_attempt(existing) != canonical_attempt(attempt):
            raise ValueError(f"attempt_id replay content changed: {attempt_id}")
        return False
    outcome = str(attempt.get("outcome") or "")
    if outcome not in BROWSER_OUTCOMES:
        raise ValueError(f"invalid exact browser outcome {outcome!r}: {row['row_id']}")
    if row.get("disposition") not in {None, "", "eligible"}:
        raise ValueError(f"browser attempt cannot target a non-eligible row: {row['row_id']}")
    if outcome != "downloaded" and not str(attempt.get("failure_reason") or "").strip():
        raise ValueError(f"non-download browser outcome requires failure_reason: {row['row_id']}:{attempt_id}")

    prior_status = row.get("status")
    prior_pdf = row.get("pdf") if isinstance(row.get("pdf"), dict) else {}
    stored = dict(attempt)
    row.setdefault("attempts", []).append(stored)
    row["observed_url"] = str(attempt.get("observed_url") or row.get("observed_url") or "")
    row["observed_title"] = str(attempt.get("observed_title") or row.get("observed_title") or "")
    for evidence_key in ("failure_screenshot_path", "failure_screenshot_error"):
        if attempt.get(evidence_key):
            row[evidence_key] = str(attempt[evidence_key])
    if attempt.get("pubmed_full_text_checked") is True:
        row["pubmed_full_text_checked"] = True
        row["pubmed_full_text_links"] = list(attempt.get("pubmed_full_text_links") or [])

    if outcome == "downloaded":
        pdf_path = Path(str(attempt.get("pdf_path") or ""))
        if not pdf_path.is_absolute():
            pdf_path = output_root / pdf_path
        receipt = verify_pdf(
            pdf_path,
            output_root,
            row,
            identity_match_method=attempt.get("identity_match_method"),
            identity_match_evidence=attempt.get("identity_match_evidence"),
        )
        validate_claimed_pdf_receipt(attempt, receipt)
        row["pdf"] = receipt
        if receipt["validated"]:
            row["status"] = "downloaded"
            row["failure_reason"] = ""
            row["pubmed_followup_required"] = False
            row["pmcid_followup_required"] = False
        else:
            row["status"] = "needs_manual_review"
            row["failure_reason"] = receipt["failure_reason"]
    elif outcome == "needs_manual_review" and attempt.get("pdf_path"):
        pdf_path = Path(str(attempt["pdf_path"]))
        if not pdf_path.is_absolute():
            pdf_path = output_root / pdf_path
        receipt = verify_pdf(
            pdf_path,
            output_root,
            row,
            identity_match_method=attempt.get("identity_match_method"),
            identity_match_evidence=attempt.get("identity_match_evidence"),
        )
        validate_claimed_pdf_receipt(attempt, receipt)
        if receipt["validated"] or receipt["failure_reason"] != "identity_needs_manual_review":
            raise ValueError(f"manual-review PDF candidate has inconsistent disk evidence: {row['row_id']}")
        if prior_status == "downloaded" or (
            prior_status == "needs_manual_review" and prior_pdf.get("path")
        ):
            stored["manifest_disposition"] = "attempt_retained_without_downgrading_existing_pdf_evidence"
        else:
            row["pdf"] = receipt
            row["status"] = "needs_manual_review"
            row["failure_reason"] = str(attempt["failure_reason"])
    else:
        if prior_status == "downloaded" or (
            prior_status == "needs_manual_review" and prior_pdf.get("path")
        ):
            stored["manifest_disposition"] = "attempt_retained_without_downgrading_existing_pdf_evidence"
        else:
            row["status"] = outcome
            row["failure_reason"] = str(attempt.get("failure_reason") or outcome)

    row["pmcid_followup_required"] = bool(
        row.get("pmcid") and row["status"] != "downloaded" and not attempt.get("pmcid_route_checked")
    )
    row["pubmed_followup_required"] = bool(
        row.get("pmid")
        and row["status"] != "downloaded"
        and row.get("pubmed_full_text_checked") is not True
    )
    return True


def apply_journal(manifest: dict[str, Any], journal: dict[str, Any], output_root: Path) -> int:
    if journal.get("inventory_sha256") != manifest["inventory"]["sha256"]:
        raise ValueError("journal inventory SHA does not match manifest")
    validate_replay_bindings(manifest, journal)
    by_id = {row["row_id"]: row for row in manifest["rows"]}
    journal_row_ids = [str(entry.get("row_id") or "") for entry in journal["rows"]]
    if len(journal_row_ids) != len(set(journal_row_ids)):
        raise ValueError("journal row_id entries must be unique")
    applied = 0
    for entry in journal["rows"]:
        row_id = str(entry.get("row_id") or "")
        row = by_id.get(row_id)
        if row is None:
            raise ValueError(f"orphan browser journal row: {row_id}")
        validate_entry(entry, row)
        for attempt in entry["attempts"]:
            if apply_attempt(row, entry, attempt, output_root):
                applied += 1
    return applied


def all_attempts_already_applied(manifest: dict[str, Any], journal: dict[str, Any]) -> bool:
    return validate_replay_bindings(manifest, journal) == 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--journal", required=True, type=Path)
    parser.add_argument("--manifest-out", required=True, type=Path)
    parser.add_argument("--receipt-out", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    args = parser.parse_args()

    root = declared_output_root(args.output_root)
    manifest_path = declared_output_path(args.manifest, root)
    journal_path = declared_output_path(args.journal, root)
    manifest_out = declared_output_path(args.manifest_out, root)
    receipt_out = declared_output_path(args.receipt_out, root)
    require_distinct_paths(
        source_manifest=manifest_path,
        journal=journal_path,
        manifest_out=manifest_out,
        receipt_out=receipt_out,
    )
    manifest = load_manifest(manifest_path, output_root=root)
    paper_root = declared_output_path(Path(str(manifest.get("paper_root") or "papers")), root)
    for label, path in (
        ("source manifest", manifest_path),
        ("journal", journal_path),
        ("manifest output", manifest_out),
        ("receipt output", receipt_out),
    ):
        if is_within(path, paper_root):
            raise ValueError(f"{label} must not be inside manifest paper_root")
    journal = load_journal(journal_path)
    current_manifest_sha = sha256_file(manifest_path)
    current_manifest_bytes = manifest_path.stat().st_size
    current_journal_sha = sha256_file(journal_path)
    base_matches = journal.get("manifest_sha256") == current_manifest_sha
    if not base_matches and not all_attempts_already_applied(manifest, journal):
        raise SystemExit("stale browser journal: manifest changed before unapplied attempts")

    updated_manifest = copy.deepcopy(manifest)
    applied = apply_journal(updated_manifest, journal, root)
    if applied:
        updated_manifest["reconciled_at"] = utc_now()
    verify_downloaded_collection(updated_manifest, root)
    if sha256_file(manifest_path) != current_manifest_sha:
        raise ValueError("source manifest changed before journal apply write")
    if sha256_file(journal_path) != current_journal_sha:
        raise ValueError("browser journal changed before apply write")
    manifest_receipt = save_manifest(manifest_out, updated_manifest, root)
    reread = load_manifest(manifest_out, output_root=root)
    disk = verify_downloaded_collection(reread, root)
    receipt = {
        "schema": "paper-downloader/browser-journal-apply-receipt/v1",
        "source_manifest": {
            "path": relative_output_path(manifest_path, root),
            "sha256": current_manifest_sha,
            "bytes": current_manifest_bytes,
        },
        "journal": {
            "path": relative_output_path(journal_path, root),
            "sha256": current_journal_sha,
            "bytes": journal_path.stat().st_size,
        },
        "inventory_sha256": updated_manifest["inventory"]["sha256"],
        "attempts_applied": applied,
        "idempotent_replay": applied == 0,
        "manifest": {
            "path": relative_output_path(manifest_out, root),
            **manifest_receipt,
        },
        "disk": disk,
    }
    receipt_write = atomic_write_json(receipt_out, receipt)
    if json.loads(receipt_out.read_text(encoding="utf-8")) != receipt:
        raise RuntimeError("browser journal apply receipt readback mismatch")
    load_manifest(manifest_out, output_root=root)
    verify_downloaded_collection(reread, root)
    print(json.dumps({**receipt, "receipt": {"path": relative_output_path(receipt_out, root), **receipt_write}}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
