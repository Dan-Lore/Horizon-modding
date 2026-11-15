//! Thin climate + calendar (hybrid W1). Uses day_time when available.

#[derive(Clone, Copy, Debug)]
pub struct ClimateSample {
    pub season: &'static str,
    pub month: &'static str,
    pub temp_c: f32,
    pub rainfall: f32,
}

const MONTHS: &[(&str, &str, f32)] = &[
    ("january", "winter", -8.0),
    ("february", "winter", -6.0),
    ("march", "spring", -2.0),
    ("april", "spring", 2.0),
    ("may", "spring", 6.0),
    ("june", "summer", 10.0),
    ("july", "summer", 12.0),
    ("august", "summer", 10.0),
    ("september", "autumn", 4.0),
    ("october", "autumn", 0.0),
    ("november", "autumn", -4.0),
    ("december", "winter", -8.0),
];

const DAYS_PER_MONTH: i64 = 8;
const BASE_TEMP: f32 = 14.0;
const BASE_RAIN: f32 = 300.0;

/// `day_time` is Minecraft day-time ticks (0..24000) plus days*24000 when host provides it.
pub fn sample(absolute_day: i64, x: i32, z: i32) -> ClimateSample {
    let month_idx = ((absolute_day / DAYS_PER_MONTH).rem_euclid(12)) as usize;
    let (month, season, offset) = MONTHS[month_idx.min(11)];
    // Soft spatial noise from block coords (no worldgen map yet).
    let spatial = ((x.wrapping_mul(374761393) ^ z.wrapping_mul(668265263)) as f32).sin() * 3.0;
    let rain_noise = ((x.wrapping_mul(127) ^ z.wrapping_mul(311)) as f32 % 97.0).abs();
    ClimateSample {
        season,
        month,
        temp_c: BASE_TEMP + offset + spatial,
        rainfall: (BASE_RAIN + rain_noise * 2.0).clamp(50.0, 500.0),
    }
}

pub fn hud_line(c: &ClimateSample, thirst: f32) -> String {
    format!(
        "TFC {} ({}) | {:.0}°C | rain {:.0} | thirst {:.0}%",
        c.season,
        c.month,
        c.temp_c,
        c.rainfall,
        (thirst * 100.0).clamp(0.0, 100.0)
    )
}

pub fn crop_allowed(c: &ClimateSample, min_temp: f32, max_temp: f32, seasons: &[&str]) -> bool {
    c.temp_c >= min_temp
        && c.temp_c <= max_temp
        && seasons.iter().any(|s| *s == c.season)
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn winter_is_cold() {
        let c = sample(0, 0, 0); // january
        assert_eq!(c.season, "winter");
        assert!(c.temp_c < BASE_TEMP);
    }

    #[test]
    fn summer_allows_crops() {
        let c = sample(DAYS_PER_MONTH * 6, 10, 10); // july-ish
        assert_eq!(c.season, "summer");
        assert!(crop_allowed(&c, 0.0, 35.0, &["spring", "summer"]));
    }
}
