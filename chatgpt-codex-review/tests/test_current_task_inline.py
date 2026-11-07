"""Offline current-task native Luna collection and exit-obligation regressions."""

import copy
import unittest

from test_review_cycle import A, HELPER, apply, event, observation, preparation, state


def current_task(phase="waiting_web"):
    current = state(phase)
    current.update(execution_scope="review_only", followup_mode="inline",
                   web_io_binding=None, followup=None,
                   inline_policy={"basis": "current_task", "task_instruction_ref": "authority/research-request.md",
                                  "native_return_ref": "runtime/native-parent-return.json", "turn_id": "active-turn"},
                   inline_observer_binding={
                       "surface": "internal_agent", "agent_id": "/root/luna-web-io",
                       "execution_ref": "runtime/luna-execution.json", "turn_id": "active-turn",
                       "model": "gpt-6-luna", "reasoning": "max", "runtime_pair_verified": True,
                       "model_readback_ref": "runtime/luna-pair.json", "reasoning_readback_ref": "runtime/luna-pair.json",
                       "verified_at": "2025-12-31T23:59:59+00:00", "deadline_at": "2026-01-01T00:10:00+00:00"})
    current["acceptance_contract"] = {"required_checks": [], "delivery_items": ["review report"]}
    current["acceptance_digest"] = HELPER.acceptance_digest(current["acceptance_contract"])
    return current


def native_event(current, item):
    binding = current["inline_observer_binding"]
    return {**item, "inline_execution_ref": binding["execution_ref"], "inline_turn_id": binding["turn_id"]}


def checkpoint(current, kind="turn_end", when="2026-01-01T00:00:20+00:00"):
    return native_event(current, event(current, "followup_check", checkpoint=kind, observed_at=when))


def observed(current, seconds=0, **fields):
    return native_event(current, {**observation(current, seconds, **fields), "type": "inline_observation"})


