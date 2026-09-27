"""Offline route and saved-file verification using real temporary files."""

import hashlib
import importlib.util
import json
from pathlib import Path
import subprocess
import tempfile
import unittest
import zipfile

ROOT = Path(__file__).resolve().parents[1]


def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


ROUTE = load("route_source")
FILES = load("verify_artifacts")


def git(root, *args):
    result = subprocess.run(["git", "-C", str(root), *args], capture_output=True, text=True)
    if result.returncode:
        raise AssertionError(result.stderr)
    return result.stdout.strip()


def binding(root):
    return {"run_id": "run", "round": 2, "source_id": "git:" + "a" * 40,
            "request_token": "token-2", "consumer_host": "host-1", "artifact_root": str(root)}


class RouteTests(unittest.TestCase):
    def test_github_route_is_sticky_when_access_fails_and_sanitizes_credentials(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            git(root, "init", "-q")
            (root / "a.txt").write_text("hello", encoding="utf-8")
            git(root, "add", "a.txt")
            git(root, "-c", "user.name=T", "-c", "user.email=t@example.test", "commit", "-qm", "initial")
            head = git(root, "rev-parse", "HEAD")
            git(root, "remote", "add", "upstream", "https://gitlab.com/a/b.git")
            git(root, "remote", "add", "origin", "https://user:secret@github.com/owner/project.git")
            pending = ROUTE.select(root, {})
            self.assertEqual((pending["route"], pending["status"]),
                             ("github", "verify_remote_commit_and_web_access"))
            self.assertEqual(pending["remote_url"], "https://github.com/owner/project.git")
            self.assertNotIn("secret", json.dumps(pending))
            observed = {"github": {"repository": "owner/project", "commit": head,
                                   "remote_has_commit": False, "web_can_read": False}}
            self.assertEqual(ROUTE.select(root, observed)["status"], "github_access_blocked")
            observed["github"].update(remote_has_commit=True, web_can_read=True,
                                      evidence_ref="tool/readback.json")
            self.assertEqual(ROUTE.select(root, observed)["status"], "ready")
            (root / "unrelated.txt").write_text("untracked", encoding="utf-8")
            self.assertEqual(ROUTE.select(root, observed)["status"], "freeze_commit")
            observed["github"].update(dirty_scope_disposition="excluded_from_review",
                                      dirty_scope_evidence_ref="scope/checked.json")
            self.assertEqual(ROUTE.select(root, observed)["status"], "ready")

    def test_local_git_without_github_and_plain_directory_use_mcp(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertEqual(ROUTE.select(root, {})["status"], "mcp_connection_needed")
            git(root, "init", "-q")
            git(root, "remote", "add", "origin", "https://gitlab.com/a/b.git")
            self.assertEqual(ROUTE.select(root, {})["route"], "mcp")
            evidence = {"mcp": {"configured": True, "server": "host-server", "tool": "read_content",
                                "version": "v1", "snapshot_sha256": "c" * 64,
                                "manifest_sha256": "d" * 64, "evidence_ref": "tool/readback.json"}}
            self.assertEqual(ROUTE.select(root, evidence)["source_id"], "mcp:" + "c" * 64)
            git(root, "remote", "set-url", "origin", "https://github.com/owner/project.git")
            self.assertEqual(ROUTE.select(root, evidence)["route"], "github")

    def test_unknown_github_url_never_becomes_mcp(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            git(root, "init", "-q")
            git(root, "remote", "add", "origin", "https://github.com/owner/project/extra")
            self.assertEqual(ROUTE.select(root, {})["route"], "unknown")

    def test_declared_github_repository_without_local_remote_needs_verified_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            url = "https://user:secret@github.com/owner/project.git"
            self.assertEqual(ROUTE.select(root, {"declared_github_url": url})["route"], "unknown")
            observed = {"declared_github_url": url,
                        "github": {"repository_verified": True, "repository": "owner/project",
                                   "commit": "a" * 40, "remote_has_commit": True,
                                   "web_can_read": True, "evidence_ref": "tool/repository.json"}}
            result = ROUTE.select(root, observed)
            self.assertEqual((result["route"], result["status"]), ("github", "ready"))
            self.assertIsNone(result["working_tree_dirty"])
            self.assertNotIn("secret", json.dumps(result))


class ArtifactTests(unittest.TestCase):
    def document(self, root, required, optional=None, files=None):
        return {"binding": binding(root), "artifact_contract":
                {"required": required, "optional": optional or []}, "files": files or {}}

    def test_no_required_and_optional_missing_are_ready(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            optional = [{"name": "preview", "kind": "png"}]
            result = FILES.verify(self.document(root, [], optional))
            self.assertTrue(result["required_ready"])
            self.assertEqual(result["files"]["preview"]["status"], "missing")

    def test_hash_json_utf8_and_root_boundary(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            saved = root / "body.json"
            saved.write_text('{"ok": true}', encoding="utf-8")
            sha = hashlib.sha256(saved.read_bytes()).hexdigest()
            required = [{"name": "body", "kind": "json", "sha256": sha, "size": saved.stat().st_size}]
            doc = self.document(root, required, files={"body": str(saved)})
            report = FILES.verify(doc)
            self.assertTrue(report["required_ready"])
            self.assertTrue(report["files"]["body"]["origin_hash_matched"])
            doc["artifact_contract"]["required"][0]["sha256"] = "0" * 64
            self.assertEqual(FILES.verify(doc)["files"]["body"]["status"], "invalid")
            saved.write_bytes(b"\xff")
            del doc["artifact_contract"]["required"][0]["sha256"]
            self.assertEqual(FILES.verify(doc)["files"]["body"]["status"], "invalid")
            outside = root.parent / (root.name + "-outside")
            outside.write_text("{}", encoding="utf-8")
            try:
                doc["files"]["body"] = str(outside)
                self.assertEqual(FILES.verify(doc)["files"]["body"]["status"], "invalid")
            finally:
                outside.unlink()

    def test_zip_crc_traversal_alias_and_fake_zip(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            saved = root / "report.zip"
            required = [{"name": "report", "kind": "zip"}]
            doc = self.document(root, required, files={"report": str(saved)})
            with zipfile.ZipFile(saved, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                archive.writestr("safe/report.txt", "accepted")
            self.assertTrue(FILES.verify(doc)["required_ready"])
            self.assertFalse(FILES.verify(doc)["files"]["report"]["origin_hash_matched"])
            for names in (["../escape"], ["Report.txt", "report.TXT"],
                          ["NUL.txt"], ["folder.", "folder./child"],
                          ["file", "file/child"]):
                with self.subTest(names=names):
                    with zipfile.ZipFile(saved, "w") as archive:
                        for name in names:
                            archive.writestr(name, "data")
                    self.assertEqual(FILES.verify(doc)["files"]["report"]["status"], "invalid")
            saved.write_bytes(b"not a zip")
            self.assertEqual(FILES.verify(doc)["files"]["report"]["status"], "invalid")
            with zipfile.ZipFile(saved, "w", compression=zipfile.ZIP_DEFLATED) as archive:
                archive.writestr("stream.bin", b"a" * 1000)
            with zipfile.ZipFile(saved) as archive:
                member = archive.infolist()[0]
                offset = member.header_offset + 30 + len(member.filename.encode()) + len(member.extra)
            broken = bytearray(saved.read_bytes())
            broken[offset] = 0xFF
            saved.write_bytes(broken)
            self.assertEqual(FILES.verify(doc)["files"]["report"]["status"], "invalid")

    def test_malformed_contract_is_clean_error(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            for item in ({"name": 12, "kind": "zip"}, {"name": "x", "kind": ["zip"]}):
                with self.subTest(item=item), self.assertRaises(ValueError):
                    FILES.verify(self.document(root, [item]))

    def test_png_needs_real_decode(self):
        try:
            from PIL import Image
        except ImportError:
            self.skipTest("Pillow not installed on this test host")
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            saved = root / "image.png"
            Image.new("RGB", (2, 2), "red").save(saved)
            doc = self.document(root, [{"name": "image", "kind": "png"}],
                                files={"image": str(saved)})
            self.assertTrue(FILES.verify(doc)["required_ready"])
            saved.write_bytes(b"\x89PNG\r\n\x1a\ninvalid")
            self.assertEqual(FILES.verify(doc)["files"]["image"]["status"], "invalid")


if __name__ == "__main__":
    unittest.main()
