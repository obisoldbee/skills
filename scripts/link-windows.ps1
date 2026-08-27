param(
    [switch]$Apply,
    [string]$Agent,
    [string]$Target,
    [switch]$AllAgents,
    [string]$Skill,
    [switch]$AllSkills,
    [switch]$SyncDevice
)

# Read-only Skill junction scan. Apply fails closed until a directory-handle-
# bound, exclusive Windows creation primitive is implemented and verified.

$ErrorActionPreference = 'Stop'

if ($Apply) {
    throw 'safe-consumer-create-unsupported: Windows apply is disabled (including SyncDevice); no repository update or junction creation was attempted'
}

if ($Agent -and $Agent -notmatch '^[a-z0-9]+(?:-[a-z0-9]+)*$') {
    throw "invalid-agent: $Agent"
}

# Resolve every ancestor junction too; Resolve-Path alone is a provider path,
# not a physical-path guarantee on Windows PowerShell 5.1.
function Resolve-PhysicalPath([string]$Path, [int]$Depth = 0) {
    if ($Depth -gt 40) { throw "link-resolution-limit: $Path" }
    $FullPath = [IO.Path]::GetFullPath($Path)
    $Root = [IO.Path]::GetPathRoot($FullPath)
    $Current = $Root
    foreach ($Part in $FullPath.Substring($Root.Length).Split([char[]]'\/', [StringSplitOptions]::RemoveEmptyEntries)) {
        $Item = Get-Item -LiteralPath (Join-Path $Current $Part) -Force
        $Current = $Item.FullName
        if (-not [bool]($Item.Attributes -band [IO.FileAttributes]::ReparsePoint)) { continue }
        $RawTarget = $null
        if ($null -ne $Item.PSObject.Properties['Target']) {
            $RawTarget = @($Item.Target)[0]
        }
        if ([string]::IsNullOrWhiteSpace([string]$RawTarget) -and
            $null -ne $Item.PSObject.Properties['LinkTarget']) {
            $RawTarget = @($Item.LinkTarget)[0]
        }
        if ([string]::IsNullOrWhiteSpace([string]$RawTarget)) {
            throw "physical-path-target-unavailable: $Current"
        }
        if ($RawTarget.StartsWith('\??\UNC\') -or $RawTarget.StartsWith('\\?\UNC\')) {
            $RawTarget = '\\' + $RawTarget.Substring(8)
        } elseif ($RawTarget.StartsWith('\??\') -or $RawTarget.StartsWith('\\?\')) {
            $RawTarget = $RawTarget.Substring(4)
        }
        if (-not [IO.Path]::IsPathRooted([string]$RawTarget)) {
            $RawTarget = Join-Path (Split-Path -Parent $Current) $RawTarget
        }
        $Current = Resolve-PhysicalPath $RawTarget ($Depth + 1)
    }
    return $Current
}

$ScriptDir = Resolve-PhysicalPath $PSScriptRoot
$ScriptPath = Join-Path $ScriptDir 'link-windows.ps1'
$RepoRoot = Resolve-PhysicalPath (Join-Path $ScriptDir '..')
$ExportsFile = Join-Path $RepoRoot 'config\skill-exports.tsv'
$TargetsFile = Join-Path $RepoRoot 'config\agent-paths.tsv'
$Verifier = Join-Path $RepoRoot 'scripts\verify_release.py'
$ConsumerPaths = Join-Path $RepoRoot 'scripts\consumer_paths.py'

if (-not (Test-Path -LiteralPath $ExportsFile -PathType Leaf) -or
    -not (Test-Path -LiteralPath $TargetsFile -PathType Leaf) -or
    -not (Test-Path -LiteralPath $Verifier -PathType Leaf) -or
    -not (Test-Path -LiteralPath $ConsumerPaths -PathType Leaf)) {
    throw "repository-root-input-missing: $RepoRoot"
}

$Python = if ($env:PYTHON) { $env:PYTHON } else { 'python' }
if (-not (Get-Command $Python -ErrorAction SilentlyContinue)) {
    throw "python-not-found: $Python"
}

function Assert-ConsumerTarget([string]$Path) {
    $null = & $Python -B $ConsumerPaths check --repository $RepoRoot --target $Path
    if ($LASTEXITCODE -ne 0) {
        throw "consumer-boundary-check-failed: $Path"
    }
}

if ($SyncDevice) {
    if ($Target -or $AllAgents -or $Skill -or $AllSkills) {
        throw 'sync-device-allows-only-optional-agent'
    }
    if (-not $env:USERPROFILE) {
        throw 'USERPROFILE-is-not-set'
    }

    $Mode = 'plan'
    Write-Host "operation=repository-device-refresh mode=$Mode repository=$RepoRoot"
    & $Python -B $Verifier $RepoRoot --check-repository
    if ($LASTEXITCODE -ne 0) {
        throw "repository-refresh-failed: $LASTEXITCODE"
    }

    $ConfiguredTargets = @(
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
    if ($ConfiguredTargets.Count -eq 0) {
        throw "agent-not-configured: $Agent"
    }

    $SelectedTargets = @()
    $MissingParents = 0
    foreach ($ConfiguredTarget in $ConfiguredTargets) {
        if (-not (Test-Path -LiteralPath $ConfiguredTarget.path -PathType Container)) {
            Write-Host "target-parent-missing $($ConfiguredTarget.agent) $($ConfiguredTarget.path)"
            $MissingParents++
            continue
        }
        $SelectedTargets += $ConfiguredTarget
    }
    if ($Agent -and $SelectedTargets.Count -eq 0) {
        throw "selected-agent-parent-missing: $Agent"
    }
    if ($SelectedTargets.Count -eq 0) {
        throw 'no-existing-agent-targets'
    }

    $PreflightFailures = 0
    foreach ($SelectedTarget in $SelectedTargets) {
        & powershell.exe -NoProfile -ExecutionPolicy Bypass -File $ScriptPath `
            -Agent $SelectedTarget.agent -AllSkills
        if ($LASTEXITCODE -ne 0) { $PreflightFailures++ }
    }
    if ($PreflightFailures -gt 0) {
        throw "device-refresh-preflight-failed: $PreflightFailures consumer roots"
    }

    $Exports = @(Import-Csv -LiteralPath $ExportsFile -Delimiter "`t")
    $Pairs = 0
    $ApplyOperations = 0
    foreach ($SelectedTarget in $SelectedTargets) {
        foreach ($Export in $Exports) {
            $Consumers = if ($Export.consumers) { $Export.consumers } else { 'all' }
            if ($Consumers -ne 'all') {
                $ConsumerSet = @($Consumers.Split(',') | ForEach-Object { $_.Trim() })
                if ($SelectedTarget.agent -notin $ConsumerSet) { continue }
            }
            $Pairs++
        }
    }

    Write-Host 'plan-ready apply-unavailable=Windows-safe-create-unsupported'
    Write-Host "summary operation=repository-device-refresh mode=$Mode agents=$($SelectedTargets.Count) pairs=$Pairs apply_operations=$ApplyOperations skipped_missing_parents=$MissingParents"
    exit 0
}

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
if ($Skill -and $Skill -notmatch '^[a-z0-9]+(?:-[a-z0-9]+)*$') {
    throw "invalid-skill: $Skill"
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

$Mode = 'scan'
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
    $TargetRequested = [IO.Path]::GetFullPath($TargetPath)
    $TargetPath = Resolve-PhysicalPath $TargetRequested
    Assert-ConsumerTarget $TargetRequested

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
    }
}

Write-Host "summary checked=$Checked would_link=$WouldLink linked=$Linked conflicts=$Conflicts missing_parents=$MissingParents"
if ($Conflicts -gt 0 -or $MissingParents -gt 0) {
    exit 4
}
