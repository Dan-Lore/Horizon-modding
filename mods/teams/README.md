# Horizon Teams

Clean-room Horizon rewrite inspired by **FTB Teams**. Not a jar port.
Plan: [`docs/quests-plan.md`](../../docs/quests-plan.md).

## Build

```bash
python3 mods/teams/tools/gen_content.py
python3 tools/pack-teams.py
```

Writes `mods/teams/dist/teams.hmod`. Pin: Horizon `fdc87ae` (hooks 411).
Do not native-build onto `tfg-horizon` until intentional smoke.

## Commands

| Command | Effect |
| --- | --- |
| `/team create <name>` | Create team; you become owner |
| `/team invite <player>` | Invite online player by name |
| `/team join <name>` | Accept invite / join empty name if invited |
| `/team leave` | Leave current team (owner transfers or dissolves) |
| `/team kick <player>` | Owner kicks member |
| `/team info` | Show your team |
| `/team invites` | List pending invites for you |

Solo players get an automatic personal team on first `/team info` or quests access.
