# Observed recovery case (sanitized)

One local recovery attempt produced usable diagnostic artifacts but failed full visual conversion. No private source, preview, product text or raw log is distributed here.

- `file` reported Corel Draw version 17–22, while magic was PK and Python could read a ZIP. Members included mimetype, content/root.dat, content/data/*.dat, previews/thumbnail.png, previews/page1.png, META-INF metadata/textinfo and ICC data. Container inspection takes precedence over assuming RIFF from the extension.
- Metadata recorded NumPages=1, NumLayers=1, CoreVersion=1800, AppVersion=2700 and A4. FontsUsed was empty and the text-object count was zero. These are metadata observations, not proof that visible lettering never existed or that text is editable; text can be outlined.
- CorelDRAW and Inkscape were absent. One bundled LibreOffice headless PDF attempt failed with `source file could not be loaded` and font-cache warnings. The cause was not established, and this does not establish universal LibreOffice incompatibility.
- Temporarily relocated, SHA256-verified libcdr 0.1.9 / librevenge 0.0.6 macOS bottles ran cdr2xhtml successfully. Namespace-aware extraction yielded 3320 paths, 46 groups, absolute M/L/C/Z commands, and no transforms. Group identifiers such as Layer1000 did not prove 46 original layers.
- Artwork lay outside the declared A4 page. A trial used coordinate/control-point bounds plus margin without changing path coordinates. This was a conservative bound, not an exact cubic-curve box; the enlarged page no longer preserved A4 dimensions.
- rsvg-convert produced PDF and transparent PNG; a white-background preview and PDF readback enabled comparison. Of 3320 paths, 2652 had fill:none with no stroke. That count is a warning signal, not by itself a fidelity verdict: intentionally invisible paths exist.
- Visual comparison with the embedded thumbnail showed substantial red/purple/gray fill and text-appearance loss. The output was therefore partial/incomplete despite zero converter exit status and abundant paths. No colors were guessed back into the output.
- PSD was not generated. Full rendering, vector editability, original layers, editable text and print readiness remained separate goals. The source hash was unchanged; only copies and separate outputs were processed, with no source upload or global tool installation.

Embedded PNG, XHTML, extracted SVG and SVG-derived PDF/PNG were observed outputs; the latter derivatives were incomplete. Object/layer asset packages, assembled layered PSD, Inkscape import and native CorelDRAW export are conditional alternatives, not tested successes for this case.
