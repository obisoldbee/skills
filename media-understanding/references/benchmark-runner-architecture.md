# Benchmark Runner Architecture

## One benchmark, separate tracks

Use one immutable manifest and evidence model for image, video, OCR, and document vision. Share case IDs, source hashes, participant IDs, raw artifacts, attempts, reliability, cost fields, machine-usability metrics, human rankings, and final route records. Keep each track's prompt, normalization, review UI, and correctness dimensions separate.

## Participant adapters

Declare exactly one adapter for every participant.

| Adapter | Use when | Required manifest data | Failure handling |
| --- | --- | --- | --- |
| `api` | Direct provider HTTP/SDK call | endpoint reference, model, credential env name, accepted media | Preserve every attempt; retry only declared connection classes. |
| `local_service` | LAN OCR, MinerU, oMLX, or another bound service | exact endpoint reference, health check, concurrency limit, model/service version | Keep an active task on its declared endpoint; respect single-thread services. |
| `subagent` | A model is exposed only through an agent/session runner | model ID, isolated output root, task contract | Isolate each participant; a failure cannot erase other evidence. |
| `manual_return` | UI-only/manual route | delivery packet, return schema, source path | Validate returned case union and preserve the human handoff boundary. |

Provider clients and credentials stay in provider-specific skills or private configuration. This skill coordinates them with stable participant IDs and normalized results only.

## Invariants and stop rules

- Freeze the same task and materials for every participant; keep outputs isolated; record failure and continue only eligible participants.
- Set concurrency per endpoint and resource conflict. A single-memory local OCR service may require serial execution; independent cloud providers may run concurrently only when authorized.
- Do not call a runner without current provider authority, place secrets in manifests, change endpoint/model/media representation as fallback, or rerun verified participant-case successes.
- Record incompatible media as `not_run/incompatible_media`. A frame-only route is not video-native unless the manifest defines a frame-sampling track.
- Use [benchmark-contract.md](benchmark-contract.md), [evaluation-policy.md](evaluation-policy.md), and [benchmark-and-reporting.md](benchmark-and-reporting.md) with the built-in scripts.
