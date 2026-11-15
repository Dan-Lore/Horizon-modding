# TFC Horizon — full core port (waves)

**Own mod:** `mods/tfc/` (not a TerraFirmaCraft jar port).  
**Inspiration:** TerraFirmaCraft 1.20.1 (TFG stack) — clean Horizon rewrite + `NOTICE`.  
**Tracker:** `mods/tfc/tracker/catalog.json` → board `docs/tfc-tracker.md`.

## Locks

- Clean-room Horizon rewrite (`.hmod` + `.hnmod`); TFC **core only** (no Firmalife / Ambient).
- **Hybrid worldgen:** thin climate + calendar early; rock/ore content slice on vanilla overworld; full TFC worldgen in late waves (`blocked` until engine hooks).
- Ship into `tfg-horizon` only after a smokeable wave; do not break AE2/Greglite pin (`fdc87ae`).

## Non-goals

- Official TFC / TFG branding or Firmalife.
- Waiting on Create pin convergence.
- Full animal genetics in early waves.

## Architecture

- Data-driven blocks/items/recipes in `data/tfc/`.
- Table-driven native systems under `mods/tfc/api/src/` (`climate`, `thirst`, `heat`, `forge`, `food`, `crops`, `collapse`, `prospect`, `worldgen`).
- Statuses: `todo` | `wip` | `done` | `blocked` | `deferred`. `done` only with a written smoke path.

## Waves

| Wave | Deliverable | Smoke |
| --- | --- | --- |
| **W0** | Scaffold, NOTICE, tracker, pack script | Pack builds; login tip |
| **W1** | Calendar + thin climate + thirst + HUD | Thirst drains; drink; season/climate on HUD |
| **W2** | Rock/ore slice + prospector lite | `/give` rocks/ores; prospector message |
| **W3** | Knapping + stone tools + firepit | Knap tool; light firepit |
| **W4** | Clay / pottery / pit kiln | Vessel → ceramic |
| **W5** | Heating + charcoal forge + copper cast | Heat copper; cast head |
| **W6** | Bloomery + anvil subset | Bloom → work tool |
| **W7** | Food size/weight, decay, 5 nutrients | Nutrient HUD; spoilage |
| **W8** | Crops + season/climate growth gate | Crop grows only in range |
| **W9** | Quern + barrel lite | Grind; barrel recipe |
| **W10** | Log piles, lumber, support/collapse lite | Unsupported rock collapses |
| **W11** | Panning / sluice + more ores | Pan → nugget |
| **W12** | Full worldgen v1 | `blocked` until hooks; hybrid remains |
| **W13** | Animals subset | `deferred` if entity API insufficient |
| **W14** | Chisel, powderkeg, blast furnace leftovers | Checklist gaps filed |
| **W15** | JEI/Jade polish + Greglite wire-up notes | Pack smoke with Batch A |

**Rules:** after W3 green, parallelize content tables; do not start W6 until W5 heat smoke; do not start W12 until hooks clear or a documented subset ships.

## Pack

| Layer | Where |
| --- | --- |
| Sources | `mods/tfc/` |
| Pack out | `tools/pack-tfc.py` → `tfc.hmod` |
| Play | optional on `tfg-horizon` after W3+ |

## Version

Mod version tracks wave delivery: **0.1.0** = W0–W2 scaffold + hybrid survival start content/native stubs through W15 tables.
