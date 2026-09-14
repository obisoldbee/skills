# Ordinary Project Root Initialization

Use this workflow for Code, Document, or Hybrid Project Roots outside the special shared-Skills collection profile.

This workflow runs only for an explicit initialization/adoption lifecycle. Seeing an old Project Root during a bug fix, review, build, or other unrelated task is not adoption authority: do not pause that task merely because `.project-conventions/` is absent, and do not create it without the selected initialization scope.

## Select the type from the intended deliverable

- **Code**: runnable software/source is the primary deliverable. A PRD that supports development still goes under `docs/specs/`; its presence alone does not make the project Hybrid.
- **Document**: forms, reports, submissions, certifications, or other documents are the primary deliverable.
- **Hybrid**: source code and a substantial document/submission lifecycle are both primary deliverables.

Existing file extensions are evidence, not the decision by themselves. A directory containing only `material/` can still initialize as Code when the requested outcome is “analyze these materials, write a PRD, and build the product.”

## Select a profile when the source is an Agent Skill

An Agent Skill workspace is a **Code Project** with an `agent-skill` profile, even when `SKILL.md` and YAML make up most of its package:

```bash
python3 -B scripts/initialize_project_root.py <target> \
  --type code --profile agent-skill --skill-name <skill-name> \
  --mode <fresh-empty|adopt-existing>
```

Its owned-local package root is `src/<skill-name>/`, with the entry at `src/<skill-name>/SKILL.md`. Fresh initialization creates a structurally valid, explicitly unfinished scaffold; Project Root validation does not mean the Skill behavior is ready, installed, discovered, or executed. Adoption preserves an existing correct package byte-for-byte. A root `SKILL.md`, `src/SKILL.md`, a Skill entry under `docs/`, a sibling package under `src/`, or a linked path hiding another package is a migration conflict: stop before writing and require a separately authorized exact old-to-new move. Do not move the package into `.minimax`, `.codex`, `.agents`, or another Agent directory; those are consumers. A shared-repository wrapper uses its separately verified projection and is not created by this ordinary profile.

## Select the mode

| Mode | Use when | Existing content |
|---|---|---|
| `fresh-empty` | The target is missing, empty, already initialized, or contains only recognized Harness directories | Reject unrelated user entries |
| `adopt-existing` | The target already contains user material, source, documents, or routing files | Preserve every existing item; add only the missing managed baseline |

Neither mode moves existing content, initializes Git, creates a worktree, scans siblings, or edits a Harness-owned hidden directory.

## 旧项目治理接入合同

脚本模式 `adopt-existing` 在本文中称为“旧项目治理接入”。它只适用于用户针对某一个已经存在的项目根目录逐项目明确授权的治理动作。它的作用仅限于补齐 `AGENTS.md` 路由、项目本地准入助手 `.project-conventions/project_access.py` 及其配置，以及缺失的最小管理目录和初始管理记录；它不是源码整理、仓库迁移、发布或安装流程。

接入必须原样保留所有已有资料、目录、文件和规则，不得移动、重命名、删除、复制或重新归类任何源码与用户内容；不得新建或移动 `Git` 仓库，不得执行 `fetch` 或 `push`，不得上传或发布，不得安装 `Skill`，也不得建立 `Agent` 消费者链接。

每个项目必须单独获得用户授权。`dry-run` 指只展示计划而不写入，`apply` 指按已确认计划执行写入；必须先运行 `dry-run`，确认无冲突后才能运行 `apply`。任何已有路径、内容或边界冲突都必须立即停止；任何失败都必须回滚本轮新建内容和对 `AGENTS.md` 的编辑，且不得删除或覆盖并发出现的用户内容。在无关修复、审查、构建或运行任务中，即使看到旧项目缺少本地准入助手，也不得自动接入，也不得仅因此阻断原任务；只有项目当前规则或已观察到的真实并发写冲突才能构成独立停止依据。

## Dry-run, apply, validate

Run from the installed or cloned `project-conventions` package:

```bash
python3 -B scripts/initialize_project_root.py <target> \
  --type <code|document|hybrid> \
  --mode <fresh-empty|adopt-existing>

python3 -B scripts/initialize_project_root.py <target> \
  --type <code|document|hybrid> \
  --mode <fresh-empty|adopt-existing> \
  --apply

python3 -B scripts/validate_project_root.py <target>
```

Optional fields:

- `--name <human project name>` changes generated headings only.
- `--repository-root <relative/path>` records an intended source mapping without creating or claiming that Git exists.
- `--records-dir <relative/path>` enables a version ledger for any type. It is never created merely because the type is Document; add it only for a real submission or version cycle.
- `--profile agent-skill --skill-name <name>` fixes the editable package root at `src/<name>/`; omit both for ordinary projects.

Use only normalized Project-Root-relative paths. Do not pass a user-home path, mounted-volume path, drive-qualified user path, file URI, remote machine path, or `..`.

## Adoption behavior

The initializer:

- preserves existing `README.md`, `INDEX.md`, `memory/MEMORY.md`, record indexes, and all unnamed content;
- appends one bounded access block to an existing UTF-8 `AGENTS.md` while preserving its other rules;
- stops when an existing managed block or project-control file differs;
- creates a small self-contained `.project-conventions/` access entry;
- creates only type-required directories and missing baseline files;
- reports `moved: []` because classification is not move authority;
- returns `already_initialized` on a repeated matching run.

Original/user-provided material stays where the user placed it unless a separate migration authorizes an exact old-to-new map. Typical routing for later Agent outputs is:

| Output | Destination |
|---|---|
| PRD, product/architecture specification | `docs/specs/` |
| Research, source analysis, transcript correction | `docs/research/` |
| Implementation plan | `docs/plans/` |
| Review | `docs/reviews/` |
| Design prototype/assets | `design/` |
| Runnable source and tests | `src/` |
| Decision process and user corrections | `conversation/` |
| Cross-task continuity | `memory/` |

Do not copy raw material into `docs/` merely because an Agent analyzed it. Derived documents cite the relative source path; they do not replace the source.

## Harness and remote-host boundary

`.workbuddy/`, `.codex/`, `.minimax/`, `.qoder*`, `.claude/`, and similar Harness directories are opaque. The initializer neither reads their contents nor counts them as project material. Their memory never replaces project `conversation/` or `memory/`.

When work arrives from another computer, an absolute path in the handoff is only `source_host_observed_path` evidence. Resolve the actual target on the current host and write active `AGENTS.md`, `README.md`, indexes, and configuration with relative paths. Validate those paths from disk after writing.

## Collaboration after initialization

Generated AGENTS.md and ACCESS.md default to worktree-first collaboration. Read `worktree-collaboration.md` for direct reading, independent report outputs, task branches/worktrees and single-editor integration. The retained helper is compatibility tooling, not mandatory admission. `--coordination-policy legacy-claims` is for explicitly requested old-protocol compatibility only. Existing projects switch via `migrate_worktree_policy.py <project-root> --apply`, not reinitialization or claim recovery.
