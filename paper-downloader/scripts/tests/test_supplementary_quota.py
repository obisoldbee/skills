import json
import subprocess
import tempfile
import sys
import unittest
from pathlib import Path
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import manifest_contract as contract
import build_inventory_download_manifest as builder
from test_manifest_v2_contract import pdf_bytes

class SupplementaryQuotaTests(unittest.TestCase):
    def rows(self, count):
        return [{"doi": f"10.1000/{i}", "status": "downloaded", "pdf": {"validated": True}}
                for i in range(count)]

    def test_extra_counterevidence_does_not_fill_target_shortfall(self):
        rows = self.rows(50)
        rows[-1].update(collection_role="supplementary", collection_role_reason="counterevidence")
        counts = contract.quota_counts(rows, 50)
        self.assertEqual((49, 1, 1, False), (counts["target_downloaded"], counts["supplementary_downloaded"], counts["target_remaining"], counts["target_quota_met"]))
        rows.append({"doi": "10.1000/another", "status": "downloaded", "pdf": {"validated": True}})
        counts = contract.quota_counts(rows, 50)
        self.assertEqual((50, 1, True), (counts["target_downloaded"], counts["supplementary_downloaded"], counts["target_quota_met"]))

    def test_role_is_frozen_and_supplement_requires_reason(self):
        rows = self.rows(1)
        previous = contract.rows_binding_sha256(rows)
        rows[0]["collection_role"] = "supplementary"
        self.assertNotEqual(previous, contract.rows_binding_sha256(rows))
        with self.assertRaises(ValueError):
            contract.quota_counts(rows, 50)

    def test_reference_doi_is_not_primary_identity(self):
        row = {"doi": "10.1000/target", "title": "Target paper"}
        raw = b"%PDF References DOI: 10.1000/target"
        self.assertFalse(contract._identity_matches(row, raw)[0])
        conflict = (b"%PDF 1 0 obj << /Title (Another paper) /DOI (10.1000/target) >> "
                    b"endobj trailer << /Info 1 0 R >>")
        self.assertFalse(contract._identity_matches(row, conflict)[0])
        matching = conflict.replace(b"Another paper", b"Target paper")
        self.assertTrue(contract._identity_matches(row, matching)[0])

    def test_duplicate_supplement_and_unverified_candidate_do_not_count(self):
        rows = self.rows(1)
        rows.append(dict(rows[0], collection_role="supplementary", collection_role_reason="critique"))
        rows.append({"doi": "10.1000/candidate", "status": "needs_manual_review", "collection_role": "supplementary", "collection_role_reason": "identity pending"})
        self.assertEqual(0, contract.quota_counts(rows, 1)["supplementary_downloaded"])

    def test_persisted_inventory_and_reports_keep_quota_separate(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source = root / "inventory.csv"
            source.write_text("row_id,title,doi,collection_role,collection_role_reason\n"
                              "T1,Target,10.1000/one,target,\n"
                              "S1,Counterevidence,10.1000/two,supplementary,counterevidence\n")
            manifest = builder.build_manifest(source, root, target_count=2)
            (root / "papers").mkdir()
            for row in manifest["rows"]:
                path = root / "papers" / (row["row_id"] + ".pdf")
                path.write_bytes(pdf_bytes(identifier="DOI: " + row["doi"]))
                row["pdf"] = contract.verify_pdf(path, root, row, identity_match_method=None, identity_match_evidence=None)
                row["status"] = "downloaded"
            contract.save_manifest(root / "manifest.json", manifest, root)
            command = [sys.executable, "-B", str(Path(__file__).resolve().parents[1] / "summarize_download_manifest.py"),
                "--manifest", str(root / "manifest.json"), "--inventory", str(source),
                "--coverage-out", str(root / "coverage.md"), "--failed-out", str(root / "failed.md"),
                "--receipt-out", str(root / "receipt.json"), "--output-root", str(root)]
            process = subprocess.run(command, text=True, capture_output=True)
            self.assertEqual(0, process.returncode, process.stderr)
            receipt = json.loads((root / "receipt.json").read_text())
            self.assertEqual(1, receipt["quota"]["target_downloaded"])
            self.assertEqual(1, receipt["quota"]["supplementary_downloaded"])
            self.assertFalse(receipt["quota"]["target_quota_met"])
            self.assertIn("counterevidence", (root / "coverage.md").read_text())
            manifest["rows"][1]["collection_role"] = "target"
            with self.assertRaisesRegex(ValueError, "binding"):
                contract.validate_manifest(manifest, output_root=root)
