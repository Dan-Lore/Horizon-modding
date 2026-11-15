//! Prospector's pick lite — scan nearby ore blocks (W2 / W11).

pub struct OreDef {
    pub block: &'static str,
    pub name: &'static str,
}

pub const ORES: &[OreDef] = &[
    OreDef {
        block: "tfc:ore_native_copper",
        name: "native copper",
    },
    OreDef {
        block: "tfc:ore_native_gold",
        name: "native gold",
    },
    OreDef {
        block: "tfc:ore_hematite",
        name: "hematite",
    },
];

pub const RADIUS: i32 = 12;

pub fn is_propick(item: &str) -> bool {
    item == "tfc:prospector_pick" || item.ends_with("_propick")
}
