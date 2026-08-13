#!/usr/bin/env python3
"""Build an offline, self-contained model-by-image human review matrix.

The input contract is defined in ../references/benchmark-contract.md:

  build_review_matrix.py --manifest manifest.json \
      --results normalized/results.json --output review/visual-output-review.html

The command is review-only. It reads manifest/result evidence, validates the
exact participant-case union, embeds source images as data URLs, and writes one
portable HTML file. It never invokes a provider or changes benchmark results.
"""

from __future__ import annotations

import argparse
import base64
import hashlib
import json
import mimetypes
import re
import sys
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


MANIFEST_SCHEMAS = {"visual-model-benchmark/v1", "visual-model-benchmark/v2"}
RESULTS_SCHEMA = "visual-model-results/v1"
EXPORT_SCHEMA = "akashic-visual-output-review-rankings/v1"
DATA_SCHEMA = "visual-model-review-matrix-data/v1"
TERMINAL_STATUSES = {"success", "failed", "not_run"}

HUMAN_FIELD_ORDER = (
    "visual_summary",
    "verbatim_text",
    "claims_or_facts",
    "likely_use_in_bookmark_workflow",
    "likely_use_in_workflow",
    "likely_use_in_bookflow",
    "needs_article_context",
    "uncertainties",
    "layout",
)

HUMAN_FIELD_LABELS = {
    "visual_summary": "画面概述",
    "verbatim_text": "识别文字",
    "claims_or_facts": "关键信息",
    "likely_use_in_bookmark_workflow": "可能用途",
    "likely_use_in_workflow": "可能用途",
    "likely_use_in_bookflow": "可能用途",
    "needs_article_context": "仍需上下文",
    "uncertainties": "不确定项",
    "layout": "版式关系",
}


def strip_code_fence(text: str) -> str:
    candidate = text.strip()
    if candidate.startswith("```"):
        candidate = re.sub(r"^```(?:json)?\s*", "", candidate, flags=re.IGNORECASE)
        candidate = re.sub(r"\s*```$", "", candidate)
    return candidate


def parse_json_string(text: str) -> Any | None:
    candidate = strip_code_fence(text)
    if not candidate.startswith(("{", "[")):
        return None
    try:
        return json.loads(candidate)
    except json.JSONDecodeError:
        return None


def readable_list(values: list[Any]) -> list[str]:
    lines: list[str] = []
    for value in values:
        if isinstance(value, dict):
            region = str(value.get("region", "")).strip()
            content = str(value.get("content", "")).strip()
            relation = str(value.get("relation", "")).strip()
            main = "：".join(part for part in (region, content) if part)
            if relation:
                main = f"{main}（{relation}）" if main else relation
            if main:
                lines.append(f"• {main}")
        elif isinstance(value, (str, int, float)) and str(value).strip():
            lines.append(f"• {str(value).strip()}")
    return lines


def humanize_structured(value: Any) -> str | None:
    if isinstance(value, dict) and "model_response" in value:
        value = value["model_response"]
    if not isinstance(value, dict):
        return None
    sections: list[str] = []
    emitted_labels: set[str] = set()
    for key in HUMAN_FIELD_ORDER:
        field = value.get(key)
        if field in (None, "", [], {}):
            continue
        label = HUMAN_FIELD_LABELS[key]
        if label in emitted_labels and label == "可能用途":
            continue
        emitted_labels.add(label)
        if isinstance(field, list):
            content = "\n".join(readable_list(field))
        elif isinstance(field, dict):
            content = humanize_structured(field) or ""
        else:
            content = str(field).strip()
        if content:
            sections.append(f"{label}\n{content}")
    return "\n\n".join(sections) or None


def humanize_jsonish_text(text: str) -> str:
    """Render a truncated structured response without JSON control machinery."""
    labels = HUMAN_FIELD_LABELS | {"region": "区域", "content": "内容", "relation": "关系"}
    skipped = {"case_id", "image_type", "confidence"}
    output: list[str] = []
    for raw_line in text.splitlines():
        line = raw_line.strip()
        if not line or line in {"{", "}", "[", "]", "},", "],"}:
            continue
        match = re.match(r'^"([^"]+)"\s*:\s*(.*)$', line)
        if match:
            key, remainder = match.groups()
            if key in skipped:
                continue
            if key in labels:
                output.append(labels[key])
                remainder = remainder.strip()
                if remainder not in {"", "[", "{", "[],", "{},"}:
                    cleaned = remainder.rstrip(",").strip().strip('"')
                    if cleaned:
                        output.append(cleaned)
                continue
        cleaned = line.rstrip(",").strip()
        if cleaned.startswith('"') and cleaned.endswith('"'):
            cleaned = cleaned[1:-1]
        cleaned = cleaned.replace('\\"', '"')
        if cleaned and cleaned not in {"{", "}", "[", "]"}:
            output.append(f"• {cleaned}" if raw_line.lstrip().startswith('"') else cleaned)
    return "\n".join(output).strip()


def clean_ocr_text(text: str) -> str:
    cleaned = re.sub(r"<\|det\|>.*?<\|/det\|>", "", text, flags=re.DOTALL)
    cleaned = re.sub(r"!\[[^\]]*\]\([^\)]+\)", "", cleaned)
    cleaned = re.sub(r"(?m)^\s{0,3}#{1,6}\s*", "", cleaned)
    cleaned = cleaned.replace("**", "").replace("__", "").replace("`", "")
    cleaned = re.sub(r"(?m)^\s*[-*+]\s+", "• ", cleaned)
    cleaned = re.sub(r"[ \t]+\n", "\n", cleaned)
    cleaned = re.sub(r"\n{3,}", "\n\n", cleaned)
    return cleaned.strip()


