#!/usr/bin/env python3
"""Generate TFC Horizon content (blocks, items, recipes, lang, placeholder textures)."""
from __future__ import annotations

import json
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "tfc"
HORIZON_BLOCK = DATA / "horizon" / "block"
HORIZON_ITEM = DATA / "horizon" / "item"
HORIZON_MENU = DATA / "horizon" / "menu"
RECIPE = DATA / "recipe"
ASSETS = ROOT / "assets" / "tfc"
LANG = ASSETS / "lang" / "en_us.json"
MODELS_BLOCK = ASSETS / "models" / "block"
MODELS_ITEM = ASSETS / "models" / "item"
BLOCKSTATES = ASSETS / "blockstates"
TEX_BLOCK = ASSETS / "textures" / "block"
TEX_ITEM = ASSETS / "textures" / "item"

ROCKS = [
    ("andesite", "Andesite"),
    ("basalt", "Basalt"),
    ("chalk", "Chalk"),
    ("chert", "Chert"),
    ("claystone", "Claystone"),
    ("conglomerate", "Conglomerate"),
]
ORES = [
    ("native_copper", "Native Copper", "copper"),
    ("native_gold", "Native Gold", "gold"),
    ("hematite", "Hematite", "iron"),
]
METALS = [
    ("copper", "Copper"),
    ("tin", "Tin"),
    ("bronze", "Bronze"),
    ("wrought_iron", "Wrought Iron"),
    ("steel", "Steel"),
]
TOOLS = ["axe", "hoe", "knife", "pickaxe", "shovel", "hammer", "chisel", "propick"]
FOODS = [
    ("red_apple", "Red Apple", {"grain": 0, "fruit": 2, "veg": 0, "protein": 0, "dairy": 0}, 48),
    ("carrot", "Carrot", {"grain": 0, "fruit": 0, "veg": 2, "protein": 0, "dairy": 0}, 36),
    ("bread", "Bread", {"grain": 3, "fruit": 0, "veg": 0, "protein": 0, "dairy": 0}, 72),
    ("cooked_meat", "Cooked Meat", {"grain": 0, "fruit": 0, "veg": 0, "protein": 3, "dairy": 0}, 48),
    ("cheese", "Cheese", {"grain": 0, "fruit": 0, "veg": 0, "protein": 0, "dairy": 2}, 96),
]
CROPS = [("barley", "Barley"), ("wheat", "Wheat"), ("cabbage", "Cabbage")]

