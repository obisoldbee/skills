#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
import shutil
import subprocess
import sys
import time
import urllib.error
import urllib.request
from datetime import datetime
from pathlib import Path
from typing import Any


PROVIDERS_DIR = Path(__file__).resolve().parent
if str(PROVIDERS_DIR) not in sys.path:
    sys.path.insert(0, str(PROVIDERS_DIR))

from minimax_request_state import (  # noqa: E402
    atomic_write_json,
    classify_response,
    last_verified_response,
    load_operation,
    operation_fingerprint,
    provider_request_id,
    response_reference,
    resume_disposition,
)


DEFAULT_ENDPOINT = "https://api.minimaxi.com/anthropic/v1/messages"
DEFAULT_MODEL = "MiniMax-M3"
DEFAULT_ENV_FILE = str(Path.home() / ".codex" / "secrets" / "minimax.env")
MAX_BASE64_CHARACTERS = 50_000_000

DEFAULT_PROMPT = """你正在分析一段课程视频画面。

课程片段时间范围：{start_time} - {end_time}

请用中文输出结构化视觉学习笔记：
1. 本段画面主题：一句话说明这段主要展示了什么。
2. 可见信息：提取屏幕文字、标题、代码、菜单、参数、时间线、工具面板、图表或示例素材。
3. 操作步骤：按时间顺序描述老师在画面中演示的动作，尽量写成可以复现的步骤。
4. 视觉证据：指出哪些结论来自画面，而不是来自音频推测。
5. 不确定项：列出看不清、太快、被遮挡或需要复查的地方。
6. 学习行动：给出暂停回看点、截图点、练习任务和需要与音频/ASR核对的问题。

只基于画面可见内容，不要根据音频或常识补全。
不要输出思考过程、草稿、Self-Correction、Analyze the User Request。"""


def fail(message: str) -> None:
    print(f"error: {message}", file=sys.stderr)
    raise SystemExit(1)


def run(cmd: list[str]) -> subprocess.CompletedProcess[str]:
    return subprocess.run(cmd, check=True, text=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)


def ensure_tool(name: str) -> None:
    if not shutil.which(name):
        fail(f"{name} is required but was not found on PATH")


def read_env(path: Path) -> dict[str, str]:
    values: dict[str, str] = {}
    if not path.exists():
        return values
    for raw_line in path.read_text(encoding="utf-8").splitlines():
        line = raw_line.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[len("export ") :].strip()
        if "=" not in line:
            continue
        key, value = line.split("=", 1)
        value = value.strip().strip('"').strip("'")
        values[key.strip()] = value
    return values


def resolve_api_key(args: argparse.Namespace) -> str | None:
    env = read_env(Path(args.env_file).expanduser())
    key = args.api_key or os.environ.get("MINIMAX_API_KEY") or env.get("MINIMAX_API_KEY")
    if key and key.strip().lower() in {"", "your-key", "replace_with_your_minimax_api_key"}:
        fail("MiniMax API key is still a placeholder")
    return key


def resolve_endpoint(args: argparse.Namespace) -> str:
    env = read_env(Path(args.env_file).expanduser())
    base_url = args.base_url or os.environ.get("MINIMAX_BASE_URL") or env.get("MINIMAX_BASE_URL")
    if base_url:
        normalized = base_url.rstrip("/")
        if normalized.endswith("/anthropic/v1/messages"):
            return normalized
        if normalized.endswith("/anthropic"):
            return normalized + "/v1/messages"
        return normalized + "/anthropic/v1/messages"
    return args.endpoint


def ffprobe(path: Path) -> dict[str, Any]:
    ensure_tool("ffprobe")
    try:
        return json.loads(
            run(
                [
                    "ffprobe",
                    "-v",
                    "error",
                    "-print_format",
                    "json",
                    "-show_format",
                    "-show_streams",
                    str(path),
                ]
            ).stdout
        )
    except subprocess.CalledProcessError as exc:
        fail(f"ffprobe failed: {exc.stderr.strip()}")
    except json.JSONDecodeError as exc:
        fail(f"ffprobe returned invalid JSON: {exc}")