class CurrentTaskInlineTests(unittest.TestCase):
    def test_new_request_submits_collects_and_is_received_without_message_authority_or_timer(self):
        current = current_task("ready_to_submit")
        current.update(conversation_url=None, prepared_request=None)
        prepared = HELPER.decide(current, native_event(current, preparation(current)))
        self.assertEqual(prepared["action"], "verify_before_submit")
        self.assertEqual(prepared["schedule_action"], "none")
        current = apply(current, prepared)
        checked = HELPER.decide(current, checkpoint(current, "before_submit"))
        self.assertEqual(checked["action"], "verify_before_submit")
        self.assertFalse(checked["submission_ready"])
        absent = native_event(current, event(current, "submission", status="not_sent", definitive_absence=True,
                                             conversation_url=None, observed_at="2026-01-01T00:00:20+00:00"))
        sending = HELPER.decide(current, absent)
        self.assertEqual(sending["action"], "submit_once")
        self.assertTrue(sending["submission_ready"])
        self.assertEqual(sending["schedule_action"], "none")
        current = apply(current, sending)
        sent = native_event(current, event(current, "submission", status="sent", request_present=True,
                                          conversation_url="https://chatgpt.com/c/native-current-task", user_message_id="native-user",
                                          ui_model_verified=True, prompt_sha256="e" * 64,
                                          observed_at="2026-01-01T00:00:20+00:00"))
        current = apply(current, HELPER.decide(current, sent))
        first = HELPER.decide(current, observed(current, 20))
        self.assertEqual(first["action"], "keep_quiet")
        full = HELPER.decide(current, observed(current, 30), first["observer_updates"])
        self.assertEqual(full["action"], "return_to_controller")
        self.assertEqual(full["schedule_action"], "none")
        self.assertTrue(full["activate_controller"])
        self.assertEqual(full["observer_updates"]["notifications"][0]["attempts"], 0)
        current = apply(current, HELPER.decide(current, full["controller_event"], full["observer_updates"]))
        self.assertTrue(current["received_notifications"][full["notification_key"]]["applied"])
        closed = HELPER.decide(current, checkpoint(current), full["observer_updates"])
        self.assertEqual(closed["action"], "continue_current_step")
        self.assertEqual(closed["schedule_action"], "none")
        current = apply(current, HELPER.decide(current, event(current, "assessment", review_message_id="message-1",
                                                             coverage_complete=True, confirmed_findings=0, unresolved_claims=0)))
        done = HELPER.decide(current, event(current, "delivery", delivered_source_id=A, complete=True))
        self.assertTrue(done["terminal"])
        self.assertIsNone(current["followup"])
        self.assertIsNone(current["web_io_binding"])
        self.assertNotIn("controller_notification_authorization", current)

    def test_unfinished_current_task_continues_the_active_turn_at_exit_checkpoints(self):
        current = current_task()
        before = copy.deepcopy(current)
        for kind in ("turn_end", "inline_deadline"):
            with self.subTest(kind=kind):
                answer = HELPER.decide(current, checkpoint(current, kind))
                self.assertEqual(answer["action"], "continue_inline_collection")
                self.assertEqual(answer["schedule_action"], "none")
                self.assertFalse(answer["terminal"])
                self.assertFalse(answer["submission_ready"])
                self.assertEqual(apply(current, answer), before)

    def test_expired_or_different_turn_or_execution_cannot_submit_or_keep_observing(self):
        current = current_task("ready_to_submit")
        prepared = native_event(current, preparation(current))
        for changes in ({"observed_at": "2026-01-01T00:10:01+00:00"},
                        {"inline_turn_id": "other-turn"}, {"inline_execution_ref": "runtime/other.json"}):
            with self.subTest(changes=changes):
                answer = HELPER.decide(current, {**prepared, **changes})
                self.assertEqual(answer["action"], "ensure_inline_luna")
                self.assertEqual(answer["schedule_action"], "none")
        waiting = current_task()
        expired = HELPER.decide(waiting, checkpoint(waiting, "inline_deadline", "2026-01-01T00:10:01+00:00"))
        self.assertEqual(expired["action"], "ensure_inline_luna")
        self.assertEqual(expired["schedule_action"], "none")
        self.assertFalse(expired["terminal"])

    def test_current_task_requires_runtime_pair_and_real_internal_agent_identity(self):
        for changes in ({"model": "gpt-6-astra"}, {"reasoning": "high"}, {"runtime_pair_verified": False},
                        {"model_readback_ref": ""}, {"reasoning_readback_ref": ""}, {"agent_id": ""}):
            with self.subTest(changes=changes):
                current = current_task("ready_to_submit")
                current["inline_observer_binding"].update(changes)
                answer = HELPER.decide(current, native_event(current, preparation(current)))
                self.assertEqual(answer["action"], "ensure_inline_luna")
                self.assertEqual(answer["schedule_action"], "none")
        current = current_task("ready_to_submit")
        current["inline_observer_binding"].pop("agent_id")
        self.assertEqual(HELPER.decide(current, native_event(current, preparation(current)))["action"], "ensure_inline_luna")

    def test_missing_task_return_or_turn_evidence_requests_inline_evidence(self):
        for field in ("task_instruction_ref", "native_return_ref", "turn_id"):
            with self.subTest(field=field):
                current = current_task("ready_to_submit")
                current["inline_policy"].pop(field)
                answer = HELPER.decide(current, native_event(current, preparation(current)))
                self.assertEqual(answer["action"], "ensure_inline_luna")
                self.assertEqual(answer["schedule_action"], "none")
        current = current_task("ready_to_submit")
        current["inline_policy"]["turn_id"] = "different-policy-turn"
        self.assertEqual(HELPER.decide(current, native_event(current, preparation(current)))["action"], "ensure_inline_luna")

    def test_explicit_durable_visible_or_existing_owner_is_never_downgraded(self):
        durable = current_task("ready_to_submit")
        durable["durable_followup_requested"] = True
        with self.assertRaisesRegex(ValueError, "cannot silently become inline"):
            HELPER.decide(durable, native_event(durable, preparation(durable)))
        original = state("ready_to_submit")
        for changes in ({"visible_task_requested": True}, {"web_io_binding": original["web_io_binding"]},
                        {"followup": original["followup"]}):
            with self.subTest(changes=changes):
                current = {**current_task("ready_to_submit"), **changes}
                self.assertFalse(HELPER.inline_policy_valid(current))
                answer = HELPER.decide(current, native_event(current, preparation(current)))
                self.assertEqual(answer["action"], "ensure_durable_followup")
                self.assertFalse(answer["submission_ready"])
                self.assertNotIn("followup_mode", answer["state_updates"])

    def test_real_original_user_model_override_stays_supported(self):
        current = current_task("ready_to_submit")
        current["inline_observer_binding"].update(model="gpt-6-sol", reasoning="high", route_basis="explicit_user",
                                                  user_override_ref="authority/original-model-choice.md")
        self.assertEqual(HELPER.decide(current, native_event(current, preparation(current)))["action"], "verify_before_submit")

    def test_captured_unreceived_result_is_applied_before_any_expired_execution_repair(self):
        current = current_task()
        current["submitted_user_message_id"] = "original-user-message"
        first = HELPER.decide(current, observed(current))
        full = HELPER.decide(current, observed(current, 10), first["observer_updates"])
        ledger = copy.deepcopy(full["observer_updates"])
        ledger.update(refresh_count=3, browser_recovery_attempts=2)
        saved = copy.deepcopy(ledger)
        answer = HELPER.decide(current, checkpoint(current, "turn_end", "2026-01-01T00:10:01+00:00"), ledger)
        self.assertEqual(answer["action"], "receive_saved_result")
        self.assertEqual(answer["controller_event"], full["controller_event"])
        self.assertEqual(answer["schedule_action"], "none")
        self.assertEqual(ledger, saved)
        current = apply(current, HELPER.decide(current, answer["controller_event"], ledger))
        closed = HELPER.decide(current, checkpoint(current, "turn_end", "2026-01-01T00:10:01+00:00"), ledger)
        self.assertEqual(closed["action"], "continue_current_step")
        self.assertEqual(closed["schedule_action"], "none")

    def test_browser_recovery_cannot_replace_the_policy_turn(self):
        current = current_task()
        current.update(submitted_user_message_id="original-user-message", submitted_prompt_sha256="e" * 64)
        renewed = {**current["inline_observer_binding"], "turn_id": "another-turn",
                   "execution_ref": "runtime/restored.json", "verified_at": "2026-01-01T00:11:39+00:00",
                   "deadline_at": "2026-01-01T00:20:00+00:00"}
        recovered = event(current, "browser_recovered", reason_code="space_missing", observed_at="2026-01-01T00:11:40+00:00",
                          conversation_url=current["conversation_url"], old_space_id="old-space",
                          browser_context={"space_id": "restored-space", "page_label": "p1", "ownership": "agent"},
                          recovery_evidence_ref="runtime/recovered.json", request_status="present",
                          user_message_id="original-user-message", prompt_sha256="e" * 64,
                          inline_observer_binding=renewed, inline_turn_id=renewed["turn_id"],
                          inline_execution_ref=renewed["execution_ref"])
        with self.assertRaisesRegex(ValueError, "actual current execution evidence"):
            HELPER.decide(current, recovered)
        renewed["turn_id"] = current["inline_policy"]["turn_id"]
        recovered["inline_turn_id"] = renewed["turn_id"]
        answer = HELPER.decide(current, recovered)
        self.assertEqual(answer["action"], "watch")
        self.assertEqual(answer["schedule_action"], "none")
        self.assertEqual(answer["state_updates"]["inline_observer_binding"]["turn_id"], current["inline_policy"]["turn_id"])

    def test_current_task_exit_checkpoint_preserves_real_browser_input_gates(self):
        for code in HELPER.HUMAN_BROWSER_GATES:
            with self.subTest(code=code):
                current = current_task()
                stopped = HELPER.decide(current, observed(current, ui_error=code, error_fingerprint="actual-browser-stop"))
                ledger = stopped["observer_updates"]
                checked = HELPER.decide(current, checkpoint(current), ledger)
                self.assertEqual(checked["action"], "request_browser_input")
                self.assertFalse(checked["observe_webpage"])
                self.assertEqual(checked["schedule_action"], "none")
                self.assertFalse(checked["terminal"])
                self.assertEqual(checked["state_updates"]["browser_gate"], ledger["browser_gate"])


if __name__ == "__main__":
    unittest.main()
