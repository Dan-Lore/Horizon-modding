#!/usr/bin/env python3
"""Generate TFC Horizon content JSON (blocks, items, recipes, lang) from tables."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "tfc"
BLOCK = DATA / "horizon" / "block"
ITEM = DATA / "horizon" / "item"
RECIPE = DATA / "recipe"
LANG = ROOT / "assets" / "tfc" / "lang" / "en_us.json"
TABLES = ROOT / "tables"

ROCKS = [
    "andesite",
    "basalt",
    "chalk",
    "chert",
    "conglomerate",
    "dacite",
    "diorite",
    "dolomite",
    "gabbro",
    "gneiss",
    "limestone",
    "marble",
    "phyllite",
    "quartzite",
    "rhyolite",
    "schist",
    "shale",
    "slate",
]

# W2 slice highlighted first; full list for later waves.
SLICE_ROCKS = ["andesite", "basalt", "limestone", "shale", "gneiss", "marble"]

ORES = [
    ("native_copper", "copper"),
    ("native_gold", "gold"),
    ("hematite", "iron"),
    ("limonite", "iron"),
    ("magnetite", "iron"),
    ("malachite", "copper"),
    ("tetrahedrite", "copper"),
    ("cassiterite", "tin"),
    ("sphalerite", "zinc"),
    ("galena", "lead"),
    ("bismuthinite", "bismuth"),
    ("garnierite", "nickel"),
    ("silver", "silver"),
]

METALS = [
    "copper",
    "tin",
    "bronze",
    "bismuth",
    "bismuth_bronze",
    "black_bronze",
    "wrought_iron",
    "steel",
    "gold",
    "silver",
    "zinc",
    "lead",
    "nickel",
]

TOOL_TYPES = ["pickaxe", "axe", "shovel", "hoe", "sword", "knife", "hammer", "saw", "scythe", "propick"]

FOODS = [
    ("red_apple", {"grain": 0, "fruit": 2, "veg": 0, "protein": 0, "dairy": 0}, "medium", "light"),
    ("carrot", {"grain": 0, "fruit": 0, "veg": 2, "protein": 0, "dairy": 0}, "small", "light"),
    ("cooked_beef", {"grain": 0, "fruit": 0, "veg": 0, "protein": 3, "dairy": 0}, "large", "heavy"),
    ("barley_bread", {"grain": 3, "fruit": 0, "veg": 0, "protein": 0, "dairy": 0}, "medium", "light"),
    ("cheese", {"grain": 0, "fruit": 0, "veg": 0, "protein": 0, "dairy": 3}, "small", "light"),
    ("green_bean", {"grain": 0, "fruit": 0, "veg": 2, "protein": 0, "dairy": 0}, "small", "light"),
    ("onion", {"grain": 0, "fruit": 0, "veg": 2, "protein": 0, "dairy": 0}, "small", "light"),
    ("potato", {"grain": 2, "fruit": 0, "veg": 1, "protein": 0, "dairy": 0}, "medium", "light"),
]

CROPS = [
    ("barley", 5, 25, 100, 300),
    ("wheat", 0, 30, 100, 400),
    ("oat", 5, 25, 150, 400),
    ("rye", -5, 20, 100, 350),
    ("maize", 10, 35, 200, 400),
    ("cabbage", 0, 25, 150, 400),
    ("tomato", 10, 35, 100, 350),
    ("onion", 0, 30, 100, 400),
    ("potato", 0, 25, 150, 400),
    ("green_bean", 5, 30, 150, 400),
]

MACHINES = [
    ("firepit", "minecraft:campfire"),
    ("pit_kiln", "minecraft:dirt"),
    ("charcoal_forge", "minecraft:furnace"),
    ("bloomery", "minecraft:blast_furnace"),
    ("anvil_stone", "minecraft:anvil"),
    ("anvil_copper", "minecraft:anvil"),
    ("anvil_bronze", "minecraft:anvil"),
    ("anvil_wrought_iron", "minecraft:anvil"),
    ("quern", "minecraft:grindstone"),
    ("barrel", "minecraft:barrel"),
    ("sluice", "minecraft:hopper"),
    ("blast_furnace", "minecraft:blast_furnace"),
    ("crucible", "minecraft:cauldron"),
    ("powderkeg", "minecraft:tnt"),
]


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def block(name: str, template: str = "minecraft:stone", hardness: float = 1.5) -> None:
    write_json(
        BLOCK / f"{name}.json",
        {
            "template": template,
            "properties": {"hardness": hardness, "sounds": "minecraft:stone"},
            "item": True,
        },
    )


def item(name: str, template: str = "minecraft:iron_ingot") -> None:
    write_json(ITEM / f"{name}.json", {"template": template})


def shaped(name: str, pattern: list[str], keys: dict, result: str, count: int = 1) -> None:
    write_json(
        RECIPE / f"{name}.json",
        {
            "type": "minecraft:crafting_shaped",
            "pattern": pattern,
            "key": {k: {"item": v} for k, v in keys.items()},
            "result": {"item": result, "count": count},
        },
    )


def shapeless(name: str, ingredients: list[str], result: str, count: int = 1) -> None:
    write_json(
        RECIPE / f"{name}.json",
        {
            "type": "minecraft:crafting_shapeless",
            "ingredients": [{"item": i} for i in ingredients],
            "result": {"item": result, "count": count},
        },
    )


def title(s: str) -> str:
    return s.replace("_", " ").title()


def main() -> None:
    for d in (BLOCK, ITEM, RECIPE, LANG.parent):
        d.mkdir(parents=True, exist_ok=True)
        for p in d.glob("*.json"):
            if p.name != "en_us.json":
                p.unlink()

    lang: dict[str, str] = {
        "itemGroup.tfc": "TFC Horizon",
        "tfc.hud.climate": "Climate",
        "tfc.hud.thirst": "Thirst",
        "tfc.hud.season": "Season",
    }

    # --- Rocks ---
    for rock in ROCKS:
        for form, tmpl, hard in [
            ("", "minecraft:stone", 1.5),
            ("_cobble", "minecraft:cobblestone", 1.5),
            ("_gravel", "minecraft:gravel", 0.6),
            ("_sand", "minecraft:sand", 0.5),
            ("_bricks", "minecraft:stone_bricks", 1.5),
            ("_smooth", "minecraft:smooth_stone", 1.5),
            ("_raw", "minecraft:stone", 2.0),
        ]:
            name = f"rock_{rock}{form}"
            block(name, tmpl, hard)
            lang[f"block.tfc.{name}"] = f"{title(rock)}{(' ' + title(form[1:])) if form else ' Rock'}"
            lang[f"item.tfc.{name}"] = lang[f"block.tfc.{name}"]
        item(f"rock_{rock}_loose", "minecraft:flint")
        lang[f"item.tfc.rock_{rock}_loose"] = f"Loose {title(rock)}"
        # knapping rock → stone tool heads (W3)
        shapeless(
            f"knap_{rock}_axe_head",
            [f"tfc:rock_{rock}_loose", f"tfc:rock_{rock}_loose"],
            f"tfc:stone_axe_head",
        )
        shapeless(
            f"knap_{rock}_knife_blade",
            [f"tfc:rock_{rock}_loose"],
            f"tfc:stone_knife_blade",
        )

    # --- Ores / nuggets ---
    for ore, metal in ORES:
        block(f"ore_{ore}", "minecraft:iron_ore", 3.0)
        item(f"ore_{ore}", "minecraft:raw_iron")
        item(f"small_ore_{ore}", "minecraft:iron_nugget")
        lang[f"block.tfc.ore_{ore}"] = f"{title(ore)} Ore"
        lang[f"item.tfc.ore_{ore}"] = f"{title(ore)}"
        lang[f"item.tfc.small_ore_{ore}"] = f"Small {title(ore)}"
        shapeless(f"nugget_from_{ore}", [f"tfc:small_ore_{ore}"] * 4, f"tfc:ore_{ore}")

    # --- Metals (ingots, sheets, double ingots, unfinished) ---
    for metal in METALS:
        for form, tmpl in [
            ("ingot", "minecraft:iron_ingot"),
            ("double_ingot", "minecraft:iron_ingot"),
            ("sheet", "minecraft:iron_ingot"),
            ("double_sheet", "minecraft:iron_ingot"),
            ("rod", "minecraft:stick"),
            ("dust", "minecraft:gunpowder"),
            ("nugget", "minecraft:iron_nugget"),
            ("unfinished_lamp", "minecraft:iron_ingot"),
        ]:
            name = f"metal_{metal}_{form}"
            item(name, tmpl)
            lang[f"item.tfc.{name}"] = f"{title(metal)} {title(form)}"
        for tool in TOOL_TYPES:
            head = f"metal_{metal}_{tool}_head"
            item(head, "minecraft:iron_ingot")
            lang[f"item.tfc.{head}"] = f"{title(metal)} {title(tool)} Head"
            full = f"metal_{metal}_{tool}"
            item(full, "minecraft:iron_pickaxe" if tool == "pickaxe" else "minecraft:iron_axe")
            lang[f"item.tfc.{full}"] = f"{title(metal)} {title(tool)}"
            shaped(
                f"tool_{metal}_{tool}",
                ["H", "S"],
                {"H": f"tfc:{head}", "S": "minecraft:stick"},
                f"tfc:{full}",
            )

    # Stone tools (W3)
    for part in ["axe_head", "knife_blade", "shovel_head", "hoe_head", "hammer_head", "javelin_head"]:
        item(f"stone_{part}", "minecraft:flint")
        lang[f"item.tfc.stone_{part}"] = f"Stone {title(part)}"
    for tool, head in [
        ("axe", "axe_head"),
        ("knife", "knife_blade"),
        ("shovel", "shovel_head"),
        ("hoe", "hoe_head"),
        ("hammer", "hammer_head"),
        ("javelin", "javelin_head"),
    ]:
        item(f"stone_{tool}", "minecraft:stone_axe")
        lang[f"item.tfc.stone_{tool}"] = f"Stone {title(tool)}"
        shaped(
            f"stone_{tool}",
            ["H", "S"],
            {"H": f"tfc:stone_{head}", "S": "minecraft:stick"},
            f"tfc:stone_{tool}",
        )

    item("prospector_pick", "minecraft:iron_pickaxe")
    lang["item.tfc.prospector_pick"] = "Prospector's Pick"
    shaped(
        "prospector_pick",
        ["CI", " S"],
        {"C": "tfc:metal_copper_ingot", "I": "minecraft:stick", "S": "minecraft:stick"},
        "tfc:prospector_pick",
    )

    # Pottery / clay (W4)
    for name, tmpl in [
        ("clay_ball_tfc", "minecraft:clay_ball"),
        ("unfired_vessel", "minecraft:flower_pot"),
        ("ceramic_vessel", "minecraft:flower_pot"),
        ("unfired_jug", "minecraft:flower_pot"),
        ("ceramic_jug", "minecraft:flower_pot"),
        ("unfired_mold_ingot", "minecraft:brick"),
        ("ceramic_mold_ingot", "minecraft:brick"),
        ("unfired_mold_pickaxe", "minecraft:brick"),
        ("ceramic_mold_pickaxe", "minecraft:brick"),
        ("unfired_mold_axe", "minecraft:brick"),
        ("ceramic_mold_axe", "minecraft:brick"),
        ("spindle", "minecraft:stick"),
        ("firestarter", "minecraft:flint_and_steel"),
        ("straw", "minecraft:wheat"),
        ("thatch", "minecraft:hay_block"),
        ("charcoal_tfc", "minecraft:charcoal"),
        ("flux", "minecraft:sugar"),
        ("wood_ash", "minecraft:gunpowder"),
        ("mortar", "minecraft:clay_ball"),
        ("glass_batch", "minecraft:glass"),
        ("blowpipe", "minecraft:stick"),
        ("powder_sulfur", "minecraft:gunpowder"),
        ("powder_saltpeter", "minecraft:sugar"),
        ("wool_yarn", "minecraft:string"),
        ("wool_cloth", "minecraft:white_wool"),
        ("burlap_cloth", "minecraft:brown_wool"),
        ("glue", "minecraft:slime_ball"),
        ("soaked_hide", "minecraft:leather"),
        ("scraped_hide", "minecraft:leather"),
        ("prepared_hide", "minecraft:leather"),
        ("large_raw_hide", "minecraft:leather"),
        ("medium_raw_hide", "minecraft:leather"),
        ("small_raw_hide", "minecraft:leather"),
        ("pan_empty", "minecraft:bowl"),
        ("pan_filled", "minecraft:bowl"),
        ("support_beam", "minecraft:oak_fence"),
        ("log_pile", "minecraft:oak_log"),
        ("lumber", "minecraft:oak_planks"),
        ("chisel", "minecraft:iron_axe"),
        ("wrought_iron_bloom", "minecraft:raw_iron"),
        ("raw_iron_bloom", "minecraft:raw_iron"),
        ("refined_iron_bloom", "minecraft:iron_ingot"),
    ]:
        item(name, tmpl)
        lang[f"item.tfc.{name}"] = title(name)

    shapeless("unfired_vessel", ["minecraft:clay_ball"] * 5, "tfc:unfired_vessel")
    shapeless("unfired_jug", ["minecraft:clay_ball"] * 3, "tfc:unfired_jug")
    shapeless("unfired_mold_ingot", ["minecraft:clay_ball"] * 2, "tfc:unfired_mold_ingot")
    # pit kiln "recipe" as shapeless surrogate for datapack smoke
    shapeless("fire_vessel", ["tfc:unfired_vessel", "minecraft:coal"], "tfc:ceramic_vessel")
    shapeless("fire_jug", ["tfc:unfired_jug", "minecraft:coal"], "tfc:ceramic_jug")
    shapeless("fire_mold_ingot", ["tfc:unfired_mold_ingot", "minecraft:coal"], "tfc:ceramic_mold_ingot")

    # Foods (W7)
    for fname, nutrients, size, weight in FOODS:
        item(f"food_{fname}", "minecraft:apple")
        lang[f"item.tfc.food_{fname}"] = title(fname)
        write_json(
            TABLES / "food" / f"{fname}.json",
            {"id": fname, "nutrients": nutrients, "size": size, "weight": weight, "decay_ticks": 48000},
        )

    # Crops (W8)
    for crop, tmin, tmax, rmin, rmax in CROPS:
        block(f"crop_{crop}", "minecraft:wheat", 0.0)
        item(f"seeds_{crop}", "minecraft:wheat_seeds")
        lang[f"block.tfc.crop_{crop}"] = title(crop)
        lang[f"item.tfc.seeds_{crop}"] = f"{title(crop)} Seeds"
        write_json(
            TABLES / "crops" / f"{crop}.json",
            {
                "id": crop,
                "temp_min": tmin,
                "temp_max": tmax,
                "rain_min": rmin,
                "rain_max": rmax,
                "stages": 8,
            },
        )

    # Machines (W3–W14)
    for mid, tmpl in MACHINES:
        block(mid, tmpl, 2.5)
        lang[f"block.tfc.{mid}"] = title(mid)
        lang[f"item.tfc.{mid}"] = title(mid)

    # Wood / supports (W10)
    for wood in ["oak", "birch", "spruce", "acacia", "ash", "aspen", "maple", "pine", "sequoia", "white_cedar", "willow"]:
        block(f"wood_{wood}_log", "minecraft:oak_log", 2.0)
        block(f"wood_{wood}_planks", "minecraft:oak_planks", 2.0)
        item(f"wood_{wood}_lumber", "minecraft:stick")
        lang[f"block.tfc.wood_{wood}_log"] = f"{title(wood)} Log"
        lang[f"block.tfc.wood_{wood}_planks"] = f"{title(wood)} Planks"
        lang[f"item.tfc.wood_{wood}_lumber"] = f"{title(wood)} Lumber"
        shapeless(f"lumber_{wood}", [f"tfc:wood_{wood}_log"], f"tfc:wood_{wood}_lumber", 8)

    block("support_horizontal", "minecraft:oak_fence", 2.0)
    block("support_vertical", "minecraft:oak_fence", 2.0)
    lang["block.tfc.support_horizontal"] = "Horizontal Support"
    lang["block.tfc.support_vertical"] = "Vertical Support"

    # Heat recipes table (W5)
    heat = []
    for metal, melt in [
        ("copper", 1085),
        ("tin", 230),
        ("bronze", 950),
        ("gold", 1064),
        ("silver", 962),
        ("bismuth", 271),
        ("zinc", 420),
        ("wrought_iron", 1535),
        ("steel", 1540),
        ("lead", 327),
        ("nickel", 1455),
    ]:
        heat.append(
            {
                "input": f"tfc:ore_native_copper" if metal == "copper" else f"tfc:metal_{metal}_ingot",
                "output": f"tfc:metal_{metal}_ingot",
                "temp": melt,
            }
        )
    write_json(TABLES / "heat_recipes.json", heat)

    # Climate biomes lite (W1 / W12 prep)
    write_json(
        TABLES / "climate_regions.json",
        [
            {"id": "temperate", "temp": 15.0, "rain": 300.0},
            {"id": "tropical", "temp": 28.0, "rain": 450.0},
            {"id": "arid", "temp": 25.0, "rain": 40.0},
            {"id": "boreal", "temp": 2.0, "rain": 250.0},
            {"id": "polar", "temp": -15.0, "rain": 100.0},
        ],
    )

    # Alloy recipes (W5/W6)
    write_json(
        TABLES / "alloys.json",
        [
            {"id": "bronze", "inputs": {"copper": 0.88, "tin": 0.12}, "output": "tfc:metal_bronze_ingot"},
            {
                "id": "bismuth_bronze",
                "inputs": {"copper": 0.5, "zinc": 0.3, "bismuth": 0.2},
                "output": "tfc:metal_bismuth_bronze_ingot",
            },
            {
                "id": "black_bronze",
                "inputs": {"copper": 0.5, "gold": 0.25, "silver": 0.25},
                "output": "tfc:metal_black_bronze_ingot",
            },
        ],
    )

    # Barrel recipes (W9)
    write_json(
        TABLES / "barrel_recipes.json",
        [
            {"id": "tannin", "input_item": "tfc:wood_oak_log", "fluid": "water", "ticks": 8000, "output": "tfc:wood_ash"},
            {"id": "limewater", "input_item": "tfc:flux", "fluid": "water", "ticks": 1000, "output": "tfc:mortar"},
            {"id": "alcohol_apple", "input_item": "tfc:food_red_apple", "fluid": "water", "ticks": 72000, "output": "tfc:food_red_apple"},
        ],
    )

    # Anvil rules subset (W6)
    write_json(
        TABLES / "anvil_recipes.json",
        [
            {"id": "copper_pick_head", "input": "tfc:metal_copper_ingot", "output": "tfc:metal_copper_pickaxe_head", "tier": 1, "steps": ["hit", "draw", "hit"]},
            {"id": "copper_axe_head", "input": "tfc:metal_copper_ingot", "output": "tfc:metal_copper_axe_head", "tier": 1, "steps": ["hit", "hit", "punch"]},
            {"id": "bronze_pick_head", "input": "tfc:metal_bronze_ingot", "output": "tfc:metal_bronze_pickaxe_head", "tier": 2, "steps": ["hit", "draw", "hit"]},
            {"id": "wrought_sheet", "input": "tfc:metal_wrought_iron_ingot", "output": "tfc:metal_wrought_iron_sheet", "tier": 3, "steps": ["hit", "hit", "hit"]},
        ],
    )

    # Worldgen vein stubs (W12 blocked)
    write_json(
        TABLES / "veins.json",
        [
            {"id": "native_copper_surface", "ore": "tfc:ore_native_copper", "y_min": 40, "y_max": 120, "rarity": 40, "status": "hybrid_placeable"},
            {"id": "cassiterite", "ore": "tfc:ore_cassiterite", "y_min": 0, "y_max": 80, "rarity": 60, "status": "blocked_worldgen"},
            {"id": "hematite", "ore": "tfc:ore_hematite", "y_min": -32, "y_max": 64, "rarity": 50, "status": "blocked_worldgen"},
        ],
    )

    write_json(LANG, lang)
    print(f"Generated blocks={len(list(BLOCK.glob('*.json')))} items={len(list(ITEM.glob('*.json')))} recipes={len(list(RECIPE.glob('*.json')))}")


if __name__ == "__main__":
    main()
