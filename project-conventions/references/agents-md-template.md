# AGENTS.md Template & Example

This document provides a ready-to-use template for `AGENTS.md` and a worked example based on the OB Dim project.

## Design Philosophy

AGENTS.md is an **index**, not a reference manual. It follows three principles:

1. **Index only** — list what exists and where to find details, but do not duplicate the details themselves.
2. **One file, one topic** — each indexed file should focus on a single subject. If a file becomes bloated, split it.
3. **Point to rules, don't inline them** — naming conventions, format rules, and templates live in the skill's `references/`, not in AGENTS.md.

## Template

The managed access block below is for an explicitly initialized or adopted Project Root. Do not paste it into an unrelated legacy project merely because its helper is absent. Missing or failed access infrastructure blocks writes only when the project's current rules require it; actual concurrent-write conflicts remain independent blockers.

Template edits apply to future initialization. Update existing managed blocks and their contract hashes together when the user requests that maintenance.

```markdown
# AGENTS.md

> Agent entry point for this workspace. Read this first.

## Project

[One-line project description]

## Mandatory Rules

<!-- project-conventions:access:start -->
- Coordination policy: `worktree-first`; follow `.project-conventions/ACCESS.md`.
- Read directly for response-only work. New reports use unique exact files and no-clobber creation; no admission is required.
- Code changes use a task branch and linked worktree per concurrent writer. Preserve dirty inputs in the original workspace; a worktree starts from a committed base. Integrate exact validated commits through one editor.
- Do not run enter/check/finish/recover for ordinary work or block on historical claims. Shared build outputs/services require actual isolation.
- Use task-specific records; the integrator updates shared logs/indexes. Reload the policy after an authorized migration.
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
| `.project-conventions/` | Worktree-first policy and compatibility helper | `.project-conventions/ACCESS.md` |

## Source Mapping

| Field | Value |
|---|---|
| Project Root | `.` |
| Repository Root | `src` or `src/<repo-name>` |
| Clone URL / remote | `<credential-free URL or local only>` |
| Default ref | `<branch/ref or unknown>` |
| Managed scope | `whole repository` or `<monorepo subpath>` |

## Quick Reminders

- Ordinary worktree-first work does not depend on helper admission. Diagnose actual file/Git conflicts at their resource; do not block on a historical claim
- Explicit repository/Skill update? Use update-only: fast-forward and validate the requested project or named package, then stop without restructuring, records, or link work
- Significant decision or direction change? Create a unique task record; the integrator assigns canonical sequence numbers
- New review file? Name it `YYYY-MM-DD-<reviewer>-<scope>-HHMMSS.md`, scan `docs/reviews/` for collisions first
- Record meaningful work in separate task files; one integrator updates canonical logs/indexes and allocates sequence numbers. Response-only tasks create no project records
- Read the rules and materials needed for the selected task; reuse current readings, preserve required quality gates, and run checks for the changed behavior. Complete authorized corrections without per-step approval
- Harness-owned memory does not replace project `conversation/` or `memory/`; never write into the harness's system memory directory
- Concurrent work does not add fixed role directories or a permanent `work/lanes/` tree; physical worktrees and distinct output paths provide isolation, not separate chats
- Document/submission projects only: treat canonical certificates and reports as read-only; copy before modifying
- Code in `src/`, artifacts in `release/`, documents in `docs/` — never mix
```

For an Agent Skill Code Project, the generated managed block must additionally identify the exact package root:

```markdown
| Skill Package Root | `src/<skill-name>` |
| Agent consumer | separate installation target; never source |
```

The package entry is `src/<skill-name>/SKILL.md`; do not shorten it to `src/SKILL.md` or move it under `docs/` merely because it is Markdown.

The project-root `conversation/` and `memory/` directories are required for Code, Document, and Hybrid projects. Use separate task records and one integrator for canonical shared files. Separate Agent tasks or Harness conversations do not create isolated filesystems, and another Skill is not required for coordination.

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

## Maintenance

Update this entry when source mappings, active rules or directory navigation change. Keep detailed procedures in their routed source, project history in `conversation/` and cross-task continuity in `memory/`. Retain the project-specific facts needed to act.
