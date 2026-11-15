# TFC Horizon

Clean-room Horizon rewrite inspired by **TerraFirmaCraft** 1.20.1 (TFG reference).  
Not a jar port. See `NOTICE` and `docs/tfc-plan.md`.

## Layout

| Path | Role |
| --- | --- |
| `data/tfc/` | Blocks, items, recipes, data tables |
| `api/` | Native Hooks (climate, thirst, machines, prospecting, …) |
| `tracker/catalog.json` | Wave board |
| `tools/gen_content.py` | Regenerates content + tables + placeholder textures |

## Pack

```powershell
pwsh tools/pack-tfc.ps1
# or
python3 tools/pack-tfc.py
```

Install into `tfg-horizon` only after a smokeable wave. Prefer co-build on Nightly `fdc87ae` with Batch A + Greglite.

## Smoke (W1–W2)

1. Join world → login tip.
2. Action bar shows season / climate / thirst periodically.
3. `/give @s tfc:ceramic_jug` then use on water (or drink) to restore thirst.
4. `/give @s tfc:rock_andesite` / `tfc:ore_native_copper` / `tfc:prospectors_pick`.
5. Use prospector's pick on nearby ore blocks.

## Waves

See `docs/tfc-plan.md` and `docs/tfc-tracker.md`.
