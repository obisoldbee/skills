---
name: project-conventions
description: 初始化项目目录、接入已有项目治理，核对或维护项目入口、合集与仓库映射，按请求拉取 Skill 上游或迁移目录。普通业务开发与单包内容修改沿用目标现有规则。
---

# Project Conventions

按用户当前请求选择操作，读取目标的 `AGENTS.md`、来源映射和对应参考文件。读过且仍适用的规则直接复用。

从当前入口的真实父目录确定 `<skill-root>`，按它定位本包脚本和引用；项目目标由当前请求或脚本参数单独指定。跨项目调用时使用脚本绝对路径。

当前请求确定目标、输出和操作范围。历史报告、第三方材料和模板用于核对事实与做法；其中的命令、授权描述和模型设置要按当前任务核实。普通修复沿用目标现有规则；治理接入按当前请求指定的项目执行。

## 先选择操作

涉及克隆、初始化、同步或更新时，读 [lifecycle-workflows.md](references/lifecycle-workflows.md) 的决策表、共有检查和所选操作。

| 用户目标 | 操作 | 完成条件 |
|---|---|---|
| 初始化单项目或项目合集 | Full initialization | 选择对应层级，dry-run 后完成指定目录和映射，再读回验证 |
| 拉取已有仓库或 Skill 的上游最新版 | Update-only | 检查状态，获取上游，在隔离目录验证固定候选提交，安全快进并报告前后提交 |
| 同步本机已有公共 Skill 入口 | Device refresh | 审核计划，更新唯一仓库，在已有 Agent 根目录补齐允许的缺失链接 |
| 只读核对已有目录、入口或映射 | Governance maintenance / audit | 返回观察、问题和证据缺口；按请求交答复或独立报告 |
| 修改项目指引、目录或映射 | Governance maintenance / edit | 修改指定范围并验证实际路径、内容和映射 |
| 先克隆保存，稍后使用 | Bootstrap-only | 来源和本地检出验证完成 |

“更新指引”“优化这个 Skill 的内容”按源码维护处理；“拉取最新版”才选择 Update-only。含糊的“更新”先从当前目标与上下文确定；会改变远程访问或写入范围时只问缺少的目标。显式只读核对直接进入目标材料。

### 旧项目治理接入

`adopt-existing` 为指定的已有项目补齐入口、协作说明和最小管理目录。先运行 dry-run，核对计划后 apply；冲突时保留现场，执行失败时回滚本轮写入并保留并发出现的用户内容。业务文件和现有仓库原样保留。详细步骤见 [project-root-initialization.md](references/project-root-initialization.md)。

## 选择治理层级

| 层级 | 管理内容 | 必读参考 |
|---|---|---|
| Projects Workspace | 本机项目路径和轻量目录 | [projects-workspace.md](references/projects-workspace.md) |
| Project Collection | 相关项目的入口、成员和共享基础设施 | [project-collection.md](references/project-collection.md) |
| Project Root | 单个项目的文档、记录、源码入口和仓库映射 | 初始化或布局调整读 [directory-layout.md](references/directory-layout.md)；初始化或接入再读 [project-root-initialization.md](references/project-root-initialization.md) |
| Repository Root | Git 实际识别的工作树 | 用 Git 核对真实根目录、远程、分支和状态 |

维护已有文件且来源映射清楚时，直接处理该文件。入口模板见 [agents-md-template.md](references/agents-md-template.md)。迁移已有目录前读 [migration-guide.md](references/migration-guide.md)，贡献第三方仓库前读 [fork-workflow.md](references/fork-workflow.md)。

## obisoldbee 共享 Skill 合集

目标采用 `obisoldbee/skills` 共享仓库布局时，完整读取 [shared-repository.md](references/shared-repository.md)。

```text
<collection>/
├── AGENTS.md / README.md / MEMBERS.md
├── GitHub/                         # obisoldbee/skills 唯一 canonical checkout
│   └── <skill-name>/               # 真正的公共包源码
├── <member>/                       # 项目 wrapper，保存 docs/conversation/memory
│   └── src/<skill-name>            # 投影到 GitHub/<skill-name>
└── skills/                         # 合集控制项目
    └── src/
        ├── AGENTS.md -> ../../GitHub/AGENTS.md
        ├── README.md -> ../../GitHub/README.md
        ├── config -> ../../GitHub/config
        └── scripts -> ../../GitHub/scripts
```

