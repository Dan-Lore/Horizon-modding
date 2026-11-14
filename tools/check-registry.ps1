#Requires -Version 5.1
<#
.SYNOPSIS
  At-most-once-per-day check of Horizon registry for TFG-adjacent mods.

.DESCRIPTION
  Reads local launcher cache horizon-index.json (preferred) or fails with a clear message.
  Skips work if already run today (UTC date in last-check.json) unless -Force.
#>
param(
  [switch]$Force,
  [string]$IndexPath = $(Join-Path $env:APPDATA 'horizon\mod-browser\horizon-index.json'),
  [string]$RepoRoot = $(Split-Path $PSScriptRoot -Parent)
)

$ErrorActionPreference = 'Stop'
$watchDir = Join-Path $RepoRoot 'docs\registry-watch'
$statePath = Join-Path $watchDir 'last-check.json'
$logPath = Join-Path $watchDir 'changelog.md'
New-Item -ItemType Directory -Force -Path $watchDir | Out-Null

$today = [DateTime]::UtcNow.ToString('yyyy-MM-dd')
if (-not $Force -and (Test-Path $statePath)) {
  $prev = Get-Content $statePath -Raw | ConvertFrom-Json
  if ($prev.date_utc -eq $today) {
    Write-Output "Already checked today (UTC $today). Use -Force to run again."
    Write-Output "Last summary: $($prev.summary)"
    exit 0
  }
}

if (-not (Test-Path $IndexPath)) {
  throw "Horizon index not found: $IndexPath — open the launcher Mods page (Horizon tab) once to refresh the cache."
}

$index = Get-Content $IndexPath -Raw -Encoding UTF8 | ConvertFrom-Json
$tracked = @(
  'create', 'ae2', 'jei', 'justenoughitems', 'roughlyenoughitems',
  'jade', 'lookat', 'appleskin', 'appleskin_horizon', 'connected_textures',
  'voicechat', 'horizonmatica'
)
$keywords = @('tfc', 'terrafirma', 'gregtech', 'gtceu', 'firmalife', 'greate', 'terrafirmagreg', 'tfg')

function Get-ProjectFingerprint($p) {
  $ver = $null
  if ($p.versions -and $p.versions.Count -gt 0) {
    $ver = $p.versions[0].version
    if (-not $ver) { $ver = $p.versions[0].name }
  }
  [pscustomobject]@{
    id        = $p.id
    name      = $p.name
    kind      = $p.kind
    downloads = $p.downloads
    version   = $ver
    summary   = $p.summary
  }
}

$byId = @{}
foreach ($p in $index.projects) { $byId[$p.id] = $p }

$snapshot = [ordered]@{}
foreach ($id in $tracked) {
  if ($byId.ContainsKey($id)) {
    $snapshot[$id] = Get-ProjectFingerprint $byId[$id]
  } else {
    $snapshot[$id] = $null
  }
}

$keywordHits = @()
foreach ($p in $index.projects) {
  $blob = ("{0} {1} {2}" -f $p.id, $p.name, $p.summary).ToLowerInvariant()
  foreach ($k in $keywords) {
    if ($blob.Contains($k)) {
      $keywordHits += (Get-ProjectFingerprint $p)
      break
    }
  }
}

$prevSnap = $null
if (Test-Path $statePath) {
  try { $prevSnap = (Get-Content $statePath -Raw | ConvertFrom-Json).snapshot } catch { $prevSnap = $null }
}

$changes = New-Object System.Collections.Generic.List[string]
foreach ($id in $tracked) {
  $cur = $snapshot[$id]
  $old = $null
  if ($prevSnap -and $prevSnap.PSObject.Properties.Name -contains $id) {
    $old = $prevSnap.$id
  }
  $curKey = if ($null -eq $cur) { '<missing>' } else { "{0}|{1}|{2}" -f $cur.version, $cur.downloads, $cur.name }
  $oldKey = if ($null -eq $old) { '<none>' } else { "{0}|{1}|{2}" -f $old.version, $old.downloads, $old.name }
  if ($curKey -ne $oldKey) {
    if ($null -eq $cur) {
      [void]$changes.Add("- ``$id`` removed / missing from registry")
    } elseif ($oldKey -eq '<none>' -or $null -eq $old) {
      [void]$changes.Add("- **new/first seen** ``$id``: $($cur.name) v$($cur.version) ($($cur.downloads) dl) — $($cur.summary)")
    } else {
      [void]$changes.Add("- **updated** ``$id``: v$($old.version)→v$($cur.version), dl $($old.downloads)→$($cur.downloads)")
    }
  }
}

$create = $snapshot['create']
$summary = if ($create) {
  "create=$($create.version) dl=$($create.downloads); tracked=$($tracked.Count); keyword_hits=$($keywordHits.Count); changes=$($changes.Count)"
} else {
  "create=<missing>; keyword_hits=$($keywordHits.Count); changes=$($changes.Count)"
}

$state = [ordered]@{
  date_utc     = $today
  checked_at   = [DateTime]::UtcNow.ToString('o')
  index_path   = $IndexPath
  project_count = @($index.projects).Count
  summary      = $summary
  snapshot     = $snapshot
  keyword_hits = $keywordHits
}

($state | ConvertTo-Json -Depth 6) | Set-Content -Path $statePath -Encoding UTF8

if ($changes.Count -gt 0) {
  if (-not (Test-Path $logPath)) {
    @(
      '# Registry watch changelog',
      '',
      'Append-only. Written by `tools/check-registry.ps1` when tracked entries change.',
      ''
    ) | Set-Content $logPath -Encoding UTF8
  }
  Add-Content -Path $logPath -Value "" -Encoding UTF8
  Add-Content -Path $logPath -Value "## $today" -Encoding UTF8
  Add-Content -Path $logPath -Value "" -Encoding UTF8
  foreach ($line in $changes) {
    Add-Content -Path $logPath -Value $line -Encoding UTF8
  }
  Write-Output "CHANGES DETECTED:"
  $changes | ForEach-Object { Write-Output $_ }
} else {
  Write-Output "No tracked changes since last snapshot."
}

Write-Output "Summary: $summary"
if ($create) {
  Write-Output "Create: $($create.name) v$($create.version) — $($create.summary)"
} else {
  Write-Output "Create: not in registry"
}
if ($keywordHits.Count -gt 0) {
  Write-Output "Keyword hits (tfc/gt/...):"
  $keywordHits | ForEach-Object { Write-Output (" - {0} ({1}) v{2}" -f $_.name, $_.id, $_.version) }
} else {
  Write-Output "Keyword hits (tfc/gt/...): none"
}
