from __future__ import annotations

import base64
import contextlib
import errno
import http.client
import importlib.util
import io
import json
import os
import stat
import sys
import tempfile
import threading
import unittest
import urllib.error
from concurrent.futures import ThreadPoolExecutor
from pathlib import Path
from unittest import mock


SCRIPT = Path(__file__).resolve().parents[1] / "scripts" / "agnes_media.py"
SPEC = importlib.util.spec_from_file_location("agnes_output", SCRIPT)
assert SPEC and SPEC.loader
agnes = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(agnes)

CONTENT = b"complete generated media"
RESULT_URL = "https://media.invalid/result?signature=private-result-signature"


class AgnesOutputTests(unittest.TestCase):
    def setUp(self) -> None:
        if not agnes.DIR_FD_OUTPUT_SUPPORTED and self._testMethodName not in (
            "test_existing_entries_stop_before_credentials_and_submission",
            "test_dry_run_does_not_preflight_write_read_credentials_or_call_provider",
        ):
            self.skipTest("platform lacks safe directory-relative publication")
        self.temporary = tempfile.TemporaryDirectory()
        self.addCleanup(self.temporary.cleanup)
        self.root = Path(self.temporary.name).resolve()
        self.config = self.enterContext(
            mock.patch.object(agnes, "execution_config", return_value=("https://api.invalid", "test-key"))
        )
        self.credentials = self.enterContext(mock.patch.object(agnes, "parse_env_file"))
        self.request = self.enterContext(mock.patch.object(agnes, "request_json"))
        self.urlopen = self.enterContext(
            mock.patch.object(agnes.urllib.request, "urlopen", side_effect=lambda *a, **kw: io.BytesIO(CONTENT))
        )

    def response(self, route: str) -> dict:
        if route == "video":
            return {"status": "completed", "video_id": "video-123", "metadata": {"url": RESULT_URL}}
        field = {"url": RESULT_URL} if route == "url" else {"b64_json": base64.b64encode(CONTENT).decode()}
        return {"data": [field], "debug": {"api_key": "private-provider-debug"}}

    def run_cli(self, route: str, output: Path, *extra: str, execute: bool = True) -> tuple[int, dict]:
        arguments = ["video" if route == "video" else "image", "--prompt", "Generate", "--output", str(output)]
        if route == "video":
            arguments.append("--wait")
        elif route == "b64":
            arguments.extend(["--response-format", "b64_json"])
        if execute:
            arguments.append("--execute")
        self.request.return_value = self.response(route)
        with contextlib.redirect_stdout(io.StringIO()) as stdout:
            code = agnes.main([*arguments, *extra])
        return code, json.loads(stdout.getvalue())

    def assert_recovery(self, report: dict, output: Path) -> dict:
        self.assertTrue(report["provider_calls"])
        self.assertTrue(report["secrets_read"])
        self.assertFalse(report["recovery"]["automatic_regeneration"])
        self.assertEqual(report["recovery"]["status"], "saved")
        receipt = Path(report["recovery"]["path"])
        self.assertEqual(receipt.parent, output.parent.resolve())
        if os.name != "nt":
            self.assertEqual(stat.S_IMODE(receipt.stat().st_mode), 0o600)
        contents = json.loads(receipt.read_text())
        self.assertNotIn("private-provider-debug", receipt.read_text())
        public = json.dumps(report)
        self.assertNotIn("private-result-signature", public)
        self.assertNotIn(base64.b64encode(CONTENT).decode(), public)
        self.assertNotIn("test-key", public)
        self.assertEqual(list(output.parent.glob(".agnes-media-*.tmp")), [])
        self.config.assert_called_once()
        self.request.assert_called_once()
        self.credentials.assert_not_called()
        return contents

    def test_existing_entries_stop_before_credentials_and_submission(self) -> None:
        for route in ("url", "b64", "video"):
            for kind in ("file", "symlink", "dangling", "hardlink", "same-input", "normalized", "directory"):
                with self.subTest(route=route, kind=kind):
                    directory = self.root / f"{route}-{kind}"
                    directory.mkdir()
                    original = directory / "input.png"
                    original.write_bytes(b"original")
                    output = directory / "result"
                    extra = []
                    if kind == "file":
                        output.write_bytes(b"existing output")
                    elif kind == "symlink":
                        output.symlink_to(original)
                    elif kind == "dangling":
                        output.symlink_to(directory / "absent")
                    elif kind == "hardlink":
                        os.link(original, output)
                    elif kind == "same-input":
                        output = original
                        extra = ["--image", str(original)]
                    elif kind == "normalized":
                        (directory / "child").mkdir()
                        output = directory / "child" / ".." / original.name
                    else:
                        output.mkdir()
                    before = output.lstat()
                    code, report = self.run_cli(route, output, *extra)
                    self.assertEqual(code, 1, report)
                    self.assertFalse(report["provider_calls"])
                    self.assertFalse(report["secrets_read"])
                    self.assertIn("already exists", report["error"])
                    self.assertEqual(output.lstat(), before)
                    self.assertEqual(original.read_bytes(), b"original")
                    self.assertEqual(list(directory.glob(".agnes-*")), [])
                    self.config.assert_not_called()
                    self.credentials.assert_not_called()
                    self.request.assert_not_called()
                    self.urlopen.assert_not_called()

    def test_new_targets_work_for_each_result_format(self) -> None:
        for route in ("url", "b64", "video"):
            with self.subTest(route=route):
                output = self.root / route / "nested" / "result"
                code, report = self.run_cli(route, output)
                self.assertEqual(code, 0, report)
                self.assertEqual(output.read_bytes(), CONTENT)
                self.assertEqual(list(output.parent.iterdir()), [output])

    def test_output_parent_inspection_failure_stops_before_configuration(self) -> None:
        for failure in (PermissionError("not readable"), OSError(errno.ELOOP, "symlink loop")):
            with self.subTest(failure=type(failure).__name__):
                with mock.patch.object(Path, "lstat", side_effect=failure):
                    code, report = self.run_cli("url", self.root / "result")
                self.assertEqual(code, 1, report)
                self.assertFalse(report["provider_calls"])
                self.assertFalse(report["secrets_read"])
                self.config.assert_not_called()
                self.request.assert_not_called()
                self.urlopen.assert_not_called()
                self.assertEqual(list(self.root.iterdir()), [])

    @unittest.skipUnless(sys.platform == "darwin", "macOS /tmp alias")
    def test_macos_tmp_alias_is_supported(self) -> None:
        if not self.root.is_relative_to("/private/tmp"):
            self.skipTest("run with a lane-owned TMPDIR under /private/tmp")
        output = self.root / "result"
        alias = Path("/tmp") / output.relative_to("/private/tmp")
        code, report = self.run_cli("b64", alias)
        self.assertEqual(code, 0, report)
        self.assertEqual(output.read_bytes(), CONTENT)

    def test_home_output_is_expanded_before_configuration(self) -> None:
        with mock.patch.dict(os.environ, {"HOME": str(self.root)}):
            code, report = self.run_cli("url", Path("~/result"))
        self.assertEqual(code, 0, report)
        self.assertEqual((self.root / "result").read_bytes(), CONTENT)

    def test_parent_alias_and_cwd_are_frozen_before_reading_configuration(self) -> None:
        parent = self.root / "original"
        other = self.root / "other"
        parent.mkdir()
        other.mkdir()
        alias = self.root / "alias"
        alias.symlink_to(parent, target_is_directory=True)
        (other / "result").write_bytes(b"other output")
        old_cwd = Path.cwd()
        self.addCleanup(os.chdir, old_cwd)
        os.chdir(self.root)

        def change_paths(args):
            alias.unlink()
            alias.symlink_to(other, target_is_directory=True)
            os.chdir(other)
            return "https://api.invalid", "test-key"

        self.config.side_effect = change_paths
        code, report = self.run_cli("url", Path("alias/result"))
        self.assertEqual(code, 0, report)
        self.assertEqual((parent / "result").read_bytes(), CONTENT)
        self.assertEqual((other / "result").read_bytes(), b"other output")

    def test_submit_time_collisions_preserve_the_winner_and_the_result(self) -> None:
        for route in ("url", "b64", "video"):
            for kind in ("file", "symlink", "dangling", "hardlink", "directory"):
                with self.subTest(route=route, kind=kind):
                    directory = self.root / f"{route}-{kind}"
                    directory.mkdir()
                    output = directory / "result"
                    source = directory / "source"
                    source.write_bytes(b"racer source")

                    def submit(*args, **kwargs):
                        if kind == "file":
                            output.write_bytes(b"racer output")
                        elif kind == "symlink":
                            output.symlink_to(source)
                        elif kind == "dangling":
                            output.symlink_to(directory / "absent")
                        elif kind == "hardlink":
                            os.link(source, output)
                        else:
                            output.mkdir()
                        return self.response(route)

                    self.request.side_effect = submit
                    code, report = self.run_cli(route, output)
                    self.assertEqual(code, 1, report)
                    recovery = self.assert_recovery(report, output)
                    self.assertEqual(source.read_bytes(), b"racer source")
                    if kind == "file":
                        self.assertEqual(output.read_bytes(), b"racer output")
                    elif kind in ("symlink", "dangling"):
                        self.assertTrue(output.is_symlink())
                        self.assertEqual(os.readlink(output), str(source if kind == "symlink" else directory / "absent"))
                    elif kind == "hardlink":
                        self.assertEqual(output.stat().st_ino, source.stat().st_ino)
                    else:
                        self.assertTrue(output.is_dir())
                    self.assertEqual(recovery["result"], {k: v for k, v in self.response(route).items() if k != "debug"})
                    self.request.reset_mock()
                    self.config.reset_mock()

    def test_two_publishers_only_one_can_win(self) -> None:
        output = self.root / "result"
        barrier = threading.Barrier(2)
        real_link = os.link

        def publish(source, target, **kwargs):
            if target == output.name:
                self.assertFalse(output.exists())
                barrier.wait(timeout=5)
            real_link(source, target, **kwargs)

        def save(content):
            try:
                agnes.save_bytes(content, output)
                return content
            except agnes.AgnesError:
                return None

        with mock.patch.object(agnes.os, "link", side_effect=publish), ThreadPoolExecutor(max_workers=2) as pool:
            winners = list(pool.map(save, (b"first complete result", b"second complete result")))
        self.assertEqual(sum(winner is not None for winner in winners), 1)
        self.assertIn(output.read_bytes(), [winner for winner in winners if winner is not None])
        self.assertEqual(list(self.root.iterdir()), [output])

    def test_download_failures_keep_private_result_and_no_partial_output(self) -> None:
        for route in ("url", "video"):
            with self.subTest(route=route):
                output = self.root / route / "result"
                self.urlopen.side_effect = urllib.error.URLError(RESULT_URL)
                code, report = self.run_cli(route, output)
                self.assertEqual(code, 1, report)
                self.assertFalse(output.exists())
                self.assert_recovery(report, output)
                self.request.reset_mock()
                self.config.reset_mock()

    def test_invalid_base64_keeps_response_without_creating_output(self) -> None:
        for invalid in ("not base64!", "\ud800"):
            with self.subTest(invalid=repr(invalid)):
                output = self.root / "result"
                self.request.side_effect = lambda *a, **kw: {"data": [{"b64_json": invalid}]}
                code, report = self.run_cli("b64", output)
                self.assertEqual(code, 1, report)
                self.assertFalse(output.exists())
                recovery = self.assert_recovery(report, output)
                self.assertEqual(recovery["result"]["data"][0]["b64_json"], invalid)
                self.request.reset_mock()
                self.config.reset_mock()

    def test_interrupted_download_keeps_result_without_partial_output(self) -> None:
        output = self.root / "result"
        response = mock.MagicMock()
        response.__enter__.return_value = response
        response.read.side_effect = http.client.IncompleteRead(b"private downloaded fragment", 100)
        self.urlopen.side_effect = None
        self.urlopen.return_value = response
        code, report = self.run_cli("video", output)
        self.assertEqual(code, 1, report)
        self.assertFalse(output.exists())
        self.assertNotIn("private downloaded fragment", json.dumps(report))
        self.assert_recovery(report, output)

    def test_write_and_publish_failures_clean_staging_without_overwrite_fallback(self) -> None:
        real_fdopen = os.fdopen
        real_link = os.link

        @contextlib.contextmanager
        def broken_writer(fd, mode, **kwargs):
            with real_fdopen(fd, mode, **kwargs) as stream:
                if mode == "wb":
                    write = stream.write

                    def partial_write(data):
                        write(data[:3])
                        raise OSError(errno.ENOSPC, RESULT_URL)

                    with mock.patch.object(stream, "write", side_effect=partial_write):
                        yield stream
                else:
                    yield stream

        def fail_publication(source, target, **kwargs):
            if target == "result":
                raise OSError(errno.ENOTSUP, RESULT_URL)
            real_link(source, target, **kwargs)

        for failure in ("write", "fsync", "link"):
            for route in ("url", "b64", "video"):
                with self.subTest(failure=failure, route=route):
                    output = self.root / f"{failure}-{route}" / "result"
                    if failure == "write":
                        patcher = mock.patch.object(agnes.os, "fdopen", side_effect=broken_writer)
                    elif failure == "fsync":
                        patcher = mock.patch.object(agnes.os, "fsync", side_effect=[OSError(errno.EIO, RESULT_URL), None])
                    else:
                        patcher = mock.patch.object(agnes.os, "link", side_effect=fail_publication)
                    with patcher:
                        code, report = self.run_cli(route, output)
                    self.assertEqual(code, 1, report)
                    self.assertFalse(output.exists())
                    self.assert_recovery(report, output)
                    self.request.reset_mock()
                    self.config.reset_mock()

    def test_video_recovery_keeps_initial_ids_when_poll_response_omits_them(self) -> None:
        output = self.root / "result"
        self.request.side_effect = lambda *a, **kw: {"video_id": "video-123", "task_id": "task-123", "status": "queued"}
        self.urlopen.side_effect = OSError("download failed")
        with mock.patch.object(agnes, "poll_video", return_value={"status": "completed", "metadata": {"url": RESULT_URL}}):
            code, report = self.run_cli("video", output)
        self.assertEqual(code, 1, report)
        recovery = self.assert_recovery(report, output)
        self.assertEqual(recovery["result"]["video_id"], "video-123")
        self.assertEqual(recovery["result"]["task_id"], "task-123")

    def test_recovery_write_failure_is_explicit_without_leaking_or_resubmitting(self) -> None:
        output = self.root / "result"
        self.urlopen.side_effect = urllib.error.URLError(RESULT_URL)
        create_private = agnes.OutputTarget.create_private

        def fail_receipt(target, prefix, suffix):
            if prefix == ".agnes-recovery-":
                raise PermissionError(RESULT_URL)
            return create_private(target, prefix, suffix)

        with mock.patch.object(agnes.OutputTarget, "create_private", fail_receipt):
            code, report = self.run_cli("url", output)
        self.assertEqual(code, 1, report)
        self.assertEqual(report["recovery"]["status"], "unavailable")
        self.assertFalse(report["recovery"]["automatic_regeneration"])
        self.assertNotIn("private-result-signature", json.dumps(report))
        self.assertEqual(list(self.root.iterdir()), [])
        self.request.assert_called_once()

    def test_partial_recovery_receipt_is_removed_on_write_failure(self) -> None:
        output = self.root / "result"
        self.urlopen.side_effect = urllib.error.URLError(RESULT_URL)

        def partial_dump(payload, stream, **kwargs):
            stream.write('{"media":')
            raise OSError(errno.ENOSPC, RESULT_URL)

        with mock.patch.object(agnes.json, "dump", side_effect=partial_dump):
            code, report = self.run_cli("url", output)
        self.assertEqual(code, 1, report)
        self.assertEqual(report["recovery"]["status"], "unavailable")
        self.assertFalse(report["recovery"]["automatic_regeneration"])
        self.assertNotIn("private-result-signature", json.dumps(report))
        self.assertEqual(list(self.root.iterdir()), [])
        self.request.assert_called_once()

    def test_dry_run_does_not_preflight_write_read_credentials_or_call_provider(self) -> None:
        for route in ("url", "b64", "video"):
            for existing in (False, True):
                with self.subTest(route=route, existing=existing):
                    output = self.root / ("result" if existing else "missing/result")
                    if existing and not output.exists():
                        output.write_bytes(b"existing")
                    before = sorted(str(path) for path in self.root.rglob("*"))
                    with mock.patch.object(agnes, "prepare_output", side_effect=AssertionError("dry-run preflight")):
                        code, report = self.run_cli(route, output, execute=False)
                    self.assertEqual(code, 0, report)
                    self.assertFalse(report["provider_calls"])
                    self.assertFalse(report["secrets_read"])
                    self.assertEqual(sorted(str(path) for path in self.root.rglob("*")), before)
                    self.config.assert_not_called()
                    self.credentials.assert_not_called()
                    self.request.assert_not_called()
                    self.urlopen.assert_not_called()


if __name__ == "__main__":
    unittest.main()
