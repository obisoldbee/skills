import unittest
from pathlib import Path


SKILL_TEXT = (Path(__file__).resolve().parents[1] / "SKILL.md").read_text(encoding="utf-8")


class SkillRoutingContractTests(unittest.TestCase):
    def test_description_covers_implicit_wechat_link_requests(self):
        description = next(
            line.removeprefix("description: ")
            for line in SKILL_TEXT.splitlines()
            if line.startswith("description: ")
        )

        self.assertIn("public webpages", description)
        self.assertIn("WeChat/微信公众号 link", description)
        self.assertIn("including a bare URL with no stated task", description)
        self.assertIn("acknowledge this Skill and ask one concise question", description)

    def test_purpose_built_route_is_selected_before_generic_browser(self):
        purpose_built = SKILL_TEXT.index("purpose-built page-extraction or browser-control route")
        generic = SKILL_TEXT.index("generic web or browser capability")

        self.assertLess(purpose_built, generic)
        self.assertIn("when `ego-browser` is listed", SKILL_TEXT)
        self.assertIn("use it first", SKILL_TEXT)

    def test_static_probe_does_not_exhaust_rendered_browser_route(self):
        self.assertIn(
            "A static fetch that returns only metadata is a probe, not the one allowed rendered-browser attempt",
            SKILL_TEXT,
        )

    def test_route_level_policy_block_is_not_reported_as_page_failure(self):
        self.assertIn("Do not switch tools to evade an explicit safety-policy", SKILL_TEXT)
        self.assertIn("Do not claim that the webpage itself is inaccessible", SKILL_TEXT)

    def test_later_failure_cannot_erase_substantive_body(self):
        self.assertIn(
            "do not let a later weaker probe or failed route downgrade it to “正文不可得”",
            SKILL_TEXT,
        )

    def test_ordinary_review_hides_legacy_versions_and_editions(self):
        self.assertIn(
            "must not appear in a normal user response unless the user is diagnosing that adapter",
            SKILL_TEXT,
        )
        self.assertIn(
            "Do not mention executor brands, versions, hashes, receipt schemas, or internal status codes in an ordinary review",
            SKILL_TEXT,
        )


if __name__ == "__main__":
    unittest.main()
