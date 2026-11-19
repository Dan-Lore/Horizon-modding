"""Fetch selected GregTech Modern textures (LGPL-3.0) and bake gtceu assets."""
from __future__ import annotations

import io
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "assets" / "gtceu" / "textures"
BASE = "https://raw.githubusercontent.com/GregTechCEu/GregTech-Modern/1.20.1/src/main/resources/assets/gtceu/textures"

MATERIALS = {
    "copper": (0xE7, 0x7C, 0x56),
    "tin": (0xDC, 0xE1, 0xDE),
    "bronze": (0xFF, 0x80, 0x33),
    "iron": (0xC8, 0xC8, 0xC8),
}

FORMS = ["ingot", "dust", "plate"]


def fetch(rel: str) -> Image.Image:
    url = f"{BASE}/{rel}"
    print("GET", url)
    with urllib.request.urlopen(url, timeout=60) as r:
        return Image.open(io.BytesIO(r.read())).convert("RGBA")


def tint(base: Image.Image, overlay: Image.Image | None, rgb: tuple[int, int, int]) -> Image.Image:
    img = base.copy()
    px = img.load()
    r, g, b = rgb
    for y in range(img.height):
        for x in range(img.width):
            pr, pg, pb, pa = px[x, y]
            if pa == 0:
                continue
            px[x, y] = ((pr * r) // 255, (pg * g) // 255, (pb * b) // 255, pa)
    if overlay is not None:
        img.alpha_composite(overlay)
    return img


def save(img: Image.Image, path: Path) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)
    print("wrote", path.relative_to(ROOT))


def compose(base: Image.Image, overlay: Image.Image | None) -> Image.Image:
    out = base.copy()
    if overlay is not None:
        # Overlays may be smaller or same size; paste centered if needed.
        if overlay.size != out.size:
            overlay = overlay.resize(out.size, Image.NEAREST)
        out.alpha_composite(overlay)
    return out


def main() -> None:
    # Material items from dull set (colorized).
    for form in FORMS:
        base = fetch(f"item/material_sets/dull/{form}.png")
        try:
            overlay = fetch(f"item/material_sets/dull/{form}_overlay.png")
        except Exception:
            overlay = None
        for name, rgb in MATERIALS.items():
            # Skip copper/iron ingots — vanilla items used in recipes.
            if form == "ingot" and name in ("copper", "iron"):
                continue
            save(tint(base, overlay, rgb), TEX / "item" / f"{name}_{form}.png")

    casing_side = fetch("block/casings/steam/bronze/side.png")
    casing_top = fetch("block/casings/steam/bronze/top.png")
    casing_bottom = fetch("block/casings/steam/bronze/bottom.png")

    machines = {
        "steam_alloy_smelter": "block/machines/alloy_smelter",
        "steam_macerator": "block/machines/macerator",
        "steam_compressor": "block/machines/compressor",
    }
    for block, prefix in machines.items():
        front = fetch(f"{prefix}/overlay_front.png")
        try:
            front_on = fetch(f"{prefix}/overlay_front_active.png")
        except Exception:
            front_on = front
        side = compose(casing_side, None)
        save(compose(casing_side, front), TEX / "block" / f"{block}_front.png")
        save(compose(casing_side, front_on), TEX / "block" / f"{block}_front_on.png")
        save(side, TEX / "block" / f"{block}_side.png")
        save(casing_top.copy(), TEX / "block" / f"{block}_top.png")
        save(casing_bottom.copy(), TEX / "block" / f"{block}_bottom.png")

    # Solid boiler (coal).
    boiler_front = fetch("block/generators/boiler/coal/overlay_front.png")
    try:
        boiler_front_on = fetch("block/generators/boiler/coal/overlay_front_active.png")
    except Exception:
        boiler_front_on = boiler_front
    save(compose(casing_side, boiler_front), TEX / "block" / "steam_solid_boiler_lp_front.png")
    save(compose(casing_side, boiler_front_on), TEX / "block" / "steam_solid_boiler_lp_front_on.png")
    save(casing_side.copy(), TEX / "block" / "steam_solid_boiler_lp_side.png")
    save(casing_top.copy(), TEX / "block" / "steam_solid_boiler_lp_top.png")
    save(casing_bottom.copy(), TEX / "block" / "steam_solid_boiler_lp_bottom.png")

    # GUI: bronze steam-style panels (baked simple backgrounds + GT progress bars).
    gui = TEX / "gui"
    # 176x166 generic panel tinted bronze/dark
    panel = Image.new("RGBA", (176, 166), (40, 35, 30, 255))
    # inner slot-ish rectangle
    for x in range(7, 169):
        for y in range(16, 84):
            panel.putpixel((x, y), (55, 48, 40, 255))
    # inventory area
    for x in range(7, 169):
        for y in range(84, 160):
            panel.putpixel((x, y), (48, 42, 36, 255))
    save(panel, gui / "steam_machine.png")
    save(panel.copy(), gui / "steam_boiler.png")

    for name in (
        "progress_bar/progress_bar_arrow_bronze.png",
        "progress_bar/progress_bar_boiler_fuel_bronze.png",
        "progress_bar/progress_bar_boiler_empty_bronze.png",
    ):
        img = fetch(f"gui/{name}")
        save(img, gui / Path(name).name)


if __name__ == "__main__":
    main()
