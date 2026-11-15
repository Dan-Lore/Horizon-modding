//! Load TFC machine recipes from the world's recipe table (+ baked fallbacks).

use horizon_client::mod_api::serde_json::Value;
use horizon_client::mod_api::{Host, Ingredient, ItemStack};
use std::collections::HashSet;

#[derive(Clone, Debug)]
pub struct MachineRecipe {
    pub inputs: Vec<Ingredient>,
    pub output: ItemStack,
    pub duration: i32,
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
    let duration = json.get("duration").and_then(|v| v.as_i64()).unwrap_or(200) as i32;
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

fn stack(id: &str, count: u32) -> ItemStack {
    ItemStack::new(id, count)
}

fn one_in(inp: &str, out: &str, duration: i32) -> MachineRecipe {
    MachineRecipe {
        inputs: vec![item_ing(inp)],
        output: stack(out, 1),
        duration,
    }
}

fn two_in(a: &str, b: &str, out: &str, duration: i32) -> MachineRecipe {
    MachineRecipe {
        inputs: vec![item_ing(a), item_ing(b)],
        output: stack(out, 1),
        duration,
    }
}

fn fallback(kind: &str) -> Vec<MachineRecipe> {
    match kind {
        "tfc:pit_kiln" => vec![
            one_in("tfc:unfired_vessel", "tfc:vessel", 400),
            one_in("tfc:unfired_mold_ingot", "tfc:mold_ingot", 400),
        ],
        "tfc:charcoal_forge" => vec![
            one_in("tfc:nugget_native_copper", "tfc:copper_ingot", 300),
            two_in("tfc:copper_ingot", "tfc:tin_ingot", "tfc:bronze_ingot", 280),
            two_in("tfc:copper_ingot", "tfc:mold_ingot", "tfc:copper_pickaxe_head", 250),
        ],
        "tfc:bloomery" => vec![two_in(
            "tfc:nugget_hematite",
            "minecraft:charcoal",
            "tfc:raw_iron_bloom",
            600,
        )],
        "tfc:anvil" => vec![
            one_in("tfc:raw_iron_bloom", "tfc:wrought_iron_ingot", 400),
            one_in("tfc:copper_ingot", "tfc:copper_sheet", 200),
            one_in("tfc:wrought_iron_ingot", "tfc:wrought_iron_sheet", 200),
        ],
        "tfc:quern" => vec![one_in("tfc:chalk_raw", "tfc:powder_flux", 100)],
        "tfc:barrel" => vec![two_in(
            "minecraft:oak_log",
            "minecraft:water_bucket",
            "tfc:powder_wood_ash",
            800,
        )],
        "tfc:sluice" => vec![one_in("tfc:pan_gravel", "tfc:nugget_native_copper", 120)],
        "tfc:blast_furnace" => vec![two_in(
            "tfc:wrought_iron_ingot",
            "minecraft:coal",
            "tfc:steel_ingot",
            800,
        )],
        "tfc:firepit" => vec![one_in("minecraft:porkchop", "tfc:cooked_meat", 200)],
        _ => vec![one_in("minecraft:cobblestone", "minecraft:gravel", 80)],
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
        _ => *slot = Some(ItemStack::new(want.item.as_ref(), want.count)),
    }
}
