import unittest
from pathlib import Path


SKILL_ROOT = Path(__file__).resolve().parents[2]


class SkillContractTest(unittest.TestCase):
    def test_skill_declares_serial_shared_egress_and_ego_primary(self) -> None:
        text = (SKILL_ROOT / "SKILL.md").read_text(encoding="utf-8")

        self.assertIn("shared-egress-ip:paper-download", text)
        self.assertIn("Prefer the separately registered `$ego-browser`", text)
        self.assertIn("--workers 1", text)

    def test_ego_route_preserves_handoff_and_disk_truth_gates(self) -> None:
        text = (SKILL_ROOT / "references" / "ego-browser-route.md").read_text(
            encoding="utf-8"
        )

        self.assertIn("handOffTaskSpace", text)
        self.assertIn("completeTaskSpace", text)
        self.assertIn("manual_browser_required", text)
        self.assertIn("more than 5120 bytes", text)
        self.assertIn("Playwright browser scripts are permitted only", text)


if __name__ == "__main__":
    unittest.main()
