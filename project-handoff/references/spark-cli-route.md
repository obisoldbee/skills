# Integrated Spark CLI Route

Use this route only for bounded, mechanical, read-only work.

## Contents

1. Surface guard
2. Executor contract
3. Bundled executor
4. Authorization and data boundary
5. Bounded input and output gate
6. Decision examples
7. Good Spark tasks
8. Do not send to Spark
9. Prompt requirements
10. Result shape
11. Main-agent duties
12. Failure handling

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
| Per-tool output | at most `4096` tokens |
| Result owner | main Controller/agent |
| Visible task | no |

Do not route final product judgment, user-position decisions, formal writes, secrets, private chat exports, medical conclusions, deployment, or publication to Spark.

## Bundled executor

`project-handoff` owns this branch end to end. Resolve the skill directory containing `SKILL.md`, then invoke:

~~~sh
<skill-root>/scripts/run-spark-cli.sh --cwd /absolute/workspace --prompt-file /absolute/prompt-file.md
~~~

The bundled wrapper pins `gpt-5.3-codex-spark`, `xhigh`, `--ephemeral`, read-only sandboxing, disabled concurrent reasoning summaries, `tool_output_token_limit=4096`, strict config validation, and prompt input through stdin. It creates a mode-`0700` temporary `CODEX_HOME`, copies only readable `auth.json` with mode `0600` when present, ignores user config, never copies live state/session/cache files, and removes the temporary home on exit. It captures the verbose CLI trace privately: success emits only `--output-last-message`, while failure emits at most the final 8 KiB of diagnostics followed by the terminal marker. Never add writable sandbox flags, `--add-dir`, or bypass flags.

This integration was derived from an earlier project-local Spark workflow. That historical source is provenance only, not a runtime dependency or a portable path contract.

## Authorization and data boundary

The wrapper runs locally, but its prompt and model-read content are sent to the Spark service for inference. Read-only and ephemeral describe execution and local state; they do not mean offline processing or authorize disclosure.

Complete these steps before requesting execution approval:

1. **Bind the task.** Identify the user's requested Spark purpose and selected materials. An explicit request such as “use Spark to inspect this named project/material” authorizes one call with the minimum non-sensitive material needed for that scope, subject to current instructions. Reuse that authority; do not ask the user to select Spark again. A generic request to use Spark does not select additional private histories or authorize sensitive disclosure.
2. **Prepare the input locally.** Read and filter the selected sources in the main agent. For private history or business records, default to task-local aliases such as `R01`, required field names, booleans, counts, and mechanical relationships. Keep the alias-to-source mapping and original evidence locally outside the packet; do not include or reference them in the Spark prompt. Omit original task/thread IDs, personal absolute paths, identifying titles, exact dates, and excerpts unless they are necessary and authorized. Public repository-relative paths and ordinary code identifiers need no automatic redaction. Apply the bounded-input gate below.
3. **Inspect what remains.** Review every packet file and the prompt, including filenames and directory names. Aliases alone do not make data anonymous: workflow descriptions, rare events, health facts, or combinations of metadata may still identify a person or reveal private business information. Preserve the requested question; do not discard essential evidence just to pass this check. Use the table below to decide the next action.
4. **Request only a missing decision.** If approval is needed, finish a concrete, reviewable packet first. State the destination, purpose, file/record scope, remaining sensitive categories, and why those fields are necessary; provide a local preview without echoing sensitive values into the question. Reuse existing permission for the same destination, purpose, materials, and disclosure scope. Changes within that approved scope do not require per-step confirmation; new sensitive categories or broader sources do. A prior approval for another project is not blanket permission.
5. **Dispatch once when authorized.** Validate the dispatch receipt, then invoke the bundled wrapper with the prepared prompt and a neutral packet directory. In a tool approval justification, describe the actual contents and the existing authority; saying “redacted” or “local CLI” is not evidence. Follow any required platform approval process. Do not add a separate user confirmation when the necessary authority is already present.

