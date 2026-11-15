#!/usr/bin/env python3
"""Generate TFC Horizon content, data tables, and the machine spec include.

Run from the repo root or anywhere:

    python3 mods/tfc/tools/gen_content.py

Placeholder textures are solid 16×16 PNGs. Run fetch_tfc_textures.py after this
to replace them with TerraFirmaCraft (EUPL-1.2) assets. No Mojang assets.
"""

from __future__ import annotations

import json
import shutil
import zlib
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "tfc"
DATA = ROOT / "data" / "tfc"
TABLES = ROOT / "tables"

ROCKS = ["andesite", "granite", "basalt", "chalk", "chert", "shale", "limestone", "marble"]
ROCK_FORMS = ["raw", "cobble", "smooth", "gravel"]
PLANNED_LAYERS = ROCKS + [
    "diorite",
    "gabbro",
    "claystone",
    "conglomerate",
    "dolomite",
    "quartzite",
    "slate",
    "phyllite",
    "schist",
    "gneiss",
    "rhyolite",
    "dacite",
]

ORES = [
    ("native_copper", "native copper", "copper", "forge", (184, 115, 51)),
    ("native_gold", "native gold", "gold", "forge", (212, 175, 55)),
    ("native_silver", "native silver", "silver", "forge", (200, 200, 210)),
    ("cassiterite", "cassiterite", "tin", "forge", (140, 150, 145)),
    ("hematite", "hematite", "iron", "bloomery", (140, 70, 60)),
    ("bismuthinite", "bismuthinite", "bismuth", "forge", (120, 160, 140)),
    ("sphalerite", "sphalerite", "zinc", "forge", (170, 160, 90)),
    ("malachite", "malachite", "copper", "forge", (40, 150, 90)),
]

METALS = [
    ("copper", (184, 115, 51)),
    ("tin", (180, 196, 196)),
    ("bronze", (176, 120, 56)),
    ("bismuth", (130, 170, 150)),
    ("zinc", (186, 176, 140)),
    ("brass", (214, 174, 66)),
    ("silver", (210, 210, 216)),
    ("wrought_iron", (160, 160, 168)),
    ("steel", (120, 130, 140)),
]
METAL_FORMS = ["ingot", "double_ingot", "sheet", "rod"]
CAST_METALS = ["copper", "bronze"]
FORGE_METALS = ["wrought_iron"]
TOOL_KINDS = ["axe", "hoe", "knife", "pickaxe", "shovel", "hammer", "chisel", "propick"]
HEAD_OF = {
    "axe": "axe_head",
    "hoe": "hoe_head",
    "knife": "knife_blade",
    "pickaxe": "pickaxe_head",
    "shovel": "shovel_head",
    "hammer": "hammer_head",
    "chisel": "chisel_head",
    "propick": "propick_head",
}
STONE_TOOLS = ["axe", "hoe", "knife", "shovel", "hammer"]

MACHINES = [
    {"id": "firepit", "fuel": True, "inputs": 1, "recipe": "firepit"},
    {"id": "charcoal_forge", "fuel": True, "inputs": 1, "recipe": "charcoal_forge"},
    {"id": "bloomery", "fuel": True, "inputs": 1, "recipe": "bloomery"},
    {"id": "anvil", "fuel": False, "inputs": 1, "recipe": "anvil"},
    {"id": "quern", "fuel": False, "inputs": 1, "recipe": "quern"},
    {"id": "barrel", "fuel": False, "inputs": 1, "recipe": "barrel"},
    {"id": "pit_kiln", "fuel": False, "inputs": 1, "recipe": "pit_kiln"},
    {"id": "blast_furnace", "fuel": True, "inputs": 2, "recipe": "blast_furnace"},
    {"id": "sluice", "fuel": False, "inputs": 1, "recipe": "sluice"},
    {"id": "charcoal_pit", "fuel": False, "inputs": 1, "recipe": "charcoal_pit"},
    {"id": "log_pile", "fuel": False, "inputs": 9, "recipe": None, "storage": True},
]

