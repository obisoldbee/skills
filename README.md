# OB Skills

公开、可移植的 Agent Skills 分发仓库。每个顶层 Skill 目录都是一个完整包；仓库同时提供显式清单和默认只读的链接工具。

这个仓库不是任何一台电脑上 `skills/` 目录的完整镜像。本地私有 Skill、第三方安装项、缓存、凭证和机器专用资料不会因为存在于某个 Agent 目录就自动发布。

## Skill 目录

| Skill | 用途 | 包入口 |
|---|---|---|
| `project-conventions` | 区分并维护 Projects Workspace、Project Collection、Project Root 与 Repository Root | `project-conventions/SKILL.md` |

公开范围由 [`config/skill-exports.tsv`](config/skill-exports.tsv) 明确声明。仓库不会通过扫描目录自动把未审核内容变成公开 Skill。

## 快速开始

先把仓库 clone 到任意稳定位置。下面的路径只是可移植示例，不是运行时硬编码：

```bash
git clone https://github.com/obisoldbee/skills.git "$HOME/src/ob-skills"
cd "$HOME/src/ob-skills"
```

macOS / Linux 推荐先检查通用 Agent Skill 根：

```bash
bash scripts/link-macos.sh --agent agents
bash scripts/link-macos.sh --agent agents --apply
```

Windows PowerShell：

```powershell
pwsh scripts/link-windows.ps1 -Agent agents
pwsh scripts/link-windows.ps1 -Agent agents -Apply
```

也可以选择品牌目录，例如 `--agent qwenwork-cn` / `-Agent qwenwork-cn`，或通过 `--target` / `-Target` 指定一个已经存在的自定义 Skill 根。

## 安全边界

链接工具遵循同一套规则：

- 默认只扫描并报告，不写磁盘；
- `--apply` / `-Apply` 必须同时指定一个 Agent 或自定义目标；
- 不创建缺失的目标父目录；
- 不删除、不覆盖真实目录、错误链接或失效链接；
- 只处理 `config/skill-exports.tsv` 中列出的 Skill；
- 应用后从磁盘核对新链接。

目录存在或链接成功，只能证明磁盘状态。Agent 是否发现、加载或触发 Skill，仍需在对应运行时的新会话里验证。

## 已记录的 Agent 路径

[`config/agent-paths.tsv`](config/agent-paths.tsv) 记录常见的用户级候选目录，包括：

- 通用根：`~/.agents/skills`；
- Codex、Claude、MiniMax、TRAE、CodeBuddy、Qoder/QoderWork、Qwen Work、WorkBuddy、ZCode 的品牌根；
- Windows 下对应的 `%USERPROFILE%` 路径。

这些条目是路径候选，不是对任意版本运行时兼容性的保证。优先使用已经被目标运行时实际验证的根，避免在多个目录放同名副本。

## 更新

链接指向本地 checkout 中的 Skill 目录。更新已有 Skill 时，在 checkout 中执行 `git pull` 后重启或刷新 Agent 即可；内容更新不需要重建链接。

新增 Skill 时重新运行扫描，再显式应用。删除或下架 Skill 时，脚本只报告原有链接，不会替用户自动删除。

## 仓库结构

```text
.
├── README.md
├── MANIFEST.sha256
├── config/
│   ├── agent-paths.tsv
│   └── skill-exports.tsv
├── scripts/
│   ├── link-macos.sh
│   └── link-windows.ps1
└── project-conventions/
    ├── SKILL.md
    ├── agents/
    ├── references/
    └── scripts/
```

`MANIFEST.sha256` 由发布构建生成，用于核对候选树。公开仓库 README、脚本、配置和 Skill 包应在同一变更中更新，避免文档与行为出现中间态。

## 维护原则

- 公开发布采用 allowlist，不做本机 Agent 目录镜像。
- Skill 包必须使用相对引用，不得包含个人绝对路径、本地文件 URI、凭证或私有基础设施说明。
- 本地候选、公开发布、安装、运行时发现和实际执行是不同状态，分别验证、分别陈述。
- 变更先进入专用分支或 Draft PR，经过 readback 和校验后再决定是否合并 `main`。
