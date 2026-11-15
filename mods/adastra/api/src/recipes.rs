//! Custom `adastra:*` recipes with content-matching fallbacks.

use horizon_client::mod_api::serde_json::Value;
use horizon_client::mod_api::{Host, Ingredient, ItemStack};
use std::collections::HashSet;
use std::sync::Arc;

#[derive(Clone, Debug)]
pub struct MachineRecipe {
    pub inputs: Vec<Ingredient>,
    pub output: ItemStack,
    pub duration: i32,
    pub fe: i32,
}

pub fn stack(id: &str, count: u32) -> ItemStack {
    ItemStack {
        item: Arc::from(id),
        count,
        damage: 0,
        extra: None,
    }
}

pub fn load(host: &dyn Host, kind: &str) -> Vec<MachineRecipe> {
    let mut out = Vec::new();
    for recipe in host.recipes_of_type(kind) {
        let Some(parsed) = parse(host, &recipe.json) else {
            continue;
        };
        out.push(parsed);
    }
    if out.is_empty() {
        out.extend(fallback(kind));
    }
    out
}

fn parse(host: &dyn Host, json: &Value) -> Option<MachineRecipe> {
    let duration = json.get("duration").and_then(|v| v.as_i64()).unwrap_or(100) as i32;
    let fe = json.get("fe").and_then(|v| v.as_i64()).unwrap_or(16) as i32;
    let output = host.recipe_result(json.get("result")?)?;
    let mut inputs = Vec::new();
    if let Some(arr) = json.get("ingredients").and_then(|v| v.as_array()) {
        for entry in arr {
            inputs.push(host.recipe_ingredient(entry)?);
        }
    } else if let Some(one) = json.get("ingredient") {
        inputs.push(host.recipe_ingredient(one)?);
    } else {
        return None;
    }
    if inputs.is_empty() {
        return None;
    }
    Some(MachineRecipe {
        inputs,
        output,
        duration: duration.max(1),
        fe: fe.max(1),
    })
}

fn item_ing(id: &str) -> Ingredient {
    let mut items = HashSet::new();
    items.insert(id.to_owned());
    Ingredient {
        items,
        order: vec![id.to_owned()],
        custom: None,
        children: None,
    }
}

fn one(input: &str, output: &str, duration: i32, fe: i32) -> MachineRecipe {
    MachineRecipe {
        inputs: vec![item_ing(input)],
        output: stack(output, 1),
        duration,
        fe,
    }
}

fn fallback(kind: &str) -> Vec<MachineRecipe> {
    match kind {
        "adastra:compressor" => vec![
            one("adastra:desh_ingot", "adastra:desh_plate", 100, 32),
            one("adastra:steel_ingot", "adastra:steel_plate", 100, 32),
            one("adastra:ostrum_ingot", "adastra:ostrum_plate", 120, 40),
            one("adastra:calorite_ingot", "adastra:calorite_plate", 140, 48),
        ],
        "adastra:oxygen_loader" => vec![one(
            "adastra:oxygen_tank_empty",
            "adastra:oxygen_tank",
            80,
            16,
        )],
        "adastra:fuel_refinery" => vec![one("adastra:oil", "adastra:rocket_fuel", 160, 24)],
        "adastra:cryo_freezer" => vec![
            one("minecraft:ice", "adastra:ice_shard", 100, 16),
            one("minecraft:blue_ice", "adastra:ice_shard", 60, 12),
        ],
        _ => Vec::new(),
    }
}

pub fn ingredient_accepts(ing: &Ingredient, item: &str) -> bool {
    ing.items.contains(item)
}

pub fn can_output(slot: &Option<ItemStack>, want: &ItemStack) -> bool {
    match slot {
        None => true,
        Some(have) => have.item == want.item && have.count.saturating_add(want.count) <= 64,
    }
}

pub fn merge_output(slot: &mut Option<ItemStack>, want: &ItemStack) {
    match slot {
        Some(have) if have.item == want.item => {
            have.count = have.count.saturating_add(want.count);
        }
        _ => *slot = Some(stack(want.item.as_ref(), want.count)),
    }
}
