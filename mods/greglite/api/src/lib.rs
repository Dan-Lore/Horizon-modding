//! Greglite 0.4 — GTM-oriented Steam + Electric Age (dynamic registry).
mod energy;
mod generator;
mod net;
mod processor;
mod recipes;
mod registry;
mod screens;

use horizon_client::mod_api::{
    BlockEntityContainerEvent, BlockEntityEvent, BlockEntityTickEvent, BlockEntityTicksEvent,
    Compound, Hooks, Host, ModContainer, NativeScreen, PlayerLoggedInEvent, ScreenDrawEvent,
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
                "Greglite 0.4 GTM parity: steam + LV–UV machines, cables, materials, multiblock controllers.",
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

    fn block_entity_tick(&self, host: &mut dyn Host, event: &mut BlockEntityTickEvent<'_>) {
        let Some(spec) = registry::find(&event.entity.id) else {
            return;
        };
        match spec.kind {
            Kind::SteamProcessor | Kind::EuProcessor | Kind::Multiblock => {
                processor::tick(host, event.pos, event.entity, &spec)
            }
            Kind::Boiler
            | Kind::SteamTurbine
            | Kind::FuelGen
            | Kind::Cable
            | Kind::BatteryBuffer
            | Kind::Hull => generator::tick(host, event.pos, event.entity, &spec),
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
