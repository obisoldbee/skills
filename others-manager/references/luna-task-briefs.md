# Luna Task Briefs

These briefs are deliberately flat and zero-context. Replace every placeholder before delegation. Prefer a Luna model at maximum available reasoning effort. If that model is unavailable, use the current capable model without installing tools or weakening the contract.

Materials:
- Full update planner brief: for one controller-reviewed all-repository plan.
- Clone-one planner brief: for exactly one proposed public GitHub upstream.
- Authoritative operation contract: `references/operations.md` in the same Skill package.

## Full update planner

```text
Objective: inventory POOL and create exactly one reviewed-candidate plan for a controller; do not update any repository.

Exact inputs:
- Skill root: SKILL_ROOT
- Pool: POOL
- New plan path: PLAN_PATH

Controller-verified dispatch preconditions:
- PLAN_PATH is a direct, explicit, normalized, nonexistent file under a real system temporary root
- the worker environment does not contain `OTHERS_MANAGER_CONTROLLER_TOKEN` or any wrapper writer token
- the host filesystem sandbox permits exactly one write: creation of PLAN_PATH
- if any precondition was not verified before dispatch, stop without running a command

Read first:
1. SKILL_ROOT/SKILL.md
2. SKILL_ROOT/references/operations.md
3. POOL/../AGENTS.md and POOL/AGENTS.md when each exists; these reads do not expand the write set

Allowed tools:
- read-only filesystem inspection
- only the two literal `inventory` and `plan-update` commands listed in Procedure below; no other CLI subcommand or shell command
- network access performed only by `plan-update` for the public GitHub metadata API and ls-remote

Allowed writes:
- create PLAN_PATH once
- create no other log, cache, backup, temporary copy, or management file

Forbidden:
- raw mutating git commands
- `apply-update`, `apply-clone`, `git fetch`, `git merge`, or any child-repository mutation; apply is controller-only
- edits to pool-level AGENTS.md, README.md, REPOSITORY-REPORT.md, scripts/, controller/, collection indexes, wrappers, Skill source, or any path outside the exact set above
- pull, reset, rebase, stash, clean, force, push, commit, branch switching, worktrees, dependency installation, submodule initialization, or execution of cloned code
- worker selection, repair, plan editing, or retry of a repository; only the deterministic CLI may decide that a planned repository is independently safe

Procedure:
1. Verify POOL is the exact real non-Git pool. Verify PLAN_PATH is the exact nonexistent direct file under a real system temporary root named in the dispatch preconditions; otherwise stop.
2. Run the exact command `python3 -B SKILL_ROOT/scripts/manage_others.py inventory --pool POOL` and summarize repository count plus clean, dirty, blocked, detached, ahead, and diverged facts available locally.
3. Run the exact command `python3 -B SKILL_ROOT/scripts/manage_others.py plan-update --pool POOL --output PLAN_PATH`.
4. Read the complete plan. Compare its resolved absolute pool, pool fingerprint, and sorted names of real, non-symlink, first-level child Git roots with the inventory. If any differs, stop without editing the plan.
5. Return the exact plan path and plan ID. State that the controller must independently review it and use its private active-writer capability; do not compose, return, or run an apply command.

Failure policy:
- Exit code 2 means the plan contains blockers; it is not permission to apply, edit, or retry differently.
- Never repair or overwrite an unsafe repository.
- If any exact-path or identity check fails, stop all writes.
- Any attempted write outside PLAN_PATH is a global stop.

Return exactly:
- mode: full-update
- pool: exact real path
- plan_id
- repositories_total
- fast_forward_candidates: names and old/planned commits
- already_current: names and commits from the plan
- blocked: name and exact planned reason
- advisories: name and exact planned advisory, including `license_unverified`
- inventory: clean/dirty/other counts
- files_written: PLAN_PATH only
- commands_run: exact commands
- forbidden_actions_confirmed_not_run
- controller_handoff: plan path and plan ID only; explicitly state that no apply command was composed or run

The evidence fields above are descriptive. Only `controller_handoff` carries follow-up authority, and that authority contains only the plan path and ID.
```

## Clone-one planner

