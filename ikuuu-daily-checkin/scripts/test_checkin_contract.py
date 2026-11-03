import unittest
from checkin_contract import classify_checkin


class CheckinEvidenceTests(unittest.TestCase):
    def test_fresh_checkin_and_existing_checkin_are_distinct(self):
        new = classify_checkin({"before": "available", "click_attempted": True,
                                "after": "done", "reward_popup": "new"})
        self.assertEqual(new, {"outcome": "success", "action": "clicked_once", "reward_eligible": True})
        old = classify_checkin({"before": "done", "click_attempted": False,
                                "after": "done", "reward_popup": "preexisting"})
        self.assertEqual(old, {"outcome": "already_checked_in", "action": "not_clicked", "reward_eligible": False})

    def test_clicked_done_control_and_missing_before_are_uncertain_attempts(self):
        for before in ("done", "unknown"):
            result = classify_checkin({"before": before, "click_attempted": True,
                                       "after": "done", "reward_popup": "new"})
            self.assertEqual(result["outcome"], "uncertain")
            self.assertEqual(result["action"], "clicked_once")
            self.assertFalse(result["reward_eligible"])

    def test_no_call_record_cannot_be_defaulted_to_false(self):
        result = classify_checkin({"before": "done", "click_attempted": None,
                                   "after": "done", "reward_popup": "preexisting"})
        self.assertEqual(result["action"], "unknown")
        self.assertEqual(result["outcome"], "uncertain")

    def test_success_without_new_popup_does_not_prove_reward(self):
        for popup in ("unknown", "preexisting"):
            result = classify_checkin({"before": "available", "click_attempted": True,
                                       "after": "done", "reward_popup": popup})
            self.assertEqual(result["outcome"], "success")
            self.assertFalse(result["reward_eligible"])


if __name__ == "__main__":
    unittest.main()
