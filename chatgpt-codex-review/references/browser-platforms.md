# 浏览器平台与调用边界

用户明确指定浏览器优先。自动选择先筛出当前任务能真实调用、且满足所需页面观察/操作/上传/下载能力的入口，再按用户提供的**已有订阅、常用工具和已有登录态**偏好选择。公共 Skill 不假定每位用户都订阅 MiniMax，也不假定多数 harness 的浏览器都具备相同 API。已经在 Mcode 内执行且它的浏览器能力满足时，可直接用本任务 Browser；无需为了固定品牌再切换客户端。没有适用的宿主/订阅偏好时，macOS 默认 Ego，Windows 默认 Tabbit；再按会话和能力选择已连接 Chrome 或 Codex 内置浏览器。缺一个客户端不终止整个任务，也不默认安装软件。

读取所选浏览器当前安装的 Skill/API，核实**执行主机、执行 harness、真实控制入口**。CLI 文件存在、工具被列出或网页能打开，不证明本任务所需的全部能力。跨 harness 必须有已配置且验证过的调用/交接入口；当前没有这个入口时继续使用可用浏览器，不凭品牌推测私有端点或让用户代替普通可逆操作。

把所选 `runtime/control_entry/control_tool/execution_host` 和本任务 `target_id/page_id/conversation_url`、原始 `evidence_ref` 持久保存为 `browser_execution_binding`。控制入口是实际调用入口，如当前 Ego Skill 支持的 `ego-browser nodejs` TaskSpace/Page 入口；control_tool 为调用该入口的真实宿主工具，不是“Ego Lite”窗口名。每次页面动作前与实际当前入口/所有权读回用 `scripts/validate_browser_binding.py --binding BINDING --actual ACTUAL` 核对。ACTUAL 另含真实 `ownership="agent"`、`actual_tool/call_evidence_ref` 和原始调用证据；核实该调用确实进入所选 CLI/API，不能只填驱动字符串。helper 只检查声明，调用者核对原件，runtime_verified_by_helper 仍为 false。Ego Page 的截图、鼠标、键盘和 DOM 操作均可使用其文档支持的方法，不因视觉操作误换到通用 `mcp__cua_repl`；Ego CLI 绑定拒绝实际 CUA/native app 调用，即使记录仍自称 Ego。其他运行时按其文档绑定自己的实际控制工具。Space 丢失是载体恢复依据，不是 CLI 失败或改驱动依据；只有所选入口的实际失败与当前运行时允许的切换合同才支持另选入口，不能改标签使校验通过。

恢复后再次核对同一 runtime/control entry/主机与当前所有权。换 target/page 时传 `--recovery`：保存旧→新 ID、`runtime_recovery_permitted=true`、实际 `recovery_basis_ref` 和 `original_request_readback_ref`；核对 helper 的 `binding_update` 后由 Controller 原子保存。此字段不授予重建/接管权限，真实用户接管、认证与工具拒绝仍按原门处理。历史缺绑定时 `reload_browser_binding` 只要求读取所选 Skill、原任务回执及当前入口证据，不要求新增通用许可，不阻断独立本地工作；不能用缺旧绑定永久拒绝已有授权的恢复。官方浏览器 Skill 保持原样，本包只维护兼容合同。

## Codex 导入 Chrome 数据

