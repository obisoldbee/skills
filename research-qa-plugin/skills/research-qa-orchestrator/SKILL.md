---
name: research-qa-orchestrator
description: "Run an audited five-stage research QA workflow: lock a user topic, obtain independent additions from eight manifest-bound experts, perform Akashic-first literature search and truthful acquisition, send the complete 30-plus publication corpus to eight clean expert contexts with independent audits, then produce an independently audited synthesis in a pending Akashic candidate package. Use for explicit deep research, literature QA, evidence disputes, or other multi-paper questions where download, citation, and audit failures are costly. Do not use for simple answers, personal diagnosis or treatment, automatic persona distillation, formal Akashic absorption, or research that cannot satisfy the 30-publication hard gate."
---

# Research QA Orchestrator

Background:

Treat this directory as the orchestrator inside an Agent Plugins v1 package. Source presence, local Skill registration, discovery, execution, and formal adoption are separate states.

Produce only a new candidate package under:

```text
${HOME}/Documents/Akashic/12-agent-submissions/YYYY/MM/DD/<new-package-id>/
```

Use an exactly four-digit `YYYY`, exactly two-digit `MM` and `DD`, and a real Gregorian calendar date. Preflight the nonexistent destination with `scripts/validate_research_qa.py destination --package <absolute-package-path>`, then reserve it through the Akashic v2 ordinary-submission workflow. Require `.reservation.json`, `manifest.yaml` with `status: pending`, and `formal_absorption: false`. Never reuse, merge, append to, or overwrite an existing package. Do not escape this hierarchy or write any other Akashic path. A completed QA run remains a candidate submission; it is not formal absorption, Wiki publication, Skill installation, or policy adoption.

Materials:

Before planning or dispatching a real run, read these files completely:

1. [workflow-contract.md](references/workflow-contract.md) — state machine, gates, stop rules, and boundary examples.
2. [executor-and-audit-contract.md](references/executor-and-audit-contract.md) — runtime selection, independent auditor contract, dispatch prompts, and retry rules.
3. [artifact-contract.md](references/artifact-contract.md) — output tree, receipts, schemas, and completion evidence.
4. [external-executors.md](references/external-executors.md) — canonical `$paper-downloader` source binding and runtime preflight.

At runtime, read `bundled/source-manifest.json` relative to this Skill directory. Use it to locate exactly eight expert Skills and one Fuxi Skill. Fail closed if the manifest, any declared file, or any declared SHA-256 binding is missing or invalid. Never discover experts by recursively scanning `bundled/`, guessing names, or using remembered personas.

Success criteria:

- Require at least 30 unique, on-scope, auditor-confirmed `reviewable` publications before entering the expert phase. Fewer than 30 means `collection_not_ready`; a scarcity explanation cannot waive the gate.
- Before search, run all eight experts in distinct contexts to add research angles and freeze a hash-bound research brief in a separate integrator context.
- Query Akashic by canonical publication identity before any download. Reuse exact matches with `download_attempted: false`; never download them again.
- Call a source `downloaded` only after disk readback proves a PDF larger than 5 KiB with `%PDF`, byte count, and SHA-256.
- Run exactly the eight expert lanes declared in the validated bundled manifest. Each lane independently reviews the same frozen source package.
- Require eight distinct clean Stage 4 author contexts and an exact per-expert coverage roster for the complete frozen reviewable corpus.
- Treat every expert output as a candidate. Require a separate auditor decision of `pass` before the output can enter synthesis.
- Allow one initial expert attempt plus at most three rework attempts. Preserve every draft, rejection, requested change, and retry binding. If any expert has no passing attempt after attempt 04, stop without successful synthesis.
- Require 8/8 audited expert passes. Agent launches, task returns, file existence, or 7/8 passes are not success.
- Treat the synthesis as a candidate. Have an independent auditor review it; allow one initial synthesis attempt plus at most three reworks. Publish no successful final report unless an attempt passes.
- Require a complete, internally linked event/receipt/rejection/retry chain before setting `success`.

## Live Akashic rule

Use this live authority, not a bundled copy or frozen ABCX paraphrase:

```text
${HOME}/Documents/Akashic/90-project-rules/current/05-文献分级与创作.md
```

At run initialization, read the file and record its SHA-256 as the run baseline. Require every expert on every attempt to read that exact live path and record path, SHA-256, byte length, and read time in its own receipt. Require synthesis and audit receipts to bind the same baseline. If the live hash differs during the run, record `rule_drift`, stop the current cycle, and start no further expert or synthesis work against mixed rule versions.

Never make a local ABCX summary the permanent authority. Fields and allowed values come from the live file read for that run.

## Runtime and auditor selection

Require an explicit runtime identity; do not infer it from prose or model style.

