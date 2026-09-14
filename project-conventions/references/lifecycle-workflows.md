# Lifecycle Workflows

Use the decision table and shared guards below to select the requested lifecycle before its filesystem-governance references. Read only the selected lifecycle section and its named dependencies; a mention of initialization, clone, install, or update in task materials does not activate that operation.

## Decision table

| Request | Lifecycle | Immediate scope |
|---|---|---|
| “从零初始化这个目标，并把最新版 Skill 和目录配好” | Full initialization | Exact target, approved repository, deterministic local wrapper/control files, optional exact consumers |
| “先 clone，到这里停止” | Bootstrap-only | Exact checkout and its validation |
| “更新这个 Skill / 拉取最新版” | Update-only | One resolved checkout and one named package |
| “本机全量同步 Skills / 更新 GitHub 并让本机 Agent 使用 / 同步共享 Skill 根” | Device refresh | Plan first; one existing checkout and missing public allowlisted links in existing Agent roots |
| “迁移旧目录到新结构” | Governance maintenance | Exact old/new paths and affected current mappings |

`clone` does not authorize sibling scans or Agent installation. `update` does not authorize initialization. An explicit end-to-end request naming the target, repository, migration inputs, and consumers authorizes those exact stages without making the user reconfirm the same map.

脚本模式 `adopt-existing` 指“旧项目治理接入”，它必须由用户针对每一个已有项目根目录单独明确授权。它只补齐 `AGENTS.md` 路由、项目本地准入助手和最小管理记录，不移动源码，不建立或移动 `Git` 仓库，不上传、发布、安装 `Skill` 或建立 `Agent` 消费者链接。必须先运行 `dry-run` 再运行 `apply`，冲突即停，失败回滚。无关修复不会因为旧项目缺少 `.project-conventions/` 而自动变成接入任务，也不得仅因此阻断原任务。完整合同见 `project-root-initialization.md`。

## Full initialization: shared Skills collection

Read `shared-repository.md`. Freeze these roles before writing:

```text
Collection Root        = <user-selected target>
Shared Repository Root = <collection>/GitHub
True package           = <collection>/GitHub/project-conventions
Member Project Root    = <collection>/project-conventions
Member projection      = <collection>/project-conventions/src/project-conventions
Control Project Root   = <collection>/skills
Control projections    = <collection>/skills/src/{AGENTS.md,README.md,config,scripts}
Consumer               = zero or more explicitly authorized existing Agent Skill roots
```

This standard lifecycle materializes only the public `obisoldbee/skills` distribution. Optional owned private distributions and third-party checkout pools are separate governance-maintenance or bootstrap stages, even when one explicit end-to-end user request authorizes those exact stages.

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
- exactly four independent public-root management projections under `skills/src/`, never a whole-repository `src/skills` projection or copied root files;
- a complete `project-conventions/` wrapper;
- one relative symlink on Unix or junction on Windows from the member source entry to the true package;
- an index that separates `source`, `repository_root`, and `managed_scope`;
- direct export source `GitHub/project-conventions`.

It creates no Git root and no Agent consumer link. Read back every result, then rerun with `--apply` and require `already_initialized`.

### Stage 3: optional consumers

Only if the user explicitly authorized Agent installation. Check platform support first: the current repository Windows consumer script supports scoped apply through its NT directory-handle helper; the initializer's projection support is not consumer installation support.

1. Scan configured existing parents.
2. Report `would-link`, `healthy-link`, missing parent, real-path conflict, wrong link, and dangling link separately.
3. Never create a missing Agent parent.
4. Preserve conflicts under collision-free backups only with explicit replacement authority.
5. Apply each exact Agent target independently.
6. Require every consumer to resolve directly to `<collection>/GitHub/project-conventions`.

After links are read back, report linked state separately from runtime discovery. Discovery requires an available fresh runtime readback; create a new user-visible Agent task only when the user explicitly requests it. If that evidence is unavailable, complete the authorized filesystem checks and report discovery as unverified.

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
9. extract the frozen upstream commit into an isolated temporary candidate tree and require named-package validation to pass there;
10. recheck `HEAD`, branch, upstream, status, operation markers, remote, and the frozen upstream commit;
11. fast-forward only the exact validated commit when behind;
12. perform final read-only state readback.

Dirty, ahead, detached, diverged, wrong-remote, wrong-upstream, or locked states stop without changing local commits or files. A fetch may update remote-tracking refs before a divergence is known; report that fact precisely.

Forbidden side effects in update-only:

- selecting or initializing a governance layer;
- creating or revising wrapper `AGENTS.md`, `README.md`, indexes, `docs/`, `conversation/`, or `memory/`;
- inspecting sibling projects or old workspaces;
- creating, repairing, replacing, or reapplying links;
- moving a checkout or preserving/renaming a local branch;
- auto-stash, merge, rebase, reset, cherry-pick, or delete.

