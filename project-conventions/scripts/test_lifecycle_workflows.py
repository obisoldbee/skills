#!/usr/bin/env python3
"""Regression tests for lifecycle routing and named migration semantics."""

from __future__ import annotations

import os
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


if __name__ == "__main__":
    os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    unittest.main()
