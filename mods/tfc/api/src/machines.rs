//! Machine block-entity ticks (firepit, forge, bloomery, anvil, quern, barrel, sluice).

use crate::registry::{Kind, Spec};
use horizon_client::mod_api::{Host, ModBlockEntity, Tag};

fn nbt_i32(entity: &ModBlockEntity, key: &str) -> i32 {
    match entity.nbt.get(&key.into()) {
        Some(Tag::Int(v)) => *v,
        _ => 0,
    }
}

fn nbt_set_i32(entity: &mut ModBlockEntity, key: &str, value: i32) {
    entity.nbt.insert(key.into(), Tag::Int(value));
}

fn sync(entity: &mut ModBlockEntity, a: i32, b: i32, c: i32, d: i32) {
    if entity.data.len() < 4 {
        entity.data.resize(4, 0);
    }
    entity.data[0] = a;
    entity.data[1] = b.max(1);
    entity.data[2] = c;
    entity.data[3] = d.max(1);
}

pub fn tick(_host: &mut dyn Host, _pos: [i32; 3], entity: &mut ModBlockEntity, spec: &Spec) {
    match spec.kind {
        Kind::Firepit | Kind::Forge | Kind::PitKiln => tick_heat(entity),
        Kind::Bloomery | Kind::BlastFurnace | Kind::Crucible => tick_smelt(entity),
        Kind::Anvil => tick_anvil(entity),
        Kind::Quern => tick_quern(entity),
        Kind::Barrel => tick_barrel(entity),
        Kind::Sluice => tick_sluice(entity),
        Kind::Powderkeg => {}
    }
}

fn tick_heat(entity: &mut ModBlockEntity) {
    let mut temp = nbt_i32(entity, "temp");
    let fuel = nbt_i32(entity, "fuel");
    if fuel > 0 {
        nbt_set_i32(entity, "fuel", fuel - 1);
        temp = (temp + 4).min(1600);
    } else {
        temp = (temp - 1).max(0);
    }
    nbt_set_i32(entity, "temp", temp);
    sync(entity, temp, 1600, fuel.max(0), 64);
}

fn tick_smelt(entity: &mut ModBlockEntity) {
    let mut progress = nbt_i32(entity, "progress");
    let fuel = nbt_i32(entity, "fuel");
    if fuel > 0 {
        nbt_set_i32(entity, "fuel", fuel - 1);
        progress = (progress + 1).min(200);
        if progress >= 200 {
            progress = 0;
            nbt_set_i32(entity, "done", 1);
        }
    }
    nbt_set_i32(entity, "progress", progress);
    sync(entity, progress, 200, fuel, 64);
}

fn tick_anvil(entity: &mut ModBlockEntity) {
    let steps = nbt_i32(entity, "steps");
    sync(entity, steps, 3, 0, 1);
}

fn tick_quern(entity: &mut ModBlockEntity) {
    let mut progress = nbt_i32(entity, "progress");
    if entity.items.iter().any(|s| s.is_some()) {
        progress = (progress + 1).min(100);
        if progress >= 100 {
            progress = 0;
            nbt_set_i32(entity, "ground", 1);
        }
    }
    nbt_set_i32(entity, "progress", progress);
    sync(entity, progress, 100, 0, 1);
}

fn tick_barrel(entity: &mut ModBlockEntity) {
    let mut progress = nbt_i32(entity, "progress");
    progress = (progress + 1).min(8000);
    nbt_set_i32(entity, "progress", progress);
    sync(entity, progress, 8000, 0, 1);
}

fn tick_sluice(entity: &mut ModBlockEntity) {
    let mut progress = nbt_i32(entity, "progress");
    progress = (progress + 1).min(200);
    if progress >= 200 {
        progress = 0;
        nbt_set_i32(entity, "nugget", 1);
    }
    nbt_set_i32(entity, "progress", progress);
    sync(entity, progress, 200, 0, 1);
}
