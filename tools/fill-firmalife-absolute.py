#!/usr/bin/env python3
"""Fill missing Firmalife Absolute ids from TFG jar model/blockstate paths.

MIT textures preferred via fetch script when present; else vanilla placeholder
models. Skips ids that collide with an existing horizon/block (item:true).
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


def jar_ids(prefix: str) -> list[str]:
    z = zipfile.ZipFile(JAR)
    out: list[str] = []
    for name in z.namelist():
        if name.startswith(prefix) and name.endswith(".json"):
            rel = name[len(prefix) : -5].replace("/", "_")
            out.append(rel)
    return sorted(set(out))


def ensure_item(stem: str) -> bool:
    if (DATA / "horizon" / "block" / f"{stem}.json").exists():
        return False
    if (DATA / "horizon" / "item" / f"{stem}.json").exists():
        return False
    if (ASSETS / "items" / f"{stem}.json").exists():
        return False
    write(DATA / "horizon" / "item" / f"{stem}.json", {"template": "minecraft:apple"})
    write(
        ASSETS / "items" / f"{stem}.json",
        {"model": {"type": "minecraft:model", "model": f"firmalife:item/{stem}"}},
    )
    write(
        ASSETS / "models" / "item" / f"{stem}.json",
        {
            "parent": "minecraft:item/generated",
            "textures": {"layer0": "minecraft:item/apple"},
        },
    )
    return True


def ensure_block(stem: str) -> bool:
    if (DATA / "horizon" / "block" / f"{stem}.json").exists():
        return False
    if (DATA / "horizon" / "item" / f"{stem}.json").exists():
        # item already claimed this id — skip block to avoid collision
        return False
    if (ASSETS / "blockstates" / f"{stem}.json").exists():
        return False
    write(
        DATA / "horizon" / "block" / f"{stem}.json",
        {
            "template": "minecraft:iron_block",
            "properties": {"hardness": 1.0, "sounds": "minecraft:stone"},
            "item": True,
        },
    )
    write(
        ASSETS / "blockstates" / f"{stem}.json",
        {"variants": {"": {"model": f"firmalife:block/{stem}"}}},
    )
    write(
        ASSETS / "models" / "block" / f"{stem}.json",
        {
            "parent": "minecraft:block/cube_all",
            "textures": {"all": "minecraft:block/oak_planks"},
        },
    )
    write(
        ASSETS / "models" / "item" / f"{stem}.json",
        {"parent": f"firmalife:block/{stem}"},
    )
    write(
        ASSETS / "items" / f"{stem}.json",
        {"model": {"type": "minecraft:model", "model": f"firmalife:item/{stem}"}},
    )
    return True


def main() -> None:
    if not JAR.is_file():
        raise SystemExit(f"Firmalife jar missing: {JAR}")
    item_ids = jar_ids("assets/firmalife/models/item/")
    block_ids = jar_ids("assets/firmalife/blockstates/")
    ni = sum(1 for s in item_ids if ensure_item(s))
    # Prefer filling blocks that are not already items
    nb = 0
    for s in block_ids:
        if ensure_block(s):
            nb += 1
    items_n = len(list((ASSETS / "items").glob("*.json")))
    blocks_n = len(list((ASSETS / "blockstates").glob("*.json")))
    print(f"firmalife added items={ni} blocks={nb}; now items={items_n} blocks={blocks_n}")


if __name__ == "__main__":
    main()
