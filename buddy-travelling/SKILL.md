---
name: buddy-travelling
description: "Use ego-browser to run one WorkBuddy Buddy daily travel check: claim a returned gift, close the gift modal, send Buddy when today's trip is available, or recognize that today's one-trip limit is already used and stop until tomorrow. Use for scheduled daily Buddy check-ins or an explicit travel-status check."
metadata:
  short-description: "每日领取 Buddy 礼物并处理一次旅行"
---

# Buddy Travelling

Materials:

- Target page: `https://www.workbuddy.cn/profile/growth-center`.
- Browser runtime: the available `ego-browser` skill and CLI. Follow its task-space, handoff, observation, and cleanup rules.
- User intent: the default is the full daily cycle; an optional destination may be named. Only an explicit status-only request disables mutations.
- Runtime read boundary: only the target page in the selected browser task space. Local input path: none.
- Runtime mutation boundary: only the named Buddy gift and travel controls. Local output path: none; the filesystem is read-only for this workflow.
- Live UI evidence from 2026-08-20 established the sequence below. Treat labels as observed states, not a permanent API contract; re-read the page on every run.

Background:

- Buddy can travel once per daily cycle. A normal scheduled run starts after the previous trip has returned and the card shows `领取礼物`.
- Claiming that returned gift exposes the travel control. It is enabled when today's trip is still available; it is disabled with `累啦，明天再来吧` when today's one-trip limit is already used.
- The next scheduled run continues from the live state. If today's gift was claimed during an extra same-day run, tomorrow may start directly at an enabled `派猫猫旅行` state.
- Every scheduled run starts with zero conversational context. Re-read the live page and continue from the observed state instead of assuming yesterday's result.

Constraints:

- Limit actions to the Buddy card, its returned-gift modal, and its travel-destination modal. Every other page control is outside this Skill.
- A normal or scheduled invocation authorizes only the clicks required for one daily check. A status-only request is read-only.
- Observe with `snapshotText()` before every state-changing click and again after it. Do not infer success from a click returning without error.
- `领取礼物` on the Buddy card is the returned-trip gift action. Classify it from that exact button's accessible name and enabled state. Never assign text from a sibling control or a shared ancestor to this button.
- Gift claiming, closing the claimed-gift modal, and checking travel availability are separate, ordered operations. Never inspect or click the travel control while the gift modal is still open.
- After the reward reads `已领取`, close the modal through its close control. Do not use `去使用` as a substitute for closing and re-reading the Buddy card.
- If the user names a destination, select that exact visible option. If the user only says to send Buddy, keep the modal's currently selected default instead of inventing a preference.
- Start at most one new trip per invocation. If a live countdown already exists, report it and stop without clicking.
- Never click a disabled `派猫猫旅行` button. Disabled plus `累啦，明天再来吧` is the expected `daily_limit_reached` state, not a blocker and not a reason to retry.
- Never expose, request, or store cookies, tokens, or passwords. Login or captcha work is a browser handoff, not a credential-collection step.
- Do not read or write local files as part of the runtime workflow.
- Reply in concise Simplified Chinese. Report only values observed in the current run; mark unavailable values as unknown instead of inventing them.

Tools:

Primary tool — `ego-browser nodejs`:

- Purpose: reuse the user's authenticated browser state, open the growth center, inspect labels, and perform authorized clicks.
- Use when: completing or checking the Buddy daily travel cycle.
- Do not use when: the request is not about this Buddy travel cycle.
- Parameters: one reusable task-space name, the fixed target URL, and a 30-second navigation timeout.
- Returns: `pageInfo()`, `snapshotText()`, and optional screenshots through `cliLog()`.
- Failure handling: if the CLI is unavailable, the page remains unreachable, or an expected state is absent after one fresh observation, stop; do not reload repeatedly, install, or reconfigure software.

Interaction helpers:

- Use `snapshotText()` for ordinary page controls and prefer text/XPath or stable `aria-label` selectors over unstable `@N` refs across rounds.
- Use `click(...)` only after the latest snapshot exposes one unambiguous target.
- To close the claimed-gift modal, first use the exact semantic close control exposed by the fresh snapshot. If it has no semantic label, take one screenshot and click the unique circular `×` immediately below the modal. Verify the modal title disappears before continuing.
- Use `captureScreenshot()` only for that unlabeled close control, another semantic ambiguity, or final visual evidence. Coordinate clicks require a clear screenshot target and a fresh verification afterward.
- A `user is controlling`, inactive, or unassigned task-space error is a hard stop. Follow the ego-browser handoff contract and wait for explicit user confirmation before resuming.

State routing examples:

