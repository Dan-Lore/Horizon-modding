//! Horizon Quests 0.1.0 — FTB Quests–inspired quest book.

mod baked;
mod board;
mod commands;
mod file;
mod logic;
mod progress;
mod teams_bridge;

use horizon_client::mod_api::{
    BlockEntityContainerEvent, BlockEntityEvent, BlockEntityTicksEvent, Compound, Flow, Hooks,
    Host, ModContainer, NativeScreen, PerformCommandEvent, PlayerLoggedInEvent, PlayerTickEvent,
    RegisterCommandsEvent, ScreenEvent, Text, UseItemEvent, UseItemOnEvent,
};
use std::sync::atomic::{AtomicU32, Ordering};

static TICK: AtomicU32 = AtomicU32::new(0);

pub fn hooks() -> Box<dyn Hooks> {
    Box::new(Quests)
}

struct Quests;

impl Hooks for Quests {
    fn player_logged_in(&self, host: &mut dyn Host, event: &mut PlayerLoggedInEvent<'_>) {
        if let Some(dir) = host.world_dir() {
            progress::bind(dir.clone());
            teams_bridge::refresh(&dir);
            let _ = file::reload(Some(dir));
        }
        let (chapters, quests) = file::counts();
        host.tell(
            event.player,
            Text::literal(format!(
                "Horizon Quests 0.1.0: {chapters} chapters, {quests} quests. /quests book — requires Horizon Teams."
            )),
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

    fn player_tick(&self, host: &mut dyn Host, _event: &mut PlayerTickEvent) {
        let n = TICK.fetch_add(1, Ordering::Relaxed);
        if n % 40 != 0 {
            return;
        }
        let Some(player) = host.acting_player() else {
            return;
        };
        if let Some(dir) = host.world_dir() {
            progress::bind(dir.clone());
            teams_bridge::refresh(&dir);
        }
        let team = teams_bridge::team_id(player.uuid);
        logic::tick_item_and_location(host, &team, player.uuid);
    }

    fn use_item(&self, host: &mut dyn Host, event: &mut UseItemEvent<'_>) -> Flow {
        let id = event.stack.item.as_ref();
        if id == "quests:quest_book" {
            commands::show_book(host);
            return Flow::Cancel;
        }
        if id == "quests:loot_crate" {
            let Some(player) = host.acting_player() else {
                return Flow::Cancel;
            };
            if let Some(dir) = host.world_dir() {
                progress::bind(dir.clone());
                teams_bridge::refresh(&dir);
            }
            if let Some((item, count)) = logic::roll_table("starter_crate") {
                let _ = host.take_items("quests:loot_crate", 1);
                let _ = host.give_items(&item, count as u32);
                host.tell(
                    player.uuid,
                    Text::literal(format!("Loot crate: {item} x{count}")),
                );
            } else {
                host.tell(player.uuid, Text::literal("Loot crate table empty"));
            }
            return Flow::Cancel;
        }
        Flow::Continue
    }

    fn use_item_on(&self, host: &mut dyn Host, event: &mut UseItemOnEvent<'_>) -> Flow {
        let block = host.block(event.pos);
        if !board::is_board(&block) {
            return Flow::Continue;
        }
        let Some(player) = host.acting_player() else {
            return Flow::Continue;
        };
        if let Some(dir) = host.world_dir() {
            progress::bind(dir.clone());
            teams_bridge::refresh(&dir);
        }
        let team = teams_bridge::team_id(player.uuid);
        logic::tick_item_and_location(host, &team, player.uuid);
        host.tell(
            player.uuid,
            Text::literal("Quest board: checking item tasks; /quests book for the list."),
        );
        Flow::Continue
    }

    fn block_entity(
        &self,
        _host: &mut dyn Host,
        event: &mut BlockEntityEvent<'_>,
    ) -> Option<(String, Compound)> {
        board::is_board(event.block).then(|| (event.block.to_owned(), Compound::new()))
    }

    fn block_entity_ticks(&self, _host: &dyn Host, event: &mut BlockEntityTicksEvent<'_>) {
        if board::is_board(event.block) {
            event.ticks = true;
        }
    }

    fn block_entity_container(
        &self,
        _host: &dyn Host,
        event: &mut BlockEntityContainerEvent<'_>,
    ) -> Option<ModContainer> {
        board::is_board(event.block).then(board::container)
    }

    fn screen(&self, _host: &dyn Host, event: &mut ScreenEvent<'_>) -> Option<NativeScreen> {
        board::layout(event)
    }
}
