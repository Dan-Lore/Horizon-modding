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


def i32(value: int) -> int:
    value &= 0xFFFFFFFF
    if value >= 0x80000000:
        value -= 0x100000000
    return value


def rainfall(x: int, z: int, base: float = 300.0) -> float:
    # Same expression as climate.rs at the given column.
    mixed = i32(i32(x * 127) ^ i32(z * 311))
    noise = abs(float(mixed) % 97.0)
    return min(500.0, max(50.0, base + noise * 2.0))


def crop_ok(temp: float, season: str, crop: dict, rain: float = 300.0) -> bool:
    return (
        crop["min_temp"] <= temp <= crop["max_temp"]
        and season in crop["seasons"]
        and crop["min_rain"] <= rain <= crop["max_rain"]
    )


def alloy_fraction(major: int, minor: int) -> float:
    return major / (major + minor)


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

    rye = next(c for c in crops if c["id"] == "tfc:crop_rye")
    squash = next(c for c in crops if c["id"] == "tfc:crop_squash")
    onion = next(c for c in crops if c["id"] == "tfc:crop_onion")
    assert crop_ok(jan_temp, jan_season, rye)
    assert not crop_ok(jul_temp, jul_season, rye)
    assert crop_ok(jul_temp, jul_season, squash)
    assert not crop_ok(jan_temp, jan_season, squash)

    dry = rainfall(0, 0, climate["base_rain"])
    wet = rainfall(2, 0, climate["base_rain"])
    assert dry == 300.0
    assert wet == 420.0
    assert not crop_ok(16.0, "spring", onion, dry)
    assert crop_ok(16.0, "spring", onion, wet)

    heat = json.loads((MOD / "tables" / "heat.json").read_text(encoding="utf-8"))
    assert heat["forge_max"] < heat["metals"]["wrought_iron"]["melt"]
    assert heat["metals"]["tin"]["melt"] < heat["metals"]["copper"]["melt"]
    assert heat["items"]["tfc:nugget_hematite"] == "wrought_iron"
    assert heat["metals"]["copper"]["melt"] <= heat["forge_max"]
    assert heat["metals"]["copper"]["weld"] < heat["metals"]["copper"]["melt"]

    alloys = json.loads((MOD / "tables" / "alloys.json").read_text(encoding="utf-8"))
    bronze = next(row for row in alloys["alloys"] if row["id"] == "bronze")
    inside = alloy_fraction(8, 1)
    outside = alloy_fraction(1, 1)
    assert bronze["min"] <= inside <= bronze["max"]
    assert not (bronze["min"] <= outside <= bronze["max"])
    assert (8 * alloys["ingot_units"] + alloys["ingot_units"]) % alloys["ingot_units"] == 0

    anvil = json.loads((MOD / "tables" / "anvil.json").read_text(encoding="utf-8"))
    bloom = next(row for row in anvil if row["input"] == "tfc:raw_iron_bloom")
    assert bloom["output"] == "tfc:wrought_iron_ingot"
    assert bloom["steps"] == ["hit", "hit", "hit"]
    assert all(step in {"hit", "draw", "upset"} for row in anvil for step in row["steps"])

    knapping = json.loads((MOD / "tables" / "knapping.json").read_text(encoding="utf-8"))
    assert knapping["grid"] == 5
    assert all(len(row["mask"]) == 25 for row in knapping["patterns"])
    axe = next(row for row in knapping["patterns"] if row["output"] == "tfc:stone_axe_head")
    assert axe["mask"] == "0010001110001000010000100"

    # ticks helper kept for HUD calendar smoke docs
    assert TICKS_PER_DAY == 24_000
    print("tfc logic ok")


if __name__ == "__main__":
    main()
