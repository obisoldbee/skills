#!/usr/bin/env python3
"""Behavioral tests for ordinary Project Root initialization and access claims."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
INITIALIZER = PACKAGE_ROOT / "scripts" / "initialize_project_root.py"
VALIDATOR = PACKAGE_ROOT / "scripts" / "validate_project_root.py"


class ProjectRootWorkflowTests(unittest.TestCase):
    def run_command(self, arguments: list[str], cwd: Path | None = None) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            arguments,
            cwd=cwd,
            capture_output=True,
            text=True,
            check=False,
        )

    def initialize(
        self,
        target: Path,
        project_type: str = "code",
        mode: str = "fresh-empty",
        extra: list[str] | None = None,
    ) -> dict[str, object]:
        command = [
            sys.executable,
            "-B",
            str(INITIALIZER),
            str(target),
            "--type",
            project_type,
            "--mode",
            mode,
            "--apply",
        ]
        if extra:
            command.extend(extra)
        result = self.run_command(command)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def access(self, root: Path) -> Path:
        return root / ".project-conventions" / "project_access.py"

    def finish_claim(self, root: Path, receipt: dict[str, object]) -> None:
        result = self.run_command(
            [
                sys.executable,
                "-B",
                str(self.access(root)),
                "finish",
                "--session",
                str(receipt["session_id"]),
                "--token",
                str(receipt["token"]),
                "--outcome",
                "success",
            ]
        )
        self.assertEqual(result.returncode, 0, result.stderr)

    def test_code_document_and_hybrid_are_dry_run_apply_validate_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            for project_type in ("code", "document", "hybrid"):
                root = base / project_type
                dry = self.run_command(
                    [
                        sys.executable,
                        "-B",
                        str(INITIALIZER),
                        str(root),
                        "--type",
                        project_type,
                        "--mode",
                        "fresh-empty",
                    ]
                )
                self.assertEqual(dry.returncode, 0, dry.stderr)
                self.assertEqual(json.loads(dry.stdout)["status"], "would_initialize")
                self.assertFalse(root.exists())
                first = self.initialize(root, project_type)
                self.assertEqual(first["status"], "initialized")
                second = self.initialize(root, project_type)
                self.assertEqual(second["status"], "already_initialized")
                validated = self.run_command(
                    [sys.executable, "-B", str(VALIDATOR), str(root)]
                )
                self.assertEqual(validated.returncode, 0, validated.stderr)
                self.assertEqual(json.loads(validated.stdout)["status"], "valid")
                self.assertFalse((root / ".git").exists())

    def test_nested_records_directory_is_created_and_validated(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "nested-records"
            result = self.initialize(
                root,
                project_type="hybrid",
                extra=["--records-dir", "submissions/records"],
            )
            self.assertEqual(result["status"], "initialized")
            self.assertTrue((root / "submissions" / "records" / "INDEX.md").is_file())
            validated = self.run_command(
                [sys.executable, "-B", str(VALIDATOR), str(root)]
            )
            self.assertEqual(validated.returncode, 0, validated.stderr)
            self.assertEqual(json.loads(validated.stdout)["records_dir"], "submissions/records")

    def test_agent_skill_profile_uses_named_src_package_and_preserves_real_skill(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "buddy-travelling-win"
            extra = ["--profile", "agent-skill", "--skill-name", "buddy-travelling"]
            first = self.initialize(root, extra=extra)
            self.assertEqual(first["project_profile"], "agent-skill")
            entry = root / "src" / "buddy-travelling" / "SKILL.md"
            self.assertTrue(entry.is_file())
            self.assertFalse((root / "src" / "SKILL.md").exists())
            self.assertFalse((root / "docs" / "buddy-travelling" / "SKILL.md").exists())
            real_skill = """---
name: buddy-travelling
description: Real user-authored Skill behavior.
---

# Buddy Travelling

