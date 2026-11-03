import json
import subprocess
import sys
import unittest
from pathlib import Path
from render_report import render


class ReportTests(unittest.TestCase):
    def existing(self):
        return {"service_day": "2026-09-13", "outcome": "already_checked_in",
                "checkin_evidence": {"before": "done", "click_attempted": False,
                                     "after": "done", "reward_popup": "preexisting"},
                "checkin_action": "not_clicked", "reward_verified": False, "reward": None,
                "balance_verified": True, "balance": "86.38 GB",
                "page": {"status": "closed", "space_id": 11}, "notifications": []}

    def test_existing_checkin_is_five_lines_without_redundant_claim_field(self):
        result = subprocess.run([sys.executable, "-B", str(Path(__file__).with_name("render_report.py"))],
                                input=json.dumps(self.existing()), capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "Ikuuu｜2026-09-13\n结果：已签到（本轮未重复签到）\n"
                         "剩余流量：86.38 GB\n页面：已关闭\n飞书：未触发\n")

    def test_current_click_can_report_its_verified_reward(self):
        data = self.existing()
        data.update(outcome="success", checkin_action="clicked_once", reward_verified=True, reward="522 MB")
        data["checkin_evidence"].update(before="available", click_attempted=True, reward_popup="new")
        self.assertEqual(render(data).splitlines(), ["Ikuuu｜2026-09-13",
                         "结果：签到成功（本轮已签到）；奖励 522 MB",
                         "剩余流量：86.38 GB", "页面：已关闭", "飞书：未触发"])

    def test_preexisting_success_popup_cannot_claim_current_reward(self):
        data = self.existing()
        data.update(reward_verified=True, reward="522 MB")
        with self.assertRaisesRegex(ValueError, "preexisting popup"):
            render(data)
        data.update(reward_verified=False)
        with self.assertRaisesRegex(ValueError, "unverified reward"):
            render(data)

    def test_user_requested_page_retention_is_normal(self):
        data = self.existing()
        data["page"] = {"status": "preserved", "space_id": "tabbit:tab:42",
                        "keep_reason": "user_requested"}
        report = render(data)
        self.assertNotIn("页面收尾异常", report)
        self.assertIn("页面：已保留（页面 tabbit:tab:42）", report)

    def test_unexplained_retention_stays_a_cleanup_problem(self):
        data = self.existing()
        data["page"] = {"status": "preserved", "space_id": 42}
        self.assertIn("页面收尾异常", render(data))
        data["page"]["keep_reason"] = "cleanup_failed"
        with self.assertRaisesRegex(ValueError, "keep_reason"):
            render(data)

    def test_retention_reason_requires_a_preserved_identified_page(self):
        data = self.existing()
        data["page"]["keep_reason"] = "user_requested"
        with self.assertRaisesRegex(ValueError, "keep_reason"):
            render(data)
        data["page"] = {"status": "preserved", "keep_reason": "user_requested"}
        with self.assertRaisesRegex(ValueError, "identity"):
            render(data)

    def test_query_can_complete_before_daily_checkin(self):
        data = self.existing()
        data.update(outcome="not_completed")
        data["checkin_evidence"].update(before="available", after="not_done",
                                      reward_popup="unknown")
        report = render(data)
        self.assertIn("结果：尚未签到（仅查询）", report)
        self.assertNotIn("页面收尾异常", report)

    def test_missing_balance_does_not_count_as_complete(self):
        data = self.existing()
        data.update(balance_verified=False, balance=None)
        with self.assertRaises(ValueError):
            render(data)
        data.update(outcome="uncertain", page={"status": "preserved", "space_id": 12})
        self.assertIn("结果：未确认", render(data))
        self.assertIn("剩余流量：未确认", render(data))

    def test_different_business_and_notification_outcomes_are_clear(self):
        data = self.existing()
        data["notifications"] = [{"kind": "low_traffic", "status": "failed"}]
        data["balance"] = "10.25 GB"
        self.assertIn("结果：已签到", render(data))
        self.assertIn("飞书：低流量提醒发送失败", render(data))

    def test_maintenance_is_not_completed_and_unchanged_is_explicit(self):
        data = self.existing()
        data.update(outcome="maintenance", balance=None, balance_verified=False)
        self.assertIn("维护中（本轮业务暂停）", render(data))
        self.assertNotIn("持续维护", render(data))
        data["maintenance_unchanged"] = True
        self.assertIn("持续维护，未重复提醒", render(data))

    def test_no_click_cannot_be_labeled_new_success(self):
        data = self.existing()
        data["outcome"] = "success"
        with self.assertRaises(ValueError):
            render(data)

    def test_missing_click_history_is_not_rewritten_as_no_click(self):
        data = self.existing()
        data.update(outcome="uncertain", checkin_action="unknown")
        data["checkin_evidence"]["click_attempted"] = None
        self.assertIn("结果：未确认", render(data))
        self.assertNotIn("领取：", render(data))
        data.update(reward_verified=True, reward="522 MB")
        with self.assertRaises(ValueError):
            render(data)

    def test_invoked_click_cannot_be_explained_away_as_no_effective_click(self):
        data = self.existing()
        data["checkin_evidence"].update(click_attempted=True, before="unknown")
        with self.assertRaisesRegex(ValueError, "actual click attempt"):
            render(data)
        data.update(checkin_action="clicked_once", outcome="uncertain")
        self.assertIn("结果：未确认（本轮已尝试签到）", render(data))
        self.assertNotIn("领取：", render(data))


if __name__ == "__main__":
    unittest.main()
