# project-conventions

项目工作区布局 / 文件命名 / 多 agent 协作规范。

> 本 skill 是 **`obisoldbee/skills` monorepo** 的一部分（子目录 `project-conventions/`）。
> 单独维护、单独加载，但和其他 skill 共享同一个 git 仓库同步。

## 这是什么

一套规范，用来标准化一个项目工作区的目录结构（`AGENTS.md` / `docs/` / `memory/` / `conversation/`）和文件命名，以及 fork 工作流（clone 上游到 `src/<repo-name>/`，配置 origin/upstream，提 PR）。适用于启动新项目、写文档（spec/plan/review/research/report）、记录决策、管理版本化提交、fork 别人仓库。

## 作为 monorepo 子目录的安装

**不要用 `git clone` 单独拉这个目录**——它属于上面的 monorepo。正确做法：

```bash
# 在任意设备 clone 整个 monorepo（一次拿全部 skill）
git clone https://github.com/obisoldbee/skills.git ~/proj/skills

# 跑软链脚本，自动把 project-conventions 等所有 skill 链到 agent skills 目录
# Windows:
pwsh ~/proj/skills/scripts/link-windows.ps1
# macOS / Linux:
bash ~/proj/skills/scripts/link-macos.sh
```

脚本会在 `~/.workbuddy/skills/project-conventions` 建一个**目录联接/符号链接**，直接指向
`~/proj/skills/project-conventions/`。之后你改真源、保存，重启 WorkBuddy 即加载最新版。

## 仓库结构（本 skill 包）

```
project-conventions/
├── SKILL.md            # 规范定义，agent 加载入口
├── references/         # 7 个参考文件（目录布局 / fork 流程 / 命名等）
└── README.md           # 本文件
```

## 同步

- 改完内容 → 在 monorepo 根 `git commit && git push`
- 其他设备 `git pull` → 软链指向同一 checkout，自动最新
- 详见 monorepo 根 `README.md`

## 消费者向笔记

- 仓库根 = skill 包，clone 即用（符合 Agent Skills 开放标准）。
- `.git` / `README.md` / `.gitignore` 在 skill 目录里无害，agent 只读 `SKILL.md` + `references/`。
