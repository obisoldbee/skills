#!/usr/bin/env python3
"""Create a package-local candidate case from one URL or one local image."""

from __future__ import annotations

import argparse
import ipaddress
import mimetypes
import struct
from pathlib import Path
from urllib.parse import urlparse, urlunparse

from common import sha256_file, stable_id, utc_now, write_json


def canonical_url(raw: str) -> tuple[str | None, str | None]:
    parsed = urlparse(raw.strip())
    if parsed.scheme not in {"http", "https"} or not parsed.hostname or parsed.username or parsed.password:
        return None, "requires_public_http_url"
    host = parsed.hostname.lower().rstrip(".")
    if host == "localhost" or host.endswith(".local") or host.endswith(".internal"):
        return None, "local_or_internal_host"
    try:
        address = ipaddress.ip_address(host)
        if address.is_private or address.is_loopback or address.is_link_local or address.is_multicast or address.is_reserved:
            return None, "non_public_ip_literal"
    except ValueError:
        pass
    normalized = urlunparse((parsed.scheme, parsed.netloc, parsed.path or "/", "", parsed.query, ""))
    return normalized, None


def image_dimensions(path: Path) -> tuple[int | None, int | None]:
    data = path.read_bytes()[:32]
    if data.startswith(b"\x89PNG\r\n\x1a\n") and len(data) >= 24:
        return struct.unpack(">II", data[16:24])
    if data.startswith(b"GIF") and len(data) >= 10:
        return struct.unpack("<HH", data[6:10])
    if data.startswith(b"\xff\xd8"):
        with path.open("rb") as handle:
            handle.read(2)
            while True:
                marker = handle.read(2)
                if len(marker) != 2:
                    break
                while marker[0] != 0xFF:
                    marker = marker[1:] + handle.read(1)
                if marker[1] in {0xC0, 0xC1, 0xC2, 0xC3, 0xC5, 0xC6, 0xC7, 0xC9, 0xCA, 0xCB, 0xCD, 0xCE, 0xCF}:
                    length = int.from_bytes(handle.read(2), "big")
                    payload = handle.read(length - 2)
                    return int.from_bytes(payload[3:5], "big"), int.from_bytes(payload[1:3], "big")
                length_data = handle.read(2)
                if len(length_data) != 2:
                    break
                handle.seek(int.from_bytes(length_data, "big") - 2, 1)
    return None, None


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    source = parser.add_mutually_exclusive_group(required=True)
    source.add_argument("--url")
    source.add_argument("--image", type=Path)
    parser.add_argument("--package-root", type=Path, required=True)
    parser.add_argument("--out", type=Path, required=True)
    parser.add_argument("--case-id")
    parser.add_argument("--url-kind", choices=["web_page", "video_page"], default="web_page")
    parser.add_argument("--sensitivity", choices=["public", "internal", "private", "restricted"], default="public")
    parser.add_argument("--external-send-policy", choices=["none", "exact_approved_assets_only"], default="none")
    args = parser.parse_args()

    root = args.package_root.resolve()
    if args.url:
        url, blocked_reason = canonical_url(args.url)
        identifier = url or args.url
        record = {
            "schema": "web-bookmark-intelligence/intake/v1",
            "case_id": args.case_id or stable_id("case", identifier),
            "created_at": utc_now(),
            "input_kind": args.url_kind,
            "source_locator": url or args.url,
            "source_sha256": None,
            "network_safety": "needs_dns_validation_at_execution" if url else "blocked",
            "blocked_reason": blocked_reason,
            "route_request": "video_page_capture_then_media_access_check" if url and args.url_kind == "video_page" else "html_capture_pipeline" if url else "blocked",
            "sensitivity": args.sensitivity,
            "external_send_policy": args.external_send_policy,
            "formal_write_authorized": False,
            "install_authorized": False,
            "adoption_authorized": False,
        }
    else:
        image = args.image.resolve()
        if not image.is_file():
            raise SystemExit(f"image does not exist: {image}")
        width, height = image_dimensions(image)
        mime = mimetypes.guess_type(image.name)[0] or "application/octet-stream"
        is_long = bool(width and height and height / max(width, 1) >= 3)
        digest = sha256_file(image)
        record = {
            "schema": "web-bookmark-intelligence/intake/v1",
            "case_id": args.case_id or stable_id("case", digest),
            "created_at": utc_now(),
            "input_kind": "long_image" if is_long else "screenshot",
            "source_locator": str(image),
            "source_sha256": digest,
            "mime_type": mime,
            "dimensions": {"width": width, "height": height},
            "network_safety": "not_applicable",
            "blocked_reason": None,
            "route_request": "media_understanding_then_ocr" if is_long else "media_understanding_with_optional_ocr",
            "sensitivity": args.sensitivity,
            "external_send_policy": args.external_send_policy,
            "formal_write_authorized": False,
            "install_authorized": False,
            "adoption_authorized": False,
        }
    write_json(args.out, record, root)
    print(record["case_id"])
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
