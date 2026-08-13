# Capture Quality Gates And TLS Receipts

## One capture implementation

`run_workbuddy_capture.py` invokes the supplied WorkBuddy v1.5.1 script. Generic webpages, WeChat pages, and Shoulong batches all use that one wrapper; Shoulong changes only continuity and batch controls.

```text
public URL → fast local HTML probe → DOM quality gate
  → weak/meta-only/noisy → WorkBuddy Playwright → rendered quality gate
  → image inventory → media-understanding/OCR when media carries claims
  → assess_capture_evidence.py → purpose handoff → comparison/action card
```

Static HTML is a fast probe, not a completion claim. A page is never complete merely because the title, meta description, screenshot cover, or video metadata exists.

## Body and media gates

The local DOM pass threshold is two substantive paragraphs and at least 400 meaningful characters. The gate records `body_provenance`, `body_evidence_state`, image count, canvas presence, and a `dom_noise_or_placeholder` flag. It keeps `meta_description` separate and always sets `meta_description_as_body: false`.

| DOM condition | Gate route | What may become final after evidence fusion |
| --- | --- | --- |
| Substantive DOM, no necessary visual claim | purpose handoff (media inventory if assets exist) | `full_body` |
| Substantive DOM plus a claim carried by image/canvas/video-page media | inventory then media-understanding | `full_body_with_media_supplement` only after media evidence succeeds |
| Short, placeholder/noise DOM with image/canvas evidence | Playwright if not rendered, then media-understanding/OCR | `needs_image_supplement` when media evidence is available |
| Meta-only, unusable rendered DOM, or no usable body/media | preserve failure evidence | `failed` |

Image count alone is only an inventory signal: repeated UI/carousel assets can be non-substantive. The media inventory decides whether an image carries a claim needed for page purpose. Canvas or text-short/image-led pages must enter the media route; a media-led claim cannot be inferred from a meta description.

`assess_capture_evidence.py` is the only script that emits the four final states. It does not turn a weak DOM into `full_body`; it can only use explicitly supplied, successful media evidence to form `needs_image_supplement` or `full_body_with_media_supplement`.

## TLS/certifi retry and receipt preservation

The wrapper supports verified system trust or a certifi CA bundle. `auto` starts with system trust so the first real receipt remains observable; it has no flag, code path, or fallback that disables certificate validation.

1. Preserve a first attempt in `capture-execution-receipt.json` and separate immutable stdout/stderr files with SHA-256 hashes.
2. Only an initial **system-trust** certificate-verification failure may receive one retry, and only when `certifi` is locally available. The retry uses `SSL_CERT_FILE=certifi.where()`.
3. Do not retry success, timeout, non-TLS failures, or a failed certifi attempt. Retain both attempt receipts even when the retry succeeds.
4. Keep per-attempt WorkBuddy output directories separate. Record return code, timestamps, elapsed seconds, TLS strategy, log hashes, and article candidate paths before later quality/reconciliation records.

This is the bounded Zcode v1.3 improvement absorbed into the WorkBuddy mainline. It is a certificate-store selection, not an SSL bypass.

## Regression boundaries

- `fixtures/historical-15.json` keeps the old meta-description conflict boundary: a historical marker never qualifies as a body pass.
- `fixtures/recapture-regression.json` preserves the five verified WorkBuddy receipts and their actual final states: `full_body`, `full_body_with_media_supplement`, and `needs_image_supplement`.
- Run both replay scripts after gate changes. They are offline and read evidence already retained in the two historical packages.
