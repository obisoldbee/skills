#!/usr/bin/env python3
"""Evaluate local HTML against conservative body/media gates; never fetch a URL."""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path

from common import (
    ensure_within,
    meaningful_char_count,
    package_relative,
    read_json,
    resolve_declared_path,
    sha256_file,
    utc_now,
    write_json,
)


PLACEHOLDER_TERMS = (
    "正在加载",
    "加载中",
    "请稍候",
    "点击展开",
    "登录后",
    "verify you are human",
    "enable javascript",
)


def strip_markup(fragment: str) -> str:
    fragment = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", fragment, flags=re.I | re.S)
    fragment = re.sub(r"<(nav|header|footer|aside)[^>]*>.*?</\1>", " ", fragment, flags=re.I | re.S)
    fragment = re.sub(r"<br\s*/?>", "\n", fragment, flags=re.I)
    fragment = re.sub(r"</(p|div|li|h[1-6])\s*>", "\n", fragment, flags=re.I)
    fragment = re.sub(r"<[^>]+>", " ", fragment)
    return re.sub(r"[ \t]+", " ", html.unescape(fragment)).strip()


def meta_description(document: str) -> str | None:
    for tag in re.findall(r"<meta\b[^>]*>", document, flags=re.I):
        attrs = {
            key.lower(): html.unescape(value)
            for key, value in re.findall(r"([\w:-]+)\s*=\s*['\"]([^'\"]*)['\"]", tag)
        }
        if attrs.get("name", "").lower() == "description":
            return attrs.get("content") or None
    return None


def title(document: str) -> str | None:
    match = re.search(r"<title[^>]*>(.*?)</title>", document, flags=re.I | re.S)
    return strip_markup(match.group(1)) if match else None


def body_region(document: str) -> str:
    cleaned = re.sub(r"<(script|style)[^>]*>.*?</\1>", " ", document, flags=re.I | re.S)
    for pattern in (
        r"<article\b[^>]*>(.*?)</article>",
        r"<main\b[^>]*>(.*?)</main>",
        r"<[^>]+id=['\"]js_content['\"][^>]*>(.*)",
    ):
        match = re.search(pattern, cleaned, flags=re.I | re.S)
        if match:
            return match.group(1)
    match = re.search(r"<body\b[^>]*>(.*?)</body>", cleaned, flags=re.I | re.S)
    return match.group(1) if match else cleaned


def dom_media_inventory(document: str) -> list[dict[str, object]]:
    """Return a deterministic occurrence inventory for body img/canvas nodes."""
    region = body_region(document)
    inventory: list[dict[str, object]] = []
    first_by_locator: dict[tuple[str, str], str] = {}
    for index, match in enumerate(
        re.finditer(r"<(img|canvas)\b([^>]*)>", region, flags=re.I), 1
    ):
        kind = match.group(1).lower()
        attributes = match.group(2)
        locator: str | None = None
        if kind == "img":
            source = re.search(
                r"\bsrc\s*=\s*(?:['\"]([^'\"]*)['\"]|([^\s>]+))",
                attributes,
                flags=re.I,
            )
            if source:
                locator = html.unescape(source.group(1) or source.group(2) or "").strip() or None
        else:
            canvas_id = re.search(
                r"\bid\s*=\s*(?:['\"]([^'\"]*)['\"]|([^\s>]+))",
                attributes,
                flags=re.I,
            )
            locator = (
                f"id:{html.unescape(canvas_id.group(1) or canvas_id.group(2) or '').strip()}"
                if canvas_id and (canvas_id.group(1) or canvas_id.group(2) or "").strip()
                else None
            )
        dom_id = f"media-{index:04d}"
        duplicate_of = None
        if locator is not None:
            key = (kind, locator)
            duplicate_of = first_by_locator.get(key)
            first_by_locator.setdefault(key, dom_id)
        inventory.append(
            {
                "dom_id": dom_id,
                "kind": kind,
                "locator": locator,
                "duplicate_of": duplicate_of,
            }
        )
    return inventory


