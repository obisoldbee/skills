# Deterministic Operations

Use this reference before any workspace mutation. Run commands from the Skill directory or replace
`scripts/document_workspace.py` with its exact installed path.

## Contents

1. Common contract
2. Initialize or adopt
3. Preserve an attachment
4. Register conversation and work artifacts
5. Approve a current formal version
6. Archive rejected or superseded versions
7. Validate and report
8. Recovery boundary

## 1. Common contract

Every mutating subcommand is a dry-run unless `--apply` is present. A dry-run inventories all
inputs, validates the exact root and boundaries, and emits a SHA-256 `plan_token`. Re-run the same
command with unchanged arguments, `--apply`, and that exact token. Apply recomputes the plan and
refuses a changed filesystem or argument set.

Use Python 3.10 or newer on macOS/Linux. Apply uses a locked exact-root descriptor, guarded
root-relative opens, and atomic no-clobber rename/exchange. Darwin must provide
`O_NOFOLLOW_ANY`, `O_RESOLVE_BENEATH`, and `renameatx_np`; Linux must provide `openat2` and
`renameat2`. The utility probes these boundaries and refuses before writing when they are absent.
Windows is supported for inventory, dry-run planning, and validation with Python 3.12 or newer
for junction detection; version 1 intentionally refuses apply on Windows rather than claim an
unsafe cross-root or no-clobber guarantee.

Use a known timezone-aware ISO 8601 mutation timestamp. `received_at` and `event_at` may be
`unknown`; `imported_at`, conversation, artifact, approval, and archive operations occur now and
therefore require a known timestamp. The examples use synthetic placeholders only.

Do not combine shell discovery, moves, deletions, or glob expansion with these commands. Pass one
exact workspace and explicit paths.

## 2. Initialize or adopt

First inventory:

```text
python3 -B scripts/document_workspace.py inventory <workspace>
```

Plan an empty initialization or populated adoption:

```text
python3 -B scripts/document_workspace.py initialize <workspace> \
  --timestamp 2030-01-02T03:04:05Z
```

For known upstream machine summaries, repeat their exact existing relative paths:

```text
python3 -B scripts/document_workspace.py initialize <workspace> \
  --timestamp 2030-01-02T03:04:05Z \
  --upstream-derived received/summary.txt
```

Review `workspace`, `mode`, inventory counts, every classification, every copy/write action, and
`provider_calls=false`. Apply with the emitted token and identical classification arguments.

Empty folders receive the complete layout. Populated folders retain originals and receive
byte-identical raw copies plus source records. A second identical initialization returns
`already_initialized` after full readback.

## 3. Preserve an attachment

Plan one explicitly named real file:

```text
python3 -B scripts/document_workspace.py preserve <workspace> \
  --source <exact-readable-file> \
  --original-path attachments/received-name.pdf \
  --source-class chat-attachment \
  --reliability unknown \
  --received-at unknown \
  --event-at unknown \
  --timestamp 2030-01-02T03:04:05Z
```

The stored `original-path` is a portable receipt label, never the external absolute path. For an
AI/phone-generated summary use `--source-class upstream-derived --reliability unverified`; add
known source/artifact IDs with repeated `--derived-from` or use no flag when none is known.

If the file is missing, unreadable, linked, not regular, or unsupported, the result is
`status=not_preserved`. Do not quote, analyze, transform, or cite that attachment afterward.

After apply, compare the returned SHA-256 and `current_relative_path`; then run `validate`.

## 4. Register conversation and work artifacts

Create a complete decision record without overwriting an earlier record:

```text
python3 -B scripts/document_workspace.py conversation <workspace> \
  --conversation-id 01-review-decision \
  --timestamp 2030-01-02T04:00:00Z \
  --proposal "Prepared a first draft." \
  --user-correction "Requested a shorter structure." \
  --reason "The first structure duplicated source material." \
  --final-decision "Use the revised concise structure."
```

After an authorized specialized Skill writes a work file, register it:

```text
python3 -B scripts/document_workspace.py artifact <workspace> \
  --path work/drafts/deliverable-v001.docx \
  --kind draft \
  --timestamp 2030-01-02T04:10:00Z \
  --reliability user-confirmed \
  --derived-from src-00000000000000000000
```

Use actual IDs returned by source/artifact records; the zero ID above is only shape notation and
will be refused if no matching record exists. If lineage is genuinely unavailable, omit
`--derived-from`; the record stores explicit `unknown`.

`artifact` permits drafts only under `work/drafts/`; other kinds only under `work/derived/`.
Changing a registered file invalidates validation. Write a new versioned path instead.

## 5. Approve a current formal version

Plan approval from one or more registered drafts:

```text
python3 -B scripts/document_workspace.py approve <workspace> \
  --version-id v001 \
  --file work/drafts/deliverable-v001.docx \
  --conversation conversation/01-review-decision.md \
  --timestamp 2030-01-02T04:20:00Z
```

Approval refuses an incomplete conversation, unregistered or changed draft, occupied current
record, or different current bytes. Apply copies exact bytes under
`formal/current/<version-id>/` and updates the current control record only after readback.

Archive the current version before approving its replacement. Never infer approval from the next
version number or a successful document export.

## 6. Archive rejected or superseded versions

Archive rejected registered drafts while retaining their work copies:

```text
python3 -B scripts/document_workspace.py archive <workspace> \
  --version-id v001 \
  --status rejected \
  --file work/drafts/deliverable-v001.docx \
  --reason "User rejected the structure." \
  --replacement v002 \
  --conversation conversation/01-review-decision.md \
  --timestamp 2030-01-02T04:30:00Z
```

Archive the exact current approved version as superseded; do not pass `--file` because the
complete current record is authoritative:

```text
python3 -B scripts/document_workspace.py archive <workspace> \
  --version-id v002 \
  --status superseded \
  --reason "A later approved version replaced it." \
  --replacement v003 \
  --conversation conversation/02-replacement-decision.md \
  --timestamp 2030-01-03T02:00:00Z
```

The superseded apply moves managed current copies into the archive batch, verifies every hash,
then clears `control/current.json`. It never touches raw or draft source bytes.

## 7. Validate and report

Run:

```text
python3 -B scripts/document_workspace.py validate <workspace>
```

Report the exact root, source/artifact/archive counts, current status/version, integrity outcome,
and any refusal. Also report the unchanged provider boundary: these utilities make no network,
OCR, ASR, media playback, upload, or provider call.

## 8. Recovery boundary

The tools preserve a deterministic `.document-workspace.tmp` archive directory or
`.document-workspace.displaced` control file if a write cannot complete safely. These are
collision evidence, not disposable cache. An atomic control exchange keeps concurrent bytes and
the proposed transition under separate names instead of overwriting either. Stop and inspect the
exact plan, source bytes, destination bytes, control state, and hashes. Do not delete, rename,
resume, or replace that evidence without a separately reviewed repair plan.

Do not hand-edit JSON to make validation green. If raw bytes changed or a version record conflicts,
preserve the observed state and report the exact blocker.
