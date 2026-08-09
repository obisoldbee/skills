param(
    [switch]$Apply,
    [string]$Agent,
    [string]$Target,
    [switch]$AllAgents,
    [string]$Skill,
    [switch]$AllSkills
)

# Scan or explicitly create Skill junctions from this checkout on Windows.
# Default is read-only. No target parent or conflicting path is changed.

$ErrorActionPreference = 'Stop'

$TargetSelectorCount = 0
if ($Agent) { $TargetSelectorCount++ }
if ($Target) { $TargetSelectorCount++ }
if ($AllAgents) { $TargetSelectorCount++ }
if ($TargetSelectorCount -ne 1) {
    throw 'choose-exactly-one-agent-target-or-all-agents'
}
$SkillSelectorCount = 0
if ($Skill) { $SkillSelectorCount++ }
if ($AllSkills) { $SkillSelectorCount++ }
if ($SkillSelectorCount -ne 1) {
    throw 'choose-exactly-one-skill-or-all-skills'
}
if ($Apply -and $AllAgents) {
    throw 'apply-does-not-allow-all-agents'
}
if ($Agent -and $Agent -notmatch '^[a-z0-9]+(?:-[a-z0-9]+)*$') {
    throw "invalid-agent: $Agent"
}
if ($Skill -and $Skill -notmatch '^[a-z0-9]+(?:-[a-z0-9]+)*$') {
    throw "invalid-skill: $Skill"
}

$ScriptDir = $PSScriptRoot
$RepoRoot = (Resolve-Path (Join-Path $ScriptDir '..')).Path
$ExportsFile = Join-Path $RepoRoot 'config\skill-exports.tsv'
$TargetsFile = Join-Path $RepoRoot 'config\agent-paths.tsv'

if (-not (Test-Path -LiteralPath $ExportsFile -PathType Leaf) -or
    -not (Test-Path -LiteralPath $TargetsFile -PathType Leaf)) {
    throw "config-missing: $RepoRoot\config"
}

$Targets = @()
if ($Target) {
    if (-not [IO.Path]::IsPathRooted($Target)) {
        throw "target-must-be-absolute: $Target"
    }
    $Targets = @(
        [PSCustomObject]@{
            agent = '__override__'
            path = $Target
        }
    )
} else {
    $Targets = @(
        Import-Csv -LiteralPath $TargetsFile -Delimiter "`t" |
            Where-Object {
                $_.platform -eq 'windows' -and (-not $Agent -or $_.agent -eq $Agent)
            } |
            ForEach-Object {
                [PSCustomObject]@{
                    agent = $_.agent
                    path = $_.path.Replace('%USERPROFILE%', $env:USERPROFILE)
                }
            }
    )
}

if ($Targets.Count -eq 0) {
    throw "agent-not-configured: $Agent"
}

$Exports = @(Import-Csv -LiteralPath $ExportsFile -Delimiter "`t")
if ($Skill -and $Skill -notin @($Exports.skill_name)) {
    throw "skill-not-exported: $Skill"
}

$Mode = if ($Apply) { 'apply' } else { 'scan' }
Write-Host "mode=$Mode repository=$RepoRoot"

$Checked = 0
$WouldLink = 0
$Linked = 0
$Conflicts = 0
$MissingParents = 0

