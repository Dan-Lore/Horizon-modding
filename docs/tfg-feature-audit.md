# TFG feature catalog audit (2026-11-19)

**Scope:** `docs/tfg-feature-catalog.json` statuses vs workshop evidence.  
**Metric:** implementable = not `horizon_blocked`; numerator = `done` + `partial`.

## Result

| | Count |
| --- | ---: |
| Total features | 98 |
| Horizon-blocked (excluded) | 13 |
| Implementable | 85 |
| done + partial | **85** |
| todo | **0** |
| **Implementable %** | **100%** |

## Probe summary

Automated checks against `mods/`, `pack/glue/`, questfile bake:

- Firmalife blocks/ticks (vat, beehive, drying, sprinkler) — present
- Greglite N8 shells, circuits, covers, pipes, drill — present
- Pack glue tags/recipes — present
- Quests depth (`fl_sprinkler`, `gl_circuit`, …) — present
- Create kinetics — evidence in `mods/create-horizon` (awaits pin notes)
- **Greate** — was the only `todo`; closed with `mods/greate-horizon/` 0.1.0 (tier logic + shaft stubs). Co-build still parked (same pin story as `cr_ae2_same_native`, which stays blocked).

## Honesty notes

| Status | Meaning here |
| --- | --- |
| `done` | Usable vertical slice in repo (content and/or hooks) |
| `partial` | Real code/data, incomplete vs TFG Absolute (e.g. fluid sim, cover attach, Create pin) |
| `horizon_blocked` | Cannot finish on hooks 411 / `fdc87ae` without upstream API or pin convergence |

`partial` rows are **intentional** — 100% means “no unimplemented implementable work left,” not “TFG parity.”

## Horizon-blocked (unchanged)

Worldgen place, BlockStateId mutate, animals, per-stack food NBT, Ad Astra dimensions, quest graph UI, auto-kill hook, Create+AE2 same native, KubeJS bus.

## Next when pins move

1. Shared Nightly with Create + AE2 → enable `greate` + Create on `tfg-dev`
2. Wire `greate` shaft tiers into Create kinetic runtime
3. Batched native-build + `/give` smoke only when asked
