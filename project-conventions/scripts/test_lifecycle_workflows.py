#!/usr/bin/env python3
"""Regression tests for lifecycle routing and named migration semantics."""

from __future__ import annotations

import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]


class LifecycleWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill = (PACKAGE_ROOT / "SKILL.md").read_text(encoding="utf-8")
        cls.lifecycle = (
            PACKAGE_ROOT / "references" / "lifecycle-workflows.md"
        ).read_text(encoding="utf-8")
        cls.migration = (
            PACKAGE_ROOT / "references" / "migration-guide.md"
        ).read_text(encoding="utf-8")
        cls.metadata = (PACKAGE_ROOT / "agents" / "openai.yaml").read_text(
            encoding="utf-8"
        )
        cls.collection = (
            PACKAGE_ROOT / "references" / "project-collection.md"
        ).read_text(encoding="utf-8")
        cls.initializer = PACKAGE_ROOT / "scripts" / "initialize_project_collection.py"
        cls.control_initializer = (
            PACKAGE_ROOT / "scripts" / "initialize_skills_control_project.py"
        )
        cls.distribution_root = PACKAGE_ROOT.parent
        cls.layout_repair = (
            PACKAGE_ROOT / "scripts" / "repair_project_conventions_checkout_layout.py"
        )

    def test_named_full_chain_continues_after_direct_load(self) -> None:
        for content in (self.skill, self.lifecycle):
            self.assertIn("named bootstrap-and-migrate chain", content)
        self.assertIn("continue in the same task", self.skill)
        self.assertIn("direct-loading the checked-out Skill", self.lifecycle)
        self.assertIn("It is not an automatic stop", self.lifecycle)

    def test_named_sources_are_in_scope_and_exact_map_is_authority(self) -> None:
        self.assertIn("Explicitly named migration sources are in scope", self.skill)
        self.assertIn("names every source and destination", self.lifecycle)
        self.assertIn("do not present unrelated keep/archive/delete choices", self.lifecycle)
        self.assertIn(
            "<project-parent>\\skills               -> "
            "<project-parent>\\obisoldbee-skills\\skills",
            self.lifecycle,
        )
        self.assertIn(
            "<project-parent>\\project-conventions  -> "
            "<project-parent>\\obisoldbee-skills\\project-conventions",
            self.lifecycle,
        )

    def test_checkout_and_link_use_migration_safe_paths(self) -> None:
        self.assertIn("$RepositoryRoot = Join-Path $BootstrapRoot 'src'", self.lifecycle)
        self.assertIn(
            "$PackageRoot = Join-Path $RepositoryRoot 'project-conventions'",
            self.lifecycle,
        )
        self.assertIn(
            "<project-parent>\\obisoldbee-skills\\project-conventions"
            "\\src\\project-conventions",
            self.lifecycle,
        )
        self.assertIn("obsolete nested layout", self.lifecycle)
        self.assertIn("src/skills/project-conventions/SKILL.md", self.skill)
        self.assertIn("never `src/skills/project-conventions/SKILL.md`", self.skill)
        self.assertIn("Never link a temporary path", self.skill)
        self.assertIn("Only after both moves", self.lifecycle)
        combined = self.skill + "\n" + self.lifecycle
        self.assertNotIn("App" + "Data", combined)
        self.assertNotIn(".local" + "/share", combined)

    def test_active_project_root_move_has_one_safe_handoff(self) -> None:
        self.assertIn("Moving the Active Project Root into a Collection", self.migration)
        self.assertIn("Switch command execution to the common parent", self.migration)
        self.assertIn("reopen-at-parent handoff", self.migration)
        self.assertIn("do not re-plan unrelated directories", self.migration)
        self.assertIn("including hidden entries", self.migration)

    def test_clone_only_and_update_only_keep_narrow_stop_boundaries(self) -> None:
        self.assertIn("If the request is bootstrap-only, stop after validation", self.skill)
        self.assertIn("If the user requested clone/download only", self.lifecycle)
        self.assertIn("Forbidden side effects in update-only", self.lifecycle)
        self.assertIn("creating, repairing, replacing, or reapplying links", self.lifecycle)

    def test_full_chain_can_preserve_clean_local_ahead_branch(self) -> None:
        for content in (self.skill, self.lifecycle):
            self.assertIn("preserved", content)
        self.assertIn("This recovery is forbidden for update-only", self.lifecycle)
        self.assertIn("never rebase, reset, delete, or push", self.lifecycle)

        def git(*arguments: str, cwd: Path) -> str:
            result = subprocess.run(
                ["git", *arguments],
                cwd=cwd,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            return result.stdout.strip()

        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            remote = root / "remote.git"
            seed = root / "seed"
            checkout = root / "checkout"
            git("init", "--bare", "--initial-branch=main", str(remote), cwd=root)
            git("init", "--initial-branch=main", str(seed), cwd=root)
            git("config", "user.name", "Lifecycle Test", cwd=seed)
            git("config", "user.email", "lifecycle@example.invalid", cwd=seed)
            (seed / "state.txt").write_text("remote\n", encoding="utf-8")
            git("add", "state.txt", cwd=seed)
            git("commit", "-m", "remote base", cwd=seed)
            git("remote", "add", "origin", str(remote), cwd=seed)
            git("push", "-u", "origin", "main", cwd=seed)
            git("clone", str(remote), str(checkout), cwd=root)
            git("config", "user.name", "Lifecycle Test", cwd=checkout)
            git("config", "user.email", "lifecycle@example.invalid", cwd=checkout)
            (checkout / "state.txt").write_text("local\n", encoding="utf-8")
            git("add", "state.txt", cwd=checkout)
            git("commit", "-m", "local work", cwd=checkout)

            old_head = git("rev-parse", "HEAD", cwd=checkout)
            preserved = f"main-preserved-{old_head[:7]}"
            self.assertEqual(git("status", "--porcelain=v1", cwd=checkout), "")
            git("fetch", "origin", cwd=checkout)
            git("branch", "-m", preserved, cwd=checkout)
            git("switch", "-c", "main", "--track", "origin/main", cwd=checkout)

            self.assertEqual(git("rev-parse", preserved, cwd=checkout), old_head)
            self.assertEqual(
                git("rev-parse", "HEAD", cwd=checkout),
                git("rev-parse", "origin/main", cwd=checkout),
            )
            self.assertEqual(git("status", "--porcelain=v1", cwd=checkout), "")

    def test_collection_initializer_is_first_bounded_write(self) -> None:
        for content in (self.skill, self.lifecycle, self.collection):
            self.assertIn("initialize_project_collection.py", content)
        self.assertIn("first bounded write", self.skill)
        self.assertIn("first write", self.lifecycle)
        self.assertIn("read back", self.collection)

        with tempfile.TemporaryDirectory() as raw:
            target = Path(raw) / "obisoldbee-skills"
            command = [
                sys.executable,
                "-B",
                str(self.initializer),
                str(target),
                "--control-project",
                "skills",
                "--reserve",
                "skills",
                "--reserve",
                "project-conventions",
            ]
            dry_run = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(dry_run.returncode, 0, dry_run.stderr)
            dry_payload = json.loads(dry_run.stdout)
            self.assertEqual(dry_payload["status"], "would_initialize")
            self.assertEqual(
                dry_payload["would_create"],
                ["AGENTS.md", "README.md", "MEMBERS.md"],
            )
            self.assertFalse(target.exists())

            applied = subprocess.run(
                [*command, "--apply"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(applied.returncode, 0, applied.stderr)
            applied_payload = json.loads(applied.stdout)
            self.assertEqual(applied_payload["status"], "initialized")
            self.assertEqual(
                {path.name for path in target.iterdir()},
                {"AGENTS.md", "README.md", "MEMBERS.md"},
            )
            self.assertFalse((target / "skills").exists())
            self.assertFalse((target / "project-conventions").exists())

            repeated = subprocess.run(
                [*command, "--apply"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(repeated.returncode, 0, repeated.stderr)
            self.assertEqual(json.loads(repeated.stdout)["status"], "already_initialized")

    def test_collection_initializer_refuses_existing_content(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            target = Path(raw) / "obisoldbee-skills"
            target.mkdir()
            marker = target / "keep.txt"
            marker.write_text("keep\n", encoding="utf-8")
            result = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(self.initializer),
                    str(target),
                    "--control-project",
                    "skills",
                    "--reserve",
                    "project-conventions",
                    "--apply",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("outside the minimal collection overlay", result.stderr)
            self.assertEqual(marker.read_text(encoding="utf-8"), "keep\n")
            self.assertEqual({path.name for path in target.iterdir()}, {"keep.txt"})

    def test_fresh_skills_control_project_is_complete_and_deterministic(self) -> None:
        if not (self.distribution_root / "ROOT-MANIFEST.sha256").is_file():
            self.skipTest("requires a complete distribution checkout")

        def git(*arguments: str, cwd: Path) -> str:
            result = subprocess.run(
                ["git", *arguments],
                cwd=cwd,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            return result.stdout.strip()

        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            collection = root / "obisoldbee-skills"
            remote = root / "remote.git"
            seed = root / "seed"
            member_root = collection / "project-conventions"
            checkout = member_root / "src"

            root_result = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(self.initializer),
                    str(collection),
                    "--control-project",
                    "skills",
                    "--reserve",
                    "skills",
                    "--reserve",
                    "project-conventions",
                    "--apply",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(root_result.returncode, 0, root_result.stderr)

            git("init", "--bare", "--initial-branch=main", str(remote), cwd=root)
            git("init", "--initial-branch=main", str(seed), cwd=root)
            git("config", "user.name", "Control Initializer Test", cwd=seed)
            git("config", "user.email", "control@example.invalid", cwd=seed)
            package = seed / "project-conventions"
            package.mkdir()
            (package / "SKILL.md").write_text(
                "---\nname: project-conventions\ndescription: fixture\n---\n",
                encoding="utf-8",
            )
            git("add", "project-conventions/SKILL.md", cwd=seed)
            git("commit", "-m", "fixture", cwd=seed)
            git("remote", "add", "origin", str(remote), cwd=seed)
            git("push", "-u", "origin", "main", cwd=seed)

            member_root.mkdir()
            for name in ("docs", "conversation", "memory"):
                (member_root / name).mkdir()
            git("clone", str(remote), str(checkout), cwd=root)
            git(
                "remote",
                "set-url",
                "origin",
                "https://github.com/obisoldbee/skills.git",
                cwd=checkout,
            )

            command = [
                sys.executable,
                "-B",
                str(self.control_initializer),
                str(collection),
                "--distribution-root",
                str(self.distribution_root),
            ]
            dry_run = subprocess.run(
                command,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(dry_run.returncode, 0, dry_run.stderr)
            self.assertEqual(json.loads(dry_run.stdout)["status"], "would_initialize")
            self.assertFalse((collection / "skills").exists())

            applied = subprocess.run(
                [*command, "--apply"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(applied.returncode, 0, applied.stderr)
            payload = json.loads(applied.stdout)
            self.assertEqual(payload["status"], "initialized")
            self.assertEqual(payload["links_created"], [])
            self.assertEqual(payload["git_roots_created"], [])

            control = collection / "skills"
            self.assertEqual(
                {path.name for path in (control / "src").iterdir()},
                {"README.md", "config", "public-repo", "scripts", "tests"},
            )
            for directory in (
                "conversation",
                "docs/indexes",
                "memory",
                "release",
                "runtime",
                "src/config",
                "src/public-repo",
                "src/scripts",
                "src/tests",
            ):
                self.assertTrue((control / directory).is_dir(), directory)
            self.assertTrue(
                (control / "src" / "scripts" / "link-windows.ps1").is_file()
            )
            self.assertTrue(
                (control / "src" / "scripts" / "link-macos.sh").is_file()
            )
            self.assertTrue(
                (control / "src" / "scripts" / "build_public_root_overlay.py").is_file()
            )
            self.assertTrue(
                (control / "src" / "tests" / "test_public_root_overlay.py").is_file()
            )
            exports = (control / "src" / "config" / "skill-exports.tsv").read_text(
                encoding="utf-8"
            )
            self.assertIn(
                "project-conventions/src/project-conventions", exports
            )
            members = (control / "docs" / "indexes" / "members.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("| skills | Skills Collection Control |", members)
            self.assertIn("| project-conventions | Project Conventions |", members)
            self.assertNotIn("/" + "Users" + "/", members)
            self.assertNotIn("C:" + "\\Users\\", members)

            generated_tests = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(control / "src" / "tests" / "test_public_root_overlay.py"),
                ],
                cwd=control,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(generated_tests.returncode, 0, generated_tests.stderr)

            repeated = subprocess.run(
                [*command, "--apply"],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(repeated.returncode, 0, repeated.stderr)
            self.assertEqual(json.loads(repeated.stdout)["status"], "already_initialized")

    def test_fresh_control_project_is_routed_to_the_deterministic_initializer(self) -> None:
        for content in (self.skill, self.lifecycle, self.collection, self.metadata):
            self.assertIn("initialize_skills_control_project.py", content)
        combined = self.skill + "\n" + self.lifecycle + "\n" + self.collection
        self.assertIn("Do not handwrite a reduced control project", combined)
        self.assertIn("src/config/", combined)
        self.assertIn("src/public-repo/", combined)
        self.assertIn("src/scripts/", combined)
        self.assertIn("src/tests/", combined)

    def test_obsolete_checkout_layout_is_flattened_without_git_change(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            bootstrap = Path(raw) / "project-conventions"
            checkout = bootstrap / "src" / "skills"
            package = checkout / "project-conventions"
            package.mkdir(parents=True)
            (package / "SKILL.md").write_text(
                "---\nname: project-conventions\ndescription: fixture\n---\n",
                encoding="utf-8",
            )
            fixture_repair = (
                package / "scripts" / "repair_project_conventions_checkout_layout.py"
            )
            fixture_repair.parent.mkdir()
            fixture_repair.write_bytes(self.layout_repair.read_bytes())

            def run_git(*arguments: str, cwd: Path = checkout) -> str:
                result = subprocess.run(
                    ["git", *arguments],
                    cwd=cwd,
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(result.returncode, 0, result.stderr)
                return result.stdout.strip()

            run_git("init", "--initial-branch=main")
            run_git("config", "user.name", "Layout Test")
            run_git("config", "user.email", "layout@example.invalid")
            run_git("add", "project-conventions")
            run_git("commit", "-m", "fixture")
            run_git("remote", "add", "origin", "https://github.com/obisoldbee/skills.git")
            before_head = run_git("rev-parse", "HEAD")

            dry_run = subprocess.run(
                [sys.executable, "-B", str(fixture_repair), str(bootstrap)],
                cwd=bootstrap,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(dry_run.returncode, 0, dry_run.stderr)
            self.assertEqual(json.loads(dry_run.stdout)["status"], "would_repair")
            self.assertTrue(checkout.is_dir())

            applied = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(fixture_repair),
                    str(bootstrap),
                    "--apply",
                ],
                cwd=bootstrap,
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(applied.returncode, 0, applied.stderr)
            payload = json.loads(applied.stdout)
            self.assertEqual(payload["status"], "repaired")
            repository_root = bootstrap / "src"
            self.assertTrue((repository_root / ".git").is_dir())
            self.assertTrue((repository_root / "project-conventions" / "SKILL.md").is_file())
            self.assertFalse((repository_root / "skills").exists())
            self.assertFalse((bootstrap / ".src-layout-repair").exists())
            self.assertEqual(
                run_git("rev-parse", "HEAD", cwd=repository_root),
                before_head,
            )
            self.assertEqual(run_git("status", "--porcelain=v1", cwd=repository_root), "")


if __name__ == "__main__":
    os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    unittest.main()
