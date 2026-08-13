#!/usr/bin/env python3
"""Public-package shape and safety tests."""

from __future__ import annotations

import importlib.util
import os
import shutil
import tempfile
import unittest
from pathlib import Path


PACKAGE = Path(__file__).resolve().parents[1]
VALIDATOR_PATH = PACKAGE / "scripts" / "validate_package.py"
SPEC = importlib.util.spec_from_file_location("document_workspace_package_validator", VALIDATOR_PATH)
assert SPEC is not None and SPEC.loader is not None
VALIDATOR = importlib.util.module_from_spec(SPEC)
SPEC.loader.exec_module(VALIDATOR)


class PackageValidationTest(unittest.TestCase):
    def test_real_package_is_valid_and_public_safe(self) -> None:
        result = VALIDATOR.validate_package(PACKAGE)
        self.assertEqual(result["status"], "valid")
        self.assertFalse(result["provider_calls"])
        self.assertFalse(result["network_calls"])
        self.assertFalse(result["machine_specific_paths"])

    def test_linked_node_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            candidate = Path(temporary) / "document-workspace"
            shutil.copytree(PACKAGE, candidate)
            target = candidate / "references" / "operations.md"
            target.unlink()
            target.symlink_to(candidate / "SKILL.md")
            with self.assertRaisesRegex(VALIDATOR.ValidationError, "linked package node"):
                VALIDATOR.validate_package(candidate)

    def test_machine_specific_path_is_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            candidate = Path(temporary) / "document-workspace"
            shutil.copytree(PACKAGE, candidate)
            path = candidate / "references" / "operations.md"
            machine_path = "/" + "Users" + "/example/private.txt"
            path.write_text(path.read_text(encoding="utf-8") + "\n" + machine_path + "\n", encoding="utf-8")
            with self.assertRaisesRegex(VALIDATOR.ValidationError, "user-home path"):
                VALIDATOR.validate_package(candidate)

    def test_transient_and_real_artifact_types_are_rejected(self) -> None:
        with tempfile.TemporaryDirectory() as temporary:
            candidate = Path(temporary) / "document-workspace"
            shutil.copytree(PACKAGE, candidate)
            transient = candidate / "scripts" / "__pycache__"
            transient.mkdir()
            (transient / "module.pyc").write_bytes(b"synthetic cache bytes")
            with self.assertRaisesRegex(VALIDATOR.ValidationError, "transient file"):
                VALIDATOR.validate_package(candidate)

        with tempfile.TemporaryDirectory() as temporary:
            candidate = Path(temporary) / "document-workspace"
            shutil.copytree(PACKAGE, candidate)
            (candidate / "references" / "sample.pdf").write_bytes(b"synthetic artifact bytes")
            with self.assertRaisesRegex(VALIDATOR.ValidationError, "artifact/credential file"):
                VALIDATOR.validate_package(candidate)


if __name__ == "__main__":
    unittest.main()
