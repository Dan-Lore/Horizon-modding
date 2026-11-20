#!/usr/bin/env python3
"""Player-facing Absolute TFG content score (resources / recipes / mechanics)."""

from __future__ import annotations

import collections
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

# Absolute denominators (achievable on this pin; #1/#2 excluded from "done").
# Evidence: GTM jar static models/item=2738 blockstates=1568 + runtime material dict
# (~617 colors × ~10 forms) → ~9k items / ~2k blocks. Recipes are code-gen (no jar JSON).
# Firmalife/Ad Astra from TFG instance jars. TFC jar absent locally → published-scale estimate.
ABSOLUTE = {
    "gtceu": {
        "items": 9000,
        "blocks": 2000,
        "recipes": 30000,
        "mechanics": 100.0,
    },
    "tfc": {"items": 2500, "blocks": 1500, "recipes": 4000, "mechanics": 100.0},
    "firmalife": {"items": 637, "blocks": 436, "recipes": 595, "mechanics": 100.0},
    "adastra": {"items": 413, "blocks": 333, "recipes": 534, "mechanics": 100.0},
    "quests": {"items": 20, "blocks": 5, "recipes": 1, "mechanics": 100.0},
    "teams": {"items": 10, "blocks": 1, "recipes": 1, "mechanics": 100.0},
}

# Rough mechanics completeness estimates (0–100) until we automate probes.
MECHANICS_EST = {
    "gtceu": 72.0,  # AE2 face ModContainer + fluidized chem; multis still thin
    "tfc": 56.0,  # AE2 bus faces + typed pan/barrel; animals/veins/climate #1
    "firmalife": 58.0,  # ModContainer for AE2 buses; vat/oven/drying; greenhouse weak
    "adastra": 44.0,  # AE2 bus faces + overworld FE/O2/NASA; planets #1
    "quests": 58.0,  # AE2→GT interface quests + Absolute surface
    "teams": 60.0,  # Absolute party surface + roster craft
}

MODS = [
    ("GregTech", "gtceu", "gtceu"),
    ("TerraFirmaCraft", "tfc", "tfc"),
    ("Firmalife", "firmalife", "firmalife"),
    ("Ad Astra", "adastra", "adastra"),
    ("FTB Quests", "quests", "quests"),
    ("FTB Teams", "teams", "teams"),
]

WEIGHTS = {"resources": 0.35, "recipes": 0.35, "mechanics": 0.30}

# Mod weights inside pack blend (GregTech dominates Absolute TFG).
MOD_WEIGHT = {
    "gtceu": 0.55,
    "tfc": 0.20,
    "firmalife": 0.08,
    "adastra": 0.08,
    "quests": 0.05,
    "teams": 0.04,
}


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


def clamp_pct(n: float, d: float) -> float:
    if d <= 0:
        return 0.0
    return max(0.0, min(100.0, 100.0 * n / d))


def mod_scores(folder: str, ns: str) -> dict:
    c = count_mod(folder, ns)
    abs_ = ABSOLUTE[ns]
    res_have = c["items"] + c["blocks"]
    res_need = abs_["items"] + abs_["blocks"]
    resources = clamp_pct(res_have, res_need)
    recipes = clamp_pct(c["recipes"], abs_["recipes"])
    mechanics = float(MECHANICS_EST.get(ns, 0.0))
    blend = (
        resources * WEIGHTS["resources"]
        + recipes * WEIGHTS["recipes"]
        + mechanics * WEIGHTS["mechanics"]
    )
    return {
        **c,
        "resources_pct": resources,
        "recipes_pct": recipes,
        "mechanics_pct": mechanics,
        "blend_pct": blend,
    }


def milestone_for(pack_blend: float) -> str:
    if pack_blend >= 95:
        return "M100"
    if pack_blend >= 70:
        return "M75"
    if pack_blend >= 45:
        return "M50"
    if pack_blend >= 22:
        return "M25"
    return "M0"


def main() -> None:
    print("Absolute TFG content score (achievable numerator; #1/#2 blocked out of done)\n")
    pack = 0.0
    rows = []
    for display, folder, ns in MODS:
        s = mod_scores(folder, ns)
        rows.append((display, ns, s))
        pack += s["blend_pct"] * MOD_WEIGHT[ns]
        print(
            f"{display:16} id={ns:10} items={s['items']:5} blocks={s['blocks']:4} "
            f"recipes={s['recipes']:5} | res={s['resources_pct']:5.1f}% "
            f"rcp={s['recipes_pct']:5.1f}% mech={s['mechanics_pct']:5.1f}% "
            f"blend={s['blend_pct']:5.1f}%"
        )
    ms = milestone_for(pack)
    print(f"\nPACK blend ≈ {pack:.1f}%   milestone={ms}")
    print("Blocked forever on this pin: Create/Greate (#2), dims/animals/explode (#1).")
    out = {
        "pack_blend_pct": round(pack, 2),
        "milestone": ms,
        "mods": {
            ns: {
                "items": s["items"],
                "blocks": s["blocks"],
                "recipes": s["recipes"],
                "resources_pct": round(s["resources_pct"], 2),
                "recipes_pct": round(s["recipes_pct"], 2),
                "mechanics_pct": round(s["mechanics_pct"], 2),
                "blend_pct": round(s["blend_pct"], 2),
            }
            for _, ns, s in rows
        },
    }
    dest = ROOT / "docs" / "tfg-content-score.json"
    dest.write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {dest.relative_to(ROOT)}")


if __name__ == "__main__":
    main()
