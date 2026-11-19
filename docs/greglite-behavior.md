# Greglite behaviour checklist (0.5.0)

File coverage in `mods/greglite/tracker/coverage.json` only counts blocks and recipe JSON. This list is the playable behaviour.

A row is **done** only after Play on **`tfg-dev`** (or a newer native built for that pin): `greglite` in `horizon-mod-ids.json`, `/give` works, scenario succeeds. Do not native-build pinned `tfg-horizon` just to tick these boxes.

Code/datapack for these rows shipped in Greglite 0.5.0. Unit tests live in `api/src/eu_rules.rs` (no game required).

## N0 — base loop

`/give` is allowed for the four blocks and the fuel. Copper is vanilla.

1. Coal in `greglite:steam_solid_boiler_lp` with water (bucket in the fuel slot, or a `minecraft:water` block beside it).
2. `greglite:lv_steam_turbine` beside the boiler. The boiler's steam tank drops and the turbine's EU rises.
3. `greglite:tin_cable_1x` from the turbine to `greglite:lv_macerator`.
4. `minecraft:copper_ingot` in the macerator becomes `greglite:copper_dust`.

## N1 — EU net

1. The same tin `1x` cable runs the LV macerator.
2. That cable does not run an MV machine (`greglite:mv_macerator` stays idle).
3. `greglite:lv_transformer` between the LV side and one MV machine runs that machine at 1 A of 128 V.
4. `greglite:lv_diode` passes EU only along its `facing`.
5. `greglite:lv_battery_buffer_4x` charges `greglite:lv_battery` and gives that charge back. An `mv_battery` in the LV buffer does not.

## N2 — LV craft chain

Start with vanilla copper, iron, coal, slime balls, redstone, and `greglite:tin_ingot`. No `/give` of other Greglite items.

1. Three iron ingots craft `greglite:iron_plate`. Slime and coal craft `greglite:rubber`.
2. Eight iron plates craft `greglite:lv_machine_hull`. Plates, copper, and the hull craft `greglite:lv_wiremill`.
3. The wiremill turns copper and tin ingots into `greglite:copper_wire` and `greglite:tin_wire`. Wire plus rubber crafts `greglite:tin_cable_1x`.
4. Cable, wire, and iron craft `greglite:lv_motor`, then `greglite:lv_piston`, then `greglite:lv_robot_arm`. Wire, redstone, and a plate craft `greglite:programmed_circuit_1`.
5. Hull, motor, piston, and a plate craft a second `greglite:lv_macerator`. The same parts craft `greglite:lv_bender` and `greglite:lv_assembler`.

## N3 — recipe rules

On the macerator, centrifuge, electrolyzer, and the circuit machines (bender, extruder, forming press, lathe):

1. `minecraft:copper_ingot` → `greglite:copper_dust` runs on LV (`min_voltage` 32) and finishes in half the time on MV, at four times the EU/t.
2. `greglite:steel_ingot` → `greglite:steel_dust` has `min_voltage` 128. It does not start in the LV macerator.
3. `greglite:bronze_dust` in a centrifuge gives copper dust and, half the time, tin dust.
4. A lathe recipe with `"circuit": 1` runs only with `greglite:programmed_circuit_1` in the circuit slot. An empty circuit slot still runs the older rod recipes.

## N4 — fluids

Horizon `fdc87ae` has fluid tanks (API 54) and custom fluid ids inside tanks. There is no world block or bucket for `greglite:steam`.

1. The LP boiler consumes water and fills `greglite:steam` (160 mB per burn tick). It no longer powers the turbine from an integer steam counter.
2. The turbine produces EU only while that steam tank has steam.
3. `greglite:lv_combustion` burns `minecraft:lava` or `greglite:diesel`, 1 mB per EU packet, and does not burn coal.
4. `greglite:lv_gas_turbine` burns `greglite:biogas` from `greglite:biogas_cell` (1000 mB) or a neighbour tank.
5. `greglite:lv_distillery` turns water into `greglite:distilled_water`. `greglite:lv_chemical_reactor` turns water into `greglite:creosote`.

## N5 — coke oven

1. A lone `greglite:multi_coke_oven` does not tick.
2. A face-centred controller, one-block air interior, and the rest of the 3×3×3 shell in `greglite:coke_oven_bricks` turns coal into `greglite:coke` and adds creosote to the controller tank.
3. Other `multi_*` controllers stay the old single-block processor.

## N6 — electric blast furnace

After N1 and N5. Controller `greglite:multi_electric_blast_furnace` on a face of a 3×3×3 shell. The other cells are `greglite:ebf_casing`, `greglite:cupronickel_coil_block` (heat 1800) or `greglite:kanthal_coil_block` (heat 2700), plus one `input_hatch`, one `output_hatch`, and one `energy_hatch`.

1. An incomplete shell does not tick.
2. Iron in the input hatch and coke beside it, with EU in the energy hatch, become `greglite:steel_ingot` in the output hatch. The recipe heat is 1000, which the LV electric furnace does not run.
3. A corner controller does not count as a formed shell.
