---
name: project-conventions
description: "Initialize, organize, migrate, update, or explain project filesystems. First separate full initialization from update-only work: full initialization may create an approved structure, clone its repository, and guide one scoped Skill link; update-only refreshes one existing checkout and stops without restructuring, cataloging, recording, or relinking. Then distinguish a Projects Workspace, Project Collection, Project Root, and Repository Root. Use for 项目目录初始化, 从零初始化, 克隆最新版后初始化, 更新技能版本, 拉取最新版, 项目总入口, 项目合集, 单项目根目录, 仓库放到 src, 项目结构, 文件放哪, repository mappings, or migrations."
---

# Project Conventions

## Choose the lifecycle before the governance layer

For any request involving initialization, clone, download, install, sync, pull, or update, read `references/lifecycle-workflows.md` completely. Classify the request before inspecting any broader directory:

| User intent | Lifecycle | Immediate scope |
|---|---|---|
| Create a new governed location and make it usable | **Full initialization** | The exact new target and its approved repository/link inputs |
| Clone this Skill now, then initialize another target in a fresh task | **Full initialization — bootstrap stage only** | The distribution checkout and one named Skill consumer; stop before target governance |
| Refresh an existing Skill or repository checkout | **Update-only** | That one verified checkout; update, validate, and stop |
| Organize, migrate, audit, or explain existing project structure | **Governance maintenance** | The exact requested path, then one of the three layers below |

Do not let a distribution checkout become the target merely because it contains `SKILL.md` or `AGENTS.md`. Do not inspect an old workspace, sibling projects, all configured Agent roots, or all exported Skills unless the user explicitly put them in scope.

### Full initialization

A full initialization is a complete, ordered lifecycle, but its bootstrap and target stages may be separated by a fresh Agent session.

1. If the Skill is not yet available, clone the approved distribution repository into one stable source location. Treat that checkout only as a distribution source.
2. Validate the requested Skill package from the checkout.
3. Inspect exactly one named consumer root and one named Skill. If the consumer root is absent, give one focused creation command or ask permission to create it. Show a dry run and require explicit approval before creating a link.
4. After link readback, stop. Tell the user to open a fresh task so the runtime can discover the new Skill. Do not initialize the eventual target in the bootstrap task.
5. In the fresh target task, inspect only the requested target, select exactly one governance layer, create that layer's required files and directories, and clone the approved project repository into the layer's mapped Repository Root when one was supplied.
6. Validate the resulting structure, repository mapping, and any explicitly applied link.

If the user explicitly starts at step 5 because the Skill is already loaded, do not repeat the bootstrap or link steps.

### Update-only

An update-only request is deliberately narrow:

1. Verify the exact checkout, its Git worktree root, current ref, remote, and worktree status.
2. If it is clean and only behind its tracked remote, fetch and fast-forward only. If it is already current, make no change.
3. If it is dirty, ahead, detached, or diverged, stop with one focused report. Do not merge, rebase, reset, stash, cherry-pick, or port local commits automatically.
4. Run the checkout's package/manifest validation and report the before/after commit.
5. Stop. Do not select a governance layer; create or revise `AGENTS.md`, `README.md`, indexes, `docs/`, `conversation/`, or `memory/`; scan siblings or old workspaces; or inspect, create, repair, or reapply links.

An existing healthy link points into the checkout, so a content update does not require relinking. Link troubleshooting is a separate explicitly requested task.

## Name the layer before acting

Use these terms consistently:

| Layer | Chinese | Owns |
|---|---|---|
| **Projects Workspace** | 项目工作区 / 项目总入口 | The current computer's project paths and lightweight catalog |
| **Project Collection** | 项目合集 | Membership and routing for related independent Project Roots |
| **Project Root** | 单项目根目录 | One project's documents, decisions, memory, source, and repository mapping |
| **Repository Root** | Git 仓库根目录 | The directory Git identifies as the worktree root; for a Git-backed Project Root, normally under `src/` |

