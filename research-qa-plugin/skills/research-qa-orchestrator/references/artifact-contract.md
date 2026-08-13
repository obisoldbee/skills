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
    validation/structural-result.json
```

Attempts 02-04 use the same naming pattern and appear only after a rejection. No attempt 05 is legal.

The root reservation must use `akashic-package-reservation/v2`. Root `manifest.yaml` stays `status: pending` and `formal_absorption: false`; the internal QA result lives in `payload/receipts/run-manifest.json`. This prevents a successful QA candidate from impersonating formal Akashic absorption.

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

Each `contributions/<persona-id>.json` binds its manifest component and contains a distinct author context, non-empty `research_angles`, non-empty `search_terms`, optional `candidate_exclusions`, and `created_at`.

`research-brief.json` binds the exact question SHA and all eight contribution paths/hashes in manifest order. Its integrator context differs from all eight contributor contexts. It contains non-empty search queries, inclusion criteria, exclusion criteria, and `frozen_at`.

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

- `downloaded`: full text, real PDF over 5 KiB, `%PDF`, disk bytes and SHA match;
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
  "recorded_at": "<RFC3339>"
}
```

For reuse, `akashic_lookup.result` is `reused` with an Akashic `source_id`; both download timestamps are null and validation kind is `akashic_reuse`. A lookup match and a download attempt in the same row is always invalid.

`acquisition-summary.json` binds total rows, unique identities, reviewable count, status counts, collector context, and the assertions `all_akashic_lookups_completed: true` and `download_claims_verified: true`.

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
```

`run-manifest.json` contains the internal result:

```json
{
  "schema_version": 1,
  "status": "candidate_success",
  "plugin": {"name": "research-qa-plugin", "version": "0.2.0"},
  "formal_absorption": "not_authorized",
  "plugin_installation": "not_performed",
  "fuxi": "available_not_invoked",
  "research_brief": {"path": "payload/topic/research-brief.json", "sha256": "<sha256>"},
  "reviewable_source_count": 30,
  "reviewable_source_ids_sha256": "<sha256>",
  "source_set_sha256": "<sha256>",
  "experts_passed": 8,
  "receipt_chain_complete": true
}
```

It also binds package identity/date, task/runtime, live rule, material audit, and synthesis audit.

## Expert attempt and coverage

Every attempt receipt binds candidate path/hash, source-set hash, live rule, executor, retry pointer, and a `corpus_delivery` object containing:

```text
frozen_set_path, frozen_set_sha256, source_set_sha256,
reviewable_source_count, reviewable_source_ids_sha256, delivered_at
```

Expert receipts also bind the assigned bundled Skill and `source_coverage_path`/SHA. The coverage JSON names the expert/attempt, source-set hash, exact sorted reviewable source ID list, and completion time. Any missing or extra ID fails the full-corpus gate.

Synthesis receipts replace bundled Skill/coverage fields with exactly eight accepted expert input path/hash and passing-audit bindings.

## Audit receipt

A passing audit requires non-empty `evidence_refs`, independent auditor identity, candidate/receipt/rule hashes, and structured `quality_checks`:

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

Successful stage order is:

```text
run_initialized -> plugin_validated -> live_rule_pinned
-> topic_locked -> topic_experts_completed -> research_brief_frozen
-> collection_started -> akashic_reuse_checked -> collection_completed
-> material_audit_passed -> sources_frozen
-> expert attempt/audit/retry events -> experts_8_of_8_passed
-> synthesis attempt/audit/retry events -> synthesis_passed
-> chain_validated -> success
```

`completion.json` binds the final event-line SHA, reviewable count/roster hash, `topic_experts_completed: 8`, complete Akashic lookup, verified download claims, `experts_passed: 8`, passing synthesis, and completion time.

`candidate_success` requires all of the above. It never proves plugin installation, provider execution beyond the receipted run, Git publication, or formal Akashic absorption.