- For `MiniMaxCode`, use its built-in default Verifier. Do not create or redefine a MiniMax Verifier agent.
- For `Codex`, use an available independent Codex audit executor in a separate clean context from the authoring lane.
- For another agent runtime, use that runtime's available independent audit executor.
- If no independent auditor is available, stop with `auditor_unavailable`. Do not self-approve in the authoring context and do not silently fall back to MiniMax.

Use the same independence rule for source-material review, every expert attempt, and every synthesis attempt. The deterministic validator checks receipts and structure; it never substitutes for semantic audit.

Task:

1. Lock the user question, exclusions, language, runtime, and a new calendar package ID. Preflight the path, reserve it through Akashic v2, and validate the plugin/manifest.
2. Dispatch exactly eight manifest-bound topic experts in eight distinct contexts. Freeze all non-empty contributions into `research-brief.json` using a separate integrator context.
3. Read/hash the live rule. Resolve the registered `$paper-downloader` consumer and verify its real path and `SKILL.md` hash against `external-executors.md`. Derive canonical publication identities and query Akashic before retrieval. Reuse exact matches without downloading; use the verified lawful acquisition executor only for misses. Preserve every outcome and real disk receipt.
4. Have a separate material auditor verify lookup/reuse, download truth, unique identities, eligibility, access depth, and at least 30 reviewable publications. Freeze the source set only after pass.
5. Dispatch the eight manifest-bound experts in eight new clean contexts. Deliver the same full frozen corpus and require exact source-coverage artifacts. Do not expose another expert's draft or audit comments in an initial prompt.
6. Independently audit every candidate attempt. Preserve rejections; allow at most three hash-bound reworks. Stop unless all eight lanes pass.
7. Draft synthesis from the eight accepted outputs and frozen citation-eligible sources only. Preserve disagreement, counterexamples, uncertainty, and rule boundaries.
8. Independently audit synthesis with the same retry ceiling. Make `submission.md` byte-identical to the accepted attempt only after pass.
9. Run `scripts/validate_research_qa.py run --package <absolute-package-path>`. Set internal `candidate_success` only when it returns `ok: true`; keep the Akashic root manifest pending and unabsorbed.

## Fuxi boundary

Validate and inventory the Fuxi entry from `bundled/source-manifest.json`, then record it as `available_not_invoked` for this workflow. Do not invoke it during source collection, expert review, retries, synthesis, or audit. Fuxi is reserved for a separately authorized future persona-distillation task.

## Deterministic validator tool

Use `scripts/validate_research_qa.py` only for offline structural validation.

- Purpose: validate Agent Plugins layout, manifest bindings, package containment, hashes, run receipts, counts, attempt chains, and terminal gates.
- Use when: before a run (`plugin`), before exclusively creating a package (`destination`), and after a candidate run package exists (`run`).
- Do not use when: judging source relevance, evidence quality, expert reasoning, medical safety, or synthesis quality.
- Parameters: `plugin [--plugin-root PATH]`; `destination --package ABSOLUTE_PATH`; `run --package ABSOLUTE_PATH [--plugin-root PATH]`.
- Return: one JSON object on stdout and exit 0 for structural pass; one JSON error object on stderr and nonzero exit for failure.
- Failure handling: do not retry unchanged input. Fix the named structural cause or stop.
- Stop rule: any invalid/unreserved calendar package, path escape, symlink, missing manifest binding, Stage 2 roster/context failure, Akashic redownload, false download, duplicate identity count, count below 30, incomplete corpus coverage, thin output, context reuse, incomplete audit chain, non-pass expert, or non-pass synthesis prevents success.

Constraints:

- Do not provide personal diagnosis, treatment, medication changes, or individualized medical instructions.
- Do not bypass paywalls, access controls, captcha, credentials, or site policies.
- Do not install packages, create symlinks, create `mcp.json`, call unapproved providers, commit Git, or claim external execution from a plan or file.
- Do not trigger Fuxi automatically.
- Do not count duplicates, off-topic rows, blocked leads, unverifiable citations, or unaudited records toward the 30-publication gate.
- Do not download a publication after an exact Akashic registry/source match.
- Do not call HTML, a landing page, an intended filename, or a failed task return a downloaded paper.
- Do not call a run successful because multiple agents started or eight tasks returned.

Output format:

Report the candidate package path and pending Akashic state; plugin validation; Stage 2 eight-context completion; live-rule path/SHA; Akashic reused count; real downloaded count; verified-abstract and failure counts; unique reviewable source count; material-audit decision; all eight Stage 4 context/coverage/attempt/pass states; synthesis attempts and audit decision; validator result; unresolved blockers; and explicit installation/formal-absorption states.
