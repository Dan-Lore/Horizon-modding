//! Familiar TFC animals, listed only. Nothing here is spawned.

use horizon_client::mod_api::serde_json::{from_str, Value};
use std::sync::OnceLock;

pub const STATUS: &str = "deferred";

pub fn ids() -> &'static [String] {
    static IDS: OnceLock<Vec<String>> = OnceLock::new();
    IDS.get_or_init(|| {
        let value: Value =
            from_str(include_str!("../../tables/animals.json")).expect("animals table");
        value
            .as_array()
            .map(|rows| {
                rows.iter()
                    .filter_map(|row| row.get("id").and_then(|v| v.as_str()).map(str::to_owned))
                    .collect()
            })
            .unwrap_or_default()
    })
}
