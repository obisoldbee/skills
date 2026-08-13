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
  => macOS + ego-browser + inherited ChatGPT login
       ? ChatGPT Web
       : MMX

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
speech | music | music-cover => MMX
```

## Fallback 边界

- 允许：浏览器依赖或登录在提交前明确不可用，文生图改走 MMX。
- 不允许：ChatGPT 已发送提示词或 MMX/Agnes 已返回任务 ID 后自动改投其他供应商。
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
