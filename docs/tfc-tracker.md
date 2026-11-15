# TFC Horizon — tracker board

**Generated from:** `mods/tfc/tracker/catalog.json`  
**Plan:** [`docs/tfc-plan.md`](tfc-plan.md)  
**Updated:** 2026-11-15 — mod `0.1.0` scaffold through W15 tables (W12 blocked, W13 deferred)

## Pack

| Role | Id | Notes |
| --- | --- | --- |
| pack | `tfg-horizon` | Enable `tfc` after smoke; pin `fdc87ae` with AE2/Greglite |

## Summary

| Status | Count |
| --- | --- |
| done | most W0–W11 + W14 content/systems + W15 metal bridge table |
| blocked | `worldgen_full` (W12) |
| deferred | `animals` (W13) |
| todo | JEI categories, Jade plugins (W15 integration) |

## Waves

| Wave | Focus | Status |
| --- | --- | --- |
| W0 | Scaffold / pack | done |
| W1 | Calendar, climate, thirst, action-bar HUD | done |
| W2 | Rocks, ores, prospector | done |
| W3 | Knapping, firepit | done |
| W4 | Pottery, pit kiln | done |
| W5 | Heating, forge, casting | done |
| W6 | Bloomery, anvil | done |
| W7 | Nutrition / food decay | done |
| W8 | Crops | done |
| W9 | Quern, barrel | done |
| W10 | Log pile, support/collapse | done |
| W11 | Panning, sluice | done |
| W12 | Full worldgen | **blocked** (engine) |
| W13 | Animals | **deferred** |
| W14 | Chisel, powderkeg, blast furnace, glass | done (lite) |
| W15 | JEI/Jade + Greglite bridge | bridge table done; JEI/Jade todo |

## Smoke (W1–W2)

1. Pack with `python3 tools/pack-tfc.py`
2. Native-build on `tfg-horizon` (fdc87ae) with Batch A + Greglite
3. Login tip → action bar climate/thirst
4. `/give @s tfc:ceramic_jug` / `tfc:rock_andesite` / `tfc:ore_native_copper` / `tfc:prospectors_pick`
5. Use propick near ore

## Engine risks

See plan risk register. Persistent player data and full worldgen remain the main gaps; session state lives in native `player_state` until Host persistence is available.
