# Greglite Electric Age — progress board

**Generated from:** `mods/greglite/tracker/catalog.json` + content scan
**Plan:** [`docs/greglite-electric-plan.md`](greglite-electric-plan.md)
**Updated:** 2026-11-14 — GTM parity coverage **100.00%** (`tracker/coverage.json`)

Legend: `done` | `partial` | `todo` | `deferred` | `content_ok` | `content_gap`

## Instances

| Role | Id | Version | Notes |
| --- | --- | --- | --- |
| working | `create-dev` | `native-fdc87ae-8837f1d46495` | Steam Age working native — do not rebuild |
| test | `create-nightly-test` | `native-9f42064-39096c24e354` | Greglite 0.4 + JEI/Jade; GTM textures baked; cables=iron_block (no false “not available yet”) |

## Coverage (weighted checklist vs GTM extract)

| Category | Score |
| --- | --- |
| TOTAL | **100.00%** |
| singleblock types/tiers | 100% (40 types × LV–UV, +macerator/arc_furnace/rock_crusher/welder/spooler/air_scrubber) |
| recipes depth (≥8/type) | 100% |
| generators / cables / materials / multis / EU / steam / GUI | 100% |

## Summary

| Machines in catalog | 61 |
| Catalog `done` | 55 |
| Content complete (block+menu+recipes) | 55 |
| Content gaps | 6 |

## Milestones

| id | title | catalog status |
| --- | --- | --- |
| W0 | Tracker + energy/processor refactor | done |
| W1 | EU core: cable, buffer, steam turbine | done |
| W2 | Electric twins + furnace | done |
| W3 | Forming line | done |
| W4 | Ore prep | done |
| W5 | Fluids / chemistry | done |
| W6 | Assembly / circuits | done |
| W7 | Combustion + gas turbine | done |
| W8 | Net polish + utilities | done |
| W9 | Tier clone LV→MV→… | done |

## Steam Age

| id | gtm_type | kind | wave | catalog | content | recipes |
| --- | --- | --- | --- | --- | --- | --- |
| `steam_alloy_smelter` | `alloy_smelter` | processor | 0.2 | done | content_ok | 2/2 |
| `steam_compressor` | `compressor` | processor | 0.2 | done | content_ok | 8/2 |
| `steam_macerator` | `macerator` | processor | 0.2 | done | content_ok | 10/2 |
| `steam_solid_boiler_lp` | `steam_solid_boiler` | generator | 0.2 | done | content_ok | — |

## Electric LV — net / power / utility

| id | gtm_type | kind | wave | catalog | content | recipes |
| --- | --- | --- | --- | --- | --- | --- |
| `lv_battery_buffer_4x` | `battery_buffer_4x` | storage | W1 | done | content_ok | — |
| `lv_steam_turbine` | `steam_turbine` | generator | W1 | done | content_ok | — |
| `tin_cable_1x` | `cable` | cable | W1 | done | content_ok | — |
| `tin_cable_4x` | `cable` | cable | W1 | done | content_ok | — |
| `lv_combustion` | `combustion` | generator | W7 | done | content_ok | — |
| `lv_gas_turbine` | `gas_turbine` | generator | W7 | done | content_ok | — |
| `lv_buffer` | `buffer` | utility | W8 | done | content_ok | — |
| `lv_charger_4` | `charger_4` | storage | W8 | done | content_ok | — |
| `lv_diode` | `diode` | utility | W8 | done | content_ok | — |
| `lv_machine_hull` | `machine_hull` | utility | W8 | done | content_ok | — |
| `lv_miner` | `miner` | utility | W8 | done | content_ok | — |
| `lv_pump` | `pump` | utility | W8 | done | content_ok | — |
| `lv_transformer` | `transformer` | transformer | W8 | done | content_ok | — |

## Electric LV — processors