def humanize_output(raw_text: str, track: str) -> tuple[str, str]:
    parsed = parse_json_string(raw_text)
    structured = humanize_structured(parsed) if parsed is not None else None
    if structured:
        return structured, "结构化视觉结果已转换为人类可读标签"
    if track.lower() == "ocr":
        return clean_ocr_text(raw_text), "OCR 检测标记、坐标、图像占位和装饰性 Markdown 已隐藏"
    jsonish = strip_code_fence(raw_text)
    if jsonish.lstrip().startswith("{"):
        fallback = humanize_jsonish_text(jsonish)
        if fallback:
            return fallback, "截断的结构化结果已移除 JSON 控制字段"
    return raw_text.strip(), "模型原生正文"


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_json(path: Path) -> dict[str, Any]:
    try:
        with path.open(encoding="utf-8") as handle:
            document = json.load(handle)
    except (OSError, json.JSONDecodeError) as error:
        raise ValueError(f"cannot read JSON {path}: {error}") from error
    if not isinstance(document, dict):
        raise ValueError(f"{path}: expected a JSON object")
    return document


def required_string(value: Any, label: str) -> str:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{label}: expected a non-empty string")
    return value


def resolve_image(manifest_path: Path, image_path: str) -> Path:
    candidate = Path(image_path)
    return candidate if candidate.is_absolute() else (manifest_path.parent / candidate).resolve()


def image_data(case: dict[str, Any], manifest_path: Path) -> dict[str, Any]:
    case_id = required_string(case.get("case_id"), "manifest case_id")
    media_kind = str(case.get("media_kind", "image")).strip().lower()
    if media_kind != "image":
        raise ValueError(
            f"{case_id}: build_review_matrix.py supports image cases only; "
            f"use the video review contract for media_kind={media_kind!r}"
        )
    image_path = required_string(
        case.get("media_path", case.get("image_path")),
        f"{case_id}.media_path",
    )
    declared_hash = required_string(case.get("sha256"), f"{case_id}.sha256").lower()
    media_type = required_string(case.get("media_type"), f"{case_id}.media_type")
    if not media_type.startswith("image/"):
        raise ValueError(f"{case_id}: media_type must be image/*, got {media_type!r}")
    resolved = resolve_image(manifest_path, image_path)
    if not resolved.is_file():
        raise ValueError(f"{case_id}: image_path does not exist: {resolved}")
    actual_hash = sha256(resolved)
    if actual_hash != declared_hash:
        raise ValueError(f"{case_id}: image SHA-256 mismatch")
    guessed = mimetypes.guess_type(resolved.name)[0]
    # The contract's declared media type is authoritative. A guess catches
    # obvious malformed fixtures while allowing SVG and uncommon image types.
    if guessed and guessed != media_type:
        raise ValueError(f"{case_id}: media_type {media_type!r} does not match file type {guessed!r}")
    return {
        "id": case_id,
        "image_path": image_path,
        "sha256": actual_hash,
        "media_type": media_type,
        "data_url": f"data:{media_type};base64,{base64.b64encode(resolved.read_bytes()).decode('ascii')}",
    }


def validate_manifest(manifest: dict[str, Any], manifest_path: Path) -> tuple[str, list[dict[str, Any]], list[dict[str, Any]]]:
    if manifest.get("schema_version") not in MANIFEST_SCHEMAS:
        raise ValueError(f"manifest schema_version must be one of {sorted(MANIFEST_SCHEMAS)}")
    benchmark_id = required_string(manifest.get("benchmark_id"), "manifest benchmark_id")
    raw_cases = manifest.get("cases")
    raw_participants = manifest.get("participants")
    if not isinstance(raw_cases, list) or not raw_cases:
        raise ValueError("manifest cases must be a non-empty array")
    if not isinstance(raw_participants, list) or not raw_participants:
        raise ValueError("manifest participants must be a non-empty array")

    cases: list[dict[str, Any]] = []
    case_ids: set[str] = set()
    for index, raw_case in enumerate(raw_cases):
        if not isinstance(raw_case, dict):
            raise ValueError(f"manifest cases[{index}] must be an object")
        encoded = image_data(raw_case, manifest_path)
        if encoded["id"] in case_ids:
            raise ValueError(f"duplicate manifest case_id: {encoded['id']}")
        case_ids.add(encoded["id"])
        cases.append(encoded)

    participants: list[dict[str, Any]] = []
    participant_ids: set[str] = set()
    for index, raw_participant in enumerate(raw_participants):
        if not isinstance(raw_participant, dict):
            raise ValueError(f"manifest participants[{index}] must be an object")
        participant_id = required_string(raw_participant.get("participant_id"), f"participants[{index}].participant_id")
        if participant_id in participant_ids:
            raise ValueError(f"duplicate manifest participant_id: {participant_id}")
        participant_ids.add(participant_id)
        participants.append({
            "id": participant_id,
            "provider": required_string(raw_participant.get("provider"), f"{participant_id}.provider"),
            "model": required_string(raw_participant.get("model"), f"{participant_id}.model"),
            "track": required_string(raw_participant.get("track"), f"{participant_id}.track"),
        })
    return benchmark_id, cases, participants


