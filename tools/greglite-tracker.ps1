#Requires -Version 5.1
<#
.SYNOPSIS
  GregTech Electric Age tracker — catalog.json ↔ SQLite + progress markdown.

.DESCRIPTION
  build-db  — import mods/gtceu/tracker/catalog.json, scan content, write gtceu.db, regenerate docs/gtceu-electric-tracker.md
  status    — summary counts by tier/kind/wave
  gaps      — machines missing block, menu, or min EU recipes (processors)
#>
param(
  [Parameter(Position = 0)]
  [ValidateSet('build-db', 'status', 'gaps')]
  [string]$Action = 'status',
  [string]$RepoRoot = '',
  [string]$Wave
)

$ErrorActionPreference = 'Stop'
if (-not $RepoRoot) {
  $scriptDir = if ($PSScriptRoot) { $PSScriptRoot } else { Split-Path -Parent $MyInvocation.MyCommand.Path }
  $RepoRoot = Split-Path $scriptDir -Parent
}

$catalogPath = Join-Path $RepoRoot 'mods\gtceu\tracker\catalog.json'
$dbPath = Join-Path $RepoRoot 'mods\gtceu\tracker\gtceu.db'
$gtceuRoot = Join-Path $RepoRoot 'mods\gtceu'
$docPath = Join-Path $RepoRoot 'docs\gtceu-electric-tracker.md'
$recipeDir = Join-Path $gtceuRoot 'data\gtceu\recipe'
$blockDir = Join-Path $gtceuRoot 'data\gtceu\horizon\block'
$menuDir = Join-Path $gtceuRoot 'data\gtceu\horizon\menu'

if (-not (Test-Path $catalogPath)) {
  throw "Catalog not found: $catalogPath"
}

$menuAliases = @{
  'steam_solid_boiler_lp' = 'steam_boiler'
}

function Get-MenuFileName([string]$MachineId) {
  if ($menuAliases.ContainsKey($MachineId)) { return $menuAliases[$MachineId] }
  return $MachineId
}

function Invoke-TrackerDbImport($Rows, $CatalogPath, $DbPath) {
  $py = Join-Path $RepoRoot 'mods\gtceu\tools\tracker_db.py'
  if (-not (Test-Path $py)) { throw "Missing $py" }
  $rowsFile = [System.IO.Path]::GetTempFileName()
  try {
    $jsonRows = $Rows | ConvertTo-Json -Depth 6 -Compress
    $utf8 = New-Object System.Text.UTF8Encoding $false
    [System.IO.File]::WriteAllText($rowsFile, $jsonRows, $utf8)
    $args = @($py, $CatalogPath, $rowsFile, $DbPath)
    & python @args
    if ($LASTEXITCODE -ne 0) { throw "tracker_db.py failed ($LASTEXITCODE)" }
  } finally {
    Remove-Item -LiteralPath $rowsFile -Force -ErrorAction SilentlyContinue
  }
}

function Test-HasBlock([string]$Id) {
  Test-Path (Join-Path $blockDir "$Id.json")
}

function Test-HasMenu([string]$Id) {
  $menu = Get-MenuFileName $Id
  Test-Path (Join-Path $menuDir "$menu.json")
}

function Get-RecipeCount([string]$MachineId, [string]$GtmType, [string]$Tier) {
  if (-not (Test-Path $recipeDir)) { return 0 }
  if ($Tier -eq 'lv') {
    return @(Get-ChildItem -Path $recipeDir -Filter "eu_$MachineId`_*.json" -File).Count
  }
  $pattern = "gtceu:$GtmType"
  $n = 0
  Get-ChildItem -Path $recipeDir -Filter '*.json' -File | ForEach-Object {
    if ($_.Name -like 'eu_*') { return }
    try {
      $j = Get-Content $_.FullName -Raw -Encoding UTF8 | ConvertFrom-Json
      if ($j.type -eq $pattern -and $null -ne $j.steam) { $n++ }
    } catch { }
  }
  return $n
}

function Get-ContentRow($Machine) {
  $id = $Machine.id
  $gtm = $Machine.gtm_type
  $min = 0
  if ($Machine.PSObject.Properties.Name -contains 'min_recipes') {
    $min = [int]$Machine.min_recipes
  } elseif ($Machine.kind -eq 'processor') {
    $min = 2
  }
  $hasBlock = Test-HasBlock $id
  $hasMenu = Test-HasMenu $id
  $recipes = if ($Machine.kind -eq 'processor') { Get-RecipeCount $id $gtm $Machine.tier } else { 0 }
  $gap = @()
  if (-not $hasBlock) { $gap += 'block' }
  if (-not $hasMenu) { $gap += 'menu' }
  if ($Machine.kind -eq 'processor' -and $recipes -lt $min) { $gap += "recipes($recipes/$min)" }
  $content = if ($gap.Count -eq 0) { 'content_ok' } else { 'content_gap' }
  [pscustomobject]@{
    id            = $id
    gtm_type      = $gtm
    tier          = $Machine.tier
    kind          = $Machine.kind
    catalog_status = $Machine.status
    wave          = $Machine.wave
    min_recipes   = $min
    has_block     = $hasBlock
    has_menu      = $hasMenu
    recipe_count  = $recipes
    content_status = $content
    gaps          = ($gap -join ', ')
  }
}

$catalog = Get-Content $catalogPath -Raw -Encoding UTF8 | ConvertFrom-Json
$rows = foreach ($m in $catalog.machines) { Get-ContentRow $m }