用户所说的“导入 Chrome 数据”和直接共享 Chrome profile 是两件事。**通过产品入口完成数据导入、且本次网站登录态已验证的 Codex 内置浏览器，可优先复用**，不能仅因它是独立浏览器就排除。导入范围按当前版本界面确认，不把书签导入等同所有站点登录态迁移；也不把一次导入说成持续同步。需要新的导入时按用户授权使用产品提供的入口，不自行搬运 profile/凭据。直接复用原 Chrome profile 的另一条路线是已连接 Chrome。[OpenAI 官方说明](https://help.openai.com/en/articles/20001277-using-the-built-in-browser-in-the-chatgpt-desktop-app)确认独立状态与 Chrome 连接的区别，未在该页完整列举数据导入范围。

## Mcode / MiniMax Code 内置浏览器

[官方桌面浏览器文档](https://agent.minimax.cn/docs/code/desktop/browser)仍使用 MiniMax Code 名称：Coding 模式右侧 Browser 支持网页/本地 HTML、页面检查调试、多 Tab、移动端预览和可视操作轨迹。将此入口记为 `mcode-browser`；这是本 Skill 的执行器标识，不是 shell 命令。先在实际 Mcode 任务中检查暴露工具、页面控制和本次所需文件能力。官方功能介绍不等于任意网站上传、认证附件下载、外部 CLI 控制均已验证。

[官方 CLI README](https://github.com/MiniMax-AI/minimax-code#readme)提供 `mcode` 与 BYOK 配置；**CLI/BYOK 可用不等于桌面 Browser 已向 Codex 开放**。从 Codex 发起跨 harness 工作时需真实已配置桥接，并核对请求、状态、产物读回和续接方式；本包不虚构 `mcode browser` 命令，也不为优先使用订阅而自动换 Key/模型/账户。订阅与 BYOK 使用当前实际配置及计费来源，不能假定用户的订阅覆盖外部 API 消耗。

执行器、执行模型和网页模型分别记录。Mcode 原生 Agent 不能自称 Luna；流程明确要求 Luna/max 等路由时，需要实际可用且已验证的配置，或用户显式覆盖。缺少 Mcode 调用入口不阻止其他已授权浏览器继续任务。恢复和清理使用 Mcode 当前接口，不套 Ego TaskSpace 或 Tabbit finish 参数。

## Windows Tabbit

先读当前安装的 `tabbit/SKILL.md`。官方 CLI 的 Windows 稳定入口是 `$env:LOCALAPPDATA\Tabbit\LocalAgent\bin\tabbit-cli.exe`；按当前文档使用 `diagnose`、`create`、`nodejs`、`tabs`、`resume`、`finish`。不硬编码版本 bundle、不读 endpoint.json、不直接启动浏览器内部服务。[官方 CLI 介绍](https://www.tabbit.com/blog/2026-09-09-tabbit-cli)。

多行/中文 JavaScript 在 PowerShell 中写**临时 UTF-8 无 BOM 文件**，用 CMD 标准输入重定向传入稳定 launcher；不要把 POSIX heredoc、PowerShell 管道或终端 PTY 当作同等入口。按本机 Skill 的真实参数调用，例如：

```powershell
$tabbitCli = "$env:LOCALAPPDATA\Tabbit\LocalAgent\bin\tabbit-cli.exe"
$program = [IO.Path]::GetTempFileName()
$code = @'
return await tabbit.observe({frames: "none", maxChars: 4000});
'@
try {
  [IO.File]::WriteAllText($program, $code, [Text.UTF8Encoding]::new($false))
  cmd.exe /d /c "`"$tabbitCli`" nodejs --task `"Web review`" --request-id inspect-page < `"$program`""
} finally {
  Remove-Item -LiteralPath $program -ErrorAction SilentlyContinue
}
```

`Web review` 是示例名称，每个 run 使用自己的短任务名；恢复用回执中真实 group/tab ID，不能靠同名猜测或抢用户标签。`create --task` 只列出清单，不证明已取得页面控制；首次 `nodejs` 提供初始 page 时直接导航它，不再创建多余页。恢复按当前 Skill 对实际 group 执行 create/resume，核实所有权后操作。

文件上传用实际观察到的 file input 与 `setInputFiles`，再核对附件名称/数量/完成状态。下载先检查当前能力：Tabbit capabilityVersion 18 不支持通用 Playwright download event，不能盲套 `waitForEvent('download')/saveAs()`。可对已观察的下载 URL 用文档支持的 `page.fetch(..., {as:"file", savePath:...})`，或点击原生下载后核实本次实际落盘文件；页面生成的 blob/认证附件另行验证，不承诺本地 fixture 成功等于 ChatGPT 附件全可下载。其他运行时仅在其文档支持时使用事件监听。校验实际文件类型、大小、SHA 与业务合同，下载失败只取同一结果，不重新提交。

## 恢复、身份与清理

记录 `runtime`、实际任务/group/tab 标识、原 URL、原请求身份和证据。Ego TaskSpace、Tabbit group、Chrome/IAB tab 不共用 API。当前 review state 的历史字段 `space_id` 可写有命名空间的真实字符串（如 `tabbit:group:<实际ID>`），并附原始回执；不是伪造 Ego 数字 ID。换载体记录旧→新映射，保持原服务端对话和业务请求。

创建/导航调用超时不证明没有创建页面：先按已返回 ID 或原 URL 只读核对现有标签，再恢复，不能反复创建。连接失败可按已授权任务恢复/切换可用载体；登录、验证码、工具拒绝、用户接管不能通过换浏览器绕过。任何发送/生成状态未知时先核对原消息或结果，不能在另一个浏览器重发。

完成后保存 URL、正文与文件，再关闭本任务创建的临时页/组。Ego 按当前 Skill 的 `task.finish({keep: []})` 合同；Tabbit 普通 `finish` 默认保留组，**不是关闭证明**：对确认全为本任务创建且仍有控制权的组，用当前 CLI 支持的 `finish --task <本轮任务名> --discard`，核对 `keep:false`、`closedTabIds` 与组清单；混有用户页时只关闭自己的页，再 finish，不整组丢弃；Chrome/IAB 按其真实 close API 只关自己创建的页。原有用户页只释放控制。需要继续等待、人工操作或用户明确保留时才留页并记录原因；仅为留个入口不保留空组。清理失败单独报告，不重新执行已完成业务。
