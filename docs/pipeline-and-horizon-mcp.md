# Pipeline & Horizon agent surfaces

## Does Horizon have MCP?

**Yes.** Official agent control (docs in upstream `docs/agent-control.md`, players: https://playhorizon.dev/docs/agents):

| Surface | How | What it does |
| --- | --- | --- |
| **`horizon-launcher mcp`** | stdio MCP | One server for Cursor/Claude/etc.: launcher tools + session (`play`, `server`, …) + game tools as `game_*` |
| **`horizon-ctl mcp`** | stdio MCP | Game-only tools (drive a running client via control socket) |
| **`horizon-ctl` CLI** | shell | Same commands without MCP (`state`, `goto`, `break`, `screenshot`, …) |
| Control socket | local | Low-level JSON lines; what ctl wraps |

Rough scale: ~96 `horizon-ctl` commands, ~88 exposed as MCP tools; launcher adds mods/modpack/versions/account tools.

**Cursor MCP config:** `~/.cursor/mcp.json` includes server `horizon` →  
`C:\Dev\Horizon-modding\launcher\windows-x64\horizon-launcher.exe mcp`  
(generated via `horizon-launcher agent-config`; keep `context-mode` entry).

After editing `mcp.json`, **reload MCP / restart Cursor** so the agent session picks up the `horizon` namespace. Then ask it to call e.g. `links` or `play`.

Enable **Agent Control** in-game (Settings → AI Agent) or start via MCP `play` so `game_*` tools answer.

## Our pipeline (Horizon modding workshop)

```
┌─────────────────────────────────────────────────────────┐
│  This repo (draft / workshop)                           │
│  mods/<id>/  ·  docs/  ·  tools/  ·  reference/         │
└───────────────┬─────────────────────────┬───────────────┘
                │                         │
                ▼                         ▼
     registry mods (use)          our .hmod / .hnmod WIP
     JEI, Jade, Create α, …       only if missing / blocked
                │                         │
                └──────────┬──────────────┘
                           ▼
              contribute upstream when possible
                           │
                           ▼
              separate **pack repo** (public modpack)
                           │
                           ▼
              players: Releases / Horizon registry
```

### Daily / recurring

| Cadence | Action |
| --- | --- |
| ≤ 1× / day | `tools/check-registry.ps1` — Create/JEI/Jade/AE2/TFC keywords |
| On demand | Develop/test mods; try PRs to Create-for-Horizon etc. |
| When ready | Publish mod artifacts; assemble pack in **other** repo |

### Agent interaction modes (once MCP is on)

1. **Playtest** — `play` / `game_state` / `game_screenshot` / move-break for smoke tests of content mods. For combined native+content mods, `/give` beats JEI search; see `docs/dev-tips-native-content.md`.
2. **Launcher ops** — `mods_search`, install registry mods, modpack import (not a substitute for native ports).
3. **Dev without MCP** — edit `mods/`, build via Horizon native-mod tooling / launcher Build, manual play.

### Sourcing reminder

Exists → use → contribute → own if alpha insufficient or contrib fails. See `docs/mod-sourcing-policy.md`.
