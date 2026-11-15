//! Five TFC-style nutrients.

#[derive(Clone, Debug)]
pub struct Nutrition {
    pub fruit: f32,
    pub vegetable: f32,
    pub grain: f32,
    pub protein: f32,
    pub dairy: f32,
}

impl Nutrition {
    pub fn new() -> Self {
        Self {
            fruit: 50.0,
            vegetable: 50.0,
            grain: 50.0,
            protein: 50.0,
            dairy: 50.0,
        }
    }

    pub fn add(&mut self, kind: &str, amount: f32) {
        let slot = match kind {
            "fruit" => &mut self.fruit,
            "vegetable" => &mut self.vegetable,
            "grain" => &mut self.grain,
            "protein" => &mut self.protein,
            "dairy" => &mut self.dairy,
            _ => return,
        };
        *slot = (*slot + amount).clamp(0.0, 100.0);
    }

    pub fn decay_day(&mut self, rate: f32) {
        self.fruit = (self.fruit - rate).max(0.0);
        self.vegetable = (self.vegetable - rate).max(0.0);
        self.grain = (self.grain - rate).max(0.0);
        self.protein = (self.protein - rate).max(0.0);
        self.dairy = (self.dairy - rate).max(0.0);
    }

    pub fn summary(&self) -> String {
        format!(
            "F{:.0} V{:.0} G{:.0} P{:.0} D{:.0}",
            self.fruit, self.vegetable, self.grain, self.protein, self.dairy
        )
    }
}

impl Default for Nutrition {
    fn default() -> Self {
        Self::new()
    }
}

pub fn food_nutrient(item: &str) -> Option<(&'static str, f32)> {
    match item {
        "tfc:food_red_apple" => Some(("fruit", 1.5)),
        "tfc:food_carrot" => Some(("vegetable", 1.5)),
        "tfc:food_wheat_bread" => Some(("grain", 1.5)),
        "tfc:food_cooked_beef" => Some(("protein", 1.5)),
        "tfc:food_cheese" => Some(("dairy", 1.5)),
        _ => None,
    }
}
