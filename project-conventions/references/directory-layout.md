# Directory Layout — Full Specification

This document provides the complete, authoritative specification for the project workspace directory layout. Refer to it when initializing a new project, migrating a non-conforming project, or resolving edge cases about where a file should go.

## Project Types

Three project types, each with different required directories:

| Type | Primary deliverable | Required dirs | Typical examples |
|---|---|---|---|
| **Code** | Source code / software | `AGENTS.md`, `README.md`, `docs/`, `src/`, `conversation/`, `memory/` | Web app, CLI tool, mobile app, library |
| **Document** | Documents, forms, submissions, certifications | `AGENTS.md`, `README.md`, `INDEX.md`, `docs/`, versioned records (e.g. `提交记录/`) | 申报材料, 合同管理, 报表, 认证材料 |
| **Hybrid** | Both code and significant document/submission components | Code dirs + document dirs | SaaS with compliance docs, open-source with certifications |

### What changes by project type

| Element | Code | Document | Hybrid |
|---|---|---|---|
| `src/` | Required | Not needed | Required |
| `release/` | On demand | Not needed | On demand |
| `conversation/` | Required | Optional | Required |
| `memory/` daily logs | Required | Optional (use versioned records instead) | Required |
| `docs/specs/`, `docs/plans/` | Required | Optional | Required |
| Versioned records (`vNNN/RECORD.md`) | Not typical | Required | Optional |
| Review naming (second-precision) | Required | Optional (date-precision OK for single-user) | Required |
| `design/` | Optional | Optional | Optional |

### How to determine project type

- Primary deliverable is **source code** → **Code**
- Primary deliverable is **documents/forms/submissions** → **Document**
- Both → **Hybrid**

When unsure, start minimal and add directories as needed. It's easier to add a directory later than to remove an unused one.

For a Document Project Root, the root `INDEX.md` is the human navigation page. The version-record directory has its own `INDEX.md` as the version ledger and may contain `MATERIALS.md` as the shared source-material checklist. See `versioned-records.md` for the exact boundary.

## Complete Tree

```
project-root/
├── AGENTS.md                # Required. Agent entry point — directory index + rule reference (auto-loaded)
├── README.md                # Required. Project overview & directory navigation
├── conversation/            # Required for Code/Hybrid; optional for Document
├── docs/                    # Required. All formal documents, centralized
│   ├── specs/               # Spec / design documents
│   ├── plans/               # Implementation plans, task breakdowns
│   ├── reviews/             # Review documents (strict naming)
│   │   └── artifacts/       # On demand. Review attachments (.diff, screenshots, logs)
│   ├── research/            # Research / competitive analysis
│   ├── reports/             # On demand. Implementation reports, status reports, issue logs
│   ├── decisions/           # On demand. Decision records (ADR-style), pre-execution confirmations
│   ├── archive/             # On demand. Historical variants, superseded docs (never delete)
│   └── migrations/          # On demand. Directory restructuring records
├── design/                  # On demand. Design assets (prototypes, SVGs, HTML mockups, design system)
├── src/                     # Required for code projects. Source and normal Repository Root
│   └── ...                  # Follow language ecosystem conventions; internal docs (e.g. src/docs/qa/) OK
├── release/                 # On demand. Final distributable artifacts only (no build intermediates)
├── memory/                  # Required for Code/Hybrid; optional for Document
│   ├── YYYY-MM-DD.md        # Daily work log (append-only)
│   └── MEMORY.md            # Curated long-term project notes
└── <agent-system-dir>/      # Agent platform's system directory (e.g. .workbuddy/, .qoderworkcn/) — NOT managed by this skill
    └── memory/              # Platform auto-maintained memory
```

## Per-Directory Specification

### `AGENTS.md` (Required)

**Purpose**: Agent entry point — the first file an agent reads when entering a workspace. Most agent tools auto-detect and load it into the system prompt. It is an **index**, not a reference manual.

**Content** (keep under ~60 lines):
- **Project**: one-line description
- **Mandatory Rules**: reference to `project-conventions` skill + 3-5 key rules (one line each)
- **Directory Index**: table of path → one-line description → link to details
- **Quick Reminders**: 5-7 critical naming patterns and do/don't bullets

**Naming**: Fixed as `AGENTS.md`. Some agent tools also support `CODEBUDDY.md` (takes priority if both exist — do NOT create both). Use `AGENTS.md` for cross-tool portability.

**Maintained by**: Any agent initializing or restructuring the project. Update when directory structure changes or key conventions change. Do NOT update for daily work logs or individual file content changes.

