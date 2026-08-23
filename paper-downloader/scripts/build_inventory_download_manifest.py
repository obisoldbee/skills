#!/usr/bin/env python3
"""Build the canonical v2 manifest without dropping any inventory table row."""

from __future__ import annotations

import argparse
import csv
import io
import json
import re
import sys
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from manifest_contract import (  # noqa: E402
    SCHEMA,
    atomic_write_json,
    canonical_identity,
    declared_output_path,
    declared_output_root,
    empty_pdf_receipt,
    identity_key,
    normalized_identifier,
    relative_output_path,
    require_distinct_paths,
    rows_binding_sha256,
    sha256_file,
    utc_now,
    validate_manifest,
)


def clean_cell(value: str) -> str:
    return value.strip().strip("`").strip()


def normalize_key(value: str) -> str:
    return re.sub(r"[^a-z0-9]+", "_", clean_cell(value).lower()).strip("_")


def split_row(line: str) -> list[str]:
    stripped = line.strip()
    cells: list[str] = []
    current: list[str] = []
    escaped = False
    for character in stripped:
        if escaped:
            if character == "|":
                current.append("|")
            else:
                current.extend(("\\", character))
            escaped = False
        elif character == "\\":
            escaped = True
        elif character == "|":
            cells.append("".join(current))
            current = []
        else:
            current.append(character)
    if escaped:
        current.append("\\")
    cells.append("".join(current))
    if stripped.startswith("|"):
        cells = cells[1:]
    if stripped.endswith("|"):
        backslashes = 0
        cursor = len(stripped) - 2
        while cursor >= 0 and stripped[cursor] == "\\":
            backslashes += 1
            cursor -= 1
        if backslashes % 2 == 0:
            cells = cells[:-1]
    return [clean_cell(cell) for cell in cells]


def looks_like_separator(line: str) -> bool:
    cells = split_row(line)
    return bool(cells) and all(re.fullmatch(r":?-{3,}:?", cell.strip()) for cell in cells)


def has_unescaped_pipe(line: str) -> bool:
    escaped = False
    for character in line:
        if escaped:
            escaped = False
        elif character == "\\":
            escaped = True
        elif character == "|":
            return True
    return False


def normalized_headers(cells: list[str]) -> list[str]:
    headers = [normalize_key(cell) for cell in cells]
    if not headers or any(not header for header in headers):
        raise ValueError("inventory contains an empty column header")
    if len(headers) != len(set(headers)):
        raise ValueError("inventory contains duplicate normalized column headers")
    return headers


def iter_markdown_tables(text: str) -> list[tuple[list[str], list[dict[str, Any]]]]:
    lines = text.splitlines()
    tables: list[tuple[list[str], list[dict[str, Any]]]] = []
    index = 0
    while index + 1 < len(lines):
        if not has_unescaped_pipe(lines[index]) or not looks_like_separator(lines[index + 1]):
            index += 1
            continue
        header = normalized_headers(split_row(lines[index]))
        if len(split_row(lines[index + 1])) != len(header):
            raise ValueError(f"Markdown table separator width mismatch at line {index + 2}")
        rows: list[dict[str, Any]] = []
        index += 2
        row_index = 0
        while index < len(lines) and lines[index].strip() and has_unescaped_pipe(lines[index]):
            line = lines[index]
            cells = split_row(line)
            if len(cells) > len(header):
                raise ValueError(f"Markdown table row has too many cells at line {index + 1}")
            if len(cells) < len(header):
                cells.extend([""] * (len(header) - len(cells)))
            rows.append(
                {
                    "values": dict(zip(header, cells)),
                    "line": index + 1,
                    "row_index": row_index,
                }
            )
            row_index += 1
            index += 1
        tables.append((header, rows))
    return tables


