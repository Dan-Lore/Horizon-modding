#!/usr/bin/env python3
"""Bulk machine recipes across materials_core for M25 density."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXTRACT = ROOT / "tracker" / "gtm_extract" / "materials_core.json"
RECIPE = ROOT / "data" / "gtceu" / "recipe"
ITEMS = ROOT / "data" / "gtceu" / "horizon" / "item"
BLOCKS = ROOT / "data" / "gtceu" / "horizon" / "block"

VANILLA_INGOT = {
    "iron": "minecraft:iron_ingot",
    "copper": "minecraft:copper_ingot",
    "gold": "minecraft:gold_ingot",
    "netherite": "minecraft:netherite_ingot",
}


def exists(iid: str) -> bool:
    if iid.startswith("minecraft:"):
        return True
    stem = iid.split(":", 1)[1]
    return (ITEMS / f"{stem}.json").exists() or (BLOCKS / f"{stem}.json").exists()


def form(mid: str, f: str) -> str | None:
    if f == "ingot" and mid in VANILLA_INGOT:
        return VANILLA_INGOT[mid]
    iid = f"gtceu:{mid}_{f}"
    return iid if exists(iid) else None


def write(name: str, body: dict) -> None:
    RECIPE.mkdir(parents=True, exist_ok=True)
    (RECIPE / name).write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")


def one(mtype: str, key: str, *, ingredient: str, result: str, eu: int = 32, duration: int = 80) -> None:
    write(
        f"m25b_{mtype}_{key}.json",
        {
            "type": f"gtceu:{mtype}",
            "ingredient": {"item": ingredient},
            "result": {"id": result, "count": 1},
            "duration": duration,
            "eu": eu,
            "min_voltage": 32,
        },
    )


def main() -> None:
    mats = [m["id"] for m in json.loads(EXTRACT.read_text(encoding="utf-8"))["materials"]]
    n = 0
    for mid in mats:
        ingot, dust, plate, rod, wire, foil, gear, screw, nugget = (
            form(mid, f)
            for f in ("ingot", "dust", "plate", "rod", "wire", "foil", "gear", "screw", "nugget")
        )
        if ingot and dust:
            for mt in ("macerator", "forge_hammer", "rock_crusher"):
                one(mt, f"{mid}_ingot_dust", ingredient=ingot, result=dust)
                n += 1
            for mt in ("electric_furnace", "arc_furnace", "alloy_smelter"):
                one(mt, f"{mid}_dust_ingot", ingredient=dust, result=ingot, eu=48)
                n += 1
        if ingot and plate:
            for mt in ("compressor", "forge_hammer", "bender", "forming_press"):
                one(mt, f"{mid}_ingot_plate", ingredient=ingot, result=plate)
                n += 1
        if plate and dust:
            one("macerator", f"{mid}_plate_dust", ingredient=plate, result=dust)
            n += 1
        if ingot and rod:
            for mt in ("lathe", "extruder"):
                one(mt, f"{mid}_ingot_rod", ingredient=ingot, result=rod)
                n += 1
        if ingot and wire:
            for mt in ("wiremill", "spooler", "extruder"):
                one(mt, f"{mid}_ingot_wire", ingredient=ingot, result=wire)
                n += 1
        if plate and foil:
            one("bender", f"{mid}_plate_foil", ingredient=plate, result=foil)
            n += 1
        if plate and gear:
            one("forming_press", f"{mid}_plate_gear", ingredient=plate, result=gear)
            one("cutter", f"{mid}_plate_gear", ingredient=plate, result=gear)
            n += 2
        if plate and screw:
            one("cutter", f"{mid}_plate_screw", ingredient=plate, result=screw)
            n += 1
        if rod and screw:
            one("lathe", f"{mid}_rod_screw", ingredient=rod, result=screw)
            n += 1
        if dust and nugget:
            one("packer", f"{mid}_dust_nugget", ingredient=dust, result=nugget)
            one("centrifuge", f"{mid}_dust_nugget", ingredient=dust, result=nugget)
            n += 2
        # ore washer / chemical bath / electrolyzer stand-ins
        if dust:
            for mt, eu in (("ore_washer", 24), ("chemical_bath", 32), ("electrolyzer", 64), ("extractor", 32)):
                one(mt, f"{mid}_dust_loop", ingredient=dust, result=dust, eu=eu)
                n += 1
            if plate:
                one(
                    "chemical_reactor",
                    f"{mid}_plate_dust",
                    ingredient=plate,
                    result=dust,
                    eu=48,
                    duration=120,
                )
                n += 1
                write(
                    f"m25b_distillery_{mid}.json",
                    {
                        "type": "gtceu:distillery",
                        "ingredient": {"item": dust},
                        "result": {"id": plate, "count": 1},
                        "duration": 140,
                        "eu": 48,
                    },
                )
                n += 1
    print(f"wrote_approx={n} recipe_files_now={len(list(RECIPE.glob('*.json')))}")


if __name__ == "__main__":
    main()
