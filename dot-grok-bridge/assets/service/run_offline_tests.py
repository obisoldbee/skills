"""Run bundled fake-transport checks without inherited bridge configuration.

Only temporary SQLite/files and loopback HTTP listeners are used. No service
startup, production database, credential lookup, or provider call is performed.
The fixture cases reuse base invariants through unittest inheritance/imports;
the number of executed cases is not a count of unique real-agent scenarios.
"""
import os
from pathlib import Path
import subprocess
import sys


def main():
    environment = os.environ.copy()
    for key in (
        "ADMIN_KEY", "GROK_KEY", "GROK_WEBHOOK_URL", "GROK_WEBHOOK_KEY",
        "BOT_ROUTES_FILE", "PUBLIC_BASE_URL", "CALLBACK_HOSTS",
        "OAUTH_REDIRECT_HOSTS", "DB_PATH", "BIND_HOST", "PORT",
        "MAX_COMPLETED_TURNS", "MAX_MESSAGES_PER_DAY",
        "CONVERSATION_TIMEOUT_SECONDS", "CLAIM_TIMEOUT_SECONDS", "PYTHONPATH",
    ):
        environment.pop(key, None)
    environment["PYTHONDONTWRITEBYTECODE"] = "1"
    return subprocess.call(
        [sys.executable, "-B", "-m", "unittest", "discover", "-s", ".", "-p", "test_*.py", "-q"],
        cwd=Path(__file__).resolve().parent,
        env=environment,
    )


if __name__ == "__main__":
    raise SystemExit(main())