MONTHS = [
    ("january", "winter", -8),
    ("february", "winter", -6),
    ("march", "spring", -2),
    ("april", "spring", 2),
    ("may", "spring", 6),
    ("june", "summer", 10),
    ("july", "summer", 12),
    ("august", "summer", 10),
    ("september", "autumn", 4),
    ("october", "autumn", 0),
    ("november", "autumn", -4),
    ("december", "winter", -8),
]

FOODS = [
    ("red_apple", 0, 1, 0, 0, 0, "small", "light", 4),
    ("carrot", 0, 0, 1, 0, 0, "small", "light", 5),
    ("bread", 1, 0, 0, 0, 0, "small", "light", 6),
    ("cooked_meat", 0, 0, 0, 1, 0, "medium", "medium", 3),
    ("cheese", 0, 0, 0, 0, 1, "small", "light", 5),
    ("cabbage", 0, 0, 1, 0, 0, "medium", "medium", 4),
    ("wheat", 1, 0, 0, 0, 0, "small", "light", 12),
    ("barley_grain", 1, 0, 0, 0, 0, "small", "light", 12),
    ("flour", 1, 0, 0, 0, 0, "small", "light", 8),
    ("dough", 1, 0, 0, 0, 0, "small", "medium", 3),
]

CROPS = [
    ("crop_wheat", "wheat", "wheat_seed", 10, 30, ["spring", "summer"]),
    ("crop_barley", "barley_grain", "barley_seed", 4, 28, ["spring", "autumn"]),
    ("crop_cabbage", "cabbage", "cabbage_seed", 5, 26, ["spring", "summer", "autumn"]),
]

ANIMALS = ["cow", "sheep", "pig", "chicken", "horse", "wolf", "deer", "fish"]


def output_index(machine: dict) -> int | None:
    if machine.get("storage"):
        return None
    start = 1 if machine["fuel"] else 0
    return start + machine["inputs"]


def write_json(path: Path, body: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")


def _shade(rgb: tuple[int, int, int], factor: float) -> tuple[int, int, int]:
    return tuple(max(0, min(255, int(c * factor))) for c in rgb)  # type: ignore[return-value]


def png(path: Path, rgb: tuple[int, int, int], shape: str = "flat") -> None:
    """Write textures with PIL (same path as Greglite) so Horizon atlases them."""
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    hi, mid, lo = _shade(rgb, 1.2), rgb, _shade(rgb, 0.55)

    def fill_rect(xy: tuple[int, int, int, int], color: tuple[int, int, int]) -> None:
        d.rectangle(xy, fill=(*color, 255))

    if shape == "block" or shape == "flat":
        fill_rect((0, 0, 15, 15), mid)
        d.rectangle((0, 0, 15, 15), outline=(*hi, 255))
        d.rectangle((1, 1, 14, 14), outline=(*lo, 255))
        # Noise so cubes aren't flat missing-texture look.
        for y in range(2, 14):
            for x in range(2, 14):
                if (x * 3 + y * 5) % 7 == 0:
                    img.putpixel((x, y), (*_shade(mid, 0.85), 255))
    elif shape == "ingot":
        fill_rect((3, 5, 12, 10), mid)
        fill_rect((2, 6, 13, 9), mid)
        d.line([(3, 5), (12, 5)], fill=(*hi, 255))
        d.line([(3, 10), (12, 10)], fill=(*lo, 255))
    elif shape == "double_ingot":
        fill_rect((2, 2, 13, 6), mid)
        fill_rect((2, 9, 13, 13), mid)
        d.line([(2, 2), (13, 2)], fill=(*hi, 255))
        d.line([(2, 9), (13, 9)], fill=(*hi, 255))
    elif shape == "sheet":
        fill_rect((1, 2, 14, 13), mid)
        d.rectangle((1, 2, 14, 13), outline=(*hi, 255))
    elif shape == "rod":
        fill_rect((6, 1, 9, 14), mid)
        fill_rect((7, 0, 8, 15), hi)
    elif shape == "nugget":
        d.ellipse((4, 4, 11, 11), fill=(*mid, 255), outline=(*hi, 255))
    elif shape == "dust":
        for xy in ((3, 5), (6, 4), (9, 5), (5, 7), (8, 8), (4, 9), (10, 9), (7, 11)):
            fill_rect((xy[0], xy[1], xy[0] + 2, xy[1] + 2), mid)
    elif shape == "tool":
        # Thick pickaxe silhouette — thin masks were invisible in creative.
        d.polygon([(14, 1), (15, 2), (15, 5), (12, 8), (10, 6), (13, 3)], fill=(*mid, 255))
        fill_rect((3, 10, 5, 15), lo)
        fill_rect((4, 6, 6, 12), lo)
        fill_rect((6, 4, 9, 7), mid)
    else:
        fill_rect((2, 2, 13, 13), mid)

    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)


