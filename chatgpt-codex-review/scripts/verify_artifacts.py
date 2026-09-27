#!/usr/bin/env python3
"""Verify saved web artifacts against a round-bound contract without executing them."""

import argparse
import hashlib
import json
from pathlib import Path, PurePosixPath
import re
import stat
import sys
import unicodedata
import warnings
import zipfile
import zlib

SHA256 = re.compile(r"[0-9a-f]{64}\Z")
NAME = re.compile(r"[A-Za-z0-9][A-Za-z0-9._-]*\Z")
KINDS = {"zip", "png", "json", "utf8"}
MAX_FILE = 128 * 1024 * 1024
MAX_MEMBER = 64 * 1024 * 1024
MAX_TOTAL = 256 * 1024 * 1024
MAX_MEMBERS = 2000
WINDOWS_DEVICES = {"CON", "PRN", "AUX", "NUL", *(f"COM{i}" for i in range(1, 10)),
                   *(f"LPT{i}" for i in range(1, 10))}


class UnverifiedFormatError(Exception):
    pass


def digest(contract):
    return hashlib.sha256(json.dumps(contract, sort_keys=True, ensure_ascii=False,
                                     separators=(",", ":")).encode("utf-8")).hexdigest()


def validate_contract(contract):
    if not isinstance(contract, dict) or set(contract) != {"required", "optional"}:
        raise ValueError("artifact_contract needs required and optional lists")
    seen = set()
    for category in ("required", "optional"):
        if not isinstance(contract[category], list):
            raise ValueError(category + " must be a list")
        for item in contract[category]:
            if (not isinstance(item, dict) or not isinstance(item.get("name"), str)
                    or not NAME.fullmatch(item["name"])):
                raise ValueError("invalid artifact name")
            if item["name"].casefold() in seen:
                raise ValueError("duplicate artifact name")
            seen.add(item["name"].casefold())
            if not isinstance(item.get("kind"), str) or item["kind"] not in KINDS:
                raise ValueError("unsupported artifact kind")
            if "sha256" in item and not SHA256.fullmatch(str(item["sha256"])):
                raise ValueError("invalid expected SHA-256")
            if "size" in item and (type(item["size"]) is not int or item["size"] < 0):
                raise ValueError("invalid expected size")
            if set(item) - {"name", "kind", "sha256", "size"}:
                raise ValueError("unsupported artifact contract field")


def safe_member(name):
    if not name or "\\" in name or "\x00" in name or name.startswith("/"):
        raise ValueError("unsafe ZIP member path")
    trimmed = name[:-1] if name.endswith("/") else name
    parts = PurePosixPath(trimmed).parts
    if not parts or any(part in {"", ".", ".."} for part in trimmed.split("/")):
        raise ValueError("unsafe ZIP member path")
    if any(ord(char) < 32 for char in name):
        raise ValueError("unsafe ZIP member path")
    for part in parts:
        if (any(char in '<>:"|?*' for char in part) or part.endswith((".", " "))
                or part.split(".", 1)[0].upper() in WINDOWS_DEVICES):
            raise ValueError("ZIP member has an unsafe Windows alias")
    normalized = unicodedata.normalize("NFC", "/".join(parts))
    if normalized != trimmed:
        raise ValueError("non-normalized ZIP member path")
    return normalized.casefold()


def verify_zip(path):
    seen = set()
    files = set()
    total = 0
    with zipfile.ZipFile(path) as archive:
        members = archive.infolist()
        if len(members) > MAX_MEMBERS:
            raise ValueError("ZIP member count exceeds bound")
        for member in members:
            key = safe_member(member.filename)
            if key in seen:
                raise ValueError("duplicate or case-colliding ZIP member")
            seen.add(key)
            if not member.is_dir():
                files.add(key)
            mode = (member.external_attr >> 16) & 0xFFFF
            if stat.S_ISLNK(mode):
                raise ValueError("ZIP symlink is not accepted")
            if member.flag_bits & 0x1:
                raise ValueError("encrypted ZIP member is not accepted")
            if member.file_size > MAX_MEMBER:
                raise ValueError("ZIP member exceeds size bound")
            total += member.file_size
            if total > MAX_TOTAL:
                raise ValueError("ZIP expanded size exceeds bound")
            if member.is_dir():
                continue
            read = 0
            with archive.open(member) as stream:
                while chunk := stream.read(1024 * 1024):
                    read += len(chunk)
                    if read > MAX_MEMBER or read > member.file_size:
                        raise ValueError("ZIP member expanded past declared size")
            if read != member.file_size:
                raise ValueError("ZIP member size mismatch")
        for key in seen:
            parts = key.split("/")
            if any("/".join(parts[:count]) in files for count in range(1, len(parts))):
                raise ValueError("ZIP file and child path conflict")
    return {"members": len(members), "expanded_bytes": total}


