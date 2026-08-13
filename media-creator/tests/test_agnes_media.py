from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "agnes_media.py"
SPEC = importlib.util.spec_from_file_location("agnes_media", SCRIPT)
assert SPEC and SPEC.loader
agnes_media = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(agnes_media)


class AgnesMediaTests(unittest.TestCase):
    def run_cli(self, *arguments: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [sys.executable, str(SCRIPT), *arguments],
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
        self.assertNotIn("response_format", payload)
        self.assertEqual(payload["extra_body"]["response_format"], "b64_json")
        self.assertEqual(payload["extra_body"]["image"][0], "https://example.com/one.png")
        self.assertTrue(payload["extra_body"]["image"][1].startswith("<data-uri-from:"))

    def test_video_text_image_and_keyframe_payloads(self) -> None:
        text = agnes_media.parse_args(["video", "--prompt", "Move slowly"])
        text_payload = agnes_media.build_video_payload(text)
        self.assertNotIn("image", text_payload)
        self.assertEqual(text_payload["frame_rate"], 24)

        text.frame_rate = 23.5
        self.assertEqual(agnes_media.build_video_payload(text)["frame_rate"], 23.5)

        image = agnes_media.parse_args(
            ["video", "--prompt", "Move slowly", "--image", "https://example.com/start.png"]
        )
        self.assertEqual(
            agnes_media.build_video_payload(image)["image"],
            "https://example.com/start.png",
        )

        keyframes = agnes_media.parse_args(
            [
                "video",
                "--prompt",
                "Transition",
                "--keyframe",
                "https://example.com/one.png",
                "--keyframe",
                "https://example.com/two.png",
            ]
        )
        self.assertEqual(
            agnes_media.build_video_payload(keyframes)["extra_body"],
            {
                "image": ["https://example.com/one.png", "https://example.com/two.png"],
                "mode": "keyframes",
            },
        )

    def test_video_dry_run_does_not_offer_video_input(self) -> None:
        result = self.run_cli("video", "--prompt", "Animate", "--video", "input.mp4")
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("unrecognized arguments", result.stderr)

    def test_video_frame_constraints_fail_clearly(self) -> None:
        for arguments, message in (
            (("--num-frames", "120"), "8n+1"),
            (("--num-frames", "449"), "8n+1"),
            (("--frame-rate", "61"), "between 1 and 60"),
        ):
            with self.subTest(arguments=arguments):
                result = self.run_cli("video", "--prompt", "Animate", *arguments)
                self.assertNotEqual(result.returncode, 0)
                self.assertIn(message, result.stderr)

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
