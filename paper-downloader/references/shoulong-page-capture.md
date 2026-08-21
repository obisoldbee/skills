# Shoulong article-page branch

Use this branch only when the user provides or authorizes discovery of public `chinalowcarb.com` article URLs and asks to capture those pages as inputs for explicit paper identifiers.

## Shared capture engine

Use the separately registered top-level `$web-bookmark-intelligence` Skill with `profile=shoulong`. It provides one serial, resumable case per URL; Shoulong is a profile, not a second scraper.

The WorkBuddy implementation source must be supplied explicitly and receipted by path and SHA-256. The current WorkBuddy metadata is inconsistent: its `SKILL.md` reports 1.4.0 while its live script declares v1.5.1. Bind bytes, not the label.

## Allowed evidence

- public article URL and canonical URL;
- capture timestamp and attempt receipts;
- rendered article text and page metadata that pass the DOM/body gate;
- explicit DOI, PMID, PMCID, PubMed/PMC, publisher, or direct PDF links present in that text;
- source-page-to-identifier mapping.

## Excluded routes

- `media-understanding` or any image OCR;
- interpreting screenshots, figures, covers, QR codes, or page images;
- creating paper-download tasks from image contents;
- reusing the historical 40,479-image pipeline or rerunning its prior results;
- treating article capture as an Akashic formal write.

If the rendered text does not expose a stable identifier or article landing link, record `no_explicit_text_citation` for this branch. Do not inspect images to fill the gap.
