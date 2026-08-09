# OB Skills

公开、可移植的 Agent Skills 分发仓库。每个顶层 Skill 目录都是由对应成员项目独立维护的完整包；仓库根目录提供显式路由配置、根文件校验工具和默认只读的链接工具。

这个 checkout 是 **Skill 分发源**，不是任何设备上的 Projects Workspace 或 `obisoldbee-skills` Project Collection 镜像。它可以按用户指定放在某个 Project Root 的 `src/` 下，并随该 Project Root 一起迁移。只处理用户明确给出的当前根、最终目标、迁移来源和一个 Agent consumer；不要从仓库内容推断其他本地路径。

## 先选择场景

| 目的 | 正确流程 | 停止边界 |
|---|---|---|
| 当前目录内先取得最新版 Skill，再初始化目标并迁移指定旧目录 | 在当前 Project Root 的 `src/` 内 clone → 校验并直接读取 Skill → 初始化目标 → 原子迁移指定目录；若没有旧 `skills/`，运行完整控制项目初始化器 → 最终路径校验 → 再询问链接 | 整条链路验证完成，或遇到真实碰撞/工作区锁 |
| 只克隆最新版 Skill | clone 到用户给定位置 → 校验 | 校验后立即停止，不看最终目标、兄弟目录或链接 |
| 只更新已有 Skill 版本 | 在现有 checkout 中仅做 fast-forward 更新 → 校验 | 校验后立即停止，不触发目录治理或链接工作 |

“需要 clone”不等于“只能另开会话”。用户明确要求完整链路且给出了所有路径时，clone 后直接读取新 checkout 里的 `project-conventions/SKILL.md`，在同一任务继续；只有用户明确说“先只克隆”时才提前停止。

## 场景一：完全初始化

### Windows 完整示例：当前 bootstrap 目录随后也要迁移

假设当前任务打开在 `Documents\project\project-conventions`，用户指定最终集合为同级 `obisoldbee-skills`，并指定迁移同级 `skills` 与整个当前 `project-conventions`。路径角色必须固定为：

```powershell
$ProjectParent = Join-Path $env:USERPROFILE 'Documents\project'
$BootstrapRoot = Join-Path $ProjectParent 'project-conventions'
$RepositoryRoot = Join-Path $BootstrapRoot 'src'
$PackageRoot = Join-Path $RepositoryRoot 'project-conventions'
$LegacyControl = Join-Path $ProjectParent 'skills'
$TargetCollection = Join-Path $ProjectParent 'obisoldbee-skills'
```

这里的 Git Repository Root 就是 `project-conventions\src`，仓库内受管 Skill 包是 `src\project-conventions`。不要根据远端仓库名再插入一层 `src\skills`；也不要另造全局下载目录或直接把仓库 clone 成最终 `obisoldbee-skills`。

#### 1. 先在当前目录内 clone 并校验

确认 `$RepositoryRoot` 不存在且不会碰撞后执行：

```powershell
git clone https://github.com/obisoldbee/skills.git "$RepositoryRoot"
python -B (Join-Path $RepositoryRoot 'scripts\verify_release.py') $RepositoryRoot
python -B (Join-Path $PackageRoot 'scripts\test_inspect_projects_workspace.py')
python -B (Join-Path $PackageRoot 'scripts\test_lifecycle_workflows.py')
if (-not (Test-Path -LiteralPath (Join-Path $PackageRoot 'SKILL.md') -PathType Leaf)) {
  throw "Skill 没有位于正确路径：$PackageRoot"
}
```

若 `$RepositoryRoot` 已经是同一仓库，不重复 clone；先核实 remote、branch、status、ahead/behind。可以 clean fast-forward 时直接更新并继续。

若旧版流程已经产生 `$BootstrapRoot\src\skills\project-conventions\SKILL.md`，不要再 clone。先把 `$BootstrapRoot\src\skills` 当作旧 Repository Root 验证并更新，然后直接读取其最新 `project-conventions\references\lifecycle-workflows.md` 中的 **obsolete nested layout** 修复流程。只有 `src` 内除这个 clean checkout 外没有任何条目时，才可以整体展平为 `$BootstrapRoot\src`；不复制后删除，不丢弃本地保留分支。

```powershell
$OldPackageRoot = Join-Path $BootstrapRoot 'src\skills\project-conventions'
$LayoutRepair = Join-Path $OldPackageRoot 'scripts\repair_project_conventions_checkout_layout.py'
python -B $LayoutRepair $BootstrapRoot
python -B $LayoutRepair $BootstrapRoot --apply
```

如果它正是旧任务留下的 **clean、attached、本地 `main` ahead/diverged** checkout，而本次完整链路已经明确授权“保留旧本地提交并切回最新远端 main”，使用分支保留，不 rebase、不 reset、不删除提交：

