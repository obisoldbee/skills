#!/usr/bin/env bash
set -euo pipefail

if [[ $# -lt 1 ]]; then
  echo "usage: with_playwright_python.sh <python-script-or-args> [args...]" >&2
  exit 64
fi

candidate="${PLAYWRIGHT_PYTHON:-}"

if [[ -z "$candidate" ]] && command -v playwright >/dev/null 2>&1; then
  playwright_bin="$(command -v playwright)"
  first_line="$(head -n 1 "$playwright_bin" 2>/dev/null || true)"
  if [[ "$first_line" == '#!'* ]]; then
    candidate="${first_line#\#!}"
  fi
fi

if [[ -z "$candidate" ]]; then
  candidate="python3"
fi

# Split shebang-style commands such as "/usr/bin/env python3" deliberately.
# shellcheck disable=SC2206
candidate_parts=($candidate)

if ! "${candidate_parts[@]}" - <<'PY' >/dev/null 2>&1
import playwright
from playwright.async_api import async_playwright
from playwright.sync_api import sync_playwright
PY
then
  echo "blocked_runtime_missing_python_playwright: candidate=${candidate}" >&2
  echo "Set PLAYWRIGHT_PYTHON to the Python executable that owns the playwright package." >&2
  exit 69
fi

exec "${candidate_parts[@]}" "$@"
