#!/usr/bin/env python3
"""Regression tests for lifecycle routing and named migration semantics."""

from __future__ import annotations

import os
import subprocess
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

    def test_named_full_chain_continues_after_direct_load(self) -> None:
        for content in (self.skill, self.lifecycle):
            self.assertIn("named bootstrap-and-migrate chain", content)
        self.assertIn("continue in the same task", self.skill)
        self.assertIn("direct-loading the checked-out Skill", self.lifecycle)
        self.assertIn("It is not an automatic stop", self.lifecycle)
        self.assertIn("same task", self.metadata)

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
        self.assertIn("$Checkout = Join-Path $BootstrapRoot 'src\\skills'", self.lifecycle)
        self.assertIn(
            "<project-parent>\\obisoldbee-skills\\project-conventions"
            "\\src\\skills\\project-conventions",
            self.lifecycle,
        )
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
        self.assertIn("preserve", self.metadata)
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


if __name__ == "__main__":
    os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    unittest.main()
