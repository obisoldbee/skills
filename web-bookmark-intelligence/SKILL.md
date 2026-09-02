---
name: web-bookmark-intelligence
description: Read, summarize, evaluate, or fact-check public webpages and WeChat Official Account articles from one or more URLs. Use whenever the user supplies a webpage or WeChat/微信公众号 link, including a bare URL with no stated task; acknowledge this Skill and ask one concise question when the intended result is unclear. Also use for supplied webpage screenshots or long images. Default to response-only; create files, evidence cases, batches, or action cards only when explicitly requested.
---

# Web Bookmark Intelligence

Background:

Read and evaluate public web content without binding the task to a particular Agent, browser, or capture product. A bare Skill invocation does not authorize file creation, archiving, adoption, installation, or publication.

Materials:

Use only the webpage URL, screenshot, long image, PDF, pasted text, or batch list supplied by the user, plus body or media evidence obtained through an authorized available route. Do not load unrelated project history or create a knowledge package for an ordinary review.

Parameters:

- `source`: one or more user-supplied URLs or local inputs.
- `requested_result`: read, summarize, evaluate, compare, fact-check, save, archive, or batch-process.
- `output_root`: required only when the user asks for saved files and no project rule already defines the destination.

Path boundary: this general Skill has no fixed `input/` or `output/` directories. In read-only review, every user-supplied input is read-only and no filesystem path is writable. In durable mode, only the authorized `output_root` is writable.

Do not use this Skill for general web searching without a supplied source, authenticated private content without explicit access authority, or installing/adopting a project discovered on a webpage.

Task:

Choose the mode from the result the user requested:

| User request | Mode |
| --- | --- |
| Read, summarize, evaluate, explain, compare, or fact-check a page | Read-only review |
| Save, archive, audit, batch-process, or resume a set of pages | Durable evidence |
| Install, adopt, publish, deploy, or write to a formal knowledge layer | Stop for explicit authorization |

When handling a supplied webpage or WeChat article, say in the first short progress update that `web-bookmark-intelligence` is handling the link. If the user sends only a URL and their intended result is unclear, ask one concise question. Explicitly naming this Skill alone does not switch a read-only request into durable mode.

## Select The Retrieval Route Before Access

Choose the primary route before opening or fetching the page.

1. If the user explicitly selected a browser or retrieval tool, that choice overrides the default priority. Use that route and obey its own fallback and stop rules.
2. Otherwise inspect the Skills and tools listed in the current session for a purpose-built page-extraction or browser-control route. Read the applicable Skill completely and follow its stated selection priority. For example, when `ego-browser` is listed, its contract prefers it over built-in browser automation and web fetch for page extraction, so use it first. This is conditional capability discovery, not a required edition or dependency of `web-bookmark-intelligence`.
3. Only when no applicable purpose-built route is available, use the current runtime's authorized generic web or browser capability.
4. A static fetch that returns only metadata is a probe, not the one allowed rendered-browser attempt. It must not prevent use of the selected browser route.
5. If the selected route reports an ordinary bootstrap or sandbox-only availability failure, follow that route's documented recovery once. Then use at most one materially different authorized route if its contract permits fallback. A listed Skill or healthy link does not prove execution availability; its executable may still be unavailable. Do not switch tools to evade an explicit safety-policy, access-control, CAPTCHA, login, or user-control stop.
6. If a tool rejects the URL before navigation, report that the selected automation route was blocked. Do not claim that the webpage itself is inaccessible unless a request actually reached the page and established that fact.

Examples:

| Situation | Required action |
| --- | --- |
| WeChat link plus “如何评价”, and `ego-browser` is listed | Use `ego-browser` first, read the substantive body, return a response only |
| WeChat link plus “如何评价”, with no purpose-built route listed | Use the runtime's authorized generic browser, return a response only |
| A chosen browser rejects the URL by an explicit safety policy | Stop that browser route; report the route-level blocker without calling the page unavailable |
| WeChat link plus “保存到本地” | Enter durable mode; do not confuse the archive request with ordinary review |

## Read-Only Review

Use this mode by default.