**What it must NOT contain**: Full rule specifications (live in skill's `references/`), detailed templates, long-form documentation, project history.

**Template**: See `agents-md-template.md` for a ready-to-use template and worked example.

**Relationship to README.md**: AGENTS.md is for AI agents (auto-loaded, lean index). README.md is for humans (project overview, tech stack, quick start). Both coexist; AGENTS.md may link to README.md.

---

### `README.md` (Required)

**Purpose**: Single entry point for humans (and a secondary reference for agents) opening the project.

**Content**:
- Project name and one-line description
- Tech stack table
- Quick start instructions (how to run / build / test)
- Directory navigation table (what each top-level folder contains)
- Known limitations and follow-up directions

**Naming**: Fixed as `README.md`. Never rename or move.

**Maintained by**: Any agent or human. Update whenever the project structure or tech stack changes meaningfully.

---

### `conversation/` (Required for Code/Hybrid; optional for Document)

**Purpose**: Capture the collaboration process — agent proposals, user modifications, rationale, and final decisions. This is the "how we got here" record, distinct from formal specs.

**Naming**: `NN-kebab-topic.md`
- `NN` = 2-digit zero-padded incrementing number, starting at `00`
- `kebab-topic` = lowercase hyphenated short topic descriptor
- Examples:
  - `00-overview.md`
  - `01-brainstorming.md`
  - `02-decision-changes.md`
  - `03-implementation-log.md`
  - `04-verification-report.md`
  - `05-brand-and-naming.md`

**Numbering rule**:
- Always use the next available number when creating a new file.
- Scan the directory first; if `05-*.md` is the highest, the next file is `06-*.md`.
- Never renumber existing files (breaks references).

**Maintained by**: Agents during active collaboration. One file per major topic or phase.

**Format**: See `conversation-format.md` for the full template.

---

### `docs/` (Required)

**Purpose**: Central home for all formal project documents. Never scatter documents at the project root.

**Subdirectories**:

#### `docs/specs/`
- **Holds**: Product requirement documents (PRD), architecture designs, technical design docs, interface definitions.
- **Naming**: `YYYY-MM-DD-<scope>-spec.md`
  - Example: `2026-07-19-screen-timeout-toggle-spec.md`
- **Maintained by**: Architect or PM agent.

#### `docs/plans/`
- **Holds**: Implementation plans, task breakdowns, milestone plans.
- **Naming**: `YYYY-MM-DD-<scope>-plan.md`
  - Example: `2026-07-19-screen-timeout-toggle-plan.md`
- **Maintained by**: Architect or Engineer agent.

#### `docs/reviews/`
- **Holds**: All review documents — code review, design review, PR review, takeover review, release review, etc.
- **Naming**: See `review-naming.md` for the full specification. Briefly: `YYYY-MM-DD-<reviewer>-<scope>-HHMMSS.md`.
- **Maintained by**: Whatever agent (or human) is performing the review.

#### `docs/research/`
- **Holds**: Competitive analysis, market research, technology investigations, feasibility studies.
- **Naming**: `YYYY-MM-DD-<topic>-research.md`
  - Example: `2026-07-19-bee-logo-generation-research.md`
- **Maintained by**: PM or research-focused agent.

#### `docs/reports/` (On demand)
- **Holds**: Implementation reports, status reports, issue logs, verification reports.
- **Naming**: `YYYY-MM-DD-<topic>-report.md`
  - Example: `2026-07-19-memory-pressure-report.md`
- **Maintained by**: Engineer or QA agent.

#### `docs/decisions/` (On demand)
- **Holds**: Decision records (ADR-style), pre-execution confirmations, rulings on design choices.
- **Naming**: `YYYY-MM-DD-<topic>-decision.md`
  - Example: `2026-07-20-menubar-icon-ruling-decision.md`
- **Maintained by**: Any decision-making agent or human.

#### `docs/archive/` (On demand)
- **Holds**: Historical variants, superseded documents, draft versions replaced by finals.
- **Naming**: `YYYY-MM-DD-<topic>/` (subdirectory per archive batch; files inside keep original names)
  - Example: `docs/archive/2026-07-20-plan-variants/plan-01-draft.md`
- **Maintained by**: Migration agent.
- **Rule**: Never delete superseded documents — always archive. See `migration-guide.md` for the archive procedure.

#### `docs/migrations/` (On demand)
- **Holds**: Directory restructuring records — before/after trees, file mappings, reference update logs.
- **Naming**: `YYYY-MM-DD-directory-migration.md`
  - Example: `2026-07-20-directory-migration.md`
- **Maintained by**: Migration agent.
- **Note**: This is the authoritative record of what moved where and why.

#### `docs/reviews/artifacts/` (On demand)
- **Holds**: Review attachments — `.diff` files, screenshots, log captures, test evidence.
- **Naming**: Preserve original filenames. Use `artifacts/legacy/` for migrated historical attachments.
  - Example: `docs/reviews/artifacts/2026-07-15-code-review.diff`
- **Maintained by**: Reviewing agent.
- **Note**: Artifacts stay with the review they belong to. If a review spans multiple files, group artifacts in a subdirectory named after the review.

---

### `design/` (On demand)

**Purpose**: Design assets that are not source code — prototypes, HTML mockups, SVG assets, design system files, Figma exports.

**Naming**: Preserve the internal structure of the design package. Use a descriptive subdirectory per design package (e.g., `design/trae-k3/`).

**Maintained by**: Designer or PM agent.

**Notes**:
- If the design package contains JSON metadata with absolute paths, update them after moving.
- Do not flatten or reorganize internal structure during migration — move as-is.
- Design assets here are distinct from `docs/specs/` (which holds written design specifications).

---

### `src/` (Required for code projects)

**Purpose**: All source code, tests, and project/build files. For a Git-backed Project Root, `src/` normally contains the one mapped Repository Root.

**Naming**: Follow the conventions of the language ecosystem (e.g., `.sln`/`.csproj` for .NET, `package.json` for Node, `Cargo.toml` for Rust, `Package.swift` for Swift).

**Maintained by**: Engineer agent.

**Notes**:
- **One Project Root, one source-repository mapping by default.** Record it in `AGENTS.md`. If unrelated repositories are needed, create sibling Project Roots instead of hiding them in one wrapper.
- The Repository Root may be `src/` itself or one named child such as `src/<repo-name>/`. Verify it with `git rev-parse --show-toplevel`.
- **Explicit shared-repository exception**: inside a Project Collection, `src/<package-name>` may be a verified projection to `<collection>/<repository_root>/<managed_scope>`. The canonical member index must record `source`, collection-relative `repository_root`, and repository-relative `managed_scope` separately. Read `shared-repository.md`; do not infer this exception from a symlink alone.
- Keep the Project Root wrapper outside the source repository unless the user explicitly chooses a repository that includes the wrapper.
- When migrating an existing Git worktree into `src/`, preserve its `.git` data atomically; do not re-init, commit, reset, or rewrite history. See `migration-guide.md`.
- Tests typically live under `src/tests/` or alongside source per ecosystem convention.
- **Internal docs are OK**: code repositories may have their own documentation that is version-tracked with the code (e.g., `src/docs/qa/`, `src/script/qa/`). These stay in `src/` — they are part of the codebase, not project-level docs.
- **Build intermediates** (`DerivedData/`, `bin/`, `obj/`) stay under `src/`. Only final distributable artifacts go to `release/`. Never move build intermediates to `release/`.
- **Uncommitted changes** travel with the directory during migration. Do not stash or commit during a migration.
- **Monorepo member**: clone or check out the actual repository under `src/` and record the managed subpath. A provider `/tree/<ref>/<subpath>` URL is not a clone URL. Sparse checkout is optional and must preserve the verified Repository Root.
- **Fork workflow**: one contribution fork is still the Project Root's one repository mapping. Use `origin` for the personal fork and `upstream` for the original. See `fork-workflow.md`.

### Repository mapping contract

Every Git-backed Project Root's `AGENTS.md` must identify:

| Field | Required value |
|---|---|
| Project Root | The wrapper path governed by this convention |
| Repository Root | Relative path under the wrapper, normally `src` or `src/<repo-name>` |
| Shared Repository Root | For the explicit collection profile only, a collection-relative path such as `GitHub`; never a user-home absolute path |
| Clone URL / remote | Credential-free URL or repository identity; write `local only` when no remote exists |
| Default ref | Observed default branch/ref, or `unknown` |
| Managed scope | `whole repository` or an explicit monorepo subpath |

This mapping prevents future agents from confusing wrapper files with repository contents or trying to push the Project Root to a repository that only owns `src/`.

---

### `release/` (Optional, created on demand)

**Purpose**: Compiled binaries, packaged executables, distribution artifacts.

**Naming**: Follow release versioning conventions of the ecosystem.
- Example: `ScreenTimeoutToggle.exe`, `myapp-1.0.0.zip`

**Maintained by**: Engineer or release agent.

**Notes**:
- Keep this directory clean — only final distributable artifacts, not intermediate build outputs.
- Intermediate build outputs stay under `src/.../bin/` or equivalent.

---

### `memory/` (Required for Code/Hybrid; optional for Document)

**Purpose**: Agent-maintained project memory, visible to any agent that reads the project. Distinct from the agent platform's system memory directory.

**Files**:
- `memory/YYYY-MM-DD.md` — Daily work log. Append-only. One file per calendar day.
- `memory/MEMORY.md` — Curated long-term project notes. Updated in place. Keep under ~3000 chars.

**When to write**:
- After completing substantive work (building, fixing, refactoring, generating a deliverable).
- When the user shares a project convention or preference.

**When to skip**:
- Trivial exchanges (greetings, simple lookups, short Q&A).

**What goes in daily log**:
- What was done today
- Key decisions made
- Blockers encountered
- Follow-up items

**What goes in `MEMORY.md`**:
- Distilled project conventions
- Architecture decisions and their rationale
- User preferences specific to this project
- Cross-session context that future agents should know

**Maintenance**:
- Distill daily logs older than 30 days into `MEMORY.md` by topic. If retention is unnecessary, archive those logs under `memory/archive/`; never delete undistilled project history.
- Never store secrets unless the user explicitly asks.

---

### `<agent-system-dir>/` (System — NOT managed by this skill)

**Purpose**: The agent platform's own system directory (e.g. `.workbuddy/`, `.qoderworkcn/`, `.claude/`). Contains platform-managed memory that gets auto-injected into the system prompt.

**Important**: This skill's workflows NEVER write to the agent platform's system memory directory. That location is reserved for the platform itself. Use `memory/` at project root instead.

If you need to record something for other agents to discover, write to `memory/` — not the platform's system directory.

## Migration Guidance

For the full step-by-step migration procedure (pre-flight checks, atomic moves, reference sync, archive strategy, verification, and common migration patterns), see **`migration-guide.md`**.

Key rule: never restructure without reading that guide first. Move code atomically (`mv`, not `cp`+`rm`), sync ALL reference types (not just Markdown), and archive superseded docs instead of deleting.

## Edge Cases

### What if a document type doesn't fit any subdirectory?

If a document genuinely doesn't fit `specs/`, `plans/`, `reviews/`, or `research/`, propose a new subdirectory under `docs/` and document it in this file. Do not dump non-conforming files at `docs/` root.

### What if the project has no code (docs-only project)?

Follow the Document row in **Project Types**: require `AGENTS.md`, `README.md`, root `INDEX.md`, `docs/`, and versioned records. Add `conversation/` or `memory/` only when the project needs those patterns.

### What if multiple agents are working concurrently?

- Each agent writes to its own files (review documents include the reviewer name, conversation files use sequential numbers).
- For `memory/YYYY-MM-DD.md`, use append-only writes. If two agents write simultaneously, both appends are valid — the file is a chronological log.
- Never overwrite another agent's memory entry; append your own with a timestamp.

## File Focus Principle

Every file in the project should focus on a **single topic or responsibility**. Bloated files that try to cover everything are hard to navigate, hard to maintain, and hard for agents to load into context efficiently.

### Guidelines

| File type | Should contain | Should NOT contain |
|---|---|---|
| `AGENTS.md` | Directory index + rule references + quick reminders | Full rule specs, templates, project history, tech stack details |
| `README.md` | Project overview, tech stack, quick start, navigation | Detailed rules (those live in skill), daily logs |
| `conversation/NN-*.md` | One discussion topic: proposals, modifications, rationale, decision | Unrelated topics (split into separate files), full code listings |
| `docs/specs/*.md` | One design document for one scope | Multiple unrelated designs, implementation code |
| `docs/plans/*.md` | One implementation plan | Design rationale (that's in specs), test results |
| `docs/reviews/*.md` | One review session's findings | Multiple review sessions, unrelated artifacts |
| `memory/YYYY-MM-DD.md` | One day's work log | Long-term reference info (that's in `MEMORY.md`) |
| `memory/MEMORY.md` | Curated long-term project facts | Daily activity logs (those are in dated files) |

### When to Split a File

- A file exceeds ~500 lines and covers multiple distinct topics → split by topic.
- A conversation file spans multiple unrelated decisions → split into separate numbered files.
- A spec covers multiple independent modules → split into separate spec files per module.
- AGENTS.md grows beyond ~60 lines → you're inlining details; move them to referenced files.

### When NOT to Split

- A single coherent topic that happens to be long (e.g., a comprehensive design spec) — length alone is not a reason to split if the content is cohesive.
- A review that covers multiple files in a single review session — that's one review, one file.
