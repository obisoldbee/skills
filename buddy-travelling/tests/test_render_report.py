import json
import os
import subprocess
import sys
import unittest
from pathlib import Path

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))
from buddy_contract import dispatch_receipt, previous_receipt_block_receipt, receipt_for_observed_state
from render_report import render


class ReportTests(unittest.TestCase):
    def completed(self):
        return {"receipt": dispatch_receipt("2026-09-13", "咖啡馆", "Buddy 正在咖啡馆采风中...",
                                           "旅行倒计时 03:59:47"),
                "gift": "claimed", "points": 10, "page": {"status": "closed", "space_id": 10},
                "notifications": []}

    def test_observed_live_dispatch_has_one_short_consistent_result(self):
        data = self.completed()
        result = subprocess.run([sys.executable, "-B", str(SCRIPTS / "render_report.py")],
                                input=json.dumps(data, ensure_ascii=False), capture_output=True,
                                text=True, encoding="utf-8")
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, "Buddy｜2026-09-13\n结果：已完成（本轮已派出）\n"
                         "领取：10 积分（本轮已领取）\n旅行：咖啡馆 · 剩余 03:59:47\n"
                         "页面：已关闭\n飞书：未触发\n")

    def test_cli_uses_utf8_under_legacy_windows_pipe_encoding(self):
        result = subprocess.run(
            [sys.executable, "-B", str(SCRIPTS / "render_report.py")],
            input=json.dumps(self.completed(), ensure_ascii=False),
            capture_output=True, text=True, encoding="utf-8",
            env={**os.environ, "PYTHONIOENCODING": "cp1252", "PYTHONUTF8": "0"})
        self.assertEqual(result.returncode, 0, result.stderr)
        self.assertEqual(result.stdout, render(self.completed()) + "\n")

    def test_already_travelling_does_not_claim_reward_or_dispatch(self):
        data = self.completed()
        data.update(receipt=receipt_for_observed_state("2026-09-13",
                    {"state": "already_travelling", "countdown": "旅行倒计时 03:05:54"}),
                    gift="not_claimed", points=None)
        self.assertEqual(render(data), "Buddy｜2026-09-13\n结果：旅行中（本轮未派出）\n"
                         "领取：本轮未领取\n旅行：剩余 03:05:54\n页面：已关闭\n飞书：未触发")

    def test_unknown_dispatch_and_prior_unknown_never_become_completed(self):
        data = self.completed()
        data["receipt"] = dispatch_receipt("2026-09-13", "咖啡馆", None, None)
        data["page"] = {"status": "preserved", "space_id": 9}
        self.assertIn("结果：派出结果未确认", render(data))
        self.assertNotIn("旅行：咖啡馆", render(data))
        data["receipt"] = previous_receipt_block_receipt("2026-09-13", data["receipt"])
        self.assertIn("此前结果仍未解决", render(data))

    def test_old_points_and_contradictory_receipt_are_rejected(self):
        for change in ("old_points", "contradiction"):
            data = self.completed()
            if change == "old_points":
                data["gift"] = "not_claimed"
            else:
                data["receipt"]["dispatch_confirmed"] = False
            with self.subTest(change=change), self.assertRaises(ValueError):
                render(data)

    def test_maintenance_and_notification_failures_stay_separate(self):
        data = self.completed()
        data.update(receipt=receipt_for_observed_state("2026-09-13",
                    {"state": "maintenance", "evidence_text": "当前官网维护"}),
                    gift="not_claimed", points=None, maintenance_unchanged=True)
        self.assertIn("持续维护，未重复提醒", render(data))
        data["notifications"] = [{"kind": "maintenance_entered", "status": "failed"}]
        self.assertIn("飞书：维护开始提醒发送失败", render(data))
        self.assertIn("页面：已关闭", render(data))

    def test_sent_requires_receipt_but_does_not_print_internal_id(self):
        data = self.completed()
        data["notifications"] = [{"kind": "maintenance_recovered", "status": "sent"}]
        with self.assertRaises(ValueError):
            render(data)
        data["notifications"][0]["message_id"] = "om_test_only"
        self.assertIn("维护结束提醒已发送", render(data))
        self.assertNotIn("om_test_only", render(data))

    def test_cleanup_problem_does_not_erase_real_dispatch(self):
        data = self.completed()
        data["page"] = {"status": "unconfirmed", "space_id": 10}
        self.assertIn("已完成（本轮已派出）（页面收尾异常）", render(data))
        self.assertIn("页面：关闭未确认（空间 10）", render(data))

    def test_multiline_trace_is_not_accepted_as_a_reason(self):
        data = self.completed()
        data["reason"] = "日志一\n日志二"
        with self.assertRaises(ValueError):
            render(data)


if __name__ == "__main__":
    unittest.main()
