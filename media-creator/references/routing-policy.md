# 路由策略与能力矩阵

## 目录

- 路由所有权
- 图片矩阵
- 视频矩阵
- 默认决策
- Fallback 边界
- 回归用例

## 路由所有权

`media-creator` 是非原生生成能力补充，不是 Codex `imagegen` 的上层路由。

| 请求 | Codex | 非 Codex |
|---|---|---|
| 未指定 provider 的普通生图/修图 | 原生 `imagegen`，本 Skill 不触发 | 本 Skill 选择 ChatGPT Web 或兼容 fallback |
| 显式 ChatGPT Web/MMX/Agnes 图片 | 本 Skill | 本 Skill |
| 视频、语音、音乐、翻唱 | 本 Skill | 本 Skill |

## 共享浏览器执行合同

ChatGPT Web 图片和 MiniMax Web Music 先由发起任务的主任务完成创意规划，再交给浏览器执行器。主任务必须在交接前冻结最终 provider payload；ChatGPT Web 的 payload 是最终图片 prompt、输入顺序和调用方授权的输出路径，MiniMax Web Music 的 payload 是标题、纯音乐/人声模式、style prompt、歌词（如有）、数量和调用方授权的输出路径。worker 只做页面映射、一次提交、同一任务等待、下载和文件验证，不重写这些字段。

live `project-handoff` visible-task surface 存在时，两条路线都必须使用精确的 `luna-max` visible thread：`gpt-5.6-luna` + `max` + `visible_thread`。主任务按 `$project-handoff` 创建和校验 thread，worker 使用 `ego-browser`，并接收 `execution_role=browser_worker`、`handoff_depth=1`。worker 直接执行 envelope，禁止递归 dispatch Luna。选定浏览器生成路线授权一个有界可见任务；提示词/规划/预览请求不授权派发。Harness 缺少 visible-task dispatch 时，只有它自身已验证等价浏览器执行能力，才可本地执行同一 envelope；ego-browser 仍是首选。这只表示能力缺失，不能作为 Luna 创建失败后的 fallback，显式 Luna 请求不得降级。详见 [browser-handoff-envelope.md](browser-handoff-envelope.md)。

登录、验证码、人工接管、当前非零费用、费用不明确或未获授权的支付均在提交前 handoff 并暂停。提交后不切换 provider、不重复提交；下载失败只能重试同一已提交结果的下载。

## 图片矩阵

| 模式 | ChatGPT Web | MMX | Agnes |
|---|---|---|---|
| 文生图 | 支持 | 支持 | 支持 |
| 通用图生图/编辑 | 上传工作流验证后支持 | 不支持 | 支持 |
| 单主体参考 | 上传工作流验证后支持 | `subject-ref` | 支持 |
| 多图合成 | 多上传工作流验证后支持 | 不支持 | 支持 |
| mask/inpainting | 未验证 | 不支持 | 未单独文档化 |

不要把 MMX 的 `--n` 当作多图输入；它只生成同一提示词的多个输出。不要把 `--subject-ref` 当作任意图像编辑。

## 视频矩阵

| 模式 | MMX Legacy | MMX H3 | Agnes Video V2.0 |
|---|---|---|---|
| 文生视频 | 支持 | 支持 | 支持 |
| 单图生视频 | 支持 | 支持 | 支持 |
| 首尾帧 | 支持 | 支持 | 图片关键帧模式 |
| 单主体参考图 | S2V-01 | 参考图 | 图生视频/关键帧 |
| 多参考图 | 不支持 | 支持 | 仅关键帧图片数组 |
| 参考视频 | 不支持 | 支持 | 不支持/未文档化 |
| 参考音频 | 不支持 | 支持，且需同时有参考图或视频 | 不支持/未文档化 |
| 精确原视频编辑 | 不承诺 | 不承诺 | 不支持/未文档化 |

将 H3 `reference-video` 称为“参考视频条件生成”，不得写成确定性的原视频编辑。

## 默认决策

### 图片

```text
Codex + generic image + native imagegen available
  => exclude media-creator; owner=imagegen

non-Codex + text-to-image
  => eligible macOS + ego-browser + inherited ChatGPT login
       ? main-authored payload -> luna-max visible thread -> ego-browser ChatGPT Web
       : MMX only when the browser capability is absent before handoff

non-Codex + image edit / multi-image
  => verified ChatGPT Web upload route
       ? ChatGPT Web
       : ask before Agnes
```

