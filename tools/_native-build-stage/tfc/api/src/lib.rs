// TFC Horizon 0.2.0 — heat, alloys, anvil steps, knapping, and container rot.
// Animals stay deferred. Full worldgen stays blocked. See docs/tfc-plan.md.

mod animals;
mod anvil;
mod climate;
mod collapse;
mod crops;
mod crucible;
mod food;
mod heat;
mod knapping;
mod machines;
mod player_state;
mod prospect;
mod recipes;
mod registry;
mod rot;
mod screens;
mod worldgen;

use horizon_client::mod_api::{
    BlockEntityContainerEvent, BlockEntityEvent, BlockEntityTickEvent, BlockEntityTicksEvent,
    CanEatEvent, Compound, DestroyBlockEvent, Flow, Hooks, Host, LivingEntityUseItemFinishEvent,
    ModContainer, NativeScreen, PlayerLoggedInEvent, PlayerTickEvent, ScreenDrawEvent,
    ScreenEvent, Text, TooltipEvent, UseDurationEvent, UseItemEvent, UseItemOnEvent,
};
use registry::Kind;

pub fn hooks() -> Box<dyn Hooks> {
    Box::new(Tfc)
}

struct Tfc;

impl Hooks for Tfc {
    fn player_logged_in(&self, host: &mut dyn Host, event: &mut PlayerLoggedInEvent<'_>) {
        let _ = (animals::STATUS, worldgen::STATUS, animals::ids().len());
        host.tell(
            event.player,
            Text::literal(
                "TerraFirmaCraft 0.2.0 (Horizon rewrite): heat, crucible, anvil, knapping, rot. Animals/worldgen blocked.",
            ),
        );
    }

    fn player_tick(&self, host: &mut dyn Host, _event: &mut PlayerTickEvent) {
        let Some(player) = host.acting_player() else {
            return;
        };
        let (state, refresh) = player_state::tick(player.uuid);
        if state.thirst <= 0.0 && state.ticks % 200 == 0 {
            host.tell(
                player.uuid,
                Text::literal("TFC: you are thirsty. Drink from a jug or wooden bucket."),
            );
        }
        if !refresh {
            return;
        }
        let day = host.day_time() / 24_000;
        let sample = climate::sample(
            day,
            player.position[0] as i32,
            player.position[2] as i32,
        );
        let line = climate::hud_line(
            &sample,
            state.thirst,
            &player_state::nutrition_line(&state),
        );
        host.action_bar(player.uuid, Text::literal(line));
    }

    fn tooltip(&self, _host: &dyn Host, event: &mut TooltipEvent<'_>) {
        let Some(line) = food::tooltip_line(event.stack.item.as_ref()) else {
            return;
        };
        event.lines.push((Text::literal(line), 0xFF_C8_C8_C8));
    }

    fn can_eat(&self, _host: &dyn Host, event: &mut CanEatEvent<'_>) {
        if food::is_edible(event.stack.item.as_ref()) {
            event.can_eat = true;
        }
    }

    fn use_duration(&self, _host: &dyn Host, event: &mut UseDurationEvent<'_>) {
        if food::is_edible(event.stack.item.as_ref()) {
            event.duration = 32;
        }
    }

    fn living_entity_use_item_finish(
        &self,
        host: &mut dyn Host,
        event: &mut LivingEntityUseItemFinishEvent<'_>,
    ) {
        let id = event.stack.item.as_ref().to_owned();
        let count = event.stack.count;
        let Some(player) = host.acting_player() else {
            return;
        };
        if let Some((grain, fruit, veg, protein, dairy)) = food::nutrients(&id) {
            player_state::eat(player.uuid, grain, fruit, veg, protein, dairy);
            *event.result = if count <= 1 {
                None
            } else {
                Some(recipes::stack(&id, count - 1))
            };
        } else if food::is_drink(&id) {
            player_state::drink(player.uuid, 0.4);
        }
    }

