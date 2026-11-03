# MiniMaxCode scheduled wrapper

Background:

This wrapper owns scheduled retries, notifications, cleanup, and the user-facing report around the one-round browser workflow. It does not duplicate that workflow.

Materials:

1. The one-round report returned by `SKILL.md`.
2. The current MiniMaxCode session state and Mavis results.
3. The caller-supplied bot `lark_chat_id`.

Constraints:

Before any browser tool call, apply the `SKILL.md` intent gate. A current query remains query-only even in a scheduled conversation: return its query report and do not manage reminders or notify. Ambiguous requests ask first. Scheduled **execution** requires the caller to explicitly authorize:

- execution of today's check-in, not merely inspection of today's state;
- creation, reuse, and terminal deletion of one current-session Mavis `cron self` reminder;
- a bot `lark_chat_id` for the notifications below.

Missing authorization or destination is `needs_configuration`: stop before browser work and ask for the missing item; never silently run manual execution. Never infer a target from another task, package default, account records, or tool availability. A self-reminder may reuse only the originating run's explicit authorization/target already retained in this same session. Never create, modify, or delete the main recurring task.

Return the report in Chinese. Preserve unknown or conflicting browser evidence as `未确认`; never invent a successful round, reward, balance, notification, or reminder result.

## Orchestration tools

Read the available runtime instructions/schema before using Mavis or Lark; no tool name in this document proves availability. Do not install a missing tool or substitute a scheduler.

| Tool | Purpose / use when | Do not use when | Parameters and returns | Failure / stop rule |
|---|---|---|---|---|
| Mavis current-session `cron self` | Arrange the one authorized 30-minute retry after a closed retryable round; delete this run's reminder at terminal cleanup | Query-only, missing authorization, unresolved run identity, creating a replacement, or changing the main schedule | Use the current runtime's schema with this session, 30-minute timing, short Skill invocation, and only the returned owned `cron_id`; require a usable ID on creation and explicit deletion confirmation | Unavailable/failed/ambiguous creation is terminal `retry_unavailable`; deletion failure stays terminal with bounded residue cleanup |
| `lark-cli im +messages-send --as bot` | Send only a due, caller-authorized conditional notification after browser cleanup | Query-only, missing target, failed browser cleanup, an already attempted notification, a reservation inherited from an interrupted invocation, or terminal wake-up | Caller-provided chat ID, rendered plain text, date/type idempotency key; require exit 0 and JSON `ok == true` | Missing tool, command failure, or unknown result is `send_failed`; do not resend |

## Retry

- One complete browser workflow is one round.
- Close the browser task space after every completed round, including a retryable failure, before returning the report or arranging the 30-minute retry. The task space is not a retry-state or login-state store; the next round creates a fresh space. Keep it only when an attention-required result has handed the exact page to the user.
- A one-round report with `本轮: success` is a successful terminal result; its check-in status may be `newly_completed` or `already_completed`.
- `login_failed`, `page_changed`, and `blocked_manual_action` require immediate user attention: finalize the run, then send the attention notification once only if handoff is confirmed. Stop without another round.
- `network`, `points_unverified`, and `unknown` may retry every 30 minutes, up to 10 rounds for one `run_date` in `Asia/Shanghai`. Never run round 11.
- `browser_cleanup`, `runtime_unavailable`, `needs_configuration`, `retry_unavailable`, and notification failure are also terminal. Every terminal reason uses the finalizer below; none is a bare early return that leaves an existing reminder active.
- After closing the first retryable failed round, record `reminder_create_attempted` in this session **before** attempting one current-session `mavis cron self`. Its short prompt invokes `$ego-browser` and `$minimax-agent-daily-checkin` in execute/scheduled mode under this run's retained authorization and asks to recover the same run from this session. It does not duplicate retry/notification mechanics. Rounds 2–9 reuse the same confirmed `cron_id`; never create a replacement, even after an ambiguous creation response.
- If `cron self` is unavailable, creation fails, or no usable `cron_id` is returned, stop as `retry_unavailable`. Do not substitute WorkBuddy automation, an independent/once cron, a state file, or shell sleep.
- Keep `run_date`, round, `cron_id`, `reminder_create_attempted`, terminal reason, cleanup attempts/results, and notification reservations/results in the current session only. Do not print raw JSON, an HTML comment, or a progress marker; do not restore a disk-state script.

