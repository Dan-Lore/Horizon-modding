#!/usr/bin/env python3
"""Generate Horizon Quests content (book, board, loot crate) + 26.3 items/ defs."""

from __future__ import annotations

import json
import struct
import zlib
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "quests"
DATA = ROOT / "data" / "quests"


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def png(path: Path, rgb: tuple[int, int, int]) -> None:
    r, g, b = rgb
    row = bytes([0]) + bytes([r, g, b, 255]) * 16
    raw = row * 16
    compressed = zlib.compress(raw, 9)

    def chunk(tag: bytes, data: bytes) -> bytes:
        return (
            struct.pack(">I", len(data))
            + tag
            + data
            + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)
        )

    ihdr = struct.pack(">IIBBBBB", 16, 16, 8, 6, 0, 0, 0)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_bytes(
        b"\x89PNG\r\n\x1a\n"
        + chunk(b"IHDR", ihdr)
        + chunk(b"IDAT", compressed)
        + chunk(b"IEND", b"")
    )


def item_files(name: str, rgb: tuple[int, int, int], template: str) -> None:
    write_json(DATA / "horizon" / "item" / f"{name}.json", {"template": template})
    write_json(
        ASSETS / "models" / "item" / f"{name}.json",
        {"parent": "minecraft:item/generated", "textures": {"layer0": f"quests:item/{name}"}},
    )
    write_json(
        ASSETS / "items" / f"{name}.json",
        {"model": {"type": "minecraft:model", "model": f"quests:item/{name}"}},
    )
    png(ASSETS / "textures" / "item" / f"{name}.png", rgb)


def block_board() -> None:
    name = "quest_board"
    write_json(
        DATA / "horizon" / "block" / f"{name}.json",
        {
            "template": "minecraft:furnace",
            "properties": {"hardness": 2.0, "sounds": "minecraft:wood"},
            "item": True,
        },
    )
    tex = f"quests:block/{name}"
    write_json(
        ASSETS / "models" / "block" / f"{name}.json",
        {
            "parent": "minecraft:block/orientable",
            "textures": {
                "top": tex,
                "front": tex,
                "side": tex,
                "bottom": tex,
                "particle": tex,
            },
        },
    )
    write_json(ASSETS / "models" / "item" / f"{name}.json", {"parent": f"quests:block/{name}"})
    write_json(
        ASSETS / "items" / f"{name}.json",
        {"model": {"type": "minecraft:model", "model": f"quests:item/{name}"}},
    )
    variants = {}
    for facing, rot in (("north", None), ("south", 180), ("west", 270), ("east", 90)):
        for lit in ("false", "true"):
            entry: dict = {"model": f"quests:block/{name}"}
            if rot is not None:
                entry["y"] = rot
            variants[f"facing={facing},lit={lit}"] = entry
    write_json(ASSETS / "blockstates" / f"{name}.json", {"variants": variants})
    png(ASSETS / "textures" / "block" / f"{name}.png", (120, 80, 40))
    write_json(
        DATA / "horizon" / "menu" / f"{name}.json",
        {"slots": 3, "data_slots": 2, "results": [2]},
    )
    write_json(
        DATA / "loot_table" / "blocks" / f"{name}.json",
        {
            "type": "minecraft:block",
            "pools": [
                {
                    "rolls": 1,
                    "entries": [{"type": "minecraft:item", "name": f"quests:{name}"}],
                    "conditions": [{"condition": "minecraft:survives_explosion"}],
                }
            ],
        },
    )


def main() -> None:
    item_files("quest_book", (160, 100, 40), "minecraft:book")
    item_files("loot_crate", (140, 90, 50), "minecraft:chest")
    block_board()
    write_json(
        DATA / "horizon" / "creative_tab" / "quests.json",
        {
            "title": "Horizon Quests",
            "icon": "quests:quest_book",
            "items": ["quests:quest_book", "quests:loot_crate", "quests:quest_board"],
        },
    )
    write_json(
        ASSETS / "lang" / "en_us.json",
        {
            "item.quests.quest_book": "Quest Book",
            "item.quests.loot_crate": "Loot Crate",
            "block.quests.quest_board": "Quest Board",
        },
    )
    print(f"quests content under {ROOT}")


if __name__ == "__main__":
    main()
