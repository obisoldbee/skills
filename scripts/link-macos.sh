#!/usr/bin/env bash
# link-macos.sh
# 把本 monorepo 里所有含 SKILL.md 的 skill 子目录，逐个建 symlink 到各 agent 的 skills 目录。
# 用法：在 macOS/Linux 终端运行  bash scripts/link-macos.sh
# 依赖：用户目录内 ln -s 一般无需特殊权限
# 自动发现：遍历仓库根下所有目录，含 SKILL.md 的即为 skill，无需手动列名字。

set -euo pipefail

# 仓库根 = 本脚本所在 scripts/ 的上一级
repo="$(cd "$(dirname "$0")/.." && pwd)"

# 目标 agent 的 skills 目录（按需增删；每个 agent 一个）
targets=(
  "$HOME/.workbuddy/skills"   # WorkBuddy
  # "$HOME/.claude/skills"    # Claude Code（取消注释启用）
)

# 自动发现所有 skill（含 SKILL.md 的顶层目录）
mapfile -t skills < <(find "$repo" -maxdepth 1 -mindepth 1 -type d -exec test -f "{}/SKILL.md" \; -print)

if [ "${#skills[@]}" -eq 0 ]; then
  echo "未在 $repo 下发现任何 skill（需含 SKILL.md）" >&2
  exit 0
fi

for t in "${targets[@]}"; do
  mkdir -p "$t"
  for d in "${skills[@]}"; do
    name="$(basename "$d")"
    link="$t/$name"
    real="$(cd "$d" && pwd)"
    if [ -L "$link" ]; then
      cur="$(readlink "$link")"
      if [ "$cur" = "$real" ]; then
        echo "skip   $link (已指向正确)"
        continue
      fi
    fi
    [ -e "$link" ] && rm -rf "$link"
    ln -s "$real" "$link"
    echo "linked $link -> $real"
  done
done

echo ""
echo "完成。共链接 ${#skills[@]} 个 skill 到 ${#targets[@]} 个 agent 目录。"
echo "提示：改完 skill 内容后，对应 agent 需重启才会重新加载；git 同步见 README。"
