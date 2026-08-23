#!/usr/bin/env python3
"""Shared single-attempt browser executor for DOI and PMC result journals."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path
from typing import Any
from urllib.parse import urljoin


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
    sha256_file,
    utc_now,
    verify_pdf,
)


def safe_name(value: str) -> str:
    return re.sub(r"[^A-Za-z0-9._-]+", "_", value).strip("._")[:180] or "paper"


def load_bound_row(
    manifest_path: Path, journal_path: Path, output_root: Path, row_id: str
) -> tuple[dict[str, Any], dict[str, Any], dict[str, Any], Path, str, str]:
    manifest_path = declared_output_path(manifest_path, output_root)
    journal_path = declared_output_path(journal_path, output_root)
    manifest = load_manifest(manifest_path, output_root=output_root)
    journal = json.loads(journal_path.read_text(encoding="utf-8"))
    if journal.get("schema") != JOURNAL_SCHEMA or not isinstance(journal.get("rows"), list):
        raise ValueError(f"journal must use schema {JOURNAL_SCHEMA}")
    if journal.get("inventory_sha256") != manifest["inventory"]["sha256"]:
        raise ValueError("journal inventory SHA does not match manifest")
    manifest_sha = sha256_file(manifest_path)
    if journal.get("manifest_sha256") != manifest_sha:
        raise ValueError("stale browser journal: manifest SHA does not match current manifest")
    manifest_rows = {row["row_id"]: row for row in manifest["rows"]}
    seen_journal_rows: set[str] = set()
    seen_attempt_ids: dict[str, str] = {}
    for journal_entry in journal["rows"]:
        if not isinstance(journal_entry, dict) or not isinstance(journal_entry.get("attempts"), list):
            raise ValueError("every journal row must contain an attempts array")
        entry_row_id = str(journal_entry.get("row_id") or "")
        if not entry_row_id or entry_row_id in seen_journal_rows:
            raise ValueError(f"journal row_id must be non-empty and unique: {entry_row_id}")
        seen_journal_rows.add(entry_row_id)
        manifest_row = manifest_rows.get(entry_row_id)
        if manifest_row is None or journal_entry.get("identity") != canonical_identity(manifest_row):
            raise ValueError(f"journal row identity does not bind current manifest: {entry_row_id}")
        for attempt in journal_entry["attempts"]:
            if not isinstance(attempt, dict):
                raise ValueError(f"journal attempt must be an object: {entry_row_id}")
            attempt_id = str(attempt.get("attempt_id") or "").strip()
            if not attempt_id:
                raise ValueError("journal attempt_id is missing")
            if (
                attempt.get("row_id") != entry_row_id
                or attempt.get("identity") != journal_entry.get("identity")
            ):
                raise ValueError(f"journal attempt row/identity binding mismatch: {attempt_id}")
            previous = seen_attempt_ids.get(attempt_id)
            if previous is not None:
                raise ValueError(f"global journal attempt_id collision: {attempt_id}:{previous}")
            seen_attempt_ids[attempt_id] = str(journal_entry.get("row_id") or "")
    rows = [row for row in manifest["rows"] if row["row_id"] == row_id]
    entries = [entry for entry in journal.get("rows", []) if entry.get("row_id") == row_id]
    if len(rows) != 1 or len(entries) != 1:
        raise ValueError("row id must bind exactly one manifest row and journal entry")
    if entries[0].get("identity") != canonical_identity(rows[0]):
        raise ValueError("journal identity does not match canonical manifest row")
    return rows[0], entries[0], journal, manifest_path, manifest_sha, sha256_file(journal_path)


def route_for(kind: str, row: dict[str, Any]) -> tuple[str, str, str]:
    if kind == "doi":
        value = str(row.get("doi") or "").strip()
        if not value:
            raise ValueError("DOI browser route requires a DOI on the bound row")
        return f"https://doi.org/{value}", "doi_route", value
    if kind == "pmc":
        value = str(row.get("pmcid") or "").strip().upper()
        if not re.fullmatch(r"PMC\d+", value):
            raise ValueError("PMC browser route requires a valid PMCID on the bound row")
        return f"https://pmc.ncbi.nlm.nih.gov/articles/{value}/", "pmcid_route", value
    if kind == "pubmed":
        value = str(row.get("pmid") or "").strip()
        if not re.fullmatch(r"\d+", value):
            raise ValueError("PubMed browser route requires a valid PMID on the bound row")
        return f"https://pubmed.ncbi.nlm.nih.gov/{value}/", "pmid_route", value
    raise ValueError(f"unsupported browser route: {kind}")


def page_outcome(body_text: str) -> tuple[str, str]:
    low = body_text.lower()
    if any(marker in low for marker in ("captcha", "checking your browser", "verify you are human")):
        return "manual_browser_required", "human_verification_required"
    if any(marker in low for marker in ("purchase this article", "buy article", "institutional access", "subscribe to")):
        return "paywalled", "observed_paywall"
    return "browser_required", "no_verified_pdf_observed"


def discovered_pdf_url(page: Any) -> str:
    locator = page.locator(
        'meta[name="citation_pdf_url"], a[href$=".pdf"], a[href*="/pdf/"]'
    ).first
    if not locator.count():
        return ""
    value = locator.get_attribute("content") or locator.get_attribute("href") or ""
    return urljoin(page.url, value)


def pubmed_full_text_links(page: Any) -> tuple[bool, list[str]]:
    selector = (
        ".full-text-links-list a, .full-text-links a, "
        "a[data-ga-action='full_text'], a[href*='pmc.ncbi.nlm.nih.gov/articles/']"
    )
    try:
        values = page.locator(selector).evaluate_all(
            "elements => elements.map(element => element.href).filter(Boolean)"
        )
    except Exception:
        return False, []
    links = [urljoin(page.url, str(value)) for value in values if str(value).strip()]
    return True, list(dict.fromkeys(links))


def append_attempt(
    journal_path: Path,
    journal: dict[str, Any],
    entry: dict[str, Any],
    attempt: dict[str, Any],
    expected_journal_sha: str,
) -> None:
    if sha256_file(journal_path) != expected_journal_sha:
        raise ValueError("journal changed during browser attempt")
    attempt_id = attempt["attempt_id"]
    for journal_entry in journal["rows"]:
        if any(item.get("attempt_id") == attempt_id for item in journal_entry.get("attempts", [])):
            raise ValueError(f"global journal attempt_id collision: {attempt_id}")
    entry.setdefault("attempts", []).append(attempt)
    try:
        atomic_write_json(journal_path, journal)
    except Exception:
        entry["attempts"].pop()
        raise


def assert_execution_cas(
    manifest_path: Path,
    manifest_sha: str,
    journal_path: Path,
    journal_sha: str,
    target_path: Path | None = None,
) -> None:
    if sha256_file(manifest_path) != manifest_sha:
        raise ValueError("manifest changed during browser attempt")
    if sha256_file(journal_path) != journal_sha:
        raise ValueError("journal changed during browser attempt")
    if target_path is not None and target_path.exists():
        raise ValueError(f"browser target CAS failed; path already exists: {target_path.name}")


def capture_failure_screenshot(page: Any, screenshot: Path, root: Path) -> dict[str, Any]:
    data = page.screenshot(full_page=True)
    if not isinstance(data, bytes) or not data:
        raise ValueError("browser screenshot returned no bytes")
    receipt = atomic_create_bytes(screenshot, data)
    return {
        "failure_screenshot_path": screenshot.relative_to(root).as_posix(),
        "failure_screenshot": {
            "path": screenshot.relative_to(root).as_posix(),
            **receipt,
        },
    }


def execute_browser_route(kind: str, args: Any) -> dict[str, Any]:
    root = declared_output_root(args.output_root)
    journal_path = declared_output_path(args.journal, root)
    paper_dir = declared_output_path(args.paper_dir, root)
    screenshot_dir = declared_output_path(args.screenshot_dir, root)
    row, entry, journal, manifest_path, manifest_sha, journal_sha = load_bound_row(
        args.manifest, journal_path, root, args.row_id
    )
    require_distinct_paths(
        manifest=manifest_path,
        journal=journal_path,
        paper_dir=paper_dir,
        screenshot_dir=screenshot_dir,
    )
    manifest_payload = load_manifest(manifest_path, output_root=root)
    expected_paper_dir = declared_output_path(
        Path(str(manifest_payload.get("paper_root") or "papers")), root
    )
    if paper_dir != expected_paper_dir:
        raise ValueError("browser paper-dir must equal the manifest declared paper_root")
    if is_within(screenshot_dir, paper_dir) or is_within(paper_dir, screenshot_dir):
        raise ValueError("browser screenshot-dir and paper-dir must be separate trees")
    route_url, identity_method, identifier = route_for(kind, row)
    identity = canonical_identity(row)
    if identity is None:
        raise ValueError("browser route requires a stable canonical identity")
    attempt_id = str(args.attempt_id or "").strip()
    if not attempt_id:
        raise ValueError("attempt_id must not be empty")
    if any(
        str(attempt.get("attempt_id") or "") == attempt_id
        for journal_entry in journal["rows"]
        for attempt in journal_entry.get("attempts", [])
        if isinstance(attempt, dict)
    ):
        raise ValueError(f"attempt_id already exists in journal: {attempt_id}")
    manifest_attempt_ids = {
        str(attempt.get("attempt_id"))
        for manifest_row in manifest_payload["rows"]
        for attempt in manifest_row.get("attempts", [])
        if isinstance(attempt, dict) and attempt.get("attempt_id")
    }
    if attempt_id in manifest_attempt_ids:
        raise ValueError(f"attempt_id already exists in manifest: {attempt_id}")
    filename = f"{safe_name(row['row_id'])}__{safe_name(identifier)}__{kind}_browser.pdf"
    pdf_target = declared_output_path(paper_dir / filename, root)
    assert_execution_cas(manifest_path, manifest_sha, journal_path, journal_sha, pdf_target)

    try:
        from playwright.sync_api import sync_playwright
    except ModuleNotFoundError as exc:
        raise SystemExit(
            "blocked_runtime_missing_python_playwright: do not install it or mark the row failed"
        ) from exc

    paper_dir.mkdir(parents=True, exist_ok=True)
    screenshot_dir.mkdir(parents=True, exist_ok=True)
    attempt: dict[str, Any] = {
        "attempt_id": attempt_id,
        "row_id": row["row_id"],
        "identity": identity,
        "route": f"{kind}_browser",
        "route_url": route_url,
        "attempted_at": utc_now(),
    }
    if kind == "pmc":
        attempt["pmcid_route_checked"] = True
    if kind == "pubmed":
        attempt["pubmed_full_text_checked"] = False
        attempt["pubmed_full_text_links"] = []
    written_pdf: Path | None = None

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(headless=False)
        context = browser.new_context(accept_downloads=False)
        page = None
        try:
            page = context.pages[0] if context.pages else context.new_page()
            page.goto(route_url, wait_until="domcontentloaded", timeout=args.timeout_ms)
            attempt["observed_url"] = page.url
            attempt["observed_title"] = page.title()
            body_text = page.locator("body").inner_text(timeout=5000)
            pdf_url = discovered_pdf_url(page)
            prefetched_pdf: bytes | None = None
            if kind == "pubmed":
                checked, full_text_links = pubmed_full_text_links(page)
                attempt["pubmed_full_text_checked"] = checked
                attempt["pubmed_full_text_links"] = full_text_links
                if not pdf_url:
                    for full_text_url in full_text_links:
                        full_text_response = page.request.get(full_text_url, timeout=args.timeout_ms)
                        full_text_body = full_text_response.body()
                        if (
                            full_text_response.ok
                            and len(full_text_body) > PDF_MIN_BYTES
                            and full_text_body.startswith(b"%PDF")
                        ):
                            pdf_url = full_text_url
                            prefetched_pdf = full_text_body
                            break
                        page.goto(full_text_url, wait_until="domcontentloaded", timeout=args.timeout_ms)
                        attempt["observed_url"] = page.url
                        attempt["observed_title"] = page.title()
                        body_text += "\n" + page.locator("body").inner_text(timeout=5000)
                        pdf_url = discovered_pdf_url(page)
                        if pdf_url:
                            break
            if pdf_url:
                response = None if prefetched_pdf is not None else page.request.get(pdf_url, timeout=args.timeout_ms)
                data = prefetched_pdf if prefetched_pdf is not None else response.body()
                response_ok = True if response is None else response.ok
                if response_ok and len(data) > PDF_MIN_BYTES and data.startswith(b"%PDF"):
                    assert_execution_cas(manifest_path, manifest_sha, journal_path, journal_sha, pdf_target)
                    atomic_create_bytes(pdf_target, data)
                    written_pdf = pdf_target
                    receipt = verify_pdf(
                        pdf_target,
                        root,
                        row,
                        identity_match_method=identity_method,
                        identity_match_evidence=route_url,
                    )
                    attempt.update(
                        {
                            "outcome": "downloaded" if receipt["validated"] else "needs_manual_review",
                            "pdf_path": receipt["path"],
                            "pdf": receipt,
                            "identity_match_method": identity_method,
                            "identity_match_evidence": route_url,
                            "failure_reason": receipt["failure_reason"],
                            "candidate_pdf": receipt if not receipt["validated"] else None,
                        }
                    )
                else:
                    attempt["outcome"], attempt["failure_reason"] = page_outcome(body_text)
            else:
                attempt["outcome"], attempt["failure_reason"] = page_outcome(body_text)
            if attempt["outcome"] != "downloaded":
                screenshot = screenshot_dir / f"{safe_name(row['row_id'])}__{safe_name(attempt_id)}.png"
                try:
                    attempt.update(capture_failure_screenshot(page, screenshot, root))
                except Exception as exc:  # browser evidence boundary
                    attempt["failure_screenshot_error"] = f"{type(exc).__name__}:{exc}"[:200]
        except Exception as exc:  # runtime/browser observation boundary
            if written_pdf is not None and not attempt.get("outcome"):
                written_pdf.unlink(missing_ok=True)
                written_pdf = None
            attempt["outcome"] = "browser_required"
            attempt["failure_reason"] = f"browser_execution_error:{type(exc).__name__}:{exc}"[:300]
            if page is not None:
                try:
                    attempt["observed_url"] = page.url
                    attempt["observed_title"] = page.title()
                except Exception:
                    pass
                screenshot = screenshot_dir / f"{safe_name(row['row_id'])}__{safe_name(attempt_id)}.png"
                try:
                    attempt.update(capture_failure_screenshot(page, screenshot, root))
                except Exception as screenshot_exc:
                    attempt["failure_screenshot_error"] = (
                        f"{type(screenshot_exc).__name__}:{screenshot_exc}"[:200]
                    )
            else:
                attempt["failure_screenshot_error"] = "browser_page_not_created"
        finally:
            try:
                context.close()
            except Exception as exc:
                attempt["browser_context_close_error"] = f"{type(exc).__name__}:{exc}"[:200]
            try:
                browser.close()
            except Exception as exc:
                attempt["browser_close_error"] = f"{type(exc).__name__}:{exc}"[:200]

    try:
        assert_execution_cas(manifest_path, manifest_sha, journal_path, journal_sha)
        append_attempt(journal_path, journal, entry, attempt, journal_sha)
    except Exception:
        if written_pdf is not None:
            written_pdf.unlink(missing_ok=True)
        raise
    return attempt
