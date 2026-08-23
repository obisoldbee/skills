import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from common import package_relative, sha256_file  # noqa: E402
from assess_capture_evidence import validate_media_content  # noqa: E402


class CaseLineageTests(unittest.TestCase):
    def test_media_inventory_must_cover_the_exact_dom_media_set(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            case = root / "case"
            case.mkdir()
            first = case / "first.png"
            second = case / "second.png"
            first.write_bytes(b"first")
            second.write_bytes(b"second")
            first_ref = {"path": package_relative(first, root), "sha256": sha256_file(first)}
            second_ref = {"path": package_relative(second, root), "sha256": sha256_file(second)}
            capture_inventory = [
                {
                    "dom_id": "media-0001",
                    "kind": "img",
                    "locator": "first.png",
                    "duplicate_of": None,
                    "availability": "captured",
                    "source_asset": first_ref,
                },
                {
                    "dom_id": "media-0002",
                    "kind": "img",
                    "locator": "second.png",
                    "duplicate_of": None,
                    "availability": "captured",
                    "source_asset": second_ref,
                },
            ]
            valid_items = [
                {"dom_id": "media-0001", "source_asset": first_ref, "classification": "non_claim_content"},
                {"dom_id": "media-0002", "source_asset": second_ref, "classification": "cover_or_ui"},
            ]
            fixtures = {
                "missing": valid_items[:1],
                "duplicate": [valid_items[0], valid_items[0]],
                "foreign_extra": [
                    *valid_items,
                    {"dom_id": "media-9999", "source_asset": first_ref, "classification": "non_claim_content"},
                ],
            }
            for name, inventory_items in fixtures.items():
                with self.subTest(name=name):
                    media = {
                        "status": "success",
                        "inventory_status": "completed",
                        "media_claims_required": False,
                        "inventory_items": inventory_items,
                    }
                    completed, _claims, _available, failures = validate_media_content(
                        media,
                        root,
                        case,
                        first,
                        sha256_file(first),
                        capture_inventory,
                    )
                    self.assertFalse(completed)
                    self.assertTrue(
                        "media_inventory_dom_set_mismatch" in failures
                        or "media_inventory_duplicate_dom_id" in failures
                    )

    def test_cross_case_media_asset_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            case_a = root / "cases" / "a"
            case_b = root / "cases" / "b"
            case_a.mkdir(parents=True)
            case_b.mkdir(parents=True)
            intake = case_a / "intake.json"
            intake.write_text(
                json.dumps(
                    {
                        "schema": "web-bookmark-intelligence/intake/v2",
                        "case_id": "a",
                        "case_root": package_relative(case_a, root),
                        "input_kind": "web_page",
                        "source_locator": "https://example.com/a",
                    }
                ),
                encoding="utf-8",
            )
            html = case_a / "rendered.html"
            html.write_text("fixture", encoding="utf-8")
            foreign_asset = case_b / "image.png"
            foreign_asset.write_bytes(b"foreign")
            capture = case_a / "capture.json"
            capture.write_text(
                json.dumps(
                    {
                        "schema": "web-bookmark-intelligence/capture-record/v3",
                        "case_id": "a",
                        "case_root": package_relative(case_a, root),
                        "intake": {"path": package_relative(intake, root), "sha256": sha256_file(intake)},
                        "source": {
                            "url": "https://example.com/a",
                            "local_html": package_relative(html, root),
                            "sha256": sha256_file(html),
                        },
                        "source_assets": [
                            {"path": package_relative(foreign_asset, root), "sha256": sha256_file(foreign_asset)}
                        ],
                        "quality_gate": {"body_evidence_state": "substantive", "meta_description_as_body": False},
                    }
                ),
                encoding="utf-8",
            )
            media = case_a / "media.json"
            media.write_text(
                json.dumps(
                    {
                        "schema": "web-bookmark-intelligence/media-evidence/v2",
                        "case_id": "a",
                        "case_root": package_relative(case_a, root),
                        "status": "success",
                        "inventory_status": "completed",
                        "media_claims_required": True,
                        "lineage": {
                            "intake": {"path": package_relative(intake, root), "sha256": sha256_file(intake)},
                            "capture": {"path": package_relative(capture, root), "sha256": sha256_file(capture)},
                            "source_asset": {
                                "path": package_relative(foreign_asset, root),
                                "sha256": sha256_file(foreign_asset),
                            },
                        },
                    }
                ),
                encoding="utf-8",
            )
            out = case_a / "assessment.json"
            environment = os.environ.copy()
            environment["PYTHONDONTWRITEBYTECODE"] = "1"

            completed = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(SCRIPT_DIR / "assess_capture_evidence.py"),
                    "--intake",
                    str(intake),
                    "--capture",
                    str(capture),
                    "--media",
                    str(media),
                    "--package-root",
                    str(root),
                    "--case-root",
                    str(case_a),
                    "--out",
                    str(out),
                ],
                capture_output=True,
                text=True,
                check=False,
                env=environment,
            )

            self.assertEqual(1, completed.returncode)
            payload = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual("case_lineage_mismatch", payload["reason"])
            self.assertIn("media_source_asset_path_mismatch", payload["case_binding"]["failures"])
            self.assertFalse(payload["page_purpose_ready"])


if __name__ == "__main__":
    unittest.main()
