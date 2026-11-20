#!/usr/bin/env python3
"""Add missing Firmalife blockstates for Absolute blocks axis.

When an item already owns the id, register horizon/block with item:false
so content loads without item/block collision.
"""

from __future__ import annotations

import json
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MOD = ROOT / "mods" / "firmalife"
ASSETS = MOD / "assets" / "firmalife"
DATA = MOD / "data" / "firmalife"
JAR = (
    Path.home()
    / "curseforge/minecraft/Instances/TerraFirmaGreg-Modern/mods/Firmalife-1.20.1-2.1.28.jar"
)


def write(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    z = zipfile.ZipFile(JAR)
    prefix = "assets/firmalife/blockstates/"
    ids = sorted(
        {
            n[len(prefix) : -5].replace("/", "_")
            for n in z.namelist()
            if n.startswith(prefix) and n.endswith(".json")
        }
    )
    added = 0
    for stem in ids:
        bs = ASSETS / "blockstates" / f"{stem}.json"
        if bs.exists():
            continue
        has_item = (DATA / "horizon" / "item" / f"{stem}.json").exists()
        write(
            DATA / "horizon" / "block" / f"{stem}.json",
            {
                "template": "minecraft:iron_block",
                "properties": {"hardness": 1.0, "sounds": "minecraft:stone"},
                "item": not has_item,
            },
        )
        write(bs, {"variants": {"": {"model": f"firmalife:block/{stem}"}}})
        write(
            ASSETS / "models" / "block" / f"{stem}.json",
            {
                "parent": "minecraft:block/cube_all",
                "textures": {"all": "minecraft:block/oak_planks"},
            },
        )
        if not has_item:
            write(
                ASSETS / "models" / "item" / f"{stem}.json",
                {"parent": f"firmalife:block/{stem}"},
            )
            write(
                ASSETS / "items" / f"{stem}.json",
                {"model": {"type": "minecraft:model", "model": f"firmalife:item/{stem}"}},
            )
        added += 1
    blocks_n = len(list((ASSETS / "blockstates").glob("*.json")))
    print(f"firmalife blocks added={added} now={blocks_n}")


if __name__ == "__main__":
    main()
