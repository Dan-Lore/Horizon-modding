//! Shared steam / EU processing machines.

use crate::energy::{eu, progress, set_eu, set_packet_voltage, set_progress, set_steam, steam, sync_data, STEAM_CAP};
use crate::eu_rules;
use crate::fluids::{self, STEAM};
use crate::net::transfer_eu_in;
use crate::recipes::{self, can_output, ingredient_accepts, merge_output, MachineRecipe};
use crate::registry::{Kind, Spec};
use crate::world_machines;
use horizon_client::mod_api::{Host, ModBlockEntity};

const STEAM_TANK: i32 = 16_000;

pub fn tick(host: &mut dyn Host, pos: [i32; 3], entity: &mut ModBlockEntity, spec: &Spec) {
    let Some(recipe_type) = spec.recipe_type.as_deref() else {
        return;
    };
    let first_out = spec.output.unwrap_or(0);
    let need = spec.slots();
    if entity.items.len() < need {
        entity.items.resize(need, None);
    }

    match spec.kind {
        Kind::SteamProcessor => {
            fluids::pull_from_neighbours(host, pos, entity, 0, 1, STEAM, STEAM_TANK, 500);
        }
        Kind::EuProcessor | Kind::Multiblock => transfer_eu_in(host, pos, entity, spec),
        _ => {}
    }

    let recipes = recipes::load(host, recipe_type);
    let matched = find_recipe(entity, &recipes, spec);

    let (mut prog, _) = progress(entity);
    let mut prog_max = 1;
    let mut working = false;

    if let Some(recipe) = matched {
        let (duration, eu_cost) = if spec.kind == Kind::SteamProcessor {
            (recipe.duration.max(1), recipe.eu.max(1))
        } else {
            match eu_rules::overclock(
                recipe.min_voltage,
                spec.voltage.max(1),
                recipe.duration,
                recipe.eu.max(1),
            ) {
                Some(scaled) => scaled,
                None => {
                    set_progress(entity, 0, 1);
                    return;
                }
            }
        };
        prog_max = duration;
        let paid = match spec.kind {
            Kind::SteamProcessor => {
                let cost = recipe.steam.max(1);
                let have = fluids::amount(entity, 0, STEAM);
                if have >= cost {
                    let _ = fluids::drain(entity, 0, 1, STEAM, cost);
                    true
                } else if steam(entity) >= cost {
                    set_steam(entity, steam(entity) - cost);
                    true
                } else {
                    false
                }
            }
            Kind::EuProcessor | Kind::Multiblock => {
                let have = eu(entity);
                let cap = spec.gauge_cap();
                if have >= eu_cost {
                    set_eu(entity, have - eu_cost, cap);
                    set_packet_voltage(entity, spec.voltage);
                    true
                } else {
                    false
                }
            }
            _ => false,
        };
        let fluids_ok = fluid_ready(entity, recipe);
        if paid && fluids_ok {
            prog += 1;
            working = true;
            if prog >= duration {
                if complete_fluids(entity, recipe) {
                    consume_inputs(entity, item_inputs(spec));
                    let roll = pos[0]
                        .wrapping_mul(31)
                        .wrapping_add(pos[1].wrapping_mul(17))
                        .wrapping_add(pos[2]);
                    for (i, output) in recipe.outputs.iter().enumerate() {
                        if !eu_rules::chance_passes(roll.wrapping_add(i as i32), output.chance) {
                            continue;
                        }
                        let slot = first_out + i;
                        if entity.items.len() > slot {
                            merge_output(&mut entity.items[slot], &output.stack);
                        }
                    }
                    prog = 0;
                } else {
                    prog = duration - 1;
                    working = false;
                }
            }
        } else {
            prog = 0;
        }
    } else {
        prog = 0;
        prog_max = 1;
    }

    set_progress(entity, prog, prog_max.max(1));
    // World-touching machines: miner breaks ores; pump fills water (EU cost inside).
    world_machines::tick_miner(host, pos, entity, spec);
    world_machines::tick_pump(host, pos, entity, spec);
    let (gauge, cap) = match spec.kind {
        Kind::SteamProcessor => (fluids::amount(entity, 0, STEAM).max(steam(entity)), STEAM_CAP),
        Kind::EuProcessor | Kind::Multiblock => (eu(entity), spec.gauge_cap()),
        _ => (eu(entity), spec.gauge_cap()),
    };
    sync_data(entity, prog, prog_max.max(1), gauge, cap);
    let _ = host.set_block_property(pos, "lit", if working { "true" } else { "false" });
}

