import argparse
import hashlib
import importlib.util
import io
import json
import subprocess
import sys
import tarfile
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "manifest_pdf_downloader.py"
SPEC = importlib.util.spec_from_file_location("manifest_pdf_downloader", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def valid_pdf_bytes() -> bytes:
    return b"%PDF" + b"\nfixture\n" + b"x" * MODULE.PDF_MIN_BYTES


class ManifestPdfDownloaderTest(unittest.TestCase):
    def test_pdf_gate_rejects_html_and_small_pdf(self) -> None:
        self.assertFalse(MODULE.valid_pdf_bytes(b"<html>not a PDF</html>" * 400))
        self.assertFalse(MODULE.valid_pdf_bytes(b"%PDF\nsmall"))
        self.assertTrue(MODULE.valid_pdf_bytes(valid_pdf_bytes()))

    def test_local_doi_match_short_circuits_acquisition(self) -> None:
        payload = valid_pdf_bytes()
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            local_pdf = root / "10-1000_test.pdf"
            local_pdf.write_bytes(payload)
            row = {
                "row_id": "src-001",
                "title": "Fixture",
                "doi": "10.1000/test",
                "pmid": "",
                "pmcid": "",
                "status": "pending",
                "failure_reason": "",
            }
            args = argparse.Namespace(skip_recursive_local_scan=False)

            result = MODULE.process_row(row, args, [root])

        self.assertEqual(result["status"], "already_local_pdf")
        self.assertEqual(result["attempted_routes"], [])
        self.assertEqual(result["file_size_bytes"], len(payload))
        self.assertEqual(result["sha256"], hashlib.sha256(payload).hexdigest())
        self.assertTrue(result["validated"])

    def test_tgz_extraction_accepts_only_valid_pdf_member(self) -> None:
        valid = valid_pdf_bytes()
        buffer = io.BytesIO()
        with tarfile.open(fileobj=buffer, mode="w:gz") as archive:
            invalid_info = tarfile.TarInfo("article/invalid.pdf")
            invalid = b"<html>not pdf</html>"
            invalid_info.size = len(invalid)
            archive.addfile(invalid_info, io.BytesIO(invalid))
            valid_info = tarfile.TarInfo("article/main.pdf")
            valid_info.size = len(valid)
            archive.addfile(valid_info, io.BytesIO(valid))

        extracted, member = MODULE.extract_pdf_from_tgz(buffer.getvalue())

        self.assertEqual(extracted, valid)
        self.assertEqual(member, "article/main.pdf")

    def test_route_urls_are_lawful_declared_sources_only(self) -> None:
        routes = MODULE.route_urls(
            {
                "pmcid": "PMC123",
                "doi": "10.1000/test",
                "pdf_url": "https://example.org/open.pdf",
            }
        )

        self.assertEqual(
            routes,
            [
                ("europepmc_render", "https://europepmc.org/articles/PMC123?pdf=render"),
                ("pmc_pdf", "https://pmc.ncbi.nlm.nih.gov/articles/PMC123/pdf/"),
                ("provided_pdf_url", "https://example.org/open.pdf"),
                ("doi_landing", "https://doi.org/10.1000/test"),
            ],
        )

    def test_cli_rejects_parallel_network_workers_before_acquisition(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            input_path = root / "input.json"
            input_path.write_text(json.dumps([]), encoding="utf-8")
            proc = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    "--input",
                    str(input_path),
                    "--paper-dir",
                    str(root / "papers"),
                    "--manifest-out",
                    str(root / "manifest.json"),
                    "--status-out",
                    str(root / "status.md"),
                    "--workers",
                    "2",
                ],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                check=False,
            )

        self.assertEqual(2, proc.returncode)
        self.assertIn("--workers must be 1", proc.stderr)


if __name__ == "__main__":
    unittest.main()
