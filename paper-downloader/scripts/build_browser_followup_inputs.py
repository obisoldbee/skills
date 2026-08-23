#!/usr/bin/env python3
"""Build browser follow-up inputs from a first-pass download manifest."""

from __future__ import annotations

import argparse
import json
import re
import sys
from collections import Counter
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from manifest_contract import (  # noqa: E402
    ALLOWED_STATUSES,
    JOURNAL_SCHEMA,
    atomic_write_json,
    canonical_identity,
    declared_output_path,
    declared_output_root,
    is_within,
    load_manifest,
    relative_output_path,
    require_distinct_paths,
    sha256_file,
)


PAYWALL_STATUSES = {"paywalled", "paywalled_or_no_pdf"}
DONE_STATUSES = {"downloaded"}
DEFAULT_FOLLOWUP_STATUSES = {"browser_required", "manual_browser_required", "failed"}
CONTINUATION_STATUSES = {"browser_required", "manual_browser_required", "paywalled_or_no_pdf"}


def identify_publisher(doi: str) -> str:
    d = (doi or "").lower().strip()
    if not d:
        return "unknown"
    if d.startswith("10.3390"):
        return "MDPI"
    if d.startswith("10.3389"):
        return "Frontiers"
    if d.startswith("10.1371"):
        return "PLOS"
    if d.startswith("10.1186"):
        return "BMC"
    if d.startswith("10.2147"):
        return "DovePress"
    if d.startswith("10.3892"):
        return "Spandidos"
    if d.startswith("10.1161"):
        return "JAHA_AHA"
    if d.startswith("10.7150"):
        return "Theranostics"
    if d.startswith("10.18632"):
        return "Oncotarget"
    if d.startswith("10.3748"):
        return "WJG"
    if d.startswith("10.1007"):
        return "Springer"
    if d.startswith("10.1038"):
        return "Nature"
    if d.startswith("10.1016"):
        return "Elsevier"
    if d.startswith("10.1002"):
        return "Wiley"
    if d.startswith("10.1001"):
        return "JAMA"
    if d.startswith("10.1093"):
        return "Oxford"
    if d.startswith("10.1080"):
        return "TandF"
    if d.startswith("10.1177") or d.startswith("10.1176"):
        return "Sage"
    if d.startswith("10.1021"):
        return "ACS"
    if d.startswith("10.1039"):
        return "RSC"
    if d.startswith("10.1158"):
        return "AACR"
    if d.startswith("10.1056"):
        return "NEJM"
    if d.startswith("10.1159"):
        return "Karger"
    if d.startswith("10.1097"):
        return "LWW_WoltersKluwer"
    if d.startswith("10.1017"):
        return "Cambridge"
    if d.startswith("10.1055"):
        return "Thieme"
    if d.startswith("10.1210"):
        return "EndocrineSociety"
    if d.startswith("10.1126"):
        return "Science_AAAS"
    if d.startswith("10.1136"):
        return "BMJ"
    if d.startswith("10.1111"):
        return "Wiley_Blackwell"
    if d.startswith("10.7307"):
        return "AnticancerResearch"
    if d.startswith("10.2337"):
        return "ADA_Diabetes"
    if d.startswith("10.1084"):
        return "JEM_Rockefeller"
    if d.startswith("10.4049"):
        return "J_Immunol"
    if d.startswith("10.1073"):
        return "PNAS"
    if d.startswith("10.1074"):
        return "JBC"
    if d.startswith("10.1194"):
        return "JLR_Lipids"
    if d.startswith("10.3168"):
        return "JDS_Dairy"
    if d.startswith("10.3945"):
        return "ASN_Nutrition"
    if d.startswith("10.1096"):
        return "FASEB"
    return "other"


def load_rows(path: Path) -> list[dict[str, Any]]:
    return load_manifest(path)["rows"]


def clean_doi(value: Any) -> str:
    doi = str(value or "").strip()
    doi = doi.split("|")[0].rstrip(".,;)\"'")
    if not re.match(r"^10\.\d{4,9}/", doi):
        return ""
    return doi


def safe_filename(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())
    return re.sub(r"_+", "_", value).strip("_")[:180] or "paper"


def browser_route_attempted(row: dict[str, Any], kind: str) -> bool:
    route = f"{kind}_browser"
    return any(
        isinstance(attempt, dict) and attempt.get("route") == route
        for attempt in row.get("attempts", [])
    )


def doi_followup_required(row: dict[str, Any], statuses: set[str]) -> bool:
    if not clean_doi(row.get("doi")):
        return False
    if not browser_route_attempted(row, "doi"):
        return str(row.get("status") or "") in statuses | {"paywalled_or_no_pdf"}
    return str(row.get("status") or "") in CONTINUATION_STATUSES


