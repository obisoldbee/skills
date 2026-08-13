#!/usr/bin/env python3
"""Small standard-library helpers for the package-local candidate skill."""

from __future__ import annotations

import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path


def utc_now() -> str:
    return datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def stable_id(prefix: str, value: str, length: int = 12) -> str:
    return f"{prefix}-{hashlib.sha256(value.encode('utf-8')).hexdigest()[:length]}"


def ensure_within(target: Path, package_root: Path) -> Path:
    root = package_root.resolve()
    resolved = target.resolve()
    try:
        resolved.relative_to(root)
    except ValueError as exc:
        raise ValueError(f"write target escapes package root: {target}") from exc
    return resolved


def write_json(target: Path, data: object, package_root: Path) -> None:
    target = ensure_within(target, package_root)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(target.suffix + ".tmp")
    temporary.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    os.replace(temporary, target)


def write_text(target: Path, value: str, package_root: Path) -> None:
    """Atomically write a UTF-8 evidence artifact inside the package root."""
    target = ensure_within(target, package_root)
    target.parent.mkdir(parents=True, exist_ok=True)
    temporary = target.with_suffix(target.suffix + ".tmp")
    temporary.write_text(value, encoding="utf-8")
    os.replace(temporary, target)


def read_json(path: Path) -> object:
    return json.loads(path.read_text(encoding="utf-8"))


def meaningful_char_count(text: str) -> int:
    return sum(1 for char in text if char.isalnum())
