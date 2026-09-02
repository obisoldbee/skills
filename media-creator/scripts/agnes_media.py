#!/usr/bin/env python3
"""Build or execute Agnes Image 2.1 and Video V2 requests.

The CLI is dry-run by default. It reads no credential source and performs no
network request unless ``--execute`` is supplied explicitly.
"""

from __future__ import annotations

import argparse
import base64
import http.client
import json
import mimetypes
import os
import stat
import time
import urllib.error
import urllib.parse
import urllib.request
import uuid
from pathlib import Path
from typing import Any, Callable


DEFAULT_BASE_URL = "https://apihub.agnes-ai.com"
IMAGE_MODEL = "agnes-image-2.1-flash"
VIDEO_MODEL = "agnes-video-v2.0"
TERMINAL_VIDEO_STATES = {"completed", "failed"}
RATIOS = ("1:1", "3:4", "4:3", "16:9", "9:16", "2:3", "3:2", "21:9")
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
        raise AgnesError(f"cannot read input image {path}: {error_category(exc)}") from exc
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
    if frame_rate == int(frame_rate):
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
        raise AgnesError("Agnes video generation failed (status=failed)")
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


def preserve_result(
    media: str, initial: dict[str, Any], result: dict[str, Any], output: OutputTarget
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
        endpoint = "/v1/images/generations" if args.media == "image" else "/v1/videos"
        provider_calls = True
        result = request_json("POST", base_url + endpoint, key, payload=payload, timeout=args.timeout)
        initial = result
        try:
            if args.media == "image":
                if output is not None:
                    save_image_result(result, output, timeout=args.timeout)
            elif args.wait:
                result = poll_video(
                    result,
                    base_url=base_url,
                    key=key,
                    timeout=args.timeout,
                    poll_interval=args.poll_interval,
                    max_wait=args.max_wait,
                )
                if output is not None:
                    download(video_result_url(result) or "", output, timeout=args.timeout)
        except AgnesError as exc:
            if output is not None:
                exc.recovery = preserve_result(args.media, initial, result, output)
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
        report = {"error": str(exc), "provider_calls": exc.provider_calls, "secrets_read": exc.secrets_read}
        if exc.recovery is not None:
            report["recovery"] = exc.recovery
        if exc.artifact is not None:
            report["artifact"] = exc.artifact
        print(json.dumps(report, ensure_ascii=False))
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
