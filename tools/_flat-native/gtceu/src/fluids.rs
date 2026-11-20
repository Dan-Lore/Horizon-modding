//! Fluid tanks stored in the block entity `fluids` list (Horizon API 54).
//! During a block's own tick the entity is out of the world, so this module
//! reads and writes that list directly. Neighbours are moved with `Host::fluid_extract`.

use horizon_client::mod_api::{parse_snbt, Direction, Host, ModBlockEntity, Tag};

pub const WATER: &str = "minecraft:water";
pub const STEAM: &str = "gtceu:steam";
pub const LAVA: &str = "minecraft:lava";
pub const DIESEL: &str = "gtceu:diesel";
pub const BIOGAS: &str = "gtceu:biogas";
pub const DISTILLED: &str = "gtceu:distilled_water";
pub const CREOSOTE: &str = "gtceu:creosote";
pub const SULFURIC_ACID: &str = "gtceu:sulfuric_acid";
pub const ETHYLENE: &str = "gtceu:ethylene";
pub const OXYGEN: &str = "gtceu:oxygen";

/// Fluids allowed in chem / wash / pipe path (keep short for Horizon pin).
pub fn is_chem_fluid(fluid: &str) -> bool {
    matches!(
        fluid,
        WATER
            | STEAM
            | LAVA
            | DIESEL
            | BIOGAS
            | DISTILLED
            | CREOSOTE
            | SULFURIC_ACID
            | ETHYLENE
            | OXYGEN
    )
}

const OFFSETS: [[i32; 3]; 6] = [
    [1, 0, 0],
    [-1, 0, 0],
    [0, 1, 0],
    [0, -1, 0],
    [0, 0, 1],
    [0, 0, -1],
];

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

fn read_list(entity: &ModBlockEntity) -> Vec<(Option<String>, i32)> {
    let Some(Tag::List(list)) = entity.nbt.get(&"fluids".into()) else {
        return Vec::new();
    };
    list.iter()
        .map(|tag| match tag {
            Tag::Compound(map) => {
                let fluid = match map.get(&"Fluid".into()) {
                    Some(Tag::String(fluid)) => {
                        let name: String = fluid.to_string_lossy();
                        if name == "minecraft:empty" || name.is_empty() {
                            None
                        } else {
                            Some(name)
                        }
                    }
                    _ => None,
                };
                let amount = match map.get(&"Amount".into()) {
                    Some(Tag::Int(amount)) => *amount,
                    _ => 0,
                };
                (fluid, amount.max(0))
            }
            _ => (None, 0),
        })
        .collect()
}

fn write_list(entity: &mut ModBlockEntity, tanks: &[(Option<String>, i32)]) {
    let mut list = Vec::with_capacity(tanks.len());
    for (fluid, amount) in tanks {
        let name = fluid.as_deref().unwrap_or("minecraft:empty");
        let text = format!("{{Fluid:\"{name}\",Amount:{amount}}}");
        if let Ok((Tag::Compound(map), _)) = parse_snbt(&text) {
            list.push(Tag::Compound(map));
        }
    }
    entity.nbt.insert("fluids".into(), Tag::List(list));
}

fn tanks_mut(entity: &ModBlockEntity, count: usize) -> Vec<(Option<String>, i32)> {
    let mut tanks = read_list(entity);
    tanks.resize(count, (None, 0));
    tanks.truncate(count);
    tanks
}

pub fn can_fill(entity: &ModBlockEntity, index: usize, fluid: &str, add: i32, capacity: i32) -> bool {
    if add <= 0 {
        return true;
    }
    let tanks = read_list(entity);
    match tanks.get(index) {
        None | Some((None, _)) => add <= capacity,
        Some((_, n)) if *n <= 0 => add <= capacity,
        Some((Some(have), n)) if have == fluid => n.saturating_add(add) <= capacity,
        _ => false,
    }
}

pub fn amount(entity: &ModBlockEntity, index: usize, fluid: &str) -> i32 {
    let tanks = read_list(entity);
    match tanks.get(index) {
        Some((Some(have), amount)) if have == fluid => *amount,
        _ => 0,
    }
}

