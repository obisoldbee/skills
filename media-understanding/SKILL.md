---
name: media-understanding
description: 不用于单张普通图片或截图的描述、粗略读字和直接问答；这类请求由 Codex 原生视觉直接完成。仅在用户明确点名本 Skill，或任务需要精确 OCR/文档版式、批量媒体、坐标定位、视频时间线、ASR/字幕/说话人、混合媒体、外部 provider/成本/隐私选型、可追溯证据或多模型评测时使用。负责专项媒体任务的总路由、凭据隔离、执行器委派和结果封装。
---

# Media Understanding

本 Skill 是已有媒体的专项理解总路由，不是普通看图包装，也不负责图片、音频或视频生成。

## 入口门槛

同时满足以下条件时，直接用 Codex 原生视觉回答并停止：只有一张已附且可读的普通图片或截图；目标只是描述、粗略读字或直接问答；用户未点名本 Skill、外部 provider/model、精确 OCR、坐标、批量、正式证据或 benchmark。

以下任一条件成立才进入本路由：

- 用户明确点名 `$media-understanding`；
- 精确 OCR、扫描 PDF、版式/表格/公式、grounding 或 GUI；
- 视频时间线、音视频联合、ASR、字幕、说话人、翻译或会议纪要；
- 批量媒体、长媒体、provider/成本/隐私选择、正式证据或模型比较。

## 路由顺序

严格按以下顺序，不先选模型：

```text
媒体类型 → 理解任务 → 授权/隐私边界 → provider route → 本地绑定检查 → 执行器
```

1. 识别 `image|document|video|audio|mixed` 和实际任务。
2. 读取 [provider-routing.md](references/provider-routing.md)，再只读所选赛道：
   - 图片：[image-understanding.md](references/image-understanding.md)
   - OCR/文档：[ocr-and-document-understanding.md](references/ocr-and-document-understanding.md)
   - 视频：[video-understanding.md](references/video-understanding.md)
   - 音频：[audio-understanding.md](references/audio-understanding.md)
   - 需要核对当前 provider 合同时：[official-sources.md](references/official-sources.md)
3. 从 `config/routes.json` 选择一个精确 route id。调用外部 provider 前，运行：

   ```bash
   python3 scripts/check_routes.py --route <route-id>
   ```

   `configured_not_called` 只证明执行器和凭据槽位存在，不证明远端鉴权、余额、模型接受或本次素材成功。
4. 外部调用必须得到当前请求对 provider、素材范围和成本边界的明确授权。用户点名的 provider/model 优先；未经授权不得切换 provider。
5. 委派到精确执行器：
   - MiniMax 快速图片：`$mmx-cli`，命令 `mmx vision describe`；CLI 不暴露底层模型，不得写成 `MiniMax-VL-01`；
   - MiniMax-M3 图片：选择 `minimax-m3-image`；默认走官方推荐的 Anthropic-compatible `/anthropic/v1/messages`，在 direct adapter 明确绑定前保持 `needs_explicit_binding`；
   - MiniMax 课程视频视觉：选择 `minimax-m3-course-video`，运行包内 `python3 scripts/providers/minimax_m3_course_video.py --input <video> [--analyze]`；M3 direct 默认走 Anthropic-compatible Messages；
   - MiniMax 音频语义默认先做获授权的 ASR，再通过 Anthropic-compatible Messages 把 transcript 交给 `MiniMax-M3`；实验兼容路线 `minimax-m3-course-audio-via-video-experimental` 运行包内 `python3 scripts/providers/minimax_m3_course_audio.py --input <media> [--analyze]`，把音频装入真实低清 MP4，只能显式选择；
   - Agnes 图片：选择 `agnes-image`，运行包内 `python3 scripts/providers/agnes_vision.py --image-url <url> --prompt <question>`，模型 `agnes-2.5-flash`；
   - 火山生产主路由：普通 Ark Platform 的 Responses API + Files API；需要先绑定普通 Platform adapter 和非 Plan 的 Base URL/key；
   - 火山交互式配方：`arkcli +understand <recipe>`，使用 Ark CLI 自己的登录/配置，调用前核对 recipe 实际解析模型；
   - 火山 Agent/Coding Plan：只经官方支持的 AI/编程工具；不得把自定义 Python Chat/Responses 请求当作普通 Plan API；
   - 本地 OCR/ASR：只在当前任务绑定到实际可用的本地执行器后使用；源码存在或文档提及不算可执行；
   - MiMo：`mimo-v2.5-image|audio|video` 三条合同分别保留为 `disabled`，当前不得调用，也不得作为自动 fallback。
