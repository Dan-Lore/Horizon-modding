//! Firmalife Horizon 0.1.2 — food slice with vat / hive / drying / sprinkler.

use horizon_client::mod_api::{
    BlockEntityTickEvent, BlockEntityTicksEvent, Hooks, Host, ItemStack, PlayerLoggedInEvent, Tag,
    Text,
};

pub fn hooks() -> Box<dyn Hooks> {
    Box::new(Firmalife)
}

struct Firmalife;

fn nbt_i32(entity: &horizon_client::mod_api::ModBlockEntity, key: &str) -> i32 {
    let key = key.to_owned();
    let jk = key.as_str().into();
    match entity.nbt.get(&jk) {
        Some(Tag::Int(v)) => *v,
        _ => 0,
    }
}

fn set_nbt_i32(entity: &mut horizon_client::mod_api::ModBlockEntity, key: &str, value: i32) {
    entity.nbt.insert(key.into(), Tag::Int(value));
}

fn ensure_slots(entity: &mut horizon_client::mod_api::ModBlockEntity, n: usize) {
    if entity.items.len() < n {
        entity.items.resize(n, None);
    }
}

fn consume_slot(entity: &mut horizon_client::mod_api::ModBlockEntity, slot: usize) {
    if let Some(stack) = entity.items.get_mut(slot).and_then(|s| s.as_mut()) {
        stack.count = stack.count.saturating_sub(1);
        if stack.count == 0 {
            entity.items[slot] = None;
        }
    }
}

fn merge_out(entity: &mut horizon_client::mod_api::ModBlockEntity, slot: usize, id: &str) {
    match entity.items.get_mut(slot).and_then(|s| s.as_mut()) {
        Some(stack) if stack.item.as_ref() == id => {
            stack.count = stack.count.saturating_add(1);
        }
        _ => {
            if entity.items.len() <= slot {
                entity.items.resize(slot + 1, None);
            }
            entity.items[slot] = Some(ItemStack::new(id, 1));
        }
    }
}

fn is_dryable(item: &str) -> bool {
    matches!(
        item,
        "minecraft:potato" | "minecraft:apple" | "minecraft:carrot" | "minecraft:sweet_berries"
    )
}

impl Hooks for Firmalife {
    fn player_logged_in(&self, host: &mut dyn Host, event: &mut PlayerLoggedInEvent<'_>) {
        host.tell(
            event.player,
            Text::literal(
                "Firmalife Horizon 0.1.2: vat, beehive, drying mat, sprinkler, oven, greenhouse.",
            ),
        );
    }

    fn block_entity_ticks(&self, _host: &dyn Host, event: &mut BlockEntityTicksEvent<'_>) {
        let id: &str = event.block.as_ref();
        if id.ends_with("oven")
            || id.ends_with("vat")
            || id.ends_with("beehive")
            || id.ends_with("drying_mat")
            || id.ends_with("sprinkler")
        {
            event.ticks = true;
        }
    }

    fn block_entity_tick(&self, host: &mut dyn Host, event: &mut BlockEntityTickEvent<'_>) {
        let id: &str = event.entity.id.as_ref();
        if id.ends_with("oven") {
            tick_oven(host, event);
        } else if id.ends_with("vat") {
            tick_vat(host, event);
        } else if id.ends_with("beehive") {
            tick_beehive(event);
        } else if id.ends_with("drying_mat") {
            tick_drying_mat(event);
        } else if id.ends_with("sprinkler") {
            tick_sprinkler(host, event.pos);
        }
    }
}

