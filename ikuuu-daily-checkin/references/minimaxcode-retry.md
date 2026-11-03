# MiniMaxCode scheduled wrapper

Background:

This wrapper adds bounded current-session orchestration around the one-round browser workflow; it does not replace or duplicate that workflow.

Materials:

1. The one-round result produced by `SKILL.md` and `references/workflow.md`.
2. The current MiniMaxCode session history and Mavis tool results.
3. The available Lark Skills, read only when a notification is due.

Constraints:

Use this reference only when the task explicitly requests scheduled mode and authorizes both:

1. one Mavis `cron self` reminder for this current session; and
2. the conditional bot notifications below to Feishu chat `NOTIFICATION_CHAT_ID`, supplied explicitly by the current invoking task.

Never infer or recover `NOTIFICATION_CHAT_ID` from a previous task, a package default, or unrelated records. Without that authorization and an explicit destination, run manual mode only. Never create, edit, or delete the main recurring task.

## Round and retry contract

- One complete browser workflow is one round.
- Close the browser task space after every completed round, including a retryable failure, before returning the report or waiting 30 minutes. The task space is not a retry-state or login-state store; the next round creates a fresh space. Keep it only when `needs_user_action` has handed the exact page to the user.
- Use `success` and `already_checked_in` as successful terminal states. Treat `site_unreachable`, `uncertain`, and `failed` as retryable failed rounds. `needs_user_action` is a failed terminal state for unattended scheduled mode: do not create a retry reminder or retake the browser until the user explicitly resumes.
- Run at most 10 rounds for one `run_date` in `Asia/Shanghai`. Never run round 11.
- After a retryable failed round below 10, create or reuse one current-session Mavis `cron self` reminder for 30 minutes later. The runtime owns the normal `cron self` mechanics; this reference defines only the retry policy.
- Rounds 2–9 reuse the same `cron_id`; never create a second reminder.
- On any terminal outcome (`success`, `already_checked_in`, `needs_user_action`, `retry_unavailable`, or completion of round 10), delete the reminder before stopping when a `cron_id` exists. Attempt deletion once; if it fails, mark the session terminal before reporting so a later wake-up cannot run another browser round, and append the redacted cleanup failure as `说明`.
- If `cron self` is unavailable, creation fails, or no usable `cron_id` is returned, stop as `retry_unavailable`. Do not substitute WorkBuddy automation, an independent cron, a one-time cron, a state file, or shell sleep.

Keep the round, `run_date`, `cron_id`, and notification states in the current session context. Never output `<mavis-progress>`, bare JSON, or another state marker. On a later wake-up, recover state from the current session before deciding the round. If it is already terminal, do not run the browser or send another notification.

## Feishu notifications

Before sending, read the available `lark-shared`, `lark-im`, and `lark-im-messages-send` instructions. Send plain text with `lark-cli im +messages-send --as bot` to `NOTIFICATION_CHAT_ID`. Success requires exit code 0 and stdout JSON `ok == true`. Each notification type is attempted at most once; a failed send is recorded as `send_failed` and is not retried.

### Low remaining traffic

After every round with a fresh remaining-traffic value, normalize `MB`, `GB`, and `TB` using 1024-based units. If the value is strictly below `20 GB`, send once for the `run_date` with idempotency key `ikuuu-daily-checkin-YYYYMMDD-low-traffic`:

```text
【Ikuuu 流量不足提醒】
日期：YYYY-MM-DD
今日获取流量：{value_or_未报告}
剩余流量：{fresh_value}
提醒阈值：20 GB
```

Exactly `20 GB` does not trigger the alert. Missing or ambiguous values are `not_evaluable`; do not guess or send.

### Ten failed rounds

Only after round 10 fails, send once with idempotency key `ikuuu-daily-checkin-YYYYMMDD-failed`:

```text
【Ikuuu 每日签到失败】
日期：YYYY-MM-DD
结果：10/10 轮失败
最后状态：{status}
最后站点：{origin_or_未确认}
最后原因：{one_redacted_sentence}
```

Task:

Execute the next scheduled round, apply the retry and notification gates above, retain state only in the current session, and return the report below.

Output format:

Return one concise Chinese report after every round. Render it as a fenced `text` block so MiniMaxCode preserves line breaks. Do not add process narration, a raw state object, or a clickable site URL outside the block.

```text
Ikuuu 每日签到｜YYYY-MM-DD｜第 N/10 轮
结果：成功 | 成功（今日已签到） | 失败
今日获取流量：<value or 未报告>
剩余流量：<fresh value or 未确认>
```

Use `成功` for `success`, `成功（今日已签到）` for `already_checked_in`, and `失败` otherwise. Append only applicable lines:

- `原因：<一句脱敏说明>` for a failed round;
- `后续：30 分钟后重试 | 需要用户处理 | 重试不可用 | 结束` when the next action is not obvious;
- `流量提醒：已发送 | 发送失败` only when a low-traffic notification was attempted;
- `失败提醒：已发送 | 发送失败` only after the round-10 notification was attempted;
- `说明：重试提醒清理失败，已禁止后续执行` only when terminal reminder deletion failed.

Omit every untriggered notification field. The report contains no email, password, cookie, token, account identifier, complete login snapshot, raw technical state, continuation marker, or JSON.

## Boundary examples

- Example 1: round 1 is `success` with `229 GB` remaining → no low-traffic alert, no retry, terminal report.
- Example 2: round 1 is `success` with `19.99 GB` remaining → send the low-traffic alert once, no retry, terminal report.
- Example 3: round 1 is `site_unreachable` → close the round's task space, create one 30-minute `cron self`, then report failure, reason, and `30 分钟后重试`.
- Example 4: remaining traffic is exactly `20 GB` or cannot be parsed unambiguously → do not send a low-traffic alert.

Success criteria:

- No more than 10 rounds and one current-session reminder exist for a `run_date`.
- No completed round leaves an agent-owned browser task space open; only a page handed to the user for required action may remain.
- Terminal states cannot trigger another browser round or duplicate notification.
- Every round returns one minimal readable report containing the result, today's obtained traffic, and fresh remaining traffic; no continuation marker, raw status, or JSON is visible to the user.
