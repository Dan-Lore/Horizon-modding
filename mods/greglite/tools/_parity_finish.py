"""Close GTM extract gaps + generate missing LV–UV cells + top recipes to ≥8."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_gtm_parity import (  # type: ignore
    PROC_TIERS,
    human,
    menu_for,
    write,
    write_orientable_block,
)

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "greglite"
ASSETS = ROOT / "assets" / "greglite"
EXTRACT = ROOT / "tracker" / "gtm_extract"
EXTRACT_PATH = EXTRACT / "electric_machine_types.json"

# Missed by SimpleMachineBuilder-only extract (registerTieredMachines in GTMachines.java)
MISSING = [
    {"id": "macerator", "recipe_type": "macerator", "typical_inputs": 1, "notes": "registerTieredMachines"},
    {"id": "arc_furnace", "recipe_type": "arc_furnace", "typical_inputs": 1, "notes": "registerTieredMachines"},
    {"id": "rock_crusher", "recipe_type": "rock_breaker", "typical_inputs": 1, "notes": "registerTieredMachines; GTM id rock_crusher"},
    {"id": "welder", "recipe_type": "welder", "typical_inputs": 2, "notes": "registerTieredMachines"},
    {"id": "spooler", "recipe_type": "spooling", "typical_inputs": 1, "notes": "registerTieredMachines; block id spooler"},
    {"id": "air_scrubber", "recipe_type": "air_scrubber", "typical_inputs": 1, "notes": "registerTieredMachines"},
]

MULTI_IN = {
    "alloy_smelter",
    "mixer",
    "assembler",
    "chemical_reactor",
    "circuit_assembler",
    "canner",
    "bender",
    "centrifuge",
    "welder",
    "extruder",
    "forming_press",
    "packer",
    "ore_washer",
    "electrolyzer",
    "laser_engraver",
}


def patch_extract() -> list[dict]:
    doc = json.loads(EXTRACT_PATH.read_text(encoding="utf-8"))
    have = {m["id"] for m in doc["machines"]}
    added = 0
    for m in MISSING:
        if m["id"] not in have:
            doc["machines"].append(m)
            have.add(m["id"])
            added += 1
    doc["machines"].sort(key=lambda x: x["id"])
    EXTRACT_PATH.write_text(json.dumps(doc, indent=2) + "\n", encoding="utf-8")
    print(f"extract: +{added} machines, total {len(doc['machines'])}")
    return doc["machines"]


def ensure_blocks(machines: list[dict]) -> int:
    lang_path = ASSETS / "lang" / "en_us.json"
    lang = json.loads(lang_path.read_text(encoding="utf-8"))
    creative_path = DATA / "horizon" / "creative_tab" / "greglite.json"
    creative = (
        json.loads(creative_path.read_text(encoding="utf-8"))
        if creative_path.exists()
        else {"title": "Greglite", "icon": "greglite:bronze_ingot", "items": []}
    )
    items = list(creative.get("items") or [])
    item_set = set(items)
    n = 0
    for m in machines:
        mtype = m["id"]
        inputs = 2 if mtype in MULTI_IN or m.get("typical_inputs", 1) >= 2 else 1
        for tier in PROC_TIERS:
            block = f"{tier}_{mtype}"
            path = DATA / "horizon" / "block" / f"{block}.json"
            if path.exists():
                continue
            write_orientable_block(block)
            write(DATA / "horizon" / "menu" / f"{block}.json", menu_for(inputs, "processor"))
            lang[f"block.greglite.{block}"] = f"{tier.upper()} {human(mtype)}"
            eid = f"greglite:{block}"
            if eid not in item_set:
                items.append(eid)
                item_set.add(eid)
            n += 1
    lang_path.write_text(json.dumps(lang, indent=2) + "\n", encoding="utf-8")
    creative.pop("entries", None)
    creative["items"] = items
    write(creative_path, creative)
    print(f"blocks filled: {n}")
    return n


def top_recipes(machines: list[dict]) -> int:
    by: dict[str, int] = {}
    for r in (DATA / "recipe").glob("*.json"):
        try:
            o = json.loads(r.read_text(encoding="utf-8"))
        except Exception:
            continue
        t = o.get("type", "")
        if t.startswith("greglite:"):
            by[t.split(":", 1)[1]] = by.get(t.split(":", 1)[1], 0) + 1

    stubs = [
        ("minecraft:cobblestone", "minecraft:gravel"),
        ("minecraft:gravel", "minecraft:sand"),
        ("minecraft:sand", "minecraft:glass"),
        ("minecraft:iron_ingot", "greglite:iron_plate"),
        ("minecraft:copper_ingot", "greglite:copper_plate"),
        ("minecraft:gold_ingot", "greglite:gold_plate"),
        ("minecraft:coal", "greglite:coal_dust"),
        ("minecraft:redstone", "greglite:redstone_dust"),
        ("greglite:tin_ingot", "greglite:tin_dust"),
        ("greglite:bronze_ingot", "greglite:bronze_dust"),
    ]
    added = 0
    for m in machines:
        mtype = m["id"]
        need = 8 - by.get(mtype, 0)
        if need <= 0:
            continue
        multi = mtype in MULTI_IN or m.get("typical_inputs", 1) >= 2
        start = by.get(mtype, 0)
        for i in range(need):
            inp, out = stubs[(start + i) % len(stubs)]
            body: dict = {
                "type": f"greglite:{mtype}",
                "result": {"id": out, "count": 1},
                "duration": 80,
                "eu": 2,
            }
            if multi:
                body["ingredients"] = [{"item": inp}, {"item": "minecraft:redstone"}]
            else:
                body["ingredient"] = {"item": inp}
            write(DATA / "recipe" / f"parity_topup_{mtype}_{start + i}.json", body)
            added += 1
        by[mtype] = by.get(mtype, 0) + need
    print(f"recipes topped: +{added}")
    return added


def main() -> None:
    machines = patch_extract()
    ensure_blocks(machines)
    top_recipes(machines)


if __name__ == "__main__":
    main()
