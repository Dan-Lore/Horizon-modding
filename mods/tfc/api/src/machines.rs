//! Workstation tick — progress toward table-driven recipes.

use crate::registry::{self, Kind, Spec};
use horizon_client::mod_api::{Host, ItemStack, ModBlockEntity};

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

fn duration_for(kind: Kind) -> i32 {
    match kind {
        Kind::Firepit | Kind::Forge => 200,
        Kind::PitKiln => 800,
        Kind::Bloomery | Kind::BlastFurnace => 1200,
        Kind::Anvil => 40,
        Kind::Quern => 100,
        Kind::Barrel => 400,
        Kind::Sluice => 80,
        _ => 100,
    }
}

pub fn tick(host: &mut dyn Host, pos: [i32; 3], entity: &mut ModBlockEntity, spec: &Spec) {
    match spec.kind {
        Kind::LogPile | Kind::Support | Kind::Powderkeg => return,
        _ => {}
    }

    let need = spec.output.unwrap_or(0) + 1;
    if entity.items.len() < need {
        entity.items.resize(need, None);
    }

    let input_ok = entity.items.first().and_then(|s| s.as_ref()).is_some();
    let (mut prog, _) = progress(entity);
    let max = duration_for(spec.kind);

    if input_ok {
        prog += 1;
        if prog >= max {
            let input_id = entity.items[0]
                .as_ref()
                .map(|s| s.item.as_ref().to_string())
                .unwrap_or_default();
            if let Some(slot) = entity.items.get_mut(0) {
                if let Some(stack) = slot.as_mut() {
                    stack.count = stack.count.saturating_sub(1);
                    if stack.count == 0 {
                        *slot = None;
                    }
                }
            }
            if let Some(out_i) = spec.output {
                if entity.items[out_i].is_none() {
                    let out_item = guess_output(spec.kind, &input_id);
                    entity.items[out_i] = Some(ItemStack::new(out_item, 1));
                }
            }
            prog = 0;
        }
        let _ = host.set_block_property(pos, "lit", "true");
    } else {
        prog = 0;
        let _ = host.set_block_property(pos, "lit", "false");
    }
    set_progress(entity, prog, max);
}

fn guess_output(kind: Kind, input: &str) -> &'static str {
    match kind {
        Kind::PitKiln => {
            if input.contains("unfired_vessel") {
                "tfc:ceramic_vessel"
            } else if input.contains("unfired_jug") {
                "tfc:ceramic_jug"
            } else if input.contains("unfired_ingot_mold") {
                "tfc:ceramic_ingot_mold"
            } else {
                "tfc:ceramic_vessel"
            }
        }
        Kind::Firepit | Kind::Forge => "tfc:copper_ingot",
        Kind::Bloomery | Kind::BlastFurnace => "tfc:wrought_iron_ingot",
        Kind::Anvil => "tfc:copper_pickaxe_head",
        Kind::Quern => "tfc:powder_flux",
        Kind::Barrel => "tfc:straw",
        Kind::Sluice => "tfc:nugget_copper",
        _ => "minecraft:air",
    }
}

pub fn tick_if_ours(host: &mut dyn Host, pos: [i32; 3], entity: &mut ModBlockEntity) {
    if let Some(spec) = registry::find(&entity.id) {
        tick(host, pos, entity, spec);
    }
}
