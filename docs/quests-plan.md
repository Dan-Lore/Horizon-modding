# Horizon Quests / Teams — wave plan (depth B + Teams)

**Own mods:** `mods/teams/` (id `teams`) + `mods/quests/` (id `quests`).  
**Inspiration:** FTB Teams / FTB Quests UX and data shape. **Not a jar port.** No SNBT import; no FTB assets/code (typically ARR).  
**Tracker:** `mods/teams/tracker/catalog.json`, `mods/quests/tracker/catalog.json` → `docs/quests-tracker.md`.  
**Pin:** Horizon `fdc87ae` / hooks 411 (same as AE2 on `tfg-horizon`). `on = []` until intentional smoke.

## Locks

- Naming: “Horizon Teams / Horizon Quests” — not “FTB …”.
- Progress is **per-team**; reward claim is **per claiming player** (team shares unlock).
- Definitions live in JSON under `mods/quests/tables/` (baked into the native crate) plus optional world overrides in `world_dir()/horizon-quests/`.
- Teams persist under `world_dir()/horizon-teams/`.
- Chapter graph / pan-zoom UI stays blocked until richer client UI hooks; book UX is command + quest book item + quest board block.

## Waves

See `docs/quests-tracker.md` for smoke status.

## Pack

```bash
python3 tools/pack-teams.py
python3 mods/quests/tools/gen_content.py
python3 tools/pack-quests.py
```

Do not native-build onto the live AE2 pin until W6+ is smoked on purpose.