foreach ($TargetEntry in $Targets) {
    $TargetAgent = $TargetEntry.agent
    $TargetPath = $TargetEntry.path
    if (-not (Test-Path -LiteralPath $TargetPath -PathType Container)) {
        Write-Host "target-parent-missing $TargetAgent $TargetPath"
        $MissingParents++
        continue
    }

    foreach ($Export in $Exports) {
        $SkillName = $Export.skill_name
        $SourceRelative = $Export.source
        $Consumers = if ($Export.consumers) { $Export.consumers } else { 'all' }
        if ($Skill -and $SkillName -ne $Skill) {
            continue
        }
        if ($TargetAgent -ne '__override__' -and $Consumers -ne 'all') {
            $ConsumerSet = @($Consumers.Split(',') | ForEach-Object { $_.Trim() })
            if ($TargetAgent -notin $ConsumerSet) {
                continue
            }
        }
        if ($SkillName -notmatch '^[a-z0-9]+(?:-[a-z0-9]+)*$') {
            Write-Host "skill-name-invalid $SkillName"
            $Conflicts++
            continue
        }
        if ([IO.Path]::IsPathRooted($SourceRelative) -or
            $SourceRelative.Split([IO.Path]::DirectorySeparatorChar) -contains '..' -or
            $SourceRelative.Split('/') -contains '..') {
            Write-Host "source-config-invalid $SkillName $SourceRelative"
            $Conflicts++
            continue
        }

        $SourceCandidate = Join-Path $RepoRoot $SourceRelative
        if (-not (Test-Path -LiteralPath (Join-Path $SourceCandidate 'SKILL.md') -PathType Leaf)) {
            Write-Host "source-invalid $SkillName $SourceCandidate"
            $Conflicts++
            continue
        }
        $Source = (Resolve-Path -LiteralPath $SourceCandidate).Path
        if (-not $Source.StartsWith($RepoRoot + [IO.Path]::DirectorySeparatorChar, [StringComparison]::OrdinalIgnoreCase)) {
            Write-Host "source-outside-repository $SkillName $Source"
            $Conflicts++
            continue
        }

        $Destination = Join-Path $TargetPath $SkillName
        $Checked++
        $Existing = Get-Item -LiteralPath $Destination -Force -ErrorAction SilentlyContinue
        if ($null -ne $Existing) {
            $IsReparse = [bool]($Existing.Attributes -band [IO.FileAttributes]::ReparsePoint)
            if ($IsReparse) {
                $RawTarget = @($Existing.Target)[0]
                if ($RawTarget) {
                    if ([IO.Path]::IsPathRooted($RawTarget)) {
                        $ResolvedTarget = [IO.Path]::GetFullPath($RawTarget)
                    } else {
                        $ResolvedTarget = [IO.Path]::GetFullPath((Join-Path $TargetPath $RawTarget))
                    }
                } else {
                    $ResolvedTarget = ''
                }
                if ($ResolvedTarget -eq $Source -and (Test-Path -LiteralPath $Destination)) {
                    Write-Host "healthy-link $Destination -> $Source"
                } elseif (-not (Test-Path -LiteralPath $Destination)) {
                    Write-Host "dangling-link-conflict $Destination -> $RawTarget"
                    $Conflicts++
                } else {
                    Write-Host "wrong-link-conflict $Destination -> $RawTarget"
                    $Conflicts++
                }
            } else {
                Write-Host "real-path-conflict $Destination"
                $Conflicts++
            }
            continue
        }

        Write-Host "would-link $Destination -> $Source"
        $WouldLink++
        if ($Apply) {
            New-Item -ItemType Junction -Path $Destination -Target $Source | Out-Null
            $Created = Get-Item -LiteralPath $Destination -Force
            $CreatedRawTarget = @($Created.Target)[0]
            if ($CreatedRawTarget -and [IO.Path]::IsPathRooted($CreatedRawTarget)) {
                $CreatedResolvedTarget = [IO.Path]::GetFullPath($CreatedRawTarget)
            } elseif ($CreatedRawTarget) {
                $CreatedResolvedTarget = [IO.Path]::GetFullPath((Join-Path $TargetPath $CreatedRawTarget))
            } else {
                $CreatedResolvedTarget = ''
            }
            if ([bool]($Created.Attributes -band [IO.FileAttributes]::ReparsePoint) -and
                $CreatedResolvedTarget -eq $Source) {
                Write-Host "linked $Destination -> $Source"
                $Linked++
            } else {
                throw "apply-verification-failed: $Destination"
            }
        }
    }
}

Write-Host "summary checked=$Checked would_link=$WouldLink linked=$Linked conflicts=$Conflicts missing_parents=$MissingParents"
if ($Conflicts -gt 0 -or $MissingParents -gt 0) {
    exit 4
}
