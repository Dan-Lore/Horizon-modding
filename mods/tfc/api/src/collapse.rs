//! Support beams + collapse lite (W10).

pub fn is_support(block: &str) -> bool {
    block == "tfc:support_beam"
}

pub fn is_collapsible(block: &str) -> bool {
    block.starts_with("tfc:")
        && (block.ends_with("_cobble")
            || block.ends_with("_raw")
            || block.ends_with("_gravel")
            || block.contains("ore_"))
}

/// Horizontal search radius for a supporting beam above/beside.
pub const SUPPORT_RANGE: i32 = 4;
