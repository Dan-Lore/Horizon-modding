#!/usr/bin/env python3
"""Generate TFC Horizon content JSON, data tables, creative tab, and placeholder PNGs."""
from __future__ import annotations

import json
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "tfc"
HORIZON = DATA / "horizon"
BLOCK = HORIZON / "block"
ITEM = HORIZON / "item"
TAB = HORIZON / "creative_tab"
MENU = HORIZON / "menu"
RECIPE = DATA / "recipe"
TABLES = DATA / "tables"
TEX_BLOCK = ROOT / "assets" / "tfc" / "textures" / "block"
TEX_ITEM = ROOT / "assets" / "tfc" / "textures" / "item"

ROCKS = [
    ("andesite", 0x6E6E6E),
    ("basalt", 0x2A2A2A),
    ("chalk", 0xE8E4D8),
    ("chert", 0xA09070),
    ("claystone", 0xC4A484),
    ("conglomerate", 0x9A8B7A),
]

ORES = [
    ("native_copper", 0xB87333, "copper"),
    ("native_gold", 0xD4AF37, "gold"),
    ("hematite", 0x8B3A3A, "iron"),
    ("cassiterite", 0x8A8A8A, "tin"),
    ("sphalerite", 0x6B6B4A, "zinc"),
    ("tetrahedrite", 0x5C4033, "copper"),
]

METALS = [
    ("copper", 0xB87333),
    ("tin", 0xC0C0C0),
    ("bronze", 0xCD7F32),
    ("wrought_iron", 0x8B8B8B),
    ("steel", 0x4A4A4A),
    ("gold", 0xD4AF37),
    ("zinc", 0xA0A0A0),
]

TOOL_TYPES = ["axe", "pickaxe", "shovel", "hoe", "knife", "hammer", "sword", "propick"]
STONE_TOOLS = ["axe", "knife", "shovel", "hoe", "hammer"]

FOODS = [
    ("red_apple", "fruit", 0xCC3333),
    ("carrot", "vegetable", 0xE67E22),
    ("wheat_bread", "grain", 0xD2B48C),
    ("cooked_beef", "protein", 0x8B4513),
    ("cheese", "dairy", 0xF5D76E),
]

CROPS = [
    ("barley", 8, 12, 40, 100),  # min_temp, max_temp, min_rain, max_rain (°C-ish / mm proxy)
    ("wheat", 5, 25, 50, 150),
    ("maize", 15, 32, 80, 200),
    ("squash", 10, 30, 60, 180),
]

SEASONS = ["Early Spring", "Spring", "Late Spring", "Early Summer", "Summer", "Late Summer",
           "Early Autumn", "Autumn", "Late Autumn", "Early Winter", "Winter", "Late Winter"]


