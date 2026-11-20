//! Hybrid rock preview. Full layer generation stays off until chunk hooks exist.
//!
//! When custom chunk generators / density functions are available for native mods,
//! replace the hybrid sampler and spawn veins from planned layers in `tables/worldgen.json`.

use horizon_client::mod_api::serde_json::{from_str, Value};
use std::sync::OnceLock;

pub const STATUS: &str = "blocked";
pub const REASON: &str =
    "custom biome/rock-layer/vein worldgen hooks incomplete for TFC parity";

fn rocks() -> &'static Vec<String> {
    static ROCKS: OnceLock<Vec<String>> = OnceLock::new();
    ROCKS.get_or_init(|| {
        let value: Value =
            from_str(include_str!("../tables/worldgen.json")).expect("worldgen table");
        value
            .get("content_rocks")
            .and_then(|v| v.as_array())
            .map(|rows| {
                rows.iter()
                    .filter_map(|v| v.as_str().map(str::to_owned))
                    .collect()
            })
            .filter(|rows: &Vec<String>| !rows.is_empty())
            .unwrap_or_else(|| vec!["andesite".to_owned()])
    })
}

pub fn rock_at(x: i32, z: i32) -> String {
    let rows = rocks();
    let idx = (x.wrapping_mul(73_428_767) ^ z.wrapping_mul(912_931)).unsigned_abs() as usize
        % rows.len();
    rows[idx].clone()
}
