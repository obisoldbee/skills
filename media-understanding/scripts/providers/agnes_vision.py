#!/usr/bin/env python3
"""Call Agnes image understanding with an OpenAI-compatible chat request."""

from __future__ import annotations

import argparse
import json
import os
import re
import stat
import sys
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Dict, Optional


DEFAULT_ENV = Path.home() / ".codex" / "secrets" / "agnes.env"


class NoCredentialRedirect(urllib.request.HTTPRedirectHandler):
    """Authenticated API calls never follow redirects or resend a POST."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


def authenticated_urlopen(request, *, timeout):
    return urllib.request.build_opener(NoCredentialRedirect()).open(request, timeout=timeout)


DEFAULT_BASE_URL = "https://apihub.agnes-ai.com/v1"
DEFAULT_MODEL = "agnes-3.0-flash"


def load_env(path: Path) -> Dict[str, str]:
    values: Dict[str, str] = {}
    if path.exists():
        for line in path.read_text(encoding="utf-8").splitlines():
            line = line.strip()
            if not line or line.startswith("#") or "=" not in line:
                continue
            if line.startswith("export "):
                line = line[7:].strip()
            key, value = line.split("=", 1)
            values[key.strip()] = value.strip().strip("'\"")
    for key in ("AGNES_API_KEY", "AGNES_BASE_URL", "AGNES_MODEL"):
        if os.environ.get(key):
            values[key] = os.environ[key]
    return values


def key_status(path: Path) -> Dict[str, Any]:
    values = load_env(path)
    mode = None
    if path.exists():
        mode = stat.filemode(path.stat().st_mode)
    return {
        "env_path": str(path),
        "exists": path.exists(),
        "mode": mode,
        "has_agnes_api_key": bool(values.get("AGNES_API_KEY")),
        "has_agnes_base_url": bool(values.get("AGNES_BASE_URL")),
        "has_agnes_model": bool(values.get("AGNES_MODEL")),
        "safe_permissions": (not path.exists()) or (path.stat().st_mode & (stat.S_IRWXG | stat.S_IRWXO) == 0),
    }


def extract_json_object(text: str) -> Dict[str, Any]:
    text = text.strip()
    if not text:
        return {}
    try:
        parsed = json.loads(text)
        return parsed if isinstance(parsed, dict) else {}
    except json.JSONDecodeError:
        pass
    fence = re.search(r"```(?:json)?\s*(\{.*?\})\s*```", text, flags=re.S)
    if fence:
        try:
            parsed = json.loads(fence.group(1))
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            pass
    match = re.search(r"\{.*\}", text, flags=re.S)
    if match:
        try:
            parsed = json.loads(match.group(0))
            return parsed if isinstance(parsed, dict) else {}
        except json.JSONDecodeError:
            return {}
    return {}


def response_text(payload: Dict[str, Any]) -> str:
    choices = payload.get("choices")
    if not isinstance(choices, list) or not choices:
        return ""
    message = choices[0].get("message", {}) if isinstance(choices[0], dict) else {}
    if not isinstance(message, dict):
        return ""
    content = message.get("content", "")
    if isinstance(content, str):
        return content
    if isinstance(content, list):
        parts = []
        for item in content:
            if isinstance(item, dict) and item.get("type") == "text":
                parts.append(str(item.get("text", "")))
        return "\n".join(parts)
    return ""


def call_agnes(
    image_url: str,
    prompt: str,
    env_path: Path,
    timeout: int,
    model_override: Optional[str] = None,
    max_tokens: int = 700,
    thinking: Optional[bool] = None,
) -> Dict[str, Any]:
    if type(max_tokens) is not int or not 1 <= max_tokens <= 65536:
        return {
            "status": "failure", "failure_type": "invalid_max_tokens",
            "request_state": "not_sent", "error": "max_tokens must be between 1 and 65536",
        }
    parsed_url = urllib.parse.urlparse(image_url)
    if parsed_url.scheme not in {"http", "https"} or not parsed_url.netloc:
        return {
            "status": "failure",
            "failure_type": "invalid_image_url",
            "error": "Agnes image input must be a public http(s) URL; local paths and file:// are not accepted",
        }
    values = load_env(env_path)
    api_key = values.get("AGNES_API_KEY")
    if not api_key:
        return {"status": "failure", "failure_type": "missing_key", "error": f"missing AGNES_API_KEY in {env_path}"}
    base_url = values.get("AGNES_BASE_URL", DEFAULT_BASE_URL).rstrip("/")
    model = model_override or values.get("AGNES_MODEL", DEFAULT_MODEL)
    if model != DEFAULT_MODEL:
        return {
            "status": "failure",
            "failure_type": "unsupported_model",
            "error": f"Agnes route is pinned to {DEFAULT_MODEL}",
        }
    body = {
        "model": model,
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "image_url", "image_url": {"url": image_url}},
                ],
            }
        ],
        "temperature": 0.1,
        "max_tokens": max_tokens,
    }
    if thinking is not None:
        body["chat_template_kwargs"] = {"enable_thinking": thinking}
    req = urllib.request.Request(
        f"{base_url}/chat/completions",
        data=json.dumps(body, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json",
        },
        method="POST",
    )
    started = time.time()
    try:
        with authenticated_urlopen(req, timeout=timeout) as resp:
            raw = resp.read().decode("utf-8", errors="replace")
            status_code = resp.status
    except urllib.error.HTTPError as exc:
        try:
            body_text = exc.read(4000).decode("utf-8", errors="replace")
        finally:
            exc.close()
        return {
            "status": "failure",
            "failure_type": "agnes_server_error" if exc.code >= 500 else "agnes_rejected",
            "request_state": "rejected" if 400 <= exc.code < 500 and exc.code != 408 else "acceptance_unknown",
            "http_status": exc.code,
            "error": body_text,
            "latency_sec": round(time.time() - started, 3),
        }
    except TimeoutError as exc:
        return {
            "status": "failure",
            "failure_type": "agnes_timeout",
            "request_state": "acceptance_unknown",
            "error": str(exc),
            "latency_sec": round(time.time() - started, 3),
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "status": "failure",
            "failure_type": "agnes_request_error",
            "request_state": "acceptance_unknown",
            "error": repr(exc),
            "latency_sec": round(time.time() - started, 3),
        }

    try:
        payload = json.loads(raw)
    except json.JSONDecodeError:
        return {
            "status": "failure",
            "failure_type": "parse_failure",
            "request_state": "accepted",
            "http_status": status_code,
            "raw_response": raw[:4000],
            "latency_sec": round(time.time() - started, 3),
        }
    if not isinstance(payload, dict):
        return {
            "status": "failure", "failure_type": "parse_failure", "request_state": "accepted",
            "http_status": status_code, "raw_response": payload,
            "latency_sec": round(time.time() - started, 3),
        }
    text = response_text(payload)
    parsed = extract_json_object(text)
    choices = payload.get("choices") or []
    finish_reason = choices[0].get("finish_reason") if isinstance(choices, list) and choices and isinstance(choices[0], dict) else None
    truncated = finish_reason == "length"
    return {
        "status": "incomplete" if truncated else "success" if text else "failure",
        "failure_type": "output_truncated" if truncated else None if text else "empty_response",
        "request_state": "completed" if text and not truncated else "accepted",
        "finish_reason": finish_reason,
        "http_status": status_code,
        "model": model,
        "content": text,
        "parsed_json": parsed,
        "raw_response": payload,
        "latency_sec": round(time.time() - started, 3),
    }


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--env", default=str(DEFAULT_ENV))
    parser.add_argument("--check-key", action="store_true")
    parser.add_argument("--image-url")
    parser.add_argument("--prompt", default="Return compact JSON describing the image.")
    parser.add_argument("--model")
    parser.add_argument("--max-tokens", type=int, default=700)
    parser.add_argument("--thinking", action=argparse.BooleanOptionalAction, default=None,
                        help="Explicitly enable/disable Chat Completions thinking; omitted keeps provider default")
    parser.add_argument("--timeout", type=int, default=90)
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    env_path = Path(args.env)
    if args.check_key:
        print(json.dumps(key_status(env_path), ensure_ascii=False, indent=2))
        return
    if not args.image_url:
        raise SystemExit("--image-url is required unless --check-key is used")
    result = call_agnes(args.image_url, args.prompt, env_path, args.timeout, args.model,
                        max_tokens=args.max_tokens, thinking=args.thinking)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    if result.get("status") != "success":
        sys.exit(1)


if __name__ == "__main__":
    main()
