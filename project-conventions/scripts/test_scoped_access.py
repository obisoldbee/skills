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

    def test_schema_open_retries_only_transient_sqlite_lock(self):
        busy = sqlite3.OperationalError("database is locked")
        busy.sqlite_errorcode = sqlite3.SQLITE_BUSY
        sentinel = object()
        with mock.patch.object(access, "_connect_once", side_effect=[busy, sentinel]) as opening:
            with mock.patch.object(access.time, "sleep"):
                self.assertIs(access.connect(self.root / "test.sqlite3"), sentinel)
        self.assertEqual(opening.call_count, 2)
        corrupt = sqlite3.OperationalError("file is not a database")
        corrupt.sqlite_errorcode = sqlite3.SQLITE_NOTADB
        with mock.patch.object(access, "_connect_once", side_effect=corrupt) as opening:
            with self.assertRaises(sqlite3.OperationalError):
                access.connect(self.root / "test.sqlite3")
        self.assertEqual(opening.call_count, 1)

    def test_schema_retry_has_a_deadline(self):
        busy = sqlite3.OperationalError("database is locked")
        busy.sqlite_errorcode = sqlite3.SQLITE_LOCKED
        with mock.patch.object(access, "_connect_once", side_effect=busy) as opening:
            with mock.patch.object(access.time, "monotonic", side_effect=[0.0, 6.0]):
                with self.assertRaises(sqlite3.OperationalError):
                    access.connect(self.root / "test.sqlite3")
        self.assertEqual(opening.call_count, 1)

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
        content = helper.read_text().replace("PROTOCOL_VERSION = 3", "PROTOCOL_VERSION = 1")
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
        self.assertEqual(result["database_protocol"], "3")
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
        writer = {"mode": "writer", "workspace": "/fixture/wt-a", "write_paths": []}
        self.assertTrue(access.claims_conflict(writer, isolated_a))
        self.assertTrue(access.claims_conflict(writer, scoped))
        self.assertFalse(access.claims_conflict(writer, isolated_b))
        self.assertFalse(access.claims_conflict(isolated_b, writer))
        self.assertTrue(access.claims_conflict(writer, dict(writer, workspace="/fixture/wt-a/nested")))
        maintenance = dict(writer, evidence={"registry_maintenance": True})
        self.assertTrue(access.claims_conflict(maintenance, isolated_b))
        self.assertTrue(access.claims_conflict(isolated_b, maintenance))
        self.assertFalse(access.claims_conflict(maintenance, {"mode": "read-only"}))

    def test_scoped_command_releases_on_success_failure_and_start_error(self):
        for code in (0, 7):
            result = self.command("run", "--actor", "builder", "--write-dir", "out/test", "--",
                                  sys.executable, "-c", f"raise SystemExit({code})")
            self.assertEqual(result.returncode, code, result.stderr)
            self.assertTrue(json.loads(result.stdout)["claim_released"])
            self.assertEqual(json.loads(self.command("status").stdout)["claims"], [])
        failed = self.command("run", "--actor", "builder", "--write-dir", "out/test", "--",
                              str(self.root / "missing-executable"))
        self.assertEqual(failed.returncode, 3)
        self.assertEqual(json.loads(self.command("status").stdout)["claims"], [])

    def test_scoped_command_does_not_execute_when_output_is_owned(self):
        claim = self.enter("--write-dir", "out/test")
        marker = self.root / "should-not-exist"
        result = self.command("run", "--actor", "builder", "--write-dir", "out/test", "--",
                              sys.executable, "-c", "from pathlib import Path; Path('should-not-exist').touch()")
        self.assertEqual(result.returncode, 2)
        self.assertFalse(marker.exists())
        self.finish_claim(self.root, claim)

    def test_v2_metadata_upgrade_preserves_claims(self):
        receipt = self.enter(mode="writer")
        database = self.root / ".project-conventions/runtime/access.sqlite3"
        with closing(sqlite3.connect(database)) as connection:
            connection.execute("UPDATE meta SET value='2' WHERE key='protocol_version'")
            connection.commit()
            before = connection.execute("SELECT * FROM claims").fetchall()
        with closing(access.connect(database)) as connection:
            self.assertEqual(connection.execute("SELECT * FROM claims").fetchall(), before)
            self.assertEqual(connection.execute("SELECT value FROM meta WHERE key='protocol_version'").fetchone()[0], "3")
        self.finish_claim(self.root, receipt)

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
        canonical = self.run_command([sys.executable, "-B", str(self.access(repository)),
                                      "enter", "--mode", "writer", "--actor", "canonical"])
        self.assertEqual(canonical.returncode, 0, canonical.stderr)
        canonical_receipt = json.loads(canonical.stdout)
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
        self.finish_claim(repository, canonical_receipt)

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


