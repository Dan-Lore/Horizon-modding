#!/usr/bin/env python3
"""Add fluid_in to existing abs_* chem/wash recipes (no new abs catalog).

Targets: chemical_bath, ore_washer, chemical_reactor, distillery.
Does not change item IO. Idempotent.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RECIPE = ROOT / "data" / "gtceu" / "recipe"

# type -> (fluid id, amount mB)
FLUID_FOR = {
    "gtceu:chemical_bath": ("minecraft:water", 100),
    "gtceu:ore_washer": ("minecraft:water", 100),
    "gtceu:chemical_reactor": ("minecraft:water", 200),
    "gtceu:distillery": ("minecraft:water", 500),
}


def main() -> None:
    touched = 0
    skipped = 0
    for path in RECIPE.glob("abs_*.json"):
        try:
            data = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        rtype = data.get("type")
        if rtype not in FLUID_FOR:
            continue
        if "fluid_in" in data:
            skipped += 1
            continue
        fid, amount = FLUID_FOR[rtype]
        data["fluid_in"] = {"id": fid, "amount": amount}
        path.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
        touched += 1
    print(f"fluidized={touched} already_had={skipped}")


if __name__ == "__main__":
    main()
