# OB Skills

公开、可移植的 Agent Skills 分发仓库。每个顶层 Skill 目录都是一个完整包；仓库同时提供显式发布清单、校验工具和默认只读的链接工具。

这个 checkout 只是 **Skill 分发源**，不是任何设备上的 Projects Workspace 或 `obisoldbee-skills` Project Collection 镜像。不要因为仓库里有 `SKILL.md` 或 `AGENTS.md`，就初始化它的父目录、扫描旧工作区或重建本地项目结构。

## 先选择场景

| 目的 | 正确流程 | 停止边界 |
|---|---|---|
| 完全初始化一个新目标 | 引导 Skill → 新会话 → 初始化目标目录/文件 → 克隆目标仓库 → 验证 | 完成所选治理层并验证 |
| 只更新已有 Skill 版本 | 在现有 checkout 中仅做 fast-forward 更新 → 校验 | 校验后立即停止，不触发目录治理或链接工作 |

如果当前要求是“只把 Skill 克隆下来，稍后另开会话初始化”，只执行下面的“阶段 A”；不要提前检查或初始化最终目标。

## 场景一：完全初始化

### 阶段 A：引导最新版 Skill

把本仓库 clone 到一个稳定的工具源码位置，不要直接 clone 到最终待初始化的项目目标中。

macOS / Linux 示例：

```bash
git clone https://github.com/obisoldbee/skills.git "$HOME/.local/share/obisoldbee-skills"
cd "$HOME/.local/share/obisoldbee-skills"
python3 -B scripts/verify_release.py .
```

Windows PowerShell 示例：

```powershell
git clone https://github.com/obisoldbee/skills.git "$env:USERPROFILE\AppData\Local\obisoldbee-skills"
Set-Location "$env:USERPROFILE\AppData\Local\obisoldbee-skills"
python -B scripts\verify_release.py .
```

如果用户明确说“只克隆”，到校验完成就停止。否则，继续为 **一个指定 Agent + 一个指定 Skill** 做只读扫描。不要默认扫描所有 Agent 根或所有 Skill。

macOS / Linux（把 `codex` 换成实际使用的 Agent id）：

```bash
bash scripts/link-macos.sh --agent codex --skill project-conventions
bash scripts/link-macos.sh --agent codex --skill project-conventions --apply
```

