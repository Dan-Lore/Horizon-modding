# TFC Horizon — tracker board

**Generated from:** `mods/tfc/tracker/catalog.json`  
**Plan:** [`docs/tfc-plan.md`](tfc-plan.md)  
**Updated:** 2026-11-15 — mod **0.1.0** (W0–W15 tables + hybrid native)

| System | Wave | Status | Notes |
| --- | --- | --- | --- |
| scaffold | W0 | done | pack script + manifests |
| calendar / thin climate / thirst / HUD | W1 | done | `player_tick` + `hud` |
| rock/ore slice + prospector | W2 | done | content + propick scan |
| knapping / firepit | W3 | done | recipes + BE |
| pottery / pit kiln | W4 | done | items + fire recipes |
| heating / charcoal forge | W5 | done | heat tables + forge BE |
| bloomery / anvil | W6 | done | tables + BE |
| food nutrition / decay | W7 | done / wip | nutrients on HUD; item NBT decay limited |
| crops | W8 | done | crop blocks + climate tables |
| quern / barrel | W9 | done | BE + barrel_recipes |
| woodworking / collapse | W10 | done | supports + soft warning |
| panning / sluice / ores | W11 | done | pan + sluice BE |
| full worldgen | W12 | **blocked** | hybrid bridge remains |
| animals | W13 | **deferred** | entity AI hooks |
| chisel / powderkeg / blast furnace | W14 | done | content + stubs |
| pack polish | W15 | done | `draft-mods.toml` entry |

## Smoke

1. `python3 tools/pack-tfc.py`
2. Copy `pack/mods/tfc.hmod` into `tfg-horizon` `horizon-native-mods/`
3. Native-build on `fdc87ae` with Batch A (allow-version-mismatch as needed)
4. Join → HUD season/climate/thirst; `/give @s tfc:rock_andesite`; propick near ore
