"""Pure-Python mirror of api/src/tiers.rs for CI without cargo on PATH."""

from __future__ import annotations


VOLTAGE = {
    "ULV": 8,
    "LV": 32,
    "MV": 128,
    "HV": 512,
    "EV": 2048,
    "IV": 8192,
    "LUV": 32768,
    "ZPM": 131072,
    "UV": 524288,
}

SHAFT = {
    "andesteel_shaft": "ULV",
    "steel_shaft": "LV",
    "aluminium_shaft": "MV",
    "stainless_shaft": "HV",
}


def accepts(tier: str, recipe_min: int) -> bool:
    return VOLTAGE[tier] >= recipe_min


def dynamo_eu(tier: str, rpm: int) -> int:
    if rpm <= 0:
        return 0
    amps = max(1, min(4, rpm // 32))
    return VOLTAGE[tier] * amps


def main() -> None:
    assert accepts("LV", 32)
    assert not accepts("LV", 512)
    assert accepts("HV", 512)
    assert SHAFT["steel_shaft"] == "LV"
    assert dynamo_eu("LV", 0) == 0
    assert dynamo_eu("LV", 32) == 32
    assert dynamo_eu("LV", 128) == 128
    print("greate tier tests ok")


if __name__ == "__main__":
    main()
