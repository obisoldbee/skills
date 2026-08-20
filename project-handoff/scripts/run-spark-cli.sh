#!/bin/sh
set -eu

usage() {
  printf '%s\n' 'Usage: run-spark-cli.sh --cwd <absolute-dir> --prompt-file <file>'
}

terminal_failure() {
  status=$1
  shift
  if [ "$#" -gt 0 ]; then
    printf '%s\n' "$*" >&2
  fi
  printf 'PROJECT_HANDOFF_SPARK_TERMINAL_FAILURE exit=%s action=stop_lane visible_fallback=forbidden route_change=requires_new_user_request\n' "$status" >&2
  exit "$status"
}

cwd=''
prompt_file=''

while [ "$#" -gt 0 ]; do
  case "$1" in
    --cwd)
      if [ "$#" -lt 2 ]; then
        usage >&2
        terminal_failure 64
      fi
      cwd=$2
      shift 2
      ;;
    --prompt-file)
      if [ "$#" -lt 2 ]; then
        usage >&2
        terminal_failure 64
      fi
      prompt_file=$2
      shift 2
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      printf 'Unknown argument: %s\n' "$1" >&2
      usage >&2
      terminal_failure 64
      ;;
  esac
done

if [ -z "$cwd" ] || [ -z "$prompt_file" ]; then
  usage >&2
  terminal_failure 64
fi

case "$cwd" in
  /*) ;;
  *)
    terminal_failure 64 '--cwd must be an absolute directory path'
    ;;
esac

if [ ! -d "$cwd" ]; then
  terminal_failure 66 "Workspace does not exist: $cwd"
fi

if [ ! -r "$prompt_file" ] || [ ! -s "$prompt_file" ]; then
  terminal_failure 66 "Prompt file must be readable and non-empty: $prompt_file"
fi

if ! command -v codex >/dev/null 2>&1; then
  terminal_failure 69 'codex CLI is not available on PATH'
fi

codex_bin=$(command -v codex)

if [ -n "${CODEX_HOME:-}" ]; then
  source_codex_home=$CODEX_HOME
elif [ -n "${HOME:-}" ]; then
  source_codex_home=$HOME/.codex
else
  source_codex_home=''
fi

runtime_parent=${TMPDIR:-/tmp}
umask 077
isolated_codex_home=$(mktemp -d "$runtime_parent/project-handoff-spark.XXXXXX") || {
  terminal_failure 73 'Could not create isolated Spark CLI state directory'
}

cleanup() {
  if [ -n "${isolated_codex_home:-}" ] && [ -d "$isolated_codex_home" ]; then
    rm -rf -- "$isolated_codex_home"
  fi
}
trap cleanup EXIT
trap 'terminal_failure 129 "Spark CLI wrapper received HUP"' HUP
trap 'terminal_failure 130 "Spark CLI wrapper received INT"' INT
trap 'terminal_failure 143 "Spark CLI wrapper received TERM"' TERM
chmod 700 "$isolated_codex_home" || terminal_failure 73 'Could not secure isolated Spark CLI state directory'

# The CLI needs writable runtime state even for an ephemeral read-only agent run.
# Give it a private temporary home instead of allowing writes to the user's live
# state database. Copy only authentication when present; ignore user config,
# hooks, sessions, caches, and state files.
if [ -n "$source_codex_home" ] && [ -f "$source_codex_home/auth.json" ] && [ -r "$source_codex_home/auth.json" ]; then
  cp "$source_codex_home/auth.json" "$isolated_codex_home/auth.json" || terminal_failure 74 'Could not copy authentication into isolated Spark CLI state'
  chmod 600 "$isolated_codex_home/auth.json" || terminal_failure 73 'Could not secure isolated Spark CLI authentication'
fi

last_message_file=$isolated_codex_home/last-message.txt
diagnostic_file=$isolated_codex_home/diagnostic.log

if CODEX_HOME="$isolated_codex_home" "$codex_bin" exec \
  --strict-config \
  --ignore-user-config \
  --ephemeral \
  --skip-git-repo-check \
  --color never \
  -C "$cwd" \
  -s read-only \
  -m gpt-5.3-codex-spark \
  --disable concurrent_reasoning_summaries \
  -c 'model_reasoning_effort="xhigh"' \
  -c 'model_reasoning_summary="none"' \
  -c 'tool_output_token_limit=4096' \
  --output-last-message "$last_message_file" \
  - < "$prompt_file" > "$diagnostic_file" 2>&1; then
  if [ ! -r "$last_message_file" ] || [ ! -s "$last_message_file" ]; then
    terminal_failure 70 'Spark CLI succeeded without a final message'
  fi
  cat "$last_message_file"
  exit 0
else
  status=$?
  if [ -s "$diagnostic_file" ]; then
    tail -c 8192 "$diagnostic_file" >&2
    printf '\n' >&2
  fi
  terminal_failure "$status"
fi
