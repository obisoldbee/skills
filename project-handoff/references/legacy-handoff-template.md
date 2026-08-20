# Complete Portable Handoff

Use for `complete`, `full`, `manual`, `text-only`, `file-only`, or `完整交接` mode; for an external recipient; for progress transfer; or when the recipient lacks direct thread or CLI capabilities. The filename remains `legacy-handoff-template.md` only for compatibility.

~~~markdown
# Complete Project Handoff

## 交接类型与接收方
- type: complete
- recipient:
- recipient capabilities: create_thread=<yes/no/unknown>, CLI=<yes/no/unknown>, filesystem=<scope/unknown>
- harness:

## 项目与目录
- cwd:
- repository/workspace:
- file access: read_only | write
- workspace mode: shared_checkout | worktree | non_git
- worktree source:
- Repository Root (actual lane Git top-level):
- workspace path:
- base revision:
- actual environment receipt:

## 当前目标
- 用户当前要完成什么:
- 不要做什么:

## 任务图、路由与负责人
- run id:
- Controller:
- integration owner:
- active/ready/blocked lanes:
- lane read/write paths and mutable resources:
- dependencies and phase gates:
- explicit model/reasoning choices to preserve:

## 已完成
-

## 当前状态
- 本地服务:
- 远程服务:
- 最近验证:

## 关键文件
- <path> — access=<direct/paste/package/unavailable>; role=<input/output/evidence>

## 关键决策
-

## 验证与集成状态
- lane validations:
- integrated outputs:
- full validation:
- stale/superseded outputs:

## 失败、重试、中止与归档
- retry budget/attempts:
- failed or aborted lanes:
- archived task receipts:

## 待处理
-

## 风险/需复核
-

## 接收 Agent 第一动作
-
~~~

Rules:

- Keep paths absolute.
- Distinguish materials the recipient can access from materials that must be pasted or packaged.
- Put exact commands only when useful and safe.
- Mark unverified volatile facts as `需复核`.
- Replace secrets with `<redacted>` or describe where they are configured.
- Do not copy full chat history, full PRDs, or long logs.
- Do not call a model or create a task merely to produce this artifact.
- Preserve dependency, lifecycle, route-basis, and integration state when transferring a Controller run; do not reduce it to a prose progress summary.
- Do not mark an external harness lane running from this handoff alone. Require current launch or disk/Git readback for the exact workspace and base.
- If the recipient changes from review to repair, require a new write-scope and execution-environment decision before any edit.
- Do not call multi-Agent use successful unless required artifacts, lane validation, and the integration gate are closed.
