from __future__ import annotations

import json
import shutil
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
CHECKER = ROOT / "scripts" / "check_routes.py"


class RouteCheckTests(unittest.TestCase):
    def run_checker(self, config: dict, home: Path) -> tuple[int, str, str]:
        config_path = home / "routes.json"
        config_path.write_text(json.dumps(config), encoding="utf-8")
        result = subprocess.run(
            [sys.executable, str(CHECKER), "--config", str(config_path), "--home", str(home)],
            text=True,
            capture_output=True,
            check=False,
        )
        return result.returncode, result.stdout, result.stderr

    def test_secret_values_are_never_printed(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            secret = home / ".codex" / "secrets" / "minimax.env"
            secret.parent.mkdir(parents=True)
            secret.write_text("MINIMAX_API_KEY=top-secret-value\n", encoding="utf-8")
            secret.chmod(0o600)
            config = {"routes": [{
                "id": "test",
                "status": "active_if_configured",
                "provider": "test",
                "model": None,
                "credentials": {"file": "~/.codex/secrets/minimax.env", "required_env": ["MINIMAX_API_KEY"]},
                "executor": {"kind": "script", "path": "scripts/check_routes.py"},
            }]}
            code, stdout, stderr = self.run_checker(config, home)
            self.assertEqual(code, 0, stderr)
            self.assertNotIn("top-secret-value", stdout)
            self.assertEqual(json.loads(stdout)["routes"][0]["readiness"], "configured_not_called")

    def test_missing_required_key_is_reported(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            secret = home / ".codex" / "secrets" / "agnes.env"
            secret.parent.mkdir(parents=True)
            secret.write_text("AGNES_MODEL=agnes-2.5-flash\n", encoding="utf-8")
            secret.chmod(0o600)
            config = {"routes": [{
                "id": "test",
                "status": "active_if_configured",
                "provider": "test",
                "model": "agnes-2.5-flash",
                "credentials": {"file": "~/.codex/secrets/agnes.env", "required_env": ["AGNES_API_KEY", "AGNES_MODEL"]},
                "executor": {"kind": "script", "path": "scripts/check_routes.py"},
            }]}
            code, stdout, stderr = self.run_checker(config, home)
            self.assertEqual(code, 0, stderr)
            route = json.loads(stdout)["routes"][0]
            self.assertEqual(route["readiness"], "missing_credentials")
            self.assertEqual(route["credentials"]["missing_env"], ["AGNES_API_KEY"])

    def test_disabled_route_stays_disabled(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            config = {"routes": [{
                "id": "mimo",
                "status": "disabled",
                "provider": "mimo",
                "model": None,
                "credentials": {"file": "~/.codex/secrets/mimo.env", "required_env": []},
                "executor": {"kind": "none"},
                "runtime_state": "not_run/unverified_capability",
                "stop_reason": "local_route_not_ready: adapter_absent",
            }]}
            code, stdout, stderr = self.run_checker(config, home)
            self.assertEqual(code, 0, stderr)
            route = json.loads(stdout)["routes"][0]
            self.assertEqual(route["readiness"], "disabled")
            self.assertEqual(route["runtime_state"], "not_run/unverified_capability")
            self.assertTrue(route["stop_reason"].startswith("local_route_not_ready:"))

    def test_configuration_mismatch_precedes_external_binding(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            secret = home / ".codex" / "secrets" / "volc.env"
            secret.parent.mkdir(parents=True)
            secret.write_text("BASE_URL=https://example.invalid/plan\n", encoding="utf-8")
            secret.chmod(0o600)
            config = {"routes": [{
                "id": "platform",
                "status": "external_configuration",
                "provider": "test",
                "model": None,
                "credentials": {
                    "file": "~/.codex/secrets/volc.env",
                    "required_env": ["BASE_URL"],
                    "expected_values": {"BASE_URL": "https://example.invalid/platform"},
                    "safe_report_env": ["BASE_URL"],
                },
                "executor": {"kind": "none"},
            }]}
            code, stdout, stderr = self.run_checker(config, home)
            self.assertEqual(code, 0, stderr)
            route = json.loads(stdout)["routes"][0]
            self.assertEqual(route["readiness"], "configuration_mismatch")
            self.assertEqual(route["credentials"]["mismatched_expected_env"], ["BASE_URL"])

    def test_package_relative_script_is_ready(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            config = {"routes": [{
                "id": "internal",
                "status": "active_if_configured",
                "provider": "test",
                "model": None,
                "executor": {"kind": "script", "path": "scripts/check_routes.py"},
            }]}
            code, stdout, stderr = self.run_checker(config, home)
            self.assertEqual(code, 0, stderr)
            route = json.loads(stdout)["routes"][0]
            self.assertEqual(route["readiness"], "configured_not_called")
            self.assertTrue(route["executor"]["present"])
            self.assertEqual(route["executor"]["path"], "scripts/check_routes.py")

    def test_packaged_registry_contains_no_host_native_route(self) -> None:
        routes = json.loads((ROOT / "config" / "routes.json").read_text(encoding="utf-8"))["routes"]
        self.assertNotIn("codex-native-image", {route["id"] for route in routes})
        self.assertFalse(any(str(route.get("provider") or "").endswith("_native") for route in routes))
        self.assertFalse(any(route.get("authorization") == "session_native" for route in routes))
        self.assertFalse(any(route.get("executor", {}).get("kind") == "native" for route in routes))

    def test_minimax_mmx_is_scoped_nonvision_host_image_default(self) -> None:
        routes = json.loads((ROOT / "config" / "routes.json").read_text(encoding="utf-8"))["routes"]
        route = next(item for item in routes if item["id"] == "minimax-mmx-image")
        self.assertIsNone(route["model"])
        self.assertEqual(route["authorization"], "implicit_current_attachment_request")
        self.assertEqual(route["default_for"], ["nonvision_host_single_image_understanding"])
        self.assertEqual(route["authorization_scope"], "current_request_single_image_only")
        self.assertEqual(route["cost_scope"], "one_default_minimax_image_call")
        self.assertEqual(route["fallback_policy"], "requires_user_opt_in")

    def test_checker_reports_route_authorization_contract(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            home = Path(temporary)
            config = {"routes": [{
                "id": "default-image",
                "status": "active_if_configured",
                "provider": "minimax",
                "model": None,
                "authorization": "implicit_current_attachment_request",
                "default_for": ["nonvision_host_single_image_understanding"],
                "authorization_scope": "current_request_single_image_only",
                "cost_scope": "one_default_minimax_image_call",
                "fallback_policy": "requires_user_opt_in",
                "executor": {"kind": "script", "path": "scripts/check_routes.py"},
            }]}
            code, stdout, stderr = self.run_checker(config, home)
            self.assertEqual(code, 0, stderr)
            route = json.loads(stdout)["routes"][0]
            self.assertEqual(route["authorization"], "implicit_current_attachment_request")
            self.assertEqual(route["default_for"], ["nonvision_host_single_image_understanding"])
            self.assertEqual(route["authorization_scope"], "current_request_single_image_only")
            self.assertEqual(route["cost_scope"], "one_default_minimax_image_call")
            self.assertEqual(route["fallback_policy"], "requires_user_opt_in")

    def test_validator_rejects_renamed_host_native_route(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            package = Path(temporary) / "media-understanding"
            shutil.copytree(ROOT, package, ignore=shutil.ignore_patterns("__pycache__"))
            registry = package / "config" / "routes.json"
            data = json.loads(registry.read_text(encoding="utf-8"))
            data["routes"].append({
                "id": "zai-native-image",
                "status": "active_if_configured",
                "media": ["image"],
                "tasks": ["description"],
                "provider": "zai_native",
                "model": None,
                "authorization": "session_native",
                "credentials": None,
                "executor": {"kind": "none"},
            })
            registry.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
            result = subprocess.run(
                [sys.executable, str(package / "scripts" / "validate_skill.py")],
                text=True,
                capture_output=True,
                check=False,
            )
            self.assertEqual(result.returncode, 1, result.stdout + result.stderr)
            self.assertIn("host-native capability must not be a portable route: zai-native-image", result.stdout)


if __name__ == "__main__":
    unittest.main()
