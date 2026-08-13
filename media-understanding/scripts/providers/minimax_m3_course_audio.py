#!/usr/bin/env python3
from __future__ import annotations

import argparse
import base64
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


DEFAULT_ENDPOINT = "https://api.minimaxi.com/anthropic/v1/messages"
DEFAULT_MODEL = "MiniMax-M3"
DEFAULT_ENV_FILE = str(Path.home() / ".codex" / "secrets" / "minimax.env")
MAX_BASE64_CHARACTERS = 50_000_000

DEFAULT_PROMPT = """你正在分析一段课程音频。视频画面只是承载音频的容器，请只根据声音内容判断，不要根据画面、字幕、镜头切换或屏幕内容猜。

课程片段时间范围：{start_time} - {end_time}

请用中文输出结构化语义音频学习笔记：
1. 本段主题：一句话说明这段在讲什么。
2. 关键知识点：列出概念、判断标准、重要结论。
3. 讲解逻辑：说明老师如何从前提推到结论。
4. 音频中的示例与操作暗示：只提取声音里明确说到的案例、步骤、参数、快捷键、注意事项。
5. 疑似原文/术语：列出较有把握听到的关键原句或术语；不能确认时标注“不确定”。
6. 学习行动：给出复习、练习、暂停回看或向视频画面核对的事项。

这不是逐字稿。不要虚构没有听到的内容。不要输出 thinking。不要写“画面提示”“镜头显示”“视频切换”等视觉描述。"""


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
        values[key.strip()] = value.strip().strip('"').strip("'")
    return values


def resolve_api_key(args: argparse.Namespace) -> str | None:
    env = read_env(Path(args.env_file).expanduser())
    return args.api_key or os.environ.get("MINIMAX_API_KEY") or env.get("MINIMAX_API_KEY")


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


def has_stream(probe: dict[str, Any], kind: str) -> bool:
    return any(stream.get("codec_type") == kind for stream in probe.get("streams", []))


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
    return input_path.resolve().parent / f"{input_path.stem}.m3-study" / "audio"


def segment_audio_as_video(input_path: Path, output_dir: Path, duration: float, has_video: bool, args: argparse.Namespace) -> list[dict[str, Any]]:
    ensure_tool("ffmpeg")
    segments_dir = output_dir / "av_segments"
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
        if has_video:
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
                f"scale={args.max_width}:-2,fps={args.encode_fps}",
                "-c:v",
                "libx264",
                "-preset",
                args.preset,
                "-crf",
                str(args.crf),
                "-ac",
                "1",
                "-ar",
                "24000",
                "-c:a",
                "aac",
                "-b:a",
                args.audio_bitrate,
                str(out_path),
            ]
        else:
            cmd = [
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "error",
                "-y",
                "-f",
                "lavfi",
                "-i",
                f"color=c=black:s={args.max_width}x{max(2, args.max_width // 2)}:r={args.encode_fps}",
                "-ss",
                f"{start:.3f}",
                "-i",
                str(input_path),
                "-t",
                f"{length:.3f}",
                "-shortest",
                "-c:v",
                "libx264",
                "-preset",
                args.preset,
                "-crf",
                str(args.crf),
                "-ac",
                "1",
                "-ar",
                "24000",
                "-c:a",
                "aac",
                "-b:a",
                args.audio_bitrate,
                str(out_path),
            ]
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
                "audio_wrapped_as_video": True,
            }
        )
    return segments


def data_url(path: Path) -> str:
    encoded_length = 4 * ((path.stat().st_size + 2) // 3)
    if encoded_length > MAX_BASE64_CHARACTERS:
        fail(f"Base64 video payload exceeds {MAX_BASE64_CHARACTERS} characters: {path}")
    return "data:video/mp4;base64," + base64.b64encode(path.read_bytes()).decode("ascii")


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


def call_m3(api_key: str, endpoint: str, segment_file: Path, prompt: str, args: argparse.Namespace) -> dict[str, Any]:
    payload = {
        "model": args.model,
        "max_tokens": args.max_tokens,
        "temperature": args.temperature,
        "thinking": {"type": "disabled"},
        "messages": [
            {
                "role": "user",
                "content": [
                    {"type": "text", "text": prompt},
                    {"type": "video", "source": {"type": "url", "url": data_url(segment_file)}},
                ],
            }
        ],
    }
    request = urllib.request.Request(
        endpoint,
        data=json.dumps(payload, ensure_ascii=False).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {api_key}",
            "X-Api-Key": api_key,
            "Content-Type": "application/json",
        },
        method="POST",
    )
    try:
        with urllib.request.urlopen(request, timeout=args.timeout) as response:
            return {"ok": True, "status_code": response.status, "body": json.loads(response.read().decode("utf-8", "replace"))}
    except urllib.error.HTTPError as exc:
        text = exc.read().decode("utf-8", "replace")
        try:
            body: Any = json.loads(text)
        except json.JSONDecodeError:
            body = {"raw_text": text}
        return {"ok": False, "status_code": exc.code, "body": body}
    except Exception as exc:  # noqa: BLE001
        return {"ok": False, "error": repr(exc), "body": {}}


