# GregTech — continuation after the Electric Age checklist

**Date:** 2026-11-15  
**Supersedes for next work:** [`gtceu-electric-plan.md`](gtceu-electric-plan.md) (W0–W9 content checklist, locked 2026-11-14).  
**Own mod:** `mods/gtceu/` — clean Horizon rewrite, GTM textures + `NOTICE`.  
**Play instance:** `tfg-dev` → `native-fdc87ae-e0aa83869033` (Nightly `fdc87ae`, hooks 411, AE2 15.4.18, GregTech 0.5.5).  
`tfg-horizon` pinned to the same smoked native. Do not native-build it; rebuild only `tfg-dev`, then re-pin + drop older hashes.  
Create stays off this pin (`4e5296d` / `9c7f9b2`).

The 2026-11-14 plan’s instances `create-dev` and `create-nightly-test` are gone. Do not native-build them.

## Where the port actually is

`tracker/coverage.json` at **100%** measures files on disk:

| Signal | What the scorer counts | What the tick does |
| --- | --- | --- |
| 40 types × LV–UV | block JSON exists | one `EuProcessor` path: 1 input, or 2 for a short dual-input list, 1 output, consume 1 item |
| ≥8 recipes / type | non-placeholder JSON | shared recipe type `gtceu:<mtype>` for every tier |
| 34 `multi_*` blocks | `multiblocks_hit` | `Kind::Multiblock`: 128 V, 1 in / 1 out, recipe type `gtceu:multiblock`, no structure |
| EU net 100% | cable + transformer + buffer + diode files exist, plus a flat +10% | adjacent EU push; every cable is `V = 32 × amps`; transformer and diode are `Kind::Cable` |
| Generators | LV–HV block names | combustion and gas turbine burn solid coal; steam is an integer counter |
| Materials | dust/plate/rod/wire items | no material properties, no ore veins, no machine crafts |

Code: `mods/gtceu/api/src/registry.rs`, `processor.rs`, `generator.rs`, `net.rs`.

There is no crafting recipe for `lv_macerator`, `lv_machine_hull`, or LV components (motor, piston, robot arm). A player reaches machines with `/give`.

`miner` and `pump` are generic processors. They do not touch the world.

## Rule for every wave below

A wave is done only on **`tfg-dev`** after a real Play:

1. Active version is `native-fdc87ae-01abd5b2b6a6` (or a newer native built from that same pin).
2. `instances/tfg-dev/.horizon-cache/mod-content/<hash>/horizon-mod-ids.json` lists `gtceu`.
3. `/give` of the wave’s item succeeds.
4. The scenario in the wave table succeeds in game.
5. Login chat and `coverage.json` do not count.

Native-build only `tfg-dev`. Keep `tfg-horizon` pinned. Keep prune-old-versions off while `fdc87ae` must stay. Smoke path: `.cursor/rules/horizon-native-build-smoke.mdc`.

Do not add blocks to lift the coverage percent. New `multi_*` controllers and extra tiers stay parked until their wave.

## Waves

### N0 — Confirm the base loop

The checklist says W1–W2 already smoked (boiler → turbine → `lv_macerator`). That smoke was on a deleted test instance. Repeat it on the pack pin before any new mechanic.

Scenario: coal in LP boiler beside `lv_steam_turbine`, tin cable, copper in `lv_macerator` → copper dust.

If content is missing or the cache lists only `ae2`, restore `horizon-mod.toml` + `assets/` + `data/`, delete `.horizon-cache/mod-content/`, relaunch. No new Rust in that case.

Also point `docs/gtceu-electric-tracker.md` and `mods/gtceu/README.md` at `tfg-dev`. Leave `coverage.json` as the **content** score. Add a separate behavior checklist that starts at N0 = 1 loop, everything else open.

### N1 — EU network v2

Higher tiers are voltage numbers on the same push. This wave makes voltage, amps, and loss real. Later machines depend on it.

| Piece | Behavior |
| --- | --- |
| Cable | Material sets voltage and loss per block. `1x` = 1 A, `4x` = 4 A. Tin stays LV. |
| Machine intake | Accepts a packet only when packet V ≤ machine V. A higher packet is refused. Explosion stays a later wave. |
| Diode | Passes EU one way. |
| Transformer | Classic step: 4 A low ↔ 1 A high, step-up and step-down. |
| Battery buffer | Charges and discharges tier batteries in the four slots. Drop the `lv_battery` virtual-cap bonus. |

Scenario:

- LV turbine → tin `1x` → `lv_macerator` runs.
- Same tin cable on an MV machine does not run it.
- LV→MV transformer runs one MV machine at 1 A.

