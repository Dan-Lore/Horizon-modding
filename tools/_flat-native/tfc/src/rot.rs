//! Food in a TFC container counts down to rot. A stack in the player inventory does not.

use crate::food;
use crate::recipes;
use horizon_client::mod_api::{ModBlockEntity, Tag};

fn nbt_i32(entity: &ModBlockEntity, key: &str) -> i32 {
    match entity.nbt.get(&key.into()) {
        Some(Tag::Int(value)) => *value,
        _ => 0,
    }
}

fn nbt_set(entity: &mut ModBlockEntity, key: &str, value: i32) {
    entity.nbt.insert(key.into(), Tag::Int(value));
}

pub fn tick_all(entity: &mut ModBlockEntity) {
    let count = entity.items.len();
    for index in 0..count {
        tick_slot(entity, index);
    }
}

pub fn tick_slot(entity: &mut ModBlockEntity, index: usize) {
    let stamp_key = format!("Stamp{index}");
    let decay_key = format!("Decay{index}");
    let Some(id) = entity
        .items
        .get(index)
        .and_then(|slot| slot.as_ref())
        .map(|stack| stack.item.as_ref().to_owned())
    else {
        return;
    };
    let Some(limit) = food::decay_ticks(&id) else {
        return;
    };
    let mark = food::item_stamp(&id);
    if nbt_i32(entity, &stamp_key) != mark {
        nbt_set(entity, &stamp_key, mark);
        nbt_set(entity, &decay_key, limit);
    }
    let left = nbt_i32(entity, &decay_key) - 1;
    if left > 0 {
        nbt_set(entity, &decay_key, left);
        return;
    }
    let count = entity
        .items
        .get(index)
        .and_then(|slot| slot.as_ref())
        .map(|stack| stack.count)
        .unwrap_or(1);
    entity.items[index] = Some(recipes::stack("tfc:rot", count));
    nbt_set(entity, &stamp_key, food::item_stamp("tfc:rot"));
    nbt_set(entity, &decay_key, 0);
}