def analyze_segments(segments: list[dict[str, Any]], output_dir: Path, api_key: str, endpoint: str, args: argparse.Namespace) -> None:
    responses_dir = output_dir / "responses"
    responses_dir.mkdir(parents=True, exist_ok=True)
    prompt_template = Path(args.prompt_file).read_text(encoding="utf-8") if args.prompt_file else args.prompt
    notes: list[str] = []
    terminal_failure = False
    for segment in segments:
        if terminal_failure:
            segment["status"] = "not_attempted_after_terminal_failure"
            segment["attempts"] = []
            segment["text_chars"] = 0
            segment["thinking_chars"] = 0
            notes.append(
                f"## {segment['start_time']} - {segment['end_time']}\n\n"
                "[NOT ATTEMPTED AFTER TERMINAL PROVIDER FAILURE]\n"
            )
            continue
        index = segment["index"]
        response_path = responses_dir / f"segment_{index:03d}.json"
        note_text = ""
        thinking_text = ""
        if args.resume and response_path.exists():
            saved = json.loads(response_path.read_text(encoding="utf-8"))
            saved_body = saved.get("body", {})
            stop_reason = saved_body.get("stop_reason") if isinstance(saved_body, dict) else None
            if stop_reason != "max_tokens":
                note_text, thinking_text = extract_text(saved_body)
                if note_text:
                    segment["status"] = "cached"
        attempts: list[dict[str, Any]] = []
        if not note_text:
            prompt = render_prompt(prompt_template, segment)
            for attempt in range(1, args.retries + 1):
                result = call_m3(api_key, endpoint, Path(segment["file"]), prompt, args)
                body = result.get("body", {})
                text, thinking = extract_text(body if isinstance(body, dict) else {})
                attempts.append(
                    {
                        "attempt": attempt,
                        "status_code": result.get("status_code"),
                        "ok": result.get("ok", False),
                        "error": error_message(result),
                        "stop_reason": body.get("stop_reason") if isinstance(body, dict) else None,
                        "usage": body.get("usage", {}) if isinstance(body, dict) else {},
                        "text_chars": len(text),
                        "thinking_chars": len(thinking),
                    }
                )
                response_path.write_text(json.dumps(result, ensure_ascii=False, indent=2), encoding="utf-8")
                if result.get("ok") and text:
                    note_text, thinking_text = text, thinking
                    segment["status"] = "success"
                    break
                if is_1026_error(attempts[-1].get("error")):
                    segment["status"] = "m3_blocked_1026_provider_fallback_requires_user_opt_in"
                    terminal_failure = True
                    break
                time.sleep(args.retry_sleep)
        if not note_text:
            segment["status"] = segment.get("status") or "failed_or_empty"
            note_text = "[EMPTY_OR_FAILED]"
        segment["response_file"] = str(response_path)
        segment["attempts"] = attempts or segment.get("attempts", [])
        segment["text_chars"] = len(note_text)
        segment["thinking_chars"] = len(thinking_text)
        notes.append(f"## {segment['start_time']} - {segment['end_time']}\n\n{note_text}\n")
    (output_dir / "audio_notes.md").write_text("# MiniMax-M3 Audio Course Notes\n\n" + "\n".join(notes), encoding="utf-8")


def main() -> None:
    parser = argparse.ArgumentParser(description="Prepare/analyze course audio through MiniMax-M3 video input.")
    parser.add_argument("--input", required=True)
    parser.add_argument("--output-dir")
    parser.add_argument("--analyze", action="store_true")
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--api-key")
    parser.add_argument("--env-file", default=DEFAULT_ENV_FILE)
    parser.add_argument("--base-url")
    parser.add_argument("--endpoint", default=DEFAULT_ENDPOINT)
    parser.add_argument("--model", default=DEFAULT_MODEL)
    parser.add_argument("--segment-seconds", type=float, default=300.0)
    parser.add_argument("--overlap-seconds", type=float, default=5.0)
    parser.add_argument("--encode-fps", type=float, default=3.0)
    parser.add_argument("--max-width", type=int, default=640)
    parser.add_argument("--crf", type=int, default=32)
    parser.add_argument("--preset", default="veryfast")
    parser.add_argument("--audio-bitrate", default="48k")
    parser.add_argument("--prompt", default=DEFAULT_PROMPT)
    parser.add_argument("--prompt-file")
    parser.add_argument("--max-tokens", type=int, default=1800)
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
    if not has_stream(probe, "audio"):
        (output_dir / "audio_notes.md").write_text("# MiniMax-M3 Audio Course Notes\n\nno_speech_or_no_audio_detected\n", encoding="utf-8")
        print(output_dir)
        return
    duration = duration_seconds(probe)
    segments = segment_audio_as_video(input_path, output_dir, duration, has_stream(probe, "video"), args)
    manifest = {
        "kind": "minimax-m3-course-audio-understanding",
        "generated_at": datetime.now().isoformat(timespec="seconds"),
        "source": str(input_path),
        "source_duration_seconds": duration,
        "model": args.model,
        "endpoint": resolve_endpoint(args),
        "thinking": {"type": "disabled"},
        "audio_input_mode": "audio_wrapped_as_low_detail_video",
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
        analysis_failed = any(segment.get("status") not in {"success", "cached"} for segment in segments)
    (output_dir / "manifest.json").write_text(json.dumps(manifest, ensure_ascii=False, indent=2), encoding="utf-8")
    print(output_dir)
    if analysis_failed:
        print("error: MiniMax-M3 audio analysis failed; see manifest and response files", file=sys.stderr)
        raise SystemExit(1)


if __name__ == "__main__":
    main()
