//! Shared steam / EU processing machines.

use crate::energy::{
    eu, progress, set_eu, set_progress, set_steam, steam, sync_data, STEAM_CAP,
};
use crate::net::{transfer_eu_in, transfer_steam_in};
use crate::recipes::{self, can_output, ingredient_accepts, merge_output, MachineRecipe};
use crate::registry::{Kind, Spec};
use horizon_client::mod_api::{Host, ModBlockEntity};

pub fn tick(host: &mut dyn Host, pos: [i32; 3], entity: &mut ModBlockEntity, spec: &Spec) {
    let Some(recipe_type) = spec.recipe_type.as_deref() else {
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

    match spec.kind {
        Kind::SteamProcessor => transfer_steam_in(host, pos, entity),
        Kind::EuProcessor | Kind::Multiblock => transfer_eu_in(host, pos, entity, spec),
        _ => {}
    }

    let recipes = recipes::load(host, recipe_type);
    let matched = find_recipe(entity, &recipes, spec.inputs, out_slot);

    let (mut prog, _) = progress(entity);
    let mut prog_max = 1;
    let mut working = false;

    if let Some(recipe) = matched {
        prog_max = recipe.duration;
        let paid = match spec.kind {
            Kind::SteamProcessor => {
                let cost = recipe.steam.max(1);
                let have = steam(entity);
                if have >= cost {
                    set_steam(entity, have - cost);
                    true
                } else {
                    false
                }
            }
            Kind::EuProcessor | Kind::Multiblock => {
                // GTM-like: consume ~tier voltage as EU/t (recipe.eu scales lightly).
                let cost = recipe.eu.max(1).max(spec.voltage / 16).max(1);
                let have = eu(entity);
                let cap = spec.gauge_cap();
                if have >= cost {
                    set_eu(entity, have - cost, cap);
                    true
                } else {
                    false
                }
            }
            _ => false,
        };
        if paid {
            prog += 1;
            working = true;
            if prog >= recipe.duration {
                consume_inputs(entity, spec.inputs);
                merge_output(&mut entity.items[out_slot], &recipe.output);
                prog = 0;
            }
        } else {
            prog = 0;
        }
    } else {
        prog = 0;
        prog_max = 1;
    }

    set_progress(entity, prog, prog_max.max(1));
    let (gauge, cap) = match spec.kind {
        Kind::SteamProcessor => (steam(entity), STEAM_CAP),
        Kind::EuProcessor | Kind::Multiblock => (eu(entity), spec.gauge_cap()),
        _ => (eu(entity), spec.gauge_cap()),
    };
    sync_data(entity, prog, prog_max.max(1), gauge, cap);
    let _ = host.set_block_property(pos, "lit", if working { "true" } else { "false" });
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

fn consume_inputs(entity: &mut ModBlockEntity, in_slots: usize) {
    for i in 0..in_slots {
        if let Some(stack) = entity.items[i].as_mut() {
            stack.count = stack.count.saturating_sub(1);
            if stack.count == 0 {
                entity.items[i] = None;
            }
        }
    }
}
