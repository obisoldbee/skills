# Provenance

- Frozen source package: `Akashic/12-agent-submissions/2026/08/07/20260807001-codex/payload/snapshots/candidates/web-bookmark-intelligence-2.0/`.
- Earlier package source: `Akashic/12-agent-submissions/2026/07/31/20260731002-codex/payload/skills/web-bookmark-intelligence/`.
- Frozen source `SKILL.md` SHA-256: `16377e265751d1c820e9199fda50177c7aa72011b19aeffdf7de630dbe2b2790`.
- Frozen source tree SHA-256: `a80902f8987a12ceaedf308d46a2d5539b4b5bb609710d8830f5f325666c65f2`.

The migrated package keeps one capture core for public webpages, WeChat/public-account pages, bookmark batches, and the serial/resumable Shoulong profile. It does not create a second Shoulong scraper.

The WorkBuddy lineage has an apparent metadata mismatch: the current WorkBuddy `SKILL.md` frontmatter reports `1.4.0`, while its live `wechat_archive.py` declares `VERSION = "v1.5.1"`. Runtime execution must bind and receipt the actual script path and SHA-256; it must not infer implementation bytes from the frontmatter version alone.

On 2026-08-11, the 21-file working candidate was atomically moved from the collection-relative `working-skills/src/workflows/media/web-bookmark-intelligence/` path to the shared Git package scope `GitHub/web-bookmark-intelligence/`. Its pre-migration sorted relative-path/content-SHA inventory digest was `0e4c3b05d78d923a3b897c2be4d513abda874649916bfdf0365f52f04ba6b2bc`. The former working path is now a route adapter with no implementation bytes.

The Git package is the one physical implementation source. A wrapper projection, export declaration, or direct Agent link does not by itself prove runtime discovery, execution, or formal adoption.
