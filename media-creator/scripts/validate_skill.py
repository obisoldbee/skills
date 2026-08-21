#!/usr/bin/env python3
"""Statically validate the portable media-creator package."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any


DEFAULT_ROOT = Path(__file__).resolve().parents[1]
REQUIRED_FILES = {
    "SKILL.md",
    "agents/openai.yaml",
    "config/routes.json",
    "references/browser-handoff-envelope.md",
    "references/chatgpt-web-image.md",
    "references/local-skill-audit.md",
    "references/minimax-web-music.md",
    "references/mmx.md",
    "references/routing-policy.md",
    "scripts/check_routes.py",
    "scripts/validate_skill.py",
}
TEXT_SUFFIXES = {".md", ".json", ".yaml", ".yml", ".py", ".sh", ".txt"}
SECRET_FILE_SUFFIXES = {".env", ".key", ".pem", ".p12", ".pfx"}
SECRET_ASSIGNMENT = re.compile(
    r"(?im)^\s*(?:export\s+)?(?:AGNES|MINIMAX|OPENAI)_[A-Z0-9_]*(?:KEY|TOKEN)\s*=\s*"
    r'''(?!\s*(?:$|<[^>]+>|\$\{[^}]+\}|REDACTED\b|YOUR_[A-Z0-9_]+\b))["']?[^\s"']{8,}'''
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=DEFAULT_ROOT)
    return parser.parse_args()


def load_registry(root: Path, errors: list[str]) -> dict[str, Any]:
    path = root / "config/routes.json"
    if not path.is_file():
        return {}
    try:
        registry = json.loads(path.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        errors.append(f"invalid route registry: {exc}")
        return {}
    if not isinstance(registry, dict):
        errors.append("route registry must be a JSON object")
        return {}
    return registry


def route_by_id(registry: dict[str, Any], route_id: str) -> dict[str, Any]:
    routes = registry.get("routes", [])
    if not isinstance(routes, list):
        return {}
    return next(
        (route for route in routes if isinstance(route, dict) and route.get("id") == route_id),
        {},
    )


def validate_files(root: Path, errors: list[str]) -> None:
    for relative in sorted(REQUIRED_FILES):
        if not (root / relative).is_file():
            errors.append(f"missing required file: {relative}")

    nested_skills = [
        path.relative_to(root).as_posix()
        for path in root.rglob("SKILL.md")
        if path.resolve() != (root / "SKILL.md").resolve()
    ]
    if nested_skills:
        errors.append(f"embedded Skill copies are forbidden: {sorted(nested_skills)}")

    secret_files = [
        path.relative_to(root).as_posix()
        for path in root.rglob("*")
        if path.is_file() and path.suffix.lower() in SECRET_FILE_SUFFIXES
    ]
    if secret_files:
        errors.append(f"credential files must not be stored in package: {sorted(secret_files)}")

    personal_prefix = "/" + "Users/"
    validator = Path(__file__).resolve()
    for path in root.rglob("*"):
        if not path.is_file() or path.suffix.lower() not in TEXT_SUFFIXES:
            continue
        if path.resolve() == validator:
            continue
        try:
            text = path.read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue
        relative = path.relative_to(root).as_posix()
        if personal_prefix in text:
            errors.append(f"personal absolute path found in {relative}")
        if SECRET_ASSIGNMENT.search(text):
            errors.append(f"possible secret value found in {relative}")

    forbidden_mmx_paths = []
    for path in root.rglob("*"):
        relative_parts = {part.lower() for part in path.relative_to(root).parts}
        if relative_parts & {"mmx-cli", "mmx-h3-video", "h3-video"}:
            forbidden_mmx_paths.append(path.relative_to(root).as_posix())
    if forbidden_mmx_paths:
        errors.append(f"vendored MMX Skill copy is forbidden: {sorted(forbidden_mmx_paths)}")


def validate_registry(registry: dict[str, Any], errors: list[str]) -> None:
    if registry.get("schema") != "media-creator-routes/v1":
        errors.append("route registry schema must be media-creator-routes/v1")

    scope = registry.get("scope", {})
    codex = scope.get("codex_ordinary_image_generation", {}) if isinstance(scope, dict) else {}
    if codex.get("action") != "exclude" or codex.get("owner") != "imagegen":
        errors.append("ordinary Codex image generation must be excluded and owned by imagegen")

    execution = registry.get("execution_contract", {})
    if not isinstance(execution, dict):
        errors.append("execution_contract must be an object")
        execution = {}
    if execution.get("planner") != "originating_main_task":
        errors.append("browser routes must keep creative planning in the originating main task")
    final_payload = execution.get("final_payload", {})
    if (
        not isinstance(final_payload, dict)
        or final_payload.get("required_before_handoff") is not True
        or final_payload.get("creative_authority") != "originating_main_task"
        or final_payload.get("worker_mutation") != "mechanical_mapping_only"
    ):
        errors.append("browser routes must require a main-authored final payload")
    luna_max = execution.get("luna_max", {})
    if (
        not isinstance(luna_max, dict)
        or luna_max.get("route") != "luna-max"
        or luna_max.get("model") != "gpt-5.6-luna"
        or luna_max.get("reasoning") != "max"
        or luna_max.get("thread") != "visible"
        or luna_max.get("surface") != "visible_thread"
        or luna_max.get("orchestrator") != "project-handoff"
    ):
        errors.append("visible browser routes must use the exact visible luna-max thread")
    authorization = execution.get("authorization", {})
    if (
        not isinstance(authorization, dict)
        or authorization.get("selected_browser_generation_request")
        != "one_bounded_luna_visible_task"
        or authorization.get("plan_or_prompt_only_request") != "no_dispatch"
        or authorization.get("additional_task_or_submission") != "requires_new_authority"
    ):
        errors.append("browser dispatch authority must be bounded to one selected generation task")
    worker = execution.get("worker", {})
    if (
        not isinstance(worker, dict)
        or worker.get("executor") != "ego-browser"
        or worker.get("execution_role") != "browser_worker"
        or worker.get("handoff_depth") != 1
        or worker.get("recursive_dispatch") is not False
        or worker.get("action") != "execute_envelope_directly"
    ):
        errors.append("browser worker contract must forbid recursive handoff")
    cross_harness = execution.get("cross_harness", {})
    if (
        not isinstance(cross_harness, dict)
        or cross_harness.get("local_execution_requires_all") is not True
        or cross_harness.get("preferred_local_executor") != "ego-browser"
        or cross_harness.get("is_fallback_after_luna_creation_failure") is not False
        or cross_harness.get("explicit_luna_request_may_downgrade") is not False
    ):
        errors.append("cross-Harness browser execution must not downgrade a Luna request")
    submission = execution.get("submission", {})
    if (
        not isinstance(submission, dict)
        or submission.get("pre_submission_manual_or_login_check") != "handoff_and_pause"
        or submission.get("nonzero_or_ambiguous_cost") != "pause_before_submission"
        or submission.get("duplicate_submission") is not False
        or submission.get("post_submission_provider_switch") is not False
    ):
        errors.append("browser submission contract must pause safely and prevent duplicates/switches")

    policies = registry.get("policies", {})
    text_policy = policies.get("non_codex_text_to_image", {}) if isinstance(policies, dict) else {}
    if (
        text_policy.get("primary") != "chatgpt-web-image"
        or text_policy.get("pre_submission_fallback") != "minimax-mmx-image"
        or text_policy.get("fallback_phase") != "before_submission_only"
        or text_policy.get("agnes_selection") != "explicit_or_user_confirmed"
        or text_policy.get("post_submission_cross_provider_fallback") != "none"
    ):
        errors.append("non-Codex text-to-image priority or fallback policy is invalid")
    fallback_exclusions = text_policy.get("fallback_exclusions", [])
    if (
        "luna_creation_failed" not in fallback_exclusions
        or "visible_task_handoff_failed" not in fallback_exclusions
        or "explicit_luna_request" not in fallback_exclusions
        or "login_or_manual_check_required" not in fallback_exclusions
    ):
        errors.append("ChatGPT Web fallback must exclude Luna failure and login/manual handoff states")

    routes = registry.get("routes", [])
    if not isinstance(routes, list):
        errors.append("routes must be a list")
        routes = []
    ids = [route.get("id") for route in routes if isinstance(route, dict)]
    if len(ids) != len(set(ids)):
        errors.append("route ids must be unique")

    chatgpt = route_by_id(registry, "chatgpt-web-image")
    chatgpt_preconditions = chatgpt.get("runtime_preconditions", {})
    if (
        chatgpt_preconditions.get("platform") != "Darwin"
        or chatgpt_preconditions.get("ego_browser") is not True
        or chatgpt_preconditions.get("chatgpt_login") is not True
        or chatgpt_preconditions.get("login_check") != "runtime_only"
    ):
        errors.append("ChatGPT Web must require Darwin, ego-browser, and a runtime-confirmed login")

    browser_route_ids = ("chatgpt-web-image", "minimax-web-music")
    for route_id in browser_route_ids:
        route = route_by_id(registry, route_id)
        executor = route.get("executor", {})
        worker_executor = executor.get("worker", {})
        handoff = route.get("browser_handoff", {})
        payload = route.get("payload", {})
        if (
            executor.get("kind") != "project_handoff_visible_thread"
            or executor.get("orchestrator") != "project-handoff"
            or executor.get("route") != "luna-max"
            or executor.get("model") != "gpt-5.6-luna"
            or executor.get("reasoning") != "max"
            or executor.get("surface") != "visible_thread"
            or worker_executor.get("kind") != "external_browser_cli"
            or worker_executor.get("command") != "ego-browser"
            or worker_executor.get("vendored") is not False
        ):
            errors.append(f"browser route executor must be project-handoff -> Luna -> ego-browser: {route_id}")
        if (
            handoff.get("required_when_visible_task_surface_available") is not True
            or handoff.get("orchestrator") != "project-handoff"
            or handoff.get("luna_route") != "luna-max"
            or handoff.get("model") != "gpt-5.6-luna"
            or handoff.get("reasoning") != "max"
            or handoff.get("thread") != "visible"
            or handoff.get("surface") != "visible_thread"
            or handoff.get("worker_executor") != "ego-browser"
            or handoff.get("execution_role") != "browser_worker"
            or handoff.get("handoff_depth") != 1
            or handoff.get("recursive_dispatch") is not False
            or handoff.get("payload_author") != "originating_main_task"
            or handoff.get("worker_creative_rewrite") is not False
        ):
            errors.append(f"browser route handoff contract is invalid: {route_id}")
        if (
            not isinstance(payload.get("required_before_handoff"), list)
            or payload.get("worker_creative_rewrite") is not False
        ):
            errors.append(f"browser route must require a non-rewritten final payload: {route_id}")

    chatgpt_payload = route_by_id(registry, "chatgpt-web-image").get("payload", {})
    if not {"final_image_prompt", "inputs", "output_path"}.issubset(
        chatgpt_payload.get("required_before_handoff", [])
    ):
        errors.append("ChatGPT Web payload must include final prompt, inputs, and output path")

    music_policy = policies.get("music", {}) if isinstance(policies, dict) else {}
    if (
        not isinstance(music_policy, dict)
        or music_policy.get("primary") != "minimax-web-music"
        or music_policy.get("default_count") != 1
        or music_policy.get("web_music_failure") != "stop_and_report"
        or music_policy.get("post_submission_fallback") != "none"
        or music_policy.get("mmx_music_api") != "explicit_and_runtime_eligibility_gated"
    ):
        errors.append("MiniMax Web Music must be the generic music default without MMX fallback")

    web_music = route_by_id(registry, "minimax-web-music")
    if (
        web_music.get("provider") != "minimax_web"
        or web_music.get("selection") != "default_for_generic_music"
        or web_music.get("url") != "https://www.minimaxi.com/audio/music"
    ):
        errors.append("MiniMax Web Music route identity or default selection is invalid")
    web_preconditions = web_music.get("runtime_preconditions", {})
    if (
        web_preconditions.get("platform") != "Darwin"
        or web_preconditions.get("ego_browser") is not True
        or web_preconditions.get("minimax_web_login") is not True
        or web_preconditions.get("visible_task_dispatch") != "required_when_available"
    ):
        errors.append("MiniMax Web Music must require eligible macOS/ego-browser runtime conditions")
    web_payload = web_music.get("payload", {})
    if (
        web_payload.get("default_count") != 1
        or not {
            "title",
            "mode",
            "style_prompt",
            "lyrics",
            "count",
            "output_path",
        }.issubset(web_payload.get("required_before_handoff", []))
    ):
        errors.append("MiniMax Web Music payload fields or default count are incomplete")
    web_capabilities = web_music.get("capabilities", {}).get("music", {})
    if (
        web_capabilities.get("original_song") is not True
        or web_capabilities.get("instrumental_bgm") is not True
        or web_capabilities.get("voice_cloning") is not False
        or web_capabilities.get("reference_audio_editing") is not False
        or web_capabilities.get("cover") is not False
        or web_capabilities.get("exact_duration") is not False
        or web_capabilities.get("commercial_license") != "not_claimed"
    ):
        errors.append("MiniMax Web Music capability claims exceed the observed contract")
    completion = web_music.get("completion", {})
    if (
        completion.get("wait_for") != "full_completion"
        or completion.get("download_format") != "mp3"
        or not {"regular_file", "nonzero_size", "mp3_type", "sha256"}.issubset(completion.get("verify", []))
    ):
        errors.append("MiniMax Web Music must wait for and verify a downloaded MP3")

    mmx_music = route_by_id(registry, "minimax-mmx-music")
    eligibility = mmx_music.get("eligibility", {})
    if (
        mmx_music.get("status") != "legacy_if_explicit_and_eligible"
        or mmx_music.get("selection") != "explicit_only_after_runtime_eligibility_confirmation"
        or eligibility.get("official_notice_date") != "2026-08-20"
        or eligibility.get("new_users_paid_music_api") != "not_offered"
        or eligibility.get("historical_paid_api_users") != "may_continue_after_runtime_confirmation"
        or eligibility.get("free_music_models") != "stopped"
        or eligibility.get("local_cli_help") != "interface_evidence_only"
    ):
        errors.append("MMX music API must be legacy, explicit, and runtime eligibility-gated")

    mmx_image = route_by_id(registry, "minimax-mmx-image")
    mmx_image_caps = mmx_image.get("capabilities", {}).get("image", {})
    if mmx_image_caps.get("image_to_image") is not False or mmx_image_caps.get("multi_image") is not False:
        errors.append("MMX image route must reject general image-to-image and multi-image requests")

    agnes_image = route_by_id(registry, "agnes-image")
    agnes_image_caps = agnes_image.get("capabilities", {}).get("image", {})
    if not all(agnes_image_caps.get(name) is True for name in ("text_to_image", "image_to_image", "multi_image")):
        errors.append("Agnes image route must support text-to-image, image-to-image, and multi-image")
    if agnes_image.get("selection") != "explicit_or_user_confirmed":
        errors.append("Agnes image route must be selected explicitly or after user confirmation")

    mmx_video = route_by_id(registry, "minimax-mmx-video")
    mmx_video_caps = mmx_video.get("capabilities", {}).get("video", {})
    if mmx_video_caps.get("reference_video") is not True:
        errors.append("MMX H3 route must declare reference-video support")
    if mmx_video_caps.get("precise_video_edit") is not False:
        errors.append("MMX H3 reference video must not be described as precise video editing")

    agnes_video = route_by_id(registry, "agnes-video")
    agnes_video_caps = agnes_video.get("capabilities", {}).get("video", {})
    if agnes_video_caps.get("video_to_video") is not False:
        errors.append("Agnes must not claim video-to-video support")

    quota = policies.get("minimax_video_quota", {}) if isinstance(policies, dict) else {}
    states = quota.get("states", {})
    if set(states) != {"known_positive", "known_exhausted", "unknown"}:
        errors.append("MMX video quota policy must expose exactly three states")
    if (
        states.get("known_positive") != "continue_mmx"
        or states.get("known_exhausted") != "ask_user_mmx_or_agnes"
        or states.get("unknown") != "ask_user_mmx_or_agnes"
        or quota.get("h3_quota_authoritative") is not False
    ):
        errors.append("MMX video quota actions or H3 authority boundary is invalid")

    for route in routes:
        if not isinstance(route, dict) or route.get("provider") != "minimax":
            continue
        executor = route.get("executor", {})
        if (
            executor.get("kind") != "external_cli"
            or executor.get("command") != "mmx"
            or executor.get("vendored") is not False
        ):
            errors.append(f"MMX route must use the non-vendored external CLI: {route.get('id')}")


def main() -> None:
    args = parse_args()
    root = args.root.resolve()
    errors: list[str] = []
    validate_files(root, errors)
    registry = load_registry(root, errors)
    if registry:
        validate_registry(registry, errors)

    result = {
        "valid": not errors,
        "errors": errors,
        "provider_calls": False,
        "secrets_read": False,
    }
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if errors:
        raise SystemExit(1)


if __name__ == "__main__":
    main()
