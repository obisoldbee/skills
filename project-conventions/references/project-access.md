# Project Access — Harness-Neutral Concurrency Contract

Use this contract in a Project Root whose current AGENTS.md adopts the local helper. A missing helper in an unrelated legacy project does not authorize adoption or block its original task. This is cooperative coordination for every Harness, not a Codex-only filesystem lock.

The task is to admit independent work while excluding actual write collisions. Before entering, bind the input Project Root from the current AGENTS.md and the exact output files or task-owned directory from the user's requested deliverable. If a new output name was not specified, choose a unique task name within the authorized location. Keep inputs read-only unless editing them is part of the task. Do not broaden a directory claim to avoid deciding the output boundary.

Completion means the authorized outputs were written and checked, required record batches were finished, and every claim owned by this task was released. Reply in the user's language with the resulting paths, verification and any remaining conflict. A response-only task returns its findings directly without inventing an output file; runtime JSON field names remain unchanged.

## Choose the scope

Check the local status protocol_version first. The commands below require version 3. If the copied helper is version 1 or 2, follow its current contract and use the reviewed upgrade workflow only for an authorized named target; retrying version-3 flags cannot repair an old copy.

Every cooperating Agent uses the same local helper. Select the smallest scope covering the actual task effects:

| Task | Admission | Concurrency |
|---|---|---|
| Response-only reading | read-only | Coexists with every writer; does not freeze inputs |
| One report or bounded file edits | scoped-writer + --write-file | Different files in one directory can run together |
| A task-owned output subtree | scoped-writer + --write-dir | Reserves the directory and everything below it |
| Code implementation | isolated-writer in a linked worktree | Separate branches/worktrees; same logical filenames allowed |
| Short workspace maintenance or integration | writer | Excludes physically overlapping writers; disjoint external worktrees remain usable |

```bash
python3 -B .project-conventions/project_access.py status
python3 -B .project-conventions/project_access.py enter --mode read-only --actor <label>
python3 -B .project-conventions/project_access.py enter --mode scoped-writer --actor reviewer-a --write-file docs/reviews/a.md
python3 -B .project-conventions/project_access.py enter --mode scoped-writer --actor reviewer-b --write-file docs/reviews/b.md
python3 -B .project-conventions/project_access.py enter --mode scoped-writer --actor researcher --write-dir docs/research/task-c
python3 -B .project-conventions/project_access.py enter --mode isolated-writer --actor <label> --workspace <linked-worktree> --write-path <repo-relative-path>
python3 -B .project-conventions/project_access.py enter --mode writer --actor <maintenance-label>
python3 -B .project-conventions/project_access.py check --session <id> --token <token>
python3 -B .project-conventions/project_access.py finish --session <id> --token <token> --outcome <success|failed|aborted>
```

In the examples, a.md and b.md can be written concurrently. A second claim for a.md, or a directory claim for docs/reviews, conflicts with a.md. Paths are project-relative, literal, normalized and contain no wildcards; use forward slashes, including on Windows. Repeat --write-file and/or --write-dir to cover every output. File claims do not reserve the parent: creating missing parent directories with mkdir(exist_ok=True) is allowed, but renaming/deleting the parent or changing siblings is not. File versus directory is explicit even before the target exists. Case/Unicode aliases are compared conservatively; symlink/junction paths and hard-linked file targets are rejected. Within a claimed directory, do not follow links or mutate reserved Git, protocol or Harness metadata.

Save the returned session_id and token privately. Re-read current state after entering; run check before each write batch and finish afterward. New reports use no-clobber creation (for example Python open(path, 'x')); an existing filename is a conflict, not permission to overwrite. On collision, select a new authorized name and obtain a claim covering it before writing. A denied write claim does not prohibit read-only entry or a fresh nonconflicting claim. A reader becoming an editor obtains a writing claim first; never silently upgrade its reader claim.

Read-only admission does not freeze files. For a consistent review, use a fixed commit/snapshot or compare input hashes before and after and reread changed inputs. The helper coordinates cooperating Harnesses; it is not a filesystem lock and does not intercept writes from Agents that ignore the protocol.

