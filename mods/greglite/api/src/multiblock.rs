//! Coke oven, EBF, vacuum freezer, and N8 hatch-shell multis
//! (distillation / cracker / LCR / cleanroom).
//! A controller with an incomplete shell does nothing.

use crate::energy::{eu, set_eu, set_packet_voltage};
use crate::eu_rules::{self, ShellKind, ShellScan};
use crate::fluids::{self, CREOSOTE};
use crate::recipes::{self, merge_output};
use crate::registry::{self, Spec};
use horizon_client::mod_api::{Host, ModBlockEntity, Tag};

const CREOSOTE_MB: i32 = 500;
const TANK: i32 = 16_000;

fn block_at(host: &mut dyn Host, pos: [i32; 3]) -> String {
    let dim = host.dimension();
    let Some(level) = host.level(dim) else {
        return "minecraft:air".to_owned();
    };
    level
        .block(host, pos)
        .unwrap_or_else(|| "minecraft:air".to_owned())
}

fn scan(host: &mut dyn Host, origin: [i32; 3], kind: ShellKind) -> Option<ShellScan> {
    // Prefetch so scan_shell's Fn does not need &mut Host.
    let mut map = std::collections::HashMap::new();
    for dz in -2..=2 {
        for dy in -2..=2 {
            for dx in -2..=2 {
                let pos = [origin[0] + dx, origin[1] + dy, origin[2] + dz];
                map.insert(pos, block_at(host, pos));
            }
        }
    }
    eu_rules::scan_shell(
        origin,
        &|pos| {
            map.get(&pos)
                .cloned()
                .unwrap_or_else(|| "minecraft:air".to_owned())
        },
        kind,
    )
}

fn item_count(entity: &ModBlockEntity, slot: usize, item: &str) -> u32 {
    entity
        .items
        .get(slot)
        .and_then(|s| s.as_ref())
        .filter(|stack| stack.item.as_ref() == item)
        .map(|stack| stack.count)
        .unwrap_or(0)
}

fn consume(entity: &mut ModBlockEntity, slot: usize) {
    if let Some(stack) = entity.items.get_mut(slot).and_then(|s| s.as_mut()) {
        stack.count = stack.count.saturating_sub(1);
        if stack.count == 0 {
            entity.items[slot] = None;
        }
    }
}

pub fn tick_coke(host: &mut dyn Host, pos: [i32; 3], entity: &mut ModBlockEntity, spec: &Spec) {
    if entity.items.len() < 2 {
        entity.items.resize(2, None);
    }
    let formed = scan(host, pos, ShellKind::Coke).is_some();
    entity.nbt.insert("Formed".into(), Tag::Int(if formed { 1 } else { 0 }));
    if !formed {
        let _ = host.set_block_property(pos, "lit", "false");
        return;
    }
    let (mut prog, _) = crate::energy::progress(entity);
    let duration = 200;
    let ready = item_count(entity, 0, "minecraft:coal") > 0
        || item_count(entity, 0, "minecraft:charcoal") > 0;
    let room = entity.items.get(1).and_then(|s| s.as_ref()).is_none_or(|stack| {
        stack.item.as_ref() == "greglite:coke" && stack.count < 64
    });
    let mut working = false;
    if ready && room {
        prog += 1;
        working = true;
        if prog >= duration {
            consume(entity, 0);
            let stack = horizon_client::mod_api::ItemStack::new("greglite:coke", 1);
            merge_output(&mut entity.items[1], &stack);
            let _ = fluids::fill(entity, 0, 1, CREOSOTE, CREOSOTE_MB, TANK);
            prog = 0;
        }
    } else {
        prog = 0;
    }
    crate::energy::set_progress(entity, prog, duration);
    crate::energy::sync_data(entity, prog, duration, fluids::amount(entity, 0, CREOSOTE), TANK);
    let _ = host.set_block_property(pos, "lit", if working { "true" } else { "false" });
    let _ = spec;
}

pub fn tick_ebf(host: &mut dyn Host, pos: [i32; 3], entity: &mut ModBlockEntity, spec: &Spec) {
    tick_hatch_machine(host, pos, entity, spec, ShellKind::Ebf, "greglite:electric_blast_furnace", true);
}

pub fn tick_freezer(host: &mut dyn Host, pos: [i32; 3], entity: &mut ModBlockEntity, spec: &Spec) {
    tick_hatch_machine(host, pos, entity, spec, ShellKind::Freezer, "greglite:vacuum_freezer", false);
}

pub fn tick_distillation(host: &mut dyn Host, pos: [i32; 3], entity: &mut ModBlockEntity, spec: &Spec) {
    tick_hatch_machine(host, pos, entity, spec, ShellKind::Distillation, "greglite:distillation_tower", false);
}

pub fn tick_cracker(host: &mut dyn Host, pos: [i32; 3], entity: &mut ModBlockEntity, spec: &Spec) {
    tick_hatch_machine(host, pos, entity, spec, ShellKind::Cracker, "greglite:cracker", false);
}