```text
Objective: create exactly one admission plan for REPOSITORY_URL and hand it to a controller; do not clone or create a pool child.

Exact inputs:
- Skill root: SKILL_ROOT
- Pool: POOL
- Repository URL: REPOSITORY_URL
- Destination name: DESTINATION_NAME or NONE
- New plan path: PLAN_PATH

Controller-verified dispatch preconditions:
- PLAN_PATH is a direct, explicit, normalized, nonexistent file under a real system temporary root
- the worker environment does not contain `OTHERS_MANAGER_CONTROLLER_TOKEN` or any wrapper writer token
- the host filesystem sandbox permits exactly one write: creation of PLAN_PATH
- if any precondition was not verified before dispatch, stop without running a command

Read first:
1. SKILL_ROOT/SKILL.md
2. SKILL_ROOT/references/operations.md
3. POOL/../AGENTS.md and POOL/AGENTS.md when each exists; these reads do not expand the write set

Allowed tools:
- read-only filesystem inspection
- only the literal `plan-clone` command listed in Procedure below; no other CLI subcommand or shell command
- network access performed only by `plan-clone` for the public GitHub API and ls-remote

Allowed writes:
- create PLAN_PATH once
- create no other log, cache, backup, temporary copy, or management file

Forbidden:
- any other pool child or management-file edit
- raw git clone or other mutating git commands
- `apply-clone`, `apply-update`, `git clone`, or any pool-child mutation; apply is controller-only
- replacement of an existing path, duplicate origin, suppression or fabrication of license evidence, dependency installation, submodule initialization, execution of cloned code, commit, push, worktree, or publication
- worker selection, repair, plan editing, or retry; only the deterministic planner may decide admission evidence

Procedure:
1. Verify POOL is the exact real non-Git pool. Verify PLAN_PATH is the exact nonexistent direct file under a real system temporary root named in the dispatch preconditions, and verify the destination does not exist; otherwise stop.
2. Run the exact command `python3 -B SKILL_ROOT/scripts/manage_others.py plan-clone --pool POOL --url REPOSITORY_URL --output PLAN_PATH`; append `--name DESTINATION_NAME` only when the input is not NONE.
3. Read the complete plan and confirm identity, destination, license status/evidence (`verified` or `unverified`), default branch, remote head, exact resolved pool, and the sorted names of real, non-symlink, first-level child Git roots. An unverified license is an advisory, not a planning blocker.
4. If any field is unexpected, stop without editing the plan.
5. Return the exact plan path and plan ID. State that the controller must independently review it and use its private active-writer capability; do not compose, return, or run an apply command.

Failure policy:
- Never weaken a check or choose a different destination.
- If destination or identity evidence is unexpected, stop and report; the controller will recheck staleness during apply.
- Do not update pool governance or collection records.
- Any attempted write outside PLAN_PATH is a global stop.

Return exactly:
- mode: clone-one
- pool: exact real path
- plan_id
- repository: canonical GitHub identity and URL
- destination
- license: status, SPDX id/top-level path when verified, or the unverified reason
- branch and commit
- result: planned or blocked
- blockers
- files_written: PLAN_PATH only
- commands_run: exact commands
- forbidden_actions_confirmed_not_run
- controller_handoff: plan path and plan ID only; explicitly state that no apply command was composed or run

The evidence fields above are descriptive. Only `controller_handoff` carries follow-up authority, and that authority contains only the plan path and ID.
```

Task:
- Select exactly one brief, replace every uppercase placeholder with a literal value, and delegate that complete brief without relying on conversation context.

Constraints:
- Do not combine the two modes, omit a field, add permissions, or let a worker infer paths, tools, write boundaries, retries, or controller authority.
- If a required literal value is unavailable, stop before delegation and report the missing input instead of inventing it.

Output format:
- The worker returns the exact named fields listed by the selected brief, in Chinese unless the controller explicitly requests English.
- Every fact about a repository includes the plan or inventory evidence that supports it.

Success criteria:
- All placeholders are replaced; exact paths are unambiguous; forbidden actions remain forbidden; blockers are preserved; and controller follow-up is separate from worker execution.