def verify_png(path):
    try:
        from PIL import Image, UnidentifiedImageError
    except ImportError as exc:
        raise UnverifiedFormatError("PNG decode unverified: Pillow is unavailable") from exc
    try:
        with warnings.catch_warnings():
            warnings.simplefilter("error", Image.DecompressionBombWarning)
            with Image.open(path) as img:
                if img.format != "PNG":
                    raise ValueError("file is not PNG")
                width, height = img.size
                img.verify()
            with Image.open(path) as img:
                img.load()
        return {"width": width, "height": height}
    except (UnidentifiedImageError, OSError, SyntaxError, Image.DecompressionBombWarning) as exc:
        raise ValueError("PNG failed full decode: " + str(exc)) from exc


def verify_one(item, path, root):
    if not isinstance(path, str) or not path:
        return {"status": "missing"}
    file = Path(path)
    if not file.is_absolute():
        return {"status": "invalid", "error": "artifact path must be absolute"}
    try:
        resolved = file.resolve(strict=True)
    except OSError as exc:
        return {"status": "invalid", "error": str(exc)}
    if not resolved.is_relative_to(root) or file.is_symlink() or not file.is_file():
        return {"status": "invalid", "error": "artifact must be a regular non-symlink file"}
    try:
        size = file.stat().st_size
        if size > MAX_FILE:
            raise ValueError("file exceeds size bound")
        h = hashlib.sha256()
        with file.open("rb") as stream:
            while chunk := stream.read(1024 * 1024):
                h.update(chunk)
        actual = h.hexdigest()
        base = {"path": str(resolved), "size": size, "sha256": actual,
                "origin_hash_matched": "sha256" in item}
        if "size" in item and size != item["size"]:
            raise ValueError("size mismatch")
        if "sha256" in item and actual != item["sha256"]:
            raise ValueError("SHA-256 mismatch")
        kind = item["kind"]
        if kind == "zip":
            details = verify_zip(file)
        elif kind == "png":
            details = verify_png(file)
        else:
            body = file.read_text(encoding="utf-8")
            if kind == "json":
                json.loads(body)
            details = {"utf8_chars": len(body)}
        return {**base, "status": "verified", "kind": kind, **details}
    except UnverifiedFormatError as exc:
        return {"status": "unverified", "error": str(exc)}
    except (OSError, UnicodeError, ValueError, RuntimeError, NotImplementedError,
            zipfile.BadZipFile, zlib.error, json.JSONDecodeError) as exc:
        return {"status": "invalid", "error": str(exc)}


def verify(document):
    if not isinstance(document, dict):
        raise ValueError("input must be an object")
    binding = document.get("binding")
    if not isinstance(binding, dict) or any(not binding.get(k) for k in
                                            ("run_id", "round", "source_id", "request_token",
                                             "consumer_host", "artifact_root")):
        raise ValueError("missing artifact binding")
    if type(binding["round"]) is not int or binding["round"] < 1:
        raise ValueError("round must be positive")
    root = Path(binding["artifact_root"])
    if not root.is_absolute() or root.is_symlink() or not root.is_dir():
        raise ValueError("artifact_root must be an existing absolute real directory")
    root = root.resolve(strict=True)
    contract = document.get("artifact_contract")
    validate_contract(contract)
    files = document.get("files")
    if not isinstance(files, dict):
        raise ValueError("files must be a name to path object")
    expected = {item["name"] for kind in ("required", "optional") for item in contract[kind]}
    if set(files) - expected:
        raise ValueError("unlisted artifact file")
    reports = {}
    for kind in ("required", "optional"):
        for item in contract[kind]:
            reports[item["name"]] = verify_one(item, files.get(item["name"]), root)
    ready = all(reports[item["name"]]["status"] == "verified" for item in contract["required"])
    return {"validator": "verify_artifacts/v2", "binding": binding,
            "contract_digest": digest(contract), "required_ready": ready, "files": reports}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", required=True, type=Path)
    args = parser.parse_args()
    try:
        report = verify(json.loads(args.input.read_text(encoding="utf-8")))
    except (ValueError, OSError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps({"valid": True, **report}, ensure_ascii=False, indent=2))
    return 0 if report["required_ready"] else 1


if __name__ == "__main__":
    sys.exit(main())
