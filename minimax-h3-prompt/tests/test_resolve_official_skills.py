from __future__ import annotations

import importlib.util
import os
import subprocess
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch


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

    def test_rejects_route_outside_allowlist(self) -> None:
        result = MODULE.resolve(self.repo, "../../outside", expected_head=self.head)
        self.assertEqual(result["status"], "unavailable")
        self.assertIn("unsupported official Skill route", result["reason"])

    def test_rejects_ignored_extra_reference(self) -> None:
        relative = "skills/3d-animation-short-generator/references/ignored.md"
        exclude = self.repo / ".git" / "info" / "exclude"
        exclude.write_text(relative + "\n", encoding="utf-8")
        (self.repo / relative).write_text("local only\n", encoding="utf-8")
        self.assertEqual(run("status", "--porcelain=v1", cwd=self.repo), "")

        result = MODULE.resolve(
            self.repo,
            "3d-animation-short-generator",
            expected_head=self.head,
        )
        self.assertEqual(result["status"], "unavailable")
        self.assertIn("absent from reviewed HEAD", result["reason"])

    def test_rejects_assume_unchanged_modification(self) -> None:
        relative = "skills/h3-prompt-writing/references/base-en.txt"
        run("update-index", "--assume-unchanged", relative, cwd=self.repo)
        (self.repo / relative).write_text("hidden change\n", encoding="utf-8")
        self.assertEqual(run("status", "--porcelain=v1", cwd=self.repo), "")

        result = MODULE.resolve(self.repo, "h3-base", expected_head=self.head)
        self.assertEqual(result["status"], "unavailable")
        self.assertIn("differs from reviewed HEAD", result["reason"])

    def test_rejects_replacement_object_materialized_on_disk(self) -> None:
        relative = "skills/h3-prompt-writing/SKILL.md"
        (self.repo / relative).write_text("malicious replacement\n", encoding="utf-8")
        run("add", relative, cwd=self.repo)
        run("commit", "-q", "-m", "replacement", cwd=self.repo)
        replacement = run("rev-parse", "HEAD", cwd=self.repo)
        run("reset", "--hard", self.head, cwd=self.repo)
        run("replace", self.head, replacement, cwd=self.repo)
        run("reset", "--hard", self.head, cwd=self.repo)
        self.assertEqual(run("rev-parse", "HEAD", cwd=self.repo), self.head)
        self.assertEqual((self.repo / relative).read_text(encoding="utf-8"), "malicious replacement\n")
        self.assertEqual(run("status", "--porcelain=v1", cwd=self.repo), "")

        result = MODULE.resolve(self.repo, "h3-base", expected_head=self.head)
        self.assertEqual(result["status"], "unavailable")
        self.assertIn("dirty", result["reason"])

    def test_ignores_inherited_git_trace_outputs(self) -> None:
        trace = Path(self.temp.name) / "git-trace.log"
        trace2 = Path(self.temp.name) / "git-trace2.json"
        with patch.dict(
            os.environ,
            {
                "GIT_TRACE": str(trace),
                "GIT_TRACE2_EVENT": str(trace2),
            },
            clear=False,
        ):
            result = MODULE.resolve(self.repo, "h3-base", expected_head=self.head)

        self.assertEqual(result["status"], "available")
        self.assertFalse(trace.exists())
        self.assertFalse(trace2.exists())

    def test_ignores_all_inherited_git_repository_and_config_state(self) -> None:
        alternate_index = Path(self.temp.name) / "injected-index"
        with patch.dict(
            os.environ,
            {
                "GIT_CONFIG_COUNT": "1",
                "GIT_CONFIG_KEY_0": "core.bare",
                "GIT_CONFIG_VALUE_0": "true",
                "GIT_DIR": str(Path(self.temp.name) / "not-the-repo"),
                "GIT_ICASE_PATHSPECS": "1",
                "GIT_INDEX_FILE": str(alternate_index),
                "GIT_WORK_TREE": str(Path(self.temp.name) / "not-the-worktree"),
            },
            clear=False,
        ):
            result = MODULE.resolve(self.repo, "h3-ref", expected_head=self.head)

        self.assertEqual(result["status"], "available")
        self.assertFalse(alternate_index.exists())


if __name__ == "__main__":
    unittest.main()
