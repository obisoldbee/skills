# Output and acceptance boundaries

| Output | Capability and required evidence |
|---|---|
| Embedded thumbnail/page PNG | Recovered preview only; record pixel dimensions. Not a high-resolution original reconstruction. |
| XHTML and extracted SVG | Converter intermediate and candidate geometry. Confirm pages, coverage, paints and text appearance. Paths alone do not prove fidelity or editable text. |
| PDF / transparent PNG / white preview | Rendered derivatives inherit conversion losses. Read back PDF, check alpha/background and requested dimensions. |
| Object/layer SVG or PNG asset package | Conditional on correct source reading and verified object/layer membership. Converter groups must not be silently relabeled as original layers. |
| Layered PSD assembled from PNGs | Raster layers, not native editable text/vector layers; requires actual assembly and independent reopen/flatten comparison. Not implemented by the bundled helpers. |
| CorelDRAW native PDF / PSD | Conditional on available compatible application and actual export/reopen. PSD may retain layers while rasterizing text. No native route was tested in the recorded recovery case. |

For an asset package, record a manifest with canvas width/height, pixel resolution and physical size, color profile, ordered unique layer IDs/names, source object provenance where known, file paths, alpha, and offsets in a single coordinate system. Keep a common full canvas or explicit offsets. Preserve stacking order and opacity; identify unsupported blend modes/masks. Recompose and compare with a trusted full rendering. Empty source-layer count is unknown; one source layer can contain many separately editable objects and does not establish a flat bitmap.

For PSD assembly, use a discovered capable library/editor only within existing setup authorization. Reopen the resulting PSD in an independent reader/editor, verify layer count/names/order/visibility and canvas, then flatten and compare. Report rasterized text and vectors explicitly. Do not generate a PSD from already incomplete intermediates and call it the recovered original. The helpers intentionally make no PSD-generation claim.

For print production, check only relevant requirements: final physical dimensions and bleed, page/drawing range, fonts versus outlines/rasterization, CMYK/ICC and spot colors, transparency/gradients/clipping and resolution. A visual thumbnail match cannot certify separations, font editability or print readiness. Use native export/preflight when those properties matter.

Official asset workflow: [CorelDRAW export objects and pages](https://help.coreldraw.com/CorelDRAW/540111192/Documentation-Windows/CorelDRAW-en/CorelDRAW-Export-assets.html). Availability and options depend on the installed edition/version. References checked 2026-09-11; application routes remain conditional until tested on the user's file.
