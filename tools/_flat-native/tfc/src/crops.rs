//! Crop blocks fill their output slot only inside the climate window.

use crate::climate;
use crate::recipes::stack;
use horizon_client::mod_api::serde_json::{from_str, Value};
use horizon_client::mod_api::{Host, ModBlockEntity, Tag};
use std::sync::OnceLock;

struct Crop {
    id: String,
    product: String,
    min_temp: f32,
    max_temp: f32,
    min_rain: f32,
    max_rain: f32,
    seasons: Vec<String>,
}

fn crops() -> &'static Vec<Crop> {
    static CROPS: OnceLock<Vec<Crop>> = OnceLock::new();
    CROPS.get_or_init(|| {
        let value: Value = from_str(include_str!("../tables/crops.json")).expect("crops table");
        value
            .as_array()
            .map(|rows| {
                rows.iter()
                    .filter_map(|row| {
                        Some(Crop {
                            id: row.get("id")?.as_str()?.to_owned(),
                            product: row.get("product")?.as_str()?.to_owned(),
                            min_temp: row.get("min_temp")?.as_f64()? as f32,
                            max_temp: row.get("max_temp")?.as_f64()? as f32,
                            min_rain: row.get("min_rain").and_then(|v| v.as_f64()).unwrap_or(0.0) as f32,
                            max_rain: row.get("max_rain").and_then(|v| v.as_f64()).unwrap_or(500.0) as f32,
                            seasons: row
                                .get("seasons")?
                                .as_array()?
                                .iter()
                                .filter_map(|v| v.as_str().map(str::to_owned))
                                .collect(),
                        })
                    })
                    .collect()
            })
            .unwrap_or_default()
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

pub fn tick(host: &dyn Host, pos: [i32; 3], entity: &mut ModBlockEntity) {
    let Some(crop) = crops().iter().find(|crop| crop.id == entity.id) else {
        return;
    };
    if entity.items.is_empty() {
        entity.items.push(None);
    }
    let day = host.day_time() / 24_000;
    let sample = climate::sample(day, pos[0], pos[2]);
    let allowed = climate::crop_allowed(
        &sample,
        crop.min_temp,
        crop.max_temp,
        crop.min_rain,
        crop.max_rain,
        &crop.seasons,
    );
    let mut growth = nbt_i32(entity, "Growth");
    if allowed && growth < 7 {
        let age = nbt_i32(entity, "Age").saturating_add(1);
        nbt_set(entity, "Age", age);
        if age % 200 == 0 {
            growth += 1;
            nbt_set(entity, "Growth", growth);
        }
    }
    if growth >= 7 && entity.items[0].is_none() {
        entity.items[0] = Some(stack(&crop.product, 1));
    }
    if entity.data.len() < 4 {
        entity.data.resize(4, 0);
    }
    entity.data[0] = growth;
    entity.data[1] = 7;
    entity.data[2] = if allowed { 1 } else { 0 };
    entity.data[3] = 1;
}
