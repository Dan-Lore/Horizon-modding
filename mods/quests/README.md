# Horizon Quests

Clean-room Horizon rewrite inspired by **FTB Quests**. Not a jar port.
Depends on **Horizon Teams** for per-team progress.
Plan: [`docs/quests-plan.md`](../../docs/quests-plan.md).

## Build

```bash
python3 mods/quests/tools/gen_content.py
python3 tools/pack-quests.py
```

## Commands

| Command | Effect |
| --- | --- |
| `/quests book` | List chapters / quests (theme-coloured) |
| `/quests check` | Complete pending checkmark tasks |
| `/quests claim <quest>` | Claim rewards |
| `/quests choose <quest> <index>` | Pick a choice reward |
| `/quests progress` | Show team progress |
| `/quests reload` | Op: reload baked + world overrides |
| `/quests theme <id>` | Set world theme |
| `/quests edit title <quest> <text…>` | Op: world override title |
| `/quests kill <task>` | Stub for kill tasks |
| `/quests adv <task>` | Stub for advancement-like tasks |

Use `quests:quest_book` or place `quests:quest_board`.
