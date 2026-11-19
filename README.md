# Horizon modding

Workshop for **Horizon** (Minecraft JE on Rust) and native mods.

Path: `C:\Dev\Horizon-modding`

**Agents:** read [`AGENTS.md`](AGENTS.md) first. Doc map: [`docs/README.md`](docs/README.md).

## Layout

| Path | Contents |
| --- | --- |
| `AGENTS.md` | Current briefing — instances, rules, next work |
| `docs/` | Plans, trackers, license table, smoke tips |
| `.cursor/rules/` | Always-on: porting licenses + native smoke |
| `mods/<mod-id>/` | One folder per WIP Horizon mod |
| `pack/` | Draft pack manifest (`draft-mods.toml`) — public pack = other repo |
| `reference/` | Pointers to Java packs (TFG), not shippable content |
| `tools/` | Helper scripts |
| `upstream/` | Shallow clone of horizon (local, gitignored) |
| `launcher/` | Portable Windows launcher |

## Play

1. `launcher\windows-x64\horizon-launcher.exe`
2. Microsoft account that owns Java Edition
3. Install / Prepare **26.3** → Play

Instances: **`tfg-horizon`** (pinned) · **`tfg-dev`** (rebuild only). Details in `AGENTS.md`.

## Develop

Upstream mods docs + [native mod template](https://github.com/horizon-rust/horizon-native-mod-template). New work under `mods/`.

- Pipeline / MCP: `docs/pipeline-and-horizon-mcp.md`
- Sourcing: `docs/mod-sourcing-policy.md`
- Licenses: `docs/asset-license-table.md`
- Registry watch: `tools/check-registry.ps1` (≤1×/day)

## License note

Upstream Horizon is MIT. Minecraft assets/code are Mojang/Microsoft — not redistributed here. Third-party mod assets: check `docs/asset-license-table.md` before vendoring.
