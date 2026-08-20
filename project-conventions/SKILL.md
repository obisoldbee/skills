---
name: project-conventions
description: "Initialize, organize, migrate, or update project filesystems without confusing a workspace, collection, project wrapper, Git checkout, Agent Skill root, or temporary worktree. Provides deterministic ordinary Project Root initialization and a project-local, Harness-neutral reader/writer admission protocol, plus owned public/private Skill distributions, third-party checkout pools, stable member projections, device/network boundaries, scoped Agent links, and a strict update-only path. Use for 项目目录初始化, 任意 Agent 安全进入, 多 Agent 并发, 跨 Harness, worktree, obisoldbee-skills 初始化, 克隆最新版技能, 更新某个 Skill, 多设备同步, 私有 Skill 仓库, GitHub-private, GitHub-others, 设备或网络限定 Skill, 项目合集, 项目根目录, AGENTS.md, README.md, repository mapping, symlink or junction, and directory migration."
---

# Project Conventions

## Route the lifecycle before touching the filesystem

For clone, initialization, sync, pull, or update work, read `references/lifecycle-workflows.md` completely. Choose exactly one lifecycle:

| Intent | Lifecycle | Stop boundary |
|---|---|---|
| Build a new governed target and make it usable | **Full initialization** | Target, repository mapping, validation, then separately authorized consumer links |
| Refresh an existing checkout or named Skill | **Update-only** | Fetch/fast-forward, validate the requested package, report, stop |
| Reorganize or audit existing paths | **Governance maintenance** | Only the exact authorized paths and selected governance layer |
| Clone/download now for a later task | **Bootstrap-only** | Validate the clone and stop |

The presence of `AGENTS.md`, `README.md`, another project, or an Agent Skill directory never broadens the request. Do not inspect or modify unnamed siblings.

Loading this Skill during an unrelated implementation, review, or bug-fix task does not authorize or require retroactive initialization. The project-local admission protocol is mandatory only when the exact Project Root already contains its managed access block/config, or when the user selected initialization/adoption in this task. If a legacy Project Root has no local entry and its own `AGENTS.md` does not require one, do not pause the requested work merely to propose `adopt-existing`; follow its current rules and report the uncoordinated legacy boundary. Stop only on observed concurrent-write evidence or another actual conflict. Never install governance files as a side effect of an unrelated task.

## Shared-repository Skills collection profile

Read `references/shared-repository.md` completely when the target is a Skills collection backed by `obisoldbee/skills`, or when the user asks for the same directory shape on another device.

The standard shape is:

```text
<collection>/
├── AGENTS.md
├── README.md
├── MEMBERS.md
├── GitHub/                                  # the one Git worktree
│   └── project-conventions/                 # true package source
├── project-conventions/                     # stable Project Root wrapper
│   ├── .project-conventions/                # project-local cross-Harness access entry
│   ├── docs/
│   ├── conversation/
│   ├── memory/
│   └── src/project-conventions              # symlink/junction projection
└── skills/                                  # collection-control Project Root
    ├── .project-conventions/                 # independent control-project access entry
    └── src/config/skill-exports.tsv          # direct source: GitHub/project-conventions
```

Six path roles are distinct:

1. **Project Collection**: `<collection>`; it is not a Git repository.
2. **Shared Repository Root**: `<collection>/GitHub`; it is the only checkout of `obisoldbee/skills` in this collection.
3. **True Skill source**: `<collection>/GitHub/project-conventions`.
4. **Member Project Root**: `<collection>/project-conventions`; it owns documents and continuity records.
5. **Member projection**: `<collection>/project-conventions/src/project-conventions`; relative symlink on Unix, junction on Windows.
6. **Agent consumer**: an existing Agent-specific Skill root; it links directly to the true source, never through the member projection.

`GitHub` is a collection-local infrastructure name. Never replace an exact user-selected collection with an application-data or user-global source directory.

### Optional repository infrastructure

The standard initializer above owns only the public `obisoldbee/skills` distribution at `<collection>/GitHub`. A collection may additionally declare, through governance maintenance:

