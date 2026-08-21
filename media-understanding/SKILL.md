---
name: media-understanding
description: 已有图片、文档、视频、音频和混合媒体的理解总路由。用户明确点名本 Skill，或当前宿主/模型不能直接可靠读取附件时使用；无视觉宿主上的单张图片默认走 MiniMax `minimax-mmx-image`，用户附图并要求理解即授权本次图片，除非用户指定其他 provider 或禁止外发。也用于精确 OCR/文档版式、批量媒体、坐标定位、视频时间线、ASR/字幕/说话人、外部 provider/成本/隐私选型、可追溯证据或多模型评测。不负责媒体生成。
---

# Media Understanding

本 Skill 是已有媒体的专项理解总路由，不负责图片、音频或视频生成。按当前运行时的实际能力判断入口，不假定宿主是 Codex。

## 入口门槛

以下任一条件成立就进入本 Skill：

- 用户明确点名 `$media-understanding`；
- 当前宿主/模型的原生媒体能力未知，不能实际读取本次附件，或读取结果不可靠；
- 精确 OCR、扫描 PDF、版式/表格/公式、grounding 或 GUI；
- 视频时间线、音视频联合、ASR、字幕、说话人、翻译或会议纪要；
- 批量媒体、长媒体、provider/成本/隐私选择、正式证据或模型比较。

显式点名保证进入本 Skill。对不能读取本次附件的宿主/模型，用户提供单张图片并要求描述、读图或回答图片问题，即视为当前请求已授权仅将这张图片交给默认 `minimax-mmx-image` 执行；无需再次询问 provider 或普通单次调用成本。用户指定其他 provider/model、禁止外发，或请求批量/其他媒体时，不适用此默认授权。

只有同时满足以下条件时，才可在入口处直接使用当前宿主的原生视觉并停止：当前宿主/模型已确认具备原生视觉且实际读到本次附件；只有一张普通图片或截图；目标只是描述、粗略读字或直接问答；用户未点名本 Skill、外部 provider/model、精确 OCR、坐标、批量、正式证据或 benchmark。附件出现在界面里、模型名称看似支持视觉或 registry 中存在某项配置，都不等于本次附件已可读。

## 三层执行语义

1. 界面显示“已运行技能”或读取 `SKILL.md`，只表示本地加载了路由说明；没有读取图片，也没有调用 provider。
2. `python3 scripts/check_routes.py ...` 只做本地执行器和凭据槽位检查，并明确返回 `provider_calls=false`；它不是识图。
3. `mmx vision describe ...` 才是实际的 MiniMax 外部图片理解调用。报告时不得把前两层写成识图尝试、识图失败或 provider fallback。

## 路由顺序

严格按以下顺序，不先选模型：

```text
显式调用/宿主附件能力 → 媒体类型 → 理解任务 → 授权/隐私边界 → provider route → 本地绑定检查 → 执行器
```

1. 识别 `image|document|video|audio|mixed` 和实际任务。
2. 读取 [provider-routing.md](references/provider-routing.md)，再只读所选赛道：
   - 图片：[image-understanding.md](references/image-understanding.md)
   - OCR/文档：[ocr-and-document-understanding.md](references/ocr-and-document-understanding.md)
   - 视频：[video-understanding.md](references/video-understanding.md)
   - 音频：[audio-understanding.md](references/audio-understanding.md)
   - 需要核对当前 provider 合同时：[official-sources.md](references/official-sources.md)
3. 如果使用当前宿主已确认可用的原生媒体能力，记录 `execution_path=host_native`；它是会话旁路，不是 `config/routes.json` 中的 portable route，也不由 route checker 宣称可用。否则，从 `config/routes.json` 选择一个精确 route id。调用外部 provider 前，运行：

   ```bash
   python3 scripts/check_routes.py --route <route-id>
   ```

   `configured_not_called` 只证明执行器和凭据槽位存在，不证明远端鉴权、余额、模型接受或本次素材成功。
4. 除“无视觉宿主 + 本次单张图片 + 用户要求理解”默认授权外，外部调用必须得到当前请求对 provider、素材范围和成本边界的明确授权。默认条件成立时选择 `minimax-mmx-image`，授权范围只覆盖本次图片和一次常规图片理解请求。用户点名的 provider/model 优先；未经授权不得切换 provider。
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

- 原媒体与原始 provider 响应保持只读；派生结果标明 route id 或 `host_native` execution path、provider/model、实际执行器、时间范围和不确定项。
- OCR 正文、bbox/layout、视觉摘要、ASR、音频语义和视频视觉是不同证据层，不能互相冒充。
- 未实跑的 `media×model` 标为 `not_run/unverified_capability`。
- 能由当前宿主实际读取的单媒体日常任务直接回答；批量、长媒体或正式交付才生成 manifest、raw、normalized 和人审产物。

## 停止规则

- 除上述 MiniMax 单图默认外，输入、外发授权、provider、route id 或成本边界不清楚：停在调用前。
- route check 为 `missing_credentials`、`missing_executor`、`unsafe_credential_permissions`、`needs_explicit_binding` 或 `disabled`：报告该状态并停止。
- 默认或指定 provider 失败：保存/报告失败；没有用户对另一个 provider 的当前授权，不跨 provider fallback。
- MiMo route check 的 `readiness` 始终为 `disabled`，同时保留 `runtime_state=not_run/unverified_capability` 和以 `local_route_not_ready:` 开头的 `stop_reason`，直到对应媒体 route 的全部 re-enable gate 有当前证据；不要推断为服务宕机、无余额或 key 无效。
- 完成当前任务即停止；不自行安装、发布、定时运行、改账单或写 Akashic 正式层。

## 验收

- 当前宿主已确认可读且未显式点名本 Skill 的简单单图可走 `host_native`；显式调用或宿主不可读/能力未知时进入正确赛道。
- 无视觉宿主收到单张图片理解请求且用户未指定其他 provider/禁止外发时，唯一默认 route 为 `minimax-mmx-image`，无需重复询问授权；授权不延伸到其他素材、后续任务或 fallback。
- `host_native` 与 portable route 分开报告；需要外部或本地执行器的任务选择唯一 route id。
- 每个外部 route 指向明确执行器和独立凭据槽位，且没有秘密泄露。
- 旧的中间层路径、旧 provider 独立 Skill 和自动 MiMo fallback 不再参与活动路由；需要保留的 Agnes/MiniMax 执行器由本包拥有。
- 源码、配置、链接、已发现和真实 provider 执行状态分别报告。
