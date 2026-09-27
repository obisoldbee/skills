"""Behavioral regressions for version binding, recovery and repeated repair."""

import copy
from datetime import datetime, timedelta, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest


ROOT = Path(__file__).resolve().parents[1]
SPEC = importlib.util.spec_from_file_location("next_action", ROOT / "scripts/next_action.py")
HELPER = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(HELPER)
A = "git:" + "a" * 40
B = "git:" + "b" * 40
CONTRACT = {"required": [], "optional": []}
DIGEST = hashlib.sha256(json.dumps(CONTRACT, sort_keys=True, ensure_ascii=False,
                                   separators=(",", ":")).encode()).hexdigest()
ACCEPTANCE = {"required_checks": ["local tests"], "delivery_items": ["review report"]}
ACCEPTANCE_DIGEST = hashlib.sha256(json.dumps(ACCEPTANCE, sort_keys=True, ensure_ascii=False,
                                              separators=(",", ":")).encode()).hexdigest()
SOURCE_BINDING = {"repository": "owner/project", "commit": "a" * 40}
SOURCE_BINDING_DIGEST = hashlib.sha256(json.dumps(SOURCE_BINDING, sort_keys=True,
                                                  ensure_ascii=False, separators=(",", ":")).encode()).hexdigest()


def state(phase="waiting_web"):
    current = {"schema_version": 2, "run_id": "test-run", "round": 1, "phase": phase,
            "controller_thread_id": "controller-thread", "controller_host": "controller-host",
            "state_path": str(Path(tempfile.gettempdir()) / "review-run" / "state.json"),
            "source_route": "github", "source_id": A, "request_token": "test-round-1",
            "source_binding": SOURCE_BINDING, "source_binding_digest": SOURCE_BINDING_DIGEST,
            "used_request_tokens": ["test-round-1"], "consumer_host": "test-host",
            "artifact_root": str(Path(tempfile.gettempdir()) / "review-artifacts"),
            "artifact_contract": CONTRACT, "contract_digest": DIGEST,
            "acceptance_contract": ACCEPTANCE, "acceptance_digest": ACCEPTANCE_DIGEST,
            "conversation_url": "https://chatgpt.com/c/test-conversation"}
    current["followup"] = followup(current)
    current["prepared_request"] = {
        **{k: current[k] for k in ("run_id", "round", "source_id", "source_binding_digest",
                                    "contract_digest", "acceptance_digest", "consumer_host", "request_token")},
        "path": "round-1/review-request.md", "sha256": "e" * 64, "evidence": ["round-1/request.json"]}
    return current


def followup(current, *, checked_seconds=-1, status="ACTIVE", evidence_ref="view-initial"):
    moment = datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=checked_seconds)
    return {"tool": "automation_update/view", "kind": "heartbeat",
            "automation_id": "heartbeat-1", "status": status,
            "owner_thread_id": current["controller_thread_id"],
            "owner_host": current["controller_host"], "run_id": current["run_id"],
            "state_path": current["state_path"], "prompt_binding_verified": True,
            "cadence_minutes": 5, "checked_at": moment.isoformat(),
            "next_check_at": (moment + timedelta(minutes=5)).isoformat() if status == "ACTIVE" else None,
            "evidence_ref": evidence_ref}


def event(current, kind, **fields):
    identity = {k: current[k] for k in ("run_id", "round", "source_id", "source_binding_digest",
                                        "request_token",
                                        "contract_digest", "acceptance_digest", "consumer_host", "artifact_root")}
    return {**identity, "type": kind, "evidence": ["evidence/observed.json"], **fields}


def observation(current, seconds=0, **fields):
    moment = datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=seconds)
    return event(current, "observation", **{
        "conversation_url": current["conversation_url"], "observed_at": moment.isoformat(),
        "ui_error": "none", "generation": "idle", "request_present": True,
        "after_request": True, "assistant_message_id": "message-1", "completion_controls": True,
        "request_user_message_id": current.get("submitted_user_message_id"),
        "body_chars": 200, "body_sha256": "c" * 64, "raw_reply_path": "round-1/reply.md",
        "full_body_saved": True, **fields,
    })


def apply(current, report):
    return {**current, **report["state_updates"]}


def submission(current):
    return event(current, "submission", status="sent", request_present=True,
                 conversation_url=current["conversation_url"], user_message_id="user-message",
                 ui_model_verified=True, prompt_sha256="e" * 64,
                 observed_at=datetime(2026, 1, 1, tzinfo=timezone.utc).isoformat(),
                 followup_view=followup(current, checked_seconds=0,
                                         evidence_ref=f"view-send-{current['round']}"))


