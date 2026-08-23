# Package Contract

Use this file when a download run writes into `12-agent-submissions`.

## Allowed Package Layout

Write only inside the active package:

```text
12-agent-submissions/YYYY/MM/DD/<package_id>/
  payload/
    papers/
    source-collection/
      download-status.md
      download-manifest.json
      browser-result-journal.json
      browser-apply-receipt.json
      rebuild-receipt.json
      final-report-receipt.json
      download-coverage.md
      failed-downloads.md
      failure-screenshots/
```

If the caller gives a sharded download task, write shard-local files:

```text
payload/source-collection/download-shards/<shard_id>/
  input.md
  download-status.md
  download-manifest.json
  failed-downloads.md
```

Do not create global directories such as `12-agent-submissions/papers/`, and do not place a package directly under `12-agent-submissions/` without the date hierarchy.

## Canonical Manifest Envelope

There is one versioned manifest envelope: `paper-downloader/download-manifest/v2`.
It binds the resolved frozen-inventory path, its SHA-256, total data-row count,
the SHA-256 of the complete frozen row-binding projection, the detected
`markdown|csv` format, and the complete ordered canonical `row_ids` list. Every
inventory data row appears once, including rows with no source row id, no title, no stable
identifier, a do-not-cite disposition, or a duplicate identity. Generated row
ids preserve a `source_coordinate`; duplicates preserve `duplicate_of` instead
of disappearing.

Do not persist a bare row array or a second manifest shape. Do not use both
`status` and `download_status`.

## Manifest Row Shape

Each row should include these fields when available:

```json
{
  "row_id": "paper-0001",
  "title": "",
  "doi": "",
  "pmid": "",
  "pmcid": "",
  "source_origin": "local|online",
  "input_url": "",
  "original_publication_url": "",
  "source_row_id": "",
  "source_coordinate": {"table_index": 0, "row_index": 0, "line": 1, "format": "markdown"},
  "disposition": "eligible",
  "duplicate_of": null,
  "attempts": [],
  "status": "pending|downloaded|verified_abstract|browser_required|manual_browser_required|paywalled|paywalled_or_no_pdf|access_blocked|unverified_citation|duplicate|needs_manual_review|failed",
  "failure_reason": "",
  "failure_screenshot_path": "",
  "failure_screenshot_error": "",
  "observed_url": "",
  "observed_title": "",
  "pubmed_full_text_checked": false,
  "pubmed_full_text_links": [],
  "pmcid_followup_required": false,
  "pdf": {
    "validated": false,
    "path": "",
    "bytes": 0,
    "sha256": "",
    "magic": "",
    "failure_reason": "not_downloaded",
    "identity_match": {
      "method": null,
      "evidence": null,
      "matched": false,
      "reason": "not_checked"
    }
  }
}
```

`bytes` is the only size unit. A `downloaded` row is invalid unless the file is
inside the declared output root, is reread from disk, is strictly larger than
5120 bytes, starts with `%PDF`, has matching exact bytes and SHA-256, and has an
actual strict-boundary DOI/PMID/PMCID match in its PDF bytes or an exact PDF
Title metadata match. Filename, route URL, HTTP/client headers, and caller text
are audit claims only. If disk-derived identity cannot be proved, retain the
structurally valid PDF candidate as `needs_manual_review`.

## Browser Result Journal

Browser preparation writes `paper-downloader/browser-result-journal/v1`. It
binds the canonical manifest hash and inventory SHA. Every entry and attempt
must repeat the canonical `row_id` and identity. Browser failures remain in the
journal. Executors and the loopback receiver require the journal base manifest
SHA to equal the current manifest before navigation or request-body read.
`apply_browser_result_journal.py` rejects orphan or mismatched rows, global
attempt-id collisions, and same-id changed content; it is the only supported
way for a browser result to update the canonical manifest.

## Existing Local Sources

If an item is already present in Akashic or in the current package:

- mark `source_origin: local`;
- record the local path;
- do not download it again;
- keep it available for later expert discussion if it is topic-relevant.

## Reporting

Every download shard must report:

- input rows;
- downloaded files;
- abstract-only rows;
- verified local rows;
- paywalled or access-blocked rows;
- unverified citations;
- duplicates;
- exact blockers.
- browser-required rows separately from final blocked rows.
- PubMed full-text / PMCID follow-up coverage for rows with PMID or PMCID.
- failure screenshot paths for browser-attempted non-download rows when available.
- clickable DOI, PubMed, PMC, and observed-page links for unresolved rows when available.

## Failure Screenshots

For browser-attempted rows that end as `failed`, `manual_browser_required`, `paywalled`, or `paywalled_or_no_pdf`, save a screenshot of the observed page state when feasible:

```text
payload/source-collection/failure-screenshots/
payload/source-collection/download-shards/<shard_id>/failure-screenshots/
```

Record the screenshot path in `failure_screenshot_path` and keep `failure_reason`, `observed_url`, and `observed_title` explicit enough for later review.

These screenshots are package-local diagnostic evidence only. During formal absorption, do not copy failure screenshots into `01-sources`, do not create SourceRecords for them, and do not treat them as paper/source payloads. They may be retained in the 12 package for audit, then ignored or pruned with package retention.

The coordinator may merge shard manifests only after each shard passes
disk-state validation. Final reports require an exact inventory SHA/row-id
and frozen-row-binding readback plus an exact manifest-to-disk PDF set; missing,
extra, tampered, escaped, or multiply claimed paths fail closed. Queue states,
pending PMID/PMCID follow-up, eligible manual-review rows, missing failure
reasons, or missing observable browser evidence block a `complete` receipt. The
receipt records relative output paths, hashes, and bytes but never recursively
hashes itself.
