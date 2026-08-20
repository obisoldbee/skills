#!/usr/bin/env python3
import argparse
import datetime as dt
import os
import subprocess
import sys


def run(cmd, cwd):
    try:
        proc = subprocess.run(
            cmd,
            cwd=cwd,
            text=True,
            capture_output=True,
            timeout=5,
            check=False,
        )
    except Exception as exc:
        return f"unavailable: {exc}"
    output = (proc.stdout or proc.stderr).strip()
    return output[:1200] if output else "no output"


def main():
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(
        description="Print a complete portable project handoff scaffold."
    )
    parser.add_argument("--cwd", default=os.getcwd(), help="Project directory.")
    args = parser.parse_args()

    cwd = os.path.abspath(args.cwd)
    now = dt.datetime.now().astimezone().isoformat(timespec="seconds")
    git_status = (
        run(["git", "status", "--short"], cwd)
        if os.path.isdir(os.path.join(cwd, ".git"))
        else "not a git repository or .git not in cwd"
    )

    print(
        f"""# Complete Project Handoff

created_at: {now}
cwd: {cwd}

## 交接类型与接收方
- type: complete
- recipient:
- harness:
- recipient capabilities: create_thread=unknown, CLI=unknown, filesystem=unknown

## 项目、执行环境与权限
- file access: read_only | write
- workspace mode: shared_checkout | worktree | non_git
- worktree source:
- Repository Root (actual lane Git top-level):
- workspace path: {cwd}
- base revision (full commit for Git; verified content-state digest for non-Git):
- environment receipt: pending; this scaffold alone never proves launch or write authority

## 当前目标
-

## 任务图、路由与负责人
- run id:
- Controller:
- integration owner:
- active/ready/blocked lanes:
- lane read paths:
- lane write paths:
- mutable resources:
- dependencies and phase gates:
- explicit model/reasoning choices to preserve:

## 已完成
-

## 当前状态
- git status: {git_status}
- local services:
- remote services:

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
- Read back the actual workspace, base, and current state before doing work.
- If this is an external-harness handoff, remain standby until launch/environment evidence exists.
- If review changes to repair, re-plan file access, write scope, conflicts, and environment before editing.
"""
    )


if __name__ == "__main__":
    main()
