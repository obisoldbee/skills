# Batch Profiles

`plan_batch.py` uses one generic pipeline. A profile changes route hints and batch cadence; it never selects a separate crawler implementation.

## Generic profile

- Accepts any public `http(s)` URL.
- Starts with a WorkBuddy-compatible `playwright` plan. The supplied implementation must pass exact hash identity and redirect/rebind compatibility gates before execution.
- Creates one independent case per URL.
- Uses serial execution by default; preserves completed/blocked cases during resume and keeps successful execution at `pending_quality` until assessment.

## Shoulong profile

- Matches `chinalowcarb.com` URLs.
- Uses the same `run_workbuddy_capture.py` wrapper, `capture_pipeline.py` gate, media inventory, and media-understanding route.
- Adds batch fields: `continuity_key`, `source_list_ref`, `cursor`, `resume_policy: preserve_terminal_states`, and `max_workers: 1`.
- Preserves continuous/list-page discovery as a workflow concern. A caller may add URLs to a batch only through explicit authorized discovery; the profile does not crawl a list page or maintain a second fetch engine.

For both profiles, `planned`, `pending_quality`, `captured`, `blocked`, and `failed` are case-local states. Exit code 0 from capture can produce only `pending_quality`; `captured` requires a same-case `evidence-assessment/v2` with `case_binding.valid: true`, `page_purpose_ready: true`, and a passing final evidence state. A missing, failed, or mismatched assessment leaves the case pending. Do not re-run a terminal `captured` case simply because another item failed.
