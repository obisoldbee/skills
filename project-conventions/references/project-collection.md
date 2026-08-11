# Project Collection

A Project Collection groups related but independently governed Project Roots. Its root is a routing overlay, not a Project Root, Git super-repository, or monorepo.

## Required shape

```text
<collection>/
├── AGENTS.md
├── README.md
├── MEMBERS.md
├── <control-project>/
│   └── docs/indexes/members.md
└── <member-project>/
    ├── AGENTS.md
    ├── README.md
    ├── docs/
    ├── conversation/
    ├── memory/
    └── src/
```

The three collection-root files route; they do not absorb member documents or source. Exactly one **collection-control Project Root** owns the canonical member index and collection-wide deterministic tools.

## Canonical member index

Use one table:

| key | name | path | role | source | repository_root | vcs | remote | managed_scope | category | status | tags |
|---|---|---|---|---|---|---|---|---|---|---|---|
| skills | Skills Collection Control | skills | collection-control | src | - | none | - | local control files | local-only | active | collection,links |
| project-conventions | Project Conventions | project-conventions | member | src/project-conventions | GitHub | git | obisoldbee/skills | project-conventions/ | personal-open | active | skill,governance |

Field semantics:

- `path`: stable collection-relative Project Root.
- `role`: `collection-control` for exactly one row; otherwise `member`.
- `source`: Project Root-relative deliverable/source entry.
- `repository_root`: always collection-relative (`member/src` for an ordinary member, `GitHub` for the shared profile), or `-` when none.
- `vcs`: `none`, `local_git`, or `git`.
- `remote`: normalized identity such as `owner/repository`, or `-`.
- `managed_scope`: repository-relative subpath, `whole repository`, or a local description when no repository exists.
- `category`: `local-only`, `personal-open`, `personal-private`, or `upstream-open`.
- `status`: `active`, `inactive`, `observed`, or `archived`.

The collection-root `MEMBERS.md` is a readable mirror, not a second fact source.

## Ordinary member repository mapping

Normally a Git-backed member owns one Repository Root under its own `src/`:

```text
<collection>/<member>/src/<checkout>/
```

Record that Repository Root relative to the member and verify it with `git rev-parse --show-toplevel`. Do not infer it from the remote or directory name.

## Shared Repository Root exception

Read `shared-repository.md` before using this exception.

A collection may hold one or more shared Repository Roots as infrastructure when owned distribution repositories are the physical source for explicitly mapped packages. Each affected member still owns its own documents and continuity records. Every normalized remote identity may have only one checkout in the collection.

The member source must be a verified projection:

```text
<member>/<source>
  -> <collection>/<repository_root>/<managed_scope>
```

Rules:

1. The collection root remains non-Git.
2. The shared Repository Root is a real directory and exact Git worktree, not a link.
3. `repository_root` and `managed_scope` must both be explicit and safe relative paths.
4. The projection must resolve exactly to that scope.
5. Unix uses the exact final-path-relative symlink; Windows uses a final-path directory junction. Reject absolute Unix links and Windows directory symlinks even when they resolve to the expected bytes.
6. Agent exports point directly to the true package, not through the projection.
7. Updating the shared checkout does not authorize wrapper/index/link changes.
8. Private or local-only members outside that checkout remain independent.

An optional owned private distribution follows the same explicit `repository_root` plus `managed_scope` mapping, but its remote identity and private visibility must be verified before push or export. The standard public initializer does not create it.

A third-party checkout pool is different: the pool root has no `.git/`, every named child is an independent upstream Repository Root, and mere presence never authorizes export or adoption.

## Publication class and runtime boundary

`category` records source ownership and publication policy; it does not say where a Skill can execute. For an environment-bound Skill, keep a concise runtime boundary in its `SKILL.md` and route to it from the member wrapper:

- `availability`: `portable`, `device-bound`, `network-bound`, `device-and-network-bound`, or `unverified`;
- `allowed devices`: `any`, stable non-secret device labels, or `unknown`;
- `required network`: `any`, a stable non-secret profile label, or `unknown`;
- external dependencies, safe verification method, and mismatch stop rule.

Multiple allowed devices are alternatives, as are multiple allowed network profiles. The device axis and network axis are conjunctive when both are constrained. A matching device on the wrong network is unavailable. Do not record credentials, SSIDs, private keys, tokens, cookies, or secret endpoints in the runtime boundary.

## Collection-control responsibilities

The control project may own:

- canonical member index;
- generated root member view;
- explicit Skill export allowlist;
- known Agent path candidates;
- scan-first link utilities;
- deterministic public-repository root overlay tools that read the shared checkout directly;
- collection-level plans, reviews, decisions, conversation, and memory.

It must not own member package source, member-specific research, another member's Git history, or Agent runtime state.

For a fresh shared Skills collection, use `scripts/initialize_skills_control_project.py`. It creates the complete control project, wrapper, projection, and routing overlay after the shared checkout is validated. Do not run `initialize_project_collection.py` first and do not handwrite a reduced control project.

For a generic non-shared collection, `scripts/initialize_project_collection.py` creates the three-file root overlay only. Existing control and member roots are added or migrated separately.

## Skill exports and links

`src/config/skill-exports.tsv` is an allowlist:

```text
skill_name	source	consumers
project-conventions	GitHub/project-conventions	all
```

The source is collection-relative and must resolve inside the collection to a package containing `SKILL.md`. Link tools:

- default to read-only scan;
- require an exact Agent/target and Skill for apply;
- never create target parents;
- never replace real paths, wrong links, or dangling links;
- reject apply-to-all;
- read back every created link/junction.

Initialization creates no Agent link. A successful link is not proof of runtime discovery.

## Workspace indexing

A Projects Workspace indexes the collection once in its structural collection index and expands this member index. It does not duplicate each member into workspace category tables.

The inspector must cover:

- collection and member paths;
- declared Repository Roots, including shared ones;
- Git remote/VCS agreement;
- projection type and exact managed-scope target;
- missing or dangling paths;
- duplicate member keys/paths;
- exactly one collection-control role.

Run it before and after changing collection membership, paths, repository mappings, categories, remotes, or Skill-link delegation.

## Validation checklist

- collection root has no `.git`;
- exactly one control Project Root;
- canonical index exists and root mirror agrees;
- every active member path exists;
- `source`, `repository_root`, and `managed_scope` have distinct meanings;
- every declared Git root is observed and remote/VCS fields agree;
- every shared projection has the correct type and exact target;
- every remote identity has at most one collection-local checkout;
- optional private distributions have verified private visibility before publication or export;
- third-party pool roots are non-Git and child repositories preserve upstream provenance;
- exports use true sources and stay inside the collection;
- environment-bound Skills declare device/network eligibility and a stop rule without secret values;
- no user-home absolute path appears in portable files;
- no Agent links were created as an initialization side effect.
