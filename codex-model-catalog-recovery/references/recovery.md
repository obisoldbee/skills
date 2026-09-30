# 平台诊断与恢复

## 绑定运行环境

以下变量必须来自本次观察，示例不是固定安装路径：`codexHome` 为目标桌面实际 home；`desktopCore` 为桌面使用的核心可执行文件；`candidateCore` 为已安装且来源可信的候选新版核心；`workDir` 为复现故障的工作目录。记录 UTC 时间及本地时区。

确认启动环境中的 `CODEX_HOME`，未设置才用目标用户的 `.codex`。远程 shell 的 home 和环境不一定等于桌面。检查相关 profile、provider、启动参数和项目配置的差异；不要输出凭据字段或完整命令行中的敏感参数。若无法确认有效配置，两次核心查询只能算近似对照。

### Windows：安装包、桌面核心和独立 CLI 分开看

只读发现可用 PowerShell：

```powershell
Get-Command codex -ErrorAction SilentlyContinue | Select-Object Source
Get-CimInstance Win32_Process |
  Where-Object { $_.Name -match '^(codex|chatgpt).*\.exe$' } |
  Select-Object ProcessId,ParentProcessId,Name,ExecutablePath
Get-AppxPackage *Codex* | Select-Object Name,Version,PackageFamilyName,InstallLocation
[Environment]::GetEnvironmentVariable('CODEX_CLI_PATH','User')
[Environment]::GetEnvironmentVariable('CODEX_CLI_PATH','Machine')
```

结合桌面父子进程和安装元数据确定核心；不要选到独立 daemon、code-mode-host 或沙箱服务。分别对已确认的可执行文件运行 `--version`。不要用 `Get-Content` 读 exe，也不要改 WindowsApps 权限或替换包内二进制。不同版本会使用不同布局，禁止硬编码缓存哈希目录或商店包版本。

通过应用更新工具检查当前渠道；`busy/unavailable/error` 不等于没有更新。商店包可进一步通过已发现的包标识检查 Microsoft Store/winget；显示名可能是 ChatGPT。不能拿 `winget list --name Codex` 无结果断言未安装。检查和实际升级分开：升级只在任务授权时执行，不硬编码历史商店 ID。

### macOS：定位当前应用内的核心

从实际运行应用及其包元数据定位资源目录；应用可能叫 ChatGPT 或 Codex。核心可能在资源根，也可能在嵌套 CLI app 内。与 shell 的 `command -v codex` 区分。验证具体路径的 `--version`，不递归打印整个应用或用户目录。

正常退出并从已绑定应用路径重开；记录退出前后 PID。正常退出超时就说明仍在运行，不升级为 `kill -9`。窗口关闭不一定退出进程。任务执行器依赖该应用时按 SKILL 的续接边界处理。

## 读取缓存与查询核心目录

缓存只提取 `fetched_at`、`client_version`、目标条目的 `slug/display_name/visibility`；不转存完整账户配置。先保存两次查询各自的摘要，再看缓存。新版核心可能写入缓存，旧核心随后又覆盖，因此最终缓存不能代表两次结果。

检查目标核心 `app-server --help`。协议不确定时，可用它的 `app-server generate-json-schema --out <新的临时目录>` 离线核查 `initialize`、`model/list`。不要给接口猜测 `refresh`、`force` 参数。下面脚本使用 newline JSON stdio、`initialize` → `initialized` → `model/list`（含隐藏项和分页）。它查询运行时目录，**不保证绕过运行时自身缓存，也不承诺强制服务端刷新**。

在已绑定平台上调用；Windows 可用已确认的 `python`/`py -3`，macOS 用 `python3`：

```text
python -B <skill>/scripts/probe_models.py --binary <核心绝对路径> --codex-home <目标home绝对路径> --cwd <工作目录绝对路径> --expect <模型ID>
```

