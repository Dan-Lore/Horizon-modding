# TFC Horizon — full core port (waves)

**Own mod:** `mods/tfc/` (clean-room Horizon rewrite, not a TerraFirmaCraft jar).  
**Inspiration:** TerraFirmaCraft 1.20.1 as used by TerraFirmaGreg-Modern. Attribution: `mods/tfc/NOTICE`.  
**Tracker:** `mods/tfc/tracker/catalog.json` → `docs/tfc-tracker.md`.  
**Version:** 0.2.0 adds W16–W22 on the same hooks 411 pin. 0.1.x covered W0–W15.

## Locks

- TFC **core only**. Firmalife and other addons stay out.
- **Hybrid worldgen (choice C):** calendar, temperature, and rainfall early; a hand-placed rock and ore slice; full layers, climate maps, biomes, and veins stay `blocked`.
- Pin `fdc87aecdbd116bf1e08adcd062fcbaea8c2e2ca` (hooks 411), the same native as `tfg-horizon` / AE2 15.4.18.
- `pack/draft-mods.toml` lists TFC with `on = []`. Do not native-build it into the AE2/Greglite pin until a wave is smoked on purpose.

## Statuses

`todo` | `wip` | `done` | `blocked` | `deferred`.  
`done` only with a written smoke path in the catalog.

## Waves

| Wave | Deliverable | 0.1.0 |
| --- | --- | --- |
| **W0** | Scaffold, NOTICE, tracker, `tools/pack-tfc.py` | done |
| **W1** | 12×8-day calendar, thin climate, thirst, action-bar HUD | done |
| **W2** | Eight rocks × raw/cobble/smooth/gravel, eight ores, prospector | done |
| **W3** | Knapping as crafting, stone tools, firepit | done |
| **W4** | Clay vessels, pit kiln, charcoal pit | done |
| **W5** | Charcoal forge, copper/bronze/tin/bismuth/zinc/silver/gold melt, cast heads | done |
| **W6** | Bloomery, anvil sheets and wrought heads, weld as two-ingot crafting | done |
| **W7** | Size, weight, decay days, five nutrients | nutrition done; per-stack rot blocked |
| **W8** | Wheat, barley, cabbage; growth only inside season and temperature | done |
| **W9** | Quern and barrel | done |
| **W10** | Lumber, log pile, support beam, collapse warning | warning done; block replace blocked (API 446) |
| **W11** | Pan and sluice | done |
| **W12** | Blast furnace steel, brass alloy | done |
| **W13** | Animals | deferred (no spawn) |
| **W14** | Full worldgen | blocked; prospect prints a preview rock |
| **W15** | Glass batch, chisel mark, powderkeg content, JEI recipe types | done |

W12 here is the blast furnace. Worldgen is W14. That is the wave order this repo implements.

## 0.2.0

Same pin. Heat stays on the block entity. Inventory rot, collapse replacement, animals, and worldgen stay locked.

| Wave | Deliverable | 0.2.0 |
| --- | --- | --- |
| **W16** | Forge heat from `tables/heat.json`, cap 1400. Copper melts at 1080, tin at 230, hematite does not become an ingot | done |
| **W17** | Crucible ratios for bronze and brass. Shapeless alloys removed | done |
| **W18** | Hammer steps on the anvil. Weld is two ingots in the forge | done |
| **W19** | 5×5 knapping block. Stone tools are head plus stick | done |
| **W20** | Bread in the small vessel or an idle barrel becomes `tfc:rot`. Inventory stacks do not | done |
| **W21** | Rain gate. Oat, rye, onion, squash | done |
| **W22** | Version 0.2.0, checker, tracker | done |

## What hooks 411 cannot do

- `default_state` is API 446, so native code does not place or replace blocks. Collapse, chisel, and worldgen report in chat.
- Item components are not written, so rot is a tooltip number plus nutrient drain, not a stack timer.
- Animals are a table only.

## Pack

```bash
python3 mods/tfc/tools/gen_content.py
python3 mods/tfc/tools/check.py
python3 tools/pack-tfc.py
```

Output: `mods/tfc/dist/tfc.hmod` (gitignored). Install it only on a native that is not the live AE2 pin, then `/give` before trusting the login line. See `docs/dev-tips-native-content.md`.

## Content shape

`mods/tfc/tools/gen_content.py` writes blocks, items, recipes, loot, menus, lang, placeholder PNGs, the JSON tables under `mods/tfc/tables/`, and `api/src/specs.inc.rs`. Native code reads those tables. Machine slots are fuel (when the bench burns), then inputs, then one output.
