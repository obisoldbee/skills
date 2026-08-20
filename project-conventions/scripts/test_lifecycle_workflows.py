#!/usr/bin/env python3
"""Regression tests for lifecycle routing and the shared repository layout."""

from __future__ import annotations

import json
import os
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
DISTRIBUTION_ROOT = PACKAGE_ROOT.parent


def is_windows_junction(path: Path) -> bool:
    native = getattr(os.path, "isjunction", None)
    if native is not None:
        return bool(native(path))
    if os.name != "nt":
        return False
    try:
        observed = os.lstat(path)
    except OSError:
        return False
    return getattr(observed, "st_reparse_tag", None) == getattr(
        stat, "IO_REPARSE_TAG_MOUNT_POINT", 0xA0000003
    )


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
        cls.layout = (
            PACKAGE_ROOT / "references" / "directory-layout.md"
        ).read_text(encoding="utf-8")
        cls.agents_template = (
            PACKAGE_ROOT / "references" / "agents-md-template.md"
        ).read_text(encoding="utf-8")
        cls.metadata = (PACKAGE_ROOT / "agents" / "openai.yaml").read_text(
            encoding="utf-8"
        )

    def test_all_project_types_require_project_owned_records(self) -> None:
        for required in (
            "| Code | `AGENTS.md`, `README.md`, `docs/`, `src/`, `conversation/`, `memory/` |",
            "| Document | `AGENTS.md`, `README.md`, `INDEX.md`, `docs/`, `conversation/`, `memory/`, versioned records |",
            "`conversation/` and `memory/` remain required",
            "Harness-owned memory or hidden directories never replace either project record",
        ):
            self.assertIn(required, self.skill)
        for required in (
            "| `conversation/` | Required | Required | Required |",
            "| `memory/` daily logs | Required | Required | Required |",
            "conversation/            # Required for every project type",
            "memory/                  # Required for every project type",
            "### `conversation/` (Required for Code, Document, and Hybrid)",
            "### `memory/` (Required for Code, Document, and Hybrid)",
            "Versioned records preserve deliverable submissions; they do not replace collaboration history or project continuity",
            "does not satisfy or replace the required project-root `conversation/` and `memory/` records",
        ):
            self.assertIn(required, self.layout)
        self.assertNotIn("optional for Document", self.layout)
        self.assertNotIn("Optional (use versioned records instead)", self.layout)
        self.assertIn(
            "required for Code, Document, and Hybrid projects",
            self.agents_template,
        )
        self.assertIn(
            "Harness-owned memory does not replace project `conversation/` or `memory/`",
            self.agents_template,
        )

    def test_concurrency_is_routed_without_permanent_role_layout(self) -> None:
        for required in (
            "$project-handoff",
            "temporary per-lane execution resource",
            "single-writer resources",
            "response-only findings",
            "integration owner",
        ):
            self.assertIn(required, self.skill)
        for required in (
            "permanent `work/lanes/`",
            "response-only reviewers",
            "temporary worktrees",
            "one writer at a time",
            "scan for the next `conversation/NN-*`",
            "One integration owner",
            "Separate Agent conversations do not imply separate filesystems",
        ):
            self.assertIn(required, self.layout)
        for required in (
            "sole active writer",
            "only the integration owner allocates the canonical number",
            "workers return response-only findings or use preallocated unique artifacts",
            "integration owner updates canonical conversation, memory, and indexes",
            "fixed role directories",
            "permanent `work/lanes/`",
        ):
            self.assertIn(required, self.agents_template)
        self.assertNotIn("both appends are valid", self.layout)
        for forbidden in (
            "Create a `conversation/NN-topic.md` file (scan for next number)",
            "Done working? Append a note to `memory/YYYY-MM-DD.md`",
            "After substantive work, append to `memory/YYYY-MM-DD.md`",
        ):
            self.assertNotIn(forbidden, self.agents_template)
        self.assertIn("temporary worktrees or serialized execution", self.metadata)

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

    def create_directory_link(self, link: Path, target: Path) -> None:
        if os.name == "nt":
            result = self.run_command(
                ["cmd", "/d", "/c", "mklink", "/J", str(link), str(target)]
            )
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        else:
            link.symlink_to(target, target_is_directory=True)

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

    def test_contract_distinguishes_optional_repository_infrastructure(self) -> None:
        combined = "\n".join(
            (self.skill, self.lifecycle, self.shared, self.collection, self.metadata)
        )
        for text in (
            "Multiple owned distributions",
            "GitHub-private",
            "third-party checkout pool",
            "one checkout per remote identity",
            "device-and-network-bound",
            "both must match",
        ):
            self.assertIn(text, combined)
        self.assertIn(
            "The standard public initializer never creates or clones an additional private root",
            self.shared,
        )
        self.assertIn(
            "Require the pool root to be a real non-Git directory",
            self.lifecycle,
        )

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
                self.assertTrue(is_windows_junction(projection))
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

    def test_initializer_refuses_linked_shared_repository_root(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            collection, checkout, _remote = self.create_shared_fixture(base)
            outside = base / "outside-checkout"
            checkout.rename(outside)
            self.create_directory_link(checkout, outside)
            initializer = (
                outside
                / "project-conventions"
                / "scripts"
                / "initialize_skills_control_project.py"
            )
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
            self.assertIn("shared Repository Root is missing or linked", result.stderr)
            self.assertFalse((collection / "skills").exists())

    @unittest.skipIf(os.name == "nt", "Unix raw symlink contract")
    def test_initializer_rejects_absolute_member_projection(self) -> None:
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
                "--apply",
            ]
            first = self.run_command(command)
            self.assertEqual(first.returncode, 0, first.stderr)
            projection = (
                collection
                / "project-conventions"
                / "src"
                / "project-conventions"
            )
            projection.unlink()
            projection.symlink_to(
                (checkout / "project-conventions").resolve(),
                target_is_directory=True,
            )
            repeated = self.run_command(command)
            self.assertEqual(repeated.returncode, 2)
            self.assertIn("member projection raw target differs", repeated.stderr)

    def test_initializer_validates_package_and_redacts_remote_credentials(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            collection, checkout, _remote = self.create_shared_fixture(Path(raw))
            initializer = (
                checkout
                / "project-conventions"
                / "scripts"
                / "initialize_skills_control_project.py"
            )
            credential = "secret-token"
            self.git(
                checkout,
                "remote",
                "set-url",
                "origin",
                f"https://{credential}@github.com/obisoldbee/skills.git",
            )
            command = [
                sys.executable,
                "-B",
                str(initializer),
                str(collection),
                "--distribution-root",
                str(checkout),
            ]
            valid = self.run_command(command)
            self.assertEqual(valid.returncode, 0, valid.stderr)
            self.assertNotIn(credential, valid.stdout + valid.stderr)
            self.assertEqual(
                json.loads(valid.stdout)["repository"]["origin"],
                "obisoldbee/skills",
            )

            transient = checkout / "project-conventions" / ".DS_Store"
            transient.write_bytes(b"transient")
            self.git(checkout, "add", "-f", "project-conventions/.DS_Store")
            self.git(checkout, "commit", "-m", "malformed package fixture")
            head = self.git(checkout, "rev-parse", "HEAD")
            self.git(checkout, "update-ref", "refs/remotes/origin/main", head)
            invalid = self.run_command(command)
            self.assertEqual(invalid.returncode, 2)
            self.assertIn("package verification failed", invalid.stderr)
            self.assertFalse((collection / "skills").exists())

    @unittest.skipIf(os.name == "nt", "Git symlink fixture is Unix-only")
    def test_initializer_rejects_linked_managed_package_root(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            collection, checkout, _remote = self.create_shared_fixture(base)
            package = checkout / "project-conventions"
            outside = base / "outside-package"
            shutil.copytree(package, outside)
            shutil.rmtree(package)
            package.symlink_to(outside, target_is_directory=True)
            self.git(checkout, "add", "-A")
            self.git(checkout, "commit", "-m", "linked package fixture")
            head = self.git(checkout, "rev-parse", "HEAD")
            self.git(checkout, "update-ref", "refs/remotes/origin/main", head)
            initializer = outside / "scripts" / "initialize_skills_control_project.py"
            result = self.run_command(
                [
                    sys.executable,
                    "-B",
                    str(initializer),
                    str(collection),
                    "--distribution-root",
                    str(checkout),
                ]
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("managed package root is missing or linked", result.stderr)

    @unittest.skipIf(os.name == "nt", "Git symlink fixture is Unix-only")
    def test_initializer_rejects_linked_package_validator(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            collection, checkout, _remote = self.create_shared_fixture(base)
            fake = base / "fake-validator.py"
            fake.write_text("print('fake valid')\n", encoding="utf-8")
            validator = (
                checkout
                / "project-conventions"
                / "scripts"
                / "validate_package.py"
            )
            validator.unlink()
            validator.symlink_to(fake)
            self.git(checkout, "add", "-A")
            self.git(checkout, "commit", "-m", "linked validator fixture")
            head = self.git(checkout, "rev-parse", "HEAD")
            self.git(checkout, "update-ref", "refs/remotes/origin/main", head)
            initializer = (
                checkout
                / "project-conventions"
                / "scripts"
                / "initialize_skills_control_project.py"
            )
            result = self.run_command(
                [
                    sys.executable,
                    "-B",
                    str(initializer),
                    str(collection),
                    "--distribution-root",
                    str(checkout),
                ]
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("required package validator file is missing", result.stderr)

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
            self.assertEqual(len(payload["validations"]), 1)
            self.assertIn("validate_package.py", payload["validations"][0])
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

    def test_update_only_ignores_root_publication_drift_and_redacts_credentials(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            seed, checkout, remote = self.create_update_fixture(Path(raw))
            package = checkout / "project-conventions"
            updater = package / "scripts" / "update_shared_checkout.py"

            readme = seed / "README.md"
            readme.write_text(
                readme.read_text(encoding="utf-8") + "\nRoot-only drift fixture.\n",
                encoding="utf-8",
            )
            self.git(seed, "add", "README.md")
            self.git(seed, "commit", "-m", "advance root without rebuilding manifest")
            self.git(seed, "push", "origin", "main")
            updated = self.run_command(
                [
                    sys.executable,
                    "-B",
                    str(updater),
                    str(package),
                    "--remote-identity",
                    str(remote),
                ]
            )
            self.assertEqual(updated.returncode, 0, updated.stderr)
            self.assertEqual(len(json.loads(updated.stdout)["validations"]), 1)
            root_check = self.run_command(
                [
                    sys.executable,
                    "-B",
                    str(checkout / "scripts" / "verify_release.py"),
                    str(checkout),
                ]
            )
            self.assertEqual(root_check.returncode, 1)

            credential = "secret-token"
            self.git(
                checkout,
                "remote",
                "set-url",
                "origin",
                f"https://{credential}@github.com/example/wrong.git",
            )
            mismatch = self.run_command(
                [sys.executable, "-B", str(updater), str(package)]
            )
            self.assertEqual(mismatch.returncode, 2)
            self.assertNotIn(credential, mismatch.stdout + mismatch.stderr)
            self.assertIn("expected obisoldbee/skills", mismatch.stderr)
            self.assertIn("example/wrong", mismatch.stderr)

    def test_update_only_redacts_non_github_remote_fetch_failure(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            _seed, checkout, _remote = self.create_update_fixture(Path(raw))
            package = checkout / "project-conventions"
            updater = package / "scripts" / "update_shared_checkout.py"
            marker = "secret-remote-marker"
            missing_remote = Path(raw) / f"{marker}-missing.git"
            self.git(
                checkout,
                "remote",
                "set-url",
                "origin",
                str(missing_remote),
            )
            result = self.run_command(
                [
                    sys.executable,
                    "-B",
                    str(updater),
                    str(package),
                    "--remote-identity",
                    str(missing_remote),
                ]
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("git fetch failed for configured remote origin", result.stderr)
            self.assertNotIn(marker, result.stdout + result.stderr)

    @unittest.skipIf(os.name == "nt", "Git symlink fixture is Unix-only")
    def test_update_only_rejects_linked_package_validator(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            seed, checkout, remote = self.create_update_fixture(base)
            fake = base / "fake-validator.py"
            fake.write_text("print('fake valid')\n", encoding="utf-8")
            seed_validator = (
                seed
                / "project-conventions"
                / "scripts"
                / "validate_package.py"
            )
            seed_validator.unlink()
            seed_validator.symlink_to(fake)
            self.git(seed, "add", "-A")
            self.git(seed, "commit", "-m", "linked validator fixture")
            self.git(seed, "push", "origin", "main")
            package = checkout / "project-conventions"
            updater = package / "scripts" / "update_shared_checkout.py"
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
            self.assertIn("package validator is missing or linked", result.stderr)

    @unittest.skipIf(os.name == "nt", "Git symlink fixture is Unix-only")
    def test_update_only_rejects_package_replaced_by_link_after_fast_forward(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            seed, checkout, remote = self.create_update_fixture(base)
            checkout_package = checkout / "project-conventions"
            updater = checkout_package / "scripts" / "update_shared_checkout.py"
            seed_package = seed / "project-conventions"
            outside = base / "outside-package"
            shutil.copytree(seed_package, outside)
            shutil.rmtree(seed_package)
            seed_package.symlink_to(outside, target_is_directory=True)
            self.git(seed, "add", "-A")
            self.git(seed, "commit", "-m", "replace package with linked fixture")
            self.git(seed, "push", "origin", "main")
            result = self.run_command(
                [
                    sys.executable,
                    "-B",
                    str(updater),
                    str(checkout_package),
                    "--remote-identity",
                    str(remote),
                ]
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn("managed package root is outside its exact real path or linked", result.stderr)
            self.assertTrue(checkout_package.is_symlink())

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

        with tempfile.TemporaryDirectory() as raw:
            linked = Path(raw) / "project-conventions"
            self.create_directory_link(linked, PACKAGE_ROOT)
            invalid_link = self.run_command(
                [sys.executable, "-B", str(validator), str(linked)]
            )
            self.assertEqual(invalid_link.returncode, 1)
            self.assertIn("package root is missing or linked", invalid_link.stderr)

    def test_package_validator_rejects_required_links_before_reading_them(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            package = base / "project-conventions"
            shutil.copytree(PACKAGE_ROOT, package)
            outside_agents = base / "outside-agents"
            outside_agents.mkdir()
            (outside_agents / "openai.yaml").write_bytes(b"\xff")
            shutil.rmtree(package / "agents")
            self.create_directory_link(package / "agents", outside_agents)
            result = self.run_command(
                [
                    sys.executable,
                    "-B",
                    str(package / "scripts" / "validate_package.py"),
                    str(package),
                ]
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("required package paths are linked", result.stderr)
            self.assertNotIn("non-utf8", result.stderr)
            self.assertNotIn("codec can't decode", result.stderr)

        if os.name != "nt":
            with tempfile.TemporaryDirectory() as raw:
                base = Path(raw)
                package = base / "project-conventions"
                shutil.copytree(PACKAGE_ROOT, package)
                outside_skill = base / "outside-skill.md"
                outside_skill.write_bytes(b"\xff")
                (package / "SKILL.md").unlink()
                (package / "SKILL.md").symlink_to(outside_skill)
                result = self.run_command(
                    [
                        sys.executable,
                        "-B",
                        str(package / "scripts" / "validate_package.py"),
                        str(package),
                    ]
                )
                self.assertEqual(result.returncode, 1)
                self.assertIn("required package paths are linked", result.stderr)
                self.assertNotIn("codec can't decode", result.stderr)

    def test_package_validator_does_not_follow_nested_directory_links(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            package = base / "project-conventions"
            shutil.copytree(PACKAGE_ROOT, package)
            outside = base / "outside"
            outside.mkdir()
            (outside / "outside-secret.md").write_text(
                "/" + "Users" + "/example/private\n", encoding="utf-8"
            )
            self.create_directory_link(package / "assets" / "nested-link", outside)
            result = self.run_command(
                [
                    sys.executable,
                    "-B",
                    str(package / "scripts" / "validate_package.py"),
                    str(package),
                ]
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("link:assets/nested-link", result.stderr)
            self.assertNotIn("outside-secret.md", result.stderr)
            self.assertNotIn("personal-path", result.stderr)

    def test_root_verifier_rejects_linked_repository_root(self) -> None:
        verifier = DISTRIBUTION_ROOT / "scripts" / "verify_release.py"
        with tempfile.TemporaryDirectory() as raw:
            linked = Path(raw) / "GitHub"
            self.create_directory_link(linked, DISTRIBUTION_ROOT)
            result = self.run_command(
                [sys.executable, "-B", str(verifier), str(linked)]
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("repository root is missing or linked", result.stderr)

    def test_root_verifier_rejects_nested_directory_link(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw)
            repository = base / "GitHub"
            self.copy_distribution(repository)
            outside = base / "outside"
            outside.mkdir()
            (outside / "outside-secret.md").write_text("fixture\n", encoding="utf-8")
            self.create_directory_link(repository / "config" / "nested-link", outside)
            verifier = repository / "scripts" / "verify_release.py"
            result = self.run_command(
                [sys.executable, "-B", str(verifier), str(repository)]
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("config/nested-link", result.stderr)
            self.assertNotIn("outside-secret.md", result.stderr)


if __name__ == "__main__":
    os.environ.setdefault("PYTHONDONTWRITEBYTECODE", "1")
    unittest.main()
