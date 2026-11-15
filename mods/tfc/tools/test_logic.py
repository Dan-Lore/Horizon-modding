#!/usr/bin/env python3
"""Mirror of pure TFC Rust helpers (no Horizon required)."""
from __future__ import annotations

TICKS_PER_DAY = 24_000
DAYS_PER_MONTH = 8
MONTHS = [
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
]


def month_index(day_time: int) -> int:
    day = day_time // TICKS_PER_DAY
    return (day // DAYS_PER_MONTH) % 12


def sample_temp(x: float, y: float, z: float, season_off: float = 0.0) -> float:
    return 14.0 + season_off - (z * 0.04) + ((y - 64.0) * -0.006)


def thirst_drain(value: float, seconds: float, sprint: bool = False) -> float:
    rate = 0.075 if sprint else 0.05
    return max(0.0, value - rate * seconds)


def crop_ok(temp: float, rain: float, min_t: float, max_t: float, min_r: float, max_r: float) -> bool:
    return min_t <= temp <= max_t and min_r <= rain <= max_r


def main() -> None:
    assert MONTHS[month_index(0)] == "Early Spring"
    assert MONTHS[month_index(DAYS_PER_MONTH * TICKS_PER_DAY)] == "Spring"
    assert sample_temp(0, 164, 0) < sample_temp(0, 64, 0)
    assert thirst_drain(100, 10) < 100
    assert crop_ok(20, 100, 5, 25, 50, 150)
    assert not crop_ok(0, 100, 5, 25, 50, 150)
    print("tfc logic ok")


if __name__ == "__main__":
    main()
