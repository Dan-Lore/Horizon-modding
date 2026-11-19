//! Place / remove covers on gtceu machines with use_item_on.

use crate::pipes::{cover_of, filter_item, set_cover, set_filter_item};
use crate::registry;
use horizon_client::mod_api::{Flow, Host, Text, UseItemOnEvent};

fn is_cover(item: &str) -> bool {
    matches!(
        item,
        "gtceu:cover_conveyor" | "gtceu:cover_pump" | "gtceu:cover_item_filter"
    )
}

pub fn use_item_on(host: &mut dyn Host, event: &mut UseItemOnEvent<'_>) -> Flow {
    let block = host.block(event.pos);
    let Some(spec) = registry::find(&block) else {
        return Flow::Continue;
    };
    // Only machines / hatches take covers — not cables/pipes themselves.
    if matches!(
        spec.kind,
        registry::Kind::Cable
            | registry::Kind::ItemPipe
            | registry::Kind::FluidPipe
            | registry::Kind::Conveyor
            | registry::Kind::Hull
    ) {
        return Flow::Continue;
    }

    let item = event.stack.item.as_ref();
    let Some(player) = host.acting_player() else {
        return Flow::Continue;
    };

    // Empty hand while sneaking removes cover (avoids fighting the machine GUI).
    if player.sneaking && (item == "minecraft:air" || event.stack.count == 0) {
        let mut removed = None;
        let _ = host.change_mod_block_entity(event.pos, &mut |entity| {
            removed = cover_of(entity);
            if removed.is_some() {
                set_cover(entity, None);
            }
        });
        if let Some(cover) = removed {
            let _ = host.give_items(&cover, 1);
            host.tell(
                player.uuid,
                Text::literal(format!("GregTech: removed {cover}")),
            );
            return Flow::Cancel;
        }
        return Flow::Continue;
    }

    // Configure item filter: hold the whitelist item and use on a filtered machine.
    if !is_cover(item) {
        let mut configured = false;
        let mut msg = String::new();
        let sample = item.to_owned();
        let _ = host.change_mod_block_entity(event.pos, &mut |entity| {
            if cover_of(entity).as_deref() != Some("gtceu:cover_item_filter") {
                return;
            }
            if player.sneaking {
                set_filter_item(entity, None);
                msg = "GregTech: filter cleared".into();
            } else {
                set_filter_item(entity, Some(&sample));
                msg = format!("GregTech: filter set to {sample}");
            }
            configured = true;
            let _ = filter_item(entity);
        });
        if configured {
            host.tell(player.uuid, Text::literal(msg));
            return Flow::Cancel;
        }
        return Flow::Continue;
    }

    let cover_id = item.to_owned();
    let mut applied = false;
    let mut had = None;
    let _ = host.change_mod_block_entity(event.pos, &mut |entity| {
        had = cover_of(entity);
        if had.is_none() {
            set_cover(entity, Some(&cover_id));
            applied = true;
        }
    });
    if applied {
        let _ = host.take_items(&cover_id, 1);
        host.tell(
            player.uuid,
            Text::literal(format!(
                "GregTech: attached {cover_id}{}",
                if cover_id == "gtceu:cover_item_filter" {
                    " (use an item on the machine to set the filter; sneak clears)"
                } else {
                    ""
                }
            )),
        );
        return Flow::Cancel;
    }
    if had.is_some() {
        host.tell(
            player.uuid,
            Text::literal("GregTech: machine already has a cover (sneak empty-hand remove)."),
        );
        return Flow::Cancel;
    }
    Flow::Continue
}
