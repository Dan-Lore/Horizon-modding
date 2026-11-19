# TFG content coverage (player-facing)

**This is the scoreboard to quote when someone asks “how complete is the port?”**  
Do **not** quote the old catalog “100% Horizon capability / #4 debt” number — that only meant “we stopped artificially stubbing what the pin already allows,” **not** GregTech/TFG Absolute parity.

**Reference:** TerraFirmaGreg-Modern (Forge 1.20.1) at  
`C:\Users\smoln\curseforge\minecraft\Instances\TerraFirmaGreg-Modern`  
**Ours:** Horizon rewrite under `mods/<id>/` (technical ids stay `greglite`, `tfc`, … until a dedicated namespace migration).

## How to score

Three axes, each 0–100%, then a blended pack score (weights below).

| Axis | What counts | “100%” means |
| --- | --- | --- |
| **Resources** | Items + blocks (ids the player can `/give` / see in JEI `@modid`) | Roughly the upstream set for that mod’s TFG role (not every GTM material ever) |
| **Recipes** | Datapack / machine recipes that actually run in our processors | Upstream recipe surface for the same machines we ship |
| **Mechanics** | Behaviours that change the world (EU net, multiblocks, heat, oxygen, quests…) | Upstream loop for that system on this Horizon pin (#1/#2/#3 still cap the ceiling) |

**Honesty rules**

- A machine **block + empty GUI** without recipes/behaviour ≠ mechanics done.
- JSON recipe files that the processor never reads ≠ recipes done.
- Login tips / creative tabs ≠ coverage.
- `#1` API gaps (dims, animals, explode…) stay **blocked**, not “missing because lazy.”
- Create/Greate on this AE2 pin stay **#2 parked**.

Refresh counts:

```powershell
python tools/score-tfg-content.py
```

## Snapshot — 2026-11-20 (`native-fdc87ae-8a627f102c73`)

### Pack blend (weights)

| Axis | Weight | Score | Notes |
| --- | ---: | ---: | --- |
| Resources | 35% | **~8%** | Thin material/machine sets vs TFG |
| Recipes | 35% | **~5%** | ~1.2k greglite recipes vs GTM’s generated ocean + kubejs |
| Mechanics | 30% | **~18%** | Real EU/TFC-heat/O₂/quests loops; most GT depth still missing |
| **Pack (weighted)** | 100% | **~10%** | Playable draft, **not** a TFG replacement |

### Per workshop mod

| Display name | Id | Resources (ours) | Recipes (ours) | Mechanics (est.) | vs TFG role |
| --- | --- | ---: | ---: | ---: | --- |
| **GregTech** | `greglite` | ~1480 items / ~497 blocks | ~1247 / 48 types | ~20% | GTM jar is code-gen heavy (~2k classes, ~3.8k png in `gtceu`); we are a **slice** |
| **TerraFirmaCraft** | `tfc` | ~195 / ~63 | ~119 | ~25% | Heat/anvil/knapping/rot yes; animals, veins, climate maps, collapse **#1** |
| **Firmalife** | `firmalife` | ~13 / ~7 | ~12 | ~30% | Food machines tick; greenhouse weak vs upstream |
| **Ad Astra** | `adastra` | ~38 / ~14 | ~24 | ~15% | Overworld FE/O₂; planets/rocket travel **#1** |
| **FTB Quests** | `quests` | book + tables | quest JSON | ~40% | Kill/adv/UI wired; not full FTB quest graph editor |
| **FTB Teams** | `teams` | roster item | — | ~50% | `/hteam` parties; not full FTB Teams |
| **Greate** | `greate` | shafts (content) | — | **0% live** | **#2** — needs Create pin ≠ AE2 |
| AE2 / JEI / Jade / … | registry | upstream | upstream | as shipped | Not our rewrite |

### GregTech axis detail (why JEI feels empty)

| Area | Ours | Gap |
| --- | --- | --- |
| Namespace players expect | often `gregtech:` / `gtceu:` | We still register **`greglite:`** → `gregtech:hv_chemical_bath` shows **not available** |
| Chemical bath | block + few `greglite:chemical_bath` recipes | Not GTM bath chemistry |
| Centrifuge GUI | multi-output slots | Sparse recipe set; empty GUI ≠ “no machine,” but ≠ full GT |
| Materials | ~120 dust/ingot/plate-ish | GTM material dictionary is far larger |
| Multiblocks | coke / EBF / freezer shells | Most `multi_*` still thin |

## Naming

| Shown in game / docs | Technical folder + id | Upstream |
| --- | --- | --- |
| GregTech | `mods/greglite` / `greglite` | GregTech Modern (`gtceu`) |
| TerraFirmaCraft | `mods/tfc` / `tfc` | TFC |
| Firmalife | `mods/firmalife` | Firmalife |
| Ad Astra | `mods/adastra` | Ad Astra |
| FTB Quests | `mods/quests` | FTB Quests |
| FTB Teams | `mods/teams` | FTB Teams |
| Greate | `mods/greate-horizon` / `greate` | Greate |

**Id migration** (`greglite` → `gtceu`) is a separate breaking wave (all recipes, tags, quests, saves). Display names are GregTech **now**; ids stay until that wave.

## Related

- Behaviour checklists: `docs/greglite-behavior.md`, mod trackers  
- Engine headroom / #4 policy (internal): `docs/horizon-capability-policy.md` — **not** the pack completeness %.
