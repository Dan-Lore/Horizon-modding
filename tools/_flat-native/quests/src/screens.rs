//! Quest board screen overlay + book open_menu surface.

use crate::board;
use crate::file;
use crate::logic;
use crate::progress;
use crate::teams_bridge;
use horizon_client::mod_api::{Host, ItemStack, ScreenDrawEvent, Text};

/// Draw a compact quest status strip on the quest board menu.
pub fn draw(host: &dyn Host, event: &mut ScreenDrawEvent<'_>) {
    if event.block != board::BLOCK {
        return;
    }
    let ox = event.origin[0];
    let oy = event.origin[1];
    host.fill(event.batch, [ox + 8.0, oy + 6.0, 160.0, 24.0], 0xFF_202028);
    let Some(player) = host.acting_player() else {
        host.text(
            event.batch,
            "Quest board",
            [ox + 12.0, oy + 12.0],
            0xFFE0E0E0,
            true,
        );
        return;
    };
    let team = teams_bridge::team_id(player.uuid);
    let loaded = file::load();
    let mut line = String::from("Quests: ");
    let mut shown = 0usize;
    for ch in &loaded.chapters {
        for qid in &ch.quests {
            let Some(q) = loaded.quests.get(qid) else {
                continue;
            };
            if !logic::deps_met(&team, q) && !progress::is_quest_done(&team, qid) {
                continue;
            }
            let mark = if progress::is_quest_done(&team, qid) {
                "[x]"
            } else {
                "[ ]"
            };
            if shown > 0 {
                line.push_str(" · ");
            }
            line.push_str(&format!("{mark}{}", q.title));
            shown += 1;
            if shown >= 3 {
                break;
            }
        }
        if shown >= 3 {
            break;
        }
    }
    if shown == 0 {
        line.push_str("(none unlocked — /quests book)");
    }
    host.text(event.batch, &line, [ox + 12.0, oy + 12.0], 0xFFE8F0FF, true);
}

/// Open a chest-style menu summarizing quest progress (book UI slice).
pub fn open_book_menu(host: &mut dyn Host) {
    let Some(player) = host.acting_player() else {
        return;
    };
    if let Some(dir) = host.world_dir() {
        progress::bind(dir.clone());
        teams_bridge::refresh(&dir);
    }
    let team = teams_bridge::team_id(player.uuid);
    let loaded = file::load();
    let mut items: Vec<Option<ItemStack>> = Vec::new();
    for ch in &loaded.chapters {
        for qid in &ch.quests {
            let Some(q) = loaded.quests.get(qid) else {
                continue;
            };
            let done = progress::is_quest_done(&team, qid);
            let open = logic::deps_met(&team, q);
            if !done && !open {
                continue;
            }
            let icon = if done {
                "minecraft:lime_dye"
            } else {
                "minecraft:paper"
            };
            items.push(Some(ItemStack::new(icon, 1)));
            if items.len() >= 27 {
                break;
            }
        }
        if items.len() >= 27 {
            break;
        }
    }
    while items.len() < 27 {
        items.push(None);
    }
    let title = Text::literal(format!(
        "FTB Quests ({})",
        progress::theme()
    ));
    let _ = host.open_menu(player.uuid, 3, title, items);
}
