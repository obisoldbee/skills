# Ego Browser Route

Load this file when a paper remains unresolved after the dependency-light pass
and interactive browser work is authorized.

## Route Contract

- Primary tool: the separately registered `$ego-browser` Skill and its
  `ego-browser nodejs` runtime.
- Use when: a DOI, PubMed/PMC, or publisher page needs real-page observation,
  a visible PDF action, or an authorized user session.
- Do not use when: the lane does not hold
  `shared-egress-ip:paper-download`, the identifier is unverified, or browser
  authority is absent.
- Parameters: one stable DOI/PMID/PMCID or verified URL, one named task space
  for the active lane, and the declared package output root.
- Return: observed URL/title, page controls or stable PDF URL, route outcome,
  and blocker evidence. Browser navigation alone never returns `downloaded`.
- Failure: on CAPTCHA, login, or human verification, call
  `handOffTaskSpace`, preserve the page, set `manual_browser_required`, and wait
  for explicit user confirmation. Never bypass the challenge or call
  `takeOverTaskSpace` without that confirmation.
- Stop: after the lane is complete, call `completeTaskSpace` in its own final
  command with `keep: false`, unless the page must remain open for the user's
  action. Stop all requests and write a checkpoint before transferring the
  shared-egress token.

## Execution Order

1. Acquire the shared-egress token from the Controller. Confirm no other lane
   has an active HTTP, browser, or download process.
2. Reuse one named Ego task space for the lane. Open the exact verified route,
   inspect `snapshotText()` and `pageInfo()`, and re-observe after each action.
3. Prefer PMCID, then DOI, then PubMed full-text links, then the publisher's
   visible PDF action. Pace requests and use the bounded smoke-batch rule.
4. If a stable PDF URL is exposed, pass it to the canonical downloader or an
   existing package tool for persistence. Do not invent a temporary downloader.
5. Validate the resulting file from disk: `%PDF`, more than 5120 bytes,
   SHA-256, and DOI/title identity. Only then set `downloaded`.
6. Reconcile the manifest, close or hand off the task space as required, write
   the lane checkpoint, and release the shared-egress token.

## Fallback Boundary

Playwright browser scripts are permitted only when Ego is unavailable and the
user did not explicitly require Ego. Record the exact Ego runtime failure and
fallback decision before starting Playwright. A CAPTCHA or user takeover is not
an availability failure and must not trigger a different browser route.