若宿主提供自己的内置浏览器，只有在它同时满足以下条件后，才能把它登记为 ChatGPT Web executor：

- 能复用或正常建立 ChatGPT 登录态；
- 能稳定观察 DOM/页面状态并上传本地文件；
- 能在浏览器上下文下载需要 cookie 的结果；
- 能把产物保存并读回验证。

未验证的内置浏览器只能标记为 `candidate_executor`，不能静默代替 ego-browser。不要为普通 harness 强行控制外部 Chrome。

### 视频

```text
explicit Agnes => Agnes
otherwise => query MMX Token Plan video quota
  known_positive  => MMX compatible model
  known_exhausted => ask MMX paid path vs Agnes
  unknown         => ask MMX vs Agnes
```

H3 使用 Pay-as-you-go/Credit Key，Token Plan 查询不是其权威余额或剩余次数证明。

### 音频

```text
speech => MMX speech route
generic original song | instrumental BGM
  => MiniMax Web Music on eligible macOS/ego-browser environments
music-cover
  => no Web Music claim; explicit MMX legacy route only after historical-paid-user eligibility confirmation
```

MiniMax Web Music 使用 <https://www.minimaxi.com/audio/music>，默认数量为 1；模型、费用、登录态和页面控件以实时页面为准。必须等待全曲完成，下载 MP3，并验证普通文件、非零大小、类型和 SHA-256。它不承诺 voice cloning、reference-audio editing、cover、精确时长或商用许可。MMX music API 因 2026-08-20 官方公告不再是通用默认：新用户没有付费音乐/歌词 API，历史付费用户只有在运行时确认仍有资格后才能显式选择；免费音乐模型已停止。网页音乐失败不得静默切 MMX。

## Fallback 边界

- 允许：在选择/交接前确认所需 browser capability 根本不存在时，文生图改走 MMX。
- 登录或人工检查应先按 ego-browser handoff 暂停，不以“未确认登录”自动切换 provider。
- 不允许：Luna thread 创建失败、visible handoff 失败或显式 Luna 请求时降级到本地 ego-browser、MMX 或其他 provider。
- 不允许：ChatGPT 已发送提示词或 MMX/Agnes 已返回任务 ID 后自动改投其他供应商。
- 不允许：worker 改写主任务的最终 prompt、歌词、风格、标题、模式、数量或输出路径。
- 不允许：MMX 不支持图生图时丢弃输入图，退化成纯文生图。
- 不允许：配额查询失败时把 `unknown` 报成“0 次”。
- Agnes 图片只有显式请求或用户确认后才使用。

## 回归用例

1. Codex：“画一只猫” => 直接原生 imagegen；`media-creator` 不加载。
2. Codex：“用 Agnes 画一只猫” => `media-creator` / Agnes。
3. 非 Codex + macOS + ego + 登录：“画一只猫” => ChatGPT Web。
4. 非 Codex + 无 ego：“画一只猫” => MMX 文生图。
5. 非 Codex：“把这张图片改成夜景”，ChatGPT 上传路线不可用 => 询问 Agnes，不得调用 MMX。
6. MMX 视频配额明确有余量 => 继续一次任务。
7. MMX 视频配额耗尽或未知 => 询问 MMX/Agnes。
8. “参考这段视频生成新镜头” => 可选 H3 reference-video。
9. “逐帧保持原视频，只换衣服” => 当前路线不承诺；不得把 reference-video 当精确编辑。
10. 非 Codex 通用原创歌曲/纯音乐 BGM => MiniMax Web Music；默认 `count=1`，不因页面默认批量而提交多首。
11. MiniMax Web Music 页面费用非零/不明确、登录或人工确认未完成 => handoff 并暂停，不提交。
12. MiniMax Web Music 已提交后等待或下载失败 => 继续同一任务/同一作品，不重复提交、不切 MMX。
13. MMX music API => 只有显式选择且运行时确认历史付费 API 资格时可用；`mmx --help` 单独不足以证明资格。
14. ChatGPT Web 或 MiniMax Web Music visible thread => `luna-max` + visible + ego-browser + `execution_role=browser_worker` + `handoff_depth=1`；worker 不得递归 dispatch。
