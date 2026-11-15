//! Food nutrition table (W7).

pub struct FoodDef {
    pub id: &'static str,
    pub grain: f32,
    pub fruit: f32,
    pub veg: f32,
    pub protein: f32,
    pub dairy: f32,
}

pub const FOODS: &[FoodDef] = &[
    FoodDef {
        id: "tfc:red_apple",
        grain: 0.0,
        fruit: 2.0,
        veg: 0.0,
        protein: 0.0,
        dairy: 0.0,
    },
    FoodDef {
        id: "tfc:carrot",
        grain: 0.0,
        fruit: 0.0,
        veg: 2.0,
        protein: 0.0,
        dairy: 0.0,
    },
    FoodDef {
        id: "tfc:bread",
        grain: 3.0,
        fruit: 0.0,
        veg: 0.0,
        protein: 0.0,
        dairy: 0.0,
    },
    FoodDef {
        id: "tfc:cooked_meat",
        grain: 0.0,
        fruit: 0.0,
        veg: 0.0,
        protein: 3.0,
        dairy: 0.0,
    },
    FoodDef {
        id: "tfc:cheese",
        grain: 0.0,
        fruit: 0.0,
        veg: 0.0,
        protein: 0.0,
        dairy: 2.0,
    },
];

pub fn find(id: &str) -> Option<&'static FoodDef> {
    FOODS.iter().find(|f| f.id == id)
}
