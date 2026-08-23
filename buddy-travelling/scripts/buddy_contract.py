#!/usr/bin/env python3
"""Pure, offline Buddy state and receipt contract used by semantic tests."""

from __future__ import annotations

import re
from datetime import date


TRAVEL_BUTTON = "派猫猫旅行"
DAILY_LIMIT_TEXT = "累啦，明天再来吧"
COUNTDOWN_PATTERN = re.compile(
    r"^旅行倒计时 (?:[01]\d|2[0-3]):[0-5]\d:[0-5]\d$"
)
RECEIPT_FIELDS = {
    "service_day",
    "outcome",
    "dispatch_attempted",
    "dispatch_confirmed",
    "terminal_for_day",
    "retry_allowed",
    "next_action",
}
OUTCOME_INVARIANTS = {
    "completed_cycle": (True, True, True, False, {"wait_until_next_day"}),
    "dispatch_outcome_unknown": (True, False, True, False, {"manual_status_check_only"}),
    "daily_limit_reached": (False, False, True, False, {"wait_until_next_day"}),
    "already_travelling": (False, False, True, False, {"wait_for_return"}),
    "already_handled_for_service_day": (False, False, True, False, {"honor_previous_receipt"}),
    "status_only": (False, False, False, True, {"none"}),
    "destination_unavailable": (
        False,
        False,
        False,
        False,
        {"ask_user_or_wait_for_destination_change"},
    ),
    "auth_required": (False, False, False, False, {"browser_handoff"}),
    "blocked": (
        False,
        False,
        False,
        False,
        {"manual_review_required", "provide_valid_previous_receipt"},
    ),
}


def validate_outcome_evidence(receipt: dict[str, object]) -> None:
    outcome = receipt.get("outcome")
    if outcome == "daily_limit_reached" and receipt.get("evidence_text") != DAILY_LIMIT_TEXT:
        raise ValueError("daily_limit_reached requires exact evidence_text")
    if outcome == "already_travelling":
        countdown = receipt.get("countdown")
        if not isinstance(countdown, str) or not COUNTDOWN_PATTERN.fullmatch(countdown):
            raise ValueError("already_travelling requires a valid countdown")
    if outcome == "completed_cycle":
        destination = receipt.get("destination")
        countdown = receipt.get("countdown")
        if not isinstance(destination, str) or not destination.strip():
            raise ValueError("completed_cycle requires an observed destination")
        if not isinstance(countdown, str) or not COUNTDOWN_PATTERN.fullmatch(countdown):
            raise ValueError("completed_cycle requires a valid countdown")
    if outcome == "dispatch_outcome_unknown":
        expected = receipt.get("expected_destination")
        if not isinstance(expected, str) or not expected.strip():
            raise ValueError("dispatch_outcome_unknown requires expected_destination")


def validate_service_day(value: str) -> str:
    parsed = date.fromisoformat(value)
    if parsed.isoformat() != value:
        raise ValueError("service_day must be YYYY-MM-DD")
    return value


def make_receipt(
    service_day: str,
    outcome: str,
    *,
    dispatch_attempted: bool,
    dispatch_confirmed: bool,
    terminal_for_day: bool,
    retry_allowed: bool,
    next_action: str,
    **evidence: object,
) -> dict[str, object]:
    validate_service_day(service_day)
    invariant = OUTCOME_INVARIANTS.get(outcome)
    if invariant is None:
        raise ValueError(f"unsupported receipt outcome: {outcome}")
    expected = invariant[:4]
    observed = (
        dispatch_attempted,
        dispatch_confirmed,
        terminal_for_day,
        retry_allowed,
    )
    if observed != expected:
        raise ValueError(f"receipt fields contradict outcome={outcome}")
    if next_action not in invariant[4]:
        raise ValueError(f"next_action contradicts outcome={outcome}")
    receipt: dict[str, object] = {
        "service_day": service_day,
        "outcome": outcome,
        "dispatch_attempted": dispatch_attempted,
        "dispatch_confirmed": dispatch_confirmed,
        "terminal_for_day": terminal_for_day,
        "retry_allowed": retry_allowed,
        "next_action": next_action,
    }
    receipt.update(evidence)
    validate_outcome_evidence(receipt)
    return receipt


