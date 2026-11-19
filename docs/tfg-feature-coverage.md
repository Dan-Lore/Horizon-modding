# TFG Horizon — implementable feature coverage

**Metric (policy 2026-11-19):** among features where blockers **1–3** do not apply, status must be **`done`** (`partial` = debt).  
**Not in denominator:** `horizon_blocked` (#1 API / #2 pin clash / #3 registry).  
**Not in goal:** jar count, ARR asset clones, Forge-only runtimes, Absolute TFG parity.

Machine source: [`tfg-feature-catalog.json`](tfg-feature-catalog.json).  
Policy: [`horizon-capability-policy.md`](horizon-capability-policy.md).

## Scoreboard

| When | Implementable | strict `done` | % | Notes |
| --- | ---: | ---: | ---: | --- |
| Old done+partial metric | 85 | 85 (incl. partial) | 100% | counted stubs as success |
| **2026-11-20 capability audit** | **77** | **77** | **100%** | Create→#2; rocket→#1; deepen + `lv_drill` |

Horizon-blocked: **21** (TFC worldgen/animals/powder-adjacent, Ad Astra dims, Create/Greate pin, KubeJS parity).

Re-score (strict):

```powershell
python -c "import json; from pathlib import Path; c=json.loads(Path('docs/tfg-feature-catalog.json').read_text(encoding='utf-8')); f=c['features']; i=[x for x in f if x['status']!='horizon_blocked']; d=[x for x in i if x['status']=='done']; print(f'{len(d)}/{len(i)} = {100*len(d)/len(i):.1f}%'); print('partial', sum(1 for x in i if x['status']=='partial'))"
```

## Pillars (implementable = not blocked)

| Pillar | Coverage | Notes |
| --- | --- | --- |
| qol_registry | done | Batch A |
| ae2 | done | Registry AE2 on `fdc87ae` |
| gtceu | done | Through 0.5.5 + drill `break_speed` |
| tfc | done (core) | Animals/worldgen/per-stack rot blocked |
| firmalife | done | 0.1.2 ticks + recipes |
| adastra | done (overworld) | Planets/rocket travel #1 |
| teams_quests | done | kill/adv/UI + `/hteam` |
| create | **blocked #2** | pin ≠ AE2 |
| pack_glue | done | tips / glue; KubeJS parity blocked |

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
