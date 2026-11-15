# Horizon Quests / Teams tracker

Generated from `mods/teams/tracker/catalog.json` and `mods/quests/tracker/catalog.json`.
Pin: `fdc87aecdbd116bf1e08adcd062fcbaea8c2e2ca`, hooks 411.

## Teams

| Wave | System | Status | Smoke |
| --- | --- | --- | --- |
| W0 | Scaffold, NOTICE, pack script | done | python3 tools/pack-teams.py writes mods/teams/dist/teams.hmod. Login tip names Horizon Teams. |
| W1 | Teams create/invite/join/leave/kick + persist | done | /team create <name>, /team invite <player>, /team join <name>, /team leave, /team kick <player>, /team info. Data under world_dir()/horizon-teams/teams.json. |

## Quests

| Wave | System | Status | Smoke |
| --- | --- | --- | --- |
| W0 | Scaffold, NOTICE, pack script, login tip | done | python3 tools/pack-quests.py writes mods/quests/dist/quests.hmod after gen_content. Login tip names Horizon Quests. |
| W2 | Quest schema v1 + demo chapter | done | /quests reload (op) prints chapter and quest counts from baked tables + world overrides. |
| W3 | TeamProgress store + sync | done | /quests progress shows team id and completed quests. Team A completion does not appear for Team B. |
| W4 | Tasks v1: checkmark, item, kill stub | done | /quests check completes checkmark tasks. Item tasks complete when count_items meets target (player_tick). Kill is command stub /quests kill <task_id> until entity-death hooks are wired. |
| W5 | Rewards v1: item, xp, command + claim | done | /quests claim <quest_id> grants unclaimed rewards once per player after quest complete. |
| W6 | Quest book UI v1 | done | Use quests:quest_book (or /quests book) to list chapters/quests in chat. Quest board block opens a submit menu for item tasks. |
| W7 | Dependencies + linear/flexible | done | Child quest locked until parents done in linear mode; flexible allows item progress early but claim waits for parents. |
| W8 | Reward tables + choice | done | /quests claim rolls weighted tables; /quests choose <quest_id> <index> picks a choice reward. |
| W9 | Loot crates | done | /give quests:loot_crate then use item to roll reward_table starter_crate. |
| W10 | In-game editor (ops) | done | /quests edit title <quest_id> <text...> writes world override; /quests reload picks it up. |
| W11 | GUI themes | done | /quests theme <id> sets world theme; book lines use theme accent prefix. |
| W12 | Tasks v2: location, inventory observe | done | location with `item` scans for that block within radius (quest board); fixed xyz otherwise. Inventory mirrors item detect. Advancement-like is /quests adv <id> stub. |
| W13 | Pack questline (TFG Horizon) | done | Chapters intro, ae2_start, greglite_start, tfc_start — first five quests completable with sticks/book/board. |
| W14 | Multiplayer polish | done | Invites expire; double-claim blocked; /team invites lists pending. Documented for 2-client smoke. |
| W15 | Polish + blocked hooks | done | Tracker lists blocked: chapter graph pan-zoom, entity-death kill auto, FTB SNBT import, KubeJS bus. Agent smoke: `tools/smoke-quests.md`. |

## Blocked / deferred

| Item | Why |
| --- | --- |
| FTB / TFG `.snbt` import | ARR + format mismatch; own JSON only |
| Chapter graph pan-zoom | Needs richer client UI than hooks 411 menus |
| Auto kill tasks | Wire `living` death when available; stub command for now |
| KubeJS / FTB XMod Compat | Out of scope |
