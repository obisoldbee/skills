# Provider And Model Routing

## 三层选择

```text
媒体：image | document | video | audio | mixed
任务：holistic | OCR | layout | grounding | GUI | timeline | ASR | speakers | semantics | benchmark
路线：一个 config/routes.json route id
```

`host_native` 是当前会话已确认可读取本次附件时的宿主旁路，不是 portable route。用户未点名本 Skill 且任务仅为普通单图描述、粗略读字或直接问答时，可在进入本表前使用该旁路。用户显式调用本 Skill，或宿主/模型不能读取本次附件、能力未知时，必须进入本路由；不要从附件存在、模型名称或静态配置推断原生能力。

## 无视觉宿主的单图默认

以下条件同时成立时，不再询问 provider 或普通单次调用成本，直接选择 `minimax-mmx-image`：

- 当前宿主/模型不能实际读取本次附件；
- 用户提供的是本次任务所指向的单张图片，并要求描述、读图或回答图片问题；
- 用户没有指定其他 provider/model，也没有禁止把图片发给外部服务。

“附图 + 要求理解”即为本次图片的窄范围授权，只覆盖一次常规 MiniMax 图片理解调用；不覆盖其他附件、批量任务、后续请求、其他媒体或失败后的跨 provider fallback。若 MiniMax route 未配置或调用失败，报告并停止，等待用户决定是否改用其他路线。

## 活动路线

| 媒体/任务 | Route id | 精确执行器 | 外部凭据 |
|---|---|---|---|
| 无视觉宿主的默认单图理解 | `minimax-mmx-image` | `$mmx-cli` → `mmx vision describe`；底层模型未暴露 | `~/.codex/secrets/minimax.env` |
| MiniMax-M3 direct 图片理解 | `minimax-m3-image` | Anthropic-compatible Messages adapter；当前需显式绑定 | `~/.codex/secrets/minimax.env` |
| MiniMax 课程视频视觉 | `minimax-m3-course-video` | 包内 `scripts/providers/minimax_m3_course_video.py` | `~/.codex/secrets/minimax.env` |
| MiniMax 音频语义主路由 | `minimax-m3-transcript-semantics` | 获授权的 ASR → transcript → MiniMax-M3 文本请求；需显式绑定 | `~/.codex/secrets/minimax.env` |
| MiniMax 音频语义实验 | `minimax-m3-course-audio-via-video-experimental` | 包内 `scripts/providers/minimax_m3_course_audio.py`，真实低清 MP4 载体 | `~/.codex/secrets/minimax.env` |
| Agnes 图片理解 | `agnes-image` | 包内 `scripts/providers/agnes_vision.py` | `~/.codex/secrets/agnes.env` |
| 火山生产图/文/视频/音频 | `volcengine-platform-responses-files` | 普通 Ark Platform Responses + Files；当前需绑定 adapter | 普通 Platform 专用变量 |
| 火山通用图/文/视频/音频 | `volcengine-arkcli-understand` | `arkcli +understand <recipe>` | Ark CLI 自己的认证状态 |
| 火山 Agent Plan | `volcengine-agent-plan-profile` | 仅绑定官方支持的 AI 工具 | Agent Plan 专用变量 |
| 火山 Coding Plan | `volcengine-coding-plan-profile` | 仅绑定官方支持的编程工具 | Coding Plan 专用变量 |
| 本地 OCR/文档 | `local-ocr-document` | 当前请求显式绑定 | 该服务自己的配置 |
| 本地时间戳 ASR | `local-timed-transcription` | 仅限已发现的 `timed-transcription` | 通常无外部 key |
| MiMo 图片 | `mimo-v2.5-image` | 无 | 禁用；凭据文件存在，adapter/profile alias 未绑定 |
| MiMo 音频 | `mimo-v2.5-audio` | 无 | 禁用；凭据文件存在，adapter/profile alias 未绑定 |
| MiMo 视频 | `mimo-v2.5-video` | 无 | 禁用；凭据文件存在，adapter/profile alias 未绑定 |

## 状态词

