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


class ActionCardGateTests(unittest.TestCase):
    def run_cards(self, root: Path, case_root: Path, case: Path, assessment: Path, purpose: Path, units: Path, out: Path):
        environment = os.environ.copy()
        environment["PYTHONDONTWRITEBYTECODE"] = "1"
        return subprocess.run(
            [
                sys.executable,
                "-B",
                str(SCRIPT_DIR / "build_action_cards.py"),
                "--case",
                str(case),
                "--capture",
                str(assessment),
                "--purpose",
                str(purpose),
                "--content-units",
                str(units),
                "--package-root",
                str(root),
                "--case-root",
                str(case_root),
                "--out",
                str(out),
            ],
            capture_output=True,
            text=True,
            check=False,
            env=environment,
        )

    def fixture(self, root: Path, *, assessment_status="full_body", binding=True, units_case_id="case-1"):
        case_root = root / "cases" / "case-1"
        case_root.mkdir(parents=True)
        relative_root = package_relative(case_root, root)
        case = case_root / "intake.json"
        case.write_text(
            json.dumps(
                {
                    "schema": "web-bookmark-intelligence/intake/v2",
                    "case_id": "case-1",
                    "case_root": relative_root,
                }
            ),
            encoding="utf-8",
        )
        assessment = case_root / "assessment.json"
        assessment.write_text(
            json.dumps(
                {
                    "schema": "web-bookmark-intelligence/evidence-assessment/v2",
                    "case_id": "case-1",
                    "case_root": relative_root,
                    "case_binding": {"valid": binding},
                    "final_status": assessment_status,
                    "page_purpose_ready": assessment_status != "failed" and binding,
                }
            ),
            encoding="utf-8",
        )
        purpose = case_root / "purpose.json"
        purpose.write_text(
            json.dumps(
                {
                    "schema": "web-bookmark-intelligence/page-purpose-request/v2",
                    "case_id": "case-1",
                    "case_root": relative_root,
                    "case_binding_valid": binding,
                    "page_purpose_status": "ready_for_semantic_interpretation" if assessment_status != "failed" and binding else "blocked_insufficient_evidence",
                    "evidence_assessment": {
                        "path": package_relative(assessment, root),
                        "sha256": sha256_file(assessment),
                    },
                }
            ),
            encoding="utf-8",
        )
        units = case_root / "units.json"
        units.write_text(
            json.dumps(
                {
                    "schema": "web-bookmark-intelligence/content-units/v2",
                    "case_id": units_case_id,
                    "case_root": relative_root,
                    "evidence_assessment": {
                        "path": package_relative(assessment, root),
                        "sha256": sha256_file(assessment),
                    },
                    "content_units": [{"unit_id": "u1", "evidence_refs": ["span-1"]}],
                }
            ),
            encoding="utf-8",
        )
        return case_root, case, assessment, purpose, units

    def test_failed_or_unbound_assessment_produces_no_action_card(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            case_root, case, assessment, purpose, units = self.fixture(root, assessment_status="failed", binding=False)
            out = case_root / "cards.json"

            completed = self.run_cards(root, case_root, case, assessment, purpose, units, out)

            self.assertEqual(1, completed.returncode)
            payload = json.loads(out.read_text(encoding="utf-8"))
            self.assertEqual("blocked_evidence_gate", payload["action_card_status"])
            self.assertEqual([], payload["action_cards"])

    def test_cross_case_content_units_produce_no_action_card(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            case_root, case, assessment, purpose, units = self.fixture(root, units_case_id="case-2")
            out = case_root / "cards.json"

            completed = self.run_cards(root, case_root, case, assessment, purpose, units, out)

            self.assertEqual(1, completed.returncode)
            payload = json.loads(out.read_text(encoding="utf-8"))
            self.assertIn("content_units_assessment_binding_mismatch", payload["action_gate_failures"])
            self.assertEqual([], payload["action_cards"])


if __name__ == "__main__":
    unittest.main()
