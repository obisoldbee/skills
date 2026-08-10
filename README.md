# obisoldbee Skills

Portable Git source for published Skill packages.

## Recommended local layout

Use one checkout per device and keep local project governance outside Git:

```text
<collection>/
├── GitHub/                                  # clone of this repository
│   └── project-conventions/                 # true Skill source
├── project-conventions/                     # stable local Project Root
│   ├── docs/
│   ├── conversation/
│   ├── memory/
│   └── src/project-conventions              # projection to GitHub package
└── skills/                                  # local collection-control project
```

This avoids copied package trees and nested paths such as `project-conventions/src/skills/project-conventions`.

## Fresh initialization

Clone directly into the final shared Repository Root:

```bash
mkdir -p <collection>
git clone https://github.com/obisoldbee/skills.git <collection>/GitHub
python3 -B <collection>/GitHub/scripts/verify_release.py <collection>/GitHub
python3 -B <collection>/GitHub/project-conventions/scripts/validate_package.py \
  <collection>/GitHub/project-conventions
```

Then preview and materialize the local collection:

```bash
python3 -B <collection>/GitHub/project-conventions/scripts/initialize_skills_control_project.py \
  <collection> --distribution-root <collection>/GitHub
python3 -B <collection>/GitHub/project-conventions/scripts/initialize_skills_control_project.py \
  <collection> --distribution-root <collection>/GitHub --apply
```

The initializer creates the routing files, complete `skills/` control project, stable `project-conventions/` wrapper, and member projection. It does not install the Skill into any Agent.

On macOS/Linux the projection is the relative link:

```text
project-conventions/src/project-conventions -> ../../GitHub/project-conventions
```

On Windows it is a directory junction to the final package path.

## Update one Skill

Updating does not rerun initialization or links:

```bash
python3 -B <collection>/GitHub/project-conventions/scripts/update_shared_checkout.py \
  <collection>/GitHub/project-conventions
```

The helper resolves the shared checkout, permits only a clean fast-forward, validates the requested package, reports before/after commits, and stops. Dirty, ahead, detached, diverged, or wrong-remote states fail closed. It does not turn a package update into repository-root publication work.

Git advances the repository as one commit, so bytes in other published packages may also advance. That does not authorize editing, installing, or governing their local wrappers.

## Agent installation

Agent installation is a separate explicit action. Exports are declared in [`config/skill-exports.tsv`](config/skill-exports.tsv), and target candidates are declared in [`config/agent-paths.tsv`](config/agent-paths.tsv).

Scan one exact Agent and Skill first:

```bash
./scripts/link-macos.sh --agent codex --skill project-conventions
```

Apply only after reviewing the source and destination:

```bash
./scripts/link-macos.sh --apply --agent codex --skill project-conventions
```

Windows:

```powershell
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\link-windows.ps1 `
  -Agent codex -Skill project-conventions
powershell.exe -NoProfile -ExecutionPolicy Bypass -File .\scripts\link-windows.ps1 `
  -Apply -Agent codex -Skill project-conventions
```

The repository scripts derive their source from the current checkout, so consumers point directly to `GitHub/project-conventions` when run from the recommended layout. They never create missing target parents or replace conflicts.

## Validation boundaries

Repository root:

```bash
python3 -B scripts/verify_release.py .
```

Named package:

```bash
python3 -B project-conventions/scripts/validate_package.py project-conventions
python3 -B project-conventions/scripts/test_inspect_projects_workspace.py
python3 -B project-conventions/scripts/test_lifecycle_workflows.py
```

`ROOT-MANIFEST.sha256` intentionally lists only root-owned files. Root verification does not validate package contents. A filesystem link also does not prove that an Agent discovered, loaded, or executed a Skill; verify that in a fresh Agent task.

## Repository structure

```text
.
├── .github/workflows/verify.yml
├── AGENTS.md
├── README.md
├── ROOT-MANIFEST.sha256
├── config/
├── scripts/
└── project-conventions/
    ├── SKILL.md
    ├── agents/
    ├── assets/
    ├── references/
    └── scripts/
```
