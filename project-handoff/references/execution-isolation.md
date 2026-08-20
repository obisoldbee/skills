# Execution Isolation

Use this contract whenever lanes may overlap in time, use different harnesses, write project files, run mutable tests, or change from review to repair. Isolation is selected per lane from its side effects; it is never allocated from a fixed list of roles.

## Contents

1. Lane execution contract
2. Selection rules
3. Git worktree boundary
4. Codex visible tasks
5. External harnesses
6. Review-to-repair transition
7. Project records
8. Integration and cleanup

## 1. Lane execution contract

Every executable lane declares:

| Field | Meaning |
|---|---|
| `harness` | Actual executor surface, such as `codex`, `codex-cli`, `workbuddy`, `qoder`, or `trae`; not a job title |
| `file_access` | `read_only` or `write`; this is independent from mutable devices, ports, databases, and services |
| `workspace_mode` | `shared_checkout`, `worktree`, or `non_git` |
| `worktree_source` | Existing Repository Root used to provision a linked worktree; otherwise `null` |
| `repository_root` | The lane's actual `git rev-parse --show-toplevel`; pending for a not-yet-created managed worktree, or `null` for non-Git |
| `workspace_path` | Exact physical execution directory inside `repository_root`; pending with a managed worktree |
| `base_revision` | Full commit for Git, or a verified content-state digest for non-Git; a dependency lane may stay pending until its upstream gate closes |
| `read_paths` | Inputs relative to `workspace_path`; absolute and parent-escaping forms are invalid |
| `write_paths` | Exact authorized outputs; empty for `read_only` |
| `mutable_resources` | Databases, ports, devices, services, lockfiles, generated trees, and build state not isolated by path alone |

File access and workspace placement are separate decisions:

- `file_access=read_only`: no project-file writes. Response-only findings are valid output; separately declared mutable resources may still require serialization.
- `file_access=write`: exact `write_paths` or mutable resources are required.
- `workspace_mode=shared_checkout`: one existing Git checkout; use for one writer or read-only lanes against one frozen base.
- `workspace_mode=worktree`: one temporary linked Git worktree. It protects the live checkout from immediate overwrite; it does not resolve logical merge conflicts.
- `workspace_mode=non_git`: a non-Git or binary-document workspace. Dependencies, not a fake Git mode, establish its single-writer window.

## 2. Selection rules

| Situation | Required decision |
|---|---|
| One writer | `file_access=write` with `shared_checkout` is sufficient when no overlapping lane uses the same repository |
| Multiple reviewers on one frozen base | `file_access=read_only`; they may share one checkout and return responses owned by the Controller |
| Unordered writers in one Git repository | `file_access=write` and one `worktree` per lane, even when declared writes are disjoint |
| Same logical file, lockfile, or generated tree | Serialize or narrow scope; worktrees do not waive the conflict |
| One writer while reviewers read its target | Order the reviewer after the writer or freeze a separate base |
| Non-Git or binary document | Multiple readers are allowed; order every writer through dependencies so only one writes that workspace at a time |
| Sequential harness switching | Reuse one checkout only after the prior harness stopped and current status, hashes, and artifacts were read back |

Tests, builds, and reviews are not automatically read-only. A command that updates snapshots, coverage, dependencies, caches inside the project, a database, or a service must declare those effects.

## 3. Git worktree boundary

A worktree is a temporary execution resource of the same Git repository, not a second repository and not a permanent project directory.

Before dispatch:

1. Verify `worktree_source` and the frozen base revision.
2. Preserve current dirty work. Do not silently start a worktree from the default branch when the requested work depends on uncommitted state. Create an authorized checkpoint first, or serialize the work in the existing checkout; a content digest does not transport dirty Git changes into another worktree.
3. Give every unordered writer a distinct physical worktree and branch or tool-managed equivalent.
4. Keep the main checkout under the integration owner. Workers do not merge, rebase, reset, or delete another lane's worktree.
5. After creation, record the linked worktree's own `repository_root` and `workspace_path`. Before any writer in a same-source concurrency wave becomes `running`, record every writer's actual paths, rerun plan validation across the wave, and require each clean Git readback.

