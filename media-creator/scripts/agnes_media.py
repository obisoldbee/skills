#!/usr/bin/env python3
"""Build or execute Agnes Image 2.5 Flash and Video 2.5 requests.

The CLI is dry-run by default. It reads no credential source and performs no
network request unless ``--execute`` is supplied explicitly.
"""

from __future__ import annotations

import argparse
import base64
import http.client
import ipaddress
import json
import math
import mimetypes
import os
import re
import stat
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path
from typing import Any, Callable


DEFAULT_BASE_URL = "https://apihub.agnes-ai.com"
IMAGE_MODEL = "agnes-image-2.5-flash"
VIDEO_MODEL = "agnes-video-2.5-flash"
STANDARD_VIDEO_MODEL = "agnes-video-2.5"
VIDEO_MODELS = (VIDEO_MODEL, STANDARD_VIDEO_MODEL)
TERMINAL_VIDEO_STATES = {"completed", "failed"}
VIDEO_STATES = {"queued", "in_progress", *TERMINAL_VIDEO_STATES}
RATIOS = ("1:1", "3:4", "4:3", "16:9", "9:16", "2:3", "3:2", "21:9")
VIDEO_RATIOS = ("21:9", "16:9", "4:3", "1:1", "3:4", "9:16")
VIDEO_SIZES = ("720P", "1080P", "1K", "2K")
DIR_FD_OUTPUT_SUPPORTED = (
    all(function in os.supports_dir_fd for function in (os.open, os.mkdir, os.stat, os.link, os.unlink))
    and all(function in os.supports_follow_symlinks for function in (os.stat, os.link))
    and hasattr(os, "O_DIRECTORY")
    and hasattr(os, "O_NOFOLLOW")
)


class AgnesError(RuntimeError):
    """A clear, user-facing Agnes request error."""

    def __init__(self, message: str) -> None:
        super().__init__(message)
        self.provider_calls = False
        self.secrets_read = False
        self.recovery: dict[str, Any] | None = None
        self.artifact: dict[str, Any] | None = None


class SingleFrameURL(argparse.Action):
    def __call__(self, parser, namespace, values, option_string=None):
        if getattr(namespace, self.dest) is not None:
            parser.error(f"{option_string} accepts one frame; use reference mode for multiple images")
        setattr(namespace, self.dest, values)


def error_category(exc: BaseException) -> str:
    """Public errors never include transport bodies, URLs, reasons or reprs."""
    if isinstance(exc, urllib.error.HTTPError):
        code = exc.code if isinstance(exc.code, int) else "unknown"
        try:
            exc.close()
        except (OSError, ValueError):
            return f"HTTP {code} (response_close_failed)"
        return f"HTTP {code}"
    if isinstance(exc, urllib.error.URLError):
        return "network_error"
    if isinstance(exc, TimeoutError):
        return "timeout"
    if isinstance(exc, http.client.HTTPException):
        return "http_protocol_error"
    if isinstance(exc, OSError):
        return f"io_error (errno={exc.errno})" if isinstance(exc.errno, int) else "io_error"
    if isinstance(exc, ValueError):
        return "invalid_value"
    return "operation_failed"


