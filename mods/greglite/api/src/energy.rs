//! Shared NBT energy buffers (steam + EU) and menu sync.

use horizon_client::mod_api::{ModBlockEntity, Tag};

const KEY_STEAM: &str = "Steam";
const KEY_EU: &str = "Eu";
const KEY_EU_V: &str = "EuV";
const KEY_BURN: &str = "BurnTime";
const KEY_BURN_MAX: &str = "BurnMax";
const KEY_PROGRESS: &str = "Progress";
const KEY_PROGRESS_MAX: &str = "ProgressMax";

pub const STEAM_CAP: i32 = 16_000;
pub const LV_EU_CAP: i32 = 2_048;
pub const CABLE_EU_CAP: i32 = 512;
pub const BUFFER_EU_CAP: i32 = 128_000;
pub const STEAM_TRANSFER: i32 = 64;
pub const EU_TRANSFER: i32 = 32;

fn nbt_i32(entity: &ModBlockEntity, key: &str) -> i32 {
    match entity.nbt.get(&key.into()) {
        Some(Tag::Int(v)) => *v,
        _ => 0,
    }
}

fn nbt_set_i32(entity: &mut ModBlockEntity, key: &str, value: i32) {
    entity.nbt.insert(key.into(), Tag::Int(value));
}

pub fn steam(entity: &ModBlockEntity) -> i32 {
    nbt_i32(entity, KEY_STEAM).clamp(0, STEAM_CAP)
}

pub fn set_steam(entity: &mut ModBlockEntity, value: i32) {
    nbt_set_i32(entity, KEY_STEAM, value.clamp(0, STEAM_CAP));
}

pub fn eu(entity: &ModBlockEntity) -> i32 {
    nbt_i32(entity, KEY_EU).max(0)
}

pub fn set_eu(entity: &mut ModBlockEntity, value: i32, cap: i32) {
    nbt_set_i32(entity, KEY_EU, value.clamp(0, cap.max(0)));
}

/// Voltage of the EU sitting in the buffer. 0 means "use the block rating".
pub fn packet_voltage(entity: &ModBlockEntity) -> i32 {
    nbt_i32(entity, KEY_EU_V).max(0)
}

pub fn set_packet_voltage(entity: &mut ModBlockEntity, voltage: i32) {
    nbt_set_i32(entity, KEY_EU_V, voltage.max(0));
}

pub fn burn(entity: &ModBlockEntity) -> (i32, i32) {
    (
        nbt_i32(entity, KEY_BURN).max(0),
        nbt_i32(entity, KEY_BURN_MAX).max(0),
    )
}

pub fn set_burn(entity: &mut ModBlockEntity, time: i32, max: i32) {
    nbt_set_i32(entity, KEY_BURN, time.max(0));
    nbt_set_i32(entity, KEY_BURN_MAX, max.max(0));
}

pub fn progress(entity: &ModBlockEntity) -> (i32, i32) {
    (
        nbt_i32(entity, KEY_PROGRESS).max(0),
        nbt_i32(entity, KEY_PROGRESS_MAX).max(0),
    )
}

pub fn set_progress(entity: &mut ModBlockEntity, time: i32, max: i32) {
    nbt_set_i32(entity, KEY_PROGRESS, time.max(0));
    nbt_set_i32(entity, KEY_PROGRESS_MAX, max.max(0));
}

/// data[0]=progress/burn, data[1]=max, data[2]=energy gauge, data[3]=cap
pub fn sync_data(entity: &mut ModBlockEntity, primary: i32, primary_max: i32, energy: i32, cap: i32) {
    if entity.data.len() < 4 {
        entity.data.resize(4, 0);
    }
    entity.data[0] = primary;
    entity.data[1] = primary_max.max(1);
    entity.data[2] = energy.max(0);
    entity.data[3] = cap.max(1);
}
