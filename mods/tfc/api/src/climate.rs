//! Thin climate + calendar (W1). Full rock-layer worldgen stays blocked (W12).

#[derive(Clone, Copy, Debug, PartialEq, Eq)]
pub enum Season {
    Spring,
    Summer,
    Autumn,
    Winter,
}

impl Season {
    pub fn label(self) -> &'static str {
        match self {
            Season::Spring => "Spring",
            Season::Summer => "Summer",
            Season::Autumn => "Autumn",
            Season::Winter => "Winter",
        }
    }
}

/// Deterministic climate from block position (hybrid bridge until W12).
pub fn sample(pos: [i32; 3]) -> (f32, f32) {
    let x = pos[0] as f32;
    let z = pos[2] as f32;
    let y = pos[1] as f32;
    // Rough latitude from Z + altitude lapse.
    let temp = 18.0 - (z.abs() / 250.0) - ((y - 64.0) * 0.05);
    let rain = 280.0 + (x * 0.07).sin() * 120.0 + (z * 0.05).cos() * 80.0;
    (temp, rain.clamp(0.0, 500.0))
}

/// Season from world day-of-year (8 Minecraft days ≈ 1 TFC month lite).
pub fn season_from_day(day: u64) -> Season {
    match (day / 8) % 4 {
        0 => Season::Spring,
        1 => Season::Summer,
        2 => Season::Autumn,
        _ => Season::Winter,
    }
}

pub fn crop_ok(temp: f32, rain: f32, tmin: f32, tmax: f32, rmin: f32, rmax: f32) -> bool {
    temp >= tmin && temp <= tmax && rain >= rmin && rain <= rmax
}