class OutputTarget:
    """One output's pinned parent; every filesystem mutation is dir_fd-relative."""

    def __init__(self, path: Path, parent_fd: int) -> None:
        self.path = path
        self.parent_fd = parent_fd
        info = os.fstat(parent_fd)
        self.identity = (info.st_dev, info.st_ino)
        self.published = False

    def __str__(self) -> str:
        return str(self.path)

    def __enter__(self) -> OutputTarget:
        return self

    def __exit__(self, *args: Any) -> None:
        self.close()

    def close(self) -> None:
        os.close(self.parent_fd)

    def parent_is_current(self) -> bool:
        try:
            info = self.path.parent.lstat()
        except OSError:
            return False
        return stat.S_ISDIR(info.st_mode) and (info.st_dev, info.st_ino) == self.identity

    def check_parent(self) -> None:
        if not self.parent_is_current():
            raise AgnesError("output parent identity changed; refusing redirected writes")

    def location(self, name: str) -> dict[str, Any]:
        return {
            "name": name,
            "original_parent": str(self.path.parent),
            "parent_identity": {"device": self.identity[0], "inode": self.identity[1]},
            "path_verified": self.parent_is_current(),
        }

    def create_private(self, prefix: str, suffix: str) -> tuple[str, int]:
        self.check_parent()
        name = prefix + uuid.uuid4().hex + suffix
        fd = os.open(
            name, os.O_WRONLY | os.O_CREAT | os.O_EXCL | os.O_NOFOLLOW,
            0o600, dir_fd=self.parent_fd,
        )
        return name, fd

    def unlink(self, name: str) -> None:
        os.unlink(name, dir_fd=self.parent_fd)

    def link(self, source: str, destination: str) -> None:
        os.link(
            source, destination, src_dir_fd=self.parent_fd,
            dst_dir_fd=self.parent_fd, follow_symlinks=False,
        )

    def probe(self) -> None:
        """Fail before credentials if this volume cannot perform safe publication."""
        name, fd = self.create_private(".agnes-probe-", ".tmp")
        os.close(fd)
        linked = False
        try:
            self.link(name, name + ".link")
            linked = True
            self.check_parent()
        finally:
            try:
                if linked:
                    self.unlink(name + ".link")
            finally:
                self.unlink(name)


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
    parser = argparse.ArgumentParser(description=__doc__, allow_abbrev=False)
    subparsers = parser.add_subparsers(dest="media", required=True)
    common = execution_parent()

    image = subparsers.add_parser("image", parents=[common], allow_abbrev=False, help="Generate or edit an image.")
    image.add_argument("--model", choices=(IMAGE_MODEL,), default=IMAGE_MODEL)
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
    image.add_argument("--response-format", choices=("url", "b64_json"))
    image.add_argument("--return-base64", action="store_true", help="Text-to-image Base64 output.")
    image.add_argument("--output", type=Path, help="Save the first returned image here.")

    video = subparsers.add_parser("video", parents=[common], allow_abbrev=False, help="Create a Video 2.5 task.")
    video.add_argument("--model", choices=VIDEO_MODELS, default=VIDEO_MODEL)
    video.add_argument("--prompt", required=True)
    video.add_argument("--mode", choices=("text", "keyframe", "reference"), help="Omit to infer from explicit media flags.")
    video.add_argument("--seconds", choices=tuple(str(n) for n in range(4, 13)), default="5")
    video.add_argument("--size", choices=VIDEO_SIZES, default="720P")
    video.add_argument("--aspect-ratio", choices=VIDEO_RATIOS, help="Default: 16:9, or 1:1 for standard 1K.")
    video.add_argument("--seed", type=int)
    video.add_argument("--n", type=int, choices=(1,), default=1)
    video.add_argument("--first-frame", "--image", dest="first_frame", action=SingleFrameURL, metavar="PUBLIC_URL", help="First frame; --image is a single-frame alias.")
    video.add_argument("--last-frame", action=SingleFrameURL, metavar="PUBLIC_URL")
    video.add_argument("--reference-image", action="append", default=[], metavar="PUBLIC_URL")
    video.add_argument("--reference-audio", action="append", default=[], metavar="PUBLIC_URL")
    video.add_argument("--reference-video", action="append", default=[], metavar="PUBLIC_URL", help="Standard 2.5 only; maximum one.")
    video.add_argument("--video-start-seconds", type=float)
    video.add_argument("--video-require-audio", action=argparse.BooleanOptionalAction, default=None)

    status = subparsers.add_parser("video-status", parents=[common], allow_abbrev=False, help="Query the same task without creating a video.")
    status.add_argument("--video-id", required=True)
    status.add_argument("--model", choices=VIDEO_MODELS, required=True, help="Use the original task's model.")
    for command in (video, status):
        command.add_argument("--wait", action="store_true", help="Poll until completed or failed.")
        command.add_argument("--poll-interval", type=float, default=1.5)
        command.add_argument("--max-wait", type=float, default=600.0)
        command.add_argument("--output", type=Path, help="With --wait, download metadata.url here.")

    args = parser.parse_args(argv)
    validate_args(parser, args)
    return args


