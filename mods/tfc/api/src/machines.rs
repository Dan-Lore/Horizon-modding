//! Tick processors for TFC machines (heat / forge / anvil / barrel / …).

use crate::recipes::{self, can_output, ingredient_accepts, merge_output, MachineRecipe};
use crate::registry::Spec;
use horizon_client::mod_api::{Host, ModBlockEntity};

fn progress(entity: &ModBlockEntity) -> (i32, i32) {
    if entity.data.len() >= 2 {
        (entity.data[0], entity.data[1].max(1))
    } else {
        (0, 1)
    }
}

fn set_progress(entity: &mut ModBlockEntity, prog: i32, max: i32) {
    if entity.data.len() < 2 {
        entity.data.resize(2, 0);
    }
    entity.data[0] = prog;
    entity.data[1] = max.max(1);
}

pub fn tick(_host: &mut dyn Host, _pos: [i32; 3], entity: &mut ModBlockEntity, spec: &Spec) {
    let Some(recipe_type) = spec.recipe_type else {
        return;
    };
    let out_slot = match spec.output {
        Some(o) => o,
        None => return,
    };
    let need = out_slot + 1;
    if entity.items.len() < need {
        entity.items.resize(need, None);
    }

    let recipes = recipes::load(_host, recipe_type);
    let matched = find_recipe(entity, &recipes, spec.inputs, out_slot);

    let (mut prog, _) = progress(entity);
    let mut prog_max = 1;

    if let Some(recipe) = matched {
        prog_max = recipe.duration;
        prog += 1;
        if prog >= recipe.duration {
            consume_inputs(entity, spec.inputs);
            merge_output(&mut entity.items[out_slot], &recipe.output);
            prog = 0;
        }
    } else {
        prog = 0;
    }

    set_progress(entity, prog, prog_max);
}

fn find_recipe<'a>(
    entity: &ModBlockEntity,
    recipes: &'a [MachineRecipe],
    inputs: usize,
    out_slot: usize,
) -> Option<&'a MachineRecipe> {
    for recipe in recipes {
        if recipe.inputs.len() != inputs {
            continue;
        }
        let mut ok = true;
        for (i, ing) in recipe.inputs.iter().enumerate() {
            let Some(stack) = entity.items.get(i).and_then(|s| s.as_ref()) else {
                ok = false;
                break;
            };
            if !ingredient_accepts(ing, stack.item.as_ref()) {
                ok = false;
                break;
            }
        }
        if !ok {
            continue;
        }
        if !can_output(&entity.items[out_slot], &recipe.output) {
            continue;
        }
        return Some(recipe);
    }
    None
}

fn consume_inputs(entity: &mut ModBlockEntity, inputs: usize) {
    for i in 0..inputs {
        if let Some(stack) = entity.items.get_mut(i).and_then(|s| s.as_mut()) {
            if stack.count <= 1 {
                entity.items[i] = None;
            } else {
                stack.count -= 1;
            }
        }
    }
}
