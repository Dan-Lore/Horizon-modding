"""Generate Greglite content JSON (Steam Age + LV Electric datapack slice)."""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "greglite"
ASSETS = ROOT / "assets" / "greglite"
CATALOG = ROOT / "tracker" / "catalog.json"
TEXTURES = ASSETS / "textures"

STEAM_ITEMS = [
    "tin_ingot",
    "tin_dust",
    "tin_plate",
    "bronze_ingot",
    "bronze_dust",
    "bronze_plate",
    "copper_dust",
    "copper_plate",
    "iron_dust",
    "iron_plate",
]

ELECTRIC_ITEMS = [
    "tin_wire",
    "copper_wire",
    "tin_rod",
    "copper_rod",
    "rubber",
    "lv_battery",
]

STEAM_BLOCKS = [
    "steam_solid_boiler_lp",
    "steam_alloy_smelter",
    "steam_macerator",
    "steam_compressor",
]

MENU_ALIASES = {"steam_solid_boiler_lp": "steam_boiler"}

TEXTURE_SRC = "steam_macerator"
TEXTURE_DST = "lv_machine"

MACERATE_PAIRS = [
    ("minecraft:copper_ingot", "greglite:copper_dust"),
    ("minecraft:raw_copper", "greglite:copper_dust"),
    ("greglite:tin_ingot", "greglite:tin_dust"),
    ("greglite:bronze_ingot", "greglite:bronze_dust"),
    ("minecraft:iron_ingot", "greglite:iron_dust"),
    ("minecraft:raw_iron", "greglite:iron_dust"),
    ("greglite:copper_plate", "greglite:copper_dust"),
    ("greglite:tin_plate", "greglite:tin_dust"),
    ("greglite:bronze_plate", "greglite:bronze_dust"),
    ("greglite:iron_plate", "greglite:iron_dust"),
]

COMPRESS_PAIRS = [
    ("greglite:copper_dust", "greglite:copper_plate"),
    ("minecraft:copper_ingot", "greglite:copper_plate"),
    ("greglite:tin_dust", "greglite:tin_plate"),
    ("greglite:tin_ingot", "greglite:tin_plate"),
    ("greglite:bronze_dust", "greglite:bronze_plate"),
    ("greglite:bronze_ingot", "greglite:bronze_plate"),
    ("greglite:iron_dust", "greglite:iron_plate"),
    ("minecraft:iron_ingot", "greglite:iron_plate"),
]

MULTI_INPUT_TYPES = {
    "alloy_smelter",
    "mixer",
    "assembler",
    "chemical_reactor",
    "circuit_assembler",
    "canner",
    "chemical_bath",
    "distillery",
    "brewery",
    "fermenter",
    "autoclave",
}


def load_catalog() -> dict:
    return json.loads(CATALOG.read_text(encoding="utf-8"))


def lv_machines(catalog: dict) -> list[dict]:
    return [m for m in catalog["machines"] if m.get("tier") == "lv"]


def human_name(machine_id: str) -> str:
    return re.sub(r"\b\w", lambda m: m.group(0).upper(), machine_id.replace("_", " "))


def human_item(name: str) -> str:
    special = {
        "lv_battery": "LV Battery",
        "tin_wire": "Tin Wire",
        "copper_wire": "Copper Wire",
        "tin_rod": "Tin Rod",
        "copper_rod": "Copper Rod",
    }
    return special.get(name, human_name(name))


