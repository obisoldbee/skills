# Artifact and Receipt Contract

## Plugin package

`plugin.json` follows Agent Plugins v1 and the plugin exposes exactly one first-level Skill:

```text
research-qa-plugin/
  plugin.json
  skills/
    research-qa-orchestrator/
      SKILL.md
      bundled/
        source-manifest.json
        personas/<eight fixed persona trees>/
        fuxi-skill/
```

`bundled/source-manifest.json` uses schema `research-qa-orchestrator/bundled-source-manifest/v1`. It declares exactly `persona-01` through `persona-08` plus `fuxi-skill`, relative targets, file counts, byte counts, `SKILL.md` hashes, and tree hashes. Nested Skills are private runtime materials; Agent Plugins discovers only the immediate orchestrator Skill.

## Akashic v2 candidate tree

```text
12-agent-submissions/YYYY/MM/DD/<package_id>/
  .reservation.json
  manifest.yaml
  submission.md
  payload/
    events.jsonl
    topic/
      question.json
      contributions/persona-01.json ... persona-08.json
      research-brief.json
    receipts/
      run-init.json
      run-manifest.json
      plugin-validation.json
      live-rule.json
      material-audit.json
      completion.json
    runtime-receipts/
      paper-downloader-discovery.json
      acquisition/<source_id>.json
      tasks/<role>-<artifact>.json
    sources/
      inventory.jsonl
      search-log.md
      access-log.jsonl
      acquisition-summary.json
      acquisition-receipts/<source_id>.json
      files/<retained payloads>
      frozen-set.json
    experts/<persona-id>/
      attempt-01.md
      attempt-01.coverage.json
      attempt-01.receipt.json
      attempt-01.audit.json
      accepted.json
    synthesis/
      attempt-01.md
      attempt-01.receipt.json
      attempt-01.audit.json
      accepted.json
    validation/
      plugin-validator-result.json
      structural-result.json
```

Attempts 02-04 use the same naming pattern and appear only after a rejection. No attempt 05 is legal.

The root reservation must use `akashic-package-reservation/v2`. Root `manifest.yaml` stays `status: pending` and `formal_absorption: false`; the internal QA result lives in `payload/receipts/run-manifest.json`. This prevents a successful QA candidate from impersonating formal Akashic absorption.

## Plugin validation receipt v2

`payload/receipts/plugin-validation.json` uses `research-qa-orchestrator/plugin-validation-receipt/v2`. It must bind:

- the complete runtime tree consisting of `plugin.json` plus every regular file below the orchestrator Skill, with file count, total bytes, and tree SHA-256;
- explicit SHA-256 values for `plugin.json`, the orchestrator `SKILL.md`, workflow/executor/artifact/external-executor contracts, validator, bundled verifier, and bundled source manifest;
- the complete bundled tree count/bytes/hash and bundled manifest path/hash;
- validator path, SHA-256, exact argv-style command, and a package-confined `plugin-validator-result.json` path/hash whose parsed JSON equals a fresh plugin validation result; and
- a separate current Git observation object: `repository_present`, `repository_root`, `head_commit`, `runtime_tree_tracked`, and `package_dirty`.

Git fields are independent observations, not a combined PASS label. When Git is unavailable, commit/tracked/dirty are null. A clean checkout records `package_dirty: false`; do not preserve a static string such as `Git-untracked 30/30 PASS` or infer dirty state from package history.

## Topic artifacts

`question.json` contains:

```json
{
  "schema_version": 1,
  "initiated_by": "user",
  "question": "<non-empty question>",
  "output_language": "zh-CN",
  "exclusions": [],
  "locked_at": "<RFC3339>"
}
```

Each `contributions/<persona-id>.json` binds its manifest component and contains a distinct author context, package-relative runtime operation receipt path, non-empty `research_angles`, non-empty `search_terms`, optional `candidate_exclusions`, and `created_at`.

`research-brief.json` binds the exact question SHA and all eight contribution paths/hashes in manifest order. Its integrator context differs from all eight contributor contexts and binds its own runtime operation receipt. It contains non-empty search queries, inclusion criteria, exclusion criteria, and `frozen_at`.

## Runtime operation receipt

Every topic expert, integrator, source collector, material auditor, expert author/auditor, and synthesis author/auditor binds one `research-qa-orchestrator/runtime-operation-receipt/v1` file below `payload/runtime-receipts/`. It records `evidence_origin: runtime_tool_result`, runtime, role, operation ID, `status: succeeded`, runtime-backed context ID, artifact path/SHA, and ordered start/end timestamps.

For Codex it additionally contains the normalized claimed `create_thread` result and result readback for the same thread/host and artifact hash. Hidden subagent fields, path-like IDs, queued/unconfirmed creation, or missing readback are invalid. Other runtimes require a named provider operation, provider receipt ID, and successful result state. These are package-local normalized records: offline validation can establish only their structural and byte-binding consistency. They are not independent host attestation and cannot set `runtime_execution_verified: true` or overall run success.

