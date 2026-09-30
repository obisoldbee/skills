# Kimi Code：ReadMediaFile 与 AgentSwarm

这是一条新增执行分支。MiniMax direct、mmx、Ark 等原路线保留。这里的 Kimi Code
是执行工具的 CLI；实际识别模型取决于选中的 API Key/profile，不等于 Kimi K3。

## 选择模型与模式

| 选择 | 默认/合同 |
|---|---|
| 模型 | `MiniMax-M3`；第二个已知选项 `agnes-3.0-flash` |
| 普通模式 | `kimi-readmedia`，一个全新 Agent 读取全部指定媒体 |
| 增强模式 | `kimi-readmedia-swarm`，一次内置 `AgentSwarm` 启动 3 个独立上下文，各自完成相同观察任务，然后主 Agent 汇总 |
| 数量 | 默认 3；用户明确要求时传 `--observers N`，Kimi 新 Swarm 允许 2–128；1 人使用普通模式 |

两种模式都必须实际调用 Kimi 内置 `ReadMediaFile`。不能用自定义 HTTP、Codex
subagents、旧报告或“已经看过”的自述冒充。Swarm 是可选增强，不是默认多花三倍调用。

从调用方 Kimi 配置解析 exact model ID 与 alias。默认配置 `~/.kimi-code/config.toml`，
可显式传 `--config`；同模型有多个 alias 时必须选 `--model-alias`，不能混用 Key/endpoint。
新 API Key/profile 可继续扩充模型：核对官方合同、当前 `image_in|video_in|tool_use`、
实际绑定和授权 smoke test，再把结果加入已知模型表。Key 存在不证明能力，禁止靠加标签
绕过检查。OAuth、额外 headers 或单独 protocol/endpoint override 目前需另行适配。

## Swarm 调度与多视频任务

Kimi Code 0.43.0 的原生 CLI 案例确认：同一个父 Agent 在同一模型步骤并列发出两次
`AgentSwarm`，会在调度校验阶段被拒绝。**一次 Swarm 可以包含多个 items；多个 Swarm
调用必须等前一次完整返回，再发下一次。** items 数量是任务总数，实际同时启动多少人由
运行时并发上限决定；6 个 items 不等于6人同时运行。不要把这个限制扩大成禁止多子 Agent，
也不要推断不同独立 CLI 进程必然共享此限制。

可直接加入原生 CLI 的提示词：

> 每次只调用一个 AgentSwarm。多个视频合并为一次调用的多个 items，或等前一次完整返回后
> 顺序调用；不得在同一步并列发出多个 AgentSwarm。每个 item 明确 video_id、observer_id
> 和绝对媒体路径；独立新上下文，不互读报告，主 Agent 按 video_id 分组汇总。

“2 个视频 × 每个3人”的原生 CLI 调度示例：

| video_id | observer_id | path |
|---|---|---|
| V1 | R1 | `/absolute/video-a.mp4` |
| V1 | R2 | `/absolute/video-a.mp4` |
| V1 | R3 | `/absolute/video-a.mp4` |
| V2 | R1 | `/absolute/video-b.mp4` |
| V2 | R2 | `/absolute/video-b.mp4` |
| V2 | R3 | `/absolute/video-b.mp4` |

将这6行各编码为一个 JSON 字符串放入同一次 `items`；`prompt_template` 用 `{{item}}`
传入身份与路径。每个观察者完成对应视频的全部分析，不擅自拆成“只看画面/只读故事/只听音”
三个角色。主 Agent 保留 `(video_id, observer_id)` 和该视频的时间基准，不能串用其他视频结论。
这是原生 CLI 的编排说明，不是包内脚本新增了六人按视频分组的参数。

现有 `kimi_readmedia.py` 每次只生成一个 Swarm：`--observers 3` 的3人各读取整个 manifest。
manifest 放两个视频时，是3人各读两个视频，**不是每视频各3个上下文**。需要后者可在原生
CLI 使用上面的6项编排；使用当前脚本则为每个视频准备独立 manifest/输出目录，前一轮完整
返回并核验后再运行下一轮。不得把同一个输出目录或成功任务重新提交来凑数量。

遇到 `AgentSwarm must be called one swarm at a time`：