def validate_args(parser: argparse.ArgumentParser, args: argparse.Namespace) -> None:
    if not math.isfinite(args.timeout) or args.timeout <= 0:
        parser.error("--timeout must be greater than zero")
    if args.media in ("image", "video") and not args.prompt.strip():
        parser.error("--prompt must not be empty")
    if args.media == "image":
        if not re.fullmatch(r"(?:[1-4]K|[1-9][0-9]*x[1-9][0-9]*)", args.size):
            parser.error("image --size must be 1K, 2K, 3K, 4K or positive WIDTHxHEIGHT")
        if args.return_base64 and (args.image or args.response_format == "url"):
            parser.error("--return-base64 is text-only and conflicts with --image or URL output")
        args.response_format = args.response_format or ("b64_json" if args.return_base64 else "url")
    else:
        if args.output and not args.wait:
            parser.error("--output requires --wait for video generation")
        if any(not math.isfinite(n) or n <= 0 for n in (args.poll_interval, args.max_wait)):
            parser.error("--poll-interval and --max-wait must be greater than zero")
        if args.media == "video-status":
            if not args.video_id.strip():
                parser.error("--video-id must not be empty")
            return
        frames = bool(args.first_frame or args.last_frame)
        references = bool(args.reference_image or args.reference_audio or args.reference_video)
        args.mode = args.mode or ("keyframe" if frames else "reference" if references else "text")
        if args.mode == "text" and (frames or references):
            parser.error("text mode accepts no media; choose keyframe or reference")
        if args.mode == "keyframe" and (not frames or references):
            parser.error("keyframe requires first/last frame and forbids reference media")
        if args.mode == "reference" and (frames or not references):
            parser.error("reference requires reference media and forbids first/last frame")
        flash = args.model == VIDEO_MODEL
        if flash and args.size != "720P":
            parser.error("Agnes Video 2.5 Flash size must be 720P; model will not be changed automatically")
        if args.size == "1K" and args.aspect_ratio not in (None, "1:1"):
            parser.error("standard Video 2.5 size 1K is fixed at 1024x1024; choose 1:1 or another size")
        args.aspect_ratio = args.aspect_ratio or ("1:1" if args.size == "1K" else "16:9")
        if flash and args.reference_video:
            parser.error("Agnes Video 2.5 Flash does not support reference video")
        if len(args.reference_image) > (5 if flash else 8):
            parser.error(f"reference images must not exceed {5 if flash else 8}")
        if len(args.reference_audio) > 3 or len(args.reference_video) > 1:
            parser.error("reference audio must not exceed 3; reference video must not exceed 1")
        if not args.reference_video and (args.video_start_seconds is not None or args.video_require_audio is not None):
            parser.error("video object options require --reference-video")
        if args.video_start_seconds is not None and (not math.isfinite(args.video_start_seconds) or args.video_start_seconds < 0):
            parser.error("--video-start-seconds must be finite and non-negative")
        media_urls = [args.first_frame, args.last_frame, *args.reference_image, *args.reference_audio, *args.reference_video]
        if any(not public_media_url(value) for value in media_urls if value is not None):
            parser.error("video media requires public HTTP(S) URLs without credentials; local paths and Data URIs are unsupported")


def public_media_url(value: str) -> bool:
    """Check URL form only; never fetch media or claim public reachability."""
    try:
        url = urllib.parse.urlsplit(value)
        host = url.hostname
        if url.scheme not in ("https", "http") or not host or url.username or url.password:
            return False
        if any(c.isspace() for c in value) or url.fragment or url.port == 0:
            return False
        if host.lower().rstrip(".") == "localhost" or host.lower().rstrip(".").endswith((".localhost", ".local")):
            return False
        try:
            return ipaddress.ip_address(host).is_global
        except ValueError:
            return True  # DNS and actual accessibility remain runtime checks.
    except ValueError:
        return False


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
        raise AgnesError(f"cannot read input image {path}: {error_category(exc)}") from exc
    media_type = mimetypes.guess_type(path.name)[0] or "application/octet-stream"
    return f"data:{media_type};base64,{base64.b64encode(data).decode('ascii')}"


