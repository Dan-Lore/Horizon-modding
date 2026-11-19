//! Quest gating, completion, rewards.

use crate::file::{self, Quest, Reward};
use crate::progress;
use horizon_client::mod_api::{Host, Text};

pub fn deps_met(team: &str, quest: &Quest) -> bool {
    quest
        .dependencies
        .iter()
        .all(|d| progress::is_quest_done(team, d))
}

pub fn flexible_chapter(quest_id: &str) -> bool {
    file::chapter_for_quest(quest_id)
        .map(|c| c.progression == "flexible")
        .unwrap_or(false)
}

pub fn can_progress_tasks(team: &str, quest: &Quest) -> bool {
    if flexible_chapter(&quest.id) {
        true
    } else {
        deps_met(team, quest)
    }
}

pub fn can_complete_quest(team: &str, quest: &Quest) -> bool {
    if !deps_met(team, quest) {
        return false;
    }
    quest
        .tasks
        .iter()
        .all(|t| progress::is_task_done(team, &t.id))
}

pub fn refresh_quest(team: &str, quest: &Quest) {
    if can_complete_quest(team, quest) && !progress::is_quest_done(team, &quest.id) {
        progress::complete_quest(team, &quest.id);
    }
}

pub fn roll_table(table: &str) -> Option<(String, i32)> {
    let file = file::load();
    let entries = file.tables.get(table)?;
    let total: i32 = entries.iter().map(|e| e.weight.max(1)).sum();
    if total <= 0 {
        return None;
    }
    // simple LCG from time
    let mut seed = std::time::SystemTime::now()
        .duration_since(std::time::UNIX_EPOCH)
        .map(|d| d.as_nanos() as u64)
        .unwrap_or(1);
    seed = seed.wrapping_mul(6364136223846793005).wrapping_add(1);
    let pick = (seed % total as u64) as i32;
    let mut acc = 0;
    for e in entries {
        acc += e.weight.max(1);
        if pick < acc {
            return Some((e.item.clone(), e.count));
        }
    }
    entries
        .last()
        .map(|e| (e.item.clone(), e.count))
}

fn give(host: &mut dyn Host, item: &str, count: i32) {
    if count > 0 {
        let _ = host.give_items(item, count as u32);
    }
}

pub fn grant_reward(
    host: &mut dyn Host,
    team: &str,
    player: u128,
    quest_id: &str,
    reward: &Reward,
) -> String {
    if progress::is_claimed(team, player, quest_id, &reward.id) {
        return format!("{} already claimed", reward.id);
    }
    match reward.kind.as_str() {
        "item" => {
            if let Some(item) = &reward.item {
                give(host, item, reward.count);
                progress::mark_claimed(team, player, quest_id, &reward.id);
                format!("claimed {} x{}", item, reward.count)
            } else {
                "item reward missing item".into()
            }
        }
        "xp" => {
            // Hooks 101+: give_experience; fall back message if the host no-ops.
            let _ = host.give_experience(player, reward.amount as u32);
            progress::mark_claimed(team, player, quest_id, &reward.id);
            format!("claimed {} XP", reward.amount)
        }
        "command" => {
            if let Some(cmd) = &reward.command {
                // Console run_command needs no swapped player; announce to everyone instead.
                for p in host.server_players() {
                    host.tell(
                        p.uuid,
                        Text::literal(format!("[quests] {cmd}")),
                    );
                }
                progress::mark_claimed(team, player, quest_id, &reward.id);
                format!("announced /{cmd}")
            } else {
                "command reward empty".into()
            }
        }
        "table" => {
            if let Some(table) = &reward.table {
                if let Some((item, count)) = roll_table(table) {
                    give(host, &item, count);
                    progress::mark_claimed(team, player, quest_id, &reward.id);
                    format!("table {table} -> {item} x{count}")
                } else {
                    format!("empty table {table}")
                }
            } else {
                "table reward missing id".into()
            }
        }
        "choice" => {
            let Some(idx) = progress::choice(team, quest_id) else {
                return "use /quests choose <quest> <index> first".into();
            };
            let Some((item, count)) = reward.options.get(idx as usize).cloned() else {
                return "choice index out of range".into();
            };
            give(host, &item, count);
            progress::mark_claimed(team, player, quest_id, &reward.id);
            format!("chose {item} x{count}")
        }
        "broadcast" => {
            let line = format!("Horizon Quests: team {team} finished {quest_id}");
            for p in host.server_players() {
                host.tell(p.uuid, Text::literal(line.clone()));
            }
            progress::mark_claimed(team, player, quest_id, &reward.id);
            "team broadcast sent".into()
        }
        other => format!("unknown reward type {other}"),
    }
}

pub fn claim_all(host: &mut dyn Host, team: &str, player: u128, quest_id: &str) -> Vec<String> {
    let Some(quest) = file::quest(quest_id) else {
        return vec!["unknown quest".into()];
    };
    if !progress::is_quest_done(team, quest_id) {
        refresh_quest(team, &quest);
    }
    if !progress::is_quest_done(team, quest_id) {
        return vec!["quest not complete".into()];
    }
    quest
        .rewards
        .iter()
        .map(|r| grant_reward(host, team, player, quest_id, r))
        .collect()
}

