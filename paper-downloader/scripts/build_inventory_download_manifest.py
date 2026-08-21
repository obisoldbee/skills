#!/usr/bin/env python3
"""Build a download manifest from Akashic paper inventory Markdown tables."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


def clean_cell(value: str) -> str:
    value = value.strip()
    value = value.strip("`")
    return value.strip()


def normalize_key(value: str) -> str:
    value = clean_cell(value).lower()
    value = re.sub(r"[^a-z0-9]+", "_", value)
    return value.strip("_")


def split_row(line: str) -> list[str]:
    return [clean_cell(cell) for cell in line.strip().strip("|").split("|")]


def looks_like_separator(line: str) -> bool:
    return bool(re.match(r"^\|\s*[-:| ]+\s*\|?$", line.strip()))


def iter_markdown_tables(text: str) -> list[tuple[list[str], list[dict[str, str]]]]:
    lines = text.splitlines()
    tables: list[tuple[list[str], list[dict[str, str]]]] = []
    index = 0
    while index < len(lines):
        if not lines[index].lstrip().startswith("|"):
            index += 1
            continue

        start = index
        while index < len(lines) and lines[index].lstrip().startswith("|"):
            index += 1
        block = lines[start:index]
        if len(block) < 2 or not looks_like_separator(block[1]):
            continue

        header = [normalize_key(cell) for cell in split_row(block[0])]
        rows: list[dict[str, str]] = []
        for line in block[2:]:
            if looks_like_separator(line):
                continue
            cells = split_row(line)
            if len(cells) < len(header):
                cells.extend([""] * (len(header) - len(cells)))
            rows.append(dict(zip(header, cells[: len(header)])))
        tables.append((header, rows))
    return tables


def first_value(row: dict[str, str], *keys: str) -> str:
    for key in keys:
        value = clean_cell(row.get(key, ""))
        if value:
            return value
    return ""


def pdf_url_from_row(row: dict[str, str]) -> str:
    for key in ("online_source_url", "original_publication_url", "url"):
        value = first_value(row, key)
        if value.lower().endswith(".pdf"):
            return value
    return ""


def row_has_identifier(row: dict[str, str]) -> bool:
    return any(first_value(row, key) for key in ("pmcid", "pmid", "doi", "pdf_url"))


def should_skip(row: dict[str, str], include_duplicates: bool) -> bool:
    text = " ".join(
        first_value(row, key)
        for key in ("final_status", "citation_use", "status_label", "download_status", "note")
    ).lower()
    if not include_duplicates and ("duplicate" in text or "do_not_cite" in text):
        return True
    return False


def build_rows(path: Path, include_duplicates: bool) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    seen: set[tuple[str, str, str, str]] = set()
    for table_index, (_header, table_rows) in enumerate(iter_markdown_tables(path.read_text(encoding="utf-8"))):
        for raw in table_rows:
            row_id = first_value(raw, "row_id", "id")
            title = first_value(raw, "title")
            if not row_id or not title:
                continue
            if should_skip(raw, include_duplicates):
                continue

            item = {
                "row_id": row_id,
                "title": title,
                "doi": first_value(raw, "doi"),
                "pmid": first_value(raw, "pmid"),
                "pmcid": first_value(raw, "pmcid"),
                "pdf_url": pdf_url_from_row(raw),
                "local_download_path": first_value(raw, "local_download_path"),
                "local_source_path": first_value(raw, "local_source_path"),
                "local_or_download_path": first_value(raw, "local_or_download_path"),
                "source_origin": first_value(raw, "source_origin"),
                "status": first_value(raw, "download_status", "final_status", "status_label"),
                "source_table_index": table_index,
                "inventory_path": str(path),
            }
            if not row_has_identifier(item):
                continue
            key = (
                str(item["pmcid"]).lower(),
                str(item["pmid"]).lower(),
                str(item["doi"]).lower(),
                str(item["title"]).lower(),
            )
            if key in seen:
                continue
            seen.add(key)
            rows.append(item)
    return rows


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--input", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    parser.add_argument("--include-duplicates", action="store_true")
    args = parser.parse_args()

    rows = build_rows(args.input, args.include_duplicates)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "input": str(args.input),
        "row_count": len(rows),
        "rows": rows,
    }
    args.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps({"input": str(args.input), "rows": len(rows)}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
