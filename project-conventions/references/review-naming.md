# Review Naming — Extended Guide

This document provides the complete specification for naming review documents under `docs/reviews/`, including the reviewer/scope vocabulary, collision handling procedures, and a checklist for reviewing agents.

## Naming Pattern

```
YYYY-MM-DD-<reviewer>-<scope>-HHMMSS.md
```

All segments are mandatory. All segments use lowercase ASCII. Segments are separated by hyphens. The `.md` extension is required.

## Segment Specification

### `YYYY-MM-DD` — Review Date

- The calendar date when the review was started (not completed).
- Use the local timezone of the reviewer.
- Example: `2026-07-20`

### `<reviewer>` — Who Reviewed

Lowercase identifier from the vocabulary below. If a review is jointly conducted, use the primary reviewer's identifier.

| Value | Meaning | Typical trigger |
|---|---|---|
| `architect` | Architect agent | Design review, architecture review |
| `engineer` | Engineer agent | Code review, implementation review |
| `qa` | QA agent | Test review, quality review |
| `pm` | Product Manager agent | Spec review, requirement review |
| `security` | Security-focused review | Security audit, vulnerability review |
| `auditor` | Independent audit or third-party review | Cross-document audit, package scan, compliance review |
| `takeover` | Project handover / takeover | When a new agent or person takes over a project |
| `user` | Human user's manual review | When the user personally reviews something |

If the reviewer doesn't fit any of the above, propose a new value and document it here. Use a single lowercase word.

### `<scope>` — What Was Reviewed

Lowercase identifier from the vocabulary below.

| Value | Meaning | Typical content |
|---|---|---|
| `code` | Source code review | Review of implementation files under `src/` |
| `design` | Architecture / design document review | Review of files under `docs/specs/` |
| `pr` | Pull request review | Review of a specific PR or changeset |
| `release` | Pre-release / release readiness review | Review before cutting a release |
| `spec` | Spec document review | Review of a PRD or spec |
| `full` | Comprehensive end-to-end review | Full project review covering multiple aspects |

If the scope doesn't fit any of the above, propose a new value and document it here. Use a single lowercase word.

### `HHMMSS` — Review Start Time

- 24-hour format, second precision.
- Use the local timezone of the reviewer.
- This is the **start time** of the review, not the completion time.
- Example: `143052` = 14:30:52 (2:30:52 PM)

The second-precision timestamp is the primary uniqueness guarantee. Combined with reviewer and scope, collisions become extremely unlikely.

**Relaxation for single-agent projects**: When only one agent (or human) creates reviews, date-precision is acceptable — omit `HHMMSS` and use `YYYY-MM-DD-<reviewer>-<scope>.md`. HHMMSS is mandatory only when multiple agents may create reviews concurrently. If a project transitions from single-agent to multi-agent, existing date-precision files remain valid; new files adopt HHMMSS from that point.

## Examples

```
2026-07-20-engineer-code-143052.md       ← Engineer reviewed code, started 14:30:52
2026-07-20-architect-design-091500.md    ← Architect reviewed design, started 09:15:00
2026-07-20-qa-full-180000.md             ← QA did a full review, started 18:00:00
2026-07-20-takeover-release-235900.md    ← Takeover review for release, started 23:59:00
2026-07-20-security-code-020517.md       ← Security review of code, started 02:05:17
2026-07-20-pm-spec-110030.md             ← PM reviewed a spec, started 11:00:30
```

## Collision Handling Procedure

Even with second-precision timestamps, two agents could theoretically start reviews in the same second, or an agent could resume work after a delay and accidentally reuse a timestamp. Follow this procedure before writing any review file:

### Step 1: Generate the Planned Name

Compute the planned filename using the current date, reviewer, scope, and start time.

### Step 2: Scan the Target Directory

List all files in `docs/reviews/` and check for any file matching the planned name exactly.

### Step 3: Handle Collision

- **No collision**: Proceed with the planned name.
- **Collision exists**: Append a numeric suffix to the new file:
  - First collision: `2026-07-20-engineer-code-143052-1.md`
  - Second collision: `2026-07-20-engineer-code-143052-2.md`
  - And so on.
- Determine the suffix by finding the highest existing suffix for the same base name and incrementing by 1.

### Step 4: Write Immediately

Write the file as soon as it is named. Do not hold a planned name for an extended period — this minimizes the collision window for other agents.

## Reviewing Agent Checklist

Before creating a review document, the reviewing agent should confirm:

- [ ] The `docs/reviews/` directory exists (create if missing).
- [ ] The planned filename follows the `YYYY-MM-DD-<reviewer>-<scope>-HHMMSS.md` pattern exactly.
- [ ] `reviewer` is a valid value from the vocabulary (or a documented new value).
- [ ] `scope` is a valid value from the vocabulary (or a documented new value).
- [ ] `HHMMSS` reflects the actual review start time (not a placeholder).
- [ ] The directory has been scanned for collisions and a suffix applied if needed.
- [ ] The file is written immediately after naming.

## Review Document Content Guidance

While this skill primarily governs **naming**, a well-formed review document should typically include:

1. **Metadata** — date, reviewer, scope, what was reviewed (file paths / PR number).
2. **Findings** — issues found, severity, location.
3. **Recommendations** — suggested changes.
4. **Approval status** — approved / changes requested / blocked.
5. **References** — links to the reviewed artifacts.

The exact content format is left to the reviewing agent's discretion or domain-specific skills (e.g., the `requesting-code-review` skill).

## Common Mistakes to Avoid

| Mistake | Correct approach |
|---|---|
| `2026-07-20-code-review.md` | Use the full pattern: `2026-07-20-engineer-code-HHMMSS.md` |
| `2026-7-20-engineer-code-143052.md` (non-zero-padded month/day) | Always zero-pad: `2026-07-20-...` |
| `2026-07-20-Engineer-Code-143052.md` (uppercase) | Always lowercase |
| `2026-07-20-engineer_code-143052.md` (underscore) | Use hyphens only |
| Placing review file at `docs/code-review-...md` | Always place under `docs/reviews/` |
| Reusing a timestamp from a previous review | Use the actual start time of THIS review |
| Holding a planned name for a long time before writing | Write immediately after naming |

## Migration of Existing Review Files

When encountering review files that don't conform to this naming convention:

1. **Do not rename unilaterally** — other documents may reference the old name.
2. **Propose a migration** listing each file and its target name.
3. **Get user confirmation** before renaming.
4. **Update references** in other documents (README, conversation files, etc.).
5. **Record the migration** in `conversation/` and `memory/`.

### Common Migration Mappings

| Old pattern | New pattern | Notes |
|---|---|---|
| `docs/code-review-2026-07-20.md` | `docs/reviews/2026-07-20-<reviewer>-<scope>-HHMMSS.md` | Determine reviewer/scope from file content |
| `docs/review/2026-07-19-takeover-review.md` | `docs/reviews/2026-07-19-takeover-<scope>-HHMMSS.md` | Scope from content; often `full` for takeover |
| `docs/2026-07-20-review.md` | `docs/reviews/2026-07-20-<reviewer>-<scope>-HHMMSS.md` | Determine reviewer/scope from file content |
| `docs/superpowers/reviews/...md` | `docs/reviews/...md` (renamed) | Move out of superpowers layer + rename |

### Handling Unknown Timestamps in Historical Files

When migrating historical review files, the exact start time (HHMMSS) is often not recorded. Handle this as follows:

1. **Use `000000` as a placeholder** — `000000` signals "time not recorded" to any future reader.
2. **Check for same-day collisions** — if two migrated files share the same date + reviewer + scope + `000000`, the second file gets a `-1` suffix: `2026-07-20-takeover-full-000000-1.md`.
3. **Different dates never collide** — `2026-07-19-takeover-full-000000.md` and `2026-07-20-takeover-full-000000.md` are distinct; no suffix needed.
4. **Document the placeholder** — in the migration record, explicitly note that `000000` means "time unknown" so future readers don't interpret it as midnight.
5. **New reviews must never use `000000`** — always capture the actual start time for reviews created going forward. The `000000` placeholder is exclusively for migrated historical files.

### Determining Reviewer and Scope from File Content

When migrating a file with a non-standard name, determine the reviewer and scope by reading the file content:

| Content signals | reviewer | scope |
|---|---|---|
| Title says "接手 Review" / "Takeover Review" / "Handover" | `takeover` | `full` (usually comprehensive) |
| Title says "Code Review" / focuses on source code | `engineer` | `code` |
| Title says "Design Review" / focuses on architecture | `architect` | `design` |
| Title says "全面 Review" / covers progress + code + bugs | `takeover` or `engineer` | `full` |
| Authored by QA agent, focuses on tests | `qa` | `full` or `code` |
| Security-focused audit | `security` | `code` or `full` |
| User's own review | `user` | varies |

When ambiguous, default to the agent role that authored the review. If the review was done by the agent tool directly (not a specific team role), use the most fitting role from the content (e.g., `takeover` for a comprehensive project review).
