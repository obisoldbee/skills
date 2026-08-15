#!/usr/bin/env python3
import argparse
import datetime as dt
import os
import subprocess


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
- recipient capabilities: create_thread=unknown, CLI=unknown, filesystem=unknown

## 当前目标
-

## 任务图、路由与负责人
- run id:
- Controller:
- integration owner:
- active/ready/blocked lanes:
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
-
"""
    )


if __name__ == "__main__":
    main()