def build_image_payload(args: argparse.Namespace, *, execute: bool) -> dict[str, Any]:
    extra_body: dict[str, Any] = {"response_format": args.response_format}
    if args.image:
        extra_body["image"] = [image_input(value, execute=execute) for value in args.image]
    payload = {
        "model": args.model,
        "prompt": args.prompt,
        "size": args.size,
        "ratio": args.ratio,
        "extra_body": extra_body,
    }
    if not args.image and args.response_format == "b64_json":
        payload.pop("extra_body")
        payload["return_base64"] = True
    return payload


def build_video_payload(args: argparse.Namespace) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "model": args.model,
        "prompt": args.prompt,
        "mode": args.mode,
        "seconds": args.seconds,
        "size": args.size,
        "aspect_ratio": args.aspect_ratio,
        "n": args.n,
    }
    if args.seed is not None:
        payload["seed"] = args.seed
    for field in ("first_frame", "last_frame"):
        if getattr(args, field) is not None:
            payload[field] = getattr(args, field)
    for flag, field in ((args.reference_image, "images"), (args.reference_audio, "audios")):
        if flag:
            payload[field] = flag
    if args.reference_video:
        payload["videos"] = [{
            "url": args.reference_video[0],
            "start_seconds": args.video_start_seconds if args.video_start_seconds is not None else 0,
            "require_audio": args.video_require_audio if args.video_require_audio is not None else False,
        }]
    return payload


def service_root(value: str) -> str:
    """Accept the documented origin or /v1 API base, without duplicating /v1."""
    try:
        parsed = urllib.parse.urlsplit(value)
        if (parsed.scheme not in ("https", "http") or not parsed.hostname
                or parsed.username or parsed.password or parsed.query or parsed.fragment
                or parsed.port == 0 or any(c.isspace() for c in value)
                or parsed.path.rstrip("/") not in ("", "/v1")):
            raise ValueError
        return urllib.parse.urlunsplit((parsed.scheme, parsed.netloc, "", "", ""))
    except ValueError:
        raise AgnesError("AGNES_BASE_URL must be a service origin or its /v1 API base") from None


def video_query_url(base_url: str, video_id: str, model: str) -> str:
    if not isinstance(video_id, str) or not video_id.strip() or model not in VIDEO_MODELS:
        raise AgnesError("video query requires the original video_id and a supported model")
    query = urllib.parse.urlencode({"video_id": video_id, "model_name": model})
    return f"{service_root(base_url)}/agnesapi?{query}"


def parse_env_file(path: Path) -> dict[str, str]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        return {}
    except OSError as exc:
        raise AgnesError(f"cannot read credential file {path}: {error_category(exc)}") from exc
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
    return service_root(base_url), key


def request_json(
    method: str,
    url: str,
    key: str,
    *,
    payload: dict[str, Any] | None = None,
    timeout: float,
) -> dict[str, Any]:
    data = None if payload is None else json.dumps(payload).encode("utf-8")
    try:
        request = urllib.request.Request(
            url,
            data=data,
            method=method,
            headers={"Authorization": f"Bearer {key}", "Content-Type": "application/json"},
        )
        with urllib.request.urlopen(request, timeout=timeout) as response:
            result = json.loads(response.read().decode("utf-8"))
    except json.JSONDecodeError as exc:
        raise AgnesError("Agnes returned invalid JSON") from exc
    except (OSError, ValueError, http.client.HTTPException) as exc:
        raise AgnesError(f"Agnes request failed: {error_category(exc)}") from exc
    if not isinstance(result, dict):
        raise AgnesError("Agnes returned a non-object JSON response")
    return result


