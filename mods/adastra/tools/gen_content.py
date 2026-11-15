#!/usr/bin/env python3
"""Generate Ad Astra Horizon content, tables, and machine spec include.

    python3 mods/adastra/tools/gen_content.py

Placeholder textures are solid 16×16 PNGs. No Mojang assets are copied.
"""

from __future__ import annotations

import json
import shutil
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "adastra"
DATA = ROOT / "data" / "adastra"
TABLES = ROOT / "tables"

METALS = [
    ("steel", (120, 130, 140)),
    ("desh", (196, 120, 64)),
    ("ostrum", (160, 72, 96)),
    ("calorite", (200, 64, 72)),
]
METAL_FORMS = ["ingot", "nugget", "plate"]

PLANET_BLOCKS = [
    ("moon_stone", (180, 180, 190)),
    ("moon_cobblestone", (150, 150, 160)),
    ("mars_stone", (160, 90, 70)),
    ("mars_cobblestone", (130, 70, 55)),
]

EXTRA_ITEMS = [
    ("cheese", (230, 210, 90)),
    ("flag", (40, 80, 180)),
    ("oxygen_tank_empty", (80, 120, 160)),
    ("oxygen_tank", (60, 180, 220)),
    ("space_helmet", (200, 200, 210)),
    ("space_suit", (190, 190, 200)),
    ("space_pants", (180, 180, 190)),
    ("space_boots", (170, 170, 180)),
    ("oil", (40, 40, 40)),
    ("rocket_fuel", (80, 200, 100)),
    ("rocket_t1", (220, 220, 230)),
    ("ice_shard", (180, 220, 240)),
]

# kind: generator | processor | loader | distributor | vacuum | storage | marker
MACHINES = [
    {"id": "coal_generator", "kind": "generator", "fuel": True, "inputs": 1, "recipe": None, "eu_cap": 16000, "rate": 40},
    {"id": "solar_panel", "kind": "solar", "fuel": False, "inputs": 0, "recipe": None, "eu_cap": 8000, "rate": 8},
    {"id": "compressor", "kind": "processor", "fuel": False, "inputs": 1, "recipe": "compressor", "eu_cap": 16000, "rate": 32},
    {"id": "oxygen_loader", "kind": "loader", "fuel": False, "inputs": 1, "recipe": "oxygen_loader", "eu_cap": 16000, "rate": 16},
    {"id": "fuel_refinery", "kind": "processor", "fuel": False, "inputs": 1, "recipe": "fuel_refinery", "eu_cap": 16000, "rate": 24},
    {"id": "nasa_workbench", "kind": "storage", "fuel": False, "inputs": 9, "recipe": None, "eu_cap": 0, "rate": 0},
    {"id": "oxygen_distributor", "kind": "distributor", "fuel": False, "inputs": 1, "recipe": None, "eu_cap": 16000, "rate": 8},
    {"id": "cryo_freezer", "kind": "processor", "fuel": False, "inputs": 1, "recipe": "cryo_freezer", "eu_cap": 16000, "rate": 16},
    {"id": "vacuum_marker", "kind": "vacuum", "fuel": False, "inputs": 0, "recipe": None, "eu_cap": 0, "rate": 0},
    {"id": "launch_pad", "kind": "marker", "fuel": False, "inputs": 0, "recipe": None, "eu_cap": 0, "rate": 0},
]


def write_json(path: Path, body: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(body, indent=2) + "\n", encoding="utf-8")


def png(path: Path, rgb: tuple[int, int, int]) -> None:
    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    raw = b"".join(b"\x00" + bytes(rgb) * 16 for _ in range(16))
    ihdr = struct.pack(">IIBBBBB", 16, 16, 8, 2, 0, 0, 0)
    data = (
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", zlib.compress(raw, 9))
        + chunk(b"IEND", b"")
    )
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(data)


