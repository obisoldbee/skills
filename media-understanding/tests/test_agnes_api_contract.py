from __future__ import annotations

import importlib.util
import io
import json
import subprocess
import sys
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import urllib.error


ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location("agnes_contract", ROOT / "scripts/providers/agnes_vision.py")
agnes = importlib.util.module_from_spec(spec)
spec.loader.exec_module(agnes)


class AgnesContractTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.env = Path(self.temp.name) / "fixture.env"
        self.env.write_text("AGNES_API_KEY=fixture-key\nAGNES_MODEL=agnes-3.0-flash\n")
        self.env.chmod(0o600)
        self.patch = mock.patch.dict(agnes.os.environ, {}, clear=True)
        self.patch.start()
        self.addCleanup(self.patch.stop)

    def response(self, *, content="observed", finish_reason="stop"):
        response = mock.MagicMock()
        response.__enter__.return_value = response
        response.status = 200
        response.read.return_value = json.dumps({"choices": [{"message": {"content": content},
                                                             "finish_reason": finish_reason}]}).encode()
        return response

    def call(self, **kwargs):
        return agnes.call_agnes("https://example.com/image.png", "describe", self.env, 1, **kwargs)

    def test_documented_image_shape_and_explicit_thinking_budget(self):
        for thinking in (None, True, False):
            with self.subTest(thinking=thinking), mock.patch.object(agnes, "authenticated_urlopen", return_value=self.response()) as send:
                result = self.call(max_tokens=2048, thinking=thinking)
            request = send.call_args.args[0]
            body = json.loads(request.data)
            self.assertEqual(request.full_url, "https://apihub.agnes-ai.com/v1/chat/completions")
            self.assertEqual(body["messages"][0]["content"][1],
                             {"type": "image_url", "image_url": {"url": "https://example.com/image.png"}})
            self.assertEqual(body["max_tokens"], 2048)
            if thinking is None:
                self.assertNotIn("chat_template_kwargs", body)
            else:
                self.assertEqual(body["chat_template_kwargs"], {"enable_thinking": thinking})
            self.assertEqual(result["request_state"], "completed")

    def test_route_preflight_and_execution_use_the_same_slot(self):
        slot = Path(self.temp.name) / ".codex/secrets/agnes.env"
        slot.parent.mkdir(parents=True)
        self.env = slot
        base = {"AGNES_API_KEY": "fixture-private", "AGNES_MODEL": agnes.DEFAULT_MODEL}
        cases = [
            ({}, {}, "missing_credentials", None),
            ({"AGNES_MODEL": agnes.DEFAULT_MODEL}, {}, "missing_credentials", None),
            (dict(base, AGNES_API_KEY=""), {}, "missing_credentials", None),
            (dict(base, AGNES_API_KEY="   "), {}, "missing_credentials", None),
            (base, {"AGNES_MODEL": "old-model"}, "configuration_mismatch", "AGNES_MODEL"),
            (dict(base, AGNES_MODEL="nonpublic-synthetic-model-marker"), {}, "configuration_mismatch", "AGNES_MODEL"),
            (base, {"AGNES_API_KEY": "inherited-private"}, "configuration_mismatch", "AGNES_API_KEY"),
            (base, {"AGNES_BASE_URL": "https://other.invalid/v1"}, "configuration_mismatch", "AGNES_BASE_URL"),
            (base, dict(base, AGNES_BASE_URL=agnes.DEFAULT_BASE_URL + "/"), "configured_not_called", None),
        ]
        for values, inherited, expected, conflict in cases:
            with self.subTest(expected=expected, conflict=conflict):
                slot.write_text("".join(f"{k}={v}\n" for k, v in values.items()))
                slot.chmod(0o600)
                with mock.patch.dict(agnes.os.environ, inherited, clear=True):
                    output = subprocess.check_output([
                        sys.executable, "-B", str(ROOT / "scripts/check_routes.py"),
                        "--route", "agnes-image", "--home", self.temp.name], text=True)
                    route = json.loads(output)["routes"][0]
                    self.assertEqual(route["readiness"], expected)
                    self.assertNotIn("fixture-private", output)
                    self.assertNotIn("inherited-private", output)
                    self.assertNotIn("nonpublic-synthetic-model-marker", output)
                    if conflict:
                        self.assertIn(conflict, route["credentials"]["mismatched_expected_env"])
                        self.assertEqual({}, route["credentials"]["safe_values"])
                    with mock.patch.object(agnes, "authenticated_urlopen", return_value=self.response()) as send:
                        result = self.call()
                if expected == "configured_not_called":
                    self.assertEqual(result["model"], route["model"])
                    self.assertEqual(result["request_state"], "completed")
                    send.assert_called_once()
                else:
                    self.assertNotIn("nonpublic-synthetic-model-marker", json.dumps(result))
                    self.assertEqual(result["failure_type"], expected)
                    self.assertEqual(result["request_state"], "not_sent")
                    send.assert_not_called()

    def test_invalid_budget_stops_before_request(self):
        with mock.patch.object(agnes, "authenticated_urlopen") as send:
            for value in (0, -1, 65537, True):
                self.assertEqual(self.call(max_tokens=value)["request_state"], "not_sent")
            send.assert_not_called()

    def test_partial_or_empty_result_keeps_accepted_state(self):
        for text, finish in (("partial", "length"), ("", "stop")):
            with self.subTest(finish=finish), mock.patch.object(agnes, "authenticated_urlopen", return_value=self.response(content=text, finish_reason=finish)) as send:
                result = self.call()
            self.assertNotEqual(result["status"], "success")
            self.assertEqual(result["request_state"], "accepted")
            self.assertEqual(send.call_count, 1)

    def test_transport_and_server_errors_are_unknown_without_retry(self):
        errors = [TimeoutError("fixture timeout"), urllib.error.URLError("fixture connection lost"),
                  urllib.error.HTTPError("https://example.com", 503, "fixture", {}, io.BytesIO(b"unavailable"))]
        for error in errors:
            with self.subTest(error=type(error).__name__), mock.patch.object(agnes, "authenticated_urlopen", side_effect=error) as send:
                result = self.call()
            self.assertEqual(result["request_state"], "acceptance_unknown")
            self.assertEqual(send.call_count, 1)

    def test_explicit_authentication_error_is_rejected_once(self):
        error = urllib.error.HTTPError("https://example.com", 401, "fixture", {}, io.BytesIO(b"unauthorized"))
        with mock.patch.object(agnes, "authenticated_urlopen", side_effect=error) as send:
            result = self.call()
        self.assertEqual(result["request_state"], "rejected")
        self.assertEqual(send.call_count, 1)

    def test_malformed_success_shapes_preserve_accepted_evidence(self):
        for body in ({"choices": {"message": {"content": "bad shape"}}},
                     {"choices": [{"message": []}]}, ["not an object"]):
            response = self.response()
            response.read.return_value = json.dumps(body).encode()
            with self.subTest(body=body), mock.patch.object(agnes, "authenticated_urlopen", return_value=response) as send:
                result = self.call()
            self.assertEqual(result["request_state"], "accepted")
            self.assertEqual(result["raw_response"], body)
            self.assertNotEqual(result["status"], "success")
            self.assertEqual(send.call_count, 1)


if __name__ == "__main__":
    unittest.main()
