#!/usr/bin/env python3
"""Build or verify a local review packet from an explicit file allowlist. No uploads."""

import argparse
import hashlib
import json
from pathlib import Path
import shutil
import stat
import sys
import zipfile

sys.path.insert(0, str(Path(__file__).resolve().parent))
from verify_artifacts import safe_member

SCHEMA = "chatgpt-codex-review/local-packet/v1"
MANIFEST = "SOURCE_MANIFEST.json"


def sha_stream(stream):
    digest = hashlib.sha256()
    while chunk := stream.read(1024 * 1024):
        digest.update(chunk)
    return digest.hexdigest()


def sha_file(path):
    with path.open("rb") as stream:
        return sha_stream(stream)


def source_file(root, relative):
    safe_member(relative)
    path = root
    for part in relative.split("/"):
        path = path / part
        if path.is_symlink():
            raise ValueError("source symlink is not allowed: " + relative)
    if not path.is_file() or not path.resolve().is_relative_to(root):
        raise ValueError("source must be a regular file inside root: " + relative)
    return path


def check_names(names):
    seen = set()
    for name in names:
        if not isinstance(name, str) or name.endswith("/"):
            raise ValueError("files must contain relative regular-file paths")
        key = safe_member(name)
        if key in seen:
            raise ValueError("duplicate or case-colliding file path")
        seen.add(key)
        parts = Path(name).parts
        if ".git" in parts or "__pycache__" in parts or any(
                part == ".env" or part.startswith(".env.") and part not in {".env.example", ".env.template"}
                for part in parts):
            raise ValueError("exclude repository metadata, caches and credential files: " + name)
    for name in seen:
        if any("/".join(name.split("/")[:i]) in seen for i in range(1, len(name.split("/")))):
            raise ValueError("file and child path conflict")


def validate_manifest(data):
    if not isinstance(data, dict) or data.get("schema") != SCHEMA:
        raise ValueError("invalid packet manifest schema")
    for key in ("scope", "authority_ref"):
        if not isinstance(data.get(key), str) or not data[key].strip():
            raise ValueError("manifest needs " + key)
    rows = data.get("files")
    if not isinstance(rows, list) or not rows or not all(isinstance(row, dict) for row in rows):
        raise ValueError("packet needs a non-empty file inventory")
    check_names([row.get("path") for row in rows])
    for row in rows:
        if (type(row.get("bytes")) is not int or row["bytes"] < 0
                or not isinstance(row.get("sha256"), str) or len(row["sha256"]) != 64
                or any(c not in "0123456789abcdef" for c in row["sha256"])):
            raise ValueError("invalid file byte count or SHA-256")
    excluded = data.get("exclusions", [])
    if not isinstance(excluded, list) or any(
            not isinstance(item, dict) or any(not isinstance(item.get(k), str) or not item[k].strip()
                                             for k in ("path", "reason")) for item in excluded):
        raise ValueError("exclusions need paths and reasons")


def verify_packet(archive_path, manifest_path):
    for path in (archive_path, manifest_path):
        if path.is_symlink() or not path.is_file():
            raise ValueError("packet and manifest must be regular files")
    archive_hash = sha_file(archive_path)
    raw = manifest_path.read_bytes()
    manifest_hash = hashlib.sha256(raw).hexdigest()
    manifest = json.loads(raw)
    validate_manifest(manifest)
    expected = {"files/" + row["path"]: row for row in manifest["files"]}
    with zipfile.ZipFile(archive_path) as archive:
        infos = archive.infolist()
        if len(infos) != len(expected) + 1 or {i.filename for i in infos} != set(expected) | {MANIFEST}:
            raise ValueError("ZIP members do not exactly match the frozen inventory")
        for info in infos:
            safe_member(info.filename)
            if info.is_dir() or stat.S_ISLNK(info.external_attr >> 16) or info.flag_bits & 1:
                raise ValueError("ZIP contains a directory, symlink or encrypted member")
            if info.filename == MANIFEST:
                if info.file_size != len(raw) or archive.read(info) != raw:
                    raise ValueError("embedded manifest differs from supplied manifest")
                continue
            row = expected[info.filename]
            if info.file_size != row["bytes"]:
                raise ValueError("packet file size mismatch: " + row["path"])
            with archive.open(info) as stream:
                if sha_stream(stream) != row["sha256"]:
                    raise ValueError("packet file hash mismatch: " + row["path"])
    if sha_file(archive_path) != archive_hash or manifest_path.read_bytes() != raw:
        raise ValueError("packet changed during verification")
    return {"route": "local_packet", "status": "ready_to_upload",
            "source_id": "packet:" + archive_hash,
            "source_binding": {"archive_sha256": archive_hash, "manifest_sha256": manifest_hash},
            "local_packet": {"archive_path": str(archive_path.resolve()),
                             "manifest_path": str(manifest_path.resolve()),
                             "file_count": len(expected)},
            "uploaded": False, "web_read_verified": False}