| Current evidence | State | Allowed next action |
|---|---|---|
| Example 1 — Buddy card shows one enabled exact button named `领取礼物` | `gift_available` | Claim the returned gift, then continue to the claimed-modal state |
| Example 2 — Returned-gift modal shows `已领取` and its close `×` | `gift_claimed_modal` | Close the modal once and verify it disappears |
| Example 3 — Card shows enabled `派猫猫旅行` | `ready_to_travel` | Open the destination modal and dispatch |
| Example 4 — Card shows disabled `派猫猫旅行` with `累啦，明天再来吧` | `daily_limit_reached` | Do not click; report that today's trip is already used and wait until tomorrow |
| Example 5 — Card shows `旅行倒计时 HH:MM:SS` | `travelling` | Report `already_travelling`; do not start another trip |

Task:

- On each normal invocation, claim any returned gift, close its modal, and then dispatch only if today's travel control is enabled.
- End as `completed_cycle` when a new countdown is verified, or as the expected `daily_limit_reached` when today's one-trip allowance is already used.
- Only an explicit status-only request changes the task to read-only observation.

Handle the observed current state in this exact order:

1. Create or reuse one task space for this user goal and open the target page with load waiting enabled.
2. Wait through a visible `加载中...` state, then inspect `pageInfo()` and a full-page `snapshotText()`.
3. If authentication is required, hand off the task space. Do not seize it back without explicit confirmation.
4. If the request is explicitly status-only, report the Buddy name, current state, destination when visible, and countdown when visible; make no clicks and stop.
5. If the card already shows `旅行倒计时 HH:MM:SS`, report `already_travelling`; make no clicks and stop.
6. If the returned-gift modal is not already open and the card shows one enabled exact button named `领取礼物`, click that exact button once. Do not inspect a shared ancestor to decide what the button means.
7. If the returned-gift modal shows `领取 N 积分`, extract `N`, click that reward button once, and verify it changes to `已领取`.
8. Whenever the returned-gift modal shows `已领取`, close it once using the fresh semantic close control or, if unlabeled, the unique visible `×` immediately below the modal. Do not click `去使用`. Verify `Buddy 满载而归啦～` is no longer present. If the modal remains open, report `blocked` and do not interact with the covered card.
9. Take one fresh snapshot of the unobstructed Buddy card and classify the exact travel control:
   - enabled `派猫猫旅行` → continue to step 10;
   - disabled `派猫猫旅行` plus `累啦，明天再来吧` → report `daily_limit_reached`, set next action to `wait_until_next_day`, and stop without clicking;
   - disabled for any other observed reason → report `blocked` with that reason and stop without clicking;
   - no recognized travel state → report `blocked` and stop.
10. Click the enabled `派猫猫旅行` once. Verify the modal shows `想让 Buddy 今天去哪里逛逛？` and `确定派出`. If the user named a visible destination, select its `aria-label="切换到 <地点>"`; otherwise keep the current default.
11. Click `确定派出` once. Verify both `Buddy 正在 <地点> 采风中...` and `旅行倒计时 HH:MM:SS`. These readbacks, not the click itself, prove `completed_cycle`.
12. Run `completeTaskSpace(..., {keep: false})` in its own final heredoc after the result is confirmed, unless the user explicitly asked to keep the live page open.

Stop rules:

- After a click, wait 2–4 seconds and take one fresh snapshot for classification.
- Do not retry any click. Never repeat `领取礼物`, `领取 N 积分`, modal close, `派猫猫旅行`, destination selection, or `确定派出` in the same run.
- Never test a disabled button by clicking it.
- Stop on an unchanged or unknown state, an unknown modal, or more than one matching actionable button.
- Never begin a second gift-and-dispatch cycle after a countdown appears, even if another matching label is present elsewhere on the page.

Output format:

Return a concise Chinese result containing:

- run result: `completed_cycle`, `daily_limit_reached`, `already_travelling`, `status_only`, `auth_required`, or `blocked`;
- observed start state;
- actions actually completed;
- claimed points only when the modal exposed the number;
- selected destination only when observed;
- final countdown only when observed;
- next action: `wait_until_next_day` only for `daily_limit_reached`;
- blocker and required user action when incomplete.

Success criteria:

- Status checks perform no mutation.
- A claimed-gift modal is always closed and verified absent before the card is classified.
- `completed_cycle` requires a newly verified `旅行倒计时 HH:MM:SS` and the active destination after `确定派出`.
- `daily_limit_reached` requires an observed disabled `派猫猫旅行` plus `累啦，明天再来吧`; it is an expected daily terminal state, performs no dispatch click, and reports `wait_until_next_day`.
- `already_travelling` requires an existing live countdown and performs no mutation.
- No non-travel page control is triggered, and every reported value comes from the current browser readback.
