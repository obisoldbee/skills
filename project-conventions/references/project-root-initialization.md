# Ordinary Project Root Initialization

Use this workflow for Code, Document, or Hybrid Project Roots outside the special shared-Skills collection profile.

This workflow runs only for an explicit initialization/adoption lifecycle. Seeing an old Project Root during a bug fix, review, build, or other unrelated task is not adoption authority: do not pause that task merely because `.project-conventions/` is absent, and do not create it without the selected initialization scope.

## Select the type from the intended deliverable

- **Code**: runnable software/source is the primary deliverable. A PRD that supports development still goes under `docs/specs/`; its presence alone does not make the project Hybrid.
- **Document**: forms, reports, submissions, certifications, or other documents are the primary deliverable.
- **Hybrid**: source code and a substantial document/submission lifecycle are both primary deliverables.

Existing file extensions are evidence, not the decision by themselves. A directory containing only `material/` can still initialize as Code when the requested outcome is “analyze these materials, write a PRD, and build the product.”

## Select a profile when the source is an Agent Skill

An Agent Skill workspace is a **Code Project** with an `agent-skill` profile, even when `SKILL.md` and YAML make up most of its package:

```bash
python3 -B scripts/initialize_project_root.py <target> \
  --type code --profile agent-skill --skill-name <skill-name> \
  --mode <fresh-empty|adopt-existing>
```

Its owned-local package root is `src/<skill-name>/`, with the entry at `src/<skill-name>/SKILL.md`. Fresh initialization creates a structurally valid, explicitly unfinished scaffold; Project Root validation does not mean the Skill behavior is ready, installed, discovered, or executed. Adoption preserves an existing correct package byte-for-byte. A root `SKILL.md`, `src/SKILL.md`, a Skill entry under `docs/`, a sibling package under `src/`, or a linked path hiding another package is a migration conflict: stop before writing and require a separately authorized exact old-to-new move. Do not move the package into `.minimax`, `.codex`, `.agents`, or another Agent directory; those are consumers. A shared-repository wrapper uses its separately verified projection and is not created by this ordinary profile.

## Select the mode

| Mode | Use when | Existing content |
|---|---|---|
| `fresh-empty` | The target is missing, empty, already initialized, or contains only recognized Harness directories | Reject unrelated user entries |
| `adopt-existing` | The target already contains user material, source, documents, or routing files | Preserve every existing item; add only the missing managed baseline |

Neither mode moves existing content, initializes Git, creates a worktree, scans siblings, or edits a Harness-owned hidden directory.

## Dry-run, apply, validate

Run from the installed or cloned `project-conventions` package:

```bash
python3 -B scripts/initialize_project_root.py <target> \
  --type <code|document|hybrid> \
  --mode <fresh-empty|adopt-existing>

python3 -B scripts/initialize_project_root.py <target> \
  --type <code|document|hybrid> \
  --mode <fresh-empty|adopt-existing> \
  --apply

python3 -B scripts/validate_project_root.py <target>
```

Optional fields:

- `--name <human project name>` changes generated headings only.
- `--repository-root <relative/path>` records an intended source mapping without creating or claiming that Git exists.
- `--records-dir <relative/path>` enables a version ledger for any type. It is never created merely because the type is Document; add it only for a real submission or version cycle.
- `--profile agent-skill --skill-name <name>` fixes the editable package root at `src/<name>/`; omit both for ordinary projects.

Use only normalized Project-Root-relative paths. Do not pass a user-home path, mounted-volume path, drive-qualified user path, file URI, remote machine path, or `..`.

## Adoption behavior

The initializer:

- preserves existing `README.md`, `INDEX.md`, `memory/MEMORY.md`, record indexes, and all unnamed content;
- appends one bounded access block to an existing UTF-8 `AGENTS.md` while preserving its other rules;
- stops when an existing managed block or project-control file differs;
- creates a small self-contained `.project-conventions/` access entry;
- creates only type-required directories and missing baseline files;
- reports `moved: []` because classification is not move authority;
- returns `already_initialized` on a repeated matching run.

Original/user-provided material stays where the user placed it unless a separate migration authorizes an exact old-to-new map. Typical routing for later Agent outputs is:

| Output | Destination |
|---|---|
| PRD, product/architecture specification | `docs/specs/` |
| Research, source analysis, transcript correction | `docs/research/` |
| Implementation plan | `docs/plans/` |
| Review | `docs/reviews/` |
| Design prototype/assets | `design/` |
| Runnable source and tests | `src/` |
| Decision process and user corrections | `conversation/` |
| Cross-task continuity | `memory/` |

Do not copy raw material into `docs/` merely because an Agent analyzed it. Derived documents cite the relative source path; they do not replace the source.

## Harness and remote-host boundary

`.workbuddy/`, `.codex/`, `.minimax/`, `.qoder*`, `.claude/`, and similar Harness directories are opaque. The initializer neither reads their contents nor counts them as project material. Their memory never replaces project `conversation/` or `memory/`.

When work arrives from another computer, an absolute path in the handoff is only `source_host_observed_path` evidence. Resolve the actual target on the current host and write active `AGENTS.md`, `README.md`, indexes, and configuration with relative paths. Validate those paths from disk after writing.

## Agent admission after initialization

The generated `AGENTS.md` points every Harness to the project-local access helper. Read `project-access.md` for the exact reader/writer/worktree rules. This is the safety baseline; an optional orchestrator may improve scheduling, but it is not required for admission or mutual exclusion.
