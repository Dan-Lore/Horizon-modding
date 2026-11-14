# Horizon modding

Working directory for **Horizon** (Minecraft JE on Rust) and native mods.

Path: `C:\Dev\Horizon-modding`

## Layout

| Path | Contents |
| --- | --- |
| `AGENTS.md` | Short briefing for Cursor/other agents — **read first** |
| `docs/CONTEXT.md` | Longer chat/decision dump |
| `mods/<mod-id>/` | **One folder per WIP mod** (`.hmod` / `.hnmod`) |
| `pack/` | Local/draft pack experiments only — **public pack = other repo** |
| `docs/benchmarks/` | Perf snapshots (e.g. vanilla Horizon baseline) |
| `reference/` | Design notes / pointers (e.g. TFG), not shippable content |
| `tools/` | Helper scripts |
| `upstream/` | Shallow clone of [horizon-rust/horizon](https://github.com/horizon-rust/horizon) (local) |
| `launcher/` | Portable Windows launcher `0.2.59` |

## Play (launcher)

1. Run `launcher\windows-x64\horizon-launcher.exe` (path may vary after extract).
2. Sign in with a Microsoft account that owns Java Edition.
3. Install a Horizon version → **Prepare** against your Minecraft **26.3** files → Play.

## Develop

See upstream `docs/mods.md` and the [native mod template](https://github.com/horizon-rust/horizon-native-mod-template). Put new mods under `mods/`.

Pipeline + Horizon MCP: `docs/pipeline-and-horizon-mcp.md`.  
Sourcing policy: `docs/mod-sourcing-policy.md`.  
**MVP plan:** `docs/mvp-tfg-plan.md`.  
Daily registry: `tools/check-registry.ps1`.

## License note

Upstream Horizon is MIT (their original work). Minecraft assets/code are Mojang/Microsoft; this workspace does not redistribute them.
