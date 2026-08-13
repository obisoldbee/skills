#!/usr/bin/env python3
"""Build or execute Agnes Image 2.1 and Video V2 requests.

The CLI is dry-run by default. It reads no credential source and performs no
network request unless ``--execute`` is supplied explicitly.
"""

from __future__ import annotations

import argparse
import base64
import json
import mimetypes
import os
import time
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Callable


DEFAULT_BASE_URL = "https://apihub.agnes-ai.com"
IMAGE_MODEL = "agnes-image-2.1-flash"
VIDEO_MODEL = "agnes-video-v2.0"
TERMINAL_VIDEO_STATES = {"completed", "failed"}
RATIOS = ("1:1", "3:4", "4:3", "16:9", "9:16", "2:3", "3:2", "21:9")


class AgnesError(RuntimeError):
    """A clear, user-facing Agnes request error."""


def execution_parent() -> argparse.ArgumentParser:
    parent = argparse.ArgumentParser(add_help=False)
    parent.add_argument(
        "--execute",
        action="store_true",
        help="Read external credentials and call Agnes. Omit for a local dry-run.",
    )
    parent.add_argument(
        "--env-file",
        type=Path,
        help="Credential file read only with --execute (default: ~/.codex/secrets/agnes.env).",
    )
    parent.add_argument("--timeout", type=float, default=120.0, help="HTTP timeout in seconds.")
    return parent


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    subparsers = parser.add_subparsers(dest="media", required=True)
    common = execution_parent()

    image = subparsers.add_parser("image", parents=[common], help="Generate or edit an image.")
    image.add_argument("--prompt", required=True)
    image.add_argument("--size", default="1K")
    image.add_argument("--ratio", choices=RATIOS, default="1:1")
    image.add_argument(
        "--image",
        action="append",
        default=[],
        metavar="URL_OR_FILE",
        help="Input image; repeat for multi-image composition.",
    )
    image.add_argument("--response-format", choices=("url", "b64_json"), default="url")
    image.add_argument("--output", type=Path, help="Save the first returned image here.")

    video = subparsers.add_parser("video", parents=[common], help="Create an async video task.")
    video.add_argument("--prompt", required=True)
    inputs = video.add_mutually_exclusive_group()
    inputs.add_argument("--image", metavar="PUBLIC_URL", help="Single public image URL.")
    inputs.add_argument(
        "--keyframe",
        action="append",
        default=[],
        metavar="PUBLIC_URL",
        help="Public keyframe URL; repeat at least twice.",
    )
    video.add_argument("--width", type=int, default=1152)
    video.add_argument("--height", type=int, default=768)
    video.add_argument("--num-frames", type=int, default=121)
    video.add_argument("--frame-rate", type=float, default=24)
    video.add_argument("--num-inference-steps", type=int)
    video.add_argument("--seed", type=int)
    video.add_argument("--negative-prompt")
    video.add_argument("--wait", action="store_true", help="Poll until completed or failed.")
    video.add_argument("--poll-interval", type=float, default=5.0)
    video.add_argument("--max-wait", type=float, default=360.0)
    video.add_argument("--output", type=Path, help="With --wait, download metadata.url here.")

    args = parser.parse_args(argv)
    validate_args(parser, args)
    return args


