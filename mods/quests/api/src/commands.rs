//! `/quests` command surface.

use crate::file;
use crate::logic;
use crate::progress;
use crate::teams_bridge;
use horizon_client::mod_api::{Host, NativeCommand, Text};

pub fn usages() -> Vec<NativeCommand> {
    vec![
        NativeCommand::new("quests book"),
        NativeCommand::new("quests check"),
        NativeCommand::new("quests claim <quest:word>"),
        NativeCommand::new("quests choose <quest:word> <index:integer>"),
        NativeCommand::new("quests progress"),
        NativeCommand::op("quests reload", 2),
        NativeCommand::new("quests theme <id:word>"),
        NativeCommand::op("quests edit title <quest:word> <text:text>", 2),
        NativeCommand::new("quests kill <task:word>"),
        NativeCommand::new("quests adv <task:word>"),
    ]
}

fn say(host: &mut dyn Host, uuid: u128, line: &str) {
    host.tell(uuid, Text::literal(line));
    host.feedback(Text::literal(line));
}

fn bind(host: &mut dyn Host) -> Option<std::path::PathBuf> {
    let dir = host.world_dir()?;
    progress::bind(dir.clone());
    teams_bridge::refresh(&dir);
    Some(dir)
}

fn team_of(host: &mut dyn Host) -> Option<(u128, String)> {
    let player = host.acting_player()?;
    let _ = bind(host);
    let team = teams_bridge::team_id(player.uuid);
    Some((player.uuid, team))
}

pub fn show_book(host: &mut dyn Host) {
    let Some((uuid, team)) = team_of(host) else {
        return;
    };
    let accent = file::accent(&progress::theme());
    let file = file::load();
    say(
        host,
        uuid,
        &format!("{accent}Horizon Quests — theme {}§r", progress::theme()),
    );
    for ch in &file.chapters {
        say(host, uuid, &format!("{accent}# {}§r [{}]", ch.title, ch.id));
        for qid in &ch.quests {
            let Some(q) = file.quests.get(qid) else {
                continue;
            };
            let status = if progress::is_quest_done(&team, qid) {
                "done"
            } else if logic::deps_met(&team, q) {
                "available"
            } else {
                "locked"
            };
            say(host, uuid, &format!("  - {} ({status})", q.title));
            for t in &q.tasks {
                let mark = if progress::is_task_done(&team, &t.id) {
                    "[x]"
                } else {
                    "[ ]"
                };
                say(host, uuid, &format!("      {mark} {} ({})", t.title, t.kind));
            }
        }
    }
    say(
        host,
        uuid,
        "/quests check | claim <id> | choose <id> <n> | progress | theme <id>",
    );
}

pub fn perform(host: &mut dyn Host, command: &str) -> bool {
    let mut words = command.split_whitespace();
    if words.next() != Some("quests") {
        return false;
    }
    let Some(player) = host.acting_player() else {
        return false;
    };
    let uuid = player.uuid;
    let world = bind(host);
    let team = teams_bridge::team_id(uuid);

    match words.next() {
        Some("book") => show_book(host),
        Some("check") => {
            let file = file::load();
            let mut n = 0;
            for quest in file.quests.values() {
                if !logic::can_progress_tasks(&team, quest) {
                    continue;
                }
                for task in &quest.tasks {
                    if task.kind == "checkmark" && !progress::is_task_done(&team, &task.id) {
                        progress::complete_task(&team, &task.id);
                        n += 1;
                    }
                }
                logic::refresh_quest(&team, quest);
            }
            say(host, uuid, &format!("completed {n} checkmark task(s)"));
        }
        Some("claim") => {
            let Some(qid) = words.next() else {
                say(host, uuid, "/quests claim <quest>");
                return true;
            };
            for line in logic::claim_all(host, &team, uuid, qid) {
                say(host, uuid, &line);
            }
        }
        Some("choose") => {
            let Some(qid) = words.next() else {
                say(host, uuid, "/quests choose <quest> <index>");
                return true;
            };
            let Some(idx) = words.next().and_then(|s| s.parse().ok()) else {
                say(host, uuid, "/quests choose <quest> <index>");
                return true;
            };
            progress::set_choice(&team, qid, idx);
            say(host, uuid, &format!("chose option {idx} for {qid}"));
        }
        Some("progress") => {
            let snap = progress::snapshot(&team);
            say(
                host,
                uuid,
                &format!(
                    "team {team}: {} quests done, {} tasks done, theme {}",
                    snap.completed_quests.len(),
                    snap.completed_tasks.len(),
                    progress::theme()
                ),
            );
        }
        Some("reload") => {
            let file = file::reload(world.clone());
            say(
                host,
                uuid,
                &format!(
                    "reloaded {} chapters, {} quests",
                    file.chapters.len(),
                    file.quests.len()
                ),
            );
        }
        Some("theme") => {
            let Some(id) = words.next() else {
                say(host, uuid, "/quests theme <id>");
                return true;
            };
            progress::set_theme(id);
            say(host, uuid, &format!("theme set to {id}"));
        }
        Some("edit") => {
            if words.next() != Some("title") {
                say(host, uuid, "/quests edit title <quest> <text…>");
                return true;
            }
            let Some(qid) = words.next() else {
                say(host, uuid, "/quests edit title <quest> <text…>");
                return true;
            };
            let title = words.collect::<Vec<_>>().join(" ");
            if title.is_empty() {
                say(host, uuid, "title empty");
                return true;
            }
            if let Some(dir) = world {
                file::set_title_override(dir, qid, &title);
                say(host, uuid, &format!("title override for {qid}: {title}"));
            } else {
                say(host, uuid, "no world dir");
            }
        }
        Some("kill") | Some("adv") => {
            let Some(task) = words.next() else {
                say(host, uuid, "need task id");
                return true;
            };
            progress::complete_task(&team, task);
            say(host, uuid, &format!("stub completed task {task}"));
            let file = file::load();
            for quest in file.quests.values() {
                logic::refresh_quest(&team, quest);
            }
        }
        _ => say(
            host,
            uuid,
            "/quests book|check|claim|choose|progress|theme|reload|edit|kill|adv",
        ),
    }
    true
}