def prepare_output(output: Path) -> OutputTarget:
    """Reject collisions and pin/verify the physical parent before submission."""
    parent_fd: int | None = None
    try:
        output = output.expanduser()
        output = output.parent.resolve() / output.name
        try:
            output.lstat()
        except FileNotFoundError:
            pass
        else:
            raise AgnesError(f"output already exists; refusing to overwrite {output}")
        if not DIR_FD_OUTPUT_SUPPORTED:
            raise AgnesError("safe output requires directory-relative no-follow primitives; not supported")

        anchor = output.parent
        missing = []
        while True:
            try:
                expected = anchor.lstat()
                break
            except FileNotFoundError:
                missing.append(anchor.name)
                anchor = anchor.parent
        if not stat.S_ISDIR(expected.st_mode):
            raise AgnesError("output parent is not a verified directory")
        flags = os.O_RDONLY | os.O_DIRECTORY | os.O_NOFOLLOW
        parent_fd = os.open(anchor, flags)
        opened = os.fstat(parent_fd)
        if (opened.st_dev, opened.st_ino) != (expected.st_dev, expected.st_ino):
            raise AgnesError("output parent identity changed during preflight")
        for name in reversed(missing):
            # Missing descendants are created only through the verified ancestor.
            # A concurrently appearing entry is a conflict, never an adopted link.
            os.mkdir(name, dir_fd=parent_fd)
            child_fd = os.open(name, flags, dir_fd=parent_fd)
            os.close(parent_fd)
            parent_fd = child_fd
        target = OutputTarget(output, parent_fd)
        target.check_parent()
        try:
            os.stat(output.name, dir_fd=parent_fd, follow_symlinks=False)
        except FileNotFoundError:
            pass
        else:
            raise AgnesError(f"output already exists; refusing to overwrite {output}")
        target.probe()
        parent_fd = None  # Ownership passes to the returned target.
        return target
    except AgnesError:
        raise
    except (OSError, RuntimeError, ValueError) as exc:
        raise AgnesError(f"cannot prepare output {output}: {error_category(exc)}") from exc
    finally:
        if parent_fd is not None:
            os.close(parent_fd)


def save_bytes(data: bytes, output: OutputTarget | Path) -> None:
    """Publish complete bytes without replacing any entry at the frozen output."""
    if isinstance(output, Path):
        with prepare_output(output) as target:
            save_bytes(data, target)
        return
    temporary: str | None = None
    try:
        try:
            temporary, fd = output.create_private(".agnes-media-", ".tmp")
            with os.fdopen(fd, "wb") as stream:
                stream.write(data)
                stream.flush()
                os.fsync(stream.fileno())
            output.check_parent()
            output.link(temporary, output.path.name)
            output.published = True
            output.check_parent()
        finally:
            if temporary is not None:
                output.unlink(temporary)
    except FileExistsError as exc:
        raise AgnesError(f"output already exists; refusing to overwrite {output}") from exc
    except OSError as exc:
        raise AgnesError(f"cannot save result to {output}: {error_category(exc)}") from exc


def download(url: str, output: OutputTarget | Path, *, timeout: float) -> None:
    if isinstance(output, Path):
        with prepare_output(output) as target:
            download(url, target, timeout=timeout)
        return
    output.check_parent()
    try:
        with urllib.request.urlopen(url, timeout=timeout) as response:
            data = response.read()
    except (OSError, ValueError, http.client.HTTPException) as exc:
        raise AgnesError(f"cannot download result to {output}: {error_category(exc)}") from exc
    save_bytes(data, output)


def save_image_result(result: dict[str, Any], output: OutputTarget | Path, *, timeout: float) -> None:
    if isinstance(output, Path):
        with prepare_output(output) as target:
            save_image_result(result, target, timeout=timeout)
        return
    items = result.get("data")
    if not isinstance(items, list) or not items or not isinstance(items[0], dict):
        raise AgnesError("Agnes image response has no data[0] result")
    first = items[0]
    if isinstance(first.get("url"), str):
        download(first["url"], output, timeout=timeout)
        return
    if isinstance(first.get("b64_json"), str):
        try:
            data = base64.b64decode(first["b64_json"], validate=True)
        except ValueError as exc:
            raise AgnesError(f"cannot decode Base64 image: {error_category(exc)}") from exc
        save_bytes(data, output)
        return
    raise AgnesError("Agnes image response contains neither data[0].url nor data[0].b64_json")


