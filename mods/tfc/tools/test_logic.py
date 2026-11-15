#!/usr/bin/env python3
"""Pure helpers mirroring climate/thirst gates (no Horizon). From PR #3, aligned to PR #4 tables."""

from __future__ import annotations

import json
from pathlib import Path

MOD = Path(__file__).resolve().parents[1]
TICKS_PER_DAY = 24_000


def load_climate() -> dict:
    return json.loads((MOD / "tables" / "climate_seasons.json").read_text(encoding="utf-8"))


def month_index(day: int, days_per_month: int) -> int:
    return (day // days_per_month) % 12


def sample_temp(table: dict, day: int, y: float = 64.0, z: float = 0.0) -> float:
    months = table["months"]
    idx = month_index(day, table["days_per_month"])
    # Match climate.rs / check.py: x=z=0 → no spatial term; altitude mild.
    return table["base_temp"] + months[idx]["temp_offset"] + ((y - 64.0) * -0.006)


def thirst_drain(value: float, seconds: float, sprint: bool = False) -> float:
    rate = 0.075 if sprint else 0.05
    return max(0.0, value - rate * seconds)


def crop_ok(temp: float, season: str, crop: dict) -> bool:
    return crop["min_temp"] <= temp <= crop["max_temp"] and season in crop["seasons"]


def main() -> None:
    climate = load_climate()
    crops = json.loads((MOD / "tables" / "crops.json").read_text(encoding="utf-8"))
    wheat = next(c for c in crops if c["id"] == "tfc:crop_wheat")
    barley = next(c for c in crops if c["id"] == "tfc:crop_barley")

    assert climate["months"][month_index(0, 8)]["name"] == "january"
    assert climate["months"][month_index(48, 8)]["name"] == "july"
    assert sample_temp(climate, 0) < sample_temp(climate, 48)
    assert thirst_drain(100, 10) < 100

    jul_temp = sample_temp(climate, 48)
    jul_season = climate["months"][month_index(48, 8)]["season"]
    jan_temp = sample_temp(climate, 0)
    jan_season = climate["months"][month_index(0, 8)]["season"]
    assert crop_ok(jul_temp, jul_season, wheat)
    assert not crop_ok(jan_temp, jan_season, wheat)
    assert not crop_ok(jul_temp, jul_season, barley)

    # ticks helper kept for HUD calendar smoke docs
    assert TICKS_PER_DAY == 24_000
    print("tfc logic ok")


if __name__ == "__main__":
    main()
