# Pack mods/tfc into mods/tfc/dist/tfc.hmod. Does not install it.
$ErrorActionPreference = "Stop"
$py = Join-Path $PSScriptRoot "pack-tfc.py"
python $py
if ($LASTEXITCODE -ne 0) { exit $LASTEXITCODE }
