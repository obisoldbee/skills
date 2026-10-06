"""Browser driver, readiness, historical owner and bounded notification behavior."""

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_review_cycle import HELPER, ROOT, apply, event, followup, observation, state, submission
from test_scheduler import authorized, collected, delivery, notification_check, scheduled, recovery

SPEC = importlib.util.spec_from_file_location("browser_binding", ROOT / "scripts/validate_browser_binding.py")
BROWSER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(BROWSER)


class BrowserBindingTests(unittest.TestCase):
    def binding(self):
        return {"runtime": "ego-browser", "control_entry": "ego-browser nodejs:TaskSpace/Page",
                "control_tool": "exec_command",
                "execution_host": "browser-host", "target_id": "91", "page_id": "p1",
                "conversation_url": "https://chatgpt.com/c/original", "evidence_ref": "ui/owned-page.json"}

    def actual(self, **fields):
        return {**self.binding(), "ownership": "agent", "actual_tool": "exec_command",
                "call_evidence_ref": "tool-calls/actual-ego-nodejs.json", **fields}

    def test_missing_space_does_not_switch_to_cua_driver(self):
        binding = self.binding()
        actual = self.actual(control_entry="mcp__cua_repl", actual_tool="mcp__cua_repl__js")
        rejected = BROWSER.validate_binding(binding, actual)
        self.assertFalse(rejected["valid"])
        self.assertEqual(rejected["next_action"], "reload_browser_binding")
        self.assertIsNone(rejected["binding_update"])

    def test_documented_page_visual_controls_remain_valid(self):
        for operation in ("screenshot", "mouse", "keyboard", "DOM"):
            actual = self.actual(operation=operation)
            self.assertTrue(BROWSER.validate_binding(self.binding(), actual)["valid"])

    def test_claimed_ego_driver_cannot_hide_actual_cua_or_native_app_call(self):
        for actual_tool in ("mcp__cua_repl__js", "cua.getApp", "getApp"):
            self.assertFalse(BROWSER.validate_binding(self.binding(), self.actual(actual_tool=actual_tool))["valid"])
        self.assertFalse(BROWSER.validate_binding(self.binding(), self.actual(call_evidence_ref=""))["valid"])
        selected = {**self.binding(), "runtime": "iab", "control_entry": "cua IAB tab", "control_tool": "mcp__cua_repl__js"}
        actual = {**selected, "actual_tool": "mcp__cua_repl__js", "call_evidence_ref": "tool-calls/iab.json", "ownership": "agent"}
        self.assertTrue(BROWSER.validate_binding(selected, actual)["valid"])
        self.assertFalse(BROWSER.validate_binding(selected, {**actual, "actual_tool": "mcp__another_runtime__js"})["valid"])
        self.assertTrue(BROWSER.validate_binding(self.binding(), self.actual(actual_tool="tools.exec_command"))["valid"])

    def test_recovered_target_retains_driver_and_requires_current_ownership(self):
        binding = self.binding()
        actual = self.actual(target_id="92", page_id="p2", evidence_ref="ui/restored.json")
        recovery = {"old_target_id": "91", "old_page_id": "p1", "new_target_id": "92", "new_page_id": "p2",
                    "runtime_recovery_permitted": True, "recovery_basis_ref": "runtime/current-skill.json",
                    "original_request_readback_ref": "ui/original-request.json"}
        self.assertFalse(BROWSER.validate_binding(binding, actual)["valid"])
        self.assertEqual(BROWSER.validate_binding(binding, actual, recovery)["binding_update"], actual)
        for changes in ({"ownership": "user"}, {"control_entry": "mcp__cua_repl"},
                        {"conversation_url": "https://chatgpt.com/c/other"}):
            self.assertFalse(BROWSER.validate_binding(binding, {**actual, **changes}, recovery)["valid"])

    def test_legacy_missing_binding_requests_reload_without_granting_authority(self):
        report = BROWSER.validate_binding(None, self.actual())
        self.assertEqual(report["next_action"], "reload_browser_binding")
        self.assertNotEqual(report["next_action"], "request_user_permission")
        self.assertFalse(report["runtime_verified_by_helper"])
        self.assertFalse(report["authority_verified"])

    def test_controller_check_persists_binding_and_recovery_rejects_actual_driver_change(self):
        current = state("submitting")
        current = apply(current, HELPER.decide(current, submission(current)))
        selected = {**self.binding(), "conversation_url": current["conversation_url"]}
        actual = {**self.actual(), "conversation_url": current["conversation_url"]}
        checked = HELPER.decide(current, event(current, "browser_driver_check",
            browser_execution_binding=selected, browser_actual=actual))
        self.assertEqual(checked["action"], "use_selected_browser_driver")
        current = apply(current, checked)
        current["browser_recovery_attempts"] = 1
        actual = {**actual, "target_id": "92", "page_id": "p2"}
        mapping = {"old_target_id": "91", "old_page_id": "p1", "new_target_id": "92", "new_page_id": "p2",
            "runtime_recovery_permitted": True, "recovery_basis_ref": "runtime/current-skill.json",
            "original_request_readback_ref": "ui/original-request.json"}
        incoming = recovery(current, 20, old_space_id="91", browser_context={"space_id": "92", "page_label": "p2", "ownership": "agent"},
            browser_actual=actual, browser_driver_recovery=mapping)
        rejected = HELPER.decide(current, {**incoming, "browser_actual": {**actual, "actual_tool": "mcp__cua_repl__js"}})
        self.assertEqual(rejected["action"], "reload_browser_binding")
        self.assertNotIn("browser_recovery_attempts", rejected["state_updates"])
        restored = HELPER.decide(current, incoming)
        self.assertEqual(restored["state_updates"]["browser_execution_binding"], actual)
        self.assertEqual(restored["state_updates"]["browser_recovery_attempts"], 0)
        local = HELPER.decide(current, observation(current))
        self.assertNotEqual(local["action"], "reload_browser_binding")


