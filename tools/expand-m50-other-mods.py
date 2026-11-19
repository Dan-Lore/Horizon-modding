#!/usr/bin/env python3
"""M50+: deepen Firmalife / Ad Astra / TFC recipe+item surface within Horizon pin."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


def write(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def ensure_simple_item(mod: str, stem: str, template: str = "minecraft:apple") -> bool:
    items = ROOT / "mods" / mod / "data" / mod / "horizon" / "item"
    blocks = ROOT / "mods" / mod / "data" / mod / "horizon" / "block"
    assets = ROOT / "mods" / mod / "assets" / mod
    # Horizon rejects a whole mod if horizon/item collides with a block's item:true
    if (blocks / f"{stem}.json").exists() or (items / f"{stem}.json").exists():
        return False
    write(items / f"{stem}.json", {"template": template})
    write(
        assets / "items" / f"{stem}.json",
        {"model": {"type": "minecraft:model", "model": f"{mod}:item/{stem}"}},
    )
    write(
        assets / "models" / "item" / f"{stem}.json",
        {"parent": "minecraft:item/generated", "textures": {"layer0": f"minecraft:item/{template.split(':',1)[1]}"}},
    )
    return True


def shapeless(mod: str, name: str, inp: str, out: str, count: int = 1) -> None:
    write(
        ROOT / "mods" / mod / "data" / mod / "recipe" / f"{name}.json",
        {
            "type": "minecraft:crafting_shapeless",
            "ingredients": [{"item": inp}],
            "result": {"id": out, "count": count},
        },
    )


def main() -> None:
    # Firmalife foods / drying chain breadth
    fl_items = [
        ("dried_apple", "minecraft:apple"),
        ("dried_carrot", "minecraft:carrot"),
        ("dried_potato", "minecraft:potato"),
        ("cheese_wheel", "minecraft:milk_bucket"),
        ("tofu", "minecraft:wheat"),
        ("soy_milk", "minecraft:wheat_seeds"),
        ("cured_meat", "minecraft:beef"),
        ("smoked_ham", "minecraft:porkchop"),
        ("chocolate", "minecraft:cocoa_beans"),
        ("pie_dough", "minecraft:egg"),
        ("flatbread", "minecraft:bread"),
        ("pickled_egg", "minecraft:egg"),
        ("honey_glazed_apple", "minecraft:apple"),
        ("compost", "minecraft:bone_meal"),
        ("yeast", "minecraft:sugar"),
    ]
    fl_n = 0
    for stem, tex in fl_items:
        if ensure_simple_item("firmalife", stem, tex):
            fl_n += 1
        shapeless("firmalife", f"m50_craft_{stem}", tex, f"firmalife:{stem}")
    # extra oven/vat style shapeless
    for name, inp, out in [
        ("m50_vat_milk", "minecraft:milk_bucket", "firmalife:cheese_wheel"),
        ("m50_oven_flatbread", "minecraft:wheat", "firmalife:flatbread"),
        ("m50_dry_carrot", "minecraft:carrot", "firmalife:dried_carrot"),
        ("m50_dry_potato", "minecraft:potato", "firmalife:dried_potato"),
        ("m50_smoke_ham", "minecraft:porkchop", "firmalife:smoked_ham"),
        ("m50_cure_beef", "minecraft:beef", "firmalife:cured_meat"),
    ]:
        shapeless("firmalife", name, inp, out)
    print(f"firmalife new_items={fl_n}")

    # Ad Astra overworld materials / plates (planets stay #1)
    aa_items = [
        ("desh_plate", "minecraft:iron_ingot"),
        ("ostrum_plate", "minecraft:iron_ingot"),
        ("calorite_plate", "minecraft:iron_ingot"),
        ("desh_nugget", "minecraft:iron_nugget"),
        ("ostrum_nugget", "minecraft:iron_nugget"),
        ("calorite_nugget", "minecraft:iron_nugget"),
        ("desh_plate_block", "minecraft:iron_block"),
        ("ostrum_plate_block", "minecraft:iron_block"),
        ("steel_plate", "minecraft:iron_ingot"),
        ("steel_nugget", "minecraft:iron_nugget"),
        ("engine_fan", "minecraft:iron_ingot"),
        ("engine_frame", "minecraft:iron_ingot"),
        ("oxygen_gear", "minecraft:iron_ingot"),
        ("gas_tank", "minecraft:bucket"),
        ("large_gas_tank", "minecraft:bucket"),
        ("space_painting", "minecraft:painting"),
        ("rocket_fin", "minecraft:iron_ingot"),
        ("rocket_nose_cone", "minecraft:iron_ingot"),
        ("tier_1_rover", "minecraft:minecart"),
        ("wheel", "minecraft:iron_ingot"),
    ]
    aa_n = 0
    horizon_aa = ROOT / "mods" / "adastra" / "data" / "adastra" / "horizon" / "item"

    def aa_base(stem: str) -> str:
        for key, iid in (
            ("desh", "adastra:desh_ingot"),
            ("ostrum", "adastra:ostrum_ingot"),
            ("calorite", "adastra:calorite_ingot"),
            ("steel", "adastra:steel_ingot"),
        ):
            if key in stem and (horizon_aa / f"{iid.split(':', 1)[1]}.json").exists():
                return iid
        return "minecraft:iron_ingot"

    for stem, tex in aa_items:
        if ensure_simple_item("adastra", stem, tex):
            aa_n += 1
        shapeless("adastra", f"m50_craft_{stem}", aa_base(stem), f"adastra:{stem}")
    print(f"adastra new_items={aa_n}")

    # TFC: more tool heads / sheets / double ingots as craftable surface
    tfc_items = [
        ("metal/sheet/copper", "minecraft:copper_ingot"),
        ("metal/sheet/bronze", "minecraft:copper_ingot"),
        ("metal/sheet/wrought_iron", "minecraft:iron_ingot"),
        ("metal/sheet/steel", "minecraft:iron_ingot"),
        ("metal/double_ingot/copper", "minecraft:copper_ingot"),
        ("metal/double_ingot/bronze", "minecraft:copper_ingot"),
        ("metal/double_ingot/wrought_iron", "minecraft:iron_ingot"),
        ("metal/double_ingot/steel", "minecraft:iron_ingot"),
        ("metal/rod/copper", "minecraft:copper_ingot"),
        ("metal/rod/bronze", "minecraft:copper_ingot"),
        ("metal/rod/wrought_iron", "minecraft:iron_ingot"),
        ("metal/rod/steel", "minecraft:iron_ingot"),
        ("powder/flux", "minecraft:bone_meal"),
        ("powder/coke", "minecraft:coal"),
        ("powder/charcoal", "minecraft:charcoal"),
        ("powder/graphite", "minecraft:coal"),
        ("food/wheat_bread", "minecraft:bread"),
        ("food/barley_bread", "minecraft:bread"),
        ("food/maize_bread", "minecraft:bread"),
        ("food/oat_bread", "minecraft:bread"),
        ("food/rye_bread", "minecraft:bread"),
        ("food/rice_bread", "minecraft:bread"),
        ("food/cooked_beef", "minecraft:cooked_beef"),
        ("food/cooked_pork", "minecraft:cooked_porkchop"),
        ("food/cooked_chicken", "minecraft:cooked_chicken"),
        ("food/cooked_mutton", "minecraft:cooked_mutton"),
        ("food/cooked_fish", "minecraft:cooked_cod"),
        ("bloom", "minecraft:iron_ingot"),
        ("raw_iron_bloom", "minecraft:raw_iron"),
        ("refined_iron_bloom", "minecraft:iron_ingot"),
    ]
    tfc_n = 0
    for stem, tex in tfc_items:
        # horizon item paths use flat names with underscores
        flat = stem.replace("/", "_")
        if ensure_simple_item("tfc", flat, tex):
            tfc_n += 1
        shapeless("tfc", f"m50_craft_{flat}", tex, f"tfc:{flat}")
    print(f"tfc new_items={tfc_n}")


if __name__ == "__main__":
    main()
