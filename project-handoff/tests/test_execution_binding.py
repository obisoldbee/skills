"""Retained choices and actual execution identity, rather than prompt labels."""

import copy
from pathlib import Path
import sys
import unittest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
from validate_execution_binding import validate_binding


class ExecutionBindingTests(unittest.TestCase):
    def selection(self):
        return {"scope_id": "independent-review", "selection_ref": "authority/original-review-route.json",
                "model": "gpt-6.1-sol", "model_basis": "explicit_skill_route",
                "reasoning": "max", "reasoning_basis": "explicit_skill_route", "surface": "visible_thread"}

    def actual(self):
        return {"scope_id": "independent-review", "execution_id": "visible-review-thread",
                "surface": "visible_thread", "actual_tool": "codex_app__read_thread",
                "model": "gpt-6.1-sol", "reasoning": "max",
                "metadata_source": "runtime_metadata", "evidence_ref": "runtime/actual-review-pair.json"}

    def test_simplification_cannot_erase_selected_axes_or_visible_surface(self):
        original = self.selection()
        merged = {"scope_id": original["scope_id"], "selection_ref": "changes/role-merge.json",
                  "surface": "internal_agent", "model_basis": "platform_default", "reasoning_basis": "platform_default"}
        report = validate_binding(merged, {**self.actual(), "surface": "internal_agent",
                                          "actual_tool": "collaboration.spawn_agent", "reasoning": "low"}, original)
        self.assertFalse(report["valid"])
        for axis in ("model", "reasoning", "surface"):
            self.assertIn("selection_lost_or_changed: " + axis, report["errors"])

    def test_actual_returned_child_low_effort_cannot_satisfy_sol_max(self):
        actual = {**self.actual(), "surface": "internal_agent", "execution_id": "/root/local-helper",
                  "actual_tool": "collaboration.spawn_agent", "reasoning": "low"}
        report = validate_binding(self.selection(), actual)
        self.assertFalse(report["execution_verified"])
        self.assertIn("actual_reasoning_mismatch", report["errors"])
        self.assertIn("actual_surface_mismatch", report["errors"])

    def test_requested_arguments_or_prompt_self_claim_are_not_actual_metadata(self):
        for source in ("prompt", "requested_arguments", "create_parameters"):
            self.assertFalse(validate_binding(self.selection(), {**self.actual(), "metadata_source": source})["valid"])
        self.assertTrue(validate_binding(self.selection(), self.actual())["execution_verified"])
        for report in (validate_binding(self.selection(), self.actual()), validate_binding(None, self.actual())):
            self.assertFalse(report["runtime_verified_by_helper"])
            self.assertFalse(report["authority_verified"])

    def test_raw_visible_native_null_agent_path_is_preserved_and_hidden_path_is_rejected(self):
        actual = {**self.actual(), "agent_path": None}
        self.assertTrue(validate_binding(self.selection(), actual)["valid"])
        self.assertIn("agent_path", actual)
        self.assertIsNone(actual["agent_path"])
        for key in ("agent_path", "agentPath", "agentThreadId"):
            self.assertFalse(validate_binding(self.selection(), {**actual, key: "/root/hidden"})["valid"])

    def test_internal_helpers_and_unselected_effort_remain_allowed(self):
        selected = {"scope_id": "helper", "selection_ref": "scope/helper.json", "surface": "internal_agent",
                    "model_basis": "platform_default", "reasoning_basis": "platform_default"}
        actual = {**self.actual(), "scope_id": "helper", "surface": "internal_agent",
                  "execution_id": "/root/helper", "actual_tool": "collaboration.spawn_agent", "reasoning": "low"}
        self.assertTrue(validate_binding(selected, actual)["valid"])
        selected.update(model="gpt-6.1-sol", model_basis="explicit_user")
        self.assertTrue(validate_binding(selected, actual)["valid"])
        selected["reasoning"] = "max"
        self.assertIn("silent_default_override: reasoning", validate_binding(selected, actual)["errors"])

    def test_role_merge_is_not_human_route_change_and_direct_change_is_axis_bound(self):
        original = self.selection()
        merged = {**copy.deepcopy(original), "surface": "internal_agent"}
        actual = {**self.actual(), "surface": "internal_agent", "actual_tool": "collaboration.spawn_agent"}
        merged["user_route_change"] = {"author_is_human": False, "user_instruction_ref": "heartbeat/continue", "axes": ["surface"]}
        self.assertFalse(validate_binding(merged, actual, original)["valid"])
        merged["user_route_change"].update(author_is_human=True, user_instruction_ref="authority/direct-change.json")
        self.assertTrue(validate_binding(merged, actual, original)["valid"])


if __name__ == "__main__":
    unittest.main()
