#!/usr/bin/env python3
"""Report local route prerequisites without reading secrets or calling providers."""

from __future__ import annotations

import argparse
import json
import os
import platform
import shutil
import stat
from pathlib import Path
from typing import Any


DEFAULT_AGNES_ENV = Path(".codex/secrets/agnes.env")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--home", type=Path, default=Path.home())
    parser.add_argument(
        "--agnes-env",
        type=Path,
        help="Override the Agnes env file path. The file contents are never read.",
    )
    return parser.parse_args()


def command_metadata(command: str) -> dict[str, Any]:
    """Resolve a command locally without invoking it."""
    resolved = shutil.which(command)
    return {
        "command": command,
        "present": resolved is not None,
        "resolved": resolved,
        "invoked": False,
    }


def tabbit_metadata(system: str, home: Path) -> dict[str, Any]:
    """Inspect the documented stable launcher only; never invoke the runtime."""
    local_app_data = os.environ.get("LOCALAPPDATA")
    if system == "Windows":
        candidate = (Path(local_app_data) / "Tabbit/LocalAgent/bin/tabbit-cli.exe"
                     if local_app_data else None)
    else:
        candidate = home / ".local/bin/tabbit-cli"
    present = candidate is not None and candidate.is_file()
    return {"command": "tabbit", "present": present,
            "resolved": str(candidate) if present else None, "invoked": False,
            "connection": "not_tested", "capabilities": "runtime_probe_required"}


def file_metadata(path: Path, display_path: str) -> dict[str, Any]:
    """Return non-content metadata for a credential file."""
    try:
        file_stat = path.stat()
    except FileNotFoundError:
        return {
            "path": display_path,
            "exists": False,
            "is_file": False,
            "is_symlink": path.is_symlink(),
            "private_permissions": None,
            "owner_matches_process": None,
        }

    getuid = getattr(os, "getuid", None)
    private_permissions = None
    owner_matches_process = None
    if getuid is not None:
        private_permissions = file_stat.st_mode & (stat.S_IRWXG | stat.S_IRWXO) == 0
        owner_matches_process = file_stat.st_uid == getuid()
    return {
        "path": display_path,
        "exists": True,
        "is_file": path.is_file(),
        "is_symlink": path.is_symlink(),
        "private_permissions": private_permissions,
        "owner_matches_process": owner_matches_process,
    }


def main() -> None:
    args = parse_args()
    if args.agnes_env is None:
        agnes_path = args.home / DEFAULT_AGNES_ENV
        agnes_display = "~/.codex/secrets/agnes.env"
    else:
        agnes_path = args.agnes_env.expanduser()
        agnes_display = str(args.agnes_env)

    system = platform.system()
    report = {
        "schema": "media-creator-local-check/v1",
        "provider_calls": False,
        "secrets_read": False,
        "chatgpt_login_checked": False,
        "host": {
            "system": system,
            "darwin": system == "Darwin",
        },
        "executors": {
            "ego_browser": command_metadata("ego-browser"),
            "mmx": command_metadata("mmx"),
            "tabbit": tabbit_metadata(system, args.home),
            "chrome": {"connection": "runtime_probe_required"},
            "codex_browser": {"connection": "runtime_probe_required", "state": "independent"},
        },
        "agnes_env": file_metadata(agnes_path, agnes_display),
    }
    print(json.dumps(report, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
