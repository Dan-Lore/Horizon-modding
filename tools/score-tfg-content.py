#!/usr/bin/env python3
"""Print player-facing TFG content counts for docs/tfg-content-coverage.md."""

from __future__ import annotations

import collections
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

MODS = [
    ("GregTech", "greglite", "greglite"),
    ("TerraFirmaCraft", "tfc", "tfc"),
    ("Firmalife", "firmalife", "firmalife"),
    ("Ad Astra", "adastra", "adastra"),
    ("FTB Quests", "quests", "quests"),
    ("FTB Teams", "teams", "teams"),
]


def count_mod(folder: str, ns: str) -> dict:
    root = ROOT / "mods" / folder
    items_dir = root / "assets" / ns / "items"
    blocks_dir = root / "assets" / ns / "blockstates"
    recipe_dir = root / "data" / ns / "recipe"
    items = len(list(items_dir.glob("*.json"))) if items_dir.is_dir() else 0
    blocks = len(list(blocks_dir.glob("*.json"))) if blocks_dir.is_dir() else 0
    types: collections.Counter[str] = collections.Counter()
    recipes = 0
    if recipe_dir.is_dir():
        for path in recipe_dir.glob("*.json"):
            try:
                data = json.loads(path.read_text(encoding="utf-8"))
            except (OSError, json.JSONDecodeError):
                continue
            recipes += 1
            types[str(data.get("type", "?"))] += 1
    return {
        "items": items,
        "blocks": blocks,
        "recipes": recipes,
        "recipe_types": len(types),
        "top_types": types.most_common(8),
    }


def main() -> None:
    print("TFG content counts (ours only — not Absolute parity)\n")
    for display, folder, ns in MODS:
        c = count_mod(folder, ns)
        print(
            f"{display:16} id={ns:10} items={c['items']:5} blocks={c['blocks']:4} "
            f"recipes={c['recipes']:5} types={c['recipe_types']:3}"
        )
        for typ, n in c["top_types"][:5]:
            print(f"                 {n:4}  {typ}")
    print(
        "\nRe-read docs/tfg-content-coverage.md for weighted % vs TFG. "
        "Do not treat catalog #4 '100%' as pack completeness."
    )


if __name__ == "__main__":
    main()
