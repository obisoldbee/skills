---
name: paper-downloader
description: Download and verify academic PDFs and references from DOI, PMID, PMCID, publisher URLs, inventories, or explicitly captured Shoulong article pages. Use when the user asks for real paper/PDF acquisition, batch download recovery, download manifests, or Shoulong article-page capture followed by downloading only explicitly cited papers, with lawful access and network/write permission.
---

# Paper Downloader

先在真实可调用且满足任务能力的入口中，按用户已有订阅、常用工具和已验证登录态选路；Mcode（MiniMax Code）内置 Browser 也是候选。在 Mcode 内可用原生工具，从 Codex 调用则须已验证的桥接，安装了 mcode CLI 或支持 BYOK 不证明可控制桌面 Browser。已通过产品入口导入 Chrome 数据并核实登录的 Codex 内置浏览器可优先复用；导入不等于持续共享 profile。没有适用偏好时才采用下述平台默认。

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
- Follow `references/ego-browser-route.md`: explicit browser choice first, then caller-supplied subscription/frequent-use and verified session preferences among callable, task-capable routes. Only without an applicable preference use macOS Ego / Windows Tabbit defaults and their verified fallbacks. Record runtime and selection or fallback reason; do not bypass authentication or resend unknown requests.
- Do not store browser profiles, cookies, tokens, passwords, or session databases in the package. Runtime browser data belongs under a temporary directory.
- Do not add PDFs to Git or write outside the declared output root. In Akashic mode, do not write `03-metadata`, `04-extracts`, `05-wiki`, `10-events`, `11-reports`, or `99-system`.
- The declared output root must be neither the Skill package nor any ancestor or
  descendant of it. Every persisted path is an explicit CLI argument or a
  documented child of one, and no output may alias an input.
- A raw HTTP 403/HTML response is `browser_required`, not final proof that a paper is unavailable. Conversely, browser startup or navigation is not download success.
- For the Shoulong branch, capture only public article-page text/metadata and explicit citation identifiers. Do not invoke image understanding/OCR, inspect images for citations, or create paper tasks from images.

## Tools

Resolve `<skill-root>` from this `SKILL.md` real path. Do not assume a caller cwd or a historical `00-agent-skills` path.

Every tool contract below states its purpose, when to use or not use it, parameters or input shape, return/output shape, failure handling, retry boundary, and stop rule. Do not install a missing runtime dependency without separate authority.

### Inventory builder

- Tool: `scripts/build_inventory_download_manifest.py`
- Use for: converting a broad Markdown source inventory into deterministic downloader input.
- Do not use for: arbitrary title inference or silently shrinking a broader inventory.
- Return: one `paper-downloader/download-manifest/v2` envelope containing every
  table data row, the original inventory SHA-256 and row count, ordered canonical
  row ids, source coordinates, dispositions, and duplicate lineage.
- Input format: pass `--format auto|markdown|csv`. `auto` uses the suffix and a
  strict content check; a format conflict or an inventory with zero data rows
  fails instead of producing an empty manifest.
- Failure: stop on invalid/missing input; retry limit 0.

### Dependency-light first pass

- Tool: `scripts/manifest_pdf_downloader.py`
- Use for: local-file verification, NCBI OA package, Europe PMC render, PMC PDF, DOI landing, and provided PDF URL attempts.
- Resume: reread any recorded PDF and matching files already in `--paper-dir`
  before making a request; never redownload or downgrade a verified row.
- Return: per-row manifest plus status output.
- Persistence: require `--output-root`, `--paper-dir`, `--manifest-out`, and
  `--status-out`; never default a write into the package or caller cwd.
- Failure: queue plausible browser-resolvable rows as `browser_required` or `paywalled_or_no_pdf`; do not finalize them early.

### Browser follow-up

- Primary browser: the runtime selected under `references/ego-browser-route.md`, honoring explicit choice and applicable caller preferences before platform defaults; use one owned task space/group for the active download lane.
- Preparation tools: `scripts/build_browser_followup_inputs.py`,
  `scripts/extract_doi_papers.py`, and `scripts/extract_pmcids.py`.
- Fallback tools: `scripts/doi_downloader.py`, `scripts/pmc_downloader.py`, and `scripts/with_playwright_python.sh` only under the platform fallback contract and when the user did not mandate a different runtime. The `.sh` wrapper requires a compatible POSIX shell; do not prescribe it as a native PowerShell command.
- PubMed fallback: `scripts/pubmed_downloader.py` for one explicitly selected,
  unchecked PMID journal row under the same fallback boundary.
