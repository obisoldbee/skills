# Shared Repository Skills Collection

Use this profile only when one explicitly named distribution repository is the physical source for one or more Skill member wrappers in the same Project Collection.

## Authority model

The shared Repository Root is collection infrastructure. It owns Git history and published package bytes. It does not own member documents, conversation, memory, local collection membership, or Agent installation state.

| Fact | Canonical location |
|---|---|
| Git history and package bytes | `<collection>/GitHub` |
| Project documents and continuity | `<collection>/<member>/` |
| Cross-Harness reader/writer admission | `<collection>/<member>/.project-conventions/` and `<collection>/skills/.project-conventions/` |
| Member and Repository Root mapping | `<collection>/skills/docs/indexes/members.md` |
| Agent export allowlist | `<collection>/skills/src/config/skill-exports.tsv` |
| Runtime consumer | Existing Agent-specific Skill root |

Never make the collection root a Git repository. Never copy a package into the control project. Never treat the member projection as a second source.

The control project's `src/` is a real directory containing exactly four independent management projections:

```text
skills/src/AGENTS.md -> ../../GitHub/AGENTS.md
skills/src/README.md -> ../../GitHub/README.md
skills/src/config    -> ../../GitHub/config
skills/src/scripts   -> ../../GitHub/scripts
```

On Unix all four are exact relative symlinks. On Windows `config` and `scripts` are directory junctions, while `AGENTS.md` and `README.md` are file symbolic links. If file-symlink creation is unavailable, initialization fails and rolls back; it never falls back to copies or hard links. `skills/src/skills -> ../../GitHub`, package projections under `skills/src/`, and real repository files under the control `src/` are invalid.

## Multiple owned distributions

The public `GitHub` checkout is the standard distribution initialized by this package, not a claim that the collection can contain no other Git Repository Root. A collection may map packages from multiple explicitly named owned distributions, for example a public root and a separately provisioned private root, when all of the following hold:

- every root is a real exact Git worktree, not a link or container;
- every member row names its collection-relative `repository_root`, remote identity, and `managed_scope`;
- each normalized remote identity has only one checkout in the collection;
- private visibility is read back before the first push or private export;
- public-root management projections continue to target only the public distribution;
- initialization, update, publication, and consumer links stay repository- and package-scoped.

The standard public initializer never creates or clones an additional private root. Add it only through an explicitly scoped governance-maintenance or bootstrap workflow.

A third-party checkout pool is not a shared Repository Root. Its container has no `.git/`; each cloned child is a separate upstream-owned worktree and is not exportable merely because it exists.

## Canonical mapping

The member index must keep these fields separate:

```text
path=project-conventions
source=src/project-conventions
repository_root=GitHub
vcs=git
remote=obisoldbee/skills
managed_scope=project-conventions/
```

- `path` identifies the stable Project Root wrapper.
- `source` identifies the wrapper entry used by local project tools.
- `repository_root` is collection-relative and identifies the real Git worktree.
- `managed_scope` is repository-relative and identifies the package.
- `source` must resolve exactly to `<collection>/<repository_root>/<managed_scope>`.

If `repository_root` or `managed_scope` is absent, a linked `source` is not authorized by this profile and the inspector must report it.

## Fresh bootstrap

For a new or explicitly cleared collection, the allowed initial write order is:

1. Create the exact collection directory when missing.
2. Clone the approved remote to `<collection>/GitHub`.
3. Verify Git identity, branch, upstream, clean status, and `HEAD == origin/main`.
4. Validate repository-root manifest and named package separately.
5. Run `initialize_skills_control_project.py` dry-run.
6. Run the same initializer with `--apply`.
7. Read back root files, control project, its four root-management projections, wrapper, both project-local access entries, member projection, index, and direct export.
8. Rerun the initializer and require `already_initialized`.
9. Stop before consumer links unless exact Agent targets were also authorized.

The clone path is final from the start. Do not clone beneath a temporary member `src/` and then ask the initializer to discover or move it.

The generated control and member Project Roots each contain a Harness-neutral access helper, and every member helper stores claims in the collection-control runtime. Readers coexist with writers. Scoped report/record claims compare physical paths, so distinct wrapper outputs may run together. The exclusive writer remains collection-wide for shared Git index/HEAD maintenance; do not use a scoped report claim to mutate Git through a source projection. A member wrapper with a missing/wrong `coordination_root` is invalid and must fail closed. Worktree admission requires an explicitly configured Git-common backend; this collection-control binding does not silently change to one. No dual manual lock sequence, Agent messaging, or orchestration Skill is required.

## Git safety gate

Before clone into an absent destination, verify only the exact destination and parent. For bootstrap into an existing checkout or update-only, require:

