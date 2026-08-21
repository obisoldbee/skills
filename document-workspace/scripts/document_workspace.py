#!/usr/bin/env python3
"""Offline CLI for one exact document workspace."""

from __future__ import annotations

import argparse
import json
import sys
from typing import Any

from workspace_core import (
    ARTIFACT_KINDS,
    RELIABILITY_VALUES,
    SOURCE_CLASSES,
    WorkspaceError,
    apply_approve,
    apply_archive,
    apply_artifact,
    apply_conversation,
    apply_initialize,
    apply_preserve,
    inventory_report,
    plan_approve,
    plan_archive,
    plan_artifact,
    plan_conversation,
    plan_initialize,
    plan_preserve,
    plan_with_token,
    validate_workspace,
)


def emit(value: dict[str, Any]) -> None:
    print(json.dumps(value, ensure_ascii=False, indent=2, sort_keys=True))


def add_apply_options(parser: argparse.ArgumentParser) -> None:
    parser.add_argument(
        "--apply",
        action="store_true",
        help="Apply only after reviewing a dry-run from the same command.",
    )
    parser.add_argument(
        "--plan-token",
        help="Exact plan_token emitted by the prior dry-run.",
    )


def parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(
        description=(
            "Inventory, initialize, preserve, register, approve, archive, and validate "
            "one exact local document workspace. Every mutating command is a dry-run by default."
        )
    )
    subparsers = parser.add_subparsers(dest="command", required=True)

    inventory = subparsers.add_parser("inventory", help="Read-only byte/hash inventory.")
    inventory.add_argument("workspace")

    initialize = subparsers.add_parser(
        "initialize",
        help=(
            "Initialize an empty folder or adopt a populated folder without moving originals; "
            "unknown regular-file suffixes are preserved as unclassified raw material."
        ),
    )
    initialize.add_argument("workspace")
    initialize.add_argument("--timestamp", required=True)
    initialize.add_argument(
        "--upstream-derived",
        action="append",
        default=[],
        metavar="RELATIVE_PATH",
        help="Classify one inventoried machine-generated input as upstream-derived and unverified.",
    )
    add_apply_options(initialize)

    preserve = subparsers.add_parser(
        "preserve",
        help=(
            "Byte-preserve one explicitly named attachment before depending on it; "
            "an unknown regular-file suffix alone is not a refusal."
        ),
    )
    preserve.add_argument("workspace")
    preserve.add_argument("--source", required=True)
    preserve.add_argument("--original-path", required=True)
    preserve.add_argument("--source-class", choices=sorted(SOURCE_CLASSES), required=True)
    preserve.add_argument("--reliability", choices=sorted(RELIABILITY_VALUES), required=True)
    preserve.add_argument("--received-at", default="unknown")
    preserve.add_argument("--event-at", default="unknown")
    preserve.add_argument("--timestamp", required=True, help="Known import timestamp.")
    preserve.add_argument("--derived-from", action="append", default=[])
    add_apply_options(preserve)

    conversation = subparsers.add_parser(
        "conversation",
        help="Create a complete no-clobber decision record.",
    )
    conversation.add_argument("workspace")
    conversation.add_argument("--conversation-id", required=True)
    conversation.add_argument("--timestamp", required=True)
    conversation.add_argument("--proposal", required=True)
    conversation.add_argument("--user-correction", required=True)
    conversation.add_argument("--reason", required=True)
    conversation.add_argument("--final-decision", required=True)
    add_apply_options(conversation)

    artifact = subparsers.add_parser(
        "artifact",
        help="Register an existing work/derived or work/drafts file and its derivation.",
    )
    artifact.add_argument("workspace")
    artifact.add_argument("--path", required=True)
    artifact.add_argument("--kind", choices=sorted(ARTIFACT_KINDS), required=True)
    artifact.add_argument("--timestamp", required=True)
    artifact.add_argument("--reliability", choices=sorted(RELIABILITY_VALUES), required=True)
    artifact.add_argument("--derived-from", action="append", default=[])
    add_apply_options(artifact)

    approve = subparsers.add_parser(
        "approve",
        help="Copy registered drafts into the explicit current formal version.",
    )
    approve.add_argument("workspace")
    approve.add_argument("--version-id", required=True)
    approve.add_argument("--file", action="append", default=[], required=True)
    approve.add_argument("--conversation", required=True)
    approve.add_argument("--timestamp", required=True)
    add_apply_options(approve)

    archive = subparsers.add_parser(
        "archive",
        help="Archive one rejected draft batch or the exact superseded current version.",
    )
    archive.add_argument("workspace")
    archive.add_argument("--version-id", required=True)
    archive.add_argument("--status", choices=("rejected", "superseded"), required=True)
    archive.add_argument(
        "--file",
        action="append",
        default=[],
        help="Rejected drafts only; superseded uses the complete current record.",
    )
    archive.add_argument("--reason", required=True)
    archive.add_argument("--replacement", default="unknown")
    archive.add_argument("--conversation", required=True)
    archive.add_argument("--timestamp", required=True)
    add_apply_options(archive)

    validate = subparsers.add_parser("validate", help="Validate structure, records, and byte baselines.")
    validate.add_argument("workspace")
    return parser.parse_args(argv)


