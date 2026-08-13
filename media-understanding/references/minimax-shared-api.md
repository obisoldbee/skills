# MiniMax Provider Profile

本文件只描述 `minimax` profile。火山、Agnes、MiMo、本地 OCR/ASR 各自使用独立配置。

## 凭据

```text
env: ~/.codex/secrets/minimax.env
key: MINIMAX_API_KEY
optional base: MINIMAX_BASE_URL
```

同一个 MiniMax profile 可以复用凭据读取和错误分类，但图片、视频视觉和音频语义仍是不同 adapter，不能猜测共用 payload。

## 协议优先级

图片/视频理解默认且推荐走 Anthropic-compatible：

```text
base_url: https://api.minimaxi.com/anthropic
endpoint: POST https://api.minimaxi.com/anthropic/v1/messages
model: MiniMax-M3
```

该路径是官方文本生成指南标注的推荐/default 路径，支持 thinking 与 interleaved thinking。OpenAI-compatible `POST https://api.minimaxi.com/v1/chat/completions` 是官方支持但非推荐的兼容备选，只在项目已经绑定 OpenAI SDK、当前不便迁移时显式选择，不与 Anthropic 并列为默认路由。

## 当前执行器

| Route | 输入/执行器 | 边界 |
|---|---|---|
| `minimax-mmx-image` | `$mmx-cli` → `mmx vision describe --image ...` | 快速图片理解；CLI 1.0.19 不接受 `--model`，底层模型未知 |
| `minimax-m3-course-video` | 包内 `scripts/providers/minimax_m3_course_video.py` | 课程屏幕/UI/幻灯片视觉 |
| `minimax-m3-transcript-semantics` | 获授权的 ASR → transcript → M3 文本请求 | 音频语义默认路径；执行器需在当前任务绑定 |
| `minimax-m3-course-audio-via-video-experimental` | 包内 `scripts/providers/minimax_m3_course_audio.py` | 实验兼容；不是原生音频/逐字稿；使用真实低清视频载体 |

MiniMax-M3 官方支持图像与视频。图片/视频默认通过 Anthropic Messages 合同发送。视频可直接 URL/Base64（≤50MB）或先通过 Files 上传并用 `mm_file://file_id` 引用（≤512MB、文件默认保留 7 天）；文档/PDF 无原生合同，应先本地解析/OCR 再给文本。

`mmx-cli` 的 `vision describe` 对快速单图最方便，但走 `/v1/coding_plan/vlm` 且不暴露底层 model id，不能把输出归因于 `MiniMax-VL-01`。M3 视频/结构化生产调用继续使用 Anthropic direct API；本包的课程视频/音频脚本就是该端点，旧同名独立 Skills 已退役。普通 MiniMax MCP 当前侧重生成、TTS、音乐等工具，不是本总路由的通用理解入口；MCP 文档存在不等于能力已安装或执行。

## 错误处理

- `1026` / `input new_sensitive`：不短切、不循环重试，记录终态。
- 其他瞬时失败或空响应：按具体执行器规则进行有限尝试。
- 保存原始响应、媒体段落和实际 model ID。
- 未经当前授权，不从 MiniMax 自动切换火山、Agnes、MiMo 或其他 provider。
- MiMo 当前是 disabled；MiniMax 失败只返回 `provider_fallback_requires_user_opt_in`。