function Write-TrackerDoc($Rows, $Catalog) {
  $today = [DateTime]::UtcNow.ToString('yyyy-MM-dd')
  $sb = New-Object System.Text.StringBuilder
  [void]$sb.AppendLine('# GregTech Electric Age — progress board')
  [void]$sb.AppendLine('')
  [void]$sb.AppendLine('**Generated from:** `mods/gtceu/tracker/catalog.json` + content scan')
  [void]$sb.AppendLine('**Plan:** [`docs/gtceu-electric-plan.md`](gtceu-electric-plan.md)')
  [void]$sb.AppendLine("**Updated:** $today UTC (``tools/gtceu-tracker.ps1`` build-db)")
  [void]$sb.AppendLine('')
  [void]$sb.AppendLine('Legend: `done` | `partial` | `todo` | `deferred` | `content_ok` | `content_gap`')
  [void]$sb.AppendLine('')

  [void]$sb.AppendLine('## Instances')
  [void]$sb.AppendLine('')
  [void]$sb.AppendLine('| Role | Id | Version | Notes |')
  [void]$sb.AppendLine('| --- | --- | --- | --- |')
  foreach ($prop in $Catalog.instances.PSObject.Properties) {
    $inst = $prop.Value
    $note = if ($inst.create) { 'Create 0.9; Electric builds' } else { 'Steam Age working native' }
    [void]$sb.AppendLine("| $($prop.Name) | ``$($inst.id)`` | ``$($inst.version)`` | $note |")
  }
  [void]$sb.AppendLine('')

  [void]$sb.AppendLine('## Summary')
  [void]$sb.AppendLine('')
  $ok = @($Rows | Where-Object { $_.content_status -eq 'content_ok' }).Count
  $gap = @($Rows | Where-Object { $_.content_status -eq 'content_gap' }).Count
  $done = @($Rows | Where-Object { $_.catalog_status -eq 'done' }).Count
  [void]$sb.AppendLine("| Machines in catalog | $($Rows.Count) |")
  [void]$sb.AppendLine("| Catalog ``done`` | $done |")
  [void]$sb.AppendLine("| Content complete (block+menu+recipes) | $ok |")
  [void]$sb.AppendLine("| Content gaps | $gap |")
  [void]$sb.AppendLine('')

  [void]$sb.AppendLine('## Milestones')
  [void]$sb.AppendLine('')
  [void]$sb.AppendLine('| id | title | catalog status |')
  [void]$sb.AppendLine('| --- | --- | --- |')
  foreach ($ms in $Catalog.milestones) {
    [void]$sb.AppendLine("| $($ms.id) | $($ms.title) | $($ms.status) |")
  }
  [void]$sb.AppendLine('')

  function Add-Section($Title, $Filter) {
    [void]$sb.AppendLine("## $Title")
    [void]$sb.AppendLine('')
    [void]$sb.AppendLine('| id | gtm_type | kind | wave | catalog | content | recipes |')
    [void]$sb.AppendLine('| --- | --- | --- | --- | --- | --- | --- |')
    foreach ($r in ($Rows | Where-Object $Filter | Sort-Object wave, id)) {
      $rc = if ($r.kind -eq 'processor') { "$($r.recipe_count)/$($r.min_recipes)" } else { '—' }
      [void]$sb.AppendLine("| ``$($r.id)`` | ``$($r.gtm_type)`` | $($r.kind) | $($r.wave) | $($r.catalog_status) | $($r.content_status) | $rc |")
    }
    [void]$sb.AppendLine('')
  }

  Add-Section 'Steam Age' { $_.tier -like 'steam*' }
  Add-Section 'Electric LV — net / power / utility' { $_.tier -eq 'lv' -and $_.kind -ne 'processor' }
  Add-Section 'Electric LV — processors' { $_.tier -eq 'lv' -and $_.kind -eq 'processor' }
  Add-Section 'Deferred / multiblock' { $_.catalog_status -eq 'deferred' -or $_.tier -eq 'multi' }

  $utf8 = New-Object System.Text.UTF8Encoding $false
  [System.IO.File]::WriteAllText($docPath, $sb.ToString(), $utf8)
  Write-Output "Wrote $docPath"
}

switch ($Action) {
  'build-db' {
    Invoke-TrackerDbImport $rows $catalogPath $dbPath
    Write-TrackerDoc $rows $catalog
  }
  'status' {
    $byTier = $rows | Group-Object tier | Sort-Object Name
    Write-Output "GregTech tracker — $($catalog.updated)"
    Write-Output "DB: $(if (Test-Path $dbPath) { $dbPath } else { '(run build-db)' })"
    foreach ($g in $byTier) {
      $ok = @($g.Group | Where-Object { $_.content_status -eq 'content_ok' }).Count
      Write-Output "  tier $($g.Name): $($g.Count) machines, content_ok=$ok"
    }
    $proc = @($rows | Where-Object { $_.kind -eq 'processor' })
    $euRecipes = ($proc | Measure-Object -Property recipe_count -Sum).Sum
    Write-Output "  processor EU recipes (sum per type): $euRecipes"
    $catDone = @($rows | Where-Object { $_.catalog_status -eq 'done' }).Count
    Write-Output "  catalog done: $catDone / $($rows.Count)"
  }
  'gaps' {
    $filtered = $rows | Where-Object { $_.content_status -eq 'content_gap' }
    if ($Wave) { $filtered = $filtered | Where-Object { $_.wave -eq $Wave }
    }
    if (-not $filtered) {
      Write-Output 'No content gaps.'
      exit 0
    }
    $filtered | Sort-Object wave, id | Format-Table id, wave, kind, gaps, recipe_count, min_recipes -AutoSize
  }
}