def video_result_url(result: dict[str, Any]) -> str | None:
    if result.get("status") != "completed":
        return None
    metadata = result.get("metadata")
    if not isinstance(metadata, dict):
        return None
    url = metadata.get("url")
    return url if isinstance(url, str) and url else None


def validate_video_response(result: dict[str, Any], *, model: str, video_id: str | None = None) -> None:
    if not isinstance(result.get("status"), str) or result["status"] not in VIDEO_STATES:
        raise AgnesError("Agnes video response has a missing or unknown status")
    if result.get("model") is not None and result["model"] != model:
        raise AgnesError("Agnes video response model does not match the requested model")
    if video_id is not None and result.get("video_id") is not None and result["video_id"] != video_id:
        raise AgnesError("Agnes video response ID does not match the queried task")
    if result["status"] == "failed":
        raise AgnesError("Agnes video generation failed (status=failed)")
    if result["status"] == "completed" and not video_result_url(result):
        raise AgnesError("completed Agnes video response has no metadata.url")


def poll_video(
    initial: dict[str, Any],
    *,
    base_url: str,
    key: str,
    timeout: float,
    poll_interval: float,
    max_wait: float,
    model: str | None = None,
    request: Callable[..., dict[str, Any]] | None = None,
) -> dict[str, Any]:
    video_id = initial.get("video_id")
    selected_model = model or initial.get("model")
    if not video_id:
        raise AgnesError("Agnes response has no video_id; task_id and id are not query IDs")
    result_url = video_query_url(base_url, video_id, selected_model)
    validate_video_response(initial, model=selected_model, video_id=video_id)
    request = request or request_json

    deadline = time.monotonic() + max_wait
    result = initial
    while result.get("status") not in TERMINAL_VIDEO_STATES:
        if time.monotonic() >= deadline:
            raise AgnesError(f"timed out waiting for Agnes video after {max_wait:g} seconds")
        time.sleep(min(poll_interval, max(0.0, deadline - time.monotonic())))
        remaining = deadline - time.monotonic()
        if remaining <= 0:
            raise AgnesError(f"timed out waiting for Agnes video after {max_wait:g} seconds")
        result = request("GET", result_url, key, timeout=min(timeout, remaining))
        validate_video_response(result, model=selected_model, video_id=video_id)
    return result


def dry_run(args: argparse.Namespace, payload: dict[str, Any]) -> dict[str, Any]:
    endpoint = "/v1/images/generations" if args.media == "image" else "/v1/videos"
    request = {"method": "POST", "url": DEFAULT_BASE_URL + endpoint, "payload": payload}
    if args.media == "video-status":
        request = {"method": "GET", "url": video_query_url(DEFAULT_BASE_URL, args.video_id, args.model)}
    return {
        "mode": "dry_run",
        "provider_calls": False,
        "secrets_read": False,
        "request": request,
    }


def preserve_result(
    media: str, initial: dict[str, Any], result: dict[str, Any], output: OutputTarget,
    *, model: str | None = None, mode: str | None = None,
) -> dict[str, Any]:
    """Keep only recovery fields in a private, exclusive, same-parent receipt."""
    retained: dict[str, Any] = {}
    if media == "image":
        items = result.get("data")
        if isinstance(items, list) and items and isinstance(items[0], dict):
            retained["data"] = [
                {name: items[0][name] for name in ("url", "b64_json") if isinstance(items[0].get(name), str)}
            ]
    else:
        for response in (initial, result):
            for name in ("video_id", "task_id", "id", "status"):
                if isinstance(response.get(name), (str, int)):
                    retained[name] = response[name]
        if model in VIDEO_MODELS:
            retained["model"] = model
        if mode in ("text", "keyframe", "reference"):
            retained["mode"] = mode
        url = video_result_url(result)
        if url:
            retained["metadata"] = {"url": url}

    receipt: str | None = None
    recovery: dict[str, Any] = {"automatic_regeneration": False, "retry": "same_result_only"}
    try:
        receipt, fd = output.create_private(".agnes-recovery-", ".json")
        with os.fdopen(fd, "w", encoding="utf-8") as stream:
            json.dump({"media": media, "result": retained}, stream)
            stream.flush()
            os.fsync(stream.fileno())
        output.check_parent()
    except (OSError, AgnesError) as exc:
        recovery.update(status="unavailable", error=str(exc) if isinstance(exc, AgnesError) else error_category(exc))
        if receipt is not None:
            try:
                output.unlink(receipt)
            except OSError:
                recovery["partial_location"] = output.location(receipt)
        return recovery
    recovery.update(status="saved", path=str(output.path.parent / receipt))
    return recovery


