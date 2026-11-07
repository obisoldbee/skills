# Model Routing

Use this reference for an explicitly selected route or `auto`. Resolve each lane from verified scope, then check the selected host's current task-tool capability.

## Contents

1. Field-level precedence
2. Current aliases and compatibility
3. Automatic recommendations
4. Mixed work and continuity
5. Mandatory preflight and receipts
6. Evaluation examples

## Field-level precedence

Resolve `model` and `reasoning` independently:

1. Preserve each explicit raw user value.
2. An explicitly selected alias binds both model and reasoning.
3. Classify only an axis explicitly set to `auto`.
4. An unselected axis is `platform_default`: record null and omit its tool field.

A bare `$project-handoff` or “创建任务” does not authorize model selection. Use `requested_route=platform-default`, `create_thread_arguments={}`, and omit both `model` and `thinking`. A model-only request omits `thinking`; a reasoning-only request omits `model`.

Keep raw selections in `requested_model` and `requested_reasoning`. Model-only names `Astra`, `Sol`, `Terra`, and `Luna` select a family without selecting effort; resolve them with the destination snapshot below. `GPT6` pins `gpt-6-astra`, not every GPT-6 variant. Exact IDs such as `gpt-6-sol` or `gpt-5.6-terra` stay exact even when a newer release is present. Unknown raw model IDs require live capability verification; do not rewrite them.

Valid per-axis bases are `explicit_user`, `explicit_skill_route`, `explicit_auto`, and `platform_default`. The guard returns `requested_axes`, the exact `create_thread_arguments`, and `omitted_create_thread_fields`. Adding a value to a platform-default axis is `silent_default_override` and stops dispatch. An explicit route or pipeline always takes precedence over automatic recommendations.

## Current aliases and compatibility

| Alias | Model | Reasoning | Use |
|---|---|---|---|
| `astra-ultra` | Astra (baseline `gpt-6-astra`) | `ultra` | Hardest reasoning |
| `astra-high` | Astra | `high` | Default orchestration |
| `astra-xhigh` | Astra | `xhigh` | Explicit thinking/review selection |
| `sol-max` | Sol (baseline `gpt-6.1-sol`) | `max` | Default writing and development, accepted-plan execution |
| `sol-medium` | Sol | `medium` | Explicit alternative |
| `terra-ultra` | Terra (baseline `gpt-6.1-terra`) | `ultra` | Default general computer operation; optional writing or independent QA when selected |
| `terra-medium` | Terra | `medium` | Default known fixed-step simple browser operation |
| `terra-xhigh` | Terra | `xhigh` | Explicit UI operation selection |
| `luna-max` | Luna (baseline `gpt-6-luna`) | `max` | Mechanical audits, file lookup, specified status checks |
| `astra-max` / `sol-ultra` | Current corresponding family | `max` / `ultra` | Explicit alternatives |
| `gpt6-max` / `gpt6-ultra` | `gpt-6-astra` (pinned generation) | `max` / `ultra` | Explicit compatibility aliases |
| `terra-max` | Terra | `max` | Explicit alternative |

Normalize alias casing. Aliases bind only model and effort; select the executor surface separately below. Raw GPT-5.6 IDs and other live-supported model/effort pairs remain available when explicitly chosen. A raw older model plus explicit reasoning `auto` uses the declared role's effort, or max without role context, while retaining that exact model.

Baselines as of 2026-10-27: Astra is GPT-6, Sol and Terra are GPT-6.1, Luna is GPT-6. Existing tasks keep their verified original model/effort, including earlier Terra-max at GPT-5.6 and automatic Sol-medium/Luna-max operation tasks. Spark aliases and model ID are retired and rejected. An explicit request for a retired route requires a new user choice.

Capability observation on 2026-10-27: the calling task schema advertises GPT-6 Astra, GPT-6.1 Sol and GPT-6.1 Terra with low, medium, high, xhigh, max, ultra; GPT-6 Luna with low, medium, high, xhigh, max. Recheck the actual destination. `destination_state.supported_reasoning` or the catalog below can restrict the pair. Read back the actual execution binding after dispatch.

### Executor surface

Resolve the user's surface choice independently from the model alias. A requested visible chat uses `surface=visible_thread`, the visible dispatch guard, `create_thread`, and the bound real receipt. Keep an existing visible selection on continuation.

