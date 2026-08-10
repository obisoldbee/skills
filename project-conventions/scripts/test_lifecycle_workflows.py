#!/usr/bin/env python3
"""Regression tests for lifecycle routing and the shared repository layout."""

from __future__ import annotations

import json
import os
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
DISTRIBUTION_ROOT = PACKAGE_ROOT.parent


class LifecycleWorkflowTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.skill = (PACKAGE_ROOT / "SKILL.md").read_text(encoding="utf-8")
        cls.lifecycle = (
            PACKAGE_ROOT / "references" / "lifecycle-workflows.md"
        ).read_text(encoding="utf-8")
        cls.shared = (
            PACKAGE_ROOT / "references" / "shared-repository.md"
        ).read_text(encoding="utf-8")
        cls.collection = (
            PACKAGE_ROOT / "references" / "project-collection.md"
        ).read_text(encoding="utf-8")
        cls.metadata = (PACKAGE_ROOT / "agents" / "openai.yaml").read_text(
            encoding="utf-8"
        )

    def run_command(
        self, command: list[str], cwd: Path | None = None
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            command,
            cwd=cwd,
            check=False,
            capture_output=True,
            text=True,
        )

    def git(self, cwd: Path, *arguments: str) -> str:
        result = self.run_command(["git", *arguments], cwd=cwd)
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    def copy_distribution(self, destination: Path) -> None:
        def ignore(_directory: str, names: list[str]) -> set[str]:
            ignored = {name for name in names if name in {".git", ".DS_Store", "__pycache__"}}
            ignored.update(name for name in names if name.endswith(".pyc"))
            return ignored

        shutil.copytree(DISTRIBUTION_ROOT, destination, ignore=ignore)
        rebuild = self.run_command(
            [
                sys.executable,
                "-B",
                str(destination / "scripts" / "verify_release.py"),
                str(destination),
                "--rebuild-root-manifest",
            ]
        )
        self.assertEqual(rebuild.returncode, 0, rebuild.stderr)

    def create_shared_fixture(
        self, base: Path
    ) -> tuple[Path, Path, Path]:
        collection = base / "obisoldbee-skills"
        collection.mkdir()
        checkout = collection / "GitHub"
        remote = base / "remote.git"
        self.copy_distribution(checkout)
        self.git(base, "init", "--bare", "--initial-branch=main", str(remote))
        self.git(checkout, "init", "--initial-branch=main")
        self.git(checkout, "config", "user.name", "Lifecycle Test")
        self.git(checkout, "config", "user.email", "lifecycle@example.invalid")
        self.git(checkout, "add", ".")
        self.git(checkout, "commit", "-m", "fixture distribution")
        self.git(checkout, "remote", "add", "origin", str(remote))
        self.git(checkout, "push", "-u", "origin", "main")
        self.git(
            checkout,
            "remote",
            "set-url",
            "origin",
            "https://github.com/obisoldbee/skills.git",
        )
        return collection, checkout, remote

    def create_update_fixture(
        self, base: Path
    ) -> tuple[Path, Path, Path]:
        remote = base / "remote.git"
        seed = base / "seed"
        collection = base / "collection"
        checkout = collection / "GitHub"
        self.copy_distribution(seed)
        self.git(base, "init", "--bare", "--initial-branch=main", str(remote))
        self.git(seed, "init", "--initial-branch=main")
        self.git(seed, "config", "user.name", "Update Test")
        self.git(seed, "config", "user.email", "update@example.invalid")
        self.git(seed, "add", ".")
        self.git(seed, "commit", "-m", "base")
        self.git(seed, "remote", "add", "origin", str(remote))
        self.git(seed, "push", "-u", "origin", "main")
        collection.mkdir()
        self.git(collection, "clone", str(remote), str(checkout))
        return seed, checkout, remote

    def test_contract_has_one_source_and_strict_update_boundary(self) -> None:
        combined = "\n".join(
            (self.skill, self.lifecycle, self.shared, self.collection, self.metadata)
        )
        for text in (
            "<collection>/GitHub",
            "GitHub/project-conventions",
            "initialize_skills_control_project.py",
            "update_shared_checkout.py",
            "repository_root",
            "managed_scope",
            "Every consumer must resolve directly",
        ):
            self.assertIn(text, combined)
        self.assertIn("Forbidden side effects in update-only", self.lifecycle)
        self.assertIn("never through the member projection", combined)
        self.assertNotIn("App" + "Data", combined)
        self.assertNotIn("src/skills/project-conventions", combined)

    def test_fresh_shared_collection_is_complete_and_idempotent(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            collection, checkout, _remote = self.create_shared_fixture(Path(raw))
            initializer = (
                checkout
                / "project-conventions"
                / "scripts"
                / "initialize_skills_control_project.py"
            )
            command = [
                sys.executable,
                "-B",
                str(initializer),
                str(collection),
                "--distribution-root",
                str(checkout),
            ]
            before_head = self.git(checkout, "rev-parse", "HEAD")
            dry = self.run_command(command)
            self.assertEqual(dry.returncode, 0, dry.stderr)
            dry_payload = json.loads(dry.stdout)
            self.assertEqual(dry_payload["status"], "would_initialize")
            self.assertFalse((collection / "skills").exists())
            self.assertFalse((collection / "project-conventions").exists())
            self.assertEqual(dry_payload["agent_links_created"], [])

            applied = self.run_command([*command, "--apply"])
            self.assertEqual(applied.returncode, 0, applied.stderr)
            payload = json.loads(applied.stdout)
            self.assertEqual(payload["status"], "initialized")
            self.assertEqual(payload["agent_links_created"], [])
            self.assertEqual(payload["git_roots_created"], [])

            wrapper = collection / "project-conventions"
            projection = wrapper / "src" / "project-conventions"
            target = checkout / "project-conventions"
            if os.name == "nt":
                self.assertTrue(
                    bool(getattr(os.path, "isjunction", lambda _: False)(projection))
                )
            else:
                self.assertTrue(projection.is_symlink())
                self.assertEqual(os.readlink(projection), "../../GitHub/project-conventions")
            self.assertEqual(projection.resolve(), target.resolve())
            self.assertTrue((projection / "SKILL.md").is_file())
            self.assertFalse((collection / ".git").exists())
            self.assertFalse((wrapper / ".git").exists())
            self.assertEqual(self.git(checkout, "rev-parse", "HEAD"), before_head)
            self.assertEqual(self.git(checkout, "status", "--porcelain=v1"), "")

            control = collection / "skills"
            self.assertEqual(
                {path.name for path in (control / "src").iterdir()},
                {"README.md", "config", "scripts", "tests"},
            )
            exports = (control / "src" / "config" / "skill-exports.tsv").read_text(
                encoding="utf-8"
            )
            self.assertIn("project-conventions\tGitHub/project-conventions\tall", exports)
            members = (control / "docs" / "indexes" / "members.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("| source | repository_root | vcs |", members)
            self.assertIn("| GitHub | git | obisoldbee/skills | project-conventions/ |", members)
            for portable in (
                collection / "AGENTS.md",
                collection / "README.md",
                collection / "MEMBERS.md",
                control / "docs" / "indexes" / "members.md",
                control / "src" / "config" / "skill-exports.tsv",
                wrapper / "AGENTS.md",
                wrapper / "README.md",
            ):
                text = portable.read_text(encoding="utf-8")
                self.assertNotIn("/" + "Users" + "/", text)
                self.assertNotIn("C:" + "\\Users\\", text)
                self.assertNotIn("file" + "://", text.lower())

            generated_tests = self.run_command(
                [
                    sys.executable,
                    "-B",
                    str(control / "src" / "tests" / "test_public_root_overlay.py"),
                ],
                cwd=control,
            )
            self.assertEqual(generated_tests.returncode, 0, generated_tests.stderr)

            repeated = self.run_command([*command, "--apply"])
            self.assertEqual(repeated.returncode, 0, repeated.stderr)
            self.assertEqual(json.loads(repeated.stdout)["status"], "already_initialized")
            self.assertEqual(self.git(checkout, "rev-parse", "HEAD"), before_head)

    def test_initializer_refuses_unknown_collection_content(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            collection, checkout, _remote = self.create_shared_fixture(Path(raw))
            marker = collection / "unknown"
            marker.mkdir()
            initializer = checkout / "project-conventions" / "scripts" / "initialize_skills_control_project.py"
            result = self.run_command(
                [
                    sys.executable,
                    "-B",
                    str(initializer),
                    str(collection),
                    "--distribution-root",
                    str(checkout),
                    "--apply",
                ]
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("fresh collection contains unnamed entries", result.stderr)
            self.assertEqual({path.name for path in marker.iterdir()}, set())
            self.assertFalse((collection / "skills").exists())

    def test_update_only_fast_forwards_validates_and_stops(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            seed, checkout, remote = self.create_update_fixture(Path(raw))
            package = checkout / "project-conventions"
            updater = package / "scripts" / "update_shared_checkout.py"
            before = self.git(checkout, "rev-parse", "HEAD")

            readme = seed / "project-conventions" / "README.md"
            readme.write_text(
                readme.read_text(encoding="utf-8") + "\nUpdate fixture marker.\n",
                encoding="utf-8",
            )
            self.git(seed, "add", "project-conventions/README.md")
            self.git(seed, "commit", "-m", "advance package")
            self.git(seed, "push", "origin", "main")

            result = self.run_command(
                [
                    sys.executable,
                    "-B",
                    str(updater),
                    str(package),
                    "--remote-identity",
                    str(remote),
                ]
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            payload = json.loads(result.stdout)
            self.assertEqual(payload["status"], "updated")
            self.assertEqual(payload["lifecycle"], "update-only")
            self.assertEqual(payload["before"], before)
            self.assertNotEqual(payload["after"], before)
            self.assertEqual(payload["ahead"], 0)
            self.assertEqual(payload["behind"], 0)
            self.assertFalse((checkout.parent / "skills").exists())
            self.assertFalse((checkout.parent / "project-conventions").exists())

            repeated = self.run_command(
                [
                    sys.executable,
                    "-B",
                    str(updater),
                    str(package),
                    "--remote-identity",
                    str(remote),
                ]
            )
            self.assertEqual(repeated.returncode, 0, repeated.stderr)
            self.assertEqual(json.loads(repeated.stdout)["status"], "already_current")

    def test_update_only_refuses_dirty_checkout_before_fetch(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            _seed, checkout, remote = self.create_update_fixture(Path(raw))
            package = checkout / "project-conventions"
            updater = package / "scripts" / "update_shared_checkout.py"
            before = self.git(checkout, "rev-parse", "HEAD")
            marker = checkout / "untracked-local.txt"
            marker.write_text("keep\n", encoding="utf-8")
            result = self.run_command(
                [
                    sys.executable,
                    "-B",
                    str(updater),
                    str(package),
                    "--remote-identity",
                    str(remote),
                ]
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("stopped before fetch", result.stderr)
            self.assertEqual(self.git(checkout, "rev-parse", "HEAD"), before)
            self.assertEqual(marker.read_text(encoding="utf-8"), "keep\n")

    def test_package_validator_is_offline_and_rejects_transients(self) -> None:
        validator = PACKAGE_ROOT / "scripts" / "validate_package.py"
        valid = self.run_command(
            [sys.executable, "-B", str(validator), str(PACKAGE_ROOT)]
        )
        self.assertEqual(valid.returncode, 0, valid.stderr)
        self.assertEqual(json.loads(valid.stdout)["status"], "valid")

        with tempfile.TemporaryDirectory() as raw:
            copy = Path(raw) / "project-conventions"
            shutil.copytree(PACKAGE_ROOT, copy)
            (copy / ".DS_Store").write_bytes(b"transient")
            invalid = self.run_command(
                [sys.executable, "-B", str(copy / "scripts" / "validate_package.py"), str(copy)]
            )
            self.assertEqual(invalid.returncode, 1)
            self.assertIn("transient:.DS_Store", invalid.stderr)


if __name__ == "__main__":
    os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    unittest.main()
