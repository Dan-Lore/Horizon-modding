# Pack mods/tfc into a combined .hmod (POSIX zip paths).
param(
    [string]$Out = ""
)
$ErrorActionPreference = "Stop"
$root = Join-Path $PSScriptRoot ".." | Resolve-Path
if (-not $Out) {
    $Out = Join-Path $env:USERPROFILE "AppData\Roaming\horizon\instances\tfg-horizon\horizon-native-mods\tfc.hmod"
}
python (Join-Path $PSScriptRoot "pack-tfc.py") $Out