For explicitly requested subagents or ordinary internal collaboration, use `surface=internal_agent` and the host's native collaboration tools and return path. `validate_route` checks the model/effort selection for either surface; `validate_attempt` and the visible receipt validator are exclusively for visible dispatch. Internal routes emit no `create_thread` arguments. Inspect the host's model/effort fields, inheritance and override conditions before starting a child, then use `validate_execution_binding.py` with actual runtime evidence when the selected responsibility requires verification. Record native agent identity as internal evidence, without constructing a visible-task receipt. A model alias alone grants no new-chat authority.

For example, explicitly selected Astra-xhigh thinking and Terra-xhigh UI subagents stay internal; an explicitly requested Terra-ultra visible independent QA task uses the visible guard and receipt. If the selected surface cannot run the pair, report that exact capability gap and retain the selection.

### Newest available family policy

For a **new** unversioned family alias or automatic role, follow the user's upgrade preference by choosing the highest numeric version in the same family among visible releases supported by the selected executor service. Compare version tuples, so 6.10 is newer than 6.9; never sort lexically. Keep selection within that family and use only verified release IDs.

Record `route.model_catalog` (also `context.model_catalog` for the fixture resolver):

```json
{
  "source": "exact destination executor-tool capability reference",
  "host_id": "target-host-id",
  "observed_at": "2026-10-27T00:00:00Z",
  "models": [
    {"model": "gpt-6.1-sol", "hidden": false,
     "reasoning_efforts": ["low", "medium", "high", "xhigh", "max", "ultra"]}
  ]
}
```

Use a fresh observation in this dispatch session, bound to the actual host and executing service. A newer local CLI catalog, stale cache, other host's schema, or UI menu alone does not establish destination capability. Corroborate raw catalog evidence against the selected executor tool before including it here. Capture the complete relevant family, including efforts. The offline guard validates declared evidence, not its authenticity/freshness or runtime availability; keep the source reference and verify it externally.

Without a snapshot, the offline resolver uses the dated baselines; it does not discover models or authorize skipping live preflight. With a snapshot it resolves deterministically and refuses a family older than the baseline, rather than quietly going back to 6 Sol or 5.6 Sol. Diagnose stale destination configuration/core when appropriate. If the newest model lacks the requested effort, stop with the mismatch; do not choose an older version merely to make validation pass. Existing task follow-ups use their recorded pair, not today's catalog; keep historical receipts unchanged.

A tool's capability is not route authority. Never substitute `spawn_agent`, collaboration subagents, agent paths, or CLI runs for a requested visible task.

## Automatic recommendations

Automatic model selection requires a verified `task_kind`. When reasoning is also `auto`, use that role's effort. Explicit reasoning still wins; an unselected reasoning axis stays omitted. Role defaults do not turn a bare task-creation request into automatic routing.

| Verified lane evidence | Recommended route | Expected output |
|---|---|---|
| Hardest reasoning or demanding integration (`top_difficulty`) | Astra ultra | Decisions, risks, acceptance criteria, downstream plan |
| Task decomposition, coordination, integration planning (`orchestration`) | Astra high | Dependency graph, bounded assignments and integration gates |
| Writing (`writing`) | Sol max; Terra ultra available by explicit selection | Draft from the supplied brief, outputs and checks |
| Development (`development`) or executing Astra's accepted plan (`astra_planned_execution`) | Sol max | Artifacts, named checks and deviations |
| General computer operation (`computer_operation`) | Terra ultra | Verified actions and observed state |
| Known fixed-step simple browser operation (`browser_operation`) | Terra medium | Bounded actions and page readback |
| Mechanical audits, file lookup, existing scripts, specified status observation (`mechanical`) | Luna max | Exact evidence and bounded results |
| Other work, ambiguous difficulty, or missing plan evidence | Explicit human route | Resolve the missing scope or selection before dispatch |

Do not infer top difficulty from total project size, the Controller's model, or the word “design” alone. Do not infer mechanical work from “read-only”, “audit”, or “review”: evidence interpretation, semantic judgments, risk prioritization, and final acceptance do not qualify. A complex audit may belong to Astra; a fully specified review step may belong to Sol; otherwise obtain an explicit route.

A writing lane names the brief, outputs and checks. Keep development and accepted Sol execution plans on their selected routes; an Astra-planned execution lane additionally names the accepted plan and its gate. If execution uncovers unresolved design, report it to the Controller. A Luna lane names exact inputs/actions and result format. Classify browser research/review by its substantive reasoning role. Use `browser_operation` only when the existing procedure supplies known steps, expected page state and a stop condition; an unfamiliar UI procedure uses `computer_operation`. Model routing itself never authorizes scheduling, sending, purchases or other extra side effects.

