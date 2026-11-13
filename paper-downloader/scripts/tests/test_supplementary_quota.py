import argparse
import json
import subprocess
import tempfile
import sys
import unittest
from pathlib import Path
from unittest import mock
sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
import manifest_contract as contract
import build_inventory_download_manifest as builder
import manifest_pdf_downloader as downloader
import summarize_download_manifest as summary
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

    def test_shared_identifiers_preserve_rows_and_count_distinct_files_once(self):
        sources = ["A,Exact title,10.1000/one,", "B,Exact title,10.1000/one,PMC12345"]
        for lines in (sources, list(reversed(sources))):
            with self.subTest(lines=lines), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                source = root / "inventory.csv"
                source.write_text("row_id,title,doi,pmcid\n" + "\n".join(lines) + "\n")
                manifest = builder.build_manifest(source, root)
                first, duplicate = manifest["rows"]
                self.assertEqual((first["status"], duplicate["status"], duplicate["duplicate_of"]),
                                 ("pending", "duplicate", first["row_id"]))
                # Exercise an older v2 freeze with two independently validated file versions.
                del manifest["inventory"]["identity_grouping"]
                manifest["rows"] = builder.build_rows(source, legacy_frozen=True)
                manifest["inventory"]["rows_sha256"] = contract.rows_binding_sha256(manifest["rows"])
                (root / "papers").mkdir()
                for i, row in enumerate(manifest["rows"]):
                    path = root / "papers" / (row["row_id"] + ".pdf")
                    path.write_bytes(pdf_bytes(size=5200 + i, identifier="DOI: 10.1000/one", title="Exact title"))
                    row.update(status="downloaded", pdf=contract.verify_pdf(
                        path, root, row, identity_match_method=None, identity_match_evidence=None))
                contract.save_manifest(root / "manifest.json", manifest, root)
                result = subprocess.run([sys.executable, "-B", str(Path(summary.__file__)),
                    "--manifest", str(root / "manifest.json"), "--inventory", str(source),
                    "--coverage-out", str(root / "coverage.md"), "--failed-out", str(root / "failed.md"),
                    "--receipt-out", str(root / "receipt.json"), "--output-root", str(root)], capture_output=True)
                self.assertEqual(result.returncode, 0, result.stderr)
                quota = json.loads((root / "receipt.json").read_bytes())["quota"]
                self.assertEqual((quota["target_requested"], quota["target_downloaded"]), (1, 1))

    def test_alias_bridge_and_conflicting_identifiers(self):
        rows = [{"doi": "10.1000/one"}, {"pmid": "12345"},
                {"doi": "10.1000/one", "pmid": "12345", "pmcid": "PMC12345"}]
        self.assertEqual(contract.publication_groups(rows), [[0, 1, 2]])
        rows[1]["doi"] = "10.1000/two"
        with self.assertRaisesRegex(ValueError, "conflicting doi"):
            contract.publication_groups(rows)

    def test_first_pass_title_and_supplied_pdf_use_document_metadata(self):
        for title, status in (("Exact title", "downloaded"), ("Other title", "needs_manual_review")):
            with self.subTest(title=title), tempfile.TemporaryDirectory() as temporary:
                root = Path(temporary)
                source = root / "inventory.csv"
                url = "https://publisher.example/article.pdf"
                source.write_text(f"row_id,title,pdf_url\nA,Exact title,{url}\nB,Title only,\n")
                linked, unlinked = builder.build_manifest(source, root)["rows"]
                self.assertEqual((linked["status"], unlinked["status"]), ("pending", "unverified_citation"))
                args = argparse.Namespace(output_root=root, paper_dir=root / "papers", timeout=1,
                    skip_recursive_local_scan=True, skip_doi_landing=True, skip_oa_package=True)
                linked["status"] = "unverified_citation"  # Older frozen row still resumes through its own URL.
                with mock.patch.object(downloader, "curl_bytes", return_value=(
                    pdf_bytes(identifier="", title=title), url, "fixture")) as fetch:
                    result = downloader.process_row(linked, args, [])
                    self.assertEqual(downloader.process_row(unlinked, args, [])["attempts"], [])
                fetch.assert_called_once_with(url, 1)
                self.assertEqual(result["attempts"][0]["route"], "provided_pdf_url")
                self.assertEqual(result["status"], status)
                if status == "downloaded":
                    self.assertEqual(result["pdf"]["identity_match"]["method"], "pdf_title_metadata")
                else:
                    self.assertEqual(result["pdf"]["identity_match"]["reason"],
                                     "pdf_title_metadata_conflicts_with_requested_publication")

    def test_duplicate_rows_preserve_the_open_lookup_route_in_both_orders(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "inventory.csv"
            plain = "A,Exact title,10.1000/one,,"
            enriched = "B,Exact title,10.1000/one,PMC12345,https://publisher.example/article.pdf"
            args = argparse.Namespace(output_root=root, paper_dir=root / "papers", timeout=1,
                                      skip_recursive_local_scan=True, skip_doi_landing=True, skip_oa_package=True)
            args.paper_dir.mkdir()
            for first, second in ((plain, enriched), (enriched, plain)):
                with self.subTest(first=first[0]):
                    source.write_text(f"row_id,title,doi,pmcid,pdf_url\n{first}\n{second}\n")
                    manifest = builder.build_manifest(source, root)
                    primary, duplicate = manifest["rows"]
                    self.assertEqual(duplicate["duplicate_of"], primary["row_id"])
                    self.assertEqual((primary["pmcid"], primary["pdf_url"]),
                                     ("PMC12345", "https://publisher.example/article.pdf"))
                    if first == plain:
                        self.assertEqual(primary["route_sources"], {"pmcid": "B", "pdf_url": "B"})
                        self.assertFalse(primary["source_row"]["pmcid"])
                        self.assertIn("route_sources", contract.row_binding_projection(primary))
                    else:
                        self.assertNotIn("route_sources", primary)
                    route = "https://europepmc.org/articles/PMC12345?pdf=render"
                    args.paper_dir = root / ("papers-" + primary["row_id"])
                    args.paper_dir.mkdir()
                    with mock.patch.object(downloader, "curl_bytes", return_value=(
                        pdf_bytes(identifier="DOI: 10.1000/one", title="Exact title"), route, "fixture")) as fetch:
                        saved = downloader.process_row(primary, args, [])
                    fetch.assert_called_once_with(route, 1)
                    self.assertEqual(saved["status"], "downloaded")
                    self.assertEqual(contract.quota_counts([saved, duplicate])["target_downloaded"], 1)

    def test_failed_supplied_url_can_reach_duplicate_rows_other_locator(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "inventory.csv"
            first = "https://one.example/paper.pdf"
            second = "https://two.example/paper.pdf"
            source.write_text("row_id,title,doi,pdf_url\n"
                              f"A,Exact title,10.1000/one,{first}\nB,Exact title,10.1000/one,{second}\n")
            primary, duplicate = builder.build_manifest(source, root)["rows"]
            self.assertEqual(primary["alternate_pdf_urls"], {second: duplicate["row_id"]})
            args = argparse.Namespace(output_root=root, paper_dir=root / "papers", timeout=1,
                                      skip_recursive_local_scan=True, skip_doi_landing=True, skip_oa_package=True)
            args.paper_dir.mkdir()
            replies = [(None, first, "fixture unavailable"),
                       (pdf_bytes(identifier="DOI: 10.1000/one", title="Exact title"), second, "fixture")]
            with mock.patch.object(downloader, "curl_bytes", side_effect=replies) as fetch:
                saved = downloader.process_row(primary, args, [])
            self.assertEqual(fetch.call_args_list, [mock.call(first, 1), mock.call(second, 1)])
            self.assertEqual(saved["status"], "downloaded")
            self.assertEqual(contract.quota_counts([saved, duplicate])["target_downloaded"], 1)

    def test_search_and_wildcard_inputs_never_become_supplied_pdf_routes(self):
        args = argparse.Namespace(skip_recursive_local_scan=True, skip_doi_landing=True,
                                  skip_oa_package=True, timeout=1)
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            args.output_root, args.paper_dir = root, root / "papers"
            source = root / "inventory.csv"
            for url in ("https://publisher.example/search?q=clock", "https://publisher.example/?term=clock",
                        "https://publisher.example/action/doSearch?title=clock",
                        "https://publisher.example/papers/%2A.pdf"):
                with self.subTest(url=url):
                    source.write_text(f"row_id,title,pdf_url\nA,Exact title,{url}\n")
                    row = builder.build_manifest(source, root)["rows"][0]
                    self.assertEqual((row["status"], row["pdf_url"]), ("unverified_citation", ""))
                    row["pdf_url"] = url  # A previously saved locator gets the same check at execution.
                    with mock.patch.object(downloader, "curl_bytes") as fetch:
                        self.assertEqual(downloader.process_row(row, args, [])["attempts"], [])
                    fetch.assert_not_called()
                    self.assertNotIn(("provided_pdf_url", url), downloader.route_urls({**row, "doi": "10.1000/example"}))
            direct = "https://publisher.example/retrieve?asset=42&token=fixture"
            direct_pdf = "https://publisher.example/article.pdf?q=fixture"
            for provided in (direct, direct_pdf, "https://publisher.example/search/paper.pdf"):
                self.assertEqual(builder.pdf_url_from_row({"pdf_url": provided}), provided)

    def test_same_title_distinct_pdf_resources_keep_independent_rows(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "inventory.csv"
            source.write_text("row_id,title,pdf_url\n"
                              "A,Editorial,https://one.example/paper.pdf\n"
                              "B,Editorial,https://two.example/paper.pdf\n"
                              "C,Editorial,https://one.example/paper.pdf#page=1\n")
            rows = builder.build_manifest(source, root)["rows"]
            self.assertEqual([row["status"] for row in rows], ["pending", "pending", "duplicate"])
            self.assertEqual(rows[2]["duplicate_of"], rows[0]["row_id"])
            self.assertEqual(contract.quota_counts(rows)["target_requested"], 2)

    def test_unavailable_title_bound_pdf_returns_an_actionable_manual_state(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "inventory.csv"
            url = "https://publisher.example/expired.pdf"
            source.write_text(f"row_id,title,pdf_url\nA,Exact title,{url}\n")
            row = builder.build_manifest(source, root)["rows"][0]
            args = argparse.Namespace(output_root=root, paper_dir=root / "papers", timeout=1,
                                      skip_recursive_local_scan=True, skip_doi_landing=True, skip_oa_package=True)
            with mock.patch.object(downloader, "curl_bytes", return_value=(None, url, "fixture expired")) as fetch:
                result = downloader.process_row(row, args, [])
                self.assertEqual(result["status"], "needs_manual_review")
                self.assertIn("current_pdf_url_or_publication_identifier", result["failure_reason"])
                self.assertEqual(result["attempts"][0]["outcome"], "request_failed")
                historical = {**result, "status": "browser_required"}
                repaired = downloader.process_row(historical, args, [])
                self.assertEqual((repaired["status"], repaired["attempts"]), (result["status"], result["attempts"]))
                self.assertEqual(downloader.process_row(repaired, args, [])["status"], "needs_manual_review")
                fetch.assert_called_once_with(url, 1)

    def test_search_pdf_filename_is_a_direct_file_not_a_search_endpoint(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            source = root / "inventory.csv"
            url = "https://publisher.example/papers/search.pdf"
            source.write_text(f"row_id,title,doi,pdf_url\nA,Exact title,10.1000/one,{url}\n")
            row = builder.build_manifest(source, root)["rows"][0]
            args = argparse.Namespace(output_root=root, paper_dir=root / "papers", timeout=1,
                                      skip_recursive_local_scan=True, skip_doi_landing=True, skip_oa_package=True)
            args.paper_dir.mkdir()
            with mock.patch.object(downloader, "curl_bytes", return_value=(
                pdf_bytes(identifier="DOI: 10.1000/one", title="Exact title"), url, "fixture")) as fetch:
                saved = downloader.process_row(row, args, [])
            fetch.assert_called_once_with(url, 1)
            self.assertEqual(saved["status"], "downloaded")
            self.assertEqual(builder.pdf_url_from_row({"pdf_url": "https://publisher.example/search.php?q=clock"}), "")

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
