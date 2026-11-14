"""Bake GTM LGPL textures into greglite assets (materials + machines + cables)."""
from __future__ import annotations

import json
import shutil
import urllib.request
from io import BytesIO
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "assets" / "greglite" / "textures"
ASSETS = ROOT / "assets" / "greglite"
DATA = ROOT / "data" / "greglite"
EXTRACT = ROOT / "tracker" / "gtm_extract"
BASE = "https://raw.githubusercontent.com/GregTechCEu/GregTech-Modern/1.20.1/src/main/resources/assets/gtceu/textures"

FORMS = ["ingot", "dust", "plate", "rod", "wire", "screw", "gear", "foil"]
# GTM material set used for most metals
MAT_SET = "dull"

TIER_CASING = {
    "lv": "block/casings/voltage/lv",
    "mv": "block/casings/voltage/mv",
    "hv": "block/casings/voltage/hv",
    "ev": "block/casings/voltage/ev",
    "iv": "block/casings/voltage/iv",
    "luv": "block/casings/voltage/luv",
    "zpm": "block/casings/voltage/zpm",
    "uv": "block/casings/voltage/uv",
}

# fallback colors for materials missing from extract
FALLBACK_RGB = {
    "iron": 0xC8C8C8,
    "copper": 0xE77C56,
    "tin": 0xDCE1DE,
    "bronze": 0xFF8033,
    "steel": 0x808080,
    "gold": 0xFFE650,
    "silver": 0xDCDCFF,
    "lead": 0x8C648C,
    "nickel": 0xC8C8F0,
    "zinc": 0xFAF0DE,
    "aluminium": 0x80C8F0,
    "aluminum": 0x80C8F0,
    "invar": 0xB4B478,
    "brass": 0xFFB400,
    "electrum": 0xFFFF64,
    "stainless_steel": 0xC8C8DC,
    "titanium": 0xDCA0F0,
    "tungsten": 0x323232,
    "platinum": 0xFFFFC8,
    "iridium": 0xFFFFFF,
    "osmium": 0x3232FF,
    "naquadah": 0x323232,
    "neutronium": 0xFAFAFA,
    "rubber": 0x141414,
    "redstone": 0xC80000,
    "coal": 0x464646,
    "diamond": 0xC8FFFF,
    "emerald": 0x50FF50,
    "glass": 0xFAFAFA,
    "annealed_copper": 0xFF7814,
    "cupronickel": 0xE77C56,
    "kanthal": 0xC2D2DF,
    "nichrome": 0xCDCEF6,
    "rtm_alloy": 0x6464A0,
    "hssg": 0xADBBF0,
    "hsss": 0xAE801D,
    "vanadium_gallium": 0x80808C,
    "yttrium_barium_cuprate": 0x504600,
    "niobium_titanium": 0x1D1D29,
    "trinium": 0xC8C8D2,
}


def fetch(rel: str) -> Image.Image:
    url = f"{BASE}/{rel}"
    with urllib.request.urlopen(url, timeout=60) as r:
        return Image.open(BytesIO(r.read())).convert("RGBA")


def try_fetch(rel: str) -> Image.Image | None:
    try:
        return fetch(rel)
    except Exception as e:
        print("skip", rel, e)
        return None


