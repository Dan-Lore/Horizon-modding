//! Custom `tfc:*` recipes, with the same fallbacks the content generator writes.

use horizon_client::mod_api::serde_json::Value;
use horizon_client::mod_api::{Host, Ingredient, ItemStack};
use std::collections::HashSet;
use std::sync::Arc;

#[derive(Clone, Debug)]
pub struct MachineRecipe {
    pub inputs: Vec<Ingredient>,
    pub output: ItemStack,
    pub duration: i32,
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

fn one(input: &str, output: &str, duration: i32) -> MachineRecipe {
    MachineRecipe {
        inputs: vec![item_ing(input)],
        output: stack(output, 1),
        duration,
    }
}

fn fallback(kind: &str) -> Vec<MachineRecipe> {
    match kind {
        "tfc:firepit" => vec![
            one("minecraft:beef", "tfc:cooked_meat", 120),
            one("minecraft:porkchop", "tfc:cooked_meat", 120),
            one("tfc:dough", "tfc:bread", 120),
        ],
        "tfc:charcoal_forge" => vec![
            one("tfc:nugget_native_copper", "tfc:copper_ingot", 160),
            one("tfc:nugget_malachite", "tfc:copper_ingot", 160),
            one("tfc:nugget_cassiterite", "tfc:tin_ingot", 140),
            one("tfc:nugget_bismuthinite", "tfc:bismuth_ingot", 120),
            one("tfc:nugget_sphalerite", "tfc:zinc_ingot", 140),
            one("tfc:nugget_native_silver", "tfc:silver_ingot", 180),
            one("tfc:nugget_native_gold", "minecraft:gold_ingot", 180),
            one("tfc:copper_ingot", "tfc:copper_axe_head", 200),
            one("tfc:bronze_ingot", "tfc:bronze_axe_head", 200),
        ],
        "tfc:bloomery" => vec![one("tfc:nugget_hematite", "tfc:raw_iron_bloom", 300)],
        "tfc:anvil" => vec![
            one("tfc:raw_iron_bloom", "tfc:wrought_iron_ingot", 200),
            one("tfc:copper_ingot", "tfc:copper_sheet", 160),
            one("tfc:bronze_ingot", "tfc:bronze_sheet", 160),
            one("tfc:wrought_iron_ingot", "tfc:wrought_iron_sheet", 200),
            one("tfc:wrought_iron_ingot", "tfc:wrought_iron_axe_head", 220),
        ],
        "tfc:quern" => vec![
            one("tfc:wheat", "tfc:flour", 120),
            one("tfc:barley_grain", "tfc:flour", 120),
            one("tfc:limestone_gravel", "tfc:flux", 100),
        ],
        "tfc:barrel" => vec![one("minecraft:oak_log", "tfc:tannin", 200)],
        "tfc:pit_kiln" => vec![
            one("tfc:unfired_vessel", "tfc:vessel", 240),
            one("tfc:unfired_jug", "tfc:jug", 240),
            one("tfc:glass_batch", "minecraft:glass", 240),
        ],
        "tfc:blast_furnace" => vec![MachineRecipe {
            inputs: vec![item_ing("tfc:wrought_iron_ingot"), item_ing("tfc:flux")],
            output: stack("tfc:steel_ingot", 1),
            duration: 320,
        }],
        "tfc:sluice" => vec![one("tfc:ore_deposit", "tfc:nugget_native_copper", 160)],
        "tfc:charcoal_pit" => vec![one("minecraft:oak_log", "minecraft:charcoal", 240)],
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
