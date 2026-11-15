# TFC Horizon — full core port (waves)

**Own mod:** `mods/tfc/` (not a TFC/TFG jar port).  
**Inspiration:** TerraFirmaCraft 1.20.1 (TFG reference) — clean Horizon rewrite + `NOTICE`.  
**Tracker:** `mods/tfc/tracker/catalog.json` → summary `docs/tfc-tracker.md`.

## Locks (agreed 2026-11-15)

- Clean-room Horizon rewrite (`.hmod` + `.hnmod`).
- **TFC core only** — no Firmalife / Ambient / other addons.
- **Hybrid worldgen:** thin climate + calendar/season early; small rock/ore slice on vanilla overworld; full TFC worldgen late, gated on Horizon hooks.
- One mod folder `mods/tfc/`. Ship into `tfg-horizon` only after a smokeable wave — do not block AE2/Greglite pin.
- Create remains parked until pin converges with AE2.

## Non-goals

- Official TFC / TFG branding or parity claims.
- Firmalife or TFG quest/balance.
- Waiting for Create before starting waves.
- Full animal genetics in early waves.

## Architecture

- Data-driven content (blocks/items/recipes in content pack).
- Native Hooks for player stats, machines, prospecting, HUD readout.
- Table-driven systems under `mods/tfc/tables/` (+ Rust tables).
- Tracker statuses: `todo` / `wip` / `done` / `blocked` / `deferred`.

## Engine risk register

| Need | Used by | Status |
| --- | --- | --- |
| Persistent player/chunk data + HUD | thirst, nutrition, climate | W1 uses in-memory + action_bar; persistent helpers when available |
| Item heat / stack data | forge, food decay | machine progress in BE data; food table ready |
| Custom menus / BE tick | forge, barrel, quern | same patterns as Greglite |
| Worldgen / biome / ore APIs | W12+ | **blocked** — hybrid bridge remains |
| Entities / AI | animals W13 | **deferred** |

## Waves

| Wave | Deliverable | Exit smoke |
| --- | --- | --- |
| **W0** | Scaffold `mods/tfc/`, NOTICE, tracker, pack script | content packs; native stub builds |
| **W1** | Calendar + thin climate + thirst + HUD | thirst drains; drink recovers; season visible |
| **W2** | Rock/ore slice + prospector lite | propick finds placed ore; JEI sees items |
| **W3** | Knapping + stone tools + firepit | knap/craft heads; light firepit |
| **W4** | Clay/pottery/pit kiln | vessel via pit kiln |
| **W5** | Heating + charcoal forge + copper molds | melt copper; cast tool head |
| **W6** | Bloomery + anvil bronze/iron loop | bloom → wrought on anvil |
| **W7** | Food weight/size, decay table, 5 nutrients | eat foods; nutrient HUD |
| **W8** | Crops + climate gate | seeds blocked out of season |
| **W9** | Quern + barrel | grind flux; barrel recipe |
| **W10** | Log piles, lumber, support/collapse lite | unsupported warning / beams |
| **W11** | Panning/sluice + ore expand | sluice pan → nugget |
| **W12** | Full worldgen v1 | **blocked** until ore/climate map hooks |
| **W13** | Animals subset | **deferred** (entity API) |
| **W14** | Chisel, powderkeg, blast furnace, glass, parity checklist | content + recipes present; gaps filed |
| **W15** | JEI/Jade/pack wire-up with Greglite | documented smoke on `tfg-horizon` |

**Multitask:** after W3 green, parallelize content tables; no W6 before W5 heat smoke; no W12 until hooks cleared.

## Pack placement

| Layer | Where |
| --- | --- |
| WIP | `mods/tfc/` |
| Tracker | `mods/tfc/tracker/catalog.json` |
| Docs | `docs/tfc-plan.md`, `docs/tfc-tracker.md` |
| Pack | optional on `tfg-horizon` after smoke |

## Done means

TFC **core survival identity** playable: climate/season, geology (slice → full WG when unblocked), early–mid metal loop, food/nutrition, crops, barrels/quern, collapse/supports, living tracker for `deferred`/`blocked` — not a silent 100% claim.
