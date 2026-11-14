"""Generate MV clones + copper cable content."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "greglite"
ASSETS = ROOT / "assets" / "greglite"


def write(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


MV = [
    ("mv_alloy_smelter", 3, [2]),
    ("mv_macerator", 2, [1]),
    ("mv_compressor", 2, [1]),
    ("mv_electric_furnace", 2, [1]),
    ("mv_steam_turbine", 1, []),
    ("copper_cable_1x", 0, []),
]


def main() -> None:
    for block, slots, results in MV:
        write(
            DATA / "horizon" / "block" / f"{block}.json",
            {
                "template": "minecraft:furnace",
                "properties": {"hardness": 3.5, "sounds": "minecraft:iron_block"},
                "item": True,
            },
        )
        write(
            DATA / "loot_table" / "blocks" / f"{block}.json",
            {
                "type": "minecraft:block",
                "pools": [
                    {
                        "rolls": 1,
                        "entries": [{"type": "minecraft:item", "name": f"greglite:{block}"}],
                        "conditions": [{"condition": "minecraft:survives_explosion"}],
                    }
                ],
            },
        )
        variants = {}
        for facing, y in [("north", 0), ("south", 180), ("west", 270), ("east", 90)]:
            for lit, suf in [(False, ""), (True, "_on")]:
                key = f"facing={facing},lit={str(lit).lower()}"
                m = {"model": f"greglite:block/{block}{suf}"}
                if y:
                    m["y"] = y
                variants[key] = m
        write(ASSETS / "blockstates" / f"{block}.json", {"variants": variants})
        tex = "lv_machine" if not block.startswith("copper") else "tin_cable_1x"
        for suf, front in (("", "front"), ("_on", "front_on")):
            write(
                ASSETS / "models" / "block" / f"{block}{suf}.json",
                {
                    "parent": "minecraft:block/orientable",
                    "textures": {
                        "top": f"greglite:block/{tex}_top",
                        "front": f"greglite:block/{tex}_{front}",
                        "side": f"greglite:block/{tex}_side",
                        "bottom": f"greglite:block/{tex}_bottom",
                        "particle": f"greglite:block/{tex}_side",
                    },
                },
            )
        write(
            ASSETS / "items" / f"{block}.json",
            {"model": {"type": "minecraft:model", "model": f"greglite:item/{block}"}},
        )
        write(
            ASSETS / "models" / "item" / f"{block}.json",
            {"parent": f"greglite:block/{block}"},
        )
        if slots > 0:
            write(
                DATA / "horizon" / "menu" / f"{block}.json",
                {"slots": slots, "data_slots": 4, "results": results},
            )

    lang_path = ASSETS / "lang" / "en_us.json"
    lang = json.loads(lang_path.read_text(encoding="utf-8"))
    for block, _, _ in MV:
        lang[f"block.greglite.{block}"] = block.replace("_", " ").title()
    lang_path.write_text(json.dumps(lang, indent=2) + "\n", encoding="utf-8")

    tab = DATA / "horizon" / "creative_tab" / "greglite.json"
    obj = json.loads(tab.read_text(encoding="utf-8"))
    for block, _, _ in MV:
        item = f"greglite:{block}"
        if item not in obj["items"]:
            obj["items"].append(item)
    tab.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")

    tag = ROOT / "data" / "minecraft" / "tags" / "block" / "mineable" / "pickaxe.json"
    t = json.loads(tag.read_text(encoding="utf-8"))
    for block, _, _ in MV:
        v = f"greglite:{block}"
        if v not in t["values"]:
            t["values"].append(v)
    tag.write_text(json.dumps(t, indent=2) + "\n", encoding="utf-8")
    print("mv content ok", len(MV))


if __name__ == "__main__":
    main()
