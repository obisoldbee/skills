import argparse
import copy
import json
import subprocess
import sys
import tempfile
import types
import unittest
from pathlib import Path
from unittest import mock


SCRIPT_DIR = Path(__file__).resolve().parents[1]
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

import apply_browser_result_journal as apply_journal
import browser_route_executor
import build_inventory_download_manifest as inventory_builder
import manifest_contract as contract
import manifest_pdf_downloader
import pdf_receiver
import rebuild_manifest
import summarize_download_manifest


def inventory_one(identifier_column: str = "doi", identifier: str = "10.1000/one") -> str:
    return (
        f"| row_id | title | {identifier_column} |\n"
        f"|---|---|---|\n"
        f"| R1 | First Paper | {identifier} |\n"
    )


def pdf_bytes(identifier: str = "DOI: 10.1000/one", title: str = "") -> bytes:
    metadata = f"\n{identifier}\n".encode("ascii") if identifier else b"\n"
    if title:
        metadata += (
            f"1 0 obj\n<< /Title ({title}) >>\nendobj\n"
            "trailer\n<< /Info 1 0 R >>\n"
        ).encode("utf-8")
    return b"%PDF" + metadata + b"x" * (contract.PDF_MIN_BYTES + 32)


def manifest_and_path(root: Path, text: str | None = None) -> tuple[dict, Path, Path]:
    inventory = root / "inventory.md"
    inventory.write_text(text or inventory_one(), encoding="utf-8")
    manifest = inventory_builder.build_manifest(inventory, root)
    manifest_path = root / "manifest.json"
    contract.save_manifest(manifest_path, manifest, root)
    return manifest, manifest_path, inventory


def journal_for(manifest: dict, manifest_path: Path, attempts: list[dict] | None = None) -> dict:
    row = manifest["rows"][0]
    return {
        "schema": contract.JOURNAL_SCHEMA,
        "manifest_path": "manifest.json",
        "manifest_sha256": contract.sha256_file(manifest_path),
        "inventory_sha256": manifest["inventory"]["sha256"],
        "rows": [
            {
                "row_id": row["row_id"],
                "identity": contract.canonical_identity(row),
                "attempts": list(attempts or []),
            }
        ],
    }