- 检查同一 `stepUuid` 的工具调用及对应 `tool.result`；这是调度拒绝，尚不能判为媒体解析失败。
- 确认所涉调用均被本地拒绝、未启动子任务后，可在当前授权内改成单次合并或顺序调用。
  父模型生成这些工具调用仍可能产生费用，不能把本地拒绝说成整轮零成本。
- 只纠正被拒绝的调度；不要因此去音轨、转码、换模型，也不要重试已经成功的子任务。
  若有子任务已启动或 provider 接受状态不明，沿用原有不自动重投边界，不能一概重新运行。
- 界面6个红叉不能证明6次媒体理解分别失败；应分别报告调度、媒体读取、provider和内容质量。

案例来源：2026-09-16 原生 Kimi CLI 0.43.0 / MiniMax-M3 的直接使用，**不是调用本 Skill
产生的缺陷**。证据确认同一步两次三人 Swarm 被拒绝，下一步改为单次调用；本次未核验该
用户会话最终报告，不记端到端成功。现有脚本的一次 Swarm 合同无需改为多 Swarm 调度器。

## 模型与媒体边界

- MiniMax-M3：Kimi profile 需有 `video_in`。视频应先探测，按需要分段、H.264 转码；
  包内 `minimax_m3_course_video.py` 仅预处理时**不传 `--analyze`**，并显式传
  `--keep-audio`。其旧 direct 默认去音轨不适用于本分支。保留音轨不证明模型能听懂。
- Agnes 3.0 Flash：官方明确列出文本和图像 URL，未明确原生视频。用户可显式授权
  给其现有 Kimi model profile 增加 `video_in` 并测试原生 MP4。备份配置、仅修改对应
  capabilities、核对其他字段不变；不改 Key/endpoint。此时标签表示本地实验设置，
  不是官方能力证据。只把实测通过的格式/素材/版本记为兼容，失败不自动改走抽帧。
- 跨模型比较要记录不同输入格式、抽帧间隔、画质和音频损失，不能把结果归因于模型本身。

## 执行

先用 `python3 <skill-root>/scripts/check_routes.py --route kimi-readmedia --model MiniMax-M3`
检查 CLI 与本地绑定。模型选择也适用于 `kimi-readmedia-swarm`；无网络检查不是读媒体。

冻结唯一输出目录、原媒体 hash 与问题。原件只读。Manifest 是 JSON 数组，每项至少包含：

```json
[{"path":"/absolute/prepared/segment.mp4","kind":"video","sha256":"<sha256>","original_start":0,"original_end":34.4}]
```

路径须绝对、存在、逐项 hash 一致且不重复；补充处理参数、原视频时间范围和损失。
Kimi 单文件上限 100 MiB 不等于 provider 的实际接受上限。视频可用前述分段脚本准备，
再记录每个片段的 SHA-256。已支持视频的模型可共用相同片段和问题进行普通/Swarm 对照：

```bash
python3 <skill-root>/scripts/providers/kimi_readmedia.py --model MiniMax-M3 --manifest <video-manifest.json>
python3 <skill-root>/scripts/providers/kimi_readmedia.py --model MiniMax-M3 --manifest <video-manifest.json> --prompt-file <question.txt> --output-dir <new-single-run> --execute
python3 <skill-root>/scripts/providers/kimi_readmedia.py --model MiniMax-M3 --mode swarm --observers 3 --manifest <video-manifest.json> --prompt-file <question.txt> --output-dir <new-swarm-run> --execute
```

省略 `--model` 使用 MiniMax-M3。省略 `--execute` 仅检查；执行需要当前授权。
输出目录必须尚不存在，避免覆盖证据或意外重投。执行器创建临时 Kimi home/工作目录，
选中 Key 仅经进程环境进入临时模型，不改用户全局配置；不继承模型池、历史上下文或项目工具。
子 Agent 只允许 `ReadMediaFile`；manifest 含 `kind=text` 时另外允许 `Read` 精确指定的转写文件，不允许读其他路径。主 Agent 只允许 `AgentSwarm` 与读取其结果的 `Read`。
一条 prompt 分别复制到各新上下文；只有观察者编号不同。无 fork/resume，禁止互读报告。
`max_attempts_per_step=1` 和 `compaction_max_attempts=1`；脚本不重跑整个操作。
Kimi 的上下文溢出恢复可能另外触发压缩，因此执行器轮询 native step error 并停止 CLI，
另设最大步骤数和总超时。该监测不是原子网络拦截，不能保证阻止运行时已经发出的下一请求。
超时、空结果或证据缺失保存原状，不能自动再发。