def preparation(current):
    return event(current, "prepare_submission", review_request_path=f"round-{current['round']}/review-request.md",
                 prompt_sha256="e" * 64, requirements_ref="source/requirements.md",
                 source_readback_ref="source/readback.json", checks_ref="checks/current.json",
                 dispositions_ref="review/dispositions.json", materials_verified=True,
                 observed_at=datetime(2026, 1, 1, tzinfo=timezone.utc).isoformat())


def closed_followup(current):
    return event(current, "followup_closed",
                 followup=followup(current, checked_seconds=20, status="PAUSED",
                                   evidence_ref="view-closed"))


def with_required(current):
    contract = {"required": [{"name": "report", "kind": "zip"}],
                "optional": [{"name": "preview", "kind": "png"}]}
    current["artifact_contract"] = contract
    current["contract_digest"] = HELPER.contract_digest(contract)
    return current


def receipt(current, *, host=None, required="verified", optional="missing"):
    binding = {k: current[k] for k in ("run_id", "round", "source_id", "request_token",
                                        "consumer_host", "artifact_root")}
    if host:
        binding["consumer_host"] = host
    return {"validator": "verify_artifacts/v2", "binding": binding,
            "contract_digest": current["contract_digest"], "required_ready": required == "verified",
            "files": {"report": {"status": required}, "preview": {"status": optional}}}


def ready_review():
    current = state()
    current = apply(current, HELPER.decide(current, observation(current)))
    return apply(current, HELPER.decide(current, observation(current, 10)))


