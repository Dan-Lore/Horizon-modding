//! Prospector's pick: nearby ores plus the hybrid rock preview.

use crate::worldgen;
use horizon_client::mod_api::serde_json::{from_str, Value};
use std::sync::OnceLock;

struct Ore {
    block: String,
    name: String,
}

fn ores() -> &'static Vec<Ore> {
    static ORES: OnceLock<Vec<Ore>> = OnceLock::new();
    ORES.get_or_init(|| {
        let value: Value = from_str(include_str!("../tables/ores.json")).expect("ores table");
        value
            .as_array()
            .map(|rows| {
                rows.iter()
                    .filter_map(|row| {
                        Some(Ore {
                            block: row.get("block")?.as_str()?.to_owned(),
                            name: row.get("name")?.as_str()?.to_owned(),
                        })
                    })
                    .collect()
            })
            .unwrap_or_default()
    })
}

pub fn is_propick(item: &str) -> bool {
    item == "tfc:prospector_pick" || item.ends_with("_propick")
}

pub fn is_chisel(item: &str) -> bool {
    item.ends_with("_chisel")
}

pub fn is_hammer(item: &str) -> bool {
    item.ends_with("_hammer")
}

pub fn is_pan(item: &str) -> bool {
    item == "tfc:pan"
}

pub const RADIUS: i32 = 8;

pub fn scan(block_at: impl Fn([i32; 3]) -> String, origin: [i32; 3]) -> String {
    let mut found = Vec::new();
    for dy in -RADIUS..=RADIUS {
        for dz in -RADIUS..=RADIUS {
            for dx in -RADIUS..=RADIUS {
                let pos = [origin[0] + dx, origin[1] + dy, origin[2] + dz];
                let name = block_at(pos);
                if let Some(ore) = ores().iter().find(|ore| ore.block == name) {
                    if !found.contains(&ore.name) {
                        found.push(ore.name.clone());
                    }
                }
            }
        }
    }
    let rock = worldgen::rock_at(origin[0], origin[2]);
    if found.is_empty() {
        format!("Prospect: no ore within {RADIUS} blocks. Local rock preview: {rock}.")
    } else {
        format!(
            "Prospect: {}. Local rock preview: {rock}.",
            found.join(", ")
        )
    }
}