class InventoryAndIdentityHardeningTest(unittest.TestCase):
    def test_markdown_csv_escaped_pipe_and_decorated_identifiers(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            markdown = root / "inventory.md"
            markdown.write_text(
                "row_id | title | doi | pmid | pmcid\n"
                "---|---|---|---|---\n"
                "R1 | Alpha \\| Beta | https://doi.org/10.1000/ONE | PMID: [12345]. | "
                "PMCID: (PMC678);\n",
                encoding="utf-8",
            )
            rows = inventory_builder.build_rows(markdown)
            self.assertEqual(1, len(rows))
            self.assertEqual("Alpha | Beta", rows[0]["title"])
            self.assertEqual("10.1000/one", rows[0]["doi"])
            self.assertEqual("12345", rows[0]["pmid"])
            self.assertEqual("PMC678", rows[0]["pmcid"])

            csv_path = root / "inventory.csv"
            csv_path.write_text(
                'row_id,title,doi,pmid,pmcid\nC1,"Title, With Comma","doi: 10.1000/TWO",'
                '"https://pubmed.ncbi.nlm.nih.gov/77/","PMCID: PMC88"\n',
                encoding="utf-8",
            )
            csv_rows = inventory_builder.build_rows(csv_path)
            self.assertEqual("Title, With Comma", csv_rows[0]["title"])
            self.assertEqual("10.1000/two", csv_rows[0]["doi"])
            self.assertEqual("77", csv_rows[0]["pmid"])
            self.assertEqual("PMC88", csv_rows[0]["pmcid"])

    def test_zero_row_inventory_fails(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "empty.md"
            path.write_text("| row_id | doi |\n|---|---|\n", encoding="utf-8")
            with self.assertRaisesRegex(ValueError, "no parseable data rows"):
                inventory_builder.build_rows(path)

    def test_row_binding_tamper_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest, _manifest_path, _inventory = manifest_and_path(root)
            manifest["rows"][0]["title"] = "silently changed"
            with self.assertRaisesRegex(ValueError, "rows_sha256"):
                contract.validate_manifest(manifest, output_root=root)

    def test_downloaded_row_cannot_self_report_pathless_pdf_evidence(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest, _manifest_path, _inventory = manifest_and_path(root)
            row = manifest["rows"][0]
            row["status"] = "downloaded"
            row["failure_reason"] = ""
            row["pdf"] = {
                "validated": True,
                "path": "",
                "bytes": contract.PDF_MIN_BYTES + 1,
                "sha256": "0" * 64,
                "magic": "%PDF",
                "failure_reason": "",
                "identity_match": {
                    "method": "pdf_bytes_doi",
                    "evidence": "10.1000/one",
                    "matched": True,
                },
            }
            with self.assertRaisesRegex(ValueError, "pathless PDF receipt"):
                contract.validate_manifest(manifest, output_root=root)

    def test_atomic_create_cas_never_overwrites_existing_target(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            target = Path(temporary) / "target.pdf"
            target.write_bytes(b"existing")
            with self.assertRaisesRegex(ValueError, "target CAS failed"):
                contract.atomic_create_bytes(target, b"replacement")
            self.assertEqual(b"existing", target.read_bytes())

    def test_package_ancestor_is_not_an_output_root(self) -> None:
        with self.assertRaisesRegex(ValueError, "ancestors"):
            contract.declared_output_root(contract.PACKAGE_ROOT.parent)

    def test_inventory_builder_rejects_input_output_alias_without_overwrite(self) -> None:
        script = SCRIPT_DIR / "build_inventory_download_manifest.py"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            inventory = root / "inventory.md"
            inventory.write_text(inventory_one(), encoding="utf-8")
            before = inventory.read_bytes()
            result = subprocess.run(
                [
                    sys.executable, str(script), "--input", str(inventory),
                    "--output", str(inventory), "--output-root", str(root),
                    "--format", "markdown",
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("path alias", result.stderr)
            self.assertEqual(before, inventory.read_bytes())

    def test_actual_pdf_identity_has_strict_boundary_or_exact_title(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            row = {"row_id": "R1", "doi": "10.1000/one", "pmid": "", "pmcid": "", "title": "Exact Title"}
            path = root / "10.1000_one.pdf"
            path.write_bytes(pdf_bytes("DOI: 10.1000/one-more"))
            receipt = contract.verify_pdf(
                path, root, row,
                identity_match_method="route_and_header_claim",
                identity_match_evidence="10.1000/one",
            )
            self.assertEqual("identity_needs_manual_review", receipt["failure_reason"])
            path.write_bytes(
                b"%PDF\nstream\n/Title (Exact Title)\nendstream\n"
                + b"x" * (contract.PDF_MIN_BYTES + 32)
            )
            receipt = contract.verify_pdf(
                path, root, row, identity_match_method=None, identity_match_evidence=None
            )
            self.assertEqual("identity_needs_manual_review", receipt["failure_reason"])
            path.write_bytes(pdf_bytes("", "Exact Title"))
            receipt = contract.verify_pdf(path, root, row, identity_match_method=None, identity_match_evidence=None)
            self.assertTrue(receipt["validated"])
            self.assertEqual("pdf_title_metadata", receipt["identity_match"]["method"])


class FirstPassAndRebuildHardeningTest(unittest.TestCase):
    @staticmethod
    def args(root: Path) -> argparse.Namespace:
        return argparse.Namespace(
            output_root=root,
            paper_dir=root / "papers",
            skip_recursive_local_scan=False,
            skip_doi_landing=False,
            skip_oa_package=True,
            timeout=1,
            europepmc_timeout=1,
        )

    def test_first_pass_skips_excluded_and_resumes_recorded_pdf_without_network(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            args = self.args(root)
            excluded = {
                "row_id": "X", "doi": "10.1000/x", "pmid": "", "pmcid": "",
                "disposition": "excluded_do_not_cite", "status": "needs_manual_review",
                "failure_reason": "excluded_do_not_cite", "attempts": [],
                "pdf": contract.empty_pdf_receipt(),
            }
            with mock.patch.object(manifest_pdf_downloader, "curl_bytes", side_effect=AssertionError("network called")):
                excluded_result = manifest_pdf_downloader.process_row(excluded, args, [])
            self.assertEqual("excluded_do_not_cite", excluded_result["disposition"])
            self.assertEqual("needs_manual_review", excluded_result["status"])
            self.assertEqual([], excluded_result["attempts"])

            papers = root / "papers"
            papers.mkdir()
            path = papers / "renamed.PDF"
            path.write_bytes(pdf_bytes())
            row = {
                "row_id": "R1", "title": "First", "doi": "10.1000/one", "pmid": "", "pmcid": "",
                "disposition": "eligible", "status": "downloaded", "failure_reason": "stale",
                "attempts": [], "pubmed_followup_required": True, "pmcid_followup_required": True,
            }
            row["pdf"] = contract.verify_pdf(path, root, row, identity_match_method="header", identity_match_evidence="claim")
            with mock.patch.object(manifest_pdf_downloader, "curl_bytes", side_effect=AssertionError("network called")):
                result = manifest_pdf_downloader.process_row(row, args, [papers])
            self.assertEqual("downloaded", result["status"])
            self.assertFalse(result["pubmed_followup_required"])
            self.assertFalse(result["pmcid_followup_required"])

    def test_html_first_pass_is_queued_not_terminal_failed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            row = {
                "row_id": "R1", "title": "First", "doi": "10.1000/one", "pmid": "", "pmcid": "",
                "disposition": "eligible", "status": "pending", "failure_reason": "", "attempts": [],
                "pdf": contract.empty_pdf_receipt(),
            }
            with mock.patch.object(
                manifest_pdf_downloader,
                "curl_bytes",
                return_value=(b"<html>landing</html>" * 400, "https://doi.org/10.1000/one", "text/html http=200"),
            ):
                result = manifest_pdf_downloader.process_row(row, self.args(root), [])
            self.assertEqual("browser_required", result["status"])
            self.assertIn("not_pdf_or_too_small", result["failure_reason"])

    def test_first_pass_rerun_does_not_repeat_network_for_queued_row(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            row = {
                "row_id": "R1", "title": "First", "doi": "10.1000/one", "pmid": "", "pmcid": "",
                "disposition": "eligible", "status": "browser_required",
                "failure_reason": "browser_followup_required_after_first_pass", "attempts": [],
                "pdf": contract.empty_pdf_receipt(),
            }
            with mock.patch.object(manifest_pdf_downloader, "curl_bytes", side_effect=AssertionError("network repeated")):
                result = manifest_pdf_downloader.process_row(row, self.args(root), [])
            self.assertEqual("browser_required", result["status"])
            self.assertEqual([], result["attempts"])

    def test_first_pass_binds_unrecorded_pdf_already_in_paper_dir_in_place(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            papers = root / "papers"
            papers.mkdir()
            existing = papers / "cached_10-1000-one.PDF"
            existing.write_bytes(pdf_bytes())
            row = {
                "row_id": "R1", "title": "First", "doi": "10.1000/one", "pmid": "", "pmcid": "",
                "disposition": "eligible", "status": "pending", "failure_reason": "", "attempts": [],
                "pdf": contract.empty_pdf_receipt(),
            }
            with mock.patch.object(manifest_pdf_downloader, "curl_bytes", side_effect=AssertionError("network called")):
                result = manifest_pdf_downloader.process_row(row, self.args(root), [papers])
            self.assertEqual("downloaded", result["status"])
            self.assertEqual("papers/cached_10-1000-one.PDF", result["pdf"]["path"])
            self.assertEqual([existing.name], contract.pdf_files(papers))

    def test_rebuild_finds_renamed_uppercase_pdf_and_preserves_excluded_row(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "inventory.md"
            source.write_text(
                "| row_id | title | doi | final_status |\n|---|---|---|---|\n"
                "| R1 | First | 10.1000/one | |\n| X | Excluded | 10.1000/x | do_not_cite |\n",
                encoding="utf-8",
            )
            manifest = inventory_builder.build_manifest(source, root)
            papers = root / "papers"
            papers.mkdir()
            (papers / "totally-renamed.PDF").write_bytes(pdf_bytes())
            rebuilt, evidence = rebuild_manifest.reconcile_manifest(manifest, root, papers)
            self.assertEqual("downloaded", rebuilt["rows"][0]["status"])
            self.assertEqual("excluded_do_not_cite", rebuilt["rows"][1]["disposition"])
            self.assertEqual("needs_manual_review", rebuilt["rows"][1]["status"])
            self.assertEqual(["papers/totally-renamed.PDF"], evidence["assigned_pdf_files"])

    def test_rebuild_rejects_one_pdf_claimed_by_two_rows(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "inventory.md"
            source.write_text(
                "| row_id | title | doi |\n|---|---|---|\n"
                "| R1 | One | 10.1000/one |\n| R2 | Two | 10.1000/two |\n",
                encoding="utf-8",
            )
            manifest = inventory_builder.build_manifest(source, root)
            papers = root / "papers"
            papers.mkdir()
            (papers / "both.pdf").write_bytes(pdf_bytes("DOI: 10.1000/one DOI: 10.1000/two"))
            with self.assertRaisesRegex(ValueError, "bijection"):
                rebuild_manifest.reconcile_manifest(manifest, root, papers)

    def test_manifest_mutators_reject_source_output_alias_before_writing(self) -> None:
        scripts = {
            "first_pass": SCRIPT_DIR / "manifest_pdf_downloader.py",
            "journal_apply": SCRIPT_DIR / "apply_browser_result_journal.py",
            "rebuild": SCRIPT_DIR / "rebuild_manifest.py",
        }
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest, manifest_path, _inventory = manifest_and_path(root)
            journal_path = root / "journal.json"
            contract.atomic_write_json(journal_path, journal_for(manifest, manifest_path))
            before = manifest_path.read_bytes()
            commands = {
                "first_pass": [
                    sys.executable, str(scripts["first_pass"]),
                    "--input", str(manifest_path),
                    "--output-root", str(root),
                    "--paper-dir", "papers",
                    "--manifest-out", str(manifest_path),
                    "--status-out", "status.md",
                ],
                "journal_apply": [
                    sys.executable, str(scripts["journal_apply"]),
                    "--manifest", str(manifest_path),
                    "--journal", str(journal_path),
                    "--manifest-out", str(manifest_path),
                    "--receipt-out", "apply-receipt.json",
                    "--output-root", str(root),
                ],
                "rebuild": [
                    sys.executable, str(scripts["rebuild"]),
                    "--manifest", str(manifest_path),
                    "--manifest-out", str(manifest_path),
                    "--paper-dir", "papers",
                    "--receipt-out", "rebuild-receipt.json",
                    "--output-root", str(root),
                ],
            }
            for name, command in commands.items():
                with self.subTest(name=name):
                    result = subprocess.run(command, capture_output=True, text=True, check=False)
                    self.assertNotEqual(0, result.returncode)
                    self.assertIn("path alias", result.stderr)
                    self.assertEqual(before, manifest_path.read_bytes())
            self.assertFalse((root / "status.md").exists())
            self.assertFalse((root / "apply-receipt.json").exists())
            self.assertFalse((root / "rebuild-receipt.json").exists())


class JournalReceiverAndFinalGateTest(unittest.TestCase):
    def test_terminal_status_requires_browser_and_identifier_route_evidence(self) -> None:
        identity = {"kind": "pmcid", "value": "PMC456"}
        row = {
            "row_id": "R1", "status": "access_blocked", "disposition": "eligible",
            "pmid": "123", "pmcid": "PMC456", "failure_reason": "raw_http_403",
            "attempts": [], "pubmed_followup_required": False,
            "pmcid_followup_required": False,
        }
        blockers = summarize_download_manifest.completion_blockers([row])
        self.assertIn(
            "R1:terminal_status_without_browser_attempt:access_blocked", blockers
        )
        self.assertIn(
            "R1:terminal_status_without_pubmed_followup_evidence", blockers
        )
        self.assertIn(
            "R1:terminal_status_without_pmcid_followup_evidence", blockers
        )
        row["attempts"] = [
            {
                "attempt_id": "PUBMED-1", "row_id": "R1", "identity": identity,
                "route": "pubmed_browser", "outcome": "access_blocked",
                "pubmed_full_text_checked": True,
                "observed_url": "https://example.invalid/blocked",
            },
            {
                "attempt_id": "PMC-1", "row_id": "R1", "identity": identity,
                "route": "pmc_browser", "outcome": "access_blocked",
                "pmcid_route_checked": True,
            },
        ]
        self.assertEqual([], summarize_download_manifest.completion_blockers([row]))

    def test_doi_browser_terminal_failure_requires_observable_evidence(self) -> None:
        row = {
            "row_id": "R1", "status": "failed", "disposition": "eligible",
            "doi": "10.1000/one", "failure_reason": "observed failure",
            "attempts": [{
                "attempt_id": "DOI-1", "row_id": "R1",
                "identity": {"kind": "doi", "value": "10.1000/one"},
                "route": "doi_browser", "outcome": "failed",
            }],
            "pubmed_followup_required": False, "pmcid_followup_required": False,
        }
        self.assertIn(
            "R1:browser_failure_observable_evidence_missing",
            summarize_download_manifest.completion_blockers([row]),
        )

    def test_changed_attempt_content_and_cross_row_collision_fail(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest, manifest_path, _inventory = manifest_and_path(root)
            row = manifest["rows"][0]
            identity = contract.canonical_identity(row)
            attempt = {
                "attempt_id": "A1", "row_id": "R1", "identity": identity,
                "outcome": "failed", "failure_reason": "first",
            }
            journal = journal_for(manifest, manifest_path, [attempt])
            self.assertEqual(1, apply_journal.apply_journal(manifest, journal, root))
            changed = copy.deepcopy(journal)
            changed["rows"][0]["attempts"][0]["failure_reason"] = "changed"
            with self.assertRaisesRegex(ValueError, "content changed"):
                apply_journal.apply_journal(manifest, changed, root)

            second = copy.deepcopy(journal["rows"][0])
            second["row_id"] = "R2"
            colliding = copy.deepcopy(journal)
            colliding["rows"].append(second)
            with self.assertRaisesRegex(ValueError, "global journal attempt_id collision"):
                apply_journal.apply_journal(manifest, colliding, root)

    def test_executor_and_receiver_reject_stale_journal_before_execution(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest, manifest_path, _inventory = manifest_and_path(root)
            journal = journal_for(manifest, manifest_path)
            journal["manifest_sha256"] = "0" * 64
            journal_path = root / "journal.json"
            contract.atomic_write_json(journal_path, journal)
            with self.assertRaisesRegex(ValueError, "stale browser journal"):
                browser_route_executor.load_bound_row(manifest_path, journal_path, root, "R1")
            with self.assertRaisesRegex(ValueError, "stale browser journal"):
                pdf_receiver.load_state(manifest_path, journal_path, root, root / "papers")
            self.assertFalse((root / "papers").exists())

    def test_executor_and_receiver_reject_unbound_existing_journal_attempt(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest, manifest_path, _inventory = manifest_and_path(root)
            identity = contract.canonical_identity(manifest["rows"][0])
            attempt = {
                "attempt_id": "BAD", "row_id": "OTHER", "identity": identity,
                "outcome": "failed", "failure_reason": "bad binding",
            }
            journal_path = root / "journal.json"
            contract.atomic_write_json(
                journal_path, journal_for(manifest, manifest_path, [attempt])
            )
            with self.assertRaisesRegex(ValueError, "row/identity binding mismatch"):
                browser_route_executor.load_bound_row(
                    manifest_path, journal_path, root, "R1"
                )
            with self.assertRaisesRegex(ValueError, "row/identity binding mismatch"):
                pdf_receiver.load_state(
                    manifest_path, journal_path, root, root / "papers"
                )
            self.assertFalse((root / "papers").exists())

    def test_receiver_preflight_rejects_collision_and_existing_target(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest, manifest_path, _inventory = manifest_and_path(root)
            identity = contract.canonical_identity(manifest["rows"][0])
            old_attempt = {
                "attempt_id": "OLD", "row_id": "R1", "identity": identity,
                "outcome": "failed", "failure_reason": "old",
            }
            journal_path = root / "journal.json"
            contract.atomic_write_json(journal_path, journal_for(manifest, manifest_path, [old_attempt]))
            state = pdf_receiver.load_state(manifest_path, journal_path, root, root / "papers")
            with self.assertRaisesRegex(ValueError, "attempt_id collision"):
                pdf_receiver.preflight_request(state, "R1", "OLD", identity, "new.pdf")
            target = root / "papers" / "exists.pdf"
            target.write_bytes(pdf_bytes())
            with self.assertRaisesRegex(ValueError, "target CAS"):
                pdf_receiver.preflight_request(state, "R1", "NEW", identity, target.name)

    def test_pubmed_executor_uses_offline_browser_mock(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest, manifest_path, _inventory = manifest_and_path(
                root, inventory_one("pmid", "PMID: 12345")
            )
            journal_path = root / "journal.json"
            contract.atomic_write_json(journal_path, journal_for(manifest, manifest_path))

            class FakeResponse:
                ok = True

                @staticmethod
                def body() -> bytes:
                    return pdf_bytes("PMID: 12345")

            class FakeLocator:
                def __init__(self, page, selector: str) -> None:
                    self.page = page
                    self.selector = selector

                def inner_text(self, timeout: int) -> str:
                    del timeout
                    return "article page"

                @property
                def first(self):
                    return self

                def count(self) -> int:
                    if "citation_pdf_url" in self.selector and "pubmed.ncbi" in self.page.url:
                        return 0
                    return 1

                def get_attribute(self, name: str) -> str:
                    return "https://local.invalid/article.pdf" if name == "content" else ""

                def evaluate_all(self, _script: str) -> list[str]:
                    if "full-text-links" in self.selector:
                        return ["https://local.invalid/full-text"]
                    return []

            class FakePage:
                url = "https://pubmed.ncbi.nlm.nih.gov/12345/"
                request = types.SimpleNamespace(get=lambda *_args, **_kwargs: FakeResponse())

                def goto(self, url: str, **_kwargs) -> None:
                    self.url = url

                @staticmethod
                def title() -> str:
                    return "PubMed fixture"

                def locator(self, selector: str) -> FakeLocator:
                    return FakeLocator(self, selector)

                @staticmethod
                def screenshot(*_args, **_kwargs) -> None:
                    raise AssertionError("downloaded route must not screenshot")

            page = FakePage()
            context = types.SimpleNamespace(pages=[page], close=lambda: None)
            browser = types.SimpleNamespace(new_context=lambda **_kwargs: context, close=lambda: None)
            playwright = types.SimpleNamespace(
                chromium=types.SimpleNamespace(launch=lambda **_kwargs: browser)
            )

            class Manager:
                def __enter__(self):
                    return playwright

                def __exit__(self, *_args):
                    return False

            fake_sync_api = types.ModuleType("playwright.sync_api")
            fake_sync_api.sync_playwright = lambda: Manager()
            fake_playwright = types.ModuleType("playwright")
            fake_playwright.sync_api = fake_sync_api
            args = argparse.Namespace(
                output_root=root,
                journal=journal_path,
                paper_dir=root / "papers",
                screenshot_dir=root / "screenshots",
                manifest=manifest_path,
                row_id="R1",
                attempt_id="PUBMED-1",
                timeout_ms=1000,
            )
            with mock.patch.dict(
                sys.modules,
                {"playwright": fake_playwright, "playwright.sync_api": fake_sync_api},
            ):
                result = browser_route_executor.execute_browser_route("pubmed", args)
            self.assertEqual("downloaded", result["outcome"])
            self.assertTrue(result["pubmed_full_text_checked"])
            self.assertEqual(["https://local.invalid/full-text"], result["pubmed_full_text_links"])
            self.assertEqual(
                "https://pubmed.ncbi.nlm.nih.gov/12345/",
                browser_route_executor.route_for("pubmed", manifest["rows"][0])[0],
            )

    def test_final_gate_refuses_unresolved_or_output_alias_without_writes(self) -> None:
        summary_script = SCRIPT_DIR / "summarize_download_manifest.py"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            _manifest, manifest_path, inventory = manifest_and_path(root)
            coverage = root / "coverage.md"
            failed = root / "failed.md"
            receipt = root / "receipt.json"
            command = [
                sys.executable, str(summary_script), "--manifest", str(manifest_path),
                "--inventory", str(inventory), "--coverage-out", str(coverage),
                "--failed-out", str(failed), "--receipt-out", str(receipt),
                "--output-root", str(root),
            ]
            result = subprocess.run(command, capture_output=True, text=True, check=False)
            self.assertNotEqual(0, result.returncode)
            self.assertIn("final completion gate failed", result.stderr)
            self.assertFalse(coverage.exists())
            self.assertFalse(failed.exists())
            self.assertFalse(receipt.exists())

            before = manifest_path.read_bytes()
            alias_command = command.copy()
            alias_command[alias_command.index(str(coverage))] = str(manifest_path)
            alias = subprocess.run(alias_command, capture_output=True, text=True, check=False)
            self.assertNotEqual(0, alias.returncode)
            self.assertIn("path alias", alias.stderr)
            self.assertEqual(before, manifest_path.read_bytes())

    def test_final_inventory_readback_rejects_rehashed_row_content_tamper(self) -> None:
        summary_script = SCRIPT_DIR / "summarize_download_manifest.py"
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            manifest, manifest_path, inventory = manifest_and_path(root)
            manifest["rows"][0]["title"] = "tampered but rehashed"
            manifest["inventory"]["rows_sha256"] = contract.rows_binding_sha256(manifest["rows"])
            contract.save_manifest(manifest_path, manifest, root)
            result = subprocess.run(
                [
                    sys.executable, str(summary_script), "--manifest", str(manifest_path),
                    "--inventory", str(inventory), "--coverage-out", str(root / "coverage.md"),
                    "--failed-out", str(root / "failed.md"), "--receipt-out", str(root / "receipt.json"),
                    "--output-root", str(root),
                ],
                capture_output=True,
                text=True,
                check=False,
            )
            self.assertNotEqual(0, result.returncode)
            self.assertIn("frozen row bindings", result.stderr)
            self.assertFalse((root / "coverage.md").exists())


if __name__ == "__main__":
    unittest.main()