- an **owned private distribution Repository Root**, such as `GitHub-private`, with one Skill package per top-level directory; or
- a **third-party checkout pool**, such as `GitHub-others`, whose container has no `.git/` and whose named children are independent upstream Repository Roots.

Multiple owned distribution roots are valid only when every member mapping names one exact collection-relative `repository_root`, one normalized remote identity, and one `managed_scope`. Keep at most one checkout of each normalized remote identity in the collection. Never infer a remote, ownership, privacy, or export authority from a directory name.

An owned private repository is not a secret store. Keep credentials and raw sensitive data outside Git. Treat source publication class and runtime availability as independent: a private or local Skill may be portable, device-bound, network-bound, or device-and-network-bound. When device and network restrictions both exist, both must match; unknown evidence means do not execute the integration.

The public initializer must not create, clone, index, or link optional private distributions or third-party pools. Provisioning either is a separately scoped governance-maintenance or bootstrap action.

### Fresh initialization

For a new or explicitly cleared target:

1. Freeze the exact collection path and write set. Do not scan its parent or siblings.
2. Create the collection directory only if authorized and missing.
3. Clone `https://github.com/obisoldbee/skills.git` exactly as `<collection>/GitHub`. If `GitHub` exists, do not overwrite it; verify it is the intended clean checkout or stop on the exact conflict.
4. Require a clean attached `main`, upstream `origin/main`, normalized remote `obisoldbee/skills`, and `HEAD == origin/main`.
5. Run `GitHub/scripts/verify_release.py GitHub`; this verifies only repository-root publication files.
6. Run `GitHub/project-conventions/scripts/validate_package.py GitHub/project-conventions`; this separately validates the named package.
7. Run `initialize_skills_control_project.py` from that checked-out package first without `--apply`, inspect its exact plan, then with `--apply`:

```text
python -B <collection>/GitHub/project-conventions/scripts/initialize_skills_control_project.py \
  <collection> --distribution-root <collection>/GitHub
python -B <collection>/GitHub/project-conventions/scripts/initialize_skills_control_project.py \
  <collection> --distribution-root <collection>/GitHub --apply
```

8. Read back the three collection files, complete `skills/` control project, member wrapper, projection target, member index, and direct export source.
9. Confirm the collection root and member wrapper contain no second `.git`.
10. Stop before Agent installation unless the user separately authorized exact consumers.

The initializer is deterministic, dry-run first, and fresh-layout only. It creates no Git root and no Agent link. Do not handwrite a reduced `skills/` project.

### Update-only

An update request never runs initialization. From either the true package or member projection, use:

```text
python -B <package>/scripts/update_shared_checkout.py <package>
```

The helper resolves the shared Git worktree, requires clean/attached/tracked/ahead=0/fast-forwardable state, fetches and fast-forwards if needed, validates only the requested package, reports before/after commits, and stops.

If dirty, ahead, detached, diverged, locked, wrong-remote, or wrong-upstream, stop. Never auto-stash, merge a divergence, rebase, reset, preserve/rename branches, move files, rebuild wrappers, edit indexes, scan siblings, or relink during update-only.

One repository commit may contain changes to more than one published package. That is a Git fact, not permission to govern, install, or edit sibling Project Roots. Validate and report the requested package only.

### Agent consumers

Initialization and installation are separate states. For links:

1. Read the control allowlists.
2. Scan existing configured Agent parents first.
3. Never create an unknown or missing Agent parent.
4. Show exact conflicts and preserve rollback evidence for any existing real path or wrong link.
5. Apply only the explicitly authorized Agent targets, one at a time.
6. Every consumer must resolve directly to `<collection>/GitHub/project-conventions`.
7. Read back raw link/junction type and resolved target, then start a fresh Agent task to test discovery.

A healthy filesystem link proves only the linked state, not runtime discovery, loading, activation, or execution.

## Name the governance layer

For full initialization outside the shared profile, or governance maintenance, select exactly one layer:

