"""Static checks for the user-selected routing policy.

Capture and network behavior are covered by the package's behavioral tests.
These checks protect the ordered browser preference and the access stop gate.
"""
import re
import unittest
from pathlib import Path


SKILL_TEXT = (Path(__file__).resolve().parents[1] / "SKILL.md").read_text(encoding="utf-8")


class SkillRoutingContractTests(unittest.TestCase):
    def test_browser_preference_order(self):
        route = SKILL_TEXT.split("## Select The Retrieval Route Before Access", 1)[1].split("## Read-only review", 1)[0]
        choices = re.findall(r"^\d+\. (.+)$", route, re.MULTILINE)
        self.assertEqual(len(choices), 4)
        self.assertIn("ego-browser", choices[0])
        self.assertIn("Tabbit", choices[1])
        self.assertIn("system default browser", choices[2])
        self.assertIn("recorded by the current harness", choices[2])
        self.assertIn("built-in browser", choices[3])

    def test_access_challenges_stop_browser_fallback(self):
        route = SKILL_TEXT.split("## Select The Retrieval Route Before Access", 1)[1].split("## Read-only review", 1)[0]
        stop = next(line for line in route.splitlines() if "Stop for user action" in line)
        for condition in ("login", "CAPTCHA", "permission denial", "user takeover"):
            self.assertIn(condition, stop)


if __name__ == "__main__":
    unittest.main()