def first_stream(probe: dict[str, Any], kind: str) -> dict[str, Any] | None:
    for stream in probe.get("streams", []):
        if stream.get("codec_type") == kind:
            return stream
    return None


def duration_seconds(probe: dict[str, Any]) -> float:
    value = probe.get("format", {}).get("duration")
    if value is not None:
        return float(value)
    for stream in probe.get("streams", []):
        value = stream.get("duration")
        if value is not None:
            return float(value)
    fail("could not determine duration")


def fmt_time(seconds: float) -> str:
    seconds = max(0.0, float(seconds))
    whole = int(seconds)
    ms = int(round((seconds - whole) * 1000))
    if ms == 1000:
        whole += 1
        ms = 0
    return f"{whole // 3600:02d}:{(whole % 3600) // 60:02d}:{whole % 60:02d}.{ms:03d}"


def render_prompt(template: str, segment: dict[str, Any]) -> str:
    text = template
    for key in ("start_time", "end_time", "start_seconds", "end_seconds", "duration_seconds"):
        text = text.replace("{" + key + "}", str(segment[key]))
    return text


def build_output_dir(input_path: Path, output_dir: str | None) -> Path:
    if output_dir:
        return Path(output_dir).expanduser().resolve()
    return input_path.resolve().parent / f"{input_path.stem}.m3-study" / "video"


def segment_video(input_path: Path, output_dir: Path, duration: float, source_width: int, args: argparse.Namespace) -> list[dict[str, Any]]:
    ensure_tool("ffmpeg")
    segments_dir = output_dir / "video_segments"
    segments_dir.mkdir(parents=True, exist_ok=True)
    if args.segment_seconds <= 0 or args.overlap_seconds < 0 or args.overlap_seconds >= args.segment_seconds:
        fail("invalid segment/overlap seconds")
    starts: list[float] = []
    current = 0.0
    stride = args.segment_seconds - args.overlap_seconds
    while current < duration:
        starts.append(current)
        current += stride

    segments: list[dict[str, Any]] = []
    for index, start in enumerate(starts):
        end = min(duration, start + args.segment_seconds)
        length = max(0.01, end - start)
        out_path = segments_dir / f"segment_{index:03d}.mp4"
        scale_expr = f"scale={args.max_width}:-2" if source_width > args.max_width else "scale=trunc(iw/2)*2:trunc(ih/2)*2"
        cmd = [
            "ffmpeg",
            "-hide_banner",
            "-loglevel",
            "error",
            "-y",
            "-ss",
            f"{start:.3f}",
            "-i",
            str(input_path),
            "-t",
            f"{length:.3f}",
            "-vf",
            f"scale=trunc(iw/2)*2:trunc(ih/2)*2,fps={args.encode_fps},{scale_expr}",
            "-c:v",
            "libx264",
            "-preset",
            args.preset,
            "-crf",
            str(args.crf),
        ]
        if args.keep_audio:
            cmd += ["-ac", "1", "-ar", "24000", "-c:a", "aac", "-b:a", args.audio_bitrate]
        else:
            cmd += ["-an"]
        cmd.append(str(out_path))
        try:
            run(cmd)
        except subprocess.CalledProcessError as exc:
            fail(f"ffmpeg failed while creating {out_path}: {exc.stderr.strip()}")
        segments.append(
            {
                "index": index,
                "file": str(out_path),
                "start_seconds": round(start, 3),
                "end_seconds": round(end, 3),
                "start_time": fmt_time(start),
                "end_time": fmt_time(end),
                "duration_seconds": round(length, 3),
                "size_bytes": out_path.stat().st_size,
                "muted": not args.keep_audio,
            }
        )
    return segments


