//! Support beam / collapse lite.

pub fn needs_support(block: &str) -> bool {
    block.starts_with("tfc:rock_") || block.starts_with("tfc:cobble_")
}

pub fn is_support(block: &str) -> bool {
    block == "tfc:support_beam"
}

/// True if any support beam is within Chebyshev radius `r`.
pub fn supported(
    origin: [i32; 3],
    r: i32,
    mut block_at: impl FnMut([i32; 3]) -> String,
) -> bool {
    for dx in -r..=r {
        for dy in -r..=r {
            for dz in -r..=r {
                let pos = [origin[0] + dx, origin[1] + dy, origin[2] + dz];
                if is_support(&block_at(pos)) {
                    return true;
                }
            }
        }
    }
    false
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn beam_supports() {
        assert!(supported([0, 0, 0], 4, |p| {
            if p == [2, 0, 0] {
                "tfc:support_beam".into()
            } else {
                "minecraft:air".into()
            }
        }));
    }
}
