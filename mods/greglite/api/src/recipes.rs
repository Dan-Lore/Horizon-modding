//! Load custom greglite recipe maps from the world's recipe table.

use horizon_client::mod_api::serde_json::Value;
use horizon_client::mod_api::{Host, Ingredient, ItemStack};
use std::collections::HashSet;

#[derive(Clone, Debug)]
pub struct MachineRecipe {
    pub inputs: Vec<Ingredient>,
    pub output: ItemStack,
    pub duration: i32,
    pub steam: i32,
    pub eu: i32,
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
    let steam = json.get("steam").and_then(|v| v.as_i64()).unwrap_or(1) as i32;
    let eu = json
        .get("eu")
        .and_then(|v| v.as_i64())
        .unwrap_or(2) as i32;
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
        steam: steam.max(0),
        eu: eu.max(0),
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

fn one_in(inp: &str, out: &str, duration: i32, steam: i32, eu: i32) -> MachineRecipe {
    MachineRecipe {
        inputs: vec![item_ing(inp)],
        output: stack(out, 1),
        duration,
        steam,
        eu,
    }
}

fn fallback(kind: &str) -> Vec<MachineRecipe> {
    match kind {
        "greglite:alloy_smelter" => vec![
            MachineRecipe {
                inputs: vec![item_ing("minecraft:copper_ingot"), item_ing("greglite:tin_ingot")],
                output: stack("greglite:bronze_ingot", 2),
                duration: 100,
                steam: 1,
                eu: 2,
            },
            MachineRecipe {
                inputs: vec![item_ing("greglite:copper_dust"), item_ing("greglite:tin_dust")],
                output: stack("greglite:bronze_ingot", 2),
                duration: 100,
                steam: 1,
                eu: 2,
            },
        ],
        "greglite:macerator" => [
            ("minecraft:copper_ingot", "greglite:copper_dust"),
            ("minecraft:raw_copper", "greglite:copper_dust"),
            ("greglite:tin_ingot", "greglite:tin_dust"),
            ("greglite:bronze_ingot", "greglite:bronze_dust"),
            ("minecraft:iron_ingot", "greglite:iron_dust"),
            ("minecraft:raw_iron", "greglite:iron_dust"),
        ]
        .into_iter()
        .map(|(i, o)| one_in(i, o, 80, 1, 2))
        .collect(),
        "greglite:compressor" => [
            ("greglite:copper_dust", "greglite:copper_plate"),
            ("minecraft:copper_ingot", "greglite:copper_plate"),
            ("greglite:tin_dust", "greglite:tin_plate"),
            ("greglite:tin_ingot", "greglite:tin_plate"),
            ("greglite:bronze_dust", "greglite:bronze_plate"),
            ("greglite:bronze_ingot", "greglite:bronze_plate"),
            ("greglite:iron_dust", "greglite:iron_plate"),
            ("minecraft:iron_ingot", "greglite:iron_plate"),
        ]
        .into_iter()
        .map(|(i, o)| one_in(i, o, 80, 1, 2))
        .collect(),
        "greglite:electric_furnace" => [
            ("minecraft:raw_iron", "minecraft:iron_ingot"),
            ("minecraft:raw_copper", "minecraft:copper_ingot"),
            ("minecraft:cobblestone", "minecraft:stone"),
            ("minecraft:sand", "minecraft:glass"),
        ]
        .into_iter()
        .map(|(i, o)| one_in(i, o, 100, 0, 2))
        .collect(),
        "greglite:wiremill" => [
            ("greglite:tin_ingot", "greglite:tin_wire"),
            ("minecraft:copper_ingot", "greglite:copper_wire"),
            ("greglite:tin_plate", "greglite:tin_wire"),
            ("greglite:copper_plate", "greglite:copper_wire"),
        ]
        .into_iter()
        .map(|(i, o)| one_in(i, o, 60, 0, 2))
        .collect(),
        "greglite:lathe" => [
            ("greglite:tin_ingot", "greglite:tin_rod"),
            ("minecraft:copper_ingot", "greglite:copper_rod"),
            ("minecraft:iron_ingot", "greglite:tin_rod"),
        ]
        .into_iter()
        .map(|(i, o)| one_in(i, o, 60, 0, 2))
        .collect(),
        "greglite:bender" | "greglite:forge_hammer" | "greglite:forming_press"
        | "greglite:extruder" | "greglite:cutter" | "greglite:packer" => [
            ("minecraft:iron_ingot", "greglite:iron_plate"),
            ("minecraft:copper_ingot", "greglite:copper_plate"),
        ]
        .into_iter()
        .map(|(i, o)| one_in(i, o, 80, 0, 2))
        .collect(),
        _ => {
            // Generic fallback so every recipe type still processes something.
            vec![
                one_in("minecraft:cobblestone", "minecraft:gravel", 80, 0, 2),
                one_in("minecraft:gravel", "minecraft:sand", 80, 0, 2),
            ]
        }
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
