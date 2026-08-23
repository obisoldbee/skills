import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import apply_browser_result_journal as apply_journal
import build_browser_followup_inputs as followup
import build_inventory_download_manifest as inventory_builder
import manifest_contract as contract
import rebuild_manifest


def inventory_text() -> str:
    return """# Frozen

| row_id | title | doi | pmid | pmcid | final_status |
|---|---|---|---|---|---|
| R1 | First | 10.1000/one |  |  |  |
|  |  | 10.1000/two |  |  |  |
| R3 | No stable id |  |  |  |  |
| R4 | Do not cite | 10.1000/four |  |  | do_not_cite |
| R5 | Repeated | 10.1000/one |  |  |  |
"""


def pdf_bytes(
    size: int = contract.PDF_MIN_BYTES + 1,
    *,
    identifier: str = "DOI: 10.1000/one",
    title: str = "",
) -> bytes:
    metadata = f"\n{identifier}\n".encode("ascii") if identifier else b"\n"
    if title:
        metadata += (
            f"1 0 obj\n<< /Title ({title}) >>\nendobj\n"
            "trailer\n<< /Info 1 0 R >>\n"
        ).encode("utf-8")
    if len(metadata) + 4 > size:
        raise ValueError("fixture size is too small")
    return b"%PDF" + metadata + b"x" * (size - 4 - len(metadata))


