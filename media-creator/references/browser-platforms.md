# 浏览器选择与操作

用户当次指定浏览器时按指定执行；已有任务正在使用已登录页面时，沿用该会话。其余情况按下面顺序选择能完成本次操作的入口。

1. Ego Lite，读取当前 `ego-browser` Skill，再运行 `ego-browser skill` 获取本机版本指引。
2. Tabbit，读取当前安装的 Tabbit Skill。
3. 系统默认浏览器，或当前 harness 已记录的用户常用浏览器。
4. 当前 harness 内置浏览器。

某个入口未安装、未连接或缺少本次上传/下载能力时，继续检查下一项。使用所选入口实际提供的工具和参数；跨 harness 使用已有桥接。需要登录、验证码或用户接管时保留原页面交给用户，恢复后继续原任务。

`executor` 记录实际入口，如 `ego-browser`、`tabbit`、`chrome`、`edge`、`codex-browser` 或 `mcode-browser`；其他默认或常用浏览器用 `system-browser`，其他 harness 内置用 `harness-browser`，并按 [envelope](browser-handoff-envelope.md) 记录实际浏览器及控制入口。操作前核对目标网站登录态、页面控件和所需文件能力。Mcode 内置浏览器使用该任务已暴露的 Browser 工具；已有 Chrome 数据导入的内置浏览器直接检查目标网站会话。按当前配置使用账户与计费方式。

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

每个 run 使用自己的短任务名，`Web review` 仅作示例。恢复时使用回执中的真实 group/tab ID。`create --task` 返回清单后，首次 `nodejs` 直接导航提供的初始 page；恢复按当前 Skill 对该 group 执行 create/resume。

文件上传用实际观察到的 file input 与 `setInputFiles`，再核对附件名称/数量/完成状态。下载先检查当前能力：Tabbit capabilityVersion 18 不支持通用 Playwright download event，不能盲套 `waitForEvent('download')/saveAs()`。可对已观察的下载 URL 用文档支持的 `page.fetch(..., {as:"file", savePath:...})`，或点击原生下载后核实本次实际落盘文件；页面生成的 blob/认证附件另行验证，按本次实际附件核对下载结果。其他运行时仅在其文档支持时使用事件监听。校验实际文件类型、大小、SHA 与业务合同，下载失败只取同一结果，不重新提交。

## 恢复、身份与清理

记录 `runtime`、实际任务/group/tab 标识、原 URL、原请求身份和证据。Ego TaskSpace、Tabbit group、Chrome/IAB tab 不共用 API。当前 review state 的历史字段 `space_id` 可写有命名空间的真实字符串（如 `tabbit:group:<实际ID>`），并附原始回执；不是伪造 Ego 数字 ID。换载体记录旧→新映射，保持原服务端对话和业务请求。

创建或导航超时后，先按已返回 ID 或原 URL 核对现有标签，再恢复。连接失败可按已授权任务恢复/切换可用载体；登录、验证码、工具拒绝、用户接管不能通过换浏览器绕过。任何发送/生成状态未知时先核对原消息或结果，不能在另一个浏览器重发。

完成后保存 URL、正文与文件，再关闭本任务创建的临时页/组。Ego 按当前 Skill 的 `task.finish({keep: []})` 合同；Tabbit 普通 `finish` 默认保留组；对确认全为本任务创建且仍有控制权的组，用当前 CLI 支持的 `finish --task <本轮任务名> --discard`，核对 `keep:false`、`closedTabIds` 与组清单；混有用户页时只关闭自己的页，再 finish，不整组丢弃；Chrome/IAB 按其真实 close API 只关自己创建的页。原有用户页只释放控制。需要继续等待、人工操作或用户明确保留时才留页并记录原因；仅为留个入口不保留空组。清理失败单独报告，不重新执行已完成业务。
