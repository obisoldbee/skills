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


def notification_check(current, seconds=20, **fields):
    moment = datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=seconds)
    view = {} if current.get("followup_mode") == "inline" else {
        "followup_view": followup(current, checked_seconds=seconds, evidence_ref=f"receipt-view-{seconds}")}
    return event(current, "notification_check", observed_at=moment.isoformat(),
                 **view, **fields)


def delivery(current, key, status, seconds=11):
    moment = datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=seconds)
    return event(current, "observer_delivery", observed_at=moment.isoformat(), notification_key=key,
                 delivery_status=status, delivery_evidence_ref=f"io/{status}-{seconds}.json",
                 destination_thread_id=current["controller_thread_id"], destination_host=current["controller_host"])


def destination_readback(current, seconds, **fields):
    moment = datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=seconds)
    return {"destination_thread_id": current["controller_thread_id"], "destination_host": current["controller_host"],
            "readback_observed_at": moment.isoformat(), "readback_evidence_ref": f"io/destination-{seconds}.json", **fields}


def collected(current):
    first = HELPER.decide(current, scheduled(current))
    return HELPER.decide(current, scheduled(current, 10), first["observer_updates"])


def recovery(current, seconds=5, **fields):
    moment = datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=seconds)
    view = {} if current.get("followup_mode") == "inline" else {
        "followup_view": followup(current, checked_seconds=seconds, evidence_ref=f"recovery-view-{seconds}")}
    return event(current, "browser_recovered", **{
        "observed_at": moment.isoformat(), "reason_code": "space_missing",
        "conversation_url": current["conversation_url"], "old_space_id": "space-old",
        "browser_context": {"space_id": "space-restored", "page_label": "p1", "ownership": "agent"},
        "recovery_evidence_ref": f"ui/recovery-{seconds}.json", "request_status": "present",
        "user_message_id": current.get("submitted_user_message_id"),
        "prompt_sha256": current.get("submitted_prompt_sha256"), "assistant_message_id": "message-1",
        **view, **fields})


