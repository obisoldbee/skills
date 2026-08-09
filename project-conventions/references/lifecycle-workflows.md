# Lifecycle Workflows

Use this reference before the filesystem-governance references whenever a request mentions initialization, clone, download, install, sync, pull, or update.

## Decision table

| Observed request | Select | Do not do |
|---|---|---|
| “从零初始化这个目录，并把仓库和 Skill 配好” | Full initialization | Do not omit repository or consumer readback |
| “先把最新版 Skill 克隆到当前 A，再初始化 B，并把明确列出的 C/D 迁进去” | Full initialization, named bootstrap-and-migrate chain | Do not invent another checkout root, inspect unnamed siblings, or link before moving the source |
| “先把最新版 Skill 克隆下来，到这里停止；我稍后另开会话初始化 X” | Full initialization, bootstrap stage only | Do not inspect or initialize X; do not inspect old workspaces or consumers |
| “更新这个 Skill / 拉取最新版代码” and the checkout exists | Update-only | Do not restructure, catalog, record, or relink |
| “整理 / 迁移 / 审计这个现有目录” | Governance maintenance | Do not clone or update unrelated repositories |

The verb `clone` does not by itself authorize governance of the clone's parent, siblings, or eventual target. Conversely, an end-to-end request that names the current bootstrap root, final target, and migration sources authorizes inspection of those exact paths; do not erase that scope with a blanket sibling prohibition. The presence of an `AGENTS.md` in a parent directory never expands the named scope.

## Full initialization lifecycle

### Stage A — bootstrap the Skill

Use this stage when the required Skill is not already available from an approved source.

1. Confirm the exact distribution clone URL, current bootstrap Project Root, checkout path inside it, and Skill package subpath. Do not substitute a conventional global directory for a path the user supplied.
2. Refuse a provider `/tree/<ref>/<subpath>` page as a clone URL. Clone the repository URL and address the Skill by its managed subpath.
3. For a governed Project Root, default the checkout to its mapped `src/<repository-name>/` Repository Root. If the exact checkout path is absent, clone there. If it exists, verify its identity and apply the update-only Git safety gates to that checkout; do not clone over it or reduce the overall full-initialization request to update-only.
4. Validate both the distribution manifest and requested Skill package.
5. If the user requested clone/download only, report the checkout and validation and stop. Do not inspect the target, siblings, consumer roots, or links.
6. For an explicitly requested end-to-end chain, read the checked-out Skill and routed references directly and continue. Runtime auto-discovery is not required merely to follow an explicitly named local `SKILL.md`.
7. If the bootstrap Project Root or checkout will move later in this lifecycle, do not create a link or junction yet. A link to the temporary source path would become stale.

A fresh task is required after bootstrap-only when later runtime discovery is desired. It is not an automatic stop inside an explicit same-task bootstrap-and-migrate chain.

The distribution checkout remains a Repository Root/tool source. The enclosing current directory may separately be a named Project Root and migration source.

### Stage B — initialize the target

Run this stage in a fresh task after bootstrap-only discovery, immediately when the Skill was already loaded, or in the same task after direct-loading the checked-out Skill for an explicit full chain.

1. Inspect the exact target, the minimum parent state needed to detect collisions, and only the explicitly named migration sources.
2. Select Projects Workspace, Project Collection, or Project Root mode from current evidence.
3. Before moving existing directories, read `migration-guide.md`; snapshot contents including hidden files, Git roots/status/remotes/stashes, active process/current-directory risks, and existing links.
4. State the exact create/edit/clone/move map. A user request that already names every source and destination is explicit migration approval. Ask again only when an observed collision, Git risk, or workspace lock requires a different map; do not present unrelated keep/archive/delete choices.
5. Create the selected target layer's entry files and non-colliding directories. Reserve names that incoming directories will occupy.
6. If the running task is rooted inside a source to move, change execution to the minimum safe parent before the move. If the host keeps the workspace locked, stop only for a reopen-at-parent handoff and resume from the recorded move map. Do not emulate an atomic directory move with copy-and-delete.
7. Move every approved source directory as a whole. Preserve hidden entries, Git metadata, worktree state, and file counts.
8. Update current source mappings, active references, collection indexes, and generated views from observed disk state. Keep historical narrative and migration before/after records unchanged.
9. After the final Skill source path exists, scan one named Agent consumer and one named Skill. Show the exact final-path link or junction, apply only with explicit approval, and read it back from disk.
10. Verify old paths are absent, final paths exist, repository identity/status is unchanged, package/manifest/tests pass, indexes match disk, and any applied link resolves to the final package.

Do not automatically initialize an entire collection merely because one member Skill was cloned. Do not treat the distribution repository as a mirror of a device's local Project Collection.

### Worked Windows path map: bootstrap source is migrated

Use this relationship when these are the paths the user named; do not replace them with another storage convention:

```powershell
$ProjectParent = Join-Path $env:USERPROFILE 'Documents\project'
$BootstrapRoot = Join-Path $ProjectParent 'project-conventions'
$Checkout = Join-Path $BootstrapRoot 'src\skills'
$LegacyControl = Join-Path $ProjectParent 'skills'
$TargetCollection = Join-Path $ProjectParent 'obisoldbee-skills'

git clone https://github.com/obisoldbee/skills.git "$Checkout"
python -B (Join-Path $Checkout 'scripts\verify_release.py') $Checkout
```

After validation, read `$Checkout\project-conventions\SKILL.md` directly. Initialize `$TargetCollection` as a Project Collection without creating paths that collide with the two incoming members. Then present and approve this exact move map:

```text
<project-parent>\skills               -> <project-parent>\obisoldbee-skills\skills
<project-parent>\project-conventions  -> <project-parent>\obisoldbee-skills\project-conventions
```

The final package source is:

```text
<project-parent>\obisoldbee-skills\project-conventions\src\skills\project-conventions
```

Only after both moves and final-path validation may a consumer junction be proposed for that package. If the checkout already exists at `$Checkout`, verify and safely fast-forward that exact checkout instead of cloning a duplicate, then continue the named full chain.

## Update-only workflow

Update-only is complete when the exact existing checkout is safely refreshed and validated.

1. Resolve the path with `git -C <path> rev-parse --show-toplevel`; stop if it is not the intended checkout.
2. Capture the current commit, branch/ref, upstream, remote URL, and porcelain status.
3. Fetch the tracked remote.
4. Compute ahead/behind state. Continue only when the worktree is clean, the branch is not detached, local ahead is zero, and the remote can be reached by fast-forward.
5. Use fast-forward-only pull or merge. Never use automatic rebase, reset, stash, conflict resolution, or commit transplantation.
6. Capture the resulting commit and rerun the package/manifest validation supplied by that checkout.
7. Stop and report the exact before/after commits and validation result.

Forbidden side effects in update-only:

- choosing or changing a governance layer;
- creating or revising wrapper `AGENTS.md`, `README.md`, indexes, `docs/`, `conversation/`, or `memory/`;
- scanning sibling projects, historical workspaces, every Agent root, or every exported Skill;
- creating, repairing, replacing, or reapplying links or junctions;
- initializing another target or migrating local commits.

If the user wants any forbidden side effect, finish the update-only task first and handle the new scope as a separate request.
