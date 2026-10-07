"""Browser driver, readiness, historical owner and bounded notification behavior."""

import copy
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_review_cycle import (HELPER, ROOT, apply, event, followup, observation, preparation,
                               receipt, state, submission, with_required)
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
        self.assertFalse(report["submission_ready"])
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

    def prepared_checkpoint(self):
        current = authorized(state("ready_to_submit"))
        current["followup"] = followup(current, status="PAUSED", checked_seconds=0, evidence_ref="paused-view")
        view = followup(current, checked_seconds=20, evidence_ref="actual-before-submit-view")
        checked = HELPER.decide(current, self.checkpoint(current, followup_view=view))
        self.assertFalse(checked["submission_ready"])
        return apply(current, checked), view

    def test_before_submit_can_reuse_the_exact_fresh_checkpoint_view_once(self):
        current, view = self.prepared_checkpoint()
        original = copy.deepcopy(view)
        incoming = {**submission(current), "status": "not_sent", "definitive_absence": True,
                    "observed_at": "2026-01-01T00:00:21+00:00", "followup_view": copy.deepcopy(view)}
        report = HELPER.decide(current, incoming)
        self.assertEqual(report["action"], "submit_once")
        self.assertTrue(report["submission_ready"])
        current = apply(current, report)
        self.assertIsNone(current["pre_submission_followup"])
        repeat = HELPER.decide(current, incoming)
        self.assertFalse(repeat["submission_ready"])
        self.assertEqual(repeat["action"], "ensure_followup")
        sent = HELPER.decide(current, {**submission(current), "observed_at": "2026-01-01T00:00:22+00:00",
                                     "followup_view": view})
        self.assertEqual(sent["action"], "watch")
        self.assertEqual(view, original)

    def test_checkpoint_reuse_preserves_freshness_owner_run_and_prompt_binding(self):
        current, view = self.prepared_checkpoint()
        incoming = {**submission(current), "status": "not_sent", "definitive_absence": True,
                    "observed_at": "2026-01-01T00:00:21+00:00", "followup_view": view}
        expired = HELPER.decide(current, {**incoming, "observed_at": "2026-01-01T00:10:21+00:00"})
        self.assertFalse(expired["submission_ready"])
        for change in ({"status": "PAUSED", "next_check_at": None, "active_automation_ids": []},
                       {"owner_thread_id": "other-owner"}, {"run_id": "other-run"}):
            with self.subTest(change=change):
                rejected = HELPER.decide(current, {**incoming, "followup_view": {**view, **change}})
                self.assertFalse(rejected["submission_ready"])
        for changes in ({"round": 2}, {"source_id": "git:" + "d" * 40}, {"request_token": "another-round"}):
            self.assertFalse(HELPER.reusable_submission_followup({**current, **changes}, incoming))
        altered = copy.deepcopy(current)
        altered["prepared_request"]["sha256"] = "d" * 64
        self.assertFalse(HELPER.decide(altered, incoming)["submission_ready"])
        for change in ({"evidence_ref": "renamed-old-view"}, {"checked_at": "2026-01-01T00:00:21+00:00"}):
            self.assertFalse(HELPER.reusable_submission_followup(current, {**incoming, "followup_view": {**view, **change}}))
        self.assertFalse(HELPER.reusable_submission_followup(state("ready_to_submit"), incoming))

    def test_unknown_submission_discards_checkpoint_reuse_and_never_grants_a_send(self):
        current, view = self.prepared_checkpoint()
        unknown = HELPER.decide(current, {**submission(current), "status": "unknown",
            "observed_at": "2026-01-01T00:00:21+00:00", "followup_view": view})
        self.assertEqual(unknown["action"], "reconcile_submission")
        self.assertFalse(unknown["submission_ready"])
        current = apply(current, unknown)
        self.assertIsNone(current["pre_submission_followup"])
        unresolved = HELPER.decide(current, {**submission(current), "status": "not_sent", "definitive_absence": True,
            "observed_at": "2026-01-01T00:00:22+00:00", "followup_view": view})
        self.assertFalse(unresolved["submission_ready"])

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
            self.assertFalse(ready["submission_ready"])

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


