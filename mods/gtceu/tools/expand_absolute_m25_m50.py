#!/usr/bin/env python3
"""Absolute ladder: expand materials_colors forms + dense machine recipes + M50 chains."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
COLORS = ROOT / "tracker" / "gtm_extract" / "material_colors.json"
CORE = ROOT / "tracker" / "gtm_extract" / "materials_core.json"
MULTIS = ROOT / "tracker" / "gtm_extract" / "multiblocks.json"
DATA = ROOT / "data" / "gtceu"
ASSETS = ROOT / "assets" / "gtceu"
ITEMS = DATA / "horizon" / "item"
BLOCKS = DATA / "horizon" / "block"
RECIPE = DATA / "recipe"
TEX = ASSETS / "textures" / "item"
LANG = ASSETS / "lang" / "en_us.json"

FORMS_CORE = ["dust", "plate", "rod", "wire", "screw", "gear", "foil", "ingot", "nugget"]
FORMS_EXTRA = ["bolt", "ring", "rotor", "fine_wire", "long_rod", "spring"]
VANILLA_INGOT = {
    "iron": "minecraft:iron_ingot",
    "copper": "minecraft:copper_ingot",
    "gold": "minecraft:gold_ingot",
    "netherite": "minecraft:netherite_ingot",
}


def write(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def title(mid: str) -> str:
    return mid.replace("_", " ").title()


def ensure_item(stem: str, form: str) -> bool:
    if (ITEMS / f"{stem}.json").exists():
        return False
    tex_src = None
    for cand in (f"tin_{form}.png", f"iron_{form}.png", "tin_ingot.png", "tin_dust.png"):
        p = TEX / cand
        if p.exists():
            tex_src = p
            break
    dest_tex = TEX / f"{stem}.png"
    if tex_src and not dest_tex.exists():
        shutil.copy2(tex_src, dest_tex)
    write(ITEMS / f"{stem}.json", {"template": "minecraft:iron_ingot"})
    write(
        ASSETS / "items" / f"{stem}.json",
        {"model": {"type": "minecraft:model", "model": f"gtceu:item/{stem}"}},
    )
    layer = f"gtceu:item/{stem}" if dest_tex.exists() or tex_src else "gtceu:item/tin_ingot"
    write(
        ASSETS / "models" / "item" / f"{stem}.json",
        {"parent": "minecraft:item/generated", "textures": {"layer0": layer}},
    )
    return True


def exists_id(iid: str) -> bool:
    if iid.startswith("minecraft:"):
        return True
    stem = iid.split(":", 1)[1]
    return (ITEMS / f"{stem}.json").exists() or (BLOCKS / f"{stem}.json").exists()


def form_id(mid: str, form: str) -> str | None:
    if form == "ingot" and mid in VANILLA_INGOT:
        return VANILLA_INGOT[mid]
    iid = f"gtceu:{mid}_{form}"
    return iid if exists_id(iid) else None


def ensure_block(stem: str) -> bool:
    if (BLOCKS / f"{stem}.json").exists():
        return False
    write(
        BLOCKS / f"{stem}.json",
        {
            "template": "minecraft:iron_block",
            "properties": {"hardness": 5.0, "sounds": "minecraft:iron_block"},
            "item": True,
        },
    )
    write(
        ASSETS / "blockstates" / f"{stem}.json",
        {"variants": {"": {"model": f"gtceu:block/{stem}"}}},
    )
    write(
        ASSETS / "models" / "block" / f"{stem}.json",
        {
            "parent": "minecraft:block/cube_all",
            "textures": {"all": "gtceu:block/casings/solid/machine_casing_steel_solid"},
        },
    )
    write(
        ASSETS / "items" / f"{stem}.json",
        {"model": {"type": "minecraft:model", "model": f"gtceu:item/{stem}"}},
    )
    write(
        ASSETS / "models" / "item" / f"{stem}.json",
        {"parent": f"gtceu:block/{stem}"},
    )
    return True


def recipe(name: str, body: dict) -> None:
    write(RECIPE / name, body)


def main() -> None:
    colors = json.loads(COLORS.read_text(encoding="utf-8"))["colors"]
    mats = sorted(colors.keys())
    core_ids = {
        m["id"] for m in json.loads(CORE.read_text(encoding="utf-8"))["materials"]
    }
    lang = {}
    if LANG.exists():
        try:
            lang = json.loads(LANG.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            lang = {}

    created_items = 0
    for mid in mats:
        forms = list(FORMS_CORE)
        if mid in core_ids:
            forms += FORMS_EXTRA
        for form in forms:
            if form == "ingot" and mid in VANILLA_INGOT:
                continue
            stem = f"{mid}_{form}"
            if ensure_item(stem, form if form in FORMS_CORE else "rod"):
                created_items += 1
                lang.setdefault(f"item.gtceu.{stem}", f"{title(mid)} {title(form)}")

    # M50: ensure multiblock controller shells exist (content + JEI; structure where wired)
    created_blocks = 0
    controllers = json.loads(MULTIS.read_text(encoding="utf-8"))["controllers"]
    for row in controllers:
        cid = row["id"]
        stem = f"multi_{cid}" if not cid.startswith("multi_") else cid
        # Prefer unprefixed id if already present under another name
        if (BLOCKS / f"{cid}.json").exists() or (BLOCKS / f"{stem}.json").exists():
            continue
        if ensure_block(stem):
            created_blocks += 1
            lang.setdefault(f"block.gtceu.{stem}", f"{title(cid)} Controller")
            lang.setdefault(f"item.gtceu.{stem}", f"{title(cid)} Controller")

    # Dense recipes across all materials
    n_recipes = 0
    for mid in mats:
        dust = form_id(mid, "dust")
        plate = form_id(mid, "plate")
        ingot = form_id(mid, "ingot")
        rod = form_id(mid, "rod")
        wire = form_id(mid, "wire")
        nugget = form_id(mid, "nugget")
        gear = form_id(mid, "gear")
        foil = form_id(mid, "foil")
        screw = form_id(mid, "screw")
        bolt = form_id(mid, "bolt")
        ring = form_id(mid, "ring")

        if dust:
            recipe(
                f"abs_bath_{mid}.json",
                {
                    "type": "gtceu:chemical_bath",
                    "ingredient": {"item": dust},
                    "result": {"id": dust, "count": 1},
                    "duration": 100,
                    "eu": 32,
                    "min_voltage": 32,
                },
            )
            n_recipes += 1
            recipe(
                f"abs_centrifuge_{mid}.json",
                {
                    "type": "gtceu:centrifuge",
                    "ingredient": {"item": dust},
                    "results": [{"id": dust, "count": 1}]
                    + ([{"id": nugget, "count": 1}] if nugget else []),
                    "duration": 120,
                    "eu": 48,
                    "min_voltage": 32,
                },
            )
            n_recipes += 1
            recipe(
                f"abs_ore_washer_{mid}.json",
                {
                    "type": "gtceu:ore_washer",
                    "ingredient": {"item": dust},
                    "result": {"id": dust, "count": 1},
                    "duration": 80,
                    "eu": 24,
                    "min_voltage": 32,
                },
            )
            n_recipes += 1
            recipe(
                f"abs_electrolyzer_{mid}.json",
                {
                    "type": "gtceu:electrolyzer",
                    "ingredient": {"item": dust},
                    "result": {"id": dust, "count": 1},
                    "duration": 160,
                    "eu": 64,
                    "min_voltage": 32,
                },
            )
            n_recipes += 1

        if dust and ingot:
            for mt, eu in (
                ("macerator", 16),
                ("forge_hammer", 16),
                ("electric_furnace", 48),
                ("arc_furnace", 64),
                ("alloy_smelter", 32),
            ):
                inp, out = (ingot, dust) if mt in ("macerator", "forge_hammer") else (dust, ingot)
                recipe(
                    f"abs_{mt}_{mid}.json",
                    {
                        "type": f"gtceu:{mt}",
                        "ingredient": {"item": inp},
                        "result": {"id": out, "count": 1},
                        "duration": 80,
                        "eu": eu,
                        "min_voltage": 32,
                    },
                )
                n_recipes += 1

        if ingot and plate:
            for mt in ("compressor", "bender", "forming_press", "forge_hammer"):
                recipe(
                    f"abs_{mt}_plate_{mid}.json",
                    {
                        "type": f"gtceu:{mt}",
                        "ingredient": {"item": ingot},
                        "result": {"id": plate, "count": 1},
                        "duration": 80,
                        "eu": 32,
                        "min_voltage": 32,
                    },
                )
                n_recipes += 1

        if ingot and rod:
            for mt in ("lathe", "extruder"):
                recipe(
                    f"abs_{mt}_rod_{mid}.json",
                    {
                        "type": f"gtceu:{mt}",
                        "ingredient": {"item": ingot},
                        "result": {"id": rod, "count": 1},
                        "duration": 80,
                        "eu": 32,
                        "min_voltage": 32,
                    },
                )
                n_recipes += 1

        if plate and foil:
            recipe(
                f"abs_bender_foil_{mid}.json",
                {
                    "type": "gtceu:bender",
                    "ingredient": {"item": plate},
                    "result": {"id": foil, "count": 4},
                    "duration": 60,
                    "eu": 24,
                    "min_voltage": 32,
                },
            )
            n_recipes += 1

        if ingot and wire:
            recipe(
                f"abs_wiremill_{mid}.json",
                {
                    "type": "gtceu:wiremill",
                    "ingredient": {"item": ingot},
                    "result": {"id": wire, "count": 2},
                    "duration": 80,
                    "eu": 32,
                    "min_voltage": 32,
                },
            )
            n_recipes += 1

        if plate and gear:
            recipe(
                f"abs_extruder_gear_{mid}.json",
                {
                    "type": "gtceu:extruder",
                    "ingredient": {"item": plate},
                    "result": {"id": gear, "count": 1},
                    "duration": 100,
                    "eu": 48,
                    "min_voltage": 32,
                },
            )
            n_recipes += 1

        if rod and screw:
            recipe(
                f"abs_lathe_screw_{mid}.json",
                {
                    "type": "gtceu:lathe",
                    "ingredient": {"item": rod},
                    "result": {"id": screw, "count": 1},
                    "duration": 60,
                    "eu": 16,
                    "min_voltage": 32,
                },
            )
            n_recipes += 1

        # M50 chem / fluid-adjacent (item stand-ins until fluid tanks are universal)
        if dust and plate:
            recipe(
                f"abs_chem_reactor_{mid}.json",
                {
                    "type": "gtceu:chemical_reactor",
                    "ingredients": [dust, plate],
                    "result": {"id": plate, "count": 1},
                    "duration": 160,
                    "eu": 64,
                    "min_voltage": 32,
                },
            )
            n_recipes += 1
            recipe(
                f"abs_distillery_{mid}.json",
                {
                    "type": "gtceu:distillery",
                    "ingredient": {"item": dust},
                    "result": {"id": plate, "count": 1},
                    "duration": 140,
                    "eu": 48,
                    "min_voltage": 32,
                },
            )
            n_recipes += 1
            recipe(
                f"abs_mixer_{mid}.json",
                {
                    "type": "gtceu:mixer",
                    "ingredients": [dust, plate],
                    "result": {"id": dust, "count": 2},
                    "duration": 100,
                    "eu": 32,
                    "min_voltage": 32,
                },
            )
            n_recipes += 1

        if bolt and rod:
            recipe(
                f"abs_cutter_bolt_{mid}.json",
                {
                    "type": "gtceu:cutter",
                    "ingredient": {"item": rod},
                    "result": {"id": bolt, "count": 2},
                    "duration": 60,
                    "eu": 16,
                    "min_voltage": 32,
                },
            )
            n_recipes += 1
        if ring and rod:
            recipe(
                f"abs_bender_ring_{mid}.json",
                {
                    "type": "gtceu:bender",
                    "ingredient": {"item": rod},
                    "result": {"id": ring, "count": 1},
                    "duration": 80,
                    "eu": 24,
                    "min_voltage": 32,
                },
            )
            n_recipes += 1

    LANG.parent.mkdir(parents=True, exist_ok=True)
    LANG.write_text(json.dumps(lang, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    items_now = len(list((ASSETS / "items").glob("*.json")))
    recipes_now = len(list(RECIPE.glob("*.json")))
    print(
        f"mats={len(mats)} created_items={created_items} created_blocks={created_blocks} "
        f"recipes_written~={n_recipes} items_now={items_now} recipes_now={recipes_now}"
    )


if __name__ == "__main__":
    main()
