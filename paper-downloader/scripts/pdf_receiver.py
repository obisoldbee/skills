#!/usr/bin/env python3
"""Loopback PDF receiver that appends row-bound browser result attempts."""

from __future__ import annotations

import argparse
import json
import re
import sys
from http.server import BaseHTTPRequestHandler, HTTPServer
from pathlib import Path
from typing import Any


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from manifest_contract import (  # noqa: E402
    JOURNAL_SCHEMA,
    PDF_MIN_BYTES,
    atomic_create_bytes,
    atomic_write_json,
    canonical_identity,
    declared_output_path,
    declared_output_root,
    is_within,
    load_manifest,
    require_distinct_paths,
    sha256_bytes,
    sha256_file,
    verify_pdf,
)


class ReceiverState:
    def __init__(
        self,
        output_root: Path,
        manifest_path: Path,
        paper_dir: Path,
        journal_path: Path,
        manifest: dict[str, Any],
        journal: dict[str, Any],
        manifest_sha: str,
        journal_sha: str,
    ) -> None:
        self.output_root = output_root
        self.manifest_path = manifest_path
        self.paper_dir = paper_dir
        self.journal_path = journal_path
        self.manifest = manifest
        self.journal = journal
        self.manifest_sha = manifest_sha
        self.journal_sha = journal_sha
        self.downloaded = 0
        self.failed = 0


def safe_filename(value: str) -> str:
    name = Path(value).name
    name = re.sub(r"[^A-Za-z0-9._-]+", "_", name).strip("._")
    return (name or "paper.pdf")[:220]


def global_attempt_ids(
    rows: list[dict[str, Any]], *, source: str, require_ids: bool = False
) -> set[str]:
    seen: set[str] = set()
    for row in rows:
        attempts = row.get("attempts")
        if not isinstance(attempts, list):
            raise ValueError(f"{source} attempts must be an array: {row.get('row_id')}")
        for attempt in attempts:
            if not isinstance(attempt, dict):
                raise ValueError(f"{source} attempt must be an object: {row.get('row_id')}")
            attempt_id = str(attempt.get("attempt_id") or "").strip()
            if not attempt_id:
                if require_ids:
                    raise ValueError(f"{source} attempt_id is missing: {row.get('row_id')}")
                continue
            if attempt_id in seen:
                raise ValueError(f"global {source} attempt_id collision: {attempt_id}")
            seen.add(attempt_id)
    return seen


def load_state(
    manifest_path: Path,
    journal_path: Path,
    output_root: Path,
    paper_dir: Path,
) -> ReceiverState:
    root = declared_output_root(output_root)
    manifest_path = declared_output_path(manifest_path, root)
    paper_dir = declared_output_path(paper_dir, root)
    journal_path = declared_output_path(journal_path, root)
    require_distinct_paths(manifest=manifest_path, journal=journal_path, paper_dir=paper_dir)
    manifest = load_manifest(manifest_path, output_root=root)
    journal = json.loads(journal_path.read_text(encoding="utf-8"))
    if journal.get("schema") != JOURNAL_SCHEMA or not isinstance(journal.get("rows"), list):
        raise ValueError(f"journal must use schema {JOURNAL_SCHEMA}")
    if journal.get("inventory_sha256") != manifest["inventory"]["sha256"]:
        raise ValueError("journal inventory SHA does not match manifest")
    manifest_sha = sha256_file(manifest_path)
    if journal.get("manifest_sha256") != manifest_sha:
        raise ValueError("stale browser journal: manifest SHA does not match current manifest")
    expected_paper_dir = declared_output_path(
        Path(str(manifest.get("paper_root") or "papers")), root, allow_root=True
    )
    if paper_dir != expected_paper_dir:
        raise ValueError("receiver paper-dir must equal the manifest declared paper_root")
    if is_within(manifest_path, paper_dir) or is_within(journal_path, paper_dir):
        raise ValueError("receiver manifest and journal must be outside paper-dir")
    manifest_rows = {row["row_id"]: row for row in manifest["rows"]}
    journal_row_ids: set[str] = set()
    for entry in journal["rows"]:
        row_id = str(entry.get("row_id") or "")
        if row_id in journal_row_ids:
            raise ValueError(f"duplicate journal row entry: {row_id}")
        journal_row_ids.add(row_id)
        row = manifest_rows.get(row_id)
        if row is None or entry.get("identity") != canonical_identity(row):
            raise ValueError(f"journal row identity does not bind current manifest: {row_id}")
        for attempt in entry.get("attempts", []):
            if not isinstance(attempt, dict):
                raise ValueError(f"journal attempt must be an object: {row_id}")
            if attempt.get("row_id") != row_id or attempt.get("identity") != entry.get("identity"):
                raise ValueError(
                    f"journal attempt row/identity binding mismatch: {attempt.get('attempt_id')}"
                )
    manifest_attempts = global_attempt_ids(manifest["rows"], source="manifest")
    journal_attempts = global_attempt_ids(
        journal["rows"], source="journal", require_ids=True
    )
    if manifest_attempts & journal_attempts:
        raise ValueError("attempt_id collision between manifest and journal")
    journal_sha = sha256_file(journal_path)
    paper_dir.mkdir(parents=True, exist_ok=True)
    return ReceiverState(
        root,
        manifest_path,
        paper_dir,
        journal_path,
        manifest,
        journal,
        manifest_sha,
        journal_sha,
    )


