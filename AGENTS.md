# Horizon modding — agent context

**Path:** `C:\Dev\Horizon-modding`  
**Updated:** 2026-11-20

Workshop for **Horizon** (Minecraft JE **26.3** on Rust) native mods (`.hmod` / `.hnmod`).  
Doc map: [`docs/README.md`](docs/README.md).

## Goal

Grow a TFG-shaped Horizon pack. Display names match upstream (**GregTech**, **TerraFirmaCraft**, **Ad Astra**, …).  
GregTech technical id is **`gtceu`** (folder `mods/gtceu/`).

**Player-facing completeness** → [`docs/tfg-content-coverage.md`](docs/tfg-content-coverage.md) + `tools/score-tfg-content.py` (Absolute denominators, milestone ladder).  
Live scoreboard: see `docs/tfg-content-score.json` (M50 band after Absolute expanders — not M100).

Not: run Forge jars, or claim 1:1 TerraFirmaGreg-Modern overnight.

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
| Working save | `tfg-horizon` | **pinned** `native-fdc87ae-19d680588c6f` | Do **not** native-build |
| Dev | `tfg-dev` | `native-fdc87ae-19d680588c6f` | Rebuild **only** here (each build replaces this pin) |

- Base: Nightly `fdc87ae` (`nightly-2026-11-08-fdc87ae`), hooks **411**, AE2 **15.4.18**.
- Create parked (pin clash with AE2). Tip `9f42064`: AE2 left_out — base only.
- After a successful smoke on `tfg-dev`, re-pin `tfg-horizon` to that native and remove older `native-fdc87ae-*`.
- `prune-old-versions` **off** (keeps Nightly `fdc87ae`). Manifest: `pack/draft-mods.toml`.

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
| **Content % (quote this)** | **`docs/tfg-content-coverage.md`** (+ `tools/score-tfg-content.py`) |
| GregTech next waves | `docs/gtceu-continuation-plan.md` (+ `docs/gtceu-behavior.md`) |
| GregTech W0–W9 checklist | `docs/gtceu-electric-plan.md` (**closed** / historical) |
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

## Two different “% complete” numbers

| Metric | Doc | Meaning |
| --- | --- | --- |
| **TFG content** | `docs/tfg-content-coverage.md` | Resources + recipes + mechanics vs TFG — **use this with the player** |
| Engine headroom (#4) | `docs/horizon-capability-policy.md` | Don’t leave free Horizon API unused — **internal**, not pack parity |

Allowed unfinished for content: only **#1** API, **#2** pin clash, **#3** registry — still does **not** make the pack Absolute GT.

## Build helper

`tools/tfg-dev-native-build.ps1` — pack workshop `.hmod` → `native-build` on `tfg-dev` / Nightly `fdc87ae` → content mirror → wipe `mod-content`. Optional `-RepinHorizon -RemoveOldNatives`. AppData Horizon paths are in-scope (see `.cursor/rules/horizon-appdata-ok.mdc`).

## Suggested next work

1. Grow **GregTech** recipe/material coverage (bath, centrifuge, ores) per `tfg-content-coverage.md`.  
2. Optional later: migrate id `gtceu` → `gtceu` so JEI matches `gtceu:` / stops looking for bare `gregtech:`.  
3. Stay on **`native-fdc87ae-19d680588c6f`** (or newer after green `tfg-dev` build); tip `dd67b76` watch-only until AE2 is back (#3).  
4. Registry ≤1×/day.

## Out of scope unless asked

- Claiming full TFG-Modern parity or shipping Forge jars as the play stack
- Java bridge as the main strategy
- Replacing the user’s Forge TFG install with Horizon
- Native-building pinned `tfg-horizon` “to try something”

## Links

- https://playhorizon.dev/ · https://github.com/horizon-rust/horizon  
- Template: https://github.com/horizon-rust/horizon-native-mod-template
