//! Calendar / season from day time (thin hybrid).

pub const TICKS_PER_DAY: i64 = 24_000;
pub const DAYS_PER_MONTH: i64 = 8;
pub const MONTHS: [&str; 12] = [
    "Early Spring",
    "Spring",
    "Late Spring",
    "Early Summer",
    "Summer",
    "Late Summer",
    "Early Autumn",
    "Autumn",
    "Late Autumn",
    "Early Winter",
    "Winter",
    "Late Winter",
];

pub fn month_index(day_time: i64) -> usize {
    let day = day_time.div_euclid(TICKS_PER_DAY);
    let month = day.div_euclid(DAYS_PER_MONTH).rem_euclid(12);
    month as usize
}

pub fn season_name(day_time: i64) -> &'static str {
    MONTHS[month_index(day_time)]
}

pub fn season_temp_offset(day_time: i64) -> f32 {
    const OFFSETS: [f32; 12] = [-6.0, -2.0, 2.0, 6.0, 10.0, 8.0, 4.0, 0.0, -2.0, -6.0, -10.0, -8.0];
    OFFSETS[month_index(day_time)]
}

pub fn season_rain_mult(day_time: i64) -> f32 {
    const MULT: [f32; 12] = [1.1, 1.2, 1.1, 1.0, 0.9, 0.85, 1.0, 1.1, 1.15, 1.0, 0.9, 0.95];
    MULT[month_index(day_time)]
}

#[cfg(test)]
mod tests {
    use super::*;

    #[test]
    fn early_spring_at_zero() {
        assert_eq!(season_name(0), "Early Spring");
    }

    #[test]
    fn advances_after_month() {
        let t = DAYS_PER_MONTH * TICKS_PER_DAY;
        assert_eq!(season_name(t), "Spring");
    }
}
