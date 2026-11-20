//! Forge temperature. The number lives on the block entity while the item sits in it.

use crate::recipes::HeatNeed;
use horizon_client::mod_api::serde_json::{from_str, Value};
use horizon_client::mod_api::{ModBlockEntity, Tag};
use std::sync::OnceLock;

struct Metal {
    melt: i32,
    weld: i32,
}

struct Table {
    forge_max: i32,
    per_tick: i32,
    cool_per_tick: i32,
    metals: Vec<(String, Metal)>,
    items: Vec<(String, String)>,
}

fn table() -> &'static Table {
    static TABLE: OnceLock<Table> = OnceLock::new();
    TABLE.get_or_init(|| {
        let value: Value = from_str(include_str!("../../tables/heat.json")).expect("heat table");
        let metals = value
            .get("metals")
            .and_then(|v| v.as_object())
            .map(|rows| {
                rows.iter()
                    .filter_map(|(name, row)| {
                        Some((
                            name.clone(),
                            Metal {
                                melt: row.get("melt")?.as_i64()? as i32,
                                weld: row.get("weld")?.as_i64()? as i32,
                            },
                        ))
                    })
                    .collect()
            })
            .unwrap_or_default();
        let items = value
            .get("items")
            .and_then(|v| v.as_object())
            .map(|rows| {
                rows.iter()
                    .filter_map(|(item, metal)| Some((item.clone(), metal.as_str()?.to_owned())))
                    .collect()
            })
            .unwrap_or_default();
        Table {
            forge_max: value.get("forge_max").and_then(|v| v.as_i64()).unwrap_or(1400) as i32,
            per_tick: value.get("per_tick").and_then(|v| v.as_i64()).unwrap_or(20) as i32,
            cool_per_tick: value
                .get("cool_per_tick")
                .and_then(|v| v.as_i64())
                .unwrap_or(10) as i32,
            metals,
            items,
        }
    })
}

pub fn forge_max() -> i32 {
    table().forge_max
}

fn nbt_i32(entity: &ModBlockEntity, key: &str) -> i32 {
    match entity.nbt.get(&key.into()) {
        Some(Tag::Int(value)) => *value,
        _ => 0,
    }
}

fn nbt_set(entity: &mut ModBlockEntity, key: &str, value: i32) {
    entity.nbt.insert(key.into(), Tag::Int(value));
}

pub fn metal_name(item: &str) -> Option<&str> {
    table()
        .items
        .iter()
        .find(|(id, _)| id == item)
        .map(|(_, metal)| metal.as_str())
}

fn metal(item: &str) -> Option<&Metal> {
    let name = metal_name(item)?;
    table()
        .metals
        .iter()
        .find(|(id, _)| id == name)
        .map(|(_, metal)| metal)
}

pub fn melt_of(name: &str) -> Option<i32> {
    table()
        .metals
        .iter()
        .find(|(id, _)| id == name)
        .map(|(_, metal)| metal.melt)
}

fn signature(entity: &ModBlockEntity, start: usize, inputs: usize) -> i32 {
    let mut hash = 0i32;
    for index in 0..inputs {
        let id = entity
            .items
            .get(start + index)
            .and_then(|slot| slot.as_ref())
            .map(|stack| stack.item.as_ref())
            .unwrap_or("-");
        for byte in id.bytes() {
            hash = hash.wrapping_mul(31).wrapping_add(byte as i32);
        }
        hash = hash.wrapping_mul(31).wrapping_add(17);
    }
    hash
}

/// Raises or cools `Heat`, and clears it when the input items change.
pub fn sync(entity: &mut ModBlockEntity, hot: bool, start: usize, inputs: usize) -> i32 {
    let data = table();
    let sig = signature(entity, start, inputs);
    let mut heat = if nbt_i32(entity, "HeatSig") != sig {
        nbt_set(entity, "HeatSig", sig);
        0
    } else {
        nbt_i32(entity, "Heat")
    };
    heat = if hot {
        (heat + data.per_tick).min(data.forge_max)
    } else {
        (heat - data.cool_per_tick).max(0)
    };
    nbt_set(entity, "Heat", heat);
    heat
}

/// `None` skips the gate. `i32::MAX` means the forge cannot reach the metal.
pub fn target(item_ids: &[&str], need: HeatNeed) -> Option<i32> {
    let data = table();
    match need {
        HeatNeed::None => None,
        HeatNeed::Melt => {
            let Some(id) = item_ids.first().copied() else {
                return Some(i32::MAX);
            };
            match metal(id) {
                Some(row) if row.melt <= data.forge_max => Some(row.melt),
                _ => Some(i32::MAX),
            }
        }
        HeatNeed::Weld => {
            if item_ids.is_empty() {
                return Some(i32::MAX);
            }
            let mut top = 0;
            for id in item_ids {
                let Some(row) = metal(id) else {
                    return Some(i32::MAX);
                };
                top = top.max(row.weld);
            }
            if top > data.forge_max {
                Some(i32::MAX)
            } else {
                Some(top)
            }
        }
    }
}

pub fn ready(heat: i32, needed: Option<i32>) -> bool {
    match needed {
        None => true,
        Some(temperature) => temperature != i32::MAX && heat >= temperature,
    }
}
