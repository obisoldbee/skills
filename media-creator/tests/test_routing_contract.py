from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
ROUTES = ROOT / "config" / "routes.json"
CHECKER = ROOT / "scripts" / "check_routes.py"
VALIDATOR = ROOT / "scripts" / "validate_skill.py"
LOCAL_SKILL_AUDIT = ROOT / "references" / "local-skill-audit.md"


def route_by_id(registry: dict, route_id: str) -> dict:
    return next(route for route in registry["routes"] if route["id"] == route_id)


class RoutingContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.registry = json.loads(ROUTES.read_text(encoding="utf-8"))

    def test_codex_ordinary_image_generation_stays_native(self) -> None:
        policy = self.registry["scope"]["codex_ordinary_image_generation"]
        self.assertEqual(policy["action"], "exclude")
        self.assertEqual(policy["owner"], "imagegen")

    def test_non_codex_text_to_image_falls_back_before_submission_only(self) -> None:
        policy = self.registry["policies"]["non_codex_text_to_image"]
        self.assertEqual(policy["primary"], "chatgpt-web-image")
        self.assertEqual(policy["pre_submission_fallback"], "minimax-mmx-image")
        self.assertEqual(policy["fallback_phase"], "before_submission_only")
        self.assertEqual(policy["agnes_selection"], "explicit_or_user_confirmed")

    def test_chatgpt_web_requires_darwin_ego_and_runtime_login(self) -> None:
        route = route_by_id(self.registry, "chatgpt-web-image")
        preconditions = route["runtime_preconditions"]
        self.assertEqual(preconditions["platform"], "Darwin")
        self.assertTrue(preconditions["ego_browser"])
        self.assertTrue(preconditions["chatgpt_login"])
        self.assertEqual(preconditions["login_check"], "runtime_only")

    def test_image_capability_boundaries(self) -> None:
        mmx = route_by_id(self.registry, "minimax-mmx-image")["capabilities"]["image"]
        self.assertTrue(mmx["text_to_image"])
        self.assertTrue(mmx["subject_reference"])
        self.assertFalse(mmx["image_to_image"])
        self.assertFalse(mmx["multi_image"])

        agnes = route_by_id(self.registry, "agnes-image")
        self.assertEqual(agnes["selection"], "explicit_or_user_confirmed")
        self.assertTrue(agnes["capabilities"]["image"]["text_to_image"])
        self.assertTrue(agnes["capabilities"]["image"]["image_to_image"])
        self.assertTrue(agnes["capabilities"]["image"]["multi_image"])

    def test_video_capability_boundaries(self) -> None:
        mmx = route_by_id(self.registry, "minimax-mmx-video")["capabilities"]["video"]
        self.assertTrue(mmx["reference_video"])
        self.assertFalse(mmx["precise_video_edit"])

        agnes = route_by_id(self.registry, "agnes-video")["capabilities"]["video"]
        self.assertFalse(agnes["video_to_video"])

    def test_video_quota_has_three_states_and_h3_is_not_authoritative(self) -> None:
        policy = self.registry["policies"]["minimax_video_quota"]
        self.assertEqual(
            set(policy["states"]),
            {"known_positive", "known_exhausted", "unknown"},
        )
        self.assertEqual(policy["states"]["known_positive"], "continue_mmx")
        self.assertEqual(policy["states"]["known_exhausted"], "ask_user_mmx_or_agnes")
        self.assertEqual(policy["states"]["unknown"], "ask_user_mmx_or_agnes")
        self.assertFalse(policy["h3_quota_authoritative"])

    def test_local_check_reports_metadata_without_reading_secret_or_login(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            temporary_path = Path(temporary)
            home = temporary_path / "home"
            bin_dir = temporary_path / "bin"
            env_path = home / ".codex" / "secrets" / "agnes.env"
            env_path.parent.mkdir(parents=True)
            secret_marker = "never-print-" + "this-secret-value"
            env_path.write_text("AGNES_API_" + "KEY=" + secret_marker + "\n", encoding="utf-8")
            env_path.chmod(0o600)
            bin_dir.mkdir()
            for command in ("ego-browser", "mmx"):
                executable = bin_dir / command
                executable.write_text("#!/bin/sh\nexit 99\n", encoding="utf-8")
                executable.chmod(0o755)

            environment = os.environ.copy()
            environment["PATH"] = str(bin_dir)
            result = subprocess.run(
                [sys.executable, str(CHECKER), "--home", str(home)],
                text=True,
                capture_output=True,
                check=False,
                env=environment,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertNotIn(secret_marker, result.stdout)
            report = json.loads(result.stdout)
            self.assertFalse(report["provider_calls"])
            self.assertFalse(report["secrets_read"])
            self.assertFalse(report["chatgpt_login_checked"])
            self.assertTrue(report["executors"]["ego_browser"]["present"])
            self.assertTrue(report["executors"]["mmx"]["present"])
            self.assertFalse(report["executors"]["ego_browser"]["invoked"])
            self.assertFalse(report["executors"]["mmx"]["invoked"])
            self.assertTrue(report["agnes_env"]["exists"])
            self.assertTrue(report["agnes_env"]["private_permissions"])
            self.assertEqual(report["agnes_env"]["path"], "~/.codex/secrets/agnes.env")

    def test_static_validator_accepts_package(self) -> None:
        result = subprocess.run(
            [sys.executable, str(VALIDATOR)],
            text=True,
            capture_output=True,
            check=False,
        )
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        report = json.loads(result.stdout)
        self.assertTrue(report["valid"])
        self.assertFalse(report["provider_calls"])
        self.assertFalse(report["secrets_read"])

    def test_other_local_generators_remain_inventory_only(self) -> None:
        audit = LOCAL_SKILL_AUDIT.read_text(encoding="utf-8")
        for marker in (
            "byted-seedream-image-generate",
            "byted-seedance-video-generate",
            "media-generation",
            "story-video-generator",
            "HyperFrames",
            "HeyGen",
            "observed_not_routed",
        ):
            self.assertIn(marker, audit)


if __name__ == "__main__":
    unittest.main()
