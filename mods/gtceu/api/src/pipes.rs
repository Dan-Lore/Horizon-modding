//! Item / fluid pipe transfer and conveyor push between adjacent gtceu BEs.

use crate::fluids::{self, amount, drain};
use crate::registry::{self, Kind, Spec};
use horizon_client::mod_api::{Direction, Host, ItemStack, ModBlockEntity, Tag};

const OFFSETS: [[i32; 3]; 6] = [
    [1, 0, 0],
    [-1, 0, 0],
    [0, 1, 0],
    [0, -1, 0],
    [0, 0, 1],
    [0, 0, -1],
];

const PIPE_FLUID_CAP: i32 = 8_000;

fn approach_face(offset: [i32; 3]) -> Direction {
    match offset {
        [1, 0, 0] => Direction::West,
        [-1, 0, 0] => Direction::East,
        [0, 1, 0] => Direction::Down,
        [0, -1, 0] => Direction::Up,
        [0, 0, 1] => Direction::North,
        _ => Direction::South,
    }
}

fn merge_into(dest: &mut ModBlockEntity, slot: usize, stack: ItemStack) -> Option<ItemStack> {
    if dest.items.len() <= slot {
        dest.items.resize(slot + 1, None);
    }
    match dest.items[slot].as_mut() {
        None => {
            dest.items[slot] = Some(stack);
            None
        }
        Some(have) if have.item == stack.item && have.count < 64 => {
            let room = 64 - have.count;
            let move_n = stack.count.min(room);
            have.count += move_n;
            if stack.count > move_n {
                Some(ItemStack::new(stack.item.as_ref(), stack.count - move_n))
            } else {
                None
            }
        }
        Some(_) => Some(stack),
    }
}

fn restack(item: &str, count: u32) -> ItemStack {
    ItemStack::new(item, count)
}

/// Push one stack from this pipe/conveyor into an adjacent gtceu inventory.
pub fn tick_item_pipe(host: &mut dyn Host, pos: [i32; 3], entity: &mut ModBlockEntity) {
    if entity.items.is_empty() {
        entity.items.resize(1, None);
    }
    let Some(stack) = entity.items[0].take() else {
        return;
    };
    let item_id = stack.item.as_ref().to_owned();
    let mut count = stack.count;
    for offset in OFFSETS {
        if count == 0 {
            break;
        }
        let npos = [pos[0] + offset[0], pos[1] + offset[1], pos[2] + offset[2]];
        let mut left = count;
        let _ = host.change_mod_block_entity(npos, &mut |other| {
            let Some(dest) = registry::find(&other.id) else {
                return;
            };
            let accepts = matches!(
                dest.kind,
                Kind::ItemPipe
                    | Kind::Conveyor
                    | Kind::ItemHatch
                    | Kind::SteamProcessor
                    | Kind::EuProcessor
                    | Kind::Multiblock
            );
            if !accepts {
                return;
            }
            left = match merge_into(other, 0, restack(&item_id, count)) {
                None => 0,
                Some(rem) => rem.count,
            };
        });
        count = left;
        if count == 0 {
            break;
        }
    }
    entity.items[0] = if count > 0 {
        Some(restack(&item_id, count))
    } else {
        None
    };
}

/// Hold a little fluid and move it toward neighbours.
pub fn tick_fluid_pipe(host: &mut dyn Host, pos: [i32; 3], entity: &mut ModBlockEntity) {
    for fluid in [fluids::WATER, fluids::STEAM, fluids::CREOSOTE] {
        fluids::pull_from_neighbours(host, pos, entity, 0, 1, fluid, PIPE_FLUID_CAP, 500);
    }
    for fluid in [fluids::WATER, fluids::STEAM, fluids::CREOSOTE] {
        let have = amount(entity, 0, fluid);
        if have <= 0 {
            continue;
        }
        let push = have.min(250);
        for offset in OFFSETS {
            let npos = [pos[0] + offset[0], pos[1] + offset[1], pos[2] + offset[2]];
            let face = approach_face(offset);
            // fluid_insert returns leftover amount (i32), not Result.
            let left = host.fluid_insert(npos, face, fluid, push);
            let moved = push.saturating_sub(left.max(0));
            if moved > 0 {
                let _ = drain(entity, 0, 1, fluid, moved);
                return;
            }
        }
    }
}

