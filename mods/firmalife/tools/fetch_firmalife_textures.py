#!/usr/bin/env python3
"""Copy Firmalife (MIT) textures from the TFG jar into mods/firmalife/assets.

License: Firmalife jar META-INF/mods.toml license = MIT — textures OK with attribution.

Default jar (TFG-Modern instance):
  %USERPROFILE%/curseforge/minecraft/Instances/TerraFirmaGreg-Modern/mods/Firmalife-*.jar

Usage:
  python mods/firmalife/tools/fetch_firmalife_textures.py
  python mods/firmalife/tools/fetch_firmalife_textures.py --jar PATH
"""

from __future__ import annotations

import argparse
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "assets" / "firmalife" / "textures"
NOTICE = ROOT / "NOTICE"

# Our simplified ids → best-matching upstream PNGs inside assets/firmalife/textures/
MAP = {
    # No dedicated beehive block PNG in 2.1.28 — use frame item as workshop stand-in.
    "block/beehive.png": "item/beehive_frame.png",
    "block/cheese_wheel.png": "block/cheese/cheddar_wheel_surface_fresh.png",
    # Upstream uses solar drier / cloth-like mats under other names; treated wood glass is closest panel look.
    "block/drying_mat.png": "block/solar_drier_mat.png",
    "block/greenhouse_panel.png": "block/greenhouse/iron_glass.png",
    "block/oven.png": "block/brick_oven_side.png",
    "block/sprinkler.png": "block/sprinkler_head.png",
    "block/vat.png": "block/vat.png",
    "item/cheese.png": "item/food/cheddar.png",
    "item/dried_fruit.png": "item/dried/dried_olive.png",
    "item/honey_jar.png": "item/jar/honey.png",
    "item/jar.png": "item/empty_jar_with_stainless_steel_lid.png",
    "item/olive_oil_bottle.png": "item/dried/dried_olive.png",
    "item/raw_honey.png": "item/raw_honey.png",
}

DEFAULT_JAR_GLOB = (
    Path.home()
    / "curseforge/minecraft/Instances/TerraFirmaGreg-Modern/mods"
)


def find_jar(explicit: Path | None) -> Path:
    if explicit is not None:
        if not explicit.is_file():
            raise SystemExit(f"jar not found: {explicit}")
        return explicit
    mods = DEFAULT_JAR_GLOB
    if not mods.is_dir():
        raise SystemExit(f"TFG mods folder missing: {mods} (pass --jar)")
    jars = sorted(mods.glob("Firmalife-*.jar"))
    if not jars:
        raise SystemExit(f"no Firmalife-*.jar under {mods}")
    return jars[-1]


def ensure_notice() -> None:
    text = NOTICE.read_text(encoding="utf-8") if NOTICE.is_file() else ""
    line = (
        "Textures: vendored from Firmalife (MIT) via fetch_firmalife_textures.py "
        "from the TFG-Modern jar; attributed; not an official Firmalife build.\n"
    )
    if "fetch_firmalife_textures.py" not in text:
        if text and not text.endswith("\n"):
            text += "\n"
        NOTICE.write_text(text + "\n" + line, encoding="utf-8")


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--jar", type=Path, default=None)
    args = ap.parse_args()
    jar = find_jar(args.jar)
    print(f"jar: {jar}")

    with zipfile.ZipFile(jar) as z:
        toml = z.read("META-INF/mods.toml").decode("utf-8", errors="replace")
        lic = re.search(r'(?im)^license\s*=\s*"?([^"\r\n]+)"?', toml)
        lic_s = (lic.group(1).strip() if lic else "").upper()
        if "MIT" not in lic_s:
            raise SystemExit(f"refusing: jar license is {lic_s!r}, expected MIT")
        print(f"license: {lic_s}")

        copied = 0
        missing = []
        for dest_rel, src_rel in MAP.items():
            zip_path = f"assets/firmalife/textures/{src_rel}"
            out = TEX / dest_rel
            if zip_path not in z.namelist():
                # try alternate names
                alt = None
                base = Path(src_rel).name
                for n in z.namelist():
                    if n.endswith("/" + base) and n.startswith("assets/firmalife/textures/"):
                        alt = n
                        break
                if alt is None:
                    missing.append(zip_path)
                    continue
                zip_path = alt
            out.parent.mkdir(parents=True, exist_ok=True)
            out.write_bytes(z.read(zip_path))
            print(f"  {zip_path} -> {dest_rel}")
            copied += 1

    ensure_notice()
    print(f"copied {copied}/{len(MAP)}")
    if missing:
        print("missing:")
        for m in missing:
            print(f"  {m}")
        raise SystemExit(1)


if __name__ == "__main__":
    main()
