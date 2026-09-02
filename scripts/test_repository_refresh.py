#!/usr/bin/env python3
"""Offline behavior regressions; every Git write targets a disposable fixture."""

from __future__ import annotations

import os
from pathlib import Path
import shutil
import subprocess
import tempfile
from types import SimpleNamespace
import unittest
from unittest.mock import patch

import verify_release as release


SOURCE = Path(__file__).resolve().parents[1]


class RepositoryRefreshTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory(prefix="skills-refresh-test-")
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        env = {key: value for key, value in os.environ.items() if not key.startswith("GIT_")}
        env.update(
            GIT_CONFIG_NOSYSTEM="1", GIT_CONFIG_GLOBAL=os.devnull,
            GIT_ALLOW_PROTOCOL="file", GIT_TERMINAL_PROMPT="0",
            PYTHONDONTWRITEBYTECODE="1",
        )
        self.environment = patch.dict(os.environ, env, clear=True)
        self.environment.start()
        self.addCleanup(self.environment.stop)
        self.seed = self.root / "seed"
        self.seed.mkdir()
        for name in release.REQUIRED_ROOT_FILES | {release.ROOT_MANIFEST}:
            target = self.seed / name
            target.parent.mkdir(parents=True, exist_ok=True)
            shutil.copyfile(SOURCE / name, target)
        self.member = self.seed / "example-member" / "SKILL.md"
        self.member.parent.mkdir()
        self.write_lf(self.member, "fixture member, not a root-managed file\n")
        release.rebuild_manifest(self.seed)
        self.git(self.seed, "init", "-q", "-b", "main")
        self.git(self.seed, "config", "user.name", "Fixture")
        self.git(self.seed, "config", "user.email", "fixture@example.invalid")
        self.git(self.seed, "config", "core.autocrlf", "false")
        self.git(self.seed, "add", ".")
        self.git(self.seed, "commit", "-qm", "initial")
        self.origin = self.root / "origin.git"
        self.checkout = self.root / "checkout"
        self.git(self.root, "clone", "-q", "--bare", str(self.seed), str(self.origin))
        self.git(self.root, "clone", "-q", str(self.origin), str(self.checkout))
        self.git(self.checkout, "config", "core.autocrlf", "false")
        self.git(self.seed, "remote", "add", "origin", str(self.origin))
        self.before = self.git(self.checkout, "rev-parse", "HEAD")

    def git(self, root, *args, input=None):
        result = subprocess.run(
            ["git", "--no-optional-locks", "-C", str(root), *args],
            input=input, capture_output=True, text=True, check=False,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        return result.stdout.strip()

    @staticmethod
    def write_lf(path, text, *, append=False):
        """Write fixture text exactly as Git stores files governed by eol=lf."""
        with path.open(
            "a" if append else "w", encoding="utf-8", newline="\n"
        ) as handle:
            handle.write(text)

    def publish(self, *, rebuild=True, stage=True):
        if rebuild:
            release.rebuild_manifest(self.seed)
        if stage:
            self.git(self.seed, "add", "-A")
        self.git(self.seed, "commit", "-qm", "candidate")
        self.git(self.seed, "push", "-q", "origin", "main")
        return self.git(self.seed, "rev-parse", "HEAD")

    def refresh(self, *, update=True):
        return release.refresh_repository(
            self.checkout, update=update, remote_name="origin",
            remote_identity=str(self.origin), expected_ref="main",
        )

    def snapshot(self):
        index = Path(self.git(self.checkout, "rev-parse", "--git-path", "index"))
        if not index.is_absolute():
            index = self.checkout / index
        files = {}
        for directory, directories, names in os.walk(self.checkout, followlinks=False):
            if Path(directory) == self.checkout:
                directories.remove(".git")
            for name in directories + names:
                path = Path(directory) / name
                relative = path.relative_to(self.checkout).as_posix()
                if path.is_symlink():
                    files[relative] = ("link", os.readlink(path))
                elif path.is_dir():
                    files[relative] = ("directory",)
                else:
                    files[relative] = ("file", path.read_bytes(), path.stat().st_mode)
        return self.git(self.checkout, "rev-parse", "HEAD"), index.read_bytes(), files

    def assert_candidate_rejected(self, pattern):
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, pattern):
            self.refresh()
        self.assertEqual(self.snapshot(), before, "failed candidate changed HEAD/index/worktree")

    def test_check_only_is_read_only_and_does_not_fetch(self):
        self.write_lf(self.member, "remote change\n")
        self.publish()
        before = self.snapshot()
        result = self.refresh(update=False)
        self.assertEqual(result["status"], "ready")
        self.assertEqual(self.git(self.checkout, "rev-parse", "origin/main"), self.before)
        self.assertEqual(self.snapshot(), before)

    def test_success_updates_root_and_member_to_full_validated_sha(self):
        self.write_lf(self.member, "new member bytes\n")
        self.write_lf(
            self.seed / "README.md", "\nFixture candidate.\n", append=True
        )
        candidate = self.publish()
        with patch.object(release, "git", wraps=release.git) as calls:
            result = self.refresh()
        self.assertEqual(result["status"], "updated")
        self.assertEqual(result["after"], candidate)
        self.assertEqual(result["candidate"], candidate)
        merges = [call.args for call in calls.call_args_list if "merge" in call.args]
        self.assertEqual(merges, [(self.checkout, "merge", "--ff-only", "--no-overwrite-ignore", candidate)])
        self.assertEqual((self.checkout / "example-member/SKILL.md").read_bytes(), self.member.read_bytes())
        release.verify(self.checkout)
        before = self.snapshot()
        self.assertEqual(self.refresh()["status"], "already_current")
        self.assertEqual(self.snapshot(), before)

    def test_extraction_is_root_only_and_ignores_archive_attributes(self):
        self.write_lf(
            self.seed / ".gitattributes",
            "\nscripts/link-macos.sh export-ignore\n",
            append=True,
        )
        candidate = self.publish()
        self.git(self.checkout, "fetch", "origin")
        destination = self.root / "extracted"
        release.extract_candidate_root(self.checkout, candidate, destination)
        self.assertFalse((destination / ".git").exists())
        self.assertFalse((destination / "example-member").exists())
        self.assertEqual((destination / "scripts/link-macos.sh").read_bytes(), (self.seed / "scripts/link-macos.sh").read_bytes())
        self.assertEqual(self.refresh()["after"], candidate)

    def test_missing_file_rejected_before_move(self):
        (self.seed / "scripts/verify_release.py").unlink()
        self.publish(rebuild=False)
        self.assert_candidate_rejected("required root file missing")

    def test_missing_manifest_rejected_before_move(self):
        (self.seed / release.ROOT_MANIFEST).unlink()
        self.publish(rebuild=False)
        self.assert_candidate_rejected("root manifest missing")

    def test_digest_mismatch_rejected_before_move(self):
        self.write_lf(self.seed / "README.md", "bad digest\n")
        self.publish(rebuild=False)
        self.assert_candidate_rejected("digest mismatch")

    def test_crlf_root_file_rejected_before_manifest_rebuild(self):
        readme = self.seed / "README.md"
        readme.write_bytes(readme.read_bytes().replace(b"\n", b"\r\n"))
        with self.assertRaisesRegex(ValueError, "non-LF line ending: README.md"):
            release.rebuild_manifest(self.seed)

    def test_existing_ignored_file_cannot_be_overwritten(self):
        # Use the shipped *.tmp rule, not a synthetic ignore-policy change.
        name = "user-draft.tmp"
        (self.checkout / name).write_bytes(b"local user draft\n")
        (self.seed / name).write_bytes(b"candidate tracked bytes\n")
        self.git(self.seed, "add", "-f", name)
        self.publish()
        self.assertEqual(self.git(self.checkout, "status", "--porcelain"), "")
        self.assert_candidate_rejected("untracked landing conflict")

    def test_index_only_concurrent_flag_is_preserved(self):
        self.write_lf(self.member, "candidate\n")
        self.publish()
        original_validate = release.validate_candidate
        observed = []
        index_states = []

        def validate_then_flag(root, candidate):
            original_validate(root, candidate)
            self.git(root, "update-index", "--assume-unchanged", "README.md")
            observed.append(self.snapshot())
            index_states.append(release.index_state(root))

        with patch.object(release, "validate_candidate", side_effect=validate_then_flag):
            with self.assertRaisesRegex(ValueError, "state changed"):
                self.refresh()
        self.assertEqual(self.snapshot(), observed[0])
        self.assertEqual(release.index_state(self.checkout), index_states[0])
        self.assertTrue(self.git(self.checkout, "ls-files", "-v", "README.md").startswith("h "))

    def test_index_identity_ignores_platform_specific_ctime(self):
        stable = dict(st_dev=1, st_ino=2, st_mode=3, st_size=4, st_mtime_ns=5)
        path_stat = SimpleNamespace(**stable, st_ctime_ns=6)
        handle_stat = SimpleNamespace(**stable, st_ctime_ns=7)
        self.assertEqual(
            release._index_identity(path_stat),
            release._index_identity(handle_stat),
        )
        changed = SimpleNamespace(**(stable | {"st_size": 8}), st_ctime_ns=6)
        self.assertNotEqual(
            release._index_identity(path_stat),
            release._index_identity(changed),
        )

    def test_ignored_file_parent_is_preserved(self):
        name = "file-parent.tmp"
        (self.seed / name).mkdir()
        self.write_lf(self.seed / name / "tracked", "candidate")
        self.write_lf(self.checkout / name, "user")
        self.git(self.seed, "add", "-f", name)
        self.publish()
        self.assert_candidate_rejected("untracked landing conflict")

    @unittest.skipIf(os.name == "nt", "Unix symlink ancestor; Windows aliases use the consumer suite")
    def test_ignored_symlink_parent_is_preserved(self):
        name = "symlink-parent.tmp"
        (self.seed / name).mkdir()
        self.write_lf(self.seed / name / "tracked", "candidate")
        (self.checkout / name).symlink_to(self.root, target_is_directory=True)
        self.git(self.seed, "add", "-f", name)
        self.publish()
        self.assert_candidate_rejected("untracked landing conflict")

    def test_ignored_extra_in_tracked_directory_is_preserved(self):
        name = "directory-extra.tmp"
        tracked = self.seed / name / "tracked"
        tracked.parent.mkdir()
        self.write_lf(tracked, "old tracked bytes")
        self.git(self.seed, "add", "-f", name)
        self.publish()
        self.refresh()
        tracked.unlink()
        tracked.parent.rmdir()
        self.write_lf(self.seed / name, "new file")
        self.write_lf(self.checkout / name / "extra.tmp", "user")
        self.git(self.seed, "add", "-f", name)
        self.publish()
        self.assert_candidate_rejected("untracked landing conflict")

    def test_noncolliding_ignored_file_survives_success(self):
        keep = self.checkout / "user-draft.tmp"
        keep.write_bytes(b"untouched\n")
        self.write_lf(self.member, "candidate\n")
        candidate = self.publish()
        self.assertEqual(self.refresh()["after"], candidate)
        self.assertEqual(keep.read_bytes(), b"untouched\n")

    def test_ignored_file_appearing_at_merge_is_not_overwritten(self):
        name = "late-draft.tmp"
        (self.seed / name).write_bytes(b"candidate\n")
        self.git(self.seed, "add", "-f", name)
        self.publish()
        original_git = release.git
        observed = []

        def git_with_late_file(root, *arguments):
            if arguments[0] == "merge":
                (root / name).write_bytes(b"concurrent user bytes\n")
                observed.append(self.snapshot())
            return original_git(root, *arguments)

        with patch.object(release, "git", side_effect=git_with_late_file):
            with self.assertRaisesRegex(ValueError, "would be overwritten"):
                self.refresh()
        self.assertEqual(len(observed), 1)
        self.assertEqual(self.snapshot(), observed[0])

    def test_file_replaced_by_directory_rejected_before_move(self):
        path = self.seed / "scripts/link-macos.sh"
        path.unlink()
        path.mkdir()
        self.write_lf(path / "nested", "wrong type")
        self.publish(rebuild=False)
        self.assert_candidate_rejected("required root file missing or wrong type")

    def test_git_symlink_rejected_without_materializing_it(self):
        oid = self.git(self.seed, "hash-object", "-w", "--stdin", input="../README.md")
        self.git(self.seed, "update-index", "--cacheinfo", f"120000,{oid},scripts/verify_release.py")
        self.publish(rebuild=False, stage=False)
        self.assert_candidate_rejected("linked or unsupported candidate path type")

    def test_gitlink_rejected_before_move(self):
        self.git(self.seed, "update-index", "--cacheinfo", f"160000,{self.before},scripts/link-macos.sh")
        self.publish(rebuild=False, stage=False)
        self.assert_candidate_rejected("linked or unsupported candidate path type")

    def test_linked_managed_directory_rejected_before_move(self):
        self.git(self.seed, "rm", "-qr", "config")
        oid = self.git(self.seed, "hash-object", "-w", "--stdin", input="scripts")
        self.git(self.seed, "update-index", "--add", "--cacheinfo", f"120000,{oid},config")
        self.publish(rebuild=False, stage=False)
        self.assert_candidate_rejected("linked or unsupported candidate path type")

    def test_windows_ambiguous_path_rejected_on_every_platform(self):
        oid = self.git(self.seed, "hash-object", "-w", "--stdin", input="ambiguous")
        before_index = self.git(self.seed, "ls-files", "--stage", "-z")
        injected = subprocess.run(
            [
                "git", "--no-optional-locks", "-C", str(self.seed),
                "update-index", "--add", "--cacheinfo",
                f"100644,{oid},scripts/NUL.txt",
            ],
            capture_output=True, text=True, check=False,
            env={**os.environ, "LC_ALL": "C"},
        )
        if injected.returncode:
            # Git for Windows rejects the unsafe path before our validator can
            # receive it.  That is the same safety outcome, while Unix runners
            # still exercise our platform-independent rejection below.
            self.assertEqual(os.name, "nt", injected.stderr)
            self.assertIn("invalid path", injected.stderr.lower())
            self.assertEqual(
                self.git(self.seed, "ls-files", "--stage", "-z"),
                before_index,
            )
            return
        self.publish(rebuild=False, stage=False)
        self.assert_candidate_rejected("unsafe or duplicate candidate path")

    def fake_verifier(self):
        self.write_lf(
            self.seed / "scripts/verify_release.py",
            "import os\nfrom pathlib import Path\n"
            "Path(os.environ['CANDIDATE_EXECUTION_MARKER']).write_text('executed')\n"
            "print('{\"status\": \"verified\", \"scope\": \"repository-root-only\"}')\n",
        )
        self.execution_marker = self.root / "must-not-exist"
        os.environ["CANDIDATE_EXECUTION_MARKER"] = str(self.execution_marker)

    def test_candidate_program_is_data_and_is_never_executed(self):
        self.fake_verifier()
        candidate = self.publish()
        self.assertEqual(self.refresh()["after"], candidate)
        self.assertFalse(self.execution_marker.exists())

    def test_self_reported_verified_cannot_hide_digest_mismatch(self):
        self.fake_verifier()
        release.rebuild_manifest(self.seed)  # The fake verifier's own hash is valid.
        self.write_lf(self.seed / "README.md", "incorrect managed bytes\n")
        self.publish(rebuild=False)
        self.assert_candidate_rejected("digest mismatch: README.md")
        self.assertFalse(self.execution_marker.exists())

    def test_self_reported_verified_cannot_hide_extra_managed_file(self):
        self.fake_verifier()
        release.rebuild_manifest(self.seed)
        self.write_lf(self.seed / "scripts/extra.txt", "unlisted bytes\n")
        self.publish(rebuild=False)
        self.assert_candidate_rejected("root-managed file set differs")
        self.assertFalse(self.execution_marker.exists())

    def test_concurrent_changes_are_not_overwritten(self):
        self.write_lf(self.member, "candidate\n")
        candidate = self.publish()
        original_validate = release.validate_candidate
        changes = ("head", "branch", "upstream", "remote", "rewrite", "tracked", "untracked", "staged", "marker", "candidate", "skip-worktree", "index-replaced")
        # Each scenario gets its own checkout; no reset or rollback can hide a write.
        original_checkout = self.checkout
        for change in changes:
            with self.subTest(change=change):
                self.checkout = self.root / ("concurrent-" + change)
                self.git(self.root, "clone", "-q", str(original_checkout), str(self.checkout))
                self.git(self.checkout, "config", "core.autocrlf", "false")
                self.git(self.checkout, "remote", "set-url", "origin", str(self.origin))
                observed = []

                def validate_then_change(root, sha):
                    original_validate(root, sha)
                    if change == "head":
                        self.git(root, "-c", "user.name=Fixture", "-c", "user.email=fixture@example.invalid", "commit", "--allow-empty", "-qm", "concurrent")
                    elif change == "branch":
                        self.git(root, "switch", "-qc", "other")
                    elif change == "upstream":
                        self.git(root, "update-ref", "refs/remotes/origin/other", self.before)
                        self.git(root, "branch", "--set-upstream-to=origin/other", "main")
                    elif change == "remote":
                        self.git(root, "remote", "set-url", "origin", str(self.seed))
                    elif change == "rewrite":
                        self.git(root, "config", f"url.{self.seed}.insteadOf", str(self.origin))
                    elif change in {"tracked", "staged"}:
                        self.write_lf(root / "README.md", "concurrent user bytes\n")
                        if change == "staged":
                            self.git(root, "add", "README.md")
                    elif change == "untracked":
                        self.write_lf(root / "user-file", "keep")
                    elif change == "marker":
                        (root / ".git/index.lock").touch()
                    elif change == "candidate":
                        self.git(root, "update-ref", "refs/remotes/origin/main", self.before)
                    elif change == "skip-worktree":
                        self.git(root, "update-index", "--skip-worktree", "README.md")
                    elif change == "index-replaced":
                        index = root / ".git/index"
                        replacement = root / ".git/replacement-index"
                        replacement.write_bytes(index.read_bytes())
                        replacement.replace(index)
                    observed.append(self.snapshot())

                with patch.object(release, "validate_candidate", side_effect=validate_then_change):
                    with self.assertRaises(ValueError):
                        self.refresh()
                self.assertEqual(len(observed), 1)
                self.assertEqual(self.snapshot(), observed[0])
                if change != "head":
                    self.assertEqual(self.snapshot()[0], self.before)
                self.assertNotEqual(self.snapshot()[0], candidate)
        self.checkout = original_checkout

    def test_dirty_checkout_stops_before_fetch(self):
        self.write_lf(self.member, "candidate\n")
        self.publish()
        self.write_lf(self.checkout / "keep", "user")
        before = self.snapshot()
        with self.assertRaisesRegex(ValueError, "dirty"):
            self.refresh()
        self.assertEqual(self.snapshot(), before)
        self.assertEqual(self.git(self.checkout, "rev-parse", "origin/main"), self.before)


if __name__ == "__main__":
    unittest.main(verbosity=2)