class ManifestV2ContractTest(unittest.TestCase):
    def test_inventory_preserves_every_row_and_lineage(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "inventory.md"
            source.write_text(inventory_text(), encoding="utf-8")
            manifest = inventory_builder.build_manifest(source, root)

        self.assertEqual(5, manifest["inventory"]["row_count"])
        self.assertEqual(5, len(manifest["inventory"]["row_ids"]))
        self.assertEqual(5, len(set(manifest["inventory"]["row_ids"])))
        self.assertEqual("", manifest["rows"][1]["source_row_id"])
        self.assertEqual("unverified_citation", manifest["rows"][2]["status"])
        self.assertEqual("excluded_do_not_cite", manifest["rows"][3]["disposition"])
        self.assertEqual("R1", manifest["rows"][4]["duplicate_of"])
        self.assertIn("line", manifest["rows"][0]["source_coordinate"])

    def test_pdf_gate_is_strict_and_identity_bound(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            row = {"row_id": "R1", "doi": "10.1000/one", "pmid": "", "pmcid": "", "title": ""}
            exact = root / "R1__10_1000_one.pdf"
            exact.write_bytes(pdf_bytes(contract.PDF_MIN_BYTES))
            receipt = contract.verify_pdf(exact, root, row, identity_match_method="filename_identifier", identity_match_evidence=exact.name)
            self.assertEqual("pdf_not_larger_than_5120_bytes", receipt["failure_reason"])
            exact.write_bytes(pdf_bytes(identifier=""))
            receipt = contract.verify_pdf(exact, root, row, identity_match_method=None, identity_match_evidence=None)
            self.assertEqual("identity_needs_manual_review", receipt["failure_reason"])
            receipt = contract.verify_pdf(exact, root, row, identity_match_method="filename_identifier", identity_match_evidence=exact.name)
            self.assertFalse(receipt["validated"])
            exact.write_bytes(pdf_bytes())
            receipt = contract.verify_pdf(exact, root, row, identity_match_method="filename_identifier", identity_match_evidence=exact.name)
            self.assertTrue(receipt["validated"])
            self.assertEqual("pdf_bytes_doi", receipt["identity_match"]["method"])
            self.assertEqual(contract.PDF_MIN_BYTES + 1, receipt["bytes"])

    def test_pdf_gate_rejects_path_escape(self) -> None:
        with tempfile.TemporaryDirectory() as temporary, tempfile.TemporaryDirectory() as outside:
            root = Path(temporary)
            path = Path(outside) / "10_1000_one.pdf"
            path.write_bytes(pdf_bytes(identifier=""))
            row = {"row_id": "R1", "doi": "10.1000/one"}
            receipt = contract.verify_pdf(path, root, row, identity_match_method="filename_identifier", identity_match_evidence=path.name)
        self.assertEqual("path_escape", receipt["failure_reason"])

    def test_manifest_rejects_status_substrings_and_dual_status(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "inventory.md"
            source.write_text(inventory_text(), encoding="utf-8")
            manifest = inventory_builder.build_manifest(source, root)
            manifest["rows"][0]["status"] = "not_downloaded"
            with self.assertRaisesRegex(ValueError, "invalid exact status"):
                contract.validate_manifest(manifest, output_root=root)
            manifest["rows"][0]["status"] = "pending"
            manifest["rows"][0]["download_status"] = "downloaded"
            with self.assertRaisesRegex(ValueError, "dual status"):
                contract.validate_manifest(manifest, output_root=root)
            del manifest["rows"][0]["download_status"]
            manifest["rows"][0]["attempts"] = [{"route": "doi_browser"}]
            with self.assertRaisesRegex(ValueError, "browser attempt lacks attempt_id"):
                contract.validate_manifest(manifest, output_root=root)

    def test_pubmed_followup_covers_all_unchecked_pmid_variants(self) -> None:
        cases = [
            {"status": "failed", "pmid": "1", "pmcid": "", "doi": ""},
            {"status": "paywalled", "pmid": "2", "pmcid": "", "doi": ""},
            {"status": "failed", "pmid": "3", "pmcid": "", "doi": "10.1000/x"},
        ]
        for row in cases:
            row["pubmed_full_text_checked"] = False
            self.assertTrue(followup.should_follow(row, set()))
            row["pubmed_full_text_checked"] = True
            self.assertFalse(followup.should_follow(row, set()))

    def test_followup_does_not_emit_an_already_terminal_browser_route(self) -> None:
        row = {
            "status": "failed",
            "disposition": "eligible",
            "doi": "10.1000/x",
            "pmid": "3",
            "pmcid": "",
            "pubmed_full_text_checked": True,
            "attempts": [{"route": "doi_browser", "outcome": "failed"}],
        }
        self.assertFalse(followup.should_follow(row, followup.DEFAULT_FOLLOWUP_STATUSES))
        self.assertFalse(
            followup.doi_followup_required(row, followup.DEFAULT_FOLLOWUP_STATUSES)
        )
        row["attempts"] = []
        self.assertTrue(followup.should_follow(row, followup.DEFAULT_FOLLOWUP_STATUSES))
        self.assertTrue(
            followup.doi_followup_required(row, followup.DEFAULT_FOLLOWUP_STATUSES)
        )

    def test_rebuild_does_not_fabricate_download_timestamp(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "inventory.md"
            source.write_text("| row_id | title | doi |\n|---|---|---|\n| R1 | First | 10.1000/one |\n", encoding="utf-8")
            manifest = inventory_builder.build_manifest(source, root)
            papers = root / "papers"
            papers.mkdir()
            (papers / "R1__10_1000_one.pdf").write_bytes(pdf_bytes())
            rebuilt, evidence = rebuild_manifest.reconcile_manifest(manifest, root, papers)
        self.assertEqual("downloaded", rebuilt["rows"][0]["status"])
        self.assertNotIn("downloaded_at", rebuilt["rows"][0])
        self.assertIsNotNone(rebuilt["reconciled_at"])
        self.assertEqual(evidence["actual_pdf_files"], evidence["assigned_pdf_files"])

    def test_collection_readback_rejects_tamper_and_extra(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "inventory.md"
            source.write_text("| row_id | title | doi |\n|---|---|---|\n| R1 | First | 10.1000/one |\n", encoding="utf-8")
            manifest = inventory_builder.build_manifest(source, root)
            papers = root / "papers"
            papers.mkdir()
            path = papers / "R1__10_1000_one.pdf"
            path.write_bytes(pdf_bytes())
            receipt = contract.verify_pdf(path, root, manifest["rows"][0], identity_match_method="filename_identifier", identity_match_evidence=path.name)
            manifest["rows"][0].update({"status": "downloaded", "pdf": receipt})
            self.assertEqual([path.name], contract.verify_downloaded_collection(manifest, root)["actual_pdf_files"])
            path.write_bytes(pdf_bytes(contract.PDF_MIN_BYTES + 2))
            with self.assertRaisesRegex(ValueError, "pdf_receipt_mismatch"):
                contract.verify_downloaded_collection(manifest, root)
            path.write_bytes(pdf_bytes())
            (papers / "extra.pdf").write_bytes(pdf_bytes())
            with self.assertRaisesRegex(ValueError, "extra_pdf"):
                contract.verify_downloaded_collection(manifest, root)

    def test_identity_review_candidate_is_manifest_bound_not_extra(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "inventory.md"
            source.write_text("| row_id | title | doi |\n|---|---|---|\n| R1 | First | 10.1000/one |\n", encoding="utf-8")
            manifest = inventory_builder.build_manifest(source, root)
            papers = root / "papers"
            papers.mkdir()
            path = papers / "candidate.pdf"
            path.write_bytes(pdf_bytes(identifier=""))
            receipt = contract.verify_pdf(
                path, root, manifest["rows"][0],
                identity_match_method=None, identity_match_evidence=None,
            )
            self.assertEqual("identity_needs_manual_review", receipt["failure_reason"])
            manifest["rows"][0].update(
                {"status": "needs_manual_review", "failure_reason": receipt["failure_reason"], "pdf": receipt}
            )
            disk = contract.verify_downloaded_collection(manifest, root)
            self.assertEqual([path.name], disk["actual_pdf_files"])

    def test_browser_journal_is_bound_and_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "inventory.md"
            source.write_text("| row_id | title | doi |\n|---|---|---|\n| R1 | First | 10.1000/one |\n", encoding="utf-8")
            manifest = inventory_builder.build_manifest(source, root)
            path = root / "papers" / "R1__10_1000_one.pdf"
            path.parent.mkdir()
            path.write_bytes(pdf_bytes())
            identity = contract.canonical_identity(manifest["rows"][0])
            attempt = {
                "attempt_id": "A1", "row_id": "R1", "identity": identity,
                "outcome": "downloaded", "pdf_path": "papers/R1__10_1000_one.pdf",
                "identity_match_method": "filename_identifier", "identity_match_evidence": path.name,
            }
            journal = {"schema": contract.JOURNAL_SCHEMA, "inventory_sha256": manifest["inventory"]["sha256"], "rows": [{"row_id": "R1", "identity": identity, "attempts": [attempt]}]}
            self.assertEqual(1, apply_journal.apply_journal(manifest, journal, root))
            self.assertEqual("downloaded", manifest["rows"][0]["status"])
            self.assertEqual(0, apply_journal.apply_journal(manifest, journal, root))
            journal["rows"][0]["row_id"] = "ORPHAN"
            journal["rows"][0]["attempts"] = []
            with self.assertRaisesRegex(ValueError, "orphan"):
                apply_journal.apply_journal(manifest, journal, root)

    def test_failed_browser_attempt_does_not_downgrade_downloaded_row(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "inventory.md"
            source.write_text("| row_id | title | doi |\n|---|---|---|\n| R1 | First | 10.1000/one |\n", encoding="utf-8")
            manifest = inventory_builder.build_manifest(source, root)
            path = root / "papers" / "R1__10_1000_one.pdf"
            path.parent.mkdir()
            path.write_bytes(pdf_bytes())
            receipt = contract.verify_pdf(path, root, manifest["rows"][0], identity_match_method="filename_identifier", identity_match_evidence=path.name)
            manifest["rows"][0].update({"status": "downloaded", "pdf": receipt})
            identity = contract.canonical_identity(manifest["rows"][0])
            attempt = {
                "attempt_id": "A-failed", "row_id": "R1", "identity": identity,
                "outcome": "failed", "failure_reason": "later_route_failed",
            }
            journal = {"schema": contract.JOURNAL_SCHEMA, "inventory_sha256": manifest["inventory"]["sha256"], "rows": [{"row_id": "R1", "identity": identity, "attempts": [attempt]}]}
            self.assertEqual(1, apply_journal.apply_journal(manifest, journal, root))
            self.assertEqual("downloaded", manifest["rows"][0]["status"])
            self.assertEqual("attempt_retained_without_downgrading_existing_pdf_evidence", manifest["rows"][0]["attempts"][-1]["manifest_disposition"])

    def test_final_reports_require_inventory_and_disk_equivalence(self) -> None:
        summary_script = SCRIPT_DIR / "summarize_download_manifest.py"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "inventory.md"
            source.write_text("| row_id | title | doi |\n|---|---|---|\n| R1 | First | 10.1000/one |\n", encoding="utf-8")
            manifest = inventory_builder.build_manifest(source, root)
            papers = root / "papers"
            papers.mkdir()
            path = papers / "R1__10_1000_one.pdf"
            path.write_bytes(pdf_bytes())
            manifest["rows"][0]["pdf"] = contract.verify_pdf(path, root, manifest["rows"][0], identity_match_method="filename_identifier", identity_match_evidence=path.name)
            manifest["rows"][0]["status"] = "downloaded"
            manifest_path = root / "manifest.json"
            contract.save_manifest(manifest_path, manifest, root)
            receipt_path = root / "report-receipt.json"
            proc = subprocess.run([
                sys.executable, str(summary_script), "--manifest", str(manifest_path),
                "--inventory", str(source), "--coverage-out", str(root / "coverage.md"),
                "--failed-out", str(root / "failed.md"), "--receipt-out", str(receipt_path),
                "--output-root", str(root),
            ], capture_output=True, text=True, check=False)
            self.assertEqual(0, proc.returncode, proc.stderr)
            receipt = json.loads(receipt_path.read_text(encoding="utf-8"))
            self.assertEqual(contract.REPORT_RECEIPT_SCHEMA, receipt["schema"])
            self.assertEqual("complete", receipt["completion_state"])
            self.assertEqual("coverage.md", receipt["coverage_report"]["path"])
            self.assertEqual("failed.md", receipt["failed_report"]["path"])
            self.assertEqual(contract.sha256_file(root / "coverage.md"), receipt["coverage_report"]["sha256"])
            self.assertEqual((root / "coverage.md").stat().st_size, receipt["coverage_report"]["bytes"])
            self.assertNotIn("receipt_sha256", receipt)
            source.write_text(source.read_text(encoding="utf-8") + "\n", encoding="utf-8")
            failed = subprocess.run([
                sys.executable, str(summary_script), "--manifest", str(manifest_path),
                "--inventory", str(source), "--coverage-out", str(root / "coverage2.md"),
                "--failed-out", str(root / "failed2.md"), "--receipt-out", str(root / "receipt2.json"),
                "--output-root", str(root),
            ], capture_output=True, text=True, check=False)
            self.assertNotEqual(0, failed.returncode)
            self.assertIn("inventory SHA", failed.stderr)

    def test_all_persistence_modules_import_without_writes(self) -> None:
        scripts = [
            "manifest_contract.py", "build_inventory_download_manifest.py",
            "manifest_pdf_downloader.py", "build_browser_followup_inputs.py",
            "browser_route_executor.py", "apply_browser_result_journal.py",
            "doi_downloader.py", "pmc_downloader.py", "pubmed_downloader.py",
            "pdf_receiver.py", "extract_doi_papers.py", "extract_pmcids.py",
            "rebuild_manifest.py", "summarize_download_manifest.py",
        ]
        with tempfile.TemporaryDirectory() as temporary:
            before = set(Path(temporary).iterdir())
            previous_cwd = Path.cwd()
            try:
                os.chdir(temporary)
                for index, name in enumerate(scripts):
                    spec = importlib.util.spec_from_file_location(f"safe_import_{index}", SCRIPT_DIR / name)
                    module = importlib.util.module_from_spec(spec)
                    assert spec.loader is not None
                    spec.loader.exec_module(module)
            finally:
                os.chdir(previous_cwd)
            self.assertEqual(before, set(Path(temporary).iterdir()))

    def test_package_root_cannot_be_declared_output_root(self) -> None:
        with self.assertRaisesRegex(ValueError, "package/source root"):
            contract.declared_output_root(contract.PACKAGE_ROOT)


if __name__ == "__main__":
    unittest.main()