| Layer | Chinese | Owns |
|---|---|---|
| **Projects Workspace** | 项目工作区 / 项目总入口 | Current-device project paths and lightweight catalog |
| **Project Collection** | 项目合集 | Routing, membership, and shared infrastructure for related independent Project Roots |
| **Project Root** | 单项目根目录 | One project's documents, decisions, memory, source entry, and repository mapping |
| **Repository Root** | Git 仓库根目录 | The worktree Git itself identifies |

A Repository Root normally lives under its Project Root's `src/`. The shared-repository profile is an explicit exception: member wrappers may declare one collection-relative `repository_root` and a `managed_scope`, while `source` is a verified projection into that scope. Never infer this exception without an explicit mapping.

## Projects Workspace mode

Read `references/projects-workspace.md` completely.

1. Keep the workspace as a local entry point, not a Git super-repository.
2. Index a Project Collection once and expand its canonical member index.
3. Run the read-only inspector before and after path, index, category, remote, or link-delegation changes.
4. Report observed findings; do not classify or repair unrelated children automatically.

```text
python3 scripts/inspect_projects_workspace.py <workspace-root> --format json
```

## Project Collection mode

Read `references/project-collection.md` completely.

1. The collection root is a routing overlay, not a Project Root.
2. Designate exactly one collection-control Project Root.
3. Keep each member's documents, conversation, and memory in its wrapper.
4. Record `source` separately from `repository_root` and `managed_scope`.
5. Each shared Repository Root is collection infrastructure and may serve multiple explicitly mapped packages; multiple roots are allowed only with explicit mappings and one checkout per remote identity.
6. Export Skills from true package sources, not copies or link chains.
7. Keep third-party checkout pools non-Git at the container root and preserve each child's upstream ownership and history.
8. Record environment-bound execution constraints in the named Skill's runtime boundary; do not mistake a clone or link for runtime eligibility.

## Project Root mode

Read `references/directory-layout.md` completely and select the primary deliverable. For initialization or adoption, also read `references/project-root-initialization.md`:

| Type | Required paths |
|---|---|
| Code | `AGENTS.md`, `README.md`, `docs/`, `src/`, `conversation/`, `memory/` |
| Document | `AGENTS.md`, `README.md`, `INDEX.md`, `docs/`, `conversation/`, `memory/`; add versioned records only for a real submission/version cycle |
| Hybrid | Code paths plus relevant document paths; `conversation/` and `memory/` remain required |

An Agent Skill development workspace remains a **Code** Project and adds the `agent-skill` profile. Its package is executable/configuration source even when the entry is Markdown: the exact entry is `src/<skill-name>/SKILL.md`, with the complete package under `src/<skill-name>/`. `src/SKILL.md` and `docs/<skill-name>/SKILL.md` are invalid. Agent-specific Skill directories are installation consumers, never editable source. The shared-repository profile is separate: its wrapper source is a verified projection to the true package in the shared checkout.

Core rules:

1. `AGENTS.md` is a lean routing and authority index; read `references/agents-md-template.md`.
2. Formal documents live under `docs/`; research stays in `docs/research/`.
3. For Code, Document, and Hybrid projects alike, decisions and collaboration history live in `conversation/`, while project-owned continuity lives in `memory/`. Harness-owned memory or hidden directories never replace either project record.
4. Read `references/migration-guide.md` before restructuring an existing Project Root.
5. Archive superseded project documents rather than silently deleting them.
6. Verify Repository Roots with Git; do not infer them from folder names.
7. Keep wrapper metadata and machine paths out of portable/public packages.
8. Ordinary initialization installs `.project-conventions/project_access.py` inside the target. This project-local helper—not Codex, another Skill, a role name, or Agent messaging—is the admission authority for cooperating Harnesses after adoption.
9. In an adopted Project Root whose local `AGENTS.md` contains the managed access block, every Agent runs `status` and obtains `read-only`, exclusive `writer`, or validated linked-worktree `isolated-writer` admission. A blocked or failed configured admission means no write, including reviews, conversation, memory, indexes, caches, Git, databases, or services. Missing governance in a legacy project is not itself permission to initialize and is not an unrelated-task blocker.
10. Do not create permanent role directories or worktrees during ordinary initialization. A Git worktree is an optional temporary execution resource and does not remove logical path, merge, lockfile, service, or canonical-record conflicts.
11. `conversation/`, `memory/`, indexes, status files, and other canonical records require the exclusive shared writer. An isolated writer cannot claim them; merge and final record updates happen only after isolated writers finish.