For code, prefer an existing clean linked Git worktree on a task-specific branch. Only one writer uses a physical worktree; different worktrees may change the same logical path and must resolve merge conflicts later. The helper validates but never creates worktrees. An isolated writer may edit/test its declared paths and commit on its admitted branch. Canonical records are updated in their owning Project Root under a short scoped claim after releasing the worktree claim. A canonical writer protects its physical workspace only. Repository-wide ref/config changes, pruning/removing worktrees, or other common-state maintenance use `enter --mode writer --registry-maintenance --actor <label>` for that short operation. It explicitly excludes all other writers in the shared registry; never infer repository-wide ownership from an ordinary workspace claim. Use a short canonical writer for integration, and preserve peer branches. Databases, ports, devices, services and build outputs need actual isolation; a file claim cannot reserve an external service. Declare shared filesystem outputs explicitly; services and devices need their own resource-specific coordination. Do not reserve an entire project for a build output directory. Build against stable input files or a fixed integrated snapshot; an output reservation does not freeze inputs.

Record significant decisions and substantive work only when they add useful continuity; update indexes only when their represented facts change. Claim exact record files for the short write batch, reread and merge concurrent additions before saving, then release. For allocating conversation/NN-topic.md, briefly claim conversation/ so numbering is unique. Do not hold a record claim throughout research. Response-only tasks create no project records; the helper's own admission/release metadata remains part of this adopted protocol. Reuse existing exact work authorization rather than asking at every check or finish step.


## Runtime and worktree boundary

Initialization copies AGENTS.md's managed block, .project-conventions/ACCESS.md, project.json and project_access.py into the target. Updating the Skill alone cannot update these copies.

The backend is fixed at adoption: an existing Git root (or explicitly configured nested repository) can use git-common-dir; ordinary non-Git projects use project-local; shared Skills wrappers use their configured collection-control registry. Later Git initialization does not switch backends. Use the same owning helper/backend for tasks sharing resources. An unconfigured non-Git root does not become Git-backed merely because its src/ children contain repositories. Independent reports need no Git initialization or worktree.

An isolated-writer must use a real clean linked worktree, an attached branch and the same Git common directory as the configured backend. The helper rejects a normal directory, another repository, active Git operations and linked write-path components. Different clean linked worktrees may declare overlapping logical paths. They still need merge review; Git common refs/config and external services remain shared. An isolated-writer cannot claim canonical conversation/, memory/, INDEX.md, MEMBERS.md, controller/ or docs/indexes/: release it, then claim the actual record in its owning Project Root. Scoped writers cannot claim Git, protocol or Harness metadata. An actor label is diagnostic, never a lock boundary.

A file claim covers only that file. A directory claim covers its subtree, even when it does not exist yet. Claims compare normalized physical paths, not just relative spelling or parent folders. An isolated-writer reserves its whole physical worktree against another writer there, including a scoped writer, while its declared paths remain its permitted task scope. A writer reserves its physical workspace subtree, not the entire registry. External sibling worktrees remain independent. A worktree nested physically inside that workspace still overlaps: place independent worktrees outside the reserved subtree.

## Entry and denied claims

Read the current AGENTS.md, run status, select the task's actual effects, then enter. Only a status: entered receipt permits writes in the declared scope. Store its session_id/token privately; use check before each write batch and finish after completion. Tokens authorize release of that exact claim and must not appear in reports. A blocked Agent writes nothing under that denied claim. It may still enter read-only, choose an independently authorized nonconflicting output and enter afresh, or wait for the actual conflict. Other Agents being active is not enough reason to wait.

If a reader becomes an editor, finish its reader claim and obtain a write claim. Do not acquire additional overlapping writer claims while holding one: release, then reacquire the complete write set. This avoids hold-and-wait deadlocks. For a sequence-number allocation, briefly reserve conversation/ and rescan after admission; for a daily log, claim only memory/YYYY-MM-DD.md and reread before saving.

