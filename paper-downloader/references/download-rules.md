# Download Rules

Load this file before each download run.

## Shared-Egress Serialization

Treat all outbound HTTP, DOI, PubMed/PMC, publisher, browser, and PDF-download
requests through one public IP as the mutable resource
`shared-egress-ip:paper-download`. One Controller grants that token to one lane
at a time. Parallel workers may prepare inventories or validate existing files
offline, but must not start network or browser work until they hold the token.

Use `--workers 1` for the dependency-light downloader by default. A larger
network worker count requires explicit proof of separate authorized egress
resources; separate output directories alone do not make network lanes
independent. Release the token only after active requests have stopped and the
lane has written a checkpoint or completion receipt.

## Real Attempt Standard

A real attempt means a browser session navigates to an article page, DOI route, PubMed/PMC route, or publisher PDF route and observes the actual result.

These do not count as real attempts:

- assuming paywall from DOI prefix or publisher name;
- treating a small PMC "preparing download" page as final failure;
- using raw HTTP failure as the only evidence;
- treating `curl` 403, HTML, or timeout as `access_blocked` before a browser route has been tried;
- treating a PubMed page as exhausted after reading metadata while right-side full-text links or PMCID are still available;
- copying a search-result URL or wildcard URL into the manifest;
- recording a title-only item as a failed download.

## Surrender Conditions

Record `paywalled`, `access_blocked`, or `failed` only when:

1. a real browser route was attempted;
2. the browser showed a login wall, paywall redirect, captcha, 403, non-PDF response, or equivalent blocker;
3. PubMed full-text links were checked when PMID exists and no PDF has been found;
4. a PMC fallback was tried when PMCID exists;
5. `failure_reason` describes the observed blocker.

Use `unverified_citation` when title, URL, DOI, PMID, PMCID, or article page cannot be verified. Do not call it a download failure.

Use `browser_required` when a command-line route reaches a DOI/publisher/PMC URL but returns 403, HTML, a browser-check page, timeout, or another result that can plausibly be resolved by a normal browser session. `browser_required` is a queue state, not a final failure.

Use `paywalled_or_no_pdf` from a dependency-light first pass as a queue state when PMID or PMCID exists. It becomes a final status only after PubMed full-text links and the PMCID route are checked or shown unavailable.

Use `manual_browser_required` when the browser route reaches a captcha, human verification, institutional-login prompt, or other user-intervention point. Open or leave the browser at the blocker, ask the user to handle it, and record the exact page state.

## Route Order

Try routes in this order when available:

1. PMCID route.
2. DOI resolver route.
3. PubMed full-text links.
4. Publisher article landing page PDF button or known publisher pattern.
5. Manual-review queue.

If PMCID exists, the PMCID route outranks the DOI/publisher route for follow-up because PMC often exposes author manuscripts even when the publisher page looks paywalled. If PMID exists but PMCID is missing from the input row, PubMed full-text links are a required discovery step before the row is surrendered.

When the publisher page visibly exposes `Download -> PDF`, `PDF`, or a download menu, use the registered `$ego-browser` as the primary interactive route:

1. `extract_doi_papers.py` to classify DOI rows by publisher without network access.
2. `$ego-browser` to inspect the real page, operate visible controls, and capture the observed URL/title or stable PDF URL.
3. The canonical downloader to persist and validate the resulting PDF under the declared output root.
4. `doi_downloader.py` or `pmc_downloader.py` only as a recorded fallback when Ego is unavailable and the user did not explicitly require it.

Do not substitute another browser merely because it is convenient. If the user explicitly selected Ego, an Ego failure is a blocker until the user changes the route.

For large PMC batches, prefer integrated browser batch mode with pacing. For DOI-heavy batches, prefer `scripts/doi_downloader.py`.

## Batch Stop Rule

For broad batches, do not spend the whole run repeating a known blocked route.

Before attempting more than 20 rows on the same route family, run a bounded
smoke batch of 5-10 representative rows. Stop the route family and mark the
remaining rows `access_blocked` or `needs_manual_review` when all are true:

- the smoke batch produces 0 validated PDFs;
- at least 80% of failures share the same observed blocker, such as PMC
  browser-check, captcha, login wall, 403, 502, or repeated non-PDF HTML;
- no alternate legal route is immediately visible for those rows.

When this happens, write `batch_stopped_same_blocker` in `failure_reason`, keep
the representative attempts in the manifest, and return control to the QA team
lead. The team lead should then choose a narrower manual-access repair set,
use local sources, or rerun through a different legal route. Do not present the
blocked batch as successful source acquisition.

## High-Success Routes To Try

Do not prematurely skip these:

- PMC PDF route after real browser wait.
- Cambridge `10.1017`.
- NEJM `10.1056`.
- Science or AAAS `10.1126`.
- JBC `10.1074`.
- PNAS `10.1073`.
- BMC, PLOS, MDPI, Frontiers, Dove, JAHA, Theranostics, Oncotarget, WJG.
- Small publishers with a visible PDF button.

For Oxford, JAMA, Endocrine Society, Thieme, RSC, AACR, Elsevier, Wiley, Nature, Springer, LWW, Sage, Taylor and Francis, and Karger, still attempt valid routes unless the task explicitly says to only use PMC/OA routes.

## File Validation

Downloaded PDFs must:

- start with `%PDF`;
- be larger than 5 KB unless an explicit exception is recorded;
- have a stable filename;
- appear in the manifest;
- be counted in the final disk-state check.

HTML-only or abstract-only captures must be labeled as such and cannot be treated as full text.

## Privacy And Access

Never print, store, summarize, or ask the user to paste cookies, tokens, passwords, session headers, or institutional credentials.

It is acceptable to record that an authenticated browser session was attempted and whether it succeeded.