## Unified terminal finalizer and wake-up gate

Every entry first distinguishes a new explicitly authorized run from a continuation. A self-reminder recovers the originating `run_date`, round, authority, and terminal flag from this session before browser work. It never resets to round 1 because midnight passed or context is incomplete. Unrecoverable identity/state means stop and ask for human inspection; no browser, notification, new reminder, or guessed deletion. An explicit new daily invocation must not erase an unresolved old terminal reminder; clear/report that residue first.

For **all** terminal outcomes — success/already-completed, attention required, exhausted round 10, browser close/handoff failure, runtime/configuration failure, retry unavailable, notification failure, and reminder deletion failure — use this order:

1. Record `terminal = true` and preserve the original browser result plus terminal reason in the current session **before any reminder deletion or notification call**. If a preceding browser close/handoff failed, record `browser_cleanup`; do not retry that browser action in the finalizer.
2. If this run has a known `cron_id` and retained deletion authorization, reserve `terminal_delete_attempted` before one deletion attempt. Record the actual result. On success clear the pending ID; on failure/unknown result retain it as residue and report `重试提醒清理失败，已禁止后续执行`. No ID means no deletion; an ambiguous creation result is not permission to guess an ID or delete unrelated reminders.
3. If the browser was closed or correctly handed off (or never created) and a notification is due under the rules below, reserve that notification attempt **before** sending. A missing send tool, failed command, or unconfirmed response becomes `send_failed` / `notification_failed`; preserve the original browser reason and keep terminal. Do not repeat the finalizer's deletion attempt or send a second failure notification about this failure. If browser cleanup failed, skip notification and report the cleanup failure in chat.
4. Return the terminal report. A deletion or send failure never clears terminal, increments the round, creates a reminder, or reopens the browser. A terminal notification reserved by this finalizer may finish in this invocation; it is not authority for a notification on a later wake-up.

On a later accidental wake-up of a terminal run, do **only** residue cleanup/reporting: if a known pending ID remains, reserve `residual_delete_attempted` and attempt its deletion once. This is one extra cleanup attempt for the entire run, not one per wake-up. Keep terminal regardless of result. If it fails again, all further wake-ups report the residue and request manual removal; no further tool calls, browser rounds, notification, or reminder creation. If deletion had already succeeded, report ended without tools. At most two deletion attempts total (terminal exit plus this single residue attempt) target the same owned reminder. Never claim that an externally undeletable reminder has stopped firing.

If a continuation loses its notification target but retains the exact existing ID and original deletion authorization, mark `needs_configuration` terminal and run only the authorized cleanup/report path. Otherwise report the missing context without guessing or touching another reminder.

## Notifications

Before sending, read the available `lark-shared`, `lark-im`, and message-send instructions. Send plain text with `lark-cli im +messages-send --as bot --chat-id <lark_chat_id> --text <rendered_message> --idempotency-key <key>`. Success requires exit code 0 and stdout JSON `ok == true`. Each notification type is reserved before the call and attempted once per originating `run_date`; missing/failed tools or unknown response are `发送失败`, terminal, and never retried. Tool capability is not notification authority.

### Attention required

Send once when the round returns `login_failed`, `page_changed`, or `blocked_manual_action`, using idempotency key `minimax-checkin-YYYYMMDD-attention`:

```text
【MiniMax Agent 每日签到需检查】
日期：YYYY-MM-DD
轮次：N/10
问题：登录失败 | 页面打卡功能疑似变化 | 需要人工验证
原因：{one_redacted_sentence}
```

### Ten failed rounds

If round 10 ends with another failure type and browser cleanup succeeded, send once using idempotency key `minimax-checkin-YYYYMMDD-failed`. Attention takes precedence on round 10; never send both types for the same terminal outcome. Cleanup failure skips notification, and notification failure itself cannot trigger another notification.

```text
【MiniMax Agent 每日签到失败】
日期：YYYY-MM-DD
结果：10/10 轮失败
最后失败类型：{failure_type}
最后原因：{one_redacted_sentence}
```

## Task-space cleanup

