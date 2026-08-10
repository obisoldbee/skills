#!/usr/bin/env python3
"""Deterministic tests for collection-aware workspace inspection."""

from __future__ import annotations

import importlib.util
import json
import os
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


SCRIPT = Path(__file__).with_name("inspect_projects_workspace.py")
sys.dont_write_bytecode = True
SPEC = importlib.util.spec_from_file_location(
    "project_conventions_inspector", SCRIPT
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load inspector module: {SCRIPT}")
INSPECTOR = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = INSPECTOR
SPEC.loader.exec_module(INSPECTOR)


class InspectorCollectionTests(unittest.TestCase):
    def create_symlink(
        self, link: Path, target: Path, *, target_is_directory: bool = False
    ) -> None:
        try:
            link.symlink_to(target, target_is_directory=target_is_directory)
        except OSError as exc:
            if os.name == "nt" and getattr(exc, "winerror", None) == 1314:
                self.skipTest("Windows symlink privilege is unavailable")
            raise

    def create_directory_projection(self, link: Path, target: Path) -> None:
        if os.name == "nt":
            result = subprocess.run(
                ["cmd", "/d", "/c", "mklink", "/J", str(link), str(target)],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr or result.stdout)
        else:
            link.symlink_to("../../GitHub/project-conventions", target_is_directory=True)

    def run_command(
        self, root: Path, *arguments: str
    ) -> subprocess.CompletedProcess[str]:
        return subprocess.run(
            [
                sys.executable,
                str(SCRIPT),
                str(root),
                "--max-depth",
                "7",
                *arguments,
            ],
            check=False,
            capture_output=True,
            text=True,
        )

    def run_inspector(self, root: Path) -> dict[str, object]:
        result = self.run_command(root, "--format", "json")
        self.assertEqual(result.returncode, 0, result.stderr)
        return json.loads(result.stdout)

    def init_git(self, path: Path, remote: str | None = None) -> None:
        path.mkdir(parents=True, exist_ok=True)
        result = subprocess.run(
            ["git", "init", "-q", str(path)],
            check=False,
            capture_output=True,
            text=True,
        )
        self.assertEqual(result.returncode, 0, result.stderr)
        if remote:
            result = subprocess.run(
                ["git", "-C", str(path), "remote", "add", "origin", remote],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 0, result.stderr)

    def test_normalizes_ssh_url_userinfo(self) -> None:
        self.assertEqual(
            INSPECTOR.normalize_remote_identity(
                "ssh://git@github.com/Owner/Repo.git"
            ),
            "github.com/owner/repo",
        )
        self.assertTrue(
            INSPECTOR.remotes_equivalent(
                "ssh://git@github.com/Owner/Repo.git",
                "https://github.com/owner/repo",
            )
        )

    def test_expands_collection_member_index_for_git_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            indexes = root / "_project-catalog" / "docs" / "indexes"
            indexes.mkdir(parents=True)
            collection = root / "skill-collection"
            members = collection / "skills" / "docs" / "indexes"
            members.mkdir(parents=True)
            (collection / "member-a" / "src" / ".git").mkdir(parents=True)
            (root / "ordinary" / ".git").mkdir(parents=True)

            (indexes / "00-collections.md").write_text(
                "| key | name | path | kind | members_index | purpose | tags |\n"
                "|---|---|---|---|---|---|---|\n"
                "| skills | Skills | skill-collection | collection | "
                "skills/docs/indexes/members.md | Test | skill |\n",
                encoding="utf-8",
            )
            (indexes / "03-local-only.md").write_text(
                "| key | name | path | vcs | remote | purpose | tags | update |\n"
                "|---|---|---|---|---|---|---|---|\n"
                "| ordinary | Ordinary | ordinary | local_git | - | Test | test | manual |\n",
                encoding="utf-8",
            )
            (members / "members.md").write_text(
                "| key | name | path | role | source | vcs | remote | category | status | tags |\n"
                "|---|---|---|---|---|---|---|---|---|---|\n"
                "| manager | Manager | skills | collection-control | src | none | - | local-only | active | control |\n"
                "| member-a | Member A | member-a | member | src | local_git | - | local-only | active | skill |\n",
                encoding="utf-8",
            )

            report = self.run_inspector(root)
            self.assertEqual(report["schema"], "projects-workspace-inspection/v3")
            self.assertEqual(report["collection_expansions"][0]["members"], 2)
            expanded_paths = {
                entry["path"]
                for entry in report["index_entries"]
                if entry["kind"] == "collection-member"
            }
            self.assertEqual(
                expanded_paths,
                {"skill-collection/skills", "skill-collection/member-a"},
            )
            findings = {
                (finding["type"], finding["path"])
                for finding in report["findings"]
            }
            self.assertNotIn(
                ("unindexed_directory", "skill-collection"), findings
            )
            self.assertNotIn(
                ("unindexed_git_root", "skill-collection/member-a/src"),
                findings,
            )
            self.assertNotIn(
                ("unindexed_git_root", "ordinary"), findings
            )
            self.assertNotIn(
                ("repository_root_mismatch", "skill-collection/member-a"),
                findings,
            )

    def test_missing_member_index_does_not_mask_nested_git(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            indexes = root / "_project-catalog" / "docs" / "indexes"
            indexes.mkdir(parents=True)
            (root / "skill-collection" / "member-a" / ".git").mkdir(
                parents=True
            )
            (indexes / "00-collections.md").write_text(
                "| key | name | path | kind | members_index | purpose | tags |\n"
                "|---|---|---|---|---|---|---|\n"
                "| skills | Skills | skill-collection | collection | "
                "skills/docs/indexes/members.md | Test | skill |\n",
                encoding="utf-8",
            )

            report = self.run_inspector(root)
            findings = {
                (finding["type"], finding["path"])
                for finding in report["findings"]
            }
            self.assertIn(
                (
                    "collection_index_missing",
                    "skill-collection/skills/docs/indexes/members.md",
                ),
                findings,
            )
            self.assertIn(
                ("unindexed_git_root", "skill-collection/member-a"),
                findings,
            )

    def test_collection_symlink_is_not_followed(self) -> None:
        with tempfile.TemporaryDirectory() as raw, tempfile.TemporaryDirectory() as external:
            root = Path(raw)
            indexes = root / "_project-catalog" / "docs" / "indexes"
            indexes.mkdir(parents=True)
            outside = Path(external)
            (outside / "skills" / "docs" / "indexes").mkdir(parents=True)
            (outside / "skills" / "docs" / "indexes" / "members.md").write_text(
                "| key | name | path | role | source | vcs | remote | category | status | tags |\n"
                "|---|---|---|---|---|---|---|---|---|---|\n"
                "| leaked | Leaked | leaked | member | src | none | - | local-only | active | test |\n",
                encoding="utf-8",
            )
            self.create_symlink(
                root / "linked-collection", outside, target_is_directory=True
            )
            (indexes / "00-collections.md").write_text(
                "| key | name | path | kind | members_index | purpose | tags |\n"
                "|---|---|---|---|---|---|---|\n"
                "| linked | Linked | linked-collection | collection | "
                "skills/docs/indexes/members.md | Test | skill |\n",
                encoding="utf-8",
            )

            report = self.run_inspector(root)
            findings = {
                (finding["type"], finding["path"])
                for finding in report["findings"]
            }
            self.assertIn(
                ("collection_path_link", "linked-collection"), findings
            )
            expanded = [
                entry
                for entry in report["index_entries"]
                if entry["kind"] == "collection-member"
            ]
            self.assertEqual(expanded, [])

    def test_repository_root_mismatch_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            indexes = root / "_project-catalog" / "docs" / "indexes"
            indexes.mkdir(parents=True)
            collection = root / "skill-collection"
            members = collection / "skills" / "docs" / "indexes"
            members.mkdir(parents=True)
            (collection / "member-a" / ".git").mkdir(parents=True)
            (collection / "member-a" / "src").mkdir()
            (indexes / "00-collections.md").write_text(
                "| key | name | path | kind | members_index | purpose | tags |\n"
                "|---|---|---|---|---|---|---|\n"
                "| skills | Skills | skill-collection | collection | "
                "skills/docs/indexes/members.md | Test | skill |\n",
                encoding="utf-8",
            )
            (members / "members.md").write_text(
                "| key | name | path | role | source | repository_root | vcs | remote | managed_scope | category | status | tags |\n"
                "|---|---|---|---|---|---|---|---|---|---|---|---|\n"
                "| member-a | Member A | member-a | collection-control | src | member-a/src | local_git | - | whole repository | local-only | active | skill |\n",
                encoding="utf-8",
            )

            report = self.run_inspector(root)
            mismatches = [
                finding["path"]
                for finding in report["findings"]
                if finding["type"] == "repository_root_mismatch"
            ]
            self.assertEqual(len(mismatches), 1)
            self.assertIn(
                "expected=skill-collection/member-a/src", mismatches[0]
            )
            self.assertIn(
                "observed=skill-collection/member-a", mismatches[0]
            )

    def test_shared_repository_projection_is_valid_and_covers_git(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            indexes = root / "_project-catalog" / "docs" / "indexes"
            indexes.mkdir(parents=True)
            collection = root / "skill-collection"
            members = collection / "skills" / "docs" / "indexes"
            members.mkdir(parents=True)
            repository = collection / "GitHub"
            self.init_git(repository, "https://github.com/obisoldbee/skills.git")
            package = repository / "project-conventions"
            package.mkdir()
            (package / "SKILL.md").write_text("fixture\n", encoding="utf-8")
            wrapper_source = collection / "project-conventions" / "src"
            wrapper_source.mkdir(parents=True)
            self.create_directory_projection(
                wrapper_source / "project-conventions", package
            )
            (indexes / "00-collections.md").write_text(
                "| key | name | path | kind | members_index | purpose | tags |\n"
                "|---|---|---|---|---|---|---|\n"
                "| skills | Skills | skill-collection | collection | "
                "skills/docs/indexes/members.md | Test | skill |\n",
                encoding="utf-8",
            )
            (members / "members.md").write_text(
                "| key | name | path | role | source | repository_root | vcs | remote | managed_scope | category | status | tags |\n"
                "|---|---|---|---|---|---|---|---|---|---|---|---|\n"
                "| manager | Manager | skills | collection-control | src | - | none | - | local control files | local-only | active | control |\n"
                "| project-conventions | Project Conventions | project-conventions | member | src/project-conventions | GitHub | git | obisoldbee/skills | project-conventions/ | personal-open | active | skill |\n",
                encoding="utf-8",
            )

            report = self.run_inspector(root)
            finding_types = {finding["type"] for finding in report["findings"]}
            for forbidden in {
                "collection_member_source_link",
                "collection_member_projection_invalid",
                "collection_member_projection_mismatch",
                "repository_root_mismatch",
                "vcs_state_mismatch",
                "unindexed_git_root",
            }:
                self.assertNotIn(forbidden, finding_types)
            member = next(
                entry
                for entry in report["index_entries"]
                if entry["key"] == "skills/project-conventions"
            )
            self.assertEqual(member["repository_root"], "skill-collection/GitHub")
            self.assertEqual(member["managed_scope"], "project-conventions/")

    def test_shared_repository_real_source_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            indexes = root / "_project-catalog" / "docs" / "indexes"
            indexes.mkdir(parents=True)
            collection = root / "skill-collection"
            members = collection / "skills" / "docs" / "indexes"
            members.mkdir(parents=True)
            self.init_git(collection / "GitHub")
            (collection / "GitHub" / "project-conventions").mkdir()
            (collection / "project-conventions" / "src" / "project-conventions").mkdir(parents=True)
            (indexes / "00-collections.md").write_text(
                "| key | name | path | kind | members_index | purpose | tags |\n"
                "|---|---|---|---|---|---|---|\n"
                "| skills | Skills | skill-collection | collection | skills/docs/indexes/members.md | Test | skill |\n",
                encoding="utf-8",
            )
            (members / "members.md").write_text(
                "| key | name | path | role | source | repository_root | vcs | remote | managed_scope | category | status | tags |\n"
                "|---|---|---|---|---|---|---|---|---|---|---|---|\n"
                "| manager | Manager | skills | collection-control | src | - | none | - | local control files | local-only | active | control |\n"
                "| pc | PC | project-conventions | member | src/project-conventions | GitHub | local_git | - | project-conventions/ | local-only | active | skill |\n",
                encoding="utf-8",
            )
            report = self.run_inspector(root)
            self.assertIn(
                "collection_member_projection_not_link",
                {finding["type"] for finding in report["findings"]},
            )

    def test_external_indexes_directory_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw, tempfile.TemporaryDirectory() as external:
            root = Path(raw)
            outside = Path(external)
            result = subprocess.run(
                [
                    sys.executable,
                    str(SCRIPT),
                    str(root),
                    "--indexes-dir",
                    str(outside),
                ],
                check=False,
                capture_output=True,
                text=True,
            )
            self.assertEqual(result.returncode, 2)
            self.assertIn(
                "indexes directory escapes Projects Workspace", result.stderr
            )

    def test_missing_member_source_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            indexes = root / "_project-catalog" / "docs" / "indexes"
            indexes.mkdir(parents=True)
            collection = root / "skill-collection"
            members = collection / "skills" / "docs" / "indexes"
            members.mkdir(parents=True)
            (indexes / "00-collections.md").write_text(
                "| key | name | path | kind | members_index | purpose | tags |\n"
                "|---|---|---|---|---|---|---|\n"
                "| skills | Skills | skill-collection | collection | "
                "skills/docs/indexes/members.md | Test | skill |\n",
                encoding="utf-8",
            )
            (members / "members.md").write_text(
                "| key | name | path | role | source | vcs | remote | category | status | tags |\n"
                "|---|---|---|---|---|---|---|---|---|---|\n"
                "| manager | Manager | skills | collection-control | missing-src | none | - | local-only | active | control |\n",
                encoding="utf-8",
            )

            report = self.run_inspector(root)
            findings = {
                (finding["type"], finding["path"])
                for finding in report["findings"]
            }
            self.assertIn(
                (
                    "collection_member_source_missing",
                    "skill-collection/skills/missing-src",
                ),
                findings,
            )

    def test_requires_exactly_one_collection_control_role(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            indexes = root / "_project-catalog" / "docs" / "indexes"
            indexes.mkdir(parents=True)
            collection = root / "skill-collection"
            members = collection / "skills" / "docs" / "indexes"
            members.mkdir(parents=True)
            (collection / "member-a" / "src").mkdir(parents=True)
            (indexes / "00-collections.md").write_text(
                "| key | name | path | kind | members_index | purpose | tags |\n"
                "|---|---|---|---|---|---|---|\n"
                "| skills | Skills | skill-collection | collection | "
                "skills/docs/indexes/members.md | Test | skill |\n",
                encoding="utf-8",
            )
            (members / "members.md").write_text(
                "| key | name | path | role | source | vcs | remote | category | status | tags |\n"
                "|---|---|---|---|---|---|---|---|---|---|\n"
                "| member-a | Member A | member-a | member | src | none | - | local-only | active | skill |\n",
                encoding="utf-8",
            )

            report = self.run_inspector(root)
            types = {finding["type"] for finding in report["findings"]}
            self.assertIn("collection_control_role_invalid", types)

    def test_member_index_symlink_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            indexes = root / "_project-catalog" / "docs" / "indexes"
            indexes.mkdir(parents=True)
            collection = root / "skill-collection"
            members_dir = collection / "skills" / "docs" / "indexes"
            members_dir.mkdir(parents=True)
            real_members = members_dir / "members-source.txt"
            real_members.write_text(
                "| key | name | path | role | source | vcs | remote | category | status | tags |\n"
                "|---|---|---|---|---|---|---|---|---|---|\n"
                "| manager | Manager | skills | collection-control | src | none | - | local-only | active | control |\n",
                encoding="utf-8",
            )
            self.create_symlink(members_dir / "members.md", real_members)
            (indexes / "00-collections.md").write_text(
                "| key | name | path | kind | members_index | purpose | tags |\n"
                "|---|---|---|---|---|---|---|\n"
                "| skills | Skills | skill-collection | collection | "
                "skills/docs/indexes/members.md | Test | skill |\n",
                encoding="utf-8",
            )

            report = self.run_inspector(root)
            findings = {
                (finding["type"], finding["path"])
                for finding in report["findings"]
            }
            self.assertIn(
                (
                    "index_path_link",
                    "skill-collection/skills/docs/indexes/members.md",
                ),
                findings,
            )
            self.assertEqual(report["collection_expansions"], [])

    def test_vcs_state_mismatch_is_reported_both_ways(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            indexes = root / "_project-catalog" / "docs" / "indexes"
            indexes.mkdir(parents=True)
            (root / "declared-none" / ".git").mkdir(parents=True)
            (root / "missing-git").mkdir()
            (indexes / "03-local-only.md").write_text(
                "| key | name | path | vcs | remote | purpose | tags | update |\n"
                "|---|---|---|---|---|---|---|---|\n"
                "| declared-none | None | declared-none | none | - | Test | test | manual |\n"
                "| missing-git | Missing | missing-git | local_git | - | Test | test | manual |\n",
                encoding="utf-8",
            )

            report = self.run_inspector(root)
            paths = {
                finding["path"]
                for finding in report["findings"]
                if finding["type"] == "vcs_state_mismatch"
            }
            self.assertEqual(
                paths,
                {
                    "declared-none: declared=none, observed=git",
                    "missing-git: declared=local_git, observed=none",
                },
            )

    def test_duplicate_key_and_path_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            indexes = root / "_project-catalog" / "docs" / "indexes"
            indexes.mkdir(parents=True)
            (root / "shared").mkdir()
            (indexes / "03-local-only.md").write_text(
                "| key | name | path | vcs | remote | purpose | tags | update |\n"
                "|---|---|---|---|---|---|---|---|\n"
                "| duplicate | First | shared | none | - | Test | test | manual |\n"
                "| duplicate | Second | shared | none | - | Test | test | manual |\n",
                encoding="utf-8",
            )

            report = self.run_inspector(root)
            types = {finding["type"] for finding in report["findings"]}
            self.assertIn("duplicate_key", types)
            self.assertIn("duplicate_path", types)

    def test_remote_mismatch_and_nested_git_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            indexes = root / "_project-catalog" / "docs" / "indexes"
            indexes.mkdir(parents=True)
            self.init_git(
                root / "remote-project",
                "ssh://git@github.com/example/actual.git",
            )
            self.init_git(root / "nested-project")
            self.init_git(root / "nested-project" / "vendor")
            (indexes / "01-personal-open.md").write_text(
                "| key | name | path | vcs | remote | purpose | tags | update |\n"
                "|---|---|---|---|---|---|---|---|\n"
                "| remote | Remote | remote-project | git | example/expected | Test | test | manual |\n"
                "| nested | Nested | nested-project | local_git | - | Test | test | manual |\n",
                encoding="utf-8",
            )

            report = self.run_inspector(root)
            findings = {
                (finding["type"], finding["path"])
                for finding in report["findings"]
            }
            self.assertIn(("remote_mismatch", "remote-project"), findings)
            self.assertIn(("nested_git_detected", "nested-project"), findings)

    def test_invalid_reserved_and_missing_paths_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            indexes = root / "_project-catalog" / "docs" / "indexes"
            indexes.mkdir(parents=True)
            (indexes / "03-local-only.md").write_text(
                "| key | name | path | vcs | remote | purpose | tags | update |\n"
                "|---|---|---|---|---|---|---|---|\n"
                "| escape | Escape | ../escape | none | - | Test | test | manual |\n"
                "| reserved | Reserved | _project-catalog | none | - | Test | test | manual |\n"
                "| missing | Missing | missing | none | - | Test | test | manual |\n",
                encoding="utf-8",
            )

            report = self.run_inspector(root)
            types = {finding["type"] for finding in report["findings"]}
            self.assertIn("invalid_index_path", types)
            self.assertIn("reserved_entry_conflict", types)
            self.assertIn("indexed_path_missing", types)

    def test_index_symlink_and_dangling_link_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            indexes = root / "_project-catalog" / "docs" / "indexes"
            indexes.mkdir(parents=True)
            source = indexes / "source.txt"
            source.write_text("not an index\n", encoding="utf-8")
            self.create_symlink(indexes / "linked.md", source)
            self.create_symlink(root / "broken-link", root / "missing-target")

            report = self.run_inspector(root)
            types = {finding["type"] for finding in report["findings"]}
            self.assertIn("index_path_link", types)
            self.assertIn("dangling_link", types)

    def test_unindexed_directory_and_git_root_are_reported(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            (root / "_project-catalog" / "docs" / "indexes").mkdir(
                parents=True
            )
            (root / "orphan" / ".git").mkdir(parents=True)

            report = self.run_inspector(root)
            findings = {
                (finding["type"], finding["path"])
                for finding in report["findings"]
            }
            self.assertIn(("unindexed_directory", "orphan"), findings)
            self.assertIn(("unindexed_git_root", "orphan"), findings)

    def test_markdown_includes_details_and_lowercase_booleans(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            indexes = root / "_project-catalog" / "docs" / "indexes"
            indexes.mkdir(parents=True)
            (root / "project-a").mkdir()
            (indexes / "03-local-only.md").write_text(
                "| key | name | path | vcs | remote | purpose | tags | update |\n"
                "|---|---|---|---|---|---|---|---|\n"
                "| project-a | Project A | project-a | none | - | Test | test | manual |\n",
                encoding="utf-8",
            )

            result = self.run_command(root, "--format", "markdown")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertIn("## Index entries", result.stdout)
            self.assertIn("## Git roots", result.stdout)
            self.assertIn("| `project-a` | `project-a` |", result.stdout)
            self.assertNotIn("True", result.stdout)
            self.assertNotIn("False", result.stdout)

    def test_custom_indexes_directory_inside_workspace_is_supported(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            indexes = root / "custom-indexes"
            indexes.mkdir()
            (root / "project-a").mkdir()
            (indexes / "projects.md").write_text(
                "| key | name | path | vcs | remote | purpose | tags | update |\n"
                "|---|---|---|---|---|---|---|---|\n"
                "| project-a | Project A | project-a | none | - | Test | test | manual |\n",
                encoding="utf-8",
            )

            result = self.run_command(
                root,
                "--indexes-dir",
                str(indexes),
                "--format",
                "json",
            )
            self.assertEqual(result.returncode, 0, result.stderr)
            report = json.loads(result.stdout)
            indexed = {entry["path"] for entry in report["index_entries"]}
            self.assertIn("project-a", indexed)

    def test_archived_member_does_not_claim_live_coverage(self) -> None:
        with tempfile.TemporaryDirectory() as raw:
            root = Path(raw)
            indexes = root / "_project-catalog" / "docs" / "indexes"
            indexes.mkdir(parents=True)
            collection = root / "skill-collection"
            members = collection / "skills" / "docs" / "indexes"
            members.mkdir(parents=True)
            (collection / "skills" / "src").mkdir()
            (collection / "old-member" / "src" / ".git").mkdir(parents=True)
            (collection / "bad-member" / "src").mkdir(parents=True)
            (indexes / "00-collections.md").write_text(
                "| key | name | path | kind | members_index | purpose | tags |\n"
                "|---|---|---|---|---|---|---|\n"
                "| skills | Skills | skill-collection | collection | "
                "skills/docs/indexes/members.md | Test | skill |\n",
                encoding="utf-8",
            )
            (members / "members.md").write_text(
                "| key | name | path | role | source | vcs | remote | category | status | tags |\n"
                "|---|---|---|---|---|---|---|---|---|---|\n"
                "| manager | Manager | skills | collection-control | src | none | - | local-only | active | control |\n"
                "| old | Old | old-member | member | src | local_git | - | local-only | archived | old |\n"
                "| bad | Bad | bad-member | member | src | none | - | local-only | stale | bad |\n",
                encoding="utf-8",
            )

            report = self.run_inspector(root)
            findings = {
                (finding["type"], finding["path"])
                for finding in report["findings"]
            }
            self.assertIn(
                ("unindexed_git_root", "skill-collection/old-member/src"),
                findings,
            )
            self.assertTrue(
                any(
                    finding["type"] == "collection_member_status_invalid"
                    for finding in report["findings"]
                )
            )

    def test_publishable_package_has_no_local_artifacts_or_paths(self) -> None:
        package_root = SCRIPT.parent.parent
        forbidden_names = {".DS_Store", "__pycache__"}
        text_suffixes = {
            ".json",
            ".md",
            ".ps1",
            ".py",
            ".sh",
            ".toml",
            ".tsv",
            ".yaml",
            ".yml",
        }
        personal_home_marker = "/" + "Users" + "/"
        personal_windows_marker = "C:" + "\\Users\\"
        local_uri_marker = "file" + "://"
        violations: list[str] = []
        for path in package_root.rglob("*"):
            relative = path.relative_to(package_root).as_posix()
            if path.name in forbidden_names or path.suffix == ".pyc":
                violations.append(relative)
                continue
            if path.is_file() and path.suffix in text_suffixes:
                content = path.read_text(encoding="utf-8")
                if (
                    personal_home_marker in content
                    or personal_windows_marker in content
                    or local_uri_marker in content
                ):
                    violations.append(relative)
        self.assertEqual(violations, [])


if __name__ == "__main__":
    unittest.main()
