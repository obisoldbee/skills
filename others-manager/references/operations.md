# Operations Contract

## Ownership model

The pool is a non-Git directory. Every real first-level repository child owns its own `.git`, upstream, branch, worktree, and license. Pool governance and public Skill publication are controller responsibilities, not worker responsibilities.

The bundled CLI separates delegated planning from controller mutation. A delegated worker may read the Skill, pool, Git metadata, and its plan, and may create only the exact new plan file named by the controller. The plan and report must be direct files in a real system temporary root. A worker never runs apply.

After review, the controller may run apply. It must hold an active exclusive writer claim in the exact sibling `others-manager` wrapper. The session ID is supplied explicitly; its 48-hex token is supplied only through the controller process environment variable `OTHERS_MANAGER_CONTROLLER_TOKEN`, passed to the access helper over anonymous stdin, and must never enter a Luna brief, plan, report, process argument, shell history, or project record. Apply verifies the wrapper-to-package projection and wrapper-to-pool topology before reserving distinct operation and lock-cleanup receipts as `in_progress`, then holds a temporary operation lock bound to the pool through terminal operation-receipt commit. It may write only child Git state selected by the reviewed plan, or one owned clone staging directory and final child.

`plan_id` is an accidental-tamper checksum. It is not a signature, approval, identity, or operating-system permission boundary. The controller passes the exact reviewed ID as `--expected-plan-id`; apply opens the plan without following symlinks, fixes its inode while reading, verifies the checksum, and requires the opened ID to match. The private active-writer token is the cooperating-Agent apply capability.

This capability, fingerprints, and the temporary lock coordinate rule-following processes. They cannot prevent a hostile process with the same operating-system account from directly editing files or replacing this program. Before Luna is dispatched, the controller must strip `OTHERS_MANAGER_CONTROLLER_TOKEN` from the worker environment and enforce a filesystem sandbox whose only writable path is the exact new plan file. If either control cannot be verified, do not delegate; the controller runs the planner itself.

The CLI does not write pool governance records. Common protected paths include pool-level `AGENTS.md`, `README.md`, `REPOSITORY-REPORT.md`, `scripts/`, and `controller/`, plus collection indexes, wrapper projects, and the public Skill repository.

## Inventory

```bash
python3 -B scripts/manage_others.py inventory --pool /absolute/path/to/GitHub-others
```

This is local and read-only. It reports each real first-level Git repository and operational blockers such as dirty state, detached HEAD, a non-GitHub origin, missing origin tracking, or operation markers. A missing recognizable top-level license is reported separately as `license_unverified`; it does not block cloning, inventory, or ordinary fast-forward maintenance.

## Full update

Create a frozen plan with remote-head evidence:

```bash
python3 -B scripts/manage_others.py plan-update \
  --pool /absolute/path/to/GitHub-others \
  --output /private/tmp/others-manager-update-plan.json
```

Review the plan, especially `repositories[*].blockers`, `head`, `remote_head`, and the exact repository set. Then apply it:

First enter the exact wrapper as an exclusive writer, keep its token private in the controller process environment, and copy the reviewed `plan_id` literally. Do not ask the planner to compose or run this command.

```bash
python3 -B scripts/manage_others.py apply-update \
  --pool /absolute/path/to/GitHub-others \
  --plan /private/tmp/others-manager-update-plan.json \
  --output /private/tmp/others-manager-update-report.json \
  --cleanup-output /private/tmp/others-manager-update-cleanup.json \
  --expected-plan-id REVIEWED_64_HEX_PLAN_ID \
  --controller-project /absolute/path/to/others-manager \
  --controller-session ACTIVE_WRITER_SESSION_ID \
  --controller-confirm-reviewed-plan
```

