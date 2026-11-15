//! Custom `tfc:*` recipes, with the same fallbacks the content generator writes.

use horizon_client::mod_api::serde_json::Value;
use horizon_client::mod_api::{Host, Ingredient, ItemStack};
use std::collections::HashSet;
use std::sync::Arc;

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum HeatNeed {
    None,
    Melt,
    Weld,
}

#[derive(Clone, Debug)]
pub struct MachineRecipe {
    pub inputs: Vec<Ingredient>,
    pub output: ItemStack,
    pub duration: i32,
    pub heat: HeatNeed,
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
    let heat = match json.get("heat").and_then(|value| value.as_str()) {
        Some("weld") => HeatNeed::Weld,
        Some("melt") => HeatNeed::Melt,
        _ => HeatNeed::None,
    };
    Some(MachineRecipe {
        inputs,
        output,
        duration: duration.max(1),
        heat,
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
    heated(input, output, duration, HeatNeed::None)
}

fn heated(input: &str, output: &str, duration: i32, heat: HeatNeed) -> MachineRecipe {
    MachineRecipe {
        inputs: vec![item_ing(input)],
        output: stack(output, 1),
        duration,
        heat,
    }
}

fn weld(metal: &str, duration: i32) -> MachineRecipe {
    let ingot = format!("tfc:{metal}_ingot");
    MachineRecipe {
        inputs: vec![item_ing(&ingot), item_ing(&ingot)],
        output: stack(&format!("tfc:{metal}_double_ingot"), 1),
        duration,
        heat: HeatNeed::Weld,
    }
}

fn fallback(kind: &str) -> Vec<MachineRecipe> {
    match kind {
        "tfc:firepit" => vec![
            one("minecraft:beef", "tfc:cooked_meat", 120),
            one("minecraft:porkchop", "tfc:cooked_meat", 120),
            one("tfc:dough", "tfc:bread", 120),
            one("tfc:squash", "tfc:cooked_squash", 120),
        ],
        "tfc:charcoal_forge" => vec![
            heated("tfc:nugget_native_copper", "tfc:copper_ingot", 160, HeatNeed::Melt),
            heated("tfc:nugget_malachite", "tfc:copper_ingot", 160, HeatNeed::Melt),
            heated("tfc:nugget_cassiterite", "tfc:tin_ingot", 140, HeatNeed::Melt),
            heated("tfc:nugget_bismuthinite", "tfc:bismuth_ingot", 120, HeatNeed::Melt),
            heated("tfc:nugget_sphalerite", "tfc:zinc_ingot", 140, HeatNeed::Melt),
            heated("tfc:nugget_native_silver", "tfc:silver_ingot", 180, HeatNeed::Melt),
            heated("tfc:nugget_native_gold", "minecraft:gold_ingot", 180, HeatNeed::Melt),
            heated("tfc:nugget_hematite", "tfc:wrought_iron_ingot", 300, HeatNeed::Melt),
            heated("tfc:copper_ingot", "tfc:copper_axe_head", 200, HeatNeed::Melt),
            heated("tfc:bronze_ingot", "tfc:bronze_axe_head", 200, HeatNeed::Melt),
            weld("copper", 160),
            weld("bronze", 160),
        ],
        "tfc:crucible" => vec![MachineRecipe {
            inputs: vec![item_ing("tfc:copper_ingot"), item_ing("tfc:tin_ingot")],
            output: stack("tfc:bronze_ingot", 9),
            duration: 200,
            heat: HeatNeed::Melt,
        }],
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
            one("tfc:oat_grain", "tfc:flour", 120),
            one("tfc:rye_grain", "tfc:flour", 120),
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
            heat: HeatNeed::None,
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
