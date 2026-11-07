"""Web IO route selection and existing-owner continuity, without browser calls."""

import unittest

from test_review_cycle import HELPER, followup, preparation, state
from test_current_task_inline import current_task, native_event


class WebExecutorRouteTests(unittest.TestCase):
    def test_terra_medium_can_prepare_inline_review(self):
        current = current_task("ready_to_submit")
        current["inline_observer_binding"].update(model="gpt-6.1-terra", reasoning="medium")
        answer = HELPER.decide(current, native_event(current, preparation(current)))
        self.assertEqual(answer["action"], "verify_before_submit")
        self.assertEqual(answer["schedule_action"], "none")

    def test_terra_medium_can_own_existing_durable_workflow(self):
        current = state("ready_to_submit")
        current["web_io_binding"].update(model="gpt-6.1-terra", reasoning="medium")
        current["followup"] = followup(current)
        answer = HELPER.decide(current, preparation(current))
        self.assertEqual(answer["action"], "verify_before_submit")
        self.assertTrue(HELPER.web_io_binding(current))

    def test_existing_luna_route_is_preserved(self):
        current = current_task("ready_to_submit")
        answer = HELPER.decide(current, native_event(current, preparation(current)))
        self.assertEqual(answer["action"], "verify_before_submit")
        self.assertEqual(current["inline_observer_binding"]["model"], "gpt-6-luna")
        self.assertEqual(current["inline_observer_binding"]["reasoning"], "max")

    def test_wrong_pair_or_missing_runtime_evidence_cannot_pass(self):
        for changes in (
            {"model": "gpt-6.1-terra", "reasoning": "low"},
            {"model": "gpt-5.6-terra", "reasoning": "medium"},
            {"model": "gpt-6.1-terra", "reasoning": "medium", "runtime_pair_verified": False},
        ):
            with self.subTest(changes=changes):
                current = current_task("ready_to_submit")
                current["inline_observer_binding"].update(changes)
                answer = HELPER.decide(current, native_event(current, preparation(current)))
                self.assertEqual(answer["action"], "ensure_inline_luna")
                self.assertFalse(answer["submission_ready"])

    def test_explicit_operator_override_is_retained(self):
        current = current_task("ready_to_submit")
        current["inline_observer_binding"].update(
            model="gpt-6.1-terra", reasoning="ultra", route_basis="explicit_user",
            user_override_ref="authority/requested-computer-operation.md")
        answer = HELPER.decide(current, native_event(current, preparation(current)))
        self.assertEqual(answer["action"], "verify_before_submit")

    def test_general_computer_route_needs_selected_role_evidence(self):
        current = current_task("ready_to_submit")
        binding = current["inline_observer_binding"]
        binding.update(model="gpt-6.1-terra", reasoning="ultra",
                       task_kind="computer_operation", route_basis="explicit_skill_route")
        answer = HELPER.decide(current, native_event(current, preparation(current)))
        self.assertEqual(answer["action"], "ensure_inline_luna")
        binding["route_selection_ref"] = "routing/selected-computer-role.json"
        answer = HELPER.decide(current, native_event(current, preparation(current)))
        self.assertEqual(answer["action"], "verify_before_submit")

    def test_old_heartbeat_pair_does_not_verify_new_owner(self):
        current = state("ready_to_submit")
        current["web_io_binding"].update(model="gpt-6.1-terra", reasoning="medium")
        answer = HELPER.decide(current, preparation(current))
        self.assertEqual(answer["action"], "ensure_followup")
        self.assertFalse(answer["submission_ready"])

    def test_selected_skill_alias_is_preserved_across_packages(self):
        for effort in ("xhigh", "ultra"):
            with self.subTest(effort=effort):
                current = current_task("ready_to_submit")
                current["inline_observer_binding"].update(
                    model="gpt-6.1-terra", reasoning=effort,
                    route_basis="explicit_skill_route", task_kind="browser_operation",
                    route_selection_ref="routing/selected-workflow-role.json")
                answer = HELPER.decide(current, native_event(current, preparation(current)))
                self.assertEqual(answer["action"], "verify_before_submit")

    def test_alias_selection_and_current_execution_both_need_evidence(self):
        for changes in ({"route_selection_ref": ""}, {"runtime_pair_verified": False}):
            with self.subTest(changes=changes):
                current = current_task("ready_to_submit")
                binding = current["inline_observer_binding"]
                binding.update(model="gpt-6.1-terra", reasoning="xhigh",
                               route_basis="explicit_skill_route",
                               route_selection_ref="routing/selected-workflow-role.json")
                binding.update(changes)
                answer = HELPER.decide(current, native_event(current, preparation(current)))
                self.assertEqual(answer["action"], "ensure_inline_luna")
                self.assertFalse(answer["submission_ready"])

    def test_recovery_instruction_names_the_selected_web_io_role(self):
        current = state("ready_to_submit")
        binding = current["web_io_binding"]
        binding.update(model="gpt-6.1-terra", reasoning="medium")
        event = preparation(current)
        event.update(type="bind_web_io", web_io_binding=binding)
        answer = HELPER.decide(current, event)
        self.assertNotIn("Luna", answer["reason"])
        self.assertIn("Web IO", answer["reason"])


if __name__ == "__main__":
    unittest.main()
