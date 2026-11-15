//! `/team` command surface.

use crate::store;
use horizon_client::mod_api::{Host, NativeCommand, Text};

pub fn usages() -> Vec<NativeCommand> {
    vec![
        NativeCommand::new("team create <name:word>"),
        NativeCommand::new("team invite <player:word>"),
        NativeCommand::new("team join <name:word>"),
        NativeCommand::new("team leave"),
        NativeCommand::new("team kick <player:word>"),
        NativeCommand::new("team info"),
        NativeCommand::new("team invites"),
    ]
}

fn say(host: &mut dyn Host, uuid: u128, line: &str) {
    host.tell(uuid, Text::literal(line));
    host.feedback(Text::literal(line));
}

pub fn perform(host: &mut dyn Host, command: &str) -> bool {
    let mut words = command.split_whitespace();
    if words.next() != Some("team") {
        return false;
    }
    let Some(player) = host.acting_player() else {
        return false;
    };
    let uuid = player.uuid;
    store::remember_player(uuid, &player.name);
    if let Some(dir) = host.world_dir() {
        store::bind_world(dir);
    }

    match words.next() {
        Some("create") => {
            let name = words.collect::<Vec<_>>().join(" ");
            if name.is_empty() {
                say(host, uuid, "/team create <name>");
                return true;
            }
            match store::create(uuid, &name) {
                Ok(team) => say(
                    host,
                    uuid,
                    &format!("created team {} ({})", team.name, team.id),
                ),
                Err(e) => say(host, uuid, e),
            }
        }
        Some("invite") => {
            let Some(who) = words.next() else {
                say(host, uuid, "/team invite <player>");
                return true;
            };
            match store::invite(uuid, who) {
                Ok(inv) => {
                    say(
                        host,
                        uuid,
                        &format!("invited {} to {}", inv.to_name, inv.team_name),
                    );
                    host.tell(
                        inv.to_uuid,
                        Text::literal(format!(
                            "Horizon Teams: invited to {}. /team join {}",
                            inv.team_name, inv.team_name
                        )),
                    );
                }
                Err(e) => say(host, uuid, e),
            }
        }
        Some("join") => {
            let name = words.collect::<Vec<_>>().join(" ");
            if name.is_empty() {
                say(host, uuid, "/team join <name>");
                return true;
            }
            match store::join(uuid, &name) {
                Ok(team) => say(host, uuid, &format!("joined {}", team.name)),
                Err(e) => say(host, uuid, e),
            }
        }
        Some("leave") => match store::leave(uuid) {
            Ok(msg) => {
                let _ = store::ensure_personal(uuid, &player.name);
                say(host, uuid, &format!("{msg}; personal party restored"));
            }
            Err(e) => say(host, uuid, e),
        },
        Some("kick") => {
            let Some(who) = words.next() else {
                say(host, uuid, "/team kick <player>");
                return true;
            };
            match store::kick(uuid, who) {
                Ok(msg) => say(host, uuid, &msg),
                Err(e) => say(host, uuid, e),
            }
        }
        Some("info") => {
            let team = store::ensure_personal(uuid, &player.name);
            let members: Vec<String> = team
                .members
                .iter()
                .map(|m| store::display_name(*m))
                .collect();
            say(
                host,
                uuid,
                &format!(
                    "team {} [{}] owner={} members={}",
                    team.name,
                    team.id,
                    store::display_name(team.owner),
                    members.join(", ")
                ),
            );
        }
        Some("invites") => {
            let list = store::invites_for(uuid);
            if list.is_empty() {
                say(host, uuid, "no pending invites");
            } else {
                for inv in list {
                    say(
                        host,
                        uuid,
                        &format!(
                            "invite: {} (expires unix {}) — /team join {}",
                            inv.team_name, inv.expires_unix, inv.team_name
                        ),
                    );
                }
            }
        }
        _ => say(
            host,
            uuid,
            "/team create|invite|join|leave|kick|info|invites",
        ),
    }
    true
}