def validate_previous_receipt(value: object) -> dict[str, object]:
    if not isinstance(value, dict) or not RECEIPT_FIELDS.issubset(value):
        raise ValueError("previous receipt is missing required fields")
    validate_service_day(str(value["service_day"]))
    for field in ("dispatch_attempted", "dispatch_confirmed", "terminal_for_day", "retry_allowed"):
        if not isinstance(value[field], bool):
            raise ValueError(f"previous receipt {field} must be boolean")
    outcome = value.get("outcome")
    invariant = OUTCOME_INVARIANTS.get(outcome)
    if invariant is None:
        raise ValueError("previous receipt has an unsupported outcome")
    observed = tuple(
        value[field]
        for field in (
            "dispatch_attempted",
            "dispatch_confirmed",
            "terminal_for_day",
            "retry_allowed",
        )
    )
    if observed != invariant[:4] or value.get("next_action") not in invariant[4]:
        raise ValueError(f"previous receipt fields contradict outcome={outcome}")
    validate_outcome_evidence(value)
    return value


def previous_receipt_gate(service_day: str, previous_receipt: object | None) -> dict[str, object]:
    """Consume an optional caller-persisted receipt without managing persistence."""
    validate_service_day(service_day)
    if previous_receipt is None:
        return {"proceed": True, "reason": None}
    try:
        previous = validate_previous_receipt(previous_receipt)
    except ValueError as exc:
        return {"proceed": False, "reason": "invalid_previous_receipt", "detail": str(exc)}
    if previous["service_day"] != service_day:
        return {"proceed": True, "reason": "previous_receipt_is_for_another_service_day"}
    if previous["dispatch_attempted"] or previous["terminal_for_day"] or not previous["retry_allowed"]:
        return {
            "proceed": False,
            "reason": "previous_receipt_blocks_same_day_dispatch",
            "previous_outcome": previous["outcome"],
        }
    return {"proceed": True, "reason": "previous_receipt_explicitly_allows_retry"}


def previous_receipt_block_receipt(service_day: str, previous_receipt: object) -> dict[str, object]:
    gate = previous_receipt_gate(service_day, previous_receipt)
    if gate["proceed"] is True:
        raise ValueError("previous receipt does not block this service day")
    if gate["reason"] == "invalid_previous_receipt":
        return make_receipt(
            service_day,
            "blocked",
            dispatch_attempted=False,
            dispatch_confirmed=False,
            terminal_for_day=False,
            retry_allowed=False,
            next_action="provide_valid_previous_receipt",
            blocker=gate["detail"],
        )
    previous = validate_previous_receipt(previous_receipt)
    return make_receipt(
        service_day,
        "already_handled_for_service_day",
        dispatch_attempted=False,
        dispatch_confirmed=False,
        terminal_for_day=True,
        retry_allowed=False,
        next_action="honor_previous_receipt",
        previous_outcome=previous["outcome"],
        previous_dispatch_attempted=previous["dispatch_attempted"],
        previous_dispatch_confirmed=previous["dispatch_confirmed"],
    )


def classify_travel_control(
    buttons: list[dict[str, object]],
    visible_texts: list[str],
    *,
    countdown_text: str | None = None,
) -> dict[str, object]:
    """Classify exact structured UI evidence; never search a combined page blob."""
    if countdown_text and COUNTDOWN_PATTERN.fullmatch(countdown_text):
        return {"state": "already_travelling", "countdown": countdown_text}
    matches = [button for button in buttons if button.get("accessible_name") == TRAVEL_BUTTON]
    if not matches:
        return {"state": "travel_state_unknown", "reason": "exact_travel_button_missing"}
    if len(matches) != 1:
        return {"state": "travel_state_unknown", "reason": "exact_travel_button_ambiguous"}
    enabled = matches[0].get("enabled")
    if enabled is True:
        return {"state": "ready_to_travel"}
    if enabled is False and visible_texts.count(DAILY_LIMIT_TEXT) == 1:
        return {"state": "daily_limit_reached", "evidence_text": DAILY_LIMIT_TEXT}
    if enabled is False and visible_texts.count(DAILY_LIMIT_TEXT) > 1:
        return {"state": "travel_state_unknown", "reason": "exact_daily_limit_text_ambiguous"}
    if enabled is False:
        return {"state": "blocked", "reason": "travel_button_disabled_without_exact_daily_limit_text"}
    return {"state": "travel_state_unknown", "reason": "travel_button_enabled_state_unknown"}


