# Context And GitHub Contract

## Minimum-necessary context snapshot

This candidate does not read or write Akashic itself. Its caller supplies a filtered JSON snapshot. Each record must retain `authority_class`, `evidence_refs`, `sensitivity`, `allowed_use`, `as_of`, and `freshness_state`.

Allowed source priority:

1. `formal_current` project decisions and user rules.
2. `formal_verified_event` with direct-user provenance and valid exact spans.
3. `validated_report_as_of` with an explicit observation date.
4. `draft_context` only as a tentative lead, never as current user fact.
5. `formal_unreviewed` and `external_observation` only as background.

`private` and `restricted` records default to a minimal local summary and `allowed_use: blocked` for provider prompts. If no permitted evidence matches, emit `context_status: context_insufficient`; do not infer an active project, office task, or personal priority.

## GitHub intelligence input

Pass `--repos` a JSON array. One repository snapshot has this minimum shape:

```json
{
  "repo_id": "github:owner/name",
  "repository": "owner/name",
  "source": {"url": "https://github.com/owner/name", "evidence_ref": "...", "observed_at": "2026-07-29T00:00:00Z"},
  "purpose": "candidate capability",
  "discussion_conclusion": {"status": "unknown|researched_candidate|poc_candidate|adopted|rejected", "summary": "...", "evidence_ref": "...", "authority_class": "formal_current|draft_context|external_observation"},
  "metrics_snapshot": {"stars": null, "forks": null, "watchers": null, "observed_at": "2026-07-29T00:00:00Z"},
  "updated_at": null,
  "freshness_state": "unknown"
}
```

`watchers` means the API/source-specific watch/subscriber field; never fabricate it from stars. `updated_at` is the upstream repository update time when observed; `metrics_snapshot.observed_at` is the snapshot time. The Skill performs no GitHub network query, so absent values remain `null` and should yield `research_refresh`, not an adoption claim.

## Action-card fields

Every candidate action card contains `same_as_existing`, `new_vs_existing`, `matched_context_ids`, `matched_repo_ids`, `evidence_refs`, `uncertainties`, `recommendation`, and `user_decision_required`. Valid recommendations include `poc_candidate`, `research_refresh`, `catalog_only`, `rule_candidate`, `duplicate_existing`, `ignore_low_value`, and `reject_conflict_or_risk`.
