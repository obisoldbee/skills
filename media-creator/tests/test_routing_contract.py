from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
ROUTES = ROOT / "config" / "routes.json"
CHECKER = ROOT / "scripts" / "check_routes.py"
VALIDATOR = ROOT / "scripts" / "validate_skill.py"
LOCAL_SKILL_AUDIT = ROOT / "references" / "local-skill-audit.md"
CHECKER_SPEC = importlib.util.spec_from_file_location("media_creator_route_checker", CHECKER)
assert CHECKER_SPEC and CHECKER_SPEC.loader
route_checker = importlib.util.module_from_spec(CHECKER_SPEC)
CHECKER_SPEC.loader.exec_module(route_checker)


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
        self.assertEqual(policy["post_submission_cross_provider_fallback"], "none")
        for excluded in (
            "login_or_manual_check_required",
            "luna_creation_failed",
            "visible_task_handoff_failed",
            "explicit_luna_request",
            "prompt_or_task_submitted",
        ):
            self.assertIn(excluded, policy["fallback_exclusions"])

    def test_browser_routes_require_main_payload_luna_max_visible_thread_and_ego(self) -> None:
        contract = self.registry["execution_contract"]
        self.assertEqual(contract["planner"], "originating_main_task")
        self.assertTrue(contract["final_payload"]["required_before_handoff"])
        self.assertEqual(contract["luna_max"]["route"], "luna-max")
        self.assertEqual(contract["luna_max"]["model"], "gpt-5.6-luna")
        self.assertEqual(contract["luna_max"]["reasoning"], "max")
        self.assertEqual(contract["luna_max"]["thread"], "visible")
        self.assertEqual(contract["luna_max"]["surface"], "visible_thread")
        self.assertEqual(contract["luna_max"]["orchestrator"], "project-handoff")
        authorization = contract["authorization"]
        self.assertEqual(
            authorization["selected_browser_generation_request"],
            "one_bounded_luna_visible_task",
        )
        self.assertEqual(authorization["plan_or_prompt_only_request"], "no_dispatch")
        self.assertEqual(
            authorization["additional_task_or_submission"],
            "requires_new_authority",
        )

        for route_id in ("chatgpt-web-image", "minimax-web-music"):
            with self.subTest(route_id=route_id):
                route = route_by_id(self.registry, route_id)
                executor = route["executor"]
                self.assertEqual(executor["kind"], "project_handoff_visible_thread")
                self.assertEqual(executor["orchestrator"], "project-handoff")
                self.assertEqual(executor["route"], "luna-max")
                self.assertEqual(executor["model"], "gpt-5.6-luna")
                self.assertEqual(executor["reasoning"], "max")
                self.assertEqual(executor["surface"], "visible_thread")
                self.assertEqual(executor["worker"]["command"], "ego-browser")
                handoff = route["browser_handoff"]
                self.assertTrue(handoff["required_when_visible_task_surface_available"])
                self.assertEqual(handoff["orchestrator"], "project-handoff")
                self.assertEqual(handoff["luna_route"], "luna-max")
                self.assertEqual(handoff["model"], "gpt-5.6-luna")
                self.assertEqual(handoff["reasoning"], "max")
                self.assertEqual(handoff["thread"], "visible")
                self.assertEqual(handoff["surface"], "visible_thread")
                self.assertEqual(handoff["worker_executor"], "ego-browser")
                self.assertEqual(handoff["execution_role"], "browser_worker")
                self.assertEqual(handoff["handoff_depth"], 1)
                self.assertFalse(handoff["recursive_dispatch"])
                self.assertEqual(handoff["payload_author"], "originating_main_task")
                self.assertFalse(handoff["worker_creative_rewrite"])
                self.assertFalse(route["payload"]["worker_creative_rewrite"])

    def test_browser_worker_cannot_recurse_or_downgrade_explicit_luna(self) -> None:
        contract = self.registry["execution_contract"]
        worker = contract["worker"]
        self.assertEqual(worker["execution_role"], "browser_worker")
        self.assertEqual(worker["handoff_depth"], 1)
        self.assertFalse(worker["recursive_dispatch"])
        self.assertEqual(worker["action"], "execute_envelope_directly")
        cross_harness = contract["cross_harness"]
        self.assertTrue(cross_harness["local_execution_requires_all"])
        self.assertEqual(cross_harness["preferred_local_executor"], "ego-browser")
        self.assertFalse(cross_harness["is_fallback_after_luna_creation_failure"])
        self.assertFalse(cross_harness["explicit_luna_request_may_downgrade"])
        submission = contract["submission"]
        self.assertEqual(submission["pre_submission_manual_or_login_check"], "handoff_and_pause")
        self.assertEqual(submission["nonzero_or_ambiguous_cost"], "pause_before_submission")
        self.assertFalse(submission["duplicate_submission"])
        self.assertFalse(submission["post_submission_provider_switch"])

    def test_chatgpt_payload_includes_output_path(self) -> None:
        route = route_by_id(self.registry, "chatgpt-web-image")
        self.assertEqual(
            set(route["payload"]["required_before_handoff"]),
            {"final_image_prompt", "inputs", "output_path"},
        )

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

    def test_minimax_web_music_is_generic_default_and_has_bounded_completion(self) -> None:
        policy = self.registry["policies"]["music"]
        self.assertEqual(policy["primary"], "minimax-web-music")
        self.assertEqual(policy["default_count"], 1)
        self.assertEqual(policy["web_music_failure"], "stop_and_report")
        self.assertEqual(policy["post_submission_fallback"], "none")
        self.assertEqual(policy["mmx_music_api"], "explicit_and_runtime_eligibility_gated")

        route = route_by_id(self.registry, "minimax-web-music")
        self.assertEqual(route["url"], "https://www.minimaxi.com/audio/music")
        self.assertEqual(route["selection"], "default_for_generic_music")
        self.assertEqual(route["payload"]["default_count"], 1)
        self.assertEqual(
            set(route["payload"]["required_before_handoff"]),
            {"title", "mode", "style_prompt", "lyrics", "count", "output_path"},
        )
        capabilities = route["capabilities"]["music"]
        self.assertTrue(capabilities["original_song"])
        self.assertTrue(capabilities["instrumental_bgm"])
        self.assertFalse(capabilities["voice_cloning"])
        self.assertFalse(capabilities["reference_audio_editing"])
        self.assertFalse(capabilities["cover"])
        self.assertFalse(capabilities["exact_duration"])
        self.assertEqual(capabilities["commercial_license"], "not_claimed")
        self.assertEqual(route["completion"]["wait_for"], "full_completion")
        self.assertEqual(route["completion"]["download_format"], "mp3")
        self.assertEqual(
            set(route["completion"]["verify"]),
            {"regular_file", "nonzero_size", "mp3_type", "sha256"},
        )

    def test_mmx_music_is_legacy_explicit_and_eligibility_gated(self) -> None:
        route = route_by_id(self.registry, "minimax-mmx-music")
        self.assertEqual(route["status"], "legacy_if_explicit_and_eligible")
        self.assertEqual(route["selection"], "explicit_only_after_runtime_eligibility_confirmation")
        eligibility = route["eligibility"]
        self.assertEqual(eligibility["official_notice_date"], "2026-08-20")
        self.assertEqual(eligibility["new_users_paid_music_api"], "not_offered")
        self.assertEqual(
            eligibility["historical_paid_api_users"],
            "may_continue_after_runtime_confirmation",
        )
        self.assertEqual(eligibility["free_music_models"], "stopped")
        self.assertEqual(eligibility["local_cli_help"], "interface_evidence_only")
        self.assertEqual(self.registry["policies"]["music"]["primary"], "minimax-web-music")

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
                executable = bin_dir / (f"{command}.cmd" if os.name == "nt" else command)
                placeholder = "@exit /b 99\r\n" if os.name == "nt" else "#!/bin/sh\nexit 99\n"
                executable.write_text(placeholder, encoding="utf-8")
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
            if os.name == "nt":
                self.assertIsNone(report["agnes_env"]["private_permissions"])
                self.assertIsNone(report["agnes_env"]["owner_matches_process"])
            else:
                self.assertTrue(report["agnes_env"]["private_permissions"])
                self.assertTrue(report["agnes_env"]["owner_matches_process"])
            self.assertEqual(report["agnes_env"]["path"], "~/.codex/secrets/agnes.env")

    def test_missing_posix_identity_reports_unverified_metadata(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "agnes.env"
            path.write_text("AGNES_API_KEY=placeholder\n", encoding="utf-8")
            with mock.patch.object(route_checker.os, "getuid", None, create=True):
                report = route_checker.file_metadata(path, "agnes.env")
            self.assertIsNone(report["private_permissions"])
            self.assertIsNone(report["owner_matches_process"])

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
