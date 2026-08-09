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

usage() {
  echo "usage: $0 [--apply] (--agent agent-id | --target /absolute/existing/skills-dir | --all-agents) (--skill skill-name | --all-skills)"
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
if [ -n "$agent_filter" ] && ! [[ "$agent_filter" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
  echo "error invalid-agent: $agent_filter" >&2
  exit 2
fi
if [ -n "$skill_filter" ] && ! [[ "$skill_filter" =~ ^[a-z0-9]+(-[a-z0-9]+)*$ ]]; then
  echo "error invalid-skill: $skill_filter" >&2
  exit 2
fi

script_dir="$(cd "$(dirname "$0")" && pwd -P)"
repo_root="$(cd "$script_dir/.." && pwd -P)"
exports_file="$repo_root/config/skill-exports.tsv"
targets_file="$repo_root/config/agent-paths.tsv"

if [ ! -f "$exports_file" ] || [ ! -f "$targets_file" ]; then
  echo "error config-missing: $repo_root/config" >&2
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
      ln -s "$source" "$destination"
      if [ -L "$destination" ] && [ "$(readlink "$destination")" = "$source" ]; then
        echo "linked $destination -> $source"
        linked=$((linked + 1))
      else
        echo "apply-verification-failed $destination" >&2
        exit 3
      fi
    fi
  done < "$exports_file"
done

echo "summary checked=$checked would_link=$would_link linked=$linked conflicts=$conflicts missing_parents=$missing_parents"
if [ "$conflicts" -gt 0 ] || [ "$missing_parents" -gt 0 ]; then
  exit 4
fi
