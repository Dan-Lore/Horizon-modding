//! Generators, FE processors, oxygen loader/distributor.

use crate::energy::{
    burn, fe, progress, set_burn, set_fe, set_progress, sync_data,
};
use crate::net::{transfer_fe_in, transfer_fe_out};
use crate::recipes::{self, can_output, ingredient_accepts, merge_output, MachineRecipe};
use crate::registry::{Kind, Spec};
use horizon_client::mod_api::{Host, ModBlockEntity};

fn solid_fuel(item: &str) -> i32 {
    match item {
        "minecraft:coal" | "minecraft:charcoal" => 1_600,
        "minecraft:coal_block" => 16_000,
        _ => 0,
    }
}

fn shrink(slot: &mut Option<horizon_client::mod_api::ItemStack>) {
    let Some(stack) = slot else {
        return;
    };
    if stack.count <= 1 {
        *slot = None;
    } else {
        stack.count -= 1;
    }
}

pub fn tick(host: &mut dyn Host, pos: [i32; 3], entity: &mut ModBlockEntity, spec: &Spec) {
    match spec.kind {
        Kind::Generator => tick_generator(host, pos, entity, spec),
        Kind::Solar => tick_solar(host, pos, entity, spec),
        Kind::Processor | Kind::Loader => tick_processor(host, pos, entity, spec),
        Kind::Distributor => tick_distributor(host, pos, entity, spec),
        Kind::Storage | Kind::Vacuum | Kind::Marker => {}
    }
}

fn tick_generator(host: &mut dyn Host, pos: [i32; 3], entity: &mut ModBlockEntity, spec: &Spec) {
    if entity.items.len() < 1 {
        entity.items.resize(1, None);
    }
    let (mut burn_left, mut burn_max) = burn(entity);
    if burn_left <= 0 {
        if let Some(stack) = entity.items[0].as_mut() {
            let value = solid_fuel(stack.item.as_ref());
            if value > 0 {
                burn_left = value;
                burn_max = value;
                stack.count = stack.count.saturating_sub(1);
                if stack.count == 0 {
                    entity.items[0] = None;
                }
            }
        }
    }
    let mut working = false;
    let cap = spec.fe_cap;
    let rate = spec.fe_rate.max(1);
    if burn_left > 0 && fe(entity) + rate <= cap {
        burn_left -= 1;
        set_fe(entity, fe(entity) + rate, cap);
        working = true;
    } else if burn_left > 0 {
        burn_left -= 1;
    }
    set_burn(entity, burn_left, burn_max);
    transfer_fe_out(host, pos, entity, spec);
    let (b, bm) = burn(entity);
    sync_data(entity, b, bm.max(1), fe(entity), cap);
    let _ = host.set_block_property(pos, "lit", if working { "true" } else { "false" });
}

fn tick_solar(host: &mut dyn Host, pos: [i32; 3], entity: &mut ModBlockEntity, spec: &Spec) {
    let day = host.day_time() % 24_000;
    let daytime = day < 12_000;
    let mut working = false;
    let cap = spec.fe_cap;
    let rate = spec.fe_rate.max(1);
    if daytime && fe(entity) + rate <= cap {
        set_fe(entity, fe(entity) + rate, cap);
        working = true;
    }
    transfer_fe_out(host, pos, entity, spec);
    sync_data(
        entity,
        if working { 1 } else { 0 },
        1,
        fe(entity),
        cap,
    );
    let _ = host.set_block_property(pos, "lit", if working { "true" } else { "false" });
}

fn tick_processor(host: &mut dyn Host, pos: [i32; 3], entity: &mut ModBlockEntity, spec: &Spec) {
    let Some(recipe_type) = spec.recipe_type else {
        return;
    };
    let Some(out_slot) = spec.output else {
        return;
    };
    let need = out_slot + 1;
    if entity.items.len() < need {
        entity.items.resize(need, None);
    }
    transfer_fe_in(host, pos, entity, spec);
    let recipes = recipes::load(host, recipe_type);
    let matched = find_recipe(entity, &recipes, spec.inputs, out_slot);
    let (mut prog, _) = progress(entity);
    let mut prog_max = 1;
    let mut working = false;
    if let Some(recipe) = matched {
        prog_max = recipe.duration;
        let cost = recipe.fe.max(1).max(spec.fe_rate / 2).max(1);
        let have = fe(entity);
        if have >= cost {
            set_fe(entity, have - cost, spec.fe_cap);
            prog += 1;
            working = true;
            if prog >= recipe.duration {
                for i in 0..spec.inputs {
                    shrink(&mut entity.items[i]);
                }
                merge_output(&mut entity.items[out_slot], &recipe.output);
                prog = 0;
            }
        } else {
            prog = 0;
        }
    } else {
        prog = 0;
    }
    set_progress(entity, prog, prog_max.max(1));
    // Push surplus FE to neighbours so generator → loader/processor chains work from data rates.
    transfer_fe_out(host, pos, entity, spec);
    sync_data(entity, prog, prog_max.max(1), fe(entity), spec.fe_cap);
    let _ = host.set_block_property(pos, "lit", if working { "true" } else { "false" });
}

fn tick_distributor(host: &mut dyn Host, pos: [i32; 3], entity: &mut ModBlockEntity, spec: &Spec) {
    if entity.items.len() < 1 {
        entity.items.resize(1, None);
    }
    transfer_fe_in(host, pos, entity, spec);
    let mut working = false;
    let rate = spec.fe_rate.max(1);
    let has_tank = entity
        .items
        .first()
        .and_then(|s| s.as_ref())
        .is_some_and(|s| s.item.as_ref() == "adastra:oxygen_tank");
    if has_tank && fe(entity) >= rate {
        set_fe(entity, fe(entity) - rate, spec.fe_cap);
        working = true;
        // Mark distributor as active for player_tick vacuum checks via NBT.
        entity.nbt.insert("Active".into(), horizon_client::mod_api::Tag::Int(1));
    } else {
        entity.nbt.insert("Active".into(), horizon_client::mod_api::Tag::Int(0));
    }
    sync_data(
        entity,
        if working { 1 } else { 0 },
        1,
        fe(entity),
        spec.fe_cap,
    );
    let _ = host.set_block_property(pos, "lit", if working { "true" } else { "false" });
    let _ = pos;
}

fn find_recipe<'a>(
    entity: &ModBlockEntity,
    recipes: &'a [MachineRecipe],
    in_slots: usize,
    out_slot: usize,
) -> Option<&'a MachineRecipe> {
    for recipe in recipes {
        if recipe.inputs.len() != in_slots {
            continue;
        }
        let mut ok = true;
        for (i, ing) in recipe.inputs.iter().enumerate() {
            match &entity.items[i] {
                Some(stack) if stack.count > 0 && ingredient_accepts(ing, stack.item.as_ref()) => {}
                _ => {
                    ok = false;
                    break;
                }
            }
        }
        if !ok || !can_output(&entity.items[out_slot], &recipe.output) {
            continue;
        }
        return Some(recipe);
    }
    None
}

/// True when a distributor at `pos` is actively bubbling oxygen.
pub fn distributor_active(entity: &ModBlockEntity) -> bool {
    matches!(
        entity.nbt.get(&"Active".into()),
        Some(horizon_client::mod_api::Tag::Int(1))
    )
}
