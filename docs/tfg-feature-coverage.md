# TFG Horizon — implementable feature coverage

**Metric:** % of features that are *in principle* implementable on Horizon (some pin), with status `done` or `partial`.  
**Not in denominator:** `horizon_blocked`.  
**Not in goal:** jar count, ARR asset clones, Forge-only runtimes, KubeJS bus parity.

Machine source: [`tfg-feature-catalog.json`](tfg-feature-catalog.json).  
Audit: [`tfg-feature-audit.md`](tfg-feature-audit.md).

## Scoreboard

| When | Implementable | done+partial | % | Notes |
| --- | ---: | ---: | ---: | --- |
| Baseline (catalog fill) | 85 | 58 | 68.2% | Batch A + Greglite N1–N7 + TFC |
| After phase 1–3 | 85 | 77 | 90.6% | N8, Firmalife, Create map, quests |
| After continue | 85 | 84 | 98.8% | vat/hive/covers/glue |
| After deepen | 85 | 84 | 98.8% | circuits, sprinkler ticks |
| **Audit → 100%** | **85** | **85** | **100%** | `greate-horizon` closes last todo |

**Goal:** ≥60% — **met**. **Implementable 100%** — **met** (0 todos). Horizon-blocked remain 13.

Re-score:

```powershell
python -c "import json; from pathlib import Path; c=json.loads(Path('docs/tfg-feature-catalog.json').read_text(encoding='utf-8')); f=c['features']; i=[x for x in f if x['status']!='horizon_blocked']; n=[x for x in i if x['status'] in ('done','partial')]; print(f'{len(n)}/{len(i)} = {100*len(n)/len(i):.1f}%')"
```

## Pillars (implementable)

| Pillar | Coverage | Notes |
| --- | --- | --- |
| qol_registry | 6/6 | Batch A |
| ae2 | 4/4 | Registry AE2 |
| greglite | 26/26 | Through 0.5.5 (N8, circuits, covers, pipes, drill) |
| tfc | 13/13 | Core 0.2 |
| firmalife | 8/8 | 0.1.2 ticks |
| adastra | 7/7 | Overworld |
| teams_quests | 7/7 | Expanded questline |
| create | 9/9 | Kinetics + cobblegen note + greate-horizon partial |
| pack_glue | 5/5 | `pack/glue` |

## Horizon-blocked (excluded)

| Gap | Feature ids |
| --- | --- |
| BlockStateId place-replace (API 446+) | `tfc_collapse_cobble`, `tfc_chisel_mutate` |
| No chunk/worldgen place | `tfc_rock_layers`, `tfc_ore_veins`, `tfc_climate_maps` |
| No custom entity spawn | `tfc_animals` |
| No item-component write | `tfc_food_rot_per_stack` |
| No custom dimensions | `aa_planets_dims`, `aa_rocket_travel` |
| Thin client UI | `tq_quest_graph_ui` |
| Living-death hook incomplete | `tq_kill_tasks_auto` |
| Create pin ≠ AE2 pin | `cr_ae2_same_native` |
| Forge KubeJS event bus | `pg_kubejs_parity` |

## Code-first rules

1. No routine `native-build`.
2. Update catalog status with each feature change.
3. Assets per [`asset-license-table.md`](asset-license-table.md).
4. Batched Play smoke only on request.