A folder named `项目/` may remain named that way. Its role—not its literal name—determines the layer.

## Route first

Inspect the requested path read-only and choose exactly one mode:

1. **Projects Workspace mode** — one local entry contains multiple unrelated projects or collections.
2. **Project Collection mode** — one group contains related independent Project Roots plus one lightweight collection-control project.
3. **Project Root mode** — one governed project with its own deliverables and normally one source repository mapping.

Ask only when evidence is genuinely ambiguous:

> 你要初始化的是“项目总入口”、“项目合集”，还是一个“单项目根目录”？

| Evidence | Route |
|---|---|
| `项目/` contains OMS, pets, skills collection, and unrelated experiments | Projects Workspace |
| `obisoldbee-skills/` groups multiple Skill projects and a collection-control project | Project Collection |
| `project-handoff/` has its own docs, conversation, memory, and `src/` | Project Root |

## Projects Workspace mode

Read `references/projects-workspace.md` completely.

1. Inspect current top-level entries and likely Git roots read-only.
2. Preserve every child in place unless a move is separately authorized.
3. Use only the lightweight overlay: `AGENTS.md`, generated `PROJECTS.md`, and `_project-catalog/`.
4. Maintain four category indexes for ordinary local Project Roots and a separate structural collection index.
5. For a collection, index the collection once and expand its declared member index; do not duplicate every member in the global category tables.
6. Inspect before and after path/index changes and report omissions, duplicates, missing paths, and dangling links.

The workspace catalog never owns child-project source, research, plans, specs, reviews, conversation, or memory.

## Project Collection mode

Read `references/project-collection.md` completely.

1. Verify that the members are related but independently governed Project Roots.
2. Keep the collection root as a routing overlay, not a Git super-repository and not another Project Root.
3. Designate exactly one member as the **collection-control project**. It owns the canonical member index and collection-wide deterministic scripts.
4. Keep each member's documents and source inside that member Project Root.
5. Do not copy member source into the control project's `src/`.
6. Expose a generated/readable member view at collection root when useful.

For a Skills collection, the control project may own an explicit Skill-export allowlist and safe link scripts. Linking remains a separate, explicitly approved action.

## Project Root mode

Read `references/directory-layout.md` completely. Determine the primary deliverable:

| Type | Primary deliverable | Required paths |
|---|---|---|
| **Code** | Software or source | `AGENTS.md`, `README.md`, `docs/`, `src/`, `conversation/`, `memory/` |
| **Document** | Documents or submissions | `AGENTS.md`, `README.md`, `INDEX.md`, `docs/`, versioned records |
| **Hybrid** | Both | Code paths plus relevant document paths |

Core rules:

1. Formal documents live under `docs/`; project research stays in `docs/research/`.
2. `AGENTS.md` is a lean routing index. Read `references/agents-md-template.md`.
3. Decisions and collaboration history live in `conversation/`; project-managed memory lives in `memory/`.
4. Read `references/migration-guide.md` before restructuring an existing Project Root.
5. Archive superseded project documents rather than deleting them.
6. Verify the Repository Root with Git; never infer it from the Project Root name.
7. A Git-backed Project Root normally maps to one Repository Root under `src/`. Record the local repository path, clone URL or remote identity, default ref, and any managed subpath in `AGENTS.md`.
8. A GitHub `/tree/<ref>/<subpath>` URL is a repository subpath, not a clone URL. Clone or check out the repository into `src/`, then record the managed subpath.
9. If unrelated repositories are needed, create sibling Project Roots. Do not turn one Project Root into a hidden multi-repository container.
10. Keep local wrapper metadata out of portable or public deliverables. Export with relative paths and exclude `.DS_Store`, `__pycache__/`, `*.pyc`, credentials, and machine-specific absolute paths.

### Fork workflow

For a contribution fork, read `references/fork-workflow.md`. Clone the one repository under `src/`, use `origin` for the personal fork and `upstream` for the original, and keep wrapper documents outside the checkout.

