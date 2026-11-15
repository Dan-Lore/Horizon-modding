# TFC Horizon

Clean-room Horizon rewrite of **TerraFirmaCraft core** ideas (1.20.1 reference).

- Plan: [`docs/tfc-plan.md`](../../docs/tfc-plan.md)
- Tracker: [`tracker/catalog.json`](tracker/catalog.json) · [`docs/tfc-tracker.md`](../../docs/tfc-tracker.md)
- Pack: `python tools/pack-tfc.py` (from repo root) or `python mods/tfc/tools/pack_tfc.py`

## Smoke (after native-build on `tfg-horizon`)

1. Join world → chat tip from TFC Horizon.
2. HUD shows season / climate / thirst.
3. `/give @s tfc:rock_andesite` and `/give @s tfc:ore_native_copper`.
4. Hold `tfc:prospector_pick` and right-click near ore → chat scan result.
5. Drink: use `tfc:ceramic_jug` or right-click water with empty jug / drink command path.
