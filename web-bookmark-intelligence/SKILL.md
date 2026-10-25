---
name: web-bookmark-intelligence
description: Read, summarize, evaluate, compare, or fact-check supplied webpages, WeChat Official Account articles, and webpage screenshots. Save evidence or process batches when requested. For a bare URL with no clear intent, ask one concise question.
---

# Web Bookmark Intelligence

Read the supplied source and answer the user's question. Ordinary review returns an answer in the chat. Save files only when the user asks to save, archive, audit, or process a batch.

## Inputs and mode

Use the supplied URLs, screenshots, long images, PDFs, pasted text, or source list. Read related page text and media as needed for the question.

| Request | Work |
|---|---|
| Read, explain, summarize, evaluate, compare, or fact-check | Read-only review |
| Save, archive, audit, batch-process, or resume saved sources | Durable evidence |
| Install or adopt a discovered project | Handle the requested action under that project's instructions |

For a bare URL, use the conversation's established purpose. Ask one concise question when the intended result remains unclear. In the first short update, name `web-bookmark-intelligence` when using it.

Durable work needs an `output_root` supplied by the user or defined by the current project. Ask for a destination if neither exists. Keep writes inside that root and leave the supplied inputs unchanged.

## Select The Retrieval Route Before Access

Honor the user's explicit tool choice and reuse the current task's working, logged-in page. For a new browser session, use the first available route in this order:

1. `ego-browser` / ego lite.
2. Tabbit.
3. The system default browser or a commonly used browser recorded by the current harness.
4. The harness's built-in browser.

Read the chosen browser's current Skill/API. For Ego, run `ego-browser skill` and read its complete output before browser actions. Check that the route supports the page access and operations required by this task. If it is absent or connection recovery fails, continue to the next available route. Stop for user action at a login, CAPTCHA, permission denial, or user takeover.

For public text, an available extraction tool can retrieve the body directly. If it returns only metadata or incomplete text, open the page in the selected browser. Keep the page's actual response separate from a tool connection or pre-navigation URL rejection when reporting a failure.

## Read-only review

1. Retrieve the substantive page text. Render the page when static extraction is incomplete.
2. Inspect images or canvas content when the requested judgment depends on them. Use the current runtime's image capabilities; read [media-routing.md](references/media-routing.md) if external media processing or saved media evidence is needed.
3. Answer in the user's language. State the source, relevant claims, your assessment, and any evidence gap that affects the conclusion. Link important sources.
4. If usable content remains unavailable, identify the failed route and request pasted text, a screenshot, or a PDF.

Keep ordinary review in the chat. Preserve body evidence already obtained if a later probe fails. Mention tool versions, hashes, and receipt fields only when they explain a requested diagnostic or saved audit.

## Durable evidence

1. Create one case per source with `scripts/intake_case.py` inside the authorized `output_root`.
2. Capture the page using the route above. Save case-local HTML and relevant media, then run `scripts/capture_pipeline.py`.
3. When claims depend on images, preserve the body/media distinction and complete the inventory in [media-routing.md](references/media-routing.md).
4. Bind the case with `scripts/assess_capture_evidence.py`. Create page-purpose notes or action cards when requested.
5. For a batch, use `scripts/plan_batch.py` to create or resume the plan, then capture each planned case through the selected route.

Read [capture-and-quality-gates.md](references/capture-and-quality-gates.md) for saved capture checks and [batch-profiles.md](references/batch-profiles.md) for batch processing. Use historical adapters only for an explicitly requested compatibility run.

## Access and evidence

- Base the answer on page text and relevant media. Identify observations, interpretation, and unresolved facts where they affect the answer.
- Use authorized access. Leave login, CAPTCHA, paywall, or other access challenges for the user.
- For direct network requests by package code, accept public `http`/`https` destinations, reject embedded credentials and non-public addresses, validate redirects, and keep TLS verification enabled.
- Before sending private or restricted content to an external provider, obtain authorization for that asset and provider.
- Install missing software only when installation is requested.

## Completion

A review is complete when it answers the requested question from substantive source content, or reports the specific missing content that prevents an answer.

For durable work, read back saved artifacts, verify their hashes and same-case bindings, and give the output path plus completed, partial, blocked, and failed counts. Leave every incomplete source in a resumable state with its next action.
