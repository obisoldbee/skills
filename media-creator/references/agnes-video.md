# Agnes Video V2.0

官方文档：<https://agnes-ai.com/zh-Hans/docs/agnes-video-v20>

## 能力与边界

- 模型：`agnes-video-v2.0`
- 创建：`POST /v1/videos`
- 推荐查询：`GET /agnesapi?video_id=<VIDEO_ID>`
- 文生视频；
- 顶层单图 `image` 的图生视频；
- `extra_body.image[] + extra_body.mode=keyframes` 的图片关键帧动画。

当前官方请求合同没有输入视频或参考音频字段。登记 `video_to_video=false`，不要把 `video_id` 误解为视频输入。

## 参数

- `num_frames <= 441` 且满足 `8n + 1`；
- `frame_rate` 范围 `1–60`；
- `width`、`height` 可能被标准化到 480p、720p 或 1080p；
- 可选 `num_inference_steps`、`seed`、`negative_prompt`。

先 dry-run：

```bash
python3 -B scripts/agnes_media.py video \
  --prompt "<prompt>" \
  --num-frames 121 \
  --frame-rate 24 \
  --wait \
  --output <output.mp4>
```

单图使用 `--image`；关键帧重复使用 `--keyframe`。确认预览正确并获真实调用授权后才加 `--execute`。

## 异步结果

创建响应保留 `task_id` 和 `video_id`。优先用 `video_id` 查询；状态包括 `queued`、`in_progress`、`completed`、`failed`。

完成 URL 位于 `metadata.url`。旧 Skill 中的 `remixed_from_video_id` 不是当前结果字段，不得迁入。

轮询中断时保留 ID，不创建重复任务。下载失败只重试同一 `metadata.url`。
