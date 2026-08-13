# Result Contract

统一 envelope 解决“不同 provider 字段难以处理”，但不得抹平赛道差异。

## 最小 envelope

```json
{
  "schema": "media-understanding/v1",
  "request_id": "...",
  "media_kind": "image|video|audio|document|mixed",
  "task_family": "...",
  "status": "success|failed|not_run",
  "route": {
    "adapter": "...",
    "provider": "...",
    "model": "...",
    "endpoint_ref": "...",
    "selection_reason": "..."
  },
  "source": {"path_or_url": "...", "sha256": "..."},
  "prompt_version": "...",
  "raw_artifact": "...",
  "normalized": {},
  "usage": {},
  "latency_seconds": null,
  "uncertainties": [],
  "failure": null
}
```

不在 envelope 中保存 key、token、cookie、完整 data URL 或隐私调试日志。

## 赛道专属 `normalized`

- 图片：`summary`、`verbatim_text`、`subjects`、`layout`、`color_and_visual_cues`、`meaning`。
- OCR/文档：`readable_text`、`pages`、`reading_order`、`layout_evidence`、`tables`、`figures`、`semantic_interpretation`；原始 det/bbox 只进入证据层。
- 视频：`overall`、`chapters`、`timeline_events`、`visible_text`、`audio_evidence`、`cross_segment_links`。
- 音频：按任务选择 `transcript`、`srt`、`speakers`、`translation`、`minutes` 或 `semantic_notes`。
- mixed：保留各赛道字段与 evidence source，再输出 `fusion_summary`；不得把推断写成逐字事实。

## 原始证据与人类显示

- `raw_artifact` 指向 provider 原始响应，不改写。
- 页面默认显示清洗后的可读投影。
- JSON 控制字段、思考块、OCR det/bbox 与哈希不进入人类正文。
- 用户可通过“原始证据”入口查看完整返回。
- 人工纠正单独记录，不覆盖模型原文。
