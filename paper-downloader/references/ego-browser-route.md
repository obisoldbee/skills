# Interactive Browser Route (macOS and Windows)

Load this file when a paper remains unresolved after the dependency-light pass
and interactive browser work is authorized.

## Route Contract

Honor an explicit browser choice and reuse an active, logged-in page for the same task. For a new browser session, choose the first available route:

1. `ego-browser` / ego lite.
2. Tabbit.
3. The system default browser or a commonly used browser recorded by the current harness.
4. The harness's built-in browser.

Read the selected browser's current Skill/API. For Ego, run `ego-browser skill` and read the complete guide before browser actions. Confirm page access and the required download capability. If a route is absent or its documented connection recovery fails, use the next available route. Preserve the original request and download journal during a switch.

When Tabbit is the selected browser and the host is Windows, use its documented launcher `$env:LOCALAPPDATA\Tabbit\LocalAgent\bin\tabbit-cli.exe`, diagnose connection, and retain the returned task/group/tab IDs. Send multiline Chinese programs through a UTF-8 no-BOM temporary file and CMD stdin redirection.

- Use when: a DOI, PubMed/PMC, or publisher page needs real-page observation,
  a visible PDF action, or an authorized user session.
- Do not use when: the lane does not hold
  `shared-egress-ip:paper-download`, the identifier is unverified, or browser
  authority is absent.
- Parameters: one stable DOI/PMID/PMCID or verified URL, one named task space
  for the active lane, and the declared package output root.
- Return: observed URL/title, page controls or stable PDF URL, route outcome,
  and blocker evidence. Set `downloaded` after the file passes the disk checks below.
- Failure: on CAPTCHA, login, or human verification, use the selected runtime’s documented human handoff, preserve the page, set `manual_browser_required`, and wait
  for explicit user confirmation. Never bypass the challenge or reclaim user control without that confirmation.
- Stop: after the lane is complete, close only self-created pages/space using the current runtime API, unless the page must remain open for the user's
  action. Stop all requests and write a checkpoint before transferring the
  shared-egress token.

## Execution Order

1. Acquire the shared-egress token from the Controller. Confirm no other lane
   has an active HTTP, browser, or download process.
2. Reuse the lane’s owned space/group by real ID. Open the exact verified route,
   inspect current DOM/semantic state and URL, and re-observe after each action.
3. Prefer PMCID, then DOI, then PubMed full-text links, then the publisher's
   visible PDF action. Pace requests and use the bounded smoke-batch rule.
4. If a stable PDF URL is exposed, pass it to the canonical downloader or an
   existing package tool for persistence. Do not invent a temporary downloader.
5. Validate the resulting file from disk: `%PDF`, more than 5120 bytes,
   SHA-256, and a primary identifier in PDF Info metadata or exact PDF Title
   metadata without a contradictory title. Then set `downloaded`.
6. Append a row-id/identifier-bound result-journal attempt, apply it
   idempotently, reconcile the canonical manifest, close or hand off the task
   space as required, write
   the lane checkpoint, and release the shared-egress token.

Before any fallback executor navigates, and before the loopback receiver reads
a request body, require the journal base manifest SHA to equal the current
manifest, reject attempt-id collisions across all rows, and reserve a
non-existing target path. Recheck manifest, journal, and target CAS immediately
before writing the PDF.

## Fallback Boundary

Playwright browser scripts are permitted only when the selected platform browser is unavailable and the
user did not explicitly require another runtime. Record the exact runtime failure and
fallback decision before starting Playwright. A CAPTCHA or user takeover is not
an availability failure and must not trigger a different browser route.

## Download and cleanup differences

Read the runtime’s supported download API. Tabbit capabilityVersion 18 does not support generic Playwright download events/saveAs: use a documented page.fetch file download for an observed URL or verify a native download’s exact output file. Do not invent a URL or export cookies to a downloader. Preserve manifest/journal CAS and no-clobber checks before persistence. Validate publisher access and the actual PDF during the run.

Ego: use current task.finish close contract. Tabbit: after confirming every group tab is self-created and owned, use the documented `finish --task <name> --discard`, verify closedTabIds and the group inventory. With mixed user tabs, close only own pages then finish; default finish retains tabs. Chrome/IAB: close only the lane’s newly created tabs with the exposed API. Existing user tabs stay open. Save URL and checkpoint before cleanup; retain only for pending work or required human action, and report cleanup failure separately from PDF results.
