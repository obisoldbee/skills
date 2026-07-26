---
name: project-conventions
description: 'Standardize project workspace layout, file naming, and multi-agent coordination. Supports code, document, hybrid, and fork-workflow projects (clone upstream to src/<repo-name>/, configure origin/upstream remotes, submit PRs). This skill should be used when starting a project, creating documents (specs/plans/reviews/research/reports), recording decisions, writing project memory, managing versioned submissions, forking a repo, or unsure where a file goes. Triggers: "create project structure", "where should I put this file", "fork a repo", "submit a PR", "项目结构", "文件放哪", "fork别人项目", "提PR", "记录决策". Does not cover code logic, tech stack selection, or WorkBuddy system memory (.workbuddy/memory/ is reserved). Outputs: directory structure, AGENTS.md template, naming rules, and fork setup guidance.'
agent_created: true
---

# Project Conventions

## Overview

Standard project workspace layout: which directory holds which content, how files are named, how multi-agent artifacts are coordinated. Keeps projects navigable, artifacts discoverable, and prevents file-name collisions.

## When to Use

- Starting a new project or initializing a workspace (code, document, or hybrid)
- Creating any project document, review, or submission
- Recording a conversation, decision, or implementation log
- Unsure where a file goes or how to name it
- Managing versioned submissions or multi-agent coordination

## Project Types

Three project types, each with different required directories:

| Type | Primary deliverable | Required dirs |
|---|---|---|
| **Code** | Source code / software | `AGENTS.md`, `README.md`, `docs/`, `src/`, `conversation/`, `memory/` |
| **Document** | Documents, forms, submissions, certifications | `AGENTS.md`, `INDEX.md`, `docs/`, `提交记录/` |
| **Hybrid** | Both code and document components | Code dirs + document dirs |