```powershell
$OldHead = (git -C "$RepositoryRoot" rev-parse HEAD).Trim()
$CurrentBranch = (git -C "$RepositoryRoot" symbolic-ref --quiet --short HEAD).Trim()
$Status = @(git -C "$RepositoryRoot" status --porcelain=v1)
if ($Status.Count -ne 0) { throw 'worktree 不是 clean，停止' }
if ($CurrentBranch -ne 'main') { throw "当前分支不是预期 main：$CurrentBranch" }

git -C "$RepositoryRoot" fetch origin
if ($LASTEXITCODE -ne 0) { throw 'fetch origin 失败' }

$ShortHead = $OldHead.Substring(0, 7)
$PreservedBranch = "main-preserved-$ShortHead"
git -C "$RepositoryRoot" show-ref --verify --quiet "refs/heads/$PreservedBranch"
if ($LASTEXITCODE -eq 0) { throw "保留分支已存在：$PreservedBranch" }
if ($LASTEXITCODE -ne 1) { throw '无法检查保留分支冲突' }

git -C "$RepositoryRoot" branch -m "$PreservedBranch"
if ($LASTEXITCODE -ne 0) { throw '无法重命名旧本地分支' }
git -C "$RepositoryRoot" switch -c main --track origin/main
if ($LASTEXITCODE -ne 0) { throw '无法从 origin/main 创建新的本地 main；旧提交仍保留在重命名分支' }

$PreservedHead = (git -C "$RepositoryRoot" rev-parse "$PreservedBranch").Trim()
$FreshHead = (git -C "$RepositoryRoot" rev-parse HEAD).Trim()
$RemoteHead = (git -C "$RepositoryRoot" rev-parse origin/main).Trim()
if ($PreservedHead -ne $OldHead) { throw '保留分支未指向旧 HEAD' }
if ($FreshHead -ne $RemoteHead) { throw '新的 main 未指向 origin/main' }
```

此操作只属于用户明确授权的完整初始化恢复，不属于 update-only。保留分支不自动 push，随后会随整个 `project-conventions` Project Root 一起迁移。dirty、detached、remote/default branch 不明或保留分支重名时仍应停止，但只报告这个真实阻塞。

随后直接读取：

```text
<bootstrap-root>\src\project-conventions\SKILL.md
<bootstrap-root>\src\project-conventions\references\lifecycle-workflows.md
<bootstrap-root>\src\project-conventions\references\migration-guide.md
```

这已经足以“基于最新版 Skill”继续执行；自动发现 Skill 才需要新会话，直接读取本地 Skill 不需要。

#### 2. 初始化目标并迁移两个明确来源

只预检 `$BootstrapRoot`、`$LegacyControl`、`$TargetCollection` 和避免碰撞所需的最小父目录。记录隐藏文件、Git 根/remote/ref/status/stash、链接和活动工作目录；不要扫描其他兄弟项目。

完成顶层碰撞与 Git 安全检查后，立即用包内确定性初始化器创建 Project Collection 的三个根文件，并当场回读；不先递归扫描大仓库：

```powershell
$Initializer = Join-Path $PackageRoot 'scripts\initialize_project_collection.py'
python -B $Initializer $TargetCollection `
  --control-project skills `
  --reserve skills `
  --reserve project-conventions `
  --apply
Get-Item (Join-Path $TargetCollection 'AGENTS.md'), `
  (Join-Path $TargetCollection 'README.md'), `
  (Join-Path $TargetCollection 'MEMBERS.md')
```

这一步只创建 `AGENTS.md`、`README.md`、`MEMBERS.md`，不创建会与迁入目录碰撞的 `skills` 或 `project-conventions`。迁移映射只有这两条：

```text
<project-parent>\skills               -> <project-parent>\obisoldbee-skills\skills
<project-parent>\project-conventions  -> <project-parent>\obisoldbee-skills\project-conventions
```

用户已经用完整源路径和目标路径明确要求这两次迁移时，不要再让用户从“归档/保留/不处理”等无关方案中重选；仅在目标碰撞、Git 状态风险或工作区锁改变了计划时暂停。

移动当前工作目录前，先把执行目录切到 `$ProjectParent`。若宿主应用仍锁定当前 workspace，只做一次必要交接：请用户在 `$ProjectParent` 或 `$TargetCollection` 重新打开任务，然后按已记录映射继续。不要用复制后删除代替原子移动。

迁移后，更新 collection 路由文件、成员索引和当前路径引用，并验证旧路径消失、最终路径存在、两个目录的隐藏文件与 Git 状态未变。历史迁移记录中的旧路径保留。

如果磁盘上根本没有要迁入的旧 `$LegacyControl`，不要临场手写一个只有 `README.md` 和 `src\config` 的缩水版。应先确保最终 member checkout 已位于 `$TargetCollection\project-conventions\src`、处于 clean `main`、跟踪并等于 `origin/main`，然后使用最新版包内的第二个确定性初始化器：

```powershell
$FinalRepositoryRoot = Join-Path $TargetCollection 'project-conventions\src'
$FinalPackageRoot = Join-Path $FinalRepositoryRoot 'project-conventions'
$ControlInitializer = Join-Path $FinalPackageRoot 'scripts\initialize_skills_control_project.py'

python -B $ControlInitializer $TargetCollection `
  --distribution-root $FinalRepositoryRoot
