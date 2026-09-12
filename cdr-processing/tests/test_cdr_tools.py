import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

SCRIPT = Path(__file__).resolve().parents[1] / 'scripts/cdr_tools.py'
spec = importlib.util.spec_from_file_location('cdr_tools', SCRIPT)
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


class ToolsTest(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.root = Path(self.tmp.name)

    def svg(self, content):
        p = self.root/'input.xhtml'
        p.write_text('<html xmlns="http://www.w3.org/1999/xhtml"><svg xmlns="http://www.w3.org/2000/svg" width="100mm" height="50mm" viewBox="0 0 100 50">'+content+'</svg></html>')
        return p

    def test_fit_scale_and_control_points(self):
        src = self.svg('<path d="M200 -20 C210 -100 220 60 230 0 Z"/>')
        before = m.digest(src)
        r = m.extract(src, self.root/'out', True, 0)
        page = r['outputs'][0]['output_page']
        self.assertEqual(page['viewBox'], '200 -100 30 160')
        self.assertEqual(page['width'], '30mm')
        self.assertEqual(page['height'], '160mm')
        self.assertEqual(m.digest(src), before)
        self.assertEqual(r['status'], 'pending_visual_qa')

    def test_reject_unsupported_without_output(self):
        for content in ['<path d="M0 0 l1 1"/>', '<g transform="translate(1)"><path d="M0 0 L2 2"/></g>', '<rect width="2" height="2"/>', '<path d="M0 0 A1 1 0 0 0 2 2"/>', '<path d="M0 0 L"/>', '<path marker-end="foo" d="M0 0 L1 1"/>']:
            with self.subTest(content=content), self.assertRaises(ValueError):
                m.extract(self.svg(content), self.root/'out', True)
            self.assertFalse((self.root/'out').exists())

    def test_inheritance_invisible_warning(self):
        r = m.extract(self.svg('<g fill="none"><path d="M0 0 L2 2"/><path stroke="red" d="M0 0 L1 1"/></g>'), self.root/'out')
        self.assertEqual(r['outputs'][0]['unpainted_paths'], 1)
        self.assertEqual(r['status'], 'pending_visual_qa')

    def test_partial_cli_not_success(self):
        src = self.svg('<path fill="none" d="M0 0 L1 1"/>')
        cp = subprocess.run([sys.executable, '-B', str(SCRIPT), 'assess', str(src), '--visual', 'fail', '--reference', str(src), '--notes', 'synthetic missing paint'], capture_output=True, text=True)
        self.assertEqual(cp.returncode, 2)
        self.assertEqual(json.loads(cp.stdout)['status'], 'partial_incomplete')
        self.assertEqual(m.assess(src, None, 'unknown', '')['status'], 'pending_visual_qa')
        with self.assertRaises(ValueError):
            m.assess(src, None, 'pass', '')
        self.assertEqual(m.assess(src, src, 'pass', 'synthetic comparison')['print_ready'], 'unverified')

    def test_external_doctype_allowed_entities_rejected(self):
        self.assertEqual(m.xml(b'<!DOCTYPE html SYSTEM "https://invalid.example/a.dtd"><html/>').tag, 'html')
        for data in [b'<!DOCTYPE a [<!ENTITY x SYSTEM "file:///secret">]><a>&x;</a>', '<!DOCTYPE a [<!ENTITY x "abc">]><a>&x;</a>'.encode('utf-16')]:
            with self.assertRaises(ValueError):
                m.xml(data)

    def test_selective_zip_and_no_overwrite(self):
        src = self.root/'synthetic.cdr'
        with zipfile.ZipFile(src, 'w') as z:
            z.writestr('previews/thumbnail.png', b'\x89PNG\r\n\x1a\nsynthetic')
            z.writestr('content/root.dat', b'not extracted')
            z.writestr('META-INF/metadata.xml', '<metadata><NumPages>1</NumPages></metadata>')
        before = m.digest(src)
        r = m.inspect(src, self.root/'out')
        self.assertEqual(r['container'], 'ZIP')
        self.assertFalse((self.root/'out/content').exists())
        self.assertEqual(m.digest(src), before)
        with self.assertRaises(FileExistsError):
            m.inspect(src, self.root/'out')

    def test_zip_traversal_rejected(self):
        src = self.root/'bad.cdr'
        with zipfile.ZipFile(src, 'w') as z:
            z.writestr('../escaped', 'bad')
        with self.assertRaises(ValueError):
            m.inspect(src, self.root/'out')
        self.assertFalse((self.root/'out').exists())

    def test_riff_and_multiple_pages(self):
        src = self.root/'riff.cdr'
        src.write_bytes(b'RIFF1234CDR6')
        self.assertEqual(m.inspect(src, self.root/'inspection')['container'], 'RIFF')
        src = self.svg('<path d="M0 0 L1 1"/>')
        data = src.read_text()
        fragment = data[data.index('<svg '):data.index('</svg>')+6]
        src.write_text(data.replace('</html>', fragment+'</html>'))
        report = m.extract(src, self.root/'pages')
        self.assertEqual(len(report['outputs']), 2)
        self.assertTrue((self.root/'pages/candidate-2.svg').exists())

    def test_nested_svg_not_extra_page(self):
        with self.assertRaises(ValueError):
            m.extract(self.svg('<svg><path d="M0 0 L1 1"/></svg>'), self.root/'out')
        self.assertFalse((self.root/'out').exists())

    def test_external_svg_rejected(self):
        with self.assertRaises(ValueError):
            m.extract(self.svg('<image href="https://invalid.example/x.png"/>'), self.root/'out')


if __name__ == '__main__':
    unittest.main()