def assert_receiver_cas(state: ReceiverState, target: Path | None = None) -> None:
    if sha256_file(state.manifest_path) != state.manifest_sha:
        raise ValueError("manifest changed while receiver was running")
    if sha256_file(state.journal_path) != state.journal_sha:
        raise ValueError("journal changed outside the receiver")
    if target is not None and target.exists():
        raise ValueError(f"receiver target CAS failed; path already exists: {target.name}")


def preflight_request(
    state: ReceiverState,
    row_id: str,
    attempt_id: str,
    identity: dict[str, str],
    filename: str,
) -> tuple[dict[str, Any], Path]:
    assert_receiver_cas(state)
    rows = [row for row in state.manifest["rows"] if row["row_id"] == row_id]
    entries = [entry for entry in state.journal["rows"] if entry.get("row_id") == row_id]
    if len(rows) != 1 or len(entries) != 1 or not attempt_id:
        raise ValueError("row id and attempt id must bind one manifest and journal row")
    if identity != canonical_identity(rows[0]) or identity != entries[0].get("identity"):
        raise ValueError("identity headers do not bind the canonical row")
    if rows[0].get("disposition") not in {None, "", "eligible"}:
        raise ValueError("receiver cannot target a non-eligible row")
    manifest_known = global_attempt_ids(state.manifest["rows"], source="manifest")
    journal_known = global_attempt_ids(
        state.journal["rows"], source="journal", require_ids=True
    )
    if manifest_known & journal_known:
        raise ValueError("attempt_id collision between manifest and journal")
    known = manifest_known | journal_known
    if attempt_id in known:
        raise ValueError(f"global attempt_id collision: {attempt_id}")
    target = declared_output_path(state.paper_dir / safe_filename(filename), state.output_root)
    assert_receiver_cas(state, target)
    return rows[0], target


def append_attempt(state: ReceiverState, row_id: str, attempt: dict[str, Any]) -> None:
    assert_receiver_cas(state)
    entries = [entry for entry in state.journal["rows"] if entry.get("row_id") == row_id]
    if len(entries) != 1:
        raise ValueError(f"journal must contain exactly one entry for row: {row_id}")
    entry = entries[0]
    if attempt["identity"] != entry.get("identity"):
        raise ValueError(f"attempt identity does not match journal: {row_id}")
    known_ids = global_attempt_ids(state.manifest["rows"], source="manifest")
    known_ids.update(
        global_attempt_ids(state.journal["rows"], source="journal", require_ids=True)
    )
    if attempt["attempt_id"] in known_ids:
        raise ValueError(f"global attempt_id collision: {attempt['attempt_id']}")
    entry.setdefault("attempts", []).append(attempt)
    try:
        atomic_write_json(state.journal_path, state.journal)
    except Exception:
        entry["attempts"].pop()
        raise
    state.journal_sha = sha256_file(state.journal_path)