def write(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def write_item(item: str, *, template: str = "minecraft:iron_ingot") -> None:
    write(DATA / "horizon" / "item" / f"{item}.json", {"template": template})
    write(
        ASSETS / "items" / f"{item}.json",
        {"model": {"type": "minecraft:model", "model": f"greglite:item/{item}"}},
    )
    write(
        ASSETS / "models" / "item" / f"{item}.json",
        {
            "parent": "minecraft:item/generated",
            "textures": {"layer0": f"greglite:item/{item}"},
        },
    )


def blockstate_orientable(block: str) -> dict:
    def variant(model: str, y: int = 0) -> dict:
        out: dict = {"model": model}
        if y:
            out["y"] = y
        return out

    base = f"greglite:block/{block}"
    on = f"greglite:block/{block}_on"
    return {
        "variants": {
            "facing=north,lit=false": variant(base),
            "facing=south,lit=false": variant(base, 180),
            "facing=west,lit=false": variant(base, 270),
            "facing=east,lit=false": variant(base, 90),
            "facing=north,lit=true": variant(on),
            "facing=south,lit=true": variant(on, 180),
            "facing=west,lit=true": variant(on, 270),
            "facing=east,lit=true": variant(on, 90),
        }
    }


def write_orientable_block(block: str, *, shared_lv_texture: bool) -> None:
    write(
        DATA / "horizon" / "block" / f"{block}.json",
        {
            "template": "minecraft:furnace",
            "properties": {"hardness": 3.5, "sounds": "minecraft:iron_block"},
            "item": True,
        },
    )
    write(
        DATA / "loot_table" / "blocks" / f"{block}.json",
        {
            "type": "minecraft:block",
            "pools": [
                {
                    "rolls": 1,
                    "entries": [{"type": "minecraft:item", "name": f"greglite:{block}"}],
                    "conditions": [{"condition": "minecraft:survives_explosion"}],
                }
            ],
        },
    )
    write(ASSETS / "blockstates" / f"{block}.json", blockstate_orientable(block))

    if shared_lv_texture:
        tex = TEXTURE_DST
    else:
        tex = block
    for suffix, front in (("", "front"), ("_on", "front_on")):
        write(
            ASSETS / "models" / "block" / f"{block}{suffix}.json",
            {
                "parent": "minecraft:block/orientable",
                "textures": {
                    "top": f"greglite:block/{tex}_top",
                    "front": f"greglite:block/{tex}_{front}",
                    "side": f"greglite:block/{tex}_side",
                    "bottom": f"greglite:block/{tex}_bottom",
                    "particle": f"greglite:block/{tex}_side",
                },
            },
        )
    write(
        ASSETS / "items" / f"{block}.json",
        {"model": {"type": "minecraft:model", "model": f"greglite:item/{block}"}},
    )
    write(
        ASSETS / "models" / "item" / f"{block}.json",
        {"parent": f"greglite:block/{block}"},
    )


def copy_lv_textures() -> None:
    block_tex = TEXTURES / "block"
    block_tex.mkdir(parents=True, exist_ok=True)
    mapping = {
        "bottom": "bottom",
        "top": "top",
        "side": "side",
        "front": "front",
        "front_on": "front_on",
    }
    for dst_part, src_part in mapping.items():
        src = block_tex / f"{TEXTURE_SRC}_{src_part}.png"
        dst = block_tex / f"{TEXTURE_DST}_{dst_part}.png"
        if not src.exists():
            print("warn: missing texture", src.relative_to(ROOT))
            continue
        shutil.copy2(src, dst)
        print("copied texture", dst.relative_to(ROOT))


def menu_spec(kind: str, gtm_type: str) -> dict:
    if gtm_type in MULTI_INPUT_TYPES:
        return {"slots": 3, "data_slots": 4, "results": [2]}
    if kind == "generator":
        return {"slots": 1, "data_slots": 4, "results": []}
    if kind in {"storage", "transformer", "cable"}:
        return {"slots": 4, "data_slots": 4, "results": []}
    if kind == "utility":
        return {"slots": 2, "data_slots": 4, "results": []}
    return {"slots": 2, "data_slots": 4, "results": [1]}


def eu_recipes_for(gtm_type: str, machine_id: str) -> list[dict]:
    """Return ≥2 recipe payloads (not yet written) for a processor."""
    recipe_type = f"greglite:{gtm_type}"
    eu = 32
    duration = 100

    def one(ingredient, result_id, count=1, *, ingredients=None, dur=duration, energy=eu):
        payload = {
            "type": recipe_type,
            "result": {"id": result_id, "count": count},
            "duration": dur,
            "eu": energy,
        }
        if ingredients:
            payload["ingredients"] = ingredients
        else:
            payload["ingredient"] = ingredient
        return payload

    if gtm_type == "alloy_smelter":
        return [
            one(
                None,
                "greglite:bronze_ingot",
                2,
                ingredients=[
                    {"item": "minecraft:copper_ingot"},
                    {"item": "greglite:tin_ingot"},
                ],
            ),
            one(
                None,
                "greglite:bronze_ingot",
                2,
                ingredients=[
                    {"item": "greglite:copper_dust"},
                    {"item": "greglite:tin_dust"},
                ],
            ),
        ]
    if gtm_type == "macerator":
        a, b = MACERATE_PAIRS[0], MACERATE_PAIRS[1]
        return [
            one({"item": a[0]}, a[1]),
            one({"item": b[0]}, b[1]),
        ]
    if gtm_type == "compressor":
        a, b = COMPRESS_PAIRS[0], COMPRESS_PAIRS[1]
        return [
            one({"item": a[0]}, a[1]),
            one({"item": b[0]}, b[1]),
        ]
    if gtm_type == "electric_furnace":
        return [
            one({"item": "minecraft:iron_ore"}, "minecraft:iron_ingot"),
            one({"item": "minecraft:copper_ore"}, "minecraft:copper_ingot"),
        ]
    if gtm_type == "forge_hammer":
        return [
            one({"item": "minecraft:iron_ingot"}, "greglite:iron_plate", dur=120),
            one({"item": "minecraft:copper_ingot"}, "greglite:copper_plate", dur=120),
        ]
    if gtm_type == "bender":
        return [
            one({"item": "greglite:iron_plate"}, "greglite:iron_dust"),
            one({"item": "greglite:copper_plate"}, "greglite:copper_dust"),
        ]
    if gtm_type == "extruder":
        return [
            one({"item": "greglite:tin_ingot"}, "greglite:tin_rod"),
            one({"item": "minecraft:copper_ingot"}, "greglite:copper_rod"),
        ]
    if gtm_type == "wiremill":
        return [
            one({"item": "greglite:tin_plate"}, "greglite:tin_wire", count=2),
            one({"item": "greglite:copper_plate"}, "greglite:copper_wire", count=2),
        ]
    if gtm_type == "lathe":
        return [
            one({"item": "greglite:tin_ingot"}, "greglite:tin_rod", count=2),
            one({"item": "minecraft:copper_ingot"}, "greglite:copper_rod", count=2),
        ]
    if gtm_type == "assembler":
        return [
            one(
                None,
                "greglite:lv_battery",
                1,
                ingredients=[
                    {"item": "greglite:tin_wire"},
                    {"item": "minecraft:redstone"},
                ],
                dur=160,
                energy=48,
            ),
            one(
                None,
                "greglite:tin_cable_4x",
                2,
                ingredients=[
                    {"item": "greglite:tin_wire"},
                    {"item": "greglite:rubber"},
                ],
                dur=120,
            ),
        ]

    # Generic fallback — still ≥2 distinct EU recipes per processor type.
    idx = sum(ord(c) for c in gtm_type) % max(1, len(MACERATE_PAIRS) - 1)
    a, b = MACERATE_PAIRS[idx], MACERATE_PAIRS[idx + 1]
    return [
        one({"item": a[0]}, a[1], energy=24),
        one({"item": b[0]}, b[1], energy=28),
    ]


def write_steam_recipes() -> int:
    n = 0
    write(
        DATA / "recipe" / "bronze_from_copper_tin.json",
        {
            "type": "greglite:alloy_smelter",
            "ingredients": [
                {"item": "minecraft:copper_ingot"},
                {"item": "greglite:tin_ingot"},
            ],
            "result": {"id": "greglite:bronze_ingot", "count": 2},
            "duration": 200,
            "steam": 32,
        },
    )
    n += 1
    write(
        DATA / "recipe" / "bronze_from_dusts.json",
        {
            "type": "greglite:alloy_smelter",
            "ingredients": [
                {"item": "greglite:copper_dust"},
                {"item": "greglite:tin_dust"},
            ],
            "result": {"id": "greglite:bronze_ingot", "count": 2},
            "duration": 200,
            "steam": 32,
        },
    )
    n += 1
    for i, (inp, out) in enumerate(MACERATE_PAIRS):
        write(
            DATA / "recipe" / f"macerate_{i}.json",
            {
                "type": "greglite:macerator",
                "ingredient": {"item": inp},
                "result": {"id": out, "count": 1},
                "duration": 100,
                "steam": 16,
            },
        )
        n += 1
    for i, (inp, out) in enumerate(COMPRESS_PAIRS):
        write(
            DATA / "recipe" / f"compress_{i}.json",
            {
                "type": "greglite:compressor",
                "ingredient": {"item": inp},
                "result": {"id": out, "count": 1},
                "duration": 100,
                "steam": 16,
            },
        )
        n += 1
    write(
        DATA / "recipe" / "tin_ingot_craft.json",
        {
            "type": "minecraft:crafting_shapeless",
            "ingredients": [
                {"item": "minecraft:iron_ingot"},
                {"item": "minecraft:clay_ball"},
            ],
            "result": {"id": "greglite:tin_ingot", "count": 1},
        },
    )
    n += 1
    return n


def write_electric_item_crafts() -> int:
    crafts = [
        (
            "tin_wire_craft.json",
            ["greglite:tin_plate"],
            "greglite:tin_wire",
            2,
        ),
        (
            "copper_wire_craft.json",
            ["greglite:copper_plate"],
            "greglite:copper_wire",
            2,
        ),
        (
            "tin_rod_craft.json",
            ["greglite:tin_ingot"],
            "greglite:tin_rod",
            2,
        ),
        (
            "copper_rod_craft.json",
            ["minecraft:copper_ingot"],
            "greglite:copper_rod",
            2,
        ),
        (
            "rubber_craft.json",
            ["minecraft:slime_ball", "minecraft:charcoal"],
            "greglite:rubber",
            1,
        ),
    ]
    for fname, ingredients, result, count in crafts:
        write(
            DATA / "recipe" / fname,
            {
                "type": "minecraft:crafting_shapeless",
                "ingredients": [{"item": i} for i in ingredients],
                "result": {"id": result, "count": count},
            },
        )
    return len(crafts)


def main() -> None:
    catalog = load_catalog()
    lv = lv_machines(catalog)

    # Obsolete alloy_smelter paths
    for obsolete in [
        DATA / "horizon" / "block" / "alloy_smelter.json",
        DATA / "loot_table" / "blocks" / "alloy_smelter.json",
        ASSETS / "blockstates" / "alloy_smelter.json",
        ASSETS / "items" / "alloy_smelter.json",
        ASSETS / "models" / "block" / "alloy_smelter.json",
        ASSETS / "models" / "block" / "alloy_smelter_on.json",
        ASSETS / "models" / "item" / "alloy_smelter.json",
    ]:
        if obsolete.exists():
            obsolete.unlink()
            print("removed", obsolete.relative_to(ROOT))

    copy_lv_textures()

    all_items = STEAM_ITEMS + ELECTRIC_ITEMS
    for item in all_items:
        write_item(item)

    for block in STEAM_BLOCKS:
        write_orientable_block(block, shared_lv_texture=False)

    for machine in lv:
        write_orientable_block(machine["id"], shared_lv_texture=True)
        menu_id = MENU_ALIASES.get(machine["id"], machine["id"])
        write(
            DATA / "horizon" / "menu" / f"{menu_id}.json",
            menu_spec(machine["kind"], machine["gtm_type"]),
        )

    # Steam menus (unchanged ids)
    write(
        DATA / "horizon" / "menu" / "steam_boiler.json",
        {"slots": 1, "data_slots": 4, "results": []},
    )
    write(
        DATA / "horizon" / "menu" / "steam_alloy_smelter.json",
        {"slots": 3, "data_slots": 4, "results": [2]},
    )
    write(
        DATA / "horizon" / "menu" / "steam_macerator.json",
        {"slots": 2, "data_slots": 4, "results": [1]},
    )
    write(
        DATA / "horizon" / "menu" / "steam_compressor.json",
        {"slots": 2, "data_slots": 4, "results": [1]},
    )

    steam_recipes = write_steam_recipes()
    craft_recipes = write_electric_item_crafts()

    eu_recipe_count = 0
    processor_machines = [m for m in lv if m["kind"] == "processor"]
    for machine in processor_machines:
        gtm = machine["gtm_type"]
        mid = machine["id"]
        for idx, payload in enumerate(eu_recipes_for(gtm, mid)):
            fname = f"eu_{mid}_{idx}.json"
            write(DATA / "recipe" / fname, payload)
            eu_recipe_count += 1

    all_blocks = STEAM_BLOCKS + [m["id"] for m in lv]
    write(
        DATA / "horizon" / "creative_tab" / "greglite.json",
        {
            "title": "Greglite",
            "icon": "greglite:bronze_ingot",
            "items": [f"greglite:{b}" for b in all_blocks]
            + [f"greglite:{i}" for i in all_items],
        },
    )

    lang: dict[str, str] = {"itemGroup.greglite.greglite": "Greglite"}
    for block in STEAM_BLOCKS:
        lang[f"block.greglite.{block}"] = human_name(block)
    for machine in lv:
        lang[f"block.greglite.{machine['id']}"] = human_name(machine["id"])
    for item in all_items:
        lang[f"item.greglite.{item}"] = human_item(item)
    write(ASSETS / "lang" / "en_us.json", lang)

    write(
        ROOT / "data" / "minecraft" / "tags" / "block" / "mineable" / "pickaxe.json",
        {"replace": False, "values": [f"greglite:{b}" for b in all_blocks]},
    )

    total_recipes = steam_recipes + craft_recipes + eu_recipe_count
    print("---")
    print(f"machines (steam): {len(STEAM_BLOCKS)}")
    print(f"machines (lv electric): {len(lv)}")
    print(f"machines total blocks: {len(all_blocks)}")
    print(f"processors with EU recipes: {len(processor_machines)}")
    print(f"recipes steam: {steam_recipes}")
    print(f"recipes electric EU: {eu_recipe_count}")
    print(f"recipes crafts: {craft_recipes}")
    print(f"recipes total: {total_recipes}")


if __name__ == "__main__":
    main()