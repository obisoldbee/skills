---
name: media-creator
description: Route non-native media generation for video, speech, music, and provider-explicit ChatGPT Web, MiniMax Web Music, MiniMax MMX, or Agnes requests. In Codex, do not use this Skill for ordinary image generation or image editing while the built-in imagegen/image_gen path is available; let native imagegen handle those requests directly. Use it for generic image generation on non-Codex agents, preferring an authenticated ChatGPT Web browser route on eligible macOS/ego-browser environments and using MMX only for supported pre-submission fallback modes. Also use it for MiniMax Web Music, MMX or Agnes video generation, MMX speech or explicitly eligible legacy music/cover generation, or when the user explicitly names one of these providers.
---

# Media Creator

统一管理非原生图片、视频、语音和音乐生成，同时保留每个宿主的原生能力边界。

## 守住 Codex 原生图片边界

遇到 Codex 中未指定供应商的普通生图、参考图生成或图片编辑请求时，停止使用本 Skill，让原生 `imagegen` / `image_gen` 直接处理。不要先加载本 Skill 再转回原生工具，也不要把 ChatGPT Web、MMX 或 Agnes 变成 Codex 原生生图的自动降级路线。

只有以下情况才在 Codex 中继续使用本 Skill：

- 用户明确指定 ChatGPT Web、MMX 或 Agnes；
- 请求是视频、语音、音乐或翻唱；
- 当前宿主明确没有原生图片生成能力。

## 冻结输入与写入边界

执行型请求在选路前先冻结本次输入集合及顺序（文本、当前附件或精确本地路径），并为每个产物给出调用方授权的精确输出路径或单一输出根。不从当前工作目录、相邻文件或历史任务推断输入/输出。输入只读；除已授权输出与所选 provider 合同要求的同根回执外，不写其他路径，不覆盖已有产物。

把提示词、规划、预览和 dry-run 的写入集合固定为空。只使用当前运行时已发现且经该路线检查可用的 Skill、CLI 或浏览器执行器；缺少时报告精确 blocker 并停止，不安装依赖、创建链接、修改配置/凭据或吸收一个未验证的替代路线。

## 共享执行合同：planner → 获授权的浏览器执行器

ChatGPT Web 图片和 MiniMax Web Music 都把创意规划与网页机械执行分开：发起任务的主任务负责理解意图，并在执行前创建完整、最终的 provider payload。ChatGPT Web payload 至少包含最终图片提示词、输入文件及顺序（没有输入图时为空列表）和调用方授权的输出路径；MiniMax Web Music payload 至少包含标题、纯音乐/人声模式、风格提示词、歌词（如有）、数量和调用方授权的输出路径。浏览器执行器只能按 payload 填表、提交、等待、下载和验证，不能重新创作、改写或补齐创意字段。

必须把 `provider_execution_authority` 与 `visible_task_creation_authority` 分开判定：普通浏览器生成请求可授权一次有界 provider 提交，但不授权 `create_thread`。仅当用户明确要求“新任务”、“新线程/新对话”、“交接”或“Luna 可见任务”时，才具有 `visible_task_creation_authority`。用户只要 prompt/提示词、规划、preview/预览或 dry-run 时，规范化为对应非执行 mode，两种权限都为 `false`：不打开浏览器、不调用 provider、不创建任务。

对已授权的生成请求，先检查当前任务的已验证浏览器能力：有能力且用户未明确要求新可见任务时，在当前任务按同一 envelope 执行，`ego-browser` 仍是首选。当前任务无可用浏览器且缺少可见任务授权时，返回 `needs_visible_task_authority`，不自行扩大请求。只有获得显式可见任务授权后，才按 `$project-handoff` 创建并校验精确的 `luna-max` visible thread：model=`gpt-5.6-luna`、reasoning=`max`、surface=`visible_thread`。交接 envelope 标记 `execution_role=browser_worker`、`handoff_depth=1`，worker 收到后直接执行，禁止递归 handoff 或再次 dispatch Luna。显式 Luna 请求失败时不得降级。

登录、验证码、人工确认、当前费用非零或费用/授权不明确时，在提交前通过 ego-browser handoff 暂停。一次提交后保留任务状态，不切换 provider、不重复提交；下载失败只处理同一结果。任何浏览器操作或可见任务创建前，必须让 `scripts/validate_browser_envelope.py` 接受完整 JSON envelope；完整字段和停止条件见 [browser-handoff-envelope.md](references/browser-handoff-envelope.md)。

## 选择路线

1. 识别模态：`image`、`video`、`speech`、`music` 或 `music-cover`。
2. 识别输入模式：文本、单图、编辑目标、多图、首尾帧、关键帧、参考视频或参考音频。
3. 用户显式指定 provider/model 时优先遵从；若该路线不支持输入模式，明确说明并请求改选，禁止丢弃输入后继续。
4. 未指定 provider 时按 [routing-policy.md](references/routing-policy.md) 选择。
5. 提交前完成依赖、登录、鉴权或配额预检。提交后保留任务 ID，不因等待中断而重复提交。
6. 下载或保存产物，验证文件类型、非零大小和用户要求的输出位置。

跨供应商 fallback 只能发生在确认原路线尚未创建任务时。路线一旦提交，禁止跨供应商 fallback；等待或下载失败只能继续核对同一任务/结果，不能靠另投 provider 掩盖不确定状态。

## 图片

