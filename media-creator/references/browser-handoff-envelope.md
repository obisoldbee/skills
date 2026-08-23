# 浏览器执行交接 Envelope

这份合同供发起任务的主任务、当前任务的浏览器执行器、`project-handoff` visible-task surface 和 ego-browser worker 共享。它只规定执行与任务创建的分轴授权边界，不替代主任务对用户意图、输入文件、输出位置或 provider 选择的判断。

## 主任务先完成规划

主任务在任何浏览器执行或经授权的 visible thread 创建前，必须形成最终 provider payload：

- ChatGPT Web 图片：最终图片 prompt、已经确认的输入文件和顺序（没有输入图时为空列表），以及调用方授权的绝对输出路径；
- MiniMax Web Music：标题、`instrumental`/人声模式、style prompt、歌词（如有）、`count` 和调用方授权的绝对输出路径。

worker 不得改写 prompt、歌词、风格、标题、模式、数量或输出路径，也不得因为网页字段变化自行添加创意内容。缺少必需字段时退回主任务，不猜测。

## Envelope 最小字段

执行型 envelope 使用以下规范化形状；`final_provider_payload` 必须展开，不能用说明字符串代替：

```json
{
  "schema": "media-creator-browser-envelope/v1",
  "mode": "execute",
  "request_authority": "ordinary_browser_generation",
  "execution_role": "browser_executor",
  "handoff_depth": 0,
  "project": "current-verified-project",
  "route": "chatgpt-web-image",
  "authority": {
    "provider_execution_authority": true,
    "visible_task_creation_authority": false
  },
  "execution_location": "current_task",
  "executor": "ego-browser",
  "payload_author": "originating_main_task",
  "worker_creative_rewrite": false,
  "final_provider_payload": {
    "final_image_prompt": "<final prompt>",
    "inputs": [],
    "output_path": "<absolute caller-authorized path>"
  },
  "submission_limit": 1,
  "provider_switch_after_submission": false,
  "download_retry": "same_submitted_result_only",
  "recursive_dispatch": false
}
```

MiniMax Web Music 的 `final_provider_payload` 精确包含 `title`、`mode`（`instrumental` 或 `vocal`）、`style_prompt`、`lyrics`、`count=1` 和绝对 `output_path`。普通生成请求可以把 `provider_execution_authority` 设为 `true`，但必须把 `visible_task_creation_authority` 保持为 `false`，并使用当前任务 depth 0。它不授权创建任务。

若用户已明确授权 `luna_visible_task`，把 `request_authority` 改为 `explicit_visible_task`，两条 authority 都设为 `true`，使用 `execution_location=luna_visible_task`、`execution_role=browser_worker`、`handoff_depth=1`，并且只由主任务创建和校验一次。执行 envelope 增加以下精确字段：

```json
{
  "orchestrator": "project-handoff",
  "created_and_validated_by": "originating_main_task",
  "luna": {
    "route": "luna-max",
    "model": "gpt-5.6-luna",
    "reasoning": "max",
    "thread": "visible",
    "surface": "visible_thread"
  }
}
```

仅在上述显式授权的 visible branch 中，主任务才读取并遵守 `$project-handoff`，用真实 `create_thread` 创建可见任务并验证回执；普通隐藏 subagent 不是替代品。worker 接收 `execution_role=browser_worker` 且 `handoff_depth=1` 后直接执行，禁止再次创建或 dispatch Luna，禁止把执行结果包装成新的交接任务。

生成请求只授权一次网页提交；它不自动授权任何可见任务。追加批次、重复提交或第二个任务需要新授权。若用户只要求提示词、规划、预览或 dry-run，分别规范化为 `prompt`、`planning`、`preview`、`dry_run`，并使用 `request_authority=non_execution`、两条 authority 均为 `false`、`execution_role=planner`、`handoff_depth=0`、`execution_location=none`、`executor=null`、`submission_limit=0`、`download_retry=not_applicable`。还必须带上以下零副作用记录：

```json
{
  "side_effects": {
    "open_browser": false,
    "provider_call": false,
    "create_thread": false
  }
}
```

主任务在任何浏览器操作或 visible task 创建前，把完整 envelope 保存为 JSON 并运行：

```bash
python3 -B scripts/validate_browser_envelope.py envelope.json
```

仅在 `valid=true` 时按 envelope 继续。这个 validator 只读取 JSON，固定报告 `provider_calls=false`、`secrets_read=false`；它验证权限、role/depth、Luna route、最终 payload、一次提交、不可递归、提交后不可换 provider，以及下载只能重试同一已提交结果，但不执行浏览器或 provider。

## Thread 与跨 Harness 规则

先判定用户是否显式要求新可见任务。有该授权时，ChatGPT Web 图片和 MiniMax Web Music 使用精确的 `luna-max` visible thread（`gpt-5.6-luna` + `max`），由该 thread 中的 ego-browser worker 操作网页、监控一次提交、下载并验证产物。主任务不要把普通 thread、模型别名或隐藏后台任务当作等价物。

没有该授权时，若当前任务已验证存在可用浏览器执行器，并能完成登录态复用、页面状态读取、文件上传（如需要）和浏览器上下文下载，就在当前任务执行同一 envelope；ego-browser 仍是首选。若当前任务无该能力，返回 `needs_visible_task_authority` 并停止，不自行创建任务。若用户明确要求 Luna，创建失败或 thread 不可用就暂停并报告，不降级到本地或其他 provider。

## 提交前与提交后

登录、验证码、人工确认、`user is controlling`/失配状态、非零费用、费用不明确或未经授权的付款/订阅都在提交前 handoff 并停止。提交按钮只操作一次，随后保留任务状态和结果身份；等待超时、页面刷新或下载错误都不能再次提交，也不能静默切 provider。下载失败只重试同一已提交结果的浏览器内下载。

完成条件必须同时包括：网页任务确实结束、产物已下载到调用方指定位置、文件为非零普通文件、类型与路由匹配，并有 SHA-256 读回记录。页面 toast、试听片段、按钮点击、任务 ID 或 worker 自报完成都不是最终成功证据。