def read_media_bytes(path: Path) -> bytes:
    encoded_length = 4 * ((path.stat().st_size + 2) // 3)
    if encoded_length > MAX_BASE64_CHARACTERS:
        fail(f"Base64 video payload exceeds {MAX_BASE64_CHARACTERS} characters: {path}")
    return path.read_bytes()


def data_url(path: Path) -> str:
    return data_url_bytes(read_media_bytes(path), path)


def data_url_bytes(source_bytes: bytes, path: Path) -> str:
    encoded_length = 4 * ((len(source_bytes) + 2) // 3)
    if encoded_length > MAX_BASE64_CHARACTERS:
        fail(f"Base64 video payload exceeds {MAX_BASE64_CHARACTERS} characters: {path}")
    return "data:video/mp4;base64," + base64.b64encode(source_bytes).decode("ascii")


def extract_text(response: dict[str, Any]) -> tuple[str, str]:
    texts: list[str] = []
    thinking: list[str] = []
    for block in response.get("content", []) or []:
        if not isinstance(block, dict):
            continue
        if block.get("type") == "text":
            texts.append(block.get("text") or "")
        elif block.get("type") == "thinking":
            thinking.append(block.get("thinking") or block.get("text") or "")
    return "\n\n".join(t for t in texts if t.strip()).strip(), "\n\n".join(t for t in thinking if t.strip()).strip()


def error_message(result: dict[str, Any]) -> str | None:
    direct = result.get("error")
    if direct:
        return str(direct)
    body = result.get("body")
    if not isinstance(body, dict):
        return None
    error = body.get("error")
    if isinstance(error, dict):
        return str(error.get("message") or error.get("type") or error)
    if error:
        return str(error)
    raw_text = body.get("raw_text")
    return str(raw_text) if raw_text else None


def is_1026_error(message: str | None) -> bool:
    return bool(message and ("1026" in message or "input new_sensitive" in message))


def build_payload(
    model: str,
    segment_file: Path,
    prompt: str,
    args: argparse.Namespace,
    source_bytes: bytes | None = None,
) -> dict[str, Any]:
    media_bytes = read_media_bytes(segment_file) if source_bytes is None else source_bytes
    return {
        "model": model,
        "max_tokens": args.max_tokens,
        "temperature": args.temperature,
        "thinking": {"type": "disabled"},
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "video", "source": {"type": "url", "url": data_url_bytes(media_bytes, segment_file)}},
                ],
            }
        ],
    }


def operation_descriptor(
    model: str,
    segment_file: Path,
    prompt: str,
    args: argparse.Namespace,
    media_bytes: bytes | None = None,
) -> dict[str, Any]:
    if media_bytes is not None:
        source_size = len(media_bytes)
        source_sha256 = hashlib.sha256(media_bytes).hexdigest()
    elif segment_file.is_file():
        observed_bytes = read_media_bytes(segment_file)
        source_size = len(observed_bytes)
        source_sha256 = hashlib.sha256(observed_bytes).hexdigest()
    else:
        source_size = None
        source_sha256 = "unavailable"
    return {
        "model": model,
        "prompt": prompt,
        "max_tokens": args.max_tokens,
        "temperature": args.temperature,
        "thinking": {"type": "disabled"},
        "source_file": str(segment_file),
        "source_bytes": source_size,
        "source_sha256": source_sha256,
        "media_type": "video/mp4",
    }


