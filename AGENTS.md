# Horizon modding — agent context

**Repo name:** Horizon modding  
**Path:** `C:\Dev\Horizon-modding`

This repo/workspace is for **open-source Minecraft-on-Rust modding**, centered on **Horizon** (Java Edition rewritten in Rust). It is not a Java Forge/Fabric port of TerraFirmaGreg.

Last updated from chat: 2026-11-15.

## Goal

- Support and grow **native Rust modding** on a Mojang-protocol-compatible Minecraft client/server.
- Mojang protocol compatibility is considered a **plus** (vanilla servers, familiar game).
- Long-term: contribute mods, examples, tooling, and upstream hooks — not “ship TFG on Horizon next week”.

## Why Horizon (decision)

| Option | Role here |
| --- | --- |
| **Horizon** | Primary bet: JE **26.3** parity, native mods (`.hmod` / `.hnmod`), MIT, open client+logic |
| Pomme / Torch | Faster vanilla-oriented clients; weaker as a full mod platform |
| Pumpkin / FerrumC / Valence | Servers / custom server frameworks — not the main client-modding path |
| Custom voxel engines | Only if abandoning Mojang protocol (explicitly **not** desired) |
| NeoForge/Fabric (Java) | Still the only realistic path for huge packs like TFG **today**; parallel to this Rust work |

Horizon is the best current **Rust Minecraft analog for a new mod ecosystem**. It is **not** yet a Forge/Fabric replacement for large tech packs.

## Hard facts (Horizon today)

- **Game version:** only **Minecraft Java Edition 26.3**. No separate Horizon builds for 1.20.1 / 1.21.x.
- **Worlds:** saves from **1.8–26.2** open and upgrade to 26.3 (vanilla-style).
- **Servers:** vanilla/Horizon **26.3** is the supported path. Older servers via experimental adapter (`HORIZON_OLDER_SERVERS=1`); incomplete; client resources still prepared from 26.3. Adapter list includes down to **1.20.2** (not a Forge path).
- **Java mods:** Forge / NeoForge / Fabric / Quilt **jars do not run**. Launcher can port some **data/assets** from jars. Optional **Java bridge** for Fabric 26.3 is planned/WIP, not the foundation of this workspace.
- **Launcher pack import (observed 2026-11-11):** Horizon can import local Prism/CurseForge instances (e.g. **TerraFirmaGreg-Modern** 1.20.1 Forge). It **ports content only** (blocks/items/structures/data/resources) — **original mod code is not executed**. Example TFG-Modern inventory in launcher UI: **0** fully ported, **11** partial, **180** not yet, **93** not needed; of mods needing port work, many need engine features Horizon lacks (machines, menus, behaviour, mobs, dimensions, client). A few pure content jars can be ported via “Port N mods”; output under `%AppData%\Roaming\horizon\ports\…`. Modrinth browser may show packs as **«Частично в Horizon»**. This confirms automated **content** porting exists; it does **not** make TFG playable as on Forge.
- **Native modding:**
  - `.hmod` — content (blocks, items, recipes, loot, models, textures); no code
  - `.hnmod` — Rust native mods; launcher compiles them into the game
- **Needs to play:** Microsoft account that owns JE; prepare from a local **26.3** install; JDK mainly for prepare, not for runtime gameplay.

## TFG-Modern (context only — not the deliverable)

- **TerraFirmaGreg-Modern** = Forge **1.20.1** pack (TFC + GregTech Modern + Create + AE2 + Ad Astra + integrations).
- **Cannot** install TFG as a Horizon instance.
- Reading TFG/TFC/GT **open source** is fine for learning mechanics and for a **clean reimplementation** with attribution where licenses allow.
- Having Java sources makes **design** easier; it is still a **rewrite** against Horizon APIs (not a mechanical port).
- Realistic near-term demos: tiny vertical slices (e.g. simple TFC-inspired HUD/stat, one block/item/recipe), **not** GregTech systems.

## Feasibility stance (agreed in chat)

- No hard technical veto against building Horizon-native content inspired by TFG/TFC/GT.
- Blockers are **API/runtime mismatch** and **scope**, not “forbidden by the engine”.
- A week can yield a **small** first mod after learning `.hnmod` — not a pack slice.

## Workspace layout

**One mod per folder; pack assembled later.**

```
C:\Dev\Horizon-modding\
  AGENTS.md           ← this file (read first)
  docs\CONTEXT.md     ← chat/decision briefing
  mods\
    <mod-id>\         ← one Horizon-native mod each (.hmod and/or .hnmod)
    _template\        ← starter / template mirror
  pack\               ← assemble a pack only after individual mods work
    mods\             ← selected builds / links for the pack
  reference\          ← notes / pointers to Java packs (TFG etc.), not the product
  tools\              ← scripts helpers
  upstream\           ← shallow clone of horizon (local, gitignored)
  launcher\           ← portable launcher (binaries gitignored)
```

Do not merge many Java mods into one Horizon mod folder. Port/reimplement separately, then compose under `pack/`.

## Repo & distribution strategy

**This repo = modding draft / workshop only** (Horizon tooling, WIP mods, notes).  
**Published modpack = separate git repo** (decided 2026-11-11). Finished mods also ship as their own downloadable artifacts (and may later get their own repos when stable).

**Players do not clone this draft.** They download built `.hmod` / `.hnmod` (and the pack from its own repo) via Releases / Horizon registry.

| Layer | Where |
| --- | --- |
| WIP mod sources | **This repo** → `mods/<id>/` |
| Local pack experiments | optional `pack/` here (draft only) |
| **Public modpack** | **Separate repository** |
| Stable single mod (optional later) | Own repo + Release assets |
| User download | Per-mod / pack **Release assets**, not `git clone` of the draft |

