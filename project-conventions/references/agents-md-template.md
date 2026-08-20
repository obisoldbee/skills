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

<!-- project-conventions:access:start -->
- Before substantive work, run `python3 -B .project-conventions/project_access.py status`.
- Response-only inspection enters `read-only`; any possible side effect enters `writer`. Do not write until the JSON receipt says `status: entered`.
- Save the returned `session_id` and `token`, re-read current state, run `check` before write batches, and `finish` only after project records are complete.
- A blocked Agent writes nothing. Never auto-clear another claim; recovery needs explicit user authorization, a reason, dry-run, then `--apply`.
- A clean linked Git worktree may use `isolated-writer` with exact non-overlapping `--write-path` values, but canonical records still require the exclusive writer.
<!-- project-conventions:access:end -->

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
| `.project-conventions/` | Harness-neutral status/enter/check/finish/recover entry | `.project-conventions/ACCESS.md` |

## Source Mapping

| Field | Value |
|---|---|
| Project Root | `.` |
| Repository Root | `src` or `src/<repo-name>` |
| Clone URL / remote | `<credential-free URL or local only>` |
| Default ref | `<branch/ref or unknown>` |
| Managed scope | `whole repository` or `<monorepo subpath>` |

## Quick Reminders

- Missing or failed local access helper? Remain read-only; do not guess that no other Agent is active
- Explicit repository/Skill update? Use update-only: fast-forward and validate the requested project or named package, then stop without restructuring, records, or link work
- Significant decision or direction change? Only the active exclusive writer scans and creates the next `conversation/NN-topic.md`
- New review file? Name it `YYYY-MM-DD-<reviewer>-<scope>-HHMMSS.md`, scan `docs/reviews/` for collisions first
- Done working? The active exclusive writer updates canonical conversation, memory, and indexes before releasing its claim
- Harness-owned memory does not replace project `conversation/` or `memory/`; never write into the harness's system memory directory
- Concurrent work does not add fixed role directories or a permanent `work/lanes/` tree; the project-local access receipt, not a role or separate chat, controls admission
- Document/submission projects only: treat canonical certificates and reports as read-only; copy before modifying
- Code in `src/`, artifacts in `release/`, documents in `docs/` — never mix
```

For an Agent Skill Code Project, the generated managed block must additionally identify the exact package root:

```markdown
| Skill Package Root | `src/<skill-name>` |
| Agent consumer | separate installation target; never source |
```

The package entry is `src/<skill-name>/SKILL.md`; do not shorten it to `src/SKILL.md` or move it under `docs/` merely because it is Markdown.

The project-root `conversation/` and `memory/` directories are required for Code, Document, and Hybrid projects. Direct writes require a valid exclusive project-local writer claim. Separate Agent tasks or Harness conversations do not create isolated filesystems, and another Skill is not required to discover active claims.

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

For a device- or network-bound Skill, add a concise routing summary and keep the executable contract in the source package's `SKILL.md`:

```markdown
## Runtime Boundary

| Field | Value |
|---|---|
| Availability | `device-bound`, `network-bound`, or `device-and-network-bound` |
| Allowed devices | Stable non-secret labels, `any`, or `unknown` |
| Required network | Stable non-secret profile label, `any`, or `unknown` |
| Verification | Safe check or routed Skill section |
| Stop rule | On mismatch or unknown, do not execute or change the environment |
```

Device alternatives are OR, network-profile alternatives are OR, and constrained device plus network axes are AND. Do not put credentials, SSIDs, private keys, tokens, cookies, or secret endpoints in this table.

## Worked Example (OB Dim Project)

```markdown
# AGENTS.md

> Agent entry point for the OB Dim workspace. Read this first.

## Project

OB Dim — Windows 系统托盘小程序，在 Work/Away 模式间一键切换显示器息屏超时（C# WinForms .NET 8，单文件 EXE 192KB）。

## Mandatory Rules

When working in this workspace, follow its initialized project-local access entry:
- Run `.project-conventions/project_access.py status`, then obtain the appropriate claim before substantive work
- Centralize all documents under `docs/` (specs/plans/reviews/research)
- Review files: `YYYY-MM-DD-<reviewer>-<scope>-HHMMSS.md` under `docs/reviews/`
- Conversation files: `NN-kebab-topic.md` under `conversation/`; only the exclusive writer allocates the next number
- Project memory: only the exclusive writer updates `memory/YYYY-MM-DD.md` and `memory/MEMORY.md`

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
| `.project-conventions/` | Harness-neutral Agent admission | `ACCESS.md` + `project_access.py` |

## Quick Reminders

- Before work, run project-local `status` and `enter`; without an entered receipt, do not write
- Explicit repository/Skill update? Fast-forward and validate only; do not turn it into a directory migration
- Significant decision or direction change? The exclusive writer scans and creates the next `conversation/NN-topic.md`
- New review file? Name it `YYYY-MM-DD-<reviewer>-<scope>-HHMMSS.md`, scan `docs/reviews/` for collisions first
- Done working? Update project memory and conversation before finishing the exclusive writer claim
- Concurrent work? Readers may coexist; shared writers are exclusive; isolated Git writers need distinct worktrees and disjoint paths
- Harness-owned memory is reserved for the tool and never substitutes for project `conversation/` or `memory/`
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
