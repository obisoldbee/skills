# Task materials

Use this routing for a multi-file investigation, acceptance, recheck or training task in an owning Project Root. Follow an explicitly declared project-specific location first; otherwise use `docs/tasks/`. Project-root and `docs/` direct children remain stable navigation and classification entries.

## Locate or create the task

1. Read the current project instructions and `docs/tasks/README.md` when it exists. Locate the task by its scope, business system and existing record, rather than by today's date alone.
2. Continue, retry and add evidence in the same task directory. A new attempt or batch may use a subdirectory inside that task. Only an independent task gets a new bundle.
3. For a new task, use `docs/tasks/YYYY-MM-DD-type-topic-HHMMSS/`. Types may include investigation, acceptance, recheck and training, including the project's Chinese equivalents. Use the user/project-declared timezone and record it in the task README; if none is declared, record the host timezone used.
4. Reserve the exact task directory with exclusive creation. On a name collision, inspect the existing entry first; reuse it only for the same task, otherwise append a short task ID and reserve another name. A prior existence or hash check alone is not exclusive creation.
5. Create the task README and only the files needed for this task. Create `docs/tasks/README.md` as navigation with the first actual bundle. One integrator updates that index when a task is added or navigation changes.

Do not prebuild empty task trees during initialization. A short task may use a single task README. Response-only work creates no records, and update-only work retains its own stop boundary.

## Minimal bundle

```text
docs/tasks/
├── README.md
└── YYYY-MM-DD-type-topic-HHMMSS/
    ├── README.md
    ├── report.md          # only when a separate report is useful
    ├── evidence/          # only when evidence is collected
    └── attachments/       # only when attachments are needed
```

The task README is the resumption entry. Record the goal, authorized scope, business system or institution when relevant, source path and observed revision, runtime/environment, current progress, result links, unresolved items and next action. Mark missing revision or environment facts as unknown rather than inventing them. Record evidence collection times. Verification results and the user's acceptance decision each need their own actual evidence.

An optional starting template follows. Omit irrelevant fields rather than leaving a large empty scaffold.

```markdown
# Task title

- Goal and scope: ...
- System / institution: ...
- Source path and observed revision: ... / unknown
- Environment and timezone: ... / unknown
- Progress: in progress / blocked / completed
- Results and evidence: [report](report.md), collected at ...
- Verification result: ... / not yet verified
- User acceptance: ... / awaiting a decision
- Unresolved items and next action: ...
```

Create a linked report before adding its link. The task index can use a small table with task, scope, status and entry columns; link historical bundles at their current paths. It is navigation, not a second evidence ledger. One task owner maintains the bundle entry, and one integrator reconciles shared navigation. Independent files use no-clobber creation; concurrent tracked-file edits follow [worktree collaboration](worktree-collaboration.md).

## Keep each kind of output in its place

| Material | Destination |
|---|---|
| Related reports, screenshots, logs, raw feedback, exports and receipts for one task | The same `docs/tasks/<task>/` bundle |
| Standalone specifications, plans, research, code reviews and reports | Existing `docs/specs/`, `docs/plans/`, `docs/research/`, `docs/reviews/`, `docs/reports/` categories |
| Review attachments | Existing `docs/reviews/artifacts/` convention |
| Source, reusable scripts, build environments and SDK caches | The mapped source/runtime location, normally under `src/`; link the exact location from the task entry |
| A one-off evidence collection script | May accompany the task evidence; running it still follows the task's execution authority |
| Decisions and collaboration history | `conversation/` |
| Cross-task continuity | Project-owned `memory/` under the current authorization |

Preserve original inputs and collected evidence. New evidence gets a unique name; read an existing file before an authorized continuation or new version. Inputs already outside the bundle stay there and are linked from its entry. Keep source materials alongside derived reports through their original paths. Clone, build and installation follow the current task's scope.

## Existing projects and historical bundles

Updating this Skill changes its source guidance and future generated entries. It does not rewrite existing project instructions, managed contract hashes, task indexes or material paths. An explicitly authorized initialization/adoption includes the brief self-contained routing in its generated AGENTS block, so another Agent can use it without an installed copy of this Skill. Existing README and task-index content remain preserved by adoption.

For existing projects, apply routing guidance only within the named maintenance authority. Link legacy bundles in place. Physical migration requires a separately authorized exact move plan, checks of active processes and path references, and post-move verification under [migration guidance](migration-guide.md). Preserve the bundle's names, contents and internal structure, including historical runtime, SDK and script evidence. Recheck path dependencies before running anything from such a bundle.
