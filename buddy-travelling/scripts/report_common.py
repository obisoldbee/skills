"""Small, offline presentation contract. No browser, network or state writes."""
import json
import sys


def short_text(value, name, limit=80):
    if not isinstance(value, str) or not value.strip() or len(value) > limit:
        raise ValueError(f"{name} must be nonempty text up to {limit} characters")
    if any(c in value for c in "\r\n\t") or "```" in value:
        raise ValueError(f"{name} must be a single plain-text line")
    return value.strip()


def page_text(page):
    status = page["status"]
    labels = {"closed": "已关闭", "preserved": "已保留", "unconfirmed": "关闭未确认", "failed": "关闭失败",
              "not_created": "未创建"}
    if status not in labels:
        raise ValueError("unsupported page status")
    value = labels[status]
    if status in ("preserved", "unconfirmed", "failed") and page.get("space_id") is not None:
        if type(page["space_id"]) is not int or page["space_id"] < 0:
            raise ValueError("space_id must be a nonnegative integer")
        value += f"（空间 {page['space_id']}）"
    return value


def notification_text(notices):
    if not isinstance(notices, list):
        raise ValueError("notifications must be a list of actual attempts")
    if not notices:
        return "未触发"
    kinds = {"auth": "登录提醒", "failure": "异常提醒", "low_traffic": "低流量提醒",
             "maintenance_entered": "维护开始提醒", "maintenance_recovered": "维护结束提醒"}
    statuses = {"sent": "已发送", "failed": "发送失败", "unknown": "发送未确认",
                "needs_configuration": "缺少配置"}
    labels = []
    for notice in notices:
        kind, status = notice["kind"], notice["status"]
        if kind not in kinds or status not in statuses:
            raise ValueError("unsupported notification kind/status")
        if status == "sent":
            short_text(notice.get("message_id"), "sent message_id", 128)
        label = kinds[kind] + statuses[status]
        if label not in labels:
            labels.append(label)
    return "；".join(labels)


def finish_lines(lines, data, *, normal, maintenance=False):
    page = page_text(data["page"])
    notices = notification_text(data["notifications"])
    if normal and data["page"]["status"] in ("preserved", "unconfirmed", "failed"):
        lines[1] += "（页面收尾异常）"
    if maintenance and data.get("maintenance_unchanged") is True and not data["notifications"]:
        notices = "持续维护，未重复提醒"
    lines += ["页面：" + page, "飞书：" + notices]
    # Only a real blocker/action belongs here. Empty optional fields are omitted.
    for key, label in (("reason", "原因"), ("action", "需处理")):
        if data.get(key):
            lines.append(label + "：" + short_text(data[key], key))
    return "\n".join(lines)


def main(render):
    # The CLI contract is UTF-8, including pipes on Windows legacy code pages.
    for stream in (sys.stdin, sys.stdout, sys.stderr):
        stream.reconfigure(encoding="utf-8")
    try:
        data = json.load(sys.stdin)
        print(render(data))
    except (ValueError, TypeError, KeyError) as exc:
        # Fail closed without dumping inputs (which may contain private evidence).
        print(f"report_input_error: {exc}", file=sys.stderr)
        raise SystemExit(2)
