# Agent-control smoke — Horizon Teams + Quests

Pin: `fdc87ae` / hooks 411. Workshop only (`on = []` in `pack/draft-mods.toml`).
Do **not** native-build onto `tfg-horizon` until intentional.

## Pack

```bash
python3 tools/pack-teams.py
python3 mods/quests/tools/gen_content.py
python3 tools/pack-quests.py
```

Install `mods/teams/dist/teams.hmod` and `mods/quests/dist/quests.hmod` on a throwaway instance.

## Smoke (chat / MCP `game_*`)

1. Join world — login tips name Horizon Teams and Horizon Quests.
2. `/team create Alpha` then second client `/team invite` / `/team join Alpha`.
3. `/quests reload` (op) — chapter/quest counts.
4. `/give @s quests:quest_book` → use item → chapter list.
5. `/quests check` → complete welcome checkmarks; `/quests claim welcome`.
6. Gather sticks → gather_sticks completes via tick; `/quests choose gather_sticks 0` then claim.
7. `/give @s quests:loot_crate` → use → table roll.
8. `/quests theme steel` → book accent changes.
9. `/quests edit title welcome New Title` → `/quests reload` keeps override.
10. Team B `/quests progress` does not show Team A completions.

## Blocked (documented)

- Chapter graph pan-zoom
- Auto kill from entity death
- FTB SNBT import
- KubeJS / FTB XMod Compat
