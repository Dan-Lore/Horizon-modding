#!/usr/bin/env python3
"""Generate Horizon Quests content (book, board, loot crate) + 26.3 items/ defs.

Textures use PIL (RGBA) so Horizon atlases them — same path as TFC/Greglite.
"""

from __future__ import annotations

import json
from pathlib import Path

from PIL import Image, ImageDraw

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "quests"
DATA = ROOT / "data" / "quests"
TABLES = ROOT / "tables"
BAKED = ROOT / "api" / "src" / "baked.rs"


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def _shade(rgb: tuple[int, int, int], factor: float) -> tuple[int, int, int]:
    return tuple(max(0, min(255, int(c * factor))) for c in rgb)  # type: ignore[return-value]


def png(path: Path, rgb: tuple[int, int, int], shape: str = "flat") -> None:
    """Write textures with PIL so Horizon atlases them (not flat zlib slabs)."""
    img = Image.new("RGBA", (16, 16), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    hi, mid, lo = _shade(rgb, 1.2), rgb, _shade(rgb, 0.55)

    def fill_rect(xy: tuple[int, int, int, int], color: tuple[int, int, int]) -> None:
        d.rectangle(xy, fill=(*color, 255))

    if shape == "book":
        fill_rect((3, 1, 12, 14), mid)
        fill_rect((4, 2, 11, 13), hi)
        d.line([(5, 4), (10, 4)], fill=(*lo, 255))
        d.line([(5, 7), (10, 7)], fill=(*lo, 255))
        d.line([(5, 10), (9, 10)], fill=(*lo, 255))
        fill_rect((2, 1, 3, 14), lo)
    elif shape == "crate":
        fill_rect((2, 3, 13, 13), mid)
        d.rectangle((2, 3, 13, 13), outline=(*hi, 255))
        fill_rect((2, 3, 13, 6), lo)
        d.line([(7, 3), (7, 13)], fill=(*hi, 255))
        d.line([(2, 8), (13, 8)], fill=(*lo, 255))
    elif shape == "block" or shape == "flat":
        fill_rect((0, 0, 15, 15), mid)
        d.rectangle((0, 0, 15, 15), outline=(*hi, 255))
        d.rectangle((1, 1, 14, 14), outline=(*lo, 255))
        for y in range(2, 14):
            for x in range(2, 14):
                if (x * 3 + y * 5) % 7 == 0:
                    img.putpixel((x, y), (*_shade(mid, 0.85), 255))
        # Board face: parchment panel
        fill_rect((4, 4, 11, 11), hi)
        d.line([(5, 6), (10, 6)], fill=(*lo, 255))
        d.line([(5, 8), (10, 8)], fill=(*lo, 255))
        d.line([(5, 10), (9, 10)], fill=(*lo, 255))
    else:
        fill_rect((2, 2, 13, 13), mid)

    path.parent.mkdir(parents=True, exist_ok=True)
    img.save(path)


def item_files(name: str, rgb: tuple[int, int, int], template: str, shape: str) -> None:
    write_json(DATA / "horizon" / "item" / f"{name}.json", {"template": template})
    write_json(
        ASSETS / "models" / "item" / f"{name}.json",
        {"parent": "minecraft:item/generated", "textures": {"layer0": f"quests:item/{name}"}},
    )
    write_json(
        ASSETS / "items" / f"{name}.json",
        {"model": {"type": "minecraft:model", "model": f"quests:item/{name}"}},
    )
    png(ASSETS / "textures" / "item" / f"{name}.png", rgb, shape)


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
    png(ASSETS / "textures" / "block" / f"{name}.png", (120, 80, 40), "block")
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


def rust_str(s: str) -> str:
    return s.replace("\\", "\\\\").replace('"', '\\"')


def bake_questfile() -> None:
    """Regenerate api/src/baked.rs from tables/questfile.json."""
    data = json.loads((TABLES / "questfile.json").read_text(encoding="utf-8"))
    lines: list[str] = [
        "//! Generated from tables/questfile.json — do not edit by hand.",
        "use super::file::{Chapter, Quest, QuestFile, Reward, TableEntry, Task};",
        "use std::collections::HashMap;",
        "",
        "pub fn baked() -> QuestFile {",
        "    let mut quests = HashMap::new();",
    ]
    for q in data["quests"]:
        tasks = []
        for t in q["tasks"]:
            tasks.append(
                "Task { id: \""
                + rust_str(t["id"])
                + "\".into(), kind: \""
                + rust_str(t["type"])
                + "\".into(), title: \""
                + rust_str(t["title"])
                + "\".into(), item: "
                + (
                    f'Some("{rust_str(t["item"])}".into())'
                    if t.get("item")
                    else "None"
                )
                + f", count: {int(t.get('count', 1))}, x: {int(t.get('x', 0))}, "
                f"y: {int(t.get('y', 64))}, z: {int(t.get('z', 0))}, "
                f"radius: {int(t.get('radius', 8))} }}"
            )
        rewards = []
        for r in q["rewards"]:
            opts = []
            for o in r.get("options") or []:
                opts.append(f'("{rust_str(o["item"])}".into(), {int(o.get("count", 1))})')
            rewards.append(
                "Reward { id: \""
                + rust_str(r["id"])
                + "\".into(), kind: \""
                + rust_str(r["type"])
                + "\".into(), item: "
                + (
                    f'Some("{rust_str(r["item"])}".into())'
                    if r.get("item")
                    else "None"
                )
                + f", count: {int(r.get('count', 1))}, amount: {int(r.get('amount', 0))}, "
                "command: "
                + (
                    f'Some("{rust_str(r["command"])}".into())'
                    if r.get("command")
                    else "None"
                )
                + ", table: "
                + (
                    f'Some("{rust_str(r["table"])}".into())'
                    if r.get("table")
                    else "None"
                )
                + ", options: vec!["
                + ", ".join(opts)
                + "] }"
            )
        deps = ", ".join(f'"{rust_str(d)}".into()' for d in q.get("dependencies") or [])
        lines.append(f'    quests.insert("{rust_str(q["id"])}".into(), Quest {{')
        lines.append(f'        id: "{rust_str(q["id"])}".into(),')
        lines.append(f'        title: "{rust_str(q["title"])}".into(),')
        lines.append(f"        dependencies: vec![{deps}],")
        lines.append(f"        tasks: vec![{', '.join(tasks)}],")
        lines.append(f"        rewards: vec![{', '.join(rewards)}],")
        lines.append("    });")
    lines.append("    let chapters = vec![")
    for c in data["chapters"]:
        qs = ", ".join(f'"{rust_str(q)}".into()' for q in c["quests"])
        lines.append(
            f'        Chapter {{ id: "{rust_str(c["id"])}".into(), '
            f'title: "{rust_str(c["title"])}".into(), '
            f'progression: "{rust_str(c["progression"])}".into(), '
            f"quests: vec![{qs}] }},"
        )
    lines.append("    ];")
    lines.append("    let mut tables = HashMap::new();")
    for table in data.get("reward_tables") or []:
        entries = []
        for e in table["entries"]:
            entries.append(
                f'TableEntry {{ item: "{rust_str(e["item"])}".into(), '
                f'count: {int(e["count"])}, weight: {int(e["weight"])} }}'
            )
        lines.append(
            f'    tables.insert("{rust_str(table["id"])}".into(), '
            f"vec![{', '.join(entries)}]);"
        )
    lines.append("    let mut themes = HashMap::new();")
    for tid, theme in (data.get("themes") or {}).items():
        accent = theme.get("accent", "§6") if isinstance(theme, dict) else str(theme)
        lines.append(f'    themes.insert("{rust_str(tid)}".into(), "{rust_str(accent)}".into());')
    default = data.get("theme_default", "copper")
    lines.append(
        f'    QuestFile {{ chapters, quests, tables, themes, theme_default: "{rust_str(default)}".into() }}'
    )
    lines.append("}")
    lines.append("")
    BAKED.parent.mkdir(parents=True, exist_ok=True)
    BAKED.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    item_files("quest_book", (160, 100, 40), "minecraft:book", "book")
    item_files("loot_crate", (140, 90, 50), "minecraft:chest", "crate")
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
    bake_questfile()
    print(f"quests content under {ROOT}")


if __name__ == "__main__":
    main()