def validate_results(
    results: dict[str, Any],
    benchmark_id: str,
    cases: list[dict[str, Any]],
    participants: list[dict[str, Any]],
) -> dict[str, dict[str, dict[str, Any]]]:
    if results.get("schema_version") != RESULTS_SCHEMA:
        raise ValueError(f"results schema_version must be {RESULTS_SCHEMA}")
    if results.get("benchmark_id") != benchmark_id:
        raise ValueError("manifest and results benchmark_id differ")
    raw_results = results.get("results")
    if not isinstance(raw_results, list):
        raise ValueError("results.results must be an array")

    participant_ids = {item["id"] for item in participants}
    participant_tracks = {item["id"]: item["track"] for item in participants}
    case_ids = {item["id"] for item in cases}
    expected = {(participant_id, case_id) for participant_id in participant_ids for case_id in case_ids}
    seen: set[tuple[str, str]] = set()
    result_map: dict[str, dict[str, dict[str, Any]]] = {participant_id: {} for participant_id in participant_ids}

    for index, raw_result in enumerate(raw_results):
        if not isinstance(raw_result, dict):
            raise ValueError(f"results[{index}] must be an object")
        participant_id = raw_result.get("participant_id")
        case_id = raw_result.get("case_id")
        key = (participant_id, case_id)
        if key in seen:
            raise ValueError(f"duplicate result pair: {key!r}")
        seen.add(key)
        if key not in expected:
            raise ValueError(f"unknown result pair: {key!r}")
        status = raw_result.get("status")
        if status not in TERMINAL_STATUSES:
            raise ValueError(f"{key!r}: invalid terminal status {status!r}")
        output_text = raw_result.get("output_text")
        if status == "success":
            if not isinstance(output_text, str) or not output_text.strip():
                raise ValueError(f"{key!r}: successful result needs non-empty output_text")
        elif output_text not in (None, "") and not isinstance(output_text, str):
            raise ValueError(f"{key!r}: output_text must be a string when provided")
        if status == "failed" and not str(raw_result.get("failure_type", "")).strip():
            raise ValueError(f"{key!r}: failed result needs failure_type")
        display_text, humanization = (None, None)
        if status == "success":
            display_text, humanization = humanize_output(output_text, participant_tracks[participant_id])
        result_map[participant_id][case_id] = {
            "status": status,
            "output": display_text,
            "raw_output": output_text if status == "success" else None,
            "humanization": humanization,
            "failure": {
                "failure_type": raw_result.get("failure_type"),
                "http_status": raw_result.get("http_status"),
                "stderr": raw_result.get("stderr", raw_result.get("error_excerpt")),
            },
            "source": {
                "raw_artifact": raw_result.get("raw_artifact"),
                "raw_sha256": raw_result.get("raw_sha256"),
                "latency_seconds": raw_result.get("latency_seconds"),
            },
        }
    missing = sorted(expected - seen)
    if missing:
        preview = ", ".join(f"{participant_id}/{case_id}" for participant_id, case_id in missing[:5])
        suffix = " …" if len(missing) > 5 else ""
        raise ValueError(f"missing {len(missing)} exact participant-case pairs: {preview}{suffix}")
    return result_map


def build_data(manifest_path: Path, results_path: Path, output_path: Path) -> dict[str, Any]:
    manifest = read_json(manifest_path)
    results = read_json(results_path)
    benchmark_id, cases, participants = validate_manifest(manifest, manifest_path)
    cells = validate_results(results, benchmark_id, cases, participants)
    generated_at = datetime.now(timezone.utc).isoformat(timespec="seconds")
    aliases = {
        participant_id: f"匿名 {index:02d}"
        for index, participant_id in enumerate(sorted(item["id"] for item in participants), start=1)
    }
    return {
        "schema_version": DATA_SCHEMA,
        "benchmark_id": benchmark_id,
        "generated_at": generated_at,
        "cases": cases,
        "participants": participants,
        "aliases": aliases,
        "cells": cells,
        "source": {
            "output_file": str(output_path),
            "manifest": str(manifest_path),
            "manifest_sha256": sha256(manifest_path),
            "results": str(results_path),
            "results_sha256": sha256(results_path),
            "contract": "references/benchmark-contract.md",
            "export_schema": EXPORT_SCHEMA,
        },
    }