After the validated fast-forward and final readback, report before/after commit and stop. A candidate validation failure leaves local `HEAD` and the worktree unchanged; fetch may still have updated the remote-tracking ref. A healthy projection or consumer automatically sees new bytes and does not require relinking.

## Device refresh

Device refresh is an explicit end-to-end lifecycle for the current device. It is selected only by the exact synchronization intents in the decision table, not by a request to update one named Skill.

1. Resolve the one existing `<collection>/GitHub` checkout; do not clone or initialize.
2. Run the platform repository script with `--sync-device` / `-SyncDevice` and no apply flag.
3. Require the repository safety check and a conflict-free scan of existing configured Agent roots.
4. On Windows, combined `-SyncDevice -Apply` is unavailable. If sync and installation are explicitly authorized, update/validate the one checkout separately, then scan and apply with `-Agent` or `-Target`, plus `-Skill` or `-AllSkills`. Do not bypass a scoped safe-create failure with `New-Item` or `mklink`.
5. On supported Unix hosts, when the request already authorizes synchronization, rerun with `--apply` without asking the user to repeat that authorization. Fast-forward only the one checkout, reread the public allowlists from the updated checkout, then create only missing allowlisted links under Agent roots that already exist.
6. Read back checkout, links, and validation receipts; report linked separately from discovered or executed.

Device refresh never creates a second checkout or missing Agent root, replaces any real/wrong/dangling path, changes export policy, regenerates wrappers, indexes, conversation, or memory, or edits member projects. A conflict stops apply. This consumer reconciliation is the intentional difference from update-only.

Windows collection/member projection initialization and consumer creation are different operations. The initializer's junction support does not establish a safe Windows consumer apply path. Restoring consumer apply requires a directory-handle-bound exclusive creation primitive and real Windows tests for aliases, case variants, reparse points, existing leaves, final-step parent replacement, and unchanged Git/consumer state on rejection. The scoped installer uses this primitive; changes to it must pass those real Windows tests before installation. A documentation change or macOS test cannot establish Windows support. Resolve a named remote host's actual OS and checkout before any separately authorized remote work.

## Governance maintenance and migration

Read `migration-guide.md` when changing paths or repository boundaries; for the shared layout also read `shared-repository.md`. Existing-file instruction maintenance does not require a migration workflow or workspace scan unless those governed facts change.

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

### Optional private distribution

For an explicitly named owned private Skill repository:

1. Freeze the exact collection-relative Repository Root, normalized remote identity, expected private visibility, and write set.
2. Treat an existing empty directory as a scaffold, not as Git evidence. If the remote exists, clone or attach only through an explicitly approved conflict-free workflow; if remote creation is authorized, create it as private before the first push.
3. Read back the exact worktree root, remote identity, default ref, clean status, and remote visibility. Stop if visibility is public or unknown.
4. Keep one Skill package per top-level directory and no nested package Git roots.
5. Reject credentials, cookies, private keys, raw sensitive data, and machine-secret configuration even in private Git.
6. Add member wrappers, mappings, exports, or consumers only when those exact paths are separately authorized.

### Third-party checkout pool

For an explicitly named upstream pool:

1. Require the pool root to be a real non-Git directory.
2. Scope work to one named child or one observed-only registry row; siblings remain read-only.
3. Every cloned child keeps its own exact Git root, upstream identity, license, and history.
4. A studied but un-cloned upstream gets no fabricated local checkout path.
5. Clone, update, fork, adopt, install, and execute are separate states and permissions.

## Generic non-shared initialization

For an ordinary Projects Workspace or Project Collection, route to its governance reference and named initializer.

For a Code, Document, or Hybrid Project Root, read `project-root-initialization.md`, choose `fresh-empty` or `adopt-existing`, and run the deterministic dry-run/apply/validate chain:

```text
python3 -B scripts/initialize_project_root.py <target> \
  --type <code|document|hybrid> \
  --mode <fresh-empty|adopt-existing>
python3 -B scripts/initialize_project_root.py <target> \
  --type <code|document|hybrid> \
  --mode <fresh-empty|adopt-existing> --apply
python3 -B scripts/validate_project_root.py <target>
```

The initializer preserves existing user material, creates no Git root or worktree, and installs the local collaboration entry. Worktree-first is the default: reading and independent reports need no claim; concurrent code writers use task branches/worktrees and one integrator. Read `worktree-collaboration.md`. The retained helper serves explicitly selected legacy compatibility only. A normal Git-backed Project Root usually keeps its Repository Root under `src/`.

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
