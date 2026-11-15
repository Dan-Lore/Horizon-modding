# TFC Horizon tracker

**Generated from:** `mods/tfc/tracker/catalog.json`  
**Plan:** [`docs/tfc-plan.md`](tfc-plan.md)  
**Updated:** 2026-11-15 — W0–W11 + W14–W15 scaffolded; W12 blocked; W13 deferred.

Legend: `done` | `wip` | `todo` | `blocked` | `deferred`

## Pack

| Role | Id | Notes |
| --- | --- | --- |
| pack | `tfg-horizon` | Enable TFC after pack-tfc into instance; pin stays `fdc87ae` for AE2 |

## Wave board

| Wave | System | Status |
| --- | --- | --- |
| W0 | scaffold | done |
| W1 | calendar_climate, thirst | done |
| W2 | rock_ore_slice, prospector_lite | done |
| W3 | knapping_stone_tools | done |
| W4 | pottery_pit_kiln | done |
| W5 | heating_forge_copper | done |
| W6 | bloomery_anvil | done |
| W7 | food_nutrition | done |
| W8 | crops_climate_gate | done |
| W9 | quern_barrel | done |
| W10 | wood_collapse | done |
| W11 | pan_sluice | done |
| W12 | full_worldgen | **blocked** (engine) |
| W13 | animals | **deferred** |
| W14 | parity_extras | done (content; some GUI deferred) |
| W15 | pack_polish | done |

## Smoke (local)

1. `python3 mods/tfc/tools/gen_content.py`
2. `python3 tools/pack-tfc.py` → instance `horizon-native-mods/tfc.hmod`
3. Native-build `tfg-horizon` with `--allow-version-mismatch` if needed
4. Login → climate/thirst action bar
5. Vessel on water; propick near `tfc:ore_native_copper`
6. Machine loop: pit kiln → forge → bloomery → anvil
