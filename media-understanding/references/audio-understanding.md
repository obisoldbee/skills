# Audio Understanding

## 不同证据层

| 目标 | 输出 | Route |
|---|---|---|
| 时间戳 ASR | 尽量忠实的 JSON/SRT/VTT | `local-timed-transcription`，仅当 Skill 真正已发现 |
| 课程语义理解（默认） | 主题、逻辑、例子、警告、学习行动 | `minimax-m3-transcript-semantics`：先 ASR，再交给 M3 文本语义层 |
| 课程语义理解（实验） | 非逐字语义笔记 | `minimax-m3-course-audio-via-video-experimental` |
| 火山 ASR/字幕/说话人 | 文本、时间轴、speaker 标签 | `volcengine-arkcli-understand` → `asr|asr-align|asr-speakers` |
| 火山翻译/会议纪要 | 目标语言、结构化纪要 | `volcengine-arkcli-understand` → `ast|meeting-minutes` |
| MiMo 音频理解 | 暂不执行 | `mimo-v2.5-audio` → `disabled` |

ASR 是可核对文字层，语义理解是派生解释层，不能互相冒充。精确引用只能来自已校验转写。

## MiniMax M3 边界

MiniMax-M3 官方合同未记录独立音频输入。默认流程应先通过获授权的 ASR 生成 transcript，再用 M3 文本合同做语义整理。

包内 `scripts/providers/minimax_m3_course_audio.py` 通过真实低清 MP4 载体发送音频语义任务；它不是原生纯音频接口，也不是逐字 ASR，因此只属于显式实验路线。旧同名独立 Skill 已退役，不再是运行依赖。

- `1026` 或其他不可重试结果：记录终态并返回 `provider_fallback_requires_user_opt_in`。
- 不再自动调用或假定任何 MiMo Skill 存在。
- 输出中的视觉陈述移交视频视觉层，不能留在音频语义笔记里。

## 输入与失败

- 长音频按执行器合同切片，字幕与说话人任务保持连续时间轴。
- 无语音时写 `no_speech`，不生成臆测纪要。
- 失败段保留索引；只有当前授权允许时才重试或切换 provider。
- Ark CLI 使用自己的认证状态；不得把火山 Plan env 当作其隐式 key 来源。