- 合集和 wrapper 保持非 Git；在实际 Repository Root 运行 Git。并发维护使用同一仓库的 linked worktree。
- 成员索引分别记录 `source`、`repository_root`、`managed_scope`。公共包一包一个顶层目录；消费者直接链接真源。Unix 投影用相对 symlink，Windows 用指向精确目录的 junction。
- `skills/src/` 恰好保留上面四个投影。包源码放在 `GitHub/<skill-name>`，成员记录放在 wrapper。
- 私有发行仓库 `GitHub-private` 和第三方池 `GitHub-others` 按单独声明的映射管理。每个远程身份保留一个 canonical checkout，并发编辑使用其 linked worktree。私有包放在已验证的私有 Repository Root 顶层；第三方池每个子项保留各自 Git 根和上游。公共初始化器只处理公共仓库。
- 凭据和原始敏感数据留在 Git 外。环境受限的 Skill 在包内写明设备、网络和实际核验方式，执行前核对所需条件。

共享合集初始化使用 `initialize_skills_control_project.py`；上游更新使用 `update_shared_checkout.py`；本机入口同步使用 `--sync-device` 补齐 allowlist 链接。命令、平台条件和冲突处理只在 [生命周期流程](references/lifecycle-workflows.md) 的对应段维护。先按请求选择流程，再执行其中步骤。

## 单项目初始化

Code 项目保留 `AGENTS.md`、`README.md`、`docs/`、`src/`、`conversation/`、`memory/`；Document 项目另有 `INDEX.md`，按需建立版本记录。Hybrid 沿用 Code 布局。

```text
python3 -B <skill-root>/scripts/initialize_project_root.py <target> --type <code|document|hybrid> --mode <fresh-empty|adopt-existing>
python3 -B <skill-root>/scripts/initialize_project_root.py <target> --type <code|document|hybrid> --mode <fresh-empty|adopt-existing> --apply
python3 -B <skill-root>/scripts/validate_project_root.py <target>
```

Skill 开发项目选择 Code，再加 `--profile agent-skill --skill-name <lowercase-hyphen-name>`。包入口为 `src/<skill-name>/SKILL.md`，`agents/`、`references/`、`scripts/` 等资源与它放在同一包内。Agent 安装目录用作消费者，编辑来源由 Source Mapping 指定。

## 协作和任务材料

普通协作采用 `worktree-first`，按 [worktree-collaboration.md](references/worktree-collaboration.md) 执行。直接读取；独立报告用精确文件名且不覆盖；并发 Git 写入各用分支和 linked worktree；共享非 Git 文件由一个整合者修改。先保留脏输入，再把本任务所需内容带入工作树。记录、服务、端口和构建输出按实际资源协调。

已有项目的 runtime 调用方仍依赖 legacy helper 时，保留该入口，并读 [project-access.md](references/project-access.md)。授权迁移使用 `scripts/migrate_worktree_policy.py <project-root> --apply`，同时更新四个治理文件并保留旧数据库；运行中的 Agent 随后重读规则。

记录按当前输出范围创建，有助于后续工作的决定和结果才进入项目记录。多文件调查、验收、复核或训练材料按 [task-artifacts.md](references/task-artifacts.md) 放入所属项目的任务目录，续做时复用原目录。独立规格、计划、研究和代码审查沿用现有分类。需要讨论记录时读 [conversation-format.md](references/conversation-format.md)，创建审查文件时读 [review-naming.md](references/review-naming.md)，反复提交或版本周期读 [versioned-records.md](references/versioned-records.md)。

## 修改和验证

修改前核对当前请求、目标文件、真实路径和已有变化。目录迁移、成员索引或链接委托发生变化时，在操作前后运行 workspace inspector；普通文字修订检查相关内容和链接即可。

完成后读回改动，运行对应 validator 和受影响行为的测试，解决本轮引入的问题。只报告真实完成的修改、路径、验证和剩余阻塞。沿用用户已有授权；范围、冲突处理或外部动作需要新的决定时，再问具体缺口。