Windows 内置 PowerShell（千问 Work 中国版）：

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\link-windows.ps1 -Agent qwenwork-cn -Skill project-conventions
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\link-windows.ps1 -Agent qwenwork-cn -Skill project-conventions -Apply
```

先检查第一条命令的目标路径和 `would-link`，得到明确同意后才运行 `-Apply` / `--apply`。如果脚本报告 `target-parent-missing` 并返回非零状态，它不会擅自创建目录；确认路径正确后，可由用户创建该 **一个** consumer 根，再重新扫描。例如：

```powershell
New-Item -ItemType Directory -Force "$env:USERPROFILE\.qwenworkcn\skills"
```

链接后必须从磁盘复核，然后结束当前任务。新建链接不代表当前会话已经加载 Skill。

### 阶段 B：在新会话初始化目标

重新打开 Agent 任务，明确调用 `$project-conventions`，并只给最终目标路径。例如：

```text
使用 $project-conventions，对 C:\Users\<you>\Documents\project\obisoldbee-skills 做完整初始化。
只检查这个目标及避免路径冲突所需的最小父目录；不要检查旧工作区或其他项目。
```

此时 Skill 会先判定目标是 Projects Workspace、Project Collection 还是 Project Root，再创建该层所需目录和文件；如果给定了目标项目的 Git 仓库，它会 clone 到该 Project Root 映射的 `src/` Repository Root，并记录 remote、ref 和 managed scope。分发 checkout 本身不会被当成目标。

## 场景二：只更新 Skill 版本

在原 checkout 中执行更新；不要重新初始化目录，也不要重跑链接脚本：

```bash
git -C /path/to/obisoldbee-skills status --short --branch
git -C /path/to/obisoldbee-skills pull --ff-only
python3 -B /path/to/obisoldbee-skills/scripts/verify_release.py /path/to/obisoldbee-skills
```

Windows 将路径替换为实际 checkout，并使用 `python`：

```powershell
git -C "$env:USERPROFILE\AppData\Local\obisoldbee-skills" status --short --branch
git -C "$env:USERPROFILE\AppData\Local\obisoldbee-skills" pull --ff-only
python -B "$env:USERPROFILE\AppData\Local\obisoldbee-skills\scripts\verify_release.py" "$env:USERPROFILE\AppData\Local\obisoldbee-skills"
```

如果 worktree dirty、本地领先、detached 或分叉，应停止并单独报告；不要自动 rebase、merge、reset、stash 或搬运本地提交。更新并校验后立即停止：不修改 `AGENTS.md` / `README.md` / `docs/` / `conversation/` / `memory/`，不扫描兄弟项目、旧工作区、Agent 根，也不创建或修复链接。健康链接会自动指向 checkout 中的新内容。

## Skill 目录

| Skill | 用途 | 包入口 |
|---|---|---|
| `project-conventions` | 区分完整初始化与 update-only，并维护 Projects Workspace、Project Collection、Project Root 与 Repository Root | `project-conventions/SKILL.md` |

公开范围由 [`config/skill-exports.tsv`](config/skill-exports.tsv) 明确声明。仓库不会通过扫描目录自动把未审核内容变成公开 Skill。

## 链接工具安全边界

- 默认只扫描并报告，不写磁盘；
- 每次必须明确选择一个 `--agent` / `-Agent` 或绝对 `--target` / `-Target`，并指定一个 `--skill` / `-Skill`；
- 只有显式 `--all-agents` / `-AllAgents` 或 `--all-skills` / `-AllSkills` 才允许宽范围只读扫描；apply 禁止 `all-agents`；
- 不创建缺失的目标父目录；
- 不删除、不覆盖真实目录、错误链接或失效链接；
- 缺失父目录或冲突返回非零状态，不会用“成功退出”掩盖未完成；
- 只处理 `config/skill-exports.tsv` 中列出的 Skill；
- 应用后从磁盘核对新链接或 junction 的实际目标。

目录存在或链接成功，只能证明磁盘状态。Agent 是否发现、加载或触发 Skill，仍需在对应运行时的新会话里验证。

## 已记录的 Agent 路径

[`config/agent-paths.tsv`](config/agent-paths.tsv) 记录常见的用户级候选目录，包括通用根及 Codex、Claude、MiniMax、TRAE、CodeBuddy、Qoder/QoderWork、Qwen Work、WorkBuddy、ZCode 的品牌根。

这些条目只是路径候选，不是对任意版本运行时兼容性的保证。每次只选择实际正在使用且已经核实的 Agent id，避免在多个目录放同名副本。

## 仓库结构

```text
.
├── .github/workflows/verify.yml
├── .gitattributes
├── AGENTS.md
├── README.md
├── MANIFEST.sha256
├── config/
│   ├── agent-paths.tsv
│   └── skill-exports.tsv
├── scripts/
│   ├── link-macos.sh
│   ├── link-windows.ps1
│   └── verify_release.py
└── project-conventions/
    ├── SKILL.md
    ├── agents/
    ├── references/
    └── scripts/
```

`MANIFEST.sha256` 由发布构建生成。CI 会在 macOS、Linux 和 Windows 上校验 manifest、运行 Skill 测试，并实际执行平台链接脚本的 scoped scan/apply/readback。

## 维护原则

- 公开发布采用 allowlist，不做本机 Agent 目录镜像。
- Skill 包必须使用相对引用，不得包含个人绝对路径、本地文件 URI、凭证或私有基础设施说明。
- 本地候选、公开发布、安装、运行时发现和实际执行是不同状态，分别验证、分别陈述。
- 变更先进入专用分支或 Draft PR，经过 readback 和跨平台校验后再合并 `main`。