def iter_csv_rows(text: str) -> list[tuple[list[str], list[dict[str, Any]]]]:
    reader = csv.reader(io.StringIO(text, newline=""))
    try:
        raw_header = next(reader)
    except StopIteration:
        return []
    if len(raw_header) == 1 and has_unescaped_pipe(raw_header[0]):
        raise ValueError("CSV inventory content looks like a Markdown table")
    header = normalized_headers([clean_cell(cell) for cell in raw_header])
    rows: list[dict[str, Any]] = []
    row_index = 0
    for cells in reader:
        if not cells or not any(str(cell).strip() for cell in cells):
            continue
        if len(cells) > len(header):
            raise ValueError(f"CSV row has too many cells at line {reader.line_num}")
        cells = [clean_cell(str(cell)) for cell in cells]
        cells.extend([""] * (len(header) - len(cells)))
        rows.append(
            {
                "values": dict(zip(header, cells)),
                "line": reader.line_num,
                "row_index": row_index,
            }
        )
        row_index += 1
    return [(header, rows)]


def detect_inventory_format(path: Path, text: str, requested: str = "auto") -> str:
    if requested in {"markdown", "csv"}:
        return requested
    suffix = path.suffix.lower()
    if suffix == ".csv":
        return "csv"
    if suffix in {".md", ".markdown"}:
        return "markdown"
    lines = text.splitlines()
    for index in range(len(lines) - 1):
        if has_unescaped_pipe(lines[index]) and looks_like_separator(lines[index + 1]):
            return "markdown"
    nonempty = [line for line in lines if line.strip()]
    if nonempty and "," in nonempty[0]:
        return "csv"
    raise ValueError(f"cannot strictly detect inventory format for {path}; pass --format")


def inventory_tables(path: Path, inventory_format: str = "auto") -> tuple[str, list[tuple[list[str], list[dict[str, Any]]]]]:
    text = path.read_text(encoding="utf-8")
    detected = detect_inventory_format(path, text, inventory_format)
    tables = iter_markdown_tables(text) if detected == "markdown" else iter_csv_rows(text)
    if not tables or not any(rows for _header, rows in tables):
        raise ValueError(f"inventory contains no parseable data rows: {path}")
    return detected, tables


