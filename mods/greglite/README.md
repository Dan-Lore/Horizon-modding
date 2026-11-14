# Greglite

**GregTech-inspired** Steam + LV Electric Age for Horizon — **not** a GTM/TFG jar port.

## What it does (v0.3)

### Steam Age
1. **LP Solid Boiler** → steam to adjacent machines  
2. Steam Alloy / Macerator / Compressor  

### Electric Age (LV)
1. Boiler → **`lv_steam_turbine`** → **`tin_cable_*`** → **`lv_*` processors**  
2. Also: combustion / gas turbine gens, battery buffer, charger, diode/transformer/hull, full singleblock processor set (forming, ore, chem, assembly), MV slice clones  
3. ≥2 EU recipes per processor type (datapack + fallbacks)  

Tracker: [`tracker/catalog.json`](tracker/catalog.json) · Plan: [`docs/greglite-electric-plan.md`](../../docs/greglite-electric-plan.md)

## Play

- **Working (do not break):** `create-dev` → `native-fdc87ae-8837f1d46495` (Steam 0.2 stack)  
- **Test (Electric):** `create-nightly-test` → `native-9f42064-e72cd9c26fa6`  

```powershell
powershell -File tools/pack-greglite.ps1   # defaults to create-nightly-test
# after native-build: restore native-content if /give unknown
powershell -File tools/restore-greglite-content.ps1 -Instance create-nightly-test -NativeVersion native-9f42064-e72cd9c26fa6
```

Smoke: coal in boiler beside turbine → cable → `lv_macerator` with copper → copper dust.

## Out of scope still

Multiblocks (EBF, large turbines, …), full material dict / ore gen, Create co-build on Nightly tip (Create pin `4e5296d` separate native).

## Build

```powershell
pwsh tools/pack-greglite.ps1
# then one native-build on instance create-dev (Nightly fdc87ae)
```

Smoke: `/give` boiler + machines; fuel the boiler; process beside it.  
Login chat alone ≠ registries loaded — see `docs/dev-tips-native-content.md`.

## Attribution

See [NOTICE](NOTICE). Inspired by GTM Steam Age; textures from GregTech-Modern (LGPL-3.0).