def paragraphs(region: str) -> list[str]:
    values = [strip_markup(value) for value in re.findall(r"<p\b[^>]*>(.*?)</p>", region, flags=re.I | re.S)]
    values = [value for value in values if meaningful_char_count(value) >= 12]
    if values:
        return values
    text = strip_markup(region)
    return [line.strip() for line in re.split(r"\n{2,}", text) if meaningful_char_count(line) >= 12]


def is_placeholder_or_noise(body_text: str, paragraph_count: int) -> bool:
    normalized = body_text.lower()
    if any(term in normalized for term in PLACEHOLDER_TERMS):
        return True
    compact = re.sub(r"[\W_]+", "", body_text, flags=re.UNICODE)
    if paragraph_count == 0 or not compact:
        return True
    control_lines = sum(
        1
        for line in body_text.splitlines()
        if line.strip().lower() in {"分享", "更多", "关闭", "返回", "menu", "close", "more"}
    )
    return meaningful_char_count(body_text) < 120 and control_lines > 0


def decide_gate(document: str, rendered: bool) -> dict[str, object]:
    region = body_region(document)
    body_paragraphs = paragraphs(region)
    body_text = "\n\n".join(body_paragraphs)
    meaningful = meaningful_char_count(body_text)
    image_count = len(re.findall(r"<img\b", region, flags=re.I))
    has_canvas = bool(re.search(r"<canvas\b", region, flags=re.I))
    description = meta_description(document)
    placeholder_or_noise = is_placeholder_or_noise(body_text, len(body_paragraphs))
    substantive = meaningful >= 400 and len(body_paragraphs) >= 2 and not placeholder_or_noise
    if substantive:
        body_evidence_state = "substantive"
    elif placeholder_or_noise:
        body_evidence_state = "noise_or_placeholder"
    elif meaningful:
        body_evidence_state = "weak"
    else:
        body_evidence_state = "not_available"

    media_inventory_required = image_count > 0 or has_canvas
    if not rendered:
        if substantive:
            status, next_route = "pass", "media_inventory" if media_inventory_required else "purpose_handoff"
        elif has_canvas or image_count:
            status, next_route = "needs_playwright", "playwright_render_then_media_inventory"
        else:
            status, next_route = "needs_playwright", "playwright_render"
    elif has_canvas or (body_evidence_state != "substantive" and image_count > 0):
        status, next_route = "needs_media_understanding", "media_understanding_then_ocr"
    elif substantive:
        status, next_route = "pass", "media_inventory" if media_inventory_required else "purpose_handoff"
    else:
        status, next_route = "failed", "preserve_failure_evidence"

    return {
        "status": status,
        "next_route": next_route,
        "body_provenance": "dom_rendered" if rendered and body_text else "dom_static" if body_text else "not_available",
        "body_evidence_state": body_evidence_state,
        "body_text": body_text,
        "body_meaningful_chars": meaningful,
        "paragraph_count": len(body_paragraphs),
        "dom_noise_or_placeholder": placeholder_or_noise,
        "meta_description": description,
        "meta_description_as_body": False,
        "image_count": image_count,
        "has_canvas": has_canvas,
        "media_inventory_required": media_inventory_required,
        "final_evidence_status": "pending_evidence_fusion",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--html", type=Path, required=True)
    parser.add_argument("--intake", type=Path, required=True)
    parser.add_argument("--package-root", type=Path, required=True)
    parser.add_argument("--case-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--source-url")
    parser.add_argument("--rendered", action="store_true")
    parser.add_argument("--case-id")
    parser.add_argument("--media-asset", type=Path, action="append", default=[])
    args = parser.parse_args()

    root = args.package_root.resolve()
    case_root = ensure_within(args.case_root, root)
    html_path = ensure_within(args.html, case_root)
    intake_path = ensure_within(args.intake, case_root)
    out_path = ensure_within(args.out, case_root)
    if not html_path.is_file():
        raise SystemExit(f"HTML input does not exist: {html_path}")
    if not intake_path.is_file():
        raise SystemExit(f"intake record does not exist: {intake_path}")
    intake = read_json(intake_path)
    if not isinstance(intake, dict):
        raise SystemExit("intake record must be an object")
    if intake.get("schema") != "web-bookmark-intelligence/intake/v2":
        raise SystemExit("intake record must use web-bookmark-intelligence/intake/v2")
    intake_case_id = str(intake.get("case_id") or "")
    if not intake_case_id:
        raise SystemExit("intake record is missing case_id")
    if args.case_id and args.case_id != intake_case_id:
        raise SystemExit("case-id does not match intake record")
    declared_case_root = resolve_declared_path(intake.get("case_root"), root)
    if declared_case_root != case_root:
        raise SystemExit("case-root does not match intake record")
    if args.source_url and intake.get("source_locator") != args.source_url:
        raise SystemExit("source-url does not match intake record")

    document = html_path.read_text(encoding="utf-8", errors="replace")
    dom_inventory = dom_media_inventory(document)
    unique_dom_items = [item for item in dom_inventory if item["duplicate_of"] is None]
    if len(args.media_asset) > len(unique_dom_items):
        raise SystemExit("more media assets were supplied than unique DOM media items")
    asset_by_dom_id: dict[str, dict[str, object]] = {}
    source_assets: list[dict[str, object]] = []
    for dom_item, asset_arg in zip(unique_dom_items, args.media_asset):
        asset = ensure_within(asset_arg, case_root)
        if not asset.is_file() or asset.is_symlink():
            raise SystemExit(f"media asset must be a regular case-local file: {asset}")
        reference = {
            "path": package_relative(asset, root),
            "sha256": sha256_file(asset),
            "bytes": asset.stat().st_size,
        }
        asset_by_dom_id[str(dom_item["dom_id"])] = reference
        source_assets.append({**reference, "dom_ids": [dom_item["dom_id"]]})
    by_dom_id: dict[str, dict[str, object]] = {}
    bound_dom_inventory: list[dict[str, object]] = []
    for item in dom_inventory:
        source_reference = asset_by_dom_id.get(str(item["dom_id"]))
        if item["duplicate_of"] is not None:
            source_reference = by_dom_id[str(item["duplicate_of"])].get("source_asset")
            if source_reference is not None:
                for source_asset in source_assets:
                    if (
                        source_asset["path"] == source_reference["path"]
                        and source_asset["sha256"] == source_reference["sha256"]
                    ):
                        source_asset["dom_ids"].append(item["dom_id"])
                        break
        bound = {
            **item,
            "availability": "captured" if source_reference is not None else "unavailable",
            "source_asset": source_reference,
        }
        by_dom_id[str(item["dom_id"])] = bound
        bound_dom_inventory.append(bound)
    gate = decide_gate(document, args.rendered)
    record = {
        "schema": "web-bookmark-intelligence/capture-record/v3",
        "created_at": utc_now(),
        "case_id": intake_case_id,
        "case_root": package_relative(case_root, root),
        "intake": {"path": package_relative(intake_path, root), "sha256": sha256_file(intake_path)},
        "source": {
            "url": args.source_url,
            "local_html": package_relative(html_path, root),
            "sha256": sha256_file(html_path),
        },
        "source_assets": source_assets,
        "dom_media_inventory": bound_dom_inventory,
        "capture_adapter": "static_html_probe" if not args.rendered else "rendered_html_probe",
        "title": title(document),
        "quality_gate": gate,
        "capture_status": "captured_pending_evidence_fusion" if gate["status"] == "pass" else "partial" if gate["status"] != "failed" else "failed",
        "formal_write_authorized": False,
    }
    write_json(out_path, record, root)
    print(gate["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
