//! Food size, weight, decay days, and the five nutrients.

use horizon_client::mod_api::serde_json::{from_str, Value};
use std::sync::OnceLock;

struct Food {
    id: String,
    grain: f32,
    fruit: f32,
    veg: f32,
    protein: f32,
    dairy: f32,
    size: String,
    weight: String,
    decay_days: i64,
}

struct Table {
    foods: Vec<Food>,
    drinks: Vec<String>,
}

fn table() -> &'static Table {
    static TABLE: OnceLock<Table> = OnceLock::new();
    TABLE.get_or_init(|| {
        let value: Value =
            from_str(include_str!("../../tables/nutrition.json")).expect("nutrition table");
        let foods = value
            .get("foods")
            .and_then(|v| v.as_array())
            .map(|rows| {
                rows.iter()
                    .filter_map(|row| {
                        Some(Food {
                            id: row.get("id")?.as_str()?.to_owned(),
                            grain: row.get("grain").and_then(|v| v.as_f64()).unwrap_or(0.0) as f32,
                            fruit: row.get("fruit").and_then(|v| v.as_f64()).unwrap_or(0.0) as f32,
                            veg: row.get("veg").and_then(|v| v.as_f64()).unwrap_or(0.0) as f32,
                            protein: row.get("protein").and_then(|v| v.as_f64()).unwrap_or(0.0)
                                as f32,
                            dairy: row.get("dairy").and_then(|v| v.as_f64()).unwrap_or(0.0) as f32,
                            size: row
                                .get("size")
                                .and_then(|v| v.as_str())
                                .unwrap_or("small")
                                .to_owned(),
                            weight: row
                                .get("weight")
                                .and_then(|v| v.as_str())
                                .unwrap_or("light")
                                .to_owned(),
                            decay_days: row.get("decay_days").and_then(|v| v.as_i64()).unwrap_or(4),
                        })
                    })
                    .collect()
            })
            .unwrap_or_default();
        let drinks = value
            .get("drinks")
            .and_then(|v| v.as_array())
            .map(|rows| {
                rows.iter()
                    .filter_map(|v| v.as_str().map(str::to_owned))
                    .collect()
            })
            .unwrap_or_default();
        Table { foods, drinks }
    })
}

pub fn nutrients(id: &str) -> Option<(f32, f32, f32, f32, f32)> {
    table().foods.iter().find(|food| food.id == id).map(|food| {
        (
            food.grain,
            food.fruit,
            food.veg,
            food.protein,
            food.dairy,
        )
    })
}

pub fn is_drink(id: &str) -> bool {
    table().drinks.iter().any(|drink| drink == id)
}

pub const DECAY_TICKS_PER_DAY: i32 = 200;

pub fn decay_ticks(id: &str) -> Option<i32> {
    let food = table().foods.iter().find(|food| food.id == id)?;
    if food.decay_days <= 0 {
        return None;
    }
    Some((food.decay_days as i32).saturating_mul(DECAY_TICKS_PER_DAY))
}

pub fn item_stamp(id: &str) -> i32 {
    let mut hash = 0i32;
    for byte in id.bytes() {
        hash = hash.wrapping_mul(31).wrapping_add(byte as i32);
    }
    hash
}

pub fn is_edible(id: &str) -> bool {
    nutrients(id).is_some() || is_drink(id)
}

pub fn tooltip_line(id: &str) -> Option<String> {
    let food = table().foods.iter().find(|food| food.id == id)?;
    Some(format!(
        "{}, {}, spoils in {} days inside a vessel or barrel",
        food.size, food.weight, food.decay_days
    ))
}
