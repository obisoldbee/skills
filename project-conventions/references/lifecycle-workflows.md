# Lifecycle Workflows

Use this reference before the filesystem-governance references whenever a request mentions initialization, clone, download, install, sync, pull, or update.

## Decision table

| Observed request | Select | Do not do |
|---|---|---|
| “从零初始化这个目录，并把仓库和 Skill 配好” | Full initialization | Do not omit repository or consumer readback |
| “先把最新版 Skill 克隆下来，我稍后另开会话初始化 X” | Full initialization, bootstrap stage only | Do not inspect or initialize X; do not inspect old workspaces |
| “更新这个 Skill / 拉取最新版代码” and the checkout exists | Update-only | Do not restructure, catalog, record, or relink |
| “整理 / 迁移 / 审计这个现有目录” | Governance maintenance | Do not clone or update unrelated repositories |

The verb `clone` does not by itself authorize governance of the clone's parent, siblings, or eventual target. The presence of an `AGENTS.md` in a parent directory does not expand the user's stated scope.

## Full initialization lifecycle

### Stage A — bootstrap the Skill

Use this stage only when the required Skill is not already discoverable in the current runtime.

1. Confirm the exact distribution clone URL, stable checkout path, one Skill name, and one Agent consumer root.
2. Refuse a provider `/tree/<ref>/<subpath>` page as a clone URL. Clone the repository URL and address the Skill by its managed subpath.
3. If the checkout path is absent, clone into that exact path. If it already exists, do not clone over it; classify a requested refresh as update-only.
4. Validate the package and distribution manifest before link work.
5. Scan only the selected consumer root and selected Skill. Never use an unscoped all-Agent or all-Skill scan as the default.
6. If the consumer root is missing, report that exact path and provide a focused creation command. Creating it is a separate write and must be approved.
7. Show the exact link or junction dry run. Apply only after explicit approval, preserve conflicts, and require a nonzero result for missing parents or conflicts.
8. Read the created link or junction back from disk.
9. Stop and request a fresh Agent task. A disk link is not proof that the current session loaded the Skill.

The distribution checkout is a tool source, not a Projects Workspace, Project Collection, or Project Root target unless the user separately says to govern that checkout itself.

### Stage B — initialize the target

Run this stage in a fresh task after discovery, or immediately if the Skill was already loaded before the task began.

1. Inspect only the exact target and the minimum parent state needed to detect a collision.
2. Select Projects Workspace, Project Collection, or Project Root mode from current evidence.
3. State the exact create/edit/clone map. Existing files, repositories, or non-empty collisions require a focused stop or explicit migration approval.
4. Create the selected layer's required directories and entry files.
5. If an approved Git repository belongs to a Project Root, clone it under the mapped `src/` Repository Root. For a monorepo, record the repository clone URL plus managed subpath.
6. Populate only current facts. Do not copy paths, indexes, remotes, or membership facts from another device.
7. Run the routed structural validator and Git readback.
8. Report what was created, the verified Repository Root and commit, and any actions not taken.

Do not automatically initialize an entire collection merely because one member Skill was cloned. Do not treat the distribution repository as a mirror of a device's local Project Collection.

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
