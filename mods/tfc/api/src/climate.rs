//! Thin climate from player position (hybrid until full worldgen).

use crate::calendar;

pub struct ClimateSample {
    pub temp_c: f32,
    pub rainfall: f32,
}

pub fn sample(x: f64, y: f64, z: f64, day_time: i64) -> ClimateSample {
    let lat = z as f32 * 0.04;
    let alt = (y as f32 - 64.0) * -0.006;
    let temp = 14.0 + calendar::season_temp_offset(day_time) - lat + alt;
    let rain = (120.0 + ((x as f32 * 0.01).sin() * 40.0)) * calendar::season_rain_mult(day_time);
    ClimateSample {
        temp_c: temp,
        rainfall: rain.max(0.0),
    }
}

pub fn crop_ok(temp: f32, rain: f32, min_t: f32, max_t: f32, min_r: f32, max_r: f32) -> bool {
    temp >= min_t && temp <= max_t && rain >= min_r && rain <= max_r
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn higher_is_colder() {
        let low = sample(0.0, 64.0, 0.0, 0).temp_c;
        let high = sample(0.0, 164.0, 0.0, 0).temp_c;
        assert!(high < low);
    }
}
