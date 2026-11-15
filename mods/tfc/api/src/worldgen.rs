//! Full TFC worldgen (W12) — blocked pending Horizon biome/vein APIs.
//!
//! Hybrid bridge: [`crate::climate::sample`] + placeable ore/rock content on vanilla overworld.
//! When custom chunk generators / density functions are available for native mods, replace
//! the hybrid sampler and spawn veins from `tables/veins.json`.

pub const STATUS: &str = "blocked";
pub const REASON: &str = "custom biome/rock-layer/vein worldgen hooks incomplete for TFC parity";
