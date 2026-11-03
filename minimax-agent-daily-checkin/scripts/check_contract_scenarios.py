#!/usr/bin/env python3
"""Offline contract oracle for synthetic or separately supplied action traces.

This does NOT execute a Skill, classify natural-language intent, call a model,
browser, Mavis or Lark, or persist retry state. Intent/evidence labels are fixture
assumptions. Passing proves only trace invariants under those assumptions.
Use --traces PATH to check another JSON packet with the same schema.

Each packet case represents one recovered session run: cron means its confirmed
owned reminder, not an arbitrary external reminder. A continued browser round
must include the prior round, retry decision, report and consumed wake in the
trace; a bare initial round/cron snapshot cannot authorize another browser.
Initial snapshots remain useful for query-only and terminal-cleanup scenarios.
MiniMax check-in routing is explicit: ``checkin_card`` records whether the card
was directly visible and whether the round used that card or the menu fallback.
"""
from __future__ import annotations

import argparse
import copy
import json
from pathlib import Path


def require(condition, message):
    if not condition:
        raise AssertionError(message)


def check(case, service):
    retryable = ({"site_unreachable", "uncertain", "failed"} if service == "ikuuu"
                 else {"network", "points_unverified", "unknown"})
    already = "already_checked_in" if service == "ikuuu" else "already_completed"
    attention_outcomes = ({"needs_user_action"} if service == "ikuuu"
                          else {"login_failed", "page_changed", "blocked_manual_action"})
    mode = case["intent"]
    scheduled = case.get("scheduled", False)
    authority = case.get("authorized", False)
    target = case.get("target_present", False)
    eligible = mode == "execute" and scheduled and authority and target
    terminal = case.get("terminal", False)
    cron = case.get("cron", False)
    round_no = case.get("round", 0)
    created = case.get("create_attempted", cron)
    create_pending = False
    deletes = set(case.get("deletes", []))
    delete_pending = None
    notices = set(case.get("notices", []))
    notice_pending = None
    active = False
    cleaned = True
    cleanup_failed = False
    woke_terminal = False
    waiting = False
    wake_ready = False
    retry_ready = False
    terminal_required = False
    round_reported = False
    claims = logins = 0
    outcome = None
    observed = {}
    completed_seen = False
    points_verified = False
    reports = 0
    browser_count = 0
    checkin_route_seen = False

    for event in case["events"]:
        action = event["action"]
        if mode == "ambiguous":
            require(action == "report", "ambiguous intent may only ask")
        if mode == "query-only":
            require(action in {"browser", "checkin_card", "observe", "cleanup", "report"},
                    "query must not mutate check-in or orchestration")
        if woke_terminal:
            require(action in {"reserve_delete", "delete", "report", "wake"},
                    "terminal wake may only clean residue or report")
        if terminal_required:
            require(action == "mark_terminal", "terminal result must finalize before continuing")
        if create_pending:
            require(action == "create", "reminder creation result missing")
        if delete_pending is not None:
            require(action == "delete", "reminder deletion result missing")
        if notice_pending is not None:
            require(action == "notify", "notification result missing")
        if action in {"reserve_create", "create", "reuse",
                      "reserve_notification", "notify"}:
            require(eligible, "scheduled effect requires execution authority and target")
        if action in {"reserve_delete", "delete"}:
            require(mode == "execute" and scheduled and authority,
                    "delete needs originating run authorization")

        if action == "browser":
            require(mode != "ambiguous" and (not terminal or mode == "query-only"),
                    "browser after stop")
            require(case.get("runtime_ready", True), "runtime unavailable")
            require(mode == "query-only" or not scheduled or eligible,
                    "incomplete scheduled configuration")
            require(not active and cleaned and not cleanup_failed,
                    "new browser before successful cleanup")
            if mode == "execute":
                if scheduled and round_no > 0:
                    require(cron and wake_ready,
                            "next round requires a confirmed same-run reminder wake")
                round_no += 1
                require(round_no <= (10 if scheduled else 1), "round limit")
                require(event["round"] == round_no, "round must not reset or skip")
            active = True
            cleaned = False
            waiting = False
            wake_ready = retry_ready = False
            round_reported = False
            claims = logins = 0
            outcome = event.get("outcome")
            observed = {}
            completed_seen = False
            points_verified = False
            checkin_route_seen = False
            browser_count += 1
        elif action == "checkin_card":
            require(active, "check-in routing requires an active query/round")
            require(not checkin_route_seen, "duplicate check-in routing")
            require(isinstance(event.get("direct_visible"), bool),
                    "check-in routing needs direct-card visibility")
            require(event.get("route") in {"direct", "menu"}, "unknown check-in route")
            require((event["route"] == "direct") == event["direct_visible"],
                    "visible card must be used directly; menu is fallback only")
            checkin_route_seen = True
        elif action in {"login", "claim"}:
            require(active and mode == "execute" and not terminal, "unapproved click")
            if action == "login":
                logins += 1
                require(logins <= 1, "duplicate login")
            else:
                require(checkin_route_seen, "claim requires this round's check-in routing")
                require(not completed_seen and outcome != already,
                        "claim forbidden after completed observation or already-completed result")
                claims += 1
                require(claims <= 1, "duplicate claim")
        elif action == "observe":
            require(active, "observation requires active query/round")
            if service == "minimax" and "completed" in event:
                require(checkin_route_seen,
                        "check-in status observation requires this round's routing")
            observed.update({k: v for k, v in event.items() if k != "action"})
            completed_seen = completed_seen or event.get("completed", False)
        elif action == "verify_points":
            require(active and mode == "execute" and claims == 1,
                    "delta verification requires this round's claim")
            require(event["after"] - event["before"] == event["reward"],
                    "points mismatch cannot prove success")
            points_verified = True
        elif action == "cleanup":
            require(active, "cleanup without owned round")
            if case.get("require_checkin_route", False):
                require(checkin_route_seen, "required check-in routing was not recorded")
            require(event["result"] in {"closed", "handed_off", "failed"},
                    "unknown cleanup result")
            if event["result"] != "failed":
                expected_cleanup = "handed_off" if outcome in attention_outcomes else "closed"
                require(event["result"] == expected_cleanup,
                        "cleanup disposition does not match the round outcome")
            # Validate this round before a later browser can reset its evidence.
            if mode == "execute" and outcome in {"success", already}:
                require(observed.get("completed") and observed.get("fresh_balance"),
                        "successful execution needs completion and fresh balance")
                require(outcome != already or claims == 0,
                        "already-completed result requires zero claims")
                if service == "minimax" and claims:
                    require(points_verified, "new MiniMax success needs matched points")
            active = False
            cleaned = event["result"] != "failed"
            cleanup_failed = not cleaned
            if cleanup_failed:
                outcome = "browser_cleanup"
            if mode == "execute" and scheduled:
                retry_ready = (event["result"] == "closed" and outcome in retryable
                               and round_no < 10)
                terminal_required = not retry_ready
        elif action == "mark_terminal":
            require(mode == "execute" and scheduled, "terminal is scheduled state")
            require(not active, "record browser cleanup before finalizing")
            terminal = True
            terminal_required = waiting = wake_ready = retry_ready = False
        elif action == "reserve_create":
            require(not terminal and retry_ready,
                    "creation requires this service's closed retryable round below ten")
            require(not created and not cron, "only one reminder creation attempt")
            retry_ready = False
            created = create_pending = True
        elif action == "create":
            require(create_pending and not terminal, "unreserved/duplicate create")
            create_pending = False
            if event["result"] == "ok":
                cron = waiting = True
            else:
                require(event["result"] in {"failed", "unknown"}, "bad create result")
                waiting = False
                terminal_required = True
        elif action == "reuse":
            require(cron and not terminal and retry_ready,
                    "reuse requires this service's closed retryable round below ten")
            retry_ready = False
            waiting = True
        elif action == "reserve_delete":
            stage = event["stage"]
            require(terminal and cron, "terminal must precede owned reminder deletion")
            require(stage in {"terminal", "residual"} and stage not in deletes
                    and delete_pending is None, "duplicate deletion attempt")
            require((stage == "residual") == woke_terminal, "wrong cleanup phase")
            if stage == "residual":
                require("terminal" in deletes, "residue follows terminal attempt")
            deletes.add(stage)
            delete_pending = stage
        elif action == "delete":
            require(delete_pending == event["stage"], "unreserved deletion")
            delete_pending = None
            require(event["result"] in {"ok", "failed", "unknown"}, "bad delete result")
            if event["result"] == "ok":
                cron = False
        elif action == "reserve_notification":
            kind = event["kind"]
            require(cleaned and not cleanup_failed and not active, "notify before cleanup")
            require(kind not in notices and notice_pending is None,
                    "notification reservation is one-shot")
            if terminal and cron:
                require("terminal" in deletes, "terminal deletion precedes notification")
            if service == "minimax":
                require(terminal, "MiniMax notifications finalize first")
                if kind == "attention":
                    require(outcome in {"login_failed", "page_changed", "blocked_manual_action"},
                            "attention predicate")
                else:
                    require(kind == "failed" and round_no == 10
                            and outcome not in {"success", "already_completed", "login_failed",
                                                "page_changed", "blocked_manual_action",
                                                "browser_cleanup"}, "failed notification predicate")
            elif kind == "low":
                scales = {"MB": 1 / 1024, "GB": 1, "TB": 1024}
                unit = observed.get("unit")
                require(observed.get("fresh_balance") and unit in scales
                        and 0 <= observed["balance"] * scales[unit] < 20,
                        "low traffic needs fresh strict-below-20-GB evidence")
            else:
                require(kind == "failed" and round_no == 10
                        and outcome not in {"success", "already_checked_in", "browser_cleanup"},
                        "failed notification predicate")
            notices.add(kind)
            notice_pending = kind
        elif action == "notify":
            require(notice_pending == event["kind"] and not woke_terminal,
                    "unreserved or repeated notification")
            require(event["result"] in {"ok", "failed", "unknown"}, "bad send result")
            notice_pending = None
            if service == "minimax":
                require(terminal, "send failure must not reactivate run")
        elif action == "wake":
            require(not active, "wake during browser round")
            if terminal:
                woke_terminal = True
            else:
                require(waiting and cron and round_reported,
                        "wake requires a reported retry and confirmed same-run reminder")
                waiting = False
                wake_ready = True
        elif action == "report":
            require(not active, "report before browser cleanup")
            if scheduled and mode == "execute" and browser_count:
                require(terminal or waiting, "each round needs a retry-or-terminal decision")
            round_reported = True
            reports += 1
            if mode == "query-only":
                require(event["kind"] == "query", "query is not execution success/failure")
            elif mode == "ambiguous":
                require(event["kind"] == "clarify", "ambiguity needs clarification")
            elif woke_terminal:
                require(event["kind"] == "terminal", "wake must report no fresh round")
            elif scheduled and not eligible and browser_count == 0 and not terminal:
                require(event["kind"] == "clarify", "configuration gate must not fake a round")
        else:
            raise AssertionError("unknown trace action: " + action)

    require(not active and reports > 0, "trace needs cleanup and report")
    if browser_count:
        require(round_reported, "last completed round needs its own report")
    require(not terminal_required, "terminal outcome escaped finalizer")
    require(not create_pending and notice_pending is None, "reserved effect result missing")
    require(delete_pending is None, "deletion result missing")
    if eligible and not case.get("runtime_ready", True):
        require(terminal, "runtime failure must finalize the scheduled run")
    if scheduled and mode == "execute" and browser_count:
        require(terminal or waiting, "retryable round needs bounded retry or terminal stop")
    if terminal and cron and authority and mode == "execute":
        require("terminal" in deletes, "existing terminal reminder was not cleaned")
    return True


