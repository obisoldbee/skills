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

The inventory must distinguish content assets from covers, repeated carousel/UI assets, tracking pixels, and unavailable remote media. Only substantive images can supply a required supplement.

Use `assess_capture_evidence.py` to bind a successful media result to its DOM evidence. OCR is not a page-purpose conclusion, visual understanding is not a verbatim transcript, and a cover/title/meta description is not video understanding.

## Privacy and provider boundary

Default `external_send_policy` is `none`. Internal, office, personal-life, health, account, token, cookie, or location media remains local unless the user approves the exact asset and provider. Preserve raw asset, OCR result, visual interpretation, and semantic page-purpose inference as distinct artifacts.
