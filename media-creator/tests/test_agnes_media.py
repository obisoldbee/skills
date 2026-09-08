from __future__ import annotations

import contextlib
import importlib.util
import io
import json
import subprocess
import sys
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "agnes_media.py"
SPEC = importlib.util.spec_from_file_location("agnes_media", SCRIPT)
assert SPEC and SPEC.loader
agnes_media = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(agnes_media)


class AgnesMediaTests(unittest.TestCase):
    def run_cli(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, "-B", str(SCRIPT), *arguments],
            text=True,
            capture_output=True,
            check=False,
        )

    def test_image_dry_run_is_local_and_uses_extra_body_images(self) -> None:
        result = self.run_cli(
            "image",
            "--prompt",
            "Combine the references",
            "--image",
            "https://example.com/one.png",
            "--image",
            "local-does-not-need-to-exist.png",
            "--response-format",
            "b64_json",
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        report = json.loads(result.stdout)
        self.assertFalse(report["provider_calls"])
        self.assertFalse(report["secrets_read"])
        payload = report["request"]["payload"]
        self.assertEqual(payload["model"], "agnes-image-2.5-flash")
        self.assertNotIn("return_base64", payload)
        self.assertNotIn("response_format", payload)
        self.assertEqual(payload["extra_body"]["response_format"], "b64_json")
        self.assertEqual(payload["extra_body"]["image"][0], "https://example.com/one.png")
        self.assertTrue(payload["extra_body"]["image"][1].startswith("<data-uri-from:"))

    def payload(self, media="video", *flags):
        args = agnes_media.parse_args([media, "--prompt", "Move slowly", *flags])
        return agnes_media.build_image_payload(args, execute=False) if media == "image" else agnes_media.build_video_payload(args)

    def invalid(self, media="video", *flags):
        with contextlib.redirect_stderr(io.StringIO()), self.assertRaises(SystemExit) as caught:
            agnes_media.parse_args([media, "--prompt", "Move slowly", *flags])
        self.assertEqual(caught.exception.code, 2)

    def test_image_base64_modes_sizes_and_ratios(self):
        for flags in (("--return-base64",), ("--response-format", "b64_json")):
            payload = self.payload("image", *flags)
            self.assertIs(payload["return_base64"], True)
            self.assertNotIn("extra_body", payload)
        self.assertEqual(self.payload("image")["extra_body"], {"response_format": "url"})
        for size in ("1K", "2K", "3K", "4K", "1024x768"):
            for ratio in ("1:1", "3:4", "4:3", "16:9", "9:16", "2:3", "3:2", "21:9"):
                payload = self.payload("image", "--size", size, "--ratio", ratio)
                self.assertEqual((payload["size"], payload["ratio"]), (size, ratio))
        for flags in (("--size", "5K"), ("--size", "0x1024"), ("--return-base64", "--image", "input.png"),
                      ("--return-base64", "--response-format", "url"), ("--model", "agnes-image-2.1-flash")):
            self.invalid("image", *flags)

    def test_video_text_defaults_and_scalar_parameters(self):
        self.assertEqual(self.payload(), {"model": "agnes-video-2.5-flash", "prompt": "Move slowly", "mode": "text",
                                          "seconds": "5", "size": "720P", "aspect_ratio": "16:9", "n": 1})
        for seconds in range(4, 13):
            for ratio in ("21:9", "16:9", "4:3", "1:1", "3:4", "9:16"):
                payload = self.payload("video", "--seconds", str(seconds), "--aspect-ratio", ratio, "--seed", "0")
                self.assertEqual((payload["seconds"], payload["aspect_ratio"], payload["seed"]), (str(seconds), ratio, 0))

    def test_video_first_last_and_alias_preserve_explicit_inputs(self):
        url = "https://example.com/start.png"
        for model in ("agnes-video-2.5-flash", "agnes-video-2.5"):
            for flag, field in (("--image", "first_frame"), ("--first-frame", "first_frame"), ("--last-frame", "last_frame")):
                payload = self.payload("video", "--model", model, flag, url)
                self.assertEqual((payload["mode"], payload[field]), ("keyframe", url))
                self.assertNotIn("extra_body", payload)
            payload = self.payload("video", "--model", model, "--first-frame", url, "--last-frame", url + "-end")
            self.assertEqual((payload["first_frame"], payload["last_frame"]), (url, url + "-end"))

    def test_reference_limits_order_audio_only_and_standard_video_object(self):
        def flags(images=0, audios=0, videos=0):
            return [v for kind, count in (("image", images), ("audio", audios), ("video", videos))
                    for i in range(count) for v in (f"--reference-{kind}", f"https://example.com/{kind}-{i}")]
        for model, count in (("agnes-video-2.5-flash", 5), ("agnes-video-2.5", 8)):
            payload = self.payload("video", "--model", model, *flags(count, 3))
            self.assertEqual(payload["mode"], "reference")
            self.assertEqual(payload["images"], [f"https://example.com/image-{i}" for i in range(count)])
            self.assertEqual(payload["audios"], [f"https://example.com/audio-{i}" for i in range(3)])
            audio = self.payload("video", "--model", model, *flags(audios=1))
            self.assertEqual(audio["mode"], "reference")
            self.assertNotIn("images", audio)
            for invalid_flags in (flags(count + 1), flags(audios=4), flags(videos=2)):
                self.invalid("video", "--model", model, *invalid_flags)
        self.invalid("video", *flags(videos=1))
        payload = self.payload("video", "--model", "agnes-video-2.5", *flags(8, 3, 1))
        self.assertEqual(payload["videos"], [{"url": "https://example.com/video-0", "start_seconds": 0, "require_audio": False}])
        for flag, enabled in (("--video-require-audio", True), ("--no-video-require-audio", False)):
            payload = self.payload("video", "--model", "agnes-video-2.5", *flags(videos=1), "--video-start-seconds", "1.25", flag)
            self.assertEqual(payload["videos"][0]["start_seconds"], 1.25)
            self.assertIs(payload["videos"][0]["require_audio"], enabled)

    def test_standard_sizes_and_fixed_square_1k_never_promote_flash(self):
        for size in ("720P", "1080P", "1K", "2K"):
            payload = self.payload("video", "--model", "agnes-video-2.5", "--size", size)
            self.assertEqual(payload["aspect_ratio"], "1:1" if size == "1K" else "16:9")
            if size != "720P":
                self.invalid("video", "--size", size)
        self.invalid("video", "--model", "agnes-video-2.5", "--size", "1K", "--aspect-ratio", "16:9")

    def test_modes_reject_missing_mixed_and_duplicate_media(self):
        url = "https://example.com/asset"
        for flags in (("--mode", "keyframe"), ("--mode", "reference"),
                      ("--mode", "text", "--first-frame", url), ("--mode", "text", "--reference-audio", url),
                      ("--mode", "keyframe", "--reference-image", url), ("--mode", "reference", "--last-frame", url),
                      ("--first-frame", url, "--reference-audio", url), ("--first-frame", url, "--image", url),
                      ("--last-frame", url, "--last-frame", url)):
            with self.subTest(flags=flags):
                self.invalid("video", *flags)

    def test_video_urls_and_object_options_fail_before_credential_access(self):
        with mock.patch.object(agnes_media, "execution_config") as config:
            for url in ("local.png", "data:image/png;base64,YQ==", "file:///tmp/asset.png", "https://localhost/a",
                        "http://127.0.0.1/a", "http://10.0.0.1/a", "http://[::1]/a", "https://host.local/a",
                        "https://user:password@example.com/a", "https://example.com:99999/a", "https://example.com/a b"):
                for flag in ("--first-frame", "--last-frame", "--reference-image", "--reference-audio"):
                    self.invalid("video", flag, url, "--execute")
            config.assert_not_called()
        for flags in (("--video-start-seconds", "0"), ("--video-require-audio",), ("--no-video-require-audio",)):
            self.invalid("video", "--model", "agnes-video-2.5", *flags)
        for number in ("-1", "nan", "inf"):
            self.invalid("video", "--model", "agnes-video-2.5", "--reference-video", "https://example.com/v.mp4", "--video-start-seconds", number)

    def test_all_dry_run_commands_avoid_input_output_and_credentials(self):
        commands = [["image", "--prompt", "generate", "--image", "missing.png", "--output", "missing/out.png"],
                    ["video", "--prompt", "generate", "--wait", "--output", "missing/out.mp4"],
                    ["video-status", "--video-id", "known", "--model", "agnes-video-2.5-flash", "--wait", "--output", "missing/out.mp4"]]
        with mock.patch.object(Path, "read_bytes", side_effect=AssertionError("input read forbidden")), \
             mock.patch.object(agnes_media, "execution_config", side_effect=AssertionError("credential read forbidden")), \
             mock.patch.object(agnes_media, "prepare_output", side_effect=AssertionError("output write forbidden")), \
             mock.patch.object(agnes_media, "request_json", side_effect=AssertionError("provider forbidden")):
            for command in commands:
                with contextlib.redirect_stdout(io.StringIO()) as stdout:
                    self.assertEqual(agnes_media.main(command), 0)
                report = json.loads(stdout.getvalue())
                self.assertEqual((report["provider_calls"], report["secrets_read"]), (False, False))

    def test_video_input_requires_explicit_supported_reference_flag(self) -> None:
        result = self.run_cli("video", "--prompt", "Animate", "--video", "input.mp4")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unrecognized arguments", result.stderr)

    def test_old_and_invalid_scalar_parameters_fail_clearly(self):
        cases = [("--seconds", v) for v in ("3", "13", "5.0")]
        cases += [("--n", "2"), ("--seed", "1.5"), ("--aspect-ratio", "2:3"), ("--prompt", " ")]
        cases += [(flag, value) for flag, value in (("--num-frames", "121"), ("--frame-rate", "24"),
                  ("--width", "1280"), ("--height", "720"), ("--num-inference-steps", "30"),
                  ("--negative-prompt", "blur"), ("--keyframe", "https://example.com/a"), ("--model", "agnes-video-v2.0"))]
        cases += [(flag, value) for flag in ("--timeout", "--max-wait", "--poll-interval") for value in ("0", "-1", "nan", "inf")]
        for flags in cases:
            with self.subTest(flags=flags):
                self.invalid("video", *flags)

    def test_completed_video_uses_metadata_url_only(self) -> None:
        expected = "https://example.com/final.mp4"
        self.assertEqual(
            agnes_media.video_result_url(
                {"status": "completed", "metadata": {"url": expected}, "remixed_from_video_id": "wrong"}
            ),
            expected,
        )
        self.assertIsNone(
            agnes_media.video_result_url(
                {"status": "completed", "remixed_from_video_id": "https://example.com/wrong.mp4"}
            )
        )

    def test_output_requires_video_wait(self) -> None:
        result = self.run_cli("video", "--prompt", "Animate", "--output", "result.mp4")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("--output requires --wait", result.stderr)


if __name__ == "__main__":
    unittest.main()
