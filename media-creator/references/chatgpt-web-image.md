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

## Executor 选择

当前首选 executor 是 macOS 上的 ego-browser，因为它提供隔离 task space，并继承用户登录态。

提交前确认：

1. 当前系统是 macOS；
2. `ego-browser` 可执行；
3. 独立 Agent task space 能打开 `https://chatgpt.com/`；
4. 页面有可用的 prompt composer，且不是登录页；
5. 输出目录可写。

若用户已明确要求 ego-browser，按 ego-browser Skill 直接尝试，不额外运行安装探测。若只是自动选路，可用本包 `check_routes.py` 做本地环境检查；它不检查登录。

非 macOS、无 ego-browser 或登录未继承时：

- 文生图在任务尚未提交前改走 MMX；
- 通用图生图/多图不得改走 MMX，询问是否使用 Agnes；
- 若当前 harness 有内置浏览器，只能在登录、上传、DOM 状态和浏览器上下文下载均验证后启用。

## ego-browser 工作流

严格遵守 ego-browser Skill：浏览器操作使用 heredoc，不先写 `.js` 文件。

1. 使用与用户目标相关的短名称调用 `useOrCreateTaskSpace`；同一目标跨轮次复用返回的数值 ID。
2. `openOrReuseTab('https://chatgpt.com/', { wait: true })`。
3. 用 `snapshotText()`、`pageInfo()` 和必要的 `js()` 观察当前界面，不假定按钮文案、模型、质量或 DOM 选择器仍与旧 Skill 相同。
4. 确认登录。若需要人工登录，调用 `handOffTaskSpace(id)` 并停止；用户明确“继续”后才 `takeOverTaskSpace(id)`。
5. 当前已验证入口是“添加文件等 → 创建图片”。操作后确认 `#prompt-textarea` 内出现 `data-id="picture_v2"` 的不可编辑胶囊。入口和标记都属于可漂移 UI，未来仍应现场观察。
6. 保留 `picture_v2` 胶囊，把光标置于其后并使用真实键盘输入 `typeText`。不要对整个 composer 执行 `innerText=''` 或 `fillInput`，否则会删除当前图片模式。读回胶囊后的精确提示词再发送。
7. 发送一次。任务可能已创建后，不因等待超时而再次发送。
8. 轮询生成状态和错误状态；确认“停止”控件消失、图源稳定且图片实际尺寸已加载。页面可能为同一结果渲染多个 `<img>`，必须按 `currentSrc/src` 去重，不能把 DOM 节点数当生成次数。
9. 在浏览器上下文下载，并保存到调用方指定的绝对路径。
10. 验证文件类型、非零大小、尺寸和 SHA-256。
11. 确认完成后，在单独的最终 heredoc 中调用 `completeTaskSpace(id, { keep: false })`。

避免坐标作为首选；优先使用语义树、稳定 locator、角色/文本关系和状态读回。页面发生变化时先停止并重新观察，不要盲点旧坐标或旧 selector。

## 下载合同

ChatGPT 结果 URL 可能依赖登录 cookie。不要假定 Node/server 侧直接请求可以访问。

优先在当前浏览器页面上下文获取最终图像，转换为 Base64/Data URL 后传回 Node 侧保存。只选择已经加载、尺寸合理且属于本次生成结果的唯一 `estuary/content` 图源；不要抓取侧边栏头像、历史缩略图或占位图。

输出路径必须由当前任务提供。创建父目录，默认不覆盖既有文件；若目标已存在，除非用户明确要求覆盖，否则生成带版本后缀的文件名。

## 图片输入

2026-08-13 的只读 UI 观察确认页面存在启用的 `input[data-testid="upload-photos-input"]`，`accept="image/*"` 且支持 multiple；ego-browser 提供：

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

- 未登录：handoff 给用户正常登录，不读取凭据或绕过验证。
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
