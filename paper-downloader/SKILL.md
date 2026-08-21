---
name: paper-downloader
description: Download and verify academic PDFs and references from DOI, PMID, PMCID, publisher URLs, inventories, or explicitly captured Shoulong article pages. Use when the user asks for real paper/PDF acquisition, batch download recovery, download manifests, or Shoulong article-page capture followed by downloading only explicitly cited papers, with lawful access and network/write permission.
---

# Paper Downloader

## Purpose

Perform real paper acquisition after the user authorizes the named sources, network use, browser route, and output root. This Skill is not merely a retrieval plan: it runs the bundled downloaders when their prerequisites are present, validates every PDF, reconciles disk state, and records exact outcomes. It does not judge medical claims, treat a download as Akashic adoption, or bypass access controls.

## Materials

Materials: Use only the frozen inventory, explicit identifiers or Shoulong URL list, authorization statement, output root, and runtime facts supplied for the current run.

Require one bounded input set:

- DOI, PMID, PMCID, explicit article/PDF URLs, or a Markdown/CSV inventory;
- optional public Shoulong (`chinalowcarb.com`) URL list for article-page capture;
- lawful access statement and exact network/browser authorization;
- one writable output root: a new Akashic `12-agent-submissions/YYYY/MM/DD/<package_id>/` or an approved local inventory;
- current browser/runtime capabilities and, if already available, an authorized browser session without revealing its credentials.

Stop on title-only similarity, wildcard/search-result URLs, missing output scope, or unclear access authority. Never infer a DOI from a similar title.

Read these files before execution:

- [download-rules.md](references/download-rules.md) for attempt and surrender rules;
- [package-contract.md](references/package-contract.md) for Akashic package output;
- [ego-browser-route.md](references/ego-browser-route.md) for the preferred interactive browser route and shared-egress serialization;
- [browser-route-playbook.md](references/browser-route-playbook.md) for browser batches and runtime failures;
- [shoulong-page-capture.md](references/shoulong-page-capture.md) only for the Shoulong branch;
- [provenance.md](references/provenance.md) for source/version lineage.

## Constraints

Constraints: These rules protect lawful access, user credentials, package boundaries, and evidence integrity.

- Try legal fallbacks—local files, PMC/Europe PMC, open publisher routes, PubMed full-text links, DOI landing pages, visible PDF actions, and user-authorized browser sessions—to increase success.
- Do not bypass paywalls, CAPTCHA, DRM, login walls, robots blocks, rate limits, or other access controls. Never use shadow libraries, leaked credentials, pasted cookies, or disabled TLS verification.
- When a human verification or institutional-login page appears, preserve the receipt and ask the user to complete it; do not automate the challenge.
- Treat outbound HTTP, browser, and download activity through one public IP as the shared mutable resource `shared-egress-ip:paper-download`. Permit one active network lane by default. Other workers may do only offline inventory, hash, PDF, or report validation until the Controller transfers the token.
- Prefer the separately registered `$ego-browser` for interactive browser follow-up. Use another browser runtime only when Ego is unavailable and the user did not explicitly require it; record the fallback trigger before switching.
- Do not store browser profiles, cookies, tokens, passwords, or session databases in the package. Runtime browser data belongs under a temporary directory.
- Do not add PDFs to Git or write outside the declared output root. In Akashic mode, do not write `03-metadata`, `04-extracts`, `05-wiki`, `10-events`, `11-reports`, or `99-system`.
- A raw HTTP 403/HTML response is `browser_required`, not final proof that a paper is unavailable. Conversely, browser startup or navigation is not download success.
- For the Shoulong branch, capture only public article-page text/metadata and explicit citation identifiers. Do not invoke image understanding/OCR, inspect images for citations, or create paper tasks from images.

## Tools

Resolve `<skill-root>` from this `SKILL.md` real path. Do not assume a caller cwd or a historical `00-agent-skills` path.

Every tool contract below states its purpose, when to use or not use it, parameters or input shape, return/output shape, failure handling, retry boundary, and stop rule. Do not install a missing runtime dependency without separate authority.

### Inventory builder

- Tool: `scripts/build_inventory_download_manifest.py`
- Use for: converting a broad Markdown source inventory into deterministic downloader input.
- Do not use for: arbitrary title inference or silently shrinking a broader inventory.
- Failure: stop on invalid/missing input; retry limit 0.

### Dependency-light first pass

- Tool: `scripts/manifest_pdf_downloader.py`
- Use for: local-file verification, NCBI OA package, Europe PMC render, PMC PDF, DOI landing, and provided PDF URL attempts.
- Return: per-row manifest plus status output.
- Failure: queue plausible browser-resolvable rows as `browser_required` or `paywalled_or_no_pdf`; do not finalize them early.

### Browser follow-up

- Primary tool: separately registered `$ego-browser`, using one named task space for the active download lane.
- Preparation tools: `scripts/build_browser_followup_inputs.py` and `scripts/extract_doi_papers.py`.
- Fallback tools: `scripts/doi_downloader.py`, `scripts/pmc_downloader.py`, and `scripts/with_playwright_python.sh` only when Ego is unavailable and the user did not mandate it.
- Use for: publisher/PMC rows that remain unresolved after the first pass, with explicit browser/network authorization and the shared-egress token.
- Return: observed URL/title and controls, route outcome, blocker evidence, and any stable PDF URL handed back to the canonical downloader; `downloaded` still requires disk validation.
- Failure: hand off the Ego task space on CAPTCHA/login/human checks and mark `manual_browser_required`. If Ego is unavailable, record the exact failure before an allowed fallback. If fallback Playwright is missing, record `blocked_runtime_missing_python_playwright`; do not mark paper rows failed.
- Retry: obey the bounded route and smoke-batch rules in `download-rules.md`; never loop the same blocker across the whole inventory.
- Stop: release the network token before another lane starts; do not run browser or download requests concurrently through the same public IP.