pub fn tick_lcr(host: &mut dyn Host, pos: [i32; 3], entity: &mut ModBlockEntity, spec: &Spec) {
    tick_hatch_machine(host, pos, entity, spec, ShellKind::Lcr, "greglite:large_chemical_reactor", false);
}

pub fn tick_cleanroom(host: &mut dyn Host, pos: [i32; 3], entity: &mut ModBlockEntity, spec: &Spec) {
    tick_hatch_machine(host, pos, entity, spec, ShellKind::Cleanroom, "greglite:cleanroom", false);
}

fn tick_hatch_machine(
    host: &mut dyn Host,
    pos: [i32; 3],
    entity: &mut ModBlockEntity,
    spec: &Spec,
    kind: ShellKind,
    recipe_type: &str,
    use_heat: bool,
) {
    let Some(shell) = scan(host, pos, kind) else {
        entity.nbt.insert("Formed".into(), Tag::Int(0));
        crate::energy::set_progress(entity, 0, 1);
        let _ = host.set_block_property(pos, "lit", "false");
        return;
    };
    entity.nbt.insert("Formed".into(), Tag::Int(1));
    if use_heat {
        entity.nbt.insert("Heat".into(), Tag::Int(shell.heat));
    }
    if let Some(hatch) = shell.energy_hatch {
        pull_eu(host, hatch, entity, spec);
    }
    let Some(input_pos) = shell.input_hatch else {
        return;
    };
    let Some(output_pos) = shell.output_hatch else {
        return;
    };
    let recipes = recipes::load(host, recipe_type);
    let mut working = false;
    let (mut prog, _) = crate::energy::progress(entity);
    let mut prog_max = 1;
    let mut snapshot_in = None;
    let _ = host.change_mod_block_entity(input_pos, &mut |hatch| {
        snapshot_in = Some(hatch.items.clone());
    });
    let inputs = snapshot_in.unwrap_or_default();
    if let Some(recipe) = recipes.iter().find(|recipe| {
        (!use_heat || (recipe.heat > 0 && recipe.heat <= shell.heat))
            && recipe.inputs.len() <= 2
            && recipe.inputs.iter().enumerate().all(|(i, ing)| {
                inputs.get(i).and_then(|s| s.as_ref()).is_some_and(|stack| {
                    stack.count > 0 && recipes::ingredient_accepts(ing, stack.item.as_ref())
                })
            })
            && eu_rules::overclock(recipe.min_voltage, spec.voltage.max(32), 1, 1).is_some()
    }) {
        let (duration, eu_cost) = eu_rules::overclock(
            recipe.min_voltage,
            spec.voltage.max(32),
            recipe.duration,
            recipe.eu.max(1),
        )
        .unwrap_or((recipe.duration, recipe.eu.max(1)));
        prog_max = duration;
        if eu(entity) >= eu_cost {
            set_eu(entity, eu(entity) - eu_cost, spec.gauge_cap());
            set_packet_voltage(entity, spec.voltage);
            prog += 1;
            working = true;
            if prog >= duration {
                let mut placed = false;
                let output = recipe.outputs.first().map(|o| o.stack.clone());
                if let Some(output) = output {
                    let _ = host.change_mod_block_entity(output_pos, &mut |hatch| {
                        if hatch.items.is_empty() {
                            hatch.items.push(None);
                        }
                        if recipes::can_output(&hatch.items[0], &output) {
                            merge_output(&mut hatch.items[0], &output);
                            placed = true;
                        }
                    });
                }
                if placed {
                    let _ = host.change_mod_block_entity(input_pos, &mut |hatch| {
                        for i in 0..recipe.inputs.len() {
                            if let Some(stack) = hatch.items.get_mut(i).and_then(|s| s.as_mut()) {
                                stack.count = stack.count.saturating_sub(1);
                                if stack.count == 0 {
                                    hatch.items[i] = None;
                                }
                            }
                        }
                    });
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
    }
    crate::energy::set_progress(entity, prog, prog_max.max(1));
    crate::energy::sync_data(entity, prog, prog_max.max(1), eu(entity), spec.gauge_cap());
    let _ = host.set_block_property(pos, "lit", if working { "true" } else { "false" });
}

fn pull_eu(host: &mut dyn Host, hatch: [i32; 3], entity: &mut ModBlockEntity, spec: &Spec) {
    let mut moved = 0;
    let room = spec.gauge_cap() - eu(entity);
    if room <= 0 {
        return;
    }
    let _ = host.change_mod_block_entity(hatch, &mut |other| {
        if !registry::find(&other.id).is_some_and(|s| s.eu_ok) {
            return;
        }
        let have = eu(other);
        let take = have.min(room).min(spec.voltage.max(32));
        if take <= 0 {
            return;
        }
        let cap = registry::find(&other.id).map(|s| s.gauge_cap()).unwrap_or(have);
        set_eu(other, have - take, cap);
        moved = take;
    });
    if moved > 0 {
        set_eu(entity, eu(entity) + moved, spec.gauge_cap());
        set_packet_voltage(entity, spec.voltage);
    }
}
