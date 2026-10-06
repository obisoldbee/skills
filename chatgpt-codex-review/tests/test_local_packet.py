"""Offline local packaging, routing and upload/readback lifecycle regressions."""
import copy
import json
from pathlib import Path
import tempfile
import unittest
from unittest import mock
import zipfile

from test_source_and_artifacts import load, git
from test_review_cycle import (HELPER, state, event, apply, observation,
                               submission, preparation)

PACKET = load("local_packet")
ROUTE = load("route_source")


class PacketTests(unittest.TestCase):
    def selection(self):
        return {"scope": "documents and current source", "authority_ref": "user review request",
                "files": ["原文.md", "src/code.py"],
                "exclusions": [{"path": "missing.pdf", "reason": "not available; not claimed read"}]}

    def inputs(self, root):
        (root / "src").mkdir()
        (root / "原文.md").write_bytes("# 原始要求\r\n保留原文。\r\n".encode())
        (root / "src/code.py").write_bytes(b"value = 1\n")

    def build(self, root, name="packet"):
        return PACKET.build_packet(root, self.selection(), root / name)

    def route(self, root, packet, **extra):
        return ROUTE.select(root, {"source_route": "local_packet", "local_packet": packet["local_packet"], **extra})

    def bind(self, current, packet):
        current.update(source_route="local_packet", source_id=packet["source_id"],
                       source_binding=packet["source_binding"])
        current["source_binding_digest"] = HELPER.source_binding_digest(
            "local_packet", current["source_id"], current["source_binding"])
        current["prepared_request"] = None
        return current

    def upload(self, packet):
        return {**packet["source_binding"], "archive_name": "source.zip", "upload_complete": True,
                "evidence_ref": "browser/actual-upload-and-message.json"}

    def test_packet_preserves_originals_and_has_reproducible_identity(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.inputs(root)
            packet = self.build(root)
            self.assertEqual(packet["source_id"], self.build(root, "packet-copy")["source_id"])
            with zipfile.ZipFile(packet["local_packet"]["archive_path"]) as archive:
                for name in self.selection()["files"]:
                    self.assertEqual((root / name).read_bytes(), archive.read("files/" + name))
                self.assertEqual(Path(packet["local_packet"]["manifest_path"]).read_bytes(), archive.read(PACKET.MANIFEST))
            result = self.route(root, packet)
            self.assertEqual("ready_to_upload", result["status"])
            self.assertFalse(result["uploaded"])
            self.assertFalse(result["web_read_verified"])
            self.assertEqual(2, result["local_packet"]["file_count"])

    def test_existing_output_and_unsafe_scope_are_not_modified(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.inputs(root)
            packet = self.build(root)
            before = Path(packet["local_packet"]["archive_path"]).read_bytes()
            with self.assertRaises(FileExistsError):
                self.build(root)
            self.assertEqual(before, Path(packet["local_packet"]["archive_path"]).read_bytes())
            (root / "alias.md").symlink_to(root / "原文.md")
            (root / ".env").write_text("synthetic")
            for names in (["../outside"], ["alias.md"], ["原文.md", "原文.md"], [".env"], ["unknown"]):
                with self.subTest(names=names), self.assertRaises(ValueError):
                    PACKET.build_packet(root, {**self.selection(), "files": names}, root / "bad")
                self.assertFalse((root / "bad").exists())

    def test_tampered_zip_or_manifest_never_becomes_ready(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.inputs(root)
            packet = self.build(root)
            manifest = Path(packet["local_packet"]["manifest_path"])
            manifest.write_bytes(manifest.read_bytes() + b"\n")
            with self.assertRaisesRegex(ValueError, "embedded manifest"):
                self.route(root, packet)
            packet = self.build(root, "another")
            archive_path = Path(packet["local_packet"]["archive_path"])
            with zipfile.ZipFile(archive_path) as archive:
                contents = {name: archive.read(name) for name in archive.namelist()}
            contents["files/src/code.py"] = b"value = 2\n"
            with zipfile.ZipFile(archive_path, "w") as archive:
                for name, data in contents.items():
                    archive.writestr(name, data)
            with self.assertRaisesRegex(ValueError, "hash mismatch"):
                self.route(root, packet)

    def test_source_change_during_build_is_rejected_without_partial_packet(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.inputs(root)
            actual = PACKET.shutil.copyfileobj
            def mutate(source, destination):
                actual(source, destination)
                (root / "src/code.py").write_bytes(b"changed during freeze\n")
            with mock.patch.object(PACKET.shutil, "copyfileobj", side_effect=mutate):
                with self.assertRaisesRegex(ValueError, "mismatch|changed"):
                    self.build(root)
            self.assertFalse((root / "packet").exists())
            self.assertEqual(b"changed during freeze\n", (root / "src/code.py").read_bytes())

    def test_no_mcp_or_github_is_not_a_review_blocker(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.assertEqual("packet_needed", ROUTE.select(root, {})["status"])
            self.assertEqual("mcp_connection_needed", ROUTE.select(root, {"source_route": "mcp"})["status"])
            self.inputs(root)
            packet = self.build(root)
            git(root, "init", "-q")
            git(root, "remote", "add", "origin", "https://github.com/owner/private.git")
            self.assertEqual("ready_to_upload", self.route(root, packet)["status"])
            self.assertEqual("local_packet", ROUTE.select(root, {})["route"])
            git(root, "add", "原文.md", "src/code.py")
            git(root, "-c", "user.name=T", "-c", "user.email=t@example.test", "commit", "-qm", "initial")
            self.assertEqual("local_packet", ROUTE.select(root, {})["route"])
            observed = {"github": {"repository": "owner/private", "commit": git(root, "rev-parse", "HEAD"),
                                   "remote_has_commit": False, "web_can_read": False,
                                   "dirty_scope_disposition": "excluded_from_review", "dirty_scope_evidence_ref": "packet outputs"}}
            self.assertEqual("local_packet", ROUTE.select(root, observed)["route"])
            self.assertEqual("github_access_blocked", ROUTE.select(root, {**observed, "source_route": "github"})["status"])

    def test_materials_only_never_authorizes_upload_or_submission(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.inputs(root)
            packet = self.build(root)
            current = self.bind(state("ready_to_submit"), packet)
            current["execution_scope"] = "materials_only"
            prepared = HELPER.decide(current, preparation(current))
            self.assertEqual("deliver_prepared_request", prepared["action"])
            current = apply(current, prepared)
            with self.assertRaisesRegex(ValueError, "materials-only"):
                HELPER.decide(current, {**submission(current), "source_upload": self.upload(packet)})

    def test_local_packet_can_send_read_review_and_repair_as_a_new_version(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            self.inputs(root)
            packet = self.build(root)
            current = self.bind(state("ready_to_submit"), packet)
            current = apply(current, HELPER.decide(current, preparation(current)))
            sent = submission(current)
            with self.assertRaisesRegex(ValueError, "completed upload"):
                HELPER.decide(current, sent)
            sent["source_upload"] = self.upload(packet)
            wrong = copy.deepcopy(sent)
            wrong["source_upload"]["archive_sha256"] = "0" * 64
            with self.assertRaisesRegex(ValueError, "matching hashes"):
                HELPER.decide(current, wrong)
            current = apply(current, HELPER.decide(current, sent))
            self.assertEqual("waiting_web", current["phase"])
            current = apply(current, HELPER.decide(current, observation(current)))
            current = apply(current, HELPER.decide(current, observation(current, 10)))
            assessment = event(current, "assessment", review_message_id="message-1", coverage_complete=True,
                               confirmed_findings=1, unresolved_claims=0)
            with self.assertRaisesRegex(ValueError, "source-content readback"):
                HELPER.decide(current, assessment)
            assessment.update(source_readback_id=current["source_id"], source_readback_ref="web/full-file-reading.json")
            current = apply(current, HELPER.decide(current, assessment))
            self.assertEqual("repairing", current["phase"])
            (root / "src/code.py").write_bytes(b"value = 2\n")
            revision = self.build(root, "revision")
            self.assertNotEqual(packet["source_id"], revision["source_id"])
            current = apply(current, HELPER.decide(current, event(current, "worker_result",
                candidate_source_id=revision["source_id"], delivery_path="worker/packet.json")))
            next_state = HELPER.decide(current, event(current, "validation",
                checked_source_id=revision["source_id"], passed=True, required_unverified=[],
                next_request_token="round-2", next_source_binding=revision["source_binding"]))
            self.assertEqual("prepare_review_request", next_state["action"])
            self.assertEqual(revision["source_id"], next_state["state_updates"]["source_id"])
            self.assertIsNone(next_state["state_updates"]["source_upload"])
            self.assertEqual(2, next_state["state_updates"]["round"])


if __name__ == "__main__":
    unittest.main()
