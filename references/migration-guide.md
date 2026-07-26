# Migration Guide — Directory Restructuring Procedure

This document provides the step-by-step procedure for migrating a project's directory layout to conform to the `project-conventions` standard. It is based on real-world migrations (OB Dim, Pets) and covers safety checks, atomic moves, reference syncing, and verification.

## When to Use This Guide

- Restructuring an existing project to conform to the standard layout
- Moving `src/` (or equivalent code directory) to the project root
- Migrating documents from a non-standard structure (e.g., `docs/superpowers/`)
- Renaming review files to the standard naming convention
- Any operation that changes file paths within a project

## Phase 1: Pre-Flight Safety Checks

**Before touching any files**, perform these checks:

### 1.1 Process Check

Determine if any processes are actively using the old directory paths:

- **IDE / Editor**: Is Xcode, VS Code, or another IDE open with the project? Close it or confirm it won't lock files.
- **Build processes**: Is a build running? Is a dev server active? Wait for completion or stop gracefully.
- **Git operations**: Is a `git commit`, `push`, `rebase`, or `merge` in progress? Wait for it to finish.
- **Terminal sessions**: Are any shells `cd`'d into directories that will be moved? They'll break.

**Rule**: If any process is actively using old paths, **pause and ask the user**. Never `kill -9` or force-terminate.

### 1.2 Git Status Snapshot

If `src/` (or the code directory) contains its own `.git/`:

```bash
git -C <old-code-path> status --short        # list uncommitted changes
git -C <old-code-path> stash list             # check for stashes
git -C <old-code-path> log --oneline -5       # recent history for reference
```

Record the count of uncommitted changes. This count must be **identical** after the move — the migration must not alter any Git state.

### 1.3 File Inventory Snapshot

List all visible files (excluding hidden directories like `.git`, `.workbuddy`, `.superpowers`):

```bash
find . -not -path '*/.*' -type f | sort > /tmp/pre-migration-files.txt
```

This serves as the baseline for the post-migration verification.

### 1.4 User Confirmation

Present the migration plan to the user:
- What will move (old path → new path)
- What will be archived (and where)
- What will NOT be touched (hidden directories, build intermediates)
- Get explicit confirmation before proceeding.

## Phase 2: Atomic Directory Moves

### 2.1 Moving a Code Directory with Its Own `.git/`

When moving a code directory (e.g., `trae/K3/code/` → `src/`):

1. **Move as one atomic unit** — use `mv` on the top-level directory, not `cp` + `rm`. This preserves `.git/`, uncommitted changes, build outputs, and internal structure intact.

   ```bash
   mv trae/K3/code src
   ```

2. **Do NOT**:
   - Re-initialize Git (`git init`) — the existing `.git/` travels with the move.
   - Commit or stash — uncommitted changes should travel as-is.
   - Reset or rewrite history — the migration is path-only, not content.
   - Run `git clean` — untracked files may be important.

3. **Verify immediately**:
   ```bash
   git -C src rev-parse --show-toplevel       # should point to src/
   git -C src status --short | wc -l          # must match pre-migration count
   ```

### 2.2 Moving Design Assets

When moving a design package (e.g., `trae/k3/` → `design/trae-k3/`):

1. Move the entire directory, preserving internal structure (`.design`, HTML, CSS, JSON, SVG).
2. **Update metadata files** — if the design package contains JSON files with absolute paths, update them to reflect the new location.
3. Do not flatten or reorganize the internal structure — move as-is.

### 2.3 Moving Documents into `docs/`

When centralizing documents:

1. Create standard subdirectories: `docs/specs/`, `docs/plans/`, `docs/reviews/`, `docs/research/`, `docs/reports/`, `docs/decisions/`.
2. Move each document to its correct subdirectory (see SKILL.md Directory Content Rules table).
3. Rename review files to the standard pattern (`YYYY-MM-DD-<reviewer>-<scope>-HHMMSS.md`).
4. For historical files with unknown timestamps, use `000000` as placeholder (see `review-naming.md`).

## Phase 3: Archive Superseded Documents

### 3.1 When to Archive

Archive (do NOT delete) when:
- A draft plan is replaced by a final version
- A document has multiple variants and only one is canonical
- Old naming convention files are superseded by renamed versions

### 3.2 How to Archive

1. Create a date-stamped subdirectory under `docs/archive/`:
   ```
   docs/archive/2026-07-20-plan-variants/
   ```

2. Move superseded files into this subdirectory, **preserving original names**:
   ```
   docs/archive/2026-07-20-plan-variants/plan-01-draft.md
   docs/archive/2026-07-20-plan-variants/plan-01-packed.md
   ```

3. Record in the migration document which files were archived and why.

### 3.3 Archive Naming

```
docs/archive/YYYY-MM-DD-<topic>/
├── <original-filename-1>
├── <original-filename-2>
└── ...
```

