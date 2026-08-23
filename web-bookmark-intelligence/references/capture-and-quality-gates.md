# Capture Quality Gates And TLS Receipts

## One capture implementation

`run_workbuddy_capture.py` recognizes an implementation only by its exact SHA-256. Immediately before execution it reads and hashes the resolved implementation once, then executes those already-verified bytes through the interpreter's standard-input script mode (`python -`). It never asks the interpreter to reopen a replaceable script path. A receipt binds the caller-supplied path, resolved path, source pre/post hashes, execution-input pre/post hashes and byte count, exact argv plus input hash, immutable stdout/stderr hashes, and every case artifact's path/bytes/SHA-256. An arbitrary exit-0 script remains `unknown`, receives no observed version, is not executed, and returns `needs_compatible_executor`.

The retained WorkBuddy v1.5.1 hash is recognized for provenance, but its retained evidence does not prove every-redirect DNS revalidation or destination IP pinning. It therefore cannot currently pass the network execution gate. `required_implementation.version: v1.5.1` states the requirement; only `observed_implementation.version` states an identified implementation.

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

Image count alone is only an inventory signal: repeated UI/carousel assets can be non-substantive. Capture therefore records every DOM image/canvas occurrence, stable locator, duplicate relation, availability, and exact case-local asset reference. Assessment recomputes that inventory from current HTML and requires every unique occurrence to be captured. When the DOM gate reports `media_inventory_required: true`, the case-bound media receipt must cover the exact DOM-id set once each, declare `inventory_status: completed`, and state an explicit boolean `media_claims_required`; omitting or partially covering that receipt cannot produce `full_body`. When an image carries a claim, successful media evidence means nonempty hash-bound OCR/visual result bytes and a case/source/result-bound executor receipt, not a self-declared success string. Canvas or text-short/image-led pages must enter the media route; a media-led claim cannot be inferred from a meta description.

`assess_capture_evidence.py` is the only script that emits the four final states. It does not turn a weak DOM into `full_body`; it can only use explicitly supplied, successful media evidence to form `needs_image_supplement` or `full_body_with_media_supplement`.

It also requires one case lineage. `intake/v2`, `capture-record/v3`, optional `media-evidence/v2`, and `evidence-assessment/v2` must declare the same case id and package-relative case root. The capture binds the intake path/hash and declares each media source asset. A successful media receipt binds the actual intake and capture paths/hashes plus one declared case-local source asset path/hash. Any missing, tampered, cross-case, symlinked, undeclared, or wrong-schema source produces `failed: case_lineage_mismatch`.

## DNS, redirect, and rebind gate

Execution evaluates A and AAAA together. It rejects NXDOMAIN/resolution failure, no address records, non-public answers, mixed public/private answers, and private IPv4-mapped IPv6. A second pre-dispatch lookup must return the same public address set. These two snapshots detect a local resolution change but do not protect later redirects or rebinding. Network execution is compatible only when the exact recognized implementation additionally proves either DNS validation on every redirect hop or destination-IP pinning. Otherwise the wrapper stops before subprocess execution with `needs_compatible_executor`.

## TLS/certifi retry and receipt preservation

The wrapper supports verified system trust or a certifi CA bundle. `auto` starts with system trust so the first real receipt remains observable; it has no flag, code path, or fallback that disables certificate validation.

1. Preserve a first attempt in `capture-execution-receipt.json`, record its full command, and keep separate immutable stdout/stderr plus complete artifact hashes.
2. Only an initial **system-trust** certificate-verification failure may receive one retry, and only when `certifi` is locally available. The retry uses `SSL_CERT_FILE=certifi.where()`.
3. Do not retry success, timeout, non-TLS failures, or a failed certifi attempt. Retain both attempt receipts even when the retry succeeds.
4. Keep per-attempt WorkBuddy output directories separate. Record return code, timestamps, elapsed seconds, TLS strategy, log hashes, and article candidate paths before later quality/reconciliation records.

An implementation SHA change before or during execution, an output symlink, or exit 0 without a hashed `article.md` artifact is a failed capture. A successful execution is only `captured_pending_quality_gate`; batch state records `pending_quality` until case-bound assessment succeeds.

This is the bounded Zcode v1.3 improvement absorbed into the WorkBuddy mainline. It is a certificate-store selection, not an SSL bypass.

## Regression boundaries

- `fixtures/historical-15.json` keeps the old meta-description conflict boundary: a historical marker never qualifies as a body pass.
- `fixtures/recapture-regression.json` preserves the five verified WorkBuddy receipts and their actual final states: `full_body`, `full_body_with_media_supplement`, and `needs_image_supplement`.
- Run both replay scripts after gate changes. They are offline and read evidence already retained in the two historical packages.
- Historical replay validates retained evidence only. It is not a current executor compatibility, DNS, redirect, provider, or browser availability receipt.
