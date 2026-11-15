//! Thirst pool (0..=max).

#[derive(Clone, Debug)]
pub struct Thirst {
    pub value: f32,
    pub max: f32,
}

impl Thirst {
    pub fn new() -> Self {
        Self {
            value: 100.0,
            max: 100.0,
        }
    }

    pub fn drain(&mut self, seconds: f32, sprinting: bool) {
        let rate = if sprinting { 0.075 } else { 0.05 };
        self.value = (self.value - rate * seconds).max(0.0);
    }

    pub fn drink(&mut self, amount: f32) {
        self.value = (self.value + amount).min(self.max);
    }

    pub fn exhausted(&self) -> bool {
        self.value < 5.0
    }
}

impl Default for Thirst {
    fn default() -> Self {
        Self::new()
    }
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn drink_and_drain() {
        let mut t = Thirst::new();
        t.drain(10.0, false);
        assert!(t.value < 100.0);
        t.drink(40.0);
        assert!(t.value > 90.0);
    }
}