fn tick_oven(host: &mut dyn Host, event: &mut BlockEntityTickEvent<'_>) {
    ensure_slots(event.entity, 2);
    let input_ok = event.entity.items[0]
        .as_ref()
        .is_some_and(|s| s.item.as_ref() == "minecraft:potato" && s.count > 0);
    let out_free = event.entity.items[1].as_ref().is_none_or(|s| {
        s.item.as_ref() == "firmalife:dried_fruit" && s.count < 64
    });
    if !(input_ok && out_free) {
        let _ = host.set_block_property(event.pos, "lit", "false");
        return;
    }
    let _ = host.set_block_property(event.pos, "lit", "true");
    let next = nbt_i32(event.entity, "Bake") + 1;
    if next >= 100 {
        consume_slot(event.entity, 0);
        merge_out(event.entity, 1, "firmalife:dried_fruit");
        set_nbt_i32(event.entity, "Bake", 0);
    } else {
        set_nbt_i32(event.entity, "Bake", next);
    }
}

fn tick_vat(host: &mut dyn Host, event: &mut BlockEntityTickEvent<'_>) {
    ensure_slots(event.entity, 2);
    let has_milk = event.entity.items[0]
        .as_ref()
        .is_some_and(|s| s.item.as_ref() == "minecraft:milk_bucket" && s.count > 0);
    let out_free = event.entity.items[1].as_ref().is_none_or(|s| {
        s.item.as_ref() == "firmalife:cheese" && s.count < 64
    });
    if !(has_milk && out_free) {
        let _ = host.set_block_property(event.pos, "lit", "false");
        return;
    }
    let _ = host.set_block_property(event.pos, "lit", "true");
    let next = nbt_i32(event.entity, "Boil") + 1;
    if next >= 120 {
        event.entity.items[0] = Some(ItemStack::new("minecraft:bucket", 1));
        merge_out(event.entity, 1, "firmalife:cheese");
        set_nbt_i32(event.entity, "Boil", 0);
    } else {
        set_nbt_i32(event.entity, "Boil", next);
    }
}

fn tick_beehive(event: &mut BlockEntityTickEvent<'_>) {
    ensure_slots(event.entity, 1);
    let out_free = event.entity.items[0].as_ref().is_none_or(|s| {
        s.item.as_ref() == "firmalife:raw_honey" && s.count < 64
    });
    if !out_free {
        return;
    }
    let next = nbt_i32(event.entity, "Buzz") + 1;
    if next >= 200 {
        merge_out(event.entity, 0, "firmalife:raw_honey");
        set_nbt_i32(event.entity, "Buzz", 0);
    } else {
        set_nbt_i32(event.entity, "Buzz", next);
    }
}

/// Slot 0 dryable crop → slot 1 dried_fruit.
fn tick_drying_mat(event: &mut BlockEntityTickEvent<'_>) {
    ensure_slots(event.entity, 2);
    let input_ok = event.entity.items[0]
        .as_ref()
        .is_some_and(|s| is_dryable(s.item.as_ref()) && s.count > 0);
    let out_free = event.entity.items[1].as_ref().is_none_or(|s| {
        s.item.as_ref() == "firmalife:dried_fruit" && s.count < 64
    });
    if !(input_ok && out_free) {
        return;
    }
    let next = nbt_i32(event.entity, "Dry") + 1;
    if next >= 150 {
        consume_slot(event.entity, 0);
        merge_out(event.entity, 1, "firmalife:dried_fruit");
        set_nbt_i32(event.entity, "Dry", 0);
    } else {
        set_nbt_i32(event.entity, "Dry", next);
    }
}

/// Moisten farmland in a 3×3 under/around the sprinkler (irrigation marker).
fn tick_sprinkler(host: &mut dyn Host, pos: [i32; 3]) {
    let dim = host.dimension();
    for dz in -1..=1 {
        for dx in -1..=1 {
            for dy in -1..=0 {
                let p = [pos[0] + dx, pos[1] + dy, pos[2] + dz];
                let Some(level) = host.level(dim) else {
                    return;
                };
                let block = level
                    .block(host, p)
                    .unwrap_or_else(|| "minecraft:air".to_owned());
                if block.contains("farmland") {
                    let _ = host.set_block_property(p, "moisture", "7");
                }
            }
        }
    }
}
