#!/usr/bin/env python3
"""Synthetic end-to-end tests for document workspace lifecycle safety."""

from __future__ import annotations

import hashlib
import json
import os
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


PACKAGE = Path(__file__).resolve().parents[1]
CLI = PACKAGE / "scripts" / "document_workspace.py"
TIME = "2030-01-02T03:04:05Z"
sys.path.insert(0, os.fspath(PACKAGE / "scripts"))
import workspace_core as CORE  # noqa: E402


def tree_snapshot(root: Path) -> dict[str, tuple[str, str | int]]:
    result: dict[str, tuple[str, str | int]] = {}
    if not root.exists():
        return result
    for path in sorted(root.rglob("*"), key=lambda item: item.as_posix()):
        relative = path.relative_to(root).as_posix()
        if path.is_symlink():
            result[relative] = ("link", os.readlink(path))
        elif path.is_dir():
            result[relative] = ("directory", 0)
        else:
            result[relative] = ("file", hashlib.sha256(path.read_bytes()).hexdigest())
    return result


@unittest.skipIf(os.name == "nt", "version 1 intentionally refuses apply on Windows")
class WorkspaceCLITest(unittest.TestCase):
    def setUp(self) -> None:
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        # Canonicalize the platform temp alias before selecting the exact root.
        self.base = Path(os.path.realpath(self.temporary.name))
        self.workspace = self.base / "workspace"
        self.workspace.mkdir()

    def run_cli(self, *arguments: str, expected: int = 0) -> dict[str, object]:
        completed = subprocess.run(
            [sys.executable, "-B", os.fspath(CLI), *map(str, arguments)],
            text=True,
            capture_output=True,
            check=False,
            env={**os.environ, "PYTHONDONTWRITEBYTECODE": "1"},
        )
        self.assertEqual(
            completed.returncode,
            expected,
            msg=f"stdout={completed.stdout}\nstderr={completed.stderr}",
        )
        self.assertEqual(completed.stderr, "")
        return json.loads(completed.stdout)

    def apply(self, *arguments: str) -> tuple[dict[str, object], dict[str, object]]:
        plan = self.run_cli(*arguments)
        self.assertIn("plan_token", plan)
        applied = self.run_cli(
            *arguments,
            "--apply",
            "--plan-token",
            str(plan["plan_token"]),
        )
        return plan, applied

    def initialize(self) -> None:
        plan, applied = self.apply("initialize", self.workspace, "--timestamp", TIME)
        self.assertEqual(plan["status"], "would_initialize")
        self.assertEqual(applied["status"], "initialized")

    def record_conversation(self, identifier: str = "01-review-decision") -> Path:
        _, applied = self.apply(
            "conversation",
            self.workspace,
            "--conversation-id",
            identifier,
            "--timestamp",
            "2030-01-02T04:00:00Z",
            "--proposal",
            "Prepared a first draft.",
            "--user-correction",
            "Requested a shorter structure.",
            "--reason",
            "The original structure duplicated material.",
            "--final-decision",
            "Use the revised concise structure.",
        )
        self.assertEqual(applied["status"], "recorded")
        return self.workspace / str(applied["conversation_record"])

    def register_draft(self, name: str = "deliverable-v001.docx") -> tuple[Path, dict[str, object]]:
        draft = self.workspace / "work" / "drafts" / name
        draft.parent.mkdir(parents=True, exist_ok=True)
        draft.write_bytes(b"synthetic draft bytes\x00\x01")
        _, applied = self.apply(
            "artifact",
            self.workspace,
            "--path",
            f"work/drafts/{name}",
            "--kind",
            "draft",
            "--timestamp",
            "2030-01-02T04:10:00Z",
            "--reliability",
            "user-confirmed",
        )
        self.assertEqual(applied["status"], "recorded")
        return draft, applied

    def approve_v001(self, draft_name: str = "deliverable-v001.docx") -> None:
        self.apply(
            "approve",
            self.workspace,
            "--version-id",
            "v001",
            "--file",
            f"work/drafts/{draft_name}",
            "--conversation",
            "conversation/01-review-decision.md",
            "--timestamp",
            "2030-01-02T04:20:00Z",
        )

    def test_empty_initialization_dry_run_apply_and_scaffolding(self) -> None:
        before = tree_snapshot(self.workspace)
        plan = self.run_cli("initialize", self.workspace, "--timestamp", TIME)
        self.assertEqual(plan["status"], "would_initialize")
        self.assertEqual(tree_snapshot(self.workspace), before)
        applied = self.run_cli(
            "initialize",
            self.workspace,
            "--timestamp",
            TIME,
            "--apply",
            "--plan-token",
            str(plan["plan_token"]),
        )
        self.assertEqual(applied["status"], "initialized")
        for relative in (
            "INDEX.md",
            "control/workspace.json",
            "raw/as-received",
            "work/derived",
            "work/drafts",
            "formal/current",
            "archive/versions",
            "conversation/00-workspace-decision.md",
            "memory/daily/2030-01-02.md",
            "memory/MEMORY.md",
        ):
            self.assertTrue((self.workspace / relative).exists(), relative)
        validation = self.run_cli("validate", self.workspace)
        self.assertEqual(validation["status"], "valid")
        self.assertFalse(validation["provider_calls"])

    def test_initialization_readback_is_idempotent(self) -> None:
        self.initialize()
        before = tree_snapshot(self.workspace)
        plan, applied = self.apply("initialize", self.workspace, "--timestamp", TIME)
        self.assertEqual(plan["status"], "already_initialized")
        self.assertEqual(applied["status"], "already_initialized")
        self.assertEqual(tree_snapshot(self.workspace), before)

    def test_populated_adoption_dry_run_preserves_bytes_and_upstream_class(self) -> None:
        source = self.workspace / "received" / "note.pdf"
        summary = self.workspace / "received" / "phone-summary.txt"
        source.parent.mkdir()
        source.write_bytes(b"synthetic-pdf-received-bytes")
        summary.write_bytes(b"synthetic upstream summary")
        before = tree_snapshot(self.workspace)
        arguments = (
            "initialize",
            self.workspace,
            "--timestamp",
            TIME,
            "--upstream-derived",
            "received/phone-summary.txt",
        )
        plan = self.run_cli(*arguments)
        self.assertEqual(plan["status"], "would_adopt")
        self.assertEqual(tree_snapshot(self.workspace), before)
        applied = self.run_cli(
            *arguments,
            "--apply",
            "--plan-token",
            str(plan["plan_token"]),
        )
        self.assertEqual(applied["status"], "adopted")
        self.assertEqual(source.read_bytes(), b"synthetic-pdf-received-bytes")
        self.assertEqual(
            (self.workspace / "raw/as-received/adopted/received/note.pdf").read_bytes(),
            source.read_bytes(),
        )
        records = [json.loads(path.read_text()) for path in (self.workspace / "control/sources").glob("*.json")]
        upstream = next(record for record in records if record["original_relative_path"].endswith("phone-summary.txt"))
        self.assertEqual(upstream["source_class"], "upstream-derived")
        self.assertEqual(upstream["reliability"], "unverified")
        self.assertEqual(upstream["received_at"], "unknown")
        self.run_cli("validate", self.workspace)

    def test_reserved_collision_refuses_without_clobber(self) -> None:
        collision = self.workspace / "INDEX.md"
        collision.write_text("existing navigation", encoding="utf-8")
        before = tree_snapshot(self.workspace)
        result = self.run_cli("initialize", self.workspace, "--timestamp", TIME, expected=2)
        self.assertEqual(result["error"], "reserved_path_collision")
        self.assertEqual(tree_snapshot(self.workspace), before)
        self.assertEqual(collision.read_text(encoding="utf-8"), "existing navigation")

    def test_stale_plan_refuses_after_inventory_change(self) -> None:
        plan = self.run_cli("initialize", self.workspace, "--timestamp", TIME)
        (self.workspace / "late.txt").write_text("appeared later", encoding="utf-8")
        result = self.run_cli(
            "initialize",
            self.workspace,
            "--timestamp",
            TIME,
            "--apply",
            "--plan-token",
            str(plan["plan_token"]),
            expected=2,
        )
        self.assertEqual(result["error"], "stale_or_mismatched_plan")
        self.assertFalse((self.workspace / "control").exists())

    def test_plan_tokens_bind_intervening_workspace_state_and_initialize_arguments(self) -> None:
        self.initialize()
        conversation = {
            "conversation_id": "01-first-decision",
            "timestamp": "2030-01-02T04:00:00Z",
            "proposal": "Prepared a synthetic proposal.",
            "user_correction": "Requested one synthetic correction.",
            "reason": "The first form was too long.",
            "final_decision": "Use the shorter synthetic form.",
        }
        old_plan = CORE.plan_with_token(CORE.plan_conversation(self.workspace, **conversation))
        self.record_conversation("02-intervening-decision")
        with self.assertRaises(CORE.WorkspaceError) as raised:
            CORE.apply_conversation(
                self.workspace,
                **conversation,
                plan_token=str(old_plan["plan_token"]),
            )
        self.assertEqual(raised.exception.code, "stale_or_mismatched_plan")

        init_plan = CORE.plan_with_token(
            CORE.plan_initialize(self.workspace, timestamp=TIME, upstream_derived=())
        )
        with self.assertRaises(CORE.WorkspaceError) as raised:
            CORE.apply_initialize(
                self.workspace,
                timestamp=TIME,
                upstream_derived=("invented-summary.txt",),
                plan_token=str(init_plan["plan_token"]),
            )
        self.assertEqual(raised.exception.code, "stale_or_mismatched_plan")

    def test_missing_attachment_is_not_preserved_and_has_no_dependency(self) -> None:
        self.initialize()
        before = tree_snapshot(self.workspace)
        result = self.run_cli(
            "preserve",
            self.workspace,
            "--source",
            self.base / "missing.pdf",
            "--original-path",
            "attachments/missing.pdf",
            "--source-class",
            "chat-attachment",
            "--reliability",
            "unknown",
            "--timestamp",
            TIME,
            expected=2,
        )
        self.assertEqual(result["status"], "not_preserved")
        self.assertEqual(result["error"], "missing_attachment")
        self.assertEqual(tree_snapshot(self.workspace), before)

    def test_unsupported_and_unreadable_attachments_are_not_preserved(self) -> None:
        self.initialize()
        unsupported = self.base / "synthetic.exe"
        unsupported.write_bytes(b"synthetic unsupported bytes")
        unreadable = self.base / "synthetic.txt"
        unreadable.write_text("synthetic unreadable bytes", encoding="utf-8")
        unreadable.chmod(0)
        try:
            for source in (unsupported, unreadable):
                with self.subTest(source=source.name):
                    result = self.run_cli(
                        "preserve",
                        self.workspace,
                        "--source",
                        source,
                        "--original-path",
                        f"attachments/{source.name}",
                        "--source-class",
                        "direct-receipt",
                        "--reliability",
                        "unknown",
                        "--timestamp",
                        TIME,
                        expected=2,
                    )
                    self.assertEqual(result["status"], "not_preserved")
        finally:
            unreadable.chmod(stat.S_IRUSR | stat.S_IWUSR)

    def test_explicit_attachment_copy_and_hash_are_preserved(self) -> None:
        self.initialize()
        attachment = self.base / "received-photo.png"
        attachment.write_bytes(b"synthetic image bytes\x00\xff")
        arguments = (
            "preserve",
            self.workspace,
            "--source",
            attachment,
            "--original-path",
            "attachments/received-photo.png",
            "--source-class",
            "photo-or-scan",
            "--reliability",
            "unknown",
            "--timestamp",
            TIME,
        )
        plan, applied = self.apply(*arguments)
        self.assertEqual(plan["status"], "would_preserve")
        self.assertEqual(applied["status"], "preserved")
        preserved = self.workspace / str(applied["current_relative_path"])
        self.assertEqual(preserved.read_bytes(), attachment.read_bytes())
        self.assertEqual(hashlib.sha256(preserved.read_bytes()).hexdigest(), applied["sha256"])
        second_plan, second_apply = self.apply(*arguments)
        self.assertEqual(second_plan["status"], "already_preserved")
        self.assertEqual(second_apply["status"], "already_preserved")

    def test_preserve_plan_token_binds_exact_external_source_path(self) -> None:
        self.initialize()
        first = self.base / "first" / "attachment.txt"
        second = self.base / "second" / "attachment.txt"
        first.parent.mkdir()
        second.parent.mkdir()
        first.write_bytes(b"same synthetic bytes")
        second.write_bytes(first.read_bytes())
        common = (
            "--original-path",
            "attachments/attachment.txt",
            "--source-class",
            "direct-receipt",
            "--reliability",
            "unknown",
            "--timestamp",
            TIME,
        )
        plan = self.run_cli("preserve", self.workspace, "--source", first, *common)
        result = self.run_cli(
            "preserve",
            self.workspace,
            "--source",
            second,
            *common,
            "--apply",
            "--plan-token",
            str(plan["plan_token"]),
            expected=2,
        )
        self.assertEqual(result["error"], "stale_or_mismatched_plan")
        self.assertEqual(list((self.workspace / "control/sources").glob("*.json")), [])

    def test_parent_link_swap_cannot_write_outside_workspace(self) -> None:
        self.initialize()
        attachment = self.base / "synthetic-attachment.txt"
        attachment.write_bytes(b"synthetic boundary bytes")
        arguments = {
            "source_raw": attachment,
            "original_relative_path": "attachments/synthetic-attachment.txt",
            "source_class": "direct-receipt",
            "reliability": "unknown",
            "received_at": "unknown",
            "event_at": "unknown",
            "timestamp": TIME,
            "derivation_links": (),
        }
        plan = CORE.plan_with_token(CORE.plan_preserve(self.workspace, **arguments))
        destination_relative = plan["source_record"]["current_relative_path"]
        destination_parent = self.workspace.joinpath(
            *Path(destination_relative).parent.parts
        )
        moved_parent = self.base / "moved-managed-parent"
        outside = self.base / "outside-target"
        outside.mkdir()
        original_open = CORE._guarded_open_beneath
        injected = False

        def inject_parent_link(root_descriptor: int, relative: str, flags: int, *, mode: int = 0o600) -> int:
            nonlocal injected
            if relative == destination_relative and flags & os.O_CREAT and not injected:
                injected = True
                destination_parent.rename(moved_parent)
                destination_parent.symlink_to(outside, target_is_directory=True)
            return original_open(root_descriptor, relative, flags, mode=mode)

        with mock.patch.object(CORE, "_guarded_open_beneath", inject_parent_link):
            with self.assertRaises(CORE.WorkspaceError) as raised:
                CORE.apply_preserve(
                    self.workspace,
                    **arguments,
                    plan_token=str(plan["plan_token"]),
                )
        self.assertEqual(raised.exception.code, "linked_path_refused")
        self.assertFalse((outside / attachment.name).exists())
        self.assertFalse((moved_parent / attachment.name).exists())
        self.assertEqual(list((self.workspace / "control/sources").glob("*.json")), [])

    def test_preserve_accepts_exact_single_unpreserved_in_workspace_arrival(self) -> None:
        self.initialize()
        arrival = self.workspace / "incoming.pdf"
        arrival.write_bytes(b"synthetic received PDF bytes")
        arguments = (
            "preserve",
            self.workspace,
            "--source",
            arrival,
            "--original-path",
            "incoming.pdf",
            "--source-class",
            "direct-receipt",
            "--reliability",
            "unknown",
            "--timestamp",
            TIME,
        )
        plan, applied = self.apply(*arguments)
        self.assertEqual(plan["status"], "would_preserve")
        self.assertEqual(applied["status"], "preserved")
        self.assertEqual(
            (self.workspace / str(applied["current_relative_path"])).read_bytes(),
            arrival.read_bytes(),
        )
        self.assertTrue(arrival.exists())
        self.run_cli("validate", self.workspace)

    def test_preserve_refuses_additional_unpreserved_in_workspace_collision(self) -> None:
        self.initialize()
        arrival = self.workspace / "incoming.pdf"
        collision = self.workspace / "other.txt"
        arrival.write_bytes(b"synthetic received PDF bytes")
        collision.write_text("other unpreserved file", encoding="utf-8")
        before = tree_snapshot(self.workspace)
        result = self.run_cli(
            "preserve",
            self.workspace,
            "--source",
            arrival,
            "--original-path",
            "incoming.pdf",
            "--source-class",
            "direct-receipt",
            "--reliability",
            "unknown",
            "--timestamp",
            TIME,
            expected=2,
        )
        self.assertEqual(result["error"], "unpreserved_workspace_file")
        self.assertEqual(tree_snapshot(self.workspace), before)

    def test_changed_in_workspace_received_original_is_detected(self) -> None:
        self.initialize()
        arrival = self.workspace / "incoming.pdf"
        arrival.write_bytes(b"first received bytes")
        self.apply(
            "preserve",
            self.workspace,
            "--source",
            arrival,
            "--original-path",
            "incoming.pdf",
            "--source-class",
            "direct-receipt",
            "--reliability",
            "unknown",
            "--timestamp",
            TIME,
        )
        arrival.write_bytes(b"changed received bytes")
        result = self.run_cli("validate", self.workspace, expected=2)
        self.assertEqual(result["error"], "received_original_changed")

    def test_raw_immutability_violation_is_detected(self) -> None:
        original = self.workspace / "source.txt"
        original.write_text("original received bytes", encoding="utf-8")
        self.apply("initialize", self.workspace, "--timestamp", TIME)
        raw = self.workspace / "raw/as-received/adopted/source.txt"
        raw.chmod(stat.S_IRUSR | stat.S_IWUSR)
        raw.write_text("tampered bytes", encoding="utf-8")
        result = self.run_cli("validate", self.workspace, expected=2)
        self.assertEqual(result["error"], "raw_immutability_violation")

    def test_raw_outside_as_received_is_refused(self) -> None:
        self.initialize()
        (self.workspace / "raw/agent-output.txt").write_text("synthetic agent output", encoding="utf-8")
        result = self.run_cli("validate", self.workspace, expected=2)
        self.assertEqual(result["error"], "raw_inventory_mismatch")

    def test_source_reclassification_and_duplicate_raw_binding_are_refused(self) -> None:
        upstream = self.workspace / "upstream-summary.txt"
        upstream.write_text("synthetic upstream summary", encoding="utf-8")
        self.apply(
            "initialize",
            self.workspace,
            "--timestamp",
            TIME,
            "--upstream-derived",
            "upstream-summary.txt",
        )
        record_path = next((self.workspace / "control/sources").glob("*.json"))
        original = json.loads(record_path.read_text(encoding="utf-8"))
        reclassified = dict(original)
        reclassified["source_class"] = "local-existing"
        reclassified["reliability"] = "verified"
        record_path.write_text(json.dumps(reclassified, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        result = self.run_cli("validate", self.workspace, expected=2)
        self.assertEqual(result["error"], "record_identity_mismatch")

        record_path.write_text(json.dumps(original, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        duplicate = dict(original)
        duplicate["original_relative_path"] = "fabricated/summary.txt"
        duplicate_id = CORE._source_identifier(CORE._source_record_identity(duplicate))
        duplicate["source_id"] = duplicate_id
        (self.workspace / f"control/sources/{duplicate_id}.json").write_text(
            json.dumps(duplicate, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        result = self.run_cli("validate", self.workspace, expected=2)
        self.assertEqual(result["error"], "record_identity_mismatch")

    def test_tampered_provenance_status_and_current_binding_are_refused(self) -> None:
        original = self.workspace / "upstream-summary.txt"
        original.write_text("synthetic upstream summary", encoding="utf-8")
        self.apply(
            "initialize",
            self.workspace,
            "--timestamp",
            TIME,
            "--upstream-derived",
            "upstream-summary.txt",
        )
        source_path = next((self.workspace / "control/sources").glob("*.json"))
        source = json.loads(source_path.read_text(encoding="utf-8"))
        source["schema_version"] = 999
        source_path.write_text(json.dumps(source, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        result = self.run_cli("validate", self.workspace, expected=2)
        self.assertEqual(result["error"], "record_schema_error")

        source["schema_version"] = 1
        source_path.write_text(json.dumps(source, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        draft, artifact_applied = self.register_draft()
        artifact_path = self.workspace / str(artifact_applied["record_path"])
        artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
        artifact["status"] = "approved"
        artifact_path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        result = self.run_cli("validate", self.workspace, expected=2)
        self.assertEqual(result["error"], "record_identity_mismatch")

        artifact["status"] = "draft"
        artifact_path.write_text(json.dumps(artifact, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        self.record_conversation()
        current_copy = self.workspace / "formal/current/v001/fabricated.docx"
        current_copy.parent.mkdir(parents=True, exist_ok=True)
        current_copy.write_bytes(draft.read_bytes())
        conversation = self.workspace / "conversation/01-review-decision.md"
        fabricated = {
            "schema_version": 1,
            "status": "approved",
            "version_id": "v001",
            "decided_at": "2030-01-02T04:20:00Z",
            "conversation_record": "conversation/01-review-decision.md",
            "conversation_sha256": hashlib.sha256(conversation.read_bytes()).hexdigest(),
            "outputs": [
                {
                    "artifact_id": "art-00000000000000000000",
                    "draft_relative_path": "raw/as-received/fabricated.docx",
                    "current_relative_path": "formal/current/v001/fabricated.docx",
                    "type_class": "document",
                    "byte_size": len(draft.read_bytes()),
                    "sha256": hashlib.sha256(draft.read_bytes()).hexdigest(),
                }
            ],
        }
        (self.workspace / "control/current.json").write_text(
            json.dumps(fabricated, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        result = self.run_cli("validate", self.workspace, expected=2)
        self.assertEqual(result["error"], "current_record_invalid")

    def test_source_metadata_tampering_and_artifact_self_cycle_are_refused(self) -> None:
        source = self.workspace / "received.txt"
        source.write_text("synthetic received material", encoding="utf-8")
        self.apply("initialize", self.workspace, "--timestamp", TIME)
        source_path = next((self.workspace / "control/sources").glob("*.json"))
        original = json.loads(source_path.read_text(encoding="utf-8"))
        for field, value in (
            ("reliability", "verified"),
            ("received_at", "2030-01-01T00:00:00Z"),
            ("event_at", "2030-01-01T01:00:00Z"),
            ("source_mode", "explicit-in-workspace"),
        ):
            with self.subTest(field=field):
                changed = dict(original)
                changed[field] = value
                source_path.write_text(
                    json.dumps(changed, indent=2, sort_keys=True) + "\n",
                    encoding="utf-8",
                )
                result = self.run_cli("validate", self.workspace, expected=2)
                self.assertEqual(result["error"], "record_identity_mismatch")
        source_path.write_text(
            json.dumps(original, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )

        _, artifact_result = self.register_draft("cycle-draft.txt")
        artifact_path = self.workspace / str(artifact_result["record_path"])
        artifact = json.loads(artifact_path.read_text(encoding="utf-8"))
        artifact["derivation_links"] = [artifact["artifact_id"]]
        artifact["artifact_id"] = CORE._artifact_identifier(
            CORE._artifact_record_identity(artifact)
        )
        artifact["derivation_links"] = [artifact["artifact_id"]]
        artifact["artifact_id"] = CORE._artifact_identifier(
            CORE._artifact_record_identity(artifact)
        )
        cycled_path = artifact_path.with_name(f"{artifact['artifact_id']}.json")
        artifact_path.unlink()
        cycled_path.write_text(
            json.dumps(artifact, indent=2, sort_keys=True) + "\n",
            encoding="utf-8",
        )
        result = self.run_cli("validate", self.workspace, expected=2)
        self.assertIn(
            result["error"],
            {"derivation_cycle", "record_identity_mismatch", "missing_derivation"},
        )

    def test_links_path_escape_unsupported_and_unreadable_are_refused(self) -> None:
        outside = self.base / "outside.txt"
        outside.write_text("outside", encoding="utf-8")
        (self.workspace / "linked.txt").symlink_to(outside)
        before = tree_snapshot(self.workspace)
        linked = self.run_cli("inventory", self.workspace, expected=2)
        self.assertEqual(linked["error"], "linked_path_refused")
        self.assertEqual(tree_snapshot(self.workspace), before)

        (self.workspace / "linked.txt").unlink()
        unsupported = self.workspace / "program.exe"
        unsupported.write_bytes(b"synthetic executable bytes")
        result = self.run_cli("initialize", self.workspace, "--timestamp", TIME, expected=2)
        self.assertEqual(result["error"], "unsupported_file_type")
        unsupported.unlink()

        unreadable = self.workspace / "unreadable.txt"
        unreadable.write_text("synthetic", encoding="utf-8")
        unreadable.chmod(0)
        try:
            result = self.run_cli("initialize", self.workspace, "--timestamp", TIME, expected=2)
            self.assertEqual(result["error"], "unreadable_file")
        finally:
            unreadable.chmod(stat.S_IRUSR | stat.S_IWUSR)

        unreadable.unlink()
        self.initialize()
        result = self.run_cli(
            "preserve",
            self.workspace,
            "--source",
            outside,
            "--original-path",
            "../escape.txt",
            "--source-class",
            "direct-receipt",
            "--reliability",
            "unknown",
            "--timestamp",
            TIME,
            expected=2,
        )
        self.assertEqual(result["error"], "path_escape")

    def test_unregistered_draft_is_not_current_then_explicit_approval(self) -> None:
        self.initialize()
        draft = self.workspace / "work/drafts/deliverable-v001.docx"
        draft.parent.mkdir(parents=True, exist_ok=True)
        draft.write_bytes(b"synthetic draft")
        invalid = self.run_cli("validate", self.workspace, expected=2)
        self.assertEqual(invalid["error"], "work_inventory_mismatch")
        self.apply(
            "artifact",
            self.workspace,
            "--path",
            "work/drafts/deliverable-v001.docx",
            "--kind",
            "draft",
            "--timestamp",
            "2030-01-02T04:10:00Z",
            "--reliability",
            "user-confirmed",
        )
        self.record_conversation()
        before_plan = tree_snapshot(self.workspace / "formal/current")
        arguments = (
            "approve",
            self.workspace,
            "--version-id",
            "v001",
            "--file",
            "work/drafts/deliverable-v001.docx",
            "--conversation",
            "conversation/01-review-decision.md",
            "--timestamp",
            "2030-01-02T04:20:00Z",
        )
        plan = self.run_cli(*arguments)
        self.assertEqual(plan["status"], "would_approve")
        self.assertEqual(tree_snapshot(self.workspace / "formal/current"), before_plan)
        applied = self.run_cli(*arguments, "--apply", "--plan-token", str(plan["plan_token"]))
        self.assertEqual(applied["status"], "approved")
        current = json.loads((self.workspace / "control/current.json").read_text())
        self.assertEqual(current["status"], "approved")
        self.assertEqual(current["version_id"], "v001")
        self.assertEqual(
            (self.workspace / "formal/current/v001/deliverable-v001.docx").read_bytes(),
            draft.read_bytes(),
        )

    def test_current_change_between_compare_and_exchange_is_not_lost(self) -> None:
        self.initialize()
        self.register_draft()
        self.record_conversation()
        arguments = {
            "version_id": "v001",
            "files": ("work/drafts/deliverable-v001.docx",),
            "conversation_relative": "conversation/01-review-decision.md",
            "timestamp": "2030-01-02T04:20:00Z",
        }
        plan = CORE.plan_with_token(CORE.plan_approve(self.workspace, **arguments))
        external_bytes = b'{"external_change":"before-exchange"}\n'
        original_exchange = CORE._secure_exchange_names
        injected = False

        def inject_before_exchange(root: Path, left: str, right: str) -> None:
            nonlocal injected
            if not injected:
                injected = True
                (self.workspace / "control/current.json").write_bytes(external_bytes)
            original_exchange(root, left, right)

        with mock.patch.object(CORE, "_secure_exchange_names", inject_before_exchange):
            with self.assertRaises(CORE.WorkspaceError) as raised:
                CORE.apply_approve(
                    self.workspace,
                    **arguments,
                    plan_token=str(plan["plan_token"]),
                )
        self.assertEqual(raised.exception.code, "control_changed")
        self.assertEqual((self.workspace / "control/current.json").read_bytes(), external_bytes)
        evidence = self.workspace / "control/.current.json.document-workspace.displaced"
        self.assertEqual(evidence.read_bytes(), CORE.canonical_json_bytes(plan["current_record"]))

    def test_current_change_after_exchange_is_not_clobbered(self) -> None:
        self.initialize()
        self.register_draft()
        self.record_conversation()
        arguments = {
            "version_id": "v001",
            "files": ("work/drafts/deliverable-v001.docx",),
            "conversation_relative": "conversation/01-review-decision.md",
            "timestamp": "2030-01-02T04:20:00Z",
        }
        plan = CORE.plan_with_token(CORE.plan_approve(self.workspace, **arguments))
        expected_empty = CORE.canonical_json_bytes(CORE.empty_current_record())
        external_bytes = b'{"external_change":"after-exchange"}\n'
        original_exchange = CORE._secure_exchange_names
        injected = False

        def inject_after_exchange(root: Path, left: str, right: str) -> None:
            nonlocal injected
            original_exchange(root, left, right)
            if not injected:
                injected = True
                external = self.workspace / "control/.external-current.json"
                external.write_bytes(external_bytes)
                os.replace(external, self.workspace / "control/current.json")

        with mock.patch.object(CORE, "_secure_exchange_names", inject_after_exchange):
            with self.assertRaises(CORE.WorkspaceError) as raised:
                CORE.apply_approve(
                    self.workspace,
                    **arguments,
                    plan_token=str(plan["plan_token"]),
                )
        self.assertEqual(raised.exception.code, "control_transition_collision")
        self.assertEqual((self.workspace / "control/current.json").read_bytes(), external_bytes)
        evidence = self.workspace / "control/.current.json.document-workspace.displaced"
        self.assertEqual(evidence.read_bytes(), expected_empty)

    def test_artifact_apply_refuses_other_unregistered_work_collision(self) -> None:
        self.initialize()
        first = self.workspace / "work/drafts/first.txt"
        second = self.workspace / "work/drafts/second.txt"
        first.parent.mkdir(parents=True, exist_ok=True)
        first.write_text("first synthetic draft", encoding="utf-8")
        second.write_text("second synthetic draft", encoding="utf-8")
        before = tree_snapshot(self.workspace / "control/artifacts")
        result = self.run_cli(
            "artifact",
            self.workspace,
            "--path",
            "work/drafts/first.txt",
            "--kind",
            "draft",
            "--timestamp",
            "2030-01-02T04:10:00Z",
            "--reliability",
            "unverified",
            expected=2,
        )
        self.assertEqual(result["error"], "unregistered_work_collision")
        self.assertEqual(tree_snapshot(self.workspace / "control/artifacts"), before)

    def test_blank_complete_conversation_cannot_authorize_approval(self) -> None:
        self.initialize()
        self.register_draft()
        blank = self.workspace / "conversation/01-blank-decision.md"
        blank.write_text(
            """# Blank decision

> Status: complete

## Agent original proposal

## User corrections

## Rejection or modification reasons

## Final decision
""",
            encoding="utf-8",
        )
        result = self.run_cli(
            "approve",
            self.workspace,
            "--version-id",
            "v001",
            "--file",
            "work/drafts/deliverable-v001.docx",
            "--conversation",
            "conversation/01-blank-decision.md",
            "--timestamp",
            "2030-01-02T04:20:00Z",
            expected=2,
        )
        self.assertEqual(result["error"], "incomplete_conversation")

    def test_rejected_archive_records_reason_replacement_hash_and_conversation(self) -> None:
        self.initialize()
        draft, _ = self.register_draft()
        self.record_conversation()
        _, applied = self.apply(
            "archive",
            self.workspace,
            "--version-id",
            "v001",
            "--status",
            "rejected",
            "--file",
            "work/drafts/deliverable-v001.docx",
            "--reason",
            "User rejected the structure.",
            "--replacement",
            "v002",
            "--conversation",
            "conversation/01-review-decision.md",
            "--timestamp",
            "2030-01-02T04:30:00Z",
        )
        self.assertEqual(applied["status"], "archived")
        archived = self.workspace / "archive/versions/v001/files/deliverable-v001.docx"
        self.assertEqual(archived.read_bytes(), draft.read_bytes())
        self.assertTrue(draft.exists())
        record = json.loads((self.workspace / "archive/versions/v001/record.json").read_text())
        self.assertEqual(record["status"], "rejected")
        self.assertEqual(record["reason"], "User rejected the structure.")
        self.assertEqual(record["replacement"], "v002")
        self.assertEqual(record["conversation_record"], "conversation/01-review-decision.md")
        self.assertEqual(record["files"][0]["sha256"], hashlib.sha256(draft.read_bytes()).hexdigest())

        approve = self.run_cli(
            "approve",
            self.workspace,
            "--version-id",
            "v001",
            "--file",
            "work/drafts/deliverable-v001.docx",
            "--conversation",
            "conversation/01-review-decision.md",
            "--timestamp",
            "2030-01-02T05:00:00Z",
            expected=2,
        )
        self.assertEqual(approve["error"], "archived_version_exists")

        record_path = self.workspace / "archive/versions/v001/record.json"
        tampered = json.loads(record_path.read_text(encoding="utf-8"))
        tampered["status"] = "superseded"
        tampered["files"][0]["source_relative_path"] = "formal/current/v999/fake.docx"
        tampered["files"][0]["artifact_id"] = "art-00000000000000000000"
        tampered["files"][0]["archive_method"] = "anything"
        record_path.write_text(json.dumps(tampered, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        validation = self.run_cli("validate", self.workspace, expected=2)
        self.assertEqual(validation["error"], "missing_record")

    def test_superseded_current_moves_to_archive_and_clears_current(self) -> None:
        self.initialize()
        draft, _ = self.register_draft()
        self.record_conversation()
        self.approve_v001()
        _, applied = self.apply(
            "archive",
            self.workspace,
            "--version-id",
            "v001",
            "--status",
            "superseded",
            "--reason",
            "A later approved version replaces it.",
            "--replacement",
            "v002",
            "--conversation",
            "conversation/01-review-decision.md",
            "--timestamp",
            "2030-01-03T02:00:00Z",
        )
        self.assertEqual(applied["status"], "archived")
        self.assertEqual(
            (self.workspace / "archive/versions/v001/files/deliverable-v001.docx").read_bytes(),
            draft.read_bytes(),
        )
        self.assertFalse((self.workspace / "formal/current/v001").exists())
        current = json.loads((self.workspace / "control/current.json").read_text())
        self.assertEqual(current["status"], "none")
        self.run_cli("validate", self.workspace)

    def test_supersede_refuses_lost_update_to_current_record(self) -> None:
        self.initialize()
        self.register_draft()
        self.record_conversation()
        self.approve_v001()
        archive_kwargs = {
            "version_id": "v001",
            "status_value": "superseded",
            "files": [],
            "reason": "A later reviewed version replaces it.",
            "replacement": "v002",
            "conversation_relative": "conversation/01-review-decision.md",
            "timestamp": "2030-01-03T02:00:00Z",
        }
        plan = CORE.plan_with_token(CORE.plan_archive(self.workspace, **archive_kwargs))
        original_claim = CORE._secure_exchange_claim

        external = CORE.canonical_json_bytes(CORE.empty_current_record())

        def inject_current_change(root: Path, relative: str, expected: bytes, replacement: bytes) -> str:
            (self.workspace / "control/current.json").write_bytes(external)
            return original_claim(root, relative, expected, replacement)

        with mock.patch.object(CORE, "_secure_exchange_claim", inject_current_change):
            with self.assertRaises(CORE.WorkspaceError) as raised:
                CORE.apply_archive(
                    self.workspace,
                    **archive_kwargs,
                    plan_token=str(plan["plan_token"]),
                )
        self.assertEqual(raised.exception.code, "control_changed")
        self.assertTrue(
            (self.workspace / "formal/current/v001/deliverable-v001.docx").exists()
        )
        self.assertFalse((self.workspace / "archive/versions/v001").exists())
        self.assertEqual((self.workspace / "control/current.json").read_bytes(), external)


@unittest.skipUnless(
    os.name == "nt" and hasattr(Path, "is_junction"),
    "requires Windows Python 3.12 or newer",
)
class WindowsReadOnlyRuntimeTest(unittest.TestCase):
    def test_initialize_plans_but_apply_is_refused(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            workspace = Path(temporary) / "workspace"
            workspace.mkdir()
            command = [
                sys.executable,
                "-B",
                os.fspath(CLI),
                "initialize",
                os.fspath(workspace),
                "--timestamp",
                TIME,
            ]
            planned = subprocess.run(command, text=True, capture_output=True, check=False)
            self.assertEqual(planned.returncode, 0, planned.stdout + planned.stderr)
            plan = json.loads(planned.stdout)
            self.assertEqual(plan["status"], "would_initialize")

            applied = subprocess.run(
                [*command, "--apply", "--plan-token", str(plan["plan_token"])],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(applied.returncode, 2, applied.stdout + applied.stderr)
            refusal = json.loads(applied.stdout)
            self.assertEqual(refusal["error"], "unsupported_mutation_runtime")
            self.assertEqual(list(workspace.iterdir()), [])


if __name__ == "__main__":
    unittest.main()
