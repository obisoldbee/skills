---
name: others-manager
description: Safely inventory, clone, and fast-forward third-party GitHub repositories kept as independent first-level checkouts inside a non-Git pool such as GitHub-others. Use when adding an upstream repository, checking every managed checkout, or updating clean repositories to verified remote heads while preserving provenance, reporting license advisories, and preventing delegated workers from editing governance files.
---

# Others Manager

Manage third-party checkouts through the bundled deterministic CLI. Treat the pool as a container, never as a repository.

## Runtime Boundary

Source classification and execution eligibility are separate:

| Field | Value |
|---|---|
| Source class | `personal-open` |
| Availability | `portable` |
| Allowed devices | `any` |
| Required network | `any` |
| External dependencies | Python 3, Git, an exact non-Git checkout pool, the matching valid `others-manager` wrapper for apply operations, and ordinary GitHub reachability for clone or update operations |
| Credential provider | none for supported public-GitHub operations |
| Verification | Run the package and wrapper validators; use `inventory` for local readback. Static validation and local inventory do not prove live GitHub reachability or a successful mutation. |
| Stop rule | Stop on a missing or invalid wrapper capability, mismatched pool topology, unavailable required tooling, unknown repository identity, or failed GitHub verification. Do not install tools, collect credentials, weaken the gates, or substitute another pool. |

`personal-open` is the public source category; `portable` means no named device or network profile is required. Ordinary internet reachability for a network operation is an external dependency, not a named network profile. Local inventory does not require network access.

## Route the request

1. Resolve the pool explicitly with `--pool`; do not infer it from the current directory.
2. Read the current collection and pool `AGENTS.md` files when they exist.
3. Choose one operation:
   - local inspection: `inventory`
   - all-repository refresh: delegate `inventory` and `plan-update`, then let the controller review and run `apply-update`
   - one new upstream: delegate `plan-clone`, then let the controller review and run `apply-clone`
4. Treat `plan_id` as an integrity checksum, not authorization. A delegated worker's controller handoff authority consists only of the plan path and ID; it may also return the required descriptive evidence, but never a writer token or apply command.
5. The controller independently reviews the plan, including `license.status`, acquires an exclusive writer claim in the matching `others-manager` wrapper, and applies with the expected plan ID plus that private capability.
6. Return the JSON report, blockers, and advisories. A license advisory does not block clone or update; an operational blocker still does.

Read [operations.md](references/operations.md) before any mutating run. When delegating execution to a low-context or Luna worker, use the exact bounded contracts in [luna-task-briefs.md](references/luna-task-briefs.md).

## Hard boundaries

- Require the pool itself to be a real, non-symlink directory with no `.git` entry.
- Treat only real first-level child Git roots as managed repositories. Never follow child symlinks.
- Preserve each child's upstream identity, branch, history, observed license evidence, and local changes.
- Update only by verified `fetch` plus `merge --ff-only`. Never use pull, reset, rebase, stash, clean, force, or push.
- Clone public, enabled, non-archived GitHub repositories even when GitHub cannot verify a license. Record `license.status=unverified` and an advisory instead of treating that uncertainty as a clone or update blocker. Stage inside an owned hidden directory, validate, then rename atomically.
- Before installing, executing, adapting, adopting, redistributing, publishing, or using a repository commercially, surface its license status and terms. If the license is unverified or the intended use is not clearly permitted, stop that use decision for review; do not retroactively block local cloning or ordinary fast-forward maintenance.
- Never install dependencies, initialize submodules, execute cloned code, create worktrees, publish, or alter credentials.
- Never let a delegated worker edit pool-level `AGENTS.md`, `README.md`, reports, scripts, controller files, collection indexes, wrappers, or the public Skill repository.
- Delegated Luna workers may create one plan in the system temporary root, but they have no child-repository write authority. Apply is always a controller action.
- A controller may reconcile management records only after reviewing machine results and only when separately authorized.
- The wrapper capability prevents a cooperating planner from calling apply without the controller's private token. It does not constrain a hostile process running as the same operating-system user; use the host sandbox to restrict a delegated worker to its one plan path.
- Before delegation, the controller must strip `OTHERS_MANAGER_CONTROLLER_TOKEN` from the worker environment and prove the one-path write sandbox is active. If the host cannot provide those controls, do not delegate; run the planner in the controller instead.

## Use the CLI

Run `python3 -B scripts/manage_others.py --help` from this Skill directory. Plan, operation-report, and cleanup-report paths must be distinct direct, explicit normalized files in a system temporary root; the tool refuses to overwrite them. Apply commands pin the opened plan to `--expected-plan-id`, require `--controller-confirm-reviewed-plan` plus an active exclusive wrapper writer session whose token is passed to the access helper over anonymous stdin, reserve both receipts before repository mutation, and hold a cooperative controller operation lock through terminal operation-receipt commit. Reconciliation requires the operation receipt and the independent lock-cleanup receipt.

Use `scripts/validate_package.py` after modifying this Skill. Use `scripts/validate_wrapper.py` from the collection controller when validating a local wrapper/projection.

## Stop conditions

Stop the affected repository and report its exact blocker when state is dirty, detached, ahead, diverged, archived, duplicated, misrouted, operation-in-progress, stale relative to the plan, or otherwise outside the declared write set. Report an unverified license as an advisory, not a repository-management blocker. Continue only with independently safe repositories in an approved all-update plan.
