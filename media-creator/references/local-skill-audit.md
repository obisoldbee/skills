# 本地生成 Skill 快速审计

## 证据边界

2026-08-13 对 11 个现有 Agent Skill 根做了只读扫描：共观察到 814 条可解析的 `SKILL.md` 路径；消除跨 Agent 链接和重复实体后为 545 个物理 Skill payload。另观察到 Codex plugin cache 中 260 个 `SKILL.md`。这些是文件系统计数，不证明宿主已发现、加载或执行。

扫描未调用生成供应商、未读取密钥值或 cookie。缺失的 `~/.claude/skills` 没有创建。`media-creator` 已在 11 个现有消费者中形成指向 GitHub 真源的健康直链。

三个融合前 Skill 的物理源完成封存后退出；审计随后发现并删除 3 条指向旧源的悬空消费者链接。活动根中不再存在 `chatgpt-image-gen`、`agnes-image-generation` 或 `agnes-video-generation`；它们只作为 Akashic 历史快照保留。

## 观察到但不纳入当前路由

| Skill/家族 | 观察能力 | 当前处置 | 原因 |
|---|---|---|---|
| Codex system `imagegen` | 文生图、参考图生成、图片编辑 | `native_owner` | Codex 普通生图直接使用原生能力，本 Skill 不触发、不包装、不修改 |
| `byted-seedream-image-generate` | 文生图、图生图、批量输出；本地文档列出 Seedream 4.x/5.x | `observed_not_routed` | 独立 ARK provider Skill；模型、鉴权、脚本与失败合同尚未按本包标准验证 |
| `byted-seedance-video-generate` | 文生视频、首尾帧、图片/视频/音频参考；部分模型声明生成音频 | `observed_not_routed` | 独立 ARK provider Skill；不是用户指定的默认 MMX/显式 Agnes 路线，版本与输入语义可能漂移 |
| QwenWork `media-generation` | 宿主内置异步视频与音乐；文生、单图、首尾帧、多参考图 | `harness_native_keep_independent` | 依赖 QwenWork 内置工具和任务卡，不可移植成通用脚本；是否优先于 MMX 需单独产品决策 |
| Qwen/Qoder `video-generation` | 结构化提示词和参考图视频 | `harness_specific_candidate` | 当前说明写死 `/mnt` 宿主路径，不能作为 macOS 通用后端 |
| MiniMax `image-creator` | 17 类风格化图片生产模板 | `specialized_workflow_keep_independent` | 上层创作模板，不是通用 provider 合同 |
| MiniMax `story-video-generator` | 脚本、参考图、分镜、视频片段、BGM、合成 | `specialized_workflow_keep_independent` | 上层多阶段故事视频流水线，不替代底层路由 |
| HyperFrames / Remotion | HTML/代码视频合成、渲染、字幕；HyperFrames 另有本地 TTS/转写/抠像 | `composition_keep_independent` | 程序化合成与资产处理，不是生成模型 provider fallback |
| HeyGen | 头像与演示者视频 | `plugin_provider_keep_independent` | 垂直插件能力，仅在明确 HeyGen 工作流中使用 |
| Adobe / Creative Production | 模板、修图、变体、mockup、quick cut | `plugin_workflow_keep_independent` | 设计/编辑工作流，不属于当前通用生成供应商集合 |
| `baoyu-*`、`image`、角色设定、表情专辑 | 封面、营销图、角色/专辑生产 | `specialized_workflow_keep_independent` | 可选择某个生成后端的上层工作流，不应被吸收到后端路由 |
| `media-understanding`、image analyzer、转写、录屏、压缩、增强 | 理解、采集或后处理 | `out_of_scope` | 与显式生成分离 |

部分其他 Agent 根存在一个指向 Codex system `imagegen` 的文件链接。它只证明文件系统投影，不能证明非 Codex 宿主拥有 Codex 的原生 `image_gen` 工具绑定；本 Skill不得据此把该宿主判定为原生生图可用。

## 当前无遗漏的合同面

- 图片：文生图、单主体参考、通用图生图/编辑、多图合成及 mask 未验证边界；
- 视频：文生、单图、首尾帧、图片关键帧、参考图/视频/音频，以及“参考视频不等于精确视频编辑”；
- 音频：文字转语音、字幕、音乐、纯伴奏、歌词歌曲与翻唱；
- 运行：登录/依赖预检、MMX 配额三态、异步任务 ID、防重复提交、下载回读；
- 治理：Codex 原生排除、MMX 外置、其他 provider `observed_not_routed`、凭据不入包。

## 未来纳入门槛

任何 `observed_not_routed` 候选要进入默认或显式路线，必须先确认：当前官方/运行时模型、可用输入模式、鉴权来源、配额语义、提交与轮询 ID、结果 URL/下载、重复提交风险、错误合同和回归测试。盘点本身不授予 provider 调用或复制 Skill 的权限。
