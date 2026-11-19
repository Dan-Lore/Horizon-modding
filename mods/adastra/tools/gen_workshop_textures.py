#!/usr/bin/env python3
"""Generate original workshop textures for Ad Astra Horizon (not Ad Astra ARR art).

Terrarium non-code is ARR — we do not copy PNGs from the Ad Astra jar.
These 16×16 procedural tiles are original MIT workshop art.
"""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "assets" / "adastra" / "textures"

# Distinct palettes (RGB) — industrial / planetary, not copied from upstream.
PALETTES = {
    "desh": ((180, 110, 55), (120, 70, 30), (220, 160, 90)),
    "ostrum": ((90, 70, 110), (50, 40, 70), (140, 120, 160)),
    "calorite": ((190, 60, 70), (120, 30, 40), (240, 120, 100)),
    "steel": ((140, 145, 150), (80, 85, 90), (200, 205, 210)),
    "iron": ((160, 160, 165), (90, 90, 95), (210, 210, 215)),
    "machine": ((70, 85, 100), (40, 50, 60), (120, 160, 180)),
    "oxygen": ((70, 140, 190), (30, 80, 120), (160, 210, 240)),
    "fuel": ((60, 140, 80), (30, 80, 40), (140, 200, 100)),
    "rocket": ((200, 200, 205), (90, 90, 100), (240, 80, 60)),
    "cheese": ((230, 200, 90), (180, 150, 50), (250, 230, 150)),
    "marker": ((40, 40, 50), (20, 20, 28), (80, 200, 120)),
}


def tile(base, dark, light, kind: str) -> Image.Image:
    im = Image.new("RGBA", (16, 16), (*base, 255))
    d = ImageDraw.Draw(im)
    # bevel frame
    d.rectangle([0, 0, 15, 15], outline=(*light, 255))
    d.rectangle([1, 1, 14, 14], outline=(*dark, 255))
    if kind == "ingot":
        d.rectangle([3, 5, 12, 10], fill=(*light, 255), outline=(*dark, 255))
    elif kind == "nugget":
        d.ellipse([4, 4, 11, 11], fill=(*light, 255), outline=(*dark, 255))
    elif kind == "plate":
        d.rectangle([2, 2, 13, 13], fill=(*light, 200), outline=(*dark, 255))
        d.line([2, 8, 13, 8], fill=(*dark, 255))
    elif kind == "block":
        for y in range(2, 14, 4):
            d.rectangle([2, y, 13, y + 2], fill=(*light, 180))
    elif kind == "machine":
        d.rectangle([3, 3, 12, 12], fill=(*dark, 255))
        d.rectangle([5, 5, 10, 10], fill=(*light, 255))
        d.point([(6, 6), (9, 6), (6, 9), (9, 9)], fill=(*base, 255))
    elif kind == "tank":
        d.rectangle([5, 2, 10, 13], fill=(*light, 220), outline=(*dark, 255))
        d.rectangle([6, 4, 9, 11], fill=(*base, 255))
    elif kind == "rocket":
        d.polygon([(8, 1), (12, 14), (4, 14)], fill=(*light, 255), outline=(*dark, 255))
        d.rectangle([6, 10, 9, 14], fill=(*PALETTES["rocket"][2], 255))
    elif kind == "glob":
        d.ellipse([3, 3, 12, 12], fill=(*light, 255), outline=(*dark, 255))
    else:
        d.rectangle([4, 4, 11, 11], fill=(*light, 200))
    return im


ITEMS = {
    "item/desh_ingot.png": ("desh", "ingot"),
    "item/desh_nugget.png": ("desh", "nugget"),
    "item/desh_plate.png": ("desh", "plate"),
    "item/ostrum_ingot.png": ("ostrum", "ingot"),
    "item/ostrum_nugget.png": ("ostrum", "nugget"),
    "item/ostrum_plate.png": ("ostrum", "plate"),
    "item/calorite_ingot.png": ("calorite", "ingot"),
    "item/calorite_nugget.png": ("calorite", "nugget"),
    "item/calorite_plate.png": ("calorite", "plate"),
    "item/steel_ingot.png": ("steel", "ingot"),
    "item/steel_nugget.png": ("steel", "nugget"),
    "item/steel_plate.png": ("steel", "plate"),
    "item/iron_plate.png": ("iron", "plate"),
    "item/cheese.png": ("cheese", "glob"),
    "item/oxygen_tank.png": ("oxygen", "tank"),
    "item/oxygen_tank_empty.png": ("steel", "tank"),
    "item/space_suit_helmet.png": ("oxygen", "block"),
    "item/space_suit_chestplate.png": ("oxygen", "block"),
    "item/space_suit_leggings.png": ("oxygen", "block"),
    "item/space_suit_boots.png": ("oxygen", "block"),
    "item/rocket_t1.png": ("rocket", "rocket"),
    "item/rocket_fuel.png": ("fuel", "glob"),
    "item/oil_bucket.png": ("fuel", "tank"),
    "block/desh_block.png": ("desh", "block"),
    "block/ostrum_block.png": ("ostrum", "block"),
    "block/calorite_block.png": ("calorite", "block"),
    "block/steel_block.png": ("steel", "block"),
    "block/moon_stone.png": ("steel", "block"),
    "block/moon_cobblestone.png": ("iron", "block"),
    "block/coal_generator.png": ("machine", "machine"),
    "block/compressor.png": ("machine", "machine"),
    "block/nasa_workbench.png": ("machine", "machine"),
    "block/fuel_refinery.png": ("fuel", "machine"),
    "block/oxygen_loader.png": ("oxygen", "machine"),
    "block/oxygen_distributor.png": ("oxygen", "machine"),
    "block/solar_panel.png": ("oxygen", "plate"),
    "block/cryo_freezer.png": ("ostrum", "machine"),
    "block/launch_pad.png": ("steel", "plate"),
    "block/vacuum_marker.png": ("marker", "machine"),
}


def main() -> None:
    n = 0
    for rel, (pal, kind) in ITEMS.items():
        base, dark, light = PALETTES[pal]
        out = TEX / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        tile(base, dark, light, kind).save(out, optimize=True)
        n += 1
    print(f"wrote {n} textures under {TEX}")


if __name__ == "__main__":
    main()
