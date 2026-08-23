from __future__ import annotations

from contextlib import redirect_stderr, redirect_stdout
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest import mock
import uuid


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

import manage_others as manager  # noqa: E402


class OthersManagerTests(unittest.TestCase):
    def test_normalize_supported_github_urls(self) -> None:
        expected = "Owner/Repo"
        for value in (
            "https://github.com/Owner/Repo",
            "https://github.com/Owner/Repo.git",
            "git@github.com:Owner/Repo.git",
            "ssh://git@github.com/Owner/Repo.git",
        ):
            with self.subTest(value=value):
                normalized = manager.normalize_github_url(value)
                self.assertEqual(expected, normalized["identity"])
                self.assertEqual("owner/repo", normalized["identity_key"])
                self.assertEqual("https://github.com/Owner/Repo.git", normalized["canonical_url"])

    def test_normalize_rejects_credentials_and_other_hosts(self) -> None:
        for value in (
            "https://token@github.com/owner/repo",
            "https://github.example/owner/repo",
            "https://github.com/owner/repo?token=secret",
        ):
            with self.subTest(value=value):
                with self.assertRaises(manager.ManagerError):
                    manager.normalize_github_url(value)

    def test_pool_rejects_git_root_and_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary).resolve()
            pool = root / "pool"
            pool.mkdir()
            self.assertEqual(pool, manager.validate_pool(str(pool)))
            (pool / ".git").mkdir()
            with self.assertRaises(manager.ManagerError):
                manager.validate_pool(str(pool))
            (pool / ".git").rmdir()
            alias = root / "alias"
            alias.symlink_to(pool, target_is_directory=True)
            with self.assertRaises(manager.ManagerError):
                manager.validate_pool(str(alias))

    def test_plan_digest_detects_tampering(self) -> None:
        plan = manager.seal_plan(
            {
                "schema_version": manager.SCHEMA_VERSION,
                "kind": "others-manager-update-plan",
                "pool": "/private/tmp/example",
                "pool_fingerprint": {"device": 1, "inode": 2, "mode": 16384},
                "repository_names": ["repo"],
                "repositories": [
                    {
                        "name": "repo",
                        "path": "/private/tmp/example/repo",
                        "fingerprint": {"device": 1, "inode": 3, "mode": 16384},
                        "git_fingerprint": {"device": 1, "inode": 4, "mode": 16384},
                        "blockers": ["fixture_blocker"],
                        "action": "blocked",
                    }
                ],
            }
        )
        manager.verify_plan(plan, "others-manager-update-plan")
        plan["pool"] = "/private/tmp/changed"
        with self.assertRaises(manager.ManagerError):
            manager.verify_plan(plan, "others-manager-update-plan")

    def test_opened_plan_must_match_controller_reviewed_id(self) -> None:
        plan = manager.seal_plan(
            {
                "schema_version": manager.SCHEMA_VERSION,
                "kind": "others-manager-update-plan",
                "pool": "/private/tmp/example",
                "pool_fingerprint": {"device": 1, "inode": 2, "mode": 16384},
                "repository_names": [],
                "repositories": [],
            }
        )
        path = manager.operation_lock_root() / f"others-manager-plan-{uuid.uuid4().hex}.json"
        try:
            manager.write_json_exclusive(path, plan)
            loaded = manager.load_plan(str(path), "others-manager-update-plan", plan["plan_id"])
            self.assertEqual(plan, loaded)
            with self.assertRaises(manager.ManagerError):
                manager.load_plan(str(path), "others-manager-update-plan", "0" * 64)
        finally:
            if path.exists() and not path.is_symlink():
                path.unlink()

    def test_exclusive_json_output_refuses_overwrite(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            output = Path(temporary).resolve() / "report.json"
            manager.write_json_exclusive(output, {"ok": True})
            self.assertEqual({"ok": True}, json.loads(output.read_text(encoding="utf-8")))
            with self.assertRaises(manager.ManagerError):
                manager.write_json_exclusive(output, {"ok": False})

    def test_output_path_must_stay_under_system_temp(self) -> None:
        outside = Path(__file__).resolve().parent / "would-not-be-created.json"
        with self.assertRaises(manager.ManagerError):
            manager.ensure_output_available(str(outside))

    def test_git_environment_does_not_inherit_injection(self) -> None:
        os.environ["GIT_CONFIG_COUNT"] = "99"
        os.environ["HTTPS_PROXY"] = "http://credential.invalid"
        try:
            environment = manager.git_environment()
        finally:
            os.environ.pop("GIT_CONFIG_COUNT", None)
            os.environ.pop("HTTPS_PROXY", None)
        self.assertNotIn("GIT_CONFIG_COUNT", environment)
        self.assertNotIn("HTTPS_PROXY", environment)
        self.assertEqual("/usr/bin:/bin", environment["PATH"])

    def test_atomic_clone_commit_never_replaces_destination(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            pool = Path(temporary).resolve()
            stage = pool / ".others-manager-clone-first"
            checkout = stage / "checkout"
            checkout.mkdir(parents=True)
            (checkout / "value").write_text("new", encoding="utf-8")
            destination = pool / "repository"
            manager.atomic_rename_noreplace(checkout, destination)
            self.assertEqual("new", (destination / "value").read_text(encoding="utf-8"))

            second_stage = pool / ".others-manager-clone-second"
            second_checkout = second_stage / "checkout"
            second_checkout.mkdir(parents=True)
            existing = pool / "existing"
            existing.mkdir()
            (existing / "value").write_text("old", encoding="utf-8")
            with self.assertRaises(manager.ManagerError):
                manager.atomic_rename_noreplace(second_checkout, existing)
            self.assertEqual("old", (existing / "value").read_text(encoding="utf-8"))
            self.assertTrue(second_checkout.is_dir())

    def test_operation_receipt_is_reserved_before_completion(self) -> None:
        output = manager.operation_lock_root() / f"others-manager-test-{uuid.uuid4().hex}.json"
        try:
            receipt = manager.reserve_operation_receipt(output.as_posix(), "fixture", Path("/private/tmp/pool"), "plan")
            current = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual("in_progress", current["status"])
            manager.finalize_operation_receipt(receipt, {"kind": "fixture-report", "status": "ok"})
            final = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual("complete", final["receipt_status"])
            self.assertEqual("fixture-report", final["kind"])
        finally:
            if output.exists() and not output.is_symlink():
                output.unlink()

    def test_operation_lock_is_exclusive_and_owned(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            pool = Path(temporary).resolve()
            lock = manager.acquire_operation_lock(pool, "plan")
            try:
                with self.assertRaises(manager.ManagerError):
                    manager.acquire_operation_lock(pool, "other-plan")
            finally:
                self.assertTrue(manager.release_operation_lock(lock))

    def test_controller_apply_persists_independent_lock_cleanup_receipt(self) -> None:
        output = manager.operation_lock_root() / f"others-manager-op-{uuid.uuid4().hex}.json"
        cleanup = manager.operation_lock_root() / f"others-manager-cleanup-{uuid.uuid4().hex}.json"
        try:
            with tempfile.TemporaryDirectory() as temporary:
                pool = Path(temporary).resolve()
                with redirect_stdout(io.StringIO()):
                    report = manager.execute_controller_apply(
                        pool=pool,
                        plan={"plan_id": "a" * 64},
                        output=str(output),
                        cleanup_output=str(cleanup),
                        operation="fixture",
                        apply_function=lambda _pool, _plan: {"kind": "fixture-report", "status": "ok"},
                        capability_check=lambda: None,
                    )
            operation_receipt = json.loads(output.read_text(encoding="utf-8"))
            cleanup_receipt = json.loads(cleanup.read_text(encoding="utf-8"))
            self.assertEqual("held", operation_receipt["operation_lock_state_at_receipt_commit"])
            self.assertEqual(str(cleanup), operation_receipt["lock_cleanup_receipt"])
            self.assertEqual("released", cleanup_receipt["release_result"])
            self.assertEqual([], cleanup_receipt["blockers"])
            self.assertNotIn("cleanup_blockers", report)
        finally:
            for path in (output, cleanup):
                if path.exists() and not path.is_symlink():
                    path.unlink()

    def test_apply_requires_controller_confirmation(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            pool = Path(temporary).resolve()
            output = manager.operation_lock_root() / f"others-manager-unused-{uuid.uuid4().hex}.json"
            cleanup = manager.operation_lock_root() / f"others-manager-unused-cleanup-{uuid.uuid4().hex}.json"
            errors = io.StringIO()
            with redirect_stderr(errors):
                code = manager.main(
                    [
                        "apply-update",
                        "--pool",
                        str(pool),
                        "--plan",
                        "/private/tmp/nonexistent-plan.json",
                        "--output",
                        str(output),
                        "--cleanup-output",
                        str(cleanup),
                        "--expected-plan-id",
                        "0" * 64,
                        "--controller-project",
                        str(pool),
                        "--controller-session",
                        "fixture",
                    ]
                )
            self.assertEqual(1, code)
            self.assertIn("reviewed-plan confirmation", errors.getvalue())
            self.assertFalse(output.exists())
            self.assertFalse(cleanup.exists())

    def test_controller_capability_requires_exact_active_writer(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            collection = Path(temporary).resolve()
            pool = collection / "GitHub-others"
            pool.mkdir()
            package = collection / "GitHub" / "others-manager"
            scripts = package / "scripts"
            scripts.mkdir(parents=True)
            fake_module = scripts / "manage_others.py"
            fake_module.write_text("# fixture\n", encoding="utf-8")
            controller = collection / "others-manager"
            helper = controller / ".project-conventions" / "project_access.py"
            helper.parent.mkdir(parents=True)
            helper.write_text("# fixture\n", encoding="utf-8")
            projection = controller / "src" / "others-manager"
            projection.parent.mkdir()
            projection.symlink_to("../../GitHub/others-manager", target_is_directory=True)
            token = "a" * 48
            evidence = {
                "status": "active",
                "project_root": str(controller),
                "session_id": "fixture",
                "mode": "writer",
                "workspace": str(controller),
            }
            completed = subprocess.CompletedProcess([], 0, stdout=json.dumps(evidence), stderr="")
            with (
                mock.patch.object(manager, "__file__", str(fake_module)),
                mock.patch.dict(os.environ, {manager.CONTROLLER_TOKEN_ENV: token}),
                mock.patch.object(manager.subprocess, "run", return_value=completed),
            ):
                result = manager.validate_controller_capability(str(controller), "fixture", pool)
            self.assertEqual("writer", result["mode"])

            read_only = dict(evidence, mode="read-only")
            completed = subprocess.CompletedProcess([], 0, stdout=json.dumps(read_only), stderr="")
            with (
                mock.patch.object(manager, "__file__", str(fake_module)),
                mock.patch.dict(os.environ, {manager.CONTROLLER_TOKEN_ENV: token}),
                mock.patch.object(manager.subprocess, "run", return_value=completed),
                self.assertRaises(manager.ManagerError),
            ):
                manager.validate_controller_capability(str(controller), "fixture", pool)

    def test_discovery_does_not_follow_child_symlink(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            pool = Path(temporary).resolve()
            repo = pool / "repo"
            repo.mkdir()
            (repo / ".git").mkdir()
            alias = pool / "alias"
            alias.symlink_to(repo, target_is_directory=True)
            repositories, ignored = manager.discover_repositories(pool)
            self.assertEqual([repo], repositories)
            self.assertEqual([{"name": "alias", "reason": "symlink_not_followed"}], ignored)

    def test_inventory_accepts_clean_independent_fixture(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            pool = Path(temporary).resolve()
            repo = pool / "fixture"
            repo.mkdir()
            self.run_git(repo, "init")
            self.run_git(repo, "config", "user.name", "Fixture")
            self.run_git(repo, "config", "user.email", "fixture@example.invalid")
            (repo / "LICENSE").write_text("fixture\n", encoding="utf-8")
            self.run_git(repo, "add", "LICENSE")
            self.run_git(repo, "commit", "-m", "fixture")
            self.run_git(repo, "branch", "-M", "main")
            self.run_git(repo, "remote", "add", "origin", "https://github.com/example/fixture.git")
            head = self.run_git(repo, "rev-parse", "HEAD").stdout.strip()
            self.run_git(repo, "update-ref", "refs/remotes/origin/main", head)
            self.run_git(repo, "branch", "--set-upstream-to", "origin/main", "main")

            report = manager.inventory(pool)
            self.assertEqual(1, report["repositories_total"])
            self.assertEqual(1, report["counts"]["clean"])
            self.assertEqual(0, report["counts"]["blocked"])
            self.assertEqual([], report["repositories"][0]["blockers"])

    def test_unknown_or_credential_local_config_blocks_before_inspection(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary).resolve()
            self.run_git(repo, "init")
            self.assertEqual([], manager.executable_local_config(repo))
            self.run_git(repo, "config", "core.alternateRefsCommand", "unsafe-command")
            self.run_git(repo, "config", "http.cookieFile", "/private/tmp/cookie")
            categories = manager.executable_local_config(repo)
            self.assertIn("unsupported-local-config-key", categories)
            state = manager.inspect_repository(repo)
            self.assertIn("unsupported_or_unsafe_local_git_config", state["blockers"])
            self.assertIsNone(state["head"])

    def test_no_tags_clone_policy_is_the_only_allowed_tag_override(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary).resolve()
            self.run_git(repo, "init")
            self.run_git(repo, "config", "remote.origin.tagOpt", "--no-tags")
            self.assertEqual([], manager.executable_local_config(repo))
            self.run_git(repo, "config", "remote.origin.tagOpt", "--tags")
            self.assertIn("unsafe-origin-tag-policy", manager.executable_local_config(repo))

    def test_remote_tracking_ref_must_move_fast_forward(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            repo = Path(temporary).resolve()
            self.run_git(repo, "init")
            self.run_git(repo, "config", "user.name", "Fixture")
            self.run_git(repo, "config", "user.email", "fixture@example.invalid")
            (repo / "value").write_text("base\n", encoding="utf-8")
            self.run_git(repo, "add", "value")
            self.run_git(repo, "commit", "-m", "base")
            base = self.run_git(repo, "rev-parse", "HEAD").stdout.strip()
            (repo / "value").write_text("next\n", encoding="utf-8")
            self.run_git(repo, "commit", "-am", "next")
            descendant = self.run_git(repo, "rev-parse", "HEAD").stdout.strip()
            manager.require_remote_tracking_fast_forward(repo, base, descendant)
            with self.assertRaises(manager.ManagerError):
                manager.require_remote_tracking_fast_forward(repo, descendant, base)

    def test_update_plan_binds_github_snapshot_and_fingerprints(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            pool = Path(temporary).resolve()
            repo = pool / "fixture"
            repo.mkdir()
            self.run_git(repo, "init")
            self.run_git(repo, "config", "user.name", "Fixture")
            self.run_git(repo, "config", "user.email", "fixture@example.invalid")
            (repo / "LICENSE").write_text("fixture\n", encoding="utf-8")
            self.run_git(repo, "add", "LICENSE")
            self.run_git(repo, "commit", "-m", "fixture")
            self.run_git(repo, "branch", "-M", "main")
            self.run_git(repo, "remote", "add", "origin", "https://github.com/example/fixture.git")
            head = self.run_git(repo, "rev-parse", "HEAD").stdout.strip()
            self.run_git(repo, "update-ref", "refs/remotes/origin/main", head)
            self.run_git(repo, "branch", "--set-upstream-to", "origin/main", "main")
            github_snapshot = {
                "identity": "example/fixture",
                "identity_key": "example/fixture",
                "canonical_url": "https://github.com/example/fixture.git",
                "default_branch": "main",
                "remote_head": head,
                "license": {"spdx_id": "MIT"},
            }
            with mock.patch.object(manager, "github_update_snapshot", return_value=github_snapshot):
                plan = manager.plan_update(pool)
            manager.verify_plan(plan, "others-manager-update-plan")
            self.assertEqual(manager.path_fingerprint(pool), plan["pool_fingerprint"])
            self.assertEqual("already_current", plan["repositories"][0]["action"])
            self.assertEqual(github_snapshot, plan["repositories"][0]["github_snapshot"])

    @staticmethod
    def run_git(repo: Path, *args: str) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            ["git", *args],
            cwd=repo,
            text=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            check=True,
        )


if __name__ == "__main__":
    unittest.main()