def build_packet(root, selection, output):
    root = root.expanduser().resolve(strict=True)
    if not root.is_dir() or not isinstance(selection, dict):
        raise ValueError("root must be a directory and selection an object")
    names = selection.get("files")
    if not isinstance(names, list) or not names:
        raise ValueError("selection needs a non-empty explicit files list")
    check_names(names)
    rows = []
    for relative in sorted(names):
        path = source_file(root, relative)
        rows.append({"path": relative, "bytes": path.stat().st_size, "sha256": sha_file(path)})
    manifest = {"schema": SCHEMA, "scope": selection.get("scope"),
                "authority_ref": selection.get("authority_ref"),
                "files": rows, "exclusions": selection.get("exclusions", [])}
    validate_manifest(manifest)
    raw = (json.dumps(manifest, ensure_ascii=False, sort_keys=True, indent=2) + "\n").encode("utf-8")
    output = output.expanduser().absolute()
    # Exclusive directory creation protects existing packets and all input paths.
    output.mkdir(parents=True, exist_ok=False)
    archive_path, manifest_path = output / "source.zip", output / MANIFEST
    try:
        with manifest_path.open("xb") as stream:
            stream.write(raw)
        with zipfile.ZipFile(archive_path, "x", compression=zipfile.ZIP_DEFLATED) as archive:
            def info(name):
                item = zipfile.ZipInfo(name, date_time=(1980, 1, 1, 0, 0, 0))
                item.compress_type = zipfile.ZIP_DEFLATED
                item.external_attr = (stat.S_IFREG | 0o644) << 16
                return item
            archive.writestr(info(MANIFEST), raw)
            for row in rows:
                path = source_file(root, row["path"])
                with path.open("rb") as source, archive.open(info("files/" + row["path"]), "w", force_zip64=True) as dest:
                    shutil.copyfileobj(source, dest)
        result = verify_packet(archive_path, manifest_path)
        for row in rows:
            if sha_file(source_file(root, row["path"])) != row["sha256"]:
                raise ValueError("source changed while freezing packet: " + row["path"])
        return result
    except Exception:
        # Remove only this invocation's exclusive outputs, never caller sources.
        archive_path.unlink(missing_ok=True)
        manifest_path.unlink(missing_ok=True)
        output.rmdir()
        raise


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest="command", required=True)
    build = commands.add_parser("build")
    build.add_argument("--root", required=True, type=Path)
    build.add_argument("--selection", required=True, type=Path)
    build.add_argument("--output", required=True, type=Path)
    verify = commands.add_parser("verify")
    verify.add_argument("--archive", required=True, type=Path)
    verify.add_argument("--manifest", required=True, type=Path)
    args = parser.parse_args()
    try:
        result = (build_packet(args.root, json.loads(args.selection.read_text(encoding="utf-8")), args.output)
                  if args.command == "build" else verify_packet(args.archive, args.manifest))
    except (ValueError, OSError, zipfile.BadZipFile, RuntimeError) as exc:
        print(json.dumps({"valid": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps({"valid": True, **result}, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
