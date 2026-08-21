import argparse
import importlib.util
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "summarize_download_manifest.py"
SPEC = importlib.util.spec_from_file_location("summarize_download_manifest", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


class FailedDownloadLinksTest(unittest.TestCase):
    def test_failed_report_emits_clickable_identifier_and_observed_links(self):
        rows = [
            {
                "row_id": "S001-001",
                "status": "manual_browser_required",
                "doi": "10.1016/j.diabres.2020.108233",
                "pmid": "32497744",
                "pmcid": "PMC7977482",
                "failure_reason": "manual review required",
                "observed_url": "https://example.org/article?id=1",
            }
        ]

        with tempfile.TemporaryDirectory() as tmp:
            output = Path(tmp) / "failed-downloads.md"
            args = argparse.Namespace(failed_out=output)
            MODULE.write_failed(args, rows)
            text = output.read_text(encoding="utf-8")

        self.assertIn("source_links", text)
        self.assertIn("[DOI](https://doi.org/10.1016/j.diabres.2020.108233)", text)
        self.assertIn("[PubMed](https://pubmed.ncbi.nlm.nih.gov/32497744/)", text)
        self.assertIn("[PMC](https://pmc.ncbi.nlm.nih.gov/articles/PMC7977482/)", text)
        self.assertIn("[observed](https://example.org/article?id=1)", text)

    def test_non_http_observed_url_is_not_linked(self):
        links = MODULE.reference_links(
            {"row_id": "S001-002", "status": "failed", "observed_url": "file:///tmp/private"}
        )

        self.assertEqual("", links)


if __name__ == "__main__":
    unittest.main()
