import sys
import unittest
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
SKILL_PATH = Path(__file__).resolve().parents[1] / "SKILL.md"
sys.path.insert(0, str(SCRIPT_DIR))

from buddy_contract import (  # noqa: E402
    DAILY_LIMIT_TEXT,
    TRAVEL_BUTTON,
    choose_destination,
    classify_travel_control,
    destination_unavailable_receipt,
    dispatch_receipt,
    make_receipt,
    previous_receipt_block_receipt,
    previous_receipt_gate,
    receipt_for_observed_state,
    status_only_receipt,
)


DAY = "2026-08-24"


class BuddyContractTests(unittest.TestCase):
    def test_live_destination_text_and_text_node_whitespace(self):
        for status in ("Buddy 正在咖啡馆采风中...", "Buddy 正在 咖啡馆 采风中...",
                       "\nBuddy 正在\n咖啡馆\n采风中...\n"):
            with self.subTest(status=status):
                receipt = dispatch_receipt(DAY, "咖啡馆", status, "旅行倒计时 03:59:47")
                self.assertEqual(receipt["outcome"], "completed_cycle")
                self.assertFalse(previous_receipt_gate(DAY, receipt)["proceed"])

    def test_similar_destination_or_extra_status_text_does_not_confirm(self):
        for status in ("Buddy 正在咖啡馆二店采风中...", "Buddy 正在咖 啡馆采风中...",
                       "示例 Buddy 正在咖啡馆采风中...", "Buddy 正在咖啡馆采风中... 未确认"):
            with self.subTest(status=status):
                receipt = dispatch_receipt(DAY, "咖啡馆", status, "旅行倒计时 03:59:47")
                self.assertEqual(receipt["outcome"], "dispatch_outcome_unknown")
                self.assertFalse(previous_receipt_gate(DAY, receipt)["proceed"])

    def test_destination_label_is_not_interpreted_as_regex(self):
        receipt = dispatch_receipt(DAY, "馆(东)+", "Buddy 正在馆(东)+采风中...", "旅行倒计时 01:00:00")
        self.assertEqual(receipt["outcome"], "completed_cycle")
        receipt = dispatch_receipt(DAY, "馆(东)+", "Buddy 正在馆东采风中...", "旅行倒计时 01:00:00")
        self.assertEqual(receipt["outcome"], "dispatch_outcome_unknown")

    def test_maintenance_before_dispatch_can_resume_but_is_not_completed(self):
        receipt = receipt_for_observed_state(DAY, {"state":"maintenance","evidence_text":"官网当前维护公告"})
        self.assertEqual(receipt["outcome"],"maintenance")
        self.assertFalse(receipt["dispatch_attempted"])
        self.assertFalse(receipt["terminal_for_day"])
        self.assertTrue(previous_receipt_gate(DAY,receipt)["proceed"])

    def test_maintenance_does_not_allow_resetting_an_attempted_dispatch(self):
        with self.assertRaises(ValueError):
            make_receipt(DAY,"maintenance",dispatch_attempted=True,dispatch_confirmed=False,
                         terminal_for_day=False,retry_allowed=True,next_action="wait_for_service",evidence_text="维护")
        with self.assertRaises(ValueError):
            receipt_for_observed_state(DAY,{"state":"maintenance"})

    def test_runtime_boundary_keeps_portable_source_separate_from_dependencies(self):
        skill = SKILL_PATH.read_text(encoding="utf-8")
        for required in (
            "| Source class | `personal-open` |",
            "| Availability | `portable` |",
            "| Allowed devices | `any` |",
            "| Required network | `any` |",
            "ordinary reachability to `workbuddy.cn`",
            "existing authenticated growth-center page",
            "Do not install, log in, reconfigure the environment, or collect credentials.",
        ):
            self.assertIn(required, skill)

    def test_daily_limit_requires_exact_disabled_button_and_exact_text(self):
        state = classify_travel_control(
            [{"accessible_name": TRAVEL_BUTTON, "enabled": False}],
            [DAILY_LIMIT_TEXT],
        )

        self.assertEqual("daily_limit_reached", state["state"])
        receipt = receipt_for_observed_state(DAY, state)
        self.assertTrue(receipt["terminal_for_day"])
        self.assertFalse(receipt["retry_allowed"])

    def test_missing_button_is_unknown_not_daily_limit(self):
        state = classify_travel_control([], [DAILY_LIMIT_TEXT])

        self.assertEqual("travel_state_unknown", state["state"])

    def test_other_disabled_reason_is_blocked(self):
        state = classify_travel_control(
            [{"accessible_name": TRAVEL_BUTTON, "enabled": False}],
            ["系统维护中"],
        )

        self.assertEqual("blocked", state["state"])

    def test_similar_but_nonexact_tired_text_is_blocked(self):
        state = classify_travel_control(
            [{"accessible_name": TRAVEL_BUTTON, "enabled": False}],
            [DAILY_LIMIT_TEXT + "!"],
        )

        self.assertEqual("blocked", state["state"])

    def test_duplicate_exact_daily_limit_text_is_ambiguous(self):
        state = classify_travel_control(
            [{"accessible_name": TRAVEL_BUTTON, "enabled": False}],
            [DAILY_LIMIT_TEXT, DAILY_LIMIT_TEXT],
        )

        self.assertEqual("travel_state_unknown", state["state"])

    def test_unknown_enabled_state_is_unknown(self):
        state = classify_travel_control([{"accessible_name": TRAVEL_BUTTON, "enabled": None}], [])

        self.assertEqual("travel_state_unknown", state["state"])

    def test_duplicate_travel_buttons_are_ambiguous(self):
        state = classify_travel_control(
            [
                {"accessible_name": TRAVEL_BUTTON, "enabled": True},
                {"accessible_name": TRAVEL_BUTTON, "enabled": False},
            ],
            [DAILY_LIMIT_TEXT],
        )

        self.assertEqual("travel_state_unknown", state["state"])

    def test_named_destination_must_be_unique_and_enabled(self):
        decision = choose_destination(
            [{"label": "北京", "enabled": True, "selected": True}],
            "北京",
        )

        self.assertEqual("destination_ready", decision["state"])
        self.assertEqual("keep_selected", decision["selection_action"])
        self.assertTrue(decision["confirm_allowed"])

    def test_named_destination_requires_selection_readback_before_confirm(self):
        decision = choose_destination(
            [{"label": "北京", "enabled": True, "selected": False}],
            "北京",
        )

        self.assertEqual("destination_selection_required", decision["state"])
        self.assertEqual("select_exact_once", decision["selection_action"])
        self.assertFalse(decision["confirm_allowed"])

    def test_missing_named_destination_does_not_confirm(self):
        decision = choose_destination([{"label": "上海", "enabled": True}], "北京")

        self.assertEqual("destination_unavailable", decision["state"])
        self.assertFalse(decision["confirm_allowed"])

    def test_disabled_named_destination_does_not_confirm(self):
        decision = choose_destination([{"label": "北京", "enabled": False}], "北京")

        self.assertEqual("destination_unavailable", decision["state"])
        self.assertFalse(decision["confirm_allowed"])

    def test_duplicate_named_destination_does_not_confirm(self):
        decision = choose_destination(
            [{"label": "北京", "enabled": True}, {"label": "北京", "enabled": True}],
            "北京",
        )

        self.assertEqual("destination_unavailable", decision["state"])
        self.assertFalse(decision["confirm_allowed"])

    def test_unspecified_destination_keeps_one_observed_default(self):
        decision = choose_destination(
            [{"label": "杭州", "enabled": True, "selected": True}],
            None,
        )

        self.assertEqual("destination_ready", decision["state"])
        self.assertEqual("杭州", decision["destination"])
        self.assertEqual("keep_default_and_read_back", decision["selection_action"])

    def test_unspecified_destination_without_selected_default_is_unknown(self):
        decision = choose_destination([{"label": "杭州", "enabled": True, "selected": False}], None)

        self.assertEqual("destination_state_unknown", decision["state"])
        self.assertFalse(decision["confirm_allowed"])

    def test_empty_selected_default_or_empty_request_cannot_confirm(self):
        default = choose_destination(
            [{"label": "", "enabled": True, "selected": True}],
            None,
        )
        requested = choose_destination(
            [{"label": "", "enabled": True, "selected": True}],
            "",
        )

        self.assertEqual("destination_state_unknown", default["state"])
        self.assertFalse(default["confirm_allowed"])
        self.assertEqual("destination_unavailable", requested["state"])
        self.assertFalse(requested["confirm_allowed"])

    def test_destination_unavailable_receipt_never_claims_attempt(self):
        decision = choose_destination([], "北京")
        receipt = destination_unavailable_receipt(DAY, decision)

        self.assertEqual("destination_unavailable", receipt["outcome"])
        self.assertFalse(receipt["dispatch_attempted"])
        self.assertFalse(receipt["dispatch_confirmed"])

    def test_both_post_confirm_readbacks_prove_completion(self):
        receipt = dispatch_receipt(DAY, "杭州", "Buddy 正在 杭州 采风中...", "旅行倒计时 23:59:59")

        self.assertEqual("completed_cycle", receipt["outcome"])
        self.assertTrue(receipt["dispatch_attempted"])
        self.assertTrue(receipt["dispatch_confirmed"])

    def test_confirm_then_failed_readback_is_unknown_and_non_retryable(self):
        receipt = dispatch_receipt(DAY, "杭州", None, None)

        self.assertEqual("dispatch_outcome_unknown", receipt["outcome"])
        self.assertTrue(receipt["dispatch_attempted"])
        self.assertFalse(receipt["dispatch_confirmed"])
        self.assertTrue(receipt["terminal_for_day"])
        self.assertFalse(receipt["retry_allowed"])
        self.assertEqual("manual_status_check_only", receipt["next_action"])

    def test_invalid_countdown_or_empty_destination_cannot_confirm(self):
        receipt = dispatch_receipt(
            DAY,
            "杭州",
            "Buddy 正在 杭州 采风中...",
            "旅行倒计时 99:99:99",
        )
        self.assertEqual("dispatch_outcome_unknown", receipt["outcome"])
        with self.assertRaisesRegex(ValueError, "expected_destination"):
            dispatch_receipt(DAY, "", "Buddy 正在  采风中...", "旅行倒计时 00:01:00")

    def test_same_day_previous_attempt_blocks_dispatch(self):
        previous = dispatch_receipt(DAY, "杭州", None, None)

        gate = previous_receipt_gate(DAY, previous)

        self.assertFalse(gate["proceed"])
        self.assertEqual("previous_receipt_blocks_same_day_dispatch", gate["reason"])

        receipt = previous_receipt_block_receipt(DAY, previous)
        self.assertEqual("already_handled_for_service_day", receipt["outcome"])
        self.assertFalse(receipt["dispatch_attempted"])
        self.assertTrue(receipt["terminal_for_day"])

    def test_previous_service_day_does_not_block(self):
        previous = dispatch_receipt("2026-08-23", "杭州", None, None)

        gate = previous_receipt_gate(DAY, previous)

        self.assertTrue(gate["proceed"])

    def test_same_day_status_only_receipt_allows_later_action(self):
        previous = status_only_receipt(DAY, "ready_to_travel")

        gate = previous_receipt_gate(DAY, previous)

        self.assertTrue(gate["proceed"])
        self.assertEqual("previous_receipt_explicitly_allows_retry", gate["reason"])

    def test_invalid_previous_receipt_fails_closed(self):
        gate = previous_receipt_gate(DAY, {"service_day": DAY})

        self.assertFalse(gate["proceed"])
        self.assertEqual("invalid_previous_receipt", gate["reason"])

    def test_contradictory_completed_previous_receipt_fails_closed(self):
        gate = previous_receipt_gate(
            DAY,
            {
                "service_day": DAY,
                "outcome": "completed_cycle",
                "dispatch_attempted": False,
                "dispatch_confirmed": False,
                "terminal_for_day": False,
                "retry_allowed": True,
                "next_action": "retry",
            },
        )

        self.assertFalse(gate["proceed"])
        self.assertEqual("invalid_previous_receipt", gate["reason"])

    def test_previous_receipt_outcome_invariants_fail_closed(self):
        for outcome, terminal, retry in (
            ("daily_limit_reached", False, True),
            ("status_only", True, False),
        ):
            with self.subTest(outcome=outcome):
                gate = previous_receipt_gate(
                    DAY,
                    {
                        "service_day": DAY,
                        "outcome": outcome,
                        "dispatch_attempted": False,
                        "dispatch_confirmed": False,
                        "terminal_for_day": terminal,
                        "retry_allowed": retry,
                        "next_action": "none",
                    },
                )
                self.assertFalse(gate["proceed"])
                self.assertEqual("invalid_previous_receipt", gate["reason"])

    def test_previous_terminal_outcomes_require_their_specific_evidence(self):
        fixtures = [
            {
                "service_day": DAY,
                "outcome": "daily_limit_reached",
                "dispatch_attempted": False,
                "dispatch_confirmed": False,
                "terminal_for_day": True,
                "retry_allowed": False,
                "next_action": "wait_until_next_day",
            },
            {
                "service_day": DAY,
                "outcome": "already_travelling",
                "dispatch_attempted": False,
                "dispatch_confirmed": False,
                "terminal_for_day": True,
                "retry_allowed": False,
                "next_action": "wait_for_return",
            },
            {
                "service_day": DAY,
                "outcome": "completed_cycle",
                "dispatch_attempted": True,
                "dispatch_confirmed": True,
                "terminal_for_day": True,
                "retry_allowed": False,
                "next_action": "wait_until_next_day",
            },
        ]
        for fixture in fixtures:
            with self.subTest(outcome=fixture["outcome"]):
                gate = previous_receipt_gate(DAY, fixture)
                self.assertFalse(gate["proceed"])
                self.assertEqual("invalid_previous_receipt", gate["reason"])

    def test_receipt_factory_rejects_outcome_contradictions(self):
        with self.assertRaisesRegex(ValueError, "contradict"):
            make_receipt(
                DAY,
                "completed_cycle",
                dispatch_attempted=True,
                dispatch_confirmed=True,
                terminal_for_day=False,
                retry_allowed=True,
                next_action="retry",
            )

    def test_receipt_rejects_unconfirmed_retryable_attempt(self):
        with self.assertRaisesRegex(ValueError, "contradict"):
            make_receipt(
                DAY,
                "dispatch_outcome_unknown",
                dispatch_attempted=True,
                dispatch_confirmed=False,
                terminal_for_day=False,
                retry_allowed=True,
                next_action="retry",
            )


if __name__ == "__main__":
    unittest.main()
