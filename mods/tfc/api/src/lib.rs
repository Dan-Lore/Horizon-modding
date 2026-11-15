//! TFC Horizon 0.1 — climate, thirst, rocks/ores, survival & metal loop.

mod calendar;
mod climate;
mod collapse;
mod machines;
mod nutrition;
mod player_state;
mod prospect;
mod registry;
mod screens;
mod thirst;

use horizon_client::mod_api::{
    BlockEntityContainerEvent, BlockEntityEvent, BlockEntityTickEvent, BlockEntityTicksEvent,
    Compound, Flow, Hooks, Host, ModContainer, NativeScreen, PlayerLoggedInEvent, PlayerTickEvent,
    ScreenDrawEvent, ScreenEvent, Text, UseItemOnEvent,
};
use nutrition::food_nutrient;
use registry::Kind;

pub fn hooks() -> Box<dyn Hooks> {
    Box::new(Tfc)
}

struct Tfc;

impl Hooks for Tfc {
    fn player_logged_in(&self, host: &mut dyn Host, event: &mut PlayerLoggedInEvent<'_>) {
        host.tell(
            event.player,
            Text::literal(
                "TFC Horizon 0.1: climate/thirst HUD on action bar; rocks/ores; early survival & metal. Hybrid worldgen.",
            ),
        );
        player_state::with_player(event.player, |_| {});
    }

    fn player_tick(&self, host: &mut dyn Host, _event: &mut PlayerTickEvent<'_>) {
        let Some(player) = host.acting_player() else {
            return;
        };
        let uuid = player.uuid;
        let pos = player.position;
        let sneaking = player.sneaking;
        // day_time helper may be unavailable; use 0 offset climate + tick clock from state.
        let day_time = 0i64;
        let sample = climate::sample(pos[0], pos[1], pos[2], day_time);

        let (line, should_hud) = player_state::with_player(uuid, |st| {
            st.ticks = st.ticks.saturating_add(1);
            st.thirst.drain(0.05, false);
            if st.ticks % 24000 == 0 {
                st.nutrition.decay_day(0.5);
            }
            let hud = st.ticks.saturating_sub(st.last_hud_tick) >= 40;
            if hud {
                st.last_hud_tick = st.ticks;
            }
            let season = calendar::season_name(day_time.saturating_add(st.ticks as i64));
            let line = format!(
                "TFC {} | {:.0}°C rain {:.0} | thirst {:.0}% | {}",
                season,
                sample.temp_c,
                sample.rainfall,
                st.thirst.value,
                st.nutrition.summary()
            );
            (line, hud)
        });

        if should_hud {
            let _ = host.action_bar(uuid, Text::literal(line.as_str()));
        }

        // Collapse lite: when sneaking with empty hand near unsupported cobble — checked on use instead.
        let _ = sneaking;
    }

    fn use_item_on(&self, host: &mut dyn Host, event: &mut UseItemOnEvent<'_>) -> Flow {
        let Some(player) = host.acting_player() else {
            return Flow::Continue;
        };
        let held = event.stack.item.as_ref();
        let block = host.block(event.pos);

        if held == "tfc:prospectors_pick" {
            let msg = prospect::scan(event.pos, 12, |p| host.block(p))
                .unwrap_or_else(|| "Found nothing nearby".into());
            let _ = host.action_bar(player.uuid, Text::literal(msg));
            return Flow::Cancel;
        }

        if held == "tfc:ceramic_jug"
            || held == "tfc:wooden_bucket"
            || (held == "minecraft:glass_bottle" && block.contains("water"))
        {
            if block.contains("water") || held == "tfc:ceramic_jug" {
                player_state::with_player(player.uuid, |st| {
                    st.thirst.drink(if held == "tfc:ceramic_jug" { 40.0 } else { 25.0 });
                });
                let _ = host.action_bar(player.uuid, Text::literal("You drink. Thirst restored."));
                return Flow::Cancel;
            }
        }

        if let Some((nut, amt)) = food_nutrient(held) {
            player_state::with_player(player.uuid, |st| st.nutrition.add(nut, amt));
            let msg = format!("Ate ({nut})");
            let _ = host.action_bar(player.uuid, Text::literal(msg.as_str()));
            return Flow::Continue;
        }

        if collapse::needs_support(&block) && !collapse::supported(event.pos, 4, |p| host.block(p))
        {
            // Soft signal — full collapse needs set_block Host write; mark via action bar.
            let _ = host.action_bar(
                player.uuid,
                Text::literal("Unstable! Place support beams nearby."),
            );
        }

        Flow::Continue
    }

    fn block_entity(
        &self,
        _host: &mut dyn Host,
        event: &mut BlockEntityEvent<'_>,
    ) -> Option<(String, Compound)> {
        registry::is_ours(event.block).then(|| (event.block.to_owned(), Compound::new()))
    }

    fn block_entity_ticks(&self, _host: &dyn Host, event: &mut BlockEntityTicksEvent<'_>) {
        if registry::is_ours(event.block) {
            event.ticks = true;
        }
    }

    fn block_entity_container(
        &self,
        _host: &dyn Host,
        event: &mut BlockEntityContainerEvent<'_>,
    ) -> Option<ModContainer> {
        registry::find(event.block).and_then(|s| s.container())
    }

    fn block_entity_tick(&self, host: &mut dyn Host, event: &mut BlockEntityTickEvent<'_>) {
        machines::tick_if_ours(host, event.pos, event.entity);
    }

    fn screen(
        &self,
        _host: &dyn Host,
        event: &mut ScreenEvent<'_>,
    ) -> Option<NativeScreen> {
        screens::layout(event)
    }

    fn screen_draw(&self, host: &dyn Host, event: &mut ScreenDrawEvent<'_>) {
        screens::draw(host, event);
    }
}

// Silence unused Kind import in release if only used in screens via registry.
#[allow(dead_code)]
fn _kind_touch(k: Kind) -> Kind {
    k
}
