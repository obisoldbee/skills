# Local conversion routes

## Discover before installing

Check `command -v cdr2xhtml rsvg-convert inkscape soffice pdfinfo pdftoppm` (or platform equivalents), inspect versions/help, and check available CorelDRAW applications. A CLI absent from PATH may be bundled in an application. Do not infer installation from an old log. Record versions and converter stderr separately from source files. Reject failed or empty intermediate output; never pipe a failed conversion straight into a renderer.

Typical libcdr route, after binding `WORK` to a new isolated directory under the authorized output root and copying the source there with hash comparison:

```sh
cdr2xhtml "$WORK/source.cdr" > "$WORK/converted.xhtml" 2> "$WORK/converter.stderr"
# Check exit status and nonempty output before extraction.
python3 -B "$SKILL_ROOT/scripts/cdr_tools.py" extract "$WORK/converted.xhtml" "$WORK/svg"
rsvg-convert --format=pdf --output="$WORK/candidate.pdf" "$WORK/svg/candidate-1.svg"
rsvg-convert --format=png --output="$WORK/transparent.png" "$WORK/svg/candidate-1.svg"
rsvg-convert --format=png --background-color=white --output="$WORK/white-preview.png" "$WORK/svg/candidate-1.svg"
pdfinfo "$WORK/candidate.pdf"
pdftoppm -png -singlefile -scale-to 1600 "$WORK/candidate.pdf" "$WORK/pdf-readback"
```

These commands illustrate a single page; process and inspect every requested page from extraction.json. Confirm each command result before continuing. A white preview prevents transparency in dark viewers being mistaken for black artwork. Set explicit resolution for final raster outputs according to the user's physical size; default renderer DPI is not a print specification. Preserve original SVG alongside any fitted candidate. A fitted artwork page is not A4 merely because the original declaration was A4.

XHTML may include an external XHTML DOCTYPE. The helper uses a non-fetching Expat validation pass and ElementTree namespace parsing; entity declarations and internal subsets are rejected. It also rejects external SVG links, events, URL paints and active content. This is a limited recovery helper, not support for arbitrary SVG resources.

## Conditional isolated macOS bottle recovery

Use only if a needed tool is absent and downloading/temporary setup is authorized. Prefer an existing working installation. One tested environment used libcdr 0.1.9 and librevenge 0.0.6 arm64_sequoia bottles, with existing little-cms2 and icu4c@78. These are historical bindings, not universal dependencies.

1. Read the official Homebrew formula/API over verified TLS. Select an actual matching OS/architecture bottle and its declared dependencies, URL and SHA256; record metadata before downloading. Never use insecure TLS or invent a bottle name.
2. Download to an isolated tool directory, verify the archive SHA256 against that metadata, and inspect archive names before extracting only there. Do not copy binaries into the Skill or install globally.
3. On Mach-O bottles, inspect `otool -L` / load commands. If relocation placeholders `@@HOMEBREW_CELLAR@@` or `@@HOMEBREW_PREFIX@@` remain, resolve each against verified local dependencies or the temporary dependency tree. Use `install_name_tool -change` (and `-id` when needed) only on temporary copies; never patch a system library. Do not treat a similarly named ICU ABI as compatible.
4. Modified Mach-O may need `codesign --force --sign -` on temporary copies. Verify load paths and run a help/version smoke test, then test conversion. Stop on missing ABI/platform support instead of bypassing verification. Tool download is network access but does not itself upload source artwork.

Official distribution reference: [Homebrew libcdr](https://formulae.brew.sh/formula/libcdr). Exact dependency/version selection must be rechecked for the execution environment.

## Conditional application routes

CorelDRAW: open a copy with a compatible version, inspect actual pages/objects, then export the requested page or drawing range to PDF or PSD and read it back. Native export is a fidelity candidate, not automatic proof. Confirm object/layer structure separately. [CorelDRAW PSD technical notes](https://product.corel.com/help/CorelDRAW/540111147/CorelDRAW-en/CorelDRAW-Adobe-Photoshop-PSD.html) describe layer support and rasterized text; verify options in the installed version.

Inkscape: check the installed version's actual CDR import filter and test on a copy. If import works, inspect appearance before exporting SVG/PDF/PNG. Do not promise native CDR round-trip or PSD layer preservation. The supplied [Inkscape Files: Save wiki](https://wiki.inkscape.org/wiki/Files:_Save) discusses save behavior and proposals; it is not evidence that this particular CDR can be imported.

LibreOffice: if available, attempt a scoped conversion only when appropriate. A `source file could not be loaded` error warrants distinguishing filter/version, dependencies, source validity and fonts; font-cache warnings alone do not establish the cause. Stop or select another available route after a meaningful failure; repeated identical attempts add no evidence.
