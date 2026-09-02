# Batch Profiles

`plan_batch.py` creates and resumes deterministic case plans. It does not choose or execute a browser. The current Agent captures each planned case with an authorized available web or browser route, then writes case-local evidence only inside the approved package root.

## Generic Profile

- Accepts any public `http` or `https` URL permitted by intake validation.
- Creates one independent case per URL.
- Uses serial handling by default.
- Preserves completed, blocked, and failed cases during resume.
- Keeps a successful retrieval at `pending_quality` until a matching assessment passes.

## Shoulong Profile

- Accepts `chinalowcarb.com` URLs.
- Adds `continuity_key` and a serial resume policy.
- Treats list-page discovery as a separately authorized workflow. The profile does not crawl a list page or select a second fetch engine.

For both profiles, `planned`, `pending_quality`, `captured`, `blocked`, and `failed` are case-local states. A browser or retrieval success can produce only `pending_quality`; `captured` requires a same-case `evidence-assessment/v2` with valid binding, `page_purpose_ready: true`, and a passing final evidence state. Do not rerun a terminal `captured` case because another item failed.

The historical WorkBuddy adapter is not part of either current profile. Its standalone compatibility executor may be used only when the user explicitly requests that legacy path.
