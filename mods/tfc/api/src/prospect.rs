//! Prospector's pick lite — scan nearby known ore block ids.

pub const ORE_BLOCKS: &[&str] = &[
    "tfc:ore_native_copper",
    "tfc:ore_native_gold",
    "tfc:ore_hematite",
    "tfc:ore_cassiterite",
    "tfc:ore_sphalerite",
    "tfc:ore_tetrahedrite",
    "minecraft:copper_ore",
    "minecraft:iron_ore",
    "minecraft:gold_ore",
];

pub fn hint_for(block: &str) -> Option<&'static str> {
    match block {
        "tfc:ore_native_copper" | "tfc:ore_tetrahedrite" | "minecraft:copper_ore" => {
            Some("Found traces of copper")
        }
        "tfc:ore_native_gold" | "minecraft:gold_ore" => Some("Found traces of gold"),
        "tfc:ore_hematite" | "minecraft:iron_ore" => Some("Found traces of iron"),
        "tfc:ore_cassiterite" => Some("Found traces of tin"),
        "tfc:ore_sphalerite" => Some("Found traces of zinc"),
        _ => None,
    }
}

pub fn is_ore(block: &str) -> bool {
    ORE_BLOCKS.contains(&block) || hint_for(block).is_some()
}

/// Scan a cube of radius `r` around `origin`; return first matching hint.
pub fn scan(
    origin: [i32; 3],
    r: i32,
    mut block_at: impl FnMut([i32; 3]) -> String,
) -> Option<String> {
    for dx in -r..=r {
        for dy in -r..=r {
            for dz in -r..=r {
                let pos = [origin[0] + dx, origin[1] + dy, origin[2] + dz];
                let id = block_at(pos);
                if let Some(hint) = hint_for(&id) {
                    return Some(hint.to_string());
                }
            }
        }
    }
    Some("Found nothing nearby".to_string())
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn finds_copper() {
        let msg = scan([0, 0, 0], 2, |p| {
            if p == [1, 0, 0] {
                "tfc:ore_native_copper".into()
            } else {
                "minecraft:stone".into()
            }
        });
        assert!(msg.unwrap().contains("copper"));
    }
}
