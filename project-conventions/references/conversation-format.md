# Conversation File Format — Template & Example

This document defines the standard format for files under `conversation/`. The goal is to capture not just the outcome of a discussion, but the **reasoning process**: what the agent proposed, what the user changed, and why.

Allocate and write a canonical conversation file only while holding the Project Root's exclusive `writer` claim. Read-only and isolated-worktree Agents return their findings or commits first; the later shared writer records the integrated reasoning and user corrections without replacing the original inputs.

## File Template

```markdown
# [NN-Topic Title]

> **Date**: YYYY-MM-DD
> **Participants**: [agent names/roles] + [user]
> **Topic**: [one-line description]
> **Phase**: [brainstorming / decision / implementation / verification / other]

---

## Context

[Brief background: why this conversation happened, what triggered it, what state the project was in.]

---

## Agent Proposals

[What the agent(s) suggested. Can be verbatim quotes or summarized bullet points. Include alternatives considered.]

### Proposal 1: [short title]
- **Proposed by**: [agent name/role]
- **Content**: [the proposal]
- **Rationale**: [why the agent suggested this]

### Proposal 2: [short title]
- **Proposed by**: [agent name/role]
- **Content**: [the proposal]
- **Rationale**: [why the agent suggested this]

---

## User Modifications

[What the user changed from the agent's proposal. Be specific — show the before/after if possible.]

### Modification 1: [what was changed]
- **Original (agent proposal)**: [the original]
- **Changed to**: [the user's version]
- **Reason**: [the user's stated reason, or inferred rationale]

### Modification 2: [what was changed]
- **Original**: [the original]
- **Changed to**: [the user's version]
- **Reason**: [the reason]

---

## Rationale

[The "why" behind the user's modifications. This section is the most valuable part — it captures decision-making context that would otherwise be lost. Address:]

- Why did the user reject or modify the agent's proposal?
- What constraint, preference, or insight did the user have that the agent didn't?
- What trade-off did the user prioritize?

---

## Final Decision

[The agreed outcome. Clear and unambiguous — a future reader should know exactly what was decided.]

- **Decision**: [the decision]
- **Action items**: [what follows from this decision]
- **Follow-ups**: [open questions or deferred items]

---

## References

- [Links to related specs, plans, reviews, or other conversation files]
- [External references if any]
```

## Worked Example

Below is a condensed example based on a real decision (brand naming for the OB Dim project).

```markdown
# 05-Brand and Naming

> **Date**: 2026-07-19
> **Participants**: WorkBuddy (GLM-5.2) + 卢文锋 (user)
> **Topic**: Brand naming for the screen timeout tool + bee logo generation
> **Phase**: decision

---

## Context

The screen timeout toggle tool was functionally complete (v1.0.0, 34/34 tests passing). The remaining open question was naming and branding. The user had mentioned wanting a unified personal brand prefix for all future software.

---

## Agent Proposals

### Proposal 1: Keep the working name "ScreenTimeoutToggle"
- **Proposed by**: Engineer agent
- **Content**: Ship as `ScreenTimeoutToggle` — descriptive, matches the namespace, no rebranding effort.
- **Rationale**: Minimal work, name already accurate.

### Proposal 2: Adopt a personal brand prefix
- **Proposed by**: WorkBuddy
- **Content**: Create a brand prefix from the user's name. Suggested "LB" (initials) or "OB" (Cantonese pronunciation of 卢文锋 ≈ "老蜜蜂" → Old Bee).
- **Rationale**: User expressed wanting all future software under one brand. "OB" doubles as Observer, fitting a screen-observer tool.

---

## User Modifications

### Modification 1: Chose "OB" over "LB" or other options
- **Original (agent proposal)**: Offered both LB and OB as options.
- **Changed to**: OB — specifically "Old Bee" with the Observer double meaning.
- **Reason**: User explained the Cantonese pronunciation origin and liked the Observer angle for a screen tool.

### Modification 2: Tool name = "OB Dim"
- **Original**: Agent suggested "OB Screen" or "OB Timeout".
- **Changed to**: "OB Dim" — "Dim" as in dimming the screen.
- **Reason**: Shorter, punchier, and "dim" is the literal action.

---

## Rationale

The user wanted a brand that:
1. Ties to personal identity (name pronunciation)
2. Has a functional double meaning (Observer = watching the screen)
3. Is short enough to prefix all future tools (OB Focus, OB Pulse, etc.)

ChatGPT/DALL-E was attempted for the bee logo but refused (IP concerns around bee mascot trademarks like Honey Nut Cheerios). Resolution: user will use Midjourney/Ideogram instead, avoiding the word "bee" in prompts.

---

## Final Decision

- **Decision**: Brand = "OB" (Old Bee / Observer). Tool name = "OB Dim". Source namespace stays `ScreenTimeoutToggle` (no rename, doesn't affect function).
- **Action items**: Update README to reflect OB branding. Document logo generation workaround.
- **Follow-ups**: Generate bee logo via Midjourney/Ideogram using "flying insect with striped body" phrasing. Plan OB series future tools.

---

## References

- `conversation/00-overview-original.md` — original delivery overview
- `docs/specs/2026-07-19-screen-timeout-toggle-spec.md` — design spec
```

## Writing Tips

- **Be specific about modifications**: "User changed the name" is less useful than "User changed 'OB Screen' to 'OB Dim'".
- **Capture the "why", not just the "what"**: The rationale section is what makes these files valuable months later.
- **Include rejected alternatives**: Knowing what was considered and rejected prevents re-litigating the same decisions.
- **Link related artifacts**: Reference specs, plans, reviews, or other conversation files by relative path.
- **One topic per file**: If a conversation spans multiple unrelated topics, split into multiple numbered files.
- **Record the agent's original proposal faithfully**: Even if the user changed everything, the original proposal shows the agent's reasoning and gives context for the modifications.