Keep a deterministic local command local when it fully answers the request and no separate task was requested. An explicitly requested scheduled execution task can use Luna with its supplied script; use the host's scheduling tools only when scheduling is authorized.

### Cost-aware monitoring

Choose an appropriate executor before tuning polling frequency. The preferred division for a clearly specified observation task is Luna-max for mechanical checks and the selected Controller for substantive judgment/quality review. When that Controller is Astra, reserve its repeated context loads and reasoning for actionable evidence rather than unchanged status. Compare the whole workflow's model/effort, context, wake-ups, and potential rework; counting calls or tokens without their executor is not a sufficient value comparison.

An explicit user selection of Luna-max monitoring, including a policy established earlier in the request, is the observer's route choice: retain `requested_route=luna-max` and the alias's two axes as `explicit_skill_route`. Reuse that choice without repeated confirmation. With authorized `auto`, classify a bounded status/checklist/script observation as `task_kind=mechanical`; semantic research or product acceptance is a different role. Preserve explicit alternative routes and unselected axes outside this observer scope.

Bind the automation to the selected observer thread and verify its owner/target through the live host contract. For each scheduled turn, compare the actual model/effort with that selection under [runtime verification and alerts](runtime-alerts.md). Preserve the selected Luna observer and `max` effort during scheduling. See [result collection](result-collection.md) for the bounded observation goal, quiet checks, escalation and receipt gate.

## Mixed work and continuity

Before resolving a shortened request, simplifying a Skill, merging roles or recovering a run, retain applicable choices from the original request and accepted decisions for each responsibility. A later message that says only “continue” or “simplify” does not reset an already selected model, effort or visible review surface. Keep helpers separate from that formal responsibility. An actual user route change controls its named axes; an unrelated earlier choice does not spread to other scopes.

For a top-difficulty design followed by implementation:

1. Create Astra ultra for the top-difficulty design lane (ordinary orchestration uses Astra high).
2. Require the accepted plan artifact and named ready state.
3. Verify that artifact and current repository state.
4. Create Sol max from the accepted plan; do not start it speculatively before the gate.

Independently scoped mechanical checks can use Luna max concurrently. For all ready lanes, dispatch the full ready, conflict-free wave within the user's cap and actual visible-task capacity. Shared files/resources require separate worktrees, narrowed scopes, or serial integration. Keep one integration owner.

Follow-ups preserve the task's verified effective route. Normally omit model/thinking on `send_message_to_thread` to retain its settings; never add a lower effort because the follow-up is short. An explicit route change controls only the requested axes.

For existing tasks, including GPT-6 Sol and GPT-5.6 tasks, bind the task ID and original route using readback and its historical receipt. Only unchanged follow-up, eligible synchronization, and failure reporting may retain a historical automatic route or pre-migration alias pair. The offline guard checks this declaration, not task existence. It cannot be used for new initial dispatch, replacement tasks, or new plans. Historical receipts remain evidence of the original call and policy; do not rewrite their model versions.

## Mandatory preflight and receipts

For visible dispatch, follow-up, retry, or availability claims, serialize one attempt and run `scripts/validate_dispatch_route.py ATTEMPT --format json`. For multi-lane work also run `scripts/validate_orchestration_plan.py` with each lane's `requested_route` and `surface`.

~~~yaml
operation: initial_dispatch | followup | sync_retry | failure_report
action: create_visible_task | read_existing_task | set_visible_task_title | send_followup | none
tool: <exact live tool name>
failure_class: none | creation_visibility_delay | prompt_readback_delay | title_metadata_delay | unsupported_parameter | invalid_request | unsupported_route | auth | permission | quota | provider_model | unknown
route_changed: false
explicit_user_route_change: false
route:
  requested_route: astra-ultra | astra-high | astra-xhigh | sol-max | terra-ultra | terra-medium | terra-xhigh | luna-max | auto | platform-default | <explicit route>
  task_kind: <required for automatic model selection; role from the table>
  requested_model: <required only for a raw explicit model>
  requested_reasoning: <required only for a raw explicit effort>
  model: <value or null>
  reasoning: <value or null>
  surface: visible_thread
  model_basis: explicit_user | explicit_skill_route | explicit_auto | platform_default
  reasoning_basis: explicit_user | explicit_skill_route | explicit_auto | platform_default
~~~

Proceed only on `valid: true`. Retain `attempt_sha256`; pass exactly its `create_thread_arguments` using the current tool's **model/thinking** names. Never add fields listed in `omitted_create_thread_fields`.

