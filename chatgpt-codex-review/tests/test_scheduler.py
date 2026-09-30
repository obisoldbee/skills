"""Offline scheduler ownership, scope and quiet observation regressions."""

import copy
from datetime import datetime, timedelta, timezone
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
import zipfile

from test_review_cycle import (A, B, HELPER, ROOT, apply, closed_followup, event, followup,
                               observation, preparation, ready_review, receipt, state,
                               submission, with_required)
from test_source_and_artifacts import FILES


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


class IntegrationOrderTests(unittest.TestCase):
    def submitted(self, required=False, artifact_root=None):
        current = with_required(state("submitting")) if required else state("submitting")
        if artifact_root is not None:
            current["artifact_root"] = str(artifact_root)
        current["execution_scope"] = "review_only"
        current["prepared_request"].update(execution_scope="review_only", contract_digest=current["contract_digest"])
        return apply(current, HELPER.decide(current, submission(current)))

    def complete(self, current, ledger, seconds=10):
        first = HELPER.decide(current, scheduled(current, seconds), ledger)
        return HELPER.decide(current, scheduled(current, seconds + 10), first["observer_updates"])

    def acknowledge(self, current, item, ledger):
        return HELPER.decide(current, event(current, "controller_received", notification_key=item["key"],
                            notification_receipt_sha256=item["receipt_sha256"]), ledger)

    def test_two_applied_progress_events_cannot_revive_or_preempt_a_complete_report(self):
        current, ledger = self.submitted(), None
        progress = []
        for number in (1, 2):
            observed = HELPER.decide(current, scheduled(current, number, completion_controls=False,
                                    body_sha256=str(number) * 64, actionable_progress=True,
                                    actionable_progress_ref=f"ui/progress-{number}.json"), ledger)
            ledger = observed["observer_updates"]
            progress.append(copy.deepcopy(observed["controller_event"]))
            current = apply(current, HELPER.decide(current, progress[-1], ledger))
        full = self.complete(current, ledger)
        ledger, payload = full["observer_updates"], copy.deepcopy(full["controller_event"])
        read = self.acknowledge(current, ledger["notifications"][-1], ledger)
        self.assertEqual(read["controller_event"], payload)
        current = apply(current, read)
        for original in progress:
            again = HELPER.decide(current, original, ledger)
            self.assertEqual(apply(current, again)["web_progress"], current["web_progress"])
        closed = HELPER.decide(current, closed_followup(current), ledger)
        self.assertEqual(closed["controller_event"], payload)
        current = apply(current, closed)
        processed = HELPER.decide(current, payload, ledger)
        self.assertEqual(processed["action"], "triage_review")
        current = apply(current, processed)
        for original in [*progress, payload]:
            again = HELPER.decide(current, original, ledger)
            self.assertEqual(apply(current, again), current)
        self.assertEqual(ledger["notifications"][-1]["controller_event"], payload)

    def test_required_artifacts_first_then_text_closes_capture_before_controller_application(self):
        current = self.submitted(required=True)
        captured = HELPER.decide(current, event(current, "scheduled_artifacts", receipt=receipt(current),
                                observed_at="2026-01-01T00:00:01+00:00",
                                followup_view=followup(current, checked_seconds=1)))
        full = self.complete(current, captured["observer_updates"])
        ledger = full["observer_updates"]
        self.assertTrue(ledger["required_artifacts_ready"])
        self.assertFalse(HELPER.artifact_ready(current))
        for item in ledger["notifications"]:
            current = apply(current, self.acknowledge(current, item, ledger))
        checked = HELPER.decide(current, notification_check(current, 20), ledger)
        self.assertFalse(checked["observe_webpage"])
        self.assertEqual(checked["action"], "pause_followup")
        closed = HELPER.decide(current, closed_followup(current), checked["observer_updates"])
        self.assertEqual(closed["action"], "process_saved_result")
        current = apply(current, closed)
        artifact = HELPER.decide(current, closed["controller_event"], ledger)
        self.assertTrue(HELPER.artifact_ready(apply(current, artifact)))
        current = apply(current, artifact)
        remaining = HELPER.decide(current, event(current, "followup_readback", followup=current["followup"]), ledger)
        self.assertEqual(remaining["controller_event"], full["controller_event"])
        processed = HELPER.decide(current, remaining["controller_event"], ledger)
        self.assertEqual(processed["action"], "triage_review")
        self.assertEqual(processed["schedule_action"], "pause_if_active")
        self.assertEqual(captured["controller_event"], ledger["notifications"][0]["controller_event"])

    def test_replayed_same_space_success_cannot_clear_a_later_incident(self):
        current = self.submitted()
        current["browser_context"] = {"space_id": "same-space", "page_label": "p1", "ownership": "agent"}
        fault = event(current, "browser_fault", reason_code="connection_failed", observed_at="2026-01-01T00:00:01+00:00")
        current = apply(current, HELPER.decide(current, fault))
        success = recovery(current, 3, reason_code="connection_failed", old_space_id="same-space",
                           browser_context={"space_id": "same-space", "page_label": "p1", "ownership": "agent"})
        current = apply(current, HELPER.decide(current, success))
        for seconds in (10, 11):
            current = apply(current, HELPER.decide(current, event(current, "browser_fault", reason_code="connection_failed",
                            observed_at=f"2026-01-01T00:00:{seconds}+00:00")))
        self.assertEqual(current["browser_recovery_attempts"], 2)
        replayed = HELPER.decide(current, success)
        self.assertEqual(apply(current, replayed), current)
        self.assertEqual(HELPER.decide(current, event(current, "browser_fault", reason_code="connection_failed",
                         observed_at="2026-01-01T00:00:12+00:00"))["action"], "diagnose_browser_recovery")

    def test_receipt_only_progress_stays_unapplied_until_each_original_event_is_consumed(self):
        current, ledger = self.submitted(), None
        payloads = []
        for number in (1, 2):
            observed = HELPER.decide(current, scheduled(current, number, completion_controls=False,
                                    body_sha256=str(number) * 64, actionable_progress=True,
                                    actionable_progress_ref=f"ui/unapplied-{number}.json"), ledger)
            ledger = observed["observer_updates"]
            payloads.append(copy.deepcopy(observed["controller_event"]))
            current = apply(current, self.acknowledge(current, ledger["notifications"][-1], ledger))
            self.assertFalse(current["received_notifications"][observed["notification_key"]]["applied"])
        full = self.complete(current, ledger)
        ledger = full["observer_updates"]
        current = apply(current, self.acknowledge(current, ledger["notifications"][-1], ledger))
        for number, original in enumerate([*payloads, full["controller_event"]]):
            check = closed_followup(current) if number == 0 else event(current, "followup_readback", followup=current["followup"])
            saved = HELPER.decide(current, check, ledger)
            self.assertEqual(saved["controller_event"], original)
            current = apply(current, saved)
            current = apply(current, HELPER.decide(current, original, ledger))
            item = next(item for item in ledger["notifications"] if item["key"] == original["notification_key"])
            current = apply(current, self.acknowledge(current, item, ledger))
            self.assertTrue(current["received_notifications"][item["key"]]["applied"])
        self.assertEqual(current["phase"], "review_ready")
        self.assertNotEqual(HELPER.decide(current, event(current, "followup_readback", followup=current["followup"]), ledger)["action"], "process_saved_result")

    def test_same_key_with_wrong_sha_or_business_cannot_claim_an_event_was_applied(self):
        current = self.submitted()
        observed = HELPER.decide(current, scheduled(current, 1, completion_controls=False,
                                actionable_progress=True, actionable_progress_ref="ui/one.json"))
        payload, ledger = observed["controller_event"], observed["observer_updates"]
        current = apply(current, HELPER.decide(current, payload, ledger))
        wrong = {**payload, "body_sha256": "f" * 64}
        with self.assertRaisesRegex(ValueError, "payload SHA"):
            HELPER.decide(current, wrong, ledger)
        with self.assertRaisesRegex(ValueError, "different payload SHA"):
            HELPER.decide(current, event(current, "controller_received", notification_key=payload["notification_key"],
                          notification_receipt_sha256="f" * 64), ledger)
        other = copy.deepcopy(current)
        other.update(round=2, request_token="different-round")
        other["used_request_tokens"].append("different-round")
        with self.assertRaisesRegex(ValueError, "stale or mismatched"):
            HELPER.decide(other, payload, ledger)
        self.assertEqual(current["web_progress"]["evidence_ref"], "ui/one.json")

    def test_unverified_boolean_and_old_or_corrupt_artifact_proofs_do_not_close_capture(self):
        current = self.submitted(required=True)
        captured = HELPER.decide(current, event(current, "scheduled_artifacts", receipt=receipt(current),
                                observed_at="2026-01-01T00:00:01+00:00", followup_view=followup(current, checked_seconds=1)))
        full = self.complete(current, captured["observer_updates"])
        ledger = full["observer_updates"]
        self.assertFalse(HELPER.web_capture_required(current, ledger))
        old = copy.deepcopy(ledger)
        del old["artifact_observation"]
        self.assertFalse(HELPER.web_capture_required(current, old))
        for mutation in ("boolean_only", "wrong_sha", "old_contract", "failed_file"):
            with self.subTest(mutation=mutation):
                invalid = copy.deepcopy(ledger)
                if mutation == "boolean_only":
                    invalid.pop("artifact_observation")
                    invalid["notifications"] = []
                elif mutation == "wrong_sha":
                    invalid["artifact_observation"]["sha256"] = "f" * 64
                else:
                    original = invalid["artifact_observation"]["payload"]
                    if mutation == "old_contract":
                        original["receipt"]["contract_digest"] = "f" * 64
                    else:
                        original["receipt"]["files"]["report"]["status"] = "invalid"
                    invalid["artifact_observation"]["sha256"] = HELPER.notification_digest(original)
                self.assertTrue(HELPER.web_capture_required(current, invalid))
        other = with_required(state())
        other["artifact_contract"]["required"].append({"name": "new-report", "kind": "utf8"})
        other["contract_digest"] = HELPER.contract_digest(other["artifact_contract"])
        self.assertTrue(HELPER.web_capture_required(other, ledger))

    def test_actual_file_revalidation_revokes_capture_and_final_delivery_until_restored(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            path = root / "report.txt"
            good = b"complete original report\n"
            path.write_bytes(good)
            current = state("submitting")
            current.update(execution_scope="review_only", artifact_root=str(root),
                           artifact_contract={"required": [{"name": "report", "kind": "utf8",
                                              "sha256": hashlib.sha256(good).hexdigest()}], "optional": []})
            current["contract_digest"] = HELPER.contract_digest(current["artifact_contract"])
            current["prepared_request"].update(execution_scope="review_only", contract_digest=current["contract_digest"])
            current = apply(current, HELPER.decide(current, submission(current)))
            request = {"binding": {key: current[key] for key in ("run_id", "round", "source_id", "request_token", "consumer_host", "artifact_root")},
                       "artifact_contract": current["artifact_contract"], "files": {"report": str(path)}}
            def capture(seconds, ledger=None):
                verified = FILES.verify(request)
                observed = event(current, "scheduled_artifacts", receipt=verified,
                                 observed_at=(datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=seconds)).isoformat(),
                                 followup_view=followup(current, checked_seconds=seconds))
                return verified, HELPER.decide(current, observed, ledger)
            valid, saved = capture(1)
            self.assertEqual(valid["files"]["report"]["status"], "verified")
            original_artifact = copy.deepcopy(saved["controller_event"])
            current = apply(current, HELPER.decide(current, original_artifact, saved["observer_updates"]))
            full = self.complete(current, saved["observer_updates"])
            ledger = full["observer_updates"]
            current = apply(current, HELPER.decide(current, full["controller_event"], ledger))
            current = apply(current, HELPER.decide(current, event(current, "assessment", review_message_id="message-1",
                            coverage_complete=True, confirmed_findings=0, unresolved_claims=0, file_dependent_findings=0), ledger))
            current = apply(current, HELPER.decide(current, event(current, "validation", checked_source_id=A,
                            passed=True, required_unverified=[]), ledger))
            self.assertEqual(current["phase"], "validating")
            path.write_bytes(b"changed bytes after verification\n")
            failed, invalid = capture(30, ledger)
            ledger = invalid["observer_updates"]
            self.assertEqual(failed["files"]["report"]["status"], "invalid")
            self.assertFalse(ledger["required_artifacts_ready"])
            self.assertTrue(HELPER.artifact_ready(current))
            delivery_event = event(current, "delivery", delivered_source_id=A, complete=True)
            blocked = HELPER.decide(current, delivery_event, ledger)
            self.assertEqual(blocked["action"], "obtain_required_artifacts")
            self.assertFalse(blocked["terminal"])
            self.assertEqual(blocked["schedule_action"], "keep_active")
            current = apply(current, blocked)
            refused_close = HELPER.decide(current, event(current, "followup_closed",
                                         followup=followup(current, checked_seconds=51, status="PAUSED")), ledger)
            self.assertFalse(refused_close["terminal"])
            self.assertNotEqual(refused_close["action"], "complete")
            path.write_bytes(good)
            restored, ready = capture(60, ledger)
            ledger = ready["observer_updates"]
            self.assertEqual(restored["files"]["report"]["status"], "verified")
            self.assertTrue(ledger["required_artifacts_ready"])
            delivered = HELPER.decide(current, delivery_event, ledger)
            self.assertEqual(delivered["action"], "disable_followup")
            current = apply(current, delivered)
            complete = HELPER.decide(current, event(current, "followup_closed",
                                    followup=followup(current, checked_seconds=70, status="PAUSED")), ledger)
            self.assertTrue(complete["terminal"])
            self.assertEqual(complete["phase"], "completed")
            self.assertEqual(ledger["notifications"][0]["controller_event"], original_artifact)

    def test_new_same_space_success_with_same_reference_is_fresh_and_resets_only_the_current_incident(self):
        current = self.submitted()
        current["browser_context"] = {"space_id": "same-space", "page_label": "p1", "ownership": "agent"}
        current = apply(current, HELPER.decide(current, event(current, "browser_fault", reason_code="connection_failed",
                        observed_at="2026-01-01T00:00:01+00:00")))
        first = recovery(current, 3, reason_code="connection_failed", old_space_id="same-space",
                         browser_context={"space_id": "same-space", "page_label": "p1", "ownership": "agent"})
        current = apply(current, HELPER.decide(current, first))
        duplicate = HELPER.decide(current, first)
        self.assertEqual(apply(current, duplicate), current)
        fault = HELPER.decide(current, scheduled(current, 10, ui_error="connection_failed", error_fingerprint="new-incident"))
        second = HELPER.decide(current, scheduled(current, 11, ui_error="connection_failed", error_fingerprint="new-incident"), fault["observer_updates"])
        ledger = second["observer_updates"]
        self.assertEqual(HELPER.recovery_attempts(current, ledger), 2)
        replayed = HELPER.decide(current, first, ledger)
        self.assertEqual(apply(current, replayed), current)
        self.assertEqual(HELPER.recovery_attempts(current, ledger), 2)
        fresh = recovery(current, 15, reason_code="connection_failed", old_space_id="same-space",
                         browser_context={"space_id": "same-space", "page_label": "p1", "ownership": "agent"},
                         recovery_evidence_ref=first["recovery_evidence_ref"])
        restored = HELPER.decide(current, fresh, ledger)
        self.assertEqual(restored["action"], "watch")
        current = apply(current, restored)
        self.assertEqual(HELPER.recovery_attempts(current, ledger), 0)
        future = HELPER.decide(current, event(current, "browser_fault", reason_code="connection_failed",
                              observed_at="2026-01-01T00:00:20+00:00"), ledger)
        self.assertEqual(future["state_updates"]["browser_recovery_attempts"], 1)
        current = apply(current, future)
        continued = HELPER.decide(current, scheduled(current, 21, ui_error="connection_failed",
                                  error_fingerprint="new-incident"), ledger)
        self.assertEqual(continued["action"], "recover_browser_context")
        self.assertEqual(continued["observer_updates"]["browser_recovery_attempts"], 2)
        exhausted = HELPER.decide(current, scheduled(current, 22, ui_error="connection_failed",
                                 error_fingerprint="new-incident"), continued["observer_updates"])
        self.assertEqual(exhausted["action"], "diagnose_browser_recovery")

    def test_renamed_or_cross_turn_old_success_cannot_precede_a_new_fault(self):
        current = self.submitted()
        current["browser_context"] = {"space_id": "same-space", "page_label": "p1", "ownership": "agent"}
        current = apply(current, HELPER.decide(current, event(current, "browser_fault", reason_code="connection_failed",
                        observed_at="2026-01-01T00:00:01+00:00")))
        first = recovery(current, 3, reason_code="connection_failed", old_space_id="same-space",
                         browser_context={"space_id": "same-space", "page_label": "p1", "ownership": "agent"})
        current = apply(current, HELPER.decide(current, first))
        for seconds in (10, 11):
            current = apply(current, HELPER.decide(current, event(current, "browser_fault", reason_code="connection_failed",
                            observed_at=f"2026-01-01T00:00:{seconds}+00:00")))
        renamed = {**first, "recovery_evidence_ref": "ui/renamed-old-success.json", "request_status": "unknown"}
        self.assertEqual(apply(current, HELPER.decide(current, renamed)), current)
        premature = {**recovery(current, 4, reason_code="connection_failed", old_space_id="same-space",
                      browser_context={"space_id": "same-space", "page_label": "p1", "ownership": "agent"}),
                     "request_status": "unknown"}
        with self.assertRaisesRegex(ValueError, "predates the current fault"):
            HELPER.decide(current, premature)
        current = inline(current)
        current["inline_observer_binding"]["turn_id"] = "later-turn"
        current["inline_observer_binding"]["execution_ref"] = "tasks/later-luna.json"
        replayed = HELPER.decide(current, first)
        self.assertEqual(apply(current, replayed), current)
        self.assertEqual(replayed["schedule_action"], "none")

    def test_received_updated_required_file_is_applied_locally_before_final_delivery(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "report.zip"
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("report.txt", "original complete report")
            current = self.submitted(required=True, artifact_root=directory)
            request = {"binding": {key: current[key] for key in ("run_id", "round", "source_id", "request_token", "consumer_host", "artifact_root")},
                       "artifact_contract": current["artifact_contract"], "files": {"report": str(path)}}
            original_receipt = FILES.verify(request)
            saved = HELPER.decide(current, event(current, "scheduled_artifacts", receipt=original_receipt,
                                 observed_at="2026-01-01T00:00:01+00:00", followup_view=followup(current, checked_seconds=1)))
            original_payload = copy.deepcopy(saved["controller_event"])
            current = apply(current, HELPER.decide(current, original_payload, saved["observer_updates"]))
            full = self.complete(current, saved["observer_updates"])
            ledger = full["observer_updates"]
            current = apply(current, HELPER.decide(current, full["controller_event"], ledger))
            current = apply(current, HELPER.decide(current, event(current, "assessment", review_message_id="message-1",
                            coverage_complete=True, confirmed_findings=0, unresolved_claims=0, file_dependent_findings=0), ledger))
            current = apply(current, HELPER.decide(current, event(current, "validation", checked_source_id=A,
                            passed=True, required_unverified=[]), ledger))
            with zipfile.ZipFile(path, "w") as archive:
                archive.writestr("report.txt", "updated complete report")
            updated_receipt = FILES.verify(request)
            self.assertTrue(updated_receipt["required_ready"])
            self.assertNotEqual(updated_receipt["files"]["report"]["sha256"], original_receipt["files"]["report"]["sha256"])
            updated = HELPER.decide(current, event(current, "scheduled_artifacts", receipt=updated_receipt,
                                   observed_at="2026-01-01T00:00:30+00:00", followup_view=followup(current, checked_seconds=30)), ledger)
            ledger = updated["observer_updates"]
            current = apply(current, self.acknowledge(current, ledger["notifications"][-1], ledger))
            self.assertEqual(current["artifact_receipt"], original_receipt)
            self.assertFalse(current["received_notifications"][updated["notification_key"]]["applied"])
            delivery_event = event(current, "delivery", delivered_source_id=A, complete=True)
            deliver = HELPER.decide(current, delivery_event, ledger)
            self.assertEqual(deliver["action"], "process_saved_result")
            self.assertEqual(deliver["controller_event"], updated["controller_event"])
            self.assertEqual(deliver["schedule_action"], "pause_if_active")
            self.assertFalse(deliver["terminal"])
            current = apply(current, deliver)
            applied = HELPER.decide(current, deliver["controller_event"], ledger)
            self.assertEqual(applied["action"], "disable_followup")
            self.assertEqual(applied["state_updates"]["artifact_receipt"], updated_receipt)
            self.assertEqual(ledger["notifications"][0]["controller_event"], original_payload)


class ArtifactSnapshotTests(unittest.TestCase):
    complete = IntegrationOrderTests.complete
    acknowledge = IntegrationOrderTests.acknowledge

    def prepared(self, directory, scope="review_only", mode="durable", fixed_hash=False):
        root = Path(directory)
        original = b"original complete report A\n"
        (root / "report.txt").write_bytes(original)
        current = state("submitting")
        required = {"name": "report", "kind": "utf8"}
        if fixed_hash:
            required["sha256"] = hashlib.sha256(original).hexdigest()
        current.update(execution_scope=scope, artifact_root=str(root), artifact_contract={
            "required": [required], "optional": [{"name": "preview", "kind": "utf8"}]})
        current["contract_digest"] = HELPER.contract_digest(current["artifact_contract"])
        current["prepared_request"].update(execution_scope=scope, contract_digest=current["contract_digest"])
        if mode == "inline":
            current = inline(current)
        sent = submission(current) if mode == "durable" else inline_event(submission({**current,
            "web_io_binding": state()["web_io_binding"]}))
        return apply(current, HELPER.decide(current, sent))

    def verify(self, current):
        root = Path(current["artifact_root"])
        request = {"binding": {key: current[key] for key in ("run_id", "round", "source_id", "request_token",
                    "consumer_host", "artifact_root")}, "artifact_contract": current["artifact_contract"],
                   "files": {"report": str(root / "report.txt"), "preview": str(root / "preview.txt")}}
        return FILES.verify(request)

    def capture(self, current, seconds, ledger=None):
        moment = datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=seconds)
        fields = {"receipt": self.verify(current), "observed_at": moment.isoformat(),
                  "execution_scope": current["execution_scope"]}
        if current.get("followup_mode") == "inline":
            observed = inline_event(event(current, "inline_artifacts", **fields))
        else:
            observed = event(current, "scheduled_artifacts", followup_view=followup(current, checked_seconds=seconds), **fields)
        return HELPER.decide(current, observed, ledger)

    def reviewed(self, directory, scope="review_only", mode="durable", fixed_hash=False):
        current = self.prepared(directory, scope, mode, fixed_hash)
        files = self.capture(current, 1)
        current = apply(current, HELPER.decide(current, files["controller_event"], files["observer_updates"]))
        ledger = files["observer_updates"]
        for seconds in (10, 20):
            observed = (inline_event({**observation(current, seconds), "type": "inline_observation"})
                        if mode == "inline" else scheduled(current, seconds))
            observed = {**observed, "execution_scope": scope}
            result = HELPER.decide(current, observed, ledger)
            ledger = result["observer_updates"]
        current = apply(current, HELPER.decide(current, result["controller_event"], ledger))
        if scope == "review_only":
            current = apply(current, HELPER.decide(current, event(current, "assessment", review_message_id="message-1",
                            coverage_complete=True, confirmed_findings=0, unresolved_claims=0, file_dependent_findings=0), ledger))
            current = apply(current, HELPER.decide(current, event(current, "validation", checked_source_id=A,
                            passed=True, required_unverified=[]), ledger))
        return current, ledger, copy.deepcopy(files["controller_event"])

    def final_delivery(self, current, ledger):
        return HELPER.decide(current, event(current, "delivery", delivered_source_id=A, complete=True,
                            observed_at="2026-01-01T00:01:00+00:00"), ledger)

    def test_latest_real_invalid_blocks_dependent_dispatch_but_preserves_independent_repair(self):
        for independent in (0, 1):
            with self.subTest(independent=independent), tempfile.TemporaryDirectory() as directory:
                current, ledger, _ = self.reviewed(directory, "repair_loop")
                (Path(directory) / "report.txt").write_bytes(b"\xff invalid utf8")
                invalid = self.capture(current, 30, ledger)
                ledger = invalid["observer_updates"]
                self.assertEqual(self.verify(current)["files"]["report"]["status"], "invalid")
                assessed = HELPER.decide(current, event(current, "assessment", review_message_id="message-1",
                                        coverage_complete=True, confirmed_findings=1 + independent,
                                        unresolved_claims=0, file_dependent_findings=1), ledger)
                self.assertEqual(assessed["action"], "dispatch_repair" if independent else "obtain_required_artifacts")
                self.assertEqual(assessed["state_updates"]["dispatchable_findings"], independent)
                self.assertEqual(assessed["state_updates"]["pending_file_findings"], 1)

    def test_latest_invalid_cannot_close_worker_file_findings_or_resume_dependent_work(self):
        with tempfile.TemporaryDirectory() as directory:
            current, ledger, _ = self.reviewed(directory, "repair_loop")
            assessed = HELPER.decide(current, event(current, "assessment", review_message_id="message-1",
                                    coverage_complete=True, confirmed_findings=2, unresolved_claims=0,
                                    file_dependent_findings=1), ledger)
            current = apply(current, assessed)
            (Path(directory) / "report.txt").write_bytes(b"\xff invalid utf8")
            ledger = self.capture(current, 30, ledger)["observer_updates"]
            worker = event(current, "worker_result", candidate_source_id=B, delivery_path="worker/fixed.md")
            with self.assertRaisesRegex(ValueError, "file-dependent"):
                HELPER.decide(current, {**worker, "addressed_file_findings": 1}, ledger)
            independent = HELPER.decide(current, {**worker, "addressed_file_findings": 0}, ledger)
            self.assertEqual(independent["state_updates"]["pending_file_findings"], 1)
            current = apply(current, independent)
            checked = HELPER.decide(current, event(current, "validation", checked_source_id=B, passed=True,
                                   required_unverified=[]), ledger)
            self.assertEqual(checked["action"], "obtain_required_artifacts")

    def test_optional_queued_receipt_cannot_hide_the_latest_required_snapshot(self):
        for mode in ("durable", "inline"):
            with self.subTest(mode=mode), tempfile.TemporaryDirectory() as directory:
                current, ledger, _ = self.reviewed(directory, mode=mode)
                (Path(directory) / "preview.txt").write_text("optional preview", encoding="utf-8")
                optional = self.capture(current, 30, ledger)
                ledger = optional["observer_updates"]
                current = apply(current, self.acknowledge(current, ledger["notifications"][-1], ledger))
                self.assertNotEqual(self.final_delivery(current, ledger)["action"], "process_saved_result")
                (Path(directory) / "report.txt").write_text("updated required report B", encoding="utf-8")
                required = self.capture(current, 40, ledger)
                ledger = required["observer_updates"]
                current = apply(current, self.acknowledge(current, ledger["notifications"][-1], ledger))
                deliver = self.final_delivery(current, ledger)
                self.assertEqual(deliver["action"], "process_saved_result")
                self.assertEqual(deliver["controller_event"], required["controller_event"])
                self.assertFalse(deliver["terminal"])
                consumed = HELPER.decide(current, deliver["controller_event"], ledger)
                current = apply(current, consumed)
                self.assertEqual(current["artifact_receipt"]["files"]["report"], self.verify(current)["files"]["report"])
                self.assertNotEqual(self.final_delivery(current, ledger)["action"], "process_saved_result")

    def test_actual_A_B_A_reverification_updates_current_snapshot_without_replaying_old_event(self):
        with tempfile.TemporaryDirectory() as directory:
            current, ledger, original_payload = self.reviewed(directory)
            path = Path(directory) / "report.txt"
            original = path.read_bytes()
            original_receipt = copy.deepcopy(current["artifact_receipt"])
            path.write_text("new valid report B", encoding="utf-8")
            changed = self.capture(current, 30, ledger)
            ledger = changed["observer_updates"]
            current = apply(current, HELPER.decide(current, changed["controller_event"], ledger))
            changed_receipt = copy.deepcopy(current["artifact_receipt"])
            self.assertNotEqual(original_receipt["files"]["report"]["sha256"], changed_receipt["files"]["report"]["sha256"])
            replayed = HELPER.decide(current, original_payload, ledger)
            self.assertEqual(apply(current, replayed)["artifact_receipt"], changed_receipt)
            path.write_bytes(original)
            restored = self.capture(current, 40, ledger)
            ledger = restored["observer_updates"]
            self.assertEqual(restored["action"], "keep_quiet")
            self.assertEqual(ledger["notifications"][0]["controller_event"], original_payload)
            deliver = self.final_delivery(current, ledger)
            self.assertEqual(deliver["action"], "process_saved_result")
            self.assertFalse(deliver["terminal"])
            self.assertEqual(deliver["controller_event"]["receipt"], original_receipt)
            self.assertEqual(deliver["controller_event"]["observed_at"], "2026-01-01T00:00:40+00:00")
            current = apply(current, HELPER.decide(current, deliver["controller_event"], ledger))
            self.assertEqual(current["artifact_receipt"], original_receipt)
            self.assertNotEqual(self.final_delivery(current, ledger)["action"], "process_saved_result")
            self.assertEqual(apply(current, HELPER.decide(current, original_payload, ledger))["artifact_receipt"], original_receipt)

    def test_new_actual_controller_verification_supersedes_old_invalid_observer_proof(self):
        with tempfile.TemporaryDirectory() as directory:
            current, ledger, _ = self.reviewed(directory, fixed_hash=True)
            path = Path(directory) / "report.txt"
            original = path.read_bytes()
            path.write_bytes(b"\xff broken")
            ledger = self.capture(current, 30, ledger)["observer_updates"]
            older_invalid = copy.deepcopy(ledger["artifact_observation"]["payload"])
            self.assertFalse(HELPER.captured_artifacts_ready(current, ledger))
            path.write_bytes(original)
            verified = self.verify(current)
            fresh = event(current, "artifact_receipt", receipt=verified, observed_at="2026-01-01T00:00:40+00:00",
                          execution_scope="review_only", followup_mode="durable")
            current = apply(current, HELPER.decide(current, fresh, ledger))
            self.assertTrue(HELPER.captured_artifacts_ready(current, ledger))
            self.assertNotEqual(self.final_delivery(current, ledger)["action"], "obtain_required_artifacts")
            late_delivery = HELPER.decide(current, older_invalid, ledger)
            self.assertEqual(late_delivery["action"], "keep_quiet")
            self.assertTrue(late_delivery["observer_updates"]["required_artifacts_ready"])
            self.assertFalse(late_delivery["observe_webpage"])
            path.write_bytes(b"\xff broken again")
            ledger = self.capture(current, 50, ledger)["observer_updates"]
            self.assertFalse(HELPER.captured_artifacts_ready(current, ledger))
            self.assertEqual(self.final_delivery(current, ledger)["action"], "obtain_required_artifacts")

    def test_original_progress_cannot_be_rebound_to_a_changed_scope_or_mode(self):
        original = state("submitting")
        original = apply(original, HELPER.decide(original, submission(original)))
        progress = HELPER.decide(original, scheduled(original, 1, generation="generating", actionable_progress=True,
                                actionable_progress_ref="ui/current-progress.json"))
        payload = copy.deepcopy(progress["controller_event"])
        for axis in ("scope", "mode"):
            with self.subTest(axis=axis):
                changed = copy.deepcopy(original)
                if axis == "scope":
                    changed["execution_scope"] = "review_only"
                else:
                    changed = inline(changed)
                with self.assertRaisesRegex(ValueError, "scope|mode|business"):
                    HELPER.decide(changed, payload, progress["observer_updates"])
        same = {**original, "execution_scope": "repair_loop", "followup_mode": "durable"}
        accepted = HELPER.decide(same, payload, progress["observer_updates"])
        self.assertEqual(accepted["action"], "assess_web_progress")
        self.assertEqual(payload, progress["controller_event"])

    def test_conflicting_same_time_proofs_wait_for_actual_fresh_verification(self):
        with tempfile.TemporaryDirectory() as directory:
            current, ledger, _ = self.reviewed(directory)
            receipt_a = self.verify(current)
            same_time_a = event(current, "artifact_receipt", receipt=receipt_a,
                                observed_at="2026-01-01T00:00:30+00:00", execution_scope="review_only")
            current = apply(current, HELPER.decide(current, same_time_a, ledger))
            (Path(directory) / "report.txt").write_text("actual valid report B", encoding="utf-8")
            newer = self.capture(current, 30, ledger)
            ledger = newer["observer_updates"]
            self.assertFalse(ledger["required_artifacts_ready"])
            self.assertFalse(HELPER.captured_artifacts_ready(current, ledger))
            self.assertFalse(self.final_delivery(current, ledger)["terminal"])
            incoming = newer["controller_event"]
            reconcile = HELPER.decide(current, incoming, ledger)
            self.assertEqual(reconcile["action"], "reconcile_artifact_verification")
            self.assertEqual(apply(current, reconcile)["artifact_receipt"], receipt_a)
            self.assertFalse(reconcile["state_updates"]["received_notifications"][newer["notification_key"]]["applied"])
            fresh = event(current, "artifact_receipt", observed_at="2026-01-01T00:00:31+00:00",
                          execution_scope="review_only", receipt=self.verify(current))
            current = apply(current, HELPER.decide(current, fresh, ledger))
            self.assertTrue(HELPER.current_artifacts_applied(current, ledger))
            stale = HELPER.decide(current, same_time_a, ledger)
            self.assertEqual(stale["action"], "ignore_stale_artifact_receipt")
            self.assertEqual(apply(current, stale)["artifact_receipt"], fresh["receipt"])

    def test_legacy_undated_current_proof_is_not_given_an_invented_order(self):
        with tempfile.TemporaryDirectory() as directory:
            current, ledger, _ = self.reviewed(directory)
            old = current["artifact_observation"]["payload"]
            old.pop("observed_at")
            current["artifact_observation"]["sha256"] = HELPER.notification_digest(old)
            (Path(directory) / "report.txt").write_text("actual valid report B", encoding="utf-8")
            newer = self.capture(current, 30, ledger)
            ledger = newer["observer_updates"]
            self.assertFalse(HELPER.captured_artifacts_ready(current, ledger))
            self.assertFalse(self.final_delivery(current, ledger)["terminal"])
            fresh = event(current, "artifact_receipt", receipt=self.verify(current),
                          observed_at="2026-01-01T00:00:40+00:00", execution_scope="review_only")
            current = apply(current, HELPER.decide(current, fresh, ledger))
            self.assertTrue(HELPER.current_artifacts_applied(current, ledger))
            self.assertEqual(current["artifact_observation"]["payload"]["observed_at"], fresh["observed_at"])

    def test_legacy_undated_direct_replay_preserves_newer_applied_real_file(self):
        with tempfile.TemporaryDirectory() as directory:
            current, ledger, _ = self.reviewed(directory, mode="inline")
            legacy = event(current, "artifact_receipt", receipt=self.verify(current))
            (Path(directory) / "report.txt").write_text("actual valid report B", encoding="utf-8")
            fresh = event(current, "artifact_receipt", receipt=self.verify(current),
                          observed_at="2026-01-01T00:00:40+00:00", execution_scope="review_only")
            current = apply(current, HELPER.decide(current, fresh, ledger))
            proof = copy.deepcopy(current["artifact_observation"])
            replay = HELPER.decide(current, legacy, ledger)
            current = apply(current, replay)
            self.assertEqual(current["artifact_receipt"], fresh["receipt"])
            self.assertEqual(current["artifact_observation"], proof)
            self.assertTrue(HELPER.current_artifacts_applied(current, ledger))
            self.assertTrue(self.final_delivery(current, ledger)["terminal"])
            same_snapshot = event(current, "artifact_receipt", receipt=self.verify(current))
            current = apply(current, HELPER.decide(current, same_snapshot, ledger))
            self.assertEqual(current["artifact_observation"], proof)

    def test_direct_same_time_conflict_persists_until_fresh_real_verification(self):
        with tempfile.TemporaryDirectory() as directory:
            current, ledger, _ = self.reviewed(directory, mode="inline")
            original = event(current, "artifact_receipt", receipt=self.verify(current),
                             observed_at="2026-01-01T00:00:40+00:00", execution_scope="review_only")
            current = apply(current, HELPER.decide(current, original, ledger))
            (Path(directory) / "report.txt").write_text("actual valid report B", encoding="utf-8")
            conflicting = event(current, "artifact_receipt", receipt=self.verify(current),
                                observed_at="2026-01-01T00:00:40+00:00", execution_scope="review_only")
            raw = copy.deepcopy(conflicting)
            answer = HELPER.decide(current, conflicting, ledger)
            self.assertEqual(answer["action"], "reconcile_artifact_verification")
            current = apply(current, answer)
            self.assertEqual(current["artifact_receipt"], original["receipt"])
            self.assertFalse(HELPER.current_artifacts_applied(current, ledger))
            self.assertFalse(self.final_delivery(current, ledger)["terminal"])
            replay = HELPER.decide(current, conflicting, ledger)
            current = apply(current, replay)
            self.assertEqual(replay["action"], "reconcile_artifact_verification")
            self.assertFalse(self.final_delivery(current, ledger)["terminal"])
            fresh = event(current, "artifact_receipt", receipt=self.verify(current),
                          observed_at="2026-01-01T00:00:41+00:00", execution_scope="review_only")
            current = apply(current, HELPER.decide(current, fresh, ledger))
            self.assertTrue(HELPER.current_artifacts_applied(current, ledger))
            self.assertTrue(self.final_delivery(current, ledger)["terminal"])
            self.assertEqual(current["artifact_receipt"], self.verify(current))
            self.assertEqual(conflicting, raw)


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
        current.update(phase="blocked", resume_phase="waiting_web", blocker_reason_code="space_missing")
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


