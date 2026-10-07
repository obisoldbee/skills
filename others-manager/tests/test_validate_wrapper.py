from pathlib import Path
import os
import subprocess
import sys
import tempfile
import unittest
from unittest import mock


sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))
import validate_wrapper


class WrapperAuthorityTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        root = Path(self.temporary.name).resolve()
        self.wrapper = root / "others-manager"
        self.package = root / "GitHub" / "others-manager"
        self.pool = root / "GitHub-others"
        self.package.mkdir(parents=True)
        self.pool.mkdir()
        (self.package / "SKILL.md").write_text("fixture\n")
        for relative in (
            "AGENTS.md", "README.md", ".project-conventions/project.json",
            ".project-conventions/project_access.py", "conversation/00-initialization.md",
            "memory/MEMORY.md", "docs/specs/2026-08-24-others-manager-spec.md",
        ):
            path = self.wrapper / relative
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text("fixture\n")
        (self.wrapper / "src").mkdir()
        self.projection = self.wrapper / "src/others-manager"
        self.create_projection(self.package)
        self.guidance = (
            "The current user-authorized workspace integrator coordinates integration.\n"
            "Delegated Luna workers may only inventory and plan.\n"
            "Apply requires an active exclusive writer capability.\n"
            "Updates remain fast-forward-only.\n"
            "Delegation requires a host filesystem sandbox.\n"
        )
        (self.wrapper / "AGENTS.md").write_text(self.guidance)

    def validate(self):
        with mock.patch.object(validate_wrapper, "git_root", return_value=self.package.parent):
            return validate_wrapper.validate(self.wrapper, self.package, self.pool)

    def create_projection(self, target):
        self.link_directory(self.projection, target)

    def link_directory(self, link, target):
        if os.name == "nt":
            result = subprocess.run(["cmd", "/c", "mklink", "/J", str(link), str(target)],
                                    capture_output=True, text=True)
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
            self.assertTrue(validate_wrapper.is_junction(link))
        else:
            link.symlink_to(os.path.relpath(target, link.parent), target_is_directory=True)

    def remove_projection(self):
        if os.name == "nt":
            self.projection.rmdir()
        else:
            self.projection.unlink()

    def test_current_integrator_needs_no_historical_chat_id(self):
        self.assertEqual([], self.validate())

    def test_wrong_or_dangling_projection_still_fails(self):
        wrong = self.package.parent / "other-package"
        wrong.mkdir()
        for target in (wrong, self.package.parent / "missing-package"):
            with self.subTest(target=target.name):
                self.remove_projection()
                self.create_projection(target)
                self.assertTrue(any("projection" in error for error in self.validate()))

    def test_real_directory_is_not_a_projection(self):
        self.remove_projection()
        self.projection.mkdir()
        self.assertTrue(any("src/others-manager must be" in error for error in self.validate()))

    def test_windows_junction_detector_supports_python_311_reparse_tag(self):
        with mock.patch.object(validate_wrapper.os.path, "isjunction", None, create=True):
            with mock.patch.object(validate_wrapper.os, "lstat", return_value=mock.Mock(st_reparse_tag=0xA0000003)):
                self.assertTrue(validate_wrapper.is_junction(self.projection))
            with mock.patch.object(validate_wrapper.os, "lstat", return_value=mock.Mock(st_reparse_tag=0xA000000C)):
                self.assertFalse(validate_wrapper.is_junction(self.projection))

    @unittest.skipUnless(os.name == "nt", "requires a native Windows directory symlink")
    def test_directory_symlink_is_rejected_on_windows(self):
        self.remove_projection()
        self.projection.symlink_to(self.package, target_is_directory=True)
        self.assertIn("src/others-manager must be a directory junction", self.validate())

    def test_cli_preserves_and_rejects_linked_wrapper_package_and_pool_entries(self):
        initialized = subprocess.run(["git", "init", str(self.package.parent)], capture_output=True, text=True)
        self.assertEqual(initialized.returncode, 0, initialized.stderr)
        original = {"wrapper": self.wrapper, "package": self.package, "pool": self.pool}
        expected = {"wrapper": "wrapper must be a real directory",
                    "package": "public package source is invalid", "pool": "managed pool must be a real directory"}
        for name, target in original.items():
            with self.subTest(entry=name):
                link = self.wrapper.parent / f"alias-{name}"
                self.link_directory(link, target)
                selected = {**original, name: link}
                command = [sys.executable, "-B", str(Path(validate_wrapper.__file__))]
                for key, path in selected.items():
                    command.extend([f"--{key}", str(path)])
                result = subprocess.run(command, capture_output=True, text=True)
                self.assertEqual(result.returncode, 1, result.stderr or result.stdout)
                self.assertIn(expected[name], result.stdout)

    def test_runtime_and_delegation_boundaries_remain_required(self):
        for phrase in (
            "current user-authorized workspace integrator",
            "Delegated Luna workers may only inventory",
            "active exclusive writer capability", "fast-forward-only",
            "host filesystem sandbox",
        ):
            with self.subTest(phrase=phrase):
                (self.wrapper / "AGENTS.md").write_text(self.guidance.replace(phrase, "removed"))
                self.assertIn("AGENTS.md missing boundary phrase: " + phrase, self.validate())


if __name__ == "__main__":
    unittest.main()