- Use for: publisher/PMC rows that remain unresolved after the first pass, with explicit browser/network authorization and the shared-egress token.
- Return: a `paper-downloader/browser-result-journal/v1` attempt bound to the
  canonical row id, identity, inventory SHA, and base manifest hash. Apply it
  with `scripts/apply_browser_result_journal.py`; orphan, wrong-identifier,
  stale-unapplied, globally colliding, or changed replay attempts fail closed.
  An executor or receiver requires the journal base manifest SHA to equal the
  current manifest before it navigates or reads a request body. A failure
  attempt remains in the journal. `downloaded` still requires the common
  disk/identity gate.
- Failure: hand off the selected browser page on CAPTCHA/login/human checks and mark `manual_browser_required`. If the selected browser is unavailable, record the exact failure before an allowed fallback. If fallback Playwright is missing, record `blocked_runtime_missing_python_playwright`; do not mark paper rows failed.
- Retry: obey the bounded route and smoke-batch rules in `download-rules.md`; never loop the same blocker across the whole inventory.
- Stop: release the network token before another lane starts; do not run browser or download requests concurrently through the same public IP.

### Reconciliation and reports

- Tools: `scripts/rebuild_manifest.py` and `scripts/summarize_download_manifest.py`.
- Use for: interrupted processes, disk/manifest readback, coverage, and failure reports.
- Failure: a manifest claim without a matching validated disk file is invalid.
  Missing, extra, tampered, or escaped PDFs fail final reporting. Rebuild writes
  `reconciled_at`, can rediscover a renamed PDF by disk identity while enforcing
  one PDF per row, and never invents `downloaded_at`. Final reporting refuses
  unresolved queue/follow-up/manual-review rows or missing blocker evidence;
  its receipt records relative output paths, exact bytes and hashes for the
  manifest, inventory, disk set and reports, but never hashes itself.

### Shoulong page capture

- Tool: separately registered top-level `$web-bookmark-intelligence` with its current `profile=shoulong` contract, executed by the current Agent through an authorized available runtime. WorkBuddy is an explicitly selected legacy route only.
- Use for: a serial, resumable list of public Shoulong article URLs before extracting explicit text citations.
- Do not use for: image OCR, media interpretation, screenshot evidence mining, or discovering papers from page images.
- Failure: preserve case-local capture receipts; a failed page does not invalidate other completed pages.

## Workflow

Task: Download and verify every in-scope paper that has a lawful route, then report the complete frozen-inventory coverage without concealing unresolved rows.

1. Freeze the input inventory, authorization, output root, and larger-source coverage denominator.
2. If the request includes Shoulong URLs, run the Shoulong page-capture branch first. Accept only article text/metadata that passes its DOM/body gate; retain capture status and source URL. Ignore its image/media branch for this Skill.
3. Extract only explicit DOI/PMID/PMCID/publisher links from supplied inventories or captured article text. Preserve the source page reference for every extracted identifier.
4. Build the complete canonical manifest before selecting any hand-picked
   subset. Preserve every source row, even missing-id/title, duplicate, or
   do-not-cite rows.
5. Acquire the shared-egress token, run the dependency-light first pass with one network worker, and validate any local/OA PDF immediately. Parallel workers may only perform offline work.
6. Build DOI/publisher follow-up batches and PMCID follow-up queues. Check PubMed full-text links whenever PMID exists and no PDF has been found.
7. Run interactive browser follow-up through the platform-selected browser with one owned task
   space/group, pacing, and bounded smoke batches. Record each outcome in the prepared
   row-bound result journal; then apply/reconcile it idempotently. Keep
   user-assisted verification points open for the user; never solve them
   automatically. Use Playwright only under the declared fallback rule.
8. After interruption or browser work, apply the result journal and rebuild the
   manifest from disk before continuing. Preserve unsuccessful attempts.
9. Release the shared-egress token, generate coverage and failure reports from
   the final manifest, then independently read back the frozen inventory SHA and
   row-id set plus every PDF header, exact byte count, hash, path, and disk set.

Example command shapes:

```bash
python3 <skill-root>/scripts/build_inventory_download_manifest.py \
  --input <inventory.md> \
  --format auto \
  --output-root <output-root> \
  --output source-collection/download-input.json

python3 <skill-root>/scripts/manifest_pdf_downloader.py \
  --input <output-root>/source-collection/download-input.json \
  --output-root <output-root> \
  --paper-dir papers \
  --manifest-out source-collection/download-manifest.json \
  --status-out source-collection/download-status.md \
  --local-root <approved-readable-root> --workers 1

python3 <skill-root>/scripts/build_browser_followup_inputs.py \
  --manifest <output-root>/source-collection/download-manifest.json \
  --output-root <output-root> \
  --output-dir source-collection/browser-inputs \
  --journal-out source-collection/browser-result-journal.json

python3 <skill-root>/scripts/apply_browser_result_journal.py \
  --manifest <output-root>/source-collection/download-manifest.json \
  --journal <output-root>/source-collection/browser-result-journal.json \
  --output-root <output-root> \
  --manifest-out source-collection/download-manifest-browser-applied.json \
  --receipt-out source-collection/browser-apply-receipt.json

python3 <skill-root>/scripts/summarize_download_manifest.py \
  --manifest <output-root>/source-collection/download-manifest-browser-applied.json \
  --inventory <inventory.md> \
  --output-root <output-root> \
  --coverage-out source-collection/download-coverage.md \
  --failed-out source-collection/failed-downloads.md \
  --receipt-out source-collection/final-report-receipt.json
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

For each row, record the stable identifier, source coordinate/disposition,
duplicate lineage, input/source page, every attempted route, one exact `status`,
exact failure reason, observed browser URL/title, failure screenshot or error,
and one `pdf` receipt with path, `bytes`, SHA-256, magic and identity-match
evidence derived from the PDF bytes. A primary DOI/PMID/PMCID in the referenced PDF Info
metadata or an exact PDF Title metadata match is required; contradictory titles reject a match; filename,
route URL, response header, and client-supplied strings are claims only and
cannot independently prove identity. Never add `download_status`,
size-kilobyte fields, or route-specific
manifest variants. Use the exact enum declared by
`paper-downloader/download-manifest/v2`; a substring such as `not_downloaded`
never counts as success.

Produce `download-manifest.json`, `download-status.md`, `download-coverage.md`, and `failed-downloads.md`; in Shoulong mode also retain the page-capture batch state and source-page-to-identifier mapping. Respond in the user's language; default to Chinese.

## Success criteria

Success criteria: Close every gate below; partial acquisition must be labeled partial.

- Every downloaded file exists inside the declared output root, is reread from
  disk, starts with `%PDF`, is strictly larger than 5120 bytes, has exact bytes
  and SHA-256, and has a primary identifier in PDF Info metadata or an exact
  PDF Title metadata match, without a contradictory title.
- Manifest counts and PDF set exactly match disk readback; extra, missing,
  tampered, or escaped paths fail. Every non-download row has a specific reason
  and every browser-attempted blocker has observable evidence or a screenshot
  error.
- The full frozen inventory denominator appears in coverage; a successful subset is not mislabeled as complete acquisition.
- All applicable legal fallback routes were either attempted or explicitly marked unavailable; repeated same-blocker batches stop according to the bounded rule.
- Shoulong page capture, when used, remains text-only for this workflow and produces no image-derived paper tasks.
- No credential, browser profile, unapproved path, Git addition, formal Akashic write, or access-control bypass occurred.

## 目标数量与补充资料

按任务约定区分 `collection_role=target` 与 `supplementary`，后者须填写
`collection_role_reason`（如 counterevidence、critique、background）。本任务约定的反方论文
可以收录、引用、批判并充实资料库，但作为补充材料，不占目标文献数量。分类按任务范围，
不能为了凑数改标签，也不能因观点相反而丢弃证据。缺省历史行仍为 target。

在冻结 inventory 前记录分类，用 `build_inventory_download_manifest.py --target-count 50`
锁定目标数量；报告分别列 `target_downloaded`、`target_remaining`、`supplementary_downloaded`。
49 篇目标 + 1 篇补充 = 目标 49/50、补充 1；50 篇目标 + 1 篇补充 = 目标 50/50、补充 1。
没有显式数量时按合格且去重后的目标行数计算。所有 downloaded 仍须通过相同身份与文件核验。

论文身份与收录用途独立：参考文献中的目标 DOI 只是候选线索；主体是另一篇论文时，
按那篇论文的真实标题/标识建立补充条目，不能覆盖原目标行或抵扣缺口。
PDF Info 元数据中的主体标识或精确标题可供 helper 核验；矛盾标题或只有任意字节 DOI
保留为 needs_manual_review，不删除候选，也不声称已确认目标论文。此 helper 不替代完整 PDF
结构解析或人工主体审阅。冻结后发现补充材料时，在独立输出根建立补充 inventory/run，
或经有记录的版本化重新规划保留旧 inventory 与回执；不得静默追加、改写冻结行或污染磁盘对账。
