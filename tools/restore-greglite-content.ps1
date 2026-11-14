# Copy greglite content into the active native build's native-content/ (and horizon-mods fallback).
# Use after native-build when versions\<hash>\native-content\greglite is missing.
param(
    [string]$Instance = "create-dev",
    [string]$NativeVersion = ""
)
$ErrorActionPreference = "Stop"
$src = Join-Path $PSScriptRoot "..\mods\greglite" | Resolve-Path
$launcherVersions = Join-Path $env:APPDATA "horizon-launcher\versions"
if (-not $NativeVersion) {
    $inst = Get-Content (Join-Path $env:APPDATA "horizon\instances\$Instance\mod-browser.json") -Raw -ErrorAction SilentlyContinue
    $listed = Get-ChildItem $launcherVersions -Directory | Where-Object { $_.Name -like "native-fdc87ae*" } | Sort-Object LastWriteTime -Descending | Select-Object -First 1
    $NativeVersion = $listed.Name
}
$dst = Join-Path $launcherVersions "$NativeVersion\native-content\greglite"
New-Item -ItemType Directory -Path $dst -Force | Out-Null
Copy-Item (Join-Path $src "horizon-mod.toml") $dst -Force
Copy-Item (Join-Path $src "assets") (Join-Path $dst "assets") -Recurse -Force
Copy-Item (Join-Path $src "data") (Join-Path $dst "data") -Recurse -Force
$hm = Join-Path $env:APPDATA "horizon\instances\$Instance\horizon-mods\greglite"
New-Item -ItemType Directory -Path $hm -Force | Out-Null
Copy-Item (Join-Path $src "horizon-mod.toml") $hm -Force
Copy-Item (Join-Path $src "assets") (Join-Path $hm "assets") -Recurse -Force
Copy-Item (Join-Path $src "data") (Join-Path $hm "data") -Recurse -Force
Write-Host "Restored native-content -> $dst"
Write-Host "Restored horizon-mods  -> $hm"
