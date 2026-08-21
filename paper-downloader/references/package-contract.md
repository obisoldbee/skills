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
  "attempted_routes": [],
  "status": "downloaded|verified_abstract|browser_required|manual_browser_required|paywalled|paywalled_or_no_pdf|access_blocked|unverified_citation|duplicate|needs_manual_review|failed",
  "local_path": "",
  "failure_reason": "",
  "failure_screenshot_path": "",
  "failure_screenshot_error": "",
  "observed_url": "",
  "observed_title": "",
  "pubmed_full_text_checked": false,
  "pubmed_full_text_links": [],
  "pmcid_followup_required": false,
  "file_size_bytes": 0,
  "sha256": "",
  "validated": false
}
```

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

The coordinator may merge shard manifests only after each shard passes disk-state validation.
