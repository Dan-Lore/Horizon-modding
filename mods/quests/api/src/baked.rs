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
    quests.insert("see_greglite".into(), Quest {
        id: "see_greglite".into(),
        title: "Meet Greglite".into(),
        dependencies: vec!["welcome".into()],
        tasks: vec![Task { id: "gl_note".into(), kind: "checkmark".into(), title: "Confirm Greglite machines exist".into(), item: None, count: 1, x: 0, y: 64, z: 0, radius: 8 }],
        rewards: vec![Reward { id: "gl_xp".into(), kind: "xp".into(), item: None, count: 1, amount: 3, command: None, table: None, options: vec![] }],
    });
    quests.insert("see_tfc".into(), Quest {
        id: "see_tfc".into(),
        title: "Meet TFC Horizon".into(),
        dependencies: vec!["welcome".into()],
        tasks: vec![Task { id: "tfc_note".into(), kind: "checkmark".into(), title: "Confirm TFC content snapshot".into(), item: None, count: 1, x: 0, y: 64, z: 0, radius: 8 }],
        rewards: vec![Reward { id: "tfc_xp".into(), kind: "xp".into(), item: None, count: 1, amount: 3, command: None, table: None, options: vec![] }],
    });
    quests.insert("hunt_demo".into(), Quest {
        id: "hunt_demo".into(),
        title: "Hunt Demo".into(),
        dependencies: vec!["welcome".into()],
        tasks: vec![Task { id: "kill_any".into(), kind: "kill".into(), title: "Record a kill (stub)".into(), item: None, count: 1, x: 0, y: 64, z: 0, radius: 8 }],
        rewards: vec![Reward { id: "hunt_bone".into(), kind: "item".into(), item: Some("minecraft:bone".into()), count: 1, amount: 0, command: None, table: None, options: vec![] }],
    });
    let chapters = vec![
        Chapter { id: "intro".into(), title: "Getting Started".into(), progression: "linear".into(), quests: vec!["welcome".into(), "gather_sticks".into(), "open_board".into()] },
        Chapter { id: "combat_demo".into(), title: "Combat Demo".into(), progression: "flexible".into(), quests: vec!["hunt_demo".into()] },
        Chapter { id: "ae2_start".into(), title: "Applied Energistics".into(), progression: "flexible".into(), quests: vec!["ae2_book".into()] },
        Chapter { id: "greglite_start".into(), title: "Greglite".into(), progression: "flexible".into(), quests: vec!["see_greglite".into()] },
        Chapter { id: "tfc_start".into(), title: "TFC Horizon".into(), progression: "flexible".into(), quests: vec!["see_tfc".into()] },
    ];
    let mut tables = HashMap::new();
    tables.insert("starter_crate".into(), vec![TableEntry { item: "minecraft:stick".into(), count: 16, weight: 5 }, TableEntry { item: "minecraft:bread".into(), count: 4, weight: 3 }, TableEntry { item: "minecraft:iron_ingot".into(), count: 1, weight: 1 }]);
    let mut themes = HashMap::new();
    themes.insert("copper".into(), "§6".into());
    themes.insert("steel".into(), "§7".into());
    themes.insert("ae2".into(), "§b".into());
    QuestFile { chapters, quests, tables, themes, theme_default: "copper".into() }
}
