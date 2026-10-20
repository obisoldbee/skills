from __future__ import annotations

import argparse
import base64
import contextlib
import hashlib
import importlib.util
import io
import json
import tempfile
import unittest
from pathlib import Path
from unittest import mock


ROOT = Path(__file__).resolve().parents[1]
OLD_ENDPOINT = "https://api.minimaxi.com/anthropic/v1/messages"
NEW_ENDPOINT = "https://api.minimax.cn/anthropic/v1/messages"


def load_module(name: str, filename: str):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts/providers" / filename)
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


AUDIO = load_module("minimax_api_audio", "minimax_m3_course_audio.py")
VIDEO = load_module("minimax_api_video", "minimax_m3_course_video.py")


class MiniMaxApiContractTests(unittest.TestCase):
    def setUp(self):
        self.network = mock.patch(
            "urllib.request.OpenerDirector.open", side_effect=AssertionError("network forbidden")
        )
        self.network.start()
        self.addCleanup(self.network.stop)

    def args(self, **overrides):
        values = dict(
            model="MiniMax-M3", effort=None, max_tokens=2200, temperature=0.1,
            timeout=1, resume=True, prompt_file=None, prompt="describe",
            retries=3, retry_sleep=0,
        )
        values.update(overrides)
        return argparse.Namespace(**values)

    def segment(self, media):
        return dict(
            index=0, file=str(media), start_time="00:00:00.000", end_time="00:00:01.000",
            start_seconds=0, end_seconds=1, duration_seconds=1,
        )

    def payload(self, module, media, args, data=b"fixture-video"):
        if module is VIDEO:
            return module.build_payload(args.model, media, "describe", args, data)
        return module.build_payload(media, "describe", args, data)

    def descriptor(self, module, media, args, data):
        if module is VIDEO:
            return module.operation_descriptor(args.model, media, "describe", args, data)
        return module.operation_descriptor(media, "describe", args, data)

    def legacy_descriptor(self, media, data):
        # Frozen pre-change contract, independent of the new descriptor helper.
        return {
            "model": "MiniMax-M3", "prompt": "describe", "max_tokens": 2200,
            "temperature": 0.1, "thinking": {"type": "disabled"},
            "source_file": str(media), "source_bytes": len(data),
            "source_sha256": hashlib.sha256(data).hexdigest(), "media_type": "video/mp4",
        }

    def seed_legacy_operation(self, module, output, media, state):
        data = media.read_bytes()
        fingerprint = module.operation_fingerprint(OLD_ENDPOINT, self.legacy_descriptor(media, data))
        directory = output / "responses" / "segment_000"
        directory.mkdir(parents=True)
        operation = {
            "schema": "media-understanding/provider-operation/v1",
            "operation_fingerprint": fingerprint, "state": state,
            "retry_disposition": "completed_no_retry" if state == "completed" else "no_resubmit",
            "attempts": [], "response_evidence": [],
        }
        if state in {"completed", "accepted"}:
            response = {
                "ok": True, "status_code": 200, "operation_fingerprint": fingerprint,
                "request_state": state, "provider_request_id": "fixture-request",
                "retry_disposition": operation["retry_disposition"],
                "body": {"content": [{"type": "text", "text": "legacy notes"}] if state == "completed" else []},
            }
            response_path = directory / "attempt_01.json"
            response_path.write_text(json.dumps(response), encoding="utf-8")
            reference = module.response_reference(response_path, directory)
            operation["response_evidence"] = [reference]
            operation["attempts"] = [{
                "attempt": 1, "state": state, "status_code": 200,
                "provider_request_id": "fixture-request", "expected_operation_fingerprint": fingerprint,
                "retry_disposition": operation["retry_disposition"], "response_evidence": reference,
            }]
        (directory / "operation.json").write_text(json.dumps(operation), encoding="utf-8")
        return directory

    def test_m3_payload_uses_official_base64_source_without_temperature(self):
        for module in (AUDIO, VIDEO):
            with self.subTest(module=module.__name__):
                payload = self.payload(module, Path("fixture.mp4"), self.args())
                self.assertEqual(payload["model"], "MiniMax-M3")
                self.assertEqual(payload["thinking"], {"type": "disabled"})
                self.assertNotIn("output_config", payload)
                self.assertNotIn("temperature", payload)
                self.assertEqual(payload["messages"][0]["content"][1]["source"], {
                    "type": "base64", "media_type": "video/mp4",
                    "data": base64.b64encode(b"fixture-video").decode("ascii"),
                })

    def test_flash_payload_has_adaptive_thinking_and_each_official_effort(self):
        for module in (AUDIO, VIDEO):
            for effort in (None, "low", "medium", "high", "xhigh", "max"):
                with self.subTest(module=module.__name__, effort=effort):
                    args = self.args(model="MiniMax-M3.1-Flash", effort=effort)
                    payload = self.payload(module, Path("fixture.mp4"), args)
                    self.assertEqual(payload["thinking"], {"type": "adaptive"})
                    self.assertEqual(payload["output_config"], {"effort": effort or "max"})
                    self.assertNotIn("temperature", payload)
                    self.assertNotIn("service_tier", payload)

    def test_m3_rejects_flash_effort_instead_of_sending_it(self):
        for module in (AUDIO, VIDEO):
            with self.subTest(module=module.__name__), self.assertRaisesRegex(ValueError, "only with MiniMax-M3.1-Flash"):
                self.payload(module, Path("fixture.mp4"), self.args(effort="low"))

    def test_legacy_m3_descriptor_and_fingerprint_remain_exact(self):
        for module in (AUDIO, VIDEO):
            with self.subTest(module=module.__name__):
                media = Path("fixture.mp4")
                descriptor = self.descriptor(module, media, self.args(), b"fixture-video")
                expected = self.legacy_descriptor(media, b"fixture-video")
                self.assertEqual(descriptor, expected)
                self.assertEqual(module.operation_fingerprint(OLD_ENDPOINT, descriptor),
                                 module.operation_fingerprint(OLD_ENDPOINT, expected))

    def test_flash_effort_is_bound_to_fingerprint(self):
        for module in (AUDIO, VIDEO):
            with self.subTest(module=module.__name__):
                values = [self.descriptor(module, Path("fixture.mp4"), self.args(model="MiniMax-M3.1-Flash", effort=effort), b"fixture")
                          for effort in (None, "max", "low")]
                self.assertEqual(values[0], values[1])
                self.assertNotEqual(values[0], values[2])
                self.assertNotIn("temperature", values[0])

    def test_legacy_states_resume_without_post_or_evidence_changes(self):
        for module in (AUDIO, VIDEO):
            for state in ("not_sent", "accepted", "acceptance_unknown", "completed"):
                with self.subTest(module=module.__name__, state=state), tempfile.TemporaryDirectory() as temporary:
                    output = Path(temporary)
                    media = output / "fixture.mp4"
                    media.write_bytes(b"fixture-video")
                    directory = self.seed_legacy_operation(module, output, media, state)
                    before = {path.name: path.read_bytes() for path in directory.iterdir()}
                    segments = [self.segment(media)]
                    with mock.patch.object(module, "call_m3") as request:
                        module.analyze_segments(segments, output, "fixture-key", OLD_ENDPOINT, self.args())
                    request.assert_not_called()
                    self.assertEqual(segments[0]["request_state"], state)
                    self.assertEqual(before, {path.name: path.read_bytes() for path in directory.iterdir()})
                    if state == "completed":
                        self.assertEqual(segments[0]["status"], "cached_completed")
                        self.assertIn("legacy notes", (output / ("video_notes.md" if module is VIDEO else "audio_notes.md")).read_text())

    def test_new_default_endpoint_cannot_resubmit_legacy_accepted_operations(self):
        for module in (AUDIO, VIDEO):
            for state in ("accepted", "acceptance_unknown", "completed"):
                with self.subTest(module=module.__name__, state=state), tempfile.TemporaryDirectory() as temporary:
                    output = Path(temporary)
                    media = output / "fixture.mp4"
                    media.write_bytes(b"fixture-video")
                    directory = self.seed_legacy_operation(module, output, media, state)
                    before = {path.name: path.read_bytes() for path in directory.iterdir()}
                    segments = [self.segment(media)]
                    with mock.patch.object(module, "call_m3") as request:
                        module.analyze_segments(segments, output, "fixture-key", module.DEFAULT_ENDPOINT, self.args())
                    request.assert_not_called()
                    self.assertEqual(segments[0]["request_state"], state)
                    self.assertEqual(segments[0]["status"], "operation_fingerprint_mismatch_no_resubmit")
                    self.assertEqual(before, {path.name: path.read_bytes() for path in directory.iterdir()})

    def test_model_change_cannot_resubmit_existing_operations(self):
        for module in (AUDIO, VIDEO):
            with self.subTest(module=module.__name__), tempfile.TemporaryDirectory() as temporary:
                output = Path(temporary)
                media = output / "fixture.mp4"
                media.write_bytes(b"fixture-video")
                self.seed_legacy_operation(module, output, media, "acceptance_unknown")
                segments = [self.segment(media)]
                with mock.patch.object(module, "call_m3") as request:
                    module.analyze_segments(segments, output, "fixture-key", OLD_ENDPOINT,
                                            self.args(model="MiniMax-M3.1-Flash", effort="low"))
                request.assert_not_called()
                self.assertEqual(segments[0]["request_state"], "acceptance_unknown")

    def test_flash_interruption_and_effort_change_never_repeat_post(self):
        for module in (AUDIO, VIDEO):
            with self.subTest(module=module.__name__), tempfile.TemporaryDirectory() as temporary:
                output = Path(temporary)
                media = output / "fixture.mp4"
                media.write_bytes(b"fixture-video")
                args = self.args(model="MiniMax-M3.1-Flash", effort="low")
                with mock.patch.object(module, "call_m3", side_effect=KeyboardInterrupt):
                    with self.assertRaises(KeyboardInterrupt):
                        module.analyze_segments([self.segment(media)], output, "fixture-key", NEW_ENDPOINT, args)
                directory = output / "responses" / "segment_000"
                before = {path.name: path.read_bytes() for path in directory.iterdir()}
                self.assertEqual(json.loads(before["operation.json"])["state"], "acceptance_unknown")
                for effort in ("low", "max"):
                    segments = [self.segment(media)]
                    with mock.patch.object(module, "call_m3") as request:
                        module.analyze_segments(segments, output, "fixture-key", NEW_ENDPOINT,
                                                self.args(model="MiniMax-M3.1-Flash", effort=effort))
                    request.assert_not_called()
                    self.assertEqual(segments[0]["request_state"], "acceptance_unknown")
                    self.assertEqual(before, {path.name: path.read_bytes() for path in directory.iterdir()})

    def test_wire_and_fingerprint_still_use_one_media_snapshot(self):
        class Response:
            status = 200
            headers = {}
            def __enter__(self): return self
            def __exit__(self, *_args): return False
            def read(self): return b'{"content":[{"type":"text","text":"ok"}]}'

        for module in (AUDIO, VIDEO):
            with self.subTest(module=module.__name__), tempfile.TemporaryDirectory() as temporary:
                media = Path(temporary) / "fixture.mp4"
                media.write_bytes(b"original-video")
                args = self.args()
                builder = module.build_payload
                def swap(*positional, **keyword):
                    payload = builder(*positional, **keyword)
                    media.write_bytes(b"changed-video")
                    return payload
                with mock.patch.object(module, "build_payload", side_effect=swap), mock.patch.object(module, "authenticated_urlopen", return_value=Response()) as urlopen:
                    if module is VIDEO:
                        result = module.call_m3("fixture-key", NEW_ENDPOINT, args.model, media, "describe", args)
                    else:
                        result = module.call_m3("fixture-key", NEW_ENDPOINT, media, "describe", args)
                payload = json.loads(urlopen.call_args.args[0].data)
                source = payload["messages"][0]["content"][1]["source"]
                self.assertEqual(base64.b64decode(source["data"]), b"original-video")
                self.assertEqual(result["operation_fingerprint"], module.operation_fingerprint(
                    NEW_ENDPOINT, self.descriptor(module, media, args, b"original-video")))

    def test_endpoint_default_base_shapes_and_explicit_override(self):
        for module in (AUDIO, VIDEO):
            with self.subTest(module=module.__name__), mock.patch.object(module, "read_env", return_value={}), mock.patch.dict(module.os.environ, {}, clear=True):
                args = argparse.Namespace(endpoint=None, base_url=None, env_file="fixture.env")
                self.assertEqual(module.resolve_endpoint(args), NEW_ENDPOINT)
                for base in ("https://api.minimaxi.com", "https://api.minimaxi.com/anthropic", "https://api.minimaxi.com/anthropic/v1", OLD_ENDPOINT):
                    args.base_url = base
                    self.assertEqual(module.resolve_endpoint(args), OLD_ENDPOINT)
                args.base_url = None
                with mock.patch.object(module, "read_env", return_value={"MINIMAX_BASE_URL": "https://api.minimaxi.com"}):
                    self.assertEqual(module.resolve_endpoint(args), OLD_ENDPOINT)
                    with mock.patch.dict(module.os.environ, {"MINIMAX_BASE_URL": "https://api.minimax.cn"}):
                        self.assertEqual(module.resolve_endpoint(args), NEW_ENDPOINT)
                args.endpoint = "https://example.invalid/exact/messages"
                with mock.patch.object(module, "read_env", side_effect=AssertionError("explicit endpoint needs no env read")):
                    self.assertEqual(module.resolve_endpoint(args), args.endpoint)

    def test_cli_effort_validation_happens_before_input_or_credentials(self):
        for module in (AUDIO, VIDEO):
            with self.subTest(module=module.__name__), mock.patch("sys.argv", ["adapter", "--input", "missing.mp4", "--effort", "low"]), mock.patch.object(module, "read_env", side_effect=AssertionError("credential read forbidden")), contextlib.redirect_stderr(io.StringIO()) as error:
                with self.assertRaises(SystemExit) as stopped:
                    module.main()
                self.assertEqual(stopped.exception.code, 2)
                self.assertIn("--effort is supported only", error.getvalue())

    def test_cli_defaults_and_flash_manifest_match_wire_options(self):
        for module in (AUDIO, VIDEO):
            for model in ("MiniMax-M3", "MiniMax-M3.1-Flash"):
                with self.subTest(module=module.__name__, model=model), tempfile.TemporaryDirectory() as temporary:
                    output = Path(temporary) / "output"
                    media = Path(temporary) / "fixture.mp4"
                    media.write_bytes(b"fixture")
                    argv = ["adapter", "--input", str(media), "--output-dir", str(output)]
                    if model != "MiniMax-M3":
                        argv += ["--model", model]
                    probe = {"format": {"duration": "1"}, "streams": [
                        {"codec_type": "video", "width": 640, "height": 320},
                        {"codec_type": "audio"},
                    ]}
                    segment_function = "segment_video" if module is VIDEO else "segment_audio_as_video"
                    with mock.patch("sys.argv", argv), mock.patch.object(module, "ffprobe", return_value=probe), mock.patch.object(module, segment_function, return_value=[]), mock.patch.object(module, "read_env", return_value={}), mock.patch.dict(module.os.environ, {}, clear=True), contextlib.redirect_stdout(io.StringIO()):
                        module.main()
                    manifest = json.loads((output / "manifest.json").read_text())
                    self.assertEqual(manifest["model"], model)
                    self.assertEqual(manifest["endpoint"], NEW_ENDPOINT)
                    self.assertFalse(manifest["api_called"])
                    if model == "MiniMax-M3":
                        self.assertEqual(manifest["thinking"], {"type": "disabled"})
                        self.assertNotIn("output_config", manifest)
                    else:
                        self.assertEqual(manifest["thinking"], {"type": "adaptive"})
                        self.assertEqual(manifest["output_config"], {"effort": "max"})


if __name__ == "__main__":
    unittest.main()
