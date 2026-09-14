#!/usr/bin/env python3
"""Behavioral tests for ordinary Project Root initialization and access claims."""

from __future__ import annotations

import hashlib
import importlib.util
import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


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
            "--coordination-policy", "legacy-claims",
        ]
        if extra:
            command.extend(extra)
        result = self.run_command(command)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def access(self, root: Path) -> Path:
        return root / ".project-conventions" / "project_access.py"

    def load_initializer_module(self):
        module_name = f"_project_root_initializer_test_{id(self)}"
        spec = importlib.util.spec_from_file_location(module_name, INITIALIZER)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        sys.modules[module_name] = module
        self.addCleanup(sys.modules.pop, module_name, None)
        spec.loader.exec_module(module)
        return module

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

    def test_optional_paths_reject_reserved_non_normalized_and_file_topology_without_writing(self) -> None:
        cases = (
            ("--records-dir", "."),
            ("--records-dir", "a//b"),
            ("--records-dir", "a/."),
            ("--records-dir", ".git/records"),
            ("--records-dir", ".project-conventions/records"),
            ("--records-dir", ".codex/records"),
            ("--records-dir", "README.md/records"),
            ("--repository-root", "README.md/repo"),
        )
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            for index, (flag, value) in enumerate(cases):
                with self.subTest(flag=flag, value=value):
                    root = base / f"case-{index}"
                    for apply in (False, True):
                        command = [
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
                        if apply:
                            command.append("--apply")
                        result = self.run_command(command)
                        self.assertNotEqual(result.returncode, 0)
                        self.assertFalse(root.exists())

    def test_adopt_agents_preserves_byte_prefix_mode_and_crlf_idempotently(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "legacy"
            root.mkdir()
            agents = root / "AGENTS.md"
            original = b"# Existing Rules\r\n\r\n- Keep trailing spaces.  \r\n\r\n"
            agents.write_bytes(original)
            os.chmod(agents, 0o751)
            expected_mode = agents.stat().st_mode & 0o777
            first = self.initialize(root, mode="adopt-existing")
            self.assertEqual(first["status"], "initialized")
            adopted = agents.read_bytes()
            self.assertTrue(adopted.startswith(original))
            self.assertIn(b"\r\n<!-- project-conventions:access:start -->\r\n", adopted)
            self.assertEqual(agents.stat().st_mode & 0o777, expected_mode)
            second = self.initialize(root, mode="adopt-existing")
            self.assertEqual(second["status"], "already_initialized")
            self.assertEqual(agents.read_bytes(), adopted)
            self.assertEqual(agents.stat().st_mode & 0o777, expected_mode)
            validated = self.run_command([sys.executable, "-B", str(VALIDATOR), str(root)])
            self.assertEqual(validated.returncode, 0, validated.stderr)

    def test_apply_failure_rolls_back_created_paths_and_agents_bytes_and_mode(self) -> None:
        initializer = self.load_initializer_module()
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "legacy"
            root.mkdir()
            agents = root / "AGENTS.md"
            original = b"# Existing Rules\n\n- Preserve exact tail.  \n"
            agents.write_bytes(original)
            os.chmod(agents, 0o750)
            expected_mode = agents.stat().st_mode & 0o777
            real_inspect = initializer.inspect_target
            calls = 0

            def fail_readback(*args, **kwargs):
                nonlocal calls
                calls += 1
                if calls == 2:
                    raise OSError("injected readback failure")
                return real_inspect(*args, **kwargs)

            with mock.patch.object(initializer, "inspect_target", side_effect=fail_readback):
                with self.assertRaisesRegex(OSError, "injected readback failure"):
                    initializer.initialize(
                        root,
                        "code",
                        "adopt-existing",
                        None,
                        None,
                        "versions/records",
                        "standard",
                        None,
                        True,
                    )
            self.assertEqual(agents.read_bytes(), original)
            self.assertEqual(agents.stat().st_mode & 0o777, expected_mode)
            self.assertEqual(sorted(path.name for path in root.iterdir()), ["AGENTS.md"])

    def test_rollback_preserves_concurrent_user_replacement(self) -> None:
        initializer = self.load_initializer_module()
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "project"
            real_inspect = initializer.inspect_target
            calls = 0
            user_bytes = b"concurrent user content\n"

            def replace_then_fail(*args, **kwargs):
                nonlocal calls
                calls += 1
                if calls == 2:
                    readme = root / "README.md"
                    readme.write_bytes(user_bytes)
                    raise OSError("injected concurrent readback failure")
                return real_inspect(*args, **kwargs)

            with mock.patch.object(initializer, "inspect_target", side_effect=replace_then_fail):
                with self.assertRaisesRegex(
                    initializer.ProjectInitializationError,
                    "rollback preserved changed or unrecoverable paths",
                ):
                    initializer.initialize(
                        root,
                        "code",
                        "fresh-empty",
                        None,
                        None,
                        None,
                        "standard",
                        None,
                        True,
                    )
            self.assertEqual((root / "README.md").read_bytes(), user_bytes)

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

    def test_agent_skill_rejects_duplicate_name_and_external_suffix_routes(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            duplicate_root = base / "duplicate-name"
            duplicate_entry = duplicate_root / "src" / "demo-skill" / "SKILL.md"
            duplicate_entry.parent.mkdir(parents=True)
            duplicate_entry.write_text(
                "---\nname: demo-skill\nname : demo-skill\ndescription: duplicate\n---\n",
                encoding="utf-8",
            )
            duplicate = self.run_command(
                [
                    sys.executable,
                    "-B",
                    str(INITIALIZER),
                    str(duplicate_root),
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
            self.assertNotEqual(duplicate.returncode, 0)
            self.assertFalse((duplicate_root / ".project-conventions").exists())

            routes = (
                "/tmp/src/demo-skill/SKILL.md",
                "prefix/src/demo-skill/SKILL.md",
                "../src/demo-skill/SKILL.md",
                r"C:\\outside\\src\\demo-skill\\SKILL.md",
                "file" + ":///tmp/src/demo-skill/SKILL.md",
            )
            for index, route in enumerate(routes):
                with self.subTest(route=route):
                    root = base / f"route-{index}"
                    root.mkdir()
                    agents = root / "AGENTS.md"
                    original = f"# Existing Rules\n\nSkill source: `{route}`.\n"
                    agents.write_text(original, encoding="utf-8")
                    rejected = self.run_command(
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
                    self.assertNotEqual(rejected.returncode, 0)
                    self.assertIn("conflicting Agent Skill source routes", rejected.stderr)
                    self.assertEqual(agents.read_text(encoding="utf-8"), original)
                    self.assertFalse((root / ".project-conventions").exists())

    def test_validator_rejects_duplicate_agent_skill_name(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "skill"
            extra = ["--profile", "agent-skill", "--skill-name", "demo-skill"]
            self.initialize(root, extra=extra)
            entry = root / "src" / "demo-skill" / "SKILL.md"
            entry.write_text(
                "---\nname: demo-skill\nname: demo-skill\ndescription: duplicate\n---\n",
                encoding="utf-8",
            )
            validated = self.run_command([sys.executable, "-B", str(VALIDATOR), str(root)])
            self.assertNotEqual(validated.returncode, 0)
            self.assertIn("frontmatter name differs", validated.stderr)

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

            concurrent_reader = self.run_command(
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
            self.assertEqual(concurrent_reader.returncode, 0, concurrent_reader.stderr)
            self.finish_claim(root, json.loads(concurrent_reader.stdout))
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

    def test_readers_share_with_writer_without_freezing_inputs(self) -> None:
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
            self.assertEqual(writer.returncode, 0, writer.stderr)
            self.finish_claim(root, json.loads(writer.stdout))
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
            self.assertEqual(linked_writer.returncode, 3)
            self.finish_claim(root, json.loads(main_claim.stdout))

    @unittest.skipUnless(shutil.which("git"), "git is required")
    def test_distinct_worktrees_allow_logical_overlap_but_one_writer_per_workspace(self) -> None:
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

            for value in (".", "a//b", "a/."):
                with self.subTest(write_path=value):
                    invalid = self.run_command(
                        [
                            sys.executable,
                            "-B",
                            str(self.access(worktrees[0])),
                            "enter",
                            "--mode",
                            "isolated-writer",
                            "--actor",
                            "invalid-path",
                            "--write-path",
                            value,
                        ]
                    )
                    self.assertEqual(invalid.returncode, 3, invalid.stderr)
            empty_status = self.run_command(
                [sys.executable, "-B", str(self.access(root)), "status"]
            )
            self.assertEqual(empty_status.returncode, 0, empty_status.stderr)
            self.assertEqual(json.loads(empty_status.stdout)["claims"], [])

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
            self.assertEqual(overlap.returncode, 0, overlap.stderr)
            third_receipt = json.loads(overlap.stdout)
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
            self.finish_claim(worktrees[2], third_receipt)
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
            self.assertEqual(shared_writer.returncode, 0, shared_writer.stderr)
            self.finish_claim(root, json.loads(shared_writer.stdout))
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

    @unittest.skipIf(os.name == "nt", "portable runtime-link fixture is Unix-only")
    def test_runtime_directory_and_database_links_fail_closed(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            runtime_root = base / "runtime-link-project"
            self.initialize(runtime_root)
            external_runtime = base / "external-runtime"
            external_runtime.mkdir()
            runtime = runtime_root / ".project-conventions" / "runtime"
            runtime.symlink_to(external_runtime, target_is_directory=True)
            linked_runtime = self.run_command(
                [sys.executable, "-B", str(self.access(runtime_root)), "status"]
            )
            self.assertEqual(linked_runtime.returncode, 3)
            self.assertFalse((external_runtime / "access.sqlite3").exists())

            database_root = base / "database-link-project"
            self.initialize(database_root)
            database_runtime = database_root / ".project-conventions" / "runtime"
            database_runtime.mkdir()
            external_database = base / "external.sqlite3"
            (database_runtime / "access.sqlite3").symlink_to(external_database)
            linked_database = self.run_command(
                [sys.executable, "-B", str(self.access(database_root)), "status"]
            )
            self.assertEqual(linked_database.returncode, 3)
            self.assertFalse(external_database.exists())

    def test_validator_binds_gitignore_and_document_directories(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            gitignore_root = base / "gitignore"
            self.initialize(gitignore_root)
            (gitignore_root / ".project-conventions" / ".gitignore").write_text(
                "*.sqlite3\n", encoding="utf-8"
            )
            gitignore_validation = self.run_command(
                [sys.executable, "-B", str(VALIDATOR), str(gitignore_root)]
            )
            self.assertEqual(gitignore_validation.returncode, 1)
            self.assertIn(".gitignore differs", gitignore_validation.stderr)

            for relative in ("docs/reviews", "docs/research"):
                with self.subTest(relative=relative):
                    document_root = base / relative.replace("/", "-")
                    self.initialize(document_root, project_type="document")
                    (document_root / relative).rmdir()
                    validation = self.run_command(
                        [sys.executable, "-B", str(VALIDATOR), str(document_root)]
                    )
                    self.assertEqual(validation.returncode, 1)
                    self.assertIn("required real directory is missing", validation.stderr)

    def test_crlf_checkout_preserves_hash_bound_authority(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw) / "project"
            self.initialize(root)
            for relative in (
                ".project-conventions/project_access.py",
                ".project-conventions/ACCESS.md",
            ):
                path = root / relative
                path.write_bytes(path.read_bytes().replace(b"\n", b"\r\n"))
            runtime = self.run_command(
                [sys.executable, "-B", str(self.access(root)), "status"]
            )
            self.assertEqual(runtime.returncode, 0, runtime.stderr)
            validated = self.run_command(
                [sys.executable, "-B", str(VALIDATOR), str(root)]
            )
            self.assertEqual(validated.returncode, 0, validated.stderr)

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