class ReadinessAndExistingOwnerTests(unittest.TestCase):
    def checkpoint(self, current, **fields):
        return event(current, "followup_check", checkpoint="before_submit", observed_at="2026-01-01T00:00:20+00:00", **fields)

    def test_valid_cli_input_with_followup_gap_is_not_submit_ready(self):
        current = authorized(state("ready_to_submit"))
        current["followup"] = followup(current, status="PAUSED")
        incoming = self.checkpoint(current)
        with tempfile.TemporaryDirectory() as directory:
            paths = [Path(directory) / name for name in ("state.json", "event.json")]
            for path, data in zip(paths, (current, incoming)):
                path.write_text(json.dumps(data), encoding="utf-8")
            run = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/next_action.py"),
                                  "--state", str(paths[0]), "--event", str(paths[1])], capture_output=True, text=True)
            report = json.loads(run.stdout)
        self.assertEqual(run.returncode, 0)
        self.assertTrue(report["valid"])
        self.assertTrue(report["input_valid"])
        self.assertFalse(report["submission_ready"])
        self.assertEqual(report["action"], "ensure_followup")

    def test_fresh_rearm_view_proposes_same_id_atomic_state_update(self):
        current = authorized(state("ready_to_submit"))
        current["followup"] = followup(current, status="PAUSED", checked_seconds=0, evidence_ref="paused-view")
        view = followup(current, checked_seconds=20, evidence_ref="actual-rearmed-view")
        report = HELPER.decide(current, self.checkpoint(current, followup_view=view))
        self.assertEqual(report["action"], "followup_ready")
        self.assertTrue(report["submission_ready"])
        self.assertEqual(report["state_updates"]["followup"], view)
        self.assertEqual(current["followup"]["status"], "PAUSED")
        for changed in ({"checked_at": current["followup"]["checked_at"]},
                        {"evidence_ref": current["followup"]["evidence_ref"]},
                        {"automation_id": "another-heartbeat", "active_automation_ids": ["another-heartbeat"]},
                        {"active_automation_ids": ["heartbeat-1", "duplicate"]}):
            rejected = HELPER.decide(current, self.checkpoint(current, followup_view={**view, **changed}))
            self.assertEqual(rejected["action"], "ensure_followup")
            self.assertFalse(rejected["submission_ready"])
        self.assertIsNone(HELPER.current_followup(current, {"observed_at": "2026-01-01T00:00:20+00:00",
            "followup_view": {**view, "evidence_ref": "paused-view"}}))

    def test_verified_historical_existing_luna_is_reused_without_old_new_creation(self):
        current = state()
        binding = {**current["web_io_binding"], "model": "gpt-5.6-luna", "route_basis": "verified_existing_task"}
        readback = {key: binding[key] for key in ("thread_id", "host_id", "model", "reasoning")}
        binding["existing_task_readback"] = {**readback, "operation": "reuse_existing", "metadata_source": "runtime_metadata",
                "ready": True, "archived": False, "agent_path": None, "evidence_ref": "runtime/existing-luna.json",
                "observed_at": binding["verified_at"]}
        report = HELPER.decide(current, event(current, "bind_web_io", web_io_binding=binding))
        self.assertEqual(report["state_updates"]["web_io_binding"]["model"], "gpt-5.6-luna")
        current = apply(current, report)
        current["followup"] = followup(current)
        self.assertIsNotNone(HELPER.current_followup(current, {"observed_at": "2026-01-01T00:00:20+00:00",
            "followup_view": followup(current, checked_seconds=20, evidence_ref="existing-luna-view")}, fresh_view=True))
        for changes in ({"existing_task_readback": {}}, {"surface": "internal_agent"}, {"reasoning": "low"},
                        {"model": "gpt-5.6-sol"}, {"route_basis": "explicit_skill_route"}):
            self.assertFalse(HELPER.web_io_binding(current, {**binding, **changes}))
        for changes in ({"metadata_source": "prompt"}, {"operation": "initial_dispatch"}, {"thread_id": "different"}, {"archived": True}):
            self.assertFalse(HELPER.web_io_binding(current, {**binding, "existing_task_readback": {**binding["existing_task_readback"], **changes}}))


