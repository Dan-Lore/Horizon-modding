#!/usr/bin/env python3
"""Generate Horizon Teams Absolute surface (FTB Teams has no item models in jar).

Absolute scoreboard: 10 items / 1 block / ≥1 recipe. Placeholders — ARR art not copied.
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "teams"
DATA = ROOT / "data" / "teams"

# 9 pure items + team_banner block item = 10 Absolute items.
ITEMS: list[tuple[str, tuple[int, int, int], str]] = [
    ("team_roster", (70, 120, 160), "minecraft:paper"),
    ("party_invite", (80, 160, 120), "minecraft:paper"),
    ("team_badge", (200, 160, 40), "minecraft:paper"),
    ("team_flag", (180, 60, 60), "minecraft:paper"),
    ("team_chat_key", (100, 100, 180), "minecraft:paper"),
    ("ally_token", (60, 160, 80), "minecraft:paper"),
    ("enemy_token", (160, 60, 60), "minecraft:paper"),
    ("party_warp", (120, 80, 180), "minecraft:ender_pearl"),
    ("team_home", (140, 100, 60), "minecraft:paper"),
]


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def _shade(rgb: tuple[int, int, int], factor: float) -> tuple[int, int, int]:
    return tuple(max(0, min(255, int(c * factor))) for c in rgb)  # type: ignore[return-value]


def png_item(path: Path, rgb: tuple[int, int, int], kind: str) -> None:
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    hi, mid, lo = _shade(rgb, 1.25), rgb, _shade(rgb, 0.55)

    def fill_rect(xy: tuple[int, int, int, int], color: tuple[int, int, int]) -> None:
        d.rectangle(xy, fill=(*color, 255))

    if kind == "team_roster":
        fill_rect((3, 2, 12, 14), mid)
        d.rectangle((3, 2, 12, 14), outline=(*hi, 255))
        fill_rect((5, 1, 10, 3), lo)
        fill_rect((6, 0, 9, 2), hi)
        d.line([(5, 6), (10, 6)], fill=(*hi, 255))
        d.line([(5, 9), (10, 9)], fill=(*hi, 255))
        d.line([(5, 12), (9, 12)], fill=(*hi, 255))
    else:
        fill_rect((2, 2, 13, 13), mid)
        d.rectangle((2, 2, 13, 13), outline=(*hi, 255))
        for y in range(3, 13):
            for x in range(3, 13):
                if (x + y * 2) % 5 == 0:
                    img.putpixel((x, y), (*_shade(mid, 0.9), 255))
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)


def item_files(name: str, rgb: tuple[int, int, int], template: str) -> None:
    write_json(DATA / "horizon" / "item" / f"{name}.json", {"template": template})
    write_json(
        ASSETS / "models" / "item" / f"{name}.json",
        {"parent": "minecraft:item/generated", "textures": {"layer0": f"teams:item/{name}"}},
    )
    write_json(
        ASSETS / "items" / f"{name}.json",
        {"model": {"type": "minecraft:model", "model": f"teams:item/{name}"}},
    )
    png_item(ASSETS / "textures" / "item" / f"{name}.png", rgb, name)


def team_banner_block() -> None:
    name = "team_banner"
    write_json(
        DATA / "horizon" / "block" / f"{name}.json",
        {
            "template": "minecraft:iron_block",
            "properties": {"hardness": 1.0, "sounds": "minecraft:oak_planks"},
            "item": True,
        },
    )
    tex = f"teams:block/{name}"
    write_json(
        ASSETS / "models" / "block" / f"{name}.json",
        {"parent": "minecraft:block/cube_all", "textures": {"all": tex}},
    )
    write_json(ASSETS / "models" / "item" / f"{name}.json", {"parent": f"teams:block/{name}"})
    write_json(
        ASSETS / "items" / f"{name}.json",
        {"model": {"type": "minecraft:model", "model": f"teams:item/{name}"}},
    )
    write_json(
        ASSETS / "blockstates" / f"{name}.json",
        {"variants": {"": {"model": f"teams:block/{name}"}}},
    )
    png_item(ASSETS / "textures" / "block" / f"{name}.png", (70, 120, 160), "banner")
    write_json(
        DATA / "loot_table" / "blocks" / f"{name}.json",
        {
            "type": "minecraft:block",
            "pools": [
                {
                    "rolls": 1,
                    "entries": [{"type": "minecraft:item", "name": f"teams:{name}"}],
                    "conditions": [{"condition": "minecraft:survives_explosion"}],
                }
            ],
        },
    )


def title_case(name: str) -> str:
    return " ".join(p.capitalize() for p in name.split("_"))


def main() -> None:
    for name, rgb, template in ITEMS:
        item_files(name, rgb, template)
    team_banner_block()

    item_ids = [f"teams:{n}" for n, *_ in ITEMS] + ["teams:team_banner"]
    write_json(
        DATA / "horizon" / "creative_tab" / "teams.json",
        {
            "title": "Horizon Teams",
            "icon": "teams:team_roster",
            "items": item_ids,
        },
    )
    lang = {f"item.teams.{n}": title_case(n) for n, *_ in ITEMS}
    lang["block.teams.team_banner"] = "Team Banner"
    lang["item.teams.team_banner"] = "Team Banner"
    write_json(ASSETS / "lang" / "en_us.json", lang)

    write_json(
        DATA / "recipe" / "team_roster.json",
        {
            "type": "minecraft:crafting_shapeless",
            "ingredients": [
                {"item": "minecraft:paper"},
                {"item": "minecraft:ink_sac"},
            ],
            "result": {"id": "teams:team_roster", "count": 1},
        },
    )

    items_n = len(list((ASSETS / "items").glob("*.json")))
    blocks_n = len(list((ASSETS / "blockstates").glob("*.json")))
    print(f"teams content under {ROOT}: items={items_n} blocks={blocks_n}")


if __name__ == "__main__":
    main()