class FollowupBoundaryTests(unittest.TestCase):
    def attachment_stages(self):
        current = authorized(with_required(state()))
        full = collected(current)
        current = apply(current, HELPER.decide(current, full["controller_event"], full["observer_updates"]))
        repairing = apply(current, HELPER.decide(current, event(current, "assessment", review_message_id="message-1",
                          coverage_complete=True, confirmed_findings=2, unresolved_claims=0, file_dependent_findings=1)))
        validating = apply(repairing, HELPER.decide(repairing, event(repairing, "worker_result",
                           candidate_source_id=A, delivery_path="worker/current.json")))
        return (current, repairing, validating), full["observer_updates"]

    def test_attachment_faults_use_common_classifier_and_controller_can_consume_the_original_event(self):
        stages, saved = self.attachment_stages()
        for current in stages:
            for code in ("space_missing", "space_closed", "browser_crash", "connection_failed",
                         "auth", "user_control", "permission_denied", "quota", "provider"):
                with self.subTest(phase=current["phase"], code=code):
                    observed = HELPER.decide(current, scheduled(current, 20, ui_error=code,
                                            error_fingerprint="same-incident-" + code), saved)
                    self.assertFalse(observed["activate_developer"])
                    self.assertNotEqual(observed["action"], "capture_required_artifacts")
                    if code in HELPER.BROWSER_FAULTS:
                        self.assertEqual(observed["action"], "recover_browser_context")
                        self.assertFalse(observed["activate_controller"])
                    else:
                        self.assertEqual(observed["action"], "notify_controller")
                        payload = copy.deepcopy(observed["controller_event"])
                        consumed = HELPER.decide(current, payload, observed["observer_updates"])
                        self.assertEqual(consumed["action"], "request_browser_input")
                        self.assertEqual(consumed["phase"], current["phase"])
                        applied = apply(current, consumed)
                        self.assertEqual(applied["last_completion"], current["last_completion"])
                        self.assertEqual(applied["raw_reply_path"], current["raw_reply_path"])
                        self.assertIn(observed["notification_key"], applied["received_notifications"])
                        self.assertEqual(payload, observed["controller_event"])
                        repeated = HELPER.decide(applied, scheduled(applied, 30, ui_error=code,
                                                 error_fingerprint="same-incident-" + code), observed["observer_updates"])
                        self.assertEqual(repeated["action"], "keep_quiet")
                        self.assertFalse(repeated["activate_controller"])

    def test_attachment_transient_budget_is_bounded_and_normal_capture_preserves_collected_text(self):
        stages, saved = self.attachment_stages()
        for current in stages:
            with self.subTest(phase=current["phase"]):
                ledger = copy.deepcopy(saved)
                for seconds in (20, 50, 110, 230, 400):
                    observed = HELPER.decide(current, scheduled(current, seconds, ui_error="transient",
                                            error_fingerprint="same-busy"), ledger)
                    ledger = observed["observer_updates"]
                    self.assertFalse(observed["activate_controller"])
                    self.assertEqual(observed["phase"], current["phase"])
                self.assertEqual(ledger["refresh_count"], 3)
                self.assertEqual(ledger["last_completion"], saved["last_completion"])
                normal = HELPER.decide(current, scheduled(current, 410), ledger)
                self.assertEqual(normal["action"], "capture_required_artifacts")
                self.assertTrue(normal["observe_webpage"])
                self.assertEqual(normal["observer_updates"]["refresh_count"], 0)
                self.assertEqual(normal["observer_updates"]["last_completion"], saved["last_completion"])

    def test_receipt_only_then_pause_then_original_processing_never_rearms_or_moves_processing_to_luna(self):
        current = authorized(state())
        full = collected(current)
        payload = copy.deepcopy(full["controller_event"])
        read = event(current, "controller_received", notification_key=full["notification_key"],
                     notification_receipt_sha256=payload["notification_receipt_sha256"])
        received = HELPER.decide(current, read, full["observer_updates"])
        self.assertEqual(received["action"], "process_saved_result")
        self.assertEqual(received["controller_event"], payload)
        current = apply(current, received)
        self.assertEqual(current["phase"], "waiting_web")
        checked = HELPER.decide(current, notification_check(current), full["observer_updates"])
        self.assertEqual(checked["action"], "pause_followup")
        self.assertFalse(checked["activate_controller"])
        self.assertFalse(checked["observe_webpage"])
        closed = HELPER.decide(current, closed_followup(current), checked["observer_updates"])
        self.assertEqual(closed["action"], "process_saved_result")
        self.assertEqual(closed["schedule_action"], "pause_if_active")
        self.assertEqual(closed["controller_event"], payload)
        current = apply(current, closed)
        processed = HELPER.decide(current, closed["controller_event"], checked["observer_updates"])
        self.assertEqual(processed["action"], "triage_review")
        self.assertEqual(processed["phase"], "review_ready")
        self.assertEqual(processed["schedule_action"], "pause_if_active")
        self.assertEqual(current["followup"]["status"], "PAUSED")
        self.assertEqual(full["controller_event"], payload)

    def test_received_saved_artifact_is_processed_locally_after_reply_without_overriding_triage(self):
        current = authorized(with_required(state()))
        full = collected(current)
        captured = HELPER.decide(current, event(current, "scheduled_artifacts", observed_at="2026-01-01T00:00:11+00:00",
                               followup_view=followup(current, checked_seconds=11), receipt=receipt(current)), full["observer_updates"])
        ledger = captured["observer_updates"]
        for item in ledger["notifications"]:
            current = apply(current, HELPER.decide(current, event(current, "controller_received", notification_key=item["key"],
                            notification_receipt_sha256=item["receipt_sha256"]), ledger))
        closed = HELPER.decide(current, closed_followup(current), ledger)
        current = apply(current, closed)
        triaged = HELPER.decide(current, closed["controller_event"], ledger)
        self.assertEqual(triaged["action"], "triage_review")
        current = apply(current, triaged)
        saved = HELPER.decide(current, event(current, "followup_readback", followup=current["followup"]), ledger)
        self.assertEqual(saved["action"], "process_saved_result")
        self.assertEqual(saved["controller_event"], captured["controller_event"])
        applied = HELPER.decide(current, saved["controller_event"], ledger)
        self.assertNotEqual(applied["action"], "process_saved_result")
        self.assertTrue(HELPER.artifact_ready(apply(current, applied)))
        self.assertEqual(applied["schedule_action"], "pause_if_active")

    def test_processed_browser_error_before_complete_reply_does_not_reenter_the_input_gate(self):
        for code in ("quota", "auth", "user_control", "permission_denied", "provider"):
            with self.subTest(code=code):
                current = authorized(state())
                old = HELPER.decide(current, scheduled(current, ui_error=code,
                                   error_fingerprint="old-" + code))
                old_payload = copy.deepcopy(old["controller_event"])
                handled = HELPER.decide(current, old_payload, old["observer_updates"])
                self.assertEqual(handled["action"], "request_browser_input")
                current = apply(current, handled)
                first = HELPER.decide(current, scheduled(current, 10), old["observer_updates"])
                full = HELPER.decide(current, scheduled(current, 20), first["observer_updates"])
                payload = copy.deepcopy(full["controller_event"])
                ledger = full["observer_updates"]
                self.assertEqual(ledger["notifications"][0]["status"], "received")
                self.assertEqual(ledger["notifications"][0]["controller_event"], old_payload)
                read = event(current, "controller_received", notification_key=full["notification_key"],
                             notification_receipt_sha256=payload["notification_receipt_sha256"])
                received = HELPER.decide(current, read, ledger)
                self.assertEqual(received["action"], "process_saved_result")
                self.assertEqual(received["controller_event"], payload)
                current = apply(current, received)
                checked = HELPER.decide(current, notification_check(current, 20), ledger)
                self.assertEqual(checked["action"], "pause_followup")
                self.assertFalse(checked["observe_webpage"])
                closed = HELPER.decide(current, closed_followup(current), checked["observer_updates"])
                self.assertEqual(closed["controller_event"], payload)
                current = apply(current, closed)
                processed = HELPER.decide(current, closed["controller_event"], checked["observer_updates"])
                self.assertEqual(processed["action"], "triage_review")
                self.assertEqual(processed["phase"], "review_ready")
                self.assertEqual(processed["schedule_action"], "pause_if_active")
                self.assertEqual(payload, full["controller_event"])
                self.assertEqual(old_payload, checked["observer_updates"]["notifications"][0]["controller_event"])
                self.assertEqual(old_payload["notification_receipt_sha256"],
                                 current["received_notifications"][old["notification_key"]]["receipt_sha256"])

    def test_recovery_budget_follows_both_entry_directions_and_only_success_resets_it(self):
        current = state("submitting")
        current = apply(current, HELPER.decide(current, submission(current)))
        first = HELPER.decide(current, scheduled(current, 1, ui_error="space_missing", error_fingerprint="same-fault"))
        second = HELPER.decide(current, scheduled(current, 2, ui_error="space_missing", error_fingerprint="same-fault"), first["observer_updates"])
        exhausted = HELPER.decide(current, event(current, "browser_fault", reason_code="space_missing"), second["observer_updates"])
        self.assertEqual(exhausted["action"], "diagnose_browser_recovery")
        self.assertEqual(exhausted["state_updates"]["browser_recovery_attempts"], 2)
        current = apply(current, exhausted)
        current["web_io_binding"] = {**current["web_io_binding"], "thread_id": "other-luna", "verified_at": "2026-01-01T00:00:03+00:00"}
        current["followup"] = followup(current, checked_seconds=3, evidence_ref="other-owner-view")
        later = HELPER.decide(current, scheduled(current, 4, ui_error="browser_crash", error_fingerprint="same-fault"), second["observer_updates"])
        self.assertEqual(later["action"], "diagnose_browser_recovery")
        current = apply(current, HELPER.decide(current, recovery(current, 5), later["observer_updates"]))
        next_incident = HELPER.decide(current, event(current, "browser_fault", reason_code="browser_crash"), later["observer_updates"])
        self.assertEqual(next_incident["state_updates"]["browser_recovery_attempts"], 1)
        current = apply(current, next_incident)
        observed = HELPER.decide(current, scheduled(current, 6, ui_error="browser_crash", error_fingerprint="second-incident"))
        self.assertEqual(observed["observer_updates"]["browser_recovery_attempts"], 2)
        stopped = HELPER.decide(current, event(current, "browser_fault", reason_code="browser_crash"), observed["observer_updates"])
        self.assertEqual(stopped["action"], "diagnose_browser_recovery")

    def test_legacy_default_binding_preserves_original_key_payload_sha_status_and_refresh_budget(self):
        current = authorized(state())
        full = collected(current)
        ledger = copy.deepcopy(full["observer_updates"])
        # Exact former business shape: absent defaults were stored as null.
        ledger["binding"].update(execution_scope=None, followup_mode=None)
        old_key = HELPER.notification_key(ledger["binding"], {"kind": "reply", "message": "message-1", "sha256": "c" * 64})
        payload = {**ledger["notifications"][0]["controller_event"], "notification_key": old_key}
        sha = HELPER.notification_digest(payload)
        payload["notification_receipt_sha256"] = sha
        ledger["notifications"][0].update(key=old_key, controller_event=payload, receipt_sha256=sha)
        for status in ("pending", "unknown", "not_delivered", "active_writer", "delivered"):
            with self.subTest(status=status):
                saved = copy.deepcopy(ledger)
                saved["notifications"][0]["status"] = status
                explicit = {**current, "execution_scope": "repair_loop", "followup_mode": "durable"}
                checked = HELPER.decide(explicit, notification_check(explicit), saved)
                self.assertEqual(checked["observer_updates"]["notifications"], saved["notifications"])
                self.assertFalse(checked["observe_webpage"])
                self.assertEqual(checked["action"], "check_controller_receipt")
        first = HELPER.decide(current, scheduled(current, ui_error="transient", error_fingerprint="same-busy"))
        busy = HELPER.decide(current, scheduled(current, 30, ui_error="transient", error_fingerprint="same-busy"), first["observer_updates"])
        old = copy.deepcopy(busy["observer_updates"])
        old["binding"].update(execution_scope=None, followup_mode=None)
        explicit = {**current, "execution_scope": "repair_loop", "followup_mode": "durable"}
        kept = HELPER.decide(explicit, scheduled(explicit, 40, ui_error="transient", error_fingerprint="same-busy"), old)
        self.assertEqual(kept["observer_updates"]["refresh_count"], 1)
        self.assertEqual(kept["observer_updates"]["next_refresh_at"], old["next_refresh_at"])
        for changed in ({**explicit, "execution_scope": "review_only"}, inline(copy.deepcopy(explicit))):
            item = notification_check(changed)
            if changed.get("followup_mode") == "inline":
                item = inline_event(item)
            fresh = HELPER.decide(changed, item, ledger)
            self.assertEqual(fresh["observer_updates"]["notifications"], [])

    def test_browser_restore_preserves_unrelated_or_unknown_blocker_until_its_own_resolution(self):
        for code in ("material_host_offline", "source_unpublished", None):
            with self.subTest(blocker=code):
                current = state("submitting")
                current = apply(current, HELPER.decide(current, submission(current)))
                block = event(current, "external_blocker", reason_code=code, reason="Required business condition is unavailable",
                              attempts=["business/condition-check.json"], requires_external_change="business condition returns",
                              independent_work_remaining=False)
                current = apply(current, HELPER.decide(current, block))
                fault = HELPER.decide(current, event(current, "browser_fault", reason_code="space_missing"))
                self.assertEqual(fault["action"], "recover_browser_context")
                self.assertEqual(fault["phase"], "blocked")
                current = apply(current, fault)
                restored = HELPER.decide(current, recovery(current, 20))
                self.assertEqual(restored["action"], "continue_independent_work")
                self.assertEqual(restored["phase"], "blocked")
                self.assertEqual(restored["state_updates"]["blocker_reason_code"], code)
                current = apply(current, restored)
                resumed = HELPER.decide(current, event(current, "resume", resolution_ref="business/actual-resolution.json",
                                      observed_at="2026-01-01T00:00:21+00:00",
                                      followup_view=followup(current, checked_seconds=21, evidence_ref="after-business-resolution")))
                self.assertEqual(resumed["action"], "resume_saved_step")
                self.assertEqual(resumed["phase"], "waiting_web")

    def test_completed_capture_does_not_reopen_webpage_to_classify_an_old_browser_fault(self):
        current = authorized(state())
        full = collected(current)
        old_fault = HELPER.decide(current, scheduled(current, 20, ui_error="space_missing",
                                 error_fingerprint="old-space-error"), full["observer_updates"])
        self.assertEqual(old_fault["action"], "check_controller_receipt")
        self.assertFalse(old_fault["observe_webpage"])
        self.assertEqual(old_fault["observer_updates"]["browser_recovery_attempts"], 0)


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
