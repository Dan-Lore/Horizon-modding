//! Prospector's pick lite (W2) + pan (W11).

use crate::registry;
use horizon_client::mod_api::{Flow, Host, Text, UseItemEvent, UseItemOnEvent};

const SCAN: i32 = 12;

pub fn use_propick(host: &mut dyn Host, event: &mut UseItemOnEvent<'_>) -> Flow {
    if event.stack.item != "tfc:prospector_pick" {
        return Flow::Continue;
    }
    let origin = event.pos;
    let mut found: Vec<String> = Vec::new();
    for dx in -SCAN..=SCAN {
        for dy in -SCAN / 2..=SCAN / 2 {
            for dz in -SCAN..=SCAN {
                let pos = [origin[0] + dx, origin[1] + dy, origin[2] + dz];
                let block = host.block(pos);
                if registry::is_ore(&block) && !found.contains(&block) {
                    found.push(block);
                }
            }
        }
    }
    if let Some(p) = host.acting_player() {
        let msg = if found.is_empty() {
            "Nothing found nearby.".to_owned()
        } else {
            format!("Found: {}", found.join(", "))
        };
        host.tell(p.uuid, Text::literal(msg));
    }
    Flow::Cancel
}

pub fn use_pan(host: &mut dyn Host, event: &mut UseItemEvent<'_>) -> Flow {
    if event.stack.item != "tfc:pan_empty" && event.stack.item != "tfc:pan_filled" {
        return Flow::Continue;
    }
    if let Some(p) = host.acting_player() {
        if event.stack.item == "tfc:pan_filled" {
            let _ = host.give_items("tfc:small_ore_native_copper", 1);
            host.action_bar(p.uuid, Text::literal("Panned a small native copper."));
        } else {
            host.action_bar(p.uuid, Text::literal("Fill the pan with gravel first."));
        }
    }
    Flow::Cancel
}

pub fn chisel_smooth(host: &mut dyn Host, event: &mut UseItemOnEvent<'_>) -> Flow {
    if event.stack.item != "tfc:chisel" {
        return Flow::Continue;
    }
    let block = host.block(event.pos);
    if let Some(rest) = block.strip_prefix("tfc:rock_") {
        if !rest.contains('_') {
            // rock_andesite → rock_andesite_smooth via command when possible
            if let Some(p) = host.acting_player() {
                host.tell(
                    p.uuid,
                    Text::literal(format!("Chisel: smooth {rest} (place smooth variant).")),
                );
            }
            return Flow::Cancel;
        }
    }
    Flow::Continue
}
