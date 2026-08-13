#!/usr/bin/env python3
"""Validate the portable media-understanding package."""

from __future__ import annotations

import json
import re
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
REQUIRED = [
    "SKILL.md",
    "agents/openai.yaml",
    "config/routes.json",
    "references/provider-routing.md",
    "references/image-understanding.md",
    "references/audio-understanding.md",
    "references/video-understanding.md",
    "references/ocr-and-document-understanding.md",
    "references/minimax-shared-api.md",
    "references/official-sources.md",
    "scripts/check_routes.py",
    "scripts/providers/agnes_vision.py",
    "scripts/providers/minimax_m3_course_audio.py",
    "scripts/providers/minimax_m3_course_video.py",
]
ALLOWED_STATUS = {"active", "active_if_configured", "disabled", "external_configuration", "discovery_required"}
STALE_ACTIVE_BINDINGS = {
    "13-course-video-understanding",
    "14-video-visual-understanding",
    "15-video-audio-understanding",
    "16-video-timed-transcription",
    "mimo-course-audio-understanding",
    "agnes-image-understanding",
    "volcengine-ark-image-understanding",
    "minimax-m3-course-audio-understanding",
    "minimax-m3-course-video-understanding",
}


def fail(errors: list[str]) -> None:
    print(json.dumps({"valid": False, "errors": errors}, ensure_ascii=False, indent=2))
    raise SystemExit(1)


def main() -> None:
    errors: list[str] = []
    for relative in REQUIRED:
        if not (ROOT / relative).is_file():
            errors.append(f"missing required file: {relative}")

    env_files = [path.relative_to(ROOT).as_posix() for path in ROOT.rglob("*.env")]
    if env_files:
        errors.append(f"credential files must not be stored in package: {env_files}")

    binding_files = list(ROOT.rglob("*.md")) + list(ROOT.rglob("*.json")) + list(ROOT.rglob("*.yaml"))
    portable_files = binding_files + [path for path in ROOT.rglob("*.py") if path.resolve() != Path(__file__).resolve()]
    portable_text = "\n".join(path.read_text(encoding="utf-8") for path in portable_files)
    binding_text = "\n".join(path.read_text(encoding="utf-8") for path in binding_files)
    if "/" + "Users/" in portable_text:
        errors.append("portable package contains an absolute /Users path")
    for stale in sorted(STALE_ACTIVE_BINDINGS):
        if stale in binding_text:
            errors.append(f"stale active binding remains: {stale}")

    skill_text = (ROOT / "SKILL.md").read_text(encoding="utf-8") if (ROOT / "SKILL.md").is_file() else ""
    for target in re.findall(r"\[[^]]+\]\((references/[^)]+)\)", skill_text):
        if not (ROOT / target).is_file():
            errors.append(f"broken SKILL reference: {target}")

    routes_path = ROOT / "config" / "routes.json"
    routes: list[dict] = []
    if routes_path.is_file():
        try:
            routes = json.loads(routes_path.read_text(encoding="utf-8"))["routes"]
        except (json.JSONDecodeError, KeyError, TypeError) as exc:
            errors.append(f"invalid route registry: {exc}")
    ids = [route.get("id") for route in routes]
    if len(ids) != len(set(ids)):
        errors.append("route ids are not unique")
    for route in routes:
        if route.get("status") not in ALLOWED_STATUS:
            errors.append(f"invalid status for {route.get('id')}: {route.get('status')}")
        credentials = route.get("credentials")
        if credentials and not str(credentials.get("file", "")).startswith("~/.codex/secrets/"):
            errors.append(f"nonstandard credential path for {route.get('id')}")

    internal_executors = {
        "agnes-image": "scripts/providers/agnes_vision.py",
        "minimax-m3-course-audio-via-video-experimental": "scripts/providers/minimax_m3_course_audio.py",
        "minimax-m3-course-video": "scripts/providers/minimax_m3_course_video.py",
    }
    for route_id, path in internal_executors.items():
        route = next((item for item in routes if item.get("id") == route_id), {})
        if route.get("executor") != {"kind": "script", "path": path}:
            errors.append(f"route must use its package-owned script executor: {route_id}")

    agnes = next((route for route in routes if route.get("id") == "agnes-image"), None)
    if not agnes or agnes.get("model") != "agnes-2.5-flash":
        errors.append("Agnes route must target agnes-2.5-flash")
    mmx = next((route for route in routes if route.get("id") == "minimax-mmx-image"), None)
    if not mmx or mmx.get("model") is not None:
        errors.append("mmx vision route must not claim an underlying model id")
    minimax_m3_ids = {
        "minimax-m3-image",
        "minimax-m3-course-video",
        "minimax-m3-course-audio-via-video-experimental",
        "minimax-m3-transcript-semantics",
    }
    if not minimax_m3_ids.issubset(set(ids)):
        errors.append("all direct MiniMax-M3 routes must be present")
    for route in (route for route in routes if route.get("id") in minimax_m3_ids):
        interface = route.get("interface", {})
        if (
            route.get("model") != "MiniMax-M3"
            or interface.get("default") != "anthropic_messages"
            or interface.get("base_url") != "https://api.minimaxi.com/anthropic"
            or interface.get("endpoint") != "https://api.minimaxi.com/anthropic/v1/messages"
            or interface.get("openai_compatible_fallback") != "https://api.minimaxi.com/v1/chat/completions"
            or interface.get("openai_fallback_policy") != "only for a project already bound to the OpenAI SDK"
        ):
            errors.append(f"MiniMax-M3 route must default to the recommended Anthropic Messages endpoint: {route.get('id')}")
    mimo_ids = {"mimo-v2.5-image", "mimo-v2.5-audio", "mimo-v2.5-video"}
    mimo = [route for route in routes if route.get("id") in mimo_ids]
    if {route.get("id") for route in mimo} != mimo_ids:
        errors.append("all three MiMo media routes must be preserved")
    for route in mimo:
        if (
            route.get("status") != "disabled"
            or route.get("model") != "mimo-v2.5"
            or route.get("executor", {}).get("kind") != "none"
            or route.get("runtime_state") != "not_run/unverified_capability"
            or not str(route.get("stop_reason", "")).startswith("local_route_not_ready:")
        ):
            errors.append(f"MiMo route must stay disabled with model mimo-v2.5 and no executable: {route.get('id')}")
    mimo_image = next((route for route in mimo if route.get("id") == "mimo-v2.5-image"), {})
    input_contract = mimo_image.get("input_contract", {})
    local_image = input_contract.get("local_image", "")
    required_local_terms = ("client_reads_and_embeds_base64", "local path", "file://", "file object", "separate upload reference")
    if (
        input_contract.get("api_key_role") != "authentication_only"
        or input_contract.get("public_url") is not True
        or any(term not in local_image for term in required_local_terms)
        or input_contract.get("openai") != "image_url.url=data:{MIME_TYPE};base64,..."
        or input_contract.get("anthropic") != "source.type=base64 with media_type and data"
        or input_contract.get("limits") != "URL file <=50MB; encoded Base64 string <=50MB"
    ):
        errors.append("MiMo image contract must preserve client-side Base64 input while forbidding direct local paths")

    if errors:
        fail(errors)
    print(json.dumps({
        "valid": True,
        "routes": len(routes),
        "disabled_routes": [route["id"] for route in routes if route["status"] == "disabled"],
        "credential_files_in_package": 0,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
