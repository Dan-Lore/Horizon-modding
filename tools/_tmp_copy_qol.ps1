$ErrorActionPreference = "Stop"
$src = Join-Path $env:APPDATA "horizon\instances\create-dev\horizon-native-mods"
$dst = Join-Path $env:APPDATA "horizon\instances\create-nightly-test\horizon-native-mods"
New-Item -ItemType Directory -Path $dst -Force | Out-Null
foreach ($m in @("jei.hnmod", "jade.hnmod")) {
    Copy-Item (Join-Path $src $m) (Join-Path $dst $m) -Force
    Write-Host "copied $m -> $dst"
}
Get-ChildItem $dst | Select-Object Name, Length | Format-Table -AutoSize