Initialize an ordinary Project Root with a dry-run, explicit type/mode, apply, and target validation:

```text
python3 -B scripts/initialize_project_root.py <target> \
  --type <code|document|hybrid> \
  --mode <fresh-empty|adopt-existing>
python3 -B scripts/initialize_project_root.py <target> \
  --type <code|document|hybrid> \
  --mode <fresh-empty|adopt-existing> --apply
python3 -B scripts/validate_project_root.py <target>
```

For an Agent Skill Code Project, add `--profile agent-skill --skill-name <lowercase-hyphen-name>` to both initializer commands. Validation then requires that exact package entry and a matching frontmatter `name`.

After initialization, any Harness enters through relative project-local commands documented in `references/project-access.md`; it does not need this Skill installed at runtime. Existing materials are preserved and never moved by initialization.

For a contribution fork, read `references/fork-workflow.md`. For records, use `references/conversation-format.md`, `references/review-naming.md`, and `references/versioned-records.md` as routed.

## Mutation contract

Before a write:

1. State the lifecycle, exact path roles, and selected governance layer when applicable.
2. List exact creates, edits, moves, and links.
3. Snapshot relevant Git state, hidden entries, and existing link text.
4. Preserve unrelated dirty work and user files.
5. Run the workspace inspector before an authorized workspace path/index/link-delegation change.

After a write:

1. Read back every changed path and mapping.
2. Run the named validator/tests.
3. Rerun the workspace inspector when its governed facts changed.
4. Distinguish source, checkout, projection, linked, discovered, and executed states.
5. Report unresolved findings without expanding scope.

## Success criteria

A successful shared Skills initialization has:

- one Git worktree at `<collection>/GitHub`;
- no `.git` at the collection root or member wrapper;
- a true package at `GitHub/project-conventions`;
- a Unix relative symlink or Windows junction at `project-conventions/src/project-conventions` resolving to that package;
- a complete `skills/` control project;
- a canonical index separating `source`, `repository_root`, and `managed_scope`;
- direct Agent exports from `GitHub/project-conventions`;
- no Agent links created unless separately authorized;
- root and package validation receipts;
- an idempotent second initializer run returning `already_initialized`.

## References

| File | Load when |
|---|---|
| `references/lifecycle-workflows.md` | Initializing, cloning, syncing, pulling, or updating |
| `references/shared-repository.md` | Using one collection-local Git source with member projections |
| `references/projects-workspace.md` | Maintaining a Projects Workspace |
| `references/project-collection.md` | Initializing or maintaining a collection |
| `references/directory-layout.md` | Initializing or explaining one Project Root |
| `references/project-root-initialization.md` | Deterministically creating or adopting an ordinary Project Root |
| `references/project-access.md` | Any overlapping Agent/Harness work or linked-worktree writer |
| `references/agents-md-template.md` | Creating or revising AGENTS.md |
| `references/migration-guide.md` | Moving existing paths or repository boundaries |
| `references/fork-workflow.md` | Configuring a fork and upstream |
| `references/conversation-format.md` | Recording a significant decision |
| `references/review-naming.md` | Creating or migrating reviews |
| `references/versioned-records.md` | Managing document submissions or versions |

## Cross-model execution contract

Materials: Use only the request, exact named paths, current disk/Git/link evidence, and routed references. Never invent a local path, repository state, Agent root, or remote fact.

Task: Select one lifecycle. For a shared Skills initialization, create or verify the final `GitHub` checkout, run the deterministic initializer, validate the member projection, and handle only separately authorized Agent consumers. For update-only, run the narrow updater and stop.

Constraints: Stay within named paths; preserve conflicts and rollback evidence; never create a second source copy; never turn update-only into governance or link work.

Output: In the user's language, report lifecycle, exact paths, observed state, executed changes, validations, stop boundary, and unresolved blockers. Distinguish proposed, created, Git-backed, projected, linked, discovered, and run states.
