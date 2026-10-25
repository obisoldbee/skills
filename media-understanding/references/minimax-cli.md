# MiniMax CLI 合同

2026-10-20 核对本机和官方发布。`mmx` 为 1.0.28，npm 同版本；`mcode` 为 0.6.12。两个 CLI 使用各自的认证和命令，不互相冒充执行证据。调用前只需检查所选命令的本机 `--help`，无需重读全部工具手册。

## 绑定账号与区域

`mmx 1.0.28` 的普通请求认证优先级为显式 `--api-key`、已登录 OAuth、配置中的 API Key。仅设置 `MINIMAX_API_KEY` 不是普通请求选择该 Key 的充分证据；该变量还被首次交互配置流程使用。

使用本 Skill 的私有 MiniMax 槽位时，在内存读取已授权 profile，构造同时包含 `--api-key`、`--base-url` 和 `--region` 的参数，并传 `--non-interactive --quiet`。国内 API root 使用 `https://api.minimax.cn` 和 `cn`，其他 profile 沿用其已核实 root/region。Messages 的 `/anthropic` 是协议路径，不能直接作为 CLI 通用 API root。仅显式 key+base、未绑定 region 时，该版本仍可能探测区域、覆盖 base 并持久化区域设置。

命令记录将 key 参数脱敏，不打印真实值，不启用 `--verbose`。本次媒体任务沿用已有私有配置，不通过 `auth login`、`config set` 或升级 CLI 改写全局状态。route checker 只核对槽位和执行器，`configured_not_called` 仍需以上运行时绑定。

## 图片理解

```sh
mmx vision describe --image <one-image-path-or-url> --prompt <question> --output json
```

以上命令片段省略了前述必须绑定的认证与区域参数。支持本地文件、公开 URL 或 `--file-id`，`--image` 与 `--file-id` 二选一。没有 `--model`，实际走 `/v1/coding_plan/vlm`；保留 route 的 `model=null`，不借用文本命令的默认模型归因识图结果。

## 语音转写

`mmx 1.0.26` 新增 `speech transcribe`。本 Skill 的 `minimax-mmx-asr` 使用该命令，模型 `asr-1.0`，接口为 multipart `POST /v1/speech_to_text`。检查器接受可识别的稳定版本，预发布或未知版本保留未就绪状态，再按实际帮助与任务证据处理。

```sh
mmx speech transcribe --file <audio-path> --model asr-1.0 \
  --response-format verbose_json --timestamp-level word \
  --out <authorized-new-output-file> --output json
```

输出文件必须位于当前授权目录且尚不存在。执行前按官方合同检查单次不超过 500 秒、50 MB；长音频先按任务授权切片并保存原始时间偏移。视频先提取音轨。可选 `json|verbose_json|srt|vtt`；时间戳粒度为 `sentence|word`，`--language` 为 BCP-47 提示。`--stream` 仅配 `json`，不与带时间轴的格式或 `--out` 混用。SRT/VTT 和 verbose JSON 的时间轴须映射回原媒体。

CLI 当前没有媒体 POST 自动重试。超时、连接中断、5xx 或输出不完整时保留请求接受状态和可得证据，按 Skill 的不自动重投合同处理。先保存 ASR 转写，再用 M3 Messages 整理文本语义；音色和环境声需可核对的听音结果。

## 模型与版本

1.0.28 的 `text chat` 默认使用 `MiniMax-M3.1-Flash-Preview`，官方发布将其限定为 M Plan/MiniMax Code；按量客户端须明确指定适用模型。它与 direct 文档的 `MiniMax-M3.1-Flash` 分开记录。`vision describe` 与 `speech transcribe` 不继承该文本默认值。

Kimi 本机 2.1.1，官方 npm/GitHub 已到 2.2.0。本轮静态检查现有 runner 所用参数和环境仍匹配；实际媒体回归仍是独立验证。新版本有恢复首轮媒体读取与视频上传取消修复，升级由相应任务决定，本 Skill 不自行安装。

## 官方来源

- [MiniMax CLI 文档](https://platform.minimax.cn/docs/token-plan/minimax-cli)
- [1.0.28 发布记录](https://github.com/MiniMax-AI/cli/releases/tag/v1.0.28)
- [1.0.26 ASR 发布记录](https://github.com/MiniMax-AI/cli/releases/tag/v1.0.26)
- [认证选择源码](https://github.com/MiniMax-AI/cli/blob/v1.0.28/src/auth/resolver.ts)、[区域配置](https://github.com/MiniMax-AI/cli/blob/v1.0.28/src/config/loader.ts)、[主入口探测](https://github.com/MiniMax-AI/cli/blob/v1.0.28/src/main.ts)
- [ASR 接口](https://platform.minimax.cn/docs/api-reference/speech-to-text)
- [Kimi 官方发布](https://github.com/MoonshotAI/kimi-code/releases)
