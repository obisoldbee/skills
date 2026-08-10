#!/usr/bin/env python3
"""Portable deterministic checks for an initialized Skills control project."""

from __future__ import annotations

import hashlib
import os
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
