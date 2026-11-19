//! Greglite 0.5.1 — EU net, LV craft chain, fluids, coke oven, blast furnace, vacuum freezer.
mod energy;
mod eu_rules;
mod fluids;
mod generator;
mod multiblock;
mod net;
mod processor;
mod recipes;
mod registry;
mod screens;

use horizon_client::mod_api::{
    BlockEntityAcceptsFluidEvent, BlockEntityContainerEvent, BlockEntityEvent,
    BlockEntityFluidsEvent, BlockEntityTickEvent, BlockEntityTicksEvent, Compound, Flow, Hooks,
    Host, ModContainer, ModFluidTanks, NativeScreen, PlayerLoggedInEvent, ScreenDrawEvent,
    ScreenEvent, Text,
};
use registry::Kind;

pub fn hooks() -> Box<dyn Hooks> {
    Box::new(Greglite)
}

struct Greglite;

impl Hooks for Greglite {
    fn player_logged_in(&self, host: &mut dyn Host, event: &mut PlayerLoggedInEvent<'_>) {
        host.tell(
            event.player,
            Text::literal(
                "Greglite 0.5.1: EU net, LV craft chain, coke oven, blast furnace, vacuum freezer.",
            ),
        );
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

    fn block_entity_fluids(
        &self,
        _host: &dyn Host,
        event: &mut BlockEntityFluidsEvent<'_>,
    ) -> Option<ModFluidTanks> {
        fluids_for(event.block)
    }

    fn block_entity_accepts_fluid(
        &self,
        _host: &dyn Host,
        event: &mut BlockEntityAcceptsFluidEvent<'_>,
    ) -> Flow {
        if fluid_allowed(event.block, event.tank, event.fluid) {
            Flow::Continue
        } else {
            Flow::Cancel
        }
    }

    fn block_entity_tick(&self, host: &mut dyn Host, event: &mut BlockEntityTickEvent<'_>) {
        let Some(spec) = registry::find(&event.entity.id) else {
            return;
        };
        if spec.id.ends_with("multi_coke_oven") {
            multiblock::tick_coke(host, event.pos, event.entity, &spec);
            return;
        }
        if spec.id.ends_with("multi_electric_blast_furnace") {
            multiblock::tick_ebf(host, event.pos, event.entity, &spec);
            return;
        }
        if spec.id.ends_with("multi_vacuum_freezer") {
            multiblock::tick_freezer(host, event.pos, event.entity, &spec);
            return;
        }
        if spec.id.ends_with("multi_distillation_tower") {
            multiblock::tick_distillation(host, event.pos, event.entity, &spec);
            return;
        }
        if spec.id.ends_with("multi_cracker") {
            multiblock::tick_cracker(host, event.pos, event.entity, &spec);
            return;
        }
        if spec.id.ends_with("multi_large_chemical_reactor") {
            multiblock::tick_lcr(host, event.pos, event.entity, &spec);
            return;
        }
        if spec.id.ends_with("multi_cleanroom") {
            multiblock::tick_cleanroom(host, event.pos, event.entity, &spec);
            return;
        }
        match spec.kind {
            Kind::SteamProcessor | Kind::EuProcessor | Kind::Multiblock => {
                processor::tick(host, event.pos, event.entity, &spec)
            }
            Kind::Diode => net::tick_diode(host, event.pos, event.entity, &spec),
            Kind::Transformer => net::tick_transformer(host, event.pos, event.entity, &spec),
            Kind::Boiler
            | Kind::SteamTurbine
            | Kind::FuelGen
            | Kind::Cable
            | Kind::BatteryBuffer
            | Kind::Hull
            | Kind::EnergyHatch => generator::tick(host, event.pos, event.entity, &spec),
            Kind::ItemHatch => {}
        }
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

fn tank_set(capacities: &[i32], inputs: &[usize], outputs: &[usize]) -> ModFluidTanks {
    let all: Vec<usize> = (0..capacities.len()).collect();
    ModFluidTanks {
        tanks: capacities.to_vec(),
        faces: [
            all.clone(),
            all.clone(),
            all.clone(),
            all.clone(),
            all.clone(),
            all,
        ],
        inputs: inputs.to_vec(),
        outputs: outputs.to_vec(),
    }
}

fn fluids_for(block: &str) -> Option<ModFluidTanks> {
    if !block.starts_with("greglite:") {
        return None;
    }
    if block.contains("boiler") {
        return Some(tank_set(&[16_000, 16_000], &[0], &[1]));
    }
    if block.contains("steam_") {
        return Some(tank_set(&[16_000], &[0], &[]));
    }
    if block.ends_with("_combustion") || block.ends_with("_gas_turbine") {
        return Some(tank_set(&[16_000], &[0], &[]));
    }
    if block.ends_with("_distillery") || block.ends_with("_chemical_reactor") {
        return Some(tank_set(&[16_000, 16_000], &[0], &[1]));
    }
    if block.ends_with("multi_coke_oven") {
        return Some(tank_set(&[16_000], &[], &[0]));
    }
    None
}

fn fluid_allowed(block: &str, tank: usize, fluid: &str) -> bool {
    if fluids_for(block).is_none() {
        return false;
    }
    if block.contains("boiler") {
        return (tank == 0 && fluid == fluids::WATER) || (tank == 1 && fluid == fluids::STEAM);
    }
    if block.contains("steam_") {
        return fluid == fluids::STEAM;
    }
    if block.ends_with("_combustion") {
        return fluid == fluids::LAVA || fluid == fluids::DIESEL;
    }
    if block.ends_with("_gas_turbine") {
        return fluid == fluids::BIOGAS;
    }
    if block.ends_with("_distillery") {
        return (tank == 0 && fluid == fluids::WATER)
            || (tank == 1 && fluid == fluids::DISTILLED);
    }
    if block.ends_with("_chemical_reactor") {
        return (tank == 0 && fluid == fluids::WATER) || (tank == 1 && fluid == fluids::CREOSOTE);
    }
    if block.ends_with("multi_coke_oven") {
        return fluid == fluids::CREOSOTE;
    }
    true
}