def execute(args: argparse.Namespace) -> dict[str, Any]:
    if args.command == "inventory":
        return inventory_report(args.workspace)
    if args.command == "validate":
        return validate_workspace(args.workspace)
    if args.command == "initialize":
        kwargs = {
            "timestamp": args.timestamp,
            "upstream_derived": args.upstream_derived,
        }
        if args.apply:
            return apply_initialize(args.workspace, **kwargs, plan_token=args.plan_token)
        return plan_with_token(plan_initialize(args.workspace, **kwargs))
    if args.command == "preserve":
        kwargs = {
            "source_raw": args.source,
            "original_relative_path": args.original_path,
            "source_class": args.source_class,
            "reliability": args.reliability,
            "received_at": args.received_at,
            "event_at": args.event_at,
            "timestamp": args.timestamp,
            "derivation_links": args.derived_from,
        }
        if args.apply:
            return apply_preserve(args.workspace, **kwargs, plan_token=args.plan_token)
        return plan_with_token(plan_preserve(args.workspace, **kwargs))
    if args.command == "conversation":
        kwargs = {
            "conversation_id": args.conversation_id,
            "timestamp": args.timestamp,
            "proposal": args.proposal,
            "user_correction": args.user_correction,
            "reason": args.reason,
            "final_decision": args.final_decision,
        }
        if args.apply:
            return apply_conversation(args.workspace, **kwargs, plan_token=args.plan_token)
        return plan_with_token(plan_conversation(args.workspace, **kwargs))
    if args.command == "artifact":
        kwargs = {
            "relative_path": args.path,
            "kind": args.kind,
            "timestamp": args.timestamp,
            "reliability": args.reliability,
            "derivation_links": args.derived_from,
        }
        if args.apply:
            return apply_artifact(args.workspace, **kwargs, plan_token=args.plan_token)
        return plan_with_token(plan_artifact(args.workspace, **kwargs))
    if args.command == "approve":
        kwargs = {
            "version_id": args.version_id,
            "files": args.file,
            "conversation_relative": args.conversation,
            "timestamp": args.timestamp,
        }
        if args.apply:
            return apply_approve(args.workspace, **kwargs, plan_token=args.plan_token)
        return plan_with_token(plan_approve(args.workspace, **kwargs))
    if args.command == "archive":
        kwargs = {
            "version_id": args.version_id,
            "status_value": args.status,
            "files": args.file,
            "reason": args.reason,
            "replacement": args.replacement,
            "conversation_relative": args.conversation,
            "timestamp": args.timestamp,
        }
        if args.apply:
            return apply_archive(args.workspace, **kwargs, plan_token=args.plan_token)
        return plan_with_token(plan_archive(args.workspace, **kwargs))
    raise AssertionError(f"Unhandled command: {args.command}")


def main(argv: list[str] | None = None) -> int:
    try:
        args = parse_args(argv)
        if getattr(args, "plan_token", None) and not getattr(args, "apply", False):
            raise WorkspaceError("unexpected_plan_token", "--plan-token is only valid with --apply.")
        emit(execute(args))
        return 0
    except WorkspaceError as exc:
        emit(exc.as_dict())
        return 2
    except (OSError, UnicodeError, json.JSONDecodeError) as exc:
        emit(
            WorkspaceError(
                "filesystem_or_record_error",
                f"Operation failed visibly without fallback: {exc}",
            ).as_dict()
        )
        return 2


if __name__ == "__main__":
    sys.exit(main())
