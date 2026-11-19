#!/usr/bin/env python3
"""Original workshop textures for Horizon Quests / board (not FTB ARR art)."""

from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "assets" / "quests" / "textures"


def book() -> Image.Image:
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.rectangle([3, 1, 12, 14], fill=(90, 55, 30, 255), outline=(40, 25, 10, 255))
    d.rectangle([4, 2, 11, 13], fill=(240, 230, 200, 255))
    d.line([8, 2, 8, 13], fill=(90, 55, 30, 255))
    d.rectangle([5, 4, 7, 5], fill=(180, 60, 50, 255))
    return im


def board() -> Image.Image:
    im = Image.new("RGBA", (16, 16), (120, 85, 45, 255))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 15, 15], outline=(60, 40, 20, 255))
    for y in (3, 7, 11):
        d.rectangle([2, y, 13, y + 2], fill=(240, 230, 200, 255), outline=(80, 50, 25, 255))
        d.point([(3, y + 1)], fill=(200, 60, 50, 255))
    return im


def pin() -> Image.Image:
    im = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(im)
    d.ellipse([4, 2, 11, 9], fill=(200, 60, 50, 255), outline=(80, 20, 20, 255))
    d.polygon([(8, 8), (10, 14), (6, 14)], fill=(180, 180, 190, 255))
    return im


def crate() -> Image.Image:
    im = Image.new("RGBA", (16, 16), (140, 100, 50, 255))
    d = ImageDraw.Draw(im)
    d.rectangle([0, 0, 15, 15], outline=(60, 40, 20, 255))
    d.line([0, 5, 15, 5], fill=(60, 40, 20, 255))
    d.line([0, 10, 15, 10], fill=(60, 40, 20, 255))
    d.line([8, 0, 8, 15], fill=(60, 40, 20, 255))
    d.rectangle([5, 6, 10, 9], fill=(220, 180, 60, 255))
    return im


def main() -> None:
    mapping = {
        "item/quest_book.png": book,
        "block/quest_board.png": board,
        "item/quest_pin.png": pin,
        "item/loot_crate.png": crate,
    }
    for rel, fn in mapping.items():
        out = TEX / rel
        out.parent.mkdir(parents=True, exist_ok=True)
        fn().save(out, optimize=True)
        print("wrote", rel)

if __name__ == "__main__":
    main()
