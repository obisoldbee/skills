# Internal Handoff Template

Generate this envelope automatically. Do not ask the user to copy it when thread tools are available.

For long context, index Materials first and keep the concrete Task after the materials and constraints.

~~~text
Background:
- Source task: <thread id or current task>
- Handoff type: dispatch
- Run id / lane id: <run> / <lane>
- Project: <absolute project path>
- Current phase: <phase>
- Dependencies: <lane ids and exact verified gates, or none>
- Controller / integration owner: <task or lane responsible for routing and integration>
- Controller context: <verified model/reasoning or unknown>
- Selected route: <requested route; per-axis requested/effective values; model_basis + reasoning_basis; exact create_thread fields to pass/omit; dispatch attempt SHA-256>
- Project scale: <normal, large, or super-large plus observable evidence>
- Verified current state: <facts verified this turn>
- Volatile facts: <facts marked 需复核>

Materials:
- M1: <absolute path, date/version, why it matters>
- M2: <absolute path, date/version, why it matters>

Constraints:
- Read scope: <exact files/directories>
- Write scope: <exact files/narrow directories, or none>
- Mutable resources: <ports, services, databases, worktree/build state, or none>
- Conflicts and order: <shared paths/resources plus dependency that serializes them, or none>
- Prohibitions: <writes, paths, calls, deployment, publication, or authority not granted>
- Preserve: <dirty files, user content, immutable inputs>
- Executor role: <design, implementation, research, review, computer operation, scheduled observation, or another bounded task>

Tools:
- <tool name>: <purpose>; use when <condition>; do not use when <condition>
- Failure handling: <retry/stop/report rule>

Task:
<One concrete current goal. Do not include the full historical backlog.>

Output format:
- Expected artifacts/receipts: <exact paths or response fields>
- Report: <changed files, commands/validation, risks, user interventions>
- Result identity: <commit/file hashes, response message, or observation target/time/cursor; do not claim unperformed integration>
- Required worker status: <result_ready, needs_fix, blocked, failed, or aborted; Controller records quality acceptance>
- <language and length constraints>

Success criteria:
- <observable criterion>
- <validation command or evidence rule>
- <handoff readiness gate>
- Task creation or multi-Agent use alone is not success.

Progress state:
- Registry/status/log: <paths or single-task receipt>
- Request id: <stable id included in the exact sent message>
- Send endpoint: <caller identity, target thread, proven hostId and creation/delivery evidence>
- Return endpoint: <independently verified from the worker's caller context, or result-reader pull>
- Result collection: <Controller reader, actual storage host/path or worker thread, next check entry, receipt responsibility>
- Follow-up: <bounded waits for short work or verified completion trigger/scheduled checks for long waits; actual owner, cadence, next check/trigger, and stop condition>
- Observation executor: <selected Luna-max or explicit alternative; actual model/effort, observer thread, and automation binding; do not inherit the Controller model by accident>
- Observation objective: <exact targets/read scope, expected version, mechanical checks, conditions that require Controller judgment, and receipt/stop condition>
- Observation efficiency: <current cursor, compact change summary, backoff when unchanged, quiet unless actionable or periodic reporting was requested>
- Quality review: <Controller criteria, evidence to inspect, accepted/needs_fix/blocked decision; in-scope corrections return to this task>
- Dispatch-only exception: <omit unless explicitly requested; cite the user's request and follow-up owner>
- Sync: <how the Controller reconciles direct user/worker changes and last cursor/time>
- Ready when: <gate>
- Stop when: <blocked/needs-context/abort condition and retry budget>
~~~

## Rules

- Use only sections the task needs, but always include Task, Constraints, Output format, and Success criteria.
- Explain the intent behind material prohibitions when it affects trade-offs.
- Cite paths, commands, record ids, or source anchors for evidence-based claims.
- Allow `BLOCKED` or `NEEDS_CONTEXT` instead of guessing.
- Normal execution includes Controller collection and quality review. The worker returns its result in its own thread or agreed output location; reverse messages are optional. “Do not message the Controller” never cancels the Controller's obligation to pull the result.
- An executor's self-checks and `result_ready` reply are inputs to review, including research, operations, and scheduled observations. Do not label an unreviewed result accepted. A recurring observer's single check does not close its monitoring obligation.
- Include the observation fields only when monitoring is part of the task. Give the selected Luna-max executor bounded checks and a compact result format, not the Controller's full reasoning workload. Unchanged ticks remain quiet; the Controller receives evidence for decisions and quality review. Verify the schedule's real model/effort rather than assigning a persona in its prompt.
- End a waiting turn only with an explicit dispatch-only/user-stop boundary, verified background continuation and return route, or an honestly reported external blocker. Do not insist on repeated inline polls or require a timer for every short task.
- A transient send failure keeps that delivery pending. Follow cross-device transport recovery and let the named reader collect results; it is not a whole-project stop condition.
- Redact credentials, tokens, cookies, private endpoint data, and unnecessary personal information.
- Include only the current goal for long-running work; store broader progress in the project or Controller record.
- Give workers disjoint writes whenever possible. If this lane shares a writable path or mutable resource, state the ordering edge and integration owner explicitly.
