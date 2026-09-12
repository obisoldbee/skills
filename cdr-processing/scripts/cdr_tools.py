#!/usr/bin/env python3
"""Local CDR inspection, conservative SVG extraction, and explicit visual-QA receipts."""
import argparse
import hashlib
import json
import math
from pathlib import Path, PurePosixPath
import re
import sys
import xml.etree.ElementTree as ET
from xml.parsers import expat
import zipfile

SVG = '{http://www.w3.org/2000/svg}'
LIMIT = 64 * 1024 * 1024
NUMBER = r'[-+]?(?:\d+(?:\.\d*)?|\.\d+)(?:[eE][-+]?\d+)?'
TOKEN = re.compile(NUMBER + r'|[A-Za-z]')


def digest(path):
    h = hashlib.sha256()
    with Path(path).open('rb') as stream:
        for block in iter(lambda: stream.read(1024 * 1024), b''):
            h.update(block)
    return h.hexdigest()


def xml(data):
    if len(data) > LIMIT:
        raise ValueError('XML exceeds 64 MiB limit')
    parser = expat.ParserCreate()
    def reject(*args):
        raise ValueError('XML entities/internal DTD are forbidden')
    parser.EntityDeclHandler = reject
    parser.ExternalEntityRefHandler = reject
    parser.StartDoctypeDeclHandler = lambda name, system, public, subset: reject() if subset else None
    parser.SetParamEntityParsing(expat.XML_PARAM_ENTITY_PARSING_NEVER)
    parser.Parse(data, True)  # Does not fetch external DTDs; external entities are rejected.
    return ET.fromstring(data)


def read_xml(path):
    with Path(path).open('rb') as stream:
        return xml(stream.read(LIMIT + 1))