默认总超时 45 秒，最多 20 页。退出码 0 = 完整目录含可见目标；2 = 查询/协议失败；3 = 完整目录缺失或隐藏。输出只包含定位信息、模型 ID、隐藏状态和思考强度。不会新建聊天、发消息或执行推理；运行时仍可能联网并更新自身缓存/日志。脚本结束仅清理自己启动的诊断进程，不终止现有桌面或 daemon。

## 分支 A：移除已确认过时的目录覆盖

只在查明覆盖生效且用户要恢复默认模型目录时修改；有意使用的自定义 provider/catalog 不应自动删除。

1. 记录实际配置路径、文件 SHA-256；TOML 解析确认根键或已选 profile。注释和其他 profile 中的同名键不是候选。还要排除启动参数重新覆盖。
2. 在本地同目录以不存在的新文件名创建原始字节备份，保留权限；配置可能含秘密，备份不得提交、上传或打印。
3. 仅注释对应赋值，保留 CRLF/BOM（若原解析器支持）、编码、其他原始字节。多行值要处理完整赋值，不能只注释第一行。无法可靠识别时先生成精确补丁，不用全局正则替换或重写整份 TOML。
4. 解析候选 TOML，确认语义差异仅为所选覆盖项消失。写入前重读原文件并比对 SHA，发现并发变化就重新检查；不要覆盖别人刚改的配置。用同目录临时文件替换并回读检查权限及内容。
5. 查询同一目标核心；需要时正常重启桌面并检查 UI。回滚时仅撤销本轮变更；原文件后续未改动才可还原整份备份。

默认不删 `models_cache.json`。只有当前版本证据明确指向缓存损坏时，另行说明并备份该精确缓存，再做一次受控重建；不清空整个 Codex home。

## 分支 B：Windows 桌面核心落后

优先桌面正式更新；没有可用更新时，核心覆盖是**有条件的本地兼容措施**，不是所有版本的官方稳定设置，也不是升级桌面包。

应用前同时满足：

- 同环境对照可复现“桌面核心缺目标、候选核心有可见目标”。
- 当前安装版本的本地代码或文档确实支持以 `CODEX_CLI_PATH` 指定核心。只读检查相关代码片段即可；不能把旧案例当成现版本支持证据。
- 候选路径已存在、来源可信，`Get-AuthenticodeSignature -FilePath $candidateCore` 为 `Valid` 且签名者是 OpenAI；版本和 model/list 协议可用。保留与核心配套的 code-mode-host 等文件，不单独拷 exe 拼装运行时。
- 已记录 User/Machine/当前 Process 三层旧值及启动路径，且用户已有修复授权覆盖该目标。`User` 级覆盖影响该用户未来启动且读取此变量的其他程序，需要告知；现有非空覆盖要解释并保留，不能假设为空。

执行时先将旧值（区分未设置与字符串）和候选路径、版本、hash 写入新的本地回滚记录。然后仅设置 User 级，不动 Machine：

```powershell
# candidateCore 必须已通过上述检查；不是从案例复制的路径。
[Environment]::SetEnvironmentVariable('CODEX_CLI_PATH', $candidateCore, 'User')
[Environment]::GetEnvironmentVariable('CODEX_CLI_PATH', 'User')
```

注册表值回读成功不代表运行中的进程环境已变。可使用当前平台支持的环境变更通知促使启动器刷新，但通知成功仍不是继承证明。对目标应用正常退出重开；必要时从**独立、已授权且明确设置本次 Process 环境**的启动器按已核实的应用入口启动。不要从旧环境的 shell 重开后就宣称生效，不结束 Explorer 来强制刷新。

重开后核对桌面子进程实际路径和版本、UI 模型列表，以及普通聊天和所需工具是否正常。核心跨版本可能有兼容问题；出现启动/工具异常即撤销本轮覆盖并正常重开，保留失败证据。不能把 CLI 查询成功当成桌面协议兼容证明。

回滚只在当前 User 值仍等于本轮设置值时，用备份旧值还原；原先未设置则传 `$null`。发现后续改动就不覆盖。正式桌面更新赶上以后，优先移除此临时覆盖，验证恢复到包内核心；否则固定路径可能失效或阻止后续桌面自动采用新版核心。
