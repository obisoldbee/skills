#!/usr/bin/env python3
"""Behavioral regressions for path-scoped concurrency and copied-helper upgrades."""

from __future__ import annotations

import hashlib
import json
import os
import shutil
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from contextlib import closing
from pathlib import Path
from unittest import mock

import project_access as access
import test_project_root_workflows as fixtures
import upgrade_project_access as upgrade


class ScopedAccessTests(unittest.TestCase):
    run_command = fixtures.ProjectRootWorkflowTests.run_command
    initialize = fixtures.ProjectRootWorkflowTests.initialize
    access = fixtures.ProjectRootWorkflowTests.access
    finish_claim = fixtures.ProjectRootWorkflowTests.finish_claim

    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.root = Path(temporary.name) / "project"
        self.initialize(self.root)

    def command(self, *args):
        return self.run_command([sys.executable, "-B", str(self.access(self.root)), *args])

    def enter(self, *scopes, mode="scoped-writer", code=0):
        result = self.command("enter", "--mode", mode, "--actor", "test-agent", *scopes)
        self.assertEqual(result.returncode, code, result.stderr or result.stdout)
        return json.loads(result.stdout) if code != 3 else None

    def install_v1_fixture(self):
        # Compatibility fixture: v1 schema/CHECK and version gate, without
        # vendoring a second runtime implementation into the package.
        helper = self.access(self.root)
        content = helper.read_text().replace("PROTOCOL_VERSION = 2", "PROTOCOL_VERSION = 1")
        content = content.replace("if observed is not None and observed[0] == \"1\":", "if False:")
        content = content.replace("'isolated-writer', 'scoped-writer'", "'isolated-writer'")
        helper.write_text(content)
        config_path = helper.parent / "project.json"
        config = json.loads(config_path.read_text())
        config["helper_sha256"] = access.portable_text_sha256(helper.read_bytes())
        config_path.write_text(json.dumps(config, sort_keys=True, indent=2) + "\n")

    def test_two_reports_same_folder_and_reader_can_run_together(self):
        first = self.enter("--write-file", "docs/reviews/a.md")
        second = self.enter("--write-file", "docs/reviews/b.md")
        reader = self.enter(mode="read-only")
        status = json.loads(self.command("status").stdout)
        self.assertTrue(status["read_only_allowed"])
        self.assertEqual(len(status["claims"]), 3)
        self.assertEqual(first["write_scopes"], [{"kind": "file", "path": "docs/reviews/a.md"}])
        for receipt, name in ((first, "a.md"), (second, "b.md")):
            output = self.root / "docs/reviews" / name
            output.parent.mkdir(parents=True, exist_ok=True)
            with output.open("x") as stream:
                stream.write(name)
            check = self.command("check", "--session", receipt["session_id"], "--token", receipt["token"])
            self.assertEqual(check.returncode, 0, check.stderr)
        for receipt in (first, second, reader):
            self.finish_claim(self.root, receipt)
        self.assertEqual((self.root / "docs/reviews/a.md").read_text(), "a.md")

    def test_file_folder_overlap_and_sibling_prefixes(self):
        file_claim = self.enter("--write-file", "docs/reviews/a.md")
        for flags in (("--write-file", "docs/reviews/a.md"), ("--write-dir", "docs/reviews"),
                      ("--write-file", "DOCS/REVIEWS/A.MD")):
            self.enter(*flags, code=2)
        directory = self.enter("--write-dir", "docs/research/task")
        self.enter("--write-file", "docs/research/task/out.md", code=2)
        self.enter("--write-dir", "docs/research/task/nested", code=2)
        sibling = self.enter("--write-dir", "docs/research/task-two")
        for receipt in (file_claim, directory, sibling):
            self.finish_claim(self.root, receipt)

    def test_unicode_aliases_and_disjoint_new_target_after_denial(self):
        claim = self.enter("--write-file", "docs/caf\u00e9.md")
        blocked = self.enter("--write-file", "docs/cafe\u0301.md", code=2)
        self.assertEqual(len(blocked["claims"]), 1)
        other = self.enter("--write-file", "docs/cafe-2.md")
        for receipt in (claim, other):
            self.finish_claim(self.root, receipt)

    def test_invalid_or_ambiguous_declarations_and_target_types(self):
        for flags in ((), ("--write-file", "../escape"), ("--write-file", "/tmp/escape"),
                      ("--write-file", "docs/*.md"), ("--write-file", "a//b"),
                      ("--write-file", "docs\\a.md"), ("--write-file", "AUX.txt"),
                      ("--write-path", "a"), ("--write-dir", "docs", "--write-file", "docs/a"),
                      ("--write-file", ".git/config"), ("--write-dir", ".project-conventions"),
                      ("--write-file", "src/repo/.git/config"), ("--write-file", ".codex/settings"),
                      ("--write-file", "docs"), ("--write-dir", "AGENTS.md")):
            with self.subTest(flags=flags):
                self.enter(*flags, code=3)
        self.enter("--write-file", "docs/a", mode="read-only", code=3)

    def test_short_record_claims_only_conflict_on_the_actual_record(self):
        report = self.enter("--write-file", "docs/reviews/a.md")
        memory = self.enter("--write-file", "memory/2099-01-01.md")
        self.enter("--write-file", "memory/2099-01-01.md", code=2)
        conversation = self.enter("--write-dir", "conversation")
        self.enter("--write-file", "conversation/02-other.md", code=2)
        self.finish_claim(self.root, memory)
        next_memory = self.enter("--write-file", "memory/2099-01-01.md")
        for receipt in (report, conversation, next_memory):
            self.finish_claim(self.root, receipt)

    def test_exclusive_maintenance_blocks_writes_but_allows_reads_in_both_orders(self):
        reader = self.enter(mode="read-only")
        writer = self.enter(mode="writer")
        another_reader = self.enter(mode="read-only")
        self.enter("--write-file", "docs/report.md", code=2)
        self.finish_claim(self.root, writer)
        scoped = self.enter("--write-file", "docs/report.md")
        self.enter(mode="writer", code=2)
        for receipt in (reader, another_reader, scoped):
            self.finish_claim(self.root, receipt)

    def test_atomic_same_file_admission_and_independent_files(self):
        for same_target in (True, False):
            processes = [subprocess.Popen(
                [sys.executable, "-B", str(self.access(self.root)), "enter", "--mode", "scoped-writer",
                 "--actor", f"worker-{index}", "--write-file", f"docs/r-{0 if same_target else index}.md"],
                stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True) for index in range(12)]
            results = []
            for process in processes:
                stdout, stderr = process.communicate(timeout=20)
                results.append((process.returncode, stdout, stderr))
            winners = [json.loads(out) for code, out, _ in results if code == 0]
            self.assertEqual(len(winners), 1 if same_target else 12, results)
            self.assertEqual(sum(code == 2 for code, _, _ in results), 11 if same_target else 0)
            for receipt in winners:
                self.finish_claim(self.root, receipt)

    @unittest.skipIf(os.name == "nt", "real symlink/hardlink probe is Unix-specific")
    def test_linked_targets_and_post_admission_link_replacement_are_rejected(self):
        link = self.root / "docs/alias"
        link.symlink_to(self.root / "memory", target_is_directory=True)
        self.enter("--write-file", "docs/alias/a.md", code=3)
        original = self.root / "docs/original.md"
        original.write_text("keep")
        os.link(original, self.root / "docs/hardlink.md")
        self.enter("--write-file", "docs/hardlink.md", code=3)
        claim = self.enter("--write-file", "docs/new.md")
        (self.root / "docs/new.md").symlink_to(original)
        checked = self.command("check", "--session", claim["session_id"], "--token", claim["token"])
        self.assertEqual(checked.returncode, 3)
        self.finish_claim(self.root, claim)
        self.assertEqual(original.read_text(), "keep")

    def test_protocol_migration_preserves_live_claim_history_and_recovery_plan(self):
        self.install_v1_fixture()
        finished = self.enter(mode="writer")
        self.finish_claim(self.root, finished)
        live = self.enter(mode="writer")
        recovery = self.command("recover", "--session", live["session_id"], "--reason", "fixture")
        self.assertEqual(recovery.returncode, 0, recovery.stderr)
        database = self.root / ".project-conventions/runtime/access.sqlite3"
        with closing(sqlite3.connect(database)) as connection:
            old_claim = connection.execute("SELECT * FROM claims").fetchall()
            old_history = connection.execute("SELECT * FROM history").fetchall()
            old_recovery = connection.execute("SELECT * FROM recovery_plans").fetchall()
        connection = access.connect(database)
        try:
            self.assertEqual(connection.execute("SELECT * FROM claims").fetchall(), old_claim)
            self.assertEqual(connection.execute("SELECT * FROM history").fetchall(), old_history)
            self.assertEqual(connection.execute("SELECT * FROM recovery_plans").fetchall(), old_recovery)
            self.assertEqual(connection.execute("PRAGMA integrity_check").fetchone()[0], "ok")
        finally:
            connection.close()
        self.assertEqual(self.command("status").returncode, 3)  # old helper fails closed
        access.finish(self.root, database, live["session_id"], live["token"], "success")

    def test_upgrade_dry_run_apply_history_preservation_and_idempotence(self):
        self.install_v1_fixture()
        old = self.enter(mode="writer")
        self.finish_claim(self.root, old)
        business = self.root / "src/user.txt"
        business.write_text("keep user source\n")
        agents = self.root / "AGENTS.md"
        agents.write_text(agents.read_text() + "\nCustom project instruction: preserve this.\n")
        proposal, before, _ = upgrade.plan(self.root)
        database = self.root / ".project-conventions/runtime/access.sqlite3"
        db_before = database.read_bytes()
        self.assertEqual(upgrade.database_version(database), "1")
        upgrade.plan(self.root)
        self.assertEqual(database.read_bytes(), db_before)
        self.assertEqual({p: (self.root / p).read_bytes() for p in upgrade.FILES}, before)
        result = upgrade.apply(self.root, proposal["plan_sha256"])
        self.assertEqual(result["status"], "upgraded")
        self.assertEqual(result["database_protocol"], "2")
        self.assertFalse((Path(result["backup"]) / "claim.json").exists())
        self.assertIn("Custom project instruction: preserve this.", agents.read_text())
        self.assertEqual(business.read_text(), "keep user source\n")
        with closing(sqlite3.connect(database)) as connection:
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM history WHERE session_id = ?", (old["session_id"],)).fetchone()[0], 1)
            self.assertEqual(connection.execute("SELECT COUNT(*) FROM claims").fetchone()[0], 0)
        self.assertEqual(upgrade.plan(self.root)[0]["status"], "already_current")
        self.enter("--write-file", "docs/a.md")
        self.enter("--write-file", "docs/b.md")

    def test_upgrade_refuses_stale_plan_and_active_writer_without_changing_files(self):
        self.install_v1_fixture()
        proposal, before, _ = upgrade.plan(self.root)
        writer = self.enter(mode="writer")
        with self.assertRaises(upgrade.UpgradeError):
            upgrade.apply(self.root, proposal["plan_sha256"])
        self.assertEqual({p: (self.root / p).read_bytes() for p in upgrade.FILES}, before)
        self.finish_claim(self.root, writer)
        agents = self.root / "AGENTS.md"
        agents.write_text(agents.read_text() + "\nNew user edit\n")
        with self.assertRaisesRegex(upgrade.UpgradeError, "plan changed"):
            upgrade.apply(self.root, proposal["plan_sha256"])

    def test_upgrade_rolls_back_its_files_on_mid_apply_failure(self):
        self.install_v1_fixture()
        proposal, before, _ = upgrade.plan(self.root)
        original = upgrade.replace_owned
        calls = 0

        def fail_second(path, expected, content):
            nonlocal calls
            calls += 1
            if calls == 2:
                raise OSError("injected failure")
            return original(path, expected, content)

        with mock.patch.object(upgrade, "replace_owned", side_effect=fail_second):
            with self.assertRaisesRegex(upgrade.UpgradeError, "rolled back"):
                upgrade.apply(self.root, proposal["plan_sha256"])
        self.assertEqual({p: (self.root / p).read_bytes() for p in upgrade.FILES}, before)
        status = self.command("status")
        self.assertEqual(status.returncode, 0, status.stderr)
        self.assertEqual(json.loads(status.stdout)["claims"], [])

    def test_physical_paths_distinguish_worktrees_and_shared_wrapper_reports(self):
        isolated_a = {"mode": "isolated-writer", "workspace": "/fixture/wt-a", "write_paths": ["src/a"]}
        isolated_b = dict(isolated_a, workspace="/fixture/wt-b")
        scoped = {"mode": "scoped-writer", "workspace": "/fixture", "write_paths": ["wt-a/report.md"]}
        self.assertFalse(access.claims_conflict(isolated_a, isolated_b))
        self.assertTrue(access.claims_conflict(isolated_a, scoped))
        self.assertTrue(access.claims_conflict(scoped, isolated_a))
        self.assertFalse(access.claims_conflict(isolated_b, scoped))

    @unittest.skipUnless(shutil.which("git"), "git is required")
    def test_real_worktrees_edit_and_commit_the_same_file_independently(self):
        repository = self.root.parent / "repository"
        repository.mkdir()

        def git(*args, cwd=repository):
            result = self.run_command(["git", *args], cwd=cwd)
            self.assertEqual(result.returncode, 0, result.stderr)
            return result.stdout.strip()

        def commit(worktree, message):
            git("add", ".", cwd=worktree)
            git("-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "-m", message, cwd=worktree)

        git("init", "-b", "main")
        self.initialize(repository, mode="adopt-existing")
        (repository / "src/shared.py").write_text("original\n")
        commit(repository, "initial")
        tasks = []
        for name in ("a", "b"):
            worktree = self.root.parent / ("worktree-" + name)
            git("worktree", "add", "-b", "task-" + name, str(worktree), "HEAD")
            result = self.run_command([sys.executable, "-B", str(self.access(worktree)), "enter", "--mode",
                                       "isolated-writer", "--actor", name, "--write-path", "src/shared.py"])
            self.assertEqual(result.returncode, 0, result.stderr)
            tasks.append((worktree, json.loads(result.stdout), name))
        for worktree, receipt, name in tasks:
            (worktree / "src/shared.py").write_text(name + "\n")
            commit(worktree, name)
            check = self.run_command([sys.executable, "-B", str(self.access(worktree)), "check", "--session",
                                      receipt["session_id"], "--token", receipt["token"]])
            self.assertEqual(check.returncode, 0, check.stderr)
            self.finish_claim(worktree, receipt)
        self.assertEqual((repository / "src/shared.py").read_text(), "original\n")
        self.assertEqual(git("show", "task-a:src/shared.py"), "a")
        self.assertEqual(git("show", "task-b:src/shared.py"), "b")

    def test_upgrade_preserves_concurrent_foreign_replacement_on_rollback(self):
        self.install_v1_fixture()
        proposal, before, _ = upgrade.plan(self.root)
        original = upgrade.replace_owned
        calls = 0
        foreign = b"Concurrent user replacement\n"

        def replace_then_collide(path, expected, content):
            nonlocal calls
            calls += 1
            if calls == 2:
                (self.root / "AGENTS.md").write_bytes(foreign)
                raise OSError("concurrent replacement")
            return original(path, expected, content)

        # Force AGENTS into this plan, as it would be with actual v1 wording.
        agents = self.root / "AGENTS.md"
        agents.write_text(agents.read_text() + "\n" + next(iter(upgrade.LEGACY_LINES)) + "\n")
        proposal, before, _ = upgrade.plan(self.root)
        with mock.patch.object(upgrade, "replace_owned", side_effect=replace_then_collide):
            with self.assertRaisesRegex(upgrade.UpgradeError, "preserved=.*AGENTS.md"):
                upgrade.apply(self.root, proposal["plan_sha256"])
        self.assertEqual(agents.read_bytes(), foreign)
        for name in upgrade.FILES[1:]:
            self.assertEqual((self.root / name).read_bytes(), before[name])


if __name__ == "__main__":
    unittest.main()
