# Browser Route Playbook

Load this file for PMC or DOI batches beyond a small manual spot check.

## Why This Exists

Other local tools can download papers because they use a browser-centered route,
publisher-specific patterns, pacing, and manifest recovery. A QA run that uses
raw HTTP, a temporary package-local script, or a naive direct PDF loop can record
many access-blocked rows even when the formal downloader has a better route.

## Required Strategy

All network activity in this playbook is serialized through
`shared-egress-ip:paper-download`. Separate shards, processes, task spaces, or
write directories do not permit concurrent requests from the same public IP.

Use the separately registered `$ego-browser` as the primary interactive route.
Read [ego-browser-route.md](ego-browser-route.md) before browser work. The local
Playwright scripts remain bounded fallbacks only when Ego is unavailable and
the user did not explicitly require it.

Use the formal scripts in `../scripts/` for inventory preparation, first-pass
acquisition, persistence, reconciliation, and an allowed browser fallback:

- `extract_pmcids.py`: extract PMCID rows from Markdown or inventories.
- `extract_doi_papers.py`: extract DOI rows and group them into publisher waves.
- `pmc_downloader.py`: slow browser route for small PMC batches.
- `doi_downloader.py`: persistent browser DOI/publisher route.
- `manifest_pdf_downloader.py`: first-line repair route for manifest rows; it
  performs local PMCID/PMID/DOI precheck, NCBI OA package lookup, Europe PMC
  PDF render fallback, PMC PDF URL attempts, and DOI/provided PDF URL attempts
  through system `curl` so Python certificate or Playwright drift does not block
  the whole run.
- `build_inventory_download_manifest.py`: converts `paper-source-inventory.md`
  or `source-library-frozen.md` into downloader input so broad QA runs do not
  silently shrink to a tiny hand-picked manifest.
- `summarize_download_manifest.py`: writes `download-coverage.md` and
  `failed-downloads.md` from a manifest, including rows missing failure reasons.
- `rebuild_manifest.py`: reconcile disk state after crash or restart.
- `pdf_receiver.py`: local receiver when the route posts browser-fetched PDFs.

Do not create a package-local downloader unless it is explicitly being proposed
as a new formal tool patch. Do not switch from Ego to Playwright silently.

## Script Selection

Use this order before taking manual browser actions:

| Situation | Script | Purpose |
|---|---|---|
| Broad package inventory exists | `build_inventory_download_manifest.py` | Convert `paper-source-inventory.md` or `source-library-frozen.md` into manifest rows. |
| Need local/OA/public-route first pass | `manifest_pdf_downloader.py` | Local precheck, Europe PMC render, NCBI OA package, PMC PDF, DOI/provided PDF URL. |
| DOI rows remain unresolved | `extract_doi_papers.py` | Classify DOI rows by publisher and write batch JSON files. |
| Publisher or PubMed/PMC page needs interaction | `$ego-browser` | Primary real-page route; observe, act, and verify in one named task space. |
| Ego unavailable and fallback allowed; publisher page has PDF/download menu | `doi_downloader.py` | Fallback browser route for DOI landing pages and visible download actions. |
| Ego unavailable and fallback allowed; PMCID rows remain unresolved | `pmc_downloader.py` | Fallback slow browser route with pacing and manual human-check wait. |
| Browser/process interrupted | `rebuild_manifest.py` | Reconcile files already on disk back into the manifest. |
| Need final reports | `summarize_download_manifest.py` | Write `download-coverage.md` and `failed-downloads.md`. |

For AHA/JAHA/Circulation rows, DOI prefix `10.1161` is classified as `JAHA_AHA` by `extract_doi_papers.py`. If the page shows a `Download` menu with a `PDF` item, that is a browser-follow-up target for `doi_downloader.py`; do not leave it as `access_blocked` because raw HTTP got 403.

Before an allowed `doi_downloader.py` or `pmc_downloader.py` fallback, record why Ego was unavailable and confirm the user did not mandate Ego. Then use `with_playwright_python.sh` so the script uses the Python interpreter that owns the local `playwright` CLI. If the wrapper fails, the route is blocked by the local runtime, not by the paper source. Record `blocked_runtime_missing_python_playwright` and do not summarize the row as a paper access failure.

## PubMed Full Text Link Route

Treat PubMed as a routing hub, not just a metadata page. The right-side `Full text links` box can expose a publisher free-full-text route, a PMC author manuscript route, or both. A first pass that reaches only DOI, Europe PMC, or publisher command-line routes is incomplete when the row still has a PMID or PMCID.

