#!/usr/bin/env python3
"""Fetch TerraFirmaCraft textures (EUPL-1.2) into mods/tfc/assets.

Upstream: https://github.com/TerraFirmaCraft/TerraFirmaCraft (branch 1.20.x)
Run after gen_content.py so placeholders get replaced:

    python mods/tfc/tools/gen_content.py
    python mods/tfc/tools/fetch_tfc_textures.py
"""

from __future__ import annotations

import io
import urllib.error
import urllib.request
from pathlib import Path

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "assets" / "tfc" / "textures"
BASE = (
    "https://raw.githubusercontent.com/TerraFirmaCraft/TerraFirmaCraft/"
    "1.20.x/src/main/resources/assets/tfc/textures"
)

ROCKS = ["andesite", "granite", "basalt", "chalk", "chert", "shale", "limestone", "marble"]
ROCK_FORMS = {
    "raw": "raw",
    "cobble": "cobble",
    "smooth": "smooth",
    "gravel": "gravel",
}
ORES = [
    "native_copper",
    "native_gold",
    "native_silver",
    "cassiterite",
    "hematite",
    "bismuthinite",
    "sphalerite",
    "malachite",
]
METALS = [
    "copper",
    "tin",
    "bronze",
    "bismuth",
    "zinc",
    "brass",
    "silver",
    "wrought_iron",
    "steel",
]
METAL_FORMS = ["ingot", "double_ingot", "sheet", "rod"]
TOOL_KINDS = {
    "axe": "axe",
    "hoe": "hoe",
    "knife": "knife",
    "pickaxe": "pickaxe",
    "shovel": "shovel",
    "hammer": "hammer",
    "chisel": "chisel",
    "propick": "propick",
}
HEAD_OF = {
    "axe": "axe_head",
    "hoe": "hoe_head",
    "knife": "knife_blade",
    "pickaxe": "pickaxe_head",
    "shovel": "shovel_head",
    "hammer": "hammer_head",
    "chisel": "chisel_head",
    "propick": "propick_head",
}
CAST_OR_FORGE = ["copper", "bronze", "wrought_iron"]
STONE_TOOLS = ["axe", "hoe", "knife", "shovel", "hammer"]

# Local dest relative to textures/ -> upstream path under textures/
DIRECT: dict[str, str] = {
    # devices / structures (single representative face for orientable cubes)
    "block/firepit.png": "item/firepit.png",
    "block/charcoal_forge.png": "block/devices/charcoal_forge/5.png",
    "block/bloomery.png": "block/devices/bloomery/off.png",
    "block/anvil.png": "block/metal/block/wrought_iron.png",
    "block/quern.png": "block/devices/quern/quern_side.png",
    "block/barrel.png": "block/wood/planks/oak.png",
    "block/pit_kiln.png": "block/thatch.png",
    "block/blast_furnace.png": "block/devices/blast_furnace/side.png",
    "block/sluice.png": "block/wood/planks/oak.png",
    "block/charcoal_pit.png": "block/charcoal_pile.png",
    "block/log_pile.png": "block/log_pile_side.png",
    "block/support_beam.png": "block/wood/planks/oak.png",
    "block/powderkeg.png": "block/devices/powderkeg/powderkeg_outside.png",
    "block/crop_wheat.png": "block/crop/wheat_7.png",
    "block/crop_barley.png": "block/crop/barley_7.png",
    "block/crop_cabbage.png": "block/crop/cabbage_5.png",
    "block/crop_oat.png": "block/crop/oat_7.png",
    "block/crop_rye.png": "block/crop/rye_7.png",
    "block/crop_onion.png": "block/crop/onion_5.png",
    "block/crop_squash.png": "block/crop/squash_5.png",
    "block/crucible.png": "block/devices/crucible/side.png",
    "block/knapping.png": "block/rock/raw/andesite.png",
    "block/small_vessel.png": "item/ceramic/vessel.png",
    # items
    "item/prospector_pick.png": "item/metal/propick/copper.png",
    "item/pan.png": "item/ceramic/unfired_pan.png",
    "item/jug.png": "item/ceramic/jug_empty.png",
    "item/wooden_bucket.png": "item/bucket/wooden_bucket_empty.png",
    "item/vessel.png": "item/ceramic/vessel.png",
    "item/unfired_vessel.png": "item/ceramic/unfired_vessel.png",
    "item/unfired_jug.png": "item/ceramic/unfired_jug.png",
    "item/straw.png": "item/straw.png",
    "item/flux.png": "item/powder/flux.png",
    "item/raw_iron_bloom.png": "item/bloom/unrefined.png",
    "item/glass_batch.png": "item/silica_glass_batch.png",
    "item/lumber.png": "item/wood/lumber.png",
    "item/tannin.png": "item/powder/wood_ash.png",
    "item/ore_deposit.png": "block/deposit/native_copper.png",
    "item/red_apple.png": "item/food/red_apple.png",
    "item/carrot.png": "item/food/carrot.png",
    "item/bread.png": "item/food/wheat_bread.png",
    "item/cooked_meat.png": "item/food/cooked_beef.png",
    "item/cheese.png": "item/food/cheese.png",
    "item/cabbage.png": "item/food/cabbage.png",
    "item/wheat.png": "item/food/wheat.png",
    "item/barley_grain.png": "item/food/barley_grain.png",
    "item/flour.png": "item/food/wheat_flour.png",
    "item/dough.png": "item/food/wheat_dough.png",
    "item/oat_grain.png": "item/food/oat_grain.png",
    "item/rye_grain.png": "item/food/rye_grain.png",
    "item/onion.png": "item/food/onion.png",
    "item/squash.png": "item/food/squash.png",
    "item/cooked_squash.png": "item/food/squash.png",
    "item/rot.png": "item/compost.png",
}


