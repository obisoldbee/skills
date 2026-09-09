#!/usr/bin/env python3
"""Run the real platform link entry point only against disposable directories."""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

import consumer_paths as consumers


SOURCE = Path(__file__).resolve().parents[1]
WINDOWS = os.name == "nt"


class ConsumerBoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="skills-consumer-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.collection = self.root / "collection"
        self.repo = self.collection / "GitHub"
        self.make_repository(self.repo)
        (self.collection / "AGENTS.md").write_text(
            "# Project Collection\nGitHub/ is the Repository Root for obisoldbee/skills.\n",
            encoding="utf-8",
        )
        self.control = self.collection / "skills"
        self.projections = self.control / "src"
        self.projections.mkdir(parents=True)
        (self.control / "AGENTS.md").write_text("collection-control Project Root\n", encoding="utf-8")
        for name in ("AGENTS.md", "README.md", "config", "scripts"):
            destination = self.projections / name
            target = self.repo / name
            if target.is_dir():
                self.link_directory(destination, target)
            else:
                os.symlink(target, destination)
        self.member = self.collection / "member" / "src"
        self.member.mkdir(parents=True)
        self.external = self.root / "external-skills"
        self.external.mkdir()
        self.initial_projections = self.projection_snapshot()

    def make_repository(self, root):
        (root / "scripts").mkdir(parents=True)
        (root / "config").mkdir()
        (root / "example-skill").mkdir()
        (root / "example-skill/SKILL.md").write_text("fixture\n", encoding="utf-8")
        (root / "AGENTS.md").write_text("repository root\n", encoding="utf-8")
        (root / "README.md").write_text("repository\n", encoding="utf-8")
        for name in ("link-macos.sh", "link-windows.ps1", "verify_release.py", "consumer_paths.py", "windows_junction.py"):
            shutil.copyfile(SOURCE / "scripts" / name, root / "scripts" / name)
        (root / "config/skill-exports.tsv").write_text(
            "skill_name\tsource\tconsumers\nexample-skill\texample-skill\tall\n", encoding="utf-8"
        )
        (root / "config/agent-paths.tsv").write_text("platform\tagent\tpath\n", encoding="utf-8")

    def powershell(self, script, env):
        return subprocess.run(
            ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-Command", script],
            env=env, capture_output=True, text=True, check=False,
        )

    def link_directory(self, destination, target):
        if WINDOWS:
            env = dict(os.environ, FIXTURE_LINK=str(destination), FIXTURE_TARGET=str(target))
            result = self.powershell(
                "$ErrorActionPreference = 'Stop'; New-Item -ItemType Junction -Path $env:FIXTURE_LINK -Target $env:FIXTURE_TARGET | Out-Null",
                env,
            )
            self.assertEqual(result.returncode, 0, result.stderr)
        else:
            os.symlink(target, destination, target_is_directory=True)

    def projection_snapshot(self):
        return {
            path.name: (os.lstat(path).st_mode, str(path.resolve()), path.lstat().st_mtime_ns)
            for path in self.projections.iterdir()
        }

    def invoke(self, target, *, apply=False, repo=None, projected=False, env=None):
        repo = repo or self.repo
        scripts = self.projections if projected else repo
        script = scripts / "scripts" / ("link-windows.ps1" if WINDOWS else "link-macos.sh")
        if WINDOWS:
            command = ["powershell.exe", "-NoProfile", "-ExecutionPolicy", "Bypass", "-File", str(script), "-Target", str(target), "-Skill", "example-skill"]
            if apply:
                command.append("-Apply")
        else:
            command = ["bash", str(script), "--target", str(target), "--skill", "example-skill"]
            if apply:
                command.append("--apply")
        environment = dict(os.environ, PYTHON=sys.executable, PYTHONDONTWRITEBYTECODE="1")
        if env:
            environment.update(env)
        return subprocess.run(command, env=environment, capture_output=True, text=True, check=False)

    def assert_rejected(self, target, *, reason="target-inside-collection"):
        for apply in (False, True):
            with self.subTest(target=str(target), apply=apply):
                result = self.invoke(target, apply=apply)
                output = result.stdout + result.stderr
                self.assertNotEqual(result.returncode, 0, output)
                self.assertIn(reason, output)
                self.assertNotIn("would-link", output)
                self.assertFalse(os.path.lexists(Path(target) / "example-skill"))
                self.assertEqual(self.projection_snapshot(), self.initial_projections)

    def test_collection_root_control_member_and_repository_rejected(self):
        for target in (self.collection, self.projections, self.member, self.repo / "config"):
            self.assert_rejected(target)

    def test_external_alias_to_internal_and_alias_ancestor_rejected(self):
        alias = self.root / "outside-alias"
        self.link_directory(alias, self.collection)
        for target in (alias, alias / "skills/src", alias / "member/src"):
            self.assert_rejected(target)
        direct_alias = self.root / "control-alias"
        self.link_directory(direct_alias, self.projections)
        self.assert_rejected(direct_alias)

    def test_internal_alias_to_external_is_still_not_a_consumer(self):
        alias = self.collection / "outward-alias"
        self.link_directory(alias, self.external)
        self.assert_rejected(alias)

    def test_actual_filesystem_case_aliases_rejected(self):
        # Run on macOS too; OS-name checks missed the original APFS failure.
        alias_path = self.root / "COLLECTION"
        if not alias_path.exists():
            self.skipTest("fixture filesystem is case-sensitive")
        self.assertTrue(alias_path.samefile(self.collection))
        self.assert_rejected(alias_path / "skills/src")
        alias = self.root / "case-alias"
        self.link_directory(alias, self.collection)
        self.assert_rejected(self.root / "CASE-ALIAS" / "skills/src")

    def test_lowercase_repository_entry_keeps_collection_boundary(self):
        alias_repo = self.collection / "github"
        if not alias_repo.exists():
            self.skipTest("fixture filesystem is case-sensitive")
        self.assertTrue(alias_repo.samefile(self.repo))
        for apply in (False, True):
            result = self.invoke(self.projections, repo=alias_repo, apply=apply)
            self.assertNotEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("target-inside-collection", result.stdout + result.stderr)
        self.assertEqual(self.projection_snapshot(), self.initial_projections)

    def test_case_sensitive_distinct_sibling_remains_external(self):
        target = self.root / "COLLECTION"
        if target.exists():
            self.skipTest("fixture filesystem is case-insensitive")
        target.mkdir()
        result = self.invoke(target)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("would-link", result.stdout)
        self.install_and_verify(target)

    def install_and_verify(self, target, **options):
        result = self.invoke(target, apply=True, **options)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("linked ", result.stdout)

    def test_external_consumer_and_projected_entry_are_healthy(self):
        result = self.invoke(self.external, projected=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("would-link", result.stdout)
        self.install_and_verify(self.external, projected=True)
        result = self.invoke(self.external, projected=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertIn("healthy-link", result.stdout)
        if not WINDOWS:
            result = self.invoke(self.external, apply=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((self.external / "example-skill").resolve(), self.repo / "example-skill")
        self.assertEqual(self.projection_snapshot(), self.initial_projections)

    def test_external_alias_to_external_is_allowed(self):
        alias = self.root / "external-alias"
        self.link_directory(alias, self.external)
        result = self.invoke(alias)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.install_and_verify(alias)
        if not WINDOWS:
            self.assertEqual((self.external / "example-skill").resolve(), self.repo / "example-skill")

    def test_standalone_parent_is_not_inferred_to_be_collection(self):
        # Even the conventional checkout name alone is insufficient evidence.
        repo = self.root / "standalone" / "GitHub"
        self.make_repository(repo)
        target = repo.parent / "consumer"
        target.mkdir()
        result = self.invoke(target, repo=repo)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.install_and_verify(target, repo=repo)
        result = self.invoke(repo / "config", repo=repo)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("target-inside-repository", result.stdout + result.stderr)

    def test_prefix_sibling_is_not_inside_collection(self):
        target = self.root / "collection-neighbor"
        target.mkdir()
        result = self.invoke(target)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.install_and_verify(target)

    def test_existing_conflict_and_missing_parent_remain_unchanged(self):
        conflict = self.external / "example-skill"
        conflict.mkdir()
        keep = conflict / "keep"
        keep.write_text("user", encoding="utf-8")
        result = self.invoke(self.external)
        self.assertEqual(result.returncode, 4, result.stdout + result.stderr)
        result = self.invoke(self.external, apply=True)
        self.assertEqual(result.returncode, 4, result.stdout + result.stderr)
        self.assertEqual(keep.read_text(encoding="utf-8"), "user")
        missing = self.root / "missing"
        result = self.invoke(missing)
        self.assertEqual(result.returncode, 4)
        self.assertFalse(missing.exists())

    def test_target_replacement_at_apply_gate_is_rejected(self):
        token = consumers.inspect_target(self.repo, self.external)[1]
        self.external.rename(self.root / "saved-consumer")
        self.link_directory(self.external, self.projections)
        with self.assertRaisesRegex(ValueError, "target-inside-collection"):
            consumers.create_link(self.repo, self.external, "example-skill", self.repo / "example-skill", token)
        self.assertFalse(os.path.lexists(self.projections / "example-skill"))
        self.assertFalse(os.path.lexists(self.root / "saved-consumer/example-skill"))
        self.assertEqual(self.projection_snapshot(), self.initial_projections)

    @unittest.skipIf(WINDOWS, "Unix primitive availability")
    def test_missing_safe_primitive_stops_before_create_but_keeps_scan(self):
        token = consumers.inspect_target(self.repo, self.external)[1]
        with patch.object(os, "supports_dir_fd", set()):
            with self.assertRaisesRegex(ValueError, "safe-consumer-create-unsupported"):
                consumers.create_link(self.repo, self.external, "example-skill", self.repo / "example-skill", token)
            self.assertEqual(consumers.inspect_target(self.repo, self.external)[1], token)
        self.assertEqual(list(self.external.iterdir()), [])
        self.assertEqual(self.projection_snapshot(), self.initial_projections)

    def test_different_external_parent_cannot_reuse_scan_identity(self):
        token = consumers.inspect_target(self.repo, self.external)[1]
        saved = self.root / "saved-consumer"
        self.external.rename(saved)
        self.external.mkdir()
        with self.assertRaisesRegex(ValueError, "consumer-target-or-boundary-changed"):
            consumers.create_link(self.repo, self.external, "example-skill", self.repo / "example-skill", token)
        self.assertEqual(list(self.external.iterdir()), [])
        self.assertEqual(list(saved.iterdir()), [])

    @unittest.skipIf(WINDOWS, "Unix directory-fd syscall regressions")
    def test_last_syscall_leaf_and_parent_replacements_cannot_redirect_creation(self):
        consumers.require_safe_create()
        original_symlink = os.symlink
        for kind in ("leaf-directory", "leaf-link", "parent-link"):
            with self.subTest(kind=kind):
                target = self.root / kind
                target.mkdir()
                token = consumers.inspect_target(self.repo, target)[1]
                calls = []

                def inject_then_symlink(source, name, *, dir_fd):
                    calls.append(dir_fd)
                    if kind == "leaf-directory":
                        (target / name).mkdir()
                        (target / name / "user-file").write_text("keep", encoding="utf-8")
                    elif kind == "leaf-link":
                        original_symlink(self.projections, target / name)
                    else:
                        target.rename(self.root / "saved-parent")
                        original_symlink(self.projections, target)
                    return original_symlink(source, name, dir_fd=dir_fd)

                with patch.object(consumers.os, "symlink", side_effect=inject_then_symlink) as syscall:
                    with patch.object(os, "supports_dir_fd", os.supports_dir_fd | {syscall}):
                        with self.assertRaises((FileExistsError, ValueError)):
                            consumers.create_link(self.repo, target, "example-skill", self.repo / "example-skill", token)
                self.assertEqual(len(calls), 1, "must reach the real last-syscall race window")
                self.assertEqual(self.projection_snapshot(), self.initial_projections)
                if kind == "leaf-directory":
                    self.assertEqual((target / "example-skill/user-file").read_text(encoding="utf-8"), "keep")
                    self.assertEqual(len(list((target / "example-skill").iterdir())), 1)
                elif kind == "leaf-link":
                    self.assertEqual((target / "example-skill").resolve(), self.projections)
                else:
                    # The authorized link can remain in the pinned old parent;
                    # it must never enter the replacement path or claim success.
                    self.assertEqual((self.root / "saved-parent/example-skill").resolve(), self.repo / "example-skill")

    @unittest.skipUnless(WINDOWS, "Windows NT handle syscall regressions")
    def test_windows_final_syscall_replacements_cannot_redirect_creation(self):
        import windows_junction as junction
        original = junction.create_child
        for kind in ("leaf-directory", "leaf-link", "parent-link"):
            with self.subTest(kind=kind):
                target = self.root / kind
                target.mkdir()
                token = consumers.inspect_target(self.repo, target)[1]

                def inject(nt, parent, name):
                    if kind == "leaf-directory":
                        (target / name).mkdir()
                        (target / name / "keep").write_text("user", encoding="utf-8")
                    elif kind == "leaf-link":
                        self.link_directory(target / name, self.projections)
                    else:
                        target.rename(self.root / "saved-parent")
                        self.link_directory(target, self.projections)
                    return original(nt, parent, name)

                with patch.object(junction, "create_child", side_effect=inject) as syscall:
                    with self.assertRaises((OSError, ValueError)):
                        consumers.create_link(self.repo, target, "example-skill", self.repo / "example-skill", token)
                self.assertEqual(syscall.call_count, 1)
                self.assertFalse(os.path.lexists(self.projections / "example-skill"))
                self.assertEqual(self.projection_snapshot(), self.initial_projections)
                if kind == "leaf-directory":
                    self.assertEqual((target / "example-skill/keep").read_text(), "user")
                elif kind == "leaf-link":
                    self.assertEqual((target / "example-skill").resolve(), self.projections)

    @unittest.skipUnless(WINDOWS, "Windows combined refresh boundary")
    def test_windows_sync_apply_stops_before_repository_or_consumer_writes(self):
        result = self.powershell(
            "& $env:FIXTURE_SCRIPT -SyncDevice -Apply -Agent codex",
            dict(os.environ, FIXTURE_SCRIPT=str(self.repo / "scripts/link-windows.ps1")),
        )
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("safe-consumer-create-unsupported", result.stdout + result.stderr)
        self.assertNotIn("operation=repository-device-refresh", result.stdout)
        self.assertEqual(list(self.external.iterdir()), [])
        self.assertEqual(self.projection_snapshot(), self.initial_projections)


if __name__ == "__main__":
    unittest.main(verbosity=2)
