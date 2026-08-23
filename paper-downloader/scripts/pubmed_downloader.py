#!/usr/bin/env python3
"""Run one explicitly authorized PubMed browser attempt and append its journal result."""

from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path


SCRIPT_DIR = Path(__file__).resolve().parent
if str(SCRIPT_DIR) not in sys.path:
    sys.path.insert(0, str(SCRIPT_DIR))

from browser_route_executor import execute_browser_route  # noqa: E402


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--journal", required=True, type=Path)
    parser.add_argument("--row-id", required=True)
    parser.add_argument("--attempt-id", required=True)
    parser.add_argument("--paper-dir", required=True, type=Path)
    parser.add_argument("--screenshot-dir", required=True, type=Path)
    parser.add_argument("--output-root", required=True, type=Path)
    parser.add_argument("--timeout-ms", default=30000, type=int)
    args = parser.parse_args()
    result = execute_browser_route("pubmed", args)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