def pmc_followup_required(row: dict[str, Any]) -> bool:
    pmcid = str(row.get("pmcid") or "").strip()
    if not re.fullmatch(r"PMC\d+", pmcid):
        return False
    if row.get("pmcid_followup_required") is True:
        return True
    if not browser_route_attempted(row, "pmc"):
        return True
    return str(row.get("status") or "") in CONTINUATION_STATUSES


def pubmed_followup_required(row: dict[str, Any]) -> bool:
    return bool(
        re.fullmatch(r"\d+", str(row.get("pmid") or "").strip())
        and row.get("pubmed_full_text_checked") is not True
    )


def should_follow(row: dict[str, Any], statuses: set[str]) -> bool:
    status = str(row.get("status") or "")
    if row.get("disposition") not in {None, "", "eligible"}:
        return False
    if status in {"duplicate", "unverified_citation", "verified_abstract"}:
        return False
    if status in DONE_STATUSES:
        return False
    return any(
        (
            doi_followup_required(row, statuses),
            pmc_followup_required(row),
            pubmed_followup_required(row),
        )
    )


def doi_item(row: dict[str, Any]) -> dict[str, Any] | None:
    doi = clean_doi(row.get("doi"))
    if not doi:
        return None
    pmcid = str(row.get("pmcid") or "").strip()
    return {
        "section": str(row.get("row_id") or ""),
        "row_id": str(row.get("row_id") or ""),
        "title": str(row.get("title") or ""),
        "doi": doi,
        "all_dois": [doi],
        "pmid": str(row.get("pmid") or ""),
        "pmcids": [pmcid] if pmcid else [],
        "publisher": identify_publisher(doi),
        "source_status": str(row.get("status") or ""),
        "source_failure_reason": str(row.get("failure_reason") or ""),
    }


def pmc_item(row: dict[str, Any]) -> dict[str, Any] | None:
    pmcid = str(row.get("pmcid") or "").strip()
    if not re.fullmatch(r"PMC\d+", pmcid):
        return None
    row_id = str(row.get("row_id") or pmcid)
    return {
        "row_id": row_id,
        "title": str(row.get("title") or ""),
        "doi": str(row.get("doi") or ""),
        "pmid": str(row.get("pmid") or ""),
        "pmcid": pmcid,
        "filename": f"{safe_filename(row_id)}__{pmcid}__pmc_browser.pdf",
        "status": "pending",
        "failure_reason": "",
    }


def pubmed_item(row: dict[str, Any]) -> dict[str, Any] | None:
    pmid = str(row.get("pmid") or "").strip()
    if not re.fullmatch(r"\d+", pmid) or row.get("pubmed_full_text_checked") is True:
        return None
    return {
        "row_id": str(row.get("row_id") or pmid),
        "title": str(row.get("title") or ""),
        "doi": str(row.get("doi") or ""),
        "pmid": pmid,
        "pmcid": str(row.get("pmcid") or ""),
        "route_url": f"https://pubmed.ncbi.nlm.nih.gov/{pmid}/",
        "status": "pending",
        "failure_reason": "",
    }