fn item_inputs(spec: &Spec) -> usize {
    if spec.circuit.is_some() {
        spec.inputs.saturating_sub(1)
    } else {
        spec.inputs
    }
}

fn circuit_ok(entity: &ModBlockEntity, spec: &Spec, recipe: &MachineRecipe) -> bool {
    let Some(slot) = spec.circuit else {
        return recipe.circuit.is_none();
    };
    let have = entity.items.get(slot).and_then(|s| s.as_ref());
    match recipe.circuit {
        None => have.is_none(),
        Some(n) => have.is_some_and(|stack| {
            stack.item.as_ref() == format!("greglite:programmed_circuit_{n}")
                || (stack.item.as_ref() == "greglite:programmed_circuit" && stack.count == n as u32)
        }),
    }
}

fn fluid_ready(entity: &ModBlockEntity, recipe: &MachineRecipe) -> bool {
    let Some((id, amount)) = recipe.fluid_in.as_ref() else {
        return true;
    };
    fluids::amount(entity, 0, id) >= *amount
}

fn complete_fluids(entity: &mut ModBlockEntity, recipe: &MachineRecipe) -> bool {
    if let Some((id, amount)) = recipe.fluid_out.as_ref() {
        if !fluids::can_fill(entity, 1, id, *amount, STEAM_TANK) {
            return false;
        }
    }
    if let Some((id, amount)) = recipe.fluid_in.as_ref() {
        if fluids::drain(entity, 0, 2, id, *amount) < *amount {
            return false;
        }
    }
    if let Some((id, amount)) = recipe.fluid_out.as_ref() {
        let left = fluids::fill(entity, 1, 2, id, *amount, STEAM_TANK);
        if left > 0 {
            return false;
        }
    }
    true
}

fn find_recipe<'a>(
    entity: &ModBlockEntity,
    recipes: &'a [MachineRecipe],
    spec: &Spec,
) -> Option<&'a MachineRecipe> {
    let item_slots = item_inputs(spec);
    let first_out = spec.output.unwrap_or(0);
    for recipe in recipes {
        let fluid_only = recipe.inputs.is_empty() && recipe.fluid_in.is_some();
        if recipe.inputs.len() != item_slots && !fluid_only {
            continue;
        }
        if recipe.heat > 0 {
            continue;
        }
        if spec.kind != Kind::SteamProcessor
            && eu_rules::overclock(recipe.min_voltage, spec.voltage.max(1), 1, 1).is_none()
        {
            continue;
        }
        if !circuit_ok(entity, spec, recipe) {
            continue;
        }
        let mut ok = true;
        for (i, ing) in recipe.inputs.iter().enumerate() {
            match entity.items.get(i).and_then(|s| s.as_ref()) {
                Some(stack) if stack.count > 0 && ingredient_accepts(ing, stack.item.as_ref()) => {}
                _ => {
                    ok = false;
                    break;
                }
            }
        }
        if !ok {
            continue;
        }
        let mut outputs_fit = true;
        for (i, output) in recipe.outputs.iter().enumerate() {
            let slot = entity.items.get(first_out + i).cloned().unwrap_or(None);
            if !can_output(&slot, &output.stack) {
                outputs_fit = false;
                break;
            }
        }
        if outputs_fit {
            return Some(recipe);
        }
    }
    None
}

fn consume_inputs(entity: &mut ModBlockEntity, in_slots: usize) {
    for i in 0..in_slots {
        if let Some(stack) = entity.items.get_mut(i).and_then(|s| s.as_mut()) {
            stack.count = stack.count.saturating_sub(1);
            if stack.count == 0 {
                entity.items[i] = None;
            }
        }
    }
}