### N2 — One LV chain a player can walk

Replace independent stubs for this chain with recipes that feed the next step. Leave the other processor types alone.

Chain:

1. Vanilla copper, tin, iron.
2. LP boiler → `lv_steam_turbine` → tin cable.
3. Macerator: ore or ingot → dust. Electric furnace: dust → ingot.
4. Bender → plate. Wiremill → wire. Cable from wire.
5. New LV parts: motor, piston, conveyor or robot arm, machine hull.
6. Crafting recipes for `lv_macerator`, `lv_bender`, `lv_wiremill`, `lv_assembler`, hull, and the cable.

Scenario: from vanilla copper and tin, craft a second `lv_macerator`. `/give` is only for the vanilla starting items.

### N3 — Recipe semantics on machines that already run

Extend the recipe JSON used by N2 machines, plus centrifuge and electrolyzer:

- more than one output
- chance
- programmed-circuit slot (bender, extruder, lathe, forming press)
- `min_voltage`
- overclock: one tier up → ×2 speed, ×4 EU/t

GTM’s full recipe dump stays out. Import or hand-write only these types.

Scenario: the same macerator recipe runs on LV and MV; MV is faster and draws more EU/t. A recipe with `min_voltage` of MV does not start in an LV machine.

### N4 — Fluids, narrow

Processors have no fluid slots. Local `upstream` sources show no fluid type on the mod API. First step of this wave is to confirm tanks on the **installed** `fdc87ae` mod API (the old plan assumed hooks 54+).

If the API can store and move a fluid in a block entity:

- boiler: water → steam (replace the integer steam counter)
- turbine consumes that steam
- combustion burns a liquid fuel; gas turbine burns a gas
- chemical reactor and distillery: one fluid input and one fluid output

If the API cannot: record the gap for an upstream hook, and keep a single explicit stand-in (a steam bucket item) for the boiler→turbine loop. Do not invent fluid recipes for the rest of the chem set.

Scenario: a turbine with an empty steam buffer does not make EU; a boiler with water fills it; the macerator on that cable runs.

### N5 — Coke oven (first real multiblock)

`multi_*` controllers already tick as fake singleblocks. This wave gives **one** of them a structure. Prefer the coke oven: no EU, and its output feeds the blast furnace.

- Fixed structure of defined blocks.
- Controller does nothing while the structure is incomplete.
- Coal → coke. Creosote only if N4 fluids exist.
- Other `multi_*` blocks stay out of the behavior checklist.

Scenario: incomplete structure is inert; complete structure turns coal into coke. `/give gtceu:multi_coke_oven` alone is not the smoke.

### N6 — Electric blast furnace

After N1 (EU) and N5 (coke):

- Fixed structure, item hatches, energy hatch.
- Coil blocks set heat.
- Iron + coke → steel, at a heat the LV furnace recipe does not reach.
- Controller without the structure does not tick.

Scenario: incomplete EBF is inert; complete EBF with EU and coke yields steel.

### N7 — Vacuum freezer (0.5.1)

`multi_vacuum_freezer` is no longer a fake singleblock.

- Face-centred 3×3×3 shell: `ebf_casing` + `input_hatch` + `output_hatch` + `energy_hatch` (no coils; frost-proof casing deferred).
- Incomplete structure does not tick.
- Recipe type `gtceu:vacuum_freezer`: `hot_steel_ingot` → `steel_ingot` with EU.
- EBF steel recipe now outputs `hot_steel_ingot` so the freezer is required for cold steel.

Scenario: incomplete freezer is inert; formed freezer with EU cools hot steel. EBF alone no longer yields cold `steel_ingot`.

## After N7 (order only, no design yet)

Each one is its own wave and its own smoke:

1. Distillation tower and cracker (only after N4).
2. Large chemical reactor.
3. Cleanroom, then circuit assembler rules that require it.
4. Assembly line.

Parked until a named wave: fusion, bedrock miner, large turbines, GCYM, ore-vein worldgen, the rest of the ~120 material dict, Create×GregTech.

## Out of scope

- Treating `coverage.json` 100% as GregTech parity.
- Porting a GTM jar or executing Java machine code.
- Native-building TFC onto `tfg-horizon` in the same change as a GregTech wave.
- Tip Nightly `9f42064` while AE2 15.4.18 is on `fdc87ae`.
- Overvolt explosions (refuse the packet in N1; explosions wait).
- A third pack instance.

## Suggested next session

Verify N7 on `tfg-dev` (formed freezer cools hot steel). Then distillation tower / cracker, or behaviour checklist rows still open for N0–N6.
