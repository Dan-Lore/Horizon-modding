# Ad Astra Horizon — port plan (0.1.0 vertical slice)

**Own mod:** `mods/adastra/` (clean-room Horizon rewrite, not an Ad Astra / TFG jar).  
**Inspiration:** Ad Astra (Terrarium) as used beside TerraFirmaGreg-Modern. Attribution: `mods/adastra/NOTICE`.  
**Tracker:** `mods/adastra/tracker/catalog.json` → `docs/adastra-tracker.md`.  
**Version:** 0.1.0 covers W0–W9 overworld systems that hooks 411 can run.

## Locks

- **Overworld slice only.** No custom dimensions, planet registry, orbital mechanics, or space stations.
- **Energy:** in-mod FE buffer (`Fe` NBT). No Greglite EU dependency. Pack bridging is out of scope for this mod agent.
- Pin `fdc87aecdbd116bf1e08adcd062fcbaea8c2e2ca` (hooks 411), same native as AE2 15.4.18 / Greglite when a pack agent integrates.
- Pack agent owns `pack/draft-mods.toml` / `tfg-horizon`. Recommend `on = []` until `/give` smoke. This workshop does not native-build the pack.

## Statuses

`todo` | `wip` | `done` | `blocked` | `deferred`.  
`done` only with a written smoke path in the catalog.

## Waves

| Wave | Deliverable | 0.1.0 |
| --- | --- | --- |
| **W0** | Scaffold, NOTICE, tracker, `tools/pack-adastra.py` | done |
| **W1** | Steel/desh/ostrum/calorite, moon/mars stone, cheese, flag | done |
| **W2** | FE buffer, coal generator, thin solar panel | done |
| **W3** | Compressor + ≥2 plate recipes with FE cost | done |
| **W4** | Suit/tanks, oxygen loader, O₂ HUD, vacuum marker damage | done |
| **W5** | Oil → fuel refinery | done |
| **W6** | NASA workbench + Tier-1 rocket + launch stub | done |
| **W7** | Oxygen distributor safe zone | done |
| **W8** | Cryo freezer thin slice (≥2 recipes) | done |
| **W9** | Gravity stub on moon/mars blocks, pack-agent smoke notes | done |

## What hooks 411 cannot do

- Custom dimensions / change-dimension for rockets — launch is a chat countdown stub.
- True armor slots may be unavailable; suit pieces are **donned via use** (player-state flags).
- Vacuum “damage” is chat + O₂ drain (no guaranteed living-entity damage API on this pin).
- Gravity is HUD/slowness messaging on moon/mars foot blocks, not physics rewrite.

## Pack (workshop)

```bash
python3 mods/adastra/tools/gen_content.py
python3 mods/adastra/tools/check.py
python3 tools/pack-adastra.py
```

Output: `mods/adastra/dist/adastra.hmod` (gitignored). See `docs/dev-tips-native-content.md` for `/give` smoke.

## Smoke contract (for pack agent)

1. Install `.hmod` with `mod.adastra:true` on a native with hooks ≥ 411 / pin `fdc87ae` preferred.
2. Restore `native-content/adastra` trio if needed; wipe `.horizon-cache/mod-content`.
3. Confirm `horizon-mod-ids.json` lists `adastra`.
4. `/give adastra:desh_ingot`; coal generator beside compressor → plate; suit+loader O₂; vacuum marker without suit; craft rocket and run launch stub.

## Content shape

`mods/adastra/tools/gen_content.py` writes blocks, items, recipes, loot, menus, lang, placeholder PNGs, `tables/`, and `api/src/specs.inc.rs`. Native code owns FE transfer, oxygen, vacuum, and the rocket stub.
