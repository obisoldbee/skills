# Video Understanding

## 先区分目标

新增密集三合一分支 [kimi-trimodal.md](kimi-trimodal.md)：`kimi-trimodal-swarm`，
默认每秒 2 帧、音频导出、本地词级时间戳 ASR，再由 3 个独立 MiniMax-M3 观察者
各自读取全量材料。使用视频同目录 `frames_<视频名>`；不替换普通原生视频路径。

- `video_summary`：整体内容、章节与关键时间点。
- `video_qa`：围绕一个问题定位相关片段并回答。
- `audio_visual`：同时分析画面、说话、音乐和声音事件。
- `course_screen_visual`：屏幕文字、UI 状态、操作步骤、幻灯片与图表。
- `benchmark`：比较时间顺序、跨镜头连续性、文字、声音与整体结论。

## 直接路线

Kimi Code 新分支见 [kimi-readmedia.md](kimi-readmedia.md)：`kimi-readmedia` 普通模式，
`kimi-readmedia-swarm` 默认 3 个独立上下文同题观察。默认 MiniMax-M3；可选 Agnes 3.0 Flash
原生视频按显式授权的兼容性实验验证。两条模式均使用内置 `ReadMediaFile`，不替换下面的 direct 路线。

| 目标 | Route | 执行器 |
|---|---|---|
| 课程视频视觉 | `minimax-m3-course-video` | 包内 `scripts/providers/minimax_m3_course_video.py` |
| 课程音频语义 | `minimax-m3-transcript-semantics` | 获授权的 ASR → transcript → MiniMax-M3 文本请求 |
| 课程音频语义实验 | `minimax-m3-course-audio-via-video-experimental` | 包内 `scripts/providers/minimax_m3_course_audio.py` |
| 时间戳 ASR | `local-timed-transcription` | 仅限新任务中实际发现的 `timed-transcription` |
| 火山视频总结/问答/音视频联合 | `volcengine-arkcli-understand` | `arkcli +understand video-summary|video-qa|vau` |
| MiMo 视频理解 | `mimo-v2.5-video` | 禁用，无 executor |

不存在活动的历史中间层或同名 provider 独立 Skill。需要三轨融合时，总路由直接调用上述包内执行器和已绑定 ASR，并分别保存视觉、音频语义和 ASR 证据。

## 输出

```text
整体结论
章节/事件时间线（start/end）
关键画面与可见文字
声音/对白证据（如本任务包含）
跨片段关系
不确定与缺失片段
```

不要把视频压成一张代表截图后声称完成视频理解。批量或人审产物使用播放器、可点击时间点、关键帧/分镜和对应文字。

## 长视频

- 先探测时长、音视频流和尺寸。
- 按执行器已验证参数切段并保留少量重叠。
- 保存 segment manifest 与每段原始响应。
- 合并时去除重叠重复，保留时间戳与冲突。
- 某段失败不得伪装为整段已理解。

## 提交与恢复状态

视频 direct adapter 与音频使用同一矩阵：`not_sent|rejected|accepted|acceptance_unknown|completed`。自动重试只接受 `proven_not_sent` 或 `proven_not_accepted` 证据；POST 后超时、连接中断、5xx 和其他不明接收结果进入 `acceptance_unknown`，2xx 空结果进入 `accepted`。这两类状态禁止自动重发，`--resume` 只能读取并报告已有 operation，不能再 POST。每次响应保存到独立 attempt 文件，并记录 operation fingerprint、provider request id/usage（如有）和 retry disposition；不发送未被官方合同证明支持的幂等键。
