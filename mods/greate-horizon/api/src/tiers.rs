//! Greate-inspired kinetic tier rules (pure logic, no Host).
//! Voltage mirrors GregTech / GTCEu packet volts. Stress is a Create-like capacity proxy.

#[derive(Clone, Copy, Debug, PartialEq, Eq, PartialOrd, Ord)]
pub enum KineticTier {
    Ulv,
    Lv,
    Mv,
    Hv,
    Ev,
    Iv,
    Luv,
    Zpm,
    Uv,
}

impl KineticTier {
    pub fn voltage(self) -> i32 {
        match self {
            KineticTier::Ulv => 8,
            KineticTier::Lv => 32,
            KineticTier::Mv => 128,
            KineticTier::Hv => 512,
            KineticTier::Ev => 2_048,
            KineticTier::Iv => 8_192,
            KineticTier::Luv => 32_768,
            KineticTier::Zpm => 131_072,
            KineticTier::Uv => 524_288,
        }
    }

    /// Max stress units a shaft of this tier may carry (workshop proxy).
    pub fn stress_capacity(self) -> i32 {
        match self {
            KineticTier::Ulv => 64,
            KineticTier::Lv => 256,
            KineticTier::Mv => 1_024,
            KineticTier::Hv => 4_096,
            KineticTier::Ev => 16_384,
            KineticTier::Iv => 65_536,
            KineticTier::Luv => 262_144,
            KineticTier::Zpm => 1_048_576,
            KineticTier::Uv => 4_194_304,
        }
    }

    pub fn from_shaft_id(id: &str) -> Option<Self> {
        let id = id.rsplit_once(':').map(|(_, r)| r).unwrap_or(id);
        match id {
            "andesite_shaft" | "andesteel_shaft" => Some(KineticTier::Ulv),
            "steel_shaft" => Some(KineticTier::Lv),
            "aluminium_shaft" | "aluminum_shaft" => Some(KineticTier::Mv),
            "stainless_shaft" | "stainless_steel_shaft" => Some(KineticTier::Hv),
            "titanium_shaft" => Some(KineticTier::Ev),
            "tungstensteel_shaft" => Some(KineticTier::Iv),
            _ => None,
        }
    }

    /// Machine recipe may run when shaft tier voltage >= recipe min voltage.
    pub fn accepts_recipe(self, recipe_min_voltage: i32) -> bool {
        self.voltage() >= recipe_min_voltage
    }
}

/// Convert rotational speed (RPM proxy) + tier into EU/t a dynamo would emit.
pub fn dynamo_eu_per_tick(tier: KineticTier, rpm: i32) -> i32 {
    if rpm <= 0 {
        return 0;
    }
    let amps = (rpm / 32).clamp(1, 4);
    tier.voltage().saturating_mul(amps)
}

/// Convert EU packet into stress load for a motor driving a shaft.
pub fn motor_stress_draw(tier: KineticTier, eu: i32) -> i32 {
    if eu <= 0 {
        return 0;
    }
    let packets = (eu / tier.voltage().max(1)).max(1);
    packets.saturating_mul(tier.stress_capacity() / 16).max(1)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn lv_accepts_lv_recipe_not_hv() {
        assert!(KineticTier::Lv.accepts_recipe(32));
        assert!(!KineticTier::Lv.accepts_recipe(512));
        assert!(KineticTier::Hv.accepts_recipe(512));
    }

    #[test]
    fn shaft_ids_map() {
        assert_eq!(KineticTier::from_shaft_id("greate:steel_shaft"), Some(KineticTier::Lv));
        assert_eq!(KineticTier::from_shaft_id("greate:aluminium_shaft"), Some(KineticTier::Mv));
        assert_eq!(KineticTier::from_shaft_id("greate:unknown"), None);
    }

    #[test]
    fn dynamo_scales_with_rpm() {
        assert_eq!(dynamo_eu_per_tick(KineticTier::Lv, 0), 0);
        assert_eq!(dynamo_eu_per_tick(KineticTier::Lv, 32), 32);
        assert_eq!(dynamo_eu_per_tick(KineticTier::Lv, 128), 128);
    }

    #[test]
    fn motor_draws_stress() {
        assert!(motor_stress_draw(KineticTier::Lv, 32) > 0);
        assert_eq!(motor_stress_draw(KineticTier::Lv, 0), 0);
    }
}
