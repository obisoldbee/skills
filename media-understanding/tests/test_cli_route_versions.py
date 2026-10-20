import importlib.util
from pathlib import Path
import subprocess
import unittest
from unittest import mock

spec = importlib.util.spec_from_file_location("route_versions", Path(__file__).resolve().parents[1] / "scripts/check_routes.py")
routes = importlib.util.module_from_spec(spec)
spec.loader.exec_module(routes)


class CliVersionTests(unittest.TestCase):
    def test_asr_requires_a_compatible_cli_without_provider_requests(self):
        executor = {"kind": "cli", "command": "mmx", "minimum_version": "1.0.26"}
        for output, supported in (("mmx 1.0.25", False), ("mmx 1.0.26", True),
                                  ("mmx 1.0.28", True), ("mmx 1.0.26-rc.1", False),
                                  ("mmx 1.0.28-canary", False), ("unknown", False)):
            with self.subTest(output=output), mock.patch.object(routes.shutil, "which", return_value="/fixture/mmx"), mock.patch.object(routes.subprocess, "run", return_value=subprocess.CompletedProcess([], 0, stdout=output)) as run:
                result = routes.inspect_executor(executor, Path("/fixture"))
            self.assertEqual(result["present"], supported)
            self.assertEqual(result["version_supported"], supported)
            run.assert_called_once_with(["/fixture/mmx", "--version"], text=True, capture_output=True, timeout=5, check=False)

    def test_version_probe_failure_is_not_an_available_executor(self):
        with mock.patch.object(routes.shutil, "which", return_value="/fixture/mmx"), mock.patch.object(routes.subprocess, "run", side_effect=subprocess.TimeoutExpired("mmx", 5)):
            result = routes.inspect_executor({"kind": "cli", "command": "mmx", "minimum_version": "1.0.26"}, Path("/fixture"))
        self.assertFalse(result["present"])
        self.assertFalse(result["version_supported"])


if __name__ == "__main__":
    unittest.main()