def first_value(row: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = clean_cell(str(row.get(key, "")))
        if value:
            return value
    return ""


def pdf_url_from_row(row: dict[str, Any]) -> str:
    for key in ("pdf_url", "online_source_url", "original_publication_url", "url"):
        value = first_value(row, key)
        if value.lower().split("?", 1)[0].endswith(".pdf"):
            return value
    return ""


def source_disposition(row: dict[str, Any]) -> str:
    text = " ".join(
        first_value(row, key)
        for key in ("final_status", "citation_use", "status_label", "download_status", "note")
    ).lower()
    if "do_not_cite" in text or "do not cite" in text:
        return "excluded_do_not_cite"
    if "duplicate" in text:
        return "declared_duplicate"
    return "eligible"


def canonical_row_id(source_row_id: str, table_index: int, row_index: int, used: set[str]) -> str:
    candidate = source_row_id.strip()
    if candidate and candidate not in used:
        used.add(candidate)
        return candidate
    generated = f"inventory-t{table_index + 1:03d}-r{row_index + 1:04d}"
    suffix = 1
    while generated in used:
        suffix += 1
        generated = f"inventory-t{table_index + 1:03d}-r{row_index + 1:04d}-{suffix}"
    used.add(generated)
    return generated


def build_rows(
    path: Path,
    include_duplicates: bool = True,
    inventory_format: str = "auto",
) -> list[dict[str, Any]]:
    """Return every Markdown table data row; include_duplicates is compatibility-only."""

    del include_duplicates
    rows: list[dict[str, Any]] = []
    used_row_ids: set[str] = set()
    first_by_identity: dict[str, str] = {}
    detected_format, tables = inventory_tables(path, inventory_format)
    for table_index, (_header, table_rows) in enumerate(tables):
        for source in table_rows:
            row_index = int(source["row_index"])
            raw = source["values"]
            source_row_id = first_value(raw, "row_id", "id")
            row_id = canonical_row_id(source_row_id, table_index, row_index, used_row_ids)
            raw_doi = first_value(raw, "doi")
            raw_pmid = first_value(raw, "pmid")
            raw_pmcid = first_value(raw, "pmcid")
            row: dict[str, Any] = {
                "row_id": row_id,
                "source_row_id": source_row_id,
                "source_coordinate": {
                    "table_index": table_index,
                    "row_index": row_index,
                    "line": source["line"],
                    "format": detected_format,
                },
                "source_row": raw,
                "title": first_value(raw, "title"),
                "doi": normalized_identifier("doi", raw_doi),
                "pmid": normalized_identifier("pmid", raw_pmid),
                "pmcid": normalized_identifier("pmcid", raw_pmcid),
                "pdf_url": pdf_url_from_row(raw),
                "source_origin": first_value(raw, "source_origin") or "inventory",
                "input_url": first_value(raw, "input_url", "url"),
                "original_publication_url": first_value(raw, "original_publication_url", "online_source_url"),
                "disposition": source_disposition(raw),
                "duplicate_of": first_value(raw, "duplicate_of", "duplicate_of_row_id") or None,
                "status": "pending",
                "attempts": [],
                "failure_reason": "",
                "observed_url": "",
                "observed_title": "",
                "pubmed_full_text_checked": False,
                "pubmed_full_text_links": [],
                "pubmed_followup_required": False,
                "pmcid_followup_required": False,
                "pdf": empty_pdf_receipt(),
            }
            key = identity_key(row)
            if key and key in first_by_identity:
                row["duplicate_of"] = first_by_identity[key]
                row["status"] = "duplicate"
                row["disposition"] = "duplicate"
                row["failure_reason"] = "repeated_canonical_identity"
            elif key:
                first_by_identity[key] = row_id
            if row["disposition"] in {"declared_duplicate", "excluded_do_not_cite"}:
                row["status"] = "needs_manual_review"
                row["failure_reason"] = row["disposition"]
            if not canonical_identity(row) and row["status"] == "pending":
                row["status"] = "unverified_citation"
                row["failure_reason"] = "stable_identifier_missing_or_invalid"
            rows.append(row)
    known_row_ids = {row["row_id"] for row in rows}
    for row in rows:
        if row["disposition"] != "declared_duplicate":
            continue
        duplicate_of = str(row.get("duplicate_of") or "")
        if duplicate_of and duplicate_of != row["row_id"] and duplicate_of in known_row_ids:
            row["status"] = "duplicate"
            row["failure_reason"] = "declared_duplicate"
        else:
            row["status"] = "needs_manual_review"
            row["failure_reason"] = "declared_duplicate_lineage_missing_or_invalid"
    return rows


def build_manifest(
    path: Path,
    output_root: Path,
    inventory_format: str = "auto",
) -> dict[str, Any]:
    root = declared_output_root(output_root)
    source_sha = sha256_file(path)
    detected_format, _tables = inventory_tables(path, inventory_format)
    rows = build_rows(path, inventory_format=detected_format)
    if sha256_file(path) != source_sha:
        raise ValueError("inventory changed while canonical manifest was being built")
    return {
        "schema": SCHEMA,
        "created_at": utc_now(),
        "reconciled_at": None,
        "declared_output_root": str(root),
        "paper_root": "papers",
        "inventory": {
            "source_path": str(path.expanduser().resolve()),
            "sha256": source_sha,
            "row_count": len(rows),
            "row_ids": [row["row_id"] for row in rows],
            "rows_sha256": rows_binding_sha256(rows),
            "format": detected_format,
        },
        "rows": rows,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--format", choices=("auto", "markdown", "csv"), default="auto")
    parser.add_argument(
        "--include-duplicates",
        action="store_true",
        help="Compatibility flag; v2 always preserves duplicates and every inventory row.",
    )
    args = parser.parse_args()
    if not args.input.is_file():
        parser.error(f"inventory input not found: {args.input}")
    root = declared_output_root(args.output_root)
    output = declared_output_path(args.output, root)
    require_distinct_paths(inventory_input=args.input, manifest_output=output)
    payload = build_manifest(args.input, root, args.format)
    validate_manifest(payload, output_root=root)
    receipt = atomic_write_json(output, payload)
    validate_manifest(json.loads(output.read_text(encoding="utf-8")), output_root=root)
    print(
        json.dumps(
            {
                "schema": SCHEMA,
                "inventory_sha256": payload["inventory"]["sha256"],
                "inventory_rows": payload["inventory"]["row_count"],
                "inventory_rows_sha256": payload["inventory"]["rows_sha256"],
                "manifest": {
                    "path": relative_output_path(output, root),
                    **receipt,
                },
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
