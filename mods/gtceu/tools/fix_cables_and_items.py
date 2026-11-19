"""Fix cable block+item textures and ensure material item models point at real PNGs."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "gtceu"
DATA = ROOT / "data" / "gtceu"
TEX_BLOCK = ASSETS / "textures" / "block"
TEX_ITEM = ASSETS / "textures" / "item"
EXTRACT = ROOT / "tracker" / "gtm_extract"
REF = Path(
    r"C:\Dev\Horizon-modding\reference\GregTech-Modern\src\main\resources\assets\gtceu\textures"
)

FALLBACK = {
    "tin": 0xDCE1DE,
    "copper": 0xE77C56,
    "silver": 0xDCDCFF,
    "gold": 0xFFE650,
    "iron": 0xC8C8C8,
    "aluminium": 0x80C8F0,
    "aluminum": 0x80C8F0,
    "nickel": 0xC8C8F0,
    "platinum": 0xFFFFC8,
    "lead": 0x8C648C,
    "electrum": 0xFFFF64,
    "steel": 0x808080,
    "bronze": 0xFF8033,
}


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def tint(img: Image.Image, rgb: int) -> Image.Image:
    r, g, b = (rgb >> 16) & 0xFF, (rgb >> 8) & 0xFF, rgb & 0xFF
    out = img.copy().convert("RGBA")
    px = out.load()
    for y in range(out.height):
        for x in range(out.width):
            pr, pg, pb, pa = px[x, y]
            if pa == 0:
                continue
            px[x, y] = ((pr * r) // 255, (pg * g) // 255, (pb * b) // 255, pa)
    return out


def make_cable_item_icon(rgb: int, insulation: Image.Image, wire: Image.Image) -> Image.Image:
    """16x16 item icon: tinted wire over dark insulation sheath."""
    base = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    ins = insulation.resize((16, 16), Image.NEAREST).convert("RGBA")
    # dark rubber sheath
    sheath = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    sp = sheath.load()
    for y in range(4, 12):
        for x in range(2, 14):
            sp[x, y] = (40, 40, 40, 255)
    for y in range(5, 11):
        for x in range(3, 13):
            sp[x, y] = (55, 55, 55, 255)
    core = tint(wire.resize((16, 16), Image.NEAREST), rgb)
    base.alpha_composite(sheath)
    # draw core as horizontal band
    cp = core.load()
    bp = base.load()
    for y in range(6, 10):
        for x in range(3, 13):
            pr, pg, pb, pa = cp[x, y]
            if pa > 0:
                bp[x, y] = (pr, pg, pb, 255)
    return base


def main() -> None:
    colors = {}
    cp = EXTRACT / "material_colors.json"
    if cp.exists():
        colors = json.loads(cp.read_text(encoding="utf-8")).get("colors", {})
    cables = json.loads((EXTRACT / "cable_materials.json").read_text(encoding="utf-8"))["cables"]

    wire = Image.open(REF / "item/material_sets/dull/wire_fine.png").convert("RGBA")
    insulation = Image.open(REF / "block/cable/insulation_0.png").convert("RGBA")

    n = 0
    for c in cables:
        mid = c["id"] if isinstance(c, dict) else str(c)
        rgb = colors.get(mid, FALLBACK.get(mid, 0xAAAAAA)) or FALLBACK.get(mid, 0xAAAAAA)
        for amp in ("1x", "4x"):
            block = f"{mid}_cable_{amp}"
            # block texture: tinted insulation (solid, readable cube)
            block_tex = tint(insulation.resize((16, 16), Image.NEAREST), rgb)
            # brighten a bit for 4x
            if amp == "4x":
                px = block_tex.load()
                for y in range(16):
                    for x in range(16):
                        r, g, b, a = px[x, y]
                        if a:
                            px[x, y] = (min(255, r + 20), min(255, g + 20), min(255, b + 20), a)
            for part in ("side", "top", "bottom", "front", "front_on"):
                block_tex.save(TEX_BLOCK / f"{block}_{part}.png")

            icon = make_cable_item_icon(rgb, insulation, wire)
            icon.save(TEX_ITEM / f"{block}.png")

            write_json(
                DATA / "horizon" / "block" / f"{block}.json",
                {
                    "template": "minecraft:iron_block",
                    "properties": {"hardness": 1.5, "sounds": "minecraft:iron_block"},
                    "item": True,
                },
            )
            write_json(
                ASSETS / "blockstates" / f"{block}.json",
                {"variants": {"": {"model": f"gtceu:block/{block}"}}},
            )
            write_json(
                ASSETS / "models" / "block" / f"{block}.json",
                {
                    "parent": "minecraft:block/cube_all",
                    "textures": {"all": f"gtceu:block/{block}_side"},
                },
            )
            # ITEM uses flat generated icon — not the ugly cube-in-hand look
            write_json(
                ASSETS / "models" / "item" / f"{block}.json",
                {
                    "parent": "minecraft:item/generated",
                    "textures": {"layer0": f"gtceu:item/{block}"},
                },
            )
            write_json(
                ASSETS / "items" / f"{block}.json",
                {
                    "model": {
                        "type": "minecraft:model",
                        "model": f"gtceu:item/{block}",
                    }
                },
            )
            n += 1

    # Ensure every material item model points at its own PNG (not shared _form_)
    fixed = 0
    for p in (ASSETS / "models" / "item").glob("*.json"):
        obj = json.loads(p.read_text(encoding="utf-8"))
        tex = (obj.get("textures") or {}).get("layer0", "")
        if "_form_" in tex:
            own = f"gtceu:item/{p.stem}"
            if (TEX_ITEM / f"{p.stem}.png").exists():
                obj["textures"]["layer0"] = own
                write_json(p, obj)
                fixed += 1

    print(f"cables={n} item_models_fixed={fixed}")


if __name__ == "__main__":
    main()
