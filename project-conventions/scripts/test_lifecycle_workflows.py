#!/usr/bin/env python3
"""Regression tests for lifecycle routing and the shared repository layout."""

from __future__ import annotations

import ast
import importlib.util
import json
import os
import re
import shutil
import stat
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock

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
        cls.readme = (PACKAGE_ROOT / "README.md").read_text(encoding="utf-8")
        cls.initialization = (
            PACKAGE_ROOT / "references" / "project-root-initialization.md"
        ).read_text(encoding="utf-8")
        cls.migration = (
            PACKAGE_ROOT / "references" / "migration-guide.md"
        ).read_text(encoding="utf-8")
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
            "| Document | `AGENTS.md`, `README.md`, `INDEX.md`, `docs/`, `conversation/`, `memory/`; add versioned records only for a real submission/version cycle |",
            "`conversation/` and `memory/` remain required",
            "Harness-owned memory or hidden directories never replace either project record",
        ):
            self.assertIn(required, self.skill)
        for required in (
            "| `conversation/` | Required | Required | Required |",
            "| `memory/` project continuity | Required | Required | Required |",
            "conversation/            # Required for every project type",
            "memory/                  # Required for every project type",
            "### `conversation/` (Required for Code, Document, and Hybrid)",
            "### `memory/` (Required for Code, Document, and Hybrid)",
            "versioned records only for a real submission/version cycle",
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

    def test_concurrency_has_project_local_admission_without_external_skill(self) -> None:
        for required in (
            ".project-conventions/project_access.py",
            "project-local helper",
            "read-only",
            "isolated-writer",
            "blocked or failed configured admission means no write",
            "不得自动接入",
            "不得仅因此阻断原任务",
        ):
            self.assertIn(required, self.skill)
        for required in (
            "permanent `work/lanes/`",
            "SQLite transaction",
            "Multiple response-only reviewers",
            "different clean linked worktrees",
            "A blocked Agent writes nothing",
            "Stale claims never expire automatically",
            "Separate Agent conversations do not imply separate filesystems",
        ):
            self.assertIn(required, self.layout)
        for required in (
            ".project-conventions/project_access.py status",
            "status: entered",
            "A blocked Agent writes nothing",
            "exclusive writer",
            "permanent `work/lanes/`",
        ):
            self.assertIn(required, self.agents_template)
        self.assertNotIn("$project-handoff", self.skill)
        self.assertNotIn("$project-handoff", self.agents_template)
        self.assertNotIn("sole active writer", self.agents_template)
        self.assertNotIn("both appends are valid", self.layout)
        for forbidden in (
            "Create a `conversation/NN-topic.md` file (scan for next number)",
            "Done working? Append a note to `memory/YYYY-MM-DD.md`",
            "After substantive work, append to `memory/YYYY-MM-DD.md`",
        ):
            self.assertNotIn(forbidden, self.agents_template)
        self.assertIn("project-local reader/writer admission", self.metadata)
        self.assertIn("`src/<skill-name>/SKILL.md`", self.skill)
        self.assertIn("`docs/<skill-name>/SKILL.md` are invalid", self.skill)
        self.assertIn("one local member `enter` automatically uses the same collection-wide", self.shared)
        self.assertIn("no dual manual lock sequence", self.shared)
        for required_file in (
            "initialize_project_root.py",
            "project_access.py",
            "validate_project_root.py",
            "test_project_root_workflows.py",
        ):
            self.assertTrue((PACKAGE_ROOT / "scripts" / required_file).is_file())

    def test_legacy_project_adoption_contract_is_complete_chinese_and_routed(self) -> None:
        section = self.initialization.split("## 旧项目治理接入合同", 1)[1]
        section = section.split("\n## ", 1)[0]
        for required in (
            "`adopt-existing` 在本文中称为“旧项目治理接入”",
            "逐项目明确授权",
            "仅限于补齐 `AGENTS.md` 路由",
            "项目本地准入助手 `.project-conventions/project_access.py`",
            "最小管理目录和初始管理记录",
            "原样保留所有已有资料",
            "不得移动、重命名、删除、复制或重新归类",
            "不得新建或移动 `Git` 仓库",
            "不得执行 `fetch` 或 `push`",
            "不得安装 `Skill`",
            "不得建立 `Agent` 消费者链接",
            "`dry-run` 指只展示计划而不写入",
            "任何失败都必须回滚本轮新建内容",
            "不得自动接入",
            "不得仅因此阻断原任务",
        ):
            self.assertIn(required, section)
        chinese_narrative = re.sub(r"`[^`]+`", "", section)
        self.assertIsNone(re.search(r"[A-Za-z]{2,}", chinese_narrative))
        for routed in (self.skill, self.readme, self.lifecycle, self.migration):
            self.assertIn("旧项目治理接入", routed)

        update_contract = "\n".join((self.skill, self.lifecycle, self.shared))
        for required in (
            "frozen candidate commit",
            "isolated temporary candidate tree",
            "fast-forwards only the exact validated commit",
            "leaves local `HEAD` and the worktree unchanged",
        ):
            self.assertIn(required, update_contract)

    def test_project_root_workflow_suite_passes(self) -> None:
        result = self.run_command(
            [
                sys.executable,
                "-B",
                str(PACKAGE_ROOT / "scripts" / "test_project_root_workflows.py"),
            ]
        )
        self.assertEqual(result.returncode, 0, result.stderr or result.stdout)

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

    def load_script(self, path: Path, name: str):
        spec = importlib.util.spec_from_file_location(name, path)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

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
        for device_refresh_text in (
            "Device refresh",
            "本机全量同步 Skills",
            "更新 GitHub 并让本机 Agent 使用",
            "同步共享 Skill 根",
            "--sync-device",
            "only missing public allowlisted Skill links",
            "never materializes the collection",
        ):
            self.assertIn(device_refresh_text, combined)
        self.assertIn(
            "never a whole-repository `src/skills` projection or copied root files",
            self.lifecycle,
        )

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

    def test_minimal_collection_initializer_rejects_links_and_rolls_back(self) -> None:
        initializer = self.load_script(
            PACKAGE_ROOT / "scripts" / "initialize_project_collection.py",
            "project_collection_initializer_test",
        )
        with tempfile.TemporaryDirectory() as raw:
            base = Path(raw).resolve()
            outside = base / "outside"
            outside.mkdir()
            leaf = base / "leaf"
            self.create_directory_link(leaf, outside)
            with self.assertRaises(initializer.InitializationError):
                initializer.initialize(leaf, "control", [], True)

            relay = base / "relay"
            self.create_directory_link(relay, outside)
            with self.assertRaises(initializer.InitializationError):
                initializer.initialize(relay / "collection", "control", [], True)
            self.assertFalse((outside / "collection").exists())

        with tempfile.TemporaryDirectory() as raw:
            target = Path(raw).resolve() / "collection"
            original = initializer.write_exclusive

            def collide(path: Path, content: str):
                if path.name == "README.md":
                    path.write_text("concurrent\n", encoding="utf-8")
                return original(path, content)

            with mock.patch.object(initializer, "write_exclusive", side_effect=collide):
                with self.assertRaises(initializer.InitializationError):
                    initializer.initialize(target, "control", [], True)
            self.assertEqual(
                {path.name for path in target.iterdir()},
                {"README.md"},
            )
            self.assertEqual(
                (target / "README.md").read_text(encoding="utf-8"),
                "concurrent\n",
            )

        with tempfile.TemporaryDirectory() as raw:
            target = Path(raw).resolve() / "collection"
            original = initializer.write_exclusive

            def fail_second(path: Path, content: str):
                if path.name == "README.md":
                    raise OSError("injected write failure")
                return original(path, content)

            with mock.patch.object(initializer, "write_exclusive", side_effect=fail_second):
                with self.assertRaises(OSError):
                    initializer.initialize(target, "control", [], True)
            self.assertFalse(target.exists())

    def test_shared_initializer_preserves_race_collisions_and_rolls_back_readback(self) -> None:
        initializer = self.load_script(
            PACKAGE_ROOT / "scripts" / "initialize_skills_control_project.py",
            "skills_control_initializer_test",
        )

        def apply(collection: Path, checkout: Path):
            return initializer.initialize(
                collection,
                checkout,
                "skills",
                "GitHub",
                "project-conventions",
                "project-conventions",
                "obisoldbee/skills",
                "main",
                "personal-open",
                True,
            )

        with tempfile.TemporaryDirectory() as raw:
            collection, checkout, _remote = self.create_shared_fixture(Path(raw))
            collection, checkout = collection.resolve(), checkout.resolve()
            initializer.PACKAGE_ROOT = checkout / "project-conventions"
            original = initializer.materialize_staging_tree

            def collide_directory(staging, destination, *arguments):
                if destination == collection / "skills":
                    destination.mkdir()
                return original(staging, destination, *arguments)

            with mock.patch.object(
                initializer,
                "materialize_staging_tree",
                side_effect=collide_directory,
            ):
                with self.assertRaises(FileExistsError):
                    apply(collection, checkout)
            self.assertTrue((collection / "skills").is_dir())
            self.assertEqual(list((collection / "skills").iterdir()), [])
            self.assertFalse((collection / "project-conventions").exists())

        with tempfile.TemporaryDirectory() as raw:
            collection, checkout, _remote = self.create_shared_fixture(Path(raw))
            collection, checkout = collection.resolve(), checkout.resolve()
            initializer.PACKAGE_ROOT = checkout / "project-conventions"
            original = initializer.write_exclusive

            def collide_file(path: Path, content: str):
                if path == collection / "AGENTS.md":
                    path.write_text("concurrent\n", encoding="utf-8")
                return original(path, content)

            with mock.patch.object(initializer, "write_exclusive", side_effect=collide_file):
                with self.assertRaises(FileExistsError):
                    apply(collection, checkout)
            self.assertEqual(
                (collection / "AGENTS.md").read_text(encoding="utf-8"),
                "concurrent\n",
            )
            self.assertFalse((collection / "skills").exists())
            self.assertFalse((collection / "project-conventions").exists())

        with tempfile.TemporaryDirectory() as raw:
            collection, checkout, _remote = self.create_shared_fixture(Path(raw))
            collection, checkout = collection.resolve(), checkout.resolve()
            initializer.PACKAGE_ROOT = checkout / "project-conventions"
            original = initializer.verify_control_tree

            def fail_final_readback(root: Path, *arguments):
                original(root, *arguments)
                if root == collection / "skills":
                    raise initializer.ControlInitializationError(
                        "injected final readback failure"
                    )

            with mock.patch.object(
                initializer,
                "verify_control_tree",
                side_effect=fail_final_readback,
            ):
                with self.assertRaises(initializer.ControlInitializationError):
                    apply(collection, checkout)
            self.assertEqual(
                {path.name for path in collection.iterdir()},
                {"GitHub"},
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
            for extra in (
                ["--control-project", "CON"],
                ["--package-subpath", "project-conventions/a|b"],
            ):
                rejected_portable = self.run_command([*command, *extra])
                self.assertNotEqual(rejected_portable.returncode, 0)
                self.assertFalse((collection / "skills").exists())
                self.assertFalse((collection / "project-conventions").exists())
            before_head = self.git(checkout, "rev-parse", "HEAD")
            dry = self.run_command(command)
            self.assertEqual(dry.returncode, 0, dry.stderr)
            dry_payload = json.loads(dry.stdout)
            self.assertEqual(dry_payload["status"], "would_initialize")
            self.assertFalse((collection / "skills").exists())
            self.assertFalse((collection / "project-conventions").exists())
            self.assertEqual(dry_payload["agent_links_created"], [])
            self.assertEqual(
                {
                    Path(item["path"]).name
                    for item in dry_payload["would_create_control_projections"]
                },
                {"AGENTS.md", "README.md", "config", "scripts"},
            )

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
                {"AGENTS.md", "README.md", "config", "scripts"},
            )
            for name, kind in (
                ("AGENTS.md", "file"),
                ("README.md", "file"),
                ("config", "directory"),
                ("scripts", "directory"),
            ):
                root_projection = control / "src" / name
                root_target = checkout / name
                if os.name == "nt" and kind == "directory":
                    self.assertTrue(is_windows_junction(root_projection))
                else:
                    self.assertTrue(root_projection.is_symlink())
                if os.name != "nt" or kind == "file":
                    self.assertEqual(
                        os.readlink(root_projection).replace(os.sep, "/"),
                        f"../../GitHub/{name}",
                    )
                self.assertEqual(root_projection.resolve(), root_target.resolve())
                if kind == "file":
                    self.assertTrue(root_projection.is_file())
                else:
                    self.assertTrue(root_projection.is_dir())
            self.assertFalse((control / "src" / "skills").exists())
            self.assertFalse((control / "src" / "tests").exists())
            exports = (control / "src" / "config" / "skill-exports.tsv").read_text(
                encoding="utf-8"
            )
            self.assertIn("project-conventions\tproject-conventions\tall", exports)
            members = (control / "docs" / "indexes" / "members.md").read_text(
                encoding="utf-8"
            )
            self.assertIn("| source | repository_root | vcs |", members)
            self.assertIn(
                "| collection-control | src | - | none | - | repository-root public projections |",
                members,
            )
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

            projected_root_validation = self.run_command(
                [
                    sys.executable,
                    "-B",
                    str(control / "src" / "scripts" / "verify_release.py"),
                    str(checkout),
                ],
                cwd=control,
            )
            self.assertEqual(
                projected_root_validation.returncode,
                0,
                projected_root_validation.stderr,
            )

            project_root_validator = target / "scripts" / "validate_project_root.py"
            for generated_root in (control, wrapper):
                validated_root = self.run_command(
                    [
                        sys.executable,
                        "-B",
                        str(project_root_validator),
                        str(generated_root),
                    ]
                )
                self.assertEqual(validated_root.returncode, 0, validated_root.stderr)

            control_access = control / ".project-conventions" / "project_access.py"
            member_access = wrapper / ".project-conventions" / "project_access.py"
            entered_control = self.run_command(
                [
                    sys.executable,
                    "-B",
                    str(control_access),
                    "enter",
                    "--mode",
                    "writer",
                    "--session",
                    "control-writer",
                    "--actor",
                    "control-agent",
                ]
            )
            self.assertEqual(entered_control.returncode, 0, entered_control.stderr)
            control_receipt = json.loads(entered_control.stdout)
            blocked_member = self.run_command(
                [
                    sys.executable,
                    "-B",
                    str(member_access),
                    "enter",
                    "--mode",
                    "writer",
                    "--actor",
                    "member-agent",
                ]
            )
            self.assertEqual(blocked_member.returncode, 2, blocked_member.stderr)
            finished_control = self.run_command(
                [
                    sys.executable,
                    "-B",
                    str(control_access),
                    "finish",
                    "--session",
                    str(control_receipt["session_id"]),
                    "--token",
                    str(control_receipt["token"]),
                    "--outcome",
                    "success",
                ]
            )
            self.assertEqual(finished_control.returncode, 0, finished_control.stderr)
            entered_member = self.run_command(
                [
                    sys.executable,
                    "-B",
                    str(member_access),
                    "enter",
                    "--mode",
                    "writer",
                    "--session",
                    "member-writer",
                    "--actor",
                    "member-agent",
                ]
            )
            self.assertEqual(entered_member.returncode, 0, entered_member.stderr)
            member_receipt = json.loads(entered_member.stdout)
            self.assertEqual(member_receipt["runtime_storage"], "collection-control")
            control_status = self.run_command(
                [sys.executable, "-B", str(control_access), "status"]
            )
            self.assertEqual(control_status.returncode, 0, control_status.stderr)
            self.assertEqual(
                json.loads(control_status.stdout)["claims"][0]["session_id"],
                "member-writer",
            )
            finished_member = self.run_command(
                [
                    sys.executable,
                    "-B",
                    str(member_access),
                    "finish",
                    "--session",
                    str(member_receipt["session_id"]),
                    "--token",
                    str(member_receipt["token"]),
                    "--outcome",
                    "success",
                ]
            )
            self.assertEqual(finished_member.returncode, 0, finished_member.stderr)

            member_config = wrapper / ".project-conventions" / "project.json"
            original_member_config = member_config.read_bytes()
            changed = json.loads(original_member_config)
            changed["coordination_root"] = "../project-conventions"
            member_config.write_text(
                json.dumps(changed, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
                encoding="utf-8",
            )
            wrong_sibling_status = self.run_command(
                [sys.executable, "-B", str(member_access), "status"]
            )
            self.assertEqual(wrong_sibling_status.returncode, 3)
            wrong_sibling_validation = self.run_command(
                [sys.executable, "-B", str(project_root_validator), str(wrapper)]
            )
            self.assertNotEqual(wrong_sibling_validation.returncode, 0)
            member_config.write_bytes(original_member_config)

            control_access_readme = control / ".project-conventions" / "ACCESS.md"
            original_access_readme = control_access_readme.read_bytes()
            control_access_readme.write_bytes(original_access_readme + b"tampered\n")
            tampered_coordinator_status = self.run_command(
                [sys.executable, "-B", str(member_access), "status"]
            )
            self.assertEqual(tampered_coordinator_status.returncode, 3)
            tampered_coordinator_validation = self.run_command(
                [sys.executable, "-B", str(project_root_validator), str(wrapper)]
            )
            self.assertNotEqual(tampered_coordinator_validation.returncode, 0)
            control_access_readme.write_bytes(original_access_readme)

            repeated = self.run_command([*command, "--apply"])
            self.assertEqual(repeated.returncode, 0, repeated.stderr)
            self.assertEqual(json.loads(repeated.stdout)["status"], "already_initialized")
            self.assertEqual(self.git(checkout, "rev-parse", "HEAD"), before_head)

    def test_shared_roles_reject_empty_source_projection_sets(self) -> None:
        def initialize(raw: str):
            collection, checkout, _remote = self.create_shared_fixture(Path(raw))
            initializer = (
                checkout
                / "project-conventions"
                / "scripts"
                / "initialize_skills_control_project.py"
            )
            applied = self.run_command(
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
            self.assertEqual(applied.returncode, 0, applied.stderr)
            validator = (
                checkout
                / "project-conventions"
                / "scripts"
                / "validate_project_root.py"
            )
            return collection, validator

        with tempfile.TemporaryDirectory() as raw:
            collection, validator = initialize(raw)
            control = collection / "skills"
            for projection in (control / "src").iterdir():
                if is_windows_junction(projection):
                    projection.rmdir()
                else:
                    projection.unlink()
            control_result = self.run_command(
                [sys.executable, "-B", str(validator), str(control)]
            )
            self.assertNotEqual(control_result.returncode, 0)
            self.assertIn("exactly four projections", control_result.stderr)

        with tempfile.TemporaryDirectory() as raw:
            collection, validator = initialize(raw)
            member = collection / "project-conventions"
            for projection in (member / "src").iterdir():
                if is_windows_junction(projection):
                    projection.rmdir()
                else:
                    projection.unlink()
            member_result = self.run_command(
                [sys.executable, "-B", str(validator), str(member)]
            )
            self.assertNotEqual(member_result.returncode, 0)
            self.assertIn("only its package projection", member_result.stderr)

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

    @unittest.skipIf(os.name == "nt", "Unix raw symlink contract")
    def test_initializer_rejects_control_projection_conflicts_without_repair(self) -> None:
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
            source = collection / "skills" / "src"

            agents = source / "AGENTS.md"
            agents.unlink()
            agents.write_text("duplicate bytes\n", encoding="utf-8")
            real_path = self.run_command(command)
            self.assertEqual(real_path.returncode, 2)
            self.assertIn("control projection is not a Unix symlink", real_path.stderr)
            self.assertEqual(agents.read_text(encoding="utf-8"), "duplicate bytes\n")
            agents.unlink()
            agents.symlink_to("../../GitHub/AGENTS.md")

            readme = source / "README.md"
            readme.unlink()
            readme.symlink_to("../../GitHub/AGENTS.md")
            wrong_link = self.run_command(command)
            self.assertEqual(wrong_link.returncode, 2)
            self.assertIn("control projection raw target differs", wrong_link.stderr)
            self.assertEqual(os.readlink(readme), "../../GitHub/AGENTS.md")
            readme.unlink()
            readme.symlink_to("../../GitHub/README.md")

            config = source / "config"
            config.unlink()
            config.symlink_to("../../missing", target_is_directory=True)
            dangling = self.run_command(command)
            self.assertEqual(dangling.returncode, 2)
            self.assertIn("control projection raw target differs", dangling.stderr)
            self.assertEqual(os.readlink(config), "../../missing")
            config.unlink()
            config.symlink_to("../../GitHub/config", target_is_directory=True)

            whole_repository = source / "skills"
            whole_repository.symlink_to("../../GitHub", target_is_directory=True)
            extra_projection = self.run_command(command)
            self.assertEqual(extra_projection.returncode, 2)
            self.assertIn("control src entry set differs", extra_projection.stderr)
            self.assertIn("extra=['skills']", extra_projection.stderr)
            self.assertTrue(whole_repository.is_symlink())
            whole_repository.unlink()

            extra_directory = source / "tests"
            extra_directory.mkdir()
            empty_extra = self.run_command(command)
            self.assertEqual(empty_extra.returncode, 2)
            self.assertIn("control src entry set differs", empty_extra.stderr)
            self.assertIn("extra=['tests']", empty_extra.stderr)
            self.assertTrue(extra_directory.is_dir())

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
            before = self.git(checkout, "rev-parse", "HEAD")
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
            self.assertIn("validation failed before fast-forward", result.stderr)
            self.assertIn("candidate package contains a linked path", result.stderr)
            self.assertEqual(self.git(checkout, "rev-parse", "HEAD"), before)
            self.assertEqual(self.git(checkout, "status", "--porcelain=v1"), "")
            self.assertFalse((package / "scripts" / "validate_package.py").is_symlink())

    @unittest.skipIf(os.name == "nt", "Git symlink fixture is Unix-only")
    def test_update_only_rejects_package_replaced_by_link_before_fast_forward(self) -> None:
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
            before = self.git(checkout, "rev-parse", "HEAD")
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
            self.assertIn("validation failed before fast-forward", result.stderr)
            self.assertIn("candidate package contains a linked path", result.stderr)
            self.assertEqual(self.git(checkout, "rev-parse", "HEAD"), before)
            self.assertEqual(self.git(checkout, "status", "--porcelain=v1"), "")
            self.assertFalse(checkout_package.is_symlink())

    def test_update_only_validation_failure_leaves_checkout_unchanged(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            seed, checkout, remote = self.create_update_fixture(Path(raw))
            package = checkout / "project-conventions"
            updater = package / "scripts" / "update_shared_checkout.py"
            before = self.git(checkout, "rev-parse", "HEAD")
            (seed / "project-conventions" / "README.md").unlink()
            self.git(seed, "add", "-A")
            self.git(seed, "commit", "-m", "invalid package candidate")
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
            self.assertEqual(result.returncode, 2)
            self.assertIn("validation failed before fast-forward", result.stderr)
            self.assertEqual(self.git(checkout, "rev-parse", "HEAD"), before)
            self.assertEqual(self.git(checkout, "status", "--porcelain=v1"), "")
            self.assertTrue((package / "README.md").is_file())

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

    def test_every_required_package_file_is_enforced(self) -> None:
        validator = PACKAGE_ROOT / "scripts" / "validate_package.py"
        module = ast.parse(validator.read_text(encoding="utf-8"))
        assignment = next(
            node
            for node in module.body
            if isinstance(node, ast.Assign)
            and any(
                isinstance(target, ast.Name) and target.id == "REQUIRED_FILES"
                for target in node.targets
            )
        )
        required = sorted(ast.literal_eval(assignment.value))
        with tempfile.TemporaryDirectory() as raw:
            package = Path(raw) / "project-conventions"
            shutil.copytree(PACKAGE_ROOT, package)
            for relative in required:
                with self.subTest(relative=relative):
                    path = package / relative
                    content = path.read_bytes()
                    mode = stat.S_IMODE(path.stat().st_mode)
                    path.unlink()
                    result = self.run_command(
                        [sys.executable, "-B", str(validator), str(package)]
                    )
                    self.assertEqual(result.returncode, 1)
                    self.assertIn(relative, result.stderr)
                    path.write_bytes(content)
                    path.chmod(mode)

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
            self.create_directory_link(package / "references" / "nested-link", outside)
            result = self.run_command(
                [
                    sys.executable,
                    "-B",
                    str(package / "scripts" / "validate_package.py"),
                    str(package),
                ]
            )
            self.assertEqual(result.returncode, 1)
            self.assertIn("link:references/nested-link", result.stderr)
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
