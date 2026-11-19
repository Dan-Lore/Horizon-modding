//! Generated from tables/questfile.json — do not edit by hand.
use super::file::{Chapter, Quest, QuestFile, Reward, TableEntry, Task};
use std::collections::HashMap;

pub fn baked() -> QuestFile {
    let mut quests = HashMap::new();
    quests.insert("welcome".into(), Quest {
        id: "welcome".into(),
        title: "Welcome to Horizon Quests".into(),
        dependencies: vec![],
        tasks: vec![Task { id: "open_book".into(), kind: "checkmark".into(), title: "Mark that you opened the quest book".into(), item: None, count: 1, x: 0, y: 64, z: 0, radius: 8 }],
        rewards: vec![Reward { id: "welcome_apple".into(), kind: "item".into(), item: Some("minecraft:apple".into()), count: 1, amount: 0, command: None, table: None, options: vec![] }],
    });
    quests.insert("gather_sticks".into(), Quest {
        id: "gather_sticks".into(),
        title: "Gather Sticks".into(),
        dependencies: vec!["welcome".into()],
        tasks: vec![Task { id: "sticks".into(), kind: "item".into(), title: "Have 8 sticks".into(), item: Some("minecraft:stick".into()), count: 8, x: 0, y: 64, z: 0, radius: 8 }],
        rewards: vec![Reward { id: "stick_xp".into(), kind: "xp".into(), item: None, count: 1, amount: 5, command: None, table: None, options: vec![] }, Reward { id: "stick_choice".into(), kind: "choice".into(), item: None, count: 1, amount: 0, command: None, table: None, options: vec![("minecraft:oak_planks".into(), 4), ("minecraft:torch".into(), 4)] }],
    });
    quests.insert("open_board".into(), Quest {
        id: "open_board".into(),
        title: "Quest Board".into(),
        dependencies: vec!["gather_sticks".into()],
        tasks: vec![Task { id: "near_board".into(), kind: "location".into(), title: "Stand near a quest board".into(), item: Some("quests:quest_board".into()), count: 1, x: 0, y: 64, z: 0, radius: 8 }],
        rewards: vec![Reward { id: "board_table".into(), kind: "table".into(), item: None, count: 1, amount: 0, command: None, table: Some("starter_crate".into()), options: vec![] }],
    });
    quests.insert("ae2_book".into(), Quest {
        id: "ae2_book".into(),
        title: "AE2 On The Pack".into(),
        dependencies: vec!["welcome".into()],
        tasks: vec![Task { id: "ae2_note".into(), kind: "checkmark".into(), title: "Confirm AE2 is on the pack pin".into(), item: None, count: 1, x: 0, y: 64, z: 0, radius: 8 }],
        rewards: vec![Reward { id: "ae2_cmd".into(), kind: "command".into(), item: None, count: 1, amount: 0, command: Some("say Horizon Quests: AE2 chapter noted".into()), table: None, options: vec![] }],
    });
    quests.insert("ae2_fluix".into(), Quest {
        id: "ae2_fluix".into(),
        title: "Touch Fluix".into(),
        dependencies: vec!["ae2_book".into()],
        tasks: vec![Task { id: "fluix".into(), kind: "item".into(), title: "Have 1 fluix crystal".into(), item: Some("ae2:fluix_crystal".into()), count: 1, x: 0, y: 64, z: 0, radius: 8 }],
        rewards: vec![Reward { id: "fluix_xp".into(), kind: "xp".into(), item: None, count: 1, amount: 8, command: None, table: None, options: vec![] }],
    });
    quests.insert("see_greglite".into(), Quest {
        id: "see_greglite".into(),
        title: "Meet Greglite".into(),
        dependencies: vec!["welcome".into()],
        tasks: vec![Task { id: "gl_note".into(), kind: "checkmark".into(), title: "Confirm Greglite machines exist".into(), item: None, count: 1, x: 0, y: 64, z: 0, radius: 8 }],
        rewards: vec![Reward { id: "gl_xp".into(), kind: "xp".into(), item: None, count: 1, amount: 3, command: None, table: None, options: vec![] }],
    });
    quests.insert("gl_coke".into(), Quest {
        id: "gl_coke".into(),
        title: "Make Coke".into(),
        dependencies: vec!["see_greglite".into()],
        tasks: vec![Task { id: "coke".into(), kind: "item".into(), title: "Have 1 Greglite coke".into(), item: Some("greglite:coke".into()), count: 1, x: 0, y: 64, z: 0, radius: 8 }],
        rewards: vec![Reward { id: "coke_xp".into(), kind: "xp".into(), item: None, count: 1, amount: 10, command: None, table: None, options: vec![] }],
    });
    quests.insert("gl_hot_steel".into(), Quest {
        id: "gl_hot_steel".into(),
        title: "Hot Steel Path".into(),
        dependencies: vec!["gl_coke".into()],
        tasks: vec![Task { id: "hot_steel".into(), kind: "item".into(), title: "Have 1 hot steel ingot (or steel)".into(), item: Some("greglite:steel_ingot".into()), count: 1, x: 0, y: 64, z: 0, radius: 8 }],
        rewards: vec![Reward { id: "steel_xp".into(), kind: "xp".into(), item: None, count: 1, amount: 15, command: None, table: None, options: vec![] }],
    });
    quests.insert("gl_oil_slice".into(), Quest {
        id: "gl_oil_slice".into(),
        title: "Oil Cell Slice".into(),
        dependencies: vec!["see_greglite".into()],
        tasks: vec![Task { id: "oil_cell".into(), kind: "item".into(), title: "Craft an oil cell".into(), item: Some("greglite:oil_cell".into()), count: 1, x: 0, y: 64, z: 0, radius: 8 }],
        rewards: vec![Reward { id: "oil_xp".into(), kind: "xp".into(), item: None, count: 1, amount: 8, command: None, table: None, options: vec![] }],
    });
    quests.insert("see_tfc".into(), Quest {
        id: "see_tfc".into(),
        title: "Meet TFC Horizon".into(),
        dependencies: vec!["welcome".into()],
        tasks: vec![Task { id: "tfc_note".into(), kind: "checkmark".into(), title: "Confirm TFC content snapshot".into(), item: None, count: 1, x: 0, y: 64, z: 0, radius: 8 }],
        rewards: vec![Reward { id: "tfc_xp".into(), kind: "xp".into(), item: None, count: 1, amount: 3, command: None, table: None, options: vec![] }],
    });
    quests.insert("tfc_crucible".into(), Quest {
        id: "tfc_crucible".into(),
        title: "Crucible Ready".into(),
        dependencies: vec!["see_tfc".into()],
        tasks: vec![Task { id: "crucible".into(), kind: "item".into(), title: "Have a TFC crucible".into(), item: Some("tfc:crucible".into()), count: 1, x: 0, y: 64, z: 0, radius: 8 }],
        rewards: vec![Reward { id: "crucible_xp".into(), kind: "xp".into(), item: None, count: 1, amount: 10, command: None, table: None, options: vec![] }],
    });
    quests.insert("fl_cheese".into(), Quest {
        id: "fl_cheese".into(),
        title: "Make Cheese".into(),
        dependencies: vec!["welcome".into()],
        tasks: vec![Task { id: "cheese".into(), kind: "item".into(), title: "Have Firmalife cheese".into(), item: Some("firmalife:cheese".into()), count: 1, x: 0, y: 64, z: 0, radius: 8 }],
        rewards: vec![Reward { id: "cheese_xp".into(), kind: "xp".into(), item: None, count: 1, amount: 5, command: None, table: None, options: vec![] }],
    });
    quests.insert("fl_oven".into(), Quest {
        id: "fl_oven".into(),
        title: "Build an Oven".into(),
        dependencies: vec!["fl_cheese".into()],
        tasks: vec![Task { id: "oven".into(), kind: "item".into(), title: "Have a Firmalife oven".into(), item: Some("firmalife:oven".into()), count: 1, x: 0, y: 64, z: 0, radius: 8 }],
        rewards: vec![Reward { id: "oven_xp".into(), kind: "xp".into(), item: None, count: 1, amount: 8, command: None, table: None, options: vec![] }],
    });
    quests.insert("aa_desh".into(), Quest {
        id: "aa_desh".into(),
        title: "Desh Ingot".into(),
        dependencies: vec!["welcome".into()],
        tasks: vec![Task { id: "desh".into(), kind: "item".into(), title: "Have 1 desh ingot".into(), item: Some("adastra:desh_ingot".into()), count: 1, x: 0, y: 64, z: 0, radius: 8 }],
        rewards: vec![Reward { id: "desh_xp".into(), kind: "xp".into(), item: None, count: 1, amount: 8, command: None, table: None, options: vec![] }],
    });
    quests.insert("aa_generator".into(), Quest {
        id: "aa_generator".into(),
        title: "Coal Generator".into(),
        dependencies: vec!["aa_desh".into()],
        tasks: vec![Task { id: "gen".into(), kind: "item".into(), title: "Have a coal generator".into(), item: Some("adastra:coal_generator".into()), count: 1, x: 0, y: 64, z: 0, radius: 8 }],
        rewards: vec![Reward { id: "gen_xp".into(), kind: "xp".into(), item: None, count: 1, amount: 10, command: None, table: None, options: vec![] }],
    });
    quests.insert("hunt_demo".into(), Quest {
        id: "hunt_demo".into(),
        title: "Hunt Demo".into(),
        dependencies: vec!["welcome".into()],
        tasks: vec![Task { id: "kill_any".into(), kind: "kill".into(), title: "Record a kill (stub)".into(), item: None, count: 1, x: 0, y: 64, z: 0, radius: 8 }],
        rewards: vec![Reward { id: "hunt_bone".into(), kind: "item".into(), item: Some("minecraft:bone".into()), count: 1, amount: 0, command: None, table: None, options: vec![] }],
    });
    quests.insert("gl_circuit".into(), Quest {
        id: "gl_circuit".into(),
        title: "Basic Circuit".into(),
        dependencies: vec!["see_greglite".into()],
        tasks: vec![Task { id: "circ".into(), kind: "item".into(), title: "Have a basic electronic circuit".into(), item: Some("greglite:basic_electronic_circuit".into()), count: 1, x: 0, y: 64, z: 0, radius: 8 }],
        rewards: vec![Reward { id: "circ_xp".into(), kind: "xp".into(), item: None, count: 1, amount: 12, command: None, table: None, options: vec![] }],
    });
    quests.insert("gl_conveyor".into(), Quest {
        id: "gl_conveyor".into(),
        title: "Conveyor Module".into(),
        dependencies: vec!["see_greglite".into()],
        tasks: vec![Task { id: "conv".into(), kind: "item".into(), title: "Have a conveyor module".into(), item: Some("greglite:conveyor_module".into()), count: 1, x: 0, y: 64, z: 0, radius: 8 }],
        rewards: vec![Reward { id: "conv_xp".into(), kind: "xp".into(), item: None, count: 1, amount: 8, command: None, table: None, options: vec![] }],
    });
    quests.insert("fl_vat".into(), Quest {
        id: "fl_vat".into(),
        title: "Boil in a Vat".into(),
        dependencies: vec!["fl_cheese".into()],
        tasks: vec![Task { id: "vat".into(), kind: "item".into(), title: "Have a Firmalife vat".into(), item: Some("firmalife:vat".into()), count: 1, x: 0, y: 64, z: 0, radius: 8 }],
        rewards: vec![Reward { id: "vat_xp".into(), kind: "xp".into(), item: None, count: 1, amount: 8, command: None, table: None, options: vec![] }],
    });
    quests.insert("fl_hive".into(), Quest {
        id: "fl_hive".into(),
        title: "Keep Bees".into(),
        dependencies: vec!["fl_cheese".into()],
        tasks: vec![Task { id: "hive".into(), kind: "item".into(), title: "Have a beehive".into(), item: Some("firmalife:beehive".into()), count: 1, x: 0, y: 64, z: 0, radius: 8 }],
        rewards: vec![Reward { id: "hive_xp".into(), kind: "xp".into(), item: None, count: 1, amount: 8, command: None, table: None, options: vec![] }],
    });
    quests.insert("fl_sprinkler".into(), Quest {
        id: "fl_sprinkler".into(),
        title: "Irrigate".into(),
        dependencies: vec!["fl_oven".into()],
        tasks: vec![Task { id: "spr".into(), kind: "item".into(), title: "Have a sprinkler".into(), item: Some("firmalife:sprinkler".into()), count: 1, x: 0, y: 64, z: 0, radius: 8 }],
        rewards: vec![Reward { id: "spr_xp".into(), kind: "xp".into(), item: None, count: 1, amount: 6, command: None, table: None, options: vec![] }],
    });
    let chapters = vec![
        Chapter { id: "intro".into(), title: "Getting Started".into(), progression: "linear".into(), quests: vec!["welcome".into(), "gather_sticks".into(), "open_board".into()] },
        Chapter { id: "combat_demo".into(), title: "Combat Demo".into(), progression: "flexible".into(), quests: vec!["hunt_demo".into()] },
        Chapter { id: "ae2_start".into(), title: "Applied Energistics".into(), progression: "flexible".into(), quests: vec!["ae2_book".into(), "ae2_fluix".into()] },
        Chapter { id: "greglite_start".into(), title: "Greglite".into(), progression: "flexible".into(), quests: vec!["see_greglite".into(), "gl_coke".into(), "gl_hot_steel".into(), "gl_oil_slice".into(), "gl_circuit".into(), "gl_conveyor".into()] },
        Chapter { id: "tfc_start".into(), title: "TFC Horizon".into(), progression: "flexible".into(), quests: vec!["see_tfc".into(), "tfc_crucible".into()] },
        Chapter { id: "firmalife_start".into(), title: "Firmalife".into(), progression: "flexible".into(), quests: vec!["fl_cheese".into(), "fl_oven".into(), "fl_vat".into(), "fl_hive".into(), "fl_sprinkler".into()] },
        Chapter { id: "adastra_start".into(), title: "Ad Astra".into(), progression: "flexible".into(), quests: vec!["aa_desh".into(), "aa_generator".into()] },
    ];
    let mut tables = HashMap::new();
    tables.insert("starter_crate".into(), vec![TableEntry { item: "minecraft:stick".into(), count: 16, weight: 5 }, TableEntry { item: "minecraft:bread".into(), count: 4, weight: 3 }, TableEntry { item: "minecraft:iron_ingot".into(), count: 1, weight: 1 }]);
    let mut themes = HashMap::new();
    themes.insert("copper".into(), "§6".into());
    themes.insert("steel".into(), "§7".into());
    themes.insert("ae2".into(), "§b".into());
    themes.insert("food".into(), "§a".into());
    QuestFile { chapters, quests, tables, themes, theme_default: "copper".into() }
}