- 非 Codex 文生图：在 eligible macOS、ego-browser 可用且 ChatGPT 登录态可复用时优先 ChatGPT Web，并按上面的分轴授权/最终 payload 合同执行；只有在选定浏览器路线之前就确认所需 browser capability 根本不存在时，才可按未指定 provider 的预提交 fallback 使用 MMX；已选定浏览器路线但缺少可见任务授权时返回 `needs_visible_task_authority`。
- 非 Codex 通用图生图、编辑或多图合成：ChatGPT Web 当前只观察到可用的多文件上传控件，端到端编辑尚未验证；先做运行时验证。不可用或验证失败时询问是否改用 Agnes。MMX 当前不是通用图生图 fallback。
- Agnes 图片：仅在用户显式指定，或能力不匹配后用户确认切换时使用。
- MMX 图片：仅承诺文生图和单主体参考，不承诺 mask、通用编辑或多图合成。

执行 ChatGPT Web 前读取 [chatgpt-web-image.md](references/chatgpt-web-image.md)。执行 MMX 或 Agnes 图片前分别读取 [mmx.md](references/mmx.md) 或 [agnes-image.md](references/agnes-image.md)。

## 视频

未指定 provider 时优先 MMX，但每次创建 MMX 视频任务前查询 Token Plan 视频配额：

```bash
mmx quota show --output json --quiet --non-interactive
```

将结果归为：

- `known_positive`：精确匹配的 MMX 视频配额明确有余量，继续生成；
- `known_exhausted`：明确耗尽，询问“继续 MMX 付费路径，还是切换 Agnes”；
- `unknown`：查询失败、缺少对应模型、字段歧义或 H3 Pay-as-you-go 路线，不能当成零次，也必须询问。

MMX H3 的参考视频是参考条件生成，不等于确定性的原视频编辑、逐帧变换或保真 video-to-video。Agnes 当前只承诺文生视频、单图生视频和图片关键帧动画，不承诺视频输入。

执行前读取 [mmx.md](references/mmx.md) 或 [agnes-video.md](references/agnes-video.md)。

## 语音与音乐

- 通用原创歌曲和纯音乐 BGM 默认使用 MiniMax Web Music：`https://www.minimaxi.com/audio/music`。它是独立的浏览器路线，使用实时模型/费用控件，默认只生成 1 首，等待全曲完成后下载并验证 MP3；详细合同见 [minimax-web-music.md](references/minimax-web-music.md)。网页失败不得静默切换到 MMX API 音乐。
- MMX 音乐 API 不是通用默认路线。只有用户明确选择、且运行时确认是 2026-08-20 公告所述历史付费 API 用户时才可使用；免费音乐模型已停止。MMX 仍是外置、可升级依赖，不复制其 Skill、CLI 或凭据；speech 仍是独立的 MMX 语音路线。详细边界见 [mmx.md](references/mmx.md)。
- MiniMax Web Music 当前合同不承诺 voice cloning、reference-audio editing、cover、精确时长或商用许可。翻唱/cover 若有明确需求，不能把 Web Music 当作支持路线，应按 MMX legacy eligibility 或其他明确 provider 合同处理。

## 其他本地生成能力

本机还可能存在宿主原生、垂直工作流或其他供应商 Skill。它们不自动成为本 Skill 的 fallback，也不应因“目录存在”被吸收或视为可执行。当前盘点与处置边界见 [local-skill-audit.md](references/local-skill-audit.md)。

- Codex 系统 `imagegen`、其他宿主的内置媒体工具：保留宿主所有权；文件链接不证明工具绑定可用。
- Seedream/Seedance、HeyGen 等其他供应商：只作为已观察候选，除非用户显式点名且对应独立 Skill 的当前合同已验证，否则不进入本路由。
- HyperFrames、Remotion、故事视频、封面/专辑等：属于合成或上层生产流程，可调用生成后端，但不等于通用 provider 路由。
- `media-understanding`、转写、录屏、压缩、增强：属于理解或后处理，不纳入生成 provider fallback。

若未来要增加新 provider，先单独审计鉴权、输入模式、异步任务、配额、下载与失败语义，再修改 `config/routes.json` 和回归测试；不要只把另一个 Skill 目录复制进本包。

## 本地检查与 Agnes 适配器

先运行纯本地检查：

```bash
python3 -B scripts/check_routes.py
python3 -B scripts/validate_skill.py
python3 -B scripts/validate_browser_envelope.py <envelope.json>
```

这些验证命令不得调用供应商或读取密钥值。只有明确执行 Agnes 时才使用：

```bash
python3 -B scripts/agnes_media.py <subcommand> ... --execute
```

不带 `--execute` 时必须只输出请求预览，并明确报告 `provider_calls=false`、`secrets_read=false`。

## 状态与安全

- 区分 `documented`、`configured_not_called`、`submitted`、`completed` 和 `verified_artifact`。
- 安装、健康链接、登录页或 masked auth 不证明供应商调用成功。
- 不输出、复制或提交 API Key、cookie、账号标识或浏览器私有历史。
- 缺少登录时按浏览器 Skill 交给用户完成正常登录；不读取凭据，不绕过 CAPTCHA、MFA 或 QR。
- 所有输出路径必须由当前任务明确提供；禁止写死个人目录。
- 生成与媒体理解保持分离；需要 OCR、画面理解或转写时显式调用独立的 media-understanding 路线。

完整能力矩阵与回归用例见 [routing-policy.md](references/routing-policy.md)。
