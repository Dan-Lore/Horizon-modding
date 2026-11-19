# GregTech behaviour checklist (0.5.1)

File coverage in `mods/gtceu/tracker/coverage.json` only counts blocks and recipe JSON. This list is the playable behaviour.

A row is **done** only after Play on **`tfg-dev`** (or a newer native built for that pin): `gtceu` in `horizon-mod-ids.json`, `/give` works, scenario succeeds. Do not native-build pinned `tfg-horizon` just to tick these boxes.

Code/datapack for these rows shipped in GregTech 0.5.0. Unit tests live in `api/src/eu_rules.rs` (no game required).

## N0 — base loop

`/give` is allowed for the four blocks and the fuel. Copper is vanilla.

1. Coal in `gtceu:steam_solid_boiler_lp` with water (bucket in the fuel slot, or a `minecraft:water` block beside it).
2. `gtceu:lv_steam_turbine` beside the boiler. The boiler's steam tank drops and the turbine's EU rises.
3. `gtceu:tin_cable_1x` from the turbine to `gtceu:lv_macerator`.
4. `minecraft:copper_ingot` in the macerator becomes `gtceu:copper_dust`.

## N1 — EU net

1. The same tin `1x` cable runs the LV macerator.
2. That cable does not run an MV machine (`gtceu:mv_macerator` stays idle).
3. `gtceu:lv_transformer` between the LV side and one MV machine runs that machine at 1 A of 128 V.
4. `gtceu:lv_diode` passes EU only along its `facing`.
5. `gtceu:lv_battery_buffer_4x` charges `gtceu:lv_battery` and gives that charge back. An `mv_battery` in the LV buffer does not.

## N2 — LV craft chain

Start with vanilla copper, iron, coal, slime balls, redstone, and `gtceu:tin_ingot`. No `/give` of other GregTech items.

1. Three iron ingots craft `gtceu:iron_plate`. Slime and coal craft `gtceu:rubber`.
2. Eight iron plates craft `gtceu:lv_machine_hull`. Plates, copper, and the hull craft `gtceu:lv_wiremill`.
3. The wiremill turns copper and tin ingots into `gtceu:copper_wire` and `gtceu:tin_wire`. Wire plus rubber crafts `gtceu:tin_cable_1x`.
4. Cable, wire, and iron craft `gtceu:lv_motor`, then `gtceu:lv_piston`, then `gtceu:lv_robot_arm`. Wire, redstone, and a plate craft `gtceu:programmed_circuit_1`.
5. Hull, motor, piston, and a plate craft a second `gtceu:lv_macerator`. The same parts craft `gtceu:lv_bender` and `gtceu:lv_assembler`.

## N3 — recipe rules

On the macerator, centrifuge, electrolyzer, and the circuit machines (bender, extruder, forming press, lathe):

1. `minecraft:copper_ingot` → `gtceu:copper_dust` runs on LV (`min_voltage` 32) and finishes in half the time on MV, at four times the EU/t.
2. `gtceu:steel_ingot` → `gtceu:steel_dust` has `min_voltage` 128. It does not start in the LV macerator.
3. `gtceu:bronze_dust` in a centrifuge gives copper dust and, half the time, tin dust.
4. A lathe recipe with `"circuit": 1` runs only with `gtceu:programmed_circuit_1` in the circuit slot. An empty circuit slot still runs the older rod recipes.

## N4 — fluids

Horizon `fdc87ae` has fluid tanks (API 54) and custom fluid ids inside tanks. There is no world block or bucket for `gtceu:steam`.

1. The LP boiler consumes water and fills `gtceu:steam` (160 mB per burn tick). It no longer powers the turbine from an integer steam counter.
2. The turbine produces EU only while that steam tank has steam.
3. `gtceu:lv_combustion` burns `minecraft:lava` or `gtceu:diesel`, 1 mB per EU packet, and does not burn coal.
4. `gtceu:lv_gas_turbine` burns `gtceu:biogas` from `gtceu:biogas_cell` (1000 mB) or a neighbour tank.
5. `gtceu:lv_distillery` turns water into `gtceu:distilled_water`. `gtceu:lv_chemical_reactor` turns water into `gtceu:creosote`.

## N5 — coke oven

1. A lone `gtceu:multi_coke_oven` does not tick.
2. A face-centred controller, one-block air interior, and the rest of the 3×3×3 shell in `gtceu:coke_oven_bricks` turns coal into `gtceu:coke` and adds creosote to the controller tank.
3. Other `multi_*` controllers stay the old single-block processor.

## N6 — electric blast furnace

After N1 and N5. Controller `gtceu:multi_electric_blast_furnace` on a face of a 3×3×3 shell. The other cells are `gtceu:ebf_casing`, `gtceu:cupronickel_coil_block` (heat 1800) or `gtceu:kanthal_coil_block` (heat 2700), plus one `input_hatch`, one `output_hatch`, and one `energy_hatch`.

1. An incomplete shell does not tick.
2. Iron in the input hatch and coke beside it, with EU in the energy hatch, become `gtceu:hot_steel_ingot` in the output hatch. The recipe heat is 1000, which the LV electric furnace does not run.
3. A corner controller does not count as a formed shell.

## N7 — vacuum freezer

Controller `gtceu:multi_vacuum_freezer` on a face of a 3×3×3 shell of `gtceu:ebf_casing` plus one `input_hatch`, one `output_hatch`, and one `energy_hatch` (no coils).

1. An incomplete shell does not tick.
2. `gtceu:hot_steel_ingot` in the input hatch with EU becomes `gtceu:steel_ingot` in the output hatch.
3. A coil block in the shell breaks formation (freezer casings only).