- real directory, not symlink/junction;
- `git rev-parse --show-toplevel` equals that path;
- expected normalized remote;
- attached expected branch;
- expected tracked upstream;
- no tracked or untracked changes;
- no merge, rebase, cherry-pick, bisect, or lock marker;
- local ahead count zero;
- fast-forward reachability when behind.

Stop on a real-directory snapshot, wrong repository, dirty/ahead/diverged/detached checkout, or target collision. Do not delete, merge, reset, rebase, stash, or silently rename it.

For authorized package or repository-root maintenance, verify the exact worktree identity, remote, branch, upstream, status, and managed scope, then preserve unrelated changes. The clean/ahead-zero refresh gate is not a ban on maintaining an already modified worktree. An active Git operation, conflicting edit, or unclear ownership still blocks the affected write. Device refresh follows its own trusted root-level gate; maintenance never implies permission to fetch or move refs.

## Member projection

On macOS/Linux, the raw relative link is:

```text
project-conventions/src/project-conventions -> ../../GitHub/project-conventions
```

On Windows, create a directory junction from the same member source entry to the absolute final package target. Windows junctions are final-path artifacts; do not create them before the collection reaches its final location.

Creation is valid only when the destination is absent. A real directory, wrong link, dangling link, or wrong junction is a conflict and must be preserved until the user authorizes a specific backup-and-replace operation.

Verification requires platform-exact link type and exact target. Unix additionally requires the raw relative target derived from the final paths (for the standard layout, `../../GitHub/project-conventions`); an absolute symlink is invalid even when it resolves to the same package. Windows requires a directory junction, not a directory symlink. The presence of `SKILL.md` alone is insufficient because an accidental copied directory can expose the same file.

## Update-only

The named package's `update_shared_checkout.py` is the update entry. After fetch, it freezes the upstream commit, extracts only the named package into an isolated temporary tree, runs that candidate's package validator, then rechecks local Git state and fast-forwards only the exact validated commit. A linked package, linked validator, or failed candidate validation leaves local `HEAD` and the worktree unchanged; the fetch may still change remote-tracking refs. It may not change wrapper files, projections, indexes, records, exports, or consumer links.

Because Git updates a repository commit, other published package bytes in that checkout can also advance. This does not authorize work on their wrappers or consumers. Report the named package validation and stop.

## Consumer links

Consumers link directly to the true package source:

```text
<agent-skill-root>/project-conventions -> <collection>/GitHub/project-conventions
```

Do not create a link chain through the member projection. Do not create missing Agent parents. For existing conflicts, record the raw link target or preserve the full real directory in a collision-free backup before any explicitly authorized replacement.

The current repository `link-windows.ps1` supports scoped Agent scan/apply with the NT directory-handle helper. Combined `-SyncDevice -Apply` is unavailable; separately authorized checkout update and scoped installation are supported. Do not infer consumer-creation support from the initializer's Windows junction support, or bypass the guard with another command. See `lifecycle-workflows.md` for the Windows implementation and validation boundary.

## Existing-layout migration

Migration from a copied or member-local package is governance maintenance, not update-only.

1. Run the Projects Workspace inspector before the path/index change.
2. Snapshot the old package tree, candidate `GitHub` path, member wrapper, index/export files, and existing consumers.
3. If `GitHub` is absent, clone into a collision-free staging path, validate it, then atomically place it at `GitHub`.
4. If `GitHub` is a non-Git snapshot, preserve it under a collision-free backup name before cloning; never clone over it.
5. Compare the old canonical package with the verified shared package. A match supports migration but never authorizes deletion.
6. Preserve the old real package under a collision-free rollback path, then create the projection at the now-free source entry.
7. Update wrapper routing, canonical member index, root mirror, and direct export.
8. Run package validation, control tests, projection readback, and the Projects Workspace inspector again.
9. Retarget explicitly authorized Agent consumers directly to the true source; preserve every conflict.

Do not touch other collection members or their Git roots. A shared distribution repository for public packages does not make private/local member projects part of that remote.

## Device portability

The repository and index contain only relative collection mappings. Device-specific absolute paths exist only in live filesystem link metadata and local receipts. On another device, clone to that device's user-selected collection, rerun the deterministic initializer, and separately install that device's Agent links.

Do not sync symlink/junction metadata as though it were portable configuration. Recreate and read it back on each device.

Source portability and runtime eligibility are separate. An environment-bound Skill must declare non-secret device and network labels plus a verification and stop rule. If both axes are constrained, both must match. A healthy checkout, projection, or Agent consumer link does not prove that the current device or network can execute the Skill.
