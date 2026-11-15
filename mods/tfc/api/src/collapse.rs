//! Support beams + collapse lite (W10) — scan near the player each tick.

use crate::registry;
use horizon_client::mod_api::{Host, Text};

/// Soft collapse warning when standing under unsupported TFC rock.
pub fn check_near_player(host: &mut dyn Host, pos: [i32; 3]) {
    for dy in 0..=3 {
        let above = [pos[0], pos[1] + dy, pos[2]];
        let block = host.block(above);
        if !registry::is_rock(&block) {
            continue;
        }
        if !is_supported(host, above) {
            if let Some(p) = host.acting_player() {
                host.action_bar(
                    p.uuid,
                    Text::literal("Unsupported rock overhead — place a support beam!"),
                );
            }
            return;
        }
    }
}

fn is_supported(host: &dyn Host, pos: [i32; 3]) -> bool {
    let dirs = [
        [1, 0, 0],
        [-1, 0, 0],
        [0, 1, 0],
        [0, -1, 0],
        [0, 0, 1],
        [0, 0, -1],
    ];
    for d in dirs {
        let n = [pos[0] + d[0], pos[1] + d[1], pos[2] + d[2]];
        let nb = host.block(n);
        if registry::is_support(&nb) || nb == "minecraft:bedrock" {
            return true;
        }
    }
    for dy in 1..=3 {
        let n = [pos[0], pos[1] - dy, pos[2]];
        if registry::is_support(&host.block(n)) {
            return true;
        }
    }
    false
}
