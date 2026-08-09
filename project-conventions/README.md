# project-conventions

`project-conventions` first separates two operational lifecycles:

- **full initialization** can clone the latest distribution inside an explicitly named current Project Root, initialize one target, migrate named existing roots, and then guide one scoped final-path Skill consumer link;
- **update-only** refreshes one existing checkout, validates it, and stops without restructuring, cataloging, records, or link work.

For initialization and maintenance, it then distinguishes three filesystem-governance layers:

- a **Projects Workspace** that indexes independent local projects;
- a **Project Collection** that groups related Project Roots;
- a **Project Root** that owns one project's source, documents, decisions, and memory.

It is designed for requests such as Skill bootstrap, Skill-version updates, project initialization, directory migration, repository mapping, collection maintenance, document placement, and file naming.

## Package contents

```text
project-conventions/
├── SKILL.md
├── agents/
├── references/
├── scripts/
└── assets/skills-control/
```

The package includes a read-only Projects Workspace inspector, a fail-closed three-file Project Collection initializer, a second deterministic initializer for a complete fresh Skills collection-control Project Root, portable control templates, and deterministic tests. It provides execution rules but does not perform work merely by being installed.

## Install

When using this package from the `obisoldbee/skills` repository, follow the repository root README. For a `project-conventions` wrapper, clone the repository directly as `src/`; the package entry must therefore be `src/project-conventions/SKILL.md`, never `src/skills/project-conventions/SKILL.md`. For clone-only, validate and stop. For an explicitly named complete chain, initialize the target with `scripts/initialize_project_collection.py` and read back its three root files. Move any named existing control Project Root whole. If no control project exists, run `scripts/initialize_skills_control_project.py` after the member checkout reaches its final path; it creates the complete portable `src/config/`, `src/public-repo/`, `src/scripts/`, and `src/tests/` shape and finalizes the indexes. Never replace that step with a hand-written README-and-config skeleton. Defer consumer linking until the final source path exists. A fresh task is needed only when bootstrap stops for later runtime discovery.

You may also copy this directory as a complete unit into a Skill root supported by your agent. Keep `SKILL.md`, `agents/`, `references/`, `scripts/`, and `assets/` together.

## Validate

From this directory:

```bash
python3 -B scripts/test_inspect_projects_workspace.py
python3 -B scripts/test_lifecycle_workflows.py
```

The `-B` flag prevents validation itself from writing `__pycache__` into the publishable package.

Skill discovery and successful test execution are separate states. After installing or linking the package, start a fresh agent session and verify discovery there.

Updating an existing checkout is a separate update-only lifecycle: fast-forward and validate the checkout, then stop. A healthy existing link follows the updated content and must not be recreated.
