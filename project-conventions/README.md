# project-conventions

Filesystem-governance Skill with strict lifecycle boundaries and deterministic support for a one-checkout Skills Project Collection.

## Lifecycle routing

| Lifecycle | Behavior |
|---|---|
| Full initialization | Clone once to the final shared Repository Root, materialize complete wrappers/control files, verify projections, then optionally install exact Agent consumers |
| Update-only | Safely fast-forward the resolved checkout, validate the named package, and stop |
| Governance maintenance | Audit or migrate only exact authorized paths and mappings |
| Bootstrap-only | Clone, validate, and stop |

Update-only never initializes directories, rewrites indexes, scans siblings, or relinks consumers.

## Shared Skills collection

```text
<collection>/GitHub/project-conventions                  # true source
<collection>/project-conventions/src/project-conventions # stable projection
<collection>/skills                                      # local control project
<agent-root>/project-conventions                         # direct consumer link
```

The member index separates:

- `source`: wrapper-relative entry;
- `repository_root`: collection-relative Git worktree;
- `managed_scope`: repository-relative package.

This prevents a package name from being mistaken for another checkout directory and prevents update requests from triggering collection initialization.

## Deterministic tools

| Tool | Purpose |
|---|---|
| `scripts/initialize_skills_control_project.py` | Dry-run/apply fresh shared collection initializer; creates no Git root, source copy, or Agent link |
| `scripts/update_shared_checkout.py` | Clean fast-forward-only updater for one named package |
| `scripts/validate_package.py` | Offline package shape and portability validator |
| `scripts/inspect_projects_workspace.py` | Read-only Projects Workspace and collection-mapping inspector |
| `scripts/initialize_project_collection.py` | Generic non-shared three-file collection overlay initializer |

The shared initializer creates a complete `skills/` control project, a stable member wrapper, and a relative Unix symlink or Windows junction. Control exports point directly to the true Git package so Agent consumers never form a link chain.

## Validate

The deterministic Python tools support Python 3.11 and newer. CI exercises the Windows junction fallback on Python 3.11 and the native junction API on the latest Python.

From this package:

```bash
python3 -B scripts/validate_package.py .
python3 -B scripts/test_inspect_projects_workspace.py
python3 -B scripts/test_lifecycle_workflows.py
```

From the distribution checkout, also run:

```bash
python3 -B scripts/verify_release.py .
```

The root verifier and package validator have different scopes. Skill discovery and execution are separate runtime states and must be tested in a fresh Agent task after linking.
