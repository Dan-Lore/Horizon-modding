"""Compose proper 176x166 machine GUIs (not a blank tile stretch)."""
from __future__ import annotations

from pathlib import Path

from PIL import Image, ImageDraw

OUT = Path(__file__).resolve().parents[1] / "assets" / "gtceu" / "textures" / "gui"


def panel(w: int, h: int) -> Image.Image:
    img = Image.new("RGBA", (w, h), (198, 198, 198, 255))
    d = ImageDraw.Draw(img)
    # outer bevel
    d.rectangle([0, 0, w - 1, h - 1], outline=(255, 255, 255, 255))
    d.line([(0, h - 1), (w - 1, h - 1)], fill=(85, 85, 85, 255))
    d.line([(w - 1, 0), (w - 1, h - 1)], fill=(85, 85, 85, 255))
    d.rectangle([1, 1, w - 2, h - 2], outline=(198, 198, 198, 255))
    return img


def slot(img: Image.Image, x: int, y: int, size: int = 18) -> None:
    d = ImageDraw.Draw(img)
    # vanilla-ish slot well
    d.rectangle([x, y, x + size - 1, y + size - 1], fill=(139, 139, 139, 255))
    d.rectangle([x + 1, y + 1, x + size - 2, y + size - 2], fill=(55, 55, 55, 255))
    d.line([(x, y + size - 1), (x + size - 1, y + size - 1)], fill=(255, 255, 255, 255))
    d.line([(x + size - 1, y), (x + size - 1, y + size - 1)], fill=(255, 255, 255, 255))
    d.line([(x, y), (x + size - 2, y)], fill=(55, 55, 55, 255))
    d.line([(x, y), (x, y + size - 2)], fill=(55, 55, 55, 255))


def player_inv(img: Image.Image, ox: int = 7, oy: int = 83) -> None:
    for row in range(3):
        for col in range(9):
            slot(img, ox + col * 18, oy + row * 18)
    for col in range(9):
        slot(img, ox + col * 18, oy + 58)


def machine_gui() -> Image.Image:
    img = panel(176, 166)
    # processor: input + output
    slot(img, 52, 34)
    slot(img, 115, 34)
    player_inv(img)
    return img


def boiler_gui() -> Image.Image:
    img = panel(176, 166)
    slot(img, 79, 52)  # fuel
    player_inv(img)
    return img


def dual_gui() -> Image.Image:
    img = panel(176, 166)
    slot(img, 52, 24)
    slot(img, 70, 24)
    slot(img, 115, 34)
    player_inv(img)
    return img


def main() -> None:
    OUT.mkdir(parents=True, exist_ok=True)
    machine_gui().save(OUT / "steam_machine.png")
    boiler_gui().save(OUT / "steam_boiler.png")
    dual_gui().save(OUT / "steam_machine_dual.png")
    print(
        "wrote",
        (OUT / "steam_machine.png").stat().st_size,
        Image.open(OUT / "steam_machine.png").size,
    )


if __name__ == "__main__":
    main()
