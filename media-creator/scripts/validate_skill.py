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
    "references/local-skill-audit.md",
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

    policies = registry.get("policies", {})
    text_policy = policies.get("non_codex_text_to_image", {}) if isinstance(policies, dict) else {}
    if (
        text_policy.get("primary") != "chatgpt-web-image"
        or text_policy.get("pre_submission_fallback") != "minimax-mmx-image"
        or text_policy.get("fallback_phase") != "before_submission_only"
        or text_policy.get("agnes_selection") != "explicit_or_user_confirmed"
    ):
        errors.append("non-Codex text-to-image priority or fallback policy is invalid")

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
