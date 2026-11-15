#!/usr/bin/env python3
"""Generate Horizon Teams content textures (PIL RGBA for atlas)."""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "teams"
DATA = ROOT / "data" / "teams"


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def _shade(rgb: tuple[int, int, int], factor: float) -> tuple[int, int, int]:
    return tuple(max(0, min(255, int(c * factor))) for c in rgb)  # type: ignore[return-value]


def png_roster(path: Path) -> None:
    """Team roster clipboard icon — shaped PIL texture, not a flat slab."""
    rgb = (70, 120, 160)
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    hi, mid, lo = _shade(rgb, 1.25), rgb, _shade(rgb, 0.55)

    def fill_rect(xy: tuple[int, int, int, int], color: tuple[int, int, int]) -> None:
        d.rectangle(xy, fill=(*color, 255))

    # Clipboard body
    fill_rect((3, 2, 12, 14), mid)
    d.rectangle((3, 2, 12, 14), outline=(*hi, 255))
    # Clip
    fill_rect((5, 1, 10, 3), lo)
    fill_rect((6, 0, 9, 2), hi)
    # Lines
    d.line([(5, 6), (10, 6)], fill=(*hi, 255))
    d.line([(5, 9), (10, 9)], fill=(*hi, 255))
    d.line([(5, 12), (9, 12)], fill=(*hi, 255))
    # Noise
    for y in range(4, 13):
        for x in range(4, 12):
            if (x + y * 2) % 5 == 0:
                img.putpixel((x, y), (*_shade(mid, 0.9), 255))
    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)


def main() -> None:
    name = "team_roster"
    write_json(DATA / "horizon" / "item" / f"{name}.json", {"template": "minecraft:paper"})
    write_json(
        ASSETS / "models" / "item" / f"{name}.json",
        {"parent": "minecraft:item/generated", "textures": {"layer0": f"teams:item/{name}"}},
    )
    write_json(
        ASSETS / "items" / f"{name}.json",
        {"model": {"type": "minecraft:model", "model": f"teams:item/{name}"}},
    )
    png_roster(ASSETS / "textures" / "item" / f"{name}.png")
    write_json(
        ASSETS / "lang" / "en_us.json",
        {"item.teams.team_roster": "Team Roster"},
    )
    print(f"teams content under {ROOT}")


if __name__ == "__main__":
    main()
