//! Horizon Teams 0.1.0 — FTB Teams–inspired parties.

mod commands;
mod store;

use horizon_client::mod_api::{
    Flow, Hooks, Host, PerformCommandEvent, PlayerLoggedInEvent, RegisterCommandsEvent, Text,
};

pub fn hooks() -> Box<dyn Hooks> {
    Box::new(Teams)
}

struct Teams;

impl Hooks for Teams {
    fn player_logged_in(&self, host: &mut dyn Host, event: &mut PlayerLoggedInEvent<'_>) {
        if let Some(dir) = host.world_dir() {
            store::bind_world(dir);
        }
        store::remember_player(event.player, event.name);
        let _ = store::ensure_personal(event.player, event.name);
        host.tell(
            event.player,
            Text::literal(
                "Horizon Teams 0.1.0: /team create|invite|join|leave|kick|info|invites",
            ),
        );
    }

    fn register_commands(&self, _host: &mut dyn Host, event: &mut RegisterCommandsEvent<'_>) {
        event.commands.extend(commands::usages());
    }

    fn perform_command(&self, host: &mut dyn Host, event: &mut PerformCommandEvent<'_>) -> Flow {
        if commands::perform(host, event.command) {
            Flow::Cancel
        } else {
            Flow::Continue
        }
    }
}
