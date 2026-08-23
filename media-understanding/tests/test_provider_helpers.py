from __future__ import annotations

import argparse
import base64
import contextlib
import io
import importlib.util
import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]


def load_module(name: str, relative: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / relative)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {relative}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


AGNES = load_module("media_understanding_agnes", "scripts/providers/agnes_vision.py")
AUDIO = load_module("media_understanding_m3_audio", "scripts/providers/minimax_m3_course_audio.py")
VIDEO = load_module("media_understanding_m3_video", "scripts/providers/minimax_m3_course_video.py")
ROUTES = load_module("media_understanding_routes", "scripts/check_routes.py")


class ProviderHelperTests(unittest.TestCase):
    def analysis_args(self, *, resume: bool = False, retries: int = 3) -> argparse.Namespace:
        return argparse.Namespace(
            resume=resume,
            prompt_file=None,
            prompt="{start_time}",
            retries=retries,
            retry_sleep=0,
            model="MiniMax-M3",
            max_tokens=10,
            temperature=0.1,
            timeout=1,
        )

    def segment(self) -> dict:
        return {
            "index": 0,
            "file": "/unused/0.mp4",
            "start_time": "00:00:00.000",
            "end_time": "00:01:00.000",
            "start_seconds": 0,
            "end_seconds": 60,
            "duration_seconds": 60,
        }

    def endpoint_args(self, base_url: str) -> argparse.Namespace:
        return argparse.Namespace(
            base_url=base_url,
            env_file="/definitely/missing/minimax.env",
            endpoint="https://api.minimaxi.com/anthropic/v1/messages",
        )

    def test_minimax_base_url_is_normalized_once(self) -> None:
        expected = "https://api.minimaxi.com/anthropic/v1/messages"
        for module in (AUDIO, VIDEO):
            self.assertEqual(module.resolve_endpoint(self.endpoint_args("https://api.minimaxi.com")), expected)
            self.assertEqual(module.resolve_endpoint(self.endpoint_args("https://api.minimaxi.com/anthropic")), expected)
            self.assertEqual(module.resolve_endpoint(self.endpoint_args(expected)), expected)

    def test_windows_posix_permissions_are_unverified(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "secret.env"
            path.write_text("KEY=placeholder\n", encoding="utf-8")
            with mock.patch.object(ROUTES.os, "name", "nt"):
                self.assertIsNone(ROUTES.private_permissions(path))

    def test_minimax_base64_limit_is_checked_before_read(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "large.mp4"
            raw_size = (AUDIO.MAX_BASE64_CHARACTERS * 3 // 4) + 1
            with path.open("wb") as handle:
                handle.truncate(raw_size)
            with contextlib.redirect_stderr(io.StringIO()):
                with self.assertRaises(SystemExit):
                    AUDIO.data_url(path)
                with self.assertRaises(SystemExit):
                    VIDEO.data_url(path)

    def test_agnes_rejects_local_paths_and_model_override_without_network(self) -> None:
        missing_env = Path("/definitely/missing/agnes.env")
        result = AGNES.call_agnes("file:///tmp/image.png", "describe", missing_env, 1)
        self.assertEqual(result["failure_type"], "invalid_image_url")
        with tempfile.TemporaryDirectory() as temporary:
            env = Path(temporary) / "agnes.env"
            env.write_text("AGNES_API_KEY=placeholder\nAGNES_MODEL=agnes-old\n", encoding="utf-8")
            result = AGNES.call_agnes("https://example.com/image.png", "describe", env, 1)
        self.assertEqual(result["failure_type"], "unsupported_model")

    def test_audio_1026_stops_remaining_segments(self) -> None:
        segments = [
            {"index": 0, "file": "/unused/0.mp4", "start_time": "00:00:00.000", "end_time": "00:01:00.000", "start_seconds": 0, "end_seconds": 60, "duration_seconds": 60},
            {"index": 1, "file": "/unused/1.mp4", "start_time": "00:01:00.000", "end_time": "00:02:00.000", "start_seconds": 60, "end_seconds": 120, "duration_seconds": 60},
        ]
        args = argparse.Namespace(resume=False, prompt_file=None, prompt="{start_time}", retries=3, retry_sleep=0, model="MiniMax-M3", max_tokens=10, temperature=0.1, timeout=1)
        rejected = {"ok": False, "status_code": 400, "body": {"error": {"message": "1026 input new_sensitive"}}}
        with tempfile.TemporaryDirectory() as temporary, mock.patch.object(AUDIO, "call_m3", return_value=rejected) as request:
            AUDIO.analyze_segments(segments, Path(temporary), "placeholder", AUDIO.DEFAULT_ENDPOINT, args)
        self.assertEqual(request.call_count, 1)
        self.assertEqual(segments[0]["status"], "m3_blocked_1026_provider_fallback_requires_user_opt_in")
        self.assertEqual(segments[1]["status"], "not_attempted_after_terminal_failure")

    def test_audio_and_video_transport_failure_are_acceptance_unknown_without_retry(self) -> None:
        for module in (AUDIO, VIDEO):
            with self.subTest(module=module.__name__), tempfile.TemporaryDirectory() as temporary:
                segments = [self.segment()]
                with mock.patch.object(
                    module,
                    "call_m3",
                    return_value={"ok": False, "error": "TimeoutError('post timed out')", "body": {}},
                ) as request:
                    module.analyze_segments(
                        segments,
                        Path(temporary),
                        "placeholder",
                        module.DEFAULT_ENDPOINT,
                        self.analysis_args(),
                    )
                self.assertEqual(request.call_count, 1)
                self.assertEqual(segments[0]["request_state"], "acceptance_unknown")
                self.assertIn("acceptance_unknown", segments[0]["status"])

    def test_audio_and_video_empty_2xx_are_accepted_without_retry(self) -> None:
        result = {"ok": True, "status_code": 200, "body": {"content": [], "usage": {"total_tokens": 1}}}
        for module in (AUDIO, VIDEO):
            with self.subTest(module=module.__name__), tempfile.TemporaryDirectory() as temporary:
                segments = [self.segment()]
                with mock.patch.object(module, "call_m3", return_value=result) as request:
                    module.analyze_segments(
                        segments,
                        Path(temporary),
                        "placeholder",
                        module.DEFAULT_ENDPOINT,
                        self.analysis_args(),
                    )
                self.assertEqual(request.call_count, 1)
                self.assertEqual(segments[0]["request_state"], "accepted")
                self.assertIn("empty_result_no_resubmit", segments[0]["status"])

    def test_audio_and_video_resume_never_resubmit_unknown_acceptance(self) -> None:
        unknown = {"ok": False, "error": "ConnectionResetError('after post')", "body": {}}
        for module in (AUDIO, VIDEO):
            with self.subTest(module=module.__name__), tempfile.TemporaryDirectory() as temporary:
                output = Path(temporary)
                with mock.patch.object(module, "call_m3", return_value=unknown):
                    module.analyze_segments(
                        [self.segment()],
                        output,
                        "placeholder",
                        module.DEFAULT_ENDPOINT,
                        self.analysis_args(),
                    )
                resumed = [self.segment()]
                with mock.patch.object(module, "call_m3") as request:
                    module.analyze_segments(
                        resumed,
                        output,
                        "placeholder",
                        module.DEFAULT_ENDPOINT,
                        self.analysis_args(resume=True),
                    )
                request.assert_not_called()
                self.assertEqual(resumed[0]["request_state"], "acceptance_unknown")
                self.assertEqual(resumed[0]["status"], "resume_acceptance_unknown_no_resubmit")

    def test_audio_and_video_interruption_after_pre_submit_marker_never_resubmits(self) -> None:
        for module in (AUDIO, VIDEO):
            with self.subTest(module=module.__name__), tempfile.TemporaryDirectory() as temporary:
                output = Path(temporary)
                with mock.patch.object(
                    module,
                    "call_m3",
                    side_effect=KeyboardInterrupt("interrupted during POST"),
                ):
                    with self.assertRaises(KeyboardInterrupt):
                        module.analyze_segments(
                            [self.segment()],
                            output,
                            "placeholder",
                            module.DEFAULT_ENDPOINT,
                            self.analysis_args(),
                        )
                operation = json.loads(
                    (output / "responses" / "segment_000" / "operation.json").read_text(
                        encoding="utf-8"
                    )
                )
                self.assertEqual(operation["state"], "acceptance_unknown")
                self.assertEqual(
                    operation["retry_disposition"],
                    "submission_started_acceptance_unknown_no_resubmit",
                )
                resumed = [self.segment()]
                with mock.patch.object(module, "call_m3") as request:
                    module.analyze_segments(
                        resumed,
                        output,
                        "placeholder",
                        module.DEFAULT_ENDPOINT,
                        self.analysis_args(resume=True),
                    )
                request.assert_not_called()
                self.assertEqual(resumed[0]["status"], "resume_acceptance_unknown_no_resubmit")

    def test_audio_and_video_resume_1026_stays_terminal_without_resubmit(self) -> None:
        rejected = {
            "ok": False,
            "status_code": 400,
            "body": {"error": {"message": "1026 input new_sensitive"}},
        }
        for module in (AUDIO, VIDEO):
            with self.subTest(module=module.__name__), tempfile.TemporaryDirectory() as temporary:
                output = Path(temporary)
                initial = [self.segment()]
                with mock.patch.object(module, "call_m3", return_value=rejected):
                    module.analyze_segments(
                        initial,
                        output,
                        "placeholder",
                        module.DEFAULT_ENDPOINT,
                        self.analysis_args(),
                    )
                resumed = [self.segment(), {**self.segment(), "index": 1}]
                with mock.patch.object(module, "call_m3") as request:
                    module.analyze_segments(
                        resumed,
                        output,
                        "placeholder",
                        module.DEFAULT_ENDPOINT,
                        self.analysis_args(resume=True),
                    )
                request.assert_not_called()
                self.assertEqual(resumed[0]["status"], "resume_rejected_no_resubmit")
                self.assertEqual(resumed[1]["status"], "not_attempted_after_terminal_failure")

    def test_audio_and_video_completed_state_without_evidence_never_resubmits(self) -> None:
        for module in (AUDIO, VIDEO):
            with self.subTest(module=module.__name__), tempfile.TemporaryDirectory() as temporary:
                output = Path(temporary)
                segment = self.segment()
                args = self.analysis_args(resume=True)
                descriptor_args = (args.model, Path(segment["file"]), segment["start_time"], args) if module is VIDEO else (Path(segment["file"]), segment["start_time"], args)
                fingerprint = module.operation_fingerprint(
                    module.DEFAULT_ENDPOINT,
                    module.operation_descriptor(*descriptor_args),
                )
                operation = output / "responses" / "segment_000" / "operation.json"
                operation.parent.mkdir(parents=True)
                operation.write_text(
                    json.dumps({
                        "state": "completed",
                        "operation_fingerprint": fingerprint,
                        "retry_disposition": "completed_no_retry",
                        "attempts": [],
                        "response_evidence": [],
                    }),
                    encoding="utf-8",
                )
                segments = [segment]
                with mock.patch.object(module, "call_m3") as request:
                    module.analyze_segments(
                        segments,
                        output,
                        "placeholder",
                        module.DEFAULT_ENDPOINT,
                        args,
                    )
                request.assert_not_called()
                self.assertEqual(segments[0]["request_state"], "completed")
                self.assertEqual(segments[0]["status"], "completed_evidence_missing_no_resubmit")

    def test_audio_and_video_real_empty_2xx_are_classified_as_accepted(self) -> None:
        class EmptyResponse:
            status = 200
            headers = {}

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def read(self):
                return b""

        with tempfile.TemporaryDirectory() as temporary:
            media = Path(temporary) / "segment.mp4"
            media.write_bytes(b"fixture")
            args = self.analysis_args()
            for module in (AUDIO, VIDEO):
                with self.subTest(module=module.__name__), mock.patch.object(
                    module, "build_payload", return_value={}
                ), mock.patch.object(module.urllib.request, "urlopen", return_value=EmptyResponse()):
                    if module is VIDEO:
                        result = module.call_m3("key", module.DEFAULT_ENDPOINT, args.model, media, "prompt", args)
                    else:
                        result = module.call_m3("key", module.DEFAULT_ENDPOINT, media, "prompt", args)
                self.assertTrue(result["ok"])
                self.assertEqual({}, result["body"])
                self.assertEqual(("accepted", "provider_accepted_empty_result_no_resubmit"), module.classify_response(result, ""))

    def test_audio_and_video_keep_each_attempt_as_separate_evidence(self) -> None:
        rejected = {"ok": False, "status_code": 429, "body": {"error": {"message": "rate limited"}}}
        completed = {
            "ok": True,
            "status_code": 200,
            "provider_request_id": "req-2",
            "body": {"content": [{"type": "text", "text": "done"}], "usage": {"total_tokens": 2}},
        }
        for module in (AUDIO, VIDEO):
            with self.subTest(module=module.__name__), tempfile.TemporaryDirectory() as temporary:
                segments = [self.segment()]
                with mock.patch.object(module, "call_m3", side_effect=[rejected, completed]) as request:
                    module.analyze_segments(
                        segments,
                        Path(temporary),
                        "placeholder",
                        module.DEFAULT_ENDPOINT,
                        self.analysis_args(),
                    )
                self.assertEqual(request.call_count, 2)
                files = [Path(path) for path in segments[0]["response_files"]]
                self.assertEqual([path.name for path in files], ["attempt_01.json", "attempt_02.json"])
                self.assertEqual(json.loads(files[0].read_text(encoding="utf-8"))["request_state"], "rejected")
                self.assertEqual(json.loads(files[1].read_text(encoding="utf-8"))["request_state"], "completed")

    def test_audio_and_video_refuse_to_overwrite_orphan_response_evidence(self) -> None:
        for module in (AUDIO, VIDEO):
            with self.subTest(module=module.__name__), tempfile.TemporaryDirectory() as temporary:
                output = Path(temporary)
                response = output / "responses" / "segment_000" / "attempt_01.json"
                response.parent.mkdir(parents=True)
                response.write_text('{"preserve":true}\n', encoding="utf-8")
                with mock.patch.object(module, "call_m3") as request:
                    with self.assertRaisesRegex(RuntimeError, "refusing to overwrite"):
                        module.analyze_segments(
                            [self.segment()],
                            output,
                            "placeholder",
                            module.DEFAULT_ENDPOINT,
                            self.analysis_args(),
                        )
                request.assert_not_called()
                self.assertEqual('{"preserve":true}\n', response.read_text(encoding="utf-8"))

    def test_audio_and_video_fingerprint_drift_after_submit_is_unknown(self) -> None:
        completed_for_other_operation = {
            "ok": True,
            "status_code": 200,
            "operation_fingerprint": "f" * 64,
            "body": {"content": [{"type": "text", "text": "must not be accepted"}]},
        }
        for module in (AUDIO, VIDEO):
            with self.subTest(module=module.__name__), tempfile.TemporaryDirectory() as temporary:
                segments = [self.segment()]
                with mock.patch.object(
                    module,
                    "call_m3",
                    return_value=completed_for_other_operation,
                ) as request:
                    module.analyze_segments(
                        segments,
                        Path(temporary),
                        "placeholder",
                        module.DEFAULT_ENDPOINT,
                        self.analysis_args(),
                    )
                self.assertEqual(request.call_count, 1)
                self.assertEqual(segments[0]["request_state"], "acceptance_unknown")
                self.assertEqual(
                    segments[0]["retry_disposition"],
                    "operation_fingerprint_changed_after_submit_no_resubmit",
                )
                self.assertIn("acceptance_unknown", segments[0]["status"])
                response = json.loads(Path(segments[0]["response_files"][0]).read_text(encoding="utf-8"))
                self.assertEqual("f" * 64, response["operation_fingerprint"])
                self.assertNotEqual(
                    response["operation_fingerprint"],
                    response["expected_operation_fingerprint"],
                )

    def test_audio_and_video_payload_and_fingerprint_use_the_same_source_read(self) -> None:
        class Response:
            status = 200
            headers = {}

            def __enter__(self):
                return self

            def __exit__(self, *_args):
                return False

            def read(self):
                return b'{"content":[{"type":"text","text":"ok"}]}'

        original_bytes = b"original-media-bytes"
        replacement_bytes = b"replacement-media-bytes"
        for module in (AUDIO, VIDEO):
            with self.subTest(module=module.__name__), tempfile.TemporaryDirectory() as temporary:
                media = Path(temporary) / "segment.mp4"
                media.write_bytes(original_bytes)
                args = self.analysis_args()
                original_builder = module.build_payload

                def swapping_builder(*builder_args, **builder_kwargs):
                    payload = original_builder(*builder_args, **builder_kwargs)
                    media.write_bytes(replacement_bytes)
                    return payload

                with mock.patch.object(module, "build_payload", side_effect=swapping_builder), mock.patch.object(
                    module.urllib.request,
                    "urlopen",
                    return_value=Response(),
                ) as urlopen:
                    if module is VIDEO:
                        result = module.call_m3(
                            "key", module.DEFAULT_ENDPOINT, args.model, media, "prompt", args
                        )
                        descriptor = module.operation_descriptor(
                            args.model, media, "prompt", args, original_bytes
                        )
                    else:
                        result = module.call_m3(
                            "key", module.DEFAULT_ENDPOINT, media, "prompt", args
                        )
                        descriptor = module.operation_descriptor(
                            media, "prompt", args, original_bytes
                        )
                request = urlopen.call_args.args[0]
                payload = json.loads(request.data.decode("utf-8"))
                encoded = payload["messages"][0]["content"][1]["source"]["url"].split(",", 1)[1]
                self.assertEqual(original_bytes, base64.b64decode(encoded))
                self.assertEqual(
                    module.operation_fingerprint(module.DEFAULT_ENDPOINT, descriptor),
                    result["operation_fingerprint"],
                )
                self.assertEqual(replacement_bytes, media.read_bytes())

    def test_audio_and_video_resume_rejects_forged_safe_retry_without_evidence(self) -> None:
        for module in (AUDIO, VIDEO):
            with self.subTest(module=module.__name__), tempfile.TemporaryDirectory() as temporary:
                output = Path(temporary)
                segment = self.segment()
                args = self.analysis_args(resume=True)
                descriptor_args = (
                    (args.model, Path(segment["file"]), segment["start_time"], args)
                    if module is VIDEO
                    else (Path(segment["file"]), segment["start_time"], args)
                )
                fingerprint = module.operation_fingerprint(
                    module.DEFAULT_ENDPOINT,
                    module.operation_descriptor(*descriptor_args),
                )
                operation = output / "responses" / "segment_000" / "operation.json"
                operation.parent.mkdir(parents=True)
                forged_reference = {"path": "attempt_01.json", "sha256": "0" * 64}
                operation.write_text(
                    json.dumps(
                        {
                            "state": "rejected",
                            "operation_fingerprint": fingerprint,
                            "retry_disposition": "retry_allowed_proven_not_accepted",
                            "attempts": [
                                {
                                    "state": "rejected",
                                    "status_code": 429,
                                    "expected_operation_fingerprint": fingerprint,
                                    "response_evidence": forged_reference,
                                }
                            ],
                            "response_evidence": [forged_reference],
                        }
                    ),
                    encoding="utf-8",
                )
                segments = [segment]
                with mock.patch.object(module, "call_m3") as request:
                    module.analyze_segments(
                        segments,
                        output,
                        "placeholder",
                        module.DEFAULT_ENDPOINT,
                        args,
                    )
                request.assert_not_called()
                self.assertEqual("resume_rejected_no_resubmit", segments[0]["status"])

    def test_audio_and_video_resume_revalidates_response_hash(self) -> None:
        completed = {
            "ok": True,
            "status_code": 200,
            "body": {"content": [{"type": "text", "text": "verified"}]},
        }
        for module in (AUDIO, VIDEO):
            with self.subTest(module=module.__name__), tempfile.TemporaryDirectory() as temporary:
                output = Path(temporary)
                with mock.patch.object(module, "call_m3", return_value=completed):
                    first = [self.segment()]
                    module.analyze_segments(
                        first,
                        output,
                        "placeholder",
                        module.DEFAULT_ENDPOINT,
                        self.analysis_args(),
                    )
                response = Path(first[0]["response_files"][0])
                response.write_text('{"tampered":true}\n', encoding="utf-8")
                resumed = [self.segment()]
                with mock.patch.object(module, "call_m3") as request:
                    module.analyze_segments(
                        resumed,
                        output,
                        "placeholder",
                        module.DEFAULT_ENDPOINT,
                        self.analysis_args(resume=True),
                    )
                request.assert_not_called()
                self.assertEqual(
                    "completed_evidence_missing_no_resubmit",
                    resumed[0]["status"],
                )

    def test_audio_and_video_resume_retries_only_with_bound_429_evidence(self) -> None:
        rejected = {
            "ok": False,
            "status_code": 429,
            "body": {"error": {"message": "rate limited"}},
        }
        completed = {
            "ok": True,
            "status_code": 200,
            "body": {"content": [{"type": "text", "text": "done"}]},
        }
        for module in (AUDIO, VIDEO):
            with self.subTest(module=module.__name__), tempfile.TemporaryDirectory() as temporary:
                output = Path(temporary)
                with mock.patch.object(module, "call_m3", return_value=rejected):
                    module.analyze_segments(
                        [self.segment()],
                        output,
                        "placeholder",
                        module.DEFAULT_ENDPOINT,
                        self.analysis_args(retries=1),
                    )
                resumed = [self.segment()]
                with mock.patch.object(module, "call_m3", return_value=completed) as request:
                    module.analyze_segments(
                        resumed,
                        output,
                        "placeholder",
                        module.DEFAULT_ENDPOINT,
                        self.analysis_args(resume=True),
                    )
                self.assertEqual(1, request.call_count)
                self.assertEqual("success", resumed[0]["status"])
                self.assertEqual("completed", resumed[0]["request_state"])

    def test_audio_and_video_completed_resume_requires_the_full_attempt_chain(self) -> None:
        rejected = {
            "ok": False,
            "status_code": 429,
            "body": {"error": {"message": "rate limited"}},
        }
        completed = {
            "ok": True,
            "status_code": 200,
            "body": {"content": [{"type": "text", "text": "done"}]},
        }
        for module in (AUDIO, VIDEO):
            with self.subTest(module=module.__name__), tempfile.TemporaryDirectory() as temporary:
                output = Path(temporary)
                first = [self.segment()]
                with mock.patch.object(module, "call_m3", side_effect=[rejected, completed]):
                    module.analyze_segments(
                        first,
                        output,
                        "placeholder",
                        module.DEFAULT_ENDPOINT,
                        self.analysis_args(),
                    )
                first_response = Path(first[0]["response_files"][0])
                first_response.write_text('{"tampered":true}\n', encoding="utf-8")
                resumed = [self.segment()]
                with mock.patch.object(module, "call_m3") as request:
                    module.analyze_segments(
                        resumed,
                        output,
                        "placeholder",
                        module.DEFAULT_ENDPOINT,
                        self.analysis_args(resume=True),
                    )
                request.assert_not_called()
                self.assertEqual(
                    "completed_evidence_missing_no_resubmit",
                    resumed[0]["status"],
                )

    def test_minimax_media_requests_do_not_assume_idempotency_keys(self) -> None:
        for relative in (
            "scripts/providers/minimax_m3_course_audio.py",
            "scripts/providers/minimax_m3_course_video.py",
        ):
            self.assertNotIn("Idempotency-Key", (ROOT / relative).read_text(encoding="utf-8"))

    def test_audio_main_exits_nonzero_when_analysis_failed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            input_path = Path(temporary) / "input.mp4"
            input_path.touch()
            output_path = Path(temporary) / "output"
            segments = [{"index": 0, "file": "/unused/0.mp4", "status": "pending"}]

            def mark_failed(items, *_args):
                items[0]["status"] = "m3_failed_400"

            argv = ["audio", "--input", str(input_path), "--output-dir", str(output_path), "--analyze"]
            with (
                mock.patch.object(sys, "argv", argv),
                contextlib.redirect_stdout(io.StringIO()),
                contextlib.redirect_stderr(io.StringIO()),
                mock.patch.object(AUDIO, "ffprobe", return_value={}),
                mock.patch.object(AUDIO, "has_stream", return_value=True),
                mock.patch.object(AUDIO, "duration_seconds", return_value=1.0),
                mock.patch.object(AUDIO, "segment_audio_as_video", return_value=segments),
                mock.patch.object(AUDIO, "resolve_api_key", return_value="placeholder"),
                mock.patch.object(AUDIO, "analyze_segments", side_effect=mark_failed),
            ):
                with self.assertRaises(SystemExit) as raised:
                    AUDIO.main()
            self.assertEqual(raised.exception.code, 1)


if __name__ == "__main__":
    unittest.main()
