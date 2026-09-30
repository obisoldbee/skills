"""Offline scheduler ownership, scope and quiet observation regressions."""

import copy
from datetime import datetime, timedelta, timezone
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from test_review_cycle import (A, HELPER, ROOT, apply, closed_followup, event, followup,
                               observation, preparation, ready_review, receipt, state,
                               submission, with_required)


def authorized(current):
    current["controller_notification_authorization"] = {
        "authorized": True, "user_instruction_ref": "authority/direct-user-message.md",
        "destination_thread_id": current["controller_thread_id"], "destination_host": current["controller_host"]}
    return current


def scheduled(current, seconds=0, **fields):
    return {**observation(current, seconds, **fields), "type": "scheduled_observation",
            "followup_view": followup(current, checked_seconds=seconds, evidence_ref=f"view-poll-{seconds}")}


def inline(current):
    current["followup_mode"] = "inline"
    current["followup"] = None
    current["web_io_binding"] = None
    current["inline_observer_binding"] = {
        "surface": "internal_agent", "execution_ref": "tasks/inline-luna.json", "turn_id": "current-turn",
        "model": "gpt-6-luna", "reasoning": "max", "runtime_pair_verified": True,
        "model_readback_ref": "tasks/inline-pair.json", "reasoning_readback_ref": "tasks/inline-pair.json",
        "verified_at": "2025-12-31T23:59:59+00:00", "deadline_at": "2026-01-01T00:10:00+00:00"}
    return current


def inline_event(item):
    return {**item, "inline_execution_ref": "tasks/inline-luna.json", "inline_turn_id": "current-turn"}