- Preserve and hand off the task space only for `login_failed`, `page_changed`, or `blocked_manual_action`, because the user must inspect or act on that exact page. Do not schedule an unattended retry for these outcomes.
- For every other round result with an agent-owned space, call `completeTaskSpace(..., { keep: false })` in a dedicated final ego-browser command and require `done: true` before reporting success, notifying, or creating a retry reminder. This includes success, `network`, `points_unverified`, `unknown`, and round 10. If no space was created, record `not_created`; never close a user-owned space or invent a successful cleanup receipt.
- A later scheduled retry creates a fresh task space and relies only on browser authentication state that remains available outside the closed task space.
- If close or handoff fails, times out, or returns no confirmed `done: true`, enter the unified finalizer as `browser_cleanup`, mark terminal first, and attempt deletion of this run's existing reminder once. A missing cleanup receipt is not an early-return exception. Report failed cleanup without pretending it succeeded; do not repeat the browser operation, notify, or schedule another round.

Task:

Apply intent/configuration and the wake-up gate before browser work. For an active authorized run, execute at most one browser round, record browser cleanup, choose exactly one retry-or-terminal path, and use the unified finalizer for every terminal exit. Return the report below. A query never enters this task.

Output format:

Return one fenced `text` report after every round. Do not add process narration or internal state outside the block.

```text
MiniMax Agent 每日签到
模式：execute / scheduled
日期：YYYY-MM-DD
轮次：N/10
本轮结果：成功 | 失败
签到状态：newly_completed | already_completed | uncertain | not_applicable
今日获取积分：<integer or 未确认>
剩余积分：<integer or 未确认>
失败类型：none | login_failed | page_changed | blocked_manual_action | network | points_unverified | browser_cleanup | runtime_unavailable | unknown | retry_unavailable | needs_configuration | notification_failed
飞书提醒：未触发 | 已发送 | 发送失败
后续：结束 | 30 分钟后重试 | 请人工检查 | 重试不可用
说明：<无或一句脱敏说明>
```

Use `成功` only when the one-round report says `本轮: success` and browser cleanup passed; otherwise use `失败`. Keep a reminder-deletion failure in `说明`, not as invented check-in failure. If notification fails, retain the original browser failure in `失败类型` and add `通知失败，已终止且不重发` to `说明`. Never expose an account identifier, credential, raw login snapshot, or retry-state object.

Before the first round, an intent/configuration/runtime stop gets a concise Chinese clarification or prerequisite report saying `未执行浏览器轮次`, not a fabricated N/10 result. A terminal accidental wake-up reports `本次未执行浏览器；原任务已结束` and the residue deletion result, without incrementing N or presenting old points as fresh.

## Examples

- Example 1: round 1 succeeds → close the task space, no reminder or notification, report success.
- Example 2: round 1 returns `network` → close the round's task space, create one 30-minute self-reminder, report failure.
- Example 3: any round returns `login_failed` → hand off the page, send the attention notification once, stop.
- Example 4: any round returns `page_changed` → hand off the page, send the attention notification once, stop.
- Example 5: round 10 returns `points_unverified` → close the task space, mark the session terminal, delete the reminder, send the ten-round notification once, stop.
- Example 6: round 2 browser cleanup fails with an existing reminder → mark terminal, attempt reminder deletion once, skip notification, report; do not open round 3.
- Example 7: terminal deletion fails, then the reminder fires → only one reserved residue-deletion attempt and a report; no browser/notification. If that fails too, later wakes only report/manual-removal advice.
- Example 8: round 10 attention notification fails → keep terminal and the original attention reason, record send failure; no second notification or duplicate deletion.
- Example 9: “只查积分” arrives in the scheduled conversation → query-only, no claim or reminder management. A new scheduled request missing `lark_chat_id` → ask before browser work, no manual fallback.

Success criteria:

- At most 10 rounds and one current-session reminder exist for one `run_date`.
- No completed round leaves an agent-owned browser task space open; only a page handed to the user for required action may remain.
- Only `network`, `points_unverified`, and `unknown` with confirmed browser cleanup may retry below round 10. Attention-required results and every other terminal reason stop immediately.
- Terminal state prevents another browser round or duplicate notification.
- Every terminal reason, including `browser_cleanup` and send failure, uses the same terminal-first finalizer. Creation/send reservations prevent duplicate attempts after uncertain responses; residue cleanup is bounded and never resets the run.
- Every round returns one readable multi-line report with the current result, today's awarded points, and remaining points.
