//! Support check for the rock slice.
//!
//! `default_state` is API 446, past hooks 411, so a collapse is reported in
//! chat and the block above is left in place.

pub fn is_rock(block: &str) -> bool {
    let Some(name) = block.strip_prefix("tfc:") else {
        return false;
    };
    name.ends_with("_raw")
        || name.ends_with("_cobble")
        || name.ends_with("_smooth")
        || name.ends_with("_gravel")
}

pub fn supported(block_at: impl Fn([i32; 3]) -> String, pos: [i32; 3]) -> bool {
    let [x, y, z] = pos;
    [(1, 0, 0), (-1, 0, 0), (0, 0, 1), (0, 0, -1), (0, 1, 0)]
        .into_iter()
        .any(|(dx, dy, dz)| block_at([x + dx, y + dy, z + dz]) == "tfc:support_beam")
}

pub const WARNING: &str =
    "TFC: rock above is unsupported (no support beam). The block stays; replacement waits on default_state API 446.";