def mutations(case):
    """Reject corrupt traces, not just accept hand-authored positive examples."""
    if case["intent"] == "query-only":
        for index, event in enumerate(case["events"]):
            if event["action"] == "browser":
                bad = copy.deepcopy(case)
                bad["events"].insert(index + 1, {"action": "claim"})
                yield "query-claim", bad
                break
    if case.get("terminal") or any(e["action"] == "mark_terminal" for e in case["events"]):
        bad = copy.deepcopy(case)
        bad["events"].append({"action": "browser", "round": 1})
        yield "terminal-reopen", bad
        bad = copy.deepcopy(case)
        bad["events"] = [e for e in bad["events"] if e["action"] != "mark_terminal"]
        if not case.get("terminal"):
            yield "missing-terminal", bad
    if case["intent"] == "ambiguous" or (
        case.get("scheduled") and case["intent"] == "execute"
        and not (case.get("authorized") and case.get("target_present"))
    ):
        bad = copy.deepcopy(case)
        bad["events"].insert(0, {"action": "browser", "round": 1})
        yield "ungated-browser", bad
    for index, event in enumerate(case["events"]):
        if event["action"] == "wake" and not case.get("terminal") and not any(
            e["action"] == "mark_terminal" for e in case["events"][:index]
        ):
            next_step = next((e["action"] for e in case["events"][index + 1:]
                              if e["action"] in {"browser", "mark_terminal"}), None)
            if next_step == "browser":
                bad = copy.deepcopy(case)
                del bad["events"][index]
                yield "missing-retry-wake", bad
            bad = copy.deepcopy(case)
            bad["events"].insert(index + 1, copy.deepcopy(event))
            yield "duplicate-retry-wake", bad
        if event["action"] in {"reserve_create", "reuse", "reserve_delete", "reserve_notification", "claim"}:
            bad = copy.deepcopy(case)
            bad["events"].insert(index + 1, copy.deepcopy(event))
            yield "duplicate-" + event["action"], bad
        if event["action"] == "claim":
            bad = copy.deepcopy(case)
            bad["events"].insert(index, {"action": "observe", "completed": True})
            yield "claim-after-completed", bad
        if event["action"] == "verify_points":
            bad = copy.deepcopy(case)
            bad["events"][index]["after"] += 1
            yield "mismatched-points", bad
        if event["action"] == "checkin_card":
            bad = copy.deepcopy(case)
            bad["events"][index]["route"] = (
                "menu" if event["route"] == "direct" else "direct"
            )
            yield "wrong-checkin-route", bad
            if case.get("require_checkin_route", False):
                bad = copy.deepcopy(case)
                del bad["events"][index]
                yield "missing-checkin-route", bad


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--traces", type=Path,
                        default=Path(__file__).resolve().parents[1] / "tests/contract_scenarios.json")
    args = parser.parse_args()
    packet = json.loads(args.traces.read_text(encoding="utf-8"))
    cases = packet["cases"]
    require(packet["service"] in {"ikuuu", "minimax"}, "unsupported service")
    require(len({case["id"] for case in cases}) == len(cases), "duplicate scenario id")
    mutation_count = 0
    for case in cases:
        try:
            check(case, packet["service"])
            for name, bad in mutations(case):
                try:
                    check(bad, packet["service"])
                except AssertionError:
                    mutation_count += 1
                else:
                    raise AssertionError("accepted forbidden mutation " + name)
        except AssertionError as exc:
            raise SystemExit(case["id"] + ": " + str(exc)) from exc
    for case in packet.get("invalid_cases", []):
        try:
            check(case, packet["service"])
        except AssertionError:
            mutation_count += 1
        else:
            raise SystemExit(case["id"] + ": accepted forbidden trace")
    print(json.dumps({"service": packet["service"], "synthetic_scenarios": len(cases),
                      "rejected_mutations": mutation_count, "result": "PASS",
                      "model_evaluation": False, "live_runtime_evaluation": False},
                     ensure_ascii=False))


if __name__ == "__main__":
    main()
