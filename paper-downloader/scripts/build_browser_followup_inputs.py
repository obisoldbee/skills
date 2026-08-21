#!/usr/bin/env python3
"""Build browser follow-up inputs from a first-pass download manifest."""

from __future__ import annotations

import argparse
import json
import re
from collections import Counter
from pathlib import Path
from typing import Any


PAYWALL_STATUSES = {"paywalled", "paywalled_or_no_pdf"}
DONE_STATUSES = {"downloaded", "already_local_pdf", "local_existing"}
DEFAULT_FOLLOWUP_STATUSES = {"browser_required", "manual_browser_required", "failed"}


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
    data = json.loads(path.read_text(encoding="utf-8"))
    if isinstance(data, list):
        return data
    if isinstance(data, dict) and isinstance(data.get("rows"), list):
        return data["rows"]
    raise SystemExit(f"unsupported manifest shape: {path}")


def clean_doi(value: Any) -> str:
    doi = str(value or "").strip()
    doi = doi.split("|")[0].rstrip(".,;)\"'")
    if not re.match(r"^10\.\d{4,9}/", doi):
        return ""
    return doi


def safe_filename(value: str) -> str:
    value = re.sub(r"[^A-Za-z0-9._-]+", "_", value.strip())
    return re.sub(r"_+", "_", value).strip("_")[:180] or "paper"


def should_follow(row: dict[str, Any], statuses: set[str]) -> bool:
    status = str(row.get("status") or "")
    pmcid = str(row.get("pmcid") or "").strip()
    has_pmcid = bool(re.match(r"^PMC\d{5,}$", pmcid))
    if status in DONE_STATUSES:
        return False
    if status == "paywalled_or_no_pdf":
        return True
    if status == "paywalled":
        return has_pmcid
    return status in statuses


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
    if not re.match(r"^PMC\d{5,}$", pmcid):
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


def write_json(path: Path, rows: list[dict[str, Any]]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(rows, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--output-dir", required=True, type=Path)
    parser.add_argument(
        "--statuses",
        default=",".join(sorted(DEFAULT_FOLLOWUP_STATUSES)),
        help="Comma-separated statuses to queue for browser follow-up.",
    )
    args = parser.parse_args()

    statuses = {s.strip() for s in args.statuses.split(",") if s.strip()}
    rows = [row for row in load_rows(args.manifest) if should_follow(row, statuses)]
    doi_rows = [item for row in rows if (item := doi_item(row))]
    pmc_rows = [item for row in rows if (item := pmc_item(row))]

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

    args.output_dir.mkdir(parents=True, exist_ok=True)
    write_json(args.output_dir / "doi_papers.json", doi_rows)
    write_json(args.output_dir / "pmc_followup_manifest.json", pmc_rows)
    for name, batch in batches.items():
        write_json(args.output_dir / f"{name}.json", batch)

    summary = {
        "manifest": str(args.manifest),
        "queued_rows": len(rows),
        "doi_rows": len(doi_rows),
        "pmc_rows": len(pmc_rows),
        "publisher_counts": dict(Counter(p["publisher"] for p in doi_rows)),
        "batch_counts": {name: len(batch) for name, batch in batches.items()},
    }
    (args.output_dir / "summary.json").write_text(
        json.dumps(summary, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(summary, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