| Actual input and authority | Next action |
|---|---|
| Public, synthetic, or otherwise non-sensitive material within the user's selected scope; current instructions permit the call | Dispatch with existing authority. No additional disclosure question. |
| Private source; a smaller non-sensitive projection can still answer the assigned mechanical question | Prepare and inspect that projection locally, then dispatch within existing authority. Keep source mapping local. |
| Necessary sensitive content with explicit approval covering this destination, purpose, and disclosure scope; current instructions permit it | Use the approved scope without asking again. |
| Necessary sensitive content lacks that approval, or the shareable source scope remains unclear | Keep dispatch pending and ask one concrete question about the missing scope or disclosure. Continue independent local work. |
| Current instructions prohibit external processing, or input contains secrets, credentials, private chat exports, or another exclusion below | Do not send it through this route. Complete permitted local work and report the boundary. |

Do not treat all metadata as sensitive, or all non-secret metadata as shareable. Judge the actual contents in context. Do not demand a new consent manifest, hash receipt, or approval ceremony for an ordinary authorized non-sensitive check; the existing dispatch receipt and routing log are sufficient. When approval refers to a specific preview, retain that preview and bind the eventual input to the approved scope.

### When platform approval stops dispatch

A pending or denied execution approval is a **pre-dispatch permission stop**. If the wrapper never started, record `provider_started: false` and `attempt_count_started: 0`; do not emit a terminal Spark failure or report Spark unavailable. This state is not a provider failure receipt.

Read the stated reason and preserve the denial. Do not repeat the rejected call, disguise its contents, split the same disclosure into smaller calls, change the surface/model, or weaken sandboxing. Reconsider only when the review permits it and there is new evidence of authorization, new explicit approval, or a materially safer input that removes the rejected disclosure while still serving the task. Explain the changed evidence before resubmitting; renaming IDs alone is insufficient. If the sensitive content remains necessary and unapproved, leave the call pending and ask the specific missing question once. Elapsed time and an unanswered prompt are not approval.

Once the wrapper actually starts, its nonzero-exit terminal rule below still applies. A permission stop must not be relabeled to obtain a provider retry.

## Bounded input and output gate

Apply this gate before the provider call:

1. When discovery covers more than 20 records, any minified or one-line JSON/JSONL, or any record that may exceed 8 KiB, prefilter locally with a deterministic structured parser.
2. Build a temporary evidence packet containing at most 20 candidates and 64 KiB total across the prompt and input files. Include only fields that support the assigned check and pass the disclosure decision above. Use task-local aliases for private source references by default. Include original identifiers, source paths, or excerpts only when necessary and authorized; cap every excerpt at 2 KiB and exclude complete raw documents.
3. Point Spark at a neutrally named packet directory when it contains everything needed. Do not expose a broad workspace root for discovery convenience or place local source mappings in the packet. `--cwd` chooses a working directory; it is not a filesystem read-isolation boundary. Explicitly allow only packet files in the prompt and prohibit parent-directory discovery, source reconstruction, and extra network access. Do not claim this prompt restriction is sandbox-enforced.
4. Require no more than eight tool commands. Each command must use structured field projection and emit at most 200 short lines. Never use `cat`, `sed`, or `rg` to print complete minified JSON/JSONL records, and never treat `head` as a byte limit.
5. If the bounded packet cannot support the requested result, return `NEEDS_CONTEXT` instead of widening the scan.

The wrapper's `4096`-token per-tool cap limits accidental output inside the Spark context, and final-message extraction prevents verbose CLI traces from flooding the parent task. Neither control authorizes a larger evidence packet or replaces local prefiltering.

## Decision examples

These examples illustrate the disclosure decision; apply the actual user's scope and current instructions.