class NotificationPolicyTests(unittest.TestCase):
    def limited(self, triggers=None):
        current = authorized(state())
        current["controller_notification_authorization"]["policy"].update(
            max_deliveries=1, triggers=triggers or ["stable_reply", "actionable_progress"])
        return current

    def test_unknown_legacy_policy_retains_receipt_for_faithful_mapping(self):
        current = authorized(state())
        del current["controller_notification_authorization"]["policy"]
        full = collected(current)
        self.assertEqual(full["action"], "map_notification_policy")
        payload = copy.deepcopy(full["controller_event"])
        current = apply(current, HELPER.decide(current, payload, full["observer_updates"]))
        self.assertEqual(current["phase"], "review_ready")
        mapped = authorized(state())
        sent = HELPER.decide(mapped, notification_check(mapped, 20), full["observer_updates"])
        self.assertEqual(sent["action"], "notify_controller")
        self.assertEqual(sent["controller_event"], payload)

    def test_one_message_limit_blocks_second_send_and_preserves_local_review(self):
        current = self.limited()
        progress = HELPER.decide(current, scheduled(current, generation="generating", actionable_progress=True,
            actionable_progress_ref="ui/real-progress.json"))
        ledger = HELPER.decide(current, delivery(current, progress["notification_key"], "delivered", 1), progress["observer_updates"])["observer_updates"]
        current = apply(current, HELPER.decide(current, progress["controller_event"], ledger))
        first = HELPER.decide(current, scheduled(current, 10), ledger)
        full = HELPER.decide(current, scheduled(current, 20), first["observer_updates"])
        self.assertEqual(full["action"], "save_receipt_for_controller")
        self.assertFalse(full["activate_controller"])
        self.assertEqual(len(full["observer_updates"]["notifications"]), 2)
        current = apply(current, HELPER.decide(current, full["controller_event"], full["observer_updates"]))
        self.assertEqual(current["phase"], "review_ready")
        assessed = HELPER.decide(current, event(current, "assessment", review_message_id="message-1", coverage_complete=True,
            confirmed_findings=0, unresolved_claims=0), full["observer_updates"])
        self.assertNotIn(assessed["action"], {"map_notification_policy", "ensure_result_return"})
        replay = HELPER.decide(current, notification_check(current, 30), full["observer_updates"])
        self.assertFalse(replay["activate_controller"])

    def test_history_and_reservations_keep_one_message_limit_across_rounds(self):
        current = self.limited()
        full = collected(current)
        ledger = full["observer_updates"]
        current["round"] = 2
        current["request_token"] = "test-round-2"
        current["used_request_tokens"].append("test-round-2")
        first = HELPER.decide(current, scheduled(current, 30), ledger)
        second = HELPER.decide(current, scheduled(current, 40), first["observer_updates"])
        self.assertEqual(second["action"], "save_receipt_for_controller")
        self.assertEqual(second["observer_updates"]["notification_history"][0]["controller_event"], full["controller_event"])

    def test_unknown_delivery_reserves_once_and_actual_failed_delivery_releases_only_unsent_slot(self):
        current = self.limited()
        progress = HELPER.decide(current, scheduled(current, generation="generating", actionable_progress=True,
            actionable_progress_ref="ui/progress.json"))
        unknown = HELPER.decide(current, delivery(current, progress["notification_key"], "unknown", 1), progress["observer_updates"])
        self.assertFalse(HELPER.notification_authorized(current, unknown["observer_updates"]))
        check = HELPER.decide(current, notification_check(current, 70), unknown["observer_updates"])
        self.assertFalse(check["activate_controller"])
        self.assertEqual(check["observer_updates"]["notifications"][0]["attempts"], 1)
        failed = HELPER.decide(current, delivery(current, progress["notification_key"], "not_delivered", 71), check["observer_updates"])
        self.assertTrue(HELPER.notification_authorized(current, failed["observer_updates"]))
        first = HELPER.decide(current, scheduled(current, 80), failed["observer_updates"])
        full = HELPER.decide(current, scheduled(current, 90), first["observer_updates"])
        self.assertEqual(full["action"], "notify_controller")

    def test_same_actual_delivery_readback_is_idempotent_and_never_allows_second_send(self):
        current = self.limited()
        full = collected(current)
        incoming = delivery(current, full["notification_key"], "delivered", 11)
        ledger = HELPER.decide(current, incoming, full["observer_updates"])["observer_updates"]
        replay = HELPER.decide(current, incoming, ledger)
        self.assertEqual(replay["observer_updates"], ledger)
        self.assertEqual(ledger["notifications"][0]["attempts"], 1)
        self.assertFalse(HELPER.notification_authorized(current, ledger))
        check = HELPER.decide(current, notification_check(current, 80), ledger)
        self.assertFalse(check["activate_controller"])
        self.assertEqual(check["controller_event"], None)

    def test_stable_interrupted_reply_is_collected_but_not_review_completed(self):
        current = self.limited(["review_completed"])
        current["execution_scope"] = "review_only"
        full = collected(current)
        self.assertEqual(full["action"], "save_receipt_for_controller")
        self.assertTrue(full["observer_updates"]["text_complete"])
        self.assertEqual(full["observer_updates"]["notifications"][0]["attempts"], 0)
        self.assertTrue(HELPER.notification_authorized(current, full["observer_updates"]))
        current = apply(current, HELPER.decide(current, full["controller_event"], full["observer_updates"]))
        qa = HELPER.decide(current, event(current, "assessment", review_message_id="message-1", coverage_complete=False,
            next_request_token="followup-incomplete-review"), full["observer_updates"])
        self.assertFalse(qa["terminal"])
        self.assertEqual(qa["phase"], "ready_to_submit")
        self.assertFalse(HELPER.notification_authorized(current, full["observer_updates"], trigger="stable_reply"))

    def test_completion_only_once_is_a_future_return_route_before_submission_and_turn_end(self):
        current = self.limited(["review_completed"])
        for checkpoint in ("before_submit", "turn_end"):
            current["phase"] = "ready_to_submit" if checkpoint == "before_submit" else "waiting_web"
            incoming = event(current, "followup_check", checkpoint=checkpoint, observed_at="2026-01-01T00:00:20+00:00",
                followup_view=followup(current, checked_seconds=20, evidence_ref="fresh-" + checkpoint))
            ready = HELPER.decide(current, incoming)
            self.assertEqual(ready["action"], "followup_ready")
            self.assertEqual(ready["submission_ready"], checkpoint == "before_submit")

    def test_collected_requested_report_notifies_before_controller_receipt_or_qa(self):
        current = self.limited(["review_completed"])
        current["execution_scope"] = "review_only"
        current["submitted_user_message_id"] = "user-message"
        current["prepared_request"]["requirements_ref"] = "source/original-review-request.md"
        proof = {"complete": True, "requirements_ref": "source/original-review-request.md",
            "body_sha256": "c" * 64, "evidence_ref": "ui/full-requested-report-coverage.json"}
        first = HELPER.decide(current, scheduled(current, requested_output_collection=proof))
        full = HELPER.decide(current, scheduled(current, 10, requested_output_collection=proof), first["observer_updates"])
        self.assertEqual(full["action"], "notify_controller")
        self.assertEqual(current["phase"], "waiting_web")
        self.assertNotIn("review", current)
        self.assertNotIn("received_notifications", current)
        self.assertEqual(full["observer_updates"]["notifications"][0]["attempts"], 1)
        for changes in ({"body_sha256": "d" * 64}, {"requirements_ref": "unrelated-request.md"}, {"complete": False}):
            first = HELPER.decide(current, scheduled(current, requested_output_collection={**proof, **changes}))
            bad = HELPER.decide(current, scheduled(current, 10, requested_output_collection={**proof, **changes}), first["observer_updates"])
            self.assertEqual(bad["action"], "save_receipt_for_controller")
            self.assertEqual(bad["observer_updates"]["notifications"][0]["attempts"], 0)
        interrupted = HELPER.decide(current, scheduled(current, requested_output_collection=proof, response_interrupted=True))
        stopped = HELPER.decide(current, scheduled(current, 10, requested_output_collection=proof, response_interrupted=True), interrupted["observer_updates"])
        self.assertEqual(stopped["action"], "save_receipt_for_controller")
        self.assertEqual(stopped["observer_updates"]["notifications"][0]["attempts"], 0)

    def test_exhausted_send_authority_requires_real_return_only_when_leaving(self):
        current = self.limited()
        progress = HELPER.decide(current, scheduled(current, generation="generating", actionable_progress=True,
            actionable_progress_ref="ui/progress.json"))
        current = apply(current, HELPER.decide(current, progress["controller_event"], progress["observer_updates"]))
        incoming = event(current, "followup_check", checkpoint="turn_end", observed_at="2026-01-01T00:00:20+00:00",
            followup_view=followup(current, checked_seconds=20, evidence_ref="fresh-view"))
        self.assertEqual(HELPER.decide(current, incoming, progress["observer_updates"])["action"], "ensure_result_return")
        current["controller_result_return"] = {"kind": "verified_dispatcher", "verified": True,
            "evidence_ref": "runtime/actual-return.json", "destination_thread_id": current["controller_thread_id"],
            "destination_host": current["controller_host"]}
        self.assertEqual(HELPER.decide(current, incoming, progress["observer_updates"])["action"], "followup_ready")


if __name__ == "__main__":
    unittest.main()
