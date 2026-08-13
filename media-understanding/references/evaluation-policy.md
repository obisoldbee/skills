# Evaluation Policy

## Correctness first

Correctness is a hard gate, not a weighted dimension. Compare the answer with the source image and corroborating outputs. A confirmed hallucination, obvious text error, or material visual contradiction sets the case to `OUT`. A participant with a confirmed `OUT` case cannot become the default for that benchmark version.

Do not treat an unflagged output as proven correct. Record the exact evidence and keep subtle-error review open.

## Quality dimensions after the gate

Use this 100-point diagnostic rubric only for correct successful outputs:

| Dimension | Points | Evidence |
| --- | ---: | --- |
| Position detail | 40 | Explicit regions, hierarchy, directions, grouping, arrows, table/process relations, and element-to-element correspondence. |
| Holistic understanding | 30 | Reconstruction of purpose plus illustrations, colors, emphasis, visual hierarchy, and how those cues change interpretation. |
| Text fidelity | 20 | Accurate titles, names, numbers, commands, and key claims. |
| Uncertainty control | 10 | Clear limits for occlusion, tiny text, external context, and unverified claims. |

Response length alone earns no points.

Use track-specific evidence:

- Image understanding: position, grouping, hierarchy, colors, illustrations, arrows, and text-to-visual relations.
- Meme and cultural semantics: viewpoint, emotion polarity, social/cultural reference, punchline or wordplay, intentional blur/crop/distortion, and whether the adaptation preserves the original joke rather than only its nouns. A reversed emotion or invented cultural explanation is a correctness failure.
- Video understanding: grounded timestamps, event order, scene transitions, object/person continuity, actions, on-screen text, audio/transcript evidence, and cross-shot conclusions. Penalize a summary that ignores temporal change.
- OCR: character fidelity, reading order, table/column structure, coordinates when requested, and preservation of document hierarchy. Do not award OCR for unsupported whole-scene interpretation.
- Document vision: page order, headings, paragraphs, tables, figures, footnotes, and cross-page continuity. Keep OCR accuracy separate from semantic summarization.

## Failure taxonomy

- `connection_or_access`: timeout, connection reset, temporary DNS/access failure. Exclude from capability quality; report availability separately.
- `provider_or_model_returned_failure`: HTTP response with empty answer, rejection, model error, or terminal service response. Count against model-return success.
- Never merge these two classes into a single zero-filled quality average.

## Reconnect policy

When authorized, allow at most three reconnect retries after the initial attempt, with 2/5/10-second backoff. Retry transport failures and HTTP 429/502/503/504. Do not retry HTTP 200 empty answers, content/model rejection, invalid successful output, or hallucination.

Preserve each attempt. Report first-attempt success and retry-adjusted success separately.

## Price

Price is an operational tie-breaker after correctness and quality. Keep these fields separate:

- cash marginal cost;
- subscription plan and list price;
- provider-reported input/output/reasoning tokens;
- official plan-accounted usage;
- quota multiplier or weighted usage, only when an official source exposes it.
- quota expiry and strategic scarcity, including whether the same pool is uniquely needed for another task family.

User-confirmed free or already-included plans may use marginal cost zero. Do not invent multipliers from community estimates.

Do not compare raw provider tokens across different subscription pools as if they were one price scale. When an official source provides a relative coefficient, record its exact meaning and date, but keep it separate from pool capacity, remaining quota, expiry, marginal cash cost, and actual per-run plan consumption.

## Machine usability

Report machine usability separately from content quality. A syntactically clean response can still hallucinate, and a useful free-form response can still be unsafe for automated ingestion.

Record at least:

- `json_parse_rate`: directly parseable successful responses divided by successful responses;
- `schema_complete_rate`: responses containing every required field;
- `truncation_rate`: successful responses cut off before completion;
- `salvage_required_rate`: responses requiring heuristic repair or free-form extraction;
- `raw_to_normalized_loss`: whether normalization discards text, layout relations, uncertainty, or evidence;
- `first_attempt_success` and `retry_adjusted_success` as separate availability measures.

Do not award content-quality points for machine readability. Do not adopt a participant with a confirmed correctness `OUT` merely because its JSON is valid.

Treat OCR as an auxiliary track unless the benchmark objective is explicitly OCR. For OCR outputs, preserve readable text separately from coordinates, detection tags, hashes, and other layout metadata. Never insert raw detection markers into semantic context as if they were document text.