Keep hard folder boundaries per mod so promotion out of the draft is easy.

Release naming idea: `hello-hud-0.1.0.hmod` / `.hnmod` on tag `hello-hud/v0.1.0`.

## Perf baseline

Vanilla Horizon on the user’s machine (2026-11-11 overlay): **119 fps**, frame **8.4 ms**, max **16.0 ms**, cpu **1.3 ms**, gpu **1.0 ms**. Details: `docs/benchmarks/vanilla-horizon-2026-11-11.md`.

## Horizon registry (what already exists)

Snapshot 2026-11-11: **158** projects — mostly native QoL; **no TFC/GT/TFG** yet. See `docs/horizon-registry-snapshot-2026-11-11.md`. Notable: Create-for-Horizon (alpha), JEI/Jade ports, Additional Lights / Factory Blocks content mods.

## Mod sourcing policy (mandatory)

Full text: `docs/mod-sourcing-policy.md`.

1. **Exists → use it** (JEI, Jade, Create alpha, AE2, …).
2. **Gaps → try contribute** upstream first.
3. **Need more than alpha → own version** in `mods/<id>/` with attribution.
4. **Can't contribute → own version**.
5. **Registry watch ≤ 1× per day** — `tools/check-registry.ps1` (no more frequent polling). Especially watch for a better **Create**.

## Horizon MCP / agent control

**Horizon ships MCP:** `horizon-launcher mcp` (launcher + `game_*`) and `horizon-ctl mcp` (game only). See `docs/pipeline-and-horizon-mcp.md` and upstream `docs/agent-control.md`.

**Cursor:** `horizon` MCP is configured in `~/.cursor/mcp.json` (portable launcher under this repo). Reload MCP / restart Cursor if the `horizon` namespace is missing in the session. In-game **Agent Control** still required for `game_*` unless started via MCP `play`.

## Our pipeline (short)

Workshop repo → use/contrib registry mods + WIP in `mods/` → daily registry check → public **pack in a separate repo** → player downloads via Releases/registry. Details: `docs/pipeline-and-horizon-mcp.md`.

## Draft pack instance (one)

| Role | Id | Play version (2026-11-15) | Notes |
| --- | --- | --- | --- |
| **Pack** | `tfg-horizon` («TFG Horizon») | `native-fdc87ae-428278da87c5` | Batch A + JustEnoughItems 1.1.2 + AE2 **15.4.18** + Greglite **0.4.3** + World Map **0.7.1** (installed, rebuild pending) on Nightly `fdc87ae` |

- `create-dev` / `create-nightly-test` deleted (tests only).
- **Create** cannot join this native: registry 0.7 → `9c7f9b2`, local 0.9 → `4e5296d`; AE2 15.4.18 needs `fdc87ae`/hooks 411. Create hnmod parked under `horizon-native-mods/_parked/`.
- Tip Nightly `9f42064`: AE2 left out (`E_TARGET_NOT_FOUND`); keep installed as base only.
- Keep **prune-old-versions off** while `fdc87ae` + `9f42064` nightlies must remain.
- Create clone: `mods/create-horizon/`. Manifest: `pack/draft-mods.toml`.
- Greglite Electric Age plan + tracker: `docs/greglite-electric-plan.md`, `docs/greglite-electric-tracker.md`, `mods/greglite/tracker/catalog.json`.
- TFC Horizon 0.1.0 (workshop, not on the pack pin): `docs/tfc-plan.md`, `docs/tfc-tracker.md`, `mods/tfc/`. `on = []` so AE2/Greglite stay the native-build.
- Horizon Teams + Quests (workshop, not on the pack pin): `docs/quests-plan.md`, `docs/quests-tracker.md`, `mods/teams/`, `mods/quests/`. `on = []` until W6+ intentional smoke.


## Links

- Site / docs: https://playhorizon.dev/
- Install: https://playhorizon.dev/docs/install
- Upstream: https://github.com/horizon-rust/horizon
- Mods docs (upstream): `upstream/docs/mods.md`, native mods docs beside it
- Native mod template (upstream org): https://github.com/horizon-rust/horizon-native-mod-template

## MVP plan

Full plan: **`docs/mvp-tfg-plan.md`**.  
**Locked transfer list:** **`docs/mod-transfer-list.md`** (+ `pack/draft-mods.toml`).  
MVP Batch A on **`tfg-horizon`**: Nightly `fdc87ae` + JustEnoughItems 1.1.2 + Jade + AE2 **15.4.18** + AppleSkin + Continuity + Greglite **0.4.3**.  
Create stays isolated until upstream shares a pin with AE2. Electric Age: `docs/greglite-electric-plan.md`.

## Suggested next work for agents

1. Smoke `tfg-horizon` (JEI creative panel, AE2, Greglite machines) on `native-fdc87ae-428278da87c5`.
2. Native-build **only** for that pack instance; do not pile tip+AE2 until registry AE2 supports `9f42064`.
3. Run `tools/check-registry.ps1` ≤1×/day UTC — watch Create / AE2 pin convergence.
4. Greglite waves from `mods/greglite/tracker/catalog.json` gaps after smoke.

**Native build smoke (mandatory):** `.cursor/rules/horizon-native-build-smoke.mdc` + `docs/dev-tips-native-content.md`.  
Do **not** report a mod as playable from `native-mods.json` or a chat tip alone — require `horizon-mod-ids.json` includes the id and `/give <id>:…` succeeds. Stale `.horizon-cache/mod-content` with only `["ae2"]` is a known failure mode.

## Out of scope unless the user asks again

- Porting full TFG-Modern to Horizon
- Treating Java bridge as the main strategy
- Replacing the user’s Forge TFG play setup with Horizon
