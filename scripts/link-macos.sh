#!/usr/bin/env bash
# Scan or explicitly create Skill symlinks from this checkout on macOS/Linux.
# Default is read-only. The script never creates target parents or replaces paths.

set -euo pipefail

apply=0
agent_filter=""
target_override=""
skill_filter=""
all_agents=0
all_skills=0
sync_device=0

usage() {
  echo "usage: $0 [--apply] (--agent agent-id | --target /absolute/existing/skills-dir | --all-agents) (--skill skill-name | --all-skills)"
  echo "       $0 --sync-device [--apply] [--agent agent-id]"
}

while [ "$#" -gt 0 ]; do
  case "$1" in
    --apply)
      apply=1
      ;;
    --agent)
      shift
      if [ "$#" -eq 0 ]; then
        usage >&2
        exit 2
      fi
      agent_filter="$1"
      ;;
    --all-agents)
      all_agents=1
      ;;
    --target)
      shift
      if [ "$#" -eq 0 ]; then
        usage >&2
        exit 2
      fi
      target_override="$1"
      ;;
    --skill)
      shift
      if [ "$#" -eq 0 ]; then
        usage >&2
        exit 2
      fi
      skill_filter="$1"
      ;;
    --all-skills)
      all_skills=1
      ;;
    --sync-device)
      sync_device=1
      ;;
    -h|--help)
      usage
      exit 0
      ;;
    *)
      usage >&2
      exit 2
      ;;
  esac
  shift
done

