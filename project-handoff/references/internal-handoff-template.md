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
- Selected route: <model + reasoning; model_basis + reasoning_basis>
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
- Executor role: <design, implementation, judgmental audit, or mechanical audit>

Tools:
- <tool name>: <purpose>; use when <condition>; do not use when <condition>
- Failure handling: <retry/stop/report rule>

Task:
<One concrete current goal. Do not include the full historical backlog.>

Output format:
- Expected artifacts/receipts: <exact paths or response fields>
- Report: <changed files, commands/validation, risks, user interventions>
- Required lane status: <succeeded_pending_integration, needs_fix, blocked, failed, or aborted>
- <language and length constraints>

Success criteria:
- <observable criterion>
- <validation command or evidence rule>
- <handoff readiness gate>
- Task creation or multi-Agent use alone is not success.

Progress state:
- Registry/status/log: <paths or single-task receipt>
- Sync: <how the Controller reconciles direct user/worker changes and last cursor/time>
- Ready when: <gate>
- Stop when: <blocked/needs-context/abort condition and retry budget>
~~~

## Rules

- Use only sections the task needs, but always include Task, Constraints, Output format, and Success criteria.
- Explain the intent behind material prohibitions when it affects trade-offs.
- Cite paths, commands, record ids, or source anchors for evidence-based claims.
- Allow `BLOCKED` or `NEEDS_CONTEXT` instead of guessing.
- Redact credentials, tokens, cookies, private endpoint data, and unnecessary personal information.
- Include only the current goal for long-running work; store broader progress in the project or Controller record.
- Give workers disjoint writes whenever possible. If this lane shares a writable path or mutable resource, state the ordering edge and integration owner explicitly.