class ReviewCycleTests(unittest.TestCase):
    def test_prepare_from_existing_code_without_chat_then_send_to_new_conversation(self):
        current = state("ready_to_submit")
        current["conversation_url"] = None
        current["prepared_request"] = None
        current["followup"] = None
        report = HELPER.decide(current, preparation(current))
        self.assertEqual(report["action"], "ensure_followup")
        current = apply(current, report)
        self.assertTrue(HELPER.prepared_request(current))
        receipt = followup(current, evidence_ref="view-created")
        current = apply(current, HELPER.decide(current, event(current, "followup_readback",
                                                             followup=receipt)))
        absent = event(current, "submission", status="not_sent", definitive_absence=True,
                       conversation_url=None, observed_at=datetime(2026, 1, 1, tzinfo=timezone.utc).isoformat(),
                       followup_view=followup(current, checked_seconds=0, evidence_ref="view-before-send"))
        report = HELPER.decide(current, absent)
        self.assertEqual(report["action"], "submit_once")
        current = apply(current, report)
        sent = event(current, "submission", status="sent", request_present=True,
                     conversation_url="https://chatgpt.com/c/new-real-id", user_message_id="new-user-1",
                     ui_model_verified=True, prompt_sha256="e" * 64,
                     observed_at=(datetime(2026, 1, 1, tzinfo=timezone.utc) + timedelta(seconds=1)).isoformat(),
                     followup_view=followup(current, checked_seconds=0, evidence_ref="view-before-send"))
        report = HELPER.decide(current, sent)
        self.assertEqual(report["action"], "watch")
        self.assertEqual(report["state_updates"]["conversation_url"], sent["conversation_url"])
        self.assertEqual(report["state_updates"]["submitted_user_message_id"], "new-user-1")

    def test_explicit_materials_only_prepares_without_scheduling_or_sending(self):
        current = state("ready_to_submit")
        current["followup"] = None
        current["prepared_request"] = None
        report = HELPER.decide(current, preparation(current) | {"materials_only": True})
        self.assertEqual(report["action"], "deliver_prepared_request")
        self.assertTrue(HELPER.prepared_request(apply(current, report)))
        self.assertNotIn("followup", report["state_updates"])

    def test_adopt_existing_request_without_web_token_never_resends(self):
        current = state("ready_to_submit")
        current["prepared_request"] = None
        current["request_token"] = "local-import-1"
        current["used_request_tokens"] = ["local-import-1"]
        current["followup"] = None
        adopted = event(current, "adopt_submission", status="verified",
                        conversation_url=current["conversation_url"], user_message_id="old-user-42",
                        prompt_sha256="f" * 64, raw_user_message_path="round-1/original-user.md",
                        source_readback_id=A, source_binding_digest_observed=current["source_binding_digest"],
                        source_readback_ref="ui/source-readback.json",
                        web_token_present=False, web_request_token=None,
                        local_import_id="local-import-1", local_import_id_present_in_web=False,
                        observed_at=datetime(2026, 1, 1, tzinfo=timezone.utc).isoformat())
        report = HELPER.decide(current, adopted)
        self.assertEqual(report["action"], "ensure_followup")
        self.assertEqual(report["phase"], "waiting_web")
        current = apply(current, report)
        self.assertTrue(current["adopted_without_web_token"])
        with self.assertRaisesRegex(ValueError, "submitted user message"):
            HELPER.decide(current, observation(current, request_user_message_id="different-user"))
        report = HELPER.decide(current, observation(current))
        self.assertEqual(report["action"], "ensure_followup")
        self.assertNotEqual(report["action"], "submit_once")
        bad = dict(adopted, source_readback_id=B)
        self.assertEqual(HELPER.decide(state("ready_to_submit"),
                                       {**bad, **{k: state()[k] for k in
                                                ("request_token", "source_id")}})["action"],
                         "reconcile_submission")

    def test_followup_gate_rejects_missing_paused_wrong_host_and_stale_view(self):
        current = state("ready_to_submit")
        absent = event(current, "submission", status="not_sent", definitive_absence=True,
                       conversation_url=current["conversation_url"],
                       observed_at=datetime(2026, 1, 1, tzinfo=timezone.utc).isoformat())
        for label, saved, view in (
            ("missing", None, None),
            ("paused", followup(current, status="PAUSED"),
             followup(current, checked_seconds=0, evidence_ref="view-paused")),
            ("wrong-host", current["followup"],
             {**followup(current, checked_seconds=0, evidence_ref="view-wrong-host"),
              "owner_host": "different-host"}),
            ("stale", current["followup"],
             followup(current, checked_seconds=-700, evidence_ref="view-stale")),
        ):
            with self.subTest(label=label):
                candidate = {**current, "followup": saved}
                report = HELPER.decide(candidate, {**absent, "followup_view": view})
                self.assertEqual(report["action"], "ensure_followup")
        good = {**absent, "followup_view": followup(current, checked_seconds=0,
                                                     evidence_ref="view-fresh")}
        self.assertEqual(HELPER.decide(current, good)["action"], "submit_once")

    def test_deleted_followup_can_be_replaced_only_with_old_id_evidence(self):
        current = state("ready_to_submit")
        replacement = {**followup(current, checked_seconds=1, evidence_ref="view-new-active"),
                       "automation_id": "heartbeat-replacement"}
        item = event(current, "followup_readback", followup=replacement)
        self.assertEqual(HELPER.decide(current, item)["action"], "ensure_followup")
        item.update(replacement_of_automation_id="heartbeat-1",
                    prior_automation_status="not_found",
                    prior_automation_evidence_ref="view-old-not-found")
        report = HELPER.decide(current, item)
        self.assertEqual(report["action"], "record_followup")
        self.assertEqual(report["state_updates"]["followup_replacement"]["new_automation_id"],
                         "heartbeat-replacement")
        self.assertEqual(apply(current, report)["followup"]["automation_id"], "heartbeat-replacement")

    def test_paused_readback_has_no_next_check_and_closes_user_pause(self):
        current = state("waiting_web")
        current = apply(current, HELPER.decide(current, event(current, "pause",
                        reason="user_stop", user_instruction_ref="user turn")))
        self.assertEqual(current["phase"], "paused")
        closed = followup(current, status="PAUSED", evidence_ref="view-paused")
        self.assertIsNone(closed["next_check_at"])
        report = HELPER.decide(current, event(current, "followup_closed", followup=closed))
        self.assertEqual(report["action"], "pause")
        self.assertEqual(report["state_updates"]["followup"]["status"], "PAUSED")

    def test_sent_without_followup_preserves_message_and_requires_schedule(self):
        current = state("ready_to_submit")
        current["followup"] = None
        report = HELPER.decide(current, submission(current))
        self.assertEqual(report["action"], "ensure_followup")
        self.assertEqual(report["phase"], "waiting_web")
        self.assertEqual(report["state_updates"]["submitted_user_message_id"], "user-message")

    def test_old_v2_state_can_bind_controller_without_losing_reply(self):
        current = state()
        for key in ("controller_thread_id", "controller_host", "state_path"):
            current.pop(key)
        report = HELPER.decide(current, observation(current))
        self.assertEqual(report["action"], "ensure_followup")
        current = apply(current, report)
        report = HELPER.decide(current, observation(current, 10))
        self.assertEqual(report["action"], "triage_review")
        binding = event(current, "bind_controller", controller_thread_id="observed-thread",
                        controller_host="observed-host", state_path=str(Path(tempfile.gettempdir()) / "actual-run" / "state.json"))
        report = HELPER.decide(current, binding)
        self.assertEqual(report["action"], "ensure_followup")
        self.assertEqual(report["state_updates"]["controller_thread_id"], "observed-thread")

    def test_ensure_followup_does_not_consume_refresh_budget(self):
        current = state()
        current["followup"] = None
        current["refresh_count"] = 0
        current["next_refresh_at"] = datetime(2026, 1, 1, tzinfo=timezone.utc).isoformat()
        report = HELPER.decide(current, observation(current, 30, ui_error="transient"))
        self.assertEqual(report["action"], "ensure_followup")
        self.assertNotIn("refresh_count", report["state_updates"])

    def test_no_automation_creation_required_for_already_complete_old_work(self):
        current = ready_review()
        current["followup"] = None
        current = apply(current, HELPER.decide(current, event(current, "assessment",
                        review_message_id="message-1", coverage_complete=True,
                        confirmed_findings=0, unresolved_claims=0)))
        current = apply(current, HELPER.decide(current, event(current, "validation",
                        checked_source_id=A, passed=True, required_unverified=[])))
        report = HELPER.decide(current, event(current, "delivery", delivered_source_id=A, complete=True))
        self.assertEqual(report["action"], "complete")
        self.assertTrue(report["terminal"])

    def test_v1_needs_explicit_upgrade_and_reverification(self):
        current = state()
        current["schema_version"] = 1
        with self.assertRaisesRegex(ValueError, "migrate v1"):
            HELPER.decide(current, observation(current))

    def test_third_round_cannot_reuse_first_token(self):
        current = ready_review()
        current["round"] = 2
        current["request_token"] = "test-round-2"
        current["used_request_tokens"] = ["test-round-1", "test-round-2"]
        with self.assertRaisesRegex(ValueError, "never-used"):
            HELPER.decide(current, event(current, "assessment", review_message_id="message-1",
                                         coverage_complete=False, next_request_token="test-round-1"))

    def test_changed_reply_rejects_backward_time(self):
        current = state()
        current = apply(current, HELPER.decide(current, observation(current, 20)))
        with self.assertRaisesRegex(ValueError, "backwards"):
            HELPER.decide(current, observation(current, 10, body_sha256="d" * 64))

    def test_required_file_blocks_dependent_repair_but_optional_does_not(self):
        current = with_required(ready_review())
        assessed = event(current, "assessment", review_message_id="message-1", coverage_complete=True,
                         confirmed_findings=1, file_dependent_findings=1, unresolved_claims=0)
        report = HELPER.decide(current, assessed)
        self.assertEqual(report["action"], "obtain_required_artifacts")
        current = apply(current, report)
        bad = receipt(current, host="other-host")
        with self.assertRaises(ValueError):
            HELPER.decide(current, event(current, "artifact_receipt", receipt=bad))
        report = HELPER.decide(current, event(current, "artifact_receipt", receipt=receipt(current)))
        self.assertEqual(report["action"], "dispatch_repair")
        self.assertEqual(report["phase"], "repairing")

    def test_receipt_during_independent_repair_continues_same_developer(self):
        current = with_required(ready_review())
        report = HELPER.decide(current, event(current, "assessment", review_message_id="message-1",
                                             coverage_complete=True, confirmed_findings=2,
                                             file_dependent_findings=1, unresolved_claims=0))
        self.assertEqual(report["state_updates"]["dispatchable_findings"], 1)
        current = apply(current, report)
        self.assertEqual(current["pending_file_findings"], 1)
        report = HELPER.decide(current, event(current, "artifact_receipt", receipt=receipt(current)))
        self.assertEqual(report["action"], "continue_repair_with_files")
        self.assertEqual(report["phase"], "repairing")
        current = apply(current, report)
        report = HELPER.decide(current, event(current, "worker_result", candidate_source_id=B,
                                             delivery_path="worker/delivery.json", addressed_file_findings=1))
        self.assertEqual(report["state_updates"]["pending_file_findings"], 0)

    def test_partial_worker_result_preserves_missing_file_obligation(self):
        current = with_required(ready_review())
        current = apply(current, HELPER.decide(current, event(current, "assessment",
                        review_message_id="message-1", coverage_complete=True,
                        confirmed_findings=2, file_dependent_findings=1, unresolved_claims=0)))
        current = apply(current, HELPER.decide(current, event(current, "worker_result",
                        candidate_source_id=B, delivery_path="worker/partial.json")))
        report = HELPER.decide(current, event(current, "validation", checked_source_id=B,
                                             passed=True, required_unverified=[]))
        self.assertEqual(report["action"], "obtain_required_artifacts")
        self.assertEqual(report["phase"], "validating")
        current = apply(current, report)
        report = HELPER.decide(current, event(current, "artifact_receipt", receipt=receipt(current)))
        self.assertEqual(report["action"], "continue_repair_with_files")
        current = apply(current, report)
        report = HELPER.decide(current, event(current, "worker_result", candidate_source_id=B,
                                             delivery_path="worker/completed.json",
                                             addressed_file_findings=1))
        self.assertEqual(report["state_updates"]["pending_file_findings"], 0)

    def test_source_binding_change_invalidates_old_event_and_evidence(self):
        current = state()
        stale = observation(current)
        current["source_binding"] = {"repository": "other/project", "commit": "a" * 40}
        current["source_binding_digest"] = HELPER.source_binding_digest(
            "github", A, current["source_binding"])
        with self.assertRaisesRegex(ValueError, "source_binding_digest"):
            HELPER.decide(current, stale)
        current["review"] = {"run_id": current["run_id"], "source_id": A,
                             "source_binding_digest": SOURCE_BINDING_DIGEST,
                             "contract_digest": current["contract_digest"],
                             "acceptance_digest": current["acceptance_digest"],
                             "consumer_host": current["consumer_host"],
                             "round": 1, "request_token": current["request_token"],
                             "clean": True, "evidence": ["old-review.md"]}
        current["phase"] = "validating"
        report = HELPER.decide(current, event(current, "validation", checked_source_id=A,
                                             passed=True, required_unverified=[],
                                             next_request_token="test-round-2"))
        self.assertEqual(report["action"], "prepare_review_request")

    def test_optional_only_receipt_still_requires_current_binding(self):
        current = ready_review()
        current["artifact_contract"] = {"required": [], "optional": [{"name": "preview", "kind": "png"}]}
        current["contract_digest"] = HELPER.contract_digest(current["artifact_contract"])
        bad = {"validator": "verify_artifacts/v2",
               "binding": {k: current[k] for k in ("run_id", "round", "source_id",
                                                    "request_token", "consumer_host", "artifact_root")},
               "contract_digest": current["contract_digest"], "required_ready": True,
               "files": {"preview": {"status": "missing"}}}
        bad["binding"]["consumer_host"] = "other-host"
        with self.assertRaisesRegex(ValueError, "mismatched"):
            HELPER.decide(current, event(current, "artifact_receipt", receipt=bad))

    def test_mcp_binding_is_required_and_cannot_change_silently(self):
        current = state()
        current["source_route"] = "mcp"
        current["source_id"] = "mcp:" + "c" * 64
        current["source_binding"] = {"server": "configured-server", "tool": "read_content",
                                     "version": "v1", "snapshot_sha256": "c" * 64,
                                     "manifest_sha256": "d" * 64}
        current["source_binding_digest"] = HELPER.source_binding_digest(
            "mcp", current["source_id"], current["source_binding"])
        self.assertEqual(HELPER.decide(current, observation(current))["action"], "wait")
        current["source_binding"]["version"] = "v2"
        with self.assertRaisesRegex(ValueError, "source binding digest"):
            HELPER.decide(current, observation(current))

    def test_independent_fix_can_proceed_with_dispute_and_missing_file(self):
        current = with_required(ready_review())
        report = HELPER.decide(current, event(current, "assessment", review_message_id="message-1",
                                             coverage_complete=True, confirmed_findings=2,
                                             file_dependent_findings=1, unresolved_claims=1))
        self.assertEqual(report["action"], "dispatch_repair")
        current = apply(current, report)
        self.assertEqual(current["review"]["unresolved_claims"], 1)
        report = HELPER.decide(current, event(current, "worker_result", candidate_source_id=B,
                                             delivery_path="worker/delivery.json"))
        self.assertEqual(report["action"], "run_local_checks")

    def test_required_artifact_findings_must_be_classified(self):
        current = with_required(ready_review())
        with self.assertRaisesRegex(ValueError, "classify file-dependent"):
            HELPER.decide(current, event(current, "assessment", review_message_id="message-1",
                                         coverage_complete=True, confirmed_findings=1, unresolved_claims=0))

    def test_worker_cannot_switch_source_route_implicitly(self):
        current = ready_review()
        current = apply(current, HELPER.decide(current, event(current, "assessment",
                        review_message_id="message-1", coverage_complete=True,
                        confirmed_findings=1, unresolved_claims=0)))
        with self.assertRaisesRegex(ValueError, "fixed source"):
            HELPER.decide(current, event(current, "worker_result",
                                         candidate_source_id="mcp:" + "d" * 64,
                                         delivery_path="worker/delivery.json"))

    def test_changed_acceptance_invalidates_old_gates(self):
        current = ready_review()
        current = apply(current, HELPER.decide(current, event(current, "assessment",
                        review_message_id="message-1", coverage_complete=True,
                        confirmed_findings=0, unresolved_claims=0)))
        current = apply(current, HELPER.decide(current, event(current, "validation",
                        checked_source_id=A, passed=True, required_unverified=[])))
        current = apply(current, HELPER.decide(current, event(current, "delivery",
                        delivered_source_id=A, complete=True)))
        self.assertEqual(current["phase"], "validating")
        current["acceptance_contract"] = {"required_checks": ["local tests", "device"],
                                          "delivery_items": ["review report"]}
        current["acceptance_digest"] = HELPER.acceptance_digest(current["acceptance_contract"])
        report = HELPER.decide(current, event(current, "delivery", delivered_source_id=A, complete=True))
        self.assertEqual(report["action"], "obtain_current_review")

    def test_old_contract_or_host_cannot_satisfy_clean_review(self):
        current = ready_review()
        current = apply(current, HELPER.decide(current, event(current, "assessment",
                        review_message_id="message-1", coverage_complete=True,
                        confirmed_findings=0, unresolved_claims=0)))
        current["review"]["consumer_host"] = "old-host"
        report = HELPER.decide(current, event(current, "validation", checked_source_id=A,
                                             passed=True, required_unverified=[],
                                             next_request_token="test-round-2"))
        self.assertEqual(report["action"], "prepare_review_request")
        current["review"]["consumer_host"] = current["consumer_host"]
        current["review"]["contract_digest"] = "0" * 64
        report = HELPER.decide(current, event(current, "delivery", delivered_source_id=A,
                                             complete=True)) if current["phase"] == "validating" else None
        self.assertEqual(report["action"], "obtain_current_review")

    def test_rejects_old_round_source_token_and_conversation(self):
        current = state()
        for key, bad in (("round", 0), ("source_id", B), ("request_token", "old"),
                         ("conversation_url", "https://chatgpt.com/c/other")):
            with self.subTest(key=key), self.assertRaises(ValueError):
                HELPER.decide(current, observation(current, **{key: bad}))

    def test_full_stable_reply_is_not_final_acceptance(self):
        current = state()
        report = HELPER.decide(current, observation(current))
        self.assertEqual(report["action"], "wait")
        current = apply(current, report)
        early = HELPER.decide(current, observation(current, 5))
        self.assertEqual(early["action"], "wait")
        current = apply(current, early)
        report = HELPER.decide(current, observation(current, 10))
        self.assertEqual(report["action"], "triage_review")
        self.assertFalse(report["terminal"])

    def test_old_partial_generating_and_unknown_replies_never_complete(self):
        for fields in ({"after_request": False}, {"full_body_saved": False},
                       {"generation": "unknown"}, {"generation": "generating"},
                       {"completion_controls": False}, {"body_chars": 0}):
            current = state()
            current = apply(current, HELPER.decide(current, observation(current)))
            report = HELPER.decide(current, observation(current, 20, **fields))
            self.assertEqual(report["action"], "wait")
            self.assertIsNone(report["state_updates"].get("last_completion"))

    def test_changing_reply_restarts_stability_window(self):
        current = state()
        current = apply(current, HELPER.decide(current, observation(current)))
        report = HELPER.decide(current, observation(current, 20, body_sha256="d" * 64))
        self.assertEqual(report["action"], "wait")
        current = apply(current, report)
        report = HELPER.decide(current, observation(current, 30, body_sha256="d" * 64))
        self.assertEqual(report["action"], "triage_review")

    def test_busy_recovery_has_cooldowns_without_ending_code_work(self):
        current = state()
        expected = [(0, "wait"), (29, "wait"), (30, "reload_same_conversation"),
                    (89, "wait"), (90, "reload_same_conversation"),
                    (209, "wait"), (210, "reload_same_conversation"), (400, "backoff_and_diagnose")]
        for seconds, action in expected:
            report = HELPER.decide(current, observation(current, seconds, ui_error="transient"))
            self.assertEqual(report["action"], action)
            self.assertEqual(report["phase"], "waiting_web")
            self.assertFalse(report["terminal"])
            current = apply(current, report)
        recovered = HELPER.decide(current, observation(current, 410))
        self.assertEqual(recovered["state_updates"]["refresh_count"], 0)

    def test_generation_does_not_refresh_even_if_an_error_label_is_present(self):
        current = state()
        report = HELPER.decide(current, observation(current, ui_error="transient", generation="generating"))
        self.assertEqual(report["action"], "wait")

    def test_unknown_send_and_missing_request_do_not_resend(self):
        current = state("ready_to_submit")
        report = HELPER.decide(current, event(current, "submission", status="unknown",
                                             conversation_url=current["conversation_url"]))
        self.assertEqual(report["action"], "reconcile_submission")
        current = state()
        self.assertEqual(HELPER.decide(current, observation(current, request_present=False))["action"],
                         "reconcile_submission")
        with self.assertRaises(ValueError):
            HELPER.decide(current, event(current, "submission", status="not_sent",
                                        conversation_url=current["conversation_url"]))

    def test_sent_readback_only_starts_monitoring(self):
        current = state("submitting")
        report = HELPER.decide(current, submission(current))
        self.assertEqual(report["action"], "watch")

    def test_incomplete_and_disputed_review_cannot_pass(self):
        current = ready_review()
        report = HELPER.decide(current, event(current, "assessment", review_message_id="message-1",
                                             coverage_complete=False, next_request_token="test-round-2"))
        self.assertEqual(report["state_updates"]["round"], 2)
        self.assertFalse(report["terminal"])
        report = HELPER.decide(current, event(current, "assessment", review_message_id="message-1",
                                             coverage_complete=True, confirmed_findings=0, unresolved_claims=1))
        self.assertEqual(report["action"], "investigate_review")

    def test_clean_web_review_still_requires_local_checks_and_delivery(self):
        current = ready_review()
        report = HELPER.decide(current, event(current, "assessment", review_message_id="message-1",
                                             coverage_complete=True, confirmed_findings=0, unresolved_claims=0))
        self.assertEqual(report["action"], "run_local_checks")
        current = apply(current, report)
        report = HELPER.decide(current, event(current, "validation", checked_source_id=A,
                                             passed=True, required_unverified=[]))
        self.assertEqual(report["action"], "finish_delivery")
        current = apply(current, report)
        report = HELPER.decide(current, event(current, "delivery", delivered_source_id=A, complete=True))
        self.assertEqual(report["action"], "disable_followup")
        current = apply(current, report)
        report = HELPER.decide(current, closed_followup(current))
        self.assertTrue(report["terminal"])

    def test_worker_result_does_not_complete_and_failures_keep_repairing(self):
        current = ready_review()
        current["worker_correction_used"] = 1  # Legacy policy must not impose a hidden budget.
        current = apply(current, HELPER.decide(current, event(current, "assessment",
                        review_message_id="message-1", coverage_complete=True,
                        confirmed_findings=2, unresolved_claims=0)))
        for _ in range(6):
            report = HELPER.decide(current, event(current, "worker_result", candidate_source_id=B,
                                                 delivery_path="worker/sealed-delivery.json"))
            self.assertFalse(report["terminal"])
            current = apply(current, report)
            report = HELPER.decide(current, event(current, "validation", checked_source_id=B,
                                                 passed=False, required_unverified=[]))
            self.assertEqual(report["action"], "diagnose_or_repair")
            self.assertEqual(report["phase"], "repairing")
            current = apply(current, report)

    def test_changed_source_requires_new_token_and_new_web_review(self):
        current = state("validating")
        current["candidate_source_id"] = B
        current["review"] = {"source_id": A, "clean": True, "evidence": ["old-review.md"]}
        gate = event(current, "validation", checked_source_id=B, passed=True, required_unverified=[])
        with self.assertRaises(ValueError):
            HELPER.decide(current, gate)
        report = HELPER.decide(current, {**gate, "next_request_token": "test-round-2",
                                         "next_source_binding": {"repository": "owner/project",
                                                                 "commit": "b" * 40}})
        self.assertEqual(report["action"], "prepare_review_request")
        self.assertEqual(report["state_updates"]["source_id"], B)
        self.assertIsNone(report["state_updates"]["review"])
        self.assertFalse(report["terminal"])

    def test_required_device_check_blocks_completion_but_not_independent_work(self):
        current = state("validating")
        report = HELPER.decide(current, event(current, "validation", checked_source_id=A,
                                             passed=True, required_unverified=["required physical-device test"]))
        self.assertEqual(report["action"], "complete_missing_checks")
        issue = event(current, "external_blocker", reason="required device disconnected",
                      attempts=["device discovery log"], requires_external_change="connect the device",
                      independent_work_remaining=True)
        self.assertEqual(HELPER.decide(current, issue)["action"], "continue_independent_work")
        issue["independent_work_remaining"] = False
        report = HELPER.decide(current, issue)
        self.assertEqual(report["phase"], "blocked")
        self.assertFalse(report["terminal"])

    def test_resumed_stale_clean_flag_still_needs_current_source_review(self):
        current = state("validating")
        current["review"] = {"source_id": B, "clean": True, "evidence": ["stale-review.md"]}
        report = HELPER.decide(current, event(current, "validation", checked_source_id=A,
                                             passed=True, required_unverified=[], next_request_token="test-round-2"))
        self.assertEqual(report["action"], "prepare_review_request")
        self.assertIsNone(report["state_updates"]["review"])

    def test_auth_and_user_stop_resume_the_saved_step(self):
        current = state()
        report = HELPER.decide(current, observation(current, ui_error="auth"))
        self.assertEqual(report["action"], "request_browser_input")
        self.assertEqual(report["phase"], "waiting_web")
        current = apply(current, HELPER.decide(current, event(current, "external_blocker",
                        reason="login required", attempts=["login UI readback"],
                        requires_external_change="user signs in", independent_work_remaining=False)))
        with self.assertRaises(ValueError):
            HELPER.decide(current, observation(current))
        report = HELPER.decide(current, event(current, "resume", resolution_ref="login restored readback",
                                             observed_at=datetime(2026, 1, 1, tzinfo=timezone.utc).isoformat(),
                                             followup_view=followup(current, checked_seconds=0,
                                                                    evidence_ref="view-resume")))
        self.assertEqual(report["phase"], "waiting_web")
        current = apply(current, report)
        with self.assertRaises(ValueError):
            HELPER.decide(current, event(current, "pause", reason="one repair completed"))
        report = HELPER.decide(current, event(current, "pause", reason="user_stop", user_instruction_ref="user turn"))
        self.assertEqual(report["phase"], "paused")

    def test_wrong_source_checks_and_delivery_are_rejected(self):
        current = state("validating")
        for item in (event(current, "validation", checked_source_id=B, passed=True, required_unverified=[]),
                     event(current, "delivery", delivered_source_id=B, complete=True)):
            with self.assertRaises(ValueError):
                HELPER.decide(current, item)

    def test_three_review_rounds_reuse_workflow_then_finish_only_current_source(self):
        current = state("ready_to_submit")
        for round_number in range(1, 4):
            self.assertEqual(current["followup"]["automation_id"], "heartbeat-1")
            if not current.get("prepared_request"):
                current = apply(current, HELPER.decide(current, preparation(current)))
            current = apply(current, HELPER.decide(current, submission(current)))
            current = apply(current, HELPER.decide(current, observation(current)))
            current = apply(current, HELPER.decide(current, observation(current, 10)))
            report = HELPER.decide(current, event(current, "assessment", review_message_id="message-1",
                                  coverage_complete=True, confirmed_findings=0 if round_number == 3 else 1,
                                  unresolved_claims=0))
            current = apply(current, report)
            if round_number < 3:
                self.assertEqual(report["action"], "dispatch_repair")
                revised = "git:" + str(round_number) * 40
                current = apply(current, HELPER.decide(current, event(current, "worker_result",
                                candidate_source_id=revised, delivery_path=f"round-{round_number}/delivery.json")))
                report = HELPER.decide(current, event(current, "validation", checked_source_id=revised,
                                      passed=True, required_unverified=[],
                                      next_request_token=f"test-round-{round_number + 1}",
                                      next_source_binding={"repository": "owner/project",
                                                           "commit": str(round_number) * 40}))
                self.assertEqual(report["action"], "prepare_review_request")
                current = apply(current, report)
            else:
                self.assertEqual(report["action"], "finish_delivery")
                report = HELPER.decide(current, event(current, "delivery",
                                      delivered_source_id=current["source_id"], complete=True))
                self.assertEqual(report["action"], "disable_followup")
                current = apply(current, report)
                report = HELPER.decide(current, closed_followup(current))
                self.assertTrue(report["terminal"])
                self.assertEqual(current["round"], 3)
            self.assertEqual(current["run_id"], "test-run")
            self.assertEqual(current["conversation_url"], state()["conversation_url"])

    def test_readonly_cli_success_and_invalid_input(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            current = state()
            inputs = {"state.json": current, "event.json": observation(current)}
            for name, body in inputs.items():
                (root / name).write_text(json.dumps(body), encoding="utf-8")
            before = {p.name: p.read_bytes() for p in root.iterdir()}
            command = [sys.executable, "-B", str(ROOT / "scripts/next_action.py"),
                       "--state", str(root / "state.json"), "--event", str(root / "event.json")]
            child = subprocess.run(command, capture_output=True, text=True, check=False)
            self.assertEqual(child.returncode, 0, child.stderr)
            self.assertTrue(json.loads(child.stdout)["valid"])
            self.assertEqual(before, {p.name: p.read_bytes() for p in root.iterdir()})
            (root / "event.json").write_text("{broken", encoding="utf-8")
            child = subprocess.run(command, capture_output=True, text=True, check=False)
            self.assertEqual(child.returncode, 2)
            self.assertFalse(json.loads(child.stdout)["valid"])

    def test_decider_does_not_mutate_inputs(self):
        current = state()
        item = observation(current)
        before = copy.deepcopy((current, item))
        HELPER.decide(current, item)
        self.assertEqual((current, item), before)


if __name__ == "__main__":
    unittest.main()
