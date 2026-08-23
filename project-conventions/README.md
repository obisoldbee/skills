# project-conventions

Filesystem-governance Skill with strict lifecycle boundaries, deterministic ordinary Project Root initialization, and a self-contained cross-Harness reader/writer admission protocol. It also supports explicitly mapped public, private, local-only, and third-party Skill sources.

## Lifecycle routing

| Lifecycle | Behavior |
|---|---|
| Full initialization | Clone once to the final shared Repository Root, materialize complete wrappers/control files, verify projections, then optionally install exact Agent consumers |
| Update-only | Validate the named package from a frozen fetched candidate, safely fast-forward that exact commit, and stop |
| Device refresh | Plan first, then update the one existing checkout and add only missing public allowlisted links in existing Agent roots when authorized |
| Governance maintenance | Audit or migrate only exact authorized paths and mappings |
| Bootstrap-only | Clone, validate, and stop |

Update-only never initializes directories, rewrites indexes, scans siblings, or relinks consumers.

## Shared Skills collection

```text
<collection>/GitHub/project-conventions                  # true source
<collection>/project-conventions/src/project-conventions # stable projection
<collection>/skills/src/{AGENTS.md,README.md,config,scripts} # four root projections
<agent-root>/project-conventions                         # direct consumer link
```

The member index separates:

- `source`: wrapper-relative entry;
- `repository_root`: collection-relative Git worktree;
- `managed_scope`: repository-relative package.

This prevents a package name from being mistaken for another checkout directory and prevents update requests from triggering collection initialization.

The standard initializer creates one public `obisoldbee/skills` checkout. Governance maintenance may add another explicitly mapped owned distribution, with at most one checkout per remote identity, or a non-Git third-party checkout pool whose children keep independent upstream histories. It never creates those optional roots as a side effect of public initialization.

Publication class and runtime eligibility are independent. Environment-bound Skills declare non-secret device and network labels, a verification method, and a mismatch stop rule; when both axes are constrained, both must match.

## 旧项目治理接入

脚本模式 `adopt-existing` 指“旧项目治理接入”。它只能针对用户逐项目明确授权的已有项目根目录，只补齐 `AGENTS.md` 路由、项目本地准入助手和最小管理记录。它原样保留所有已有资料，不移动、重命名、删除或重新归类源码，不新建或移动 `Git` 仓库，不执行 `fetch` 或 `push`，不上传或发布，不安装 `Skill`，也不建立 `Agent` 消费者链接。

接入必须先运行只展示计划的 `dry-run`，确认无冲突后再运行执行写入的 `apply`；冲突即停，失败回滚本轮写入。在无关修复中看到旧项目缺少本地准入助手，不得自动接入，也不得仅因此阻断原任务。完整合同见 `references/project-root-initialization.md`。

## Deterministic tools

| Tool | Purpose |
|---|---|
| `scripts/initialize_project_root.py` | Dry-run/apply initializer for ordinary Code, Document, and Hybrid Project Roots; preserves existing material |
| `scripts/validate_project_root.py` | Validates one initialized Project Root and its local Agent-entry contract |
| `scripts/project_access.py` | Source copied into each initialized Project Root for atomic status/enter/check/finish/recover admission |
| `scripts/initialize_skills_control_project.py` | Dry-run/apply fresh shared collection initializer; creates no Git root, source copy, or Agent link |
| `scripts/update_shared_checkout.py` | Candidate-first validated, clean fast-forward-only updater for one named package |
| `scripts/validate_package.py` | Offline package shape and portability validator |
| `scripts/inspect_projects_workspace.py` | Read-only Projects Workspace and collection-mapping inspector |
| `scripts/initialize_project_collection.py` | Generic non-shared three-file collection overlay initializer |

The ordinary Project Root initializer installs only a small `.project-conventions/` control entry. Cooperating Agents in Codex, WorkBuddy, Qoder, Trae, or another Harness use the same project-local command, so no external dispatcher or Agent messaging is required to discover active readers/writers. Multiple readers may coexist; a shared writer is exclusive; clean linked-worktree writers may coexist only for declared non-overlapping paths.

The shared Skills initializer creates a complete `skills/` control project, four independent projections of the public repository-root management entries, and a stable member wrapper. It never projects the whole checkout as `skills/src/skills` and never copies repository-root files into the control project. Control exports point directly to true Git packages so Agent consumers never form a link chain.

## Validate

The deterministic Python tools support Python 3.11 and newer. CI exercises the Windows junction fallback on Python 3.11 and the native junction API on the latest Python.

From this package:

```bash
python3 -B scripts/validate_package.py .
python3 -B scripts/test_inspect_projects_workspace.py
python3 -B scripts/test_lifecycle_workflows.py
python3 -B scripts/test_project_root_workflows.py
```

From the distribution checkout, also run:

```bash
python3 -B scripts/verify_release.py .
```

The root verifier and package validator have different scopes. Skill discovery and execution are separate runtime states and must be tested in a fresh Agent task after linking.