pub fn fill(
    entity: &mut ModBlockEntity,
    index: usize,
    count: usize,
    fluid: &str,
    mut add: i32,
    capacity: i32,
) -> i32 {
    if add <= 0 {
        return 0;
    }
    let mut tanks = tanks_mut(entity, count);
    let Some(slot) = tanks.get_mut(index) else {
        return add;
    };
    let same = slot.0.as_deref() == Some(fluid) || slot.0.is_none() || slot.1 <= 0;
    if !same {
        return add;
    }
    let room = capacity.saturating_sub(slot.1);
    let moved = add.min(room).max(0);
    if moved > 0 {
        slot.0 = Some(fluid.to_owned());
        slot.1 += moved;
        add -= moved;
    }
    write_list(entity, &tanks);
    add
}

pub fn drain(
    entity: &mut ModBlockEntity,
    index: usize,
    count: usize,
    fluid: &str,
    want: i32,
) -> i32 {
    if want <= 0 {
        return 0;
    }
    let mut tanks = tanks_mut(entity, count);
    let Some(slot) = tanks.get_mut(index) else {
        return 0;
    };
    if slot.0.as_deref() != Some(fluid) {
        return 0;
    }
    let taken = want.min(slot.1).max(0);
    slot.1 -= taken;
    if slot.1 <= 0 {
        *slot = (None, 0);
    }
    write_list(entity, &tanks);
    taken
}

/// Pull `fluid` from adjacent tanks into this entity's tank. The caller is the
/// block being ticked, so its own tanks are edited here and the neighbour is
/// drained through the host.
pub fn pull_from_neighbours(
    host: &mut dyn Host,
    pos: [i32; 3],
    entity: &mut ModBlockEntity,
    index: usize,
    count: usize,
    fluid: &str,
    capacity: i32,
    max_each: i32,
) {
    let have = amount(entity, index, fluid);
    let mut room = capacity.saturating_sub(have);
    if room <= 0 {
        return;
    }
    let dim = host.dimension();
    for offset in OFFSETS {
        if room <= 0 {
            break;
        }
        let npos = [pos[0] + offset[0], pos[1] + offset[1], pos[2] + offset[2]];
        let face = approach_face(offset);
        let ask = max_each.min(room);
        let Some((got, taken)) = host.fluid_extract(dim, npos, face, ask) else {
            continue;
        };
        if got != fluid || taken <= 0 {
            let _ = host.fluid_insert(npos, face, &got, taken);
            continue;
        }
        let left = fill(entity, index, count, fluid, taken, capacity);
        if left > 0 {
            let _ = host.fluid_insert(npos, face, &got, left);
        }
        room = capacity.saturating_sub(amount(entity, index, fluid));
    }
}

pub fn absorb_water_block(
    host: &mut dyn Host,
    pos: [i32; 3],
    entity: &mut ModBlockEntity,
    index: usize,
    count: usize,
    capacity: i32,
    per_tick: i32,
) {
    let dim = host.dimension();
    for offset in OFFSETS {
        let npos = [pos[0] + offset[0], pos[1] + offset[1], pos[2] + offset[2]];
        let Some(level) = host.level(dim) else {
            continue;
        };
        if level.block(host, npos).as_deref() == Some(WATER) {
            let _ = fill(entity, index, count, WATER, per_tick, capacity);
            return;
        }
    }
}

/// A full bucket in `slot` becomes an empty bucket and fills `fluid`.
pub fn take_bucket(
    entity: &mut ModBlockEntity,
    slot: usize,
    bucket: &str,
    index: usize,
    count: usize,
    fluid: &str,
    capacity: i32,
) -> bool {
    let Some(stack) = entity.items.get(slot).and_then(|s| s.as_ref()) else {
        return false;
    };
    if stack.item.as_ref() != bucket || stack.count == 0 {
        return false;
    }
    if amount(entity, index, fluid) + 1000 > capacity && amount(entity, index, fluid) != 0 {
        let (have, _) = read_list(entity)
            .get(index)
            .cloned()
            .unwrap_or((None, 0));
        if have.as_deref().is_some_and(|name| name != fluid) {
            return false;
        }
        if capacity - amount(entity, index, fluid) < 1000 {
            return false;
        }
    }
    if capacity - amount(entity, index, fluid) < 1000 {
        return false;
    }
    let _ = fill(entity, index, count, fluid, 1000, capacity);
    if let Some(stack) = entity.items.get_mut(slot).and_then(|s| s.as_mut()) {
        if stack.count <= 1 {
            stack.item = "minecraft:bucket".into();
            stack.count = 1;
        } else {
            stack.count -= 1;
        }
    }
    true
}