def fetch(rel: str) -> Image.Image:
    url = f"{BASE}/{rel}"
    with urllib.request.urlopen(url, timeout=60) as r:
        return Image.open(io.BytesIO(r.read())).convert("RGBA")


def save(img: Image.Image, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    # Explicit format avoids rare Windows path/extension races with Pillow.
    img.save(dest, format="PNG")


def try_map(local: str, upstream: str, ok: list[str], missing: list[str]) -> None:
    dest = TEX / local
    try:
        save(fetch(upstream), dest)
        ok.append(f"{local} <- {upstream}")
    except (urllib.error.HTTPError, urllib.error.URLError, OSError) as exc:
        missing.append(f"{local} <- {upstream} ({exc})")


def build_map() -> dict[str, str]:
    mapping = dict(DIRECT)
    for rock in ROCKS:
        for form, folder in ROCK_FORMS.items():
            mapping[f"block/{rock}_{form}.png"] = f"block/rock/{folder}/{rock}.png"
    for ore in ORES:
        # Nuggets / small ore piles — item icons. Ore blocks composed separately.
        mapping[f"item/nugget_{ore}.png"] = f"item/ore/small_{ore}.png"
    for metal in METALS:
        for form in METAL_FORMS:
            mapping[f"item/{metal}_{form}.png"] = f"item/metal/{form}/{metal}.png"
        if metal in CAST_OR_FORGE:
            for tool, tfc_tool in TOOL_KINDS.items():
                mapping[f"item/{metal}_{tool}.png"] = f"item/metal/{tfc_tool}/{metal}.png"
                head = HEAD_OF[tool]
                mapping[f"item/{metal}_{head}.png"] = f"item/metal/{head}/{metal}.png"
    for tool in STONE_TOOLS:
        mapping[f"item/stone_{tool}.png"] = f"item/stone/{tool}.png"
        head = HEAD_OF[tool]
        upstream_head = "knife_head" if head == "knife_blade" else head
        mapping[f"item/stone_{head}.png"] = f"item/stone/{upstream_head}.png"
    return mapping


def compose_ores(ok: list[str], missing: list[str]) -> None:
    """TFC block/ore/*.png are transparent overlays — bake onto raw granite."""
    try:
        base = fetch("block/rock/raw/granite.png")
    except (urllib.error.HTTPError, urllib.error.URLError, OSError) as exc:
        missing.append(f"ore-base granite ({exc})")
        return
    for ore in ORES:
        local = f"block/ore_{ore}.png"
        upstream = f"block/ore/normal_{ore}.png"
        try:
            overlay = fetch(upstream)
            out = base.copy()
            out.alpha_composite(overlay)
            save(out, TEX / local)
            ok.append(f"{local} <- granite + {upstream}")
        except (urllib.error.HTTPError, urllib.error.URLError, OSError) as exc:
            missing.append(f"{local} <- {upstream} ({exc})")


def main() -> None:
    mapping = build_map()
    ok: list[str] = []
    missing: list[str] = []
    for local, upstream in sorted(mapping.items()):
        try_map(local, upstream, ok, missing)
    compose_ores(ok, missing)
    print(f"fetched {len(ok)} textures")
    if missing:
        print("missing:")
        for line in missing:
            print(" ", line)


if __name__ == "__main__":
    main()
