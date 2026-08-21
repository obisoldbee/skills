# Workspace Contract

Use this reference for layout, provenance, state, and integrity decisions. Use
`operations.md` for exact CLI sequencing.

## Contents

1. Scope selection
2. Portable layout
3. Source records
4. Work artifact records
5. Current and archived versions
6. Conversation and memory
7. Privacy and provider boundary
8. Validation and failure rules

## 1. Scope selection

A document workspace is one user-selected file boundary whose primary deliverables are documents
and work records. It may be a Project Root or a nested work package, but this Skill never decides
that from folder names, dates, event labels, a `.git` entry, or nearby projects.

Freeze one exact real directory before inventory. Reject a linked root or linked intermediate.
Do not scan parents or siblings to “find” a better root. If the selected directory collides with a
managed top-level path, stop and ask whether to select a nested work package; do not merge or
rename the collision.

## 2. Portable layout

```text
<workspace>/
├── INDEX.md
├── control/
│   ├── workspace.json
│   ├── current.json
│   ├── sources/<source-id>.json
│   └── artifacts/<artifact-id>.json
├── raw/as-received/
│   ├── adopted/<original-relative-path>
│   └── imported/<source-id>/<received-name>
├── work/
│   ├── derived/
│   └── drafts/
├── formal/current/<version-id>/
├── archive/versions/<version-id>/
│   ├── record.json
│   └── files/
├── conversation/
└── memory/
    ├── daily/YYYY-MM-DD.md
    └── MEMORY.md
```

- `INDEX.md` is navigation, not evidence.
- `control/` is machine-readable provenance and state. Managed control transitions may replace
  only their exact expected prior bytes after plan-token verification.
- `raw/as-received/` contains received bytes. It is immutable by contract and checked by hash.
- `work/derived/` contains rebuildable OCR, ASR, analysis, transformation, and QA files.
- `work/drafts/` contains revisable deliverables. A draft is never current by implication.
- `formal/current/` contains only files in the explicit approved `control/current.json` record.
- `archive/versions/` is append-only history for rejected and superseded versions.
- `conversation/` records decisions; `memory/` separates dated activity from curated lessons.

Names stored in records are slash-separated workspace-relative paths. Reject absolute paths,
drive/UNC paths, `..`, links, control characters, case-only collisions, Windows device names,
and trailing spaces or dots. Never store a machine-specific home path in the workspace contract.

## 3. Source records

One `control/sources/<source-id>.json` record owns one preserved raw file and includes:

| Field | Meaning |
|---|---|
| `original_relative_path` | Portable received/adopted label; never a local absolute path |
| `current_relative_path` | Exact preserved file under `raw/as-received/` |
| `type_class` | Operational extension class, including `unclassified`; not a truth or reliability inference |
| `source_class` | Receipt route such as local existing, chat attachment, recording, or upstream derived |
| `source_mode` | `adopted`, `explicit-attachment`, or `explicit-in-workspace` |
| `byte_size`, `sha256` | Integrity baseline from received bytes |
| `received_at` | When received, or `unknown` |
| `event_at` | When the represented event occurred, or `unknown` |
| `imported_at` | Known timestamp of workspace preservation |
| `reliability` | `unknown`, `unverified`, `user-confirmed`, or `verified` |
| `derivation_links` | Earlier source/artifact IDs, or `["unknown"]` when upstream lineage is unavailable |
| `status` | Always `preserved` for raw sources |

`raw/as-received` means byte-preserved received input. It does not mean accurate, authoritative,
originally human-authored, or suitable for a decision. A phone or AI summary remains received raw
material while being classified `upstream-derived` and `unverified`.

File extensions do not prove media type, authorship, reliability, or factual content. Known
extensions select an operational class; `.wps` maps to `document`. A portable, readable regular
file with an unknown suffix is still received evidence: preserve it as
`type_class=unclassified`, keep reliability explicit, and require a separately authorized
format route before semantic reading, conversion, artifact registration, or formal use. Never
silently relabel it. If a later package version recognizes that suffix, the historical source
record remains `unclassified`; register only a separately produced work artifact with the newer
classification.

A visible attachment chip, cached preview, URL, or transcript text is not a preserved file. The
`preserve` operation accepts only one explicitly named, real, readable regular file; it does not
search attachment caches. Missing, linked, directory, unreadable, or other non-regular inputs
return `not_preserved` and create no record. An unknown extension alone is not a refusal.

