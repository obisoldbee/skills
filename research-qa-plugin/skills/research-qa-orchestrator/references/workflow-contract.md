# Workflow Contract

## Required inputs

Before a real run, lock these values:

| Field | Requirement |
| --- | --- |
| `task_id` | Stable identifier for the discussion. |
| `research_question` | Exact question, population, context, and outcome boundaries. |
| `exclusions` | Explicitly out-of-scope claims, populations, and source types. |
| `runtime.kind` | Named runtime; never inferred from style or copied files. |
| `output_language` | Default `zh-CN` unless the user chooses another language. |
| `package_date` / `package_id` | New Akashic v2 reservation at `YYYY/MM/DD/<package_id>`. |
| `source_rights` | Lawful network, local-source, and access boundaries. |
| `medical_boundary` | Research synthesis only; no personal diagnosis or treatment. |

Preflight these external dependencies and stop clearly if any required route is unavailable:

- the live Akashic literature registry at `03-metadata/registry/`;
- the live rule `90-project-rules/current/05-文献分级与创作.md`;
- a lawful paper acquisition executor such as `paper-downloader`;
- a visible-task or equivalent runtime route capable of eight independent author contexts;
- an independent semantic auditor for Stages 3 and 4.

## Five-stage DAG

```text
Stage 1: user topic locked
  -> Stage 2: eight independent persona topic contributions
  -> research brief frozen
  -> Stage 3: Akashic-first lookup, search, lawful acquisition, independent material audit
  -> at least 30 unique reviewable publications, then source set frozen
  -> Stage 4: same full frozen corpus delivered to eight clean persona contexts
  -> every expert attempt independently audited; exact 8/8 pass
  -> Stage 5: synthesis from accepted inputs only
  -> independent synthesis audit
  -> structural chain validation
  -> candidate_success
```

No Stage 4 dispatch may occur before `sources_frozen`. No synthesis may occur before `experts_8_of_8_passed`.

## Stage 1: lock the topic

Write `payload/topic/question.json` from the user's request. Record the exact question, language, exclusions, and lock time. A later material change starts a new research brief and source-set cycle; do not rewrite history in place.

## Stage 2: eight-expert expansion

Dispatch exactly the eight manifest experts. Each contribution must:

- run in its own context;
- bind the assigned bundled Skill path and hashes;
- add research angles, search terms, and candidate exclusions;
- avoid reading another expert's contribution before submitting its own.

The topic integrator uses a ninth, separate context and freezes `research-brief.json` with all eight contribution paths and hashes. Missing, duplicate-context, empty, or unbound contributions stop the workflow.

## Stage 3: literature collection and audit

### Akashic-first identity check

Derive one canonical publication identity in this order: DOI, PMID, PMCID, then normalized publication URL. Search the Akashic registry before any network download.

- On an exact Akashic match, reuse the existing source, materialize a hash-equal package payload, and record `access_status: akashic_reused` with `download_attempted: false`.
- On a miss, a lawful acquisition executor may attempt retrieval. Every attempt must occur after the lookup timestamp.
- Never use title similarity alone to declare a match or invent an identifier.

### Honest acquisition states

`downloaded` requires a local PDF larger than 5 KiB, `%PDF` magic, byte count, SHA-256, and a matching acquisition receipt. HTML, a landing page, an intended filename, or a task return is not a download.

`verified_abstract` is not `downloaded`. It requires a retained non-trivial abstract payload, an explicit full-text failure/restriction, and `access_depth: abstract_only`. Unresolved, failed, duplicate, blocked, and non-scholarly rows cannot be reviewable.

### Thirty-publication gate

Count only unique, on-scope scholarly publications with verified identity, retained review payload, explicit access depth, and `reviewable: true`. Duplicate DOI/PMID/PMCID/URL rows count once. A scarcity note never converts 0-29 into a pass.

An independent material auditor must verify:

- all Akashic lookups and reuse claims;
- every `downloaded` disk readback;
- canonical identity uniqueness;
- the 30-publication threshold;
- corpus completeness and rule fields.

Only after that audit passes may the coordinator freeze `inventory.jsonl`, acquisition receipts, payloads, logs, and `acquisition-summary.json` into one source-set hash.

## Stage 4: full-corpus expert review and audit

Start exactly eight clean author contexts, one per manifest persona. Their initial context IDs must be distinct from each other and from Stage 2, collection, and material-audit contexts.

Every expert receives the same frozen-set path/hash, reviewable-source roster hash, count, and live-rule baseline. Each attempt must produce a coverage artifact listing every reviewable source ID. A passing report must be substantive, traceably cited, uncertainty-aware, counterevidence-aware, and within the medical boundary.

Every attempt is a candidate until an independent semantic auditor returns `pass`. The audit context cannot overlap any author or earlier-stage context. Legal attempt numbers are 01-04: one initial attempt plus at most three reworks. A rework binds the immediately preceding rejection hash. Attempt 04 rejection produces `expert_exhausted`.

Only exact 8/8 audited passes permit synthesis. File existence, agent launch, task return, or 7/8 is not success.

## Stage 5: synthesis and audit

Synthesize only from:

- the frozen material-audited corpus;
- one accepted passing attempt from each of the eight experts;
- the pinned live-rule version.

Preserve consensus, disagreements, counterexamples, access-depth limits, uncertainty, and attributable opinion. The synthesis author and auditor use contexts separate from all earlier stages. The same 01-04 retry limit applies. `submission.md` becomes byte-identical to the accepted synthesis only after its audit passes.

## Akashic package boundary

Preflight a new `12-agent-submissions/YYYY/MM/DD/<package_id>` path, then reserve it through the Akashic v2 package workflow. A valid run package keeps:

- `.reservation.json` with `lifecycle_state: pending`;
- `manifest.yaml` with `status: pending` and `formal_absorption: false`;
- the QA run manifest at `payload/receipts/run-manifest.json`.

`candidate_success` describes the QA run, not formal Akashic absorption. Never write formal metadata, Wiki, reports, or system layers from this Skill.

## Stop states

Stop without a success report on any of these conditions:

- unsafe medical request or unclear access authority;
- malformed, existing, escaped, symlinked, or unreserved package path;
- invalid plugin or bundled manifest binding;
- missing dependency, auditor, or eight-context runtime capacity;
- live-rule absence or drift;
- incomplete Stage 2 roster or reused context;
- Akashic match followed by a download attempt;
- false `downloaded` claim, non-scholarly counted row, duplicate identity counted twice, or fewer than 30 reviewable sources;
- material audit reject;
- incomplete full-corpus coverage, thin/defective expert output, context reuse, non-pass expert, or exhausted retry chain;
- synthesis reject/exhaustion or incomplete event/receipt chain.

## Boundary examples

| Situation | Required result |
| --- | --- |
| 30 rows share one DOI | One unique publication; `collection_not_ready`. |
| Akashic registry contains the exact PDF | Reuse it, record `download_attempted: false`, do not fetch again. |
| Downloader returned HTML named `.pdf` | Not downloaded; fail the disk/magic gate. |
| 31 publications pass, but one expert coverage file lists 30 | Reject that expert attempt; do not count it toward 8/8. |
| Eight reports exist but share one author context | `expert_context_reuse`; do not synthesize. |
| A 20-character report has a fabricated passing JSON audit | `candidate_too_thin`; structural validation fails. |
| QA chain passes while Akashic root manifest is pending | Valid candidate state; formal absorption remains false. |
| Fuxi validates | Record `available_not_invoked`; never invoke it in this workflow. |
