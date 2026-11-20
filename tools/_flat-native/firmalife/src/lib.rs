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
    oven_or_dry_input(item).is_some()
}

/// Oven / drying inputs → dried fruit (Firmalife-inspired food slice on Horizon hooks).
fn oven_or_dry_input(item: &str) -> Option<&'static str> {
    match item {
        "minecraft:potato"
        | "minecraft:apple"
        | "minecraft:carrot"
        | "minecraft:sweet_berries"
        | "minecraft:melon_slice"
        | "minecraft:glow_berries"
        | "minecraft:chorus_fruit"
        | "minecraft:beetroot" => Some("firmalife:dried_fruit"),
        _ => None,
    }
}

fn vat_input(item: &str) -> Option<&'static str> {
    match item {
        "minecraft:milk_bucket" => Some("firmalife:cheese"),
        "minecraft:honey_bottle" => Some("firmalife:raw_honey"),
        "firmalife:raw_honey" => Some("firmalife:honey_jar"),
        _ => None,
    }
}

impl Hooks for Firmalife {
    fn player_logged_in(&self, host: &mut dyn Host, event: &mut PlayerLoggedInEvent<'_>) {
        host.tell(
            event.player,
            Text::literal(
                "Firmalife 0.1.2 (Horizon rewrite): vat, beehive, drying, sprinkler, oven, greenhouse.",
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
            || id.ends_with("cheese_wheel")
            || id.ends_with("greenhouse_panel")
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
        } else if id.ends_with("cheese_wheel") {
            tick_cheese_wheel(event);
        } else if id.ends_with("greenhouse_panel") {
            tick_greenhouse_panel(host, event.pos);
        }
    }
}

fn tick_oven(host: &mut dyn Host, event: &mut BlockEntityTickEvent<'_>) {
    ensure_slots(event.entity, 2);
    let Some(out_id) = event.entity.items[0]
        .as_ref()
        .and_then(|s| oven_or_dry_input(s.item.as_ref()).filter(|_| s.count > 0))
    else {
        let _ = host.set_block_property(event.pos, "lit", "false");
        return;
    };
    let out_free = event.entity.items[1]
        .as_ref()
        .is_none_or(|s| s.item.as_ref() == out_id && s.count < 64);
    if !out_free {
        let _ = host.set_block_property(event.pos, "lit", "false");
        return;
    }
    let _ = host.set_block_property(event.pos, "lit", "true");
    let next = nbt_i32(event.entity, "Bake") + 1;
    if next >= 100 {
        consume_slot(event.entity, 0);
        merge_out(event.entity, 1, out_id);
        set_nbt_i32(event.entity, "Bake", 0);
    } else {
        set_nbt_i32(event.entity, "Bake", next);
    }
}

fn tick_vat(host: &mut dyn Host, event: &mut BlockEntityTickEvent<'_>) {
    ensure_slots(event.entity, 2);
    let Some(out_id) = event.entity.items[0]
        .as_ref()
        .and_then(|s| vat_input(s.item.as_ref()).filter(|_| s.count > 0))
    else {
        let _ = host.set_block_property(event.pos, "lit", "false");
        return;
    };
    let out_free = event.entity.items[1]
        .as_ref()
        .is_none_or(|s| s.item.as_ref() == out_id && s.count < 64);
    if !out_free {
        let _ = host.set_block_property(event.pos, "lit", "false");
        return;
    }
    let _ = host.set_block_property(event.pos, "lit", "true");
    let next = nbt_i32(event.entity, "Boil") + 1;
    if next >= 120 {
        let input = event.entity.items[0]
            .as_ref()
            .map(|s| s.item.as_ref().to_owned())
            .unwrap_or_default();
        if input == "minecraft:milk_bucket" || input == "minecraft:honey_bottle" {
            event.entity.items[0] = Some(ItemStack::new(
                if input == "minecraft:honey_bottle" {
                    "minecraft:glass_bottle"
                } else {
                    "minecraft:bucket"
                },
                1,
            ));
        } else {
            consume_slot(event.entity, 0);
        }
        merge_out(event.entity, 1, out_id);
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

/// Age cheese in place: every 200 ticks produce one `firmalife:cheese` into slot 0 (cap 16).
fn tick_cheese_wheel(event: &mut BlockEntityTickEvent<'_>) {
    ensure_slots(event.entity, 1);
    let out_free = event.entity.items[0].as_ref().is_none_or(|s| {
        s.item.as_ref() == "firmalife:cheese" && s.count < 16
    });
    if !out_free {
        return;
    }
    let next = nbt_i32(event.entity, "Age") + 1;
    if next >= 200 {
        merge_out(event.entity, 0, "firmalife:cheese");
        set_nbt_i32(event.entity, "Age", 0);
    } else {
        set_nbt_i32(event.entity, "Age", next);
    }
}

/// Greenhouse roof/panel: every ~100 ticks, try to advance one nearby crop's `age`.
fn tick_greenhouse_panel(host: &mut dyn Host, pos: [i32; 3]) {
    // Throttle via world time parity on position so we do not force age=7 every tick.
    let pulse = (pos[0].wrapping_add(pos[1]).wrapping_add(pos[2])).rem_euclid(100);
    if pulse != 0 {
        return;
    }
    for dz in -1..=1 {
        for dx in -1..=1 {
            for dy in -2..=0 {
                let p = [pos[0] + dx, pos[1] + dy, pos[2] + dz];
                let block = host.block(p);
                if !(block.contains("wheat")
                    || block.contains("carrots")
                    || block.contains("potatoes")
                    || block.contains("beetroots")
                    || block.contains("crop"))
                {
                    continue;
                }
                // Advance one stage when possible; ignore if property missing.
                for age in ["1", "2", "3", "4", "5", "6", "7"] {
                    if host.set_block_property(p, "age", age) {
                        return;
                    }
                }
            }
        }
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
