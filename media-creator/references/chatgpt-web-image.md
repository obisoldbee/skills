# ChatGPT Web 图片生成

## 目录

- 适用边界
- Executor 选择
- ego-browser 工作流
- 下载合同
- 图片输入
- 失败与清理

## 适用边界

将这条路线用于：

- 非 Codex Agent 的普通图片生成；
- 用户显式要求 ChatGPT Web 生图；
- Codex 原生 `imagegen` 不适用且用户明确选择网页路线。

不要用它接管 Codex 未指定 provider 的普通生图或修图。

## Planner 与浏览器 worker

发起任务的主任务必须先冻结最终图片 payload：最终 prompt、已确认的输入文件和顺序（没有输入图时为空列表），以及调用方授权的绝对输出路径。本路线的浏览器执行器只把这个 payload 映射到页面、发送一次、等待、下载和验证；不得重写 prompt、补创意或丢弃输入。

普通生成请求只授予 `provider_execution_authority`，不授予 `visible_task_creation_authority`。用户未明确说“新任务/新线程/交接/Luna 可见任务”时，当前任务有已验证浏览器能力就在当前任务执行；没有则返回 `needs_visible_task_authority`，不创建 thread。只有明确授权新可见任务时，主任务才创建并校验精确的 `luna-max` visible thread（`gpt-6-luna`、`max`），再把带有 `execution_role=browser_worker`、`handoff_depth=1`、`created_and_validated_by=originating_main_task` 的 envelope 交给 浏览器 worker。worker 直接执行，不得递归 handoff 或再次 dispatch Luna。显式 Luna 请求创建失败时不能降级。任何浏览器或 task 动作前先运行 `scripts/validate_browser_envelope.py`。

若用户只要求 prompt、规划、预览或 dry-run，只返回 payload：不打开浏览器、不调用 provider、不创建可见任务。

## Executor 选择

按 [浏览器平台](browser-platforms.md) 选择执行器：显式选择优先，再从真实可调用且满足能力的入口中按用户已有订阅、常用工具和已验证登录态选择；无适用偏好时才用 macOS Ego / Windows Tabbit 默认及其备用路线。浏览器存在不授予新可见任务权限。envelope 的 `executor` 写实际 `ego-browser`、`tabbit`、`chrome`、`codex-browser` 或 `mcode-browser`；静态校验不代替运行时能力检查。

提交前在独立的本任务页面确认 ChatGPT URL、真实登录态、图片模式、composer、所需上传/下载能力和可写输出目录。`check_routes.py` 只做本地元数据检查，不检查登录或连接。只有自动选路尚未选定/提交 Web 路线、且无可用浏览器能力时，文生图才可按路由改走 MMX；Windows 或缺 Ego 本身不是 provider fallback 原因。图生图/多图不改走 MMX；Agnes 需原选择授权。登录或人工检查保留页面交用户处理。

## 浏览器工作流

1. 完成 envelope 与授权判定；按当前运行时 Skill 创建/恢复本任务载体，记录真实 runtime/group/tab ID。有显式可见任务授权才创建 Luna worker；worker 不递归派发。
2. 打开或恢复原 ChatGPT URL，读取当前 DOM/语义状态，不套旧 Ego API 到 Tabbit。
3. 从当前 UI 选择图片模式，核对模型、输入附件与最终 prompt。不要清空 composer 中的模式胶囊；历史 `picture_v2` 标记只作线索，不是固定门槛。
4. 发送一次并读回。超时或结果未知先核对原请求，不重新生成、不换 provider。
5. 等待生成完成与最终图源加载；按图源去重，多个 DOM 节点不算多次生成。
6. 按平台下载合同保存至授权路径，校验类型、非零大小、尺寸和 SHA-256。保存 URL/证据后关闭自建临时载体。

避免坐标作为首选；优先使用语义树、稳定 locator、角色/文本关系和状态读回。页面发生变化时先停止并重新观察，不要盲点旧坐标或旧 selector。

## 下载合同

ChatGPT 结果 URL 可能依赖登录 cookie。不要假定 Node/server 侧直接请求可以访问。

按当前浏览器支持的原生下载或页面上下文文件下载获取最终图像；只有当前 API 支持时才用 Base64/Data URL 传回 Node 保存。只选择已经加载、尺寸合理且属于本次生成结果的唯一 `estuary/content` 图源；不要抓取侧边栏头像、历史缩略图或占位图。

输出路径必须由当前任务提供。创建父目录，默认不覆盖既有文件；若目标已存在，除非用户明确要求覆盖，否则生成带版本后缀的文件名。

## 图片输入

2026-08-13 的只读 UI 观察确认页面存在启用的 `input[data-testid="upload-photos-input"]`，`accept="image/*"` 且支持 multiple；当时的 Ego helper 示例是（历史 API，执行时读当前 Skill；Tabbit 使用观察到的 input 的 `setInputFiles`）：

```javascript
await uploadFile('input[type="file"]', '/absolute/path/to/input.png')
```

但“存在上传 helper”不等于 ChatGPT 当前图片编辑流程已验证。启用图生图或多图前，必须在当前 UI 中确认：

- 正确的附件/文件 input；
- 上传完成状态；
- 每张图的角色和顺序；
- composer 进入“描述或编辑图片”语义；
- 生成结果确实使用输入图。

上传 helper 与控件存在已经观察到，但上传后的附件确认、编辑语义和结果使用输入图尚未执行。将 `image-to-image` 和 `multi-image` 标记为 `candidate_unverified`。

## 失败与清理

- 未登录：对已有的当前任务 task space 使用所选浏览器的人工接管流程；若需要新可见任务交接，必须先有用户明确授权。暂停时不读取凭据或绕过验证，也不把登录/创建失败当作 MMX fallback。
- DOM/按钮未知：保存去敏截图和语义快照，停止并更新合同。
- 发送状态不明：不得重发；先确认是否出现 assistant turn、停止按钮、任务状态或生成结果。
- 下载 403：改用浏览器上下文 fetch，不重新生成。
- 用户意外接管 task space：立即停止，等待用户明确允许继续。
- 完成或失败收敛后关闭 Agent task space；不要干扰用户窗口。

## 2026-08-13 实测基线

- 独立 Agent task space 成功继承 ChatGPT 登录态并完成清理；
- 当前页面观察到“模型 GPT-5.6 Sol / 思考强度 Pro”，没有观察到旧 Skill 所称的默认“中”质量，也没有改变设置；
- 一次 Enter 提交生成一个唯一图源；页面最终有多个重复 DOM 节点；
- 浏览器上下文 fetch/Base64 下载成功；
- 测试产物为 1254×1254 PNG。尺寸只是一笔实测结果，不是固定模型合同；
- 旧 Skill 的 1448×1086、首页“生成图片”快捷按钮、placeholder 图片模式判断及清空 composer 流程均不得继续当作当前事实。
