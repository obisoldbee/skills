# project-conventions

`project-conventions` helps agents distinguish and maintain three filesystem-governance layers:

- a **Projects Workspace** that indexes independent local projects;
- a **Project Collection** that groups related Project Roots;
- a **Project Root** that owns one project's source, documents, decisions, and memory.

It is designed for requests such as project initialization, directory migration, repository mapping, collection maintenance, document placement, and file naming.

## Package contents

```text
project-conventions/
├── SKILL.md
├── agents/
├── references/
└── scripts/
```

The package includes a read-only Projects Workspace inspector and deterministic tests. It does not initialize Git, move projects, create links, or publish anything by itself.

## Install

When using this package from the `obisoldbee/skills` repository, follow the repository root README and run the link script in scan mode before applying a link.

You may also copy this directory as a complete unit into a Skill root supported by your agent. Keep `SKILL.md`, `agents/`, `references/`, and `scripts/` together.

## Validate

From this directory:

```bash
python3 -B scripts/test_inspect_projects_workspace.py
```

The `-B` flag prevents validation itself from writing `__pycache__` into the publishable package.

Skill discovery and successful test execution are separate states. After installing or linking the package, start a fresh agent session and verify discovery there.

