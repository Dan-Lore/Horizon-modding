//! Load custom gtceu recipe maps from the world's recipe table.

use horizon_client::mod_api::serde_json::Value;
use horizon_client::mod_api::{Host, Ingredient, ItemStack};
use std::collections::HashSet;

#[derive(Clone, Debug)]
pub struct RecipeOutput {
    pub stack: ItemStack,
    pub chance: i32,
}

#[derive(Clone, Debug)]
pub struct MachineRecipe {
    pub inputs: Vec<Ingredient>,
    pub outputs: Vec<RecipeOutput>,
    pub circuit: Option<i32>,
    pub duration: i32,
    pub steam: i32,
    pub eu: i32,
    pub min_voltage: i32,
    pub heat: i32,
    pub fluid_in: Option<(String, i32)>,
    pub fluid_out: Option<(String, i32)>,
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

fn parse_fluid(json: &Value, key: &str) -> Option<(String, i32)> {
    let obj = json.get(key)?;
    let id = obj.get("id")?.as_str()?.to_owned();
    let amount = obj.get("amount").and_then(|v| v.as_i64()).unwrap_or(0) as i32;
    (amount > 0).then_some((id, amount))
}

fn parse(host: &dyn Host, json: &Value) -> Option<MachineRecipe> {
    let duration = json.get("duration").and_then(|v| v.as_i64()).unwrap_or(100) as i32;
    let steam = json.get("steam").and_then(|v| v.as_i64()).unwrap_or(1) as i32;
    let eu = json.get("eu").and_then(|v| v.as_i64()).unwrap_or(2) as i32;
    let min_voltage = json
        .get("min_voltage")
        .and_then(|v| v.as_i64())
        .unwrap_or(32) as i32;
    let heat = json.get("heat").and_then(|v| v.as_i64()).unwrap_or(0) as i32;
    let circuit = json
        .get("circuit")
        .and_then(|v| v.as_i64())
        .map(|v| v as i32);

    let mut outputs = Vec::new();
    if let Some(arr) = json.get("results").and_then(|v| v.as_array()) {
        for entry in arr {
            let chance = entry
                .get("chance")
                .and_then(|v| v.as_i64())
                .unwrap_or(100) as i32;
            let mut clean = entry.clone();
            if let Some(obj) = clean.as_object_mut() {
                obj.remove("chance");
            }
            let stack = host.recipe_result(&clean)?;
            outputs.push(RecipeOutput { stack, chance });
        }
    } else if let Some(one) = json.get("result") {
        outputs.push(RecipeOutput {
            stack: host.recipe_result(one)?,
            chance: 100,
        });
    }
    if outputs.is_empty() && parse_fluid(json, "fluid_out").is_none() {
        return None;
    }

    let mut inputs = Vec::new();
    if let Some(arr) = json.get("ingredients").and_then(|v| v.as_array()) {
        for entry in arr {
            inputs.push(host.recipe_ingredient(entry)?);
        }
    } else if let Some(one) = json.get("ingredient") {
        inputs.push(host.recipe_ingredient(one)?);
    }
    Some(MachineRecipe {
        inputs,
        outputs,
        circuit,
        duration: duration.max(1),
        steam: steam.max(0),
        eu: eu.max(0),
        min_voltage: min_voltage.max(1),
        heat: heat.max(0),
        fluid_in: parse_fluid(json, "fluid_in"),
        fluid_out: parse_fluid(json, "fluid_out"),
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
        outputs: vec![RecipeOutput {
            stack: stack(out, 1),
            chance: 100,
        }],
        circuit: None,
        duration,
        steam,
        eu,
        min_voltage: 32,
        heat: 0,
        fluid_in: None,
        fluid_out: None,
    }
}

fn fallback(kind: &str) -> Vec<MachineRecipe> {
    match kind {
        "gtceu:alloy_smelter" => vec![
            MachineRecipe {
                inputs: vec![item_ing("minecraft:copper_ingot"), item_ing("gtceu:tin_ingot")],
                outputs: vec![RecipeOutput {
                    stack: stack("gtceu:bronze_ingot", 2),
                    chance: 100,
                }],
                circuit: None,
                duration: 100,
                steam: 1,
                eu: 2,
                min_voltage: 32,
                heat: 0,
                fluid_in: None,
                fluid_out: None,
            },
            MachineRecipe {
                inputs: vec![item_ing("gtceu:copper_dust"), item_ing("gtceu:tin_dust")],
                outputs: vec![RecipeOutput {
                    stack: stack("gtceu:bronze_ingot", 2),
                    chance: 100,
                }],
                circuit: None,
                duration: 100,
                steam: 1,
                eu: 2,
                min_voltage: 32,
                heat: 0,
                fluid_in: None,
                fluid_out: None,
            },
        ],
        "gtceu:macerator" => [
            ("minecraft:copper_ingot", "gtceu:copper_dust"),
            ("minecraft:raw_copper", "gtceu:copper_dust"),
            ("gtceu:tin_ingot", "gtceu:tin_dust"),
            ("gtceu:bronze_ingot", "gtceu:bronze_dust"),
            ("minecraft:iron_ingot", "gtceu:iron_dust"),
            ("minecraft:raw_iron", "gtceu:iron_dust"),
            ("gtceu:aluminium_ingot", "gtceu:aluminium_dust"),
            ("gtceu:steel_ingot", "gtceu:steel_dust"),
            ("minecraft:coal", "gtceu:coal_dust"),
            ("minecraft:gold_ingot", "gtceu:gold_dust"),
        ]
        .into_iter()
        .map(|(i, o)| one_in(i, o, 80, 1, 2))
        .collect(),
        "gtceu:compressor" => [
            ("gtceu:copper_dust", "gtceu:copper_plate"),
            ("minecraft:copper_ingot", "gtceu:copper_plate"),
            ("gtceu:tin_dust", "gtceu:tin_plate"),
            ("gtceu:tin_ingot", "gtceu:tin_plate"),
            ("gtceu:bronze_dust", "gtceu:bronze_plate"),
            ("gtceu:bronze_ingot", "gtceu:bronze_plate"),
            ("gtceu:iron_dust", "gtceu:iron_plate"),
            ("minecraft:iron_ingot", "gtceu:iron_plate"),
        ]
        .into_iter()
        .map(|(i, o)| one_in(i, o, 80, 1, 2))
        .collect(),
        "gtceu:electric_furnace" => [
            ("minecraft:raw_iron", "minecraft:iron_ingot"),
            ("minecraft:raw_copper", "minecraft:copper_ingot"),
            ("minecraft:cobblestone", "minecraft:stone"),
            ("minecraft:sand", "minecraft:glass"),
        ]
        .into_iter()
        .map(|(i, o)| one_in(i, o, 100, 0, 2))
        .collect(),
        "gtceu:wiremill" => [
            ("gtceu:tin_ingot", "gtceu:tin_wire"),
            ("minecraft:copper_ingot", "gtceu:copper_wire"),
            ("gtceu:tin_plate", "gtceu:tin_wire"),
            ("gtceu:copper_plate", "gtceu:copper_wire"),
        ]
        .into_iter()
        .map(|(i, o)| one_in(i, o, 60, 0, 2))
        .collect(),
        "gtceu:lathe" => [
            ("gtceu:tin_ingot", "gtceu:tin_rod"),
            ("minecraft:copper_ingot", "gtceu:copper_rod"),
            ("minecraft:iron_ingot", "gtceu:tin_rod"),
        ]
        .into_iter()
        .map(|(i, o)| one_in(i, o, 60, 0, 2))
        .collect(),
        "gtceu:bender" | "gtceu:forge_hammer" | "gtceu:forming_press"
        | "gtceu:extruder" | "gtceu:cutter" | "gtceu:packer" => [
            ("minecraft:iron_ingot", "gtceu:iron_plate"),
            ("minecraft:copper_ingot", "gtceu:copper_plate"),
        ]
        .into_iter()
        .map(|(i, o)| one_in(i, o, 80, 0, 2))
        .collect(),
        "gtceu:vacuum_freezer" => vec![
            one_in("gtceu:hot_steel_ingot", "gtceu:steel_ingot", 100, 0, 8),
            one_in(
                "gtceu:hot_aluminium_ingot",
                "gtceu:aluminium_ingot",
                120,
                0,
                8,
            ),
        ],
        "gtceu:assembler" => vec![one_in(
            "gtceu:phenolic_circuit_board",
            "gtceu:basic_electronic_circuit",
            100,
            0,
            8,
        )],
        "gtceu:circuit_assembler" => vec![one_in(
            "gtceu:basic_electronic_circuit",
            "gtceu:good_electronic_circuit",
            160,
            0,
            16,
        )],
        "gtceu:distillation_tower" => vec![
            MachineRecipe {
                inputs: vec![],
                outputs: vec![],
                circuit: None,
                duration: 100,
                steam: 0,
                eu: 16,
                min_voltage: 32,
                heat: 0,
                fluid_in: Some(("minecraft:water".into(), 1000)),
                fluid_out: Some(("gtceu:distilled_water".into(), 1000)),
            },
            one_in("gtceu:oil_cell", "gtceu:naphtha_cell", 200, 0, 16),
        ],
        "gtceu:distillery" => vec![MachineRecipe {
            inputs: vec![],
            outputs: vec![],
            circuit: None,
            duration: 80,
            steam: 0,
            eu: 8,
            min_voltage: 32,
            heat: 0,
            fluid_in: Some(("minecraft:water".into(), 500)),
            fluid_out: Some(("gtceu:distilled_water".into(), 500)),
        }],
        "gtceu:cracker" => vec![MachineRecipe {
            inputs: vec![item_ing("gtceu:naphtha_cell")],
            outputs: vec![RecipeOutput {
                stack: stack("gtceu:ethylene_dust", 1),
                chance: 100,
            }],
            circuit: None,
            duration: 160,
            steam: 0,
            eu: 16,
            min_voltage: 32,
            heat: 0,
            fluid_in: Some(("minecraft:water".into(), 250)),
            fluid_out: Some(("gtceu:ethylene".into(), 250)),
        }],
        "gtceu:large_chemical_reactor" => vec![MachineRecipe {
            inputs: vec![
                item_ing("gtceu:ethylene_dust"),
                item_ing("minecraft:coal"),
            ],
            outputs: vec![RecipeOutput {
                stack: stack("gtceu:polyethylene_ingot", 1),
                chance: 100,
            }],
            circuit: None,
            duration: 240,
            steam: 0,
            eu: 32,
            min_voltage: 128,
            heat: 0,
            fluid_in: Some(("gtceu:ethylene".into(), 250)),
            fluid_out: Some(("gtceu:oxygen".into(), 100)),
        }],
        "gtceu:chemical_bath" => vec![MachineRecipe {
            inputs: vec![item_ing("gtceu:copper_dust")],
            outputs: vec![RecipeOutput {
                stack: stack("gtceu:copper_plate", 1),
                chance: 100,
            }],
            circuit: None,
            duration: 100,
            steam: 0,
            eu: 8,
            min_voltage: 32,
            heat: 0,
            fluid_in: Some(("minecraft:water".into(), 200)),
            fluid_out: None,
        }],
        "gtceu:ore_washer" => vec![MachineRecipe {
            inputs: vec![item_ing("gtceu:iron_dust")],
            outputs: vec![RecipeOutput {
                stack: stack("gtceu:iron_dust", 1),
                chance: 100,
            }],
            circuit: None,
            duration: 80,
            steam: 0,
            eu: 4,
            min_voltage: 32,
            heat: 0,
            fluid_in: Some(("minecraft:water".into(), 100)),
            fluid_out: None,
        }],
        "gtceu:cleanroom" => vec![one_in(
            "gtceu:epoxy_dust",
            "gtceu:epoxy_foil",
            120,
            0,
            8,
        )],
        "gtceu:electric_blast_furnace" => vec![
            MachineRecipe {
                inputs: vec![item_ing("minecraft:iron_ingot"), item_ing("gtceu:coke")],
                outputs: vec![RecipeOutput {
                    stack: stack("gtceu:hot_steel_ingot", 1),
                    chance: 100,
                }],
                circuit: None,
                duration: 200,
                steam: 0,
                eu: 16,
                min_voltage: 32,
                heat: 1000,
                fluid_in: None,
                fluid_out: None,
            },
            MachineRecipe {
                inputs: vec![
                    item_ing("gtceu:aluminium_dust"),
                    item_ing("gtceu:coke"),
                ],
                outputs: vec![RecipeOutput {
                    stack: stack("gtceu:hot_aluminium_ingot", 1),
                    chance: 100,
                }],
                circuit: None,
                duration: 240,
                steam: 0,
                eu: 24,
                min_voltage: 32,
                heat: 1700,
                fluid_in: None,
                fluid_out: None,
            },
        ],
        // No cobblestone→gravel trap: idle when a type has zero authored recipes.
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
        _ => *slot = Some(ItemStack::new(want.item.as_ref(), want.count)),
    }
}
