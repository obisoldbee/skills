# Media Routing And Evidence Contract

Use the installed `media-understanding` workflow for actual image/OCR/visual interpretation. This candidate only prepares the input and preserves evidence; it does not call a provider by itself.

## When media is mandatory

| Source or gate result | Required work | Evidence to retain |
| --- | --- | --- |
| Screenshot | visual understanding; OCR only when readable text matters | original hash, dimensions, OCR and visual output kept separately |
| Long image or canvas | region/tile inventory, OCR, visual-layout fusion | source-region or tile coordinates and raw asset references |
| Text-short, image-led rendered page | image inventory then media-understanding/OCR | DOM quality record, image list/hashes, raw OCR/visual evidence |
| Full text page with image-led claims | media review before claiming the images' contents | body spans plus image-level evidence |
| Video page | capture page evidence first, then a separately authorized accessibility/ASR/visual route | URL, accessible media reference, timestamps, and track-specific evidence |

The capture record derives a deterministic occurrence-level `dom_media_inventory` from every body `<img>` and `<canvas>`, including locator and duplicate linkage. Captured source assets bind exact DOM ids; a missing unique asset remains explicitly unavailable and cannot pass assessment. The media receipt must cover the exact DOM-id set once each—missing, duplicate, or foreign-extra items fail—and distinguish content assets from covers, repeated carousel/UI assets, tracking pixels, and unavailable media. It declares `inventory_status: completed` and an explicit boolean `media_claims_required`. Claim-bearing media additionally requires nonempty `ocr` or `visual` result artifacts plus an executor receipt that binds the same case, source asset, and exact result hashes. A `status: success` label with no inventory/result bytes is unavailable evidence. Only substantive images can set the claim-required boolean and supply a successful supplement; a missing inventory receipt never means that claims are absent.

Use `assess_capture_evidence.py` to bind a successful media result to its intake and DOM evidence. The media receipt must carry the same case id/root and exact intake, capture, and capture-declared source-asset paths and SHA-256 values. A media result copied from another case is rejected even if its status says `success`. OCR is not a page-purpose conclusion, visual understanding is not a verbatim transcript, and a cover/title/meta description is not video understanding.

## Privacy and provider boundary

Default `external_send_policy` is `none`. Internal, office, personal-life, health, account, token, cookie, or location media remains local unless the user approves the exact asset and provider. Preserve raw asset, OCR result, visual interpretation, and semantic page-purpose inference as distinct artifacts.
