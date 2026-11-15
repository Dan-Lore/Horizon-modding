# Pack mods/greglite into a combined .hmod (POSIX zip paths).
# Default: pack instance tfg-horizon on Nightly fdc87ae.
param(
    [switch]$Working,
    [string]$Out = ""
)
$ErrorActionPreference = "Stop"
if (-not $Out) {
    $Out = "C:\Users\smoln\AppData\Roaming\horizon\instances\tfg-horizon\horizon-native-mods\greglite.hmod"
}
$src = Join-Path $PSScriptRoot "..\mods\greglite" | Resolve-Path
$stage = Join-Path $PSScriptRoot "_greglite-pack"
if (Test-Path $stage) { Remove-Item $stage -Recurse -Force }
New-Item -ItemType Directory -Path (Join-Path $stage "mixins\greglite") -Force | Out-Null
Copy-Item (Join-Path $src "horizon-mod.toml") $stage
Copy-Item (Join-Path $src "assets") (Join-Path $stage "assets") -Recurse
Copy-Item (Join-Path $src "data") (Join-Path $stage "data") -Recurse
Copy-Item (Join-Path $src "horizon-mixin.toml") (Join-Path $stage "mixins\greglite\")
Copy-Item (Join-Path $src "api") (Join-Path $stage "mixins\greglite\api") -Recurse
Copy-Item (Join-Path $src "README.md"), (Join-Path $src "NOTICE") (Join-Path $stage "mixins\greglite\") -ErrorAction SilentlyContinue
$native = @{
    schema  = 1
    id      = "greglite"
    version = "0.5.0"
    game    = "26.3"
    horizon = "fdc87aecdbd116bf1e08adcd062fcbaea8c2e2ca"
    mixins  = "5a64af938ec86b00d53d16a408aabc0038fb3e57"
    hooks   = 411
} | ConvertTo-Json -Compress
$nativePath = Join-Path $stage "horizon-native.json"
[System.IO.File]::WriteAllText($nativePath, $native)
$outDir = Split-Path $Out -Parent
if (-not (Test-Path $outDir)) { New-Item -ItemType Directory -Path $outDir -Force | Out-Null }
if (Test-Path $Out) { Remove-Item $Out -Force }
python -c @"
import zipfile
from pathlib import Path
stage = Path(r'$stage')
out = Path(r'$Out')
with zipfile.ZipFile(out, 'w', zipfile.ZIP_DEFLATED) as z:
    for path in stage.rglob('*'):
        if path.is_file():
            z.write(path, path.relative_to(stage).as_posix())
print(out, out.stat().st_size)
"@
