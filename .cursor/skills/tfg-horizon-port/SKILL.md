---
name: tfg-horizon-port
description: >-
  Port / rewrite TFG-Modern (MC JE 1.20.1 Forge) mechanics into Horizon 26.3
  native mods under mods/<id>/. Use when studying TFG jars or upstream sources,
  checking asset licenses, or mapping a wave onto Horizon hooks.
---

# TFG → Horizon port

**Canon (do not fork policy here):**

- Rule: `.cursor/rules/tfg-horizon-porting.mdc`
- Licenses: `docs/asset-license-table.md`
- Smoke: `.cursor/rules/horizon-native-build-smoke.mdc`
- Briefing: `AGENTS.md`

## Workflow

1. Name the slice (`mods/<id>/` + plan/tracker under `docs/`).
2. Read TFG / upstream **sources** (path in the porting rule). No fake clean-room ban.
3. License-check before any texture/sound/model copy.
4. Implement against Horizon hooks (default pin `fdc87ae` / 411 unless the plan says otherwise).
5. Native-build only **`tfg-dev`**. Never rebuild pinned `tfg-horizon` unless the user says so.
6. “Done” = content ids + `/give`, not login tips.

## Craft Anything

Optional for jar layout when sources are missing (**Deep mode**).  
Do **not** use Craft Anything **Rebuild** for Horizon — wrong stack; Cursor writes `mods/<id>/`.
