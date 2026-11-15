//! Fuel and recipe progress for firepit, forge, kiln, and the other benches.

use crate::recipes::{self, can_output, ingredient_accepts, merge_output, MachineRecipe};
use crate::registry::Spec;
use horizon_client::mod_api::{Host, ModBlockEntity, Tag};

fn nbt_i32(entity: &ModBlockEntity, key: &str) -> i32 {
    match entity.nbt.get(&key.into()) {
        Some(Tag::Int(value)) => *value,
        _ => 0,
    }
}

fn nbt_set(entity: &mut ModBlockEntity, key: &str, value: i32) {
    entity.nbt.insert(key.into(), Tag::Int(value));
}

fn is_fuel(item: &str) -> bool {
    item == "minecraft:coal"
        || item == "minecraft:charcoal"
        || (item.starts_with("minecraft:") && item.ends_with("_log"))
}

fn burn_time(item: &str) -> i32 {
    if item.ends_with("_log") { 300 } else { 1_600 }
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

/// Returns whether the machine has heat this tick. Fuel machines consume slot 0.
fn feed_fuel(entity: &mut ModBlockEntity) -> bool {
    let burn = nbt_i32(entity, "Burn");
    if burn > 0 {
        nbt_set(entity, "Burn", burn - 1);
        return true;
    }
    let Some(stack) = entity.items.first().and_then(|slot| slot.as_ref()) else {
        return false;
    };
    let item = stack.item.as_ref().to_owned();
    if !is_fuel(&item) {
        return false;
    }
    let time = burn_time(&item);
    shrink(&mut entity.items[0]);
    nbt_set(entity, "Burn", time);
    nbt_set(entity, "BurnMax", time);
    true
}

fn find_recipe<'a>(
    entity: &ModBlockEntity,
    recipes: &'a [MachineRecipe],
    start: usize,
    inputs: usize,
    out_slot: usize,
) -> Option<&'a MachineRecipe> {
    for recipe in recipes {
        if recipe.inputs.len() != inputs {
            continue;
        }
        let fits = recipe.inputs.iter().enumerate().all(|(index, ingredient)| {
            entity
                .items
                .get(start + index)
                .and_then(|slot| slot.as_ref())
                .is_some_and(|stack| ingredient_accepts(ingredient, stack.item.as_ref()))
        });
        if !fits {
            continue;
        }
        if entity
            .items
            .get(out_slot)
            .is_some_and(|slot| can_output(slot, &recipe.output))
        {
            return Some(recipe);
        }
    }
    None
}

pub fn tick(host: &mut dyn Host, entity: &mut ModBlockEntity, spec: &Spec) {
    let (Some(recipe_type), Some(out_slot)) = (spec.recipe_type, spec.output) else {
        return;
    };
    let need = out_slot + 1;
    if entity.items.len() < need {
        entity.items.resize(need, None);
    }
    let hot = if spec.fuel { feed_fuel(entity) } else { true };
    let recipes = recipes::load(host, recipe_type);
    let start = if spec.fuel { 1 } else { 0 };
    let matched = if hot {
        find_recipe(entity, &recipes, start, spec.inputs, out_slot)
    } else {
        None
    };
    let mut progress = nbt_i32(entity, "Progress");
    let mut progress_max = 1;
    if let Some(recipe) = matched {
        progress_max = recipe.duration.max(1);
        progress += 1;
        if progress >= recipe.duration {
            for index in 0..spec.inputs {
                shrink(&mut entity.items[start + index]);
            }
            merge_output(&mut entity.items[out_slot], &recipe.output);
            progress = 0;
        }
    } else {
        progress = 0;
    }
    nbt_set(entity, "Progress", progress);
    nbt_set(entity, "ProgressMax", progress_max);
    if entity.data.len() < 4 {
        entity.data.resize(4, 0);
    }
    let burn = nbt_i32(entity, "Burn").max(0);
    let burn_max = nbt_i32(entity, "BurnMax").max(1);
    entity.data[0] = progress;
    entity.data[1] = progress_max;
    entity.data[2] = if spec.fuel { burn } else { progress };
    entity.data[3] = if spec.fuel { burn_max } else { progress_max };
}
