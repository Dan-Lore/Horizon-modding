# TFC Horizon

Clean-room Horizon rewrite of **TerraFirmaCraft core** (1.20.1 design reference).
Not a jar port. Plan: [`docs/tfc-plan.md`](../../docs/tfc-plan.md).

## Waves

| Wave | Status source |
| --- | --- |
| W0–W15 | [`tracker/catalog.json`](tracker/catalog.json) → [`docs/tfc-tracker.md`](../../docs/tfc-tracker.md) |

## Pack

```bash
python3 mods/tfc/tools/gen_content.py
python3 tools/pack-tfc.py   # or pwsh tools/pack-tfc.ps1 on Windows
```

Enable on `tfg-horizon` only after a smokeable wave; do not block AE2/Greglite pins.

## Smoke (W1–W2)

1. Join world → chat tip + action bar climate/thirst.
2. `/give @s tfc:vessel` → use on water to drink.
3. `/give @s tfc:prospector_pick` → right-click near `tfc:ore_native_copper`.
4. Place rock/ore blocks; JEI/Jade see `tfc:*`.