## Source inventory

Every `inventory.jsonl` row includes:

```text
source_id, title, authors, year, source_type, document_kind,
publication_identity, doi, pmid, pmcid, original_publication_url,
source_origin, local_source_path, online_source_url,
access_depth, access_status, download_attempted,
local_payload_path, payload_sha256, payload_bytes,
acquisition_receipt_path, akashic_registry_path,
failure_reason, duplicate_of, on_scope, identifier_verified, reviewable,
evidence_quality, usage_role, review_depth, local_grade,
method_flags, funding_flags, diet_flags, record_sha256
```

Canonical `publication_identity` is derived in DOI, PMID, PMCID, normalized URL order. A later row with the same identity must be non-reviewable and point `duplicate_of` to the first row.

Eligible `document_kind` values are scholarly publications: trials, observational studies, case reports, mechanistic studies, reviews, meta-analyses, guidelines, consensus statements, preprints, or generic papers. Blogs, videos, product pages, and social posts cannot count.

Reviewable access statuses are:

- `downloaded`: full text, real PDF over 5 KiB, valid `%PDF` header, terminal `%%EOF`, consistent `startxref` plus classic xref/trailer or supported xref-stream structure, and matching disk bytes/SHA;
- `akashic_reused`: full text, exact registry/source path readback, materialized payload hash equals the Akashic source, `download_attempted: false`;
- `verified_abstract`: retained abstract payload of meaningful size, `access_depth: abstract_only`, and an honest non-download state.

All unresolved/failure statuses are retained but cannot count. `record_sha256` hashes the canonical JSON row without that field, with sorted keys and a final LF.

## Acquisition receipt

Every row binds one acquisition receipt:

```json
{
  "schema_version": 1,
  "source_id": "src-001",
  "publication_identity": "doi:10.1234/example",
  "status": "downloaded",
  "download_attempted": true,
  "local_payload_path": "payload/sources/files/src-001.pdf",
  "payload_sha256": "<sha256>",
  "payload_bytes": 12345,
  "akashic_lookup": {
    "performed": true,
    "result": "miss",
    "checked_at": "<RFC3339>"
  },
  "download_started_at": "<RFC3339>",
  "download_completed_at": "<RFC3339>",
  "validation": {"exists": true, "kind": "pdf", "magic": "%PDF"},
  "executor_operation_receipt_path": "payload/runtime-receipts/acquisition/src-001.json",
  "recorded_at": "<RFC3339>"
}
```

For every `download_attempted: true` row, the operation receipt uses `acquisition-operation-receipt/v1` and binds the Paper Downloader Skill hash, actual tool, operation ID, source/publication identity, ordered times, terminal access status, and payload path/hash/bytes. Disk bytes alone do not prove executor execution. For reuse, `akashic_lookup.result` is `reused` with an Akashic `source_id`; both download timestamps and the executor operation receipt path are null, and validation kind is `akashic_reuse`. A lookup match and a download attempt in the same row is always invalid.

`acquisition-summary.json` binds total rows, unique identities, reviewable count, status counts, collector context plus its runtime operation receipt, `executor_operation_receipts_structurally_validated`, `runtime_execution_verified: false`, and the assertions `all_akashic_lookups_completed: true` and `download_payloads_structurally_validated: true`.

## Frozen source set and material audit

`frozen-set.json` contains:

```text
schema_version, inventory_path, inventory_sha256,
tree_hash_algorithm, source_set_sha256,
reviewable_source_count, reviewable_source_ids_sha256,
acquisition_summary_sha256, frozen_at
```

`source_set_sha256` uses the bundled tree-hash algorithm over every regular file below `payload/sources/` except `frozen-set.json`.

`material-audit.json` binds the source-set hash, roster hash, count, acquisition summary, live rule, collector context, independent auditor context, evidence refs, and five passing checks:

```text
akashic_reuse_verified, download_claims_verified,
publication_identities_unique, reviewable_threshold_met, corpus_complete
```

The material audit must pass before the frozen-set event and expert dispatch.

## Run receipts

`run-init.json` binds task/package identity, calendar path, absolute package path, runtime, and the root reservation/manifest hashes:

```text
creation_mode: akashic_v2_reserved
reservation_path: .reservation.json
reservation_sha256: <sha256>
akashic_manifest_path: manifest.yaml
akashic_manifest_sha256: <sha256>
acquisition_executor.name: paper-downloader
acquisition_executor.registered_skill_path: <absolute consumer SKILL.md path>
acquisition_executor.canonical_realpath: <collection>/GitHub/paper-downloader
acquisition_executor.skill_sha256: <canonical SKILL.md sha256>
acquisition_executor.consumer_link_state: linked
acquisition_executor.discovery_receipt_path: payload/runtime-receipts/paper-downloader-discovery.json
acquisition_executor.discovery_receipt_sha256: <sha256>
acquisition_executor.verified_at: <RFC3339>
```

