# Benchmark Contract

## Manifest

Use stable IDs and immutable hashes:

```json
{
  "schema_version": "visual-model-benchmark/v2",
  "benchmark_id": "example-20260728",
  "prompt_version": "vu-v1",
  "cases": [
    {"case_id": "VU01", "media_kind": "image", "media_path": "cases/VU01.png", "sha256": "...", "media_type": "image/png"},
    {"case_id": "VV01", "media_kind": "video", "media_path": "cases/VV01.mp4", "sha256": "...", "media_type": "video/mp4", "duration_seconds": 42.3}
  ],
  "participants": [
    {
      "participant_id": "provider-model-version",
      "provider": "provider",
      "model": "model",
      "track": "visual",
      "runner": {
        "adapter": "api",
        "endpoint_ref": "provider-plan-v3",
        "credential_env": "PROVIDER_PLAN_API_KEY"
      },
      "accepts": ["image"]
    }
  ],
  "execution_policy": {"concurrency": 1, "connection_retry_count": 3, "fallback": false}
}
```

## Normalized Results

Keep raw provider artifacts separately. Normalize only enough for comparison:

```json
{
  "schema_version": "visual-model-results/v1",
  "benchmark_id": "example-20260728",
  "results": [
    {
      "participant_id": "provider-model-version",
      "case_id": "VU01",
      "status": "success",
      "output_text": "Exact rendered model output",
      "output_format": "structured_json",
      "machine_usability": {
        "json_parseable": true,
        "schema_complete": true,
        "truncated": false,
        "salvage_required": false
      },
      "failure_type": null,
      "latency_seconds": 12.3,
      "raw_artifact": "results/provider-model-version/VU01/provider.json",
      "raw_sha256": "..."
    }
  ]
}
```

Allowed terminal statuses are `success`, `failed`, and `not_run`. A failed result must keep `failure_type` and may keep a concise error excerpt. A successful result must have non-empty `output_text`.

Use `not_run` with `failure_type: incompatible_media` when a participant cannot accept the case media kind. Never convert a full video to a single frame and call that video understanding unless the benchmark explicitly defines a frame-sampling track.

`output_text` is immutable evidence, not presentation copy. Review builders must derive a non-destructive display projection:

- Structured visual JSON: omit control identifiers and render semantic fields with human labels.
- OCR: remove detection wrappers and coordinates from reading-order text; retain them in the raw artifact or a separate layout structure.
- Never overwrite `output_text` with the display projection.
- Default detail views show the readable projection; exact `output_text` is revealed only through an explicit raw-evidence action.

The exact result key is `(participant_id, case_id)`. Reject duplicates, unknown IDs, missing pairs, and extra pairs unless the run explicitly records an incomplete state.

For failures, also record `failure_class` as `connection_or_access`, `provider_or_model_returned_failure`, or `unclassified_failure`, and preserve `retry_count`. Do not convert connection failures into a capability score of zero. See [evaluation-policy.md](evaluation-policy.md).

## Human Rankings

```json
{
  "schema_version": "akashic-visual-output-review-rankings/v1",
  "benchmark_id": "example-20260728",
  "scoring_method": {"rank_1_points": 3, "rank_2_points": 2, "rank_3_points": 1},
  "case_rankings": {
    "VU01": [
      {"rank": 1, "participant_id": "participant-a", "track": "visual", "points": 3},
      {"rank": 2, "participant_id": "participant-b", "track": "visual", "points": 2},
      {"rank": 3, "participant_id": "participant-c", "track": "ocr", "points": 1}
    ]
  },
  "leaderboard": []
}
```

Store real participant IDs even when the page uses blind aliases.
