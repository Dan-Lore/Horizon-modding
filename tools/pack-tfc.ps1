# Pack mods/tfc into a combined .hmod (POSIX zip paths).
param(
    [string]$Out = ""
)
$ErrorActionPreference = "Stop"
$root = Split-Path $PSScriptRoot -Parent
if (-not $Out) {
    $Out = Join-Path $root "pack\mods\tfc.hmod"
}
python3 (Join-Path $PSScriptRoot "pack-tfc.py") $Out
