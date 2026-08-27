from __future__ import annotations

import base64
import contextlib
import errno
import http.client
import importlib.util
import io
import json
import os
import socket
import tempfile
import unittest
import urllib.error
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "scripts/agnes_media.py"
SPEC = importlib.util.spec_from_file_location("agnes_boundaries", SCRIPT)
assert SPEC and SPEC.loader
agnes = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(agnes)
CONTENT = b"boundary test media"
PRIVATE = "qa-private-provider-echo"
URL = "https://example.invalid/result?signature=" + PRIVATE


class BoundaryTests(unittest.TestCase):
    def setUp(self):
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.config = self.enterContext(mock.patch.object(
            agnes, "execution_config", return_value=("https://example.invalid", "qa-key")
        ))
        self.credentials = self.enterContext(mock.patch.object(
            agnes, "parse_env_file", side_effect=AssertionError("real credential read forbidden")
        ))
        self.enterContext(mock.patch.object(
            socket, "create_connection", side_effect=AssertionError("network forbidden")
        ))
        self.transport = self.enterContext(mock.patch.object(agnes.urllib.request, "urlopen"))
        self.methods = []

    def response(self, route):
        if route == "video":
            return {"video_id": "qa-video", "status": "completed", "metadata": {"url": URL}}
        item = {"url": URL} if route == "url" else {"b64_json": base64.b64encode(CONTENT).decode()}
        return {"data": [item]}

    def success_transport(self, route):
        def request(value, **kwargs):
            if isinstance(value, str):
                self.methods.append("DOWNLOAD")
                return io.BytesIO(CONTENT)
            self.methods.append(value.method)
            return io.BytesIO(json.dumps(self.response(route)).encode())
        return request

    def cli(self, route, output=None):
        args = ["video" if route == "video" else "image", "--prompt", "QA", "--execute"]
        if route == "video":
            args.extend(["--wait", "--poll-interval", "0.001"])
        if output is not None:
            args.extend(["--output", str(output)])
        with contextlib.redirect_stdout(io.StringIO()) as stdout, contextlib.redirect_stderr(io.StringIO()) as stderr:
            code = agnes.main(args)
        self.assertNotIn(PRIVATE, stdout.getvalue() + stderr.getvalue())
        self.assertNotIn("qa-key", stdout.getvalue() + stderr.getvalue())
        self.credentials.assert_not_called()
        return code, json.loads(stdout.getvalue())

    def require_binding(self):
        if not agnes.DIR_FD_OUTPUT_SUPPORTED:
            self.skipTest("platform lacks directory-relative no-follow primitives")

    def test_actual_request_errors_do_not_echo_body_reason_or_nested_exception(self):
        # Use the real request_json and poll_video paths, not an AgnesError mock.
        for phase in ("POST", "GET"):
            for kind in ("http", "url", "timeout", "protocol", "json", "unicode"):
                with self.subTest(phase=phase, kind=kind):
                    self.methods.clear()
                    bodies = []

                    class Body(io.BytesIO):
                        reads = 0

                        def read(self, *args):
                            self.reads += 1
                            return super().read(*args)

                    def request(value, **kwargs):
                        self.methods.append(value.method)
                        if phase == "GET" and value.method == "POST":
                            return io.BytesIO(b'{"video_id":"qa-video","status":"queued"}')
                        if kind == "http":
                            body = Body((PRIVATE + " " + URL).encode())
                            bodies.append(body)
                            raise urllib.error.HTTPError(value.full_url, 503, PRIVATE, {"private": PRIVATE}, body)
                        if kind == "url":
                            raise urllib.error.URLError(OSError(PRIVATE + " " + URL))
                        if kind == "timeout":
                            raise TimeoutError(PRIVATE)
                        if kind == "protocol":
                            raise http.client.IncompleteRead(PRIVATE.encode(), 100)
                        if kind == "json":
                            return io.BytesIO((PRIVATE + " not JSON").encode())
                        return io.BytesIO(b"\xff" + PRIVATE.encode())

                    self.transport.side_effect = request
                    code, report = self.cli("video")
                    self.assertEqual(code, 1)
                    self.assertEqual(self.methods, ["POST"] if phase == "POST" else ["POST", "GET"])
                    self.assertTrue(report["provider_calls"])
                    if kind == "http":
                        self.assertIn("HTTP 503", report["error"])
                        self.assertTrue(bodies[0].closed)
                        self.assertEqual(bodies[0].reads, 0)

    def test_actual_failed_video_response_keeps_private_id_only_recovery(self):
        self.require_binding()
        for phase in ("POST", "GET"):
            with self.subTest(phase=phase):
                self.methods.clear()

                def request(value, **kwargs):
                    self.methods.append(value.method)
                    response = {"video_id": "qa-video", "task_id": "qa-task", "status": "failed", "error": {"echo": PRIVATE, "url": URL}}
                    if phase == "GET" and value.method == "POST":
                        response = {"video_id": "qa-video", "task_id": "qa-task", "status": "queued"}
                    return io.BytesIO(json.dumps(response).encode())

                self.transport.side_effect = request
                output = self.root / phase / "result"
                code, report = self.cli("video", output)
                self.assertEqual(code, 1)
                self.assertIn("status=failed", report["error"])
                self.assertEqual(self.methods, ["POST"] if phase == "POST" else ["POST", "GET"])
                self.assertFalse(output.exists())
                self.assertFalse(report["recovery"]["automatic_regeneration"])
                receipt = Path(report["recovery"]["path"])
                self.assertEqual(receipt.stat().st_mode & 0o777, 0o600)
                retained = json.loads(receipt.read_text())["result"]
                self.assertEqual(retained["video_id"], "qa-video")
                self.assertEqual(retained["task_id"], "qa-task")
                self.assertNotIn(PRIVATE, receipt.read_text())
                self.assertNotIn("error", retained)

    def test_missing_platform_primitives_stop_before_configuration(self):
        output = self.root / "new" / "result"
        with mock.patch.object(agnes, "DIR_FD_OUTPUT_SUPPORTED", False):
            code, report = self.cli("b64", output)
        self.assertEqual(code, 1)
        self.assertIn("not supported", report["error"])
        self.assertFalse(report["provider_calls"])
        self.assertFalse(report["secrets_read"])
        self.config.assert_not_called()
        self.transport.assert_not_called()
        self.assertEqual(list(self.root.iterdir()), [])

    def test_unsupported_volume_stops_before_configuration_and_cleans_probe(self):
        self.require_binding()
        output = self.root / "result"
        with mock.patch.object(agnes.os, "link", side_effect=OSError(errno.ENOTSUP, PRIVATE)):
            code, report = self.cli("b64", output)
        self.assertEqual(code, 1)
        self.assertFalse(report["provider_calls"])
        self.assertFalse(report["secrets_read"])
        self.config.assert_not_called()
        self.transport.assert_not_called()
        self.assertEqual(list(self.root.iterdir()), [])

    def replacement(self, directory):
        parent = directory / "output"
        moved = directory / "moved-output"
        other = directory / "other"
        parent.mkdir(parents=True)
        other.mkdir()

        def replace():
            parent.rename(moved)
            parent.symlink_to(other, target_is_directory=True)

        return parent, moved, other, replace

    def test_real_parent_replacement_at_open_or_submission_never_redirects(self):
        self.require_binding()
        real_open = os.open
        for stage in ("bind", "configuration", "submission", "staging_open"):
            for route in ("url", "b64", "video"):
                with self.subTest(stage=stage, route=route):
                    self.methods.clear()
                    self.config.reset_mock()
                    self.config.side_effect = None
                    parent, moved, other, replace = self.replacement(self.root / f"{stage}-{route}")
                    success = self.success_transport(route)

                    def request(value, **kwargs):
                        if stage == "submission" and not isinstance(value, str) and value.method == "POST":
                            replace()
                        return success(value, **kwargs)

                    def configuration(args):
                        replace()
                        return "https://example.invalid", "qa-key"

                    def open_file(path, flags, *args, **kwargs):
                        if (stage == "bind" and path == parent) or (stage == "staging_open" and str(path).startswith(".agnes-media-")):
                            replace()
                        return real_open(path, flags, *args, **kwargs)

                    self.transport.side_effect = request
                    if stage == "configuration":
                        self.config.side_effect = configuration
                    with mock.patch.object(agnes.os, "open", side_effect=open_file):
                        code, report = self.cli(route, parent / "result")
                    self.assertEqual(code, 1, report)
                    self.assertEqual(list(other.iterdir()), [])
                    self.assertEqual(list(moved.iterdir()), [])
                    expected_submits = int(stage in ("submission", "staging_open"))
                    self.assertEqual(self.methods.count("POST"), expected_submits)
                    self.assertEqual(report["provider_calls"], bool(expected_submits))
                    if expected_submits:
                        self.assertEqual(report["recovery"]["status"], "unavailable")
                        self.assertNotIn("path", report["recovery"])
                        self.assertFalse(report["recovery"]["automatic_regeneration"])
                    if stage == "bind":
                        self.config.assert_not_called()

    def test_final_publication_uses_original_handle_after_parent_replacement(self):
        self.require_binding()
        real_link = os.link
        for route in ("url", "b64", "video"):
            with self.subTest(route=route):
                self.methods.clear()
                parent, moved, other, replace = self.replacement(self.root / route)
                self.transport.side_effect = self.success_transport(route)

                def publish(source, destination, **kwargs):
                    if destination == "result":
                        replace()
                    real_link(source, destination, **kwargs)

                with mock.patch.object(agnes.os, "link", side_effect=publish):
                    code, report = self.cli(route, parent / "result")
                self.assertEqual(code, 1, report)
                self.assertEqual(list(other.iterdir()), [])
                self.assertEqual((moved / "result").read_bytes(), CONTENT)
                self.assertEqual(list(moved.iterdir()), [moved / "result"])
                self.assertEqual(self.methods.count("POST"), 1)
                self.assertEqual(report["artifact"]["status"], "published_to_bound_parent")
                self.assertFalse(report["artifact"]["path_verified"])
                self.assertEqual(report["artifact"]["parent_identity"]["inode"], moved.stat().st_ino)
                self.assertEqual(report["recovery"]["status"], "unavailable")
                self.assertFalse(report["recovery"]["automatic_regeneration"])

    def test_new_real_parent_identity_cannot_replace_the_verified_directory(self):
        self.require_binding()
        parent = self.root / "output"
        moved = self.root / "moved"
        parent.mkdir()
        real_open = os.open

        def open_parent(path, flags, *args, **kwargs):
            if path == parent:
                parent.rename(moved)
                parent.mkdir()
            return real_open(path, flags, *args, **kwargs)

        with mock.patch.object(agnes.os, "open", side_effect=open_parent):
            code, report = self.cli("b64", parent / "result")
        self.assertEqual(code, 1)
        self.assertIn("identity changed", report["error"])
        self.assertEqual(list(parent.iterdir()), [])
        self.assertEqual(list(moved.iterdir()), [])
        self.config.assert_not_called()
        self.transport.assert_not_called()

    def test_missing_parents_are_created_under_the_pinned_ancestor(self):
        self.require_binding()
        parent, moved, other, replace = self.replacement(self.root / "nested")
        real_mkdir = os.mkdir

        def mkdir(path, *args, **kwargs):
            if path == "child":
                replace()
            return real_mkdir(path, *args, **kwargs)

        with mock.patch.object(agnes.os, "mkdir", side_effect=mkdir):
            code, report = self.cli("b64", parent / "child" / "result")
        self.assertEqual(code, 1)
        self.assertEqual(list(other.iterdir()), [])
        self.assertTrue((moved / "child").is_dir())
        self.assertEqual(list((moved / "child").iterdir()), [])
        self.config.assert_not_called()
        self.transport.assert_not_called()

    def test_direct_download_and_decode_pin_before_reading_result_bytes(self):
        self.require_binding()
        real_decode = base64.b64decode
        for route in ("url", "b64"):
            with self.subTest(route=route):
                parent, moved, other, replace = self.replacement(self.root / route)

                def download(*args, **kwargs):
                    replace()
                    return io.BytesIO(CONTENT)

                def decode(*args, **kwargs):
                    data = real_decode(*args, **kwargs)
                    replace()
                    return data

                self.transport.side_effect = download
                with mock.patch.object(agnes.base64, "b64decode", side_effect=decode):
                    with self.assertRaises(agnes.AgnesError):
                        agnes.save_image_result(self.response(route), parent / "result", timeout=1)
                self.assertEqual(list(other.iterdir()), [])
                self.assertEqual(list(moved.iterdir()), [])
                self.config.assert_not_called()

    def test_recovery_creation_write_and_cleanup_remain_bound_after_parent_move(self):
        self.require_binding()
        real_open, real_dump, real_unlink = os.open, json.dump, os.unlink
        for stage in ("open", "write", "cleanup_failure"):
            with self.subTest(stage=stage):
                self.methods.clear()
                parent, moved, other, replace = self.replacement(self.root / stage)
                success = self.success_transport("url")

                def request(value, **kwargs):
                    if isinstance(value, str):
                        self.methods.append("DOWNLOAD")
                        raise urllib.error.URLError(PRIVATE)
                    return success(value, **kwargs)

                def open_file(path, flags, *args, **kwargs):
                    if stage == "open" and str(path).startswith(".agnes-recovery-"):
                        replace()
                    return real_open(path, flags, *args, **kwargs)

                def write_receipt(value, stream, **kwargs):
                    real_dump(value, stream, **kwargs)
                    if stage in ("write", "cleanup_failure"):
                        replace()
                    if stage == "cleanup_failure":
                        raise OSError(errno.ENOSPC, PRIVATE)

                def unlink(path, **kwargs):
                    if stage == "cleanup_failure" and str(path).startswith(".agnes-recovery-"):
                        raise PermissionError(PRIVATE)
                    real_unlink(path, **kwargs)

                self.transport.side_effect = request
                with mock.patch.object(agnes.os, "open", side_effect=open_file), mock.patch.object(agnes.json, "dump", side_effect=write_receipt), mock.patch.object(agnes.os, "unlink", side_effect=unlink):
                    code, report = self.cli("url", parent / "result")
                self.assertEqual(code, 1, report)
                self.assertEqual(list(other.iterdir()), [])
                self.assertEqual(self.methods, ["POST", "DOWNLOAD"])
                self.assertEqual(report["recovery"]["status"], "unavailable")
                self.assertNotIn("path", report["recovery"])
                self.assertFalse(report["recovery"]["automatic_regeneration"])
                if stage == "cleanup_failure":
                    location = report["recovery"]["partial_location"]
                    self.assertFalse(location["path_verified"])
                    self.assertEqual(location["parent_identity"]["inode"], moved.stat().st_ino)
                    receipt = moved / location["name"]
                    self.assertEqual(receipt.stat().st_mode & 0o777, 0o600)
                    self.assertEqual(list(moved.iterdir()), [receipt])
                else:
                    self.assertEqual(list(moved.iterdir()), [])

    def test_directory_handles_close_on_success_and_failure(self):
        self.require_binding()
        real_open = os.open
        for fail in (False, True):
            with self.subTest(fail=fail):
                descriptors = []

                def open_file(*args, **kwargs):
                    fd = real_open(*args, **kwargs)
                    descriptors.append(fd)
                    return fd

                self.transport.side_effect = (
                    urllib.error.URLError(PRIVATE) if fail else self.success_transport("b64")
                )
                with mock.patch.object(agnes.os, "open", side_effect=open_file):
                    code, _ = self.cli("b64", self.root / str(fail) / "result")
                self.assertEqual(code, int(fail))
                for fd in set(descriptors):
                    with self.assertRaises(OSError):
                        os.fstat(fd)


if __name__ == "__main__":
    unittest.main()
