# AGENTS.md Template & Example

This document provides a ready-to-use template for `AGENTS.md` and a worked example based on the OB Dim project.

## Design Philosophy

AGENTS.md is an **index**, not a reference manual. It follows three principles:

1. **Index only** — list what exists and where to find details, but do not duplicate the details themselves.
2. **One file, one topic** — each indexed file should focus on a single subject. If a file becomes bloated, split it.
3. **Point to rules, don't inline them** — naming conventions, format rules, and templates live in the skill's `references/`, not in AGENTS.md.

## Template

```markdown
# AGENTS.md

> Agent entry point for this workspace. Read this first.

## Project

[One-line project description]

## Mandatory Rules

When working in this workspace, follow the `project-conventions` skill:
- Skill location: `<skills-dir>/project-conventions/SKILL.md` (path varies by agent tool)
- [3-5 key rules, one line each]

## Directory Index

| Path | Content | Details |
|---|---|---|
| `README.md` | Project overview (for humans) | — |
| `conversation/` | Discussion & decision records (`NN-topic.md`) | skill: references/conversation-format.md |
| `docs/specs/` | Design documents | — |
| `docs/plans/` | Implementation plans | — |
| `docs/reviews/` | Review documents (`YYYY-MM-DD-<reviewer>-<scope>-HHMMSS.md`) | skill: references/review-naming.md |
| `docs/research/` | Research documents | — |
| `src/` | Source code | — |
| `release/` | Build artifacts (on demand) | — |
| `memory/` | Agent-maintained project memory | — |

## Source Mapping

| Field | Value |
|---|---|
| Project Root | `.` |
| Repository Root | `src` or `src/<repo-name>` |
| Clone URL / remote | `<credential-free URL or local only>` |
| Default ref | `<branch/ref or unknown>` |
| Managed scope | `whole repository` or `<monorepo subpath>` |

## Quick Reminders

- Explicit repository/Skill update? Use update-only: fast-forward and validate the checkout, then stop without restructuring, records, or link work
- Significant decision or direction change? Create a `conversation/NN-topic.md` file (scan for next number)
- New review file? Name it `YYYY-MM-DD-<reviewer>-<scope>-HHMMSS.md`, scan `docs/reviews/` for collisions first
- Done working? Append a note to `memory/YYYY-MM-DD.md`
- Never write to the agent platform's system memory directory — use `memory/` instead
- Document/submission projects only: treat canonical certificates and reports as read-only; copy before modifying
- Code in `src/`, artifacts in `release/`, documents in `docs/` — never mix
```

The Source Mapping is required for every Git-backed Project Root. Keep one mapping per Project Root. If the source is a subdirectory of a larger GitHub repository, record the repository's clone URL and put the subtree in `Managed scope`; never use a `/tree/...` page as the clone URL.

For the explicit shared-repository Project Collection profile, the member wrapper uses this extended mapping instead:

```markdown
| Stable source entry | `src/<package-name>` |
| Repository Root | `../GitHub` |
| Clone URL / remote | `https://github.com/<owner>/<repository>.git` |
| Default ref | `main` |
| Managed scope | `<package-name>/` |
```

The member index records the same Repository Root collection-relatively as `GitHub`. The stable source entry must be a verified symlink/junction projection to that managed scope. Read `shared-repository.md`; an arbitrary linked `src/` path is not sufficient authority.

## Worked Example (OB Dim Project)

```markdown
# AGENTS.md

> Agent entry point for the OB Dim workspace. Read this first.

## Project

OB Dim — Windows 系统托盘小程序，在 Work/Away 模式间一键切换显示器息屏超时（C# WinForms .NET 8，单文件 EXE 192KB）。

## Mandatory Rules

