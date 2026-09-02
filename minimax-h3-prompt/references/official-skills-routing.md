# MiniMax H3 官方开源 Skill 路由

本页是对 MiniMax 官方开源仓库 `MiniMax-AI/MiniMax-H3` 中 `skills/` 的原创路由摘要，不是上游文件副本。核对快照：2026-09-02，`main@d21241f0a4b3acbb34c97dae47fa417b7065e438`。

## 一条入口，两层能力

`minimax-h3-prompt` 始终是用户入口。包内只读解析器会验证官方 checkout 的 remote、分支、上游、clean 状态、稀疏路径和已审查 HEAD，再返回本轮可以读取的一个官方入口。官方内容分成两层：

1. `h3-prompt-writing`：可移植的结构化提示词规范，可在能读取 Markdown 的通用 Agent 中使用。
2. 八个风格 Skill：为 MiniMax Hub 设计的完整生产流程，依赖画布、选择卡片或 `hub_*` 工具。在 Codex 等非 Hub 环境中只采用其创意目标、输入清单、分镜重点和验收思路。

不要让用户在九个 Skill 名称中自行拼装。入口先判断任务，再最多选择一个风格方向，最后统一交给 H3 模式和提示词输出流程。解析器不可用时使用本页的冻结摘要，但不得声称已经读取完整官方流程。

## 通用提示词规范

| 用户素材语义 | 官方模式 | 结构化输出 |
|---|---|---|
| 无素材 | `T2VA` | Base 三字段 |
| 一张明确首帧 | `I2VA` | 首帧对齐说明 + Base 三字段 |
| 一张明确尾帧 | `L2VA` | 尾帧对齐说明 + Base 三字段 |
| 明确首帧与尾帧 | `FL2VA` | 两端对齐说明 + Base 三字段 |
| 人物、场景、风格、视频、音频、多来源参考或视频编辑 | `Ref2VA` | 六字段引用分析与时间线 |

Base 三字段：`integrated_multimodal_description`、`overall_soundscape`、`non_diegetic_music`。

Ref2VA 六字段：`subject_definitions`、`summary`、`retention_analysis`、`detailed_description`、`overall_soundscape`、`non_diegetic_music`。

结构化字段主体使用英文；台词、歌词和画面文字保留原语言。引用标签在全部字段中保持一致。

结构化格式的标签、对齐说明、任务类型和保留关系值属于执行合同，详见 [prompt-workflow.md](prompt-workflow.md)。不要只输出字段标题或把 Ref2VA 缩成普通剧情梗概。

## 八个创意方向

| 方向 | 解析器 route | 适用目标 | 非 Hub 环境中采用 | 不采用 |
|---|---|---|---|---|
| 极简产品广告 | `minimalist-product-ad-generator` | 单一实体产品、电商上新、质感卖点短片 | 产品锚点、卖点优先级、短文案、节拍与简洁镜头 | Hub 画布、生成与合成动作 |
| 3D 动画短片 | `3d-animation-short-generator` | 有故事、角色和场景连续性的完整动画 | 故事梗概、角色/场景卡、镜头表、连续性和终审清单 | 自动选模、逐镜生成、BGM 和成片合成 |
| 纸艺定格科普 | `papercraft-stop-motion-explainer` | 科学、教育或知识主题的分层纸艺表达 | 学习目标、视觉隐喻、纸偶/布景/道具、分镜与触感音效 | 画布节点和素材生成动作 |
| 品牌宣传片 | `brand-promo-video-generator` | 品牌、产品、网站、应用或门店宣传 | 事实来源、能力与场景、叙事节拍、CTA、素材授权检查 | 虚构品牌事实、自动生成和交付承诺 |
| 歌词排版 MV | `music-video-subtitle-generator` | 音乐视频、情绪短片、歌词空间排版 | 节拍与人声时序、人物/场景/文字引用、跨镜头连续性 | 自动音频分析、生成和拼接工具调用 |
| 双人游戏开场 | `co-op-game-intro-generator` | 两名角色、玩家卡片、菜单或开场交互 | 角色身份、UI 文字、菜单布局、确认图逻辑、事件节奏 | 画布选择卡、确认图和视频的自动生成 |
| 半调纸拼贴科普 | `paper-collage-explainer-generator` | 观点、知识点、旁白或抽象主题的平面拼贴 | 意义提炼、视觉隐喻、半调纸张语言、定格运动和触感音效 | 默认追加 BGM/旁白/字幕；上游默认也不自动添加 |
| 手绘真人融合 | `handdrawn-live-video-generator` | 粗糙发光手绘在实拍空间中接触、变形与逃离 | 接触点、连续变形、逃离路径、慢半拍追拍和非恐怖质感 | 把它扩成多场景、精致 CG 或惊吓式恐怖 |

## 易混方向

- `品牌宣传片` 以已核实的品牌事实、多个能力或使用场景和 CTA 为中心；`极简产品广告` 以单个实体产品、克制文案和高质感镜头为中心。
- `纸艺定格科普` 是分层微缩布景、纸偶和道具；`半调纸拼贴科普` 是平面剪贴、半调纹理和编辑式 B-roll。
- `3D 动画短片` 是多镜头叙事生产；`手绘真人融合` 默认是单场景、连续变形的短创意。

## 选择规则

- 用户未点名且没有明显命中时，创意方向写“无”，不要强套模板。
- 同时命中多个方向时，按用户最终交付目标选择一个主方向；其余只保留明确兼容的单项约束。
- 如果多个方向都由用户明确要求且无法从最终交付目标唯一判断主方向，只问一个最小选择问题，不自行挑选、删除或静默混合。
- 用户要求比较时可以列出候选差异；用户要求生成提示词时只采用一个主方向。
- 风格方向不能改变素材事实、H3 输入限制、用户台词或授权边界。
- 在非 MiniMax Hub 环境中，不声称执行了风格 Skill 的完整流程。

## 只读解析器

将本包根目录记为 `<skill-root>`，运行：

```bash
python3 <skill-root>/scripts/resolve_official_skills.py --route h3-base
python3 <skill-root>/scripts/resolve_official_skills.py --route h3-ref
python3 <skill-root>/scripts/resolve_official_skills.py --route <一个风格目录名>
```

`status=available` 只证明返回的文件来自当前已审查、干净的官方检出；不证明许可、安装、MiniMax Hub 工具、账号、额度或生成能力。只读取 `files`，不运行上游代码。`status=unavailable` 时不联网、不更新、不安装、不绕过 HEAD 校验。

## 来源与许可边界

官方仓库根 README 声明 MiniMax H3 采用 MiniMax H3 Community License，但 `skills/` 没有独立许可证，且部分风格内容标为 community 来源。当前结论为 `NEEDS_LICENSE_CLARIFICATION`：

- 可以保留固定提交的本地上游检出用于核对和更新。
- 本包只保存原创能力摘要、路由和兼容性判断，不复制九个上游 Skill 的全文、模板或工具合同。
- 未完成许可复核前，不把上游文件混入本包、重新授权、安装为默认 Agent 入口或对外再分发。