def color_for(key: str, bias: tuple[int, int, int] = (80, 80, 80)) -> tuple[int, int, int]:
    h = zlib.crc32(key.encode()) & 0xFFFFFFFF
    return tuple((bias[i] + ((h >> (8 * i)) & 255)) // 2 for i in range(3))  # type: ignore[return-value]


def title(name: str) -> str:
    return " ".join(part.capitalize() for part in name.split("_"))


def block_files(name: str, rgb: tuple[int, int, int], furnace: bool, hardness: float, sounds: str) -> None:
    template = "minecraft:furnace" if furnace else "minecraft:iron_block"
    write_json(
        DATA / "horizon" / "block" / f"{name}.json",
        {
            "template": template,
            "properties": {"hardness": hardness, "sounds": sounds},
            "item": True,
        },
    )
    model = {"parent": "minecraft:block/cube_all", "textures": {"all": f"adastra:block/{name}"}}
    write_json(ASSETS / "models" / "block" / f"{name}.json", model)
    write_json(ASSETS / "models" / "item" / f"{name}.json", {"parent": f"adastra:block/{name}"})
    if furnace:
        variants = {}
        for facing, rot in (("north", None), ("south", 180), ("west", 270), ("east", 90)):
            for lit in ("false", "true"):
                entry: dict = {"model": f"adastra:block/{name}"}
                if rot is not None:
                    entry["y"] = rot
                variants[f"facing={facing},lit={lit}"] = entry
        write_json(ASSETS / "blockstates" / f"{name}.json", {"variants": variants})
    else:
        write_json(
            ASSETS / "blockstates" / f"{name}.json",
            {"variants": {"": {"model": f"adastra:block/{name}"}}},
        )
    png(ASSETS / "textures" / "block" / f"{name}.png", rgb)
    write_json(
        DATA / "loot_table" / "blocks" / f"{name}.json",
        {
            "type": "minecraft:block",
            "pools": [
                {
                    "rolls": 1,
                    "entries": [{"type": "minecraft:item", "name": f"adastra:{name}"}],
                    "conditions": [{"condition": "minecraft:survives_explosion"}],
                }
            ],
        },
    )


def item_files(name: str, rgb: tuple[int, int, int], template: str = "minecraft:iron_ingot") -> None:
    write_json(DATA / "horizon" / "item" / f"{name}.json", {"template": template})
    write_json(
        ASSETS / "models" / "item" / f"{name}.json",
        {"parent": "minecraft:item/generated", "textures": {"layer0": f"adastra:item/{name}"}},
    )
    png(ASSETS / "textures" / "item" / f"{name}.png", rgb)


def menu(name: str, slots: int, results: list[int]) -> None:
    write_json(
        DATA / "horizon" / "menu" / f"{name}.json",
        {"slots": slots, "data_slots": 4, "results": results},
    )


def shapeless(recipe_id: str, ingredients: list[str], result: str, count: int = 1) -> None:
    write_json(
        DATA / "recipe" / f"{recipe_id}.json",
        {
            "type": "minecraft:crafting_shapeless",
            "ingredients": [{"item": item} for item in ingredients],
            "result": {"id": result, "count": count},
        },
    )


def machine_recipe(kind: str, recipe_id: str, ingredient: str, result: str, duration: int, fe: int) -> None:
    write_json(
        DATA / "recipe" / f"{recipe_id}.json",
        {
            "type": f"adastra:{kind}",
            "ingredient": ingredient,
            "result": {"id": result, "count": 1},
            "duration": duration,
            "fe": fe,
        },
    )


def output_index(machine: dict) -> int | None:
    if machine["kind"] in {"storage", "vacuum", "marker", "solar"} and machine["inputs"] == 0:
        if machine["kind"] == "storage":
            return None
        return None
    if machine["kind"] == "generator":
        return None
    if machine["kind"] == "distributor":
        return None
    if machine["kind"] == "solar":
        return None
    start = 1 if machine["fuel"] else 0
    return start + machine["inputs"]


def write_specs(machines: list[dict]) -> None:
    lines = ["[\n"]
    for machine in machines:
        mid = machine["id"]
        kind = machine["kind"]
        rust_kind = {
            "generator": "Generator",
            "solar": "Solar",
            "processor": "Processor",
            "loader": "Loader",
            "distributor": "Distributor",
            "storage": "Storage",
            "vacuum": "Vacuum",
            "marker": "Marker",
        }[kind]
        out = output_index(machine)
        recipe = f'Some("adastra:{machine["recipe"]}")' if machine.get("recipe") else "None"
        out_s = "None" if out is None else f"Some({out})"
        lines.append(
            "    Spec {\n"
            f'        id: "adastra:{mid}",\n'
            f"        kind: Kind::{rust_kind},\n"
            f"        fuel: {str(machine['fuel']).lower()},\n"
            f"        inputs: {machine['inputs']},\n"
            f"        output: {out_s},\n"
            f"        recipe_type: {recipe},\n"
            f"        fe_cap: {machine['eu_cap']},\n"
            f"        fe_rate: {machine['rate']},\n"
            "    },\n"
        )
    lines.append("]\n")
    path = ROOT / "api" / "src" / "specs.inc.rs"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text("".join(lines), encoding="utf-8")


def write_tables(machines: list[dict]) -> None:
    TABLES.mkdir(parents=True, exist_ok=True)
    write_json(TABLES / "machines.json", machines)
    write_json(
        TABLES / "materials.json",
        {
            "metals": [m[0] for m in METALS],
            "forms": METAL_FORMS,
            "planet_blocks": [b[0] for b in PLANET_BLOCKS],
        },
    )
    write_json(
        TABLES / "oxygen.json",
        {
            "tank_capacity": 100,
            "drain_per_second": 1,
            "vacuum_radius": 4,
            "distributor_radius": 6,
            "suit_pieces": [
                "adastra:space_helmet",
                "adastra:space_suit",
                "adastra:space_pants",
                "adastra:space_boots",
            ],
        },
    )


def reset_generated() -> None:
    for path in (ASSETS, DATA):
        if path.exists():
            shutil.rmtree(path)
    ASSETS.mkdir(parents=True)
    DATA.mkdir(parents=True)


def main() -> None:
    reset_generated()
    write_tables(MACHINES)
    write_specs(MACHINES)
    lang: dict[str, str] = {}

    for metal, rgb in METALS:
        for form in METAL_FORMS:
            name = f"{metal}_{form}"
            item_files(name, rgb if form != "plate" else tuple(max(0, c - 20) for c in rgb))
            lang[f"item.adastra.{name}"] = f"{title(metal)} {title(form)}"
        shapeless(
            f"{metal}_nuggets_from_ingot",
            [f"adastra:{metal}_ingot"],
            f"adastra:{metal}_nugget",
            9,
        )
        shapeless(
            f"{metal}_ingot_from_nuggets",
            [f"adastra:{metal}_nugget"] * 9,
            f"adastra:{metal}_ingot",
            1,
        )

    for name, rgb in PLANET_BLOCKS:
        block_files(name, rgb, furnace=False, hardness=1.5, sounds="minecraft:stone")
        lang[f"block.adastra.{name}"] = title(name)

    shapeless("moon_cobble_from_stone", ["adastra:moon_stone"], "adastra:moon_cobblestone")
    shapeless("mars_cobble_from_stone", ["adastra:mars_stone"], "adastra:mars_cobblestone")

    for name, rgb in EXTRA_ITEMS:
        item_files(name, rgb)
        lang[f"item.adastra.{name}"] = title(name)

    for machine in MACHINES:
        mid = machine["id"]
        furnace = machine["kind"] not in {"vacuum", "marker", "storage", "solar"}
        # solar and storage still use furnace-ish for lit where useful
        use_furnace = machine["kind"] in {
            "generator",
            "processor",
            "loader",
            "distributor",
            "solar",
        }
        rgb = color_for(mid, (60, 90, 120))
        block_files(mid, rgb, furnace=use_furnace, hardness=3.5, sounds="minecraft:metal")
        lang[f"block.adastra.{mid}"] = title(mid)
        if machine["kind"] == "storage":
            menu(mid, 9, [])
        elif machine["kind"] in {"generator", "distributor"}:
            menu(mid, 1, [])
        elif machine["kind"] in {"vacuum", "marker", "solar"}:
            pass
        else:
            out = output_index(machine)
            slots = (out + 1) if out is not None else machine["inputs"]
            results = [out] if out is not None else []
            menu(mid, slots, results)

    # Processor recipes
    machine_recipe("compressor", "compress_desh", "adastra:desh_ingot", "adastra:desh_plate", 100, 32)
    machine_recipe("compressor", "compress_steel", "adastra:steel_ingot", "adastra:steel_plate", 100, 32)
    machine_recipe("compressor", "compress_ostrum", "adastra:ostrum_ingot", "adastra:ostrum_plate", 120, 40)
    machine_recipe("compressor", "compress_calorite", "adastra:calorite_ingot", "adastra:calorite_plate", 140, 48)

    machine_recipe(
        "oxygen_loader",
        "load_oxygen",
        "adastra:oxygen_tank_empty",
        "adastra:oxygen_tank",
        80,
        16,
    )

    machine_recipe("fuel_refinery", "refine_oil", "adastra:oil", "adastra:rocket_fuel", 160, 24)

    machine_recipe("cryo_freezer", "freeze_ice", "minecraft:ice", "adastra:ice_shard", 100, 16)
    machine_recipe("cryo_freezer", "freeze_blue_ice", "minecraft:blue_ice", "adastra:ice_shard", 60, 12)

    # Rocket craft (shapeless stand-in for NASA workbench)
    shapeless(
        "rocket_t1",
        [
            "adastra:steel_plate",
            "adastra:steel_plate",
            "adastra:desh_plate",
            "adastra:rocket_fuel",
            "adastra:rocket_fuel",
            "adastra:ostrum_ingot",
        ],
        "adastra:rocket_t1",
    )
    shapeless(
        "oxygen_tank_empty",
        ["adastra:steel_plate", "adastra:steel_nugget"],
        "adastra:oxygen_tank_empty",
    )
    shapeless(
        "space_helmet",
        ["adastra:steel_plate", "adastra:steel_plate", "minecraft:glass_pane"],
        "adastra:space_helmet",
    )
    shapeless(
        "space_suit",
        ["adastra:steel_plate", "adastra:desh_ingot", "adastra:steel_plate"],
        "adastra:space_suit",
    )
    shapeless(
        "space_pants",
        ["adastra:steel_plate", "adastra:steel_ingot", "adastra:steel_plate"],
        "adastra:space_pants",
    )
    shapeless(
        "space_boots",
        ["adastra:steel_nugget", "adastra:steel_plate", "adastra:steel_nugget"],
        "adastra:space_boots",
    )

    write_json(
        DATA / "horizon" / "creative_tab" / "adastra.json",
        {
            "title": "Ad Astra Horizon",
            "icon": "adastra:rocket_t1",
            "items": (
                [f"adastra:{m}_{f}" for m, _ in METALS for f in METAL_FORMS]
                + [f"adastra:{b}" for b, _ in PLANET_BLOCKS]
                + [f"adastra:{i}" for i, _ in EXTRA_ITEMS]
                + [f"adastra:{m['id']}" for m in MACHINES]
            ),
        },
    )
    write_json(ASSETS / "lang" / "en_us.json", lang)
    print(f"generated adastra content under {ROOT}")


if __name__ == "__main__":
    main()
