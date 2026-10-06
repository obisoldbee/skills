import copy
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]

def load(name):
    spec = importlib.util.spec_from_file_location(name, ROOT / "scripts" / (name + ".py"))
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module

envelope_validator = load("validate_browser_envelope")
policy = load("check_browser_platform_copies")

class BrowserCostAndPolicyTests(unittest.TestCase):
    def test_known_authorized_cost_and_stop_boundaries(self):
        base = json.loads((ROOT / "tests/browser-envelope-cases.json").read_text())["bases"]["current-image"]
        self.assertFalse(envelope_validator.validate_envelope(base)["cost_preflight_valid"])
        cost = dict(quoted_cost=2, unit="CNY", authorized_budget=5,
                    authority_source="user message budget CNY 5", requires_purchase_or_subscription=False)
        cases = [(dict(), True), ({"quoted_cost": 5}, True), ({"quoted_cost": 6}, False),
                 ({"quoted_cost": None}, False), ({"quoted_cost": float("nan")}, False),
                 ({"authority_source": ""}, False), ({"requires_purchase_or_subscription": True}, False),
                 ({"quoted_cost": 0, "authorized_budget": 0, "authority_source": ""}, True)]
        for changes, expected in cases:
            with self.subTest(changes=changes):
                envelope = copy.deepcopy(base)
                envelope["cost"] = dict(cost, **changes)
                result = envelope_validator.validate_envelope(envelope)
                self.assertEqual(expected, result["valid"], result)
                self.assertEqual(expected, result["cost_preflight_valid"])

    def test_shared_policy_drift_or_missing_copy_is_detected(self):
        with tempfile.TemporaryDirectory() as temporary:
            root = Path(temporary)
            for relative in policy.COPIES:
                path = root / relative
                path.parent.mkdir(parents=True)
                path.write_text("shared browser policy")
            self.assertTrue(policy.check(root)["valid"])
            path.write_text("stale browser policy")
            self.assertFalse(policy.check(root)["valid"])
            path.unlink()
            self.assertFalse(policy.check(root)["valid"])
