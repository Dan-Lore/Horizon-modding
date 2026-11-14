"""Fetch GTM GUI textures (LGPL) into greglite assets."""
from __future__ import annotations

import io
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "assets" / "greglite" / "textures" / "gui"
BASE = "https://raw.githubusercontent.com/GregTechCEu/GregTech-Modern/1.20.1/src/main/resources/assets/gtceu/textures/gui"

FILES = [
    "base/background.png",
    "widget/progress_bar_arrow.png",
    "widget/progress_bar_boiler_fuel_bronze.png",
    "widget/progress_bar_boiler_empty_bronze.png",
    "widget/slot.png",
    "widget/fluid_slot.png",
    "widget/progress_bar_fuel.png",
    "widget/progress_bar_energy.png",
]


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    for rel in FILES:
        url = f"{BASE}/{rel}"
        name = rel.replace("/", "_")
        dest = OUT / name
        try:
            print("GET", url)
            with urllib.request.urlopen(url, timeout=60) as r:
                dest.write_bytes(r.read())
            print("wrote", dest.relative_to(ROOT))
        except Exception as e:
            print("skip", rel, e)
    # Friendly aliases used by screens.rs.
    # NEVER alias full machine GUIs (176x166) to the 16x16 base panel.
    aliases = {
        "progress_bar_arrow_bronze.png": "widget_progress_bar_arrow.png",
        "progress_bar_boiler_fuel_bronze.png": "widget_progress_bar_boiler_fuel_bronze.png",
        "progress_bar_boiler_empty_bronze.png": "widget_progress_bar_boiler_empty_bronze.png",
    }
    for dst, src in aliases.items():
        s = OUT / src
        d = OUT / dst
        if s.exists():
            d.write_bytes(s.read_bytes())
            print("alias", dst)

    # Build 176x166 machine backgrounds from GTM base background if missing.
    from PIL import Image

    base = OUT / "base_background.png"
    for name in ("steam_machine.png", "steam_boiler.png"):
        dest = OUT / name
        if dest.exists() and Image.open(dest).size == (176, 166):
            continue
        if not base.exists():
            print("skip compose", name, "(no base)")
            continue
        tile = Image.open(base).convert("RGBA")
        bg = Image.new("RGBA", (176, 166), (198, 198, 198, 255))
        for y in range(0, 166, tile.height):
            for x in range(0, 176, tile.width):
                bg.alpha_composite(tile, (x, y))
        # slot wells for 1-in / 1-out processor layout
        slot = OUT / "widget_slot.png"
        if slot.exists():
            s = Image.open(slot).convert("RGBA")
            for pos in [(52, 34), (115, 34)]:
                bg.alpha_composite(s, pos)
        bg.save(dest)
        print("composed", name, bg.size)


if __name__ == "__main__":
    main()
