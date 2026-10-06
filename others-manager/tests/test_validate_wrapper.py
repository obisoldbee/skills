from pathlib import Path
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
        (self.wrapper / "src/others-manager").symlink_to("../../GitHub/others-manager")
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

    def test_current_integrator_needs_no_historical_chat_id(self):
        self.assertEqual([], self.validate())

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
