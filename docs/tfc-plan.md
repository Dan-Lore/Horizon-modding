# TFC Horizon — full core port (waves)

**Own mod:** `mods/tfc/` (not a TerraFirmaCraft jar port).  
**Inspiration:** TerraFirmaCraft 1.20.1 (TFG stack reference) — clean Horizon rewrite + `NOTICE`.  
**Tracker:** `mods/tfc/tracker/catalog.json` → board `docs/tfc-tracker.md`.

## Locks

- Clean-room `.hmod` + `.hnmod`; TFC **core only** (no Firmalife / Ambient).
- **Hybrid worldgen:** thin climate + calendar early; rock/ore content slice on vanilla overworld; full TFC worldgen in W12+ when hooks allow.
- One mod folder; enable on `tfg-horizon` after smokeable wave — do not break AE2/Greglite pin.
- Tracker statuses: `todo` / `wip` / `done` / `blocked` / `deferred`.

## Architecture

Data-driven content (blocks/items/recipes/tables) + native Hooks for player stats, machines, prospecting, collapse. Table-driven systems — no per-item `match` arms in Rust.

## Waves

| Wave | Deliverable | Exit smoke |
| --- | --- | --- |
| **W0** | Scaffold, NOTICE, tracker, pack script | launches / packs |
| **W1** | Calendar + thin climate + thirst + action-bar HUD | thirst drains; drink; season visible |
| **W2** | Rock/ore slice + prospector lite | `/give` rocks/ores; scan finds ore |
| **W3** | Knapping + stone tools + firepit | knap tool; light firepit |
| **W4** | Clay / pottery / pit kiln | vessel → ceramic |
| **W5** | Heating + charcoal forge + copper cast | melt/cast copper head |
| **W6** | Bloomery + anvil subset | bloom → wrought; work tool |
| **W7** | Food weight/size, decay, 5 nutrients | nutrients + spoil |
| **W8** | Crops + climate/season growth gate | one crop grows in range |
| **W9** | Quern + barrel lite | grind; barrel recipe |
| **W10** | Log piles, lumber, support/collapse lite | unsupported rock collapses |
| **W11** | Panning / sluice + more ores | pan → nugget |
| **W12** | Full worldgen v1 (engine-gated) | or stay `blocked` |
| **W13** | Animals subset or `deferred` | explicit status |
| **W14** | Chisel, powderkeg, blast furnace, parity pass | gaps filed |
| **W15** | JEI/Jade polish + Greglite metal bridge | pack smoke |

**Multitask:** after W3 green, parallelize content tables; W6 after W5 heat smoke; W12 only when unblocked.

## Pack

| Layer | Where |
| --- | --- |
| Sources | `mods/tfc/` |
| Pack script | `tools/pack-tfc.ps1` / `tools/pack-tfc.py` |
| Play | `tfg-horizon` after W3+ |

## Done means

TFC core survival identity on Horizon with a living tracker — not a silent 100% claim.
