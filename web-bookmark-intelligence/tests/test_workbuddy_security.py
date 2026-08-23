import hashlib
import socket
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock


SCRIPT_DIR = Path(__file__).resolve().parents[1] / "scripts"
sys.path.insert(0, str(SCRIPT_DIR))

from intake_case import canonical_url  # noqa: E402
from run_workbuddy_capture import (  # noqa: E402
    KNOWN_IMPLEMENTATIONS,
    WORKBUDDY_V1_5_1_SHA256,
    dns_rebinding_gate,
    execute_attempt,
    identify_implementation,
    resolve_dns_snapshot,
)


def answer(family, address):
    sockaddr = (address, 443, 0, 0) if family == socket.AF_INET6 else (address, 443)
    return (family, socket.SOCK_STREAM, 6, "", sockaddr)


class WorkBuddySecurityTests(unittest.TestCase):
    def test_accepts_public_a_and_aaaa_answers(self):
        def resolver(*_args):
            return [answer(socket.AF_INET, "8.8.8.8"), answer(socket.AF_INET6, "2606:4700:4700::1111")]

        snapshot = resolve_dns_snapshot("example.com", resolver)

        self.assertEqual("passed", snapshot["status"])
        self.assertEqual(["A", "AAAA"], snapshot["families"])
        self.assertEqual([], snapshot["blocked_addresses"])

    def test_rejects_mixed_public_and_private_answers(self):
        def resolver(*_args):
            return [answer(socket.AF_INET, "8.8.8.8"), answer(socket.AF_INET, "127.0.0.1")]

        snapshot = resolve_dns_snapshot("example.com", resolver)

        self.assertEqual("blocked", snapshot["status"])
        self.assertEqual("dns_contains_non_public_or_mixed_addresses", snapshot["reason"])

    def test_rejects_nxdomain(self):
        def resolver(*_args):
            raise socket.gaierror(socket.EAI_NONAME, "fixture nxdomain")

        snapshot = resolve_dns_snapshot("missing.example", resolver)

        self.assertEqual("blocked", snapshot["status"])
        self.assertEqual("dns_nxdomain_or_failure", snapshot["reason"])

    def test_rejects_ipv4_mapped_private_ipv6(self):
        def resolver(*_args):
            return [answer(socket.AF_INET6, "::ffff:127.0.0.1")]

        snapshot = resolve_dns_snapshot("example.com", resolver)

        self.assertEqual("blocked", snapshot["status"])
        self.assertEqual(["127.0.0.1"], snapshot["blocked_addresses"])

    def test_rejects_resolution_change_before_dispatch(self):
        calls = 0

        def resolver(*_args):
            nonlocal calls
            calls += 1
            value = "8.8.8.8" if calls == 1 else "1.1.1.1"
            return [answer(socket.AF_INET, value)]

        gate = dns_rebinding_gate("example.com", resolver)

        self.assertEqual("blocked", gate["status"])
        self.assertEqual("dns_resolution_changed", gate["reason"])

    def test_ipv4_mapped_ip_literal_is_rejected_before_dns(self):
        url, reason = canonical_url("https://[::ffff:127.0.0.1]/")

        self.assertIsNone(url)
        self.assertEqual("non_public_ip_literal", reason)

    def test_unknown_exit_zero_script_has_no_version_identity(self):
        with tempfile.TemporaryDirectory() as temporary:
            script = Path(temporary) / "fake.py"
            script.write_text("raise SystemExit(0)\n", encoding="utf-8")

            identity = identify_implementation(script)

        self.assertFalse(identity["recognized"])
        self.assertEqual("unknown", identity["implementation"])
        self.assertIsNone(identity["version"])

    def test_retained_v1_5_1_hash_is_not_redirect_rebind_compatible(self):
        contract = KNOWN_IMPLEMENTATIONS[WORKBUDDY_V1_5_1_SHA256]

        self.assertEqual("v1.5.1", contract["version"])
        self.assertEqual("unproven", contract["redirect_rebind_protection"])

    def test_execute_attempt_runs_verified_bytes_without_a_path_open_race(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            out = root / "case"
            implementation = root / "workbuddy.py"
            original = b"print('verified implementation')\n"
            implementation.write_bytes(original)
            digest = hashlib.sha256(original).hexdigest()

            def fake_run(command, **kwargs):
                self.assertEqual("-", command[1])
                self.assertEqual(original, kwargs["input"])
                implementation.write_bytes(b"print('malicious replacement')\n")
                attempt_root = Path(command[command.index("--out") + 1])
                attempt_root.mkdir(parents=True, exist_ok=True)
                (attempt_root / "article.md").write_text("fixture", encoding="utf-8")
                implementation.write_bytes(original)
                return subprocess.CompletedProcess(command, 0, stdout="ok", stderr="")

            with mock.patch(
                "run_workbuddy_capture.subprocess.run", side_effect=fake_run
            ):
                receipt = execute_attempt(
                    [sys.executable, str(implementation), "https://example.com", "--mode", "playwright"],
                    implementation,
                    digest,
                    root,
                    out,
                    1,
                    "system",
                    10,
                )

        self.assertTrue(receipt["execution_input"]["unchanged"])
        self.assertTrue(receipt["execution_input"]["matches_verified_source"])
        self.assertTrue(receipt["implementation_unchanged"])
        self.assertEqual(digest, receipt["execution_input"]["sha256_before"])
        self.assertEqual("-", receipt["command"][1])


if __name__ == "__main__":
    unittest.main()