python -B $ControlInitializer $TargetCollection `
  --distribution-root $FinalRepositoryRoot `
  --apply
python -B (Join-Path $TargetCollection 'skills\src\tests\test_public_root_overlay.py')
```

dry-run 会先列出完整写入集合；apply 会创建与本地标准同层级的 portable 控制项目：`docs/`、`conversation/`、`memory/`、`release/`、`runtime/`，以及 `src/README.md`、`src/config/`、`src/public-repo/`、`src/scripts/`、`src/tests/`。它不会复制另一台设备的历史记录或生成物，不创建 Git，不创建 junction，并会从最终 Git checkout 回读后再写 canonical member index 与根 `MEMBERS.md`。

#### 3. 最后才处理 Skill junction

最终 checkout 与 Skill 包路径是：

```text
<project-parent>\obisoldbee-skills\project-conventions\src
<project-parent>\obisoldbee-skills\project-conventions\src\project-conventions
```

此时才为 **一个指定 Agent + `project-conventions`** 扫描最终 junction：

```powershell
$FinalRepositoryRoot = Join-Path $TargetCollection 'project-conventions\src'
$LinkScript = Join-Path $FinalRepositoryRoot 'scripts\link-windows.ps1'
powershell.exe -NoProfile -ExecutionPolicy Bypass -File $LinkScript -Agent qwenwork-cn -Skill project-conventions
powershell.exe -NoProfile -ExecutionPolicy Bypass -File $LinkScript -Agent qwenwork-cn -Skill project-conventions -Apply
```

第一条只读扫描必须先展示 `would-link` 和最终源路径；只有用户明确同意后才执行第二条。不要先链接迁移前的临时 Repository Root，否则整个 `project-conventions` 迁移后 junction 会失效。应用后从磁盘复核；链接存在仍不等于当前会话已经自动发现 Skill。

macOS/Linux 使用相同的路径关系和阶段顺序，并在最终路径运行 `scripts/link-macos.sh`。平台差异不能改变“当前目录内 clone、迁移后再链接”的顺序。

### 只克隆时的停止边界

如果用户只要求把仓库 clone 到当前 `project-conventions` 内，执行第 1 节的 clone 与校验后立即停止：不检查 `$LegacyControl` / `$TargetCollection`，不初始化目录，不扫描 Agent，不创建 junction。

## 场景二：只更新 Skill 版本

先从用户给出的现有路径或当前 Git worktree 解析真实 checkout；不要假设它位于某个固定的用户级目录。然后只更新该 checkout，不重新初始化目录，也不重跑链接脚本：

```bash
git -C /path/to/obisoldbee-skills status --short --branch
git -C /path/to/obisoldbee-skills pull --ff-only
python3 -B /path/to/obisoldbee-skills/scripts/verify_release.py /path/to/obisoldbee-skills
```

Windows 示例使用迁移后的实际 checkout：

```powershell
$RepositoryRoot = Join-Path $env:USERPROFILE 'Documents\project\obisoldbee-skills\project-conventions\src'
git -C "$RepositoryRoot" status --short --branch
git -C "$RepositoryRoot" pull --ff-only
python -B (Join-Path $RepositoryRoot 'scripts\verify_release.py') $RepositoryRoot
```

完整执行前仍要获取 tracked remote 并计算 ahead/behind；上面的短命令不是跳过安全门的理由。如果 worktree dirty、本地领先、detached 或分叉，应停止并单独报告；不要自动 rebase、merge、reset、stash 或搬运本地提交。更新并校验后立即停止：不修改 `AGENTS.md` / `README.md` / `docs/` / `conversation/` / `memory/`，不扫描兄弟项目、旧工作区、Agent 根，也不创建或修复链接。健康链接会自动指向 checkout 中的新内容。

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
├── ROOT-MANIFEST.sha256
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
    ├── scripts/
    └── assets/skills-control/
```

`ROOT-MANIFEST.sha256` 只覆盖仓库根目录管理项目拥有的文件，不列入或校验任何成员 Skill 包。CI 会在 macOS、Linux 和 Windows 上校验根文件，并实际执行平台链接脚本的 scoped scan/apply/readback；成员包内容由各自 Project Root 独立维护。

仓库根文件获授权修改后，用 checkout 自带命令原子重建根清单，再立即只读校验；两个命令都不读取或校验成员包：

```bash
python3 -B scripts/verify_release.py . --rebuild-root-manifest
python3 -B scripts/verify_release.py .
```

任一命令失败就停止，不发布。

## 维护原则

- 公开发布采用 allowlist，不做本机 Agent 目录镜像。
- 根目录更新只替换 `ROOT-MANIFEST.sha256` 列出的根文件，所有成员 Skill 目录原样保留。
- Skill 包必须使用相对引用，不得包含个人绝对路径、本地文件 URI、凭证或私有基础设施说明。
- 本地候选、公开发布、安装、运行时发现和实际执行是不同状态，分别验证、分别陈述。
- 变更先进入专用分支或 Draft PR，经过 readback 和跨平台校验后再合并 `main`。
