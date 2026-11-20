//! Ratio alloys. Bronze and brass leave the slots alone until the mix is inside the window.

use crate::heat;
use crate::recipes::{self, can_output, merge_output};
use horizon_client::mod_api::serde_json::{from_str, Value};
use horizon_client::mod_api::{ModBlockEntity, Tag};
use std::sync::OnceLock;

struct Alloy {
    id: String,
    output: String,
    major: String,
    minor: String,
    min: f32,
    max: f32,
}

struct Table {
    ingot_units: i32,
    nugget_units: i32,
    double_units: i32,
    duration: i32,
    alloys: Vec<Alloy>,
}

fn table() -> &'static Table {
    static TABLE: OnceLock<Table> = OnceLock::new();
    TABLE.get_or_init(|| {
        let value: Value = from_str(include_str!("../tables/alloys.json")).expect("alloys");
        let alloys = value
            .get("alloys")
            .and_then(|v| v.as_array())
            .map(|rows| {
                rows.iter()
                    .filter_map(|row| {
                        Some(Alloy {
                            id: row.get("id")?.as_str()?.to_owned(),
                            output: row.get("output")?.as_str()?.to_owned(),
                            major: row.get("major")?.as_str()?.to_owned(),
                            minor: row.get("minor")?.as_str()?.to_owned(),
                            min: row.get("min")?.as_f64()? as f32,
                            max: row.get("max")?.as_f64()? as f32,
                        })
                    })
                    .collect()
            })
            .unwrap_or_default();
        Table {
            ingot_units: value.get("ingot_units").and_then(|v| v.as_i64()).unwrap_or(100) as i32,
            nugget_units: value.get("nugget_units").and_then(|v| v.as_i64()).unwrap_or(10) as i32,
            double_units: value.get("double_units").and_then(|v| v.as_i64()).unwrap_or(200) as i32,
            duration: value.get("duration").and_then(|v| v.as_i64()).unwrap_or(200) as i32,
            alloys,
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

fn stack_units(item: &str, count: i32) -> Option<(String, i32)> {
    let data = table();
    let metal = heat::metal_name(item)?.to_owned();
    let each = if item.contains("nugget") {
        data.nugget_units
    } else if item.ends_with("_double_ingot") {
        data.double_units
    } else if item.ends_with("_ingot") || item == "minecraft:gold_ingot" {
        data.ingot_units
    } else {
        return None;
    };
    Some((metal, each.saturating_mul(count)))
}

struct Mix {
    output: String,
    count: u32,
    melt: i32,
}

fn mix(entity: &ModBlockEntity) -> Option<Mix> {
    let data = table();
    let left_stack = entity.items.get(1).and_then(|slot| slot.as_ref())?;
    let right_stack = entity.items.get(2).and_then(|slot| slot.as_ref())?;
    let left = stack_units(left_stack.item.as_ref(), left_stack.count as i32)?;
    let right = stack_units(right_stack.item.as_ref(), right_stack.count as i32)?;
    if left.1 <= 0 || right.1 <= 0 || left.0 == right.0 {
        return None;
    }
    let alloy = data.alloys.iter().find(|alloy| {
        (left.0 == alloy.major && right.0 == alloy.minor)
            || (left.0 == alloy.minor && right.0 == alloy.major)
    })?;
    let major_units = if left.0 == alloy.major { left.1 } else { right.1 };
    let minor_units = if left.0 == alloy.minor { left.1 } else { right.1 };
    let total = major_units + minor_units;
    let fraction = major_units as f32 / total as f32;
    if fraction < alloy.min || fraction > alloy.max || total % data.ingot_units != 0 {
        return None;
    }
    let count = total / data.ingot_units;
    if count <= 0 {
        return None;
    }
    let melt = heat::melt_of(&alloy.id)?;
    Some(Mix {
        output: alloy.output.clone(),
        count: count as u32,
        melt,
    })
}

pub fn tick(entity: &mut ModBlockEntity, hot: bool) {
    if entity.items.len() < 4 {
        entity.items.resize(4, None);
    }
    let heat = heat::sync(entity, hot, 1, 2);
    let matched = mix(entity);
    let duration = table().duration.max(1);
    let mut progress = nbt_i32(entity, "Progress");
    if let Some(recipe) = matched {
        let wanted = recipes::stack(&recipe.output, recipe.count);
        let fits = entity
            .items
            .get(3)
            .is_some_and(|slot| can_output(slot, &wanted));
        if fits && heat::ready(heat, Some(recipe.melt)) {
            progress += 1;
            if progress >= duration {
                entity.items[1] = None;
                entity.items[2] = None;
                merge_output(&mut entity.items[3], &wanted);
                progress = 0;
            }
        }
    } else {
        progress = 0;
    }
    nbt_set(entity, "Progress", progress);
    nbt_set(entity, "ProgressMax", duration);
    if entity.data.len() < 4 {
        entity.data.resize(4, 0);
    }
    entity.data[0] = progress;
    entity.data[1] = duration;
    entity.data[2] = heat;
    entity.data[3] = heat::forge_max().max(1);
}
