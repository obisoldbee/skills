#!/usr/bin/env python3
"""Run the real platform link entry point only against disposable directories."""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest


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
        for name in ("link-macos.sh", "link-windows.ps1", "verify_release.py"):
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
        return subprocess.run(command, env=env, capture_output=True, text=True, check=False)

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

    @unittest.skipUnless(WINDOWS, "Windows case-insensitive path behavior")
    def test_windows_case_variants_and_junctions_rejected(self):
        self.assert_rejected(str(self.projections).upper())
        alias = self.root / "case-alias"
        self.link_directory(alias, self.collection)
        self.assert_rejected(str(alias / "skills/src").upper())

    def test_external_consumer_and_projected_entry_are_healthy(self):
        for apply in (False, True, False):
            result = self.invoke(self.external, apply=apply, projected=True)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
            self.assertIn("linked " if apply else ("healthy-link" if (self.external / "example-skill").exists() else "would-link"), result.stdout)
        self.assertEqual((self.external / "example-skill").resolve(), self.repo / "example-skill")
        self.assertEqual(self.projection_snapshot(), self.initial_projections)

    def test_external_alias_to_external_is_allowed(self):
        alias = self.root / "external-alias"
        self.link_directory(alias, self.external)
        result = self.invoke(alias, apply=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        self.assertEqual((self.external / "example-skill").resolve(), self.repo / "example-skill")

    def test_standalone_parent_is_not_inferred_to_be_collection(self):
        # Even the conventional checkout name alone is insufficient evidence.
        repo = self.root / "standalone" / "GitHub"
        self.make_repository(repo)
        target = repo.parent / "consumer"
        target.mkdir()
        for apply in (False, True):
            result = self.invoke(target, repo=repo, apply=apply)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        result = self.invoke(repo / "config", repo=repo)
        self.assertNotEqual(result.returncode, 0)
        self.assertIn("target-inside-repository", result.stdout + result.stderr)

    def test_prefix_sibling_is_not_inside_collection(self):
        target = self.root / "collection-neighbor"
        target.mkdir()
        result = self.invoke(target, apply=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_existing_conflict_and_missing_parent_remain_unchanged(self):
        conflict = self.external / "example-skill"
        conflict.mkdir()
        keep = conflict / "keep"
        keep.write_text("user", encoding="utf-8")
        result = self.invoke(self.external, apply=True)
        self.assertEqual(result.returncode, 4, result.stdout + result.stderr)
        self.assertEqual(keep.read_text(encoding="utf-8"), "user")
        missing = self.root / "missing"
        result = self.invoke(missing, apply=True)
        self.assertEqual(result.returncode, 4)
        self.assertFalse(missing.exists())

    def test_target_replacement_at_apply_gate_is_rejected(self):
        # Interpose only the metadata reader to deterministically place a real
        # filesystem change between scan and apply. Production has no test hook.
        env = dict(
            os.environ, FIXTURE_TARGET=str(self.external),
            FIXTURE_SAVED=str(self.root / "saved-consumer"),
            FIXTURE_INTERNAL=str(self.projections),
            FIXTURE_SCRIPT=str(self.repo / "scripts/link-windows.ps1"),
        )
        if WINDOWS:
            harness = r"""
$ErrorActionPreference = 'Stop'
$global:FixtureReads = 0
function Get-Content([string]$LiteralPath, [switch]$Raw) {
    $global:FixtureReads++
    if ($global:FixtureReads -eq 3) {
        Move-Item -LiteralPath $env:FIXTURE_TARGET -Destination $env:FIXTURE_SAVED
        New-Item -ItemType Junction -Path $env:FIXTURE_TARGET -Target $env:FIXTURE_INTERNAL | Out-Null
    }
    Microsoft.PowerShell.Management\Get-Content -LiteralPath $LiteralPath -Raw
}
& $env:FIXTURE_SCRIPT -Target $env:FIXTURE_TARGET -Skill example-skill -Apply
"""
            result = self.powershell(harness, env)
        else:
            tools = self.root / "tools"
            tools.mkdir()
            wrapper = tools / "grep"
            wrapper.write_text(
                "#!/usr/bin/env bash\nset -eu\n"
                'n=0\n[ ! -f "$FIXTURE_COUNT" ] || n="$(< "$FIXTURE_COUNT")"\n'
                'n=$((n + 1))\nprintf "%s\\n" "$n" > "$FIXTURE_COUNT"\n'
                'if [ "$n" -eq 4 ]; then\n'
                '  mv "$FIXTURE_TARGET" "$FIXTURE_SAVED"\n'
                '  ln -s "$FIXTURE_INTERNAL" "$FIXTURE_TARGET"\nfi\n'
                'exec "$FIXTURE_GREP" "$@"\n', encoding="utf-8",
            )
            wrapper.chmod(0o755)
            env.update(FIXTURE_COUNT=str(self.root / "reads"), FIXTURE_GREP=shutil.which("grep"), PATH=str(tools) + os.pathsep + os.environ["PATH"])
            result = self.invoke(self.external, apply=True, env=env)
        output = result.stdout + result.stderr
        self.assertNotEqual(result.returncode, 0, output)
        self.assertIn("target-inside-collection", output)
        self.assertFalse(os.path.lexists(self.projections / "example-skill"))
        self.assertFalse(os.path.lexists(self.root / "saved-consumer/example-skill"))
        self.assertEqual(self.projection_snapshot(), self.initial_projections)


if __name__ == "__main__":
    unittest.main(verbosity=2)
