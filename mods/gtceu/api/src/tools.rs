//! Electric tools — dig speed while held (`break_speed` on hooks 411).

use horizon_client::mod_api::{BreakSpeedEvent, Host};

const DRILL_IDS: &[&str] = &["gtceu:lv_drill"];

/// Diamond-class dig rate while holding an LV drill (survival only; creative skips the hook).
const DRILL_SPEED_MULT: f32 = 8.0;

pub fn break_speed(host: &dyn Host, event: &mut BreakSpeedEvent) {
    let Some(player) = host.acting_player() else {
        return;
    };
    let Some(stack) = host.held_stack(player.uuid) else {
        return;
    };
    let id = stack.item.as_ref();
    if !DRILL_IDS.iter().any(|want| *want == id) {
        return;
    }
    if event.original <= 0.0 {
        return;
    }
    event.speed = event.original * DRILL_SPEED_MULT;
}
