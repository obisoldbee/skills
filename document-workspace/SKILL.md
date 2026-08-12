---
name: document-workspace
description: "Create, adopt, operate, validate, or repair one exact file-based document and knowledge workspace while preserving as-received inputs, provenance, drafts, explicit current formal outputs, rejected or superseded versions, conversation history, and curated or daily memory. Use for 文书工作区, 文档资料归档, existing document-folder adoption, chat attachment preservation, document source inventory, draft-to-formal lifecycle, rejection history, document evidence boundaries, scans, recordings, photos, screenshots, PDFs, spreadsheets, transcripts, or AI summaries when the task needs local-first file governance rather than document-format editing itself."
---

# Document Workspace

Govern one exact document workspace or nested work package. Own the workspace lifecycle and
evidence boundary; do not replace project governance, format editors, media interpretation,
domain judgment, or dispatch Skills.

## Freeze scope and privacy first

1. Name one exact workspace path. Do not infer a Project Root, Git repository, or scope from a
   dated, event, customer, or attachment folder.
2. If selecting or restructuring the surrounding Project Root, route that decision to
   `project-conventions`. Use this Skill only after the exact document work package is fixed.
3. Treat initialization and adoption as local structural work. Permit byte reads for size and
   SHA-256 integrity only. Do not semantically read documents, play media, run OCR/ASR, call a
   provider, or upload content without separate scope and authorization.
4. Treat a UI-visible chat attachment as a pointer, not durable evidence. Require one real,
   readable regular file and preserve it before depending on it. If unavailable, report exactly
   `not_preserved` and stop downstream use.
5. Reject links, path escapes, unsupported nodes or file types, unreadable files, collisions,
   and uncertain write boundaries. Never follow, replace, delete, auto-clean, or silently
   reclassify a source.

Read [workspace-contract.md](references/workspace-contract.md) before the first initialization,
adoption, integrity repair, approval, or archive transition. Read
[operations.md](references/operations.md) before running a mutation command.

## Start with inventory, then dry-run

Use the package CLI with Python 3.10+ on macOS/Linux or Python 3.12+ on Windows, with
bytecode disabled. Full apply support requires the guarded filesystem primitives documented in
[operations.md](references/operations.md); unsupported systems refuse before the first write:

```text
python3 -B scripts/document_workspace.py inventory <exact-workspace>
python3 -B scripts/document_workspace.py initialize <exact-workspace> \
  --timestamp <timezone-aware-ISO-8601>
```

The first command is read-only. The second command is also read-only by default and returns a
complete plan plus `plan_token`. Review the inventory, selected root, mode, classifications,
collisions, and actions. Apply only the unchanged plan:

```text
python3 -B scripts/document_workspace.py initialize <exact-workspace> \
  --timestamp <same-timestamp> --apply --plan-token <reviewed-token>
```

For a populated folder, originals stay where they are and byte-identical preserved copies go to
`raw/as-received/`. Mark each known machine-generated summary with repeated
`--upstream-derived <relative-path>` during both plan and apply. The tool records it as
`source_class=upstream-derived` and `reliability=unverified`; raw never means reliable or true.

Stop on a reserved-path collision. Select a nested work package or obtain explicit conflict
resolution; do not merge an unknown layout into the managed one.

## Operate the lifecycle

Follow this sequence:

1. **Receive and preserve.** Run `preserve` for each material attachment before analysis. Record
   portable original/current relative paths, type and source class, byte size, SHA-256,
   received/event/import times, reliability, derivation links, and status. Leave unavailable
   times as `unknown`; never substitute filesystem timestamps.
2. **Analyze or transform outside raw.** Route OCR, ASR, media interpretation, DOCX/PDF edits,
   and domain work to their owning Skills. Put agent-produced OCR, ASR, analysis,
   transformations, and QA under `work/derived/`; put deliverable drafts under `work/drafts/`.
   Register each completed work file with `artifact` before downstream use.
3. **Record the process.** Use `conversation` to preserve the agent's original proposal, user
   corrections, rejection or modification reasons, and final decision. Append dated work facts
   to `memory/daily/`; distill only reusable lessons into `memory/MEMORY.md` without copying
   unnecessary source content.
4. **Approve explicitly.** Use `approve` only for registered drafts and a complete conversation
   record. It creates a hashed `control/current.json` decision and copies the exact version to
   `formal/current/`. Recency, filename, or “final” wording never implies approval.
5. **Archive without loss.** Use `archive --status rejected` for rejected registered drafts. Use
   `archive --status superseded` only for the exact approved current version; the tool moves that
   managed current copy into its no-clobber archive batch and clears the current record after
   hash verification. Every batch records status, reason, replacement or `unknown`, timestamp,
   file hashes, and conversation evidence. Never remove an archive version.
6. **Validate.** Run `validate` after each applied transition. Stop if a raw byte, work artifact,
   current output, archive file, or conversation evidence no longer matches its record.

All mutation commands default to dry-run and require their own unchanged `plan_token` with
`--apply`. Never reuse a token across operations, roots, arguments, or filesystem states.

## Route specialized work

Keep these responsibilities separate:

| Need | Route |
|---|---|
| Select or restructure a Project Root, collection, Git checkout, or Agent link | `project-conventions` |
| Create or edit DOCX and other office documents | `documents` or the applicable document-format Skill |
| Create, inspect, or edit PDFs | `pdf` |
| Interpret recordings, photos, screenshots, scans, audio, or video | `media-understanding` and its routed OCR/ASR provider |
| Decide business, legal, medical, financial, or other domain meaning | The applicable domain Skill and user authority |
| Dispatch or hand off work across Agents/tasks | `project-handoff` or the platform's explicit task tools |

This Skill may register the files and evidence produced by those routes. It does not silently
invoke them, authorize providers, or adopt their judgments.

## Completion report

Report the exact selected workspace, initialization/adoption mode, dry-run token reviewed,
applied actions, source/artifact/version counts, validation result, and unresolved conflicts.
State separately whether any content interpretation, media playback, OCR/ASR, provider call,
upload, Project Root change, Git change, link, installation, or dispatch occurred.
