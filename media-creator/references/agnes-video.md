# Agnes Video 2.5

官方依据：[2.5 Flash](https://agnes-ai.com/zh-Hans/docs/agnes-video-25-flash)及其明确继承的[2.5 标准版](https://agnes-ai.com/zh-Hans/docs/agnes-video-25)。参数复核日期：2026-09-07。以下是文档与本地适配合同，未据此宣称真实生成已验证。

## 选模型与模式

Agnes 默认模型为 `agnes-video-2.5-flash`。只有用户明确选定标准版 `agnes-video-2.5`，才在命令中传该 `--model`；不得因 Flash 输入超限、分辨率冲突、等待或失败而自动换模型。两者都属于参考条件生成，不承诺逐帧保真的原视频编辑。

| 模式 | 必需输入 | 不接受的输入 |
|---|---|---|
| `text` | 非空提示词，无媒体 | 所有首尾帧与参考素材 |
| `keyframe` | `first_frame`、`last_frame` 至少一个 | `images/audios/videos` |
| `reference` | `images/audios/videos` 中至少一种非空；Flash 不支持 `videos` | `first_frame/last_frame` |

未写 `--mode` 时，适配器只依据本次明确给出的媒体参数选择模式：首尾帧选 `keyframe`，参考素材选 `reference`，无媒体选 `text`。混合互斥输入会拒绝，不丢弃素材。首帧、尾帧可单独提供；音频参考也可单独使用，无需编造附加图片。

## 官方参数与 CLI

| API 参数 | CLI | 值与约束 |
|---|---|---|
| `model` | `--model` | 默认 `agnes-video-2.5-flash`，显式可选 `agnes-video-2.5` |
| `prompt` | `--prompt` | 必填、非空 |
| `mode` | `--mode` | `text/keyframe/reference`；最终请求必定包含 |
| `seconds` | `--seconds` | `4`–`12` 的整数秒，默认 `5`；发送为字符串 |
| `size` | `--size` | Flash 仅 `720P`；标准版 `720P/1080P/1K/2K`；默认 `720P` |
| `aspect_ratio` | `--aspect-ratio` | `21:9/16:9/4:3/1:1/3:4/9:16`；通常默认 `16:9`，标准版 `1K` 默认且只接受 `1:1` |
| `seed` | `--seed` | 可选整数，包括 `0`；未指定时不发送，不保证完全确定性 |
| `n` | `--n` | 仅 `1`，默认 `1` |
| `first_frame` | `--first-frame` | 公共图片 URL；`--image` 是这一参数的单首帧简写 |
| `last_frame` | `--last-frame` | 公共图片 URL |
| `images` | 重复 `--reference-image` | 保持图片顺序；Flash 最多 5 张，标准版最多 8 张 |
| `audios` | 重复 `--reference-audio` | 保持音频顺序；最多 3 段 |
| `videos[].url` | `--reference-video` | 仅标准版；最多 1 段公共视频 URL |
| `videos[].start_seconds` | `--video-start-seconds` | 有参考视频时可用；有限非负数，默认 `0` |
| `videos[].require_audio` | `--video-require-audio` / `--no-video-require-audio` | 有参考视频时可用；默认 `false`；`true` 要求片源有音轨 |

这些字段在原始 HTTP JSON 中位于顶层，视频对象除外。OpenAI SDK 示例的 `extra_body` 是 SDK 扩展传参方式，不应照抄成旧 V2.0 的嵌套 `extra_body.mode=keyframes`。

本适配器停止创建旧模型任务，不再接受 `--num-frames`、`--frame-rate`、`--width`、`--height`、`--num-inference-steps`、`--negative-prompt` 或任意多帧 `--keyframe` 数组。不要把旧帧数擅自换算成秒，也不要把多张关键帧悄悄改为首尾两张；先根据用户的实际目标和全部输入绑定新的受支持模式。

## 参考素材限制

| 素材 | 官方限制 |
|---|---|
| 图片 | Flash ≤5 张、标准版 ≤8 张；每张小于 15 MB，图片合计小于 50 MB，宽和高各为 256–5760 像素 |
| 音频 | ≤3 段，总时长 2–12 秒；每段小于 15 MB；相关请求大小小于 64 MB |
| 视频 | 仅标准版，≤1 段，时长 2–12 秒、小于 50 MB、24–60 FPS |

标准版媒体总数不得超过 12。Flash 继承标准版的通用素材限制，并以更严格的图片数量和禁止视频规则覆盖。所有视频输入必须是 Agnes 可公开访问、在任务结束前仍有效的 HTTP(S) URL；不直接接收本地路径或 Data URI，也不自动上传文件或公开本地服务。

适配器本地检查参数组合、数量、URL 形式以及显式本地地址，不会在预览中联网检查文件。远程 DNS、实际可访问性、文件大小、像素、时长、FPS 和音轨应由主任务依据获授权素材的元数据核对；缺少证据时标为未验证，不能因参数预检通过就声称这些限制已验证。不要在错误或公开记录中回显签名 URL。

## 示例与提示词

以下均为不提交任务的预览；先将示例 URL/提示词替换为本次选定的材料。在已有生成授权和费用范围内，复核后为同一请求加 `--execute`，不重复要求逐步确认。

```bash
# 文生视频
python3 -B scripts/agnes_media.py video --prompt "雨后街道，镜头缓慢前移，轻微环境声" --seconds 5 --aspect-ratio 16:9

# 首尾帧；也允许只给尾帧
python3 -B scripts/agnes_media.py video --prompt "从开场过渡到收尾画面" --first-frame https://example.com/start.png --last-frame https://example.com/end.png

# 图片与音频参考
python3 -B scripts/agnes_media.py video --prompt "以 <Picture 1> 为主体，动作跟随 <Audio 1> 的节奏" --reference-image https://example.com/subject.png --reference-audio https://example.com/rhythm.mp3

# 纯音频参考
python3 -B scripts/agnes_media.py video --prompt "按 <Audio 1> 的节奏呈现几何图形动画" --reference-audio https://example.com/rhythm.mp3

# 显式标准版的参考视频与高分辨率；不能当作 Flash 降级重试
python3 -B scripts/agnes_media.py video --model agnes-video-2.5 --prompt "参照 <Video 1> 的运动节奏，场景为月夜庭院" --reference-video https://example.com/motion.mp4 --video-start-seconds 0 --video-require-audio --size 1080P
```

按主体与环境、动作变化、镜头运动、视觉风格、声音节奏组织提示词。参考标记从 `1` 开始，并分别对应各自图片、音频、视频列表的顺序；Flash 不应出现 `<Video N>`。主任务在发送前完成创意字段，不让执行器自行补素材或改目标。面向用户的结果说明使用用户要求的语言。

## 输出尺寸与价格

`size` 是模型档位，不能只凭名称承诺实际像素。标准版 `1K` 固定为 1024×1024，与宽幅目标冲突时应改选其他档位；适配器在未显式选画幅时为 `1K` 选 `1:1`，明确的非方形画幅则拒绝。

| 比例 | Flash 720P | 标准版 720P | 标准版 1080P | 标准版 2K |
|---|---|---|---|---|
| 21:9 | 1680×720 | 1470×630 | 2206×946 | 2940×1260 |
| 16:9 | 1280×704 | 1280×720 | 1920×1080 | 2560×1440 |
| 4:3 | 960×720 | 1112×834 | 1664×1248 | 2224×1668 |
| 1:1 | 720×720 | 960×960 | 1440×1440 | 1920×1920 |
| 3:4 | 720×960 | 834×1112 | 1248×1664 | 1668×2224 |
| 9:16 | 720×1280 | 720×1280 | 1080×1920 | 1440×2560 |

这是官方页面的参考映射，尤其 Flash 16:9 的 1280×704 是官方记录的输出观察。最终以实际文件和 `metadata.size_mapping`（若返回）为准；下载保存成功也不等于画面、声音、时长或尺寸满足用户验收。

2026-09-07 文档显示 Flash 限时免费；标准版按分辨率和时长计费，参考视频时长和超额图片也会影响费用。执行时核对最新价格与用户既有预算，缺少必要费用授权时再具体询问，不将 Flash 免费政策套用到标准版。

## 查询、保存与恢复

创建为 `POST /v1/videos`。建议先不带 `--wait` 创建一次，把返回的 `video_id` 和本次 `model` 保留到任务记录，再用下面的命令查询/下载。这使等待中断后仍可继续原任务。`id`/`task_id` 标识异步任务，不是查询视频 ID，缺少 `video_id` 时不得拿它们替代或重新生成。

```bash
python3 -B scripts/agnes_media.py video-status \
  --video-id "<original-video-id>" --model agnes-video-2.5-flash \
  --wait --output "<authorized-output.mp4>"
```

预览只显示 GET 请求；已有同任务查询/下载授权时加 `--execute`。所有模式统一查询 `GET /agnesapi?video_id=...&model_name=<original-model>`，不调用创建端点。`--model` 必填且必须来自原始记录，不能按当前默认模型猜测。`AGNES_BASE_URL` 同时接受服务根和末尾 `/v1` 的官方基址。

本地控制选项：`--wait` 等待终态；`--poll-interval` 默认 1.5 秒；`--max-wait` 默认 600 秒；`--timeout` 默认 120 秒，均须有限且为正数。`--output` 需要 `--wait`，且目标须在本次授权范围、尚不存在。`video --wait --output ...` 仍支持一次调用创建并等待，但硬中断前尚未保存的 ID 不保证可恢复。

状态为 `queued/in_progress/completed/failed`；只有 `completed` 的 `metadata.url` 可交付。缺少/未知状态、模型或查询 ID 不匹配都停止；失败任务不输出 provider 原文。`remixed_from_video_id` 不是下载字段。单次命令遇到网络错误或 429 会返回非零；主任务可在既有等待预算内退避后继续同一 ID 的查询，并按需要加大查询间隔。恢复查询沿用该任务剩余等待预算，耗尽时保留 ID、模型并报告等待未完成；不重新 POST、不切模型。

`--output` 使用与图片相同的[输出保护与恢复合同](agnes-image.md#输出保护与恢复)。常规查询、下载或保存错误时，安全目录内回执保留原始 ID、模型、已知模式与已确认的完成 URL；查询结果省略 ID 时也不会丢掉初始 ID。使用回执中的同一 `video_id`/`model` 继续 `video-status`，或保存已完成的同一 URL，不重跑创建命令。父目录移动后不向替换位置写入；`recovery.status=unavailable` 或 `path_verified=false` 不代表旧路径仍安全可用。
