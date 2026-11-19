//! Greate Horizon 0.1.0 — tiered Create×Greglite bridge (awaits pin convergence).

mod tiers;

pub use tiers::{dynamo_eu_per_tick, motor_stress_draw, KineticTier};

use horizon_client::mod_api::{Hooks, Host, PlayerLoggedInEvent, Text};

pub fn hooks() -> Box<dyn Hooks> {
    Box::new(Greate)
}

struct Greate;

impl Hooks for Greate {
    fn player_logged_in(&self, host: &mut dyn Host, event: &mut PlayerLoggedInEvent<'_>) {
        host.tell(
            event.player,
            Text::literal(
                "Greate Horizon 0.1.0: tiered shafts ready in content; Create+Greglite co-build parked (pin).",
            ),
        );
    }
}
