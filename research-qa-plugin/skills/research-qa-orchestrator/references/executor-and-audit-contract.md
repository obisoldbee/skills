# Executor and Audit Contract

## Contents

1. Runtime resolution
2. Independence
3. Tool contracts
4. Expert task brief
5. Audit task brief
6. Synthesis task brief
7. Retry behavior

## Runtime resolution

Require `runtime.kind` as an explicit run input. Do not derive it from an environment variable, model name fragment, writing style, or the presence of copied Skills.

| `runtime.kind` | Author executors | Required auditor |
| --- | --- | --- |
| `minimax-code` | MiniMaxCode worker agents | MiniMaxCode built-in default Verifier |
| `codex` | Eight visible Codex tasks routed through `project-handoff` when available | An independent visible Codex audit task with clean context |
| other named runtime | That runtime's available task contexts | That runtime's available independent audit executor |

The coordinator may adapt dispatch syntax to the runtime, but it must preserve artifact paths, input hashes, isolation, attempt limits, and audit decision shape. For Codex, validate real visible-task receipts; hidden subagent IDs are not equivalent evidence. Never claim an executor exists merely because a Skill file was copied. If the runtime cannot supply eight author contexts and an independent audit context, stop with `executor_unavailable` or `auditor_unavailable`.

## Runtime boundary examples

| Example | Resolution |
| --- | --- |
| Example 1: `runtime.kind: minimax-code` and its built-in default Verifier is available | Use that default Verifier; do not create another verifier. |
| Example 2: `runtime.kind: codex` while copied MiniMax persona files are present | Use an independent Codex auditor; copied files do not change the runtime. |
| Example 3: `runtime.kind: another-agent` with only an author context | Stop `auditor_unavailable`; do not self-audit or fall back across runtimes. |
| Example 4: Runtime identity is omitted but the response style resembles MiniMax | Stop for explicit runtime identity; style is not executor evidence. |

## Independence

Apply these rules to material, expert, and synthesis audits:

- The auditor must not be the authoring context for the artifact under review.
- Give the auditor the frozen artifact, declared inputs, source/rule bindings, and audit rubric; do not provide the author's hidden reasoning.
- Give experts the frozen source package and live-rule path, but not other expert outputs or auditor editorial judgments before their first attempts.
- Use eight distinct contexts for Stage 2 topic contributions and eight new distinct contexts for Stage 4 review. Do not reuse the topic, integrator, collector, or material-auditor contexts as expert review contexts.
- Give a retrying expert only its own previous artifact, the audit rejection, unchanged frozen inputs, and the live-rule path.
- Record executor identity, context identifier when available, runtime kind, start/end times, and exit/result state.
- A deterministic validator process is not a semantic auditor.

## Tool contracts

### Topic expansion executor

- Purpose: independently add research angles, search terms, and exclusions before literature search.
- Use when: after the user question is locked and before the research brief is frozen.
- Parameters: locked question, exclusions, output language, one manifest-bound persona Skill, and a unique context ID.
- Returns: one contribution JSON with Skill bindings and non-empty additions.
- Failure handling: reject empty, unbound, duplicate-context, or missing contributions.
- Stop rule: do not start source collection until all eight contributions and the separate integrator brief are frozen.

### Source acquisition executor

- Purpose: derive stable publication identities, query Akashic first, gather candidate records, and save lawfully accessible material with truthful receipts.
- Use when: before material audit.
- Do not use when: expert analysis has begun for the current frozen source version.
- Parameters: frozen research brief, Akashic registry root, `paper-downloader` or equivalent lawful acquisition route, local read roots, network authority, and candidate output directory.
- Returns: inventory rows, per-source Akashic lookup/acquisition receipts, retained payloads, search/access logs, failures, and hashes.
- Failure handling: preserve per-source failures; never download an exact Akashic match; never label HTML, a landing page, or an intended filename as downloaded.
- Stop rule: access-control bypass, unsafe request, or inability to produce an auditable inventory.

### Semantic auditor

- Purpose: make material decisions for source reviewability and candidate-output decisions for evidence support, boundaries, and contract compliance.
- Use when: after source acquisition, after every expert attempt, and after every synthesis attempt.
- Do not use when: it would audit its own authored artifact or when runtime independence is unproven.
- Parameters: the exact artifact, frozen input bindings, pinned rule path/hash, relevant receipt, and audit rubric.
- Returns: one JSON decision object with `pass|reject`, findings, evidence references, required changes, auditor identity, and input/output hashes.
- Failure handling: tool failure is not rejection and not pass; record `audit_execution_failed` and stop or re-dispatch to an equivalent independent auditor within the same runtime.
- Stop rule: do not retry an unavailable audit route more than once without a material runtime change; never fall back across runtimes implicitly.

### Deterministic validator

- Purpose: check paths, hashes, counts, schemas, and chain continuity offline.
- Use when: validating the plugin or a completed candidate run tree.
- Do not use when: deciding scientific validity or writing conclusions.
- Parameters: `plugin [--plugin-root PATH]` or `run --package ABSOLUTE_PATH [--plugin-root PATH]`; return shape is defined in the core Skill.
- Failure handling: fix the named file/receipt mismatch; do not waive it with prose.
- Stop rule: unchanged validator input gets no retry.

## Expert task brief

Construct every expert attempt from these flat labeled sections. Substitute only values from the validated manifest and current run.

