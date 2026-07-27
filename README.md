# project-conventions

一套**项目工作区布局 + 文件命名 + 多 agent 协作**规范，作为 agent skill 分发。

> 本仓库根目录**就是 skill 包**（`SKILL.md` + `references/`）。克隆到 skills 目录即可直接被 agent 加载，无需任何额外步骤。

## 安装（某设备 / 某 agent）

```bash
# 克隆到对应 agent 工具的 skills 目录——SKILL.md 在仓库根，立即可用
git clone https://github.com/obisoldbee/project-conventions.git <skills-dir>/project-conventions
```

常见 skills 目录：

| Agent 工具 | Skills 路径 |
|---|---|
| WorkBuddy | `~/.workbuddy/skills/` |
| QoderWork | `~/.qoderworkcn/skills/` |
| Claude Code | `~/.claude/skills/` |
| CodeBuddy | `~/.codebuddy/skills/` |

> 因为 SKILL.md 在仓库根，克隆完文件夹名就是 skill 名，直接生效。

## 更新

```bash
git -C <skills-dir>/project-conventions pull --rebase
```

## 语言约定

SKILL.md 和 references/ 使用英文编写（供 agent 消费，减少 token 开销）；用户可见的模板内容（如 `提交记录/` 相关模板）可能使用中文。这是有意为之，非不一致。

## 作为开发者：迭代规范

本 GitHub 仓库的**开发真源**在开发机的工作区里，路径为 `src/project-conventions/`（遵循 project-conventions 自身的 SOP wrapper 约定：`src/<repo-name>/` 独立 git 仓库）。开发者在真源改 `SKILL.md` / `references/`，提交并推送到本 GitHub 仓库；各设备再 `pull` 同步。

多设备协作：先 `git pull --rebase origin main` 接他人改动，再 `git push origin main`。

## 内容

- `SKILL.md` — skill 定义（agent 加载入口，frontmatter + 规范概览）
- `references/` — 规范参考文档：
  - `directory-layout.md` — 完整目录布局规范
  - `fork-workflow.md` — fork 仓库工作流（gh CLI、PR、upstream 同步）
  - `agents-md-template.md` — AGENTS.md 模板
  - `conversation-format.md` — 对话记录格式
  - `review-naming.md` — 评审文件命名
  - `migration-guide.md` — 目录迁移指南
  - `versioned-records.md` — 版本化提交记录（文档类项目）

## License

个人规范库，按需自取自用。