def write_json(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def png_rgba(path: Path, rgb: int, size: int = 16) -> None:
    """Minimal solid-color RGBA PNG (stdlib only)."""
    path.parent.mkdir(parents=True, exist_ok=True)
    r = (rgb >> 16) & 0xFF
    g = (rgb >> 8) & 0xFF
    b = rgb & 0xFF
    raw = b""
    for _y in range(size):
        raw += b"\x00"
        for _x in range(size):
            raw += bytes([r, g, b, 255])

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(
            ">I", zlib.crc32(tag + data) & 0xFFFFFFFF
        )

    ihdr = struct.pack(">IIBBBBB", size, size, 8, 6, 0, 0, 0)
    data = b"\x89PNG\r\n\x1a\n" + chunk(b"IHDR", ihdr) + chunk(b"IDAT", zlib.compress(raw, 9)) + chunk(
        b"IEND", b""
    )
    path.write_bytes(data)


def item_json(template: str = "minecraft:iron_ingot") -> dict:
    return {"template": template}


def block_json(template: str = "minecraft:stone", hardness: float = 1.5) -> dict:
    return {
        "template": template,
        "properties": {"hardness": hardness, "sounds": "minecraft:stone"},
        "item": True,
    }


def furnace_block(hardness: float = 3.5) -> dict:
    return {
        "template": "minecraft:furnace",
        "properties": {"hardness": hardness, "sounds": "minecraft:stone"},
        "item": True,
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


def gen_rocks_ores(tab_items: list[str]) -> None:
    for name, color in ROCKS:
        write_json(BLOCK / f"rock_{name}.json", block_json())
        write_json(BLOCK / f"cobble_{name}.json", block_json("minecraft:cobblestone", 1.0))
        write_json(ITEM / f"brick_{name}.json", item_json("minecraft:brick"))
        write_json(ITEM / f"loose_{name}.json", item_json("minecraft:flint"))
        png_rgba(TEX_BLOCK / f"rock_{name}.png", color)
        png_rgba(TEX_BLOCK / f"cobble_{name}.png", color - 0x101010 if color > 0x202020 else color)
        png_rgba(TEX_ITEM / f"brick_{name}.png", color)
        png_rgba(TEX_ITEM / f"loose_{name}.png", color)
        tab_items.extend([f"tfc:rock_{name}", f"tfc:cobble_{name}", f"tfc:brick_{name}", f"tfc:loose_{name}"])
        write_json(
            RECIPE / f"cobble_from_{name}_loose.json",
            shapeless([f"tfc:loose_{name}"] * 4, f"tfc:cobble_{name}"),
        )

    for name, color, metal in ORES:
        write_json(BLOCK / f"ore_{name}.json", block_json("minecraft:iron_ore", 3.0))
        write_json(ITEM / f"ore_{name}.json", item_json("minecraft:raw_iron"))
        write_json(ITEM / f"nugget_{metal}.json", item_json("minecraft:iron_nugget"))
        png_rgba(TEX_BLOCK / f"ore_{name}.png", color)
        png_rgba(TEX_ITEM / f"ore_{name}.png", color)
        png_rgba(TEX_ITEM / f"nugget_{metal}.png", color)
        tab_items.extend([f"tfc:ore_{name}", f"tfc:nugget_{metal}"])


def gen_tools_knapping(tab_items: list[str]) -> None:
    write_json(ITEM / "knapping_stone.json", item_json("minecraft:flint"))
    png_rgba(TEX_ITEM / "knapping_stone.png", 0x888888)
    tab_items.append("tfc:knapping_stone")

    for tool in STONE_TOOLS:
        iid = f"stone_{tool}"
        write_json(ITEM / f"{iid}.json", item_json(f"minecraft:stone_{tool}" if tool != "knife" and tool != "hammer" else "minecraft:stone_sword"))
        png_rgba(TEX_ITEM / f"{iid}.png", 0x7A7A7A)
        tab_items.append(f"tfc:{iid}")
        write_json(
            RECIPE / f"knap_{iid}.json",
            {
                "type": "tfc:knapping",
                "ingredient": "tfc:knapping_stone",
                "pattern": ["XXX", "X X", " X "] if tool == "axe" else ["X", "X", "S"],
                "result": {"id": f"tfc:{iid}", "count": 1},
            },
        )

    write_json(ITEM / "firestarter.json", item_json("minecraft:flint_and_steel"))
    write_json(ITEM / "prospectors_pick.json", item_json("minecraft:iron_pickaxe"))
    png_rgba(TEX_ITEM / "firestarter.png", 0xAA5500)
    png_rgba(TEX_ITEM / "prospectors_pick.png", 0x556677)
    tab_items.extend(["tfc:firestarter", "tfc:prospectors_pick"])
    write_json(
        RECIPE / "prospectors_pick.json",
        shaped(
            ["II", " S", " S"],
            {"I": "minecraft:copper_ingot", "S": "minecraft:stick"},
            "tfc:prospectors_pick",
        ),
    )
    write_json(
        RECIPE / "firestarter.json",
        shapeless(["minecraft:stick", "minecraft:flint"], "tfc:firestarter"),
    )


def gen_pottery_heat(tab_items: list[str]) -> None:
    for name, color in [
        ("clay_ball_tfc", 0x9C7B5A),
        ("unfired_vessel", 0xBFA68A),
        ("ceramic_vessel", 0xC4A882),
        ("unfired_jug", 0xBFA68A),
        ("ceramic_jug", 0xC4A882),
        ("unfired_ingot_mold", 0xBFA68A),
        ("ceramic_ingot_mold", 0xC4A882),
        ("unfired_tool_mold_axe", 0xBFA68A),
        ("ceramic_tool_mold_axe", 0xC4A882),
        ("unfired_tool_mold_pickaxe", 0xBFA68A),
        ("ceramic_tool_mold_pickaxe", 0xC4A882),
    ]:
        write_json(ITEM / f"{name}.json", item_json("minecraft:brick" if "mold" in name or "vessel" in name or "jug" in name else "minecraft:clay_ball"))
        png_rgba(TEX_ITEM / f"{name}.png", color)
        tab_items.append(f"tfc:{name}")

    write_json(RECIPE / "unfired_vessel.json", shapeless(["minecraft:clay_ball"] * 5, "tfc:unfired_vessel"))
    write_json(RECIPE / "unfired_jug.json", shapeless(["minecraft:clay_ball"] * 5, "tfc:unfired_jug"))
    write_json(RECIPE / "unfired_ingot_mold.json", shapeless(["minecraft:clay_ball"] * 3, "tfc:unfired_ingot_mold"))
    write_json(
        RECIPE / "pit_kiln_vessel.json",
        {
            "type": "tfc:pit_kiln",
            "ingredient": "tfc:unfired_vessel",
            "result": {"id": "tfc:ceramic_vessel", "count": 1},
            "duration": 800,
        },
    )
    write_json(
        RECIPE / "pit_kiln_jug.json",
        {
            "type": "tfc:pit_kiln",
            "ingredient": "tfc:unfired_jug",
            "result": {"id": "tfc:ceramic_jug", "count": 1},
            "duration": 800,
        },
    )
    write_json(
        RECIPE / "pit_kiln_ingot_mold.json",
        {
            "type": "tfc:pit_kiln",
            "ingredient": "tfc:unfired_ingot_mold",
            "result": {"id": "tfc:ceramic_ingot_mold", "count": 1},
            "duration": 800,
        },
    )


def gen_machines(tab_items: list[str]) -> None:
    machines = [
        ("firepit", 0x5A3A1A),
        ("pit_kiln", 0x6B4E31),
        ("charcoal_forge", 0x333333),
        ("bloomery", 0x4A3728),
        ("anvil_stone", 0x777777),
        ("anvil_bronze", 0xCD7F32),
        ("quern", 0x8A8A8A),
        ("barrel", 0x8B5A2B),
        ("sluice", 0x6B8E23),
        ("log_pile", 0x8B6914),
        ("support_beam", 0xA0522D),
        ("blast_furnace", 0x3D3D3D),
        ("powderkeg", 0x5C4033),
    ]
    for name, color in machines:
        write_json(BLOCK / f"{name}.json", furnace_block())
        png_rgba(TEX_BLOCK / f"{name}.png", color)
        tab_items.append(f"tfc:{name}")
        write_json(
            MENU / f"{name}.json",
            {"template": "minecraft:generic_3x3" if name in ("quern", "barrel") else "minecraft:furnace"},
        )

    write_json(
        RECIPE / "firepit.json",
        shaped([" S ", "LLL"], {"S": "minecraft:stick", "L": "minecraft:oak_log"}, "tfc:firepit"),
    )
    write_json(
        RECIPE / "quern.json",
        shaped(["SSS", " S ", "SSS"], {"S": "tfc:rock_andesite"}, "tfc:quern"),
    )
    write_json(
        RECIPE / "barrel.json",
        shaped(["P P", "P P", "PPP"], {"P": "minecraft:oak_planks"}, "tfc:barrel"),
    )
    write_json(
        RECIPE / "support_beam.json",
        shaped(["L", "L", "L"], {"L": "minecraft:oak_log"}, "tfc:support_beam", 8),
    )
    write_json(
        RECIPE / "log_pile.json",
        shapeless(["minecraft:oak_log"] * 3, "tfc:log_pile"),
    )
    write_json(
        RECIPE / "sluice.json",
        shaped(["S S", "SLS", "PPP"], {"S": "minecraft:stick", "L": "minecraft:oak_log", "P": "minecraft:oak_planks"}, "tfc:sluice"),
    )


def gen_metals(tab_items: list[str]) -> None:
    for metal, color in METALS:
        for form in ("ingot", "double_ingot", "sheet", "rod", "dust"):
            iid = f"{metal}_{form}"
            write_json(ITEM / f"{iid}.json", item_json("minecraft:iron_ingot" if form != "dust" else "minecraft:gunpowder"))
            png_rgba(TEX_ITEM / f"{iid}.png", color)
            tab_items.append(f"tfc:{iid}")
        for tool in ("axe", "pickaxe", "shovel", "sword", "knife", "hammer"):
            iid = f"{metal}_{tool}"
            write_json(ITEM / f"{iid}.json", item_json("minecraft:iron_pickaxe"))
            png_rgba(TEX_ITEM / f"{iid}.png", color)
            tab_items.append(f"tfc:{iid}")
            write_json(ITEM / f"{metal}_{tool}_head.json", item_json("minecraft:iron_nugget"))
            png_rgba(TEX_ITEM / f"{metal}_{tool}_head.png", color)
            tab_items.append(f"tfc:{metal}_{tool}_head")

        write_json(
            RECIPE / f"heat_melt_{metal}.json",
            {
                "type": "tfc:heating",
                "ingredient": f"tfc:ore_native_{metal}" if metal == "copper" else f"tfc:{metal}_dust",
                "result": {"id": f"tfc:{metal}_ingot", "count": 1},
                "temperature": 1080 if metal == "copper" else 1500,
            },
        )

    # Copper cast path (W5)
    write_json(
        RECIPE / "cast_copper_ingot.json",
        {
            "type": "tfc:casting",
            "mold": "tfc:ceramic_ingot_mold",
            "fluid_metal": "tfc:copper",
            "result": {"id": "tfc:copper_ingot", "count": 1},
        },
    )
    write_json(
        RECIPE / "assemble_copper_pickaxe.json",
        shapeless(["tfc:copper_pickaxe_head", "minecraft:stick"], "tfc:copper_pickaxe"),
    )
    write_json(
        RECIPE / "bronze_alloy.json",
        {
            "type": "tfc:alloy",
            "inputs": [{"id": "tfc:copper_ingot", "count": 9}, {"id": "tfc:tin_ingot", "count": 1}],
            "result": {"id": "tfc:bronze_ingot", "count": 10},
        },
    )
    write_json(
        RECIPE / "anvil_copper_pick_head.json",
        {
            "type": "tfc:anvil",
            "ingredient": "tfc:copper_ingot",
            "result": {"id": "tfc:copper_pickaxe_head", "count": 1},
            "tier": 1,
            "rules": ["hit_last", "draw_any"],
        },
    )
    write_json(
        RECIPE / "bloom_to_wrought.json",
        {
            "type": "tfc:bloomery",
            "ingredient": "tfc:ore_hematite",
            "fuel": "minecraft:charcoal",
            "result": {"id": "tfc:wrought_iron_ingot", "count": 1},
            "duration": 1200,
        },
    )


def gen_food_crops(tab_items: list[str]) -> None:
    for name, nutrient, color in FOODS:
        write_json(
            ITEM / f"food_{name}.json",
            {
                "template": "minecraft:apple",
                "tfc": {
                    "weight": 500,
                    "size": "small",
                    "decay": 2.0,
                    "nutrients": {nutrient: 1.5},
                },
            },
        )
        png_rgba(TEX_ITEM / f"food_{name}.png", color)
        tab_items.append(f"tfc:food_{name}")

    for name, t0, t1, r0, r1 in CROPS:
        write_json(ITEM / f"seeds_{name}.json", item_json("minecraft:wheat_seeds"))
        write_json(
            BLOCK / f"crop_{name}.json",
            {
                "template": "minecraft:wheat",
                "properties": {"hardness": 0.0, "sounds": "minecraft:crop"},
                "item": False,
                "tfc": {"min_temp": t0, "max_temp": t1, "min_rain": r0, "max_rain": r1},
            },
        )
        png_rgba(TEX_ITEM / f"seeds_{name}.png", 0x88AA44)
        png_rgba(TEX_BLOCK / f"crop_{name}.png", 0x66AA33)
        tab_items.append(f"tfc:seeds_{name}")


def gen_misc(tab_items: list[str]) -> None:
    for name, color, tmpl in [
        ("lumber", 0xC4A35A, "minecraft:stick"),
        ("wooden_bucket", 0x8B5A2B, "minecraft:bucket"),
        ("pan_empty", 0xA0A0A0, "minecraft:bowl"),
        ("pan_gravel", 0x888888, "minecraft:bowl"),
        ("powder_flux", 0xEEEEEE, "minecraft:sugar"),
        ("powder_saltpeter", 0xF5F5DC, "minecraft:sugar"),
        ("glass_batch", 0xAADDFF, "minecraft:glass"),
        ("chisel", 0xAAAAAA, "minecraft:iron_sword"),
        ("straw", 0xD2B48C, "minecraft:wheat"),
    ]:
        write_json(ITEM / f"{name}.json", item_json(tmpl))
        png_rgba(TEX_ITEM / f"{name}.png", color)
        tab_items.append(f"tfc:{name}")

    write_json(
        RECIPE / "quern_flux.json",
        {
            "type": "tfc:quern",
            "ingredient": "tfc:rock_chalk",
            "result": {"id": "tfc:powder_flux", "count": 2},
            "duration": 100,
        },
    )
    write_json(
        RECIPE / "barrel_tannin.json",
        {
            "type": "tfc:barrel",
            "ingredient": "minecraft:oak_leaves",
            "fluid": "minecraft:water",
            "result": {"id": "tfc:straw", "count": 1},
            "duration": 400,
        },
    )
    write_json(
        RECIPE / "pan_native_copper.json",
        {
            "type": "tfc:panning",
            "ingredient": "minecraft:gravel",
            "result": {"id": "tfc:nugget_copper", "count": 1},
            "chance": 0.15,
        },
    )
    write_json(
        RECIPE / "lumber_from_log.json",
        {
            "type": "tfc:sawing",
            "ingredient": "minecraft:oak_log",
            "result": {"id": "tfc:lumber", "count": 8},
        },
    )


def gen_tables() -> None:
    write_json(
        TABLES / "calendar.json",
        {
            "ticks_per_month": 8 * 24000,
            "months": SEASONS,
            "days_in_month": 8,
        },
    )
    write_json(
        TABLES / "climate.json",
        {
            "base_temp_c": 14.0,
            "temp_latitude_scale": 0.04,
            "temp_altitude_scale": -0.006,
            "base_rainfall": 120.0,
            "rain_noise_scale": 40.0,
            "seasons": [
                {"id": s, "temp_offset": [-6, -2, 2, 6, 10, 8, 4, 0, -2, -6, -10, -8][i], "rain_mult": [1.1, 1.2, 1.1, 1.0, 0.9, 0.85, 1.0, 1.1, 1.15, 1.0, 0.9, 0.95][i]}
                for i, s in enumerate(SEASONS)
            ],
        },
    )
    write_json(
        TABLES / "thirst.json",
        {
            "max": 100.0,
            "drain_per_second": 0.05,
            "sprint_mult": 1.5,
            "drink_jug": 40.0,
            "drink_water_block": 25.0,
            "exhaustion_damage_below": 5.0,
        },
    )
    write_json(
        TABLES / "rocks.json",
        {"rocks": [{"id": n, "category": "igneous_extrusive" if n in ("andesite", "basalt") else "sedimentary"} for n, _ in ROCKS]},
    )
    write_json(
        TABLES / "ores.json",
        {
            "ores": [
                {"id": n, "metal": m, "prospect_hint": f"traces of {m}", "blocks": [f"tfc:ore_{n}"]}
                for n, _, m in ORES
            ]
        },
    )
    write_json(
        TABLES / "knapping.json",
        {
            "recipes": [
                {"id": f"stone_{t}", "ingredient": "tfc:knapping_stone", "result": f"tfc:stone_{t}"}
                for t in STONE_TOOLS
            ]
        },
    )
    write_json(
        TABLES / "heating.json",
        {
            "melting": [
                {"item": "tfc:ore_native_copper", "metal": "copper", "temp": 1080},
                {"item": "tfc:copper_ingot", "metal": "copper", "temp": 1080},
                {"item": "tfc:ore_hematite", "metal": "cast_iron", "temp": 1535},
                {"item": "tfc:gold_ingot", "metal": "gold", "temp": 1060},
            ]
        },
    )
    write_json(
        TABLES / "anvil.json",
        {
            "tiers": {"stone": 0, "copper": 1, "bronze": 2, "wrought_iron": 3, "steel": 4},
            "rules": ["hit_last", "hit_not_last", "hit_any", "draw_last", "draw_any", "punch_last", "bend_any", "upset_any", "shrink_any"],
        },
    )
    write_json(
        TABLES / "nutrition.json",
        {
            "nutrients": ["fruit", "vegetable", "grain", "protein", "dairy"],
            "max_per_nutrient": 100.0,
            "decay_rate_per_day": 0.5,
            "foods": {
                f"tfc:food_{n}": {"nutrient": nut, "amount": 1.5, "weight": 500, "decay": 2.0}
                for n, nut, _ in FOODS
            },
        },
    )
    write_json(
        TABLES / "crops.json",
        {
            "crops": [
                {"id": n, "min_temp": a, "max_temp": b, "min_rain": c, "max_rain": d, "block": f"tfc:crop_{n}", "seed": f"tfc:seeds_{n}"}
                for n, a, b, c, d in CROPS
            ]
        },
    )
    write_json(
        TABLES / "collapse.json",
        {
            "unstable": [f"tfc:cobble_{n}" for n, _ in ROCKS] + [f"tfc:rock_{n}" for n, _ in ROCKS],
            "support": ["tfc:support_beam"],
            "support_radius": 4,
            "check_interval_ticks": 40,
        },
    )
    write_json(
        TABLES / "worldgen.json",
        {
            "status": "blocked",
            "wave": "W12",
            "notes": "Full rock layers / climate maps / veins require Horizon worldgen hooks; hybrid overworld bridge until then.",
            "hybrid": {
                "use_vanilla_biomes": True,
                "climate_from_position": True,
                "manual_ore_blocks": True,
            },
        },
    )
    write_json(
        TABLES / "animals.json",
        {
            "status": "deferred",
            "wave": "W13",
            "reason": "Entity/AI Host APIs incomplete for TFC familiarity genetics; revisit when hooks land.",
            "planned": ["cow", "sheep", "pig", "chicken"],
        },
    )
    write_json(
        TABLES / "greglite_bridge.json",
        {
            "wave": "W15",
            "metal_map": {
                "tfc:copper_ingot": "minecraft:copper_ingot",
                "tfc:tin_ingot": "greglite:tin_ingot",
                "tfc:bronze_ingot": "greglite:bronze_ingot",
                "tfc:wrought_iron_ingot": "greglite:wrought_iron_ingot",
                "tfc:steel_ingot": "greglite:steel_ingot",
                "tfc:zinc_ingot": "greglite:zinc_ingot",
            },
        },
    )


def gen_tracker() -> None:
    systems = []

    def add(sid, wave, status, kind, smoke=""):
        systems.append(
            {
                "id": sid,
                "wave": wave,
                "status": status,
                "kind": kind,
                "source_mod": "terrafirmacraft",
                "smoke": smoke,
            }
        )

    add("scaffold", "W0", "done", "meta", "pack script + manifests")
    add("calendar", "W1", "done", "system", "season advances with day time")
    add("thin_climate", "W1", "done", "system", "action bar temp/rain")
    add("thirst", "W1", "done", "system", "drains; jug/water restores")
    add("hud_action_bar", "W1", "done", "system", "periodic climate/thirst line")
    for n, _ in ROCKS:
        add(f"rock_{n}", "W2", "done", "content", f"/give tfc:rock_{n}")
    for n, _, _ in ORES:
        add(f"ore_{n}", "W2", "done", "content", f"/give tfc:ore_{n}")
    add("prospectors_pick", "W2", "done", "tool", "use near ore → hint")
    add("knapping", "W3", "done", "system", "knap stone axe")
    add("firepit", "W3", "done", "machine", "light with firestarter")
    add("pottery", "W4", "done", "system", "unfired → pit kiln → ceramic")
    add("pit_kiln", "W4", "done", "machine", "fire unfired pottery")
    add("heating", "W5", "done", "system", "heat table")
    add("charcoal_forge", "W5", "done", "machine", "melt copper")
    add("casting", "W5", "done", "system", "mold + metal → head/ingot")
    add("bloomery", "W6", "done", "machine", "hematite → wrought")
    add("anvil", "W6", "done", "machine", "work copper pick head")
    add("nutrition", "W7", "done", "system", "5 nutrients table")
    add("food_decay", "W7", "done", "system", "decay rates on foods")
    for n, *_ in CROPS:
        add(f"crop_{n}", "W8", "done", "content", "grows in climate window")
    add("quern", "W9", "done", "machine", "grind chalk → flux")
    add("barrel", "W9", "done", "machine", "soak recipe")
    add("log_pile", "W10", "done", "content", "place log pile")
    add("support_collapse", "W10", "done", "system", "unsupported cobble collapses")
    add("panning", "W11", "done", "system", "pan gravel → nugget")
    add("sluice", "W11", "done", "machine", "sluice processes gravel")
    add("worldgen_full", "W12", "blocked", "system", "needs Horizon worldgen hooks")
    add("animals", "W13", "deferred", "system", "entity API insufficient")
    add("chisel", "W14", "done", "tool", "item present; modes lite")
    add("powderkeg", "W14", "done", "content", "block present")
    add("blast_furnace", "W14", "done", "machine", "block + recipe stub")
    add("glassworking", "W14", "done", "content", "glass_batch item")
    add("jei_categories", "W15", "todo", "integration", "register when JEI API ready")
    add("jade_plugins", "W15", "todo", "integration", "climate/thirst overlay")
    add("greglite_bridge", "W15", "done", "integration", "tables/greglite_bridge.json")

    write_json(
        ROOT / "tracker" / "catalog.json",
        {
            "schema": 1,
            "updated": "2026-11-15",
            "plan": "docs/tfc-plan.md",
            "mod_version": "0.1.0",
            "systems": systems,
        },
    )


def main() -> None:
    for d in (BLOCK, ITEM, TAB, MENU, RECIPE, TABLES, TEX_BLOCK, TEX_ITEM):
        d.mkdir(parents=True, exist_ok=True)

    tab_items: list[str] = []
    gen_rocks_ores(tab_items)
    gen_tools_knapping(tab_items)
    gen_pottery_heat(tab_items)
    gen_machines(tab_items)
    gen_metals(tab_items)
    gen_food_crops(tab_items)
    gen_misc(tab_items)
    gen_tables()
    gen_tracker()

    # de-dupe tab while preserving order
    seen = set()
    ordered = []
    for i in tab_items:
        if i not in seen:
            seen.add(i)
            ordered.append(i)

    write_json(
        TAB / "tfc.json",
        {"title": "TFC Horizon", "icon": "tfc:prospectors_pick", "items": ordered},
    )
    print(f"tfc content: {len(ordered)} tab items, rocks={len(ROCKS)}, ores={len(ORES)}")


if __name__ == "__main__":
    main()