```text
Background:
This is attempt {{attempt_no}} for expert {{expert_id}} in candidate package {{package_id}}. Passing requires a separate audit. File creation or task return is not acceptance.

Materials:
- Bundled expert Skill: {{plugin_relative_skill_path}}
- Declared expert Skill SHA-256: {{expert_skill_sha256}}
- Frozen source inventory: {{package_relative_inventory_path}}
- Frozen source-set SHA-256: {{source_set_sha256}}
- Reviewable source count: {{reviewable_source_count}}
- Reviewable source roster SHA-256: {{reviewable_source_ids_sha256}}
- Frozen-set path and SHA-256: {{frozen_set_path}} / {{frozen_set_sha256}}
- Live Akashic rule path: ${HOME}/Documents/Akashic/90-project-rules/current/05-文献分级与创作.md
- Required live-rule SHA-256 baseline: {{rule_sha256}}
- For retry only: {{previous_attempt_path}} and {{rejection_decision_path}}

Task:
Independently review the frozen research source set from the perspective contract in the assigned bundled Skill. Produce one candidate expert report; do not synthesize other experts.

Constraints:
- Read the assigned bundled Skill from its relative path; do not simulate the persona from memory.
- Read the live Akashic rule yourself and calculate its SHA-256. Stop on mismatch with the baseline.
- Cite only frozen source IDs. Respect abstract-only limits and local-rule fields.
- Review every ID in the delivered reviewable-source roster and write the exact coverage JSON; a selective subset is not a completed lane.
- Separate evidence, attributable opinion, inference, conflicts, counterexamples, limits, and falsification triggers.
- Do not read other expert drafts. Do not give personal medical instructions.
- Write only the declared attempt file and receipt inside the package.

Output format:
- Candidate Markdown with fixed sections for claims, cited evidence, conflicts/limits, counterexamples, non-evidence opinion, and unresolved questions.
- Coverage JSON listing the exact sorted reviewable source IDs.
- JSON receipt conforming to artifact-contract.md.
- Output language: {{output_language}}.

Success criteria:
- Exact input/rule/Skill hashes are recorded.
- Every material claim points to a frozen source ID.
- Corpus delivery and source coverage hashes bind the same frozen set used by every other expert.
- The report is ready for independent audit, but does not call itself accepted.
```

## Audit task brief

Use the same shape for material, expert, and synthesis audit; supply the relevant rubric.

```text
Materials:
- Candidate artifact and its SHA-256
- Frozen direct inputs and SHA-256 bindings
- Live Akashic rule path and required baseline SHA-256
- Author receipt
- Audit rubric for this artifact type

Task:
Independently audit the candidate artifact. Return exactly one decision: pass or reject.

Constraints:
- Do not rewrite the artifact.
- Verify source and rule bindings by readback.
- Reject unsupported claims, missing boundaries, receipt mismatches, unsafe advice, or use of unaudited inputs.
- Reject empty, obviously thin, boilerplate, or semantically defective output even when a file and receipt exist.
- For expert output, confirm the declared bundled Skill was read and its hash matches the source manifest.
- For synthesis, confirm exactly eight passing expert inputs and no rejected draft was used as evidence.
- Do not emit partial_pass.

Output format:
JSON with schema_version, artifact_type, artifact_id, attempt, decision, findings, required_changes, non-empty evidence_refs, quality_checks, auditor, input_sha256, artifact_sha256, Akashic rule binding, and decided_at. Every required quality check must be true for `pass`. Set `auditor.kind` to the explicit runtime route (`minimax-default-verifier`, `codex-independent`, or another named independent auditor), not a generic or cross-runtime fallback.

Success criteria:
- Decision is evidence-backed and structurally complete.
- pass has no required_changes.
- reject has at least one finding and one concrete required change.
```

## Synthesis task brief

```text
Materials:
- Eight accepted expert artifact paths, hashes, and passing audit paths/hashes
- Frozen source-set path and SHA-256
- Live Akashic rule path and baseline SHA-256
- Previous synthesis plus rejection, for retries only

Task:
Produce one candidate synthesis from exactly eight audited passing expert outputs and the frozen material-audited source set.

Constraints:
- Use no rejected expert draft as evidence.
- Preserve material disagreements, counterexamples, uncertainty, abstract-only limits, and local-rule boundaries.
- Attribute persona/practitioner positions; do not turn them into strong evidence automatically.
- Do not claim installation, formal absorption, publication, diagnosis, or treatment.

Output format:
Candidate report sections: status, one-line conclusion, consensus map, disagreement map, counterexamples, evidence boundaries, position draft, literature matrix, expert contribution matrix, audit trail, pending questions, and candidate-status notice.

Success criteria:
- All eight accepted inputs are traceably bound.
- Every scientific claim points to frozen source IDs.
- The result remains a candidate until a separate synthesis audit passes.
```

## Retry behavior

Attempt 01 has no `retry_of`. Attempts 02–04 require all of:

1. The immediately preceding attempt exists and hashes correctly.
2. Its audit decision is `reject`.
3. The new receipt records the preceding audit SHA-256.
4. Frozen source, rule, and bundled Skill hashes are unchanged.
5. The task brief includes only the lane's own prior artifact and requested changes.

Do not start attempt 05. Do not overwrite an attempt. Do not change a rejection to pass in place. A later pass supersedes earlier candidate content for synthesis selection but does not delete history.
