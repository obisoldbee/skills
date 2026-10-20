# MiniMax Provider Profile

2026-10-20 核对。本文件描述 MiniMax；Agnes、火山、MiMo 与本地 OCR/ASR 使用各自配置。

## 协议与模型

本机私有槽位为 `~/.codex/secrets/minimax.env`，变量 `MINIMAX_API_KEY` 与可选 `MINIMAX_BASE_URL`。direct 默认使用当前官方国内端点 `https://api.minimax.cn/anthropic/v1/messages`，协议为 Anthropic-compatible Messages。显式 `--endpoint` 优先，其次为指定 base、环境/私有槽位的 base，再用默认端点；保留已绑定 profile，不改写凭据或全局配置。

| 模型 | 本包选择 | Thinking | Effort |
|---|---|---|---|
| `MiniMax-M3` | 既有默认，继续保留 | adapter 显式 disabled | 不接受 Flash 专属 effort |
| `MiniMax-M3.1-Flash` | 显式 `--model` | 强制 adaptive，disabled 会报 400 | `low/medium/high/xhigh/max`；省略为 max |

两者当前均为 1M 上下文，支持图片和视频。`temperature/top_p` 是忽略字段，服务固定为 1/0.95；adapter 不再发送 temperature，旧 `--temperature` 仅为调用和历史指纹兼容保留。`max_tokens` 包含 thinking，预算不足可能只有思考而没有正文；需要更长回答时在首次请求前分配预算，不能将 accepted 空结果自动重投。

OpenAI-compatible `https://api.minimax.cn/v1/chat/completions` 保留为项目已有 OpenAI SDK 绑定时的显式兼容选择。MiniMax CLI 文本默认的 `MiniMax-M3.1-Flash-Preview` 与以上 direct ID 分开处理，不能从 CLI 默认推断按量或特定账号可用。

## 输入合同与执行器

- 图片使用 URL 或 Base64，支持 JPEG/PNG/GIF/WebP，文件最大 10 MB。
- 视频 URL/Base64 文件最大 50 MB，请求体最大 64 MB；Base64 source 使用 `type=base64`、`media_type`、`data`。大视频可经 Files API 的 `purpose=video_understanding` 上传，最大 512 MB、默认保留 7 天，使用 `mm_file://file_id`。当前课程脚本实现内联 Base64，不会自动上传 Files。
- 两个课程脚本仍保留更保守的 50,000,000 Base64 字符客户端上限，约对应 37.5 MB 原始视频；这与官方文件上限分别记录。
- Messages 的独立 audio、document/file 内容块未在当前 REST 合同明确列出。AI SDK 页另有 PDF 支持声明，与 REST schema 存在差异；在精确合同或授权验证前，文档继续本地解析/OCR后送文本，音频继续 ASR后送文本。

| Route | 执行器与边界 |
|---|---|
| `minimax-mmx-image` | `mmx vision describe`，1.0.28 不暴露模型 ID，走 Coding Plan VLM |
| `minimax-m3-image` | 图片 Messages adapter 尚需当前任务显式绑定 |
| `minimax-m3-course-video` | 包内视频 adapter，支持上述两个明确模型；课程视觉 |
| `minimax-mmx-asr` | `mmx speech transcribe`、`asr-1.0`，官方独立 ASR API |
| `minimax-m3-transcript-semantics` | 已获授权的转写 → 选定文本模型；文本执行器需绑定 |
| `minimax-m3-course-audio-via-video-experimental` | 包内音频装入 MP4 的兼容实验，仍需显式选择 |

CLI 的 key/host/region 必须同时绑定，见 [CLI 合同](minimax-cli.md)。`vision describe` 没有模型参数；direct 脚本的示例为

```sh
python3 <skill-root>/scripts/providers/minimax_m3_course_video.py \
  --input <video> --output-dir <authorized-output-dir> \
  --model MiniMax-M3.1-Flash --effort high --max-tokens 4096 --analyze
```

去掉 `--analyze` 仅预处理。保留当前素材和成本授权，模型支持的文档描述不证明账号权限或本次调用成功。图片/视频/ASR 分别使用自己的 payload；普通 MiniMax MCP 也需当前发现的精确工具，不能从文档存在推断通用理解能力。

## 恢复与失败

- `1026/input new_sensitive` 保存终态，不短切或循环重试。
- 视频与实验音频保留 `not_sent/rejected/accepted/acceptance_unknown/completed`。只有证明未发送或明确未接受的操作才可能有限重试。POST 超时、中断、5xx 为 unknown，2xx 空结果为 accepted，均保留原件并停止自动重发。
- 每次 POST 前落盘 marker，保留稳定 fingerprint、独立 attempt、request id、usage 和 retry disposition；不假定幂等键。
- 旧 M3 fingerprint 保留历史 temperature 字段；改成官方 Base64 传输不会把已完成操作当新请求。模型、端点或 effort 与旧 operation 不同也只报告差异，保留原状态，不写新 attempt。恢复旧任务时明确原模型和 endpoint，不删除旧证据来解锁重发。
- 无当前授权不跨 provider；MiMo 仍 disabled。

来源入口见 [官方合同](official-sources.md)。
