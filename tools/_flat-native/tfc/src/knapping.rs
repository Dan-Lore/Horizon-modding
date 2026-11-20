//! 5×5 rock mask. A matching pattern yields one stone tool head.

use crate::recipes::{self, can_output, merge_output};
use horizon_client::mod_api::serde_json::{from_str, Value};
use horizon_client::mod_api::{ModBlockEntity, Tag};
use std::sync::OnceLock;

struct Pattern {
    output: String,
    mask: String,
}

struct Table {
    rock: String,
    ticks: i32,
    patterns: Vec<Pattern>,
}

fn table() -> &'static Table {
    static TABLE: OnceLock<Table> = OnceLock::new();
    TABLE.get_or_init(|| {
        let value: Value = from_str(include_str!("../tables/knapping.json")).expect("knapping");
        let patterns = value
            .get("patterns")
            .and_then(|v| v.as_array())
            .map(|rows| {
                rows.iter()
                    .filter_map(|row| {
                        Some(Pattern {
                            output: row.get("output")?.as_str()?.to_owned(),
                            mask: row.get("mask")?.as_str()?.to_owned(),
                        })
                    })
                    .collect()
            })
            .unwrap_or_default();
        Table {
            rock: value
                .get("rock")
                .and_then(|v| v.as_str())
                .unwrap_or("tfc:andesite_cobble")
                .to_owned(),
            ticks: value.get("ticks").and_then(|v| v.as_i64()).unwrap_or(20) as i32,
            patterns,
        }
    })
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

fn mask_of(entity: &ModBlockEntity, rock: &str) -> String {
    let mut bits = String::with_capacity(25);
    for index in 0..25 {
        let bit = match entity.items.get(index).and_then(|slot| slot.as_ref()) {
            Some(stack) if stack.item.as_ref() == rock => '1',
            None => '0',
            Some(_) => 'x',
        };
        bits.push(bit);
    }
    bits
}

pub fn tick(entity: &mut ModBlockEntity) {
    if entity.items.len() < 26 {
        entity.items.resize(26, None);
    }
    let data = table();
    let mask = mask_of(entity, &data.rock);
    let pattern = data.patterns.iter().find(|pattern| pattern.mask == mask);
    let ticks = data.ticks.max(1);
    let mut progress = nbt_i32(entity, "Progress");
    if let Some(pattern) = pattern {
        let output = recipes::stack(&pattern.output, 1);
        if entity.items.get(25).is_some_and(|slot| can_output(slot, &output)) {
            progress += 1;
            if progress >= ticks {
                for index in 0..25 {
                    if mask.as_bytes()[index] != b'1' {
                        continue;
                    }
                    let slot = &mut entity.items[index];
                    if let Some(stack) = slot {
                        if stack.count <= 1 {
                            *slot = None;
                        } else {
                            stack.count -= 1;
                        }
                    }
                }
                merge_output(&mut entity.items[25], &output);
                progress = 0;
            }
        }
    } else {
        progress = 0;
    }
    nbt_set(entity, "Progress", progress);
    if entity.data.len() < 4 {
        entity.data.resize(4, 0);
    }
    entity.data[0] = progress;
    entity.data[1] = ticks;
    entity.data[2] = progress;
    entity.data[3] = ticks;
}