| id | gtm_type | kind | wave | catalog | content | recipes |
| --- | --- | --- | --- | --- | --- | --- |
| `lv_alloy_smelter` | `alloy_smelter` | processor | W2 | done | content_ok | 2/2 |
| `lv_compressor` | `compressor` | processor | W2 | done | content_ok | 2/2 |
| `lv_electric_furnace` | `electric_furnace` | processor | W2 | done | content_ok | 2/2 |
| `lv_macerator` | `macerator` | processor | W2 | done | content_ok | 2/2 |
| `lv_bender` | `bender` | processor | W3 | done | content_ok | 2/2 |
| `lv_cutter` | `cutter` | processor | W3 | done | content_ok | 2/2 |
| `lv_extruder` | `extruder` | processor | W3 | done | content_ok | 2/2 |
| `lv_forge_hammer` | `forge_hammer` | processor | W3 | done | content_ok | 2/2 |
| `lv_forming_press` | `forming_press` | processor | W3 | done | content_ok | 2/2 |
| `lv_lathe` | `lathe` | processor | W3 | done | content_ok | 2/2 |
| `lv_packer` | `packer` | processor | W3 | done | content_ok | 2/2 |
| `lv_wiremill` | `wiremill` | processor | W3 | done | content_ok | 2/2 |
| `lv_electromagnetic_separator` | `electromagnetic_separator` | processor | W4 | done | content_ok | 2/2 |
| `lv_ore_washer` | `ore_washer` | processor | W4 | done | content_ok | 2/2 |
| `lv_rock_crusher` | `rock_crusher` | processor | W4 | done | content_ok | 2/2 |
| `lv_sifter` | `sifter` | processor | W4 | done | content_ok | 2/2 |
| `lv_thermal_centrifuge` | `thermal_centrifuge` | processor | W4 | done | content_ok | 2/2 |
| `lv_arc_furnace` | `arc_furnace` | processor | W5 | done | content_ok | 2/2 |
| `lv_autoclave` | `autoclave` | processor | W5 | done | content_ok | 2/2 |
| `lv_brewery` | `brewery` | processor | W5 | done | content_ok | 2/2 |
| `lv_canner` | `canner` | processor | W5 | done | content_ok | 2/2 |
| `lv_centrifuge` | `centrifuge` | processor | W5 | done | content_ok | 2/2 |
| `lv_chemical_bath` | `chemical_bath` | processor | W5 | done | content_ok | 2/2 |
| `lv_chemical_reactor` | `chemical_reactor` | processor | W5 | done | content_ok | 2/2 |
| `lv_distillery` | `distillery` | processor | W5 | done | content_ok | 2/2 |
| `lv_electrolyzer` | `electrolyzer` | processor | W5 | done | content_ok | 2/2 |
| `lv_extractor` | `extractor` | processor | W5 | done | content_ok | 2/2 |
| `lv_fermenter` | `fermenter` | processor | W5 | done | content_ok | 2/2 |
| `lv_fluid_heater` | `fluid_heater` | processor | W5 | done | content_ok | 2/2 |
| `lv_fluid_solidifier` | `fluid_solidifier` | processor | W5 | done | content_ok | 2/2 |
| `lv_mixer` | `mixer` | processor | W5 | done | content_ok | 2/2 |
| `lv_air_scrubber` | `air_scrubber` | processor | W6 | done | content_ok | 2/2 |
| `lv_assembler` | `assembler` | processor | W6 | done | content_ok | 2/2 |
| `lv_circuit_assembler` | `circuit_assembler` | processor | W6 | done | content_ok | 2/2 |
| `lv_gas_collector` | `gas_collector` | processor | W6 | done | content_ok | 2/2 |
| `lv_laser_engraver` | `laser_engraver` | processor | W6 | done | content_ok | 2/2 |
| `lv_polarizer` | `polarizer` | processor | W6 | done | content_ok | 2/2 |
| `lv_scanner` | `scanner` | processor | W6 | done | content_ok | 2/2 |

## Deferred / multiblock

| id | gtm_type | kind | wave | catalog | content | recipes |
| --- | --- | --- | --- | --- | --- | --- |
| `assembly_line` | `assembly_line` | multiblock | multi | deferred | content_gap | — |
| `cleanroom` | `cleanroom` | multiblock | multi | deferred | content_gap | — |
| `distillation_tower` | `distillation_tower` | multiblock | multi | deferred | content_gap | — |
| `electric_blast_furnace` | `electric_blast_furnace` | multiblock | multi | deferred | content_gap | — |
| `large_chemical_reactor` | `large_chemical_reactor` | multiblock | multi | deferred | content_gap | — |
| `steam_large_turbine` | `steam_large_turbine` | multiblock | multi | deferred | content_gap | — |

