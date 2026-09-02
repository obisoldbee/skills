from __future__ import annotations

import importlib.util
import subprocess
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "resolve_official_skills.py"
SPEC = importlib.util.spec_from_file_location("resolve_official_skills", SCRIPT)
MODULE = importlib.util.module_from_spec(SPEC)
assert SPEC.loader is not None
SPEC.loader.exec_module(MODULE)


def run(*args: str, cwd: Path) -> str:
    result = subprocess.run(
        ["git", *args],
        cwd=cwd,
        check=True,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip()


class ResolveOfficialSkillsTests(unittest.TestCase):
    def setUp(self) -> None:
        self.temp = tempfile.TemporaryDirectory()
        self.repo = Path(self.temp.name) / "MiniMax-H3"
        self.repo.mkdir()
        run("init", "-q", "-b", "main", cwd=self.repo)
        run("config", "user.name", "Fixture", cwd=self.repo)
        run("config", "user.email", "fixture@example.invalid", cwd=self.repo)
        run(
            "remote",
            "add",
            "origin",
            "https://github.com/MiniMax-AI/MiniMax-H3.git",
            cwd=self.repo,
        )

        h3 = self.repo / "skills" / "h3-prompt-writing"
        (h3 / "references").mkdir(parents=True)
        (h3 / "SKILL.md").write_text("official h3\n", encoding="utf-8")
        (h3 / "references" / "base-en.txt").write_text("base\n", encoding="utf-8")
        (h3 / "references" / "ref-en.txt").write_text("ref\n", encoding="utf-8")

        style = self.repo / "skills" / "3d-animation-short-generator"
        (style / "references").mkdir(parents=True)
        (style / "SKILL.cn.md").write_text("style\n", encoding="utf-8")
        (style / "references" / "qc.md").write_text("qc\n", encoding="utf-8")

        run("add", "skills", cwd=self.repo)
        run("commit", "-q", "-m", "fixture", cwd=self.repo)
        self.head = run("rev-parse", "HEAD", cwd=self.repo)
        run("update-ref", "refs/remotes/origin/main", self.head, cwd=self.repo)
        run("branch", "--set-upstream-to=origin/main", "main", cwd=self.repo)
        run("sparse-checkout", "init", "--cone", cwd=self.repo)
        run("sparse-checkout", "set", "skills", cwd=self.repo)

    def tearDown(self) -> None:
        self.temp.cleanup()

    def test_resolves_base_route_from_exact_clean_checkout(self) -> None:
        result = MODULE.resolve(self.repo, "h3-base", expected_head=self.head)
        self.assertEqual(result["status"], "available")
        self.assertEqual(len(result["files"]), 2)
        self.assertTrue(result["files"][1].endswith("references/base-en.txt"))

    def test_resolves_one_style_and_its_references(self) -> None:
        result = MODULE.resolve(
            self.repo,
            "3d-animation-short-generator",
            expected_head=self.head,
        )
        self.assertEqual(result["status"], "available")
        self.assertEqual(len(result["files"]), 2)
        self.assertTrue(result["files"][0].endswith("SKILL.cn.md"))

    def test_rejects_unreviewed_head(self) -> None:
        result = MODULE.resolve(self.repo, "h3-ref", expected_head="0" * 40)
        self.assertEqual(result["status"], "unavailable")
        self.assertIn("HEAD differs", result["reason"])

    def test_rejects_dirty_checkout(self) -> None:
        path = self.repo / "skills" / "h3-prompt-writing" / "SKILL.md"
        path.write_text("changed\n", encoding="utf-8")
        result = MODULE.resolve(self.repo, "h3-base", expected_head=self.head)
        self.assertEqual(result["status"], "unavailable")
        self.assertIn("dirty", result["reason"])

    def test_rejects_wrong_remote(self) -> None:
        run("remote", "set-url", "origin", "https://github.com/example/not-h3.git", cwd=self.repo)
        result = MODULE.resolve(self.repo, "h3-base", expected_head=self.head)
        self.assertEqual(result["status"], "unavailable")
        self.assertIn("origin fetch URL", result["reason"])


if __name__ == "__main__":
    unittest.main()