Required handling:

- If PMCID exists, run or queue the PMCID browser route even when DOI or publisher first pass says `paywalled_or_no_pdf`.
- If PMID exists and no PDF was found, inspect PubMed full-text links or use a manifest field proving that this check was already done.
- If PubMed exposes a PMC link, prefer `pmc_downloader.py`; if it exposes only a publisher full-text link, route through `doi_downloader.py` or a publisher-specific browser route.
- Recompute coverage after PubMed/PMCID follow-up. Do not reuse a stale failure list from before the follow-up pass.

Repair-run examples that must not regress:

- PMID `32497744`, PMCID `PMC7977482`, DOI `10.1016/j.diabres.2020.108233`: first pass can look like `paywalled_or_no_pdf`, but PMC provides a downloadable PDF.
- PMID `34015477`, PMCID `PMC8324525`, DOI `10.1016/j.jacc.2021.05.004`: PubMed exposes both publisher and PMC routes; the PMC route provides a downloadable PDF.

When a row changes from `paywalled_or_no_pdf` to a downloaded PDF through this route, update the manifest row and the package coverage report in the same pass.

## Large PMC Batches

For PMC batches larger than 20 papers, a normal automation browser may hit 403
or browser-check pages after 10-20 rows. Prefer the integrated browser/full-batch
route with pacing:

- random delay between rows;
- regular cool-down breaks;
- stop after repeated same-blocker failures;
- manifest save after small batches;
- disk-state reconciliation before reporting.

PMC "Preparing to download" or browser-check pages are not proof that no PDF is
available. They are route blockers. Use the browser route first, then record the
exact blocker if it still fails.

When `pmc.ncbi.nlm.nih.gov` shows browser-check or reCAPTCHA pages, try the
same PMCID through `manifest_pdf_downloader.py` before declaring the row failed:
Europe PMC render can legally provide the article PDF for rows where the PMC
page route is blocked.

## PMC Proof-Of-Work And Access Challenges

Some PMC pages may return a computational proof-of-work or browser challenge
instead of a PDF. Treat this as an access-control challenge, not as proof that
the article has no PDF.

Formal downloader behavior:

- keep the row as `manual_browser_required`, `browser_required`, or
  `access_control_challenge` until a normal browser route, Europe PMC route, or
  user-assisted route confirms the outcome;
- do not add package-local challenge solvers to the formal downloader by
  default;
- do not solve captchas, login walls, paywalls, robots blocks, or DRM;
- if a solver is proposed for public PMC OA PDFs, classify it as a
  `tool_candidate` that requires explicit safety/boundary review before
  formal absorption.

The allowed lesson from a PoW repair run is operational: PMC rows can still be
downloadable after command-line failures, so they need proper browser/PMC
follow-up and exact blocker reporting. The solver itself is not accepted as a
default Akashic downloader route without a separate review.

## DOI / Publisher Waves

Use `extract_doi_papers.py` to split DOI rows into waves. Start with high-success
or open-access-friendly publishers, then decide whether the remaining waves are
worth spending time on.

Known high-yield patterns from prior local runs include Cambridge, NEJM, Science
/ AAAS, JBC, PNAS, BMC, PLOS, MDPI, Frontiers, Dove, JAHA, Theranostics,
Oncotarget, and WJG. Known low-yield or redirect-heavy publishers may still be
checked, but do not let them consume a broad run after the smoke batch proves the
same access blocker.

If a normal browser displays a cookie banner, accept or reject it as needed for navigation. If a captcha or human verification appears, stop the automated step, leave the browser on that page, and ask the user to complete it. Do not record captcha as a final download failure until the user declines or the manual wait times out.

Browser profiles are runtime state. Do not write Chrome profile folders, Cookies, Login Data, History, or other browser databases into `12-agent-submissions`. Use a temp directory such as `${TMPDIR:-/tmp}/akashic-paperdownloader/<package_id>/...` and keep only PDFs, manifests, status reports, and blocker notes in the package.

## Reporting Standard

A good download report must say:

- which formal script or browser route was used;
- source inventory rows, downloader rows, and whether a smaller core batch was
  intentionally used;
- input rows, downloaded PDFs, verified abstracts, local-existing rows, and
  access-blocked rows;
- exact blocker pattern;
- whether a same-blocker batch stop was triggered;
- whether manifest counts match files on disk.
