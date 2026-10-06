"""Browser IDs survive CLI, health notifications and UTF-8 reports without live I/O."""
from contextlib import redirect_stderr, redirect_stdout
import io
import json
import os
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest
from unittest.mock import patch

SCRIPTS = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPTS))

from buddy_contract import dispatch_receipt
from render_report import render
import service_health


IDENTITIES = [9, "tabbit:group:FF07F2943109A214EF7BA5155F89A0F5",
              "chrome:tab:1824401190", "codex-browser:tab:page-1",
              "mcode-browser:tab:page-1"]


def report(identity, status="unconfirmed"):
    return {"receipt": dispatch_receipt("2026-10-02", "咖啡馆", None, None),
            "gift": "not_claimed", "page": {"status": status, "space_id": identity},
            "notifications": []}


class BrowserIdentityTests(unittest.TestCase):
    def test_report_cli_preserves_real_identity_and_utf8(self):
        for identity in IDENTITIES:
            with self.subTest(identity=identity):
                result = subprocess.run(
                    [sys.executable, "-B", str(SCRIPTS / "render_report.py")],
                    input=json.dumps(report(identity), ensure_ascii=False),
                    capture_output=True, text=True, encoding="utf-8",
                    env={**os.environ, "PYTHONIOENCODING": "cp1252", "PYTHONUTF8": "0"})
                self.assertEqual(result.returncode, 0, result.stderr)
                label = "空间 9" if type(identity) is int else "页面 " + identity
                self.assertIn("页面：关闭未确认（" + label + "）", result.stdout)
                self.assertIn("结果：派出结果未确认", result.stdout)
                closed = render(report(identity, "closed"))
                self.assertIn("页面：已关闭\n", closed)
                self.assertNotIn("（" + label + "）", closed)

    def test_invalid_json_identity_is_rejected_even_when_closed(self):
        invalid = [True, False, -1, 1.5, [], {}, "", " ", "9", "FF07F294",
                   "tabbit:group:", "tabbit:group:bad id", "tabbit:group:a\nb",
                   "tabbit:group:a\x00b", "tabbit:group:```", "unknown:tab:1",
                   "tabbit:group:" + "x" * 256]
        for status in ("closed", "preserved", "unconfirmed", "failed"):
            for identity in invalid:
                with self.subTest(status=status, identity=identity), self.assertRaises(ValueError):
                    render(report(identity, status))

    def test_health_cli_preserves_ids_and_persistent_transition_dedup(self):
        for identity in IDENTITIES:
            with self.subTest(identity=identity), tempfile.TemporaryDirectory() as directory:
                results = []
                with patch.object(service_health, "send_notice", return_value={
                        "status": "sent", "message_id": "om_fixture_only"}) as sender:
                    for phase in ("maintenance", "maintenance", "unknown", "available", "available"):
                        argv = ["service_health.py", "--phase", phase, "--page", "closed",
                                "--space-id", str(identity), "--evidence", "离线维护状态证据",
                                "--chat-id", "oc_fixture_only", "--state-dir", directory,
                                "--config", str(Path(directory) / "unused-config.json")]
                        output = io.StringIO()
                        with patch.object(sys, "argv", argv), redirect_stdout(output):
                            self.assertEqual(service_health.main(), 0)
                        results.append(json.loads(output.getvalue()))
                    self.assertEqual([r["transition"] for r in results],
                                     ["entered", None, None, "recovered", None])
                    self.assertEqual(sender.call_count, 2)
                    label = "空间 9" if type(identity) is int else "页面 " + identity
                    for call in sender.call_args_list:
                        rows = dict(call.args[3][1])
                        self.assertEqual(rows["页面"], "已关闭（" + label + "）")
                    state = json.loads((Path(directory) / "state.json").read_text())
                    self.assertEqual((state["version"], state["phase"], state["pending"]),
                                     (1, "available", None))
                    self.assertNotIn("space_id", state)
                    self.assertNotIn("page", state)

    def test_health_cli_rejects_invalid_or_missing_id_before_observe(self):
        for identity in (None, "-1", "", " ", "FF07F294", "tabbit:group:a\nb"):
            with self.subTest(identity=identity), tempfile.TemporaryDirectory() as directory:
                argv = ["service_health.py", "--phase", "unknown", "--page", "unconfirmed",
                        "--chat-id", "oc_fixture_only", "--state-dir", directory]
                if identity is not None:
                    argv += ["--space-id", identity]
                with patch.object(sys, "argv", argv), redirect_stderr(io.StringIO()), \
                        patch.object(service_health, "observe") as observe:
                    with self.assertRaises(SystemExit) as stopped:
                        service_health.main()
                    self.assertEqual(stopped.exception.code, 2)
                    observe.assert_not_called()
                self.assertEqual(list(Path(directory).iterdir()), [])

    def test_health_cli_no_page_does_not_require_identity_or_notify(self):
        with tempfile.TemporaryDirectory() as directory:
            argv = ["service_health.py", "--phase", "unknown", "--page", "not_created",
                    "--chat-id", "oc_fixture_only", "--state-dir", directory]
            with patch.object(sys, "argv", argv), redirect_stdout(io.StringIO()), \
                    patch.object(service_health, "send_notice") as sender:
                self.assertEqual(service_health.main(), 0)
                sender.assert_not_called()


if __name__ == "__main__":
    unittest.main()
