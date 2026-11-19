#!/usr/bin/env python3
"""M25: ensure materials_core forms exist + dense bath/centrifuge recipes."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXTRACT = ROOT / "tracker" / "gtm_extract" / "materials_core.json"
DATA = ROOT / "data" / "gtceu"
ASSETS = ROOT / "assets" / "gtceu"
ITEMS = DATA / "horizon" / "item"
RECIPE = DATA / "recipe"
TEX = ASSETS / "textures" / "item"

FORMS = ["dust", "plate", "rod", "wire", "screw", "gear", "foil", "ingot", "nugget"]
VANILLA_INGOT = {
    "iron": "minecraft:iron_ingot",
    "copper": "minecraft:copper_ingot",
    "gold": "minecraft:gold_ingot",
    "netherite": "minecraft:netherite_ingot",
}


def write(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def ensure_item(stem: str, form: str) -> None:
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


def item_id(mid: str, form: str) -> str | None:
    if form == "ingot" and mid in VANILLA_INGOT:
        return VANILLA_INGOT[mid]
    return f"gtceu:{mid}_{form}"


def exists_id(iid: str) -> bool:
    if iid.startswith("minecraft:"):
        return True
    stem = iid.split(":", 1)[1]
    return (ITEMS / f"{stem}.json").exists() or (
        DATA / "horizon" / "block" / f"{stem}.json"
    ).exists()


def main() -> None:
    mats = json.loads(EXTRACT.read_text(encoding="utf-8"))["materials"]
    created = 0
    for row in mats:
        mid = row["id"]
        for form in FORMS:
            if form == "ingot" and mid in VANILLA_INGOT:
                continue
            stem = f"{mid}_{form}"
            if not (ITEMS / f"{stem}.json").exists():
                ensure_item(stem, form)
                created += 1
    # Bath: crushed/dust wash → purified dust (use dust→dust as stand-in when no crushed)
    bath = 0
    for row in mats:
        mid = row["id"]
        dust = item_id(mid, "dust")
        if not dust or not exists_id(dust):
            continue
        # chemical bath: dust + (implicit water via single-input processor) → dust (washed)
        # Prefer plate → dust for bath immersion style when plate exists
        plate = item_id(mid, "plate")
        ingot = item_id(mid, "ingot")
        src = plate if plate and exists_id(plate) else ingot if ingot and exists_id(ingot) else dust
        body = {
            "type": "gtceu:chemical_bath",
            "ingredient": {"item": src},
            "result": {"id": dust, "count": 1},
            "duration": 100,
            "eu": 32,
            "min_voltage": 32,
        }
        write(RECIPE / f"m25_chemical_bath_{mid}.json", body)
        bath += 1
        # dual-input style if ingredients list supported
        if src != dust:
            write(
                RECIPE / f"m25_chemical_bath_ing_{mid}.json",
                {
                    "type": "gtceu:chemical_bath",
                    "ingredients": [src, dust],
                    "result": {"id": dust, "count": 2},
                    "duration": 120,
                    "eu": 48,
                },
            )
            bath += 1
    # Centrifuge: dust → nugget + dust leftovers (multi-out if supported) / single dust split
    cent = 0
    for row in mats:
        mid = row["id"]
        dust = item_id(mid, "dust")
        nugget = item_id(mid, "nugget")
        if not dust or not exists_id(dust):
            continue
        if nugget and exists_id(nugget):
            write(
                RECIPE / f"m25_centrifuge_{mid}.json",
                {
                    "type": "gtceu:centrifuge",
                    "ingredient": {"item": dust},
                    "result": {"id": nugget, "count": 9},
                    "duration": 80,
                    "eu": 32,
                },
            )
        else:
            write(
                RECIPE / f"m25_centrifuge_{mid}.json",
                {
                    "type": "gtceu:centrifuge",
                    "ingredient": {"item": dust},
                    "result": {"id": dust, "count": 1},
                    "duration": 60,
                    "eu": 24,
                },
            )
        cent += 1
        # thermal centrifuge twin
        write(
            RECIPE / f"m25_thermal_centrifuge_{mid}.json",
            {
                "type": "gtceu:thermal_centrifuge",
                "ingredient": {"item": dust},
                "result": {"id": dust, "count": 1},
                "duration": 100,
                "eu": 48,
            },
        )
        cent += 1
    # Lang stubs for new items (append missing keys)
    lang_path = ASSETS / "lang" / "en_us.json"
    lang = json.loads(lang_path.read_text(encoding="utf-8"))
    added_lang = 0
    for row in mats:
        mid = row["id"]
        for form in FORMS:
            if form == "ingot" and mid in VANILLA_INGOT:
                continue
            key = f"item.gtceu.{mid}_{form}"
            if key not in lang:
                title = f"{mid.replace('_', ' ').title()} {form.title()}"
                lang[key] = title
                added_lang += 1
    lang_path.write_text(json.dumps(lang, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    # Creative tab: append new item ids
    tab = DATA / "horizon" / "creative_tab" / "gtceu.json"
    if tab.exists():
        tobj = json.loads(tab.read_text(encoding="utf-8"))
        items = tobj.get("items") or tobj.get("entries") or []
        # support either list of strings or richer schema
        if items and isinstance(items[0], str):
            have = set(items)
            for row in mats:
                mid = row["id"]
                for form in FORMS:
                    if form == "ingot" and mid in VANILLA_INGOT:
                        continue
                    iid = f"gtceu:{mid}_{form}"
                    if iid not in have:
                        items.append(iid)
                        have.add(iid)
            if "items" in tobj:
                tobj["items"] = items
            else:
                tobj["entries"] = items
            write(tab, tobj)
    print(f"created_items={created} bath_recipes~={bath} centrifuge_recipes~={cent} lang+={added_lang}")


if __name__ == "__main__":
    main()
