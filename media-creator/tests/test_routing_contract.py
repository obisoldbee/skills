from __future__ import annotations

import copy
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
BROWSER_ENVELOPE_VALIDATOR = ROOT / "scripts" / "validate_browser_envelope.py"
BROWSER_ENVELOPE_CASES = ROOT / "tests" / "browser-envelope-cases.json"
LOCAL_SKILL_AUDIT = ROOT / "references" / "local-skill-audit.md"
CHECKER_SPEC = importlib.util.spec_from_file_location("media_creator_route_checker", CHECKER)
assert CHECKER_SPEC and CHECKER_SPEC.loader
route_checker = importlib.util.module_from_spec(CHECKER_SPEC)
CHECKER_SPEC.loader.exec_module(route_checker)
VALIDATOR_SPEC = importlib.util.spec_from_file_location(
    "media_creator_validator", VALIDATOR
)
assert VALIDATOR_SPEC and VALIDATOR_SPEC.loader
route_validator = importlib.util.module_from_spec(VALIDATOR_SPEC)
VALIDATOR_SPEC.loader.exec_module(route_validator)


def route_by_id(registry: dict, route_id: str) -> dict:
    return next(route for route in registry["routes"] if route["id"] == route_id)


def set_nested(value: dict, dotted_path: str, replacement: object) -> None:
    parts = dotted_path.split(".")
    target = value
    for part in parts[:-1]:
        target = target[part]
    target[parts[-1]] = replacement


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
            "browser_route_selected_without_visible_task_authority",
            "prompt_or_task_submitted",
        ):
            self.assertIn(excluded, policy["fallback_exclusions"])

    def test_browser_routes_split_provider_execution_from_visible_task_authority(self) -> None:
        contract = self.registry["execution_contract"]
        self.assertEqual(contract["planner"], "originating_main_task")
        self.assertTrue(contract["final_payload"]["required_before_handoff"])
        self.assertEqual(contract["luna_max"]["route"], "luna-max")
        self.assertEqual(contract["luna_max"]["model"], "gpt-5.6-luna")
        self.assertEqual(contract["luna_max"]["reasoning"], "max")
        self.assertEqual(contract["luna_max"]["thread"], "visible")
        self.assertEqual(contract["luna_max"]["surface"], "visible_thread")
        self.assertEqual(contract["luna_max"]["orchestrator"], "project-handoff")
        self.assertEqual(
            contract["luna_max"]["enabled_when"],
            "visible_task_creation_authority_explicit",
        )
        self.assertEqual(
            contract["luna_max"]["created_and_validated_by"],
            "originating_main_task",
        )
        authorization = contract["authorization"]
        provider = authorization["provider_execution_authority"]
        self.assertEqual(
            provider["ordinary_browser_generation_request"],
            "one_bounded_provider_submission",
        )
        self.assertEqual(
            provider["prompt_planning_preview_dry_run"], "not_granted"
        )
        self.assertEqual(provider["does_not_grant"], "visible_task_creation_authority")
        visible = authorization["visible_task_creation_authority"]
        self.assertEqual(visible["ordinary_browser_generation_request"], "not_granted")
        self.assertEqual(
            set(visible["granted_only_by_explicit_request"]),
            {"new_task", "new_thread", "handoff", "luna_visible_task"},
        )
        self.assertFalse(visible["create_thread_without_authority"])
        non_execution = authorization["non_execution_modes"]
        self.assertEqual(
            set(non_execution["modes"]),
            {"prompt", "planning", "preview", "dry_run"},
        )
        self.assertFalse(non_execution["open_browser"])
        self.assertFalse(non_execution["provider_call"])
        self.assertFalse(non_execution["create_thread"])
        decision = authorization["decision"]
        self.assertEqual(
            decision["explicit_visible_task_authority"],
            "create_one_bounded_luna_visible_task",
        )
        self.assertEqual(
            decision["current_task_browser_available"],
            "execute_in_current_task",
        )
        self.assertEqual(
            decision["current_task_browser_unavailable_without_visible_authority"],
            "needs_visible_task_authority",
        )
        self.assertEqual(
            authorization["additional_task_or_submission"],
            "requires_new_authority",
        )

        for route_id in ("chatgpt-web-image", "minimax-web-music"):
            with self.subTest(route_id=route_id):
                route = route_by_id(self.registry, route_id)
                executor = route["executor"]
                self.assertEqual(executor["kind"], "authority_gated_browser_execution")
                current_task = executor["current_task"]
                self.assertEqual(current_task["kind"], "verified_browser_executor")
                self.assertEqual(current_task["preferred_command"], "ego-browser")
                self.assertFalse(current_task["requires_visible_task_creation_authority"])
                visible_task = executor["visible_task"]
                self.assertEqual(visible_task["kind"], "project_handoff_visible_thread")
                self.assertEqual(visible_task["orchestrator"], "project-handoff")
                self.assertEqual(visible_task["route"], "luna-max")
                self.assertEqual(visible_task["model"], "gpt-5.6-luna")
                self.assertEqual(visible_task["reasoning"], "max")
                self.assertEqual(visible_task["surface"], "visible_thread")
                self.assertTrue(visible_task["requires_visible_task_creation_authority"])
                self.assertEqual(visible_task["worker"]["command"], "ego-browser")
                handoff = route["browser_handoff"]
                self.assertEqual(
                    handoff["required_when"],
                    "visible_task_creation_authority_explicit",
                )
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
                self.assertFalse(handoff["ordinary_generation_request_grants_creation"])
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
        current_task = contract["current_task_browser"]
        self.assertEqual(current_task["capability"], "runtime_verified_browser_executor")
        self.assertEqual(current_task["execution_role"], "browser_executor")
        self.assertEqual(current_task["handoff_depth"], 0)
        self.assertFalse(current_task["recursive_dispatch"])
        self.assertEqual(current_task["action"], "execute_envelope_in_current_task")
        cross_harness = contract["cross_harness"]
        self.assertEqual(
            set(cross_harness["current_task_execution_requires"]),
            {"provider_execution_authority", "verified_browser_executor_capability"},
        )
        self.assertEqual(
            set(cross_harness["visible_task_creation_requires"]),
            {
                "explicit_visible_task_creation_authority",
                "project_handoff_visible_task_surface",
            },
        )
        self.assertTrue(cross_harness["requirements_are_conjunctive"])
        self.assertEqual(cross_harness["preferred_local_executor"], "ego-browser")
        self.assertFalse(cross_harness["is_fallback_after_luna_creation_failure"])
        self.assertFalse(cross_harness["explicit_luna_request_may_downgrade"])
        submission = contract["submission"]
        self.assertEqual(submission["pre_submission_manual_or_login_check"], "handoff_and_pause")
        self.assertEqual(submission["nonzero_or_ambiguous_cost"], "pause_before_submission")
        self.assertFalse(submission["duplicate_submission"])
        self.assertFalse(submission["post_submission_provider_switch"])
        self.assertEqual(
            submission["download_retry"], "same_submitted_result_only"
        )

    def test_twenty_browser_envelopes_jointly_validate_authority_and_execution(self) -> None:
        fixture = json.loads(BROWSER_ENVELOPE_CASES.read_text(encoding="utf-8"))
        bases = fixture["bases"]
        cases = fixture["cases"]
        self.assertEqual(3, len(bases))
        self.assertEqual(20, len(cases))

        with tempfile.TemporaryDirectory() as temporary:
            for case in cases:
                with self.subTest(case=case["id"]):
                    envelope = copy.deepcopy(bases[case["base"]])
                    for dotted_path, replacement in case.get("set", {}).items():
                        set_nested(envelope, dotted_path, replacement)
                    envelope_path = Path(temporary) / f"{case['id']}.json"
                    envelope_path.write_text(
                        json.dumps(envelope, ensure_ascii=False), encoding="utf-8"
                    )
                    process = subprocess.run(
                        [
                            sys.executable,
                            "-B",
                            str(BROWSER_ENVELOPE_VALIDATOR),
                            str(envelope_path),
                        ],
                        text=True,
                        capture_output=True,
                        check=False,
                    )
                    result = json.loads(process.stdout)
                    expected = case["expected"]
                    self.assertEqual(expected["valid"], result["valid"], result)
                    self.assertEqual(0 if expected["valid"] else 2, process.returncode)
                    self.assertFalse(result["provider_calls"])
                    self.assertFalse(result["secrets_read"])
                    if not expected["valid"]:
                        self.assertTrue(
                            any(
                                expected["error_contains"] in error
                                for error in result["errors"]
                            ),
                            result["errors"],
                        )

    def test_validator_rejects_task_authority_expansion_and_execution_side_effects(self) -> None:
        mutations = []

        ordinary_grants_task = copy.deepcopy(self.registry)
        ordinary_grants_task["execution_contract"]["authorization"][
            "visible_task_creation_authority"
        ]["ordinary_browser_generation_request"] = "granted"
        mutations.append((ordinary_grants_task, "explicit visible-task creation authority"))

        preview_opens_browser = copy.deepcopy(self.registry)
        preview_opens_browser["execution_contract"]["authorization"][
            "non_execution_modes"
        ]["open_browser"] = True
        mutations.append((preview_opens_browser, "no execution side effects"))

        recursive_worker = copy.deepcopy(self.registry)
        recursive_worker["execution_contract"]["worker"]["recursive_dispatch"] = True
        mutations.append((recursive_worker, "forbid recursive handoff"))

        browser_route_auto_creates = copy.deepcopy(self.registry)
        route_by_id(browser_route_auto_creates, "chatgpt-web-image")[
            "browser_handoff"
        ]["ordinary_generation_request_grants_creation"] = True
        mutations.append((browser_route_auto_creates, "handoff contract is invalid"))

        wrong_creator = copy.deepcopy(self.registry)
        wrong_creator["execution_contract"]["luna_max"][
            "created_and_validated_by"
        ] = "browser_worker"
        mutations.append((wrong_creator, "exact visible luna-max thread"))

        wrong_download_retry = copy.deepcopy(self.registry)
        wrong_download_retry["execution_contract"]["submission"][
            "download_retry"
        ] = "resubmit_or_switch_provider"
        mutations.append((wrong_download_retry, "prevent duplicates/switches"))

        planning_missing = copy.deepcopy(self.registry)
        planning_missing["execution_contract"]["authorization"][
            "non_execution_modes"
        ]["modes"].remove("planning")
        mutations.append((planning_missing, "planning, preview"))

        for registry, expected_error in mutations:
            with self.subTest(expected_error=expected_error):
                errors: list[str] = []
                route_validator.validate_registry(registry, errors)
                self.assertTrue(
                    any(expected_error in error for error in errors),
                    errors,
                )

    def test_browser_contract_docs_preserve_split_authority_and_stop_state(self) -> None:
        paths = (
            ROOT / "SKILL.md",
            ROOT / "references" / "browser-handoff-envelope.md",
            ROOT / "references" / "chatgpt-web-image.md",
            ROOT / "references" / "minimax-web-music.md",
            ROOT / "references" / "routing-policy.md",
        )
        for path in paths:
            with self.subTest(path=path.name):
                text = path.read_text(encoding="utf-8")
                self.assertIn("provider_execution_authority", text)
                self.assertIn("visible_task_creation_authority", text)
                self.assertIn("needs_visible_task_authority", text)

        skill = paths[0].read_text(encoding="utf-8")
        for marker in ("prompt", "规划", "preview", "dry-run", "递归"):
            self.assertIn(marker, skill)
        self.assertIn("scripts/validate_browser_envelope.py", skill)
        envelope_contract = paths[1].read_text(encoding="utf-8")
        for marker in (
            "request_authority",
            "submission_limit",
            "created_and_validated_by",
            "same_submitted_result_only",
            "side_effects",
        ):
            self.assertIn(marker, envelope_contract)

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
        self.assertEqual(
            preconditions["current_task_browser_capability"], "runtime_verified"
        )
        self.assertEqual(
            preconditions["visible_task_dispatch"], "explicit_authority_only"
        )

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

    def test_agnes_registry_rejects_model_and_parameter_drift(self) -> None:
        errors = []
        route_validator.validate_agnes_contract(self.registry, errors)
        self.assertEqual(errors, [])
        mutations = (
            ("image", "model", "agnes-image-2.1-flash"),
            ("video", "model", "agnes-video-v2.0"),
            ("contract", "automatic_model_switch", True),
            ("contract", "modes", ["text", "keyframes", "reference"]),
            ("contract", "seconds", list(range(4, 13))),
            ("contract", "query_keys", ["task_id", "model_name"]),
            ("contract", "n", 2),
            ("contract", "aspect_ratios", ["2:3"]),
            ("flash", "sizes", ["720P", "1080P"]),
            ("flash", "max_reference_images", 8),
            ("flash", "max_reference_videos", 1),
            ("standard", "selection", "automatic_fallback"),
            ("standard", "max_reference_audios", 4),
            ("capabilities", "reference_video", True),
            ("video", "model_variants", []),
            ("video", "request_contract", None),
        )
        for section, key, value in mutations:
            with self.subTest(section=section, key=key):
                registry = copy.deepcopy(self.registry)
                video = route_by_id(registry, "agnes-video")
                targets = {"image": route_by_id(registry, "agnes-image"), "video": video,
                           "contract": video["request_contract"], "flash": video["model_variants"]["agnes-video-2.5-flash"],
                           "standard": video["model_variants"]["agnes-video-2.5"], "capabilities": video["capabilities"]["video"]}
                targets[section][key] = value
                errors = []
                route_validator.validate_agnes_contract(registry, errors)
                self.assertTrue(errors)

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
