//! Calendar and thin climate. Numbers come from `tables/climate_seasons.json`.

use horizon_client::mod_api::serde_json::{from_str, Value};
use std::sync::OnceLock;

#[derive(Clone, Copy, Debug)]
pub struct ClimateSample {
    pub season: &'static str,
    pub month: &'static str,
    pub temp_c: f32,
    pub rainfall: f32,
}

fn table() -> &'static Value {
    static TABLE: OnceLock<Value> = OnceLock::new();
    TABLE.get_or_init(|| {
        from_str(include_str!("../../tables/climate_seasons.json")).expect("climate table")
    })
}

pub fn sample(absolute_day: i64, x: i32, z: i32) -> ClimateSample {
    let data = table();
    let days = data
        .get("days_per_month")
        .and_then(|v| v.as_i64())
        .unwrap_or(8);
    let base = data
        .get("base_temp")
        .and_then(|v| v.as_f64())
        .unwrap_or(14.0) as f32;
    let rain = data
        .get("base_rain")
        .and_then(|v| v.as_f64())
        .unwrap_or(300.0) as f32;
    let months = data
        .get("months")
        .and_then(|v| v.as_array())
        .expect("climate months");
    let idx = (absolute_day / days.max(1)).rem_euclid(months.len() as i64) as usize;
    let month = &months[idx];
    let offset = month
        .get("temp_offset")
        .and_then(|v| v.as_f64())
        .unwrap_or(0.0) as f32;
    let spatial = ((x.wrapping_mul(374761393) ^ z.wrapping_mul(668265263)) as f32).sin() * 3.0;
    let rain_noise = ((x.wrapping_mul(127) ^ z.wrapping_mul(311)) as f32 % 97.0).abs();
    ClimateSample {
        season: month.get("season").and_then(|v| v.as_str()).unwrap_or("?"),
        month: month.get("name").and_then(|v| v.as_str()).unwrap_or("?"),
        temp_c: base + offset + spatial,
        rainfall: (rain + rain_noise * 2.0).clamp(50.0, 500.0),
    }
}

pub fn hud_line(c: &ClimateSample, thirst: f32, nutrients: &str) -> String {
    format!(
        "TFC {} ({}) {:.0}C thirst {:.0}% | {nutrients}",
        c.season,
        c.month,
        c.temp_c,
        (thirst * 100.0).clamp(0.0, 100.0),
    )
}

pub fn crop_allowed(
    c: &ClimateSample,
    min_temp: f32,
    max_temp: f32,
    min_rain: f32,
    max_rain: f32,
    seasons: &[String],
) -> bool {
    c.temp_c >= min_temp
        && c.temp_c <= max_temp
        && c.rainfall >= min_rain
        && c.rainfall <= max_rain
        && seasons.iter().any(|season| season == c.season)
}
