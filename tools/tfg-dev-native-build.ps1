# Pack workshop .hmod mods into tfg-dev, native-build on Nightly fdc87ae,
# restore content trio, wipe mod-content cache, optionally re-pin tfg-horizon.
#
# Safe bounds: only touches horizon-launcher native cache + instances tfg-dev /
# tfg-horizon. Does NOT delete Nightly bases, user saves, or arbitrary dirs.
#
# Usage:
#   powershell -NoProfile -File tools\tfg-dev-native-build.ps1
#   powershell -NoProfile -File tools\tfg-dev-native-build.ps1 -RepinHorizon -RemoveOldNatives
#   powershell -NoProfile -File tools\tfg-dev-native-build.ps1 -SkipPack

param(
    [switch]$SkipPack,
    [switch]$RepinHorizon,
    [switch]$RemoveOldNatives,
    [string]$Nightly = "nightly-2026-11-08-fdc87ae"
)

$ErrorActionPreference = "Stop"
$Root = Split-Path $PSScriptRoot -Parent
$Exe = Join-Path $Root "launcher\windows-x64\horizon-launcher.exe"
if (-not (Test-Path $Exe)) {
    throw "missing launcher: $Exe"
}

$Dev = Join-Path $env:APPDATA "horizon\instances\tfg-dev"
$NativeMods = Join-Path $Dev "horizon-native-mods"
$HorizonMods = Join-Path $Dev "horizon-mods"
New-Item -ItemType Directory -Force -Path $NativeMods, $HorizonMods | Out-Null

function Invoke-Pack {
    param([string]$Name, [scriptblock]$Body)
    Write-Host "== pack $Name =="
    & $Body
}

if (-not $SkipPack) {
    Invoke-Pack gtceu {
        & powershell -NoProfile -File (Join-Path $Root "tools\pack-gtceu.ps1") -Out (Join-Path $NativeMods "gtceu.hmod")
    }
    Invoke-Pack adastra {
        python (Join-Path $Root "tools\pack-adastra.py")
        Copy-Item (Join-Path $Root "mods\adastra\dist\adastra.hmod") $NativeMods -Force
    }
    Invoke-Pack quests {
        python (Join-Path $Root "tools\pack-quests.py")
        Copy-Item (Join-Path $Root "mods\quests\dist\quests.hmod") $NativeMods -Force
    }
    Invoke-Pack teams {
        python (Join-Path $Root "tools\pack-teams.py")
        Copy-Item (Join-Path $Root "mods\teams\dist\teams.hmod") $NativeMods -Force
    }
    Invoke-Pack firmalife {
        python (Join-Path $Root "tools\pack-firmalife.py")
    }
    Invoke-Pack tfc {
        python (Join-Path $Root "tools\pack-tfc.py")
        Copy-Item (Join-Path $Root "mods\tfc\dist\tfc.hmod") $NativeMods -Force
    }
}

Write-Host "== mirror content (toml+assets+data) =="
python -c @"
import zipfile, shutil
from pathlib import Path
inst = Path(r'$Dev')
hm = inst / 'horizon-mods'
hm.mkdir(exist_ok=True)
for hmod in (inst / 'horizon-native-mods').glob('*.hmod'):
    dest = hm / hmod.stem
    if dest.exists():
        shutil.rmtree(dest)
    dest.mkdir(parents=True)
    with zipfile.ZipFile(hmod) as z:
        for n in z.namelist():
            if n.startswith(('assets/', 'data/')) or n == 'horizon-mod.toml':
                z.extract(n, dest)
    print(hmod.stem, 'mirrored')
"@

Write-Host "== native-build tfg-dev on $Nightly =="
& $Exe native-build --instance tfg-dev --version $Nightly --trust-native-code --ignore-pins
if ($LASTEXITCODE -ne 0) {
    Write-Host "native-build failed exit=$LASTEXITCODE — see %AppData%\Roaming\horizon-launcher\native\build.log"
    exit $LASTEXITCODE
}

$list = & $Exe instance list 2>&1 | Out-String
Write-Host $list
$active = $null
if ($list -match 'tfg-dev\)\s+(native-fdc87ae-\S+)') {
    $active = $Matches[1]
}
if (-not $active) {
    Write-Host "WARN: could not parse active native for tfg-dev"
} else {
    Write-Host "== active native: $active =="
    $verContent = Join-Path $env:APPDATA "horizon-launcher\versions\$active\native-content"
    New-Item -ItemType Directory -Force -Path $verContent | Out-Null
    python -c @"
import zipfile, shutil, json
from pathlib import Path
inst = Path(r'$Dev')
nc = Path(r'$verContent')
nc.mkdir(exist_ok=True)
for hmod in (inst / 'horizon-native-mods').glob('*.hmod'):
    mid = hmod.stem
    for dest in (nc / mid, inst / 'horizon-mods' / mid):
        if dest.exists():
            shutil.rmtree(dest)
        dest.mkdir(parents=True)
        with zipfile.ZipFile(hmod) as z:
            for n in z.namelist():
                if n.startswith(('assets/', 'data/')) or n == 'horizon-mod.toml':
                    z.extract(n, dest)
    print(mid, 'content ok')
mods_json = Path(r'$env:APPDATA') / 'horizon-launcher' / 'versions' / '$active' / 'native-mods.json'
if mods_json.exists():
    d = json.loads(mods_json.read_text(encoding='utf-8'))
    print('mods', [m['id'] for m in d.get('mods', [])])
    print('left_out', d.get('left_out'))
"@
}

$cache = Join-Path $Dev ".horizon-cache\mod-content"
if (Test-Path $cache) {
    Remove-Item -LiteralPath $cache -Recurse -Force
    Write-Host "== wiped mod-content cache =="
}

# Fail the script if any workshop mod is left_out (launcher exit 0 is not enough).
$modsJson = Join-Path $env:APPDATA "horizon-launcher\versions\$active\native-mods.json"
if ($active -and (Test-Path $modsJson)) {
    $parsed = Get-Content $modsJson -Raw | ConvertFrom-Json
    if ($parsed.left_out -and @($parsed.left_out).Count -gt 0) {
        Write-Host "FAIL: left_out = $($parsed.left_out | ConvertTo-Json -Compress)"
        Write-Host "Read %AppData%\Roaming\horizon-launcher\native\build.log — do not re-pin."
        exit 2
    }
}

if ($RepinHorizon -and $active) {
    Write-Host "== re-pin tfg-horizon -> $active =="
    & $Exe instance version tfg-horizon $active
}

if ($RemoveOldNatives -and $active) {
    $versions = Join-Path $env:APPDATA "horizon-launcher\versions"
    Get-ChildItem $versions -Directory -Filter "native-fdc87ae-*" |
        Where-Object { $_.Name -ne $active } |
        ForEach-Object {
            Write-Host "== remove old $($_.Name) =="
            & $Exe remove $_.Name
        }
}

Write-Host "DONE. Play tfg-dev, check latest.log 'content from N mod(s)' + horizon-mod-ids.json + /give."
exit 0
