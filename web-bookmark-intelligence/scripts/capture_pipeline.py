#!/usr/bin/env python3
"""Evaluate local HTML against conservative body/media gates; never fetch a URL."""

from __future__ import annotations

import argparse
import html
import re
from pathlib import Path

from common import meaningful_char_count, sha256_file, utc_now, write_json


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
    parser.add_argument("--package-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--source-url")
    parser.add_argument("--rendered", action="store_true")
    parser.add_argument("--case-id")
    args = parser.parse_args()

    html_path = args.html.resolve()
    if not html_path.is_file():
        raise SystemExit(f"HTML input does not exist: {html_path}")
    document = html_path.read_text(encoding="utf-8", errors="replace")
    gate = decide_gate(document, args.rendered)
    record = {
        "schema": "web-bookmark-intelligence/capture-record/v2",
        "created_at": utc_now(),
        "case_id": args.case_id,
        "source": {"url": args.source_url, "local_html": str(html_path), "sha256": sha256_file(html_path)},
        "capture_adapter": "static_html_probe" if not args.rendered else "rendered_html_probe",
        "title": title(document),
        "quality_gate": gate,
        "capture_status": "captured_pending_evidence_fusion" if gate["status"] == "pass" else "partial" if gate["status"] != "failed" else "failed",
        "formal_write_authorized": False,
    }
    write_json(args.out, record, args.package_root.resolve())
    print(gate["status"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