Determine type by primary deliverable: source code → Code; documents/forms → Document; both → Hybrid. When unsure, start minimal and add directories as needed. See `references/directory-layout.md` for the full project-type matrix (what's required/optional per type).

## Fork Workflow (Code variant)

When the project is a fork of an upstream repo (contribute back via PR), apply all Code-type rules plus these fork-specific conventions:

- **Directory**: `src/<repo-name>/` is the forked repo with its own `.git/`. `src/` is a container that may hold multiple forks. Never clone a fork directly into `src/` — always use a named subdirectory.
- **Remotes**: `origin` → your fork (push here), `upstream` → original repo (fetch only, never push). Setup: `git clone <upstream-url> src/<repo-name>` → `cd src/<repo-name> && gh repo fork --remote` (auto-renames `origin` to `upstream` and adds your fork as new `origin`).
- **Daily flow**: `git fetch upstream && git rebase upstream/main` before starting work → branch → commit → `git push origin <branch>` → `gh pr create --base main --head <branch>`.
- **Boundary**: SOP docs (specs/plans/reviews) stay outside `src/`; code changes stay inside `src/<repo-name>/`. Never push the SOP wrapper to the upstream repo.
- **AGENTS.md**: must include a "Fork Workflow" section documenting the remote setup and PR flow for the current workspace.

See `references/fork-workflow.md` for full setup commands (3 methods), PR workflow, upstream sync, multi-repo, and troubleshooting.

## Standard Directory Layout

```
project-root/
├── AGENTS.md                # Required (all). Agent entry point (auto-loaded by WorkBuddy)
├── README.md                # Required (all). Project overview (for humans)
├── INDEX.md                 # Required (document). Version index — one line per version
├── conversation/            # Required (code/hybrid). Optional (document). Decision records (NN-*.md)
├── docs/                    # Required (all). All formal documents, centralized
│   ├── specs/  plans/  reviews/  research/  reports/  decisions/  archive/  migrations/
├── design/                  # On demand. Design assets (prototypes, SVGs, HTML mockups)
├── src/                     # Required (code/hybrid). Source code (may have its own .git/)
├── release/                 # On demand (code/hybrid). Final distributable artifacts only
├── 提交记录/ (submissions/) # Required (document). Versioned submission records (vNNN/)
├── memory/                  # Required (code/hybrid). Optional (document). Agent-maintained memory
│   ├── YYYY-MM-DD.md        # Daily work log (append-only)
│   └── MEMORY.md            # Curated long-term project notes
└── .workbuddy/              # WorkBuddy system directory — NOT managed by this skill
```

### Key Principles

1. **Centralize documents under `docs/`** — never scatter spec/plan/review files at project root or inside `src/`.
2. **One file, one topic** — if a file exceeds ~500 lines or covers unrelated topics, split it.
3. **AGENTS.md is an index, not a dump** — keep it lean; point to where rules live, don't duplicate.
4. **Never write to `.workbuddy/memory/`** — reserved for WorkBuddy system. Use `memory/` at project root.
5. **Source files are read-only** — never modify originals (certificates, reports). Copy to `上传包/` and modify the copy.
6. **Archive, don't delete** — superseded docs go to `docs/archive/YYYY-MM-DD-<topic>/`.
7. **Adapt to project type** — don't force code-project conventions onto document projects.
8. **Before migrating, read `references/migration-guide.md`** — covers safety checks, atomic Git moves, reference sync, verification.

## Core Rules

### AGENTS.md

Agent entry point, auto-loaded by WorkBuddy. Keep under ~60 lines. Four sections: Project (1 line), Mandatory Rules (reference this skill + 3-5 key rules), Directory Index (table), Quick Reminders (5-7 bullets). Must NOT contain full rule specs, templates, or project history. Use `AGENTS.md` (not `CODEBUDDY.md`) for cross-tool portability. See `references/agents-md-template.md` for template.

### Review Naming

```
YYYY-MM-DD-<reviewer>-<scope>-HHMMSS.md
```

- `reviewer`: architect, engineer, qa, pm, security, takeover, user
- `scope`: code, design, pr, release, spec, full
- Before writing: scan `docs/reviews/` for collisions; append `-1`, `-2` suffix if needed
- Migrated historical files with unknown time: use `000000` placeholder
- Document projects may use date-precision (no HHMMSS) for single-user reviews

See `references/review-naming.md` for full vocabulary, collision handling, and migration procedures.

### Memory (Dual-Track)

| Location | Purpose | Who writes |
|---|---|---|
| `.workbuddy/memory/` | WorkBuddy system memory (auto-injected) | WorkBuddy itself — do NOT write here |
| `memory/` | Agent-maintained project memory | Any agent doing substantive work |

Write to `memory/YYYY-MM-DD.md` after substantive work (append-only). Update `memory/MEMORY.md` for long-term facts. Skip for trivial exchanges. Document projects may use versioned records instead of daily logs.

### Versioned Records (Document Projects)

For submissions/certifications, use `提交记录/` with `INDEX.md` (one line per version) + `vNNN/RECORD.md` (details) + `vNNN/上传包/` (physical copies) + `vNNN/提交凭证/` (screenshots/receipts). Source files are read-only; copies go in `上传包/`. See `references/versioned-records.md` for template and upload workflow.

### Conversation Logs

Files under `conversation/` record agent-user collaboration: proposals, modifications, rationale, decisions. Naming: `NN-kebab-topic.md` (scan for next available number). Required sections: Metadata, Agent Proposals, User Modifications, Rationale, Final Decision. See `references/conversation-format.md` for template.

**When to create a conversation file**: one file per significant decision, topic change, or phase — not every interaction. If a discussion leads to a concrete decision or direction change, record it. Routine Q&A or lookups do not need a conversation file. For code/hybrid projects, `conversation/` is required; for document projects, it's optional.

## Concurrency Rule (Multi-Agent Safety)

When multiple agents work in the same project, prevent file-write conflicts:

| File type | Conflict risk | Safe strategy |
|---|---|---|
| `conversation/NN-*.md` | Two agents pick same number | Scan before creating; if collision, append `-1` suffix (e.g., `06-topic-1.md`) |
| `docs/reviews/*.md` | Two agents start same-second review | HHMMSS + collision scan + `-1` suffix (see Review Naming above) |
| `memory/YYYY-MM-DD.md` | Concurrent appends | **Append-only** — safe; both appends are valid chronological entries |
| `memory/MEMORY.md` | Concurrent overwrites | **Read-modify-write**: re-read before writing; if content changed since last read, merge instead of overwrite |
| `AGENTS.md` | Concurrent overwrites | **Single writer**: only the lead/initializing agent updates AGENTS.md. Working agents propose changes via message, not direct edit |
| `提交记录/INDEX.md` | Concurrent version-row additions | **Read-modify-write**: re-read before adding a row; append new row at end |
| `提交记录/vNNN/` | Two agents pick same version number | Scan before creating; if collision, use next available number |

**General rule**: append-only files (`memory/YYYY-MM-DD.md`) are safe for concurrent writes. Read-modify-write files (`MEMORY.md`, `INDEX.md`, `AGENTS.md`) require re-reading before writing and merging conflicts. New-file creation (`conversation/`, `reviews/`, `vNNN/`) requires scanning for collisions before writing.

## References

| File | When to load |
|---|---|
| `references/directory-layout.md` | Full directory spec, project-type matrix, edge cases, archive strategy |
| `references/fork-workflow.md` | Forking an upstream repo: setup (gh CLI, 3 methods), PR workflow, upstream sync, multi-repo, troubleshooting |
| `references/migration-guide.md` | Restructuring a project: safety checks, atomic moves, reference sync, verification |
| `references/versioned-records.md` | Document/submission projects: INDEX + vNNN template, source file principle, upload workflow |
| `references/agents-md-template.md` | Creating AGENTS.md: ready-to-use template and worked example |
| `references/conversation-format.md` | Creating conversation files: full template with agent proposal / user modification / rationale |
| `references/review-naming.md` | Creating review files: full vocabulary, collision handling, migration procedures |

## Quick Reference Checklist

**Starting work:**
- [ ] Determine project type (Code / Document / Hybrid)
- [ ] If forking an upstream repo → follow Fork Workflow (Code variant): clone to `src/<repo-name>/`, configure origin/upstream remotes
- [ ] Confirm `AGENTS.md` and required dirs exist; create if missing
- [ ] Read `AGENTS.md` first — it indexes the project
- [ ] Place documents under correct `docs/` subdirectory
- [ ] After substantive work, append to `memory/YYYY-MM-DD.md` (code) or update `提交记录/INDEX.md` (document)

**Creating files (check for collisions first):**
- [ ] Review: `YYYY-MM-DD-<reviewer>-<scope>-HHMMSS.md` — scan `docs/reviews/`
- [ ] Conversation: `NN-kebab-topic.md` — scan `conversation/` for next number
- [ ] Submission version: `vNNN/` — scan `提交记录/` for next number

**Restructuring:**
- [ ] Read `references/migration-guide.md` first
- [ ] Snapshot processes and Git state before moving
- [ ] Move `src/` (with `.git/`) atomically — no re-init, no commit
- [ ] Grep ALL file types for old paths; update every match
- [ ] Archive superseded docs — never delete
- [ ] Record migration in `docs/migrations/`; verify build from new paths