def tint(base: Image.Image, overlay: Image.Image | None, rgb: int) -> Image.Image:
    r = (rgb >> 16) & 0xFF
    g = (rgb >> 8) & 0xFF
    b = rgb & 0xFF
    img = base.copy()
    px = img.load()
    for y in range(img.height):
        for x in range(img.width):
            pr, pg, pb, pa = px[x, y]
            if pa == 0:
                continue
            px[x, y] = ((pr * r) // 255, (pg * g) // 255, (pb * b) // 255, pa)
    if overlay is not None:
        ov = overlay if overlay.size == img.size else overlay.resize(img.size, Image.NEAREST)
        img.alpha_composite(ov)
    return img


def compose(base: Image.Image, overlay: Image.Image | None) -> Image.Image:
    out = base.copy()
    if overlay is not None:
        ov = overlay if overlay.size == out.size else overlay.resize(out.size, Image.NEAREST)
        out.alpha_composite(ov)
    return out


def save(img: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def bake_materials() -> int:
    colors = {}
    cp = EXTRACT / "material_colors.json"
    if cp.exists():
        colors = json.loads(cp.read_text(encoding="utf-8")).get("colors", {})
    mats = json.loads((EXTRACT / "materials_core.json").read_text(encoding="utf-8"))["materials"]
    form_bases: dict[str, tuple[Image.Image, Image.Image | None]] = {}
    for form in FORMS:
        form_file = {
            "wire": "wire_fine",
        }.get(form, form)
        base = try_fetch(f"item/material_sets/{MAT_SET}/{form_file}.png")
        if base is None:
            continue
        overlay = try_fetch(f"item/material_sets/{MAT_SET}/{form_file}_overlay.png")
        form_bases[form] = (base, overlay)
        save(base, TEX / "item" / f"_form_{form}.png")

    n = 0
    for m in mats:
        mid = m["id"]
        rgb = colors.get(mid, FALLBACK_RGB.get(mid, 0xAAAAAA))
        if isinstance(rgb, str):
            rgb = int(rgb, 16) if rgb.startswith("0x") else int(rgb)
        for form in FORMS:
            if form not in form_bases:
                continue
            # skip vanilla-covered ingots
            if form == "ingot" and mid in ("iron", "copper", "gold", "netherite"):
                continue
            base, overlay = form_bases[form]
            save(tint(base, overlay, rgb), TEX / "item" / f"{mid}_{form}.png")
            write_json(
                ASSETS / "models" / "item" / f"{mid}_{form}.json",
                {
                    "parent": "minecraft:item/generated",
                    "textures": {"layer0": f"greglite:item/{mid}_{form}"},
                },
            )
            write_json(
                ASSETS / "items" / f"{mid}_{form}.json",
                {
                    "model": {
                        "type": "minecraft:model",
                        "model": f"greglite:item/{mid}_{form}",
                    }
                },
            )
            n += 1
    return n


def bake_machines() -> int:
    machines = json.loads((EXTRACT / "electric_machine_types.json").read_text(encoding="utf-8"))[
        "machines"
    ]
    steam_casing_side = try_fetch("block/casings/steam/bronze/side.png")
    steam_casing_top = try_fetch("block/casings/steam/bronze/top.png")
    steam_casing_bottom = try_fetch("block/casings/steam/bronze/bottom.png")
    n = 0
    # cache casings
    casings: dict[str, tuple[Image.Image, Image.Image, Image.Image]] = {}
    for tier, prefix in TIER_CASING.items():
        side = try_fetch(f"{prefix}/side.png") or try_fetch("block/casings/voltage/lv/side.png")
        top = try_fetch(f"{prefix}/top.png") or side
        bottom = try_fetch(f"{prefix}/bottom.png") or top
        if side is None:
            continue
        casings[tier] = (side, top, bottom)

    # machine overlays keyed by gtm folder name
    overlay_cache: dict[str, tuple[Image.Image | None, Image.Image | None]] = {}

    def overlays_for(mtype: str) -> tuple[Image.Image | None, Image.Image | None]:
        if mtype in overlay_cache:
            return overlay_cache[mtype]
        # rock_crusher uses rock_breaker overlays in GTM
        folder = {
            "rock_crusher": "rock_crusher",
            "electric_furnace": "electric_furnace",
            "spooler": "spooling",
        }.get(mtype, mtype)
        front = try_fetch(f"block/machines/{folder}/overlay_front.png")
        front_on = try_fetch(f"block/machines/{folder}/overlay_front_active.png") or front
        overlay_cache[mtype] = (front, front_on)
        return front, front_on

    for m in machines:
        mtype = m["id"]
        front, front_on = overlays_for(mtype)
        for tier, (side, top, bottom) in casings.items():
            block = f"{tier}_{mtype}"
            save(compose(side, front), TEX / "block" / f"{block}_front.png")
            save(compose(side, front_on), TEX / "block" / f"{block}_front_on.png")
            save(side.copy(), TEX / "block" / f"{block}_side.png")
            save(top.copy(), TEX / "block" / f"{block}_top.png")
            save(bottom.copy(), TEX / "block" / f"{block}_bottom.png")
            # point models at own textures
            for suf, front_key in (("", "front"), ("_on", "front_on")):
                write_json(
                    ASSETS / "models" / "block" / f"{block}{suf}.json",
                    {
                        "parent": "minecraft:block/orientable",
                        "textures": {
                            "top": f"greglite:block/{block}_top",
                            "front": f"greglite:block/{block}_{front_key}",
                            "side": f"greglite:block/{block}_side",
                            "bottom": f"greglite:block/{block}_bottom",
                            "particle": f"greglite:block/{block}_side",
                        },
                    },
                )
            write_json(
                ASSETS / "models" / "item" / f"{block}.json",
                {"parent": f"greglite:block/{block}"},
            )
            n += 1

    # generators
    gens = json.loads((EXTRACT / "generators.json").read_text(encoding="utf-8"))["generators"]
    for g in gens:
        gid = g["id"]
        # GTM paths: block/generators/combustion/overlay_front.png etc.
        folder = {
            "combustion": "generators/combustion",
            "gas_turbine": "generators/gas_turbine",
            "steam_turbine": "generators/steam",
        }.get(gid, f"generators/{gid}")
        front = (
            try_fetch(f"block/{folder}/overlay_front.png")
            or try_fetch(f"block/generators/{gid}/overlay_front.png")
            or try_fetch("block/machines/macerator/overlay_front.png")
        )
        front_on = (
            try_fetch(f"block/{folder}/overlay_front_active.png")
            or try_fetch(f"block/generators/{gid}/overlay_front_active.png")
            or front
        )
        for tier in ("lv", "mv", "hv"):
            if tier not in casings:
                continue
            side, top, bottom = casings[tier]
            block = f"{tier}_{gid}"
            save(compose(side, front), TEX / "block" / f"{block}_front.png")
            save(compose(side, front_on), TEX / "block" / f"{block}_front_on.png")
            save(side.copy(), TEX / "block" / f"{block}_side.png")
            save(top.copy(), TEX / "block" / f"{block}_top.png")
            save(bottom.copy(), TEX / "block" / f"{block}_bottom.png")
            for suf, front_key in (("", "front"), ("_on", "front_on")):
                write_json(
                    ASSETS / "models" / "block" / f"{block}{suf}.json",
                    {
                        "parent": "minecraft:block/orientable",
                        "textures": {
                            "top": f"greglite:block/{block}_top",
                            "front": f"greglite:block/{block}_{front_key}",
                            "side": f"greglite:block/{block}_side",
                            "bottom": f"greglite:block/{block}_bottom",
                            "particle": f"greglite:block/{block}_side",
                        },
                    },
                )
            n += 1

    # refresh steam machines if casing available
    if steam_casing_side and steam_casing_top and steam_casing_bottom:
        for block, folder in [
            ("steam_macerator", "machines/macerator"),
            ("steam_compressor", "machines/compressor"),
            ("steam_alloy_smelter", "machines/alloy_smelter"),
        ]:
            front = try_fetch(f"block/{folder}/overlay_front.png")
            front_on = try_fetch(f"block/{folder}/overlay_front_active.png") or front
            save(compose(steam_casing_side, front), TEX / "block" / f"{block}_front.png")
            save(compose(steam_casing_side, front_on), TEX / "block" / f"{block}_front_on.png")
            save(steam_casing_side.copy(), TEX / "block" / f"{block}_side.png")
            save(steam_casing_top.copy(), TEX / "block" / f"{block}_top.png")
            save(steam_casing_bottom.copy(), TEX / "block" / f"{block}_bottom.png")
            n += 1

    return n


def bake_cables() -> int:
    cables = json.loads((EXTRACT / "cable_materials.json").read_text(encoding="utf-8"))["cables"]
    colors = {}
    cp = EXTRACT / "material_colors.json"
    if cp.exists():
        colors = json.loads(cp.read_text(encoding="utf-8")).get("colors", {})
    # use wire texture as cable face base
    wire = try_fetch("item/material_sets/dull/wire_fine.png") or try_fetch(
        "block/cable/wire_side.png"
    )
    n = 0
    for c in cables:
        mid = c["id"] if isinstance(c, dict) else str(c)
        rgb = colors.get(mid, FALLBACK_RGB.get(mid, 0xAAAAAA))
        for amp in ("1x", "4x"):
            block = f"{mid}_cable_{amp}"
            if wire is not None:
                img = tint(wire, None, rgb)
                for part in ("side", "top", "bottom", "front", "front_on"):
                    save(img.copy(), TEX / "block" / f"{block}_{part}.png")
            # solid non-furnace template — no false "not available yet" on right-click
            write_json(
                DATA / "horizon" / "block" / f"{block}.json",
                {
                    "template": "minecraft:iron_block",
                    "properties": {"hardness": 2.0, "sounds": "minecraft:iron_block"},
                    "item": True,
                },
            )
            write_json(
                ASSETS / "blockstates" / f"{block}.json",
                {"variants": {"": {"model": f"greglite:block/{block}"}}},
            )
            write_json(
                ASSETS / "models" / "block" / f"{block}.json",
                {
                    "parent": "minecraft:block/cube_all",
                    "textures": {"all": f"greglite:block/{block}_side"},
                },
            )
            write_json(
                ASSETS / "models" / "item" / f"{block}.json",
                {"parent": f"greglite:block/{block}"},
            )
            write_json(
                ASSETS / "items" / f"{block}.json",
                {
                    "model": {
                        "type": "minecraft:model",
                        "model": f"greglite:item/{block}",
                    }
                },
            )
            n += 1
    # hull / diode / transformer also should not be furnaces
    for p in (DATA / "horizon" / "block").glob("*.json"):
        stem = p.stem
        if any(
            stem.endswith(s)
            for s in (
                "_machine_hull",
                "_diode",
                "_transformer",
                "_battery_buffer_4x",
                "_charger_4",
                "_buffer",
            )
        ):
            obj = json.loads(p.read_text(encoding="utf-8"))
            if obj.get("template") == "minecraft:furnace":
                if stem.endswith(("_battery_buffer_4x", "_charger_4", "_buffer")):
                    continue  # keep furnace for container menus
                obj["template"] = "minecraft:iron_block"
                write_json(p, obj)
                n += 1
    return n


def main() -> None:
    TEX.mkdir(parents=True, exist_ok=True)
    mi = bake_materials()
    ma = bake_machines()
    ca = bake_cables()
    print(f"baked materials={mi} machines={ma} cables/utils={ca}")
    print(
        "block png",
        len(list((TEX / "block").glob("*.png"))),
        "item png",
        len(list((TEX / "item").glob("*.png"))),
    )


if __name__ == "__main__":
    main()
