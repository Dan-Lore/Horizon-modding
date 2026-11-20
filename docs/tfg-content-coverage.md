# TFG content coverage (Absolute scoreboard)

**This is the scoreboard to quote when someone asks “how complete is the port?”**  
Do **not** quote the old catalog “100% Horizon capability / #4 debt” number — that only meant “we stopped artificially stubbing what the pin already allows,” **not** Absolute TFG/GTM parity.

**Reference:** TerraFirmaGreg-Modern (Forge 1.20.1) at  
`C:\Users\smoln\curseforge\minecraft\Instances\TerraFirmaGreg-Modern`  
**Ours:** Horizon rewrite under `mods/<id>/` — GregTech technical id is **`gtceu`** (GTM’s namespace).

**Ceiling:** Absolute upstream (GTM + TFC + Firmalife + Ad Astra + Create/Greate when pin allows).  
Create/Greate stay **#2 parked** on Nightly `fdc87ae` / AE2. Dims / animals / explode stay **#1** forever on this pin and are **out of the achievable numerator**.

## How to score

Three axes, each 0–100%, then a blended pack score.

| Axis | What counts | Absolute “100%” |
| --- | --- | --- |
| **Resources** | Items + blocks (`/give`, JEI `@modid`) | Upstream set for that mod’s TFG role (jar + runtime codegen where jar is empty) |
| **Recipes** | Datapack / machine recipes the processor actually runs | Upstream recipe surface for machines we ship |
| **Mechanics** | Behaviours (EU net, multis, heat, oxygen, quests…) | Upstream loop on this Horizon pin |

**Honesty rules**

- Machine **block + empty GUI** without recipes ≠ done.
- JSON the processor never reads ≠ recipes done.
- Login tips ≠ coverage.
- `#1` / `#2` gaps stay **blocked**, not “missing because lazy.”

Refresh:

```powershell
python tools/score-tfg-content.py
```

Writes `docs/tfg-content-score.json` with `pack_blend_pct` + `milestone` (`M0` / `M25` / `M50` / `M75` / `M100`).

### Milestone ladder

| Milestone | Pack blend | Focus |
| --- | ---: | --- |
| **M0** | &lt;22% | ids live (`gtceu:`), thin Absolute surface |
| **M25** | ≥22% | materials forms + dense bath/centrifuge/… recipes |
| **M50** | ≥45% | chem/fluid/ore chains, more multis, Firmalife/Ad Astra breadth |
| **M75** | ≥70% | IV+ materials/circuits, TFC depth within hooks, Ad Astra overworld complete |
| **M100** | ≥95% | remaining Absolute achievable; Create/Greate only when #2 clears |

## Absolute denominators (evidence)

| Mod | Items | Blocks | Recipes | Source |
| --- | ---: | ---: | ---: | --- |
| GregTech (`gtceu`) | 9000 | 2000 | 30000 | GTM jar `gtceu-1.20.1-7.5.3` static models/item **2738** / blockstates **1568** + runtime material dict (~617 colors × ~10 forms); recipes are code-gen (0 JSON in jar) |
| TerraFirmaCraft | 2500 | 1500 | 4000 | Published-scale estimate (TFC jar not present in local TFG mods folder) |
| Firmalife | 637 | 436 | 595 | `Firmalife-1.20.1-2.1.28.jar` |
| Ad Astra | 413 | 333 | 534 | `ad_astra-forge-1.20.1-1.15.21.jar` |
| FTB Quests / Teams | 20 / 10 | 5 / 1 | 1 / 1 | Small party/quest surface |

Blocked forever on this pin (listed, not in “done”): **Create/Greate (#2)**, **dims/animals/explode (#1)**.

## Snapshot — refresh via `score-tfg-content.py`

See latest numbers in [`tfg-content-score.json`](tfg-content-score.json). Refresh via `score-tfg-content.py` (**M75 / ≥70%**).

**AE2 Interface glue (this pin):** workshop `ModContainer` face contract (Up=in, Down=out, sides=both) on gtceu/tfc/adastra/firmalife so stock AE2 Interface/buses/PP feed machines — no AE2 fork. Quests `ae2_interface` / `ae2_gt_hatch`. Create/Greate still **#2**.

**Launcher note:** portable `launcher/windows-x64` (0.2.0) expects flat `[native]` crates; workshop mixins `.hmod` rebuilds currently use `launcher/_old-launcher/horizon-launcher.exe` (Nov 10 zip) until the tree is migrated.

**Asset honesty:** Ad Astra / Firmalife Absolute *resource* % counts ids (jar surface) with **placeholder** textures where upstream non-code is ARR — not a license claim on Terrarium/Firmalife art.

### Pack blend weights

| Axis | Weight |
| --- | ---: |
| Resources | 35% |
| Recipes | 35% |
| Mechanics | 30% |

Mod weights inside pack: GregTech 55%, TFC 20%, Firmalife 8%, Ad Astra 8%, Quests 5%, Teams 4%.

## Naming

| Shown in game / docs | Technical folder + id | Upstream |
| --- | --- | --- |
| GregTech | `mods/gtceu` / `gtceu` | GregTech Modern (`gtceu`) |
| TerraFirmaCraft | `mods/tfc` / `tfc` | TFC |
| Firmalife | `mods/firmalife` | Firmalife |
| Ad Astra | `mods/adastra` | Ad Astra |
| FTB Quests | `mods/quests` | FTB Quests |
| FTB Teams | `mods/teams` | FTB Teams |
| Greate | `mods/greate-horizon` / `greate` | Greate (**#2** parked) |

JEI search: `@gtceu` (not `gregtech:` — that id is a different/older ecosystem label).

## Related

- Behaviour: `docs/greglite-behavior.md` / tracker under `mods/gtceu/`  
- Engine headroom / #4 (internal only): `docs/horizon-capability-policy.md` — **not** pack completeness %.
