# Integrated Spark CLI Route

Use this route only for bounded, mechanical, read-only work.

## Contents

1. Surface guard
2. Executor contract
3. Bundled executor
4. Good Spark tasks
5. Do not send to Spark
6. Prompt requirements
7. Result shape
8. Main-agent duties
9. Failure handling

## Surface guard

Spark has exactly one authorized surface in `project-handoff`: the bundled CLI wrapper below. Never call `create_thread`, `fork_thread`, `handoff_thread`, `send_message_to_thread`, or any other visible-task API for Spark, even if its schema advertises the model. Never lower, omit, or negotiate away `xhigh`.

Before execution, validate an `initial_dispatch` / `run_bundled_spark_cli` receipt with `tool: scripts/run-spark-cli.sh` through `scripts/validate_dispatch_route.py`. A valid receipt must resolve to `gpt-5.3-codex-spark`, `xhigh`, and `bundled_cli`.

## Executor contract

| Field | Value |
|---|---|
| Model | `gpt-5.3-codex-spark` |
| Reasoning | `xhigh` |
| Context | ephemeral |
| Sandbox | read-only |
| CLI state | private temporary `CODEX_HOME`, removed on exit |
| Result owner | main Controller/agent |
| Visible task | no |

Do not route final product judgment, user-position decisions, formal writes, secrets, private chat exports, medical conclusions, deployment, or publication to Spark.

## Bundled executor

`project-handoff` owns this branch end to end. Resolve the skill directory containing `SKILL.md`, then invoke:

~~~sh
<skill-root>/scripts/run-spark-cli.sh --cwd /absolute/workspace --prompt-file /absolute/prompt-file.md
~~~

The bundled wrapper pins `gpt-5.3-codex-spark`, `xhigh`, `--ephemeral`, read-only sandboxing, disabled concurrent reasoning summaries, and prompt input through stdin. It creates a mode-`0700` temporary `CODEX_HOME`, copies only readable `auth.json` with mode `0600` when present, ignores user config, never copies live state/session/cache files, and removes the temporary home on exit. Never add writable sandbox flags, `--add-dir`, or bypass flags.

This integration was derived from an earlier project-local Spark workflow. That historical source is provenance only, not a runtime dependency or a portable path contract.

## Good Spark tasks

Use one short-lived run for bounded, non-judgmental work such as:

- classify `git status --short` into explicit review buckets;
- parse JSON, JSONL, YAML, or frontmatter and report failures;
- check names, paths, hashes, counts, required fields, and duplicate ids;
- run deterministic validators and summarize exact pass/fail output;
- inspect queue, batch, manifest, or registry consistency;
- produce a non-authoritative checklist, migration table, or candidate discrepancy list;
- perform a small read-only smoke test with an exact response contract.

Portable examples include:

- inspect a package manifest's shape and status;
- compare skill registry entries with paths, required fields, dependencies, and route indexes;
- count workflow batches or list mechanical queue inconsistencies;
- scan generated indexes for malformed YAML, missing paths, duplicate sources, and broken links;
- audit workstream counts, frontmatter, JSONL, target references, blank decision cells, and source/raw untouched checks without making semantic decisions.

## Do not send to Spark

Do not assign Spark final authority over:

- user stance, correction writeback, product decisions, semantic truth, or final acceptance;
- medical, legal, financial, or other high-stakes conclusions;
- formal absorption, deployment, publication, or any write;
- deleting, moving, renaming, or editing original/raw files;
- secrets, credentials, private chat exports, account identifiers, or broad history dumps.

Spark may return a candidate table for main-agent review when judgment is explicitly reserved to the Controller.

## Prompt requirements

Include:

1. exact workspace;
2. exact files or directories;
3. read-only mode;
4. prohibited actions;
5. output fields;
6. evidence rules;
7. file/runtime/finding budget;
8. `BLOCKED` or `NEEDS_CONTEXT` stop behavior.

## Result shape

~~~text
status: DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT
files_inspected:
commands_run:
findings:
confidence:
needs_main_agent_decision:
risks:
recommended_next_step:
~~~

For a pure connectivity smoke test, require exactly `OK` and prohibit file inspection, tools, and additional text.

## Main-agent duties

- Pre-screen the exact files and prompt before the provider call.
- Keep immediate critical-path work local and avoid duplicate assignments.
- Review the complete Spark result before adopting any finding.
- Perform all writes, final validation, and judgment locally.
- For a run that materially affects conclusions, record assigned scope, adopted/rejected findings, and result status in the Controller's durable routing log.

## Failure handling

- If the bundled wrapper or `codex` CLI is unavailable, stop and report the missing executor. Do not describe that as proof that the Spark model is unavailable.
- A Desktop/API `unsupported_parameter`, `invalid_request`, or `reasoning.summary` rejection is `wrong_surface_or_request` evidence. It says nothing about Spark availability and never authorizes a second visible task with reasoning removed or changed.
- Report Spark unavailable only after a correctly validated bundled-CLI attempt returns an `unsupported_route` or `provider_model` failure and `scripts/validate_dispatch_route.py` returns `spark_unavailable_supported: true` for the failure receipt.
- Before invoking Spark, keep work local when a deterministic validator fully answers the request.
- Once the wrapper starts, every nonzero exit ends the Spark lane. Treat `PROJECT_HANDOFF_SPARK_TERMINAL_FAILURE` as binding: record and validate the failure, then call no App task, follow-up, retry, or other model for that lane.
- A fallback description is not route authority. Start another route only after a new user message explicitly selects or authorizes it.
- Never add writable sandbox flags, bypass flags, or broad directories.
- Review the complete result locally before adopting any finding.
