//! Miner / pump world interaction (hooks Host::destroy_block + fluid absorb).

use crate::energy::{eu, set_eu};
use crate::fluids::{self, WATER};
use crate::recipes::merge_output;
use crate::registry::Spec;
use horizon_client::mod_api::{Host, ModBlockEntity};

const OFFSETS: [[i32; 3]; 6] = [
    [0, -1, 0],
    [1, 0, 0],
    [-1, 0, 0],
    [0, 0, 1],
    [0, 0, -1],
    [0, 1, 0],
];

fn is_ore_like(block: &str) -> bool {
    let b = block.to_ascii_lowercase();
    (b.contains("ore") || b.contains("_ore") || b.contains("raw_"))
        && !b.contains("furnace")
        && !b.starts_with("greglite:")
}

fn is_miner(spec: &Spec) -> bool {
    spec.id.contains("miner")
        || spec
            .recipe_type
            .as_deref()
            .is_some_and(|t| t.contains("miner"))
}

fn is_pump(spec: &Spec) -> bool {
    let id_pump = spec.id.contains("pump") && !spec.id.contains("cover");
    let type_pump = spec
        .recipe_type
        .as_deref()
        .is_some_and(|t| t.ends_with(":pump") || t.ends_with("_pump"));
    id_pump || type_pump
}

/// While the machine has EU, break one adjacent ore-like block into the output slot.
pub fn tick_miner(host: &mut dyn Host, pos: [i32; 3], entity: &mut ModBlockEntity, spec: &Spec) {
    if !is_miner(spec) {
        return;
    }
    let cost = (spec.voltage.max(32) / 8).max(8);
    let have = eu(entity);
    if have < cost {
        return;
    }
    let out = spec.output.unwrap_or(0);
    if entity.items.len() <= out {
        entity.items.resize(out + 1, None);
    }
    let dim = host.dimension();
    for offset in OFFSETS {
        let npos = [pos[0] + offset[0], pos[1] + offset[1], pos[2] + offset[2]];
        let Some(level) = host.level(dim) else {
            continue;
        };
        let Some(block) = level.block(host, npos) else {
            continue;
        };
        if !is_ore_like(&block) {
            continue;
        }
        let Some(drops) = host.destroy_block(npos, None, true) else {
            continue;
        };
        set_eu(entity, have - cost, spec.gauge_cap());
        for drop in drops {
            if entity.items[out].is_none() {
                entity.items[out] = Some(drop);
            } else {
                merge_output(&mut entity.items[out], &drop);
            }
        }
        let _ = host.set_block_property(pos, "lit", "true");
        return;
    }
}

/// Pull source water into the pump's fluid tank while powered.
pub fn tick_pump(host: &mut dyn Host, pos: [i32; 3], entity: &mut ModBlockEntity, spec: &Spec) {
    if !is_pump(spec) {
        return;
    }
    let cost = (spec.voltage.max(32) / 16).max(4);
    let have = eu(entity);
    if have < cost {
        return;
    }
    let before = fluids::amount(entity, 0, WATER);
    fluids::absorb_water_block(host, pos, entity, 0, 1, 16_000, 250);
    fluids::pull_from_neighbours(host, pos, entity, 0, 1, WATER, 16_000, 250);
    let after = fluids::amount(entity, 0, WATER);
    if after > before {
        set_eu(entity, have - cost, spec.gauge_cap());
        let _ = host.set_block_property(pos, "lit", "true");
    }
}
