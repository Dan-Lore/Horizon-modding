//! In-mod FE buffer (Ad Astra energy). Independent of Greglite EU.

use horizon_client::mod_api::{ModBlockEntity, Tag};

const KEY_FE: &str = "Fe";
const KEY_BURN: &str = "BurnTime";
const KEY_BURN_MAX: &str = "BurnMax";
const KEY_PROGRESS: &str = "Progress";
const KEY_PROGRESS_MAX: &str = "ProgressMax";

pub const FE_TRANSFER: i32 = 32;
pub const DEFAULT_CAP: i32 = 16_000;

fn nbt_i32(entity: &ModBlockEntity, key: &str) -> i32 {
    match entity.nbt.get(&key.into()) {
        Some(Tag::Int(v)) => *v,
        _ => 0,
    }
}

fn nbt_set_i32(entity: &mut ModBlockEntity, key: &str, value: i32) {
    entity.nbt.insert(key.into(), Tag::Int(value));
}

pub fn fe(entity: &ModBlockEntity) -> i32 {
    nbt_i32(entity, KEY_FE).max(0)
}

pub fn set_fe(entity: &mut ModBlockEntity, value: i32, cap: i32) {
    nbt_set_i32(entity, KEY_FE, value.clamp(0, cap.max(0)));
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

/// data[0]=progress/burn, data[1]=max, data[2]=FE gauge, data[3]=cap
pub fn sync_data(entity: &mut ModBlockEntity, primary: i32, primary_max: i32, energy: i32, cap: i32) {
    if entity.data.len() < 4 {
        entity.data.resize(4, 0);
    }
    entity.data[0] = primary;
    entity.data[1] = primary_max.max(1);
    entity.data[2] = energy.max(0);
    entity.data[3] = cap.max(1);
}
