---
name: web-bookmark-intelligence
description: Turn a public URL, webpage, bookmark batch, screenshot, long image, or video page into a reviewable evidence case with verified body/media evidence, contextual comparison, GitHub record snapshots, and user-gated action cards. Use for webpage capture quality, WeChat or Shoulong bookmark batches, screenshot or canvas understanding, video-page intake, and deciding whether a discovered project merits research, a PoC, cataloging, or later adoption.
---

# Web Bookmark Intelligence

## Materials

Materials: Use the user-authorized public URL list or local screenshot/video-page input, the declared output root, the actual capture-script path and SHA-256, and only caller-provided privacy-filtered context. The detailed references and fixtures are indexed below.

## Task

Core purpose — turn each in-scope source into a receipted evidence case and a user-gated action card without treating discovery as adoption.

Create evidence cases and user-gated action cards only. This top-level package is the single implementation source inside the shared `obisoldbee/skills` checkout; wrapper projections, route adapters, export rows, and Agent links must not contain copied implementation bytes. Source presence, a healthy link, and a passing offline validator do not prove runtime discovery, browser availability, execution, or adoption.

## Workflow

1. Create one case with `scripts/intake_case.py`: accept a public URL, local screenshot/long image, or a video-page URL. Keep the original input, source boundary, and authorization state.
2. For URLs, use `scripts/run_workbuddy_capture.py` with the WorkBuddy v1.5.1 entry point. Generic webpages and WeChat use this same core capture pipeline.
3. Run `scripts/capture_pipeline.py` on static or rendered local HTML. It keeps title and meta description separate from body evidence. A weak DOM, placeholder/noise DOM, canvas, or image-led page routes to media review; never promote a meta description to article body.
4. Route local screenshots, long images, canvas evidence, and substantive page images through the existing `media-understanding` workflow. Record image inventory, raw/OCR/visual outputs, hashes, and any uncertainty before interpreting the page.
5. Fuse DOM and media results with `scripts/assess_capture_evidence.py`. Use only these final evidence states: `full_body`, `full_body_with_media_supplement`, `needs_image_supplement`, or `failed`.
6. Prepare a bounded page-purpose handoff with `scripts/prepare_page_purpose.py`; semantic interpretation must cite the fused evidence rather than page metadata alone.
7. Compare the resulting case against caller-provided, privacy-filtered current-affairs/project/office/life/GitHub context. Build user-gated action cards with `scripts/build_action_cards.py`; GitHub records retain source, purpose, discussion conclusion, star/fork/watch snapshot, and observation time.

## Constraints

Constraints: Preserve access, provenance, privacy, and evidence gates; a capture attempt never grants adoption or formal-write authority.

- Start with fast local HTML/body extraction, then render with Playwright only when the quality gate requires it. Do not treat a static probe as a completed capture.
- A rendered DOM that is short, placeholder-like, canvas-led, or materially image-led must receive media inventory/understanding. A valid text body may still become `full_body_with_media_supplement` when images carry claims needed for the case.
- `plan_batch.py --profile shoulong` is only a continuity/batch profile over the same WorkBuddy capture and media pipeline. It is not a second scraper.
- Follow the bounded TLS retry in [capture-and-quality-gates.md](references/capture-and-quality-gates.md): preserve every attempt receipt, retry only one eligible certificate failure with certifi, and never disable TLS verification.

## Reference materials

- [Capture quality gates and TLS receipts](references/capture-and-quality-gates.md)
- [Media routing and evidence contract](references/media-routing.md)
- [Batch profiles](references/batch-profiles.md)
- [Context and GitHub contract](references/context-and-github-contract.md)
- [Purpose and action-card prompt](references/prompts/page-purpose-action-card.md)
- [Candidate provenance](references/provenance.md)
- [Historical baseline fixture](fixtures/historical-15.json) and [real-recapture regression fixture](fixtures/recapture-regression.json)

Task: Execute the single evidence flow for every in-scope source, preserve each route receipt, and stop at a user decision gate.

## Output format

Output format: Persist the case artifacts below and respond in the user's language; default to Chinese.

Write one case directory per source with its intake record, capture plan or execution receipt, body/media evidence state, source/hash inventory, purpose handoff, and user-gated action cards. Preserve per-attempt failures instead of flattening them into one status. Respond in the user's language; default to Chinese.

## Success criteria

Success criteria: Require evidence-backed final states and an explicit user gate before any next action.

- Stop and ask before authenticated/private capture, publication, adoption, installation, or any formal-layer write. Never bypass CAPTCHA or access controls.
- Article existence, title, meta description, screenshot cover, video metadata, a capture plan, or a route prediction is not complete content evidence.
- Do not silently switch engines, suppress a failed receipt, rerun unrelated historical cases, or query live GitHub/context without explicit authorization.
- Success requires a final evidence state backed by the required DOM/media receipts, package-contained outputs, and a user decision gate for any next action; merely invoking a browser or returning one page title is not success.
