"""Add vanilla crafting recipes JEI can show (cables, plates, basic machines)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECIPE = ROOT / "data" / "greglite" / "recipe"
EXTRACT = ROOT / "tracker" / "gtm_extract"


def write(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def shaped(key: str, pattern: list[str], keys: dict, result: str, count: int = 1) -> None:
    write(
        RECIPE / f"craft_{key}.json",
        {
            "type": "minecraft:crafting_shaped",
            "pattern": pattern,
            "key": {k: {"item": v} for k, v in keys.items()},
            "result": {"id": result, "count": count},
        },
    )


def shapeless(key: str, ingredients: list[str], result: str, count: int = 1) -> None:
    write(
        RECIPE / f"craft_{key}.json",
        {
            "type": "minecraft:crafting_shapeless",
            "ingredients": [{"item": i} for i in ingredients],
            "result": {"id": result, "count": count},
        },
    )


def main() -> None:
    n = 0
    # plates from ingots (compressor still preferred in-world)
    for mid, ingot in [
        ("tin", "greglite:tin_ingot"),
        ("bronze", "greglite:bronze_ingot"),
        ("copper", "minecraft:copper_ingot"),
        ("iron", "minecraft:iron_ingot"),
        ("gold", "minecraft:gold_ingot"),
        ("silver", "greglite:silver_ingot"),
    ]:
        shaped(
            f"{mid}_plate",
            ["H", "I", "I"],
            {"H": "minecraft:iron_ingot", "I": ingot},
            f"greglite:{mid}_plate",
        )
        n += 1
        shapeless(f"{mid}_dust_from_ingot", [ingot, "minecraft:flint"], f"greglite:{mid}_dust")
        n += 1

    cables = json.loads((EXTRACT / "cable_materials.json").read_text(encoding="utf-8"))["cables"]
    for c in cables:
        mid = c["id"] if isinstance(c, dict) else str(c)
        wire = f"greglite:{mid}_wire"
        # wire may not exist for all — skip if no item def
        if not (ROOT / "data/greglite/horizon/item" / f"{mid}_wire.json").exists():
            continue
        shapeless(
            f"{mid}_cable_1x",
            [wire, "greglite:rubber"],
            f"greglite:{mid}_cable_1x",
        )
        n += 1
        shaped(
            f"{mid}_cable_4x",
            ["CC", "CC"],
            {"C": f"greglite:{mid}_cable_1x"},
            f"greglite:{mid}_cable_4x",
        )
        n += 1

    # bronze from copper+tin (also alloy smelter)
    shaped(
        "bronze_ingot",
        ["CC", "CT"],
        {"C": "minecraft:copper_ingot", "T": "greglite:tin_ingot"},
        "greglite:bronze_ingot",
        4,
    )
    n += 1

    # rubber from slime (placeholder)
    shapeless("rubber", ["minecraft:slime_ball", "minecraft:coal"], "greglite:rubber", 2)
    n += 1

    print("crafting recipes written", n)


if __name__ == "__main__":
    main()
