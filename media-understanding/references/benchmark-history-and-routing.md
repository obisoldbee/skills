# Benchmark History And Scenario Routing

## Status and provenance

This is a decision reference retained inside `media-understanding`; it does not authorize a provider request, replace raw evidence, or make a global default permanent. The benchmark facts below are historical source material from Akashic package `20260727002-codex`, primarily VU01–VU10 on 2026-07-27. Re-run or re-evaluate when the task family, model, endpoint, quota, or user priority changes.

## Never promote one visual winner to every task

Keep at least these task families separate: `ui_layout_and_infographic`, `plain_screenshot_bulk_reading`, `meme_and_cultural_semantics`, `document_ocr_and_structure`, and `video_temporal_understanding`. A winner in UI screenshots does not become a meme, OCR, video, or general-image default without relevant cases.

## Historical VU01–VU10 and OCR conclusions

- MiniMax-M3 scored `91.7`, returned 10/10, and was 10/10 directly parseable/schema-complete in the correctness-first UI/infographic baseline. It was the current UI/infographic recommendation under the then-active included plan, not a global image or meme default.
- Ark Agent Doubao Seed 2.0 Mini scored `91.6`, returned 10/10, and had the strongest recorded position detail (`38.1/40`). Reserve this route for layout-critical work only after its separate quota state is acceptable.
- Doubao Seed 2.0 Lite scored `85.3`, returned 10/10, and was complete; use it only for lower-risk bulk screenshot processing where reduced detail is acceptable. The recorded Lite:Mini plan coefficient was `2:1`, but it does not make their separate quota pools equivalent.
- Agnes 2.0 Flash and 2.5 Flash returned text for 10/10 benchmark cases but had 0/10 complete JSON and required truncated-output salvage. Treat it as an explicitly selected free rough-reading candidate, never an automatic normalizer/default.
- For OCR, GLM-OCR had the most direct readable text projection; MinerU produced document-oriented Markdown/structure; Unlimited-OCR required strict separation of readable text from `<|det|>`/bbox evidence. OCR remained an auxiliary track for the image benchmark.

## Meme correction and current default

The current **task-family-scoped** default for `meme_and_cultural_semantics` is Doubao `doubao-seed-2.0-lite`, not a global visual default. A separate historical 17-case Lu Shuanghou comparison had MiniMax/mmx mean self-score `5.38` over 16 numeric cases and Doubao Lite `8.47` over 17; Doubao completed `17/17` cases versus `16/17` for MiniMax/mmx. These were model self-scores rather than independent human grades, so the evidence supports a low-cost working default, not a cultural-champion claim. The important conclusion is scenario drift: models repeatedly flattened or reversed subtle emotion, viewpoint, and low-resolution/crop cues.

The strongest human correction involved the text `妈妈开门 我是离谱`; all tested models missed the full Chinese wordplay and peephole/fisheye viewpoint. A meme benchmark must therefore include human truth for `cultural_punchline`, `emotion_polarity`, `viewpoint`, `visual_degradation_as_signal`, and `wordplay`. A wrong cultural explanation or reversed emotion is a correctness `OUT`, not a minor style issue.

For a single current attachment, select Doubao Lite through its independent Volcengine Coding Plan profile and state uncertainty. If that profile is unavailable or not authorized, stop or request an explicitly selected alternative; do not silently use Codex native or OCR. For high-confidence or batch work, retain the meme truth fields and rerun a meme-specific benchmark; do not inherit the UI/infographic route.

## User-provided plan and connection snapshot — 2026-07-29

- MiniMax: the user states the existing plan continues into the next calendar year. Record included-plan marginal cost only as user-provided, and recheck before any material cost decision or at plan expiry.
- Volcengine Agent Plan: the user states it may expire in September 2026. Treat it as possibly near expiry and strategically scarce; Coding Plan is a separate pool. Do not treat either as a generic fallback.
- Agnes: the user states it is free. It still requires a public image URL and a provider-side remote fetch; it is not the default for local/private images. Preserve failures such as remote-fetch failure, timeout, rejection, empty output, and parse failure rather than hiding them behind another provider.

No live billing, endpoint, or model request was made to establish this snapshot.

## Route record and review trigger

Every recommendation must retain `task_family`, `benchmark_version`, `evidence_scope`, `default_participant_id`, `quota_pool`, `marginal_cash_cost`, `strategic_quota_cost`, `valid_until`, and `cross_family_reuse: forbidden_without_relevant_cases`. Re-evaluate when a plan expires or changes, a model/endpoint changes, a source benchmark is superseded, or user priorities change.