### Records

- Significant direction change: read `references/conversation-format.md`.
- Reviews: read `references/review-naming.md`.
- Versioned submissions: read `references/versioned-records.md`.

## Layer boundaries

| Wrong | Correct |
|---|---|
| Put `src/` or project research directly in the Projects Workspace | Put it in a Project Root |
| Put member source in a collection-control project's `src/` | Keep source in the member Project Root |
| List collection members twice in workspace indexes | Index the collection once and expand its member index |
| Put the Git checkout at the Project Root while wrapper docs are meant to stay outside Git | Put the Repository Root under `src/` |
| Treat every device as a shared inventory model | Manage the current computer; another computer repeats the same local flow |
| Infer that a missing local path means a remote project is invalid | Report only the current computer's observed state |

## Mutation and safety

Inspection or planning does not authorize mutation.

Before a write:

1. State the selected lifecycle, mode when applicable, and exact target.
2. List exact creates, edits, and moves.
3. Preserve user files and unrelated dirty changes.
4. For a structural migration, show the mapping and obtain approval.
5. For links, scan targets, show a dry run, and require explicit apply approval.

Do not infer authorization for clone, fetch, pull, push, merge, rebase, delete, schedule, notify, or link creation from a vague request. The only exceptions are the exact clone or fast-forward steps explicitly selected by the lifecycle contract above; link application still requires explicit approval.

After an authorized write:

1. Re-read the resulting structure.
2. Run the relevant validator/tests.
3. Report observed facts, unresolved findings, and actions not taken.

## Workspace inspector

Use `scripts/inspect_projects_workspace.py` only for Projects Workspace mode:

```text
python3 scripts/inspect_projects_workspace.py <workspace-root> [--indexes-dir PATH] [--max-depth N] [--format json|markdown]
```

It is offline and read-only. It understands the structural collection index and expands each safe `members_index`; it does not classify, move, link, or repair anything.

## Success criteria

A successful run:

- names the selected lifecycle before any governance layer;
- hard-stops update-only work after checkout validation;
- for target initialization or governance maintenance, names exactly one of the three modes;
- does not create another layer's structure;
- keeps each Project Root's content and source inside that Project Root;
- records one clear repository mapping for each Git-backed Project Root;
- preserves existing files and Git history;
- distinguishes proposed from executed actions;
- validates authorized changes before reporting completion.

## References

| File | Load when |
|---|---|
| `references/lifecycle-workflows.md` | Initializing, cloning, installing, syncing, pulling, or updating |
| `references/projects-workspace.md` | Maintaining the current computer's Projects Workspace |
| `references/project-collection.md` | Initializing or maintaining a related-project collection |
| `references/directory-layout.md` | Initializing or explaining one Project Root |
| `references/agents-md-template.md` | Creating or revising a Project Root AGENTS.md |
| `references/migration-guide.md` | Moving existing files or repository boundaries |
| `references/fork-workflow.md` | Configuring a fork and upstream |
| `references/conversation-format.md` | Recording a significant decision |
| `references/review-naming.md` | Creating or migrating reviews |
| `references/versioned-records.md` | Managing document submissions or versions |

## Cross-model execution contract

Materials: Use the request, the exact lifecycle target, its existing entries, and only the routed references as evidence. Do not invent filesystem, Git, link, or remote facts.

Task: Select one lifecycle first. For full initialization or governance maintenance, select exactly one layer at the target stage. For update-only, update and validate the exact checkout, then stop without layer selection.

Constraints: Stay inside the authorized lifecycle target; preserve existing content; maintain stage and layer boundaries; obtain explicit authorization for structural moves and link application; never broaden a bootstrap or update into workspace governance.

Output: In the user's language, state the selected lifecycle, stage or mode when applicable, exact target, observed facts, proposed versus executed changes, validation, stop boundary, and unresolved findings.
