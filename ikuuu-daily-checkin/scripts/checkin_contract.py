"""Classify chronological page evidence without rewriting a submitted click."""


def classify_checkin(evidence):
    before, after = evidence["before"], evidence["after"]
    attempted, popup = evidence["click_attempted"], evidence["reward_popup"]
    if before not in ("available", "done", "unknown"):
        raise ValueError("before must describe the pre-click check-in control")
    if after not in ("done", "not_done", "unknown"):
        raise ValueError("after must describe the final check-in control")
    if attempted is not None and type(attempted) is not bool:
        raise ValueError("click_attempted must be true, false or null")
    if popup not in ("new", "preexisting", "unknown"):
        raise ValueError("unsupported reward_popup evidence")
    action = "unknown" if attempted is None else ("clicked_once" if attempted else "not_clicked")
    # A call is an attempt even if it hit a disabled/wrong control or timed out.
    # Final 'done' alone never proves the pre-click state or a new reward.
    outcome = "uncertain"
    if attempted is True and before == "available" and after == "done":
        outcome = "success"
    elif attempted is False and before == "done" and after == "done":
        outcome = "already_checked_in"
    elif attempted is False and before == "available" and after == "not_done":
        outcome = "not_completed"
    return {"outcome": outcome, "action": action,
            "reward_eligible": outcome == "success" and popup == "new"}
