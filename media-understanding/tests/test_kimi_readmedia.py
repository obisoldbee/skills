"""Offline regressions for model binding, exact input scope and real tool evidence."""
import importlib.util
import json
import os
from pathlib import Path
import tempfile
import sys
import time
import unittest

PATH = Path(__file__).resolve().parents[1] / "scripts/providers/kimi_readmedia.py"
SPEC = importlib.util.spec_from_file_location("kimi_readmedia", PATH)
kimi = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(kimi)


class KimiReadMediaTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.root = Path(self.tmp.name)
        self.addCleanup(self.tmp.cleanup)

    def config(self, extra=""):
        f = self.root / "config.toml"
        f.write_text('[providers.example]\ntype="anthropic"\nbase_url="https://example.invalid"\napi_key="fixture-not-a-secret"\n'
                     '[models.m3]\nprovider="example"\nmodel="MiniMax-M3"\nmax_context_size=512000\ncapabilities=["video_in","tool_use"]\n' + extra)
        f.chmod(0o600)
        return f

    def test_exact_profile_and_ambiguous_alias(self):
        f = self.config()
        self.assertEqual(kimi.binding(f, "MiniMax-M3")[0], "m3")
        f = self.config('[models.second]\nprovider="example"\nmodel="MiniMax-M3"\n')
        with self.assertRaisesRegex(ValueError, "ambiguous"):
            kimi.binding(f, "MiniMax-M3")
        self.assertEqual(kimi.binding(f, "MiniMax-M3", "m3")[0], "m3")
        with self.assertRaisesRegex(ValueError, "alias_model"):
            kimi.binding(f, "agnes-3.0-flash", "m3")

    @unittest.skipIf(os.name == "nt", "POSIX permission check")
    def test_credentials_are_private(self):
        f = self.config(); f.chmod(0o644)
        with self.assertRaisesRegex(ValueError, "unsafe_credential_permissions"):
            kimi.binding(f, "MiniMax-M3")

    def media(self):
        f = self.root / "sample.mp4"; f.write_bytes(b"fixture-media")
        item = {"path": str(f), "kind": "video", "sha256": kimi.sha(f)}
        manifest = self.root / "manifest.json"; manifest.write_text(json.dumps([item]))
        return manifest, item

    def test_capability_hash_and_duplicate_checks(self):
        manifest, item = self.media()
        with self.assertRaisesRegex(ValueError, "unsupported_media_capability"):
            kimi.inputs(manifest, ["image_in"])
        self.assertEqual(len(kimi.inputs(manifest, ["video_in"])), 1)
        manifest.write_text(json.dumps([item, item]))
        with self.assertRaisesRegex(ValueError, "duplicate"):
            kimi.inputs(manifest, ["video_in"])
        item["sha256"] = "wrong"; manifest.write_text(json.dumps([item]))
        with self.assertRaisesRegex(ValueError, "hash_mismatch"):
            kimi.inputs(manifest, ["video_in"])

    def test_swarm_same_task_and_explicit_observers(self):
        _, item = self.media()
        prompt = kimi.make_prompt([item], "Observe controls", "swarm", 3)
        request = json.loads(prompt.splitlines()[1])
        self.assertEqual(len(request["items"]), 3)
        self.assertIn("{{item}}", request["prompt_template"])
        self.assertEqual([json.loads(x) for x in request["items"]], [{"observer_id": "R1"}, {"observer_id": "R2"}, {"observer_id": "R3"}])
        self.assertNotIn("resume_agent_ids", request)

    def test_exit_zero_without_media_evidence_is_not_success(self):
        _, item = self.media()
        home = self.root / "home"; out = self.root / "out"; out.mkdir()
        f = home / "sessions/s/agents/main/wire.jsonl"; f.parent.mkdir(parents=True)
        rows = [{"type": "llm.request", "model": "MiniMax-M3"},
                {"type": "context.append_loop_event", "event": {"type": "content.part", "part": {"type": "text", "text": "I watched it"}}},
                {"type": "context.append_loop_event", "event": {"type": "step.end", "finishReason": "end_turn"}}]
        f.write_text("\n".join(json.dumps(x) for x in rows))
        result = kimi.evidence(home, out, "MiniMax-M3", [item], "single", 3, lambda x: x)
        self.assertFalse(result["passed"])
        self.assertFalse(result["checks"]["exact_successful_reads"])

    def test_auth_rejection_is_not_unknown_or_media_failure(self):
        result = kimi.execution_result(1, False, 'provider.auth_error: 401 Invalid token (request id: abc123)')
        self.assertEqual(result["state"], "rejected")
        self.assertEqual(result["provider_request_id"], "abc123")
        self.assertEqual(kimi.execution_result(1, False, "timeout")["state"], "acceptance_unknown")
        self.assertEqual(kimi.execution_result(0, False, "plain text")["state"], "acceptance_unknown")

    def test_native_step_error_stops_cli_before_continuation(self):
        home = self.root / "home"
        wire = home / "sessions/s/agents/main/wire.jsonl"
        wire.parent.mkdir(parents=True)
        script = self.root / "fake_cli.py"
        marker = self.root / "must-not-continue"
        event = {"type": "context.append_loop_event", "event": {"type": "step.end", "finishReason": "error"}}
        script.write_text("from pathlib import Path\nimport time\n" +
                          f"Path({str(wire)!r}).write_text({(json.dumps(event)+chr(10))!r})\n" +
                          f"time.sleep(3)\nPath({str(marker)!r}).write_text('continued')\n")
        with (self.root / "log").open("w") as log:
            code, reason = kimi.run_cli([sys.executable, str(script)], self.root, os.environ.copy(), log, home, 10)
        self.assertNotEqual(code, 0)
        self.assertIn("native_model_step_error", reason)
        self.assertFalse(marker.exists())


if __name__ == "__main__":
    unittest.main()