def validate_args(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    if args.timeout <= 0:
        parser.error("--timeout must be greater than zero")
    if args.media == "video":
        if args.num_frames < 1 or args.num_frames > 441 or (args.num_frames - 1) % 8:
            parser.error("--num-frames must be <= 441 and follow the 8n+1 rule")
        if not 1 <= args.frame_rate <= 60:
            parser.error("--frame-rate must be between 1 and 60")
        if args.keyframe and len(args.keyframe) < 2:
            parser.error("keyframe mode requires at least two --keyframe values")
        if args.output and not args.wait:
            parser.error("--output requires --wait for video generation")
        if args.poll_interval <= 0 or args.max_wait <= 0:
            parser.error("--poll-interval and --max-wait must be greater than zero")


def _is_remote_or_data_uri(value: str) -> bool:
    return value.startswith(("https://", "http://", "data:image/"))


def image_input(value: str, *, execute: bool) -> str:
    if _is_remote_or_data_uri(value):
        if not execute and value.startswith("data:image/"):
            media_type = value.split(";", 1)[0]
            return f"{media_type};base64,<omitted>"
        return value
    path = Path(value).expanduser()
    if not execute:
        return f"<data-uri-from:{path}>"
    try:
        data = path.read_bytes()
    except OSError as exc:
        raise AgnesError(f"cannot read input image {path}: {exc}") from exc
    media_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return f"data:{media_type};base64,{base64.b64encode(data).decode('ascii')}"


def build_image_payload(args: argparse.Namespace, *, execute: bool) -> dict[str, Any]:
    extra_body: dict[str, Any] = {"response_format": args.response_format}
    if args.image:
        extra_body["image"] = [image_input(value, execute=execute) for value in args.image]
    return {
        "model": IMAGE_MODEL,
        "prompt": args.prompt,
        "size": args.size,
        "ratio": args.ratio,
        "extra_body": extra_body,
    }


def build_video_payload(args: argparse.Namespace) -> dict[str, Any]:
    frame_rate: int | float = args.frame_rate
    if frame_rate.is_integer():
        frame_rate = int(frame_rate)
    payload: dict[str, Any] = {
        "model": VIDEO_MODEL,
        "prompt": args.prompt,
        "width": args.width,
        "height": args.height,
        "num_frames": args.num_frames,
        "frame_rate": frame_rate,
    }
    if args.image:
        payload["image"] = args.image
    if args.keyframe:
        payload["extra_body"] = {"image": args.keyframe, "mode": "keyframes"}
    for argument, field in (
        (args.num_inference_steps, "num_inference_steps"),
        (args.seed, "seed"),
        (args.negative_prompt, "negative_prompt"),
    ):
        if argument is not None:
            payload[field] = argument
    return payload


def parse_env_file(path: Path) -> dict[str, str]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return {}
    except OSError as exc:
        raise AgnesError(f"cannot read credential file {path}: {exc}") from exc
    values: dict[str, str] = {}
    for line in lines:
        stripped = line.strip()
        if not stripped or stripped.startswith("#") or "=" not in stripped:
            continue
        name, value = stripped.removeprefix("export ").split("=", 1)
        values[name.strip()] = value.strip().strip("\"'")
    return values


def execution_config(args: argparse.Namespace) -> tuple[str, str]:
    """Read external configuration. Call only after explicit --execute gating."""
    env_path = args.env_file or Path.home() / ".codex" / "secrets" / "agnes.env"
    file_values = parse_env_file(env_path)
    key = os.environ.get("AGNES_API_KEY") or file_values.get("AGNES_API_KEY")
    if not key:
        raise AgnesError("AGNES_API_KEY is not configured in the environment or credential file")
    base_url = os.environ.get("AGNES_BASE_URL") or file_values.get("AGNES_BASE_URL") or DEFAULT_BASE_URL
    return base_url.rstrip("/"), key


def request_json(
    method: str,
    url: str,
    key: str,
    *,
    payload: dict[str, Any] | None = None,
    timeout: float,
) -> dict[str, Any]:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    request = urllib.request.Request(
        url,
        data=data,
        method=method,
        headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
    )
    try:
        with urllib.request.urlopen(request, timeout=timeout) as response:
            result = json.loads(response.read().decode("utf-8"))
    except urllib.error.HTTPError as exc:
        detail = exc.read().decode("utf-8", errors="replace")
        raise AgnesError(f"Agnes HTTP {exc.code}: {detail}") from exc
    except (urllib.error.URLError, TimeoutError) as exc:
        raise AgnesError(f"Agnes request failed: {exc}") from exc
    except json.JSONDecodeError as exc:
        raise AgnesError("Agnes returned invalid JSON") from exc
    if not isinstance(result, dict):
        raise AgnesError("Agnes returned a non-object JSON response")
    return result


def download(url: str, output: Path, *, timeout: float) -> None:
    output = output.expanduser()
    output.parent.mkdir(parents=True, exist_ok=True)
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            output.write_bytes(response.read())
    except (OSError, urllib.error.URLError, TimeoutError) as exc:
        raise AgnesError(f"cannot download result to {output}: {exc}") from exc


def save_image_result(result: dict[str, Any], output: Path, *, timeout: float) -> None:
    items = result.get("data")
    if not isinstance(items, list) or not items or not isinstance(items[0], dict):
        raise AgnesError("Agnes image response has no data[0] result")
    first = items[0]
    if isinstance(first.get("url"), str):
        download(first["url"], output, timeout=timeout)
        return
    if isinstance(first.get("b64_json"), str):
        output = output.expanduser()
        output.parent.mkdir(parents=True, exist_ok=True)
        try:
            output.write_bytes(base64.b64decode(first["b64_json"], validate=True))
        except (OSError, ValueError) as exc:
            raise AgnesError(f"cannot save Base64 image to {output}: {exc}") from exc
        return
    raise AgnesError("Agnes image response contains neither data[0].url nor data[0].b64_json")


def video_result_url(result: dict[str, Any]) -> str | None:
    metadata = result.get("metadata")
    if not isinstance(metadata, dict):
        return None
    url = metadata.get("url")
    return url if isinstance(url, str) and url else None


def poll_video(
    initial: dict[str, Any],
    *,
    base_url: str,
    key: str,
    timeout: float,
    poll_interval: float,
    max_wait: float,
    request: Callable[..., dict[str, Any]] = request_json,
) -> dict[str, Any]:
    video_id = initial.get("video_id")
    task_id = initial.get("task_id") or initial.get("id")
    if video_id:
        query = urllib.parse.urlencode({"video_id": str(video_id)})
        result_url = f"{base_url}/agnesapi?{query}"
    elif task_id:
        result_url = f"{base_url}/v1/videos/{urllib.parse.quote(str(task_id), safe='')}"
    else:
        raise AgnesError("Agnes create response contains neither video_id nor task_id")

    deadline = time.monotonic() + max_wait
    result = initial
    while result.get("status") not in TERMINAL_VIDEO_STATES:
        if time.monotonic() >= deadline:
            raise AgnesError(f"timed out waiting for Agnes video after {max_wait:g} seconds")
        time.sleep(poll_interval)
        result = request("GET", result_url, key, timeout=timeout)
    if result.get("status") == "failed":
        raise AgnesError(f"Agnes video generation failed: {result.get('error') or 'unknown error'}")
    if not video_result_url(result):
        raise AgnesError("completed Agnes video response has no metadata.url")
    return result


def dry_run(args: argparse.Namespace, payload: dict[str, Any]) -> dict[str, Any]:
    endpoint = "/v1/images/generations" if args.media == "image" else "/v1/videos"
    return {
        "mode": "dry_run",
        "provider_calls": False,
        "secrets_read": False,
        "request": {"method": "POST", "url": DEFAULT_BASE_URL + endpoint, "payload": payload},
    }


def execute(args: argparse.Namespace, payload: dict[str, Any]) -> dict[str, Any]:
    base_url, key = execution_config(args)
    endpoint = "/v1/images/generations" if args.media == "image" else "/v1/videos"
    result = request_json("POST", base_url + endpoint, key, payload=payload, timeout=args.timeout)
    if args.media == "image":
        if args.output:
            save_image_result(result, args.output, timeout=args.timeout)
        return result
    if args.wait:
        result = poll_video(
            result,
            base_url=base_url,
            key=key,
            timeout=args.timeout,
            poll_interval=args.poll_interval,
            max_wait=args.max_wait,
        )
        if args.output:
            download(video_result_url(result) or "", args.output, timeout=args.timeout)
    return result


def main(argv: list[str] | None = None) -> int:
    try:
        args = parse_args(argv)
        payload = (
            build_image_payload(args, execute=args.execute)
            if args.media == "image"
            else build_video_payload(args)
        )
        if not args.execute:
            report = dry_run(args, payload)
        else:
            report = {
                "mode": "execute",
                "provider_calls": True,
                "secrets_read": True,
                "result": execute(args, payload),
            }
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    except AgnesError as exc:
        print(
            json.dumps(
                {"error": str(exc), "provider_calls": bool(locals().get("args") and args.execute)},
                ensure_ascii=False,
            )
        )
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