Different worktrees may safely preserve concurrent edits on disk, but two lanes changing the same logical path remain an integration conflict and must be serialized by this Skill.

## 4. Codex visible tasks

For Git-backed visible write lanes, request the live `create_thread` worktree environment when another writer may overlap; otherwise use the shared checkout serially. For a shared read-only review, local execution is allowed only against one frozen base with no writer mutating that checkout.

The normalized visible-task receipt must record requested and actual environment, workspace path, repository root, base revision, and verification source. A queued worktree is registerable but not execution-ready. If readback cannot prove the environment, keep the lane `created_unconfirmed`; do not authorize writes.

`fork_thread` without an explicit worktree is same-directory execution. Do not treat conversation isolation as filesystem isolation. `handoff_thread` may move an existing task and Git state, but any read-only-to-write transition still requires a new validated plan.

## 5. External harnesses

WorkBuddy, Qoder, Trae, and other external harnesses do not become Codex tasks and must never receive invented task ids or create-thread receipts.

- Use a `portable-handoff` route and include the exact harness, workspace, repository root, base revision, write set, validation, and stop rule.
- Producing the handoff leaves the lane in `standby`. It becomes `running` only after an actual external receipt or current disk/Git readback proves the named workspace and base.
- Normalize that evidence and run `scripts/validate_external_environment_receipt.py <receipt.json> --plan <plan.json>`. A passed portable route alone is never the launch receipt.
- For concurrent external writers, provision distinct worktrees before delivering their handoffs.
- For sequential switching, rebuild each handoff from current HEAD, status, changed files, and validation. A historical prompt is not current authority.
- Cross-harness communication remains Controller-mediated unless the harnesses share a separately verified coordination service. A Markdown plan is not a cross-process lock.

A verified external non-Git launch uses this exact receipt shape (Git lanes replace the mode-specific evidence with the Git shape in `thread-dispatch.md`):

~~~yaml
run_id: <plan run id>
lane_id: <plan lane id>
harness: workbuddy
status: verified
surface: portable_handoff
file_access: write
workspace_mode: non_git
worktree_source: null
repository_root: null
workspace_path: <absolute execution directory>
base_revision: <snapshot:sha256 digest>
environment_verified: true
evidence_source: controller_disk_readback
environment_evidence:
  verified_by: snapshot_readback
  worktree_source: null
  repository_root: null
  workspace_path: <same absolute execution directory>
  base_revision: <same snapshot:sha256 digest>
  content_state_verified: true
failure: null
~~~

A launch failure uses the same top-level lane identity with `status: failed`, `environment_verified: false`, null environment paths/base/evidence, and a non-empty `failure`; it is valid evidence but never execution-ready.

## 6. Review-to-repair transition

“Also fix it” changes a reviewer into a writer. Before sending that instruction:

1. stop or reconcile the current review lane;
2. declare its new write paths and mutable resources;
3. re-evaluate conflicts against every active lane;
4. select `file_access=write` plus a worktree, or an explicit dependency-ordered shared window;
5. validate the revised plan and environment receipt.

Never continue a shared `read_only` task as a writer merely because the model and conversation remain suitable.

## 7. Project records

Harness-owned hidden directories remain opaque to project governance. Project-owned `conversation/`, `memory/`, indexes, controller records, and shared status files are canonical mutable resources.

- Workers return lane-local responses or write uniquely allocated artifacts.
- Workers do not scan for the next sequential conversation number or append to one shared daily memory file concurrently.
- Only the integration owner writes the canonical conversation, memory, index, and final review synthesis after reconciling lane results.
- A lane may write its own uniquely named evidence file only when that exact path is declared in the plan.

## 8. Integration and cleanup

The integration owner verifies each lane's actual workspace, base, changed paths, commit or artifact receipt, and validation before adoption. Merge or apply lanes one at a time, rerun full validation, then write canonical project records.

Remove temporary worktrees only after their changes are integrated or explicitly abandoned and rollback evidence is preserved. A deleted worktree, completed conversation, or plausible report is not integration evidence.
