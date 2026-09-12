#!/usr/bin/env python3
"""Render a validated Buddy receipt as one compact, human-readable report."""
from buddy_contract import validate_previous_receipt
from report_common import finish_lines, main, short_text


OUTCOMES = {
    "completed_cycle": "已完成（本轮已派出）",
    "already_travelling": "旅行中（本轮未派出）",
    "daily_limit_reached": "今日次数已用完",
    "already_handled_for_service_day": "今日已处理（本轮未派出）",
    "dispatch_outcome_unknown": "派出结果未确认（本轮已尝试，勿重复派出）",
    "auth_required": "需登录",
    "destination_unavailable": "未派出（目的地不可用）",
    "maintenance": "维护中（本轮未派出）",
    "blocked": "未完成",
    "status_only": "查询完成（本轮未派出）",
}
NORMAL = {"completed_cycle", "already_travelling", "daily_limit_reached",
          "already_handled_for_service_day", "status_only"}


def render(data):
    receipt = validate_previous_receipt(data["receipt"])
    outcome = receipt["outcome"]
    result = OUTCOMES[outcome]
    if outcome == "already_handled_for_service_day" and receipt.get("previous_outcome") in (
            "dispatch_outcome_unknown", "blocked", "auth_required", "destination_unavailable"):
        result = "此前结果仍未解决（本轮未派出）"
    if outcome == "status_only":
        observed = receipt.get("observed_state")
        result = {"already_travelling": "旅行中（本轮未派出）",
                  "ready_to_travel": "可旅行（本轮未派出）",
                  "daily_limit_reached": "今日次数已用完"}.get(observed, "状态未确认")
    gift = data["gift"]
    if gift == "claimed":
        points = data["points"]
        if type(points) is not int or points < 0:
            raise ValueError("claimed points must be an observed nonnegative integer")
        gift_text = f"{points} 积分（本轮已领取）"
    elif gift in ("not_claimed", "unknown"):
        if data.get("points") is not None:
            raise ValueError("unclaimed/unconfirmed gift cannot carry confirmed points")
        gift_text = "本轮未领取" if gift == "not_claimed" else "领取未确认"
    else:
        raise ValueError("unsupported gift status")
    if outcome == "status_only" and gift == "claimed":
        result = "已领取礼物（本轮未派出）"
    lines = [f"Buddy｜{receipt['service_day']}", "结果：" + result, "领取：" + gift_text]
    # Expected destinations and stale receipt values are never presented as a
    # confirmed trip. An unknown dispatch has no confirmed travel row.
    if outcome in ("completed_cycle", "already_travelling", "status_only"):
        parts = []
        if receipt.get("destination"):
            parts.append(short_text(receipt["destination"], "destination", 30))
        if receipt.get("countdown"):
            from buddy_contract import COUNTDOWN_PATTERN
            if not COUNTDOWN_PATTERN.fullmatch(receipt["countdown"]):
                raise ValueError("invalid countdown")
            parts.append("剩余 " + receipt["countdown"].removeprefix("旅行倒计时 "))
        if parts:
            lines.append("旅行：" + " · ".join(parts))
    return finish_lines(lines, data, normal=outcome in NORMAL,
                        maintenance=outcome == "maintenance")


if __name__ == "__main__":
    main(render)