class RecoveryTests(unittest.TestCase):
    def test_sent_space_loss_recovers_original_request_and_finishes_capture(self):
        current = state("submitting")
        current = apply(current, HELPER.decide(current, submission(current)))
        identities = {key: current[key] for key in ("conversation_url", "submitted_user_message_id",
                      "submitted_prompt_sha256", "source_id", "request_token", "contract_digest")}
        fault = HELPER.decide(current, event(current, "browser_fault", reason_code="space_missing"))
        self.assertEqual(fault["action"], "recover_browser_context")
        self.assertEqual(fault["phase"], "waiting_web")
        current = apply(current, fault)
        restored = HELPER.decide(current, recovery(current))
        self.assertEqual(restored["action"], "watch")
        current = apply(current, restored)
        self.assertEqual(identities, {key: current[key] for key in identities})
        self.assertEqual(current["browser_context"]["old_space_id"], "space-old")
        first = HELPER.decide(current, observation(current, 10))
        completed = HELPER.decide(apply(current, first), observation(current, 20))
        self.assertEqual(completed["action"], "triage_review")

    def test_unsent_space_loss_recovers_then_uses_original_send_gate(self):
        current = state("ready_to_submit")
        current["awaiting_send"] = True
        fault = HELPER.decide(current, event(current, "browser_fault", reason_code="space_closed"))
        self.assertEqual(fault["action"], "recover_browser_context")
        current = apply(current, fault)
        restored = HELPER.decide(current, recovery(current, request_status="absent", definitive_absence=True))
        self.assertEqual(restored["action"], "verify_before_submit")
        current = apply(current, restored)
        absent = event(current, "submission", status="not_sent", definitive_absence=True,
                       conversation_url=current["conversation_url"], observed_at="2026-01-01T00:00:06+00:00",
                       followup_view=followup(current, checked_seconds=6, evidence_ref="send-after-recovery"))
        self.assertEqual(HELPER.decide(current, absent)["action"], "submit_once")
        self.assertEqual(current["prepared_request"]["sha256"], "e" * 64)

    def test_browser_crash_preserves_known_response_and_saved_artifacts(self):
        current = state("submitting")
        current = apply(current, HELPER.decide(current, submission(current)))
        current = apply(current, HELPER.decide(current, observation(current)))
        current = apply(current, HELPER.decide(current, observation(current, 10)))
        current = with_required(current)
        current["artifact_receipt"] = receipt(current)
        fault = HELPER.decide(current, event(current, "browser_fault", reason_code="browser_crash"))
        current = apply(current, fault)
        restored = HELPER.decide(current, recovery(current, 20, reason_code="browser_crash"))
        self.assertEqual(restored["action"], "continue_current_step")
        restored_state = apply(current, restored)
        for key in ("raw_reply_path", "review_message_id", "submitted_user_message_id", "artifact_receipt"):
            self.assertEqual(restored_state[key], current[key])
        mismatch = HELPER.decide(current, recovery(current, 20, assistant_message_id="different-reply"))
        self.assertEqual(mismatch["action"], "reconcile_submission")
        with self.assertRaisesRegex(ValueError, "server conversation"):
            HELPER.decide(current, recovery(current, conversation_url="https://chatgpt.com/c/different"))

    def test_actual_human_gates_take_priority_over_missing_space(self):
        for gate in ("auth", "user_control", "permission_denied"):
            with self.subTest(gate=gate):
                current = state()
                fault = event(current, "browser_fault", reason_code="space_missing", ui_error=gate)
                self.assertEqual(HELPER.decide(current, fault)["action"], "request_browser_input")
                mixed = observation(current, ui_error="space_missing", reason_code=gate)
                self.assertEqual(HELPER.decide(current, mixed)["action"], "request_browser_input")
                with self.assertRaisesRegex(ValueError, "recoverable fault"):
                    HELPER.decide(current, recovery(current, ui_error=gate))
                current.update(phase="blocked", resume_phase="waiting_web", blocker_reason_code=gate)
                with self.assertRaisesRegex(ValueError, "human browser gate"):
                    HELPER.decide(current, recovery(current))

    def test_unknown_request_status_never_resends_after_recovery(self):
        for phase in ("ready_to_submit", "submitting"):
            current = state(phase)
            if phase == "submitting":
                current = apply(current, HELPER.decide(current, submission(current)))
            for fields in ({"request_status": "unknown"}, {"request_status": "absent"},
                           {"request_status": "present", "user_message_id": "different-user"}):
                answer = HELPER.decide(current, recovery(current, **fields))
                self.assertEqual(answer["action"], "reconcile_submission")
                self.assertNotIn("submitted_user_message_id", answer["state_updates"])

    def test_resolved_human_gate_does_not_permanently_block_later_ordinary_recovery(self):
        current = state("blocked")
        current.update(resume_phase="waiting_web", blocker_reason_code="auth")
        resumed = HELPER.decide(current, event(current, "resume", resolution_ref="ui/login-resolved.json",
                               observed_at="2026-01-01T00:00:10+00:00",
                               followup_view=followup(current, checked_seconds=10, evidence_ref="view-after-login")))
        self.assertEqual(resumed["action"], "resume_saved_step")
        current = apply(current, resumed)
        self.assertIsNone(current["blocker_reason_code"])
        lost = HELPER.decide(current, event(current, "browser_fault", reason_code="space_missing"))
        self.assertEqual(lost["action"], "recover_browser_context")

    def test_old_missing_space_blocker_can_resume_with_actual_recovery(self):
        current = state("submitting")
        current = apply(current, HELPER.decide(current, submission(current)))
        current.update(phase="blocked", resume_phase="waiting_web")
        old = event(current, "external_blocker", reason="space not found", attempts=["ui/not-found.json"],
                    requires_external_change="reopen browser", independent_work_remaining=False)
        repaired = HELPER.decide(current, old)
        self.assertEqual(repaired["action"], "recover_browser_context")
        self.assertEqual(repaired["phase"], "waiting_web")
        resumed = HELPER.decide(current, {**recovery(current), "type": "resume"})
        self.assertEqual(resumed["action"], "watch")
        self.assertEqual(resumed["phase"], "waiting_web")
        self.assertEqual(resumed["state_updates"]["browser_recovery_attempts"], 0)
        paused = {**current, "phase": "paused"}
        self.assertEqual(HELPER.decide(paused, old)["action"], "pause")
        with self.assertRaisesRegex(ValueError, "user pause"):
            HELPER.decide(paused, recovery(paused))

    def test_successful_recovery_starts_a_new_incident_budget_only_with_evidence(self):
        current = state("submitting")
        current = apply(current, HELPER.decide(current, submission(current)))
        ledger = None
        for seconds, expected in ((1, "recover_browser_context"), (2, "recover_browser_context"),
                                  (3, "diagnose_browser_recovery")):
            result = HELPER.decide(current, scheduled(current, seconds, ui_error="space_missing",
                                   error_fingerprint="same-space-fault"), ledger)
            self.assertEqual(result["action"], expected)
            self.assertFalse(result["activate_controller"])
            ledger = result["observer_updates"]
        current = apply(current, HELPER.decide(current, recovery(current, 4)))
        new = HELPER.decide(current, scheduled(current, 5, ui_error="browser_crash",
                            error_fingerprint="new-crash"), ledger)
        self.assertEqual(new["action"], "recover_browser_context")
        self.assertEqual(new["observer_updates"]["browser_recovery_attempts"], 1)
        with self.assertRaisesRegex(ValueError, "owned old/new"):
            HELPER.decide(current, recovery(current, old_space_id=None))

    def test_expired_inline_execution_renews_from_actual_turn_without_scheduler_configuration(self):
        current = inline(state("submitting"))
        current = apply(current, HELPER.decide(current, inline_event(submission(state("submitting")))))
        old = recovery(current, 700)
        self.assertEqual(HELPER.decide(current, old)["action"], "ensure_inline_luna")
        binding = {**current["inline_observer_binding"], "turn_id": "restored-turn", "execution_ref": "tasks/restored-luna.json",
                   "verified_at": "2026-01-01T00:11:39+00:00", "deadline_at": "2026-01-01T00:20:00+00:00"}
        renewed = {**old, "inline_observer_binding": binding, "inline_turn_id": binding["turn_id"],
                   "inline_execution_ref": binding["execution_ref"]}
        restored = HELPER.decide(current, renewed)
        self.assertEqual(restored["action"], "watch")
        self.assertEqual(restored["schedule_action"], "none")
        self.assertEqual(restored["state_updates"]["inline_observer_binding"], binding)

    def test_owner_proof_refresh_preserves_window_queue_error_dedup_and_refresh_budget(self):
        current = authorized(state())
        first = HELPER.decide(current, scheduled(current, ui_error="quota", error_fingerprint="quota"))
        current["web_io_binding"] = {**current["web_io_binding"], "verified_at": "2026-01-01T00:00:05+00:00",
                                    "identity_readback_ref": "tasks/fresh-identity.json", "model_readback_ref": "tasks/fresh-pair.json",
                                    "reasoning_readback_ref": "tasks/fresh-pair.json"}
        current["followup"] = followup(current, checked_seconds=5, evidence_ref="fresh-owner-view")
        refreshed = HELPER.decide(current, scheduled(current, 10, ui_error="quota", error_fingerprint="quota"),
                                  first["observer_updates"])
        self.assertEqual(refreshed["action"], "keep_quiet")
        self.assertFalse(refreshed["activate_controller"])
        self.assertEqual(refreshed["observer_updates"]["notifications"], first["observer_updates"]["notifications"])
        self.assertEqual(refreshed["observer_updates"]["error_transition"], first["observer_updates"]["error_transition"])
        start = HELPER.decide(current, scheduled(current, 20), refreshed["observer_updates"])
        current["web_io_binding"]["verified_at"] = "2026-01-01T00:00:25+00:00"
        stable = HELPER.decide(current, scheduled(current, 30), start["observer_updates"])
        self.assertEqual(stable["action"], "notify_controller")
        ledger = None
        for seconds in (40, 70):
            busy = HELPER.decide(current, scheduled(current, seconds, ui_error="transient", error_fingerprint="same-busy"), ledger)
            ledger = busy["observer_updates"]
        current["web_io_binding"]["verified_at"] = "2026-01-01T00:01:15+00:00"
        waiting = HELPER.decide(current, scheduled(current, 80, ui_error="transient", error_fingerprint="same-busy"), ledger)
        self.assertEqual(waiting["observer_updates"]["refresh_count"], ledger["refresh_count"])
        self.assertEqual(waiting["observer_updates"]["refresh_count"], 1)

    def test_new_inline_turn_preserves_pending_payload_and_budgets_but_restarts_unfinished_window(self):
        current = inline(authorized(state()))
        first = HELPER.decide(current, inline_event({**observation(current), "type": "inline_observation",
                              "generation": "generating", "actionable_progress": True, "actionable_progress_ref": "ui/progress.json"}))
        queued = copy.deepcopy(first["observer_updates"]["notifications"])
        ledger = first["observer_updates"]
        stable = HELPER.decide(current, inline_event({**observation(current, 5), "type": "inline_observation"}), ledger)
        stable["observer_updates"].update(refresh_count=3, browser_recovery_attempts=2)
        current["inline_observer_binding"] = {**current["inline_observer_binding"], "turn_id": "next-turn",
                       "execution_ref": "tasks/next-turn-proof.json", "verified_at": "2026-01-01T00:00:10+00:00"}
        checking = {**notification_check(current, 15), "inline_turn_id": "next-turn",
                    "inline_execution_ref": "tasks/next-turn-proof.json"}
        renewed = HELPER.decide(current, checking, stable["observer_updates"])
        self.assertEqual(renewed["action"], "check_controller_receipt")
        self.assertIsNone(renewed["observer_updates"]["last_completion"])
        self.assertEqual(renewed["observer_updates"]["notifications"], queued)
        self.assertEqual(renewed["observer_updates"]["refresh_count"], 3)
        self.assertEqual(renewed["observer_updates"]["browser_recovery_attempts"], 2)
        item = {**observation(current, 20), "type": "inline_observation", "inline_turn_id": "next-turn",
                "inline_execution_ref": "tasks/next-turn-proof.json"}
        first = HELPER.decide(current, item, renewed["observer_updates"])
        self.assertEqual(first["action"], "keep_quiet")
        completed = HELPER.decide(current, {**item, "observed_at": "2026-01-01T00:00:30+00:00"}, first["observer_updates"])
        self.assertEqual(completed["action"], "return_to_controller")

    def test_new_owner_restarts_window_without_dropping_unreceived_result(self):
        current = authorized(state())
        progress = HELPER.decide(current, scheduled(current, generation="generating", actionable_progress=True,
                                actionable_progress_ref="ui/progress.json"))
        first = HELPER.decide(current, scheduled(current, 5), progress["observer_updates"])
        current["web_io_binding"] = {**current["web_io_binding"], "thread_id": "replacement-luna-thread"}
        current["followup"] = followup(current, checked_seconds=10, evidence_ref="replacement-owner-view")
        replaced = HELPER.decide(current, scheduled(current, 15), first["observer_updates"])
        self.assertEqual(replaced["action"], "keep_quiet")
        self.assertEqual(replaced["observer_updates"]["notifications"], progress["observer_updates"]["notifications"])
        completed = HELPER.decide(current, scheduled(current, 25), replaced["observer_updates"])
        self.assertEqual(completed["action"], "notify_controller")

    def test_internal_agent_identity_changes_window_but_proof_file_does_not(self):
        current = inline(state())
        current["inline_observer_binding"]["agent_id"] = "/root/luna-one"
        first = HELPER.decide(current, inline_event({**observation(current), "type": "inline_observation"}))
        current["inline_observer_binding"]["execution_ref"] = "tasks/refreshed-proof.json"
        item = {**observation(current, 10), "type": "inline_observation", "inline_turn_id": "current-turn",
                "inline_execution_ref": "tasks/refreshed-proof.json"}
        stable = HELPER.decide(current, item, first["observer_updates"])
        self.assertEqual(stable["action"], "return_to_controller")
        first = HELPER.decide(current, {**item, "observed_at": "2026-01-01T00:00:20+00:00"})
        current["inline_observer_binding"]["agent_id"] = "/root/luna-two"
        replaced = HELPER.decide(current, {**item, "observed_at": "2026-01-01T00:00:30+00:00"}, first["observer_updates"])
        self.assertEqual(replaced["action"], "keep_quiet")

    def test_review_only_failed_checks_keep_evidence_and_deliver_failed_acceptance_report(self):
        current = inline(ready_review())
        current["execution_scope"] = "review_only"
        assessed = HELPER.decide(current, event(current, "assessment", review_message_id="message-1",
                                coverage_complete=True, confirmed_findings=3, unresolved_claims=1))
        self.assertEqual(assessed["action"], "run_local_checks")
        current = apply(current, assessed)
        failed = HELPER.decide(current, event(current, "validation", checked_source_id=A, passed=False,
                              required_unverified=["unavailable check"], evidence=["checks/failed.json"]))
        self.assertEqual(failed["phase"], "validating")
        self.assertEqual(failed["action"], "finish_delivery")
        self.assertFalse(failed["state_updates"]["acceptance_passed"])
        current = apply(current, failed)
        completed = HELPER.decide(current, event(current, "delivery", delivered_source_id=A, complete=True))
        self.assertTrue(completed["terminal"])
        self.assertFalse(completed["state_updates"]["acceptance_passed"])
        self.assertEqual(current["validation"]["evidence"], ["checks/failed.json"])
        self.assertEqual(current["review"]["confirmed_findings"], 3)
        with self.assertRaisesRegex(ValueError, "cannot accept developer"):
            HELPER.decide({**current, "phase": "repairing"}, event(current, "worker_result", candidate_source_id=A,
                          delivery_path="unauthorized/repair.json"))


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
        self.assertEqual(answer["schedule_action"], "keep_active")
        ledger = answer["observer_updates"]
        triaged = HELPER.decide(current, answer["controller_event"])
        self.assertEqual(triaged["action"], "triage_review")
        self.assertEqual(current, initial)
        duplicate = HELPER.decide(current, scheduled(current, 20), ledger)
        self.assertFalse(duplicate["activate_controller"])
        self.assertFalse(duplicate["observe_webpage"])
        self.assertEqual(duplicate["action"], "check_controller_receipt")
        current = apply(current, triaged)
        received = HELPER.decide(current, notification_check(current, 30), duplicate["observer_updates"])
        self.assertEqual(received["action"], "pause_followup")
        self.assertEqual(received["schedule_action"], "pause_if_active")

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

    def test_received_progress_does_not_pause_the_unfinished_web_reply(self):
        current = authorized(state())
        progress = HELPER.decide(current, scheduled(current, generation="generating", actionable_progress=True,
                                actionable_progress_ref="ui/progress.json"))
        current = apply(current, HELPER.decide(current, progress["controller_event"], progress["observer_updates"]))
        checking = HELPER.decide(current, notification_check(current, 20), progress["observer_updates"])
        self.assertEqual(checking["phase"], "waiting_web")
        self.assertEqual(checking["action"], "keep_quiet")
        self.assertEqual(checking["schedule_action"], "keep_active")
        self.assertTrue(checking["observe_webpage"])
        self.assertFalse(checking["activate_controller"])
        self.assertEqual(checking["observer_updates"]["notifications"][0]["status"], "received")
        first = HELPER.decide(current, scheduled(current, 30), checking["observer_updates"])
        complete = HELPER.decide(current, scheduled(current, 40), first["observer_updates"])
        self.assertEqual(complete["action"], "notify_controller")

    def test_notification_check_with_no_notifications_retains_initial_web_wait(self):
        current = state()
        checking = HELPER.decide(current, notification_check(current))
        self.assertEqual(checking["action"], "keep_quiet")
        self.assertEqual(checking["schedule_action"], "keep_active")
        self.assertTrue(checking["observe_webpage"])
        self.assertEqual(checking["observer_updates"]["notifications"], [])
        current["followup"] = followup(current, status="PAUSED")
        missing = HELPER.decide(current, notification_check(current))
        self.assertEqual(missing["action"], "ensure_followup")
        self.assertEqual(missing["schedule_action"], "keep_active")

    def test_notification_check_with_no_notifications_retains_required_artifact_capture(self):
        current = with_required(ready_review())
        checking = HELPER.decide(current, notification_check(current))
        self.assertEqual(checking["action"], "capture_required_artifacts")
        self.assertEqual(checking["schedule_action"], "keep_active")
        self.assertTrue(checking["observe_webpage"])
        self.assertFalse(checking["activate_controller"])
        captured = event(current, "scheduled_artifacts", observed_at="2026-01-01T00:00:30+00:00",
                         followup_view=followup(current, checked_seconds=30), receipt=receipt(current))
        saved = HELPER.decide(current, captured, checking["observer_updates"])
        current = apply(current, HELPER.decide(current, saved["controller_event"], saved["observer_updates"]))
        closed = HELPER.decide(current, notification_check(current, 40), saved["observer_updates"])
        self.assertEqual(closed["action"], "pause_followup")

    def test_notification_check_with_no_notifications_preserves_the_armed_send_window(self):
        current = state("ready_to_submit")
        current["awaiting_send"] = True
        checking = HELPER.decide(current, notification_check(current))
        self.assertEqual(checking["action"], "keep_quiet")
        self.assertEqual(checking["schedule_action"], "keep_active")
        self.assertFalse(checking["observe_webpage"])
        self.assertEqual(checking["state_updates"], {})

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
        failed = delivery(current, full["notification_key"], "unknown")
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
        self.assertTrue(tick["observe_webpage"])
        self.assertFalse(tick["activate_controller"])
        captured = event(current, "scheduled_artifacts", observed_at="2026-01-01T00:00:30+00:00",
                         followup_view=followup(current, checked_seconds=30), receipt=receipt(current))
        ready = HELPER.decide(current, captured, tick["observer_updates"])
        self.assertEqual(ready["action"], "notify_controller")
        self.assertEqual(ready["schedule_action"], "keep_active")
        applied = HELPER.decide(current, ready["controller_event"])
        self.assertEqual(applied["action"], "continue_repair_with_files")
        current = apply(current, applied)
        received = HELPER.decide(current, notification_check(current, 40), ready["observer_updates"])
        self.assertEqual(received["schedule_action"], "pause_if_active")
        self.assertFalse(received["observe_webpage"])

    def test_delivered_is_not_received_and_processing_records_receipt_once(self):
        current = authorized(state())
        full = collected(current)
        delivered = HELPER.decide(current, delivery(current, full["notification_key"], "delivered"), full["observer_updates"])
        checking = HELPER.decide(current, notification_check(current), delivered["observer_updates"])
        self.assertEqual(checking["action"], "check_controller_receipt")
        self.assertEqual(checking["schedule_action"], "keep_active")
        self.assertFalse(checking["activate_controller"])
        self.assertFalse(checking["observe_webpage"])
        received = HELPER.decide(current, full["controller_event"], checking["observer_updates"])
        self.assertEqual(received["action"], "triage_review")
        self.assertIn(full["notification_key"], received["state_updates"]["received_notifications"])
        current = apply(current, received)
        stopped = HELPER.decide(current, notification_check(current, 30), checking["observer_updates"])
        self.assertEqual(stopped["action"], "pause_followup")
        self.assertEqual(stopped["observer_updates"]["notifications"][0]["status"], "received")
        self.assertFalse(stopped["observe_webpage"])

    def test_active_writer_waits_then_retries_original_payload_without_dedup_loss(self):
        current = authorized(state())
        current["submitted_user_message_id"] = "original-user-message"
        full = collected(current)
        failed = HELPER.decide(current, delivery(current, full["notification_key"], "active_writer"), full["observer_updates"])
        saved = failed["observer_updates"]
        self.assertEqual(saved["notifications"][0]["destination_thread_id"], current["controller_thread_id"])
        busy = HELPER.decide(current, notification_check(current, 80, **destination_readback(current, 80,
                            destination_status="active_writer")), saved)
        self.assertEqual(busy["action"], "check_controller_receipt")
        self.assertFalse(busy["activate_controller"])
        retry = HELPER.decide(current, notification_check(current, 90, **destination_readback(current, 90,
                             destination_status="idle")), busy["observer_updates"])
        self.assertEqual(retry["action"], "retry_notification")
        self.assertEqual(retry["notification_key"], full["notification_key"])
        self.assertEqual(retry["controller_event"], full["controller_event"])
        self.assertEqual(retry["controller_event"]["request_user_message_id"], "original-user-message")
        self.assertEqual(retry["observer_updates"]["notifications"][0]["attempts"], 2)
        duplicate = HELPER.decide(current, notification_check(current, 100), retry["observer_updates"])
        self.assertFalse(duplicate["activate_controller"])
        self.assertFalse(duplicate["observe_webpage"])
        self.assertEqual(len(duplicate["observer_updates"]["notifications"]), 1)

    def test_unknown_delivery_needs_sufficient_absence_readback_before_retry(self):
        current = authorized(state())
        full = collected(current)
        failed = HELPER.decide(current, delivery(current, full["notification_key"], "unknown"), full["observer_updates"])
        idle = destination_readback(current, 80, destination_status="idle")
        unknown = HELPER.decide(current, notification_check(current, 80, **idle), failed["observer_updates"])
        self.assertEqual(unknown["action"], "check_controller_receipt")
        self.assertEqual(unknown["observer_updates"]["notifications"][0]["status"], "unknown")
        present = HELPER.decide(current, notification_check(current, 90, **destination_readback(current, 90,
                               delivery_readback="present", destination_status="idle")), unknown["observer_updates"])
        self.assertEqual(present["action"], "check_controller_receipt")
        self.assertEqual(present["observer_updates"]["notifications"][0]["status"], "delivered")
        absent = HELPER.decide(current, notification_check(current, 90, **destination_readback(current, 90,
                              delivery_readback="absent", destination_status="idle")), unknown["observer_updates"])
        self.assertEqual(absent["action"], "retry_notification")
        self.assertEqual(absent["controller_event"], full["controller_event"])

    def test_retry_readback_must_match_target_be_fresh_and_follow_the_failed_attempt(self):
        current = authorized(state())
        full = collected(current)
        for status in ("delivered", "unknown", "active_writer", "not_delivered"):
            with self.subTest(status=status), self.assertRaisesRegex(ValueError, "destination mismatch"):
                HELPER.decide(current, {**delivery(current, full["notification_key"], status),
                                       "destination_host": "other-host"}, full["observer_updates"])
        failed = HELPER.decide(current, delivery(current, full["notification_key"], "not_delivered"), full["observer_updates"])
        checks = destination_readback(current, 80, destination_status="idle", delivery_readback="absent")
        for change in ({"destination_thread_id": "other-thread"}, {"destination_host": "other-host"},
                       {"readback_evidence_ref": ""}, {"readback_observed_at": "2026-01-01T00:00:00+00:00"},
                       {"readback_observed_at": "2026-01-01T00:01:21+00:00"}):
            with self.subTest(change=change), self.assertRaises(ValueError):
                HELPER.decide(current, notification_check(current, 80, **{**checks, **change}), failed["observer_updates"])
        early = HELPER.decide(current, notification_check(current, 20, **destination_readback(current, 20,
                             destination_status="idle")), failed["observer_updates"])
        self.assertEqual(early["action"], "check_controller_receipt")

    def test_failed_delivery_retries_are_bounded_but_saved_result_remains_collectable(self):
        current = authorized(state())
        full = collected(current)
        ledger = full["observer_updates"]
        for failure_time, retry_time in ((11, 80), (81, 150)):
            failed = HELPER.decide(current, delivery(current, full["notification_key"], "not_delivered", failure_time), ledger)
            retried = HELPER.decide(current, notification_check(current, retry_time, **destination_readback(current, retry_time,
                                   destination_status="idle")), failed["observer_updates"])
            self.assertEqual(retried["action"], "retry_notification")
            ledger = retried["observer_updates"]
        failed = HELPER.decide(current, delivery(current, full["notification_key"], "active_writer", 151), ledger)
        checkpoint = HELPER.decide(current, notification_check(current, 220, **destination_readback(current, 220,
                                  destination_status="idle")), failed["observer_updates"])
        self.assertEqual(checkpoint["action"], "delivery_recovery_checkpoint")
        self.assertFalse(checkpoint["activate_controller"])
        self.assertEqual(checkpoint["schedule_action"], "keep_active")
        self.assertFalse(checkpoint["observe_webpage"])
        self.assertEqual(checkpoint["observer_updates"]["notifications"][0]["controller_event"], full["controller_event"])
        current = apply(current, HELPER.decide(current, full["controller_event"], checkpoint["observer_updates"]))
        collected_by_controller = HELPER.decide(current, notification_check(current, 230), checkpoint["observer_updates"])
        self.assertEqual(collected_by_controller["action"], "pause_followup")

    def test_retry_needs_current_direct_authority_but_controller_read_does_not(self):
        current = authorized(state())
        full = collected(current)
        failed = HELPER.decide(current, delivery(current, full["notification_key"], "not_delivered"), full["observer_updates"])
        current["controller_notification_authorization"]["authorized"] = False
        check = HELPER.decide(current, notification_check(current, 80, **destination_readback(current, 80,
                            destination_status="idle")), failed["observer_updates"])
        self.assertEqual(check["action"], "check_controller_receipt")
        self.assertFalse(check["activate_controller"])
        current = apply(current, HELPER.decide(current, full["controller_event"], check["observer_updates"]))
        self.assertEqual(HELPER.decide(current, notification_check(current, 90), check["observer_updates"])["action"], "pause_followup")

    def test_pause_and_resume_preserve_unreceived_result_and_restore_luna_checker(self):
        current = authorized(state())
        full = collected(current)
        paused = HELPER.decide(current, event(current, "pause", reason="user_stop", user_instruction_ref="user/stop.md"))
        current = apply(current, paused)
        paused_tick = HELPER.decide(current, notification_check(current, 20), full["observer_updates"])
        self.assertEqual(paused_tick["schedule_action"], "pause_if_active")
        current = apply(current, HELPER.decide(current, closed_followup(current)))
        resume = event(current, "resume", observed_at="2026-01-01T00:00:30+00:00", resolution_ref="user/resume.md",
                       followup_view=followup(current, checked_seconds=30, evidence_ref="view-resumed"))
        self.assertEqual(HELPER.decide(current, resume)["action"], "ensure_followup")
        current["followup"] = followup(current, checked_seconds=30, evidence_ref="view-restored-luna")
        current = apply(current, HELPER.decide(current, {**resume,
                             "followup_view": followup(current, checked_seconds=30, evidence_ref="view-fresh-resume")}))
        checking = HELPER.decide(current, notification_check(current, 40), paused_tick["observer_updates"])
        self.assertEqual(checking["action"], "check_controller_receipt")
        self.assertEqual(checking["schedule_action"], "keep_active")
        self.assertFalse(checking["observe_webpage"])
        self.assertEqual(checking["observer_updates"]["notifications"][0]["controller_event"], full["controller_event"])

    def test_existing_processed_reply_and_legacy_observer_naturally_close(self):
        current = authorized(state())
        full = collected(current)
        current = ready_review()
        self.assertNotIn("received_notifications", current)
        for legacy in (False, True):
            ledger = copy.deepcopy(full["observer_updates"])
            if legacy:
                ledger["notifications"] = [{"key": full["notification_key"], "status": "unknown", "evidence": ["io/old.json"]}]
            with self.subTest(legacy=legacy):
                stopped = HELPER.decide(current, notification_check(current, 20), ledger)
                self.assertEqual(stopped["action"], "pause_followup")
                self.assertEqual(stopped["schedule_action"], "pause_if_active")
                self.assertEqual(stopped["observer_updates"]["notifications"][0]["status"], "received")
        unverified = {**current, "last_completion": {**current["last_completion"], "body_sha256": "d" * 64}}
        still_open = HELPER.decide(unverified, notification_check(unverified, 20), ledger)
        self.assertEqual(still_open["action"], "check_controller_receipt")
        self.assertEqual(still_open["schedule_action"], "keep_active")
        self.assertNotEqual(still_open["observer_updates"]["notifications"][0]["status"], "received")

    def test_controller_receipt_can_be_recorded_with_assessment_or_direct_shared_read(self):
        current = authorized(state())
        full = collected(current)
        current = ready_review()
        metadata = {key: full["controller_event"][key] for key in ("notification_key", "notification_receipt_sha256")}
        assessed = HELPER.decide(current, event(current, "assessment", review_message_id="message-1",
                                 coverage_complete=True, confirmed_findings=1, unresolved_claims=0, **metadata))
        self.assertIn(full["notification_key"], assessed["state_updates"]["received_notifications"])
        read = HELPER.decide(current, event(current, "controller_received", evidence=["controller/read-saved-result.json"], **metadata))
        self.assertEqual(read["action"], "record_controller_receipt")
        self.assertEqual(read["state_updates"]["received_notifications"][full["notification_key"]]["evidence"],
                         ["controller/read-saved-result.json"])
        tampered = {**full["controller_event"], "body_sha256": "d" * 64}
        with self.assertRaisesRegex(ValueError, "payload SHA mismatch"):
            HELPER.decide(state(), tampered)

    def test_controller_cannot_close_while_another_result_is_unreceived(self):
        current = authorized(state())
        progress = HELPER.decide(current, scheduled(current, generation="generating", actionable_progress=True,
                               actionable_progress_ref="ui/progress.json"))
        first = HELPER.decide(current, scheduled(current, 10), progress["observer_updates"])
        full = HELPER.decide(current, scheduled(current, 20), first["observer_updates"])
        triaged = HELPER.decide(current, full["controller_event"], full["observer_updates"])
        self.assertEqual(triaged["schedule_action"], "keep_active")
        current = apply(current, triaged)
        premature = HELPER.decide(current, closed_followup(current), full["observer_updates"])
        self.assertEqual(premature["action"], "ensure_followup")
        self.assertFalse(premature["terminal"])
        self.assertEqual(premature["schedule_action"], "keep_active")
        received = event(current, "controller_received", evidence=["controller/read-progress.json"],
                         **{key: progress["controller_event"][key] for key in ("notification_key", "notification_receipt_sha256")})
        current = apply(current, HELPER.decide(current, received, full["observer_updates"]))
        self.assertEqual(HELPER.decide(current, closed_followup(current), full["observer_updates"])["action"], "continue_current_step")

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
        current = apply(current, HELPER.decide(current, full["controller_event"], full["observer_updates"]))
        self.assertIn(full["notification_key"], current["received_notifications"])
        received = HELPER.decide(current, inline_event(notification_check(current, 20)), full["observer_updates"])
        self.assertEqual(received["action"], "finish_inline_capture")
        self.assertEqual(received["schedule_action"], "none")
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