6. MiniMax profile 的媒体合同见 [minimax-shared-api.md](references/minimax-shared-api.md)。只有需要结构化保存时读取 [result-contract.md](references/result-contract.md)；只有用户要求比赛/回归时读取 [benchmark-and-reporting.md](references/benchmark-and-reporting.md)。

## 凭据隔离

本仓库不保存任何 `.env`、key、token 或 cookie。默认本地槽位为：

| provider | env file | 关键变量 |
|---|---|---|
| MiniMax | `~/.codex/secrets/minimax.env` | `MINIMAX_API_KEY`, optional `MINIMAX_BASE_URL` |
| Agnes | `~/.codex/secrets/agnes.env` | `AGNES_API_KEY`, `AGNES_MODEL`, optional `AGNES_BASE_URL` |
| 火山普通 Platform + 两个 Plan | `~/.codex/secrets/volcengine-ark.env` | `VOLCENGINE_ARK_*`、`VOLCENGINE_AGENT_PLAN_*`、`VOLCENGINE_CODING_PLAN_*` 三组独立变量 |
| MiMo | `~/.codex/secrets/mimo.env` | 文件已存在；当前保存 `MIMO_TOKEN_PLAN_*` 与 `MIMO_API_BILLING_*` 两组独立 profile，portable route 的 generic alias 与 adapter 尚未绑定 |

同一文件中的普通 Platform、Agent Plan、Coding Plan 仍是三个独立 profile。不得互相借 key、URL、模型名单或额度。若 `VOLCENGINE_ARK_BASE_URL` 指向 `/api/plan/v3` 或 `/api/coding/v3`，普通 Platform route 必须报配置不匹配。

## 证据和结果

- 原媒体与原始 provider 响应保持只读；派生结果标明 route id、provider/model、实际执行器、时间范围和不确定项。
- OCR 正文、bbox/layout、视觉摘要、ASR、音频语义和视频视觉是不同证据层，不能互相冒充。
- 未实跑的 `media×model` 标为 `not_run/unverified_capability`。
- 单媒体日常任务直接回答；批量、长媒体或正式交付才生成 manifest、raw、normalized 和人审产物。

## 停止规则

- 输入、外发授权、provider、route id 或成本边界不清楚：停在调用前。
- route check 为 `missing_credentials`、`missing_executor`、`unsafe_credential_permissions`、`needs_explicit_binding` 或 `disabled`：报告该状态并停止。
- 指定 provider 失败：保存/报告失败；没有当前授权不跨 provider fallback。
- MiMo route check 的 `readiness` 始终为 `disabled`，同时保留 `runtime_state=not_run/unverified_capability` 和以 `local_route_not_ready:` 开头的 `stop_reason`，直到对应媒体 route 的全部 re-enable gate 有当前证据；不要推断为服务宕机、无余额或 key 无效。
- 完成当前任务即停止；不自行安装、发布、定时运行、改账单或写 Akashic 正式层。

## 验收

- 普通单图不误触发；专项任务进入正确赛道和唯一 route id。
- 每个外部 route 指向明确执行器和独立凭据槽位，且没有秘密泄露。
- 旧的中间层路径、旧 provider 独立 Skill 和自动 MiMo fallback 不再参与活动路由；需要保留的 Agnes/MiniMax 执行器由本包拥有。
- 源码、配置、链接、已发现和真实 provider 执行状态分别报告。
