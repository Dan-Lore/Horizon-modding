"""Re-tint material item textures using material_colors.json (no network)."""
from __future__ import annotations

import json
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "assets" / "greglite" / "textures" / "item"
EXTRACT = ROOT / "tracker" / "gtm_extract"
FORMS = ["ingot", "dust", "plate", "rod", "wire", "screw", "gear", "foil"]
FALLBACK = 0xAAAAAA
FORCE = {
    "steel": 0x808080,
    "wrought_iron": 0xC8B4B4,
    "dark_ash": 0x323232,
    "ash": 0x969696,
}


def tint(base: Image.Image, overlay: Image.Image | None, rgb: int) -> Image.Image:
    r, g, b = (rgb >> 16) & 0xFF, (rgb >> 8) & 0xFF, rgb & 0xFF
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


def main() -> None:
    colors = json.loads((EXTRACT / "material_colors.json").read_text(encoding="utf-8"))["colors"]
    mats = json.loads((EXTRACT / "materials_core.json").read_text(encoding="utf-8"))["materials"]
    bases = {}
    for form in FORMS:
        p = TEX / f"_form_{form}.png"
        if p.exists():
            bases[form] = Image.open(p).convert("RGBA")
    n = 0
    for m in mats:
        mid = m["id"]
        rgb = FORCE.get(mid, colors.get(mid, FALLBACK))
        if not rgb:
            rgb = FALLBACK
        for form in FORMS:
            if form not in bases:
                continue
            if form == "ingot" and mid in ("iron", "copper", "gold", "netherite"):
                continue
            out = tint(bases[form], None, rgb)
            out.save(TEX / f"{mid}_{form}.png")
            n += 1
    print(f"retinted {n} items; colors available={len(colors)}")


if __name__ == "__main__":
    main()