if [ -n "$agent_filter" ] && ! [[ "$agent_filter" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
  echo "error invalid-agent: $agent_filter" >&2
  exit 2
fi

script_dir="$(cd "$(dirname "$0")" && pwd -P)"
script_path="$script_dir/$(basename "$0")"
repo_root="$(cd "$script_dir/.." && pwd -P)"
exports_file="$repo_root/config/skill-exports.tsv"
targets_file="$repo_root/config/agent-paths.tsv"
verifier="$repo_root/scripts/verify_release.py"
consumer_paths="$repo_root/scripts/consumer_paths.py"

if [ ! -f "$exports_file" ] || [ ! -f "$targets_file" ] || [ ! -f "$verifier" ] || [ ! -f "$consumer_paths" ]; then
  echo "error repository-root-input-missing: $repo_root" >&2
  exit 2
fi

python_command="${PYTHON:-python3}"
if ! command -v "$python_command" >/dev/null 2>&1; then
  echo "error python-not-found: $python_command" >&2
  exit 2
fi
if [ "$apply" -eq 1 ]; then
  # Stop before even a device repository refresh on unsupported platforms.
  "$python_command" -B "$consumer_paths" check-create-support
fi

if [ "$sync_device" -eq 1 ]; then
  if [ -n "$target_override" ] || [ -n "$skill_filter" ] || [ "$all_agents" -eq 1 ] || [ "$all_skills" -eq 1 ]; then
    echo "error sync-device-allows-only-optional-agent" >&2
    exit 2
  fi
  mode="plan"
  if [ "$apply" -eq 1 ]; then
    mode="apply"
  fi
  echo "operation=repository-device-refresh mode=$mode repository=$repo_root"
  if [ "$apply" -eq 1 ] && [ "${OBISOLDBEE_SKILLS_REFRESHED:-0}" != "1" ]; then
    "$python_command" -B "$verifier" "$repo_root" --update-repository
    reentry=(--sync-device --apply)
    if [ -n "$agent_filter" ]; then
      reentry+=(--agent "$agent_filter")
    fi
    export OBISOLDBEE_SKILLS_REFRESHED=1
    exec bash "$repo_root/scripts/link-macos.sh" "${reentry[@]}"
  fi
  "$python_command" -B "$verifier" "$repo_root" --check-repository

  selected_agents=()
  missing_parents=0
  configured_matches=0
  while IFS="$(printf '\t')" read -r platform agent raw_path; do
    [ "$platform" = "platform" ] && continue
    [ "$platform" = "unix" ] || continue
    [ -z "$agent" ] && continue
    if [ -n "$agent_filter" ] && [ "$agent" != "$agent_filter" ]; then continue; fi
    configured_matches=$((configured_matches + 1))
    case "$raw_path" in
      "~/"*) target="$HOME/${raw_path#\~/}" ;;
      /*) target="$raw_path" ;;
      *) echo "error invalid-target-config: $agent $raw_path" >&2; exit 2 ;;
    esac
    if [ ! -d "$target" ]; then
      echo "target-parent-missing $agent $target"
      missing_parents=$((missing_parents + 1))
      continue
    fi
    selected_agents+=("$agent")
  done < "$targets_file"

  if [ "$configured_matches" -eq 0 ]; then
    echo "error agent-not-configured: $agent_filter" >&2
    exit 2
  fi
  if [ -n "$agent_filter" ] && [ "${#selected_agents[@]}" -eq 0 ]; then
    echo "error selected-agent-parent-missing: $agent_filter" >&2
    exit 4
  fi
  if [ "${#selected_agents[@]}" -eq 0 ]; then
    echo "error no-existing-agent-targets" >&2
    exit 4
  fi

  preflight_failures=0
  for agent in "${selected_agents[@]}"; do
    if ! bash "$script_path" --agent "$agent" --all-skills; then
      preflight_failures=$((preflight_failures + 1))
    fi
  done
  if [ "$preflight_failures" -gt 0 ]; then
    echo "error device-refresh-preflight-failed: $preflight_failures consumer roots" >&2
    exit 4
  fi

  pairs=0
  apply_operations=0
  for agent in "${selected_agents[@]}"; do
    while IFS="$(printf '\t')" read -r skill_name _source consumers; do
      [ "$skill_name" = "skill_name" ] && continue
      [ -z "$skill_name" ] && continue
      [ -z "$consumers" ] && consumers="all"
      if [ "$consumers" != "all" ]; then
        case ",$consumers," in *",$agent,"*) ;; *) continue ;; esac
      fi
      pairs=$((pairs + 1))
      if [ "$apply" -eq 1 ]; then
        bash "$script_path" --apply --agent "$agent" --skill "$skill_name"
        apply_operations=$((apply_operations + 1))
      fi
    done < "$exports_file"
  done

  if [ "$apply" -eq 1 ]; then
    for agent in "${selected_agents[@]}"; do
      bash "$script_path" --agent "$agent" --all-skills
    done
  else
    echo "plan-ready rerun-with=--sync-device --apply"
  fi
  echo "summary operation=repository-device-refresh mode=$mode agents=${#selected_agents[@]} pairs=$pairs apply_operations=$apply_operations skipped_missing_parents=$missing_parents"
  exit 0
fi

target_selector_count=0
if [ -n "$agent_filter" ]; then target_selector_count=$((target_selector_count + 1)); fi
if [ -n "$target_override" ]; then target_selector_count=$((target_selector_count + 1)); fi
if [ "$all_agents" -eq 1 ]; then target_selector_count=$((target_selector_count + 1)); fi
if [ "$target_selector_count" -ne 1 ]; then
  echo "error choose-exactly-one-agent-target-or-all-agents" >&2
  exit 2
fi
skill_selector_count=0
if [ -n "$skill_filter" ]; then skill_selector_count=$((skill_selector_count + 1)); fi
if [ "$all_skills" -eq 1 ]; then skill_selector_count=$((skill_selector_count + 1)); fi
if [ "$skill_selector_count" -ne 1 ]; then
  echo "error choose-exactly-one-skill-or-all-skills" >&2
  exit 2
fi
if [ "$apply" -eq 1 ] && [ "$all_agents" -eq 1 ]; then
  echo "error apply-does-not-allow-all-agents" >&2
  exit 2
fi
if [ "$apply" -eq 1 ] && [ "$all_skills" -eq 1 ]; then
  echo "error apply-does-not-allow-all-skills" >&2
  exit 2
fi
if [ -n "$skill_filter" ] && ! [[ "$skill_filter" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
  echo "error invalid-skill: $skill_filter" >&2
  exit 2
fi

if [ -n "$skill_filter" ]; then
  skill_configured=0
  while IFS="$(printf '\t')" read -r configured_name _; do
    [ "$configured_name" = "$skill_filter" ] && skill_configured=1
  done < "$exports_file"
  if [ "$skill_configured" -eq 0 ]; then
    echo "error skill-not-exported: $skill_filter" >&2
    exit 2
  fi
fi

target_agents=()
target_paths=()
if [ -n "$target_override" ]; then
  case "$target_override" in
    /*) ;;
    *)
      echo "error target-must-be-absolute: $target_override" >&2
      exit 2
      ;;
  esac
  target_agents+=("__override__")
  target_paths+=("$target_override")
else
  while IFS="$(printf '\t')" read -r platform agent raw_path; do
    [ "$platform" = "platform" ] && continue
    [ "$platform" = "unix" ] || continue
    [ -n "$agent_filter" ] && [ "$agent" != "$agent_filter" ] && continue
    case "$raw_path" in
      "~/"*) target="$HOME/${raw_path#\~/}" ;;
      /*) target="$raw_path" ;;
      *)
        echo "error invalid-target-config: $agent $raw_path" >&2
        exit 2
        ;;
    esac
    target_agents+=("$agent")
    target_paths+=("$target")
  done < "$targets_file"
fi

if [ "${#target_paths[@]}" -eq 0 ]; then
  echo "error agent-not-configured: $agent_filter" >&2
  exit 2
fi

mode="scan"
[ "$apply" -eq 1 ] && mode="apply"
echo "mode=$mode repository=$repo_root"

checked=0
would_link=0
linked=0
conflicts=0
missing_parents=0

for target_index in "${!target_paths[@]}"; do
  target_agent="${target_agents[$target_index]}"
  target="${target_paths[$target_index]}"
  if [ ! -d "$target" ]; then
    echo "target-parent-missing $target_agent $target"
    missing_parents=$((missing_parents + 1))
    continue
  fi
  target_requested="$target"
  target_identity="$("$python_command" -B "$consumer_paths" check --repository "$repo_root" --target "$target_requested")"
  target_resolved="$(cd "$target" && pwd -P)"
  target="$target_resolved"

  while IFS="$(printf '\t')" read -r skill_name source_rel consumers; do
    [ "$skill_name" = "skill_name" ] && continue
    [ -z "$skill_name" ] && continue
    [ -n "$skill_filter" ] && [ "$skill_name" != "$skill_filter" ] && continue
    [ -z "$consumers" ] && consumers="all"
    if [ "$target_agent" != "__override__" ] && [ "$consumers" != "all" ]; then
      case ",$consumers," in
        *",$target_agent,"*) ;;
        *) continue ;;
      esac
    fi
    if ! [[ "$skill_name" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
      echo "skill-name-invalid $skill_name"
      conflicts=$((conflicts + 1))
      continue
    fi
    case "$source_rel" in
      /*|*".."*)
        echo "source-config-invalid $skill_name $source_rel"
        conflicts=$((conflicts + 1))
        continue
        ;;
    esac
    source_candidate="$repo_root/$source_rel"
    if [ ! -d "$source_candidate" ] || [ ! -f "$source_candidate/SKILL.md" ]; then
      echo "source-invalid $skill_name $source_candidate"
      conflicts=$((conflicts + 1))
      continue
    fi
    source="$(cd "$source_candidate" && pwd -P)"
    case "$source" in
      "$repo_root"/*) ;;
      *)
        echo "source-outside-repository $skill_name $source"
        conflicts=$((conflicts + 1))
        continue
        ;;
    esac

    destination="$target/$skill_name"
    checked=$((checked + 1))
    if [ -L "$destination" ]; then
      current="$(readlink "$destination")"
      if [ "$current" = "$source" ] && [ -e "$destination" ]; then
        echo "healthy-link $destination -> $source"
      elif [ ! -e "$destination" ]; then
        echo "dangling-link-conflict $destination -> $current"
        conflicts=$((conflicts + 1))
      else
        echo "wrong-link-conflict $destination -> $current"
        conflicts=$((conflicts + 1))
      fi
      continue
    fi
    if [ -e "$destination" ]; then
      echo "real-path-conflict $destination"
      conflicts=$((conflicts + 1))
      continue
    fi

    echo "would-link $destination -> $source"
    would_link=$((would_link + 1))
    if [ "$apply" -eq 1 ]; then
      "$python_command" -B "$consumer_paths" create --repository "$repo_root" \
        --target "$target_requested" --name "$skill_name" --source "$source" --expected "$target_identity"
      echo "linked $destination -> $source"
      linked=$((linked + 1))
    fi
  done < "$exports_file"
done

echo "summary checked=$checked would_link=$would_link linked=$linked conflicts=$conflicts missing_parents=$missing_parents"
if [ "$conflicts" -gt 0 ] || [ "$missing_parents" -gt 0 ]; then
  exit 4
fi
