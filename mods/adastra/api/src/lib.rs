//! Ad Astra Horizon 0.1.0 — overworld materials, FE machines, oxygen, rocket stub.
//! Custom dimensions stay blocked. See `docs/adastra-plan.md`.

mod energy;
mod machines;
mod net;
mod oxygen;
mod player_state;
mod recipes;
mod registry;
mod screens;

use horizon_client::mod_api::{
    BlockEntityContainerEvent, BlockEntityEvent, BlockEntityTickEvent, BlockEntityTicksEvent,
    Compound, Flow, Hooks, Host, LivingEntityUseItemFinishEvent, ModContainer, NativeScreen,
    PlayerLoggedInEvent, PlayerTickEvent, ScreenDrawEvent, ScreenEvent, Text, UseDurationEvent,
    UseItemEvent, UseItemOnEvent,
};
use registry::Kind;

pub fn hooks() -> Box<dyn Hooks> {
    Box::new(AdAstra)
}

struct AdAstra;

impl Hooks for AdAstra {
    fn player_logged_in(&self, host: &mut dyn Host, event: &mut PlayerLoggedInEvent<'_>) {
        host.tell(
            event.player,
            Text::literal(
                "Ad Astra Horizon 0.1.0: materials, FE machines, oxygen, rocket stub. Dimensions blocked.",
            ),
        );
    }

    fn player_tick(&self, host: &mut dyn Host, _event: &mut PlayerTickEvent) {
        let Some(player) = host.acting_player() else {
            return;
        };
        let uuid = player.uuid;
        let origin = [
            player.position[0] as i32,
            player.position[1] as i32,
            player.position[2] as i32,
        ];
        let (mut state, refresh) = player_state::tick(uuid);

        // Rocket launch stub countdown.
        let phase = player_state::launch_phase(uuid);
        if phase == 80 {
            host.tell(uuid, Text::literal("Ad Astra: T-4 launch sequence…"));
        } else if phase == 40 {
            host.tell(uuid, Text::literal("Ad Astra: engines throttle up…"));
        } else if phase == 0 {
            host.tell(
                uuid,
                Text::literal(
                    "Ad Astra: launch stub complete. Dimensions blocked on hooks 411 — no planet hop.",
                ),
            );
            player_state::clear_launch(uuid);
        }

        let vacuum = oxygen::in_vacuum(host, origin);
        let safe = oxygen::in_distributor_bubble(host, origin);
        if vacuum && !safe {
            if state.sealed() && state.oxygen > 0.0 {
                state = player_state::drain_oxygen(uuid, 0.5);
            } else if player_state::should_vacuum_warn(uuid) {
                host.tell(
                    uuid,
                    Text::literal(
                        "Ad Astra: vacuum damage! Don a full suit with oxygen, or stand in a distributor bubble.",
                    ),
                );
            }
        }

        if !refresh {
            return;
        }
        let gravity = oxygen::foot_gravity(host, origin);
        let line = player_state::hud_line(&state, gravity, vacuum, safe);
        host.action_bar(uuid, Text::literal(line));
    }

    fn use_duration(&self, _host: &dyn Host, event: &mut UseDurationEvent<'_>) {
        let id = event.stack.item.as_ref();
        if oxygen::is_suit_piece(id) || oxygen::is_oxygen_tank(id) || oxygen::is_rocket(id) {
            event.duration = 24;
        }
    }

    fn living_entity_use_item_finish(
        &self,
        host: &mut dyn Host,
        event: &mut LivingEntityUseItemFinishEvent<'_, '_>,
    ) {
        let id = event.stack.item.as_ref().to_owned();
        let count = event.stack.count;
        let Some(player) = host.acting_player() else {
            return;
        };
        if let Some(msg) = player_state::don_piece(player.uuid, &id) {
            host.tell(player.uuid, Text::literal(msg));
            return;
        }
        if oxygen::is_oxygen_tank(&id) {
            player_state::refill_oxygen(player.uuid, 50.0);
            host.tell(
                player.uuid,
                Text::literal("Ad Astra: oxygen tank applied (+50 O2)."),
            );
            *event.result = if count <= 1 {
                Some(recipes::stack("adastra:oxygen_tank_empty", 1))
            } else {
                Some(recipes::stack(&id, count - 1))
            };
            return;
        }
        if oxygen::is_rocket(&id) {
            player_state::start_launch(player.uuid);
            host.tell(
                player.uuid,
                Text::literal("Ad Astra: launch stub armed (use near a launch pad)."),
            );
        }
    }

    fn use_item(&self, host: &mut dyn Host, event: &mut UseItemEvent<'_>) -> Flow {
        let id = event.stack.item.as_ref();
        if oxygen::is_rocket(id) {
            let Some(player) = host.acting_player() else {
                return Flow::Cancel;
            };
            player_state::start_launch(player.uuid);
            host.tell(
                player.uuid,
                Text::literal("Ad Astra: T-5… launch stub started. Dimensions blocked."),
            );
            return Flow::Cancel;
        }
        if oxygen::is_suit_piece(id) {
            let Some(player) = host.acting_player() else {
                return Flow::Cancel;
            };
            if let Some(msg) = player_state::don_piece(player.uuid, id) {
                host.tell(player.uuid, Text::literal(msg));
            }
            return Flow::Cancel;
        }
        Flow::Continue
    }

    fn use_item_on(&self, host: &mut dyn Host, event: &mut UseItemOnEvent<'_>) -> Flow {
        let block = host.block(event.pos);
        if block == "adastra:launch_pad" {
            let Some(player) = host.acting_player() else {
                return Flow::Continue;
            };
            if oxygen::is_rocket(event.stack.item.as_ref()) {
                player_state::start_launch(player.uuid);
                host.tell(
                    player.uuid,
                    Text::literal("Ad Astra: pad locked. Launch stub countdown…"),
                );
                return Flow::Cancel;
            }
            host.tell(
                player.uuid,
                Text::literal("Ad Astra: place or use a Tier-1 rocket on the launch pad."),
            );
            return Flow::Cancel;
        }
        Flow::Continue
    }

    fn block_entity(
        &self,
        _host: &mut dyn Host,
        event: &mut BlockEntityEvent<'_>,
    ) -> Option<(String, Compound)> {
        registry::find(event.block).map(|spec| (spec.id.to_owned(), Compound::new()))
    }

    fn block_entity_ticks(&self, _host: &dyn Host, event: &mut BlockEntityTicksEvent<'_>) {
        if registry::find(event.block).is_some() {
            event.ticks = true;
        }
    }

    fn block_entity_container(
        &self,
        _host: &dyn Host,
        event: &mut BlockEntityContainerEvent<'_>,
    ) -> Option<ModContainer> {
        registry::find(event.block).and_then(|spec| spec.container(event.block))
    }

    fn block_entity_tick(&self, host: &mut dyn Host, event: &mut BlockEntityTickEvent<'_>) {
        let Some(spec) = registry::find(&event.entity.id) else {
            return;
        };
        match spec.kind {
            Kind::Storage | Kind::Vacuum | Kind::Marker => {}
            _ => machines::tick(host, event.pos, event.entity, &spec),
        }
    }

    fn screen(&self, _host: &dyn Host, event: &mut ScreenEvent<'_>) -> Option<NativeScreen> {
        screens::layout(event)
    }

    fn screen_draw(&self, host: &dyn Host, event: &mut ScreenDrawEvent<'_>) {
        screens::draw(host, event);
    }
}