    fn use_item(&self, host: &mut dyn Host, event: &mut UseItemEvent<'_>) -> Flow {
        let id = event.stack.item.as_ref();
        if !prospect::is_propick(id) {
            return Flow::Continue;
        }
        let Some(player) = host.acting_player() else {
            return Flow::Cancel;
        };
        let origin = [
            player.position[0] as i32,
            player.position[1] as i32,
            player.position[2] as i32,
        ];
        host.tell(player.uuid, Text::literal(prospect::scan(|pos| host.block(pos), origin)));
        Flow::Cancel
    }

    fn use_item_on(&self, host: &mut dyn Host, event: &mut UseItemOnEvent<'_>) -> Flow {
        let Some(player) = host.acting_player() else {
            return Flow::Continue;
        };
        let block = host.block(event.pos);
        let id = event.stack.item.as_ref();
        if block == "tfc:anvil" && prospect::is_hammer(id) {
            let sneaking = player.sneaking;
            let pos = event.pos;
            let mut message = String::from("TFC: anvil is not ready.");
            let _changed = host.change_mod_block_entity(pos, &mut |entity| {
                message = anvil::strike(entity, sneaking);
            });
            host.tell(player.uuid, Text::literal(message));
            return Flow::Cancel;
        }
        if block == "tfc:powderkeg" {
            host.tell(
                player.uuid,
                Text::literal(
                    "TFC: powderkeg fuse blocked (#1) — Host has no explode/schedule_block_tick on hooks 411 (only destroy_block / set_block_property).",
                ),
            );
            return Flow::Cancel;
        }
        if prospect::is_propick(id) {
            host.tell(
                player.uuid,
                Text::literal(prospect::scan(|pos| host.block(pos), event.pos)),
            );
            return Flow::Cancel;
        }
        if prospect::is_chisel(id) && collapse::is_rock(&block) {
            host.tell(
                player.uuid,
                Text::literal("TFC: chisel mark recorded. Block state is unchanged on hooks 411."),
            );
            return Flow::Cancel;
        }
        if prospect::is_pan(id) {
            // Pan over gravel/sand/water → ore deposit for the sluice loop.
            let pannable = block.contains("gravel")
                || block.contains("sand")
                || block == "minecraft:water"
                || block.ends_with("_gravel");
            if !pannable {
                host.tell(
                    player.uuid,
                    Text::literal("TFC: use the pan on gravel, sand, or water."),
                );
                return Flow::Cancel;
            }
            let _ = host.give_items("tfc:ore_deposit", 1);
            host.tell(
                player.uuid,
                Text::literal("TFC: panned an ore deposit — put it in a sluice."),
            );
            return Flow::Cancel;
        }
        Flow::Continue
    }

    fn destroy_block(&self, host: &mut dyn Host, event: &mut DestroyBlockEvent) -> Flow {
        let here = host.block(event.pos);
        if !collapse::is_rock(&here) {
            return Flow::Continue;
        }
        let above = [event.pos[0], event.pos[1] + 1, event.pos[2]];
        let up = host.block(above);
        if collapse::is_rock(&up) && !collapse::supported(|pos| host.block(pos), above) {
            if let Some(player) = host.acting_player() {
                host.tell(player.uuid, Text::literal(collapse::WARNING));
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
        registry::find(event.block).and_then(|spec| spec.container(event.block))
    }

    fn block_entity_tick(&self, host: &mut dyn Host, event: &mut BlockEntityTickEvent<'_>) {
        let Some(spec) = registry::find(&event.entity.id) else {
            return;
        };
        match spec.kind {
            Kind::Machine => machines::tick(host, event.entity, &spec),
            Kind::Crop => crops::tick(host, event.pos, event.entity),
            Kind::Storage if event.entity.id == "tfc:small_vessel" => rot::tick_all(event.entity),
            Kind::Storage => {}
        }
    }

    fn screen(&self, _host: &dyn Host, event: &mut ScreenEvent<'_>) -> Option<NativeScreen> {
        screens::layout(event)
    }

    fn screen_draw(&self, host: &dyn Host, event: &mut ScreenDrawEvent<'_>) {
        screens::draw(host, event);
    }
}