/// Credit kill tasks when a mob is killed by a player (`mob_killed` hook).
pub fn on_mob_killed(host: &mut dyn Host, player: u128, kind: &str) {
    if let Some(dir) = host.world_dir() {
        progress::bind(dir.clone());
        crate::teams_bridge::refresh(&dir);
    }
    let team = crate::teams_bridge::team_id(player);
    credit_kill_tasks(host, player, &team, kind);
}

/// Credit advancement tasks when vanilla advancement completes.
pub fn on_advancement_done(host: &mut dyn Host, player: u128, advancement: &str) {
    if let Some(dir) = host.world_dir() {
        progress::bind(dir.clone());
        crate::teams_bridge::refresh(&dir);
    }
    let team = crate::teams_bridge::team_id(player);
    let file = file::load();
    for quest in file.quests.values() {
        if !can_progress_tasks(&team, quest) {
            continue;
        }
        for task in &quest.tasks {
            if task.kind != "adv" && task.kind != "advancement" {
                continue;
            }
            if progress::is_task_done(&team, &task.id) {
                continue;
            }
            let want = task.item.as_deref().unwrap_or("");
            let ok = want.is_empty()
                || want == "*"
                || advancement == want
                || advancement.ends_with(want)
                || advancement.contains(want);
            if ok {
                progress::complete_task(&team, &task.id);
                host.tell(
                    player,
                    Text::literal(format!("Quest task done: {} ({advancement})", task.title)),
                );
            }
        }
        refresh_quest(&team, quest);
    }
}

fn credit_kill_tasks(host: &mut dyn Host, uuid: u128, team: &str, kind: &str) {
    let file = file::load();
    for quest in file.quests.values() {
        if !can_progress_tasks(team, quest) {
            continue;
        }
        for task in &quest.tasks {
            if task.kind != "kill" || progress::is_task_done(team, &task.id) {
                continue;
            }
            let want = task.item.as_deref();
            let ok = match want {
                None | Some("") | Some("*") => true,
                Some(id) => kind == id || kind.ends_with(id) || id == "any",
            };
            if ok {
                progress::complete_task(team, &task.id);
                host.tell(
                    uuid,
                    Text::literal(format!("Quest task done: {} ({kind})", task.title)),
                );
            }
        }
        refresh_quest(team, quest);
    }
}

/// Credit kill tasks when a living entity dies to a player attacker (hooks 392).
pub fn on_living_death(host: &mut dyn Host, kind: &str, damage_type: &str, attacker: u32) {
    if attacker == 0 && !damage_type.contains("player") {
        return;
    }
    let killer = host.server_players().into_iter().find(|p| {
        attacker != 0 && p.entity_id == attacker as i32
    });
    let Some(killer) = killer.or_else(|| {
        // SP / edge: player_attack with attacker 0 — credit the acting player if any.
        if damage_type.contains("player") {
            host.acting_player()
        } else {
            None
        }
    }) else {
        return;
    };
    let uuid = killer.uuid;
    if let Some(dir) = host.world_dir() {
        progress::bind(dir.clone());
        crate::teams_bridge::refresh(&dir);
    }
    let team = crate::teams_bridge::team_id(uuid);
    credit_kill_tasks(host, uuid, &team, kind);
}

pub fn tick_item_and_location(host: &mut dyn Host, team: &str, uuid: u128) {
    let file = file::load();
    let Some(player) = host.acting_player() else {
        return;
    };
    if player.uuid != uuid {
        return;
    }
    let pos = [
        player.position[0] as i32,
        player.position[1] as i32,
        player.position[2] as i32,
    ];
    for quest in file.quests.values() {
        if !can_progress_tasks(team, quest) {
            continue;
        }
        for task in &quest.tasks {
            if progress::is_task_done(team, &task.id) {
                continue;
            }
            match task.kind.as_str() {
                "item" | "inventory" => {
                    if let Some(item) = &task.item {
                        if host.count_items(item) >= task.count as u32 {
                            progress::complete_task(team, &task.id);
                            host.tell(
                                uuid,
                                Text::literal(format!("Quest task done: {}", task.title)),
                            );
                        }
                    }
                }
                "location" => {
                    let done = if let Some(block_id) = &task.item {
                        // Scan a cube around the player for the named block (e.g. quest board).
                        let r = task.radius.max(1);
                        let mut found = false;
                        'scan: for dy in -r..=r {
                            for dx in -r..=r {
                                for dz in -r..=r {
                                    let p = [pos[0] + dx, pos[1] + dy, pos[2] + dz];
                                    if host.block(p) == *block_id {
                                        found = true;
                                        break 'scan;
                                    }
                                }
                            }
                        }
                        found
                    } else {
                        let dx = pos[0] - task.x;
                        let dy = pos[1] - task.y;
                        let dz = pos[2] - task.z;
                        dx * dx + dy * dy + dz * dz <= task.radius * task.radius
                    };
                    if done {
                        progress::complete_task(team, &task.id);
                        host.tell(
                            uuid,
                            Text::literal(format!("Quest task done: {}", task.title)),
                        );
                    }
                }
                _ => {}
            }
        }
        refresh_quest(team, quest);
    }
}