Apply revalidates the plan checksum, reviewed ID, controller capability, pool/repository fingerprints, exact set, local state, GitHub public/archive/default-branch snapshot, license-status snapshot, and remote head. Git uses a trusted absolute binary, a minimal environment, and a strict local-config allowlist. Apply fetches to `FETCH_HEAD`, requires both local `HEAD` and the old origin tracking ref to be ancestors of the candidate, records candidate top-level license evidence when present, updates origin tracking with compare-old semantics, then merges with `--ff-only`. An upstream force-push is blocked rather than adopted. Apply compares the complete final identity snapshot. The terminal operation receipt is committed while the lock is held; the separate cleanup receipt then persists `released`, `not_acquired`, or `retained_requires_review`. Reconciliation is incomplete until both receipts are read. A stale or unsafe repository is skipped while other independently safe planned repositories may continue. Exit code `2` means operational blockers, cleanup blockers, or partial completion; a license advisory alone does not make the operation partial. Exit code `1` means a fatal contract failure.

## Add one repository

Create a plan:

```bash
python3 -B scripts/manage_others.py plan-clone \
  --pool /absolute/path/to/GitHub-others \
  --url https://github.com/OWNER/REPOSITORY \
  --output /private/tmp/others-manager-clone-plan.json
```

An optional `--name` may select a different safe first-level destination name. The planner uses the public GitHub API and `git ls-remote` to require a public, enabled, non-archived repository, a default branch, and a stable remote head. It records a verified SPDX/top-level-file snapshot when GitHub exposes one; otherwise it records `license.status=unverified` with a reason and continues. It also rejects an existing destination or duplicate GitHub origin.

Apply the reviewed plan:

Acquire and privately supply the same wrapper writer capability described above, and use the exact reviewed plan ID.

```bash
python3 -B scripts/manage_others.py apply-clone \
  --pool /absolute/path/to/GitHub-others \
  --plan /private/tmp/others-manager-clone-plan.json \
  --output /private/tmp/others-manager-clone-report.json \
  --cleanup-output /private/tmp/others-manager-clone-cleanup.json \
  --expected-plan-id REVIEWED_64_HEX_PLAN_ID \
  --controller-project /absolute/path/to/others-manager \
  --controller-session ACTIVE_WRITER_SESSION_ID \
  --controller-confirm-reviewed-plan
```

Apply repeats the external checks and requires the same pool fingerprint, complete entry set, repository set, license-status snapshot, and remote head. It clones with no checkout and no submodule initialization in a minimal Git environment, validates origin, branch, upstream, head, and config, and validates the license blob when the plan contains verified evidence. An unverified license produces an advisory and does not weaken the Git or filesystem gates. Apply performs the initial checkout inside owned staging, rechecks GitHub, then commits with a platform no-replace atomic rename. Unsupported platforms fail closed. Cleanup after the commit point can only add an operational warning; it cannot deny that the clone already exists.

Clone/update permission and use permission are separate. Before installing, executing, adapting, adopting, redistributing, publishing, or using a repository commercially, present the recorded license status and applicable terms. If the intended use is not clearly permitted, pause that use decision for review. Do not describe a public checkout as unrestricted merely because it was cloneable.

## Controller reconciliation

After a successful or partial operation, the controller compares both JSON receipts with current disk state. Updating a pool report, repository registry, collection index, export allowlist, wrapper record, commit, or publication is a separate write and authorization. Never infer it from successful Git child updates.

## Failure handling

- Do not repair dirty or divergent children automatically.
- Do not delete or replace an existing destination.
- Do not retry with a weaker command or bypass identity, state, destination, or stale-plan checks. Preserve license evidence and advisories without converting them back into clone/update blockers.
- A worker that prepared a plan must stop before apply and hand the exact plan path to the controller.
- The worker's handoff authority contains only the plan path and ID. Its descriptive evidence report may include the bounded fields required by the brief, but never an executable apply command or writer session token.
- Do not expose credential-bearing remote URLs in reports.
- If an owned staging directory cannot be proven safe to remove, leave it in place and report it for manual review.
- Never call cloned repository scripts, package managers, build tools, tests, hooks, or submodule commands as part of management.