def make_handler(state: ReceiverState) -> type[BaseHTTPRequestHandler]:
    class PDFReceiver(BaseHTTPRequestHandler):
        def send_json(self, status: int, payload: dict[str, Any]) -> None:
            data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
            self.send_response(status)
            self.send_header("Content-Type", "application/json; charset=utf-8")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Content-Length", str(len(data)))
            self.end_headers()
            self.wfile.write(data)

        def do_POST(self) -> None:  # noqa: N802
            if self.path != "/pdf":
                self.send_json(404, {"error": "unknown_path"})
                return
            try:
                row_id = str(self.headers.get("X-Row-Id") or "").strip()
                attempt_id = str(self.headers.get("X-Attempt-Id") or "").strip()
                identity = {
                    "kind": str(self.headers.get("X-Identity-Kind") or "").strip(),
                    "value": str(self.headers.get("X-Identity-Value") or "").strip(),
                }
                filename = safe_filename(str(self.headers.get("X-Filename") or f"{row_id}.pdf"))
                if not filename.lower().endswith(".pdf"):
                    filename += ".pdf"
                row, path = preflight_request(state, row_id, attempt_id, identity, filename)
                base_attempt: dict[str, Any] = {
                    "attempt_id": attempt_id,
                    "row_id": row_id,
                    "identity": identity,
                    "route": "browser_receiver",
                    "observed_url": str(self.headers.get("X-Observed-Url") or ""),
                    "observed_title": str(self.headers.get("X-Observed-Title") or ""),
                }
                length = int(self.headers.get("Content-Length") or "0")
                if length <= PDF_MIN_BYTES:
                    base_attempt.update(
                        {"outcome": "failed", "failure_reason": "pdf_not_larger_than_5120_bytes"}
                    )
                    append_attempt(state, row_id, base_attempt)
                    state.failed += 1
                    self.send_json(400, base_attempt)
                    return
                data = self.rfile.read(length)
                if len(data) != length or not data.startswith(b"%PDF"):
                    base_attempt.update(
                        {
                            "outcome": "failed",
                            "failure_reason": "body_length_or_pdf_magic_mismatch",
                            "response_bytes": len(data),
                            "response_sha256": sha256_bytes(data),
                            "observed_magic": data[:4].decode("latin-1", errors="replace"),
                        }
                    )
                    append_attempt(state, row_id, base_attempt)
                    state.failed += 1
                    self.send_json(400, base_attempt)
                    return

                method = str(self.headers.get("X-Identity-Match-Method") or "").strip()
                evidence = str(self.headers.get("X-Identity-Match-Evidence") or "").strip()
                assert_receiver_cas(state, path)
                atomic_create_bytes(path, data)
                receipt = verify_pdf(
                    path,
                    state.output_root,
                    row,
                    identity_match_method=method,
                    identity_match_evidence=evidence,
                )
                if not receipt["validated"]:
                    base_attempt.update(
                        {
                            "outcome": "needs_manual_review",
                            "failure_reason": receipt["failure_reason"],
                            "pdf_path": receipt["path"],
                            "identity_match_method": method,
                            "identity_match_evidence": evidence,
                            "candidate_pdf": receipt,
                        }
                    )
                    try:
                        append_attempt(state, row_id, base_attempt)
                    except Exception:
                        path.unlink(missing_ok=True)
                        raise
                    state.failed += 1
                    self.send_json(400, base_attempt)
                    return
                base_attempt.update(
                    {
                        "outcome": "downloaded",
                        "pdf_path": receipt["path"],
                        "pdf": receipt,
                        "identity_match_method": method,
                        "identity_match_evidence": evidence,
                    }
                )
                try:
                    append_attempt(state, row_id, base_attempt)
                except Exception:
                    path.unlink(missing_ok=True)
                    raise
                state.downloaded += 1
                self.send_json(200, {"outcome": "downloaded", "pdf": receipt})
            except (ValueError, OSError, json.JSONDecodeError) as exc:
                state.failed += 1
                self.send_json(400, {"outcome": "failed", "error": str(exc)})

        def do_OPTIONS(self) -> None:  # noqa: N802
            self.send_response(204)
            self.send_header("Access-Control-Allow-Origin", "*")
            self.send_header("Access-Control-Allow-Methods", "POST, GET, OPTIONS")
            self.send_header(
                "Access-Control-Allow-Headers",
                "Content-Type, X-Row-Id, X-Attempt-Id, X-Identity-Kind, "
                "X-Identity-Value, X-Filename, X-Observed-Url, X-Observed-Title, "
                "X-Identity-Match-Method, X-Identity-Match-Evidence",
            )
            self.end_headers()

        def do_GET(self) -> None:  # noqa: N802
            if self.path != "/status":
                self.send_json(404, {"error": "unknown_path"})
                return
            self.send_json(
                200,
                {"downloaded": state.downloaded, "failed": state.failed},
            )

        def log_message(self, _format: str, *_args: object) -> None:
            return

    return PDFReceiver


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--journal-out", required=True, type=Path)
    parser.add_argument("--paper-dir", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--port", required=True, type=int)
    args = parser.parse_args()
    if not 1 <= args.port <= 65535:
        parser.error("--port must be in 1..65535")
    state = load_state(
        args.manifest, args.journal_out, args.output_root, args.paper_dir
    )
    server = HTTPServer(("127.0.0.1", args.port), make_handler(state))
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    finally:
        server.server_close()
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