class WorktreePolicyTests(unittest.TestCase):
    def setUp(self):
        temporary = tempfile.TemporaryDirectory()
        self.addCleanup(temporary.cleanup)
        self.base = Path(temporary.name)
        self.root = self.base / "project"

    def initialize(self, policy=None):
        command = [sys.executable, "-B", str(fixtures.INITIALIZER), str(self.root),
                   "--type", "code", "--mode", "fresh-empty", "--apply"]
        if policy:
            command += ["--coordination-policy", policy]
        result = subprocess.run(command, capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)

    def command(self, root, *args):
        result = subprocess.run([sys.executable, "-B", str(root / ".project-conventions/project_access.py"),
                                 *args], capture_output=True, text=True)
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def test_default_status_does_not_create_runtime_or_claim(self):
        self.initialize()
        result = self.command(self.root, "status")
        self.assertFalse(result["admission_required"])
        result = self.command(self.root, "enter", "--mode", "writer", "--actor", "old-prompt")
        self.assertEqual(result["status"], "not_required")
        self.assertNotIn("token", result)
        self.assertFalse((self.root / ".project-conventions/runtime").exists())

    def test_migration_preserves_abandoned_claim_and_database_bytes(self):
        import migrate_worktree_policy as migration
        self.initialize("legacy-claims")
        self.command(self.root, "enter", "--mode", "writer", "--actor", "abandoned")
        database = self.root / ".project-conventions/runtime" / access.DATABASE_FILE
        before = database.read_bytes()
        plan = migration.migrate(self.root)
        self.assertEqual(plan["status"], "would_upgrade")
        self.assertEqual(database.read_bytes(), before)
        result = migration.migrate(self.root, apply=True)
        self.assertEqual(result["status"], "migrated")
        self.assertEqual(database.read_bytes(), before)
        self.assertFalse(self.command(self.root, "status")["legacy_registry_consulted"])
        self.assertEqual(database.read_bytes(), before)
        self.assertEqual(migration.migrate(self.root, apply=True)["status"], "already_current")

    def test_copied_corrupt_registry_does_not_block_policy_switch(self):
        import migrate_worktree_policy as migration
        self.initialize("legacy-claims")
        copied = self.base / "external-copy"
        shutil.copytree(self.root, copied)
        runtime = copied / ".project-conventions/runtime"
        runtime.mkdir()
        database = runtime / access.DATABASE_FILE
        database.write_bytes(b"copied-unreadable-runtime")
        self.assertEqual(migration.migrate(copied, apply=True)["status"], "migrated")
        self.assertFalse(self.command(copied, "status")["admission_required"])
        self.assertEqual(database.read_bytes(), b"copied-unreadable-runtime")
        self.assertEqual(json.loads((self.root / ".project-conventions/project.json").read_text())["coordination_policy"], "legacy-claims")

    def test_pre_policy_config_and_generated_outside_rules_migrate(self):
        import migrate_worktree_policy as migration
        self.initialize("legacy-claims")
        config_path = self.root / ".project-conventions/project.json"
        config = json.loads(config_path.read_text())
        del config["coordination_policy"]  # Real pre-policy configurations lack this field.
        config_path.write_text(json.dumps(config))
        agents = self.root / "AGENTS.md"
        agents.write_text(agents.read_text() + "\n" + upgrade.LEGACY_RECORD_LINE + "\n"
                         "- This member's local helper stores claims in `../skills/.project-conventions/runtime`, "
                         "so one local `enter` automatically shares the collection-wide gate used by every member "
                         "and the control project. Do not bypass it by entering `../GitHub` directly.\n"
                         "- Preserve this custom rule.\n")
        migration.migrate(self.root, apply=True)
        updated = agents.read_text()
        self.assertNotIn("collection-wide gate", updated)
        self.assertNotIn(upgrade.LEGACY_RECORD_LINE, updated)
        self.assertIn("- Preserve this custom rule.", updated)
        self.assertFalse(self.command(self.root, "status")["admission_required"])

    def test_migration_rolls_back_owned_files_on_validation_failure(self):
        import migrate_worktree_policy as migration
        self.initialize("legacy-claims")
        before = {name: (self.root / name).read_bytes() for name in upgrade.FILES}
        original = migration.validator.validate
        def fail_new(root, *args, **kwargs):
            if json.loads((root / upgrade.FILES[3]).read_text())["coordination_policy"] == "worktree-first":
                raise ValueError("injected validation failure")
            return original(root, *args, **kwargs)
        with mock.patch.object(migration.validator, "validate", side_effect=fail_new):
            with self.assertRaisesRegex(upgrade.UpgradeError, "owned files rolled back"):
                migration.migrate(self.root, apply=True)
        for name, content in before.items():
            self.assertEqual((self.root / name).read_bytes(), content)

    def test_migration_os_lock_releases_after_process_death(self):
        import migrate_worktree_policy as migration
        self.initialize()
        script = ("from pathlib import Path; import sys; from migrate_worktree_policy import migration_lock\n"
                  "with migration_lock(Path(sys.argv[1])):\n"
                  " print('held', flush=True)\n"
                  " sys.stdin.read()\n")
        control = self.root / ".project-conventions"
        child = subprocess.Popen([sys.executable, "-B", "-c", script, str(control)],
                                 cwd=Path(__file__).parent, stdin=subprocess.PIPE,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        try:
            self.assertEqual(child.stdout.readline().strip(), "held")
            with self.assertRaises(OSError):
                with migration.migration_lock(control):
                    self.fail("second process acquired active migration lock")
        finally:
            child.terminate()
            child.communicate(timeout=10)
        with migration.migration_lock(control):
            pass  # The existing lock file is harmless after owner exit.

    def test_two_worktrees_edit_same_file_and_git_reports_merge_conflict(self):
        self.initialize()
        def git(root, *args, ok=True):
            result = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
            if ok:
                self.assertEqual(result.returncode, 0, result.stderr)
            return result
        git(self.root, "init")
        git(self.root, "config", "user.name", "Fixture")
        git(self.root, "config", "user.email", "fixture@example.invalid")
        (self.root / "app.txt").write_text("base\n")
        git(self.root, "add", ".")
        git(self.root, "commit", "-m", "baseline")
        for name in ("task-a", "task-b"):
            worktree = self.base / name
            git(self.root, "worktree", "add", "-b", name, str(worktree), "HEAD")
            (worktree / "app.txt").write_text(name + "\n")
            git(worktree, "add", "app.txt")
            git(worktree, "commit", "-m", name)
            self.assertFalse(self.command(worktree, "status")["admission_required"])
        self.assertEqual((self.root / "app.txt").read_text(), "base\n")
        git(self.root, "merge", "--ff-only", "task-a")
        conflict = git(self.root, "merge", "--no-edit", "task-b", ok=False)
        self.assertNotEqual(conflict.returncode, 0)
        self.assertIn("UU app.txt", git(self.root, "status", "--short").stdout)
        git(self.root, "merge", "--abort")
        self.assertEqual((self.base / "task-b/app.txt").read_text(), "task-b\n")


if __name__ == "__main__":
    unittest.main()
