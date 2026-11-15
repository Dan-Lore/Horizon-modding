# Greglite Electric Age — plan (locked 2026-11-14)

Play Greglite on **`tfg-horizon`** / `native-fdc87ae-428278da87c5` only. `create-dev` and `create-nightly-test` are gone. File coverage stays in `tracker/coverage.json`. Behaviour is `docs/greglite-behavior.md` (0.5.0).

**Own mod:** `mods/greglite/` (not a GTM/TFG jar port).  
**Inspiration / textures:** GregTech Modern (LGPL) — clean Horizon rewrite + `NOTICE`.  
**Tracker:** `mods/greglite/tracker/catalog.json` → SQLite via `tools/greglite-tracker.ps1` (when present) → summary `docs/greglite-electric-tracker.md`.

## Pack instances (exactly two)

| Role | Launcher id | Label | Play version (2026-11-14) | Create |
| --- | --- | --- | --- | --- |
| **Working** (tested, do not break) | `create-dev` | TFG Horizon Draft | `native-fdc87ae-8837f1d46495` (Nightly `fdc87ae`) | no — Batch A + greglite 0.2 |
| **Test** (new work) | `create-nightly-test` | Create Nightly Test | `native-9f42064-e72cd9c26fa6` (Nightly tip + Greglite 0.3) | Create 0.9 isolated on `native-4e5296d-649518ee8b9d` (pin clash on tip) |

Rules:

- Native-build **only** on **test**. Never rebuild working “to try something”.
- Keep launcher **prune-old-versions off** while both natives must stay installed.
- No third pack instance. Promote test → working only after smoke (explicit step).
- Manifest: `pack/draft-mods.toml`.

## Goal

EU + generators + **all GTM singleblock electric machine types**, with **≥2 recipes per implemented machine**.  
World content starts **LV-only** (`greglite:lv_*`); higher tiers live in the tracker and ship in a later wave.

### In scope (tracker `todo` / waves)

- Generators: `steam_turbine`, `combustion`, `gas_turbine`
- Net/storage: cables, `battery_buffer_*`, `charger_4`, later `transformer` / `diode` / hulls
- Processors: full GTM singleblock type set (furnace, alloy, macerator, forming line, ore prep, chem/fluids, assemblers, …)

### Out of scope / `deferred`

- Multiblocks (EBF, large turbines, distillation tower, cleanroom, GCYM, …)
- Full material dict / ore gen / “TFG parity”
- Overvolt explosions until a dedicated wave

## Architecture refactor (before mass machines)

Today (v0.2): steam-only BE + `machine.rs` hardcoded; recipe `steam` field unused.

Target:

1. `EnergyBuffer` (Steam | Eu) + sync to menu data  
2. Table-driven `ProcessorSpec` / `GeneratorSpec` (no growing `match` in hooks)  
3. Honour energy cost in tick (`steam` / `eu` in JSON)  
4. EU net v1: adjacent tin cable, LV 32 V  
5. `gen_content.py` + tracker share one machine list  

Steam Age 0.2 loop must keep working after refactor.

## Waves

| Wave | Work |
| --- | --- |
| **W0** | Instance docs + tracker DB + energy/processor refactor |
| **W1** | Tin cable, LV `battery_buffer_4x`, LV `steam_turbine` |
| **W2** | Electric twins: alloy / macerator / compressor + `electric_furnace`; smoke boiler → turbine → machine |
| **W3** | Forming: hammer, bender, extruder, press, lathe, cutter, wiremill, packer |
| **W4** | Ore prep |
| **W5** | Fluids / chemistry (Horizon fluid tanks, hooks 54+) |
| **W6** | Assembler / circuits / polarizer / engraver / scanner |
| **W7** | Combustion + gas turbine (+ fuels) |
| **W8** | Transformer / diode / charger; thin utilities |
| **W9** | Tier clone LV → MV → … for machines already `done` |

Multitask: after W2 is green on **test**, parallelize 2–4 machines per task inside a wave. Do not start W3+ until W1–W2 smoke passes.

## Tracker statuses

Machine `done` only if block + logic + GUI + energy **and** ≥2 recipes `done`.  
`source_mod`: usually `gregtech_modern`; items may be `minecraft` / `greglite` / later `create`.

## Shipped (2026-11-14)

W0–W9 content + Rust table-driven EU/steam on test. Smoke: boiler lit → copper → `lv_macerator` → copper dust.  
Multiblocks remain `deferred`. Create co-build on tip: `left_out` (use Create-only native).

## Smoke (test only)

1. `pwsh tools/pack-greglite.ps1` into `create-nightly-test`  
2. `native-build --instance create-nightly-test`  
3. Restore native-content if needed  
4. Loop: coal → LP boiler → steam turbine → cable → `lv_macerator`  
5. `greglite-tracker` gaps for the wave = 0  
6. Leave `create-dev` / `8837` untouched  

## Related docs

- Steam slice: `mods/greglite/README.md`  
- MVP pack history: `docs/mvp-tfg-plan.md`  
- Transfer list: `docs/mod-transfer-list.md`  
- Progress board: `docs/greglite-electric-tracker.md`  
