#!/usr/bin/env python3
from pathlib import Path
import sys
import tempfile
import unittest


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from replay_recapture_regression import receipt_path  # noqa: E402


class ReceiptPathBindingTests(unittest.TestCase):
    def test_rebases_same_legacy_package_to_current_calendar_location(self):
        with tempfile.TemporaryDirectory() as temporary:
            source_root = (
                Path(temporary)
                / "12-agent-submissions"
                / "2026"
                / "07"
                / "30"
                / "20260730001-codex"
            )
            evidence = source_root / "payload" / "capture-evidence" / "case-02" / "article.md"
            evidence.parent.mkdir(parents=True)
            evidence.write_text("fixture", encoding="utf-8")
            historical = Path(
                "/Users/example/Documents/Akashic/12-agent-submissions/"
                "20260730001-codex/payload/capture-evidence/case-02/article.md"
            )

            rebound = receipt_path(historical, source_root, "20260730001-codex")

            self.assertEqual(evidence.resolve(), rebound)

    def test_rejects_unrelated_absolute_path(self):
        with tempfile.TemporaryDirectory() as temporary:
            source_root = Path(temporary) / "2026" / "07" / "30" / "20260730001-codex"
            source_root.mkdir(parents=True)

            with self.assertRaisesRegex(ValueError, "outside source package"):
                receipt_path("/private/tmp/unrelated.txt", source_root, "20260730001-codex")

    def test_rejects_mismatched_legacy_package_id(self):
        with tempfile.TemporaryDirectory() as temporary:
            source_root = Path(temporary) / "2026" / "07" / "30" / "20260730001-codex"
            source_root.mkdir(parents=True)
            historical = (
                "/Users/example/Documents/Akashic/12-agent-submissions/"
                "different-package/payload/evidence.json"
            )

            with self.assertRaisesRegex(ValueError, "outside source package"):
                receipt_path(historical, source_root, "20260730001-codex")


if __name__ == "__main__":
    unittest.main()