def shape_for_item(name: str) -> str:
    if name.endswith("_double_ingot"):
        return "double_ingot"
    if name.endswith("_ingot") or name in {"raw_iron_bloom"}:
        return "ingot"
    if name.endswith("_sheet"):
        return "sheet"
    if name.endswith("_rod"):
        return "rod"
    if name.startswith("nugget_") or name.endswith("_nugget"):
        return "nugget"
    if name.endswith("_dust") or name in {"flux", "flour", "glass_batch", "ore_deposit"}:
        return "dust"
    if any(
        name.endswith(s)
        for s in (
            "_axe",
            "_hoe",
            "_knife",
            "_pickaxe",
            "_shovel",
            "_hammer",
            "_chisel",
            "_propick",
            "_blade",
            "_head",
        )
    ) or name in {"prospector_pick"} or name.startswith("stone_"):
        return "tool"
    return "ingot"


def color_for(key: str, bias: tuple[int, int, int] = (80, 80, 80)) -> tuple[int, int, int]:
    h = zlib.crc32(key.encode()) & 0xFFFFFFFF
    return tuple((bias[i] + ((h >> (8 * i)) & 255)) // 2 for i in range(3))  # type: ignore[return-value]


def title(name: str) -> str:
    return " ".join(part.capitalize() for part in name.split("_"))


def block_files(name: str, rgb: tuple[int, int, int], furnace: bool, hardness: float, sounds: str) -> None:
    # Always use furnace + orientable: Horizon leaves cube_all / empty-variant
    # rocks with empty model-states and invisible creative icons. Barrel (furnace)
    # was the only TFC block that rendered.
    _ = furnace
    write_json(
        DATA / "horizon" / "block" / f"{name}.json",
        {
            "template": "minecraft:furnace",
            "properties": {"hardness": hardness, "sounds": sounds},
            "item": True,
        },
    )
    tex = f"tfc:block/{name}"
    write_json(
        ASSETS / "models" / "block" / f"{name}.json",
        {
            "parent": "minecraft:block/orientable",
            "textures": {
                "top": tex,
                "front": tex,
                "side": tex,
                "bottom": tex,
                "particle": tex,
            },
        },
    )
    write_json(ASSETS / "models" / "item" / f"{name}.json", {"parent": f"tfc:block/{name}"})
    # JE 26.3 item definitions (Greglite has these; without them icons are blank/white).
    write_json(
        ASSETS / "items" / f"{name}.json",
        {"model": {"type": "minecraft:model", "model": f"tfc:item/{name}"}},
    )
    variants = {}
    for facing, rot in (("north", None), ("south", 180), ("west", 270), ("east", 90)):
        for lit in ("false", "true"):
            entry: dict = {"model": f"tfc:block/{name}"}
            if rot is not None:
                entry["y"] = rot
            variants[f"facing={facing},lit={lit}"] = entry
    write_json(ASSETS / "blockstates" / f"{name}.json", {"variants": variants})
    png(ASSETS / "textures" / "block" / f"{name}.png", rgb, shape="block")
    write_json(
        DATA / "loot_table" / "blocks" / f"{name}.json",
        {
            "type": "minecraft:block",
            "pools": [
                {
                    "rolls": 1,
                    "entries": [{"type": "minecraft:item", "name": f"tfc:{name}"}],
                    "conditions": [{"condition": "minecraft:survives_explosion"}],
                }
            ],
        },
    )
    return None


def item_files(name: str, rgb: tuple[int, int, int], template: str = "minecraft:iron_ingot") -> None:
    write_json(DATA / "horizon" / "item" / f"{name}.json", {"template": template})
    write_json(
        ASSETS / "models" / "item" / f"{name}.json",
        {"parent": "minecraft:item/generated", "textures": {"layer0": f"tfc:item/{name}"}},
    )
    write_json(
        ASSETS / "items" / f"{name}.json",
        {"model": {"type": "minecraft:model", "model": f"tfc:item/{name}"}},
    )
    png(ASSETS / "textures" / "item" / f"{name}.png", rgb, shape=shape_for_item(name))


def shapeless(name: str, ingredients: list[str], result: str, count: int = 1) -> None:
    write_json(
        DATA / "recipe" / f"{name}.json",
        {
            "type": "minecraft:crafting_shapeless",
            "ingredients": [{"item": item} for item in ingredients],
            "result": {"id": result, "count": count},
        },
    )


def machine_recipe(
    kind: str,
    name: str,
    ingredients: list[str],
    result: str,
    count: int = 1,
    duration: int = 160,
) -> None:
    body: dict = {
        "type": f"tfc:{kind}",
        "result": {"id": result, "count": count},
        "duration": duration,
    }
    if len(ingredients) == 1:
        body["ingredient"] = ingredients[0]
    else:
        body["ingredients"] = ingredients
    write_json(DATA / "recipe" / f"{kind}_{name}.json", body)


def menu(name: str, slots: int, results: list[int]) -> None:
    write_json(
        DATA / "horizon" / "menu" / f"{name}.json",
        {"slots": slots, "data_slots": 4, "results": results},
    )


def reset_generated() -> None:
    for path in (ASSETS, DATA):
        if path.exists():
            shutil.rmtree(path)
    TABLES.mkdir(parents=True, exist_ok=True)


def write_tables() -> None:
    write_json(
        TABLES / "climate_seasons.json",
        {
            "days_per_month": 8,
            "base_temp": 14.0,
            "base_rain": 300.0,
            "months": [
                {"name": name, "season": season, "temp_offset": offset}
                for name, season, offset in MONTHS
            ],
        },
    )
    write_json(
        TABLES / "nutrition.json",
        {
            "drinks": ["tfc:jug", "tfc:wooden_bucket"],
            "foods": [
                {
                    "id": f"tfc:{name}",
                    "grain": grain,
                    "fruit": fruit,
                    "veg": veg,
                    "protein": protein,
                    "dairy": dairy,
                    "size": size,
                    "weight": weight,
                    "decay_days": decay,
                }
                for name, grain, fruit, veg, protein, dairy, size, weight, decay in FOODS
            ],
        },
    )
    write_json(
        TABLES / "crops.json",
        [
            {
                "id": f"tfc:{block}",
                "product": f"tfc:{product}",
                "seed": f"tfc:{seed}",
                "min_temp": min_temp,
                "max_temp": max_temp,
                "seasons": seasons,
            }
            for block, product, seed, min_temp, max_temp, seasons in CROPS
        ],
    )
    write_json(
        TABLES / "ores.json",
        [
            {
                "block": f"tfc:ore_{name}",
                "name": label,
                "metal": metal,
                "path": path,
                "nugget": f"tfc:nugget_{name}",
            }
            for name, label, metal, path, _rgb in ORES
        ],
    )
    write_json(
        TABLES / "heat.json",
        {
            "copper": 1080,
            "tin": 230,
            "bronze": 950,
            "bismuth": 270,
            "zinc": 420,
            "brass": 930,
            "silver": 961,
            "wrought_iron": 1535,
            "steel": 1540,
        },
    )
    write_json(
        TABLES / "animals.json",
        [
            {
                "id": f"tfc:{name}",
                "status": "deferred",
                "reason": "Entity spawn hooks are not used on hooks 411.",
            }
            for name in ANIMALS
        ],
    )
    write_json(
        TABLES / "worldgen.json",
        {
            "status": "blocked",
            "wave": "W12",
            "reason": "Chunk generation is not hooked. Rocks and ores are placed by hand; prospect reports a preview rock.",
            "needed_hooks": [
                "climate_map",
                "rock_layers",
                "ore_veins",
                "custom_biome_source",
            ],
            "bridge": "vanilla_overworld_plus_placeable_tfc_rocks_ores",
            "content_rocks": ROCKS,
            "planned_layers": PLANNED_LAYERS,
        },
    )
    write_json(
        TABLES / "knapping.json",
        {
            "note": "Knapping UI is a crafting stand-in in 0.1.0.",
            "recipes": [f"stone_{tool}" for tool in STONE_TOOLS],
        },
    )
    machines = []
    for machine in MACHINES:
        out = output_index(machine)
        machines.append(
            {
                "id": f"tfc:{machine['id']}",
                "fuel": machine["fuel"],
                "inputs": machine["inputs"],
                "output": out,
                "storage": bool(machine.get("storage")),
                "recipe_type": None if machine["recipe"] is None else f"tfc:{machine['recipe']}",
            }
        )
    write_json(TABLES / "machines.json", machines)


def write_specs(machines: list[dict]) -> None:
    lines = ["["]
    for machine in machines:
        kind = "Kind::Storage" if machine["storage"] else "Kind::Machine"
        fuel = "true" if machine["fuel"] else "false"
        output = "None" if machine["output"] is None else f"Some({machine['output']})"
        recipe = "None" if machine["recipe_type"] is None else f'Some("{machine["recipe_type"]}")'
        lines.append(
            "    Spec {\n"
            f'        id: "{machine["id"]}",\n'
            f"        kind: {kind},\n"
            f"        fuel: {fuel},\n"
            f"        inputs: {machine['inputs']},\n"
            f"        output: {output},\n"
            f"        recipe_type: {recipe},\n"
            "    },"
        )
    lines.append("]")
    path = ROOT / "api" / "src" / "specs.inc.rs"
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def metal_result(metal: str) -> str:
    if metal == "gold":
        return "minecraft:gold_ingot"
    if metal == "iron":
        return "tfc:raw_iron_bloom"
    return f"tfc:{metal}_ingot"


def main() -> None:
    reset_generated()
    write_tables()
    machines = json.loads((TABLES / "machines.json").read_text(encoding="utf-8"))
    write_specs(machines)
    lang: dict[str, str] = {"itemGroup.tfc.tfc": "TFC Horizon"}
    tab_items: list[str] = []

    def tab(id_: str) -> None:
        if id_ not in tab_items:
            tab_items.append(id_)

    for name in ROCKS:
        for form in ROCK_FORMS:
            block = f"{name}_{form}"
            block_files(block, color_for(block, (90, 80, 70)), False, 1.8 if form == "raw" else 1.2, "minecraft:stone")
            lang[f"block.tfc.{block}"] = f"{title(name)} {title(form)}"
            tab(f"tfc:{block}")

    for name, label, _metal, _path, rgb in ORES:
        block = f"ore_{name}"
        block_files(block, rgb, False, 2.5, "minecraft:stone")
        lang[f"block.tfc.{block}"] = title(label)
        tab(f"tfc:{block}")
        item_files(f"nugget_{name}", rgb)
        lang[f"item.tfc.nugget_{name}"] = f"{title(label)} Nugget"
        tab(f"tfc:nugget_{name}")

    for machine in MACHINES:
        name = machine["id"]
        rgb = color_for(name, (120, 70, 40))
        block_files(name, rgb, True, 3.0, "minecraft:stone")
        lang[f"block.tfc.{name}"] = title(name)
        tab(f"tfc:{name}")
        out = output_index(machine)
        slots = machine["inputs"] if machine.get("storage") else (out or 0) + 1
        results = [] if out is None else [out]
        menu(name, slots, results)

    for name, _product, _seed, _lo, _hi, _seasons in CROPS:
        block_files(name, color_for(name, (40, 120, 40)), True, 0.4, "minecraft:stone")
        lang[f"block.tfc.{name}"] = title(name)
        tab(f"tfc:{name}")
        menu(name, 1, [0])

    block_files("support_beam", (120, 86, 48), False, 1.5, "minecraft:stone")
    lang["block.tfc.support_beam"] = "Support Beam"
    tab("tfc:support_beam")
    block_files("powderkeg", (90, 50, 40), False, 1.5, "minecraft:stone")
    lang["block.tfc.powderkeg"] = "Powderkeg"
    tab("tfc:powderkeg")

    for metal, rgb in METALS:
        for form in METAL_FORMS:
            item = f"{metal}_{form}"
            item_files(item, rgb)
            lang[f"item.tfc.{item}"] = f"{title(metal)} {title(form)}"
            tab(f"tfc:{item}")
        if metal in CAST_METALS or metal in FORGE_METALS:
            for tool in TOOL_KINDS:
                item_files(f"{metal}_{tool}", rgb, "minecraft:iron_pickaxe")
                lang[f"item.tfc.{metal}_{tool}"] = f"{title(metal)} {title(tool)}"
                tab(f"tfc:{metal}_{tool}")
                head = HEAD_OF[tool]
                item_files(f"{metal}_{head}", rgb)
                lang[f"item.tfc.{metal}_{head}"] = f"{title(metal)} {title(head)}"
                tab(f"tfc:{metal}_{head}")

    for tool in STONE_TOOLS:
        item_files(f"stone_{tool}", (140, 140, 140), "minecraft:stone_pickaxe")
        lang[f"item.tfc.stone_{tool}"] = f"Stone {title(tool)}"
        tab(f"tfc:stone_{tool}")

    extras = {
        "prospector_pick": ((160, 120, 70), "minecraft:iron_pickaxe"),
        "pan": ((150, 130, 80), "minecraft:bowl"),
        "jug": ((90, 140, 170), "minecraft:potion"),
        "wooden_bucket": ((140, 100, 60), "minecraft:bucket"),
        "vessel": ((170, 150, 120), "minecraft:bowl"),
        "unfired_vessel": ((150, 110, 80), "minecraft:bowl"),
        "unfired_jug": ((150, 110, 80), "minecraft:potion"),
        "straw": ((196, 176, 90), "minecraft:wheat"),
        "flux": ((210, 210, 200), "minecraft:sugar"),
        "raw_iron_bloom": ((120, 80, 70), "minecraft:iron_ingot"),
        "glass_batch": ((180, 210, 200), "minecraft:sand"),
        "lumber": ((150, 110, 60), "minecraft:stick"),
        "tannin": ((120, 70, 40), "minecraft:potion"),
        "ore_deposit": ((130, 110, 80), "minecraft:gravel"),
    }
    for name, (rgb, template) in extras.items():
        item_files(name, rgb, template)
        lang[f"item.tfc.{name}"] = title(name)
        tab(f"tfc:{name}")

    for name, *_rest in FOODS:
        if (DATA / "horizon" / "item" / f"{name}.json").exists():
            lang[f"item.tfc.{name}"] = title(name)
            tab(f"tfc:{name}")
            continue
        item_files(name, color_for(name, (160, 80, 60)), "minecraft:apple")
        lang[f"item.tfc.{name}"] = title(name)
        tab(f"tfc:{name}")

    # Crafting stand-ins.
    for tool in STONE_TOOLS:
        shapeless(f"stone_{tool}", ["tfc:andesite_cobble", "minecraft:stick"], f"tfc:stone_{tool}")
    shapeless("prospector_pick", ["tfc:copper_ingot", "minecraft:stick"], "tfc:prospector_pick")
    shapeless("firepit", ["minecraft:stick", "minecraft:stick", "minecraft:oak_log"], "tfc:firepit")
    shapeless("charcoal_forge", ["tfc:andesite_cobble", "tfc:andesite_cobble", "minecraft:charcoal"], "tfc:charcoal_forge")
    shapeless("pit_kiln", ["tfc:straw", "tfc:straw", "minecraft:oak_log"], "tfc:pit_kiln")
    shapeless("straw", ["tfc:wheat", "tfc:wheat", "tfc:wheat", "tfc:wheat"], "tfc:straw")
    shapeless("unfired_vessel", ["minecraft:clay_ball", "minecraft:clay_ball"], "tfc:unfired_vessel")
    shapeless("unfired_jug", ["minecraft:clay_ball"], "tfc:unfired_jug")
    shapeless("anvil", ["tfc:copper_double_ingot", "tfc:copper_double_ingot"], "tfc:anvil")
    shapeless("quern", ["tfc:andesite_raw", "tfc:andesite_smooth", "minecraft:stick"], "tfc:quern")
    shapeless("barrel", ["minecraft:oak_log", "minecraft:oak_log", "tfc:lumber"], "tfc:barrel")
    shapeless("bloomery", ["tfc:bronze_sheet", "tfc:bronze_sheet", "tfc:bronze_sheet"], "tfc:bloomery")
    shapeless("blast_furnace", ["tfc:wrought_iron_sheet", "minecraft:bricks", "tfc:wrought_iron_sheet"], "tfc:blast_furnace")
    shapeless("sluice", ["tfc:lumber", "tfc:lumber", "minecraft:oak_trapdoor"], "tfc:sluice")
    shapeless("charcoal_pit", ["minecraft:oak_log", "tfc:straw"], "tfc:charcoal_pit")
    shapeless("log_pile", ["minecraft:oak_log", "minecraft:oak_log", "minecraft:oak_log", "minecraft:oak_log"], "tfc:log_pile")
    shapeless("lumber", ["minecraft:oak_log"], "tfc:lumber", 4)
    shapeless("support_beam", ["tfc:lumber", "tfc:lumber"], "tfc:support_beam")
    shapeless("wooden_bucket", ["tfc:lumber", "tfc:lumber", "tfc:lumber"], "tfc:wooden_bucket")
    shapeless("pan", ["tfc:copper_sheet"], "tfc:pan")
    shapeless("dough", ["tfc:flour"], "tfc:dough")
    shapeless("weld_copper", ["tfc:copper_ingot", "tfc:copper_ingot"], "tfc:copper_double_ingot")
    shapeless("weld_bronze", ["tfc:bronze_ingot", "tfc:bronze_ingot"], "tfc:bronze_double_ingot")
    shapeless("alloy_bronze", ["tfc:copper_ingot", "tfc:tin_ingot"], "tfc:bronze_ingot", 2)
    shapeless("alloy_brass", ["tfc:copper_ingot", "tfc:zinc_ingot"], "tfc:brass_ingot", 2)
    shapeless("glass_batch", ["minecraft:sand", "tfc:flux"], "tfc:glass_batch")
    shapeless("powderkeg", ["minecraft:gunpowder", "tfc:lumber"], "tfc:powderkeg")
    shapeless("ore_deposit", ["minecraft:gravel", "tfc:pan"], "tfc:ore_deposit")

    for metal in CAST_METALS + FORGE_METALS:
        for tool, head in HEAD_OF.items():
            shapeless(f"{metal}_{tool}", [f"tfc:{metal}_{head}", "minecraft:stick"], f"tfc:{metal}_{tool}")

    # Machine loops. One input unless blast_furnace.
    machine_recipe("firepit", "beef", ["minecraft:beef"], "tfc:cooked_meat", duration=120)
    machine_recipe("firepit", "pork", ["minecraft:porkchop"], "tfc:cooked_meat", duration=120)
    machine_recipe("firepit", "dough", ["tfc:dough"], "tfc:bread", duration=120)
    machine_recipe("charcoal_forge", "copper", ["tfc:nugget_native_copper"], "tfc:copper_ingot", duration=160)
    machine_recipe("charcoal_forge", "malachite", ["tfc:nugget_malachite"], "tfc:copper_ingot", duration=160)
    machine_recipe("charcoal_forge", "tin", ["tfc:nugget_cassiterite"], "tfc:tin_ingot", duration=140)
    machine_recipe("charcoal_forge", "bismuth", ["tfc:nugget_bismuthinite"], "tfc:bismuth_ingot", duration=120)
    machine_recipe("charcoal_forge", "zinc", ["tfc:nugget_sphalerite"], "tfc:zinc_ingot", duration=140)
    machine_recipe("charcoal_forge", "silver", ["tfc:nugget_native_silver"], "tfc:silver_ingot", duration=180)
    machine_recipe("charcoal_forge", "gold", ["tfc:nugget_native_gold"], "minecraft:gold_ingot", duration=180)
    for tool, head in HEAD_OF.items():
        for metal in CAST_METALS:
            machine_recipe(
                "charcoal_forge",
                f"{metal}_{head}",
                [f"tfc:{metal}_ingot"],
                f"tfc:{metal}_{head}",
                duration=200,
            )
    machine_recipe("bloomery", "hematite", ["tfc:nugget_hematite"], "tfc:raw_iron_bloom", duration=300)
    machine_recipe("anvil", "bloom", ["tfc:raw_iron_bloom"], "tfc:wrought_iron_ingot", duration=200)
    machine_recipe("anvil", "copper_sheet", ["tfc:copper_ingot"], "tfc:copper_sheet", duration=160)
    machine_recipe("anvil", "bronze_sheet", ["tfc:bronze_ingot"], "tfc:bronze_sheet", duration=160)
    machine_recipe("anvil", "wrought_sheet", ["tfc:wrought_iron_ingot"], "tfc:wrought_iron_sheet", duration=200)
    for tool, head in HEAD_OF.items():
        machine_recipe(
            "anvil",
            f"wrought_{head}",
            ["tfc:wrought_iron_ingot"],
            f"tfc:wrought_iron_{head}",
            duration=220,
        )
    machine_recipe("quern", "wheat", ["tfc:wheat"], "tfc:flour", duration=120)
    machine_recipe("quern", "barley", ["tfc:barley_grain"], "tfc:flour", duration=120)
    machine_recipe("quern", "flux", ["tfc:limestone_gravel"], "tfc:flux", duration=100)
    machine_recipe("barrel", "tannin", ["minecraft:oak_log"], "tfc:tannin", duration=200)
    machine_recipe("pit_kiln", "vessel", ["tfc:unfired_vessel"], "tfc:vessel", duration=240)
    machine_recipe("pit_kiln", "jug", ["tfc:unfired_jug"], "tfc:jug", duration=240)
    machine_recipe("pit_kiln", "glass", ["tfc:glass_batch"], "minecraft:glass", duration=240)
    machine_recipe(
        "blast_furnace",
        "steel",
        ["tfc:wrought_iron_ingot", "tfc:flux"],
        "tfc:steel_ingot",
        duration=320,
    )
    machine_recipe("sluice", "copper", ["tfc:ore_deposit"], "tfc:nugget_native_copper", duration=160)
    machine_recipe("charcoal_pit", "oak", ["minecraft:oak_log"], "minecraft:charcoal", duration=240)

    write_json(
        DATA / "horizon" / "creative_tab" / "tfc.json",
        {
            "title": "TFC Horizon",
            "icon": "tfc:copper_ingot",
            "items": tab_items,
        },
    )
    write_json(ASSETS / "lang" / "en_us.json", lang)
    print(f"generated {len(lang)} lang entries, creative tab {len(tab_items)} items under {ROOT}")


if __name__ == "__main__":
    main()
