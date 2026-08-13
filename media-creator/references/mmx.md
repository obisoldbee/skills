# MiniMax MMX 外部执行器

## 边界

MMX CLI 及其 `mmx-cli`、`mmx-h3-video` Skills 是独立、可升级依赖。本包只调用 `mmx`，不复制其代码、Skill、配置或凭据。

每次遇到可能漂移的模型或参数时，以当前运行时为准：

```bash
mmx --version
mmx <resource> <command> --help
```

不要在未获用户授权时安装或升级 MMX。

## 图片

当前合同：

- 文生图；
- 比例或自定义尺寸；
- 多个输出 `--n`；
- seed；
- 单一角色主体参考 `--subject-ref type=character,image=...`；
- URL/Base64 输出和明确文件路径。

当前不承诺：

- 任意图生图或图片编辑；
- mask/inpainting；
- 多图输入或多主体参考。

示例：

```bash
mmx image generate \
  --prompt "<prompt>" \
  --aspect-ratio 16:9 \
  --out <output.jpg> \
  --quiet \
  --non-interactive
```

不要给 MMX 传递未支持的 `--image` 后假定它完成了图生图；调用前先按能力矩阵拦截。

## 视频配额

创建默认 MMX 视频任务前：

```bash
mmx quota show --output json --quiet --non-interactive
```

该命令查询 Token Plan 的 `model_remains[]`。只在精确视频模型行明确有当前周期与周余量时返回 `known_positive`；明确耗尽返回 `known_exhausted`；缺行、网络/鉴权失败或字段歧义均为 `unknown`。

H3 使用 Pay-as-you-go/Credit API Key，Token Plan 查询不是 H3 的权威剩余次数或余额。当前若没有单独的 H3 余额命令，在提交前报告 `unknown` 并询问继续 MMX 还是切换 Agnes。

## 视频模式

Legacy 路线：

- Hailuo-2.3：文生视频、图生视频；
- Hailuo-2.3-Fast：图生视频快速路线；
- Hailuo-02：首尾帧；
- S2V-01：单主体参考图。

H3 路线：

- 文生视频；
- 单图/首尾帧；
- 可重复参考图；
- 可重复参考视频；
- 可重复参考音频，但至少同时提供一个参考图或参考视频；
- 图/视频/音频混合参考。

帧模式与 reference 模式不能混用。参考视频只表示条件生成，不承诺逐帧保留或精确编辑源视频。

提交完整任务时使用一个阻塞式 CLI 进程等待和下载；终端返回 session/cell ID 后继续等待同一执行，禁止另提任务。异步模式只在用户明确需要 task ID 时使用，并保留该 ID。

## 语音

使用 `mmx speech synthesize`，运行时帮助决定模型、字符上限、音色、速度、音量、音高、格式、字幕和发音控制。

```bash
mmx speech synthesize \
  --text-file <input.txt> \
  --out <output.mp3> \
  --quiet \
  --non-interactive
```

## 音乐与翻唱

使用：

```bash
mmx music generate --prompt "<style>" --lyrics-file <lyrics.txt> --out <song.mp3>
mmx music generate --prompt "<style>" --instrumental --out <bgm.mp3>
mmx music cover --prompt "<target style>" --audio-file <reference.mp3> --out <cover.mp3>
```

运行时帮助决定当前模型、歌词优化、结构化风格字段和 cover 默认模型；不要把旧 Skill 中可能过时的默认值当作事实。

## 失败边界

- 鉴权、余额、配额或内容安全错误：原样报告并停止，不自动切 provider。
- 已返回 task ID：不因轮询或下载失败而重新生成。
- 下载失败：只重试同一结果下载。
- 缺少 MMX：报告外部依赖缺失；不要从本 Skill 自动安装。