When working in this workspace, follow the `project-conventions` skill:
- Skill location: `<skills-dir>/project-conventions/SKILL.md`
- Centralize all documents under `docs/` (specs/plans/reviews/research)
- Review files: `YYYY-MM-DD-<reviewer>-<scope>-HHMMSS.md` under `docs/reviews/`
- Conversation files: `NN-kebab-topic.md` under `conversation/` (next available number)
- After substantive work, append to `memory/YYYY-MM-DD.md` (NOT the agent platform's system memory)

## Directory Index

| Path | Content | Details |
|---|---|---|
| `README.md` | Project overview, tech stack, quick start (for humans) | — |
| `conversation/` | 6 discussion records (brainstorming, decisions, implementation, verification, branding) | skill: references/conversation-format.md |
| `docs/specs/` | Design spec (11 sections) | `2026-07-19-screen-timeout-toggle-design.md` |
| `docs/plans/` | Implementation plan (12 TDD tasks) | `2026-07-19-screen-timeout-toggle.md` |
| `docs/reviews/` | 2 review documents (takeover reviews) | skill: references/review-naming.md |
| `docs/research/` | Research documents (currently empty) | — |
| `docs/migrations/2026-07-20-directory-migration.md` | Directory restructuring record | One-time migration doc |
| `src/` | Source code (C# .NET 8, 15 .cs files, .git with tag v1.0.0) | — |
| `release/` | Compiled EXE (192KB, framework-dependent) | `ScreenTimeoutToggle.exe` |
| `memory/` | Agent-maintained daily logs + long-term memory | `MEMORY.md` + `YYYY-MM-DD.md` |

## Quick Reminders

- Explicit repository/Skill update? Fast-forward and validate only; do not turn it into a directory migration
- Significant decision or direction change? Create a `conversation/NN-topic.md` (currently max is `05-`)
- New review file? Name it `YYYY-MM-DD-<reviewer>-<scope>-HHMMSS.md`, scan `docs/reviews/` for collisions first
- Done working? Append a note to `memory/YYYY-MM-DD.md`
- Never write to the agent platform's system memory — that's reserved for the tool itself, use `memory/` instead
- Code goes in `src/`, artifacts in `release/`, never in `docs/`
- Source namespace is `ScreenTimeoutToggle` (legacy, not renamed to `OBDim` — intentional)
```

## What to Avoid

### Don't: Inline full rules

```markdown
## Review Naming Rule

Review files must follow this pattern: YYYY-MM-DD-<reviewer>-<scope>-HHMMSS.md
where reviewer is one of: architect, engineer, qa, pm, security, takeover, user
and scope is one of: code, design, pr, release, spec, full
and HHMMSS is 24-hour time with second precision...
[50 more lines of detailed rules]
```

**Why bad**: This duplicates the skill's content. When the skill updates, this file becomes stale.

### Do: Reference the rule

```markdown
## Quick Reminders

- New review file? Name it `YYYY-MM-DD-<reviewer>-<scope>-HHMMSS.md` (see skill: references/review-naming.md for full vocabulary)
```

**Why good**: One line. Points to the authoritative source. Never goes stale.

### Don't: Write project history in AGENTS.md

```markdown
## Project History

This project started on 2026-07-19 when the user wanted a screen timeout toggle tool.
The brainstorming process involved 8 decision points... [20 more lines]
```

**Why bad**: History belongs in `conversation/` and `memory/`. AGENTS.md should be current state, not past events.

### Don't: Duplicate README.md content

```markdown
## Tech Stack

| Item | Choice |
|---|---|
| Language | C# WinForms .NET 8 |
| Testing | xUnit + Moq |
... [full tech stack table]
```

**Why bad**: This is README.md's job. AGENTS.md links to README.md for human-oriented details.

## Maintenance

- **When to update AGENTS.md**: directory structure changes, new top-level files/dirs added, key conventions change.
- **When NOT to update**: individual file content changes (update the file itself, not the index), daily work logs (go to `memory/`), conversation records (go to `conversation/`).
- **Keep it under ~60 lines**. If it grows beyond that, you're probably inlining details that belong elsewhere.