class WebReviewRegressionTests(unittest.TestCase):
    """Independent review counterexamples: ordering must not change authority."""

    def current(self):
        current = authorized(state())
        current["prepared_request"]["requirements_ref"] = "source/original-review-request.md"
        current["submitted_user_message_id"] = "user-message"
        current["controller_notification_authorization"]["policy"].update(
            max_deliveries=1, triggers=["review_completed"])
        return current

    def proof(self, current):
        return {"complete": True, "requirements_ref": current["prepared_request"]["requirements_ref"],
                "body_sha256": "c" * 64, "evidence_ref": "coverage/same-original-report.json"}

    def full(self, current, proof=True):
        fields = {"requested_output_collection": self.proof(current)} if proof else {}
        first = HELPER.decide(current, scheduled(current, **fields))
        return HELPER.decide(current, scheduled(current, 10, **fields), first["observer_updates"])

    def retried(self):
        current = self.current()
        full = self.full(current)
        key = full["notification_key"]
        first_id = full.get("notification_attempt_id", "attempt-1")
        failed_event = {**delivery(current, key, "not_delivered", 11), "attempt_id": first_id,
                        "attempted_at": full["observer_updates"]["notifications"][0]["attempted_at"]}
        failed = HELPER.decide(current, failed_event, full["observer_updates"])
        pending = failed["observer_updates"]["notifications"][0]
        retry = HELPER.decide(current, notification_check(current, 72,
            destination_thread_id=current["controller_thread_id"], destination_host=current["controller_host"],
            destination_status="idle", readback_observed_at="2026-01-01T00:01:12+00:00",
            readback_evidence_ref="transport/restored.json",
            write_endpoint_recovery={"notification_key": key, "receipt_sha256": pending["receipt_sha256"],
                "attempted_at": pending["attempted_at"], "evidence_ref": "transport/restored.json"}),
            failed["observer_updates"])
        self.assertEqual(retry["action"], "retry_notification")
        return current, full, failed_event, retry

    def test_old_attempt_failure_cannot_release_delivered_notification_allowance(self):
        current, full, failed_event, retry = self.retried()
        key = full["notification_key"]
        second_id = retry.get("notification_attempt_id", "attempt-2")
        delivered = HELPER.decide(current, {**delivery(current, key, "delivered", 73),
            "attempt_id": second_id}, retry["observer_updates"])
        late = HELPER.decide(current, {**failed_event, "observed_at": "2026-01-01T00:01:14+00:00"},
                            delivered["observer_updates"])
        self.assertEqual(late["observer_updates"]["notifications"][0]["delivery_status"], "delivered")
        self.assertEqual(late["observer_updates"]["notifications"][0]["delivery_observed_at"],
                         delivered["observer_updates"]["notifications"][0]["delivery_observed_at"])
        self.assertFalse(HELPER.notification_authorized(current, late["observer_updates"]))
        current["round"] = 2
        current["request_token"] = "same-authority-round-2"
        current["used_request_tokens"].append(current["request_token"])
        first = HELPER.decide(current, scheduled(current, 80, requested_output_collection=self.proof(current)),
                              late["observer_updates"])
        second = HELPER.decide(current, scheduled(current, 90, requested_output_collection=self.proof(current)),
                               first["observer_updates"])
        self.assertEqual(second["action"], "save_receipt_for_controller")

    def test_old_rejection_cannot_clear_unknown_retry_or_invent_a_third_attempt(self):
        current, full, failed_event, retry = self.retried()
        second_id = retry["notification_attempt_id"]
        self.assertNotEqual(second_id, failed_event["attempt_id"])
        unknown = HELPER.decide(current, {**delivery(current, full["notification_key"], "unknown", 73),
            "attempt_id": second_id}, retry["observer_updates"])
        late = HELPER.decide(current, {**failed_event, "observed_at": "2026-01-01T00:01:14+00:00"},
                            unknown["observer_updates"])
        self.assertEqual(late["observer_updates"]["notifications"][0]["delivery_status"], "unknown")
        self.assertEqual(late["observer_updates"]["notifications"][0]["next_check_at"],
                         unknown["observer_updates"]["notifications"][0]["next_check_at"])
        self.assertFalse(HELPER.notification_authorized(current, late["observer_updates"]))
        check = HELPER.decide(current, notification_check(current, 150), late["observer_updates"])
        self.assertFalse(check["activate_controller"])
        self.assertEqual(check["observer_updates"]["notifications"][0]["attempts"], 2)

    def test_retry_receipt_without_attempt_identity_requires_reconciliation(self):
        current, full, _, retry = self.retried()
        for fields in ({}, {"attempt_id": "unrelated-attempt"}):
            report = HELPER.decide(current, {**delivery(current, full["notification_key"], "not_delivered", 73),
                **fields}, retry["observer_updates"])
            self.assertEqual(report["action"], "reconcile_notification_attempt")
            self.assertEqual(report["observer_updates"]["notifications"], retry["observer_updates"]["notifications"])

    def test_late_collection_proof_unlocks_first_notification_without_replacing_payload(self):
        current = self.current()
        full = self.full(current, proof=False)
        self.assertEqual(full["action"], "save_receipt_for_controller")
        original = copy.deepcopy(full["controller_event"])
        original_digest = full["observer_updates"]["notifications"][0]["receipt_sha256"]
        late = HELPER.decide(current, scheduled(current, 20, requested_output_collection=self.proof(current)),
                            full["observer_updates"])
        self.assertEqual(late["action"], "notify_controller")
        self.assertEqual(late["controller_event"], original)
        self.assertEqual(late["observer_updates"]["notifications"][0]["receipt_sha256"], original_digest)
        self.assertEqual(late["observer_updates"]["notifications"][0]["attempts"], 1)

    def test_late_unknown_does_not_erase_definitive_failure_of_the_same_attempt(self):
        current = self.current()
        full = self.full(current)
        key = full["notification_key"]
        failed = HELPER.decide(current, delivery(current, key, "not_delivered", 11), full["observer_updates"])
        late = HELPER.decide(current, delivery(current, key, "unknown", 12), failed["observer_updates"])
        self.assertEqual(late["observer_updates"]["notifications"][0]["delivery_status"], "not_delivered")
        self.assertTrue(HELPER.notification_authorized(current, late["observer_updates"]))

    def test_receipt_check_can_append_collection_proof_without_webpage_or_duplicate_send(self):
        current = self.current()
        full = self.full(current, proof=False)
        item = full["observer_updates"]["notifications"][0]
        incoming = notification_check(current, 20, notification_key=item["key"],
            notification_receipt_sha256=item["receipt_sha256"], requested_output_collection=self.proof(current))
        late = HELPER.decide(current, incoming, full["observer_updates"])
        self.assertEqual(late["action"], "notify_controller")
        self.assertFalse(late["observe_webpage"])
        duplicate = HELPER.decide(current, {**incoming, "observed_at": "2026-01-01T00:00:30+00:00"},
                                  late["observer_updates"])
        self.assertFalse(duplicate["activate_controller"])
        self.assertEqual(len(duplicate["observer_updates"]["output_collection_proofs"]), 1)
        self.assertEqual(duplicate["observer_updates"]["notifications"][0]["attempts"], 1)

    def test_late_proof_cannot_rebind_body_requirements_receipt_or_interrupted_reply(self):
        current = self.current()
        full = self.full(current, proof=False)
        item = full["observer_updates"]["notifications"][0]
        for change in ({"body_sha256": "d" * 64}, {"requirements_ref": "other-request.md"},
                       {"evidence_ref": ""}, {"complete": False}):
            late = HELPER.decide(current, scheduled(current, 20,
                requested_output_collection={**self.proof(current), **change}), full["observer_updates"])
            self.assertFalse(late["activate_controller"])
            self.assertEqual(late["observer_updates"]["notifications"][0]["attempts"], 0)
        mismatched = HELPER.decide(current, notification_check(current, 20, notification_key=item["key"],
            notification_receipt_sha256="d" * 64, requested_output_collection=self.proof(current)), full["observer_updates"])
        self.assertFalse(mismatched["activate_controller"])
        first = HELPER.decide(current, scheduled(current, response_interrupted=True))
        stopped = HELPER.decide(current, scheduled(current, 10, response_interrupted=True), first["observer_updates"])
        late = HELPER.decide(current, scheduled(current, 20, requested_output_collection=self.proof(current)), stopped["observer_updates"])
        self.assertFalse(late["activate_controller"])

    def test_only_resolved_not_sent_gate_is_submission_ready(self):
        current = authorized(state("ready_to_submit"))
        ready = HELPER.decide(current, {**submission(current), "status": "not_sent", "definitive_absence": True})
        self.assertEqual(ready["action"], "submit_once")
        self.assertTrue(ready["submission_ready"])

    def test_unknown_send_stays_not_ready_when_heartbeat_is_rearmed(self):
        current = authorized(state("ready_to_submit"))
        unknown = HELPER.decide(current, {**submission(current), "status": "unknown"})
        current = apply(current, unknown)
        self.assertEqual(current["phase"], "submitting")
        ready = HELPER.decide(current, event(current, "followup_check", checkpoint="before_submit",
            observed_at="2026-01-01T00:00:20+00:00", followup_view=followup(current, checked_seconds=20,
                evidence_ref="actual-rearmed-unknown-send.json")))
        self.assertEqual(ready["action"], "followup_ready")
        self.assertFalse(ready["submission_ready"])

    def correction(self, current, ledger, seconds, complete_value, **fields):
        item = ledger["notifications"][0]
        return HELPER.decide(current, notification_check(current, seconds,
            notification_key=item["key"], notification_receipt_sha256=item["receipt_sha256"],
            requested_output_collection={**self.proof(current), "complete": complete_value,
                "evidence_ref": f"coverage/check-{seconds}.json", **fields}), ledger)

    def attachment(self, current, ledger, seconds):
        return HELPER.decide(current, event(current, "scheduled_artifacts", receipt=receipt(current),
            observed_at=scheduled(current, seconds)["observed_at"],
            followup_view=followup(current, checked_seconds=seconds, evidence_ref=f"artifact-view-{seconds}")), ledger)

    def test_negative_or_unknown_correction_blocks_until_a_new_positive_check(self):
        for complete in (False, None):
            with self.subTest(complete=complete):
                current = with_required(self.current())
                full = self.full(current)
                original = copy.deepcopy(full["controller_event"])
                negative = self.correction(current, full["observer_updates"], 20, complete)
                self.assertIs(negative["observer_updates"]["output_collection_proofs"][-1]["proof"]["complete"], complete)
                replay = self.correction(current, negative["observer_updates"], 21, True,
                                         **self.proof(current))
                attached = self.attachment(current, replay["observer_updates"], 30)
                self.assertFalse(attached["activate_controller"])
                self.assertEqual(attached["observer_updates"]["notifications"][0]["attempts"], 0)
                restored = self.correction(current, attached["observer_updates"], 40, True)
                self.assertEqual(restored["action"], "notify_controller")
                self.assertEqual(restored["controller_event"], original)

    def test_replayed_appended_positive_cannot_erase_a_later_negative(self):
        current = with_required(self.current())
        full = self.full(current, proof=False)
        positive = self.correction(current, full["observer_updates"], 20, True)
        negative = self.correction(current, positive["observer_updates"], 30, False)
        replay = self.correction(current, negative["observer_updates"], 40, True,
                                 evidence_ref="coverage/check-20.json")
        self.assertEqual(len(replay["observer_updates"]["output_collection_proofs"]), 2)
        attached = self.attachment(current, replay["observer_updates"], 50)
        self.assertFalse(attached["activate_controller"])
        self.assertEqual(self.correction(current, attached["observer_updates"], 60, True)["action"], "notify_controller")

    def test_scheduled_old_positive_does_not_replace_the_saved_baseline_or_correction(self):
        current = with_required(self.current())
        full = self.full(current)
        negative = self.correction(current, full["observer_updates"], 20, False)
        replay = HELPER.decide(current, scheduled(current, 21,
            requested_output_collection=self.proof(current)), negative["observer_updates"])
        attached = self.attachment(current, replay["observer_updates"], 30)
        self.assertFalse(attached["activate_controller"])
        self.assertEqual(self.correction(current, attached["observer_updates"], 40, True)["action"], "notify_controller")

    def test_evidence_time_conflict_and_older_positive_need_a_new_check(self):
        current = with_required(self.current())
        full = self.full(current)
        negative = self.correction(current, full["observer_updates"], 20, False)
        for second, proof_time in ((21, 15), (22, 20), (23, 20)):
            positive = self.correction(current, negative["observer_updates"], second, True,
                observed_at=scheduled(current, proof_time)["observed_at"])
            negative = positive
        attached = self.attachment(current, negative["observer_updates"], 30)
        self.assertFalse(attached["activate_controller"])
        self.assertEqual(self.correction(current, attached["observer_updates"], 40, True)["action"], "notify_controller")

    def test_unbound_or_future_negative_does_not_poison_a_valid_complete_proof(self):
        for fields in ({"body_sha256": "d" * 64}, {"requirements_ref": "other.md"},
                       {"evidence_ref": ""}, {"observed_at": "2026-01-01T00:01:00+00:00"},
                       {"complete": "unknown"}):
            with self.subTest(fields=fields):
                current = with_required(self.current())
                full = self.full(current)
                invalid = self.correction(current, full["observer_updates"], 20, False, **fields)
                attached = self.attachment(current, invalid["observer_updates"], 30)
                self.assertTrue(attached["activate_controller"])

    def test_actual_delivery_survives_a_later_incomplete_correction(self):
        current = self.current()
        full = self.full(current)
        correction = self.correction(current, full["observer_updates"], 20, False)
        delivered = HELPER.decide(current, {**delivery(current, full["notification_key"], "delivered", 21),
            "attempt_id": full["notification_attempt_id"]}, correction["observer_updates"])
        denied = self.correction(current, delivered["observer_updates"], 22, None)
        item = denied["observer_updates"]["notifications"][0]
        self.assertTrue(item["delivery_accepted"])
        self.assertEqual(item["delivery_status"], "delivered")
        self.assertEqual(item["attempts"], 1)
        self.assertFalse(denied["activate_controller"])

    def archived_attempt(self, status="unknown"):
        current = self.current()
        current["execution_scope"] = "review_only"
        full = self.full(current)
        settled = HELPER.decide(current, {**delivery(current, full["notification_key"], status, 12),
            "attempt_id": full["notification_attempt_id"]}, full["observer_updates"])
        ledger = settled["observer_updates"]
        current = apply(current, HELPER.decide(current, full["controller_event"], ledger))
        current = apply(current, HELPER.decide(current, event(current, "assessment",
            review_message_id=full["controller_event"]["assistant_message_id"], coverage_complete=False,
            next_request_token="corrected-round-2"), ledger))
        prepared = {**preparation(current), "requirements_ref": "source/original-review-request.md",
                    "observed_at": scheduled(current, 100)["observed_at"]}
        current = apply(current, HELPER.decide(current, prepared, ledger))
        current = apply(current, HELPER.decide(current, {**submission(current),
            "user_message_id": "user-message-r2", "observed_at": scheduled(current, 110)["observed_at"],
            "followup_view": followup(current, checked_seconds=110, evidence_ref="round2-send-view")}, ledger))
        first = HELPER.decide(current, scheduled(current, 120, assistant_message_id="message-2",
            requested_output_collection=self.proof(current)), ledger)
        second = HELPER.decide(current, scheduled(current, 130, assistant_message_id="message-2",
            requested_output_collection=self.proof(current)), first["observer_updates"])
        self.assertEqual(second["action"], "save_receipt_for_controller")
        incoming = {**delivery(current, full["notification_key"], "not_delivered", 140),
                    "attempt_id": full["notification_attempt_id"],
                    "notification_receipt_sha256": full["controller_event"]["notification_receipt_sha256"]}
        return current, second["observer_updates"], incoming, full["controller_event"]

    def test_history_receipt_closes_only_the_original_attempt_and_unlocks_current_once(self):
        current, ledger, incoming, original = self.archived_attempt()
        before = copy.deepcopy(ledger["notifications"])
        reconciled = HELPER.decide(current, incoming, ledger)
        saved = reconciled["observer_updates"]
        self.assertEqual(reconciled["state_updates"], {})
        self.assertEqual(saved["notifications"], before)
        self.assertEqual(saved["notification_history"][0]["controller_event"], original)
        self.assertEqual(saved["notification_history"][0]["delivery_status"], "not_delivered")
        duplicate = HELPER.decide(current, incoming, saved)
        self.assertEqual(duplicate["observer_updates"]["notification_history"], saved["notification_history"])
        first = HELPER.decide(current, notification_check(current, 150), saved)
        self.assertEqual(first["action"], "notify_controller")
        self.assertEqual(first["controller_event"], before[0]["controller_event"])
        second = HELPER.decide(current, notification_check(current, 151), first["observer_updates"])
        self.assertFalse(second["activate_controller"])

    def test_history_reconciliation_rejects_bad_identity_and_never_applies_old_business(self):
        current, ledger, incoming, original = self.archived_attempt()
        for fields in ({"notification_receipt_sha256": "d" * 64}, {"destination_host": "other-host"},
                       {"destination_thread_id": "other-thread"}, {"run_id": "other-run"},
                       {"round": 1}, {"attempt_id": None}):
            with self.subTest(fields=fields):
                with self.assertRaises(ValueError):
                    HELPER.decide(current, {**incoming, **fields}, copy.deepcopy(ledger))
        with self.assertRaisesRegex(ValueError, "stale or mismatched round"):
            HELPER.decide(current, original, ledger)
        bad_attempt = HELPER.decide(current, {**incoming, "attempt_id": "unrelated"}, ledger)
        self.assertEqual(bad_attempt["action"], "reconcile_notification_attempt")
        self.assertEqual(bad_attempt["observer_updates"]["notification_history"], ledger["notification_history"])
        for change in ("payload", "binding", "duplicate-key"):
            candidate = copy.deepcopy(ledger)
            old = candidate["notification_history"][0]
            if change == "payload":
                old["controller_event"]["source_id"] = "git:" + "d" * 40
            elif change == "binding":
                old["notification_binding"]["request_token"] = "unrecognized-token"
            else:
                candidate["notification_history"].append(copy.deepcopy(old))
            with self.subTest(change=change), self.assertRaises(ValueError):
                HELPER.decide(current, incoming, candidate)

    def test_archived_unknown_absence_and_reused_evidence_do_not_release_allowance(self):
        current, ledger, incoming, _ = self.archived_attempt()
        absent = HELPER.decide(current, notification_check(current, 140,
            destination_thread_id=current["controller_thread_id"], destination_host=current["controller_host"],
            delivery_readback="absent", readback_observed_at=scheduled(current, 140)["observed_at"],
            readback_evidence_ref="io/no-history-yet.json"), ledger)
        self.assertFalse(HELPER.notification_authorized(current, absent["observer_updates"]))
        old_ref = ledger["notification_history"][0]["delivery_receipts"][0]["evidence_ref"]
        reused = HELPER.decide(current, {**incoming, "delivery_evidence_ref": old_ref}, ledger)
        self.assertEqual(reused["action"], "reconcile_notification_attempt")
        self.assertEqual(reused["observer_updates"]["notification_history"], ledger["notification_history"])

    def test_archived_delivered_fact_cannot_be_revoked_by_a_later_cancellation(self):
        current, ledger, incoming, original = self.archived_attempt("delivered")
        reconciled = HELPER.decide(current, incoming, ledger)
        old = reconciled["observer_updates"]["notification_history"][0]
        self.assertTrue(old["delivery_accepted"])
        self.assertEqual(old["delivery_status"], "delivered")
        self.assertEqual(old["controller_event"], original)
        self.assertFalse(HELPER.notification_authorized(current, reconciled["observer_updates"]))

    def test_already_archived_legacy_reply_uses_its_verified_original_key_and_sha(self):
        current, ledger, incoming, original = self.archived_attempt()
        ledger["notification_history"][0].pop("notification_binding")
        reconciled = HELPER.decide(current, incoming, ledger)
        old = reconciled["observer_updates"]["notification_history"][0]
        self.assertEqual(old["controller_event"], original)
        self.assertEqual(old["delivery_status"], "not_delivered")
        wrong = copy.deepcopy(ledger)
        wrong["notification_history"][0]["controller_event"]["request_user_message_id"] = "other-request"
        with self.assertRaises(ValueError):
            HELPER.decide(current, incoming, wrong)

    def test_late_archived_delivery_is_recorded_without_current_round_completion_permission(self):
        current, ledger, incoming, original = self.archived_attempt()
        current["controller_notification_authorization"] = None
        actual = {**incoming, "delivery_status": "delivered", "delivery_evidence_ref": "io/accepted-round1.json"}
        reconciled = HELPER.decide(current, actual, ledger)
        old = reconciled["observer_updates"]["notification_history"][0]
        self.assertTrue(old["delivery_accepted"])
        self.assertEqual(old["delivery_status"], "delivered")
        self.assertEqual(old["controller_event"], original)
        self.assertFalse(reconciled["activate_controller"])


if __name__ == "__main__":
    unittest.main()