### Reconciliation and reports

- Tools: `scripts/rebuild_manifest.py` and `scripts/summarize_download_manifest.py`.
- Use for: interrupted processes, disk/manifest readback, coverage, and failure reports.
- Failure: a manifest claim without a matching validated disk file is invalid and must be repaired before reporting.

### Shoulong page capture

- Tool: separately registered top-level `$web-bookmark-intelligence` with `profile=shoulong` and its WorkBuddy wrapper.
- Use for: a serial, resumable list of public Shoulong article URLs before extracting explicit text citations.
- Do not use for: image OCR, media interpretation, screenshot evidence mining, or discovering papers from page images.
- Failure: preserve case-local capture receipts; a failed page does not invalidate other completed pages.

## Workflow

Task: Download and verify every in-scope paper that has a lawful route, then report the complete frozen-inventory coverage without concealing unresolved rows.

1. Freeze the input inventory, authorization, output root, and larger-source coverage denominator.
2. If the request includes Shoulong URLs, run the Shoulong page-capture branch first. Accept only article text/metadata that passes its DOM/body gate; retain capture status and source URL. Ignore its image/media branch for this Skill.
3. Extract only explicit DOI/PMID/PMCID/publisher links from supplied inventories or captured article text. Preserve the source page reference for every extracted identifier.
4. Build the complete downloader input before selecting any hand-picked subset.
5. Acquire the shared-egress token, run the dependency-light first pass with one network worker, and validate any local/OA PDF immediately. Parallel workers may only perform offline work.
6. Build DOI/publisher follow-up batches and PMCID follow-up queues. Check PubMed full-text links whenever PMID exists and no PDF has been found.
7. Run interactive browser follow-up through `$ego-browser` with one named task space, pacing, and bounded smoke batches. Keep user-assisted verification points open for the user; never solve them automatically. Use Playwright only under the declared fallback rule.
8. After interruption or browser work, rebuild the manifest from disk before continuing.
9. Release the shared-egress token, generate coverage and failure reports from the final manifest, then independently read back files, PDF headers, sizes, hashes, and counts.

Example command shapes:

```bash
python3 <skill-root>/scripts/build_inventory_download_manifest.py \
  --input <inventory.md> --output <output-root>/source-collection/download-input.json

python3 <skill-root>/scripts/manifest_pdf_downloader.py \
  --input <output-root>/source-collection/download-input.json \
  --paper-dir <output-root>/papers \
  --manifest-out <output-root>/source-collection/download-manifest.json \
  --status-out <output-root>/source-collection/download-status.md \
  --local-root <approved-readable-root> --workers 1

python3 <skill-root>/scripts/summarize_download_manifest.py \
  --manifest <output-root>/source-collection/download-manifest.json \
  --coverage-out <output-root>/source-collection/download-coverage.md \
  --failed-out <output-root>/source-collection/failed-downloads.md \
  --inventory <inventory.md>
```

Boundary examples:

- Example 1: an explicit PMCID with an open PMC route enters the downloader and must end with a validated PDF or an observed route blocker.
- Example 2: a DOI page returns HTML to the first pass but has a plausible publisher route; label it `browser_required` and run the browser follow-up rather than declaring failure.
- Example 3: a Shoulong article body contains an explicit DOI in text; preserve the page-to-DOI reference and download it through the normal paper route.
- Example 4: a Shoulong page shows a paper cover only in an image and no text identifier; record `no_explicit_text_citation` and do not OCR the image.
- Example 5: a title resembles a known paper but has no stable identifier or landing page; classify it `unverified_citation`, not a failed download.
- Example 6: three independent shards share one public egress IP; keep all three task records, but grant network/browser authority to only one shard at a time while the others remain offline-only.

## Output format

Output format: Persist the manifest and reports below, then give a concise Chinese summary unless the user requests another language.

For each row, record the stable identifier, input/source page, every attempted route, status, exact failure reason, observed browser URL/title, failure screenshot or screenshot error when applicable, local PDF path, size, SHA-256, and validation result. Use these queue/final distinctions honestly: `browser_required`, `manual_browser_required`, `downloaded`, `verified_abstract`, `paywalled`, `access_blocked`, `unverified_citation`, `duplicate`, `needs_manual_review`, or `failed`.

Produce `download-manifest.json`, `download-status.md`, `download-coverage.md`, and `failed-downloads.md`; in Shoulong mode also retain the page-capture batch state and source-page-to-identifier mapping. Respond in the user's language; default to Chinese.

## Success criteria

Success criteria: Close every gate below; partial acquisition must be labeled partial.

- Every downloaded file exists inside the output root, starts with `%PDF`, is larger than 5 KB unless explicitly justified, and has a recorded SHA-256.
- Manifest counts exactly match disk readback; every non-download row has a specific reason and every browser-attempted blocker has observable evidence or a recorded screenshot error.
- The full frozen inventory denominator appears in coverage; a successful subset is not mislabeled as complete acquisition.
- All applicable legal fallback routes were either attempted or explicitly marked unavailable; repeated same-blocker batches stop according to the bounded rule.
- Shoulong page capture, when used, remains text-only for this workflow and produces no image-derived paper tasks.
- No credential, browser profile, unapproved path, Git addition, formal Akashic write, or access-control bypass occurred.
