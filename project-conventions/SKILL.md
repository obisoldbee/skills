---
name: project-conventions
description: "Initialize, organize, migrate, or explain one of three filesystem governance layers: a Projects Workspace that indexes all local projects on the current computer, a Project Collection that groups related independent projects, or one Project Root with its own documents and source repository. Use for “项目目录初始化”, “项目总入口”, “项目合集”, “项目组”, “单项目根目录”, “仓库放到 src”, “项目结构”, “文件放哪”, workspace roots, collections, project roots, repository mappings, or existing-project migrations."
---

# Project Conventions

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

1. State the selected mode and exact target.
2. List exact creates, edits, and moves.
3. Preserve user files and unrelated dirty changes.
4. For a structural migration, show the mapping and obtain approval.
5. For links, scan targets, show a dry run, and require explicit apply approval.

Never clone, fetch, pull, push, merge, rebase, delete, schedule, notify, or create links merely because initialization was requested.

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

- names exactly one of the three modes;
- does not create another layer's structure;
- keeps each Project Root's content and source inside that Project Root;
- records one clear repository mapping for each Git-backed Project Root;
- preserves existing files and Git history;
- distinguishes proposed from executed actions;
- validates authorized changes before reporting completion.

## References

| File | Load when |
|---|---|
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

Materials: Use the request, the inspected target, its existing entries, and only the routed references as evidence. Do not invent filesystem, Git, link, or remote facts.

Task: Select exactly one layer, then inspect, propose, or apply only that layer's conventions.

Constraints: Stay inside the authorized target; preserve existing content; maintain layer boundaries; obtain explicit authorization for structural moves and link application.

Output: In the user's language, state the selected mode and target, observed facts, proposed versus executed changes, validation, and unresolved findings.