Normalize the actual creation result with the exact `actual_tool`, `actual_create_thread_arguments`, `dispatch_attempt_sha256`, IDs, and prompt-delivery evidence. Require `scripts/validate_visible_task_receipt.py RECEIPT --dispatch-attempt ATTEMPT` to pass before registration. Then verify initial progress and, when requested, completed output. A model's self-description is not model identity evidence.

Record selection evidence, route bases, requested/effective axes, runtime pair verification, dependencies, authority boundary, guard results, failure class, and fallback (`none` unless explicitly authorized). `model_unavailable_supported` is false for parameter validation errors. See `references/thread-dispatch.md` for the GPT-6 max diagnostic procedure: preserve the exact pair, inspect the executing runtime/capabilities, and never mask a validation mismatch by switching to GPT-5.6, dropping thinking, or substituting CLI/subagents.

Use `scripts/validate_execution_binding.py SELECTION --actual ACTUAL --previous ORIGINAL_SELECTION` when verifying a selected formal execution or preserving choices across a role merge. SELECTION records `scope_id`, `selection_ref`, the existing per-axis bases and selected values, and `surface` only when selected. ACTUAL records the same scope, real `execution_id`, `actual_tool`, `surface`, model/effort and `metadata_source=runtime_metadata|session_settings|execution_readback` with its original `evidence_ref`. Copy the observed pair, including a mismatch; do not normalize actual low effort to requested max. ORIGINAL_SELECTION is the independently retained pre-change selection for this same responsibility. A direct human change can supply `user_route_change={author_is_human:true,user_instruction_ref,axes}`; verify that source outside the helper. Prompt self-description, requested parameters and labels are insufficient. The helper checks declared bindings and cannot authenticate a human or query a runtime. It neither creates tasks nor selects unrequested axes; model-only Sol remains model-only, and an ordinary unselected internal helper can use platform defaults.

Before constructing SELECTION or choosing ORIGINAL_SELECTION, resolve the original
instruction's executor, scope and lifetime under [runtime verification](runtime-alerts.md#verify-the-actual-turn).
Passing a syntactically valid selection does not establish that an old delivery's
model choice still applies to a new Controller request. Keep the original selection
for unfinished or explicitly continuing work; retain completed choices as history.

## Evaluation examples

| Request and verified context | Result |
|---|---|
| Both axes auto; verified top-difficulty cross-system architecture problem | baseline `gpt-6-astra`, `thinking=ultra` |
| Both axes auto; ordinary orchestration | baseline `gpt-6-astra`, `thinking=high` |
| Both axes auto; execute Astra's accepted plan with named checks | baseline `gpt-6.1-sol`, `thinking=max` |
| Both axes auto; general computer operation | baseline `gpt-6.1-terra`, `thinking=ultra` |
| Both axes auto; known fixed-step simple browser operation | baseline `gpt-6.1-terra`, `thinking=medium` |
| Explicit `terra-ultra` writing lane | baseline `gpt-6.1-terra`, `thinking=ultra` |
| Bare Terra, reasoning unselected | Pass only baseline `gpt-6.1-terra`, omit thinking |
| Both axes auto; inspect manifest YAML/paths/SHA without judging content | `gpt-6-luna`, `thinking=max` |
| Both axes auto; find files or run an existing authorized script mechanically | `gpt-6-luna`, `thinking=max` |
| Both axes auto; assess whether research supports a conclusion, scope unspecified | Resolve scope or request an explicit route; do not select Luna |
| “用 sol-max 创建任务” | Newest verified Sol at max; current baseline GPT-6.1 Sol |
| Explicit raw `gpt-5.6-sol`; reasoning unselected | Pass only that model, omit thinking |
| Model auto with mechanical scope; reasoning unselected | Pass only `gpt-6-luna`, omit thinking |
| “创建任务” or bare Skill trigger | Omit both axes |
| Luna max rejected by create_thread reasoning validation | Preserve failure; inspect task-service capability; no silent downgrade |

The offline `resolve_request_case` parser is a bounded regression grammar, not a general intent parser. It recognizes fixture forms, aliases and family names. Auto uses the verified role table's `task_kind`, `lane_difficulty=high`, or `plan_owner=astra` with an accepted-plan request. Only narrowly structural wording is classified mechanically without context. A reasoning-only auto request without role context retains max while leaving model untouched. Its creation fixtures default to visible work; explicit subagent wording or verified `context.surface=internal_agent` selects internal work. Unknown or conflicting scope/axes/surfaces fail instead of inventing authority. Runtime callers resolve the full live request and source evidence.
