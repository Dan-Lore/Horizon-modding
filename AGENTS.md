# Horizon modding — agent context

**Path:** `C:\Dev\Horizon-modding`  
**Updated:** 2026-11-19

Workshop for **Horizon** (Minecraft JE **26.3** on Rust) native mods (`.hmod` / `.hnmod`).  
Doc map: [`docs/README.md`](docs/README.md).

## Goal

Grow Horizon-native mods and a TFG-**inspired** playable draft pack.  
Not: run Forge jars, or claim 1:1 TerraFirmaGreg-Modern parity overnight.

**Reference pack (read freely):**  
`C:\Users\smoln\curseforge\minecraft\Instances\TerraFirmaGreg-Modern`  
(Forge 1.20.1). See `.cursor/rules/tfg-horizon-porting.mdc` + [`docs/asset-license-table.md`](docs/asset-license-table.md).

## Hard facts

- Only JE **26.3** on Horizon. Forge/Fabric/Quilt jars **do not execute**.
- Launcher can port some jar **data/assets**; gameplay needs native rewrite.
- Native: `.hmod` (content) and/or `.hnmod` (Rust compiled into the game).
- Play needs a Microsoft account that owns JE; Prepare from local 26.3.

## Instances (locked)

| Role | Id | Version | Rule |
| --- | --- | --- | --- |
| Working save | `tfg-horizon` | **pinned** `native-fdc87ae-428278da87c5` | Do **not** native-build |
| Dev | `tfg-dev` | `native-fdc87ae-01abd5b2b6a6` | Rebuild **only** here |

- Base: Nightly `fdc87ae` (`nightly-2026-11-08-fdc87ae`), hooks **411**, AE2 **15.4.18**.
- Create parked (pin clash with AE2). Tip `9f42064`: AE2 left_out — base only.
- `prune-old-versions` **off**. Manifest: `pack/draft-mods.toml`.

## Always-on rules

1. **Porting / licenses** — `.cursor/rules/tfg-horizon-porting.mdc`
2. **Native smoke** — `.cursor/rules/horizon-native-build-smoke.mdc` + `docs/dev-tips-native-content.md`  
   Playable = `horizon-mod-ids.json` + `/give`, not chat tips / `native-mods.json` alone.

## Mod sourcing

[`docs/mod-sourcing-policy.md`](docs/mod-sourcing-policy.md): registry first → contribute → own in `mods/<id>/`.  
Registry watch ≤1×/day: `tools/check-registry.ps1`.

## Active plans

| Area | Active doc |
| --- | --- |
| Greglite next waves | **`docs/greglite-continuation-plan.md`** (+ `docs/greglite-behavior.md`) |
| Greglite W0–W9 checklist | `docs/greglite-electric-plan.md` (**closed** / historical) |
| TFC / Ad Astra / Quests | `docs/tfc-plan.md`, `adastra-plan.md`, `quests-plan.md` (+ trackers) |
| Transfer list | `docs/mod-transfer-list.md` |
| MVP Batch A | `docs/mvp-tfg-plan.md` (**done** / historical) |

## Layout

```
AGENTS.md, docs/, mods/<id>/, pack/, reference/, tools/, upstream/, launcher/
```

One mod per folder. Public modpack = **separate repo** later. This tree is the draft workshop.

## MCP

- Horizon: `user-horizon` (from `~\.cursor\mcp.json` → portable launcher `mcp`)
- Craft Anything (optional jar study): `user-craft-anything` — **Deep mode** for insides; do **not** use its Rebuild for Horizon ports

## Suggested next work

1. Greglite **N-waves** on `tfg-dev` per `docs/greglite-continuation-plan.md` (code for N0–N6 is largely in 0.5.0; behaviour checklist still needs Play verification when asked).
2. Native-build **only** `tfg-dev` on `nightly-2026-11-08-fdc87ae`.
3. Registry check ≤1×/day — Create/AE2 pin convergence.
4. New slices only after license check (`docs/asset-license-table.md`).

## Out of scope unless asked

- Claiming full TFG-Modern parity or shipping Forge jars as the play stack
- Java bridge as the main strategy
- Replacing the user’s Forge TFG install with Horizon
- Native-building pinned `tfg-horizon` “to try something”

## Links

- https://playhorizon.dev/ · https://github.com/horizon-rust/horizon  
- Template: https://github.com/horizon-rust/horizon-native-mod-template
