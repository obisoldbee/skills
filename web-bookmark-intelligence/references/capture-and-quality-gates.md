# Capture And Quality Gates

Read this reference only for explicitly requested durable evidence work. Ordinary read-only review uses the current runtime's authorized web or browser capability and does not require case files or a particular executor.

## Runtime-Neutral Capture

The default durable route is:

```text
public URL -> authorized browser or retrieval tool -> case-local HTML/media
  -> capture_pipeline.py -> optional media understanding
  -> assess_capture_evidence.py -> optional purpose notes/action cards
```

The Agent selects the route before access. An explicit user browser choice wins; otherwise it must first discover applicable page-extraction or browser-control Skills listed in the current session, read the selected route's contract, and obey its priority. Only when no purpose-built route applies may it default to a generic runtime browser. A static metadata probe does not consume the rendered-browser route.

An ordinary bootstrap or sandbox-only availability failure may use the selected route's documented recovery once. An explicit safety-policy, access-control, CAPTCHA, login, or user-control stop must not be bypassed through another tool. A route rejected before navigation proves only that route was blocked, not that the webpage was inaccessible. Do not expose executor versions, hashes, or internal compatibility codes unless the user requested a capture diagnostic.

Static HTML is a fast probe, not a completion claim. A page is never complete merely because the title, meta description, screenshot cover, or video metadata exists.

## Body And Media Gates

The local DOM pass threshold is two substantive paragraphs and at least 400 meaningful characters. The gate records `body_provenance`, `body_evidence_state`, image count, canvas presence, and a `dom_noise_or_placeholder` flag. It keeps `meta_description` separate and always sets `meta_description_as_body: false`.

| DOM condition | Gate route | What may become final after evidence fusion |
| --- | --- | --- |
| Substantive DOM, no necessary visual claim | purpose handoff if requested | `full_body` |
| Substantive DOM plus a claim carried by image/canvas/video-page media | inventory then media understanding | `full_body_with_media_supplement` only after media evidence succeeds |
| Short, placeholder/noise DOM with image/canvas evidence | render if needed, then media understanding/OCR | `needs_image_supplement` when media evidence is available |
| Meta-only, unusable rendered DOM, or no usable body/media | preserve failure evidence | `failed` |

Image count alone is only an inventory signal. For durable cases, record each substantive body image or canvas occurrence, its locator, duplicate relation, availability, and exact case-local asset reference. When an image carries a claim, successful media evidence requires nonempty case-bound OCR or visual result bytes, not a self-declared success label.

`assess_capture_evidence.py` emits the durable final states. `intake/v2`, `capture-record/v3`, optional `media-evidence/v2`, and `evidence-assessment/v2` must declare the same case id and package-relative case root. Missing, tampered, cross-case, symlinked, undeclared, or wrong-schema evidence produces `failed: case_lineage_mismatch`.

## Direct-Script Network Boundary

This boundary applies when package code performs direct network requests. It does not require a runtime-managed browser to prove a particular vendor's internal implementation.

- Accept only public `http` or `https` destinations without embedded credentials.
- Reject resolution failure, empty answers, non-public or mixed public/private answers, and private IPv4-mapped IPv6.
- Validate every redirect destination and keep TLS verification enabled.
- Never bypass authentication, CAPTCHA, paywalls, or access controls.

## Optional Legacy WorkBuddy Adapter

`scripts/run_workbuddy_capture.py` is a standalone legacy compatibility executor. It may be run only when that compatibility path is explicitly requested; it is not called by the default review flow or by `plan_batch.py`.

The adapter intentionally recognizes historical implementation bytes by exact hash and may return `needs_compatible_executor`. That result means only that this optional adapter cannot run; it must never be reported as proof that `web-bookmark-intelligence` itself is unusable. Exact historical versions and hashes belong in [provenance.md](provenance.md) and regression fixtures, not in ordinary user output.

The legacy adapter keeps TLS verification enabled and preserves per-attempt receipts. Do not silently substitute it for the runtime's normal browser.

## Regression Boundaries

- `fixtures/historical-15.json` keeps the old meta-description conflict boundary: a historical marker never qualifies as a body pass.
- `fixtures/recapture-regression.json` preserves five historical capture receipts and their actual final states.
- Historical replay validates retained evidence only. It is not proof of current browser availability, network compatibility, or capture execution.
