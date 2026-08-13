#!/usr/bin/env python3
"""Inspect local media route bindings without calling providers or exposing secrets."""

from __future__ import annotations

import argparse
import json
import shutil
import stat
from pathlib import Path
from typing import Any


PACKAGE_ROOT = Path(__file__).resolve().parents[1]
DEFAULT_CONFIG = PACKAGE_ROOT / "config" / "routes.json"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--config", type=Path, default=DEFAULT_CONFIG)
    parser.add_argument("--home", type=Path, default=Path.home())
    parser.add_argument("--route", action="append", default=[], help="Inspect only this route id; repeatable.")
    return parser.parse_args()


def expand_home(value: str, home: Path) -> Path:
    if value == "~":
        return home
    if value.startswith("~/"):
        return home / value[2:]
    return Path(value).expanduser()


def dotenv_values(path: Path) -> dict[str, str]:
    if not path.is_file():
        return {}
    values: dict[str, str] = {}
    for raw in path.read_text(encoding="utf-8").splitlines():
        line = raw.strip()
        if not line or line.startswith("#"):
            continue
        if line.startswith("export "):
            line = line[7:].strip()
        if "=" in line:
            key, value = line.split("=", 1)
            key = key.strip()
            if key:
                values[key] = value.strip().strip("'\"")
    return values


def private_permissions(path: Path) -> bool | None:
    if not path.exists():
        return None
    return path.stat().st_mode & (stat.S_IRWXG | stat.S_IRWXO) == 0


def inspect_executor(executor: dict[str, Any], home: Path) -> dict[str, Any]:
    kind = executor.get("kind")
    if kind == "native":
        return {"kind": kind, "present": True, "evidence": "current_session"}
    if kind == "cli":
        command = str(executor["command"])
        resolved = shutil.which(command)
        skill = executor.get("skill")
        skill_present = None
        if skill:
            skill_present = expand_home(str(skill), home).is_file()
        present = bool(resolved) and skill_present is not False
        return {
            "kind": kind,
            "present": present,
            "command": command,
            "resolved": resolved,
            "skill_present": skill_present,
        }
    if kind == "skill":
        skill_path = expand_home(str(executor["path"]), home)
        helper_value = executor.get("helper")
        helper_path = expand_home(str(helper_value), home) if helper_value else None
        skill_present = skill_path.is_file()
        helper_present = helper_path.is_file() if helper_path else True
        return {
            "kind": kind,
            "present": skill_present and helper_present,
            "skill_path": str(skill_path),
            "skill_present": skill_present,
            "helper_path": str(helper_path) if helper_path else None,
            "helper_present": helper_present,
        }
    if kind == "script":
        relative = Path(str(executor.get("path", "")))
        if not relative.parts or relative.is_absolute():
            return {
                "kind": kind,
                "present": False,
                "path": str(relative),
                "error": "script path must be package-relative",
            }
        script_path = (PACKAGE_ROOT / relative).resolve()
        try:
            script_path.relative_to(PACKAGE_ROOT)
        except ValueError:
            return {
                "kind": kind,
                "present": False,
                "path": str(relative),
                "error": "script path escapes package root",
            }
        return {
            "kind": kind,
            "present": script_path.is_file(),
            "path": relative.as_posix(),
            "resolved": str(script_path),
        }
    if kind == "skill_name":
        return {
            "kind": kind,
            "present": None,
            "name": executor.get("name"),
            "evidence": "fresh_agent_discovery_required",
        }
    return {"kind": kind or "none", "present": False}


def inspect_credentials(credentials: dict[str, Any] | None, home: Path) -> dict[str, Any] | None:
    if credentials is None:
        return None
    path = expand_home(str(credentials["file"]), home)
    required = list(credentials.get("required_env", []))
    values = dotenv_values(path)
    keys = set(values)
    missing = sorted(set(required) - keys)
    expected = dict(credentials.get("expected_values", {}))
    mismatched = sorted(key for key, value in expected.items() if values.get(key) != value)
    safe_names = list(credentials.get("safe_report_env", []))
    return {
        "file": str(path),
        "exists": path.is_file(),
        "private_permissions": private_permissions(path),
        "required_env": required,
        "present_env": sorted(set(required) & keys),
        "missing_env": missing,
        "mismatched_expected_env": mismatched,
        "safe_values": {key: values[key] for key in safe_names if key in values},
    }


def readiness(route: dict[str, Any], executor: dict[str, Any], credentials: dict[str, Any] | None) -> str:
    declared = route["status"]
    if declared == "disabled":
        return "disabled"
    if credentials is not None:
        if not credentials["exists"] or credentials["missing_env"]:
            return "missing_credentials"
        if credentials["private_permissions"] is False:
            return "unsafe_credential_permissions"
        if credentials["mismatched_expected_env"]:
            return "configuration_mismatch"
    if declared in {"external_configuration", "discovery_required"}:
        return "needs_explicit_binding"
    if executor.get("present") is not True:
        return "missing_executor"
    if declared == "active":
        return "native_ready"
    return "configured_not_called"


def main() -> None:
    args = parse_args()
    config = json.loads(args.config.read_text(encoding="utf-8"))
    routes = config.get("routes", [])
    requested = set(args.route)
    known = {route.get("id") for route in routes}
    unknown = sorted(requested - known)
    if unknown:
        raise SystemExit(f"unknown route id(s): {', '.join(unknown)}")

    results = []
    for route in routes:
        if requested and route["id"] not in requested:
            continue
        executor = inspect_executor(route["executor"], args.home)
        credentials = inspect_credentials(route.get("credentials"), args.home)
        results.append({
            "id": route["id"],
            "declared_status": route["status"],
            "provider": route["provider"],
            "model": route.get("model"),
            "readiness": readiness(route, executor, credentials),
            "runtime_state": route.get("runtime_state"),
            "executor": executor,
            "credentials": credentials,
            "stop_reason": route.get("stop_reason"),
        })

    print(json.dumps({
        "schema": "media-understanding-route-check/v1",
        "provider_calls": False,
        "secrets_exposed": False,
        "routes": results,
    }, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