1. Retrieve the supplied public page with the primary route selected above. Runtime-neutral means the Skill does not require one brand everywhere; it does not mean ignoring a higher-priority route that is actually listed and available in the current session.
2. Prefer substantive body text. Render the page when a static response is incomplete, and keep title, metadata, body text, and image evidence distinct.
3. Inspect images or canvas content only when they carry claims needed for the requested review and the current runtime can safely inspect them.
4. If the selected route and its permitted recovery cannot obtain usable body or media evidence, apply the fallback and hard-stop rules above. When no permitted route remains, ask for pasted text, a long screenshot, PDF, or another authorized input.
5. Reply in the user's language with the requested summary or evaluation, the main claims, evidence quality, and important uncertainties.

Read-only review is response-only. Do not create a case, reserve a package, write files, query unrelated context, refresh GitHub records, or build action cards unless the user asked for those effects.

An unavailable browser or legacy adapter means only that route is unavailable. Do not describe the Skill itself as unusable when another authorized route or user-supplied content can still satisfy the request.

## Durable Evidence

Enter this mode only when the user explicitly asks to save, archive, audit, batch-process, or resume later.

1. Use a user-provided output root or a project-rule-defined writable root already in scope. If neither exists, ask for the destination before writing.
2. Create one case per source with `scripts/intake_case.py`.
3. Capture the page with the current runtime's authorized browser or retrieval capability, save only the authorized case-local HTML/media, then run `scripts/capture_pipeline.py`.
4. When material claims depend on images, use the available image-understanding route and preserve the body/media distinction described in [media-routing.md](references/media-routing.md).
5. Bind the case with `scripts/assess_capture_evidence.py`. Prepare page-purpose notes or action cards only when the user requested them.
6. For batches, use `scripts/plan_batch.py` to create or resume the case plan. The plan does not select or execute a browser; the current Agent captures each planned case with an authorized available route.

Read [capture-and-quality-gates.md](references/capture-and-quality-gates.md) only for durable capture and quality checks. Read [batch-profiles.md](references/batch-profiles.md) only for a requested batch. Historical adapter receipts and compatibility code remain regression/provenance material; they are not the default route and must not appear in a normal user response unless the user is diagnosing that adapter.

Constraints:

- A title, meta description, cover, browser-open event, route prediction, or exit code is not article-body evidence.
- Keep observed page content, media interpretation, your analysis, and unknowns distinct.
- Never bypass login, CAPTCHA, paywalls, or access controls.
- When package code makes direct network requests, accept only public `http` or `https` destinations, reject embedded credentials and non-public addresses, validate redirects, and keep TLS verification enabled. Runtime-managed browsers rely on their own enforced network boundary.
- Do not send private or restricted content to an external provider without approval for the exact asset and provider.
- Do not silently switch a user-selected browser, suppress a failed attempt, or claim that discovery equals adoption.
- Once a route has produced substantive body evidence, do not let a later weaker probe or failed route downgrade it to “正文不可得”.
- Do not install a missing browser, executor, or compatibility component unless the user explicitly asks for installation.
- Do not mention executor brands, versions, hashes, receipt schemas, or internal status codes in an ordinary review. Surface them only for an explicitly requested diagnostic or durable audit where they materially explain the result.

Output format:

For read-only review, return the observed source/title, concise summary or evaluation, main claims, evidence quality, and uncertainties. State plainly when the review is partial or blocked.

For durable mode, additionally report the output path, completed/partial/blocked/failed counts, and whether saved artifacts were read back and their hashes verified.

Success criteria:

Read-only review succeeds only when substantive body or necessary media evidence was obtained and the answer is grounded in it. No filesystem or formal-layer write may occur.

Durable mode succeeds only when the user authorized persistence, every written path stays inside the authorized root, artifacts are read back with matching hashes, and each source has a terminal or resumable status. A truthful blocker is a valid outcome, but it is not a successful capture.

Final task: obtain the best authorized body or media evidence for the user's supplied source, answer the requested question, and report route-level blockers without turning them into unsupported claims about the page or the Skill.