Real workflow.
"""
            entry.write_text(real_skill, encoding="utf-8")
            second = self.initialize(root, extra=extra)
            self.assertEqual(second["status"], "already_initialized")
            self.assertEqual(entry.read_text(encoding="utf-8"), real_skill)
            validated = self.run_command(
                [sys.executable, "-B", str(VALIDATOR), str(root)]
            )
            self.assertEqual(validated.returncode, 0, validated.stderr)
            receipt = json.loads(validated.stdout)
            self.assertEqual(receipt["skill_package"], "buddy-travelling")

    def test_agent_skill_profile_rejects_misplaced_or_wrong_named_entry_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            misplaced_root = base / "misplaced"
            misplaced = misplaced_root / "docs" / "archive" / "buddy" / "SKILL.md"
            misplaced.parent.mkdir(parents=True)
            misplaced.write_text("---\nname: buddy-travelling\n---\n", encoding="utf-8")
            command = [
                sys.executable,
                "-B",
                str(INITIALIZER),
                str(misplaced_root),
                "--type",
                "code",
                "--profile",
                "agent-skill",
                "--skill-name",
                "buddy-travelling",
                "--mode",
                "adopt-existing",
                "--apply",
            ]
            rejected = self.run_command(command)
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("Agent Skill entry must be", rejected.stderr)
            self.assertFalse((misplaced_root / "AGENTS.md").exists())
            self.assertTrue(misplaced.is_file())

            wrong_root = base / "wrong-name"
            wrong_entry = wrong_root / "src" / "buddy-travelling" / "SKILL.md"
            wrong_entry.parent.mkdir(parents=True)
            wrong_entry.write_text("---\nname: another-skill\n---\n", encoding="utf-8")
            wrong = self.run_command(command[:3] + [str(wrong_root)] + command[4:])
            self.assertNotEqual(wrong.returncode, 0)
            self.assertIn("frontmatter name differs", wrong.stderr)
            self.assertFalse((wrong_root / "AGENTS.md").exists())

    @unittest.skipIf(os.name == "nt", "portable directory-link fixture is Unix-only")
    def test_agent_skill_profile_rejects_linked_skill_alias_but_preserves_plain_links(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            root = base / "skill-project"
            extra = ["--profile", "agent-skill", "--skill-name", "demo-skill"]
            self.initialize(root, extra=extra)

            external_skill = base / "external-skill"
            external_skill.mkdir()
            (external_skill / "SKILL.md").write_text(
                "---\nname: demo-skill\n---\n", encoding="utf-8"
            )
            linked_skill = root / "docs" / "linked-skill"
            linked_skill.symlink_to(external_skill, target_is_directory=True)
            rejected = self.run_command(
                [sys.executable, "-B", str(VALIDATOR), str(root)]
            )
            self.assertNotEqual(rejected.returncode, 0)
            self.assertIn("linked-skill/SKILL.md", rejected.stderr)
            linked_skill.unlink()

            external_assets = base / "external-assets"
            external_assets.mkdir()
            (external_assets / "reference.txt").write_text("keep\n", encoding="utf-8")
            plain_link = root / "docs" / "reference-link"
            plain_link.symlink_to(external_assets, target_is_directory=True)
            repeated = self.initialize(root, extra=extra)
            self.assertEqual(repeated["status"], "already_initialized")
            validated = self.run_command(
                [sys.executable, "-B", str(VALIDATOR), str(root)]
            )
            self.assertEqual(validated.returncode, 0, validated.stderr)

    def test_agent_skill_adoption_rejects_conflicting_agents_routes_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "legacy-routing"
            root.mkdir()
            agents = root / "AGENTS.md"
            agents.write_text(
                "# Existing Rules\n\nSkill source: `src/SKILL.md`.\n", encoding="utf-8"
            )
            result = self.run_command(
                [
                    sys.executable,
                    "-B",
                    str(INITIALIZER),
                    str(root),
                    "--type",
                    "code",
                    "--profile",
                    "agent-skill",
                    "--skill-name",
                    "demo-skill",
                    "--mode",
                    "adopt-existing",
                    "--apply",
                ]
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertIn("conflicting Agent Skill source routes", result.stderr)
            self.assertFalse((root / ".project-conventions").exists())
            self.assertEqual(
                agents.read_text(encoding="utf-8"),
                "# Existing Rules\n\nSkill source: `src/SKILL.md`.\n",
            )

            clean = Path(raw) / "tampered-routing"
            extra = ["--profile", "agent-skill", "--skill-name", "demo-skill"]
            self.initialize(clean, extra=extra)
            clean_agents = clean / "AGENTS.md"
            clean_agents.write_text(
                clean_agents.read_text(encoding="utf-8")
                + "\nLegacy package source: `docs/demo-skill/SKILL.md`.\n",
                encoding="utf-8",
            )
            validated = self.run_command(
                [sys.executable, "-B", str(VALIDATOR), str(clean)]
            )
            self.assertNotEqual(validated.returncode, 0)
            self.assertIn("conflicting Agent Skill source routes", validated.stderr)

    def test_adoption_preserves_material_harness_and_existing_human_files(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "adopt"
            material = root / "material"
            harness = root / ".workbuddy" / "memory"
            minimax = root / ".minimax" / "agents" / "mavis"
            material.mkdir(parents=True)
            harness.mkdir(parents=True)
            minimax.mkdir(parents=True)
            source = material / "input.bin"
            source.write_bytes(bytes(range(256)))
            harness_file = harness / "private.md"
            harness_file.write_text("opaque\n", encoding="utf-8")
            minimax_file = minimax / "state.json"
            minimax_file.write_text("{}\n", encoding="utf-8")
            (root / "README.md").write_text("# User README\n", encoding="utf-8")
            (root / "AGENTS.md").write_text("# Existing Rules\n\n- Preserve me.\n", encoding="utf-8")
            before = {
                "source": hashlib.sha256(source.read_bytes()).hexdigest(),
                "harness": hashlib.sha256(harness_file.read_bytes()).hexdigest(),
                "minimax": hashlib.sha256(minimax_file.read_bytes()).hexdigest(),
                "readme": (root / "README.md").read_bytes(),
            }
            result = self.initialize(root, mode="adopt-existing")
            self.assertEqual(result["moved"], [])
            self.assertEqual(before["source"], hashlib.sha256(source.read_bytes()).hexdigest())
            self.assertEqual(before["harness"], hashlib.sha256(harness_file.read_bytes()).hexdigest())
            self.assertEqual(before["minimax"], hashlib.sha256(minimax_file.read_bytes()).hexdigest())
            self.assertEqual(before["readme"], (root / "README.md").read_bytes())
            agents = (root / "AGENTS.md").read_text(encoding="utf-8")
            self.assertIn("# Existing Rules", agents)
            self.assertEqual(agents.count("project-conventions:access:start"), 1)

    def test_fresh_mode_rejects_user_content_without_writing(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "not-empty"
            root.mkdir()
            user_file = root / "notes.txt"
            user_file.write_text("keep\n", encoding="utf-8")
            result = self.run_command(
                [
                    sys.executable,
                    "-B",
                    str(INITIALIZER),
                    str(root),
                    "--type",
                    "code",
                    "--mode",
                    "fresh-empty",
                    "--apply",
                ]
            )
            self.assertNotEqual(result.returncode, 0)
            self.assertEqual(user_file.read_text(encoding="utf-8"), "keep\n")
            self.assertEqual(sorted(path.name for path in root.iterdir()), ["notes.txt"])

    def test_concurrent_writers_are_atomic_and_token_protected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "project"
            self.initialize(root)
            processes = [
                subprocess.Popen(
                    [
                        sys.executable,
                        "-B",
                        str(self.access(root)),
                        "enter",
                        "--mode",
                        "writer",
                        "--session",
                        f"writer-{index}",
                        "--actor",
                        f"harness-{index}",
                    ],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                )
                for index in range(16)
            ]
            results = []
            for process in processes:
                stdout, stderr = process.communicate(timeout=15)
                results.append((process.returncode, stdout, stderr))
            winners = [json.loads(stdout) for code, stdout, _ in results if code == 0]
            self.assertEqual(len(winners), 1, results)
            self.assertEqual(sum(code == 2 for code, _, _ in results), 15)
            winner = winners[0]

            blocked_reader = self.run_command(
                [
                    sys.executable,
                    "-B",
                    str(self.access(root)),
                    "enter",
                    "--mode",
                    "read-only",
                    "--actor",
                    "reviewer",
                ]
            )
            self.assertEqual(blocked_reader.returncode, 2, blocked_reader.stderr)
            wrong_token = self.run_command(
                [
                    sys.executable,
                    "-B",
                    str(self.access(root)),
                    "finish",
                    "--session",
                    str(winner["session_id"]),
                    "--token",
                    "wrong-token",
                    "--outcome",
                    "success",
                ]
            )
            self.assertEqual(wrong_token.returncode, 3)
            self.finish_claim(root, winner)

    def test_virgin_runtime_allows_concurrent_readers_without_schema_race(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            for attempt in range(3):
                root = base / f"project-{attempt}"
                self.initialize(root)
                processes = [
                    subprocess.Popen(
                        [
                            sys.executable,
                            "-B",
                            str(self.access(root)),
                            "enter",
                            "--mode",
                            "read-only",
                            "--session",
                            f"reader-{index}",
                            "--actor",
                            f"reviewer-{index}",
                        ],
                        stdout=subprocess.PIPE,
                        stderr=subprocess.PIPE,
                        text=True,
                    )
                    for index in range(24)
                ]
                receipts: list[dict[str, object]] = []
                results: list[tuple[int, str, str]] = []
                for process in processes:
                    stdout, stderr = process.communicate(timeout=20)
                    results.append((process.returncode, stdout, stderr))
                    if process.returncode == 0:
                        receipts.append(json.loads(stdout))
                self.assertEqual(len(receipts), 24, results)
                for receipt in receipts:
                    self.finish_claim(root, receipt)

    def test_portable_paths_reject_windows_invalid_characters(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            cases = (
                ("--records-dir", "records/a<b"),
                ("--repository-root", "src/a|b"),
                ("--records-dir", "records/a\"b"),
            )
            for index, (flag, value) in enumerate(cases):
                root = base / f"invalid-{index}"
                result = self.run_command(
                    [
                        sys.executable,
                        "-B",
                        str(INITIALIZER),
                        str(root),
                        "--type",
                        "code",
                        "--mode",
                        "fresh-empty",
                        flag,
                        value,
                    ]
                )
                self.assertNotEqual(result.returncode, 0)
                self.assertIn("not portable", result.stderr)
                self.assertFalse(root.exists())

            root = base / "access"
            self.initialize(root)
            invalid_write = self.run_command(
                [
                    sys.executable,
                    "-B",
                    str(self.access(root)),
                    "enter",
                    "--mode",
                    "isolated-writer",
                    "--actor",
                    "invalid-path",
                    "--write-path",
                    "src/a\x01b",
                ]
            )
            self.assertEqual(invalid_write.returncode, 3)
            self.assertIn("portable", invalid_write.stderr)

    def test_readers_share_and_block_writer_until_all_finish(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "project"
            self.initialize(root)
            readers: list[dict[str, object]] = []
            for index in range(8):
                result = self.run_command(
                    [
                        sys.executable,
                        "-B",
                        str(self.access(root)),
                        "enter",
                        "--mode",
                        "read-only",
                        "--session",
                        f"reader-{index}",
                        "--actor",
                        f"review-{index}",
                    ]
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                readers.append(json.loads(result.stdout))
            writer = self.run_command(
                [
                    sys.executable,
                    "-B",
                    str(self.access(root)),
                    "enter",
                    "--mode",
                    "writer",
                    "--actor",
                    "editor",
                ]
            )
            self.assertEqual(writer.returncode, 2)
            for reader in readers:
                self.finish_claim(root, reader)
            writer = self.run_command(
                [
                    sys.executable,
                    "-B",
                    str(self.access(root)),
                    "enter",
                    "--mode",
                    "writer",
                    "--actor",
                    "editor",
                ]
            )
            self.assertEqual(writer.returncode, 0, writer.stderr)
            self.finish_claim(root, json.loads(writer.stdout))

    def test_abandoned_claim_requires_explicit_dry_run_then_recovery(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "project"
            self.initialize(root)
            entered = self.run_command(
                [
                    sys.executable,
                    "-B",
                    str(self.access(root)),
                    "enter",
                    "--mode",
                    "writer",
                    "--session",
                    "abandoned",
                    "--actor",
                    "crashed-harness",
                ]
            )
            self.assertEqual(entered.returncode, 0, entered.stderr)
            dry = self.run_command(
                [
                    sys.executable,
                    "-B",
                    str(self.access(root)),
                    "recover",
                    "--session",
                    "abandoned",
                    "--reason",
                    "user confirmed the old task was closed",
                ]
            )
            dry_receipt = json.loads(dry.stdout)
            self.assertEqual(dry_receipt["status"], "would_recover")
            still_blocked = self.run_command(
                [
                    sys.executable,
                    "-B",
                    str(self.access(root)),
                    "enter",
                    "--mode",
                    "writer",
                    "--actor",
                    "replacement",
                ]
            )
            self.assertEqual(still_blocked.returncode, 2)
            direct_apply = self.run_command(
                [
                    sys.executable,
                    "-B",
                    str(self.access(root)),
                    "recover",
                    "--session",
                    "abandoned",
                    "--reason",
                    "user confirmed the old task was closed",
                    "--apply",
                ]
            )
            self.assertEqual(direct_apply.returncode, 3)
            wrong_plan_token = self.run_command(
                [
                    sys.executable,
                    "-B",
                    str(self.access(root)),
                    "recover",
                    "--session",
                    "abandoned",
                    "--reason",
                    "user confirmed the old task was closed",
                    "--apply",
                    "--token",
                    "wrong-token",
                ]
            )
            self.assertEqual(wrong_plan_token.returncode, 3)
            applied = self.run_command(
                [
                    sys.executable,
                    "-B",
                    str(self.access(root)),
                    "recover",
                    "--session",
                    "abandoned",
                    "--reason",
                    "user confirmed the old task was closed",
                    "--apply",
                    "--token",
                    str(dry_receipt["recovery_token"]),
                ]
            )
            self.assertEqual(json.loads(applied.stdout)["status"], "recovered")

    @unittest.skipUnless(shutil.which("git"), "git is required")
    def test_git_worktrees_share_the_same_admission_registry(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            root = base / "project"
            root.mkdir()
            initialized_git = self.run_command(["git", "init", "-b", "main"], cwd=root)
            self.assertEqual(initialized_git.returncode, 0, initialized_git.stderr)
            self.initialize(root, mode="adopt-existing")
            for command in (
                ["git", "add", "."],
                [
                    "git",
                    "-c",
                    "user.name=Fixture",
                    "-c",
                    "user.email=fixture@example.invalid",
                    "commit",
                    "-m",
                    "init",
                ],
            ):
                result = self.run_command(command, cwd=root)
                self.assertEqual(result.returncode, 0, result.stderr)
            linked = base / "linked"
            result = self.run_command(
                ["git", "worktree", "add", "-b", "lane", str(linked), "HEAD"], cwd=root
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            main_claim = self.run_command(
                [
                    sys.executable,
                    "-B",
                    str(self.access(root)),
                    "enter",
                    "--mode",
                    "writer",
                    "--actor",
                    "main-writer",
                ]
            )
            self.assertEqual(main_claim.returncode, 0, main_claim.stderr)
            linked_status = self.run_command(
                [sys.executable, "-B", str(self.access(linked)), "status"]
            )
            self.assertEqual(linked_status.returncode, 0, linked_status.stderr)
            observed = json.loads(linked_status.stdout)
            self.assertEqual(observed["runtime_storage"], "git-common-dir")
            self.assertEqual(len(observed["claims"]), 1)
            linked_writer = self.run_command(
                [
                    sys.executable,
                    "-B",
                    str(self.access(linked)),
                    "enter",
                    "--mode",
                    "writer",
                    "--actor",
                    "linked-writer",
                ]
            )
            self.assertEqual(linked_writer.returncode, 2)
            self.finish_claim(root, json.loads(main_claim.stdout))

    @unittest.skipUnless(shutil.which("git"), "git is required")
    def test_disjoint_isolated_writers_can_run_but_overlap_and_records_are_blocked(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            root = base / "project"
            root.mkdir()
            initialized_git = self.run_command(["git", "init", "-b", "main"], cwd=root)
            self.assertEqual(initialized_git.returncode, 0, initialized_git.stderr)
            self.initialize(root, mode="adopt-existing")
            for command in (
                ["git", "add", "."],
                [
                    "git",
                    "-c",
                    "user.name=Fixture",
                    "-c",
                    "user.email=fixture@example.invalid",
                    "commit",
                    "-m",
                    "init",
                ],
            ):
                result = self.run_command(command, cwd=root)
                self.assertEqual(result.returncode, 0, result.stderr)
            worktrees: list[Path] = []
            for name in ("a", "b", "c"):
                worktree = base / f"linked-{name}"
                result = self.run_command(
                    ["git", "worktree", "add", "-b", f"lane-{name}", str(worktree), "HEAD"],
                    cwd=root,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                worktrees.append(worktree)

            receipts: list[dict[str, object]] = []
            for worktree, path in zip(worktrees[:2], ("src/component-a", "src/caf\u00e9")):
                result = self.run_command(
                    [
                        sys.executable,
                        "-B",
                        str(self.access(worktree)),
                        "enter",
                        "--mode",
                        "isolated-writer",
                        "--actor",
                        worktree.name,
                        "--write-path",
                        path,
                    ]
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                receipts.append(json.loads(result.stdout))

            overlap = self.run_command(
                [
                    sys.executable,
                    "-B",
                    str(self.access(worktrees[2])),
                    "enter",
                    "--mode",
                    "isolated-writer",
                    "--actor",
                    "overlap",
                    "--write-path",
                    "src/component-a/file.py",
                ]
            )
            self.assertEqual(overlap.returncode, 2, overlap.stderr)
            case_alias = self.run_command(
                [
                    sys.executable,
                    "-B",
                    str(self.access(worktrees[2])),
                    "enter",
                    "--mode",
                    "isolated-writer",
                    "--actor",
                    "case-alias",
                    "--write-path",
                    "SRC/COMPONENT-A",
                ]
            )
            self.assertEqual(case_alias.returncode, 2, case_alias.stderr)
            unicode_alias = self.run_command(
                [
                    sys.executable,
                    "-B",
                    str(self.access(worktrees[2])),
                    "enter",
                    "--mode",
                    "isolated-writer",
                    "--actor",
                    "unicode-alias",
                    "--write-path",
                    "src/cafe\u0301",
                ]
            )
            self.assertEqual(unicode_alias.returncode, 2, unicode_alias.stderr)
            canonical = self.run_command(
                [
                    sys.executable,
                    "-B",
                    str(self.access(worktrees[2])),
                    "enter",
                    "--mode",
                    "isolated-writer",
                    "--actor",
                    "canonical",
                    "--write-path",
                    "Memory/notes.md",
                ]
            )
            self.assertEqual(canonical.returncode, 3, canonical.stderr)
            git_metadata = self.run_command(
                [
                    sys.executable,
                    "-B",
                    str(self.access(worktrees[2])),
                    "enter",
                    "--mode",
                    "isolated-writer",
                    "--actor",
                    "git-metadata",
                    "--write-path",
                    ".git/config",
                ]
            )
            self.assertEqual(git_metadata.returncode, 3, git_metadata.stderr)
            shared_writer = self.run_command(
                [
                    sys.executable,
                    "-B",
                    str(self.access(root)),
                    "enter",
                    "--mode",
                    "writer",
                    "--actor",
                    "integrator",
                ]
            )
            self.assertEqual(shared_writer.returncode, 2)
            detached = self.run_command(["git", "switch", "--detach"], cwd=worktrees[0])
            self.assertEqual(detached.returncode, 0, detached.stderr)
            drifted = self.run_command(
                [
                    sys.executable,
                    "-B",
                    str(self.access(worktrees[0])),
                    "check",
                    "--session",
                    str(receipts[0]["session_id"]),
                    "--token",
                    str(receipts[0]["token"]),
                ]
            )
            self.assertEqual(drifted.returncode, 3, drifted.stderr)
            for worktree, receipt in zip(worktrees[:2], receipts):
                self.finish_claim(worktree, receipt)
            shared_writer = self.run_command(
                [
                    sys.executable,
                    "-B",
                    str(self.access(root)),
                    "enter",
                    "--mode",
                    "writer",
                    "--actor",
                    "integrator",
                ]
            )
            self.assertEqual(shared_writer.returncode, 0, shared_writer.stderr)
            self.finish_claim(root, json.loads(shared_writer.stdout))

    @unittest.skipUnless(shutil.which("git"), "git is required")
    def test_wrapper_can_admit_worktree_from_configured_nested_repository(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            root = base / "wrapper"
            repository = root / "src" / "product"
            repository.mkdir(parents=True)
            initialized_git = self.run_command(["git", "init", "-b", "main"], cwd=repository)
            self.assertEqual(initialized_git.returncode, 0, initialized_git.stderr)
            (repository / "README.md").write_text("source\n", encoding="utf-8")
            for command in (
                ["git", "add", "."],
                [
                    "git",
                    "-c",
                    "user.name=Fixture",
                    "-c",
                    "user.email=fixture@example.invalid",
                    "commit",
                    "-m",
                    "source",
                ],
            ):
                result = self.run_command(command, cwd=repository)
                self.assertEqual(result.returncode, 0, result.stderr)
            self.initialize(
                root,
                mode="adopt-existing",
                extra=["--repository-root", "src/product"],
            )
            linked = base / "linked-product"
            worktree = self.run_command(
                ["git", "worktree", "add", "-b", "lane", str(linked), "HEAD"],
                cwd=repository,
            )
            self.assertEqual(worktree.returncode, 0, worktree.stderr)
            entered = self.run_command(
                [
                    sys.executable,
                    "-B",
                    str(self.access(root)),
                    "enter",
                    "--mode",
                    "isolated-writer",
                    "--actor",
                    "nested-repo-agent",
                    "--workspace",
                    str(linked),
                    "--write-path",
                    "component-a",
                ]
            )
            self.assertEqual(entered.returncode, 0, entered.stderr)
            receipt = json.loads(entered.stdout)
            self.assertEqual(receipt["workspace"], str(linked.resolve()))
            self.assertEqual(receipt["runtime_storage"], "git-common-dir")
            self.finish_claim(root, receipt)

    def test_validator_rejects_tampered_helper(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "project"
            self.initialize(root)
            helper = self.access(root)
            helper.write_text(helper.read_text(encoding="utf-8") + "\n# tampered\n", encoding="utf-8")
            runtime = self.run_command([sys.executable, "-B", str(helper), "status"])
            self.assertEqual(runtime.returncode, 3)
            self.assertIn("helper digest differs", runtime.stderr)
            result = self.run_command([sys.executable, "-B", str(VALIDATOR), str(root)])
            self.assertEqual(result.returncode, 1)
            self.assertIn("digest differs", result.stderr)

    def test_runtime_and_validator_reject_tampered_local_authority_documents(self) -> None:
        for relative, marker in (
            ("AGENTS.md", "project-conventions:access:start"),
            (".project-conventions/ACCESS.md", "# Project Access"),
        ):
            with self.subTest(relative=relative), tempfile.TemporaryDirectory() as raw:
                root = Path(raw) / "project"
                self.initialize(root)
                path = root / relative
                text = path.read_text(encoding="utf-8")
                path.write_text(text.replace(marker, marker + "-tampered", 1), encoding="utf-8")
                runtime = self.run_command(
                    [sys.executable, "-B", str(self.access(root)), "status"]
                )
                self.assertEqual(runtime.returncode, 3)
                validated = self.run_command(
                    [sys.executable, "-B", str(VALIDATOR), str(root)]
                )
                self.assertEqual(validated.returncode, 1)

    def test_runtime_and_validator_reject_repository_path_escape(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "project"
            self.initialize(root)
            config_path = root / ".project-conventions" / "project.json"
            config = json.loads(config_path.read_text(encoding="utf-8"))
            config["repository_root"] = "../outside"
            config_path.write_text(
                json.dumps(config, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            runtime = self.run_command(
                [sys.executable, "-B", str(self.access(root)), "status"]
            )
            self.assertEqual(runtime.returncode, 3)
            self.assertIn("normalized relative path", runtime.stderr)
            validated = self.run_command(
                [sys.executable, "-B", str(VALIDATOR), str(root)]
            )
            self.assertEqual(validated.returncode, 1)
            self.assertIn("normalized relative path", validated.stderr)

            portable_root = Path(raw) / "portable-config"
            self.initialize(portable_root)
            portable_config_path = portable_root / ".project-conventions" / "project.json"
            portable_config = json.loads(portable_config_path.read_text(encoding="utf-8"))
            portable_config["repository_root"] = "src/a|b"
            portable_config_path.write_text(
                json.dumps(portable_config, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            portable_runtime = self.run_command(
                [sys.executable, "-B", str(self.access(portable_root)), "status"]
            )
            self.assertEqual(portable_runtime.returncode, 3)
            self.assertIn("not portable", portable_runtime.stderr)
            portable_validation = self.run_command(
                [sys.executable, "-B", str(VALIDATOR), str(portable_root)]
            )
            self.assertEqual(portable_validation.returncode, 1)
            self.assertIn("not portable", portable_validation.stderr)


if __name__ == "__main__":
    os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    unittest.main()
