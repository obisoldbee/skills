from __future__ import annotations

import argparse
import contextlib
import io
import importlib.util
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
