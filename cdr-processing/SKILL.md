---
name: cdr-processing
description: Inspect CorelDRAW CDR containers, recover embedded previews, attempt local SVG/PDF/PNG conversion, and assess fidelity or layered PSD delivery options. Use for CDR artwork conversion and recovery, not call-detail records or generic image editing.
---

# CDR processing

Produce the requested usable artwork and an honest account of what survived conversion. File creation, exit code zero, and many vector paths do not prove fidelity.

## Bind the task

Bind `SOURCE` to the user-selected CDR, `OUT` to a separate authorized output directory, and `SKILL_ROOT` to this package. Discover available tools and versions before selecting a route. Ask only for missing source, output destination, or a consequential ambiguous target. Distinguish full visual rendering, editable vectors, retained source layers, editable text, and print readiness: each needs its own evidence.

Read the source without modification; hash before and after processing. Run converters on a copy in an isolated work directory. Write candidates, logs, previews and receipts only below `OUT`; never overwrite the source or existing outputs. Scripts require new output subdirectories. Do not publish private artwork, metadata, previews, filenames or logs with this public package. Conversion authorization alone does not authorize upload, dependency installation or downloads; reuse any explicit authorization already supplied.

Runtime: portable Python 3.9+ standard library for bundled helpers; any device/network for offline inspection. Conversion depends on discovered local tools. Missing dependencies mean report the missing capability and use an available authorized route, not silent installation. Native CDR parsers should process untrusted files in an OS sandbox when available.

## Workflow

1. Inspect magic bytes and container structure, not just extension or `file` version hints:
   `python3 -B "$SKILL_ROOT/scripts/cdr_tools.py" inspect "$SOURCE" "$OUT/inspection"`.
   The helper selectively reads known ZIP metadata and previews without `extractall`; RIFF is identified but not decoded. Its JSON may contain private metadata: keep it with local task outputs. Read embedded previews for comparison, never label them a full-resolution reconstruction. Zero text objects or empty FontsUsed may mean outlined text.
2. Choose the route using [conversion-routes.md](references/conversion-routes.md). Prefer the user's chosen tool when available. Use a native export when fidelity or print production requires it; local libcdr is a recovery attempt whose output still needs inspection. A failed LibreOffice invocation does not prove all LibreOffice builds cannot read CDR.
3. For `cdr2xhtml` output, extract namespace-qualified SVG:
   `python3 -B "$SKILL_ROOT/scripts/cdr_tools.py" extract "$OUT/converted.xhtml" "$OUT/svg"`.
   This preserves declared pages by default. If artwork is off-page, compare page bounds with artwork bounds before opting into `--fit-artwork --margin 10`. This changes physical page size, preserving the original unit-to-coordinate scale, not the original paper size. The helper conservatively encloses absolute M/L/C/Z endpoints/control points plus stroke allowance; it rejects unsupported geometry, transforms, CSS and effects. Do not strip rejected content to make validation pass. Use a capable renderer/editor for other SVGs. Group IDs are not source-layer evidence.
4. Render candidate SVGs to requested PDF/transparent PNG and a white-background preview; read PDF back through a separate renderer. Compare with the embedded preview and, when available, native source rendering. Check page coverage, colors, text appearance, outlines and material effects. A thumbnail supports gross comparison only; it cannot certify fine detail or printing. Use [output-contract.md](references/output-contract.md) for layered assets/PSD or print requests.
5. Record the visual decision on each actual delivered file:
   `python3 -B "$SKILL_ROOT/scripts/cdr_tools.py" assess "$OUT/candidate.pdf" --reference "$OUT/inspection/thumbnail.png" --visual fail --notes "Compared readback: major fills and text appearance missing" > "$OUT/qa.json"`.
   `assess` records a human/agent visual judgment; it does not compare pixels automatically. `fail` emits `partial_incomplete` and exit 2; default `unknown` remains `pending_visual_qa`; `pass` means `visual_match_only`, never editable/print-ready. Reference and comparison notes are required for pass/fail. Keep the corresponding rendered readback alongside the receipt.

## Finish truthfully

For accepted output, verify the requested dimensions/pages and relevant target properties, source hash stability, actual files, and visual comparison. For failed QA, stop calling the conversion complete: use names such as `trial-incomplete.svg` / `trial-incomplete.pdf`, retain the partial result if useful, list missing content and the next viable route. Do not invent missing colors or imply PSD exists when it has not been generated. Inspecting an incomplete result is a completed diagnostic, not successful full conversion.

Report paths, route/tool versions, tested versus conditional outputs, QA status, source preservation, and any unmet goal. State downloads/uploads/installations only as actually performed. Read [observed-case.md](references/observed-case.md) when diagnosing apparently successful but visually incomplete libcdr output; its counts describe one case, not universal CDR behavior.

Package checks: `python3 -B -m unittest discover -s "$SKILL_ROOT/tests" -v` and the host's skill-creator `quick_validate.py` on this package. All fixtures are synthetic and offline.