MACHINES = [
    ("firepit", "Firepit", 1),
    ("charcoal_forge", "Charcoal Forge", 2),
    ("bloomery", "Bloomery", 2),
    ("anvil", "Anvil", 2),
    ("quern", "Quern", 2),
    ("barrel", "Barrel", 2),
    ("pit_kiln", "Pit Kiln", 1),
    ("blast_furnace", "Blast Furnace", 2),
    ("sluice", "Sluice", 1),
]


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def png_solid(path: Path, rgba: tuple[int, int, int, int], size: int = 16) -> None:
    """Minimal uncompressed-ish PNG (zlib IDAT)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    r, g, b, a = rgba
    raw = b""
    row = bytes([0]) + bytes([r, g, b, a]) * size
    raw = row * size

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(
            ">I", zlib.crc32(tag + data) & 0xFFFFFFFF
        )

    ihdr = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    data = b"\x89PNG\r\n\x1a\n"
    data += chunk(b"IHDR", ihdr)
    data += chunk(b"IDAT", zlib.compress(raw, 9))
    data += chunk(b"IEND", b"")
    path.write_bytes(data)


def block_def(template: str = "minecraft:stone", hardness: float = 1.5) -> dict:
    return {
        "template": template,
        "properties": {"hardness": hardness, "sounds": template},
        "item": True,
    }


def item_def(template: str = "minecraft:iron_ingot") -> dict:
    return {"template": template}


def menu_def(slots: list[list[float]]) -> dict:
    return {
        "width": 176,
        "height": 166,
        "slots": [{"x": s[0], "y": s[1]} for s in slots],
        "inventory_x": 8,
        "inventory_y": 84,
    }


def shaped(pattern: list[str], key: dict, result: str, count: int = 1) -> dict:
    return {
        "type": "minecraft:crafting_shaped",
        "pattern": pattern,
        "key": {k: {"item": v} for k, v in key.items()},
        "result": {"id": result, "count": count},
    }


def shapeless(ingredients: list[str], result: str, count: int = 1) -> dict:
    return {
        "type": "minecraft:crafting_shapeless",
        "ingredients": [{"item": i} for i in ingredients],
        "result": {"id": result, "count": count},
    }


def machine_recipe(kind: str, ingredient: str | list[str], result: str, duration: int = 200) -> dict:
    if isinstance(ingredient, list):
        body: dict = {"type": f"tfc:{kind}", "ingredients": ingredient}
    else:
        body = {"type": f"tfc:{kind}", "ingredient": ingredient}
    body["result"] = {"id": result, "count": 1}
    body["duration"] = duration
    return body


def main() -> None:
    for p in (
        HORIZON_BLOCK,
        HORIZON_ITEM,
        HORIZON_MENU,
        RECIPE,
        MODELS_BLOCK,
        MODELS_ITEM,
        BLOCKSTATES,
        TEX_BLOCK,
        TEX_ITEM,
    ):
        p.mkdir(parents=True, exist_ok=True)

    lang: dict[str, str] = {
        "itemGroup.tfc": "TFC Horizon",
        "tfc.climate.hud": "Season %s | %s°C | rain %s | thirst %s",
        "tfc.thirst.drink": "You drink. Thirst restored.",
        "tfc.prospect.found": "Found traces of %s nearby.",
        "tfc.prospect.nothing": "No ores nearby.",
    }
    colors = {
        "rock": (110, 110, 110, 255),
        "ore": (180, 100, 40, 255),
        "metal": (160, 120, 70, 255),
        "tool": (90, 90, 90, 255),
        "food": (200, 80, 60, 255),
        "crop": (80, 140, 60, 255),
        "machine": (70, 60, 50, 255),
        "misc": (140, 140, 160, 255),
    }

    # Rocks
    for rid, name in ROCKS:
        for form, suffix, tmpl in [
            ("raw", "Raw", "minecraft:stone"),
            ("cobble", "Cobble", "minecraft:cobblestone"),
            ("smooth", "Smooth", "minecraft:stone"),
            ("gravel", "Gravel", "minecraft:gravel"),
        ]:
            bid = f"{rid}_{form}"
            write_json(HORIZON_BLOCK / f"{bid}.json", block_def(tmpl))
            write_json(
                MODELS_BLOCK / f"{bid}.json",
                {"parent": "minecraft:block/cube_all", "textures": {"all": f"tfc:block/{bid}"}},
            )
            write_json(BLOCKSTATES / f"{bid}.json", {"variants": {"": {"model": f"tfc:block/{bid}"}}})
            write_json(MODELS_ITEM / f"{bid}.json", {"parent": f"tfc:block/{bid}"})
            png_solid(TEX_BLOCK / f"{bid}.png", colors["rock"])
            lang[f"block.tfc.{bid}"] = f"{name} {suffix}"
            lang[f"item.tfc.{bid}"] = f"{name} {suffix}"

    # Ores (placeable in vanilla world for hybrid slice)
    for oid, name, _metal in ORES:
        bid = f"ore_{oid}"
        write_json(HORIZON_BLOCK / f"{bid}.json", block_def("minecraft:iron_ore", 3.0))
        write_json(
            MODELS_BLOCK / f"{bid}.json",
            {"parent": "minecraft:block/cube_all", "textures": {"all": f"tfc:block/{bid}"}},
        )
        write_json(BLOCKSTATES / f"{bid}.json", {"variants": {"": {"model": f"tfc:block/{bid}"}}})
        write_json(MODELS_ITEM / f"{bid}.json", {"parent": f"tfc:block/{bid}"})
        png_solid(TEX_BLOCK / f"{bid}.png", colors["ore"])
        lang[f"block.tfc.{bid}"] = name
        lang[f"item.tfc.{bid}"] = name
        # loose nugget
        nid = f"nugget_{oid}"
        write_json(HORIZON_ITEM / f"{nid}.json", item_def("minecraft:raw_iron"))
        write_json(
            MODELS_ITEM / f"{nid}.json",
            {"parent": "minecraft:item/generated", "textures": {"layer0": f"tfc:item/{nid}"}},
        )
        png_solid(TEX_ITEM / f"{nid}.png", colors["ore"])
        lang[f"item.tfc.{nid}"] = f"{name} Nugget"

    # Metals
    for mid, name in METALS:
        for form, tmpl in [
            ("ingot", "minecraft:iron_ingot"),
            ("double_ingot", "minecraft:iron_ingot"),
            ("sheet", "minecraft:iron_ingot"),
            ("rod", "minecraft:stick"),
            ("unfinished_lamp", "minecraft:iron_nugget"),
        ]:
            iid = f"{mid}_{form}"
            write_json(HORIZON_ITEM / f"{iid}.json", item_def(tmpl))
            write_json(
                MODELS_ITEM / f"{iid}.json",
                {"parent": "minecraft:item/generated", "textures": {"layer0": f"tfc:item/{iid}"}},
            )
            png_solid(TEX_ITEM / f"{iid}.png", colors["metal"])
            lang[f"item.tfc.{iid}"] = f"{name} {form.replace('_', ' ').title()}"

        for tool in TOOLS:
            iid = f"{mid}_{tool}"
            write_json(HORIZON_ITEM / f"{iid}.json", item_def("minecraft:iron_pickaxe"))
            write_json(
                MODELS_ITEM / f"{iid}.json",
                {"parent": "minecraft:item/handheld", "textures": {"layer0": f"tfc:item/{iid}"}},
            )
            png_solid(TEX_ITEM / f"{iid}.png", colors["tool"])
            lang[f"item.tfc.{iid}"] = f"{name} {tool.replace('_', ' ').title()}"

        # tool heads / molds
        for head in ("axe_head", "hoe_head", "knife_blade", "pickaxe_head", "shovel_head", "hammer_head", "chisel_head", "propick_head", "sword_blade"):
            iid = f"{mid}_{head}"
            write_json(HORIZON_ITEM / f"{iid}.json", item_def("minecraft:iron_nugget"))
            write_json(
                MODELS_ITEM / f"{iid}.json",
                {"parent": "minecraft:item/generated", "textures": {"layer0": f"tfc:item/{iid}"}},
            )
            png_solid(TEX_ITEM / f"{iid}.png", colors["metal"])
            lang[f"item.tfc.{iid}"] = f"{name} {head.replace('_', ' ').title()}"

    # Stone tools (knapping outputs)
    for tool in ("axe", "hoe", "knife", "shovel", "hammer"):
        iid = f"stone_{tool}"
        write_json(HORIZON_ITEM / f"{iid}.json", item_def("minecraft:stone_axe"))
        write_json(
            MODELS_ITEM / f"{iid}.json",
            {"parent": "minecraft:item/handheld", "textures": {"layer0": f"tfc:item/{iid}"}},
        )
        png_solid(TEX_ITEM / f"{iid}.png", colors["tool"])
        lang[f"item.tfc.{iid}"] = f"Stone {tool.title()}"
        hid = f"stone_{tool}_head"
        write_json(HORIZON_ITEM / f"{hid}.json", item_def("minecraft:flint"))
        write_json(
            MODELS_ITEM / f"{hid}.json",
            {"parent": "minecraft:item/generated", "textures": {"layer0": f"tfc:item/{hid}"}},
        )
        png_solid(TEX_ITEM / f"{hid}.png", colors["misc"])
        lang[f"item.tfc.{hid}"] = f"Stone {tool.title()} Head"

    # Pottery / clay
    for iid, name, tmpl in [
        ("clay_ball_tfc", "Clay Ball", "minecraft:clay_ball"),
        ("unfired_vessel", "Unfired Vessel", "minecraft:flower_pot"),
        ("vessel", "Ceramic Vessel", "minecraft:flower_pot"),
        ("unfired_mold_ingot", "Unfired Ingot Mold", "minecraft:brick"),
        ("mold_ingot", "Ingot Mold", "minecraft:brick"),
        ("unfired_jug", "Unfired Jug", "minecraft:flower_pot"),
        ("jug", "Ceramic Jug", "minecraft:flower_pot"),
        ("firestarter", "Firestarter", "minecraft:flint_and_steel"),
        ("prospector_pick", "Prospector's Pick", "minecraft:iron_pickaxe"),
        ("wooden_bucket", "Wooden Bucket", "minecraft:bucket"),
        ("spindle", "Spindle", "minecraft:stick"),
        ("wool_yarn", "Wool Yarn", "minecraft:string"),
        ("support_beam", "Support Beam", "minecraft:oak_fence"),
        ("log_pile", "Log Pile", "minecraft:oak_log"),
        ("lumber", "Lumber", "minecraft:oak_planks"),
        ("bloom", "Iron Bloom", "minecraft:raw_iron"),
        ("raw_iron_bloom", "Raw Iron Bloom", "minecraft:raw_iron"),
        ("powder_flux", "Flux", "minecraft:sugar"),
        ("powder_wood_ash", "Wood Ash", "minecraft:gunpowder"),
        ("glass_batch", "Glass Batch", "minecraft:glass"),
        ("powderkeg", "Powderkeg", "minecraft:tnt"),
        ("pan_empty", "Empty Pan", "minecraft:bowl"),
        ("pan_gravel", "Filled Pan", "minecraft:bowl"),
    ]:
        write_json(HORIZON_ITEM / f"{iid}.json", item_def(tmpl))
        write_json(
            MODELS_ITEM / f"{iid}.json",
            {"parent": "minecraft:item/generated", "textures": {"layer0": f"tfc:item/{iid}"}},
        )
        png_solid(TEX_ITEM / f"{iid}.png", colors["misc"])
        lang[f"item.tfc.{iid}"] = name

    # Foods
    for fid, name, _nut, _life in FOODS:
        write_json(HORIZON_ITEM / f"{fid}.json", item_def("minecraft:apple"))
        write_json(
            MODELS_ITEM / f"{fid}.json",
            {"parent": "minecraft:item/generated", "textures": {"layer0": f"tfc:item/{fid}"}},
        )
        png_solid(TEX_ITEM / f"{fid}.png", colors["food"])
        lang[f"item.tfc.{fid}"] = name

    # Crops (as items + crop blocks)
    for cid, name in CROPS:
        write_json(HORIZON_ITEM / f"{cid}_seeds.json", item_def("minecraft:wheat_seeds"))
        write_json(
            MODELS_ITEM / f"{cid}_seeds.json",
            {"parent": "minecraft:item/generated", "textures": {"layer0": f"tfc:item/{cid}_seeds"}},
        )
        png_solid(TEX_ITEM / f"{cid}_seeds.png", colors["crop"])
        lang[f"item.tfc.{cid}_seeds"] = f"{name} Seeds"
        write_json(HORIZON_ITEM / f"{cid}.json", item_def("minecraft:wheat"))
        write_json(
            MODELS_ITEM / f"{cid}.json",
            {"parent": "minecraft:item/generated", "textures": {"layer0": f"tfc:item/{cid}"}},
        )
        png_solid(TEX_ITEM / f"{cid}.png", colors["crop"])
        lang[f"item.tfc.{cid}"] = name
        bid = f"crop_{cid}"
        write_json(HORIZON_BLOCK / f"{bid}.json", block_def("minecraft:wheat", 0.0))
        write_json(
            MODELS_BLOCK / f"{bid}.json",
            {"parent": "minecraft:block/crop", "textures": {"crop": f"tfc:block/{bid}"}},
        )
        write_json(BLOCKSTATES / f"{bid}.json", {"variants": {"": {"model": f"tfc:block/{bid}"}}})
        png_solid(TEX_BLOCK / f"{bid}.png", colors["crop"])
        lang[f"block.tfc.{bid}"] = name

    # Machines
    for mid, name, inputs in MACHINES:
        write_json(HORIZON_BLOCK / f"{mid}.json", block_def("minecraft:furnace", 2.5))
        write_json(
            MODELS_BLOCK / f"{mid}.json",
            {"parent": "minecraft:block/cube_all", "textures": {"all": f"tfc:block/{mid}"}},
        )
        write_json(BLOCKSTATES / f"{mid}.json", {"variants": {"": {"model": f"tfc:block/{mid}"}}})
        write_json(MODELS_ITEM / f"{mid}.json", {"parent": f"tfc:block/{mid}"})
        png_solid(TEX_BLOCK / f"{mid}.png", colors["machine"])
        lang[f"block.tfc.{mid}"] = name
        lang[f"item.tfc.{mid}"] = name
        slots = [[53.0, 35.0]] if inputs < 2 else [[53.0, 25.0], [71.0, 25.0], [116.0, 35.0]]
        if inputs >= 2 and mid not in ("anvil",):
            slots = [[53.0, 35.0], [116.0, 35.0]]
        write_json(HORIZON_MENU / f"{mid}.json", menu_def(slots))

    # Support beam as block
    write_json(HORIZON_BLOCK / "support_beam.json", block_def("minecraft:oak_fence", 2.0))
    write_json(
        MODELS_BLOCK / "support_beam.json",
        {"parent": "minecraft:block/cube_all", "textures": {"all": "tfc:block/support_beam"}},
    )
    write_json(BLOCKSTATES / "support_beam.json", {"variants": {"": {"model": "tfc:block/support_beam"}}})
    write_json(MODELS_ITEM / "support_beam.json", {"parent": "tfc:block/support_beam"})
    png_solid(TEX_BLOCK / "support_beam.png", colors["misc"])
    lang["block.tfc.support_beam"] = "Support Beam"

    write_json(HORIZON_BLOCK / "log_pile.json", block_def("minecraft:oak_log", 2.0))
    write_json(
        MODELS_BLOCK / "log_pile.json",
        {"parent": "minecraft:block/cube_all", "textures": {"all": "tfc:block/log_pile"}},
    )
    write_json(BLOCKSTATES / "log_pile.json", {"variants": {"": {"model": "tfc:block/log_pile"}}})
    write_json(MODELS_ITEM / "log_pile.json", {"parent": "tfc:block/log_pile"})
    png_solid(TEX_BLOCK / "log_pile.png", colors["misc"])
    lang["block.tfc.log_pile"] = "Log Pile"

    write_json(HORIZON_BLOCK / "powderkeg.json", block_def("minecraft:tnt", 0.5))
    write_json(
        MODELS_BLOCK / "powderkeg.json",
        {"parent": "minecraft:block/cube_all", "textures": {"all": "tfc:block/powderkeg"}},
    )
    write_json(BLOCKSTATES / "powderkeg.json", {"variants": {"": {"model": "tfc:block/powderkeg"}}})
    write_json(MODELS_ITEM / "powderkeg.json", {"parent": "tfc:block/powderkeg"})
    png_solid(TEX_BLOCK / "powderkeg.png", colors["misc"])
    lang["block.tfc.powderkeg"] = "Powderkeg"

    # Recipes — early loop
    write_json(
        RECIPE / "firestarter.json",
        shaped(["S ", " F"], {"S": "minecraft:stick", "F": "minecraft:flint"}, "tfc:firestarter"),
    )
    write_json(
        RECIPE / "prospector_pick.json",
        shaped(
            ["CCC", " S ", " S "],
            {"C": "tfc:copper_ingot", "S": "minecraft:stick"},
            "tfc:prospector_pick",
        ),
    )
    write_json(
        RECIPE / "vessel_from_unfired.json",
        machine_recipe("pit_kiln", "tfc:unfired_vessel", "tfc:vessel", 400),
    )
    write_json(
        RECIPE / "mold_from_unfired.json",
        machine_recipe("pit_kiln", "tfc:unfired_mold_ingot", "tfc:mold_ingot", 400),
    )
    write_json(
        RECIPE / "unfired_vessel.json",
        shapeless(["minecraft:clay_ball", "minecraft:clay_ball", "minecraft:clay_ball"], "tfc:unfired_vessel"),
    )
    write_json(
        RECIPE / "unfired_mold.json",
        shapeless(["minecraft:clay_ball", "minecraft:clay_ball"], "tfc:unfired_mold_ingot"),
    )
    write_json(
        RECIPE / "stone_axe_assemble.json",
        shapeless(["tfc:stone_axe_head", "minecraft:stick"], "tfc:stone_axe"),
    )
    write_json(
        RECIPE / "stone_knife_assemble.json",
        shapeless(["tfc:stone_knife_head", "minecraft:stick"], "tfc:stone_knife"),
    )
    write_json(
        RECIPE / "stone_shovel_assemble.json",
        shapeless(["tfc:stone_shovel_head", "minecraft:stick"], "tfc:stone_shovel"),
    )
    write_json(
        RECIPE / "stone_hoe_assemble.json",
        shapeless(["tfc:stone_hoe_head", "minecraft:stick"], "tfc:stone_hoe"),
    )
    write_json(
        RECIPE / "stone_hammer_assemble.json",
        shapeless(["tfc:stone_hammer_head", "minecraft:stick"], "tfc:stone_hammer"),
    )
    # Knapping-as-crafting stand-in until GUI knapping screen
    write_json(
        RECIPE / "knap_axe_head.json",
        shapeless(
            ["tfc:andesite_raw", "tfc:andesite_raw", "tfc:andesite_raw"],
            "tfc:stone_axe_head",
        ),
    )
    write_json(
        RECIPE / "knap_knife_head.json",
        shapeless(["tfc:chert_raw", "tfc:chert_raw"], "tfc:stone_knife_head"),
    )
    write_json(
        RECIPE / "knap_shovel_head.json",
        shapeless(["tfc:basalt_raw", "tfc:basalt_raw"], "tfc:stone_shovel_head"),
    )
    write_json(
        RECIPE / "firepit.json",
        shaped([" S ", "LLL"], {"S": "minecraft:stick", "L": "minecraft:oak_log"}, "tfc:firepit"),
    )
    write_json(
        RECIPE / "charcoal_forge.json",
        shaped(
            ["CCC", "C C", "CCC"],
            {"C": "minecraft:charcoal"},
            "tfc:charcoal_forge",
        ),
    )
    write_json(
        RECIPE / "melt_copper.json",
        machine_recipe("charcoal_forge", "tfc:nugget_native_copper", "tfc:copper_ingot", 300),
    )
    write_json(
        RECIPE / "melt_gold.json",
        machine_recipe("charcoal_forge", "tfc:nugget_native_gold", "minecraft:gold_ingot", 300),
    )
    write_json(
        RECIPE / "copper_pick_head.json",
        machine_recipe("charcoal_forge", ["tfc:copper_ingot", "tfc:mold_ingot"], "tfc:copper_pickaxe_head", 250),
    )
    write_json(
        RECIPE / "copper_pick_assemble.json",
        shapeless(["tfc:copper_pickaxe_head", "minecraft:stick"], "tfc:copper_pickaxe"),
    )
    write_json(
        RECIPE / "bloomery.json",
        shaped(
            ["IRI", "I I", "III"],
            {"I": "tfc:wrought_iron_ingot", "R": "tfc:wrought_iron_sheet"},
            "tfc:bloomery",
        ),
    )
    write_json(
        RECIPE / "bloom_from_ore.json",
        machine_recipe("bloomery", ["tfc:nugget_hematite", "minecraft:charcoal"], "tfc:raw_iron_bloom", 600),
    )
    write_json(
        RECIPE / "wrought_from_bloom.json",
        machine_recipe("anvil", "tfc:raw_iron_bloom", "tfc:wrought_iron_ingot", 400),
    )
    write_json(
        RECIPE / "anvil_block.json",
        shaped(["III", " I ", "III"], {"I": "tfc:wrought_iron_ingot"}, "tfc:anvil"),
    )
    write_json(
        RECIPE / "bronze_alloy.json",
        machine_recipe("charcoal_forge", ["tfc:copper_ingot", "tfc:tin_ingot"], "tfc:bronze_ingot", 280),
    )
    write_json(
        RECIPE / "quern.json",
        shaped(["SSS", " S ", "SSS"], {"S": "tfc:andesite_smooth"}, "tfc:quern"),
    )
    write_json(
        RECIPE / "quern_flux.json",
        machine_recipe("quern", "tfc:chalk_raw", "tfc:powder_flux", 100),
    )
    write_json(
        RECIPE / "barrel.json",
        shaped(["P P", "P P", "PPP"], {"P": "minecraft:oak_planks"}, "tfc:barrel"),
    )
    write_json(
        RECIPE / "barrel_tannin.json",
        machine_recipe("barrel", ["minecraft:oak_log", "minecraft:water_bucket"], "tfc:powder_wood_ash", 800),
    )
    write_json(
        RECIPE / "support_beam.json",
        shaped(["L L", "L L", "L L"], {"L": "tfc:lumber"}, "tfc:support_beam", 8),
    )
    write_json(
        RECIPE / "lumber_from_log.json",
        shapeless(["minecraft:oak_log"], "tfc:lumber", 8),
    )
    write_json(
        RECIPE / "log_pile.json",
        shaped(["LLL", "LLL", "LLL"], {"L": "minecraft:oak_log"}, "tfc:log_pile"),
    )
    write_json(
        RECIPE / "pan.json",
        shaped(["B B", " B "], {"B": "minecraft:bowl"}, "tfc:pan_empty"),
    )
    write_json(
        RECIPE / "sluice.json",
        shaped(["LSL", "LSL", "LSL"], {"L": "tfc:lumber", "S": "minecraft:stick"}, "tfc:sluice"),
    )
    write_json(
        RECIPE / "pan_copper.json",
        machine_recipe("sluice", "tfc:pan_gravel", "tfc:nugget_native_copper", 120),
    )
    write_json(
        RECIPE / "blast_furnace.json",
        shaped(
            ["SSS", "S S", "SSS"],
            {"S": "tfc:wrought_iron_sheet"},
            "tfc:blast_furnace",
        ),
    )
    write_json(
        RECIPE / "steel_from_iron.json",
        machine_recipe("blast_furnace", ["tfc:wrought_iron_ingot", "minecraft:coal"], "tfc:steel_ingot", 800),
    )
    write_json(
        RECIPE / "powderkeg.json",
        shaped(
            ["GPG", "PGP", "GPG"],
            {"G": "minecraft:gunpowder", "P": "minecraft:oak_planks"},
            "tfc:powderkeg",
        ),
    )
    write_json(
        RECIPE / "glass_batch.json",
        shapeless(["minecraft:sand", "tfc:powder_flux"], "tfc:glass_batch"),
    )
    write_json(
        RECIPE / "pit_kiln.json",
        shaped([" W ", "WWW"], {"W": "minecraft:wheat"}, "tfc:pit_kiln"),
    )

    # Crop seed recipes / food copies
    for cid, _ in CROPS:
        write_json(
            RECIPE / f"{cid}_seeds_from_crop.json",
            shapeless([f"tfc:{cid}"], f"tfc:{cid}_seeds", 2),
        )

    write_json(Path(LANG), lang)

    # Data tables (JSON) for native code
    tables = ROOT / "tables"
    tables.mkdir(parents=True, exist_ok=True)
    write_json(
        tables / "climate_seasons.json",
        {
            "days_per_month": 8,
            "months": [
                {"id": "january", "season": "winter", "temp_offset": -8},
                {"id": "february", "season": "winter", "temp_offset": -6},
                {"id": "march", "season": "spring", "temp_offset": -2},
                {"id": "april", "season": "spring", "temp_offset": 2},
                {"id": "may", "season": "spring", "temp_offset": 6},
                {"id": "june", "season": "summer", "temp_offset": 10},
                {"id": "july", "season": "summer", "temp_offset": 12},
                {"id": "august", "season": "summer", "temp_offset": 10},
                {"id": "september", "season": "autumn", "temp_offset": 4},
                {"id": "october", "season": "autumn", "temp_offset": 0},
                {"id": "november", "season": "autumn", "temp_offset": -4},
                {"id": "december", "season": "winter", "temp_offset": -8},
            ],
            "base_temp_c": 14.0,
            "base_rainfall": 300.0,
        },
    )
    write_json(
        tables / "ores.json",
        {
            "prospect_radius": 12,
            "ores": [
                {"block": f"tfc:ore_{oid}", "nugget": f"tfc:nugget_{oid}", "name": name}
                for oid, name, _ in ORES
            ],
        },
    )
    write_json(
        tables / "nutrition.json",
        {
            "foods": [
                {
                    "id": f"tfc:{fid}",
                    "nutrients": nut,
                    "decay_ticks": life * 24000,
                    "weight": 1.0,
                    "size": "small",
                }
                for fid, _n, nut, life in FOODS
            ]
        },
    )
    write_json(
        tables / "crops.json",
        {
            "crops": [
                {
                    "id": cid,
                    "block": f"tfc:crop_{cid}",
                    "seeds": f"tfc:{cid}_seeds",
                    "min_temp": 0.0,
                    "max_temp": 35.0,
                    "min_rain": 100.0,
                    "max_rain": 500.0,
                    "seasons": ["spring", "summer"],
                }
                for cid, _ in CROPS
            ]
        },
    )
    write_json(
        tables / "heat.json",
        {
            "items": [
                {"id": "tfc:nugget_native_copper", "melt_temp": 1085, "result": "tfc:copper_ingot"},
                {"id": "tfc:copper_ingot", "work_temp": 800},
                {"id": "tfc:bronze_ingot", "work_temp": 900},
                {"id": "tfc:wrought_iron_ingot", "work_temp": 1100},
            ]
        },
    )
    write_json(
        tables / "knapping.json",
        {
            "patterns": [
                {"id": "axe", "result": "tfc:stone_axe_head", "rock": "any"},
                {"id": "knife", "result": "tfc:stone_knife_head", "rock": "any"},
                {"id": "shovel", "result": "tfc:stone_shovel_head", "rock": "any"},
            ]
        },
    )
    write_json(
        tables / "anvil.json",
        {
            "rules": [
                {"input": "tfc:raw_iron_bloom", "result": "tfc:wrought_iron_ingot", "hits": 5},
                {"input": "tfc:copper_ingot", "result": "tfc:copper_sheet", "hits": 3},
                {"input": "tfc:wrought_iron_ingot", "result": "tfc:wrought_iron_sheet", "hits": 3},
            ]
        },
    )

    print(
        "generated",
        len(list(HORIZON_BLOCK.glob("*.json"))),
        "blocks,",
        len(list(HORIZON_ITEM.glob("*.json"))),
        "items,",
        len(list(RECIPE.glob("*.json"))),
        "recipes",
    )


if __name__ == "__main__":
    main()