`scripts/check_routes.py` 只做本地、无网络检查：

| Readiness | 含义 |
|---|---|
| `configured_not_called` | 执行器、env 文件和必需变量名存在；POSIX 系统上的私有权限检查通过；没有调用 provider |
| `missing_credentials` | env 文件或必需变量缺失 |
| `unsafe_credential_permissions` | POSIX 系统上的 key 文件对 group/other 开放 |
| `configuration_mismatch` | 安全白名单配置（如模型 ID）与 route 合同不一致 |
| `missing_executor` | CLI、包内脚本、Skill 或 helper 缺失 |
| `needs_explicit_binding` | 需要在当前任务绑定本地 endpoint/Skill |
| `disabled` | 路线保留但禁止执行 |

不要把 `configured_not_called` 写成远端可用、余额充足、模型已接受或任务成功。
Windows 不提供等价的 POSIX group/other mode 证据，因此 `private_permissions` 报告 `null`，而不是把 Windows ACL 推断为安全或不安全。
Route checker 只检查 portable registry；它不探测或证明任何宿主的原生附件能力。

## 火山隔离

普通 Ark Platform、Agent Plan 与 Coding Plan 共用一个 env 文件只是存储选择，不代表共用 key 或额度。普通 Platform 生产路由使用 Responses + Files；两个 Plan 只经官方支持工具。Ark CLI 维护自己的认证状态，四者都不是彼此 fallback。

当前本地普通 `VOLCENGINE_ARK_BASE_URL` 若指向 Coding Plan URL，`volcengine-platform-responses-files` 仍必须停在配置检查，不能因为存在 generic key 名称就宣称普通 Platform 已绑定。

`arkcli +understand` 是一个 Responses 引擎加语义配方层。图片、视频、PDF 的已安装配方仍可能解析到陈旧的 `doubao-seed-1-6`；调用前必须查看当前 recipe/model 解析，模型不在所选 profile 当前清单即停止。PDF 的 CLI 路径最终仍是 Files + Responses，不是第二套推理引擎。

模型名单和默认模型可能变化；运行 provider adapter 的 `--check-route` 读取当前本地配置，再对照当前官方文档。不得把历史名单硬编码为永久能力。

历史火山图片独立 Skill 的自定义 Plan Chat helper 已退役并只保存在 Akashic。统一路由不会把它内部化，也不会经它调用 Plan；普通生产请求继续使用 Platform Responses + Files，Plan 继续只经官方支持工具。

## MiMo 保留边界

MiMo 的图/音/视频 route、三份官方文档 URL 和逐媒体 re-enable gate 保留在 `config/routes.json`，但当前 executor 都是 `none`、status 都是 `disabled`。任何 MiniMax `1026` 或其他失败只报告 `provider_fallback_requires_user_opt_in`；不得自动改走 MiMo。

本地凭据文件原名为 `~/.codex/secrets/mimo-routing.env`，现已原字节改名为标准槽位 `~/.codex/secrets/mimo.env`。它保留 Token Plan 与 API Billing 两套独立变量；当前 portable registry 的 generic `MIMO_API_KEY` alias 尚未绑定。不得自动复制、合并或改写 key。

当前官方合同使用 `mimo-v2.5` 和按量 OpenAI 兼容 `POST /v1/chat/completions`；Token Plan 的 Base URL/key 不得与按量 profile 混用。页面可读不等于本地 key、账号权限或调用成功。

## 授权与失败

- 对无视觉宿主的本次单张图片理解请求，用户附图并要求理解即授权 `minimax-mmx-image`；无需再问一次。该默认不扩展到批量、其他媒体或 fallback。
- 用户点名 provider/model 时，只授权该 profile 与本次素材。
- “选择最合适的外部模型”允许在同一任务族内选择一个已有当前证据的路线，不等于允许多 provider 试跑。
- 连接重试只按执行器自己的有限策略；模型拒绝、空输出或格式错误不授权跨 profile fallback。
- key、token、cookie 不进入提示词、日志、Git、12 包或 provider 结果。
