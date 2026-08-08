# Project Collection Convention

Use this reference when one directory groups related but independently governed Project Roots.

## 1. Boundary

A **Project Collection** is a routing layer. It is not:

- a Git super-repository;
- a Project Root with its own `src/`, `docs/`, conversation, or memory;
- a place to copy every member's source;
- a cross-device inventory service.

Each member remains a normal Project Root. One member is designated as the **collection-control project** and owns collection-wide indexes and deterministic utilities.

## 2. Minimal layout

```text
<collection-root>/
├── AGENTS.md                         # Collection routing and safety overlay
├── README.md                         # Human overview
├── MEMBERS.md                        # Generated/readable member view
├── <control-project>/                # A normal Project Root
│   ├── AGENTS.md
│   ├── README.md
│   ├── docs/
│   │   └── indexes/
│   │       └── members.md            # Canonical member index
│   ├── conversation/
│   ├── memory/
│   └── src/                          # Collection-control scripts/config only
├── <member-a>/                       # Independent Project Root
│   ├── AGENTS.md
│   ├── docs/
│   ├── conversation/
│   ├── memory/
│   └── src/                          # Member source and optional Repository Root
└── <member-b>/
    └── ...
```

Do not initialize Git at `<collection-root>/`. The control project and members decide their own repository boundaries independently.

## 3. Canonical member index

The canonical table lives inside the control project, for example `skills/docs/indexes/members.md`:

```markdown
| key | name | path | role | source | vcs | remote | category | status | tags |
|---|---|---|---|---|---|---|---|---|---|
| project-conventions | Project Conventions | project-conventions | member | src/project-conventions | none | - | personal-open | active | skill,governance |
```

Field rules:

| Field | Rule |
|---|---|
| `key` | Stable and unique inside the collection |
| `path` | Member Project Root relative to the collection root |
| `role` | `collection-control` or `member` |
| `source` | Source or Repository Root relative to that member; normally `src` or `src/<repo>` |
| `vcs` | Observed local state: `git` = Git worktree with a declared remote identity; `local_git` = Git worktree without one; `none` = no Git worktree at the declared source/root |
| `remote` | Credential-free repository identity or `-`; with `none`, a separately verified intended/upstream identity is allowed but is not evidence of a local remote |
| `category` | One of the workspace's four project categories |
| `status` | `active` = current live member; `inactive` = retained and still checked but not routinely maintained; `observed` = inventory-only member seen on this computer and not yet initialized/adopted; `archived` = historical row that does not provide live path or Git coverage |

The root `MEMBERS.md` is a generated/readable mirror. It is not a competing fact source.

An `observed` row still provides path and Git coverage, but it never proves initialization, adoption, or maintenance authority. An archived row keeps its key/path history and still participates in duplicate detection. Missing archived paths or sources are not drift by themselves. If a Git root is still observed under an archived row, it remains uncovered and is reported for a human decision.

## 4. Global workspace registration

The Projects Workspace registers the collection once in `_project-catalog/docs/indexes/00-collections.md`:

```markdown
| key | name | path | kind | members_index | purpose | tags |
|---|---|---|---|---|---|---|
| obisoldbee-skills | obisoldbee Skills | obisoldbee-skills | collection | skills/docs/indexes/members.md | Related Skill projects | skill,agent |
```

`00-collections.md` is a structural index, not a fifth ownership category. Every member's `category` remains in the canonical member index.

The workspace inspector:

1. validates the collection path and `members_index`;
2. expands member paths relative to the collection root;
3. treats member rows as project coverage;
4. reports missing or duplicate members;
5. leaves the collection root itself out of repository checks.

If the member index is missing or unreadable, report the error and do not treat nested repositories as covered.

## 5. Source and repository mapping

Each member Project Root normally owns one source mapping:

| Field | Meaning |
|---|---|
| Project Root | Member wrapper, documents, decisions, conversation, memory |
| Repository Root | Verified Git worktree under the member's `src/` |
| Clone URL / remote | Where the repository is cloned from or pushed to |
| Managed scope | Optional path inside a monorepo checkout |

Example:

```text
<collection>/project-conventions/                # Project Root
└── src/project-conventions/                     # Skill package source

<collection>/project-handoff/                    # Project Root
└── src/                                         # Repository Root when .git is here
    └── project-handoff/                         # Skill package source
```

Do not assume all members share one Git repository. Do not put placeholder member source directories in the control project's `src/`.

## 6. Skills collection control project

A Skills collection-control project may own:

- `docs/indexes/members.md`;
- an explicit Skill export allowlist;
- known agent Skill target-path candidates;
- read-only link scanning and an explicit apply command;
- collection-level reports, plans, and research.

These are responsibilities of the collection-control project. This Skill supplies the convention and the read-only workspace inspector; it does not bundle a renderer, link utility, or upstream checker.

Its link utility must:

1. derive the collection root from the script location;
2. read only explicit allowlists;
3. verify `SKILL.md` at every source;
4. require the target parent to already exist;
5. default to scan/dry-run;
6. never replace a real path, wrong link, or dangling link automatically;
7. create a link only after explicit `--apply` or platform equivalent.

## 7. Initialization flow

```text
inspect collection
→ identify existing member Project Roots
→ choose one collection-control Project Root
→ create root routing overlay
→ write canonical member index
→ validate member paths and source mappings
→ render MEMBERS.md
→ report unresolved boundaries
```

Do not initialize or restructure every member merely because it appears in the member index. A member is initialized only when the user asks to work on that Project Root.

## 8. Failure handling

| Condition | Behavior |
|---|---|
| Member path missing | Report; retain the row |
| Source path missing | Report; do not create or clone automatically |
| Member has Git at the Project Root but policy expects `src/` | Propose a separate history-preserving migration |
| No or multiple `collection-control` roles | Report; do not guess which project owns the member index |
| Collection root has `.git` | Report a boundary conflict; do not move it automatically |
| Duplicate member key/path | Block generated view refresh |
| Link target conflict | Report; never delete or replace automatically |
