//! TFC Horizon 0.1 — climate, thirst, rocks/ores, survival pillars.
mod climate;
mod collapse;
mod food;
mod machines;
mod player_state;
mod prospect;
mod recipes;
mod registry;
mod screens;

use climate::ClimateSample;
use horizon_client::mod_api::{
    BlockEntityContainerEvent, BlockEntityEvent, BlockEntityTickEvent, BlockEntityTicksEvent,
    Compound, Flow, Hooks, Host, ModContainer, NativeScreen, PlayerLoggedInEvent, PlayerTickEvent,
    ScreenDrawEvent, ScreenEvent, Text, UseItemOnEvent,
};
use std::sync::Mutex;

pub fn hooks() -> Box<dyn Hooks> {
    Box::new(Tfc)
}

struct Tfc;

/// Absolute day counter (approx) from host day_time when available.
static DAY_CACHE: Mutex<i64> = Mutex::new(0);

fn absolute_day(host: &dyn Host) -> i64 {
    // Prefer host.day_time() / clock helpers when the linked Horizon exposes them.
    let mut guard = DAY_CACHE.lock().unwrap_or_else(|e| e.into_inner());
    *guard = guard.saturating_add(1);
    let _ = host;
    *guard / 24000
}

fn player_pos(host: &dyn Host) -> (i32, i32) {
    if let Some(p) = host.acting_player() {
        return (p.position[0] as i32, p.position[2] as i32);
    }
    (0, 0)
}

fn refresh_hud(host: &mut dyn Host, uuid: u128, sample: &ClimateSample, thirst: f32) {
    let line = climate::hud_line(sample, thirst);
    let _ = host.action_bar(uuid, Text::literal(line));
}

impl Hooks for Tfc {
    fn player_logged_in(&self, host: &mut dyn Host, event: &mut PlayerLoggedInEvent<'_>) {
        let st = player_state::ensure(event.player);
        let (x, z) = player_pos(host);
        let sample = climate::sample(absolute_day(host), x, z);
        host.tell(
            event.player,
            Text::literal(
                "TFC Horizon 0.1: thin climate + thirst + rock/ore slice. Drink with vessel on water; propick to prospect.",
            ),
        );
        refresh_hud(host, event.player, &sample, st.thirst);
        let nut = player_state::nutrition_line(&st);
        host.tell(event.player, Text::literal(nut));
    }

    fn player_tick(&self, host: &mut dyn Host, _event: &mut PlayerTickEvent<'_>) {
        // API 31: helpers read the ticking player (acting_player).
        let Some(player) = host.acting_player() else {
            return;
        };
        let uuid = player.uuid;
        let (st, refresh) = player_state::tick(uuid);
        if !refresh {
            return;
        }
        let (x, z) = (player.position[0] as i32, player.position[2] as i32);
        let sample = climate::sample(absolute_day(host), x, z);
        refresh_hud(host, uuid, &sample, st.thirst);
        if st.thirst <= 0.05 {
            let _ = host.action_bar(uuid, Text::literal("You are thirsty! Drink water with a vessel."));
        }
    }

    fn use_item_on(&self, host: &mut dyn Host, event: &mut UseItemOnEvent<'_>) -> Flow {
        let Some(player) = host.acting_player() else {
            return Flow::Continue;
        };
        let uuid = player.uuid;
        let stack_id = event.stack.item.as_ref();
        let block = host.block(event.pos);

        // Drink: vessel / jug / wooden bucket on water.
        if matches!(stack_id, "tfc:vessel" | "tfc:jug" | "tfc:wooden_bucket")
            && (block.contains("water") || block == "minecraft:water" || block == "minecraft:kelp")
        {
            let st = player_state::drink(uuid, 0.35);
            host.tell(uuid, Text::literal("You drink. Thirst restored."));
            let (x, z) = (player.position[0] as i32, player.position[2] as i32);
            let sample = climate::sample(absolute_day(host), x, z);
            refresh_hud(host, uuid, &sample, st.thirst);
            return Flow::Cancel;
        }

        // Eat TFC foods (right-click air/block).
        if let Some(food) = food::find(stack_id) {
            let st = player_state::eat(
                uuid,
                food.grain,
                food.fruit,
                food.veg,
                food.protein,
                food.dairy,
            );
            host.tell(uuid, Text::literal(player_state::nutrition_line(&st)));
            return Flow::Continue;
        }

        // Prospector lite.
        if prospect::is_propick(stack_id) {
            let mut found = None;
            let r = prospect::RADIUS;
            'scan: for dx in -r..=r {
                for dy in -r..=r {
                    for dz in -r..=r {
                        let pos = [
                            event.pos[0] + dx,
                            event.pos[1] + dy,
                            event.pos[2] + dz,
                        ];
                        let b = host.block(pos);
                        for ore in prospect::ORES {
                            if b == ore.block {
                                found = Some(ore.name);
                                break 'scan;
                            }
                        }
                    }
                }
            }
            let msg = match found {
                Some(name) => format!("Found traces of {name} nearby."),
                None => "No ores nearby.".to_owned(),
            };
            host.tell(uuid, Text::literal(msg));
            return Flow::Cancel;
        }

        // Collapse lite: breaking unsupported cobble via... we only warn on use for now.
        if collapse::is_collapsible(&block) {
            let mut supported = false;
            let r = collapse::SUPPORT_RANGE;
            for dx in -r..=r {
                for dy in 0..=r {
                    for dz in -r..=r {
                        let pos = [
                            event.pos[0] + dx,
                            event.pos[1] + dy,
                            event.pos[2] + dz,
                        ];
                        if collapse::is_support(&host.block(pos)) {
                            supported = true;
                        }
                    }
                }
            }
            if !supported {
                let _ = host.action_bar(
                    uuid,
                    Text::literal("Unstable! Place a support beam nearby."),
                );
            }
        }

        // Crop climate gate tip when using seeds.
        if stack_id.ends_with("_seeds") && stack_id.starts_with("tfc:") {
            let (x, z) = (player.position[0] as i32, player.position[2] as i32);
            let sample = climate::sample(absolute_day(host), x, z);
            let ok = climate::crop_allowed(&sample, 0.0, 35.0, &["spring", "summer"]);
            if !ok {
                host.tell(
                    uuid,
                    Text::literal("Climate unsuitable for this crop right now."),
                );
                return Flow::Cancel;
            }
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