If the received file already sits inside the selected workspace, preserve permits exactly that
one currently unpreserved file and requires `original_relative_path` to equal its actual relative
path. Any additional unpreserved file remains a collision. The received file stays in place and
is also copied into raw with `source_mode=explicit-in-workspace`.

An inventory or preservation refusal never authorizes moving a source, shrinking the exact root,
creating a sibling conflict folder, converting bytes, or excluding the file. Stop with zero
mutation and obtain explicit authority for the exact proposed action. Record only user statements
that actually occurred; leave disputed or unavailable user decisions `unknown`.

## 4. Work artifact records

Domain and format Skills may create files only after their separate scope and authorization. Put
their outputs outside raw, then register each with `artifact`:

- `ocr`, `asr`, `analysis`, `transformation`, and `qa` belong under `work/derived/`.
- `draft` belongs under `work/drafts/`.
- `derivation_links` name exact source/artifact record IDs. Use only `unknown` when lineage is
  genuinely unavailable; never invent a link.
- The artifact record captures relative path, type class, byte size, SHA-256, creation time,
  reliability, kind, derivation, and working/draft status.

A user-named path under `raw/as-received/` identifies source evidence, never a writable target.
Do not change its permissions, edit it in place, or let an office editor save over it. Give the
owning format Skill a distinct versioned output under `work/drafts/` or `work/derived/`, then
register that output with its exact derivation link.

Changing a registered work file invalidates its record. Create and register a new path/version;
do not overwrite a recorded artifact and update history in place.

## 5. Current and archived versions

`control/current.json` has either:

- `status=none`, no outputs, and explicit `unknown` decision fields; or
- `status=approved`, one version ID, one complete conversation record and hash, a decision
  timestamp, and one or more exact output records.

Only `approve` creates approved current outputs, and only from registered drafts. “Newest,”
“latest,” “final,” a filename, a timestamp, a model response, or an export success is not approval.

An archive batch is one immutable `archive/versions/<version-id>/` directory. Its record includes
`rejected` or `superseded`, a non-empty reason, replacement version or `unknown`, timestamp,
conversation record and hash, and every archived file's source path, archive path, size, SHA-256,
artifact ID, and archive method.

- Rejected drafts are copied into the archive; their work copies remain for evidence.
- A superseded version must exactly equal the approved current record. Its managed current copies
  move into the archive after hashing. The current control record clears only after the archive
  directory and bytes read back successfully.
- Never delete, renumber, overwrite, or reuse an archive version ID.
- Never place received or unclassified sources in this version archive. Their evidence store is
  `raw/as-received/`; the archive is only for rejected or superseded deliverable versions.
- If an apply fails with a preserved temporary archive directory, stop. Treat it as collision
  evidence for explicit repair; never auto-clean or continue with a replacement version.

## 6. Conversation and memory

A complete conversation record contains all four sections:

1. agent original proposal;
2. user corrections;
3. rejection or modification reasons;
4. final decision.

`approve` and `archive` require a complete record and bind its SHA-256 so later edits are visible.
The initial `00-workspace-decision.md` is deliberately incomplete until real decisions are known.
Create a complete numbered record with the CLI; never fill unknown history with invented prose.

Append work facts, checks, blockers, and next actions to `memory/daily/YYYY-MM-DD.md`. Distill
stable reusable lessons into `memory/MEMORY.md`. Prefer record IDs and relative links over copied
source passages, personal data, credentials, or full transcripts.

## 7. Privacy and provider boundary

Initialization, adoption, inventory, preservation, and validation are offline filesystem
operations. They may enumerate portable names and read bytes for size, copying, and SHA-256.
They do not authorize semantic document reading, media playback, OCR, ASR, decompression,
external upload, network access, or provider calls.

Obtain separate scope and authorization before those activities. Register authorized outputs
under `work/`, including provider/model provenance in the work record or linked conversation.
Never put agent-produced output into raw.

## 8. Validation and failure rules

Validation rejects:

- missing or linked required paths;
- links or unsupported filesystem nodes anywhere inside the exact root;
- nonportable names, source-record classification mismatches, and unsupported work-product
  extensions;
- unrecorded raw, work, current, or archive files;
- changed/missing raw bytes, artifacts, current outputs, or archived bytes;
- upstream-derived records not marked unverified;
- current files without an explicit approved record;
- archive records without reason, replacement state, timestamp, hashes, or conversation evidence;
- files added outside managed paths that were not preserved during adoption.

Failure is visible and nonzero. Preserve collision and temporary evidence. Do not fall back to a
different root, provider, path, type, version, classification, or sibling folder.