Read-only tasks produce no report, screenshot, cache, Git, database, service or record writes. The helper itself writes local admission metadata. If even coordination writes are explicitly forbidden, do not enter or silently mutate the registry; follow the live project's read-only fallback and report the limitation. A failing configured helper means no task writes, but does not imply that the physical files cannot be read. Admission is concurrency permission within existing task authorization; it does not authorize expanding the task.

## Upgrade an already adopted project

This is scoped governance maintenance, not reinitialization or global installation. Only upgrade a named authorized project:

```bash
python3 -B scripts/upgrade_project_access.py <project-root>
python3 -B scripts/upgrade_project_access.py <project-root> --apply --plan-sha256 <reviewed-plan-sha256>
```

The dry-run verifies current contract hashes without executing the old helper or changing the registry. Review the exact four-file plan. Apply rechecks the plan, acquires the existing helper's registry-wide maintenance writer, backs up the original files, replaces the helper/ACCESS/managed AGENTS block and updates their hashes. Only recognized obsolete generated record/worktree lines outside the block are migrated; custom surrounding text is preserved. Active conflicting claims stop the upgrade without clearing them. Protocol-1 and protocol-2 databases are migrated transactionally to protocol 3, preserving sessions, token hashes, history and recovery plans. The configuration schema stays at version 1. Validate and release the maintenance claim; retain the backup and receipt.

All copies using one registry must be upgraded before resuming their work. An older helper will reject the protocol-3 registry, not silently continue with older conflict rules. The upgrader can admit the next explicitly named copy using its trusted current maintenance implementation against that version-3 registry. Do not scan or update unnamed projects automatically. Before registry activation, a failed upgrade restores only bytes still owned by that attempt, preserving concurrent replacements. After activation, a release/receipt failure retains the valid version-3 control files and private recovery material rather than restoring an incompatible older helper. The error identifies the backup and remaining repair boundary.

## Bounded command lifetime

Prefer the supervised command entry for a foreground build or file-generation batch:

```bash
python3 -B .project-conventions/project_access.py run --actor builder --write-dir out/task-a -- python3 build.py
```

Repeat `--write-file`/`--write-dir` for every actual output, including logs and caches. The command runs in the owning Project Root, without a shell, and the parent holds the scoped claim until it exits. Successful completion, a nonzero exit and process-start failure all release the claim; nonzero status is propagated. Do not daemonize children or leave background writers after the command exits. This is cooperative scope declaration, not a sandbox.

Do not retain a whole-project writer across research, model calls, quota waits or an entire conversation. For code work, choose an independent linked worktree and its own outputs. For a large shared Chromium build, use a dedicated builder with stable integrated inputs and bounded output ownership; avoid duplicating the entire build merely to simulate isolation.

A forcibly killed supervisor or machine crash can still leave a database claim. No timeout is treated as proof that its child stopped: inspect the process/resource before recovery. A stale claim in another disjoint workspace no longer blocks this work. Automatic lease expiry/fencing is not implemented and must not be advertised as filesystem enforcement.

## Crash and recovery

Claims never expire automatically. Verify that the old task has stopped, obtain authorization to clear that exact claim, then run:

```bash
python3 -B .project-conventions/project_access.py recover --session <id> --reason "<verified reason>"
python3 -B .project-conventions/project_access.py recover --session <id> --reason "<same verified reason>" --apply --token <recovery-token>
```

Recovery requires the matching one-time dry-run token and unchanged claim/reason; it is recorded in SQLite history. Never delete the database, edit claim rows or clear somebody's claim merely because it is old.

## Guarantee and verification

SQLite transactions make claims atomic for cooperating processes sharing the same registry. This is not enforcement against arbitrary writes: check validates claim/path/Git identity, not every changed byte or build side effect. Inside directory scopes, the Agent must preserve unrelated content, avoid links and keep generated effects within scope. Independent devices/clones, external databases/services and Agents ignoring the helper require separate coordination.

Validate admission behavior with real concurrent helper processes and temporary Git worktrees. Package/static tests are not proof that a specific Harness obeys AGENTS.md or that a Windows host has been tested. Report those boundaries honestly.
