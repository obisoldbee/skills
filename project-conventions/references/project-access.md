# Project Access — Harness-Neutral Concurrency Contract

Use this contract whenever two Agent tasks may overlap in time. It is part of an initialized Project Root and does not depend on Codex, another Skill, a fixed role list, or Agent-to-Agent messaging.

## What initialization installs

```text
<project-root>/
├── AGENTS.md
└── .project-conventions/
    ├── .gitignore
    ├── ACCESS.md
    ├── project.json
    └── project_access.py
```

The helper is copied into the Project Root so a newly opened Harness can use it even when that Harness has not installed this Skill. Runtime claims are local and ignored by Git. Initialization records one stable runtime backend: an already-existing Git-root project uses one database under the Git common directory so linked worktrees share it; a non-Git or wrapper project uses `.project-conventions/runtime/`. The backend never switches merely because Git is initialized later—changing that boundary is separate governance maintenance performed only with no active claims.

## Mandatory entry sequence

Every cooperating Agent follows this sequence before substantive work:

1. Read the nearest `AGENTS.md`.
2. Run:

   ```bash
   python3 -B .project-conventions/project_access.py status
   ```

3. Classify the actual effects:
   - `read-only`: response-only inspection with no project, Git, cache, database, service, screenshot, report, conversation, memory, or index write;
   - `writer`: any possible side effect in the shared Project Root;
   - `isolated-writer`: code changes inside a clean linked Git worktree, with exact repository-relative `--write-path` values and no canonical shared record.
4. Enter with a Harness/task label:

   ```bash
   python3 -B .project-conventions/project_access.py enter \
     --mode read-only --actor <harness-or-task-label>

   python3 -B .project-conventions/project_access.py enter \
     --mode writer --actor <harness-or-task-label>

   python3 -B .project-conventions/project_access.py enter \
     --mode isolated-writer --actor <harness-or-task-label> \
     --workspace <linked-worktree-path> \
     --write-path src/component-a
   ```

5. Proceed only when the JSON receipt says `status: entered`. Preserve its `session_id` and `token`, then re-read current disk and Git state; pre-entry observations are stale.
6. Before each write batch, verify the claim:

   ```bash
   python3 -B .project-conventions/project_access.py check \
     --session <id> --token <token>
   ```

7. Finish project-owned conversation/memory records while the writer claim is still active, then release it:

   ```bash
   python3 -B .project-conventions/project_access.py finish \
     --session <id> --token <token> --outcome success
   ```

A read-only task that becomes a fixer must finish its reader claim and enter again as a writer. It cannot upgrade in place.

## Conflict rules

- Multiple `read-only` claims may coexist.
- A shared `writer` claim is exclusive against every reader and writer.
- Multiple `isolated-writer` claims may coexist only in different clean linked worktrees and only for non-overlapping logical paths.
- `isolated-writer` may not claim `.git/`, `.project-conventions/`, `conversation/`, `memory/`, `INDEX.md`, `MEMBERS.md`, `controller/`, or `docs/indexes/`. Git common metadata and canonical shared records require the exclusive shared writer.
- A main/shared writer cannot start until all isolated writers finish. Merge/integration therefore happens under one shared writer claim.
- Mutable resources outside Git—lockfiles, generated output trees, databases, ports, devices, services, and binary documents—remain shared effects. Use the exclusive `writer` mode unless an independent boundary is proven.
- A blocked Agent writes nothing, including a “blocked” review or memory entry. It reports the receipt in its response and stops or waits.

These rules are based on actual effects, not roles. Two reviewers can be readers; two reviewers who both fix findings are writers.

## Worktree boundary

The access helper validates an existing linked worktree but does not create one silently. `--workspace` may identify the current Git-root Project Root or a linked worktree of the Project Root's configured nested Repository Root; the helper rejects another repository, a normal directory, a dirty worktree, a linked write-path component, or a worktree using a different Git common directory. Creating a branch and a sibling worktree changes Git and the filesystem, so the exact path/base/branch must be authorized first. An isolated lane may edit/test its declared paths and commit on its admitted branch. Fetch, ref/config changes, worktree add/remove, gc, merge/integration, and other common-Git mutations require the exclusive shared writer. No orchestration Skill is required.

A worktree isolates physical files. It does not resolve logical merge conflicts. The helper therefore also rejects overlapping declared paths and reserves canonical records for the shared writer.

## Crash and recovery

Claims do not expire automatically. A long-running task must never lose its write authority merely because a timer elapsed.

If a task crashed or was abandoned:

1. Inspect `status` and verify outside the old task that it has stopped.
2. Obtain explicit user authorization to clear that exact claim.
3. Dry-run recovery with a meaningful reason:

   ```bash
   python3 -B .project-conventions/project_access.py recover \
     --session <id> --reason "<verified reason>"
   ```

4. Repeat with `--apply` only after reviewing the receipt.

   ```bash
   python3 -B .project-conventions/project_access.py recover \
     --session <id> --reason "<same verified reason>" \
     --apply --token <recovery-token-from-dry-run>
   ```

The apply step is rejected without the matching one-time dry-run token and unchanged claim/reason. Recovery is recorded in the local SQLite history. Never delete the database, edit its rows, or auto-clear a claim. If the database is corrupt or the helper fails, fail closed and remain read-only until the user authorizes repair.

## Guarantee boundary

SQLite transactions make admission atomic for cooperating processes that share the same physical Project Root or Git common directory. This prevents two compliant Harnesses from both believing they own the shared writer slot.

It cannot:

- stop a process that ignores `AGENTS.md` and writes directly;
- coordinate independent clones on different devices;
- replace Git merge/rebase/push conflict handling;
- provide Agent messaging or task dispatch;
- prove that a read-only Agent made no external provider call.

Those facts must be reported separately. A local claim is access evidence, not deployment, publication, or acceptance authority.
