//! Vacuum marker / distributor proximity and gravity foot checks.

use crate::machines;
use horizon_client::mod_api::Host;

const VACUUM_R: i32 = 4;
const DIST_R: i32 = 6;

pub fn in_vacuum(host: &mut dyn Host, origin: [i32; 3]) -> bool {
    for dx in -VACUUM_R..=VACUUM_R {
        for dy in -VACUUM_R..=VACUUM_R {
            for dz in -VACUUM_R..=VACUUM_R {
                let pos = [origin[0] + dx, origin[1] + dy, origin[2] + dz];
                if host.block(pos) == "adastra:vacuum_marker" {
                    return true;
                }
            }
        }
    }
    false
}

pub fn in_distributor_bubble(host: &mut dyn Host, origin: [i32; 3]) -> bool {
    for dx in -DIST_R..=DIST_R {
        for dy in -DIST_R..=DIST_R {
            for dz in -DIST_R..=DIST_R {
                let pos = [origin[0] + dx, origin[1] + dy, origin[2] + dz];
                if host.block(pos) != "adastra:oxygen_distributor" {
                    continue;
                }
                let mut active = false;
                let ok = host.change_mod_block_entity(pos, &mut |entity| {
                    active = machines::distributor_active(entity);
                });
                if ok && active {
                    return true;
                }
            }
        }
    }
    false
}

pub fn foot_gravity(host: &dyn Host, origin: [i32; 3]) -> &'static str {
    let below = [origin[0], origin[1] - 1, origin[2]];
    match host.block(below).as_str() {
        "adastra:moon_stone" | "adastra:moon_cobblestone" => "low-g moon",
        "adastra:mars_stone" | "adastra:mars_cobblestone" => "low-g mars",
        _ => "1g",
    }
}

pub fn is_suit_piece(item: &str) -> bool {
    matches!(
        item,
        "adastra:space_helmet"
            | "adastra:space_suit"
            | "adastra:space_pants"
            | "adastra:space_boots"
    )
}

pub fn is_oxygen_tank(item: &str) -> bool {
    item == "adastra:oxygen_tank"
}

pub fn is_rocket(item: &str) -> bool {
    item == "adastra:rocket_t1"
}
