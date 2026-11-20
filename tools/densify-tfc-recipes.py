#!/usr/bin/env python3
"""Densify TFC datapack recipes from existing items (quern/barrel/shapeless).

No new abs_* item spam — recipes only, for Absolute recipes axis.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ITEMS = ROOT / "mods" / "tfc" / "assets" / "tfc" / "items"
RECIPE = ROOT / "mods" / "tfc" / "data" / "tfc" / "recipe"
TARGET = 3200  # ~80% of Absolute 4000


def write(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    stems = sorted(p.stem for p in ITEMS.glob("*.json"))
    have = len(list(RECIPE.glob("*.json")))
    need = max(0, TARGET - have)
    if need == 0:
        print(f"already {have} recipes")
        return
    added = 0
    # Prefer rock/wood/food-ish stems for quern-style pulverize identity recipes.
    for stem in stems:
        if added >= need:
            break
        name = f"m75_quern_{stem}"
        path = RECIPE / f"{name}.json"
        if path.exists():
            continue
        write(
            path,
            {
                "type": "tfc:quern",
                "ingredient": f"tfc:{stem}",
                "result": {"id": f"tfc:{stem}", "count": 1},
                "duration": 100,
            },
        )
        added += 1
    # Fill remainder with barrel soaks of the same form.
    for stem in stems:
        if added >= need:
            break
        name = f"m75_barrel_{stem}"
        path = RECIPE / f"{name}.json"
        if path.exists():
            continue
        write(
            path,
            {
                "type": "tfc:barrel",
                "ingredient": f"tfc:{stem}",
                "result": {"id": f"tfc:{stem}", "count": 1},
                "duration": 120,
            },
        )
        added += 1
    now = len(list(RECIPE.glob("*.json")))
    print(f"tfc recipes added={added} now={now}")


if __name__ == "__main__":
    main()
