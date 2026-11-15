# Greglite

GregTech-inspired native mod for Horizon. Version **0.5.0**. Clean rewrite; textures from GregTech-Modern (LGPL-3.0), see [NOTICE](NOTICE).

## Play

One instance: **`tfg-horizon`**, native `native-fdc87ae-428278da87c5` (Nightly `fdc87ae`, hooks 411).

```powershell
powershell -File tools/pack-greglite.ps1
```

That writes `greglite.hmod` into the `tfg-horizon` native-mods folder. Then native-build that instance only. `create-dev` and `create-nightly-test` are not pack targets.

Login chat and `tracker/coverage.json` do not prove a wave. The behaviour list is [`docs/greglite-behavior.md`](../../docs/greglite-behavior.md). This environment did not run Horizon, so that list is still unchecked in game.

## What 0.5.0 adds

- Cable voltage and loss come from the material. `1x` is 1 A, `4x` is 4 A. Tin stays 32 V.
- A machine or battery buffer takes a packet only at its own voltage. A higher packet is refused. There is no explosion.
- Diodes pass one amp along `facing`. Transformers trade 4 A of the low tier for 1 A of the next tier, both ways.
- Battery buffers charge and discharge the battery item of their tier. The old extra capacity on `lv_battery` is gone.
- LV craft chain from copper, iron, coal, slime, and a tin ingot through dust, plate, wire, cable, motor, piston, robot arm, hull, and a second `lv_macerator`.
- Recipes can list several outputs, a chance, a programmed circuit, `min_voltage`, and a fluid in or out. One tier above the minimum is twice as fast and four times the EU/t.
- Boilers turn water into `greglite:steam`. Turbines burn that steam. Combustion burns lava or `greglite:diesel`. The gas turbine burns `greglite:biogas`. The distillery and chemical reactor each move one fluid in and one fluid out.
- `multi_coke_oven` does nothing until its 3×3×3 brick shell is complete, then coal becomes `greglite:coke` and creosote.
- `multi_electric_blast_furnace` needs casings, one coil, and input, output, and energy hatches. Iron plus coke becomes steel when coil heat reaches the recipe. An incomplete shell does nothing.

## Build pin

`tools/pack-greglite.ps1` records Horizon `fdc87ae` and hooks **381** (level reads plus fluid tanks). The launcher still rewrites the crate revision to the game it compiles.
