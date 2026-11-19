"""Recompose machine front overlays onto current tier casing sides."""
from __future__ import annotations

import json
import re
import urllib.request
from io import BytesIO
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "assets" / "gtceu" / "textures" / "block"
EXTRACT = ROOT / "tracker" / "gtm_extract"
BASE = "https://raw.githubusercontent.com/GregTechCEu/GregTech-Modern/1.20.1/src/main/resources/assets/gtceu/textures"
TIERS = ["lv", "mv", "hv", "ev", "iv", "luv", "zpm", "uv"]


def fetch(rel: str) -> Image.Image | None:
    try:
        with urllib.request.urlopen(f"{BASE}/{rel}", timeout=40) as r:
            return Image.open(BytesIO(r.read())).convert("RGBA")
    except Exception as e:
        print("skip", rel, e)
        return None


def compose(base: Image.Image, overlay: Image.Image | None) -> Image.Image:
    out = base.copy()
    if overlay is not None:
        ov = overlay if overlay.size == out.size else overlay.resize(out.size, Image.NEAREST)
        out.alpha_composite(ov)
    return out


def main() -> None:
    machines = json.loads((EXTRACT / "electric_machine_types.json").read_text(encoding="utf-8"))[
        "machines"
    ]
    overlays: dict[str, tuple[Image.Image | None, Image.Image | None]] = {}
    for m in machines:
        mtype = m["id"]
        folder = {"rock_crusher": "rock_crusher", "spooler": "spooling"}.get(mtype, mtype)
        front = fetch(f"block/machines/{folder}/overlay_front.png")
        front_on = fetch(f"block/machines/{folder}/overlay_front_active.png") or front
        overlays[mtype] = (front, front_on)

    n = 0
    for mtype, (front, front_on) in overlays.items():
        for tier in TIERS:
            side = TEX / f"{tier}_casing_side.png"
            if not side.exists():
                continue
            base = Image.open(side).convert("RGBA")
            compose(base, front).save(TEX / f"{tier}_{mtype}_front.png")
            compose(base, front_on).save(TEX / f"{tier}_{mtype}_front_on.png")
            n += 1
    # generators lv-hv
    for gid, folder in [
        ("combustion", "generators/combustion"),
        ("gas_turbine", "generators/gas_turbine"),
        ("steam_turbine", "generators/steam"),
    ]:
        front = fetch(f"block/{folder}/overlay_front.png") or fetch(
            "block/machines/macerator/overlay_front.png"
        )
        front_on = fetch(f"block/{folder}/overlay_front_active.png") or front
        for tier in ("lv", "mv", "hv"):
            side = TEX / f"{tier}_casing_side.png"
            if not side.exists():
                continue
            base = Image.open(side).convert("RGBA")
            compose(base, front).save(TEX / f"{tier}_{gid}_front.png")
            compose(base, front_on).save(TEX / f"{tier}_{gid}_front_on.png")
            n += 1
    print("recomposed", n)


if __name__ == "__main__":
    main()