def choose_destination(options: list[dict[str, object]], requested: str | None) -> dict[str, object]:
    """Choose an exact unique enabled destination or retain one observed default."""
    if requested is not None:
        if not requested.strip():
            return {
                "state": "destination_unavailable",
                "reason": "requested_destination_empty",
                "confirm_allowed": False,
            }
        matches = [option for option in options if option.get("label") == requested]
        if len(matches) != 1:
            return {
                "state": "destination_unavailable",
                "reason": "requested_destination_missing_or_ambiguous",
                "confirm_allowed": False,
            }
        if matches[0].get("enabled") is not True:
            return {
                "state": "destination_unavailable",
                "reason": "requested_destination_disabled",
                "confirm_allowed": False,
            }
        return {
            "state": (
                "destination_ready"
                if matches[0].get("selected") is True
                else "destination_selection_required"
            ),
            "destination": requested,
            "selection_action": "keep_selected" if matches[0].get("selected") is True else "select_exact_once",
            "confirm_allowed": matches[0].get("selected") is True,
        }

    selected = [option for option in options if option.get("selected") is True]
    if (
        len(selected) != 1
        or selected[0].get("enabled") is not True
        or not isinstance(selected[0].get("label"), str)
        or not selected[0]["label"].strip()
    ):
        return {
            "state": "destination_state_unknown",
            "reason": "one_enabled_selected_default_was_not_observed",
            "confirm_allowed": False,
        }
    return {
        "state": "destination_ready",
        "destination": selected[0]["label"],
        "selection_action": "keep_default_and_read_back",
        "confirm_allowed": True,
    }


def receipt_for_observed_state(service_day: str, state: dict[str, object]) -> dict[str, object]:
    name = state.get("state")
    if name == "daily_limit_reached":
        return make_receipt(
            service_day,
            "daily_limit_reached",
            dispatch_attempted=False,
            dispatch_confirmed=False,
            terminal_for_day=True,
            retry_allowed=False,
            next_action="wait_until_next_day",
            evidence_text=state.get("evidence_text"),
        )
    if name == "already_travelling":
        return make_receipt(
            service_day,
            "already_travelling",
            dispatch_attempted=False,
            dispatch_confirmed=False,
            terminal_for_day=True,
            retry_allowed=False,
            next_action="wait_for_return",
            countdown=state.get("countdown"),
        )
    return make_receipt(
        service_day,
        "blocked",
        dispatch_attempted=False,
        dispatch_confirmed=False,
        terminal_for_day=False,
        retry_allowed=False,
        next_action="manual_review_required",
        blocker=state.get("reason") or name,
    )


def status_only_receipt(service_day: str, observed_state: str, **observed: object) -> dict[str, object]:
    return make_receipt(
        service_day,
        "status_only",
        dispatch_attempted=False,
        dispatch_confirmed=False,
        terminal_for_day=False,
        retry_allowed=True,
        next_action="none",
        observed_state=observed_state,
        **observed,
    )


def destination_unavailable_receipt(service_day: str, decision: dict[str, object]) -> dict[str, object]:
    return make_receipt(
        service_day,
        "destination_unavailable",
        dispatch_attempted=False,
        dispatch_confirmed=False,
        terminal_for_day=False,
        retry_allowed=False,
        next_action="ask_user_or_wait_for_destination_change",
        blocker=decision.get("reason"),
    )


def dispatch_receipt(
    service_day: str,
    expected_destination: str,
    active_status_text: str | None,
    countdown_text: str | None,
) -> dict[str, object]:
    """A confirm click is attempted; only both exact readbacks prove completion."""
    if not isinstance(expected_destination, str) or not expected_destination.strip():
        raise ValueError("expected_destination must be a non-empty observed label")
    expected_status = f"Buddy 正在 {expected_destination} 采风中..."
    confirmed = active_status_text == expected_status and bool(countdown_text and COUNTDOWN_PATTERN.fullmatch(countdown_text))
    if confirmed:
        return make_receipt(
            service_day,
            "completed_cycle",
            dispatch_attempted=True,
            dispatch_confirmed=True,
            terminal_for_day=True,
            retry_allowed=False,
            next_action="wait_until_next_day",
            destination=expected_destination,
            countdown=countdown_text,
        )
    return make_receipt(
        service_day,
        "dispatch_outcome_unknown",
        dispatch_attempted=True,
        dispatch_confirmed=False,
        terminal_for_day=True,
        retry_allowed=False,
        next_action="manual_status_check_only",
        expected_destination=expected_destination,
        active_status_text=active_status_text,
        countdown=countdown_text,
    )