## 验收与汇总

`execution.json` 保存执行状态，`verification.json` 保存真实 native wire 证据检查：
同模型、观察者人数、每人精确媒体读取、工具结果、完整输出与未改变输入。
`native-records/` 保留脱敏 wire，`*-report.md` 保留每个观察者及主 Agent 原文。
CLI 退出 0 或生成文字不等于通过：少一个观察者、没调用媒体工具、读错路径、偷偷换模型
均不得 PASS。调用合同通过与内容正确性分别报告；仍需抽查具体画面和时间。

主 Agent 汇总要保留每条结论的观察者/事件 ID、独有细节、冲突及 Unknown。
多数一致不是事实核验；不得消掉少数但具体的发现，也不能把视觉变化推成代码根因。
最后报告覆盖范围、实际模型、人数、耗时/token（若可读）、失败与需要复核项。
默认中文输出。模型自述“只收到前 N 秒/若干帧”不是 provider 截断证据：先核对提交
片段 ffprobe、工具原始结果及对应末尾画面；没有截断证据时标记时间解释不可靠，
不能把模型误读时间轴写成预处理丢失。401 出现在第一次媒体读取前，应记鉴权拒绝，
不能记成视频格式不兼容。经用户选择其他现有凭据后另建尝试，保留原失败。

## 当前回归结果（2026-09-14 至 09-15）

2026-09-15 按官方限额复测：Agnes 的上下文改为 524288、最大输出为 65536（后者原本已是
65536），同一视频仍报 input 613091 > context 524288。故不归因于最大输出设置；
该原生视频路线按当前未支持处理，仅保留文本/图像为官方明确模态，实验结果不能升级为可用。
复测后移除了本机 Agnes profile 的实验性 `video_in`，保留图像、工具与 thinking；
后续视频输入会在本地报能力不支持，不再反复进入超限恢复。Key、endpoint 和其他模型未变。

Kimi Code 0.43.0；同一 34.4 秒录屏，转码 H.264/6fps/960 宽、保留 AAC，627,125 字节。

| 模型 | 普通 | 三观察者 Swarm |
|---|---|---|
| MiniMax-M3 | 调用合同通过，65.05 秒 | 3 个独立上下文各读一次、主 Agent 汇总，通过，103.81 秒 |
| agnes-3.0-flash | 读取文件后 provider 上下文超限，无有效观察 | 3 个观察者读到文件，但上下文压缩后丢失任务，无有效观察 |

Agnes 首轮另有旧凭据 401；用户授权切换现有有效凭据后，媒体请求报告约 613K input
tokens 超过 524,288 上限。该异常与视频内容在当前网关被计入文本 token 的情况相符，
但服务端编码实现未经确认；不能据此宣称所有 Agnes 视频永远不支持，也不能宣称本路线可用。
保留它作为已知可选模型与原生视频**未通过的实验选项**，不自动回退抽帧、不增大虚假的模型上限。

MiniMax 的调用通过也不是内容质量通过：普通报告把时间轴误解为只覆盖前 11 秒，
Swarm 保留了分歧但未消除 OCR/时间误读。人工抽查原视频末尾有对应画面，未发现
本地转码裁到 11 秒的证据。不能把这类自述作为 provider 截断或视频完整性结论。

依据：2026-09-14 核对 [Kimi 工具文档](https://github.com/MoonshotAI/kimi-code/blob/main/docs/en/reference/tools.md)、
[Agent 配置](https://github.com/MoonshotAI/kimi-code/blob/main/docs/en/customization/agents.md)、
[Kimi 配置](https://github.com/MoonshotAI/kimi-code/blob/main/docs/en/configuration/config-files.md)、
[Agnes 3.0 Flash](https://agnes-ai.com/zh-Hans/docs/agnes-30-flash)。CLI 版本与实测素材范围必须随结果保存。
