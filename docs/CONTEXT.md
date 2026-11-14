# Project briefing (from planning chat)

**Repo:** Horizon modding (`C:\Dev\Horizon-modding`)

## What we decided

The user wants to **support open-source Minecraft-on-Rust modding**. Mojang protocol compatibility is welcome. **Horizon** is the chosen platform.

We explicitly rejected treating this workspace as “port TFG-Modern onto Horizon as a pack.” TFG remains useful as **inspiration and reference** (open sources where licensed), not as an install target.

## Research summary — Rust Minecraft landscape

### Clients (vanilla-compatible)

- **Horizon** — JE 26.3 rewrite in Rust; launcher; native mods; best full-game candidate.
- **Pomme** (Rust + Vulkan) — joins vanilla ~1.20–26.3; Microsoft auth; no Fabric/Forge.
- **Torch** (Rust + Bevy/wgpu) — claims large FPS/RAM wins; 26.1.1 + 1.21.11; desktop joins normal servers.

### Servers

- **Pumpkin**, **FerrumC** — Rust servers (vanilla-oriented / early).
- **Valence** — Bevy ECS framework for custom Minecraft servers.

### Custom voxel (non-protocol)

- Minerust, Wildforge, git-craft, Rezcraft, Bevy+wgpu — fine for original games; out of scope given protocol preference.

## Horizon versioning (important)

- One game: **26.3**.
- Launcher “Versions” page = Horizon build numbers / nightlies, not Mojang version picker for 1.20.1.
- Experimental older-server protocol adapter exists; not a path to Forge TFG.

## Modding model

Write Horizon-native content:

1. Learn upstream docs + `horizon-native-mod-template`.
2. Ship tiny public example mods (ecosystem value).
3. Optionally upstream missing hooks.
4. Later: small TFC-inspired mechanics with attribution — never “full TFG”.

**Repo structure:** each WIP mod in `mods/<mod-id>/`. This repo is the **modding draft**; the **public modpack is a separate repo**. Local `pack/` is optional scratch only. Do not port an entire Java pack into one Horizon mod.

**Perf baseline (vanilla Horizon, 2026-11-11):** 119 fps · frame 8.4 ms · max 16.0 · cpu 1.3 · gpu 1.0 ms — see `docs/benchmarks/vanilla-horizon-2026-11-11.md`.

## Legal / attribution (light)

Open-source reading and clean-room / licensed reimplementation with credit is fine. Do not claim official TerraFirmaGreg. Respect ARR mods (no decompile/translate of closed jars). Player must own Minecraft; Horizon prepares from their files.

## Launcher observation (user screenshots, 2026-11-11)

Horizon’s **Modpacks** UI already imports local builds and Modrinth packs:

- Local find: **TerraFirmaGreg-Modern** (1.20.1 · forge 47.4.13 · 284 files).
- Ports what it can **on this PC from your downloads**; nothing uploaded.
- TFG-Modern status shown: **0** ported · **11** partial · **180** not yet · **93** not needed.
- Explicit: needing-port mods come as **content only**; **code does not run**.
- UI breakdown: a few content-only mods portable now; **~126** need missing engine support (machines, menus, behaviour, mobs, dimensions, client).
- Port output path pattern: `%AppData%\Roaming\horizon\ports\terrafirmagreg-modern`.
- Modrinth may tag related packs **«Частично в Horizon»**.

**Takeaway:** content-port pipeline is real (assets/data experiments). TFG gameplay parity still needs **native `.hmod`/`.hnmod`** and upstream engine work — not the importer alone.

## Mod sourcing (2026-11-11)

Use existing Horizon mods → contribute if possible → own build if alpha insufficient or contribution fails. Daily registry monitor max once/day (`tools/check-registry.ps1`), watching especially for a better Create. Policy: `docs/mod-sourcing-policy.md`.

## Dev tips (from play sessions)

Native Hooks can ship without registries. Greglite 2026-11-12: login tip worked, `/give greglite:…` was Unknown item, AE2 creative tab still fine — active native build had **no** `native-content/greglite`. Notes: `docs/dev-tips-native-content.md`.

## User intent keywords

- open-source Minecraft Rust modding
- Horizon as future mod platform
- protocol compatibility = good
- incremental implementation OK
- TFG as inspiration, not binary port
