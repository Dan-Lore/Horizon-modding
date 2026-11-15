# TFC Horizon

Clean-room Horizon rewrite of a **TerraFirmaCraft core** slice (1.20.1 design reference).
Not a jar port. Plan: [`docs/tfc-plan.md`](../../docs/tfc-plan.md).
Tracker: [`tracker/catalog.json`](tracker/catalog.json).

## Build

```bash
python3 mods/tfc/tools/gen_content.py
python3 mods/tfc/tools/check.py
python3 tools/pack-tfc.py
```

`tools/pack-tfc.py` writes `mods/tfc/dist/tfc.hmod` and does not copy it onto `tfg-horizon`.
The Cargo pin is Horizon `fdc87ae` (hooks 411), the same revision as AE2 15.4.18.
Stay off that instance's native-build until you mean to smoke TFC there.

## Play slice

1. Login line names TFC Horizon 0.1.0.
2. Action bar shows season, temperature, thirst, and five nutrients.
3. `/give` a rock, an ore, and `tfc:prospector_pick`.
4. Firepit, pit kiln, charcoal forge, bloomery, anvil, quern, barrel, sluice, blast furnace: fuel slot first when the block burns, then inputs, then the output.
5. Animals are not spawned. Chunks are not rewritten. Unsupported rock is a chat warning.

Smoke paths for every wave are in the catalog. `done` is only used when that path is written down.