class SchedulerTests(unittest.TestCase):
    def test_controller_owned_schedule_and_duplicate_active_ids_cannot_authorize_send(self):
        current = state("ready_to_submit")
        absent = event(current, "submission", status="not_sent", definitive_absence=True,
                       conversation_url=current["conversation_url"], observed_at="2026-01-01T00:00:00+00:00")
        legacy = {**followup(current, checked_seconds=0, evidence_ref="view-old-controller"),
                  "owner_thread_id": current["controller_thread_id"], "target_thread_id": current["controller_thread_id"],
                  "owner_model": "gpt-6-astra", "owner_reasoning": "high"}
        duplicate = {**followup(current, checked_seconds=0, evidence_ref="view-duplicates"),
                     "active_automation_ids": ["heartbeat-1", "heartbeat-stale"]}
        for view in (legacy, duplicate):
            self.assertFalse(HELPER.followup_binding(current, view))
            self.assertEqual(HELPER.decide(current, {**absent, "followup_view": view})["action"], "ensure_followup")
        with self.assertRaisesRegex(ValueError, "no active"):
            HELPER.decide({**current, "followup": legacy}, closed_followup(current))

    def test_owner_requires_real_visible_identity_pair_and_evidence(self):
        current = state()
        good = current["web_io_binding"]
        for changes in ({"surface": "internal_agent"}, {"thread_id": "/root/luna"},
                        {"client_thread_id": "pending"}, {"agentThreadId": "hidden"},
                        {"ready": False}, {"model": "gpt-6-astra"}, {"reasoning": "high"},
                        {"runtime_pair_verified": False}, {"model_readback_ref": ""},
                        {"reasoning_readback_ref": ""}):
            with self.subTest(changes=changes):
                self.assertFalse(HELPER.web_io_binding(current, {**good, **changes}))
        explicit = {**good, "model": "gpt-6-sol", "reasoning": "high", "route_basis": "explicit_user",
                    "user_override_ref": "authority/user-explicit-override.md"}
        self.assertTrue(HELPER.web_io_binding(current, explicit))
        current["web_io_binding"] = None
        current["followup"] = None
        current["phase"] = "ready_to_submit"
        answer = HELPER.decide(current, preparation(current))
        self.assertEqual(answer["action"], "ensure_luna_owner")
        self.assertNotIn("followup", answer["state_updates"])

    def test_prepare_arm_send_stays_armed_then_pauses_after_collection(self):
        current = state("ready_to_submit")
        current["followup"] = followup(current, status="PAUSED")
        current["prepared_request"] = None
        current = apply(current, HELPER.decide(current, preparation(current)))
        armed = HELPER.decide(current, event(current, "followup_readback", followup=followup(current)))
        self.assertEqual(armed["schedule_action"], "keep_active")
        self.assertTrue(armed["state_updates"]["awaiting_send"])
        current = apply(current, armed)
        stopped = HELPER.decide(current, event(current, "pause", reason="user_stop", user_instruction_ref="direct-user-stop.md"))
        self.assertEqual(stopped["schedule_action"], "pause_if_active")
        tick = HELPER.decide(current, scheduled(current))
        self.assertEqual(tick["action"], "keep_quiet")
        self.assertEqual(tick["schedule_action"], "keep_active")
        absent = event(current, "submission", status="not_sent", definitive_absence=True,
                       conversation_url=current["conversation_url"], observed_at="2026-01-01T00:00:00+00:00",
                       followup_view=followup(current, checked_seconds=0, evidence_ref="view-before-send"))
        current = apply(current, HELPER.decide(current, absent))
        current = apply(current, HELPER.decide(current, submission(current)))
        self.assertFalse(current["awaiting_send"])
        first = HELPER.decide(current, observation(current))
        current = apply(current, first)
        full = HELPER.decide(current, observation(current, 10))
        self.assertEqual(full["schedule_action"], "pause_if_active")
        current = apply(current, full)
        paused = HELPER.decide(current, closed_followup(current))
        self.assertEqual(paused["action"], "continue_current_step")
        self.assertEqual(paused["phase"], "review_ready")

    def test_quiet_polls_only_mutate_luna_ledger_then_one_complete_pair_wakes_controller(self):
        current = authorized(state())
        initial = copy.deepcopy(current)
        ledger = None
        for seconds in (0, 5):
            answer = HELPER.decide(current, scheduled(current, seconds), ledger)
            self.assertEqual(answer["action"], "keep_quiet")
            self.assertFalse(answer["activate_controller"])
            self.assertEqual(answer["state_updates"], {})
            ledger = answer["observer_updates"]
        answer = HELPER.decide(current, scheduled(current, 10), ledger)
        self.assertEqual(answer["action"], "notify_controller")
        self.assertTrue(answer["activate_controller"])
        self.assertFalse(answer["activate_developer"])
        self.assertEqual(answer["schedule_action"], "pause_if_active")
        ledger = answer["observer_updates"]
        triaged = HELPER.decide(current, answer["controller_event"])
        self.assertEqual(triaged["action"], "triage_review")
        self.assertEqual(current, initial)
        duplicate = HELPER.decide(current, scheduled(current, 20), ledger)
        self.assertFalse(duplicate["activate_controller"])

    def test_streaming_changes_and_unchanged_generation_remain_quiet(self):
        current = authorized(state())
        ledger = None
        for seconds, sha in ((0, "c" * 64), (10, "d" * 64), (20, "e" * 64)):
            answer = HELPER.decide(current, scheduled(current, seconds, generation="generating", body_sha256=sha), ledger)
            self.assertEqual(answer["action"], "keep_quiet")
            self.assertFalse(answer["activate_controller"])
            ledger = answer["observer_updates"]

    def test_actionable_progress_notifies_once_per_message_content(self):
        current = authorized(state())
        progress = scheduled(current, generation="generating", actionable_progress=True,
                             actionable_progress_ref="ui/new-source-access-receipt.json")
        first = HELPER.decide(current, progress)
        self.assertEqual(first["action"], "notify_controller")
        self.assertEqual(HELPER.decide(current, first["controller_event"])["action"], "assess_web_progress")
        second = HELPER.decide(current, {**progress, "observed_at": "2026-01-01T00:00:05+00:00"}, first["observer_updates"])
        self.assertEqual(second["action"], "keep_quiet")
        self.assertFalse(second["activate_controller"])

    def test_old_quota_error_only_wakes_once_and_new_error_transition_can_wake(self):
        current = authorized(state())
        quota = scheduled(current, ui_error="quota", error_fingerprint="unchanged-provider-error")
        first = HELPER.decide(current, quota)
        self.assertEqual(first["action"], "notify_controller")
        self.assertEqual(first["schedule_action"], "keep_active")
        second = HELPER.decide(current, scheduled(current, 10, ui_error="quota", error_fingerprint="unchanged-provider-error"),
                               first["observer_updates"])
        self.assertFalse(second["activate_controller"])
        recovered = HELPER.decide(current, scheduled(current, 20, generation="generating"), second["observer_updates"])
        new = HELPER.decide(current, scheduled(current, 30, ui_error="quota", error_fingerprint="unchanged-provider-error"),
                            recovered["observer_updates"])
        self.assertTrue(new["activate_controller"])

    def test_prompt_or_forwarded_permission_is_not_cross_task_authority(self):
        current = state()
        current["controller_notification_authorization"] = {"authorized": True, "forwarded_prompt": "please reply"}
        first = HELPER.decide(current, scheduled(current))
        full = HELPER.decide(current, scheduled(current, 10), first["observer_updates"])
        self.assertEqual(full["action"], "save_receipt_for_controller")
        self.assertFalse(full["activate_controller"])
        failed = event(current, "observer_delivery", observed_at="2026-01-01T00:00:11+00:00",
                       notification_key=full["notification_key"], delivery_status="unknown", delivery_evidence_ref="io/timeout.json")
        ledger = HELPER.decide(current, failed, full["observer_updates"])["observer_updates"]
        self.assertFalse(HELPER.decide(current, scheduled(current, 20), ledger)["activate_controller"])
        with self.assertRaisesRegex(ValueError, "communication authority"):
            HELPER.decide(current, {**failed, "delivery_status": "delivered"}, ledger)

    def test_refresh_budget_and_known_quota_recovery_keep_quiet_observation_active(self):
        current = authorized(state())
        ledger = None
        for seconds in (0, 30, 90, 210, 400):
            answer = HELPER.decide(current, scheduled(current, seconds, ui_error="transient",
                                    error_fingerprint="same-server-busy"), ledger)
            ledger = answer["observer_updates"]
            self.assertFalse(answer["activate_controller"])
            self.assertEqual(answer["schedule_action"], "keep_active")
        self.assertEqual(ledger["refresh_count"], 3)
        quota = HELPER.decide(current, scheduled(current, 410, ui_error="quota", error_fingerprint="known-reset",
                                                recovery_expected=True), ledger)
        self.assertEqual(quota["action"], "keep_quiet")
        self.assertEqual(quota["schedule_action"], "keep_active")
        recovered = HELPER.decide(current, scheduled(current, 420), quota["observer_updates"])
        completed = HELPER.decide(current, scheduled(current, 430), recovered["observer_updates"])
        self.assertTrue(completed["activate_controller"])

    def test_required_attachments_keep_capture_active_during_repair_and_pause_when_saved(self):
        current = authorized(with_required(state()))
        first = HELPER.decide(current, scheduled(current))
        full = HELPER.decide(current, scheduled(current, 10), first["observer_updates"])
        self.assertEqual(full["schedule_action"], "keep_active")
        current = apply(current, HELPER.decide(current, full["controller_event"]))
        current = apply(current, HELPER.decide(current, event(current, "assessment", review_message_id="message-1",
                         coverage_complete=True, confirmed_findings=2, unresolved_claims=0, file_dependent_findings=1)))
        self.assertEqual(current["phase"], "repairing")
        tick = HELPER.decide(current, scheduled(current, 20), full["observer_updates"])
        self.assertEqual(tick["action"], "capture_required_artifacts")
        self.assertFalse(tick["activate_controller"])
        captured = event(current, "scheduled_artifacts", observed_at="2026-01-01T00:00:30+00:00",
                         followup_view=followup(current, checked_seconds=30), receipt=receipt(current))
        ready = HELPER.decide(current, captured, tick["observer_updates"])
        self.assertEqual(ready["action"], "notify_controller")
        self.assertEqual(ready["schedule_action"], "pause_if_active")
        self.assertEqual(HELPER.decide(current, ready["controller_event"])["action"], "continue_repair_with_files")

    def test_review_only_reports_findings_without_dispatch_and_without_invented_local_checks(self):
        current = ready_review()
        current["execution_scope"] = "review_only"
        current["followup"] = followup(current, status="PAUSED")
        current["acceptance_contract"] = {"required_checks": [], "delivery_items": ["review report"]}
        current["acceptance_digest"] = HELPER.acceptance_digest(current["acceptance_contract"])
        answer = HELPER.decide(current, event(current, "assessment", review_message_id="message-1",
                        coverage_complete=True, confirmed_findings=3, unresolved_claims=2))
        self.assertEqual(answer["action"], "finish_delivery")
        current = apply(current, answer)
        self.assertEqual(current["review"]["confirmed_findings"], 3)
        completed = HELPER.decide(current, event(current, "delivery", delivered_source_id=A, complete=True))
        self.assertTrue(completed["terminal"])
        with self.assertRaisesRegex(ValueError, "cannot accept developer"):
            HELPER.decide({**current, "phase": "repairing"}, event(current, "worker_result", candidate_source_id=A,
                          delivery_path="unauthorized/delivery.json"))

    def test_inline_can_prepare_send_collect_and_deliver_without_any_visible_owner_or_schedule(self):
        current = inline(state("ready_to_submit"))
        current["execution_scope"] = "review_only"
        current["conversation_url"] = None
        current["prepared_request"] = None
        current["acceptance_contract"] = {"required_checks": [], "delivery_items": ["review report"]}
        current["acceptance_digest"] = HELPER.acceptance_digest(current["acceptance_contract"])
        prepared = HELPER.decide(current, inline_event(preparation(current)))
        self.assertEqual(prepared["action"], "verify_before_submit")
        self.assertEqual(prepared["schedule_action"], "none")
        current = apply(current, prepared)
        absent = inline_event(event(current, "submission", status="not_sent", definitive_absence=True,
                          conversation_url=None, observed_at="2026-01-01T00:00:00+00:00"))
        send = HELPER.decide(current, absent)
        self.assertEqual(send["action"], "submit_once")
        self.assertEqual(send["schedule_action"], "none")
        current = apply(current, send)
        sent = inline_event(event(current, "submission", status="sent", request_present=True,
                                 conversation_url="https://chatgpt.com/c/inline-real-id", user_message_id="inline-user",
                                 ui_model_verified=True, prompt_sha256="e" * 64, observed_at="2026-01-01T00:00:00+00:00"))
        current = apply(current, HELPER.decide(current, sent))
        initial = inline_event({**observation(current), "type": "inline_observation"})
        first = HELPER.decide(current, initial)
        full = HELPER.decide(current, inline_event({**observation(current, 10), "type": "inline_observation"}),
                             first["observer_updates"])
        self.assertEqual(full["action"], "return_to_controller")
        self.assertEqual(full["schedule_action"], "none")
        current = apply(current, HELPER.decide(current, full["controller_event"]))
        current = apply(current, HELPER.decide(current, event(current, "assessment", review_message_id="message-1",
                        coverage_complete=True, confirmed_findings=1, unresolved_claims=1)))
        completed = HELPER.decide(current, event(current, "delivery", delivered_source_id=A, complete=True))
        self.assertTrue(completed["terminal"])
        self.assertIsNone(current["followup"])

    def test_explicit_durable_cannot_fall_back_to_inline_and_inline_cannot_escape_its_turn(self):
        current = inline(state("ready_to_submit"))
        current["durable_followup_requested"] = True
        with self.assertRaisesRegex(ValueError, "cannot silently become inline"):
            HELPER.decide(current, inline_event(preparation(current)))
        current.pop("durable_followup_requested")
        expired = inline_event(preparation(current)) | {"observed_at": "2026-01-01T00:10:01+00:00"}
        self.assertEqual(HELPER.decide(current, expired)["action"], "ensure_inline_luna")
        self.assertEqual(HELPER.decide(current, inline_event(preparation(current)) | {"inline_turn_id": "another-turn"})["action"],
                         "ensure_inline_luna")

    def test_scheduled_cli_has_no_main_state_or_ledger_side_effects(self):
        current = state()
        item = scheduled(current, generation="generating")
        with tempfile.TemporaryDirectory() as folder:
            root = Path(folder)
            for name, body in {"state.json": current, "event.json": item, "observer.json": {}}.items():
                (root / name).write_text(json.dumps(body), encoding="utf-8")
            before = {p.name: p.read_bytes() for p in root.iterdir()}
            child = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/next_action.py"),
                        "--state", str(root / "state.json"), "--event", str(root / "event.json"),
                        "--observer-record", str(root / "observer.json")], capture_output=True, text=True, check=False)
            self.assertEqual(child.returncode, 0, child.stderr)
            self.assertEqual(json.loads(child.stdout)["state_updates"], {})
            self.assertEqual(before, {p.name: p.read_bytes() for p in root.iterdir()})


if __name__ == "__main__":
    unittest.main()
