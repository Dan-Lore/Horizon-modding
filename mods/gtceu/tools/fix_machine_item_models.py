"""Machine/generator/multi inventory items: 3D block projection (not flat front)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ASSETS = ROOT / "assets" / "gtceu"
DATA = ROOT / "data" / "gtceu" / "horizon" / "block"


def write_json(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def main() -> None:
    n = 0
    for block_json in DATA.glob("*.json"):
        stem = block_json.stem
        if "_cable_" in stem:
            continue  # cables keep flat generated icons
        write_json(
            ASSETS / "models" / "item" / f"{stem}.json",
            {"parent": f"gtceu:block/{stem}"},
        )
        write_json(
            ASSETS / "items" / f"{stem}.json",
            {
                "model": {
                    "type": "minecraft:model",
                    "model": f"gtceu:item/{stem}",
                }
            },
        )
        n += 1
    print("3d block item models", n)


if __name__ == "__main__":
    main()