def html_template() -> str:
    return r'''<!doctype html>
<html lang="zh-CN">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta http-equiv="Content-Security-Policy" content="default-src 'none'; img-src data: blob:; style-src 'unsafe-inline'; script-src 'unsafe-inline'; connect-src 'none'; object-src 'none'; base-uri 'none'; form-action 'none'">
<title>视觉模型输出人工评分</title>
<style>
:root{color-scheme:light;--ink:#161c22;--muted:#66727d;--paper:#fff;--soft:#f5f7f9;--line:#dae1e6;--strong:#bdc9d2;--blue:#145de5;--violet:#7046cf;--violet-soft:#f1edff;--red:#b42318;--red-soft:#fff0ee;--amber:#935600;--amber-soft:#fff7e1;--top:64px;font-family:Inter,ui-sans-serif,-apple-system,BlinkMacSystemFont,"Segoe UI","PingFang SC","Microsoft YaHei",sans-serif}*{box-sizing:border-box}html,body{margin:0;min-height:100%;background:var(--soft);color:var(--ink)}body{font-size:14px;line-height:1.45}button,input,select{font:inherit}button{cursor:pointer}button:focus-visible,input:focus-visible,select:focus-visible{outline:3px solid rgba(20,93,229,.35);outline-offset:2px}.skip{position:fixed;z-index:999;top:8px;left:8px;padding:8px 11px;background:#111827;color:#fff;transform:translateY(-150%)}.skip:focus{transform:translateY(0)}.top{position:sticky;z-index:40;top:0;display:flex;align-items:center;justify-content:space-between;gap:16px;min-height:var(--top);padding:11px 24px;border-bottom:1px solid var(--line);background:rgba(255,255,255,.96);backdrop-filter:blur(10px)}.top h1{margin:0;font-size:17px;letter-spacing:-.01em}.top p{margin:2px 0 0;color:var(--muted);font-size:12px}.summary{display:flex;align-items:center;gap:16px;white-space:nowrap}.completion{font-weight:800;font-variant-numeric:tabular-nums}.storage{color:var(--muted);font-size:12px}main{max-width:2560px;margin:0 auto;padding:18px 24px 32px}.controls{display:flex;align-items:center;justify-content:space-between;gap:14px;margin-bottom:12px;padding-bottom:12px;border-bottom:1px solid var(--line)}.group{display:flex;align-items:center;flex-wrap:wrap;gap:8px}.group label{display:flex;align-items:center;gap:7px;color:var(--muted);font-size:13px}.group select{min-height:34px;padding:5px 9px;border:1px solid var(--strong);border-radius:7px;background:#fff;color:var(--ink)}.blind{color:var(--ink)!important;font-weight:700}.blind input{width:16px;height:16px;accent-color:var(--blue)}.btn{min-height:34px;padding:6px 10px;border:1px solid var(--strong);border-radius:7px;background:#fff;color:var(--ink);font-size:13px;font-weight:700}.btn:hover{border-color:#94a4af;background:#fafbfc}.btn.danger{border-color:#e3a39d;color:var(--red)}.btn.danger:hover{background:var(--red-soft)}.tip{margin:0 0 12px;color:var(--muted);font-size:12px}.tip strong{color:var(--ink)}.matrix-panel{border:1px solid var(--line);background:var(--paper)}.matrix-caption{display:flex;align-items:baseline;justify-content:space-between;gap:12px;padding:11px 13px;border-bottom:1px solid var(--line)}.matrix-caption h2{margin:0;font-size:14px}.matrix-caption p{margin:0;color:var(--muted);font-size:12px}.table-wrap{max-height:calc(100vh - 210px);overflow:auto;overscroll-behavior:contain}.matrix{width:max-content;min-width:100%;border-collapse:separate;border-spacing:0;table-layout:fixed}.matrix th,.matrix td{border-right:1px solid var(--line);border-bottom:1px solid var(--line);vertical-align:top}.matrix tr:last-child th,.matrix tr:last-child td{border-bottom:0}.matrix th:last-child,.matrix td:last-child{border-right:0}.matrix thead th{position:sticky;z-index:20;top:0;background:#fbfcfd}.corner{position:sticky!important;z-index:30!important;left:0;width:214px;min-width:214px;padding:12px;text-align:left;box-shadow:1px 0 0 var(--line)}.corner strong{display:block;font-size:13px}.corner span{display:block;margin-top:2px;color:var(--muted);font-size:11px;font-weight:400}.case-head{width:205px;min-width:205px;padding:9px}.case-head-inner{display:grid;grid-template-columns:minmax(0,1fr) auto;gap:6px;align-items:start}.case-image{display:block;width:100%;padding:0;border:0;background:none;text-align:left}.case-image figure{margin:0}.case-image img{display:block;width:100%;height:86px;border:1px solid var(--line);object-fit:cover;background:var(--soft)}.case-image:hover img,.case-image:focus-visible img{border-color:var(--blue);box-shadow:0 0 0 2px #eaf1ff}.case-image figcaption{margin-top:4px;font-size:12px;font-weight:800}.case-image small{display:block;color:var(--muted);font-size:10px;font-weight:400}.clear-case{min-height:26px;padding:3px 5px;border:1px solid var(--line);border-radius:5px;background:#fff;color:var(--muted);font-size:11px}.participant{position:sticky;z-index:10;left:0;width:214px;min-width:214px;padding:12px;background:#fff;box-shadow:1px 0 0 var(--line)}.participant-name{display:block;overflow-wrap:anywhere;font-size:13px;font-weight:750}.track{display:inline-block;margin-top:5px;padding:2px 5px;border:1px solid var(--line);color:var(--muted);font-size:10px;font-weight:800;letter-spacing:.04em;text-transform:uppercase}.matrix td{width:205px;min-width:205px;padding:8px;background:#fff}.cell{position:relative;min-height:130px}.output{display:block;width:100%;min-height:96px;padding:8px;border:1px solid transparent;background:#fff;color:var(--ink);text-align:left}.output:hover{border-color:#b7c4cc;background:#fcfdff}.output.selected{border-color:var(--violet);background:var(--violet-soft)}.output.rank-2{border-color:#2c73bf}.output.rank-3{border-color:#198260}.clamp{display:-webkit-box;overflow:hidden;color:#29343d;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:11px;line-height:1.48;white-space:pre-wrap;-webkit-box-orient:vertical;-webkit-line-clamp:5}.rank{position:absolute;z-index:2;top:4px;right:4px;min-width:45px;padding:3px 5px;border-radius:4px;background:var(--violet);color:#fff;font-size:11px;font-weight:800;text-align:center}.actions{display:flex;justify-content:flex-end;margin-top:4px}.details{min-height:25px;padding:2px 6px;border:1px solid var(--line);border-radius:4px;background:#fff;color:#34404a;font-size:11px}.failure{min-height:130px;padding:10px;background:var(--red-soft);color:#6d211b}.failure.not-run{background:var(--amber-soft);color:#664100}.failure strong{display:block;color:var(--red);font-size:13px}.failure.not-run strong{color:var(--amber)}.failure-meta{display:block;margin-top:7px;overflow-wrap:anywhere;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:10px;line-height:1.45}.failure .actions{justify-content:flex-start;margin-top:9px}.lower{display:grid;grid-template-columns:minmax(0,1fr) minmax(430px,680px);gap:24px;margin-top:20px}.boundary,.board{border-top:2px solid var(--ink);padding-top:10px}.boundary h2,.board h2{margin:0;font-size:14px}.boundary p{margin:7px 0 0;color:var(--muted);font-size:12px}.leaderboard{width:100%;margin-top:10px;border-collapse:collapse;font-variant-numeric:tabular-nums}.leaderboard th,.leaderboard td{padding:7px 8px;border-bottom:1px solid var(--line);text-align:right;font-size:12px}.leaderboard th:first-child,.leaderboard td:first-child,.leaderboard th:nth-child(2),.leaderboard td:nth-child(2){text-align:left}.leaderboard th{color:var(--muted);font-size:11px}.preview{position:fixed;z-index:80;display:none;width:min(520px,calc(100vw - 24px));max-height:min(62vh,650px);padding:11px 12px;overflow:auto;border:1px solid #25313b;border-radius:7px;background:#14202a;color:#f7fafc;box-shadow:0 12px 32px rgba(16,24,40,.2)}.preview.show{display:block}.preview strong{display:block;margin-bottom:7px;font-size:12px}.preview pre{margin:0;white-space:pre-wrap;overflow-wrap:anywhere;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:11px;line-height:1.55}.toast{position:fixed;z-index:100;right:18px;bottom:18px;max-width:min(420px,calc(100vw - 36px));padding:10px 12px;border:1px solid #a2b5d0;border-radius:7px;background:#edf4ff;color:#17417b;box-shadow:0 12px 32px rgba(16,24,40,.18);font-size:13px}.toast.error{border-color:#e3aaa4;background:var(--red-soft);color:#812019}.toast[hidden]{display:none}dialog{width:min(940px,calc(100vw - 28px));max-height:calc(100vh - 28px);padding:0;border:1px solid var(--strong);border-radius:9px;background:#fff;color:var(--ink);box-shadow:0 16px 44px rgba(16,24,40,.27)}dialog::backdrop{background:rgba(15,23,32,.52)}.dialog-head{display:flex;align-items:flex-start;justify-content:space-between;gap:14px;padding:16px;border-bottom:1px solid var(--line)}.dialog-head h2{margin:0;font-size:16px}.dialog-head p{margin:4px 0 0;color:var(--muted);font-size:12px}.close{min-height:30px;padding:4px 8px;border:1px solid var(--line);border-radius:5px;background:#fff}.dialog-body{padding:16px}.dialog-body pre{max-height:calc(100vh - 210px);margin:0;overflow:auto;white-space:pre-wrap;overflow-wrap:anywhere;font-family:ui-monospace,SFMono-Regular,Menlo,Consolas,monospace;font-size:12px;line-height:1.55}.meta{margin:0 0 12px;color:var(--muted);font-size:12px}.image-dialog{width:min(1320px,calc(100vw - 28px));background:#15191d}.image-dialog .dialog-head{border-bottom-color:#3a4147;color:#fff}.image-dialog .dialog-head p{color:#c5cbd0}.image-dialog .close{border-color:#66727d;background:#263037;color:#fff}.image-frame{display:flex;min-height:140px;align-items:center;justify-content:center;padding:14px}.image-frame img{display:block;max-width:100%;max-height:calc(100vh - 130px);object-fit:contain}.confirm{width:min(420px,calc(100vw - 28px))}.dialog-actions{display:flex;justify-content:flex-end;gap:8px;margin-top:18px}@media(max-width:960px){:root{--top:unset}.top{position:static;align-items:flex-start;flex-direction:column}.summary{flex-wrap:wrap;gap:7px}.controls{align-items:flex-start;flex-direction:column}.lower{grid-template-columns:1fr}.table-wrap{max-height:70vh}.case-head,.matrix td{width:188px;min-width:188px}.corner,.participant{width:175px;min-width:175px}}@media(max-width:620px){main{padding:12px}.top{padding:12px}.case-head,.matrix td{width:174px;min-width:174px}.corner,.participant{width:150px;min-width:150px}.preview{display:none!important}}@media(prefers-reduced-motion:reduce){*{scroll-behavior:auto!important;transition:none!important}}
.table-wrap{max-height:none!important;overflow:visible!important;overscroll-behavior:auto!important}
</style>
</head>
<body>
<a class="skip" href="#matrix">跳至评分矩阵</a>
<header class="top"><div><h1 id="page-title">视觉模型输出评分</h1><p id="page-subtitle"></p></div><div class="summary"><span class="completion" id="completion">已评完 0/0</span><span class="storage" id="storage">正在读取本地评分…</span></div></header>
<main>
  <section class="controls" aria-label="评分操作"><div class="group"><label>赛道筛选 <select id="track-filter" aria-label="赛道筛选"></select></label><label class="blind"><input id="blind-mode" type="checkbox"> 盲评模式（匿名编号）</label></div><div class="group"><button class="btn" id="export-json" type="button">导出 JSON</button><button class="btn" id="export-csv" type="button">导出 CSV</button><label class="btn" for="import-json">导入 JSON<input id="import-json" type="file" accept="application/json,.json" hidden></label><button class="btn danger" id="clear-all" type="button">清空全部</button></div></section>
  <p class="tip"><strong>评分规则：</strong>每张图独立评前三名，计分 3 / 2 / 1。评分区默认只显示整理后的正文；JSON 控制字段、检测坐标与原始标记仅在“原始证据”中查看。失败和未运行格不可评分。</p>
  <section class="matrix-panel" id="matrix" aria-labelledby="matrix-title"><div class="matrix-caption"><h2 id="matrix-title">人类可读输出矩阵</h2><p id="preview">格子显示摘要；点击“全文”打开可滚动的完整内容。缩略图可放大，Esc 关闭。</p></div><div class="table-wrap" id="table-wrap" tabindex="0" aria-label="模型输出比较矩阵"><table class="matrix" id="review-table"><caption>模型和图片案例组成的人类可读输出评分矩阵</caption></table></div></section>
  <section class="lower"><article class="boundary"><h2>数据边界</h2><p>评分展示使用 normalized/results.json 的人类可读投影；原始 output_text 完整保留但默认隐藏，仅供核验。导出评分始终保留真实 participant_id。</p></article><article class="board"><h2>当前总榜</h2><div id="leaderboard"></div></article></section>
</main>
<div class="toast" id="toast" role="status" aria-live="polite" hidden></div>
<dialog id="detail-dialog"><div class="dialog-head"><div><h2 id="detail-title">输出详情</h2><p id="detail-subtitle"></p></div><div class="group"><button class="close" id="toggle-raw" type="button" hidden>查看原始证据</button><button class="close" type="button" data-close="detail-dialog">关闭</button></div></div><div class="dialog-body"><p class="meta" id="detail-meta"></p><pre id="detail-text"></pre></div></dialog>
<dialog class="image-dialog" id="image-dialog"><div class="dialog-head"><div><h2 id="image-title">图像预览</h2><p>按 Esc 或“关闭”返回评分矩阵。</p></div><button class="close" type="button" data-close="image-dialog">关闭</button></div><div class="image-frame"><img id="lightbox" alt=""></div></dialog>
<dialog class="confirm" id="confirm-dialog"><div class="dialog-head"><div><h2>确认清空全部评分？</h2><p>本页所有图片的本地评分将被删除。</p></div><button class="close" type="button" data-close="confirm-dialog">取消</button></div><div class="dialog-body"><p>如需保留当前结果，请先导出 JSON。</p><div class="dialog-actions"><button class="btn" type="button" data-close="confirm-dialog">取消</button><button class="btn danger" id="confirm-clear" type="button">确认清空</button></div></div></dialog>
<script id="review-data" type="application/json">__DATA__</script>
<script>
(() => {
  "use strict";
  const DATA = JSON.parse(document.getElementById("review-data").textContent);
  const EXPORT_SCHEMA = "akashic-visual-output-review-rankings/v1";
  const STORAGE_KEY = `akashic.visual-output-review.rankings.v1.${encodeURIComponent(DATA.benchmark_id)}`;
  const CASE_IDS = DATA.cases.map(item => item.id);
  const byId = new Map(DATA.participants.map(item => [item.id, item]));
  const state = { rankings: blank(), track: "all", blind: false, storage: true };
  const $ = selector => document.querySelector(selector);
  const table = $("#review-table"), tableWrap = $("#table-wrap"), toast = $("#toast");
  let toastTimer = null;
  let activeDetail = null, rawDetailVisible = false;
  function blank(){return Object.fromEntries(CASE_IDS.map(id=>[id,[]]));}
  function cell(pid,cid){return DATA.cells[pid][cid];}
  function success(pid,cid){return cell(pid,cid).status==="success";}
  function name(pid){return state.blind ? DATA.aliases[pid] : pid;}
  function tracks(){return [...new Set(DATA.participants.map(item=>item.track))].sort();}
  function sealed(value){return value===null||value===undefined||value==="" ? "未记录" : String(value);}
  function excerpt(value,max=130){const text=String(value||"").replace(/\s+/g," ").trim();return text.length>max?text.slice(0,max)+"…":text;}
  function statusLabel(value){return value==="not_run" ? "未运行" : "失败";}
  function visible(){return DATA.participants.filter(item=>state.track==="all"||item.track===state.track);}
  function rank(pid,cid){const index=state.rankings[cid].indexOf(pid);return index<0?0:index+1;}
  function normalize(candidate,strict=false){const result=blank();if(!candidate||typeof candidate!=="object"){if(strict)throw new Error("case_rankings 必须是对象。");return result;}for(const cid of CASE_IDS){const list=candidate[cid]??[];if(!Array.isArray(list)){if(strict)throw new Error(`${cid} 的排名必须是数组。`);continue;}if(list.length>3&&strict)throw new Error(`${cid} 超过前三名。`);const seen=new Set();for(const item of list.slice(0,3)){const pid=typeof item==="string"?item:item&&item.participant_id;if(typeof pid!=="string"||!byId.has(pid)||seen.has(pid)||!success(pid,cid)){if(strict)throw new Error(`${cid} 包含未知、重复或不可评分的 participant_id。`);continue;}seen.add(pid);result[cid].push(pid);}}return result;}
  function load(){try{const raw=localStorage.getItem(STORAGE_KEY);if(raw){const saved=JSON.parse(raw);state.rankings=normalize(saved.rankings||saved.case_rankings||saved);}}catch(_){state.storage=false;}}
  function persist(){try{localStorage.setItem(STORAGE_KEY,JSON.stringify({schema_version:EXPORT_SCHEMA,rankings:state.rankings}));state.storage=true;}catch(_){state.storage=false;}}
  function say(message,kind=""){toast.textContent=message;toast.className=`toast ${kind}`.trim();toast.hidden=false;clearTimeout(toastTimer);toastTimer=setTimeout(()=>toast.hidden=true,3800);}
  function fillFilters(){const select=$("#track-filter");select.replaceChildren();const all=document.createElement("option");all.value="all";all.textContent=`全部（${DATA.participants.length}）`;select.append(all);for(const track of tracks()){const option=document.createElement("option");option.value=track;option.textContent=`${track}（${DATA.participants.filter(item=>item.track===track).length}）`;select.append(option);}select.value=state.track;}
  function makeCell(participant,cid){const record=cell(participant.id,cid),td=document.createElement("td");if(record.status==="success"){const box=document.createElement("div");box.className="cell";const button=document.createElement("button");button.type="button";button.className="output";button.dataset.action="rank";button.dataset.pid=participant.id;button.dataset.cid=cid;button.setAttribute("aria-describedby","preview");const current=rank(participant.id,cid);if(current)button.classList.add("selected",`rank-${current}`);button.setAttribute("aria-label",`${name(participant.id)} 在 ${cid} 的成功输出${current?`，当前第 ${current} 名，再次点击撤销`:"，点击加入前三名"}`);const text=document.createElement("span");text.className="clamp";text.textContent=record.output;button.append(text);if(current){const badge=document.createElement("span");badge.className="rank";badge.textContent=`第 ${current} 名`;box.append(badge);}const actions=document.createElement("div");actions.className="actions";const details=document.createElement("button");details.type="button";details.className="details";details.dataset.action="details";details.dataset.pid=participant.id;details.dataset.cid=cid;details.textContent="全文";details.setAttribute("aria-label",`查看 ${name(participant.id)} 在 ${cid} 的全文`);actions.append(details);box.append(button,actions);td.append(box);}else{const fail=document.createElement("div");fail.className=`failure ${record.status==="not_run"?"not-run":""}`;const label=document.createElement("strong");label.textContent=statusLabel(record.status);const meta=document.createElement("span");meta.className="failure-meta";meta.textContent=`failure_type: ${sealed(record.failure.failure_type)}\nhttp_status: ${sealed(record.failure.http_status)}\nstderr: ${excerpt(sealed(record.failure.stderr),115)}`;const actions=document.createElement("div");actions.className="actions";const details=document.createElement("button");details.type="button";details.className="details";details.dataset.action="details";details.dataset.pid=participant.id;details.dataset.cid=cid;details.textContent="状态详情";actions.append(details);fail.append(label,meta,actions);td.append(fail);}return td;}
  function renderTable(){const x=tableWrap.scrollLeft,y=tableWrap.scrollTop;table.replaceChildren();const thead=document.createElement("thead"),headRow=document.createElement("tr"),corner=document.createElement("th");corner.scope="col";corner.className="corner";const strong=document.createElement("strong");strong.textContent=state.blind?"匿名参与者":"模型 / OCR";const small=document.createElement("span");small.textContent="左列与图像表头可固定";corner.append(strong,small);headRow.append(corner);for(const item of DATA.cases){const th=document.createElement("th");th.scope="col";th.className="case-head";const inner=document.createElement("div");inner.className="case-head-inner";const imageButton=document.createElement("button");imageButton.type="button";imageButton.className="case-image";imageButton.dataset.action="image";imageButton.dataset.cid=item.id;imageButton.setAttribute("aria-label",`放大 ${item.id} 图像`);const figure=document.createElement("figure"),image=document.createElement("img"),caption=document.createElement("figcaption"),hint=document.createElement("small");image.src=item.data_url;image.alt=`${item.id} 原始图像缩略图`;caption.textContent=item.id;hint.textContent="点击放大";figure.append(image,caption,hint);imageButton.append(figure);const clear=document.createElement("button");clear.type="button";clear.className="clear-case";clear.dataset.action="clear-case";clear.dataset.cid=item.id;clear.textContent="清空本列";inner.append(imageButton,clear);th.append(inner);headRow.append(th);}thead.append(headRow);table.append(thead);const tbody=document.createElement("tbody");for(const participant of visible()){const row=document.createElement("tr"),head=document.createElement("th"),participantName=document.createElement("span"),track=document.createElement("span");head.scope="row";head.className="participant";participantName.className="participant-name";participantName.textContent=name(participant.id);track.className="track";track.textContent=participant.track;head.append(participantName,track);row.append(head);for(const cid of CASE_IDS)row.append(makeCell(participant,cid));tbody.append(row);}table.append(tbody);tableWrap.scrollLeft=x;tableWrap.scrollTop=y;}
  function totals(){const rows=DATA.participants.map(item=>({participant_id:item.id,track:item.track,points:0,first:0,second:0,third:0,ranked_cases:0})),map=new Map(rows.map(item=>[item.participant_id,item]));for(const cid of CASE_IDS)state.rankings[cid].forEach((pid,index)=>{const row=map.get(pid);row.points+=3-index;row.ranked_cases+=1;if(index===0)row.first+=1;if(index===1)row.second+=1;if(index===2)row.third+=1;});return rows.sort((a,b)=>b.points-a.points||b.first-a.first||b.second-a.second||b.third-a.third||a.participant_id.localeCompare(b.participant_id));}
  function renderBoard(){const holder=$("#leaderboard");holder.replaceChildren();const rows=totals().filter(row=>state.track==="all"||row.track===state.track),table=document.createElement("table"),thead=document.createElement("thead"),tr=document.createElement("tr");table.className="leaderboard";["名次",state.blind?"匿名编号":"participant_id","赛道","总分","第 1","第 2","第 3","参与图片"].forEach(label=>{const th=document.createElement("th");th.textContent=label;tr.append(th);});thead.append(tr);table.append(thead);const tbody=document.createElement("tbody");rows.forEach((row,index)=>{const line=document.createElement("tr");[index+1,name(row.participant_id),row.track,row.points,row.first,row.second,row.third,row.ranked_cases].forEach(value=>{const td=document.createElement("td");td.textContent=String(value);line.append(td);});tbody.append(line);});table.append(tbody);holder.append(table);}
  function renderStatus(){const done=CASE_IDS.filter(cid=>state.rankings[cid].length===3).length;$("#completion").textContent=`已评完 ${done}/${CASE_IDS.length}`;$("#storage").textContent=state.storage?"已自动保存到本机浏览器":"本地存储不可用；请导出 JSON";}
  function render(){fillFilters();renderTable();renderBoard();renderStatus();}
  function choose(pid,cid){if(!success(pid,cid))return;const picks=state.rankings[cid],index=picks.indexOf(pid);if(index>=0){picks.splice(index,1);persist();render();say(`已撤销 ${cid} 的第 ${index+1} 名，后续名次已压紧。`);return;}if(picks.length>=3){say(`${cid} 已选满前三名；请先撤销已入选输出。`,"error");return;}picks.push(pid);persist();render();say(`${cid} 已设为第 ${picks.length} 名。`);}
  function open(dialog){if(typeof dialog.showModal==="function")dialog.showModal();else dialog.setAttribute("open","");}
  function close(dialog){if(typeof dialog.close==="function")dialog.close();else dialog.removeAttribute("open");}
  function renderDetail(){if(!activeDetail)return;const {pid,cid}=activeDetail,record=cell(pid,cid),toggle=$("#toggle-raw");$("#detail-title").textContent=`${cid} · ${name(pid)}`;if(record.status==="success"){const source=record.source;toggle.hidden=false;toggle.textContent=rawDetailVisible?"返回可读内容":"查看原始证据";$("#detail-subtitle").textContent=rawDetailVisible?"原始机器输出（仅供核验）":"整理后的人类可读全文";$("#detail-meta").textContent=rawDetailVisible?(state.blind?"来源：已封存 normalized result":"来源：normalized/results.json"+(source.raw_artifact?` · raw_artifact：${source.raw_artifact}`:"")+(source.raw_sha256?` · SHA-256：${source.raw_sha256}`:"")):`展示处理：${record.humanization||"模型原生正文"}`;$("#detail-text").textContent=rawDetailVisible?record.raw_output:record.output;}else{toggle.hidden=true;$("#detail-subtitle").textContent="已封存失败或未运行状态（不可评分）";$("#detail-meta").textContent="来源：normalized/results.json";$("#detail-text").textContent=`状态：${record.status}\nfailure_type：${sealed(record.failure.failure_type)}\nhttp_status：${sealed(record.failure.http_status)}\nstderr：${sealed(record.failure.stderr)}`;}}
  function details(pid,cid){const dialog=$("#detail-dialog");activeDetail={pid,cid};rawDetailVisible=false;renderDetail();open(dialog);dialog.querySelector("[data-close]").focus();}
  function image(cid){const item=DATA.cases.find(value=>value.id===cid),dialog=$("#image-dialog");$("#image-title").textContent=`${cid} 原始图像`;const target=$("#lightbox");target.src=item.data_url;target.alt=`${cid} 原始图像放大预览`;open(dialog);dialog.querySelector("[data-close]").focus();}
  function payload(){const caseRankings=Object.fromEntries(CASE_IDS.map(cid=>[cid,state.rankings[cid].map((pid,index)=>({rank:index+1,participant_id:pid,track:byId.get(pid).track,points:3-index}))]));return {schema_version:EXPORT_SCHEMA,benchmark_id:DATA.benchmark_id,generated_at:new Date().toISOString(),scoring_method:{rank_1_points:3,rank_2_points:2,rank_3_points:1,tie_breakers:["first_place_votes_desc","second_place_votes_desc","third_place_votes_desc","participant_id_asc"]},case_rankings:caseRankings,leaderboard:totals(),source_html_information:DATA.source,presentation_settings:{blind_mode:state.blind,track_filter:state.track}};}
  function download(content,name,type){const a=document.createElement("a"),url=URL.createObjectURL(new Blob([content],{type}));a.href=url;a.download=name;document.body.append(a);a.click();a.remove();setTimeout(()=>URL.revokeObjectURL(url),1000);}
  function csv(value){const text=String(value??"");return /[",\n]/.test(text)?`"${text.replaceAll('"','""')}"`:text;}
  function exportJson(){download(JSON.stringify(payload(),null,2),`${DATA.benchmark_id}-human-rankings.json`,"application/json;charset=utf-8");say("已导出 JSON 评分文件。 ");}
  function exportCsv(){const lines=[["case_id","rank","participant_id","track","points"]];for(const cid of CASE_IDS)state.rankings[cid].forEach((pid,index)=>lines.push([cid,index+1,pid,byId.get(pid).track,3-index]));download(lines.map(row=>row.map(csv).join(",")).join("\r\n"),`${DATA.benchmark_id}-human-rankings.csv`,"text/csv;charset=utf-8");say("已导出 CSV 评分文件。 ");}
  function importJson(file){const reader=new FileReader();reader.onload=()=>{try{const incoming=JSON.parse(String(reader.result));if(incoming.schema_version!==EXPORT_SCHEMA)throw new Error(`schema_version 必须为 ${EXPORT_SCHEMA}。`);if(incoming.benchmark_id!==DATA.benchmark_id)throw new Error("benchmark_id 与当前页面不匹配。");state.rankings=normalize(incoming.case_rankings,true);persist();render();say("已导入 JSON，评分已恢复。 ");}catch(error){say(`导入失败：${error.message}`,"error");}};reader.onerror=()=>say("导入失败：无法读取文件。","error");reader.readAsText(file,"utf-8");}
  table.addEventListener("click",event=>{const action=event.target.closest("[data-action]");if(!action)return;if(action.dataset.action==="rank")choose(action.dataset.pid,action.dataset.cid);if(action.dataset.action==="details")details(action.dataset.pid,action.dataset.cid);if(action.dataset.action==="image")image(action.dataset.cid);if(action.dataset.action==="clear-case"){state.rankings[action.dataset.cid]=[];persist();render();say(`已清空 ${action.dataset.cid} 的评分。`);}});
  $("#track-filter").addEventListener("change",event=>{state.track=event.target.value;render();});$("#blind-mode").addEventListener("change",event=>{state.blind=event.target.checked;render();say(state.blind?"盲评模式已开启。":"盲评模式已关闭。 ");});$("#toggle-raw").addEventListener("click",()=>{rawDetailVisible=!rawDetailVisible;renderDetail();});$("#export-json").addEventListener("click",exportJson);$("#export-csv").addEventListener("click",exportCsv);$("#import-json").addEventListener("change",event=>{const file=event.target.files&&event.target.files[0];if(file)importJson(file);event.target.value="";});$("#clear-all").addEventListener("click",()=>open($("#confirm-dialog")));$("#confirm-clear").addEventListener("click",()=>{state.rankings=blank();persist();close($("#confirm-dialog"));render();say("已清空全部评分。 ");});document.addEventListener("click",event=>{const button=event.target.closest("[data-close]");if(button)close(document.getElementById(button.dataset.close));});document.querySelectorAll("dialog").forEach(dialog=>dialog.addEventListener("click",event=>{if(event.target===dialog)close(dialog);}));
  $("#page-title").textContent=`${DATA.benchmark_id} · 图像输出评分`;$("#page-subtitle").textContent=`${DATA.participants.length} 个参与者 × ${DATA.cases.length} 张固定图像 · 点击成功输出依次评为第 1 / 2 / 3 名`;load();render();
})();
</script>
</body>
</html>
'''