pub fn cover_of(entity: &ModBlockEntity) -> Option<String> {
    match entity.nbt.get(&"Cover".into()) {
        Some(Tag::String(s)) => {
            let name: String = s.to_string_lossy();
            if name.is_empty() {
                None
            } else {
                Some(name)
            }
        }
        _ => None,
    }
}

pub fn set_cover(entity: &mut ModBlockEntity, cover: Option<&str>) {
    if let Some(c) = cover {
        let text = format!("\"{c}\"");
        if let Ok((tag, _)) = horizon_client::mod_api::parse_snbt(&text) {
            entity.nbt.insert("Cover".into(), tag);
        }
    } else {
        entity.nbt.remove(&"Cover".into());
    }
}

pub fn filter_item(entity: &ModBlockEntity) -> Option<String> {
    match entity.nbt.get(&"CoverFilter".into()) {
        Some(Tag::String(s)) => {
            let name: String = s.to_string_lossy();
            if name.is_empty() {
                None
            } else {
                Some(name)
            }
        }
        _ => None,
    }
}

pub fn set_filter_item(entity: &mut ModBlockEntity, item: Option<&str>) {
    if let Some(id) = item {
        let text = format!("\"{id}\"");
        if let Ok((tag, _)) = horizon_client::mod_api::parse_snbt(&text) {
            entity.nbt.insert("CoverFilter".into(), tag);
        }
    } else {
        entity.nbt.remove(&"CoverFilter".into());
    }
}

/// Machine cover: conveyor / filter push outputs; pump moves water.
pub fn tick_cover_effects(
    host: &mut dyn Host,
    pos: [i32; 3],
    entity: &mut ModBlockEntity,
    spec: &Spec,
) {
    let Some(cover) = cover_of(entity) else {
        return;
    };
    if cover == "gtceu:cover_conveyor" || cover == "gtceu:cover_item_filter" {
        let out = spec.output.unwrap_or(0);
        if entity.items.len() <= out {
            return;
        }
        let Some(stack) = entity.items[out].take() else {
            return;
        };
        let item_id = stack.item.as_ref().to_owned();
        if cover == "gtceu:cover_item_filter" {
            if let Some(want) = filter_item(entity) {
                if item_id != want {
                    entity.items[out] = Some(restack(&item_id, stack.count));
                    return;
                }
            }
        }
        let mut count = stack.count;
        for offset in OFFSETS {
            if count == 0 {
                break;
            }
            let npos = [pos[0] + offset[0], pos[1] + offset[1], pos[2] + offset[2]];
            let mut left = count;
            let _ = host.change_mod_block_entity(npos, &mut |other| {
                left = match merge_into(other, 0, restack(&item_id, count)) {
                    None => 0,
                    Some(rem) => rem.count,
                };
            });
            count = left;
        }
        entity.items[out] = if count > 0 {
            Some(restack(&item_id, count))
        } else {
            None
        };
    }
    if cover == "gtceu:cover_pump" {
        for fluid in [fluids::WATER, fluids::STEAM, fluids::CREOSOTE] {
            fluids::pull_from_neighbours(host, pos, entity, 0, 1, fluid, 16_000, 250);
            let have = amount(entity, 0, fluid);
            if have <= 0 {
                continue;
            }
            let push = have.min(250);
            for offset in OFFSETS {
                let npos = [pos[0] + offset[0], pos[1] + offset[1], pos[2] + offset[2]];
                let face = approach_face(offset);
                let left = host.fluid_insert(npos, face, fluid, push);
                let moved = push.saturating_sub(left.max(0));
                if moved > 0 {
                    let _ = drain(entity, 0, 1, fluid, moved);
                    break;
                }
            }
        }
    }
}
