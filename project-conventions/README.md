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
└── scripts/
```

The package includes a read-only Projects Workspace inspector and deterministic tests. It provides execution rules but does not perform work merely by being installed.

## Install

When using this package from the `obisoldbee/skills` repository, follow the repository root README. For clone-only, validate and stop. For an explicitly named complete chain, clone under the current Project Root, or preserve an explicitly authorized clean local-ahead branch before restoring the checkout to fresh remote main; then read the checked-out `SKILL.md` directly, initialize and migrate the named paths in the same task, and defer consumer linking until the final source path exists. A fresh task is needed only when bootstrap stops for later runtime discovery.

You may also copy this directory as a complete unit into a Skill root supported by your agent. Keep `SKILL.md`, `agents/`, `references/`, and `scripts/` together.

## Validate

From this directory:

```bash
python3 -B scripts/test_inspect_projects_workspace.py
python3 -B scripts/test_lifecycle_workflows.py
```

The `-B` flag prevents validation itself from writing `__pycache__` into the publishable package.

Skill discovery and successful test execution are separate states. After installing or linking the package, start a fresh agent session and verify discovery there.

Updating an existing checkout is a separate update-only lifecycle: fast-forward and validate the checkout, then stop. A healthy existing link follows the updated content and must not be recreated.
