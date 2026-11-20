#!/usr/bin/env python3
"""Create TFC barrel soak items/recipes + lang for M75 close."""

from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1] / "mods" / "tfc"
ITEMS = ROOT / "assets" / "tfc" / "items"
MODELS = ROOT / "assets" / "tfc" / "models" / "item"
TEX = ROOT / "assets" / "tfc" / "textures" / "item"
HORIZON = ROOT / "data" / "tfc" / "horizon" / "item"
RECIPE = ROOT / "data" / "tfc" / "recipe"
LANG = ROOT / "assets" / "tfc" / "lang" / "en_us.json"


def ensure_item(name: str, template: str = "minecraft:paper", clone_tex: str = "soaked_hide") -> None:
    HORIZON.mkdir(parents=True, exist_ok=True)
    (HORIZON / f"{name}.json").write_text(
        json.dumps({"template": template}, indent=2) + "\n", encoding="utf-8"
    )
    (ITEMS / f"{name}.json").write_text(
        json.dumps(
            {"model": {"type": "minecraft:model", "model": f"tfc:item/{name}"}},
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    (MODELS / f"{name}.json").write_text(
        json.dumps(
            {
                "parent": "minecraft:item/generated",
                "textures": {"layer0": f"tfc:item/{name}"},
            },
            indent=2,
        )
        + "\n",
        encoding="utf-8",
    )
    src = TEX / f"{clone_tex}.png"
    dst = TEX / f"{name}.png"
    if not dst.exists():
        if src.exists():
            shutil.copy(src, dst)
        elif (TEX / "ore_deposit.png").exists():
            shutil.copy(TEX / "ore_deposit.png", dst)


def main() -> None:
    lang = json.loads(LANG.read_text(encoding="utf-8"))
    for name, tmpl, clone in [
        ("dye_yellow", "minecraft:yellow_dye", "dye_red"),
        ("dye_green", "minecraft:green_dye", "dye_red"),
        ("dye_black", "minecraft:black_dye", "dye_red"),
        ("scraped_hide", "minecraft:leather", "soaked_hide"),
        ("prepared_hide", "minecraft:leather", "soaked_hide"),
        ("malt", "minecraft:wheat", "flour" if (ITEMS / "flour.json").exists() else "soaked_hide"),
        ("beer", "minecraft:potion", "brine"),
        ("cider", "minecraft:potion", "brine"),
        ("vinegar", "minecraft:potion", "brine"),
        ("vodka", "minecraft:potion", "brine"),
    ]:
        ensure_item(name, tmpl, clone)
        lang[f"item.tfc.{name}"] = " ".join(p.capitalize() for p in name.split("_"))

    for kind in ("copper", "gold", "hematite"):
        lang[f"item.tfc.ore_deposit_{kind}"] = f"Ore Deposit ({kind.capitalize()})"

    barrels = [
        ("barrel_dye_yellow", "minecraft:yellow_dye", "tfc:dye_yellow", 80),
        ("barrel_dye_green", "minecraft:green_dye", "tfc:dye_green", 80),
        ("barrel_dye_black", "minecraft:black_dye", "tfc:dye_black", 80),
        ("barrel_scrape_hide", "tfc:soaked_hide", "tfc:scraped_hide", 200),
        ("barrel_prepare_hide", "tfc:scraped_hide", "tfc:prepared_hide", 200),
        ("barrel_leather", "tfc:prepared_hide", "minecraft:leather", 240),
        ("barrel_malt", "minecraft:wheat", "tfc:malt", 160),
        ("barrel_beer", "tfc:malt", "tfc:beer", 200),
        ("barrel_cider", "minecraft:apple", "tfc:cider", 180),
        ("barrel_vinegar", "minecraft:milk_bucket", "tfc:vinegar", 160),
        ("barrel_vodka", "minecraft:potato", "tfc:vodka", 220),
    ]
    for name, ing, out, dur in barrels:
        (RECIPE / f"{name}.json").write_text(
            json.dumps(
                {
                    "type": "tfc:barrel",
                    "ingredient": ing,
                    "result": {"id": out, "count": 1},
                    "duration": dur,
                },
                indent=2,
            )
            + "\n",
            encoding="utf-8",
        )

    LANG.write_text(json.dumps(lang, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print("tfc barrel densify ok")


if __name__ == "__main__":
    main()
