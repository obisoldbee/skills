# link-windows.ps1
# 把本 monorepo 里所有含 SKILL.md 的 skill 子目录，逐个建 junction 到各 agent 的 skills 目录。
# 用法：在 Windows PowerShell 里运行  .\scripts\link-windows.ps1
# 依赖：无需管理员（mklink /J 目录联接免管理员）
# 自动发现：遍历仓库根下所有目录，含 SKILL.md 的即为 skill，无需手动列名字。

$ErrorActionPreference = 'Stop'

# 仓库根 = 本脚本所在 scripts/ 的上一级
$repo = Resolve-Path (Join-Path $PSScriptRoot '..')

# 目标 agent 的 skills 目录（按需增删；每个 agent 一个）
$targets = @(
    "$env:USERPROFILE\.workbuddy\skills"   # WorkBuddy
    # "$env:USERPROFILE\.claude\skills"    # Claude Code（取消注释启用）
)

# 自动发现所有 skill（含 SKILL.md 的顶层目录）
$skills = Get-ChildItem -Path $repo -Directory |
    Where-Object { Test-Path (Join-Path $_.FullName 'SKILL.md') }

if ($skills.Count -eq 0) {
    Write-Host "未在 $repo 下发现任何 skill（需含 SKILL.md）" -ForegroundColor Yellow
    exit 0
}

foreach ($t in $targets) {
    if (-not (Test-Path $t)) {
        Write-Host "创建目标目录: $t"
        New-Item -ItemType Directory -Path $t -Force | Out-Null
    }
    foreach ($s in $skills) {
        $link = Join-Path $t $s.Name
        if (Test-Path $link) {
            $existing = Get-Item $link
            if ($existing.Target -eq $s.FullName) {
                Write-Host "skip   $link (已指向正确)" -ForegroundColor Gray
                continue
            }
            Write-Host "remove $link (旧/错误指向)" -ForegroundColor Yellow
            Remove-Item -LiteralPath $link -Recurse -Force
        }
        cmd /c "mklink /J `"$link`" `"$($s.FullName)`"" | Out-Null
        Write-Host "linked $link -> $($s.FullName)" -ForegroundColor Green
    }
}

Write-Host "`n完成。共链接 $($skills.Count) 个 skill 到 $($targets.Count) 个 agent 目录。" -ForegroundColor Cyan
Write-Host "提示：改完 skill 内容后，WorkBuddy 需重启才会重新加载；git 同步见 README。"