def validate_html(html: str) -> None:
    required = (
        'id="review-data"',
        'id="review-table"',
        'id="blind-mode"',
        'id="export-json"',
        'id="export-csv"',
        'id="import-json"',
        'id="detail-dialog"',
        'id="image-dialog"',
        'localStorage',
        'rank_1_points:3',
        'rank_2_points:2',
        'rank_3_points:1',
    )
    missing = [needle for needle in required if needle not in html]
    if missing:
        raise ValueError(f"generated HTML misses interaction contract: {missing}")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path, help="visual-model-benchmark/v1 or v2 image manifest.json")
    parser.add_argument("--results", required=True, type=Path, help="visual-model-results/v1 normalized/results.json")
    parser.add_argument("--output", required=True, type=Path, help="self-contained review HTML output")
    args = parser.parse_args()
    try:
        manifest_path = args.manifest.resolve()
        results_path = args.results.resolve()
        output_path = args.output.resolve()
        data = build_data(manifest_path, results_path, output_path)
        data_json = json.dumps(data, ensure_ascii=False, separators=(",", ":")).replace("</", "<\\/")
        html = html_template().replace("__DATA__", data_json)
        validate_html(html)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        output_path.write_text(html, encoding="utf-8")
        status_counts = Counter(
            record["status"]
            for participant in data["participants"]
            for record in data["cells"][participant["id"]].values()
        )
        print(json.dumps({
            "status": "pass",
            "benchmark_id": data["benchmark_id"],
            "output": str(output_path),
            "output_sha256": sha256(output_path),
            "output_bytes": output_path.stat().st_size,
            "cases": len(data["cases"]),
            "participants": len(data["participants"]),
            "cells": len(data["cases"]) * len(data["participants"]),
            "status_counts": status_counts,
        }, ensure_ascii=False, indent=2))
        return 0
    except ValueError as error:
        print(json.dumps({"status": "fail", "error": str(error)}, ensure_ascii=False, indent=2), file=sys.stderr)
        return 2


if __name__ == "__main__":
    raise SystemExit(main())