- `YYYY-MM-DD` = the date of archiving (not the file's original creation date).
- `<topic>` = short hyphenated descriptor of what was archived.
- Files inside keep their **original names** — do not rename archived files.

## Phase 4: Reference Sync (Critical)

After all files are moved, update every reference to old paths. This is the most error-prone phase — a single missed reference creates a broken link.

### 4.1 What to Search

Search the **entire project root** for old path patterns. Use `grep -rn` or the Grep tool.

### 4.2 File Types to Check

| File type | What to look for | Example |
|---|---|---|
| `.md` (Markdown) | Relative path references in text, tables, links | `docs/superpowers/specs/...` → `docs/specs/...` |
| `.json` | Absolute or relative path strings | `"path": "/Users/.../trae/K3/code"` → `".../src"` |
| `.sh` / `.py` / `.swift` (scripts) | Path variables, `cd` commands, file paths | `CODE_DIR="trae/K3/code"` → `CODE_DIR="src"` |
| `.md` with `file://` links | `file:///absolute/path/to/old/dir` | Update to new path |
| `.json` / `.plist` (config) | Build paths, DerivedData paths | May reference old code root |
| `.xcconfig` / `.pbxproj` | Xcode project file paths | Usually relative — verify still correct |

### 4.3 Search Strategy

Run multiple greps for each old path pattern:

```bash
# Search for old code directory path
grep -rn "trae/K3/code\|trae/k3/code" . --include="*.md" --include="*.json" --include="*.sh" --include="*.py"

# Search for old docs structure
grep -rn "docs/superpowers\|docs/review/" . --include="*.md" --include="*.json"

# Search for old design path
grep -rn "trae/k3" . --include="*.md" --include="*.json" --include="*.sh"
```

### 4.4 Exceptions (Do NOT Update)

- **Hidden directories** (`.workbuddy/`, `.superpowers/`, `.uploads/`) — these are system-managed; do not update their internal references unless explicitly asked.
- **Git history** inside `src/.git/` — never modify Git internals.
- **Build intermediates** (`DerivedData/`, `bin/`, `obj/`) — these will be regenerated on next build.
- **Migration records** — the `docs/migrations/` document intentionally contains old paths for before/after comparison.

### 4.5 Update Procedure

For each match:
1. Read the file to understand context.
2. Replace the old path with the new path.
3. Do NOT alter surrounding text or narrative — only the path string changes.
4. For historical files (`conversation/`, `memory/`): update path references to keep navigation valid, but never rewrite the historical narrative.

## Phase 5: Create Migration Artifacts

### 5.1 Migration Record

Create `docs/migrations/YYYY-MM-DD-directory-migration.md` containing:

- **Background**: why the migration was needed
- **Before/After directory tree**: visual comparison
- **File mapping table**: old path → new path → notes
- **Archive listing**: what was archived and where
- **Reference updates**: which files had path references updated
- **Verification results**: build/test status after migration

### 5.2 Conversation Record

Create `conversation/NN-workspace-reorganization.md` (next available number) capturing:
- What the agent proposed
- What the user changed/confirmed
- Why certain decisions were made (e.g., which plan variants to archive vs. keep)

### 5.3 Memory Update

- Append a note to `memory/YYYY-MM-DD.md` summarizing the migration.
- Update `memory/MEMORY.md` if any long-term path references changed.

### 5.4 AGENTS.md Update

If the project has an `AGENTS.md`, update its Directory Index table to reflect the new structure.

### 5.5 Cleanup

After all moves and reference updates:
1. Delete now-empty old directories (e.g., `trae/` if all contents moved).
2. Verify no files were left behind: `find <old-parent-dir> -type f` should return nothing.
3. Do NOT delete hidden directories (`.workbuddy/`, etc.).

## Phase 6: Verification

### 6.1 File Count Verification

```bash
find . -not -path '*/.*' -type f | sort > /tmp/post-migration-files.txt
diff /tmp/pre-migration-files.txt /tmp/post-migration-files.txt
```

Every file in the pre-migration list should appear in the post-migration list (possibly at a new path). The diff should show only path changes, not file additions/deletions (except for newly created migration docs).

### 6.2 Git State Verification

```bash
git -C src status --short | wc -l          # must match pre-migration count
git -C src rev-parse --show-toplevel       # must point to src/
```

### 6.3 Build Verification

Run the project's build and test commands from the new paths:

```bash
cd src && dotnet test          # for .NET
cd src && swift test           # for Swift
cd src && npm test             # for Node
```

Verify that:
- The build can locate the project file (`.sln`, `Package.swift`, `package.json`)
- Tests can locate fixtures and QA files
- No "file not found" errors related to migrated paths

### 6.4 Reference Verification

Grep for old paths one final time. The **only** acceptable remaining matches should be in:
- `docs/migrations/` (the migration record — intentionally contains old paths)
- `conversation/` (if the conversation discusses the old structure)
- `memory/` (if memory logs reference the old structure)

Any match in active code, configs, or active documents indicates a missed reference update.

## Common Pitfalls

| Pitfall | Consequence | Prevention |
|---|---|---|
| Forgetting to check for active processes | File locks, corruption | Always run Phase 1 checks first |
| `cp` + `rm` instead of `mv` for Git repo | Loses `.git/` or breaks history | Use `mv` for atomic move |
| Committing during migration | Pollutes Git history with path-only changes | Never commit during migration; let user commit after verification |
| Only updating Markdown references | Broken JSON configs, script paths | Grep ALL file types (Phase 4.2) |
| Deleting superseded docs instead of archiving | Lost history, can't recover drafts | Always archive to `docs/archive/` |
| Updating `.workbuddy/memory/` references | Breaks system-managed memory | Leave hidden directories alone |
| Forgetting to verify build after migration | Silent breakage discovered later | Always run Phase 6 verification |
| Moving build intermediates (`DerivedData/`) | Unnecessary rebuild time | Leave build intermediates in `src/`; only `release/` has final artifacts |