def inspect(source, out):
    before = digest(source)
    with Path(source).open('rb') as stream:
        magic = stream.read(12)
    report = {'source_sha256': before, 'container': 'unknown', 'status': 'inspection_only'}
    previews = {}
    if zipfile.is_zipfile(source):
        report['container'] = 'ZIP'
        with zipfile.ZipFile(source) as archive:
            infos = archive.infolist()
            if len(infos) > 10000:
                raise ValueError('too many ZIP entries')
            names = [i.filename for i in infos]
            if len(names) != len(set(names)):
                raise ValueError('duplicate ZIP entries')
            for i in infos:
                p = PurePosixPath(i.filename)
                if p.is_absolute() or '..' in p.parts or '\\' in i.filename or ':' in i.filename:
                    raise ValueError('unsafe ZIP member')
            report['entries'] = names
            report['metadata'] = {}
            for name in ('mimetype', 'META-INF/metadata.xml', 'META-INF/textinfo.xml',
                         'previews/thumbnail.png', 'previews/page1.png'):
                if name not in names:
                    continue
                info = archive.getinfo(name)
                if info.file_size > LIMIT or info.flag_bits & 1:
                    raise ValueError('oversized/encrypted selected member')
                with archive.open(info) as stream:
                    data = stream.read(LIMIT + 1)
                if len(data) > LIMIT:
                    raise ValueError('oversized selected member')
                if name.endswith('.xml'):
                    root = xml(data)
                    report['metadata'][name] = [{'tag': e.tag, 'text': e.text.strip(), 'attributes': e.attrib}
                                                for e in root.iter() if e.text and e.text.strip()]
                elif name.endswith('.png'):
                    if not data.startswith(b'\x89PNG\r\n\x1a\n'):
                        raise ValueError('preview is not PNG')
                    previews[PurePosixPath(name).name] = data
                else:
                    report['mimetype'] = data.decode('utf-8', errors='replace')
    elif magic.startswith(b'RIFF'):
        report['container'] = 'RIFF'
        report['riff_type_hex'] = magic[8:12].hex()
    if digest(source) != before:
        raise ValueError('source changed during inspection')
    Path(out).mkdir(parents=True, exist_ok=False)
    for name, data in previews.items():
        (Path(out) / name).write_bytes(data)
    (Path(out) / 'inspection.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    return report


def style(element, inherited):
    result = inherited.copy()
    for key in ('fill', 'stroke', 'stroke-width', 'stroke-miterlimit'):
        if key in element.attrib:
            result[key] = element.get(key)
    for item in element.get('style', '').split(';'):
        if item.strip():
            key, value = item.split(':', 1)
            result[key.strip()] = value.strip()
    return result


def points(d):
    if re.sub(TOKEN, '', d).strip(' \r\n\t,'):
        raise ValueError('invalid path syntax')
    tokens = TOKEN.findall(d)
    pos, command, result = 0, None, []
    if not tokens or tokens[0] != 'M':
        raise ValueError('path must start with absolute M')
    while pos < len(tokens):
        if tokens[pos].isalpha():
            command = tokens[pos]
            pos += 1
            if command not in ('M', 'L', 'C', 'Z'):
                raise ValueError('fit supports only absolute M/L/C/Z')
            if command == 'Z':
                command = None
                continue
            if pos == len(tokens) or tokens[pos].isalpha():
                raise ValueError('missing command coordinates')
        if command is None:
            raise ValueError('coordinates without command')
        count = 6 if command == 'C' else 2
        values = tokens[pos:pos + count]
        if len(values) != count:
            raise ValueError('incomplete coordinates')
        values = [float(v) for v in values]
        if not all(math.isfinite(v) for v in values):
            raise ValueError('nonfinite coordinates')
        result.extend(zip(values[::2], values[1::2]))
        pos += count
    return result


def analyze(svg, fit=False):
    coordinates, padding, invisible, paths, groups = [], 0, 0, 0, 0
    def visit(e, inherited):
        nonlocal padding, invisible, paths, groups
        if fit:
            if e.tag not in {SVG + n for n in ('svg', 'g', 'path', 'title', 'desc')}:
                raise ValueError('unsupported fit element')
            if e is not svg and e.tag == SVG + 'svg':
                raise ValueError('nested SVG unsupported for fit')
            allowed = {'id', 'd', 'version', 'width', 'height', 'viewBox', 'style',
                       'fill', 'stroke', 'stroke-width', 'stroke-miterlimit',
                       'stroke-linecap', 'stroke-linejoin', 'stroke-dasharray',
                       'stroke-dashoffset', 'fill-rule', 'opacity', 'fill-opacity', 'stroke-opacity'}
            if any(k not in allowed for k in e.attrib):
                raise ValueError('transforms/CSS/effects unsupported for fit')
        s = style(e, inherited)
        if fit and any(k not in {'fill', 'stroke', 'stroke-width', 'stroke-miterlimit',
                                 'stroke-linecap', 'stroke-linejoin', 'stroke-dasharray',
                                 'stroke-dashoffset', 'fill-rule', 'opacity', 'fill-opacity',
                                 'stroke-opacity'} for k in s):
            raise ValueError('unsupported style for fit')
        if e.tag == SVG + 'g':
            groups += 1
        if e.tag == SVG + 'path':
            paths += 1
            if s.get('fill', 'black') == 'none' and s.get('stroke', 'none') == 'none':
                invisible += 1
            if fit:
                coordinates.extend(points(e.get('d', '')))
                if s.get('stroke', 'none') != 'none':
                    width = float(s.get('stroke-width', '1'))
                    miter = float(s.get('stroke-miterlimit', '4'))
                    if not math.isfinite(width * miter) or width < 0 or miter < 1:
                        raise ValueError('invalid stroke geometry')
                    padding = max(padding, width * miter)
        for child in e:
            visit(child, s)
    visit(svg, {})
    return coordinates, padding, {'paths': paths, 'groups_not_source_layers': groups,
                                 'unpainted_paths': invisible}


def extract(source, out, fit=False, margin=10):
    if not math.isfinite(margin) or margin < 0:
        raise ValueError('margin must be finite and nonnegative')
    before = digest(source)
    root = read_xml(source)
    svgs = list(root.iter(SVG + 'svg'))
    if not svgs:
        raise ValueError('no namespace-qualified SVG')
    if any(child.tag == SVG + 'svg' for svg in svgs for child in list(svg.iter())[1:]):
        raise ValueError('nested SVG is not a separate page; unsupported')
    prepared = []
    for svg in svgs:
        # Do not send active or externally linked content to a renderer.
        for e in svg.iter():
            if e.tag in (SVG + 'script', SVG + 'foreignObject', SVG + 'style'):
                raise ValueError('active/CSS SVG content unsupported')
            if any(k.rsplit('}', 1)[-1].startswith('on') or k.rsplit('}', 1)[-1] == 'href'
                   or 'url(' in v.lower() for k, v in e.attrib.items()):
                raise ValueError('SVG links/events/URL paint unsupported')
        original = dict(svg.attrib)
        coords, pad, stats = analyze(svg, fit)
        if fit:
            if not coords:
                raise ValueError('no artwork coordinates')
            vb = [float(v) for v in original.get('viewBox', '').replace(',', ' ').split()]
            if len(vb) != 4 or not all(math.isfinite(v) for v in vb) or min(vb[2:]) <= 0:
                raise ValueError('valid original viewBox required')
            xs, ys = zip(*coords)
            bounds = [min(xs)-pad-margin, min(ys)-pad-margin,
                      max(xs)-min(xs)+2*(pad+margin), max(ys)-min(ys)+2*(pad+margin)]
            if not all(math.isfinite(v) for v in bounds) or min(bounds[2:]) <= 0:
                raise ValueError('degenerate artwork bounds')
            for axis, index in (('width', 2), ('height', 3)):
                match = re.fullmatch('(' + NUMBER + r')(in|mm|cm|pt|pc|px)?', original.get(axis, ''))
                if not match or not math.isfinite(float(match[1])) or float(match[1]) <= 0:
                    raise ValueError('absolute original dimensions required')
                svg.set(axis, f'{float(match[1])*bounds[index]/vb[index]:.10g}{match[2] or ""}')
            svg.set('viewBox', ' '.join(f'{v:.10g}' for v in bounds))
        prepared.append((ET.tostring(svg, encoding='utf-8', xml_declaration=True),
                         {'original_page': original, 'output_page': dict(svg.attrib), **stats}))
    if digest(source) != before:
        raise ValueError('source changed during extraction')
    Path(out).mkdir(parents=True, exist_ok=False)
    reports = []
    for i, (data, stats) in enumerate(prepared, 1):
        name = f'candidate-{i}.svg'
        (Path(out)/name).write_bytes(data)
        reports.append({'file': name, 'sha256': hashlib.sha256(data).hexdigest(), **stats})
    report = {'status': 'pending_visual_qa', 'source_sha256': before,
              'bounds': 'conservative_control_points_plus_stroke_margin' if fit else 'original_page',
              'outputs': reports}
    (Path(out)/'extraction.json').write_text(json.dumps(report, indent=2), encoding='utf-8')
    return report


def assess(artifact, reference, visual, notes):
    if visual != 'unknown' and (not reference or not notes.strip()):
        raise ValueError('visual decision requires reference file and comparison notes')
    return {'artifact_sha256': digest(artifact),
            'reference_sha256': digest(reference) if reference else None,
            'status': {'fail': 'partial_incomplete', 'unknown': 'pending_visual_qa',
                       'pass': 'visual_match_only'}[visual],
            'visual_review': visual, 'notes': notes,
            'vector_editability': 'unverified', 'source_layers': 'unverified',
            'editable_text': 'unverified', 'print_ready': 'unverified'}


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    subs = parser.add_subparsers(dest='action', required=True)
    for name in ('inspect', 'extract'):
        sub = subs.add_parser(name)
        sub.add_argument('source', type=Path)
        sub.add_argument('out', type=Path, help='new directory; existing paths refused')
        if name == 'extract':
            sub.add_argument('--fit-artwork', action='store_true')
            sub.add_argument('--margin', type=float, default=10, help='SVG user units')
    sub = subs.add_parser('assess')
    sub.add_argument('artifact', type=Path)
    sub.add_argument('--reference', type=Path)
    sub.add_argument('--visual', choices=('pass', 'fail', 'unknown'), default='unknown')
    sub.add_argument('--notes', default='')
    args = parser.parse_args()
    try:
        if args.action == 'inspect':
            result = inspect(args.source, args.out)
        elif args.action == 'extract':
            result = extract(args.source, args.out, args.fit_artwork, args.margin)
        else:
            result = assess(args.artifact, args.reference, args.visual, args.notes)
        print(json.dumps(result, indent=2))
        return 2 if result['status'] == 'partial_incomplete' else 0
    except (ValueError, OSError, ET.ParseError, expat.ExpatError, zipfile.BadZipFile) as error:
        print(json.dumps({'status': 'failed', 'error': str(error)}), file=sys.stderr)
        return 1


if __name__ == '__main__':
    sys.exit(main())