The validator resolves `registered_skill_path` at validation time. It must be a direct Unix symlink or Windows junction to the sibling canonical package's real `SKILL.md`, and the recorded hash must match current canonical bytes. That establishes only `consumer_link_state: linked`. A separate `skill-discovery-receipt/v1` must bind the claimed runtime catalog observation, consumer path, canonical real path, and Skill hash before the receipt is structurally complete; offline output still reports discovery as `runtime_not_verified`. A copied consumer, wrapper projection, former `working-skills` path, missing file, hash drift, or link without a normalized receipt fails before Stage 3.

`run-manifest.json` contains the internal result:

```json
{
  "schema_version": 1,
  "status": "structurally_complete_runtime_unverified",
  "runtime_attestation": {"evidence_scope": "package_local_only", "independent_host_attestation": "not_provided", "runtime_execution_verified": false, "run_success_verified": false},
  "plugin": {"name": "research-qa-plugin", "version": "0.2.0"},
  "plugin_validation": {"path": "payload/receipts/plugin-validation.json", "sha256": "<sha256>", "schema": "research-qa-orchestrator/plugin-validation-receipt/v2", "runtime_tree_sha256": "<sha256>", "git_observation": {"repository_present": true, "repository_root": "<current repo root>", "head_commit": "<current commit or null>", "runtime_tree_tracked": true, "package_dirty": false}},
  "formal_absorption": "not_authorized",
  "plugin_installation": "not_performed",
  "fuxi": "available_not_invoked",
  "research_brief": {"path": "payload/topic/research-brief.json", "sha256": "<sha256>"},
  "reviewable_source_count": 30,
  "reviewable_source_ids_sha256": "<sha256>",
  "source_set_sha256": "<sha256>",
  "acquisition_executor_evidence": {"source_state": "validated", "consumer_link_state": "linked", "runtime_discovery_state": "runtime_not_verified", "discovery_receipt_structurally_validated": true, "operation_receipts_structurally_validated": 30, "runtime_execution_verified": false},
  "experts_passed": 8,
  "receipt_chain_complete": true,
  "runtime_operation_receipts_structurally_validated": 29
}
```

It also binds package identity/date, task/runtime, live rule, material audit, and synthesis audit.

## Expert attempt and coverage

Every attempt receipt binds candidate path/hash, source-set hash, live rule, executor identity plus package-relative runtime operation receipt, retry pointer, and a `corpus_delivery` object containing:

```text
frozen_set_path, frozen_set_sha256, source_set_sha256,
reviewable_source_count, reviewable_source_ids_sha256, delivered_at
```

Expert receipts also bind the assigned bundled Skill and `source_coverage_path`/SHA. The coverage JSON names the expert/attempt, source-set hash, exact sorted reviewable source ID list, and completion time. Any missing or extra ID fails the full-corpus gate.

Synthesis receipts replace bundled Skill/coverage fields with exactly eight accepted expert input path/hash and passing-audit bindings.

## Audit receipt

A passing audit requires non-empty `evidence_refs`, independent auditor identity plus its package-relative runtime operation receipt, candidate/receipt/rule hashes, and structured `quality_checks`:

```text
nonempty, substantive, citations_traceable,
counterevidence_addressed, uncertainty_stated,
medical_boundary_observed,
source_coverage_complete (expert) or expert_roster_complete (synthesis)
```

All required checks must be true. Passing audits have no required changes. Rejections have at least one finding and one concrete required change.

Expert reports must have at least 400 non-whitespace characters and five non-empty lines; synthesis requires at least 800 and five lines. These are only obvious-defect gates. Semantic quality still belongs to the independent auditor.

## Event chain and completion

`events.jsonl` is append-only with contiguous sequence, unique event ID, state continuity, artifact path/hash, previous-line hash, and timestamp.

Structurally complete stage order is:

```text
run_initialized -> plugin_validated -> live_rule_pinned
-> topic_locked -> topic_experts_completed -> research_brief_frozen
-> collection_started -> akashic_reuse_checked -> collection_completed
-> material_audit_passed -> sources_frozen
-> expert attempt/audit/retry events -> experts_8_of_8_passed
-> synthesis attempt/audit/retry events -> synthesis_passed
-> chain_validated -> structure_validated_runtime_unverified
```

`completion.json` binds the final event-line SHA, reviewable count/roster hash, `topic_experts_completed: 8`, complete Akashic lookup, structurally validated download payloads, structurally validated acquisition/runtime-operation receipt counts, `experts_passed: 8`, the package-declared passing synthesis receipt, `runtime_execution_verified: false`, `run_success_verified: false`, and completion time.

All of the above establishes only `structurally_complete_runtime_unverified`. The offline validator deliberately returns `ok: false` and `runtime_not_verified` because package-local JSON cannot independently attest host execution. It never proves candidate success, plugin installation, provider execution, Git publication, or formal Akashic absorption.
