#!/usr/bin/env python3
"""Render the observed check-in result; never infer reward from an old popup."""
import re
from datetime import date
from checkin_contract import classify_checkin
from report_common import finish_lines, main


OUTCOMES = {
    "success": "签到成功（本轮已签到）",
    "already_checked_in": "已签到（本轮未重复签到）",
    "not_completed": "尚未签到（仅查询）",
    "maintenance": "维护中（本轮业务暂停）",
    "needs_user_action": "需人工处理",
    "needs_configuration": "未执行（缺少配置）",
    "runtime_unavailable": "未执行（运行环境不可用）",
    "site_unreachable": "失败（已尝试入口均不可用）",
    "uncertain": "未确认",
    "failed": "失败",
    "unknown": "未确认",
}
AMOUNT = re.compile(r"\d+(?:\.\d+)? (?:MB|GB|TB)")


def amount(value, name):
    if not isinstance(value, str) or not AMOUNT.fullmatch(value):
        raise ValueError(f"{name} requires a nonnegative number and MB/GB/TB")
    return value


def render(data):
    day = data["service_day"]
    if date.fromisoformat(day).isoformat() != day:
        raise ValueError("service_day must be YYYY-MM-DD")
    decision = classify_checkin(data["checkin_evidence"])
    action = decision["action"]
    outcome = data.get("outcome", decision["outcome"])
    if outcome not in OUTCOMES:
        raise ValueError("unsupported outcome")
    if data.get("checkin_action", action) != action:
        raise ValueError("checkin_action contradicts the actual click attempt")
    if outcome in ("success", "already_checked_in", "not_completed") and outcome != decision["outcome"]:
        raise ValueError("outcome contradicts chronological check-in evidence")
    verified = data["reward_verified"]
    if type(verified) is not bool or type(data["balance_verified"]) is not bool:
        raise ValueError("evidence flags must be boolean")
    if verified:
        if not decision["reward_eligible"]:
            raise ValueError("a preexisting popup does not prove this run earned a reward")
        reward = amount(data["reward"], "reward")
    else:
        if data.get("reward") is not None:
            raise ValueError("unverified reward must be null")
        reward = None
    if data["balance_verified"]:
        balance = amount(data["balance"], "balance")
    else:
        if data.get("balance") is not None:
            raise ValueError("unverified balance must be null")
        balance = "未确认"
    normal = outcome in ("success", "already_checked_in", "not_completed")
    if normal and not data["balance_verified"]:
        raise ValueError("normal completion requires verified balance")
    result = OUTCOMES[outcome]
    if outcome in ("uncertain", "unknown") and action == "clicked_once":
        result += "（本轮已尝试签到）"
    if reward is not None:
        result += "；奖励 " + reward
    lines = [f"Ikuuu｜{day}", "结果：" + result,
             "剩余流量：" + balance]
    return finish_lines(lines, data, normal=normal, maintenance=outcome == "maintenance")


if __name__ == "__main__":
    main(render)