def call_m3(
    api_key: str,
    endpoint: str,
    model: str,
    segment_file: Path,
    prompt: str,
    args: argparse.Namespace,
    media_bytes: bytes | None = None,
) -> dict[str, Any]:
    source_bytes = read_media_bytes(segment_file) if media_bytes is None else media_bytes
    payload = build_payload(model, segment_file, prompt, args, source_bytes)
    fingerprint = operation_fingerprint(
        endpoint,
        operation_descriptor(model, segment_file, prompt, args, source_bytes),
    )
    body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    request = urllib.request.Request(
        endpoint,
        data=body,
        headers={
            "Authorization": f"Bearer {api_key}",
            "X-Api-Key": api_key,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=args.timeout) as response:
            raw_text = response.read().decode("utf-8", "replace")
            try:
                body_obj: Any = json.loads(raw_text) if raw_text.strip() else {}
            except json.JSONDecodeError:
                body_obj = {"raw_text": raw_text}
            return {
                "ok": True,
                "status_code": response.status,
                "body": body_obj,
                "operation_fingerprint": fingerprint,
                "provider_request_id": provider_request_id(body_obj, response.headers),
            }
    except urllib.error.HTTPError as exc:
        text = exc.read().decode("utf-8", "replace")
        try:
            body_obj: Any = json.loads(text)
        except json.JSONDecodeError:
            body_obj = {"raw_text": text}
        return {
            "ok": False,
            "status_code": exc.code,
            "body": body_obj,
            "operation_fingerprint": fingerprint,
            "provider_request_id": provider_request_id(body_obj, exc.headers),
        }
    except Exception as exc:  # noqa: BLE001
        return {
            "ok": False,
            "error": repr(exc),
            "body": {},
            "operation_fingerprint": fingerprint,
            "provider_request_id": None,
        }


def analyze_segments(segments: list[dict[str, Any]], output_dir: Path, api_key: str, endpoint: str, args: argparse.Namespace) -> None:
    responses_dir = output_dir / "responses"
    responses_dir.mkdir(parents=True, exist_ok=True)
    notes_path = output_dir / "video_notes.md"
    prompt_template = Path(args.prompt_file).read_text(encoding="utf-8") if args.prompt_file else args.prompt
    notes: list[str] = []
    terminal_failure = False
    for segment in segments:
        if terminal_failure:
            segment["status"] = "not_attempted_after_terminal_failure"
            segment["request_state"] = "not_sent"
            segment["retry_disposition"] = "not_sent_due_to_prior_terminal_state"
            segment["attempts"] = []
            segment["text_chars"] = 0
            segment["thinking_chars"] = 0
            notes.append(
                f"## {segment['start_time']} - {segment['end_time']}\n\n"
                "[NOT ATTEMPTED AFTER TERMINAL PROVIDER FAILURE]\n"
            )
            continue
        index = segment["index"]
        operation_dir = responses_dir / f"segment_{index:03d}"
        operation_path = operation_dir / "operation.json"
        note_text = ""
        thinking_text = ""
        prompt = render_prompt(prompt_template, segment)
        segment_path = Path(segment["file"])
        media_bytes = read_media_bytes(segment_path) if segment_path.is_file() else None
        fingerprint = operation_fingerprint(
            endpoint,
            operation_descriptor(args.model, segment_path, prompt, args, media_bytes),
        )
        saved_operation = load_operation(operation_path)
        if saved_operation and saved_operation.get("operation_fingerprint") != fingerprint:
            segment["status"] = "operation_fingerprint_mismatch_no_resubmit"
            segment["operation_fingerprint"] = fingerprint
            segment["saved_operation_fingerprint"] = saved_operation.get("operation_fingerprint")
            segment["attempts"] = list(saved_operation.get("attempts") or [])
            segment["request_state"] = "not_sent"
            segment["retry_disposition"] = "operation_fingerprint_mismatch_no_resubmit"
            segment["text_chars"] = 0
            segment["thinking_chars"] = 0
            notes.append(
                f"## {segment['start_time']} - {segment['end_time']}\n\n"
                "[OPERATION FINGERPRINT MISMATCH; NOT RESUBMITTED]\n"
            )
            terminal_failure = True
            continue
        if saved_operation and not args.resume:
            segment["status"] = "existing_operation_requires_resume_no_resubmit"
            segment["operation_fingerprint"] = fingerprint
            segment["attempts"] = list(saved_operation.get("attempts") or [])
            segment["request_state"] = saved_operation["state"]
            segment["retry_disposition"] = "existing_operation_requires_explicit_resume"
            segment["text_chars"] = 0
            segment["thinking_chars"] = 0
            notes.append(
                f"## {segment['start_time']} - {segment['end_time']}\n\n"
                "[EXISTING OPERATION; USE --resume; NOT RESUBMITTED]\n"
            )
            terminal_failure = True
            continue

        disposition = resume_disposition(saved_operation, operation_dir) if args.resume else "new_operation"
        attempts: list[dict[str, Any]] = list(saved_operation.get("attempts") or []) if saved_operation else []
        if saved_operation and disposition == "reuse_completed":
            try:
                saved = last_verified_response(saved_operation, operation_dir, "completed")
                note_text, thinking_text = extract_text(saved.get("body", {}))
            except (OSError, ValueError):
                note_text = ""
            if note_text:
                segment["status"] = "cached_completed"
            else:
                segment["status"] = "completed_evidence_missing_no_resubmit"
                terminal_failure = True
        elif saved_operation and disposition in {"resume_without_resubmit", "resume_terminal_without_resubmit"}:
            segment["status"] = (
                "completed_evidence_missing_no_resubmit"
                if saved_operation["state"] == "completed"
                else f"resume_{saved_operation['state']}_no_resubmit"
            )
            terminal_failure = saved_operation["state"] in {"accepted", "acceptance_unknown", "completed"} or any(
                is_1026_error(attempt.get("error")) for attempt in attempts
            )

        if not note_text and disposition != "reuse_completed":
            for attempt in range(len(attempts) + 1, args.retries + 1):
                if saved_operation and disposition in {"resume_without_resubmit", "resume_terminal_without_resubmit"}:
                    break
                response_path = operation_dir / f"attempt_{attempt:02d}.json"
                if response_path.exists() or response_path.is_symlink():
                    raise RuntimeError(
                        f"response evidence already exists; refusing to overwrite: {response_path}"
                    )
                # Persist the conservative state before POST. If the process is
                # interrupted anywhere after this write, resume must not infer
                # that the provider never accepted the request.
                atomic_write_json(
                    operation_path,
                    {
                        "schema": "media-understanding/provider-operation/v1",
                        "operation_fingerprint": fingerprint,
                        "state": "acceptance_unknown",
                        "retry_disposition": "submission_started_acceptance_unknown_no_resubmit",
                        "provider_request_id": None,
                        "usage": {},
                        "submission_attempt": attempt,
                        "attempts": attempts,
                        "response_evidence": [item["response_evidence"] for item in attempts],
                    },
                )
                result = call_m3(api_key, endpoint, args.model, segment_path, prompt, args, media_bytes)
                body = result.get("body", {})
                text, thinking = extract_text(body if isinstance(body, dict) else {})
                state, retry_disposition = classify_response(result, text)
                observed_fingerprint = result.get("operation_fingerprint")
                if observed_fingerprint is not None and observed_fingerprint != fingerprint:
                    state = "acceptance_unknown"
                    retry_disposition = "operation_fingerprint_changed_after_submit_no_resubmit"
                    result["expected_operation_fingerprint"] = fingerprint
                else:
                    result["operation_fingerprint"] = fingerprint
                result["request_state"] = state
                result["retry_disposition"] = retry_disposition
                atomic_write_json(response_path, result)
                evidence_reference = response_reference(response_path, operation_dir)
                attempt_receipt = {
                    "attempt": attempt,
                    "state": state,
                    "status_code": result.get("status_code"),
                    "ok": result.get("ok", False),
                    "error": error_message(result),
                    "stop_reason": body.get("stop_reason") if isinstance(body, dict) else None,
                    "provider_request_id": result.get("provider_request_id"),
                    "expected_operation_fingerprint": fingerprint,
                    "observed_operation_fingerprint": observed_fingerprint,
                    "usage": body.get("usage", {}) if isinstance(body, dict) else {},
                    "text_chars": len(text),
                    "thinking_chars": len(thinking),
                    "retry_disposition": retry_disposition,
                    "response_evidence": evidence_reference,
                }
                attempts.append(attempt_receipt)
                operation = {
                    "schema": "media-understanding/provider-operation/v1",
                    "operation_fingerprint": fingerprint,
                    "observed_operation_fingerprint": observed_fingerprint,
                    "state": state,
                    "retry_disposition": retry_disposition,
                    "provider_request_id": result.get("provider_request_id"),
                    "usage": attempt_receipt["usage"],
                    "attempts": attempts,
                    "response_evidence": [item["response_evidence"] for item in attempts],
                }
                atomic_write_json(operation_path, operation)
                if state == "completed":
                    note_text, thinking_text = text, thinking
                    segment["status"] = "success"
                    break
                if is_1026_error(attempt_receipt.get("error")):
                    segment["status"] = "m3_blocked_1026_provider_fallback_requires_user_opt_in"
                    terminal_failure = True
                    break
                if retry_disposition == "retry_allowed_proven_not_accepted" and attempt < args.retries:
                    time.sleep(args.retry_sleep)
                    continue
                if state == "accepted":
                    segment["status"] = "m3_accepted_empty_result_no_resubmit"
                elif state == "acceptance_unknown":
                    segment["status"] = "m3_acceptance_unknown_no_resubmit"
                elif state == "rejected":
                    segment["status"] = f"m3_rejected_{result.get('status_code', 'request')}"
                else:
                    segment["status"] = "m3_not_sent"
                terminal_failure = state in {"accepted", "acceptance_unknown"}
                break
        if not note_text:
            segment["status"] = segment.get("status") or "failed_or_empty"
            note_text = "[EMPTY_OR_FAILED]"
        segment["operation_file"] = str(operation_path)
        segment["operation_fingerprint"] = fingerprint
        segment["request_state"] = (
            load_operation(operation_path).get("state") if operation_path.is_file() else "not_sent"
        )
        segment["retry_disposition"] = (
            load_operation(operation_path).get("retry_disposition")
            if operation_path.is_file()
            else "retry_allowed_proven_not_sent"
        )
        segment["attempts"] = attempts or segment.get("attempts", [])
        segment["response_files"] = [
            str(operation_dir / reference["path"])
            for item in segment["attempts"]
            if isinstance((reference := item.get("response_evidence")), dict)
            and isinstance(reference.get("path"), str)
        ]
        segment["text_chars"] = len(note_text)
        segment["thinking_chars"] = len(thinking_text)
        notes.append(f"## {segment['start_time']} - {segment['end_time']}\n\n{note_text}\n")
    notes_path.write_text("# MiniMax-M3 Video Course Notes\n\n" + "\n".join(notes), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare/analyze course video chunks with MiniMax-M3.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output-dir")
    parser.add_argument("--analyze", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--api-key")
    parser.add_argument("--env-file", default=DEFAULT_ENV_FILE)
    parser.add_argument("--base-url")
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--segment-seconds", type=float, default=120.0)
    parser.add_argument("--overlap-seconds", type=float, default=2.0)
    parser.add_argument("--encode-fps", type=float, default=6.0)
    parser.add_argument("--max-width", type=int, default=960)
    parser.add_argument("--crf", type=int, default=30)
    parser.add_argument("--preset", default="veryfast")
    parser.add_argument("--keep-audio", action="store_true")
    parser.add_argument("--audio-bitrate", default="48k")
    parser.add_argument("--prompt", default=DEFAULT_PROMPT)
    parser.add_argument("--prompt-file")
    parser.add_argument("--max-tokens", type=int, default=2200)
    parser.add_argument("--temperature", type=float, default=0.1)
    parser.add_argument("--timeout", type=int, default=300)
    parser.add_argument("--retries", type=int, default=3)
    parser.add_argument("--retry-sleep", type=float, default=2.0)
    args = parser.parse_args()

    input_path = Path(args.input).expanduser().resolve()
    if not input_path.exists():
        fail(f"input not found: {input_path}")
    output_dir = build_output_dir(input_path, args.output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)
    probe = ffprobe(input_path)
    stream = first_stream(probe, "video")
    if not stream:
        fail("input has no video stream")
    duration = duration_seconds(probe)
    segments = segment_video(input_path, output_dir, duration, int(stream.get("width", 0)), args)

    manifest = {
        "kind": "minimax-m3-course-video-understanding",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source": str(input_path),
        "source_duration_seconds": duration,
        "source_width": stream.get("width"),
        "source_height": stream.get("height"),
        "model": args.model,
        "endpoint": resolve_endpoint(args),
        "thinking": {"type": "disabled"},
        "segment_seconds": args.segment_seconds,
        "overlap_seconds": args.overlap_seconds,
        "encode_fps": args.encode_fps,
        "max_width": args.max_width,
        "crf": args.crf,
        "api_called": bool(args.analyze),
        "segments": segments,
    }
    analysis_failed = False
    if args.analyze:
        api_key = resolve_api_key(args)
        if not api_key:
            fail("MINIMAX_API_KEY is required for --analyze")
        analyze_segments(segments, output_dir, api_key, manifest["endpoint"], args)
        analysis_failed = any(segment.get("status") not in {"success", "cached_completed"} for segment in segments)
    (output_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(output_dir)
    if analysis_failed:
        print("error: MiniMax-M3 video analysis failed; see manifest and response files", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
