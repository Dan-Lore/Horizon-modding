//! TFC Horizon — TerraFirmaCraft-inspired core (hybrid climate + survival pillars).
mod climate;
mod collapse;
mod machines;
mod prospect;
mod registry;
mod screens;
mod state;
mod worldgen;

use climate::Season;
use horizon_client::mod_api::{
    BlockEntityContainerEvent, BlockEntityEvent, BlockEntityTickEvent, BlockEntityTicksEvent,
    Compound, Corner, Flow, Hooks, Host, HudEvent, ModContainer, NativeScreen, PlayerLoggedInEvent,
    PlayerTickEvent, ScreenDrawEvent, ScreenEvent, Text, UseItemEvent, UseItemOnEvent,
};
use state::{PlayerState, THIRST_DRAIN_EVERY, THIRST_MAX};

pub fn hooks() -> Box<dyn Hooks> {
    Box::new(Tfc)
}

struct Tfc;

impl Hooks for Tfc {
    fn player_logged_in(&self, host: &mut dyn Host, event: &mut PlayerLoggedInEvent<'_>) {
        state::with_player(event.player, |_| {});
        host.tell(
            event.player,
            Text::literal(
                "TFC Horizon 0.1 — climate, thirst, rocks/ores, early metal loop. Not official TFC.",
            ),
        );
    }

    fn player_tick(&self, host: &mut dyn Host, _event: &mut PlayerTickEvent) {
        let Some(p) = host.acting_player() else {
            return;
        };
        let pos = [
            p.position[0].floor() as i32,
            p.position[1].floor() as i32,
            p.position[2].floor() as i32,
        ];
        let (temp, rain) = climate::sample(pos);
        // Day-of-year lite from tick counter stored per player.
        let season = state::with_player(p.uuid, |s| {
            s.ticks = s.ticks.wrapping_add(1);
            s.pos = pos;
            s.last_temp = temp;
            s.last_rain = rain;
            if s.ticks % THIRST_DRAIN_EVERY == 0 {
                s.thirst = (s.thirst - 1).max(0);
            }
            // Nutrients slowly decay (W7).
            if s.ticks % 200 == 0 {
                s.grain = (s.grain - 1).max(0);
                s.fruit = (s.fruit - 1).max(0);
                s.veg = (s.veg - 1).max(0);
                s.protein = (s.protein - 1).max(0);
                s.dairy = (s.dairy - 1).max(0);
            }
            let day = (s.ticks / 24000) as u64;
            let season = climate::season_from_day(day);
            s.last_season = match season {
                Season::Spring => 0,
                Season::Summer => 1,
                Season::Autumn => 2,
                Season::Winter => 3,
            };
            season
        });
        let _ = (season, worldgen::STATUS);
        collapse::check_near_player(host, pos);
    }

    fn hud(&self, host: &mut dyn Host, event: &mut HudEvent<'_>) {
        let Some(p) = host.acting_player() else {
            return;
        };
        let s = state::get(p.uuid);
        let season = match s.last_season {
            0 => Season::Spring,
            1 => Season::Summer,
            2 => Season::Autumn,
            _ => Season::Winter,
        };
        let lines = [
            format!("TFC {}  {:.0}°C  rain {:.0}", season.label(), s.last_temp, s.last_rain),
            format!(
                "Thirst {}/{}  G{} F{} V{} P{} D{}",
                s.thirst, THIRST_MAX, s.grain, s.fruit, s.veg, s.protein, s.dairy
            ),
        ];
        let w = 210.0;
        let h = 24.0;
        let (x, y) = event.corners.place(Corner::TopLeft, w, h);
        host.fill(event.batch, [x, y, w, h], 0x78000000);
        host.text(event.batch, &lines[0], [x + 2.0, y + 2.0], 0xE8E8E8, true);
        host.text(event.batch, &lines[1], [x + 2.0, y + 12.0], 0xA0D0FF, true);
    }

    fn use_item_on(&self, host: &mut dyn Host, event: &mut UseItemOnEvent<'_>) -> Flow {
        let item = event.stack.item.as_str();
        if item == "tfc:prospector_pick" {
            return prospect::use_propick(host, event);
        }
        if item == "tfc:chisel" {
            return prospect::chisel_smooth(host, event);
        }
        if item == "tfc:ceramic_jug" || item == "tfc:ceramic_vessel" {
            // Drink from jug while targeting water / air.
            if let Some(p) = host.acting_player() {
                state::with_player(p.uuid, |s| {
                    s.thirst = THIRST_MAX;
                });
                host.action_bar(p.uuid, Text::literal("You drink. Thirst restored."));
            }
            return Flow::Cancel;
        }
        Flow::Continue
    }

    fn use_item(&self, host: &mut dyn Host, event: &mut UseItemEvent<'_>) -> Flow {
        let item = event.stack.item.as_str();
        if item.starts_with("tfc:food_") {
            if let Some(p) = host.acting_player() {
                state::with_player(p.uuid, |s| {
                    // Generic meal bump; tables refine later.
                    s.grain = (s.grain + 5).min(100);
                    s.fruit = (s.fruit + 5).min(100);
                    s.veg = (s.veg + 5).min(100);
                    s.protein = (s.protein + 5).min(100);
                    s.dairy = (s.dairy + 5).min(100);
                    s.thirst = (s.thirst + 5).min(THIRST_MAX);
                });
                host.action_bar(p.uuid, Text::literal("Nutrients restored."));
            }
            return Flow::Cancel;
        }
        if item == "tfc:pan_empty" || item == "tfc:pan_filled" {
            return prospect::use_pan(host, event);
        }
        if item == "tfc:ceramic_jug" {
            if let Some(p) = host.acting_player() {
                state::with_player(p.uuid, |s| {
                    s.thirst = THIRST_MAX;
                });
                host.action_bar(p.uuid, Text::literal("You drink from the jug."));
            }
            return Flow::Cancel;
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
        let Some(spec) = registry::find(&event.entity.id) else {
            return;
        };
        machines::tick(host, event.pos, event.entity, &spec);
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

// Silence unused in case season cast warnings
#[allow(dead_code)]
fn _player_snapshot(s: &PlayerState) -> (i32, f32) {
    (s.thirst, s.last_temp)
}