def execute(args: argparse.Namespace, payload: dict[str, Any]) -> dict[str, Any]:
    output = prepare_output(args.output) if args.output is not None else None
    provider_calls = False
    try:
        base_url, key = execution_config(args)
        if output is not None:
            output.check_parent()
        base_url = service_root(base_url)
        initial: dict[str, Any] = {}
        result: dict[str, Any] = {}
        try:
            if args.media == "video-status":
                initial = {"video_id": args.video_id, "model": args.model, "status": "queued"}
                result = initial
                if not args.wait:
                    provider_calls = True
                    result = request_json("GET", video_query_url(base_url, args.video_id, args.model), key, timeout=args.timeout)
                    validate_video_response(result, model=args.model, video_id=args.video_id)
            else:
                endpoint = "/v1/images/generations" if args.media == "image" else "/v1/videos"
                provider_calls = True
                result = request_json("POST", base_url + endpoint, key, payload=payload, timeout=args.timeout)
                initial = result
                if args.media == "video":
                    # Check the creation ID before reporting success or starting a wait.
                    video_query_url(base_url, result.get("video_id"), args.model)
            if args.media == "image":
                if output is not None:
                    save_image_result(result, output, timeout=args.timeout)
            elif args.wait:
                provider_calls = True
                result = poll_video(
                    result,
                    base_url=base_url,
                    key=key,
                    timeout=args.timeout,
                    poll_interval=args.poll_interval,
                    max_wait=args.max_wait,
                    model=args.model,
                )
                if output is not None:
                    download(video_result_url(result) or "", output, timeout=args.timeout)
            else:
                validate_video_response(result, model=args.model)
        except AgnesError as exc:
            if output is not None and (initial or result):
                exc.recovery = preserve_result(
                    "image" if args.media == "image" else "video", initial, result, output,
                    model=args.model, mode=getattr(args, "mode", None),
                )
            raise
        return result
    except AgnesError as exc:
        exc.provider_calls = provider_calls
        exc.secrets_read = True  # Configuration was attempted, unlike preflight.
        if output is not None and output.published:
            exc.artifact = {"status": "published_to_bound_parent", **output.location(output.path.name)}
        raise
    finally:
        if output is not None:
            output.close()


def main(argv: list[str] | None = None) -> int:
    try:
        args = parse_args(argv)
        payload = (
            build_image_payload(args, execute=args.execute)
            if args.media == "image"
            else build_video_payload(args) if args.media == "video" else {}
        )
        if not args.execute:
            report = dry_run(args, payload)
        else:
            report = {
                "mode": "execute",
                "provider_calls": True,
                "secrets_read": True,
                "request_context": {"model": args.model, "mode": getattr(args, "mode", None)},
                "result": execute(args, payload),
            }
        print(json.dumps(report, ensure_ascii=False, indent=2))
        return 0
    except AgnesError as exc:
        report = {"error": str(exc), "provider_calls": exc.provider_calls, "secrets_read": exc.secrets_read}
        if exc.recovery is not None:
            report["recovery"] = exc.recovery
        if exc.artifact is not None:
            report["artifact"] = exc.artifact
        print(json.dumps(report, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
