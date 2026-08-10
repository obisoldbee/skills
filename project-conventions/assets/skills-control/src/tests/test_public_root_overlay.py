#!/usr/bin/env python3
"""Portable deterministic checks for an initialized Skills control project."""

from __future__ import annotations

import hashlib
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


CONTROL_ROOT = Path(__file__).resolve().parents[2]
BUILDER = CONTROL_ROOT / "src" / "scripts" / "build_public_root_overlay.py"
SHARED_REPOSITORY_ROOT = CONTROL_ROOT.parent / "GitHub"
ROOT_MANIFEST = "ROOT-MANIFEST.sha256"
ROOT_MANAGED_ENTRIES = {
    ".gitattributes",
    ".github",
    ".gitignore",
    "AGENTS.md",
    "README.md",
    "config",
    "scripts",
}


class PublicRootOverlayTests(unittest.TestCase):
    def create_directory_link(self, link: Path, target: Path) -> None:
        if os.name == "nt":
            result = subprocess.run(
                ["cmd", "/d", "/c", "mklink", "/J", str(link), str(target)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        else:
            link.symlink_to(target, target_is_directory=True)

    def copied_builder(self, base: Path) -> tuple[Path, Path]:
        control = base / "collection" / "skills"
        builder = control / "src" / "scripts" / "build_public_root_overlay.py"
        builder.parent.mkdir(parents=True)
        (control / "release").mkdir()
        shutil.copy2(BUILDER, builder)
        return control, builder

    def copied_valid_repository(self, base: Path) -> tuple[Path, Path, Path]:
        control, builder = self.copied_builder(base)
        repository = control.parent / "GitHub"

        def ignore(_directory: str, names: list[str]) -> set[str]:
            return {name for name in names if name in {".git", ".DS_Store", "__pycache__"}}

        shutil.copytree(SHARED_REPOSITORY_ROOT, repository, ignore=ignore)
        initialized = subprocess.run(
            ["git", "init", "-q", str(repository)],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(initialized.returncode, 0, initialized.stderr)
        remote = subprocess.run(
            [
                "git",
                "-C",
                str(repository),
                "remote",
                "add",
                "origin",
                "https://github.com/obisoldbee/skills.git",
            ],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(remote.returncode, 0, remote.stderr)
        return control, builder, repository

    def test_control_source_has_complete_portable_shape(self) -> None:
        expected = {"README.md", "config", "scripts", "tests"}
        self.assertEqual({path.name for path in (CONTROL_ROOT / "src").iterdir()}, expected)
        self.assertTrue((CONTROL_ROOT / "src" / "config" / "agent-paths.tsv").is_file())
        self.assertTrue((CONTROL_ROOT / "src" / "config" / "skill-exports.tsv").is_file())
        self.assertTrue(BUILDER.is_file())
        self.assertTrue((CONTROL_ROOT / "src" / "scripts" / "link-macos.sh").is_file())
        self.assertTrue((CONTROL_ROOT / "src" / "scripts" / "link-windows.ps1").is_file())

    def test_build_is_root_only_manifested_and_verifiable(self) -> None:
        with tempfile.TemporaryDirectory(dir=CONTROL_ROOT / "release") as raw:
            overlay = Path(raw) / "overlay"
            build = subprocess.run(
                [sys.executable, "-B", str(BUILDER), "--output", str(overlay)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(build.returncode, 0, build.stderr)
            self.assertEqual(
                {path.name for path in overlay.iterdir()},
                ROOT_MANAGED_ENTRIES | {ROOT_MANIFEST},
            )
            self.assertFalse((overlay / "project-conventions").exists())

            listed: dict[str, str] = {}
            for row in (overlay / ROOT_MANIFEST).read_text(encoding="utf-8").splitlines():
                digest, relative = row.split("  ", 1)
                listed[relative] = digest
            actual = {
                path.relative_to(overlay).as_posix(): hashlib.sha256(
                    path.read_bytes()
                ).hexdigest()
                for path in overlay.rglob("*")
                if path.is_file() and path.name != ROOT_MANIFEST
            }
            self.assertEqual(listed, actual)

            verify = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(overlay / "scripts" / "verify_release.py"),
                    str(overlay),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(verify.returncode, 0, verify.stderr)

    def test_link_tools_are_collection_scoped_and_apply_is_explicit(self) -> None:
        macos = (CONTROL_ROOT / "src" / "scripts" / "link-macos.sh").read_text(
            encoding="utf-8"
        )
        windows = (CONTROL_ROOT / "src" / "scripts" / "link-windows.ps1").read_text(
            encoding="utf-8"
        )
        self.assertIn('collection_root="$(cd "$script_dir/../../.."', macos)
        self.assertIn("choose-exactly-one-agent-target-or-all-agents", macos)
        self.assertIn("target-inside-project-collection", macos)
        self.assertIn('exit 4', macos)
        self.assertIn("$CollectionRoot", windows)
        self.assertIn("choose-exactly-one-agent-target-or-all-agents", windows)
        self.assertIn("target-inside-project-collection", windows)
        self.assertIn("exit 4", windows)

    def test_builder_reads_the_shared_checkout_not_a_control_copy(self) -> None:
        self.assertTrue(
            (SHARED_REPOSITORY_ROOT / "project-conventions" / "SKILL.md").is_file()
        )
        self.assertFalse((CONTROL_ROOT / "src" / "public-repo").exists())
        builder = BUILDER.read_text(encoding="utf-8")
        self.assertIn('CONTROL_ROOT.parent / "GitHub"', builder)

    def test_builder_rejects_non_git_or_wrong_remote_shared_root(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            control, builder = self.copied_builder(base)
            repository = control.parent / "GitHub"
            repository.mkdir()
            snapshot = subprocess.run(
                [sys.executable, "-B", str(builder)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(snapshot.returncode, 2)
            self.assertIn("Git verification failed", snapshot.stderr)

            git_init = subprocess.run(
                ["git", "init", "-q", str(repository)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(git_init.returncode, 0, git_init.stderr)
            remote = subprocess.run(
                [
                    "git",
                    "-C",
                    str(repository),
                    "remote",
                    "add",
                    "origin",
                    "https://github.com/example/wrong.git",
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(remote.returncode, 0, remote.stderr)
            wrong_remote = subprocess.run(
                [sys.executable, "-B", str(builder)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(wrong_remote.returncode, 2)
            self.assertIn("remote differs", wrong_remote.stderr)

    def test_builder_rejects_linked_shared_root(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            control, builder = self.copied_builder(base)
            repository = control.parent / "GitHub"
            outside = base / "outside-repository"
            outside.mkdir()
            if os.name == "nt":
                link = subprocess.run(
                    ["cmd", "/d", "/c", "mklink", "/J", str(repository), str(outside)],
                    check=False,
                    capture_output=True,
                    text=True,
                )
                self.assertEqual(link.returncode, 0, link.stderr or link.stdout)
            else:
                repository.symlink_to(outside, target_is_directory=True)
            result = subprocess.run(
                [sys.executable, "-B", str(builder)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("missing or linked", result.stderr)

    def test_builder_rejects_output_parent_traversal(self) -> None:
        escaped = CONTROL_ROOT / "escaped-overlay-regression"
        self.assertFalse(escaped.exists())
        traversal = (
            CONTROL_ROOT
            / "release"
            / "stage"
            / ".."
            / ".."
            / escaped.name
        )
        result = subprocess.run(
            [sys.executable, "-B", str(BUILDER), "--output", str(traversal)],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 2)
        self.assertIn("parent traversal", result.stderr)
        self.assertFalse(escaped.exists())

    def test_builder_rejects_extra_root_file_and_empty_directory(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            _control, builder, repository = self.copied_valid_repository(Path(raw))
            (repository / "scripts" / "unlisted-root-helper.py").write_text(
                "fixture\n", encoding="utf-8"
            )
            (repository / "scripts" / "empty-extra-directory").mkdir()
            result = subprocess.run(
                [sys.executable, "-B", str(builder)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("extra-root-files", result.stderr)
            self.assertIn("extra-root-directories", result.stderr)

    def test_builder_does_not_follow_nested_directory_links(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            control, builder, repository = self.copied_valid_repository(base)
            outside = base / "outside"
            outside.mkdir()
            (outside / "outside-secret.md").write_text(
                "/" + "Users" + "/example/private\n", encoding="utf-8"
            )
            nested = repository / "scripts" / "nested-link"
            self.create_directory_link(nested, outside)
            output = control / "release" / "nested-link-regression"
            result = subprocess.run(
                [sys.executable, "-B", str(builder), "--output", str(output)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("nested-link:link-or-junction", result.stderr)
            self.assertNotIn("outside-secret.md", result.stderr)
            self.assertFalse(output.exists())

    def test_verifier_rejects_personal_windows_path(self) -> None:
        with tempfile.TemporaryDirectory(dir=CONTROL_ROOT / "release") as raw:
            overlay = Path(raw) / "overlay"
            build = subprocess.run(
                [sys.executable, "-B", str(BUILDER), "--output", str(overlay)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(build.returncode, 0, build.stderr)
            readme = overlay / "README.md"
            marker = "C:" + "\\Users\\" + "example\\private"
            readme.write_text(
                readme.read_text(encoding="utf-8") + "\n" + marker + "\n",
                encoding="utf-8",
            )
            verify = subprocess.run(
                [
                    sys.executable,
                    "-B",
                    str(overlay / "scripts" / "verify_release.py"),
                    str(overlay),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(verify.returncode, 1)
            self.assertIn("personal-windows-path", verify.stderr)


if __name__ == "__main__":
    os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    unittest.main()
