"""Offline replay of endpoint selection and ambiguous cross-device delivery."""
import copy
import hashlib
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "scripts"))
from resolve_thread_transport import resolve
from validate_dispatch_route import classify_failure, validate_attempt


def request():
    return {"caller_id": "device-a", "target_thread_id": "task-b", "request_id": "run-1-command-1",
            "prompt": "Continue the accepted task once. request_id=run-1-command-1",
            "write_binding": {"caller_id": "device-a", "thread_id": "task-b", "host_id": "desktop-b",
                              "basis": "confirmed_delivery", "evidence_ref": "receipts/previous-send.json"},
            "read_endpoints": [{"host_id": "ssh-b", "status": "idle"}]}


def failed(doc, status="not_delivered", host="ssh-b", failure="thread_writer_conflict"):
    doc["last_delivery"] = {"caller_id": doc["caller_id"], "target_thread_id": doc["target_thread_id"],
                            "request_id": doc["request_id"], "payload_sha256": hashlib.sha256(doc["prompt"].encode()).hexdigest(),
                            "attempt_id": "attempt-1", "host_id": host, "status": status,
                            "failure_class": failure, "evidence_ref": "receipts/attempt-1.json"}
    return doc


class TransportTests(unittest.TestCase):
    def test_new_reader_does_not_replace_successful_write_endpoint(self):
        doc = request()
        self.assertEqual(resolve(doc)["send_arguments"]["hostId"], "desktop-b")
        self.assertEqual(doc, request())

    def test_known_rejection_on_reader_recovers_original_endpoint(self):
        doc = failed(request())
        result = resolve(doc)
        self.assertEqual(result["action"], "prepare_send")
        self.assertEqual(result["send_arguments"], {"threadId": "task-b", "hostId": "desktop-b", "prompt": doc["prompt"]})

    def test_idle_is_not_writer_release(self):
        doc = failed(request(), host="desktop-b")
        doc["destination_status"] = "idle"
        self.assertEqual(resolve(doc)["action"], "restore_write_endpoint")
        self.assertIsNone(resolve(doc)["send_arguments"])

    def test_ssh_created_thread_stays_on_ssh(self):
        doc = request()
        doc["write_binding"].update(host_id="ssh-b", basis="created")
        self.assertEqual(resolve(doc)["send_arguments"]["hostId"], "ssh-b")

    def test_reader_only_or_unknown_binding_has_action_without_global_failure(self):
        for binding in ({}, {**request()["write_binding"], "basis": "read_thread"}):
            doc = request(); doc["write_binding"] = binding
            result = resolve(doc)
            self.assertEqual(result["action"], "resolve_write_endpoint")
            self.assertFalse(result["terminal"])

    def test_caller_relative_local_cannot_be_reused_from_other_device(self):
        doc = request(); doc["write_binding"]["host_id"] = "local"
        self.assertEqual(resolve(doc)["send_arguments"]["hostId"], "local")
        doc["caller_id"] = "device-b"
        self.assertEqual(resolve(doc)["action"], "resolve_write_endpoint")

    def test_timeout_and_absent_history_do_not_resend(self):
        doc = failed(request(), status="unknown", failure="transport_timeout")
        doc["delivery_readback"] = {**doc["last_delivery"], "status": "absent", "evidence_ref": "reads/full-history.json"}
        self.assertEqual(resolve(doc)["action"], "reconcile_delivery")
        self.assertIsNone(resolve(doc)["send_arguments"])

    def test_error_but_original_message_present_means_collect(self):
        doc = failed(request(), status="unknown")
        doc["delivery_readback"] = {**doc["last_delivery"], "status": "present", "evidence_ref": "reads/exact-message.json"}
        self.assertEqual(resolve(doc)["action"], "collect_result")

    def test_accepted_message_does_not_require_repairing_route(self):
        doc = failed(request(), status="delivered"); doc.pop("write_binding")
        self.assertEqual(resolve(doc)["action"], "collect_result")

    def test_changed_prompt_or_wrong_readback_cannot_reuse_receipt(self):
        doc = failed(request()); doc["prompt"] += " different scope"
        with self.assertRaises(ValueError): resolve(doc)
        doc = failed(request(), status="unknown")
        doc["delivery_readback"] = {**doc["last_delivery"], "status": "present", "target_thread_id": "other-task"}
        with self.assertRaises(ValueError): resolve(doc)

    def test_connection_recovery_is_bound_to_attempt_and_original_endpoint(self):
        doc = failed(request(), host="desktop-b", failure="transport_unavailable")
        self.assertEqual(resolve(doc)["action"], "restore_connection")
        doc["recovery"] = {"caller_id": "device-a", "thread_id": "task-b", "host_id": "desktop-b",
                           "after_attempt_id": "attempt-1", "kind": "same_endpoint_reconnected", "evidence_ref": "io/reconnected.json"}
        self.assertEqual(resolve(doc)["action"], "prepare_send")
        for field, value in (("after_attempt_id", "attempt-0"), ("host_id", "ssh-b"), ("caller_id", "device-c")):
            bad = copy.deepcopy(doc); bad["recovery"][field] = value
            self.assertEqual(resolve(bad)["action"], "restore_connection")
        doc["last_delivery"]["failure_class"] = "thread_writer_conflict"
        self.assertEqual(resolve(doc)["action"], "restore_write_endpoint")
        doc["recovery"]["kind"] = "writer_endpoint_restored"
        self.assertEqual(resolve(doc)["action"], "prepare_send")

    def test_parameter_and_permission_errors_do_not_use_transport_retry(self):
        for failure in ("unsupported_parameter", "permission", "quota", "unknown"):
            self.assertEqual(resolve(failed(request(), failure=failure))["action"], "inspect_send_failure")

    def test_specific_error_overrides_coarse_invalid_request(self):
        attempt = {"operation": "failure_report", "action": "none", "tool": "none", "failure_class": "invalid_request",
                   "route_changed": False, "explicit_user_route_change": False,
                   "route": {"requested_route": "luna-max", "model": "gpt-6-luna", "reasoning": "max",
                             "surface": "visible_thread", "model_basis": "explicit_skill_route", "reasoning_basis": "explicit_skill_route"},
                   "error": {"code": -32600, "stage": "thread/resume", "message": "thread task-b already has an active writer"}}
        result = validate_attempt(attempt)
        self.assertTrue(result["valid"])
        self.assertEqual(result["failure_class"], "thread_writer_conflict")
        self.assertEqual(result["failure_disposition"]["next_action"], "resolve_original_write_endpoint")
        self.assertFalse(result["failure_disposition"]["terminal"])
        self.assertFalse(result["failure_disposition"]["model_unavailable_supported"])

    def test_timeout_classification_keeps_provider_failures_separate(self):
        self.assertEqual(classify_failure("invalid_request", "initialize handshake timed out"), "transport_timeout")
        self.assertEqual(classify_failure("unknown", {"stage": "send_message_to_thread", "message": "connection closed"}), "transport_unavailable")
        self.assertEqual(classify_failure("provider_model", {"stage": "provider", "message": "timeout"}), "provider_model")

    def test_cli_emits_real_message_fields_without_model_override(self):
        with tempfile.TemporaryDirectory() as directory:
            path = Path(directory) / "transport.json"; path.write_text(json.dumps(request()), encoding="utf-8")
            result = subprocess.run([sys.executable, "-B", str(ROOT / "scripts/resolve_thread_transport.py"), str(path)], capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(set(json.loads(result.stdout)["send_arguments"]), {"threadId", "hostId", "prompt"})


if __name__ == "__main__":
    unittest.main()
