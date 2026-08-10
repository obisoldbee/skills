# Lifecycle Workflows

Use this reference before filesystem-governance references whenever a request mentions initialization, clone, download, install, sync, pull, or update.

## Decision table

| Request | Lifecycle | Immediate scope |
|---|---|---|
| “从零初始化这个目标，并把最新版 Skill 和目录配好” | Full initialization | Exact target, approved repository, deterministic local wrapper/control files, optional exact consumers |
| “先 clone，到这里停止” | Bootstrap-only | Exact checkout and its validation |
| “更新这个 Skill / 拉取最新版” | Update-only | One resolved checkout and one named package |
| “迁移旧目录到新结构” | Governance maintenance | Exact old/new paths and affected current mappings |

`clone` does not authorize sibling scans or Agent installation. `update` does not authorize initialization. An explicit end-to-end request naming the target, repository, migration inputs, and consumers authorizes those exact stages without making the user reconfirm the same map.

## Full initialization: shared Skills collection

Read `shared-repository.md`. Freeze these roles before writing:

```text
Collection Root        = <user-selected target>
Shared Repository Root = <collection>/GitHub
True package           = <collection>/GitHub/project-conventions
Member Project Root    = <collection>/project-conventions
Member projection      = <collection>/project-conventions/src/project-conventions
Control Project Root   = <collection>/skills
Consumer               = zero or more explicitly authorized existing Agent Skill roots
```

### Stage 1: final-path clone

If the collection is new, create only that directory. Clone the distribution directly into the final shared Repository Root:

```text
git clone https://github.com/obisoldbee/skills.git <collection>/GitHub
```

Do not derive a nested destination from the repository name. In particular, do not create `project-conventions/src/skills`, `project-conventions/src/project-conventions` as a checkout, or any application-data source.

If `GitHub` already exists, inspect that exact path. A non-Git snapshot, wrong repository, dirty worktree, detached ref, local-ahead branch, divergence, or operation lock is a blocker. Never clone over, delete, reset, stash, rebase, or merge it automatically.

Require:

```text
worktree root = <collection>/GitHub
origin identity = obisoldbee/skills
branch = main
upstream = origin/main
status = clean, including untracked
HEAD = origin/main
```

Run repository-root and named-package validation separately:

```text
python -B <collection>/GitHub/scripts/verify_release.py <collection>/GitHub
python -B <collection>/GitHub/project-conventions/scripts/validate_package.py \
  <collection>/GitHub/project-conventions
```

The first command is intentionally `repository-root-only`; it does not replace the second.

### Stage 2: deterministic collection materialization

Run the checked-out initializer dry-run and apply:

```text
python -B <collection>/GitHub/project-conventions/scripts/initialize_skills_control_project.py \
  <collection> --distribution-root <collection>/GitHub
python -B <collection>/GitHub/project-conventions/scripts/initialize_skills_control_project.py \
  <collection> --distribution-root <collection>/GitHub --apply
```

The initializer accepts only the exact fresh layout. It creates:

- collection `AGENTS.md`, `README.md`, and `MEMBERS.md`;
- a complete `skills/` collection-control Project Root;
- a complete `project-conventions/` wrapper;
- one relative symlink on Unix or junction on Windows from the member source entry to the true package;
- an index that separates `source`, `repository_root`, and `managed_scope`;
- direct export source `GitHub/project-conventions`.

It creates no Git root and no Agent consumer link. Read back every result, then rerun with `--apply` and require `already_initialized`.

### Stage 3: optional consumers

Only if the user explicitly authorized Agent installation:

1. Scan configured existing parents.
2. Report `would-link`, `healthy-link`, missing parent, real-path conflict, wrong link, and dangling link separately.
3. Never create a missing Agent parent.
4. Preserve conflicts under collision-free backups only with explicit replacement authority.
5. Apply each exact Agent target independently.
6. Require every consumer to resolve directly to `<collection>/GitHub/project-conventions`.

After links are read back, report linked state separately from runtime discovery. A fresh Agent task is required to prove discovery.

## Bootstrap-only

When the user requests clone/download only:

1. Clone to the exact named destination.
2. Verify Git identity and clean current state.
3. Verify the repository-root manifest and named package.
4. Report commit and stop.

Do not inspect an eventual collection target, old workspaces, siblings, Agent roots, or links.

## Update-only

Use the requested package's deterministic updater:

```text
python -B <package>/scripts/update_shared_checkout.py <package>
```

It resolves the worktree from the package, so it works from either:

- `<collection>/GitHub/project-conventions`; or
- `<collection>/project-conventions/src/project-conventions` when that projection is healthy.

The safety gate is:

1. exact package entry and managed subpath;
2. exact Git worktree readback;
3. expected branch, upstream, and remote;
4. clean tracked and untracked state;
5. no Git operation or lock;
6. fetch succeeds;
7. ahead count is zero;
8. local `HEAD` is an ancestor of upstream;
9. fast-forward only when behind;
10. root and named-package validation pass.

Dirty, ahead, detached, diverged, wrong-remote, wrong-upstream, or locked states stop without changing local commits or files. A fetch may update remote-tracking refs before a divergence is known; report that fact precisely.

Forbidden side effects in update-only:

- selecting or initializing a governance layer;
- creating or revising wrapper `AGENTS.md`, `README.md`, indexes, `docs/`, `conversation/`, or `memory/`;
- inspecting sibling projects or old workspaces;
- creating, repairing, replacing, or reapplying links;
- moving a checkout or preserving/renaming a local branch;
- auto-stash, merge, rebase, reset, cherry-pick, or delete.

After validation, report before/after commit and stop. A healthy projection or consumer automatically sees new bytes and does not require relinking.

## Governance maintenance and migration

Read `migration-guide.md`; for the shared layout also read `shared-repository.md`.

1. Run the Projects Workspace inspector before changing a registered path, index mapping, remote declaration, or link delegation.
2. Inspect only exact named sources, destinations, and affected mappings.
3. Snapshot hidden entries, Git roots, raw link text, and relevant index/export files.
4. Present the exact move/backup/projection map.
5. If both ends were already explicitly named by the user, that map is authorized; ask again only if an observed collision, Git risk, or host lock changes it.
6. Switch command execution out of any directory being moved.
7. Prefer same-filesystem atomic moves. Never replace a move with copy-and-delete because the host holds a workspace lock.
8. Preserve old real package or snapshot trees under collision-free rollback paths before replacing them with projections.
9. Update only current routing/index/export references. Preserve historical before/after records unchanged.
10. Validate and run the Projects Workspace inspector after the change.

Migration is not update-only. It may alter wrapper/index/link state only because the user explicitly requested that structural change.

## Generic non-shared initialization

For an ordinary Projects Workspace, Project Collection, or Project Root that does not use the shared profile, route to its governance reference and use its initializer. A normal Git-backed Project Root usually keeps its Repository Root under `src/`.

Do not apply the shared exception merely because two projects use the same hosting provider. It requires an explicit collection-relative `repository_root` plus a repository-relative `managed_scope`.

## Stop and report

Every lifecycle report includes:

- selected lifecycle;
- exact paths and roles;
- observed Git and link facts;
- writes actually executed;
- validators and their result;
- state labels: source, Git-backed, projected, linked, discovered, executed;
- stop boundary and unresolved blockers.

Never report “installed” from a clone, “discovered” from a link, or “executed” from a passing static validator.