| Request and evidence | Correct preparation and action |
|---|---|
| “Use Spark to check this public package manifest.” Paths are public repository-relative names. | Send the necessary manifest projection. Preserve useful public paths; do not ask a generic external-transfer question. |
| “Use Spark to check whether these past tasks have missing required artifacts.” Local history contains private titles and task IDs, but only artifact presence matters. | The main agent verifies existence locally and sends records such as `{"record":"R01","required":2,"found":1}` plus a truthful coverage note. Omit identities and workflow narrative. Spark may flag a count mismatch; only the main agent maps it back to a source or claims verified history. |
| The same history check requires a confidential workflow narrative, even after names become `R01`. No disclosure approval covers it. | Aliases have not removed the sensitive information. Prepare the smallest useful preview and ask once for that necessary disclosure; do not submit the narrative under a “sanitized” label. |
| The user has approved sending the previewed eight-record packet to Spark for this audit. The destination, question, and disclosure scope are unchanged. | Reuse that approval and dispatch the approved input. Do not ask again simply because the CLI is external or an execution justification is required. |
| Automatic review denies the packet before the process starts. | Record a pre-dispatch stop with no started attempt. Use only the permitted resolution described above; do not retry the same packet via another command. A synthetic connectivity test would verify connectivity only, not approve this packet. |

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
7. evidence-packet byte, candidate, excerpt, command, and output budgets;
8. `BLOCKED` or `NEEDS_CONTEXT` stop behavior.

Use the requested output language, otherwise the user's language for prose. Preserve specified schema keys and exact machine-only responses.

For a self-contained packet, “exact workspace/files” means the neutral packet directory and its permitted files, not the private original paths. Keep the prompt free of original titles and histories too. A compact template is:

~~~text
Task: <one mechanical check; no final business or historical judgment>.
Materials: <neutral absolute packet directory>; read only <exact packet filenames>.
Coverage: <what the main agent verified locally; relevant omissions or unknowns>.
Constraints: read-only. Do not inspect other files, parent directories, original
sources, credentials, or history. Do not use extra network access or delegate.
Limits: <actual candidate count and total prompt/input bytes>; at most 20 candidates,
64 KiB total, 2 KiB per excerpt, 8 tool commands, and 200 short lines per command.
Use structured field projection for JSON/JSONL; never print complete minified records.
Output: status (DONE | DONE_WITH_CONCERNS | BLOCKED | NEEDS_CONTEXT), files_inspected,
commands_run, findings, confidence, needs_main_agent_decision, risks,
recommended_next_step. Use record aliases and tie findings to supplied fields;
state coverage limits. <Bind output language and any required machine format>.
Treat locally reported checks as supplied evidence, not your own filesystem
verification. No writes or final acceptance.
If required evidence is absent, return NEEDS_CONTEXT and the missing field;
do not widen the scan or infer private source identities.
~~~

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

- Pre-screen the exact files and prompt before the provider call; build the bounded evidence packet locally when the input gate requires it.
- Keep immediate critical-path work local and avoid duplicate discovery. An explicitly requested independent Spark check is a distinct assignment; do not silently skip it because the main agent can perform the same calculation.
- Review the complete Spark result before adopting any finding.
- Perform all writes, final validation, and judgment locally.
- For a run that materially affects conclusions, record assigned scope, adopted/rejected findings, and result status in the Controller's durable routing log.

## Failure handling

- If the bundled wrapper or `codex` CLI is unavailable, stop and report the missing executor. Do not describe that as proof that the Spark model is unavailable.
- A Desktop/API `unsupported_parameter`, `invalid_request`, or `reasoning.summary` rejection is `wrong_surface_or_request` evidence. It says nothing about Spark availability and never authorizes a second visible task with reasoning removed or changed.
- Report Spark unavailable only after a correctly validated bundled-CLI attempt returns an `unsupported_route` or `provider_model` failure and `scripts/validate_dispatch_route.py` returns `spark_unavailable_supported: true` for the failure receipt.
- When choosing an automatic route, keep work local if a deterministic validator fully answers the request. When the user explicitly requests Spark, perform the authorized bounded check or report its actual blocker; local work alone does not fulfill the Spark request.
- Once the wrapper starts, every nonzero exit ends the Spark lane. Treat `PROJECT_HANDOFF_SPARK_TERMINAL_FAILURE` as binding: record and validate the failure, then call no App task, follow-up, retry, or other model for that lane.
- A fallback description is not route authority. Start another route only after a new user message explicitly selects or authorizes it.
- Never add writable sandbox flags, bypass flags, or broad directories.
- Review the complete result locally before adopting any finding.
