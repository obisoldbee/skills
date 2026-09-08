from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import socket
import tempfile
import unittest
import urllib.parse
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/agnes_media.py"
SPEC = importlib.util.spec_from_file_location("agnes_lifecycle", SCRIPT)
assert SPEC and SPEC.loader
agnes = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(agnes)
FLASH = "agnes-video-2.5-flash"
STANDARD = "agnes-video-2.5"
RESULT_URL = "https://example.com/final.mp4"


class VideoLifecycleTests(unittest.TestCase):
    def setUp(self):
        self.enterContext(mock.patch.object(agnes, "execution_config", return_value=("https://example.com/v1", "fake-key")))
        self.enterContext(mock.patch.object(agnes, "parse_env_file", side_effect=AssertionError("secrets forbidden")))
        self.enterContext(mock.patch.object(socket, "create_connection", side_effect=AssertionError("network forbidden")))
        self.request = self.enterContext(mock.patch.object(agnes, "request_json"))
        self.sleep = self.enterContext(mock.patch.object(agnes.time, "sleep"))
        self.clock = self.enterContext(mock.patch.object(agnes.time, "monotonic", return_value=0))

    def poll(self, initial, **overrides):
        options = dict(base_url="https://example.com/v1", key="fake-key", timeout=120,
                       poll_interval=1.5, max_wait=10, model=FLASH)
        options.update(overrides)
        return agnes.poll_video(initial, **options)

    def test_base_url_normalization_and_query_model_binding(self):
        for base in ("https://example.com", "https://example.com/", "https://example.com/v1", "https://example.com/v1/"):
            url = agnes.video_query_url(base, "id & ?中文", STANDARD)
            self.assertEqual(urllib.parse.urlsplit(url).path, "/agnesapi")
            self.assertEqual(urllib.parse.parse_qs(urllib.parse.urlsplit(url).query),
                             {"video_id": ["id & ?中文"], "model_name": [STANDARD]})
        for base in ("file:///v1", "https://example.com/other", "https://example.com:bad", "https://user:key@example.com", "https://example.com/?key=private", "https://example .com"):
            with self.subTest(base=base), self.assertRaises(agnes.AgnesError):
                agnes.service_root(base)

    def test_status_preview_is_get_only_and_requires_original_model(self):
        args = agnes.parse_args(["video-status", "--video-id", "known", "--model", STANDARD])
        request = agnes.dry_run(args, {})["request"]
        self.assertEqual(request["method"], "GET")
        self.assertNotIn("payload", request)
        for flags in (("--video-id", "known"), ("--video-id", " ", "--model", FLASH),
                      ("--video-id", "known", "--model", FLASH, "--output", "out.mp4")):
            with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit):
                agnes.parse_args(["video-status", *flags])
        self.request.assert_not_called()

    def test_poll_keeps_original_id_and_model_when_responses_omit_them(self):
        self.request.side_effect = [{"status": "in_progress"}, {"status": "completed", "metadata": {"url": RESULT_URL}}]
        result = self.poll({"video_id": "known", "status": "queued"}, model=STANDARD)
        self.assertEqual(result["metadata"]["url"], RESULT_URL)
        self.assertEqual(self.request.call_count, 2)
        for call in self.request.call_args_list:
            self.assertEqual(call.args[:2], ("GET", f"https://example.com/agnesapi?video_id=known&model_name={STANDARD}"))
            self.assertEqual(call.kwargs["timeout"], 10)

    def test_missing_query_id_or_model_never_substitutes_task_id(self):
        for initial in ({"task_id": "task", "id": "task", "status": "queued"},
                        {"video_id": 123, "status": "queued"}, {"video_id": " ", "status": "queued"}):
            with self.assertRaises(agnes.AgnesError):
                self.poll(initial)
        with self.assertRaises(agnes.AgnesError):
            self.poll({"video_id": "known", "status": "queued"}, model=None)
        self.request.assert_not_called()

    def test_poll_rejects_mismatch_unknown_status_failed_and_missing_url(self):
        for response in ({"status": "queued", "model": STANDARD}, {"status": "queued", "video_id": "another"},
                         {"status": "future"}, {"status": []}, {}, {"status": "failed", "error": "private-body"},
                         {"status": "completed"}, {"status": "completed", "remixed_from_video_id": RESULT_URL}):
            with self.subTest(response=response):
                self.request.return_value = response
                with self.assertRaises(agnes.AgnesError) as caught:
                    self.poll({"video_id": "known", "status": "queued"})
                self.assertNotIn("private-body", str(caught.exception))

    def test_pending_url_is_not_a_result_and_transport_failure_does_not_retry(self):
        self.assertIsNone(agnes.video_result_url({"status": "in_progress", "metadata": {"url": RESULT_URL}}))
        self.request.side_effect = agnes.AgnesError("Agnes request failed: HTTP 429")
        with self.assertRaises(agnes.AgnesError):
            self.poll({"video_id": "known", "status": "queued"})
        self.request.assert_called_once()

    def test_deadline_limits_sleep_and_network_timeout(self):
        self.clock.side_effect = [0, 0, 0, 10]
        with self.assertRaisesRegex(agnes.AgnesError, "timed out"):
            self.poll({"video_id": "known", "status": "queued"}, poll_interval=99)
        self.sleep.assert_called_once_with(10)
        self.request.assert_not_called()

    def test_status_execution_only_gets_original_task_and_saves_same_result(self):
        if not agnes.DIR_FD_OUTPUT_SUPPORTED:
            self.skipTest("platform lacks safe directory-relative publication")
        self.request.return_value = {"status": "completed", "video_id": "known", "model": STANDARD, "metadata": {"url": RESULT_URL}}
        with tempfile.TemporaryDirectory() as temporary, mock.patch.object(agnes.urllib.request, "urlopen", return_value=io.BytesIO(b"video-content")):
            target = Path(temporary) / "result.mp4"
            args = agnes.parse_args(["video-status", "--video-id", "known", "--model", STANDARD, "--wait", "--output", str(target), "--execute"])
            agnes.execute(args, {})
            self.assertEqual(target.read_bytes(), b"video-content")
            self.assertEqual(list(target.parent.iterdir()), [target])
        self.request.assert_called_once_with("GET", f"https://example.com/agnesapi?video_id=known&model_name={STANDARD}", "fake-key", timeout=120)

    def test_query_download_failure_keeps_original_id_and_model_in_receipt(self):
        if not agnes.DIR_FD_OUTPUT_SUPPORTED:
            self.skipTest("platform lacks safe directory-relative publication")
        self.request.return_value = {"status": "completed", "metadata": {"url": RESULT_URL}}
        with tempfile.TemporaryDirectory() as temporary, mock.patch.object(agnes.urllib.request, "urlopen", side_effect=OSError("download failure")):
            target = Path(temporary) / "result.mp4"
            args = agnes.parse_args(["video-status", "--video-id", "known", "--model", STANDARD, "--wait", "--output", str(target), "--execute"])
            with self.assertRaises(agnes.AgnesError) as caught:
                agnes.execute(args, {})
            receipt = json.loads(Path(caught.exception.recovery["path"]).read_text())
            self.assertEqual(receipt["media"], "video")
            self.assertEqual(receipt["result"]["video_id"], "known")
            self.assertEqual(receipt["result"]["model"], STANDARD)
            self.assertEqual(receipt["result"]["metadata"]["url"], RESULT_URL)
            self.assertFalse(target.exists())
        self.assertEqual([call.args[0] for call in self.request.call_args_list], ["GET"])

    def test_creation_is_one_post_and_missing_video_id_is_not_success(self):
        args = agnes.parse_args(["video", "--prompt", "generate", "--execute"])
        self.request.return_value = {"video_id": "known", "status": "queued"}
        agnes.execute(args, agnes.build_video_payload(args))
        self.assertEqual(self.request.call_args.args[:2], ("POST", "https://example.com/v1/videos"))
        self.request.assert_called_once()
        self.request.return_value = {"task_id": "task", "status": "queued"}
        with self.assertRaisesRegex(agnes.AgnesError, "video_id"):
            agnes.execute(args, agnes.build_video_payload(args))

    def test_single_status_read_rejects_failed_or_invalid_completion(self):
        args = agnes.parse_args(["video-status", "--video-id", "known", "--model", FLASH, "--execute"])
        for response in ({"status": "failed"}, {"status": "completed"}, {"status": "queued", "video_id": "different"}):
            self.request.return_value = response
            with self.assertRaises(agnes.AgnesError):
                agnes.execute(args, {})
        self.assertTrue(all(call.args[0] == "GET" for call in self.request.call_args_list))


if __name__ == "__main__":
    unittest.main()
