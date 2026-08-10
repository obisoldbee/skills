# Projects Workspace Convention

Use this reference for a local directory that acts as the entry point to multiple independent projects.

## Contents

1. Definition and boundary
2. Minimal layout
3. Local indexes
4. Inspection and reconciliation
5. Workspace AGENTS.md
6. Skill links
7. Upstream checks
8. Initialization and maintenance
9. Failure handling

## 1. Definition and boundary

A **Projects Workspace** is a local container such as `项目/` or `Projects/`.

It is not:

- one Project Root;
- a Git repository containing every project;
- a monorepo;
- a cross-device inventory service;
- a central store for child-project research or source code.

Each direct or nested child project remains an independent **Project Root** with its own conventions and optional Git history.

The Projects Workspace manages only the current computer. Another computer may contain fewer or different projects and repeats the same local initialization independently.

## 2. Minimal layout

```text
<projects-workspace>/
├── AGENTS.md                         # Lean workspace entry and safety rules
├── PROJECTS.md                       # Generated current-computer overview
├── _project-catalog/                 # Reserved local management project
│   ├── AGENTS.md
│   ├── README.md
│   ├── .gitignore
│   ├── config/
│   │   ├── scan.yaml
│   │   └── agent-paths.yaml
│   ├── docs/
│   │   ├── indexes/
│   │   │   ├── 00-collections.md     # Structural collection registrations
│   │   │   ├── 01-personal-open.md
│   │   │   ├── 02-personal-private.md
│   │   │   ├── 03-local-only.md
│   │   │   └── 04-upstream-open.md
│   │   ├── decisions/                # Catalog-tool decisions only
│   │   ├── plans/                    # Catalog-tool plans only
│   │   └── reports/                  # Preserved workspace reports only
│   ├── src/
│   │   ├── scanner/
│   │   ├── renderer/
│   │   ├── link-doctor/
│   │   └── upstream-check/
│   ├── tests/
│   ├── conversation/
│   ├── memory/
│   └── runtime/                      # Ignored observations and temporary output
├── <collection-a>/                   # Related Project Roots; routing overlay only
├── <project-a>/                      # Independent Project Root
├── <project-b>/                      # Independent Project Root
└── ...
```

Do not initialize Git at `<projects-workspace>/`. `_project-catalog` may use local Git for its own tooling, but its current-computer index is not a shared device inventory.

### Content boundary

For a child project named `OMS`, keep its content here:

```text
<projects-workspace>/OMS/
├── AGENTS.md
├── docs/research/
├── docs/plans/
├── docs/specs/
├── conversation/
├── memory/
└── src/
```

Never copy those paths into `_project-catalog`.

## 3. Local indexes

Maintain four ownership categories for ordinary projects physically present in the current Projects Workspace:

| File | Meaning |
|---|---|
| `01-personal-open.md` | User-led and currently public |
| `02-personal-private.md` | User-led and currently nonpublic |
| `03-local-only.md` | User-led; authoritative project content remains local |
| `04-upstream-open.md` | Third-party-led public upstream used locally |

Maintain one additional **structural** index:

| File | Meaning |
|---|---|
| `00-collections.md` | Registers a related-project collection once and points to its canonical member index |

A collection is not a fifth ownership category. Its member rows keep their four-category classification inside the collection-control project's member index.

Downloading is not a category. If a project is not cloned or created on this computer, do not add it to the local path index.

Use a fixed table:

```markdown
| key | name | path | vcs | remote | purpose | tags | update |
|---|---|---|---|---|---|---|---|
| notes-cli | Notes CLI | notes-cli | git | example/notes-cli | Personal notes utility | notes,cli | check_release |
```

Field rules:

| Field | Rule |
|---|---|
| `key` | Short stable local key; unique across the four category indexes and `00-collections.md` |
| `name` | Human display name |
| `path` | Relative to the Projects Workspace; never store credentials |
| `vcs` | Observed local state: `git` = Git worktree with a declared remote identity; `local_git` = Git worktree without one; `none` = no Git worktree at the declared source/root |
| `remote` | Credential-free provider/repository identity or `-`; for `none`, a separately verified intended/upstream identity is allowed but is not evidence of a local remote |
| `purpose` | One sentence, not project research |
| `tags` | Short retrieval terms separated consistently |
| `update` | `manual` = user-driven only; `check_release` = compare latest published release; `check_head` = compare the declared remote ref/HEAD; `pinned` = intentionally fixed and excluded from update checks |

Use this fixed collection table:

```markdown
| key | name | path | kind | members_index | purpose | tags |
|---|---|---|---|---|---|---|
| obisoldbee-skills | obisoldbee Skills | obisoldbee-skills | collection | skills/docs/indexes/members.md | Related Skill projects | skill,agent |
```

- `path` is relative to the Projects Workspace.
- `members_index` is relative to the collection root and must remain inside it.
- Register each collection only once. Do not duplicate its members in the four global category tables.
- Read `references/project-collection.md` before creating or changing a collection.

If one category becomes difficult to read, split it by topic without adding categories:

```text
docs/indexes/04-upstream-open/
├── README.md
├── agent-tools.md
├── web-apps.md
└── knowledge-tools.md
```

Generate the root `PROJECTS.md` from these local indexes, expanded collection members, and the latest read-only inspection. Do not copy child-project documents into it.

### Tooling boundary

This Skill ships only `scripts/inspect_projects_workspace.py` and its deterministic tests. The `scanner/`, `renderer/`, `link-doctor/`, `upstream-check/`, and configuration paths in the example layout describe responsibilities that a workspace catalog project may implement; they are not bundled executables promised by this Skill. The collection link utility described in `project-collection.md` is likewise a behavior contract for a collection-control project.

## 4. Inspection and reconciliation

### Full reconciliation triggers

Run pre- and post-inspection when changing:

- an indexed path;
- a project category;
- a project name that affects its directory;
- a remote identity;
- a Skill source or link target;
- multiple workspace directories.

Purpose/tag wording changes do not require a full filesystem inspection.

### Required flow

```text
inspect current workspace
→ report candidates and conflicts
→ edit local index candidate
→ inspect again
→ render PROJECTS.md atomically
→ report observed changes and unresolved findings
```

### Findings

| Finding | Meaning | Default behavior |
|---|---|---|
| `unindexed_directory` | Top-level project candidate is not indexed | Report; do not classify automatically |
| `unindexed_git_root` | Verified Git root is not covered by any indexed project path | Report; do not add automatically |
| `indexed_path_missing` | Indexed relative path does not exist | Report; do not remove the row |
| `invalid_index_path` | Index path is absolute or can escape the workspace | Block refresh; do not inspect that target |
| `dangling_link` | Symlink/junction target is missing | Report; do not repair |
| `duplicate_path` | One path appears more than once | Block overview refresh |
| `duplicate_key` | One key appears more than once | Block overview refresh |
| `remote_mismatch` | Local Git remote differs from index | Report; do not change Git config |
| `nested_git_detected` | Additional Git root exists inside a project | Report for human boundary decision |
| `reserved_entry_conflict` | `_project-catalog` was indexed as a child project | Block refresh |
| `collection_index_missing` | A declared collection member index does not exist | Report; do not cover nested repositories |
| `collection_index_invalid` | A member index escapes the collection or cannot be parsed | Block expansion; do not guess members |
| `index_read_error` | A workspace index cannot be decoded or read | Report and skip that index file |
| `collection_path_link` | A collection registration resolves through a link/junction | Block expansion; never follow it outside the workspace |
| `collection_member_path_invalid` | A declared member path is absolute, escapes, or otherwise unsafe | Block that member row |
| `collection_member_path_link` | A declared member path is a link/junction | Report and skip that member until a human confirms the boundary |
| `collection_member_source_missing` | A member's declared source path is absent | Report; never create or clone it automatically |
| `collection_member_source_invalid` | A source path is absolute, escapes, or otherwise unsafe | Block that source claim |
| `collection_member_source_link` | A declared member source is linked without a valid shared `repository_root` + `managed_scope` mapping | Report; do not infer authority |
| `collection_member_projection_invalid` | A declared shared source is dangling or cannot be resolved safely | Report; do not follow or repair it |
| `collection_member_projection_mismatch` | A declared shared source resolves somewhere other than its exact managed scope | Report the member; do not replace it |
| `collection_repository_root_missing` | A shared Repository Root declaration has no real directory | Report the declared path |
| `collection_repository_root_link` | A shared Repository Root is itself a link/junction | Report; the Git worktree boundary must be real |
| `collection_repository_root_invalid` | A declared Repository Root is absolute, escapes, or otherwise unsafe | Block that Repository Root claim |
| `collection_managed_scope_invalid` | A shared Repository Root has a missing, absolute, escaping, or otherwise unsafe managed scope | Block the shared mapping; do not follow the projection |
| `collection_member_status_invalid` | A member status is not `active`, `inactive`, `observed`, or `archived` | Report; do not treat the row as live coverage |
| `collection_control_role_invalid` | The member index has zero or multiple control projects | Report; do not guess the controller |
| `repository_root_mismatch` | Observed Git root differs from the member's declared source | Report a separate history-preserving migration; do not move it automatically |
| `index_path_link` | An index Markdown file is itself a link | Skip it; never read through the link |
| `collection_root_git` | A collection routing root is itself a Git worktree | Report a layer-boundary conflict |
| `vcs_state_mismatch` | Declared `vcs` state disagrees with observed Git roots | Report; do not initialize, remove, or reconfigure Git |