def journal_entry(row: dict[str, Any]) -> dict[str, Any]:
    identity = canonical_identity(row)
    if identity is None:
        raise ValueError(f"browser follow-up row lacks stable identity: {row.get('row_id')}")
    return {
        "row_id": row["row_id"],
        "identity": identity,
        "expected_identifiers": {
            "doi": str(row.get("doi") or ""),
            "pmid": str(row.get("pmid") or ""),
            "pmcid": str(row.get("pmcid") or ""),
        },
        "source_status": row["status"],
        "attempts": [],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument("--journal-out", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument(
        "--statuses",
        default=",".join(sorted(DEFAULT_FOLLOWUP_STATUSES)),
        help="Comma-separated statuses to queue for browser follow-up.",
    )
    args = parser.parse_args()

    root = declared_output_root(args.output_root)
    args.manifest = declared_output_path(args.manifest, root)
    args.output_dir = declared_output_path(args.output_dir, root)
    args.journal_out = declared_output_path(args.journal_out, root)
    manifest = load_manifest(args.manifest, output_root=root)
    manifest_sha = sha256_file(args.manifest)
    paper_root = declared_output_path(Path(str(manifest.get("paper_root") or "papers")), root)
    if is_within(args.output_dir, paper_root) or is_within(args.journal_out, paper_root):
        raise ValueError("browser inputs and journal must not be written inside paper_root")
    statuses = {s.strip() for s in args.statuses.split(",") if s.strip()}
    invalid_statuses = statuses - ALLOWED_STATUSES
    if invalid_statuses:
        parser.error("invalid exact follow-up statuses: " + ", ".join(sorted(invalid_statuses)))
    rows = [row for row in manifest["rows"] if should_follow(row, statuses)]
    doi_rows = [
        item for row in rows
        if doi_followup_required(row, statuses)
        if (item := doi_item(row))
    ]
    pmc_rows = [
        item for row in rows
        if pmc_followup_required(row)
        if (item := pmc_item(row))
    ]
    pubmed_rows = [
        item for row in rows
        if pubmed_followup_required(row)
        if (item := pubmed_item(row))
    ]

    oa_publishers = {
        "MDPI",
        "Frontiers",
        "PLOS",
        "BMC",
        "DovePress",
        "Spandidos",
        "JAHA_AHA",
        "Theranostics",
        "Oncotarget",
        "WJG",
        "AnticancerResearch",
    }
    batches = {
        "batch1_oa": [p for p in doi_rows if p["publisher"] in oa_publishers],
        "batch2_springer_nature": [
            p for p in doi_rows if p["publisher"] in {"Springer", "Nature", "Science_AAAS", "BMJ"}
        ],
        "batch3_often_oa": [
            p
            for p in doi_rows
            if p["publisher"]
            in {"Oxford", "LWW_WoltersKluwer", "TandF", "NEJM", "Karger", "Sage", "AACR", "PNAS", "JBC"}
        ],
        "batch4_likely_paywall": [
            p
            for p in doi_rows
            if p["publisher"]
            in {"Wiley", "Wiley_Blackwell", "JAMA", "EndocrineSociety", "Thieme", "Elsevier", "ACS", "RSC"}
        ],
    }
    classified = {id(p) for batch in batches.values() for p in batch}
    batches["batch5_small"] = [p for p in doi_rows if id(p) not in classified]

    outputs = {
        "doi_papers": declared_output_path(args.output_dir / "doi_papers.json", root),
        "pmc_followup": declared_output_path(args.output_dir / "pmc_followup_manifest.json", root),
        "pubmed_followup": declared_output_path(args.output_dir / "pubmed_followup_manifest.json", root),
        **{
            name: declared_output_path(args.output_dir / f"{name}.json", root)
            for name in batches
        },
        "summary": declared_output_path(args.output_dir / "summary.json", root),
    }
    require_distinct_paths(
        source_manifest=args.manifest,
        journal_out=args.journal_out,
        **outputs,
    )
    if sha256_file(args.manifest) != manifest_sha:
        raise ValueError("source manifest changed while building browser follow-up inputs")
    args.output_dir.mkdir(parents=True, exist_ok=True)
    artifact_receipts: dict[str, dict[str, Any]] = {}
    artifact_receipts["doi_papers"] = atomic_write_json(outputs["doi_papers"], doi_rows)
    artifact_receipts["pmc_followup"] = atomic_write_json(outputs["pmc_followup"], pmc_rows)
    artifact_receipts["pubmed_followup"] = atomic_write_json(outputs["pubmed_followup"], pubmed_rows)
    for name, batch in batches.items():
        artifact_receipts[name] = atomic_write_json(outputs[name], batch)

    summary = {
        "manifest": relative_output_path(args.manifest, root),
        "queued_rows": len(rows),
        "doi_rows": len(doi_rows),
        "pmc_rows": len(pmc_rows),
        "pubmed_rows": len(pubmed_rows),
        "publisher_counts": dict(Counter(p["publisher"] for p in doi_rows)),
        "batch_counts": {name: len(batch) for name, batch in batches.items()},
    }
    journal = {
        "schema": JOURNAL_SCHEMA,
        "manifest_path": relative_output_path(args.manifest, root),
        "manifest_sha256": manifest_sha,
        "inventory_sha256": manifest["inventory"]["sha256"],
        "rows": [journal_entry(row) for row in rows],
    }
    journal_receipt = atomic_write_json(args.journal_out, journal)
    summary["journal"] = {
        "path": relative_output_path(args.journal_out, root),
        **journal_receipt,
    }
    summary["journal_rows"] = len(journal["rows"])
    summary["artifacts"] = {
        name: {"path": relative_output_path(outputs[name], root), **receipt}
        for name, receipt in artifact_receipts.items()
    }
    summary_receipt = atomic_write_json(outputs["summary"], summary)
    print(
        json.dumps(
            {
                **summary,
                "summary": {
                    "path": relative_output_path(outputs["summary"], root),
                    **summary_receipt,
                },
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
