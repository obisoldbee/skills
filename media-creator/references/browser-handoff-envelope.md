# 浏览器执行交接 Envelope

这份合同供发起任务的主任务、`project-handoff` visible-task surface 和 ego-browser worker 共享。它只规定执行边界，不替代主任务对用户意图、输入文件、输出位置或 provider 选择的判断。

## 主任务先完成规划

主任务在创建 visible thread 前必须形成最终 provider payload：

- ChatGPT Web 图片：最终图片 prompt、已经确认的输入文件和顺序（没有输入图时为空列表），以及调用方授权的绝对输出路径；
- MiniMax Web Music：标题、`instrumental`/人声模式、style prompt、歌词（如有）、`count` 和调用方授权的绝对输出路径。

worker 不得改写 prompt、歌词、风格、标题、模式、数量或输出路径，也不得因为网页字段变化自行添加创意内容。缺少必需字段时退回主任务，不猜测。

## Envelope 最小字段

```json
{
  "execution_role": "browser_worker",
  "handoff_depth": 1,
  "project": "current-verified-project",
  "route": "chatgpt-web-image | minimax-web-music",
  "orchestrator": "project-handoff",
  "luna": {
    "route": "luna-max",
    "model": "gpt-5.6-luna",
    "reasoning": "max",
    "thread": "visible",
    "surface": "visible_thread"
  },
  "executor": "ego-browser",
  "final_provider_payload": "main-task-authored",
  "submission_limit": 1,
  "provider_switch_after_submission": false
}
```

`final_provider_payload` 在实际交接中应展开为调用方已冻结的字段，而不是只发送这个字符串。主任务读取并遵守 `$project-handoff`，先验证 `luna-max` 路由，再用真实 `create_thread` 创建可见任务并验证回执；普通隐藏 subagent 不是替代品。worker 接收 `execution_role=browser_worker` 且 `handoff_depth=1` 后直接执行，禁止再次创建或 dispatch Luna，禁止把执行结果包装成新的交接任务。

用户请求并选定浏览器生成路线时，只授权一个有界 Luna 可见任务和一次网页提交；追加批次、重复提交或第二个任务需要新授权。若用户只要求提示词、规划、预览或 dry-run，主任务只返回 payload，不创建任务、不打开网页。

## Thread 与跨 Harness 规则

有 live `project-handoff` visible-task surface 时，ChatGPT Web 图片和 MiniMax Web Music 都必须使用精确的 `luna-max` visible thread（`gpt-5.6-luna` + `max`），由该 thread 中的 ego-browser worker 操作网页、监控一次提交、下载并验证产物。主任务不要把普通 thread、模型别名或隐藏后台任务当作等价物。

Harness 没有 visible-task dispatch 时，只有在它自己已经验证存在可用的等价浏览器执行器，并能完成登录态复用、页面状态读取、文件上传（如需要）和浏览器上下文下载时，才可本地执行同一 envelope；ego-browser 仍是首选。该路径表达“没有这个能力面”，不是 Luna thread 创建失败后的 fallback；若用户明确要求 Luna，创建失败或 thread 不可用就暂停并报告，不降级到本地或其他 provider。

## 提交前与提交后

登录、验证码、人工确认、`user is controlling`/失配状态、非零费用、费用不明确或未经授权的付款/订阅都在提交前 handoff 并停止。提交按钮只操作一次，随后保留任务状态和结果身份；等待超时、页面刷新或下载错误都不能再次提交，也不能静默切 provider。下载失败只重试同一已提交结果的浏览器内下载。

完成条件必须同时包括：网页任务确实结束、产物已下载到调用方指定位置、文件为非零普通文件、类型与路由匹配，并有 SHA-256 读回记录。页面 toast、试听片段、按钮点击、任务 ID 或 worker 自报完成都不是最终成功证据。