The inspector must remain offline and read-only. Do not follow unknown links outside the workspace root. Bound traversal by depth, entry count, and timeout. A collection root covers its top-level directory only; expanded member paths—not the collection directory itself—cover nested Git roots.

Use Git commands to confirm likely repository roots; `.git` may be either a directory or a gitfile:

```text
git rev-parse --show-toplevel
git rev-parse --git-common-dir
git rev-parse --show-superproject-working-tree
```

Do not decide automatically whether a nested repository is a separate Project Root.

## 5. Workspace AGENTS.md

Keep the workspace entry short:

```markdown
# Projects Workspace

> Local entry point for independent projects on this computer.

## Mandatory Rules

1. This workspace is not a Git super-repository or monorepo.
2. Each child project follows its own AGENTS.md and project-conventions.
3. `_project-catalog` manages only local paths, indexes, scans, and links.
4. Keep research, plans, specs, decisions, conversation, memory, and source inside the relevant Project Root.
5. Inspect before and after changing paths, categories, remotes, or Skill links.
6. Report missing directories, duplicates, and dangling links before acting.
7. Do not move, delete, clone, pull, push, or create links without explicit approval.

## Entry Points

- Current overview: `PROJECTS.md`
- Local indexes: `_project-catalog/docs/indexes/`
- Temporary reports: `_project-catalog/runtime/`
```

## 6. Skill links

Treat a personal Skills checkout as one ordinary local project. Keep one physical source per computer and link individual Skills into each agent's real default directory.

Before apply:

1. Confirm the source Skill contains `SKILL.md`.
2. Confirm the target parent exists.
3. Detect existing files, directories, links, and dangling links.
4. Produce a dry run.
5. Require explicit user approval.

Do not create an agent configuration directory merely because a default path is listed. Validate Windows symlink/junction behavior on Windows before claiming support.

## 7. Upstream checks

Check only third-party repositories already present in `04-upstream-open` on the current computer.

Separate mechanical observation from mutation:

```text
local Git status
→ optional ls-remote/release metadata
→ compare
→ report
```

Use local Git, SSH, GitHub CLI, or the system credential manager for repository data operations. Treat GitHub connectors as optional metadata/PR/Issue assistance.

Never auto-merge, auto-rebase, auto-checkout, auto-push, or modify remotes. If future auto-update is authorized, allow only explicitly configured clean fast-forward-only repositories.

For GitHub metrics, use:

- Star: `stargazers_count`
- Fork: `forks_count`
- Actual Watch: `subscribers_count`

Do not treat `watchers_count` as actual subscriptions.

## 8. Initialization and maintenance

### Initialize an empty/new workspace

1. Inspect the root and confirm Projects Workspace mode.
2. Propose the minimal overlay and exact files.
3. Create only after user approval.
4. Run inspection.
5. Let the user confirm which existing directories are projects and their four categories.
6. Populate local indexes.
7. Reinspect and render `PROJECTS.md`.

### Adopt an existing workspace

1. Do not move existing projects.
2. Generate a candidate report first.
3. Classify in small user-confirmed batches.
4. Keep unresolved directories as findings, not guessed index rows.
5. Add Skill links and scheduled upstream checks only in later, separately authorized phases.

### Use on another computer

1. Clone or create only the projects needed on that computer.
2. Install or obtain the same reusable workspace tool/Skill.
3. Initialize that computer's local overlay and indexes.
4. Do not import another computer's `PROJECTS.md` as truth.

## 9. Failure handling

- Unreadable workspace root: stop without writing.
- Pre-inspection failure: stop before index edits.
- Duplicate key/path: keep the prior overview and report the conflict.
- Post-inspection drift: stop and show both observations.
- Renderer failure: keep the previous `PROJECTS.md`; retain candidate output in runtime.
- Dirty child repository: report it; do not stash, reset, pull, or update.
- Network or authentication failure: report the channel-specific error; do not label the repository deleted without evidence.
- Missing target on Skill linking: report; do not manufacture the target directory.
