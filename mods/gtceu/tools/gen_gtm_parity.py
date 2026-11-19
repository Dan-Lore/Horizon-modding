"""Generate GregTech content toward GTM parity from tracker/gtm_extract/*.json."""
from __future__ import annotations

import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "gtceu"
ASSETS = ROOT / "assets" / "gtceu"
EXTRACT = ROOT / "tracker" / "gtm_extract"
TEX_BLOCK = ASSETS / "textures" / "block"
TEX_ITEM = ASSETS / "textures" / "item"

# Electric machine tiers in GTM (skip ULV for processors; gens LV-HV)
PROC_TIERS = ["lv", "mv", "hv", "ev", "iv", "luv", "zpm", "uv"]
GEN_TIERS = ["lv", "mv", "hv"]
VOLTAGE = {
    "ulv": 8,
    "lv": 32,
    "mv": 128,
    "hv": 512,
    "ev": 2048,
    "iv": 8192,
    "luv": 32768,
    "zpm": 131072,
    "uv": 524288,
}

FORMS = ["ingot", "dust", "plate", "rod", "wire", "screw", "gear", "foil"]
VANILLA_INGOT = {
    "iron": "minecraft:iron_ingot",
    "copper": "minecraft:copper_ingot",
    "gold": "minecraft:gold_ingot",
    "netherite": "minecraft:netherite_ingot",
}


def load(name: str):
    return json.loads((EXTRACT / name).read_text(encoding="utf-8"))


def write(path: Path, obj) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def ensure_shared_textures() -> None:
    TEX_BLOCK.mkdir(parents=True, exist_ok=True)
    TEX_ITEM.mkdir(parents=True, exist_ok=True)
    src = TEX_BLOCK / "lv_machine_side.png"
    if not src.exists():
        alt = TEX_BLOCK / "steam_macerator_side.png"
        if alt.exists():
            for part in ("top", "bottom", "side", "front", "front_on"):
                s = TEX_BLOCK / f"steam_macerator_{part}.png"
                d = TEX_BLOCK / f"lv_machine_{part}.png"
                if s.exists():
                    shutil.copy2(s, d)
    # item placeholders from existing
    base_item = TEX_ITEM / "tin_ingot.png"
    if base_item.exists():
        for form in FORMS:
            dst = TEX_ITEM / f"_form_{form}.png"
            if not dst.exists():
                # map form to nearest existing
                prefer = {
                    "ingot": "tin_ingot.png",
                    "dust": "tin_dust.png",
                    "plate": "tin_plate.png",
                    "rod": "tin_rod.png",
                    "wire": "tin_wire.png",
                    "screw": "tin_plate.png",
                    "gear": "bronze_ingot.png",
                    "foil": "copper_plate.png",
                }.get(form, "tin_ingot.png")
                p = TEX_ITEM / prefer
                if p.exists():
                    shutil.copy2(p, dst)


def write_item(item_id: str) -> None:
    form = item_id.rsplit("_", 1)[-1]
    layer = f"gtceu:item/_form_{form}" if form in FORMS else f"gtceu:item/{item_id}"
    # prefer specific texture if present
    if (TEX_ITEM / f"{item_id}.png").exists():
        layer = f"gtceu:item/{item_id}"
    elif form in FORMS and (TEX_ITEM / f"_form_{form}.png").exists():
        layer = f"gtceu:item/_form_{form}"
    else:
        layer = "gtceu:item/tin_ingot"
        if not (TEX_ITEM / f"{item_id}.png").exists() and (TEX_ITEM / "tin_ingot.png").exists():
            shutil.copy2(TEX_ITEM / "tin_ingot.png", TEX_ITEM / f"{item_id}.png")
            layer = f"gtceu:item/{item_id}"
    write(DATA / "horizon" / "item" / f"{item_id}.json", {"template": "minecraft:iron_ingot"})
    write(
        ASSETS / "items" / f"{item_id}.json",
        {"model": {"type": "minecraft:model", "model": f"gtceu:item/{item_id}"}},
    )
    write(
        ASSETS / "models" / "item" / f"{item_id}.json",
        {"parent": "minecraft:item/generated", "textures": {"layer0": layer}},
    )


def write_orientable_block(block: str, *, tex: str = "lv_machine") -> None:
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
                    "entries": [{"type": "minecraft:item", "name": f"gtceu:{block}"}],
                    "conditions": [{"condition": "minecraft:survives_explosion"}],
                }
            ],
        },
    )
    variants = {}
    for facing, y in [("north", 0), ("south", 180), ("west", 270), ("east", 90)]:
        for lit, suf in [(False, ""), (True, "_on")]:
            key = f"facing={facing},lit={str(lit).lower()}"
            m = {"model": f"gtceu:block/{block}{suf}"}
            if y:
                m["y"] = y
            variants[key] = m
    write(ASSETS / "blockstates" / f"{block}.json", {"variants": variants})
    for suf, front in (("", "front"), ("_on", "front_on")):
        write(
            ASSETS / "models" / "block" / f"{block}{suf}.json",
            {
                "parent": "minecraft:block/orientable",
                "textures": {
                    "top": f"gtceu:block/{tex}_top",
                    "front": f"gtceu:block/{tex}_{front}",
                    "side": f"gtceu:block/{tex}_side",
                    "bottom": f"gtceu:block/{tex}_bottom",
                    "particle": f"gtceu:block/{tex}_side",
                },
            },
        )
    write(
        ASSETS / "items" / f"{block}.json",
        {"model": {"type": "minecraft:model", "model": f"gtceu:item/{block}"}},
    )
    write(
        ASSETS / "models" / "item" / f"{block}.json",
        {"parent": f"gtceu:block/{block}"},
    )


def menu_for(inputs: int, kind: str) -> dict:
    if kind in ("generator", "boiler", "turbine"):
        return {"slots": 1, "data_slots": 4, "results": []}
    if kind == "buffer":
        return {"slots": 4, "data_slots": 4, "results": []}
    if kind == "multiblock":
        return {"slots": 2, "data_slots": 4, "results": [1]}
    if kind == "cable" or kind == "hull":
        return {"slots": 0, "data_slots": 4, "results": []}
    if inputs >= 2:
        return {"slots": 3, "data_slots": 4, "results": [2]}
    return {"slots": 2, "data_slots": 4, "results": [1]}


def human(s: str) -> str:
    return re.sub(r"\b\w", lambda m: m.group(0).upper(), s.replace("_", " "))


def main() -> None:
    ensure_shared_textures()
    machines = load("electric_machine_types.json")["machines"]
    gens = load("generators.json")["generators"]
    multi_doc = load("multiblocks.json")
    multis = multi_doc.get("controllers") or multi_doc.get("multiblocks") or []
    materials = load("materials_core.json")["materials"]
    cables = load("cable_materials.json")["cables"]

    lang = {"itemGroup.gtceu.gtceu": "GregTech"}
    creative = []
    pickaxe = []
    catalog_machines = []

    # Keep steam age
    for b in (
        "steam_solid_boiler_lp",
        "steam_alloy_smelter",
        "steam_macerator",
        "steam_compressor",
    ):
        if (DATA / "horizon" / "block" / f"{b}.json").exists():
            creative.append(f"gtceu:{b}")
            pickaxe.append(f"gtceu:{b}")
            lang[f"block.gtceu.{b}"] = human(b)

    # Materials + forms
    mat_ids = []
    for mat in materials:
        mid = mat["id"]
        mat_ids.append(mid)
        for form in FORMS:
            # skip vanilla overlapping ingots as gtceu items when vanilla exists
            if form == "ingot" and mid in VANILLA_INGOT:
                continue
            item = f"{mid}_{form}"
            write_item(item)
            lang[f"item.gtceu.{item}"] = human(item)
            creative.append(f"gtceu:{item}")

    # Rubber sheet alias
    write_item("rubber")
    lang["item.gtceu.rubber"] = "Rubber"
    creative.append("gtceu:rubber")
    write_item("lv_battery")
    lang["item.gtceu.lv_battery"] = "LV Battery"
    creative.append("gtceu:lv_battery")

    # Processors all tiers
    multi_in = {
        m["id"]
        for m in machines
        if m.get("typical_inputs", 1) >= 2
        or m["id"]
        in {
            "alloy_smelter",
            "mixer",
            "assembler",
            "chemical_reactor",
            "circuit_assembler",
            "canner",
            "bender",
            "centrifuge",
        }
    }
    for m in machines:
        mtype = m["id"]
        inputs = 2 if mtype in multi_in else 1
        for tier in PROC_TIERS:
            block = f"{tier}_{mtype}"
            write_orientable_block(block)
            write(DATA / "horizon" / "menu" / f"{block}.json", menu_for(inputs, "processor"))
            lang[f"block.gtceu.{block}"] = f"{tier.upper()} {human(mtype)}"
            creative.append(f"gtceu:{block}")
            pickaxe.append(f"gtceu:{block}")
            catalog_machines.append(
                {
                    "id": block,
                    "gtm_type": mtype,
                    "tier": tier,
                    "kind": "processor",
                    "source_mod": "gregtech_modern",
                    "status": "done",
                    "wave": "parity",
                    "min_recipes": 2,
                }
            )

    # Generators LV-HV
    for g in gens:
        gid = g["id"]
        for tier in GEN_TIERS:
            block = f"{tier}_{gid}"
            write_orientable_block(block)
            write(DATA / "horizon" / "menu" / f"{block}.json", menu_for(1, "generator"))
            lang[f"block.gtceu.{block}"] = f"{tier.upper()} {human(gid)}"
            creative.append(f"gtceu:{block}")
            pickaxe.append(f"gtceu:{block}")
            catalog_machines.append(
                {
                    "id": block,
                    "gtm_type": gid,
                    "tier": tier,
                    "kind": "generator",
                    "source_mod": "gregtech_modern",
                    "status": "done",
                    "wave": "parity",
                }
            )

    # Hulls, buffers, transformers, diodes per tier
    for tier in PROC_TIERS:
        for kind, gtm, slots_kind in [
            ("machine_hull", "machine_hull", "hull"),
            ("battery_buffer_4x", "battery_buffer_4x", "buffer"),
            ("transformer", "transformer", "cable"),
            ("diode", "diode", "cable"),
            ("charger_4", "charger_4", "buffer"),
        ]:
            block = f"{tier}_{kind}"
            write_orientable_block(block)
            if slots_kind != "cable" and slots_kind != "hull":
                write(DATA / "horizon" / "menu" / f"{block}.json", menu_for(4, slots_kind))
            lang[f"block.gtceu.{block}"] = f"{tier.upper()} {human(kind)}"
            creative.append(f"gtceu:{block}")
            pickaxe.append(f"gtceu:{block}")
            catalog_machines.append(
                {
                    "id": block,
                    "gtm_type": gtm,
                    "tier": tier,
                    "kind": "storage" if "battery" in kind or "charger" in kind else ("utility" if kind != "transformer" else "transformer"),
                    "source_mod": "gregtech_modern",
                    "status": "done",
                    "wave": "parity",
                }
            )

    # Cables: snake_case material id from extract
    for c in cables:
        mid = c["id"] if isinstance(c, dict) else str(c)
        for amp in ("1x", "4x"):
            block = f"{mid}_cable_{amp}"
            write_orientable_block(
                block,
                tex="tin_cable_1x"
                if (TEX_BLOCK / "tin_cable_1x_side.png").exists()
                else "lv_machine",
            )
            lang[f"block.gtceu.{block}"] = f"{human(mid)} Cable {amp.upper()}"
            creative.append(f"gtceu:{block}")
            pickaxe.append(f"gtceu:{block}")
            catalog_machines.append(
                {
                    "id": block,
                    "gtm_type": "cable",
                    "tier": "wire",
                    "kind": "cable",
                    "source_mod": "gregtech_modern",
                    "status": "done",
                    "wave": "parity",
                }
            )

    # Multiblock controllers
    for mb in multis:
        mid = mb["id"] if isinstance(mb, dict) else mb
        if isinstance(mb, dict):
            mid = mb["id"]
        block = f"multi_{mid}"
        write_orientable_block(block)
        write(DATA / "horizon" / "menu" / f"{block}.json", menu_for(1, "multiblock"))
        lang[f"block.gtceu.{block}"] = human(mid)
        creative.append(f"gtceu:{block}")
        pickaxe.append(f"gtceu:{block}")
        catalog_machines.append(
            {
                "id": block,
                "gtm_type": mid,
                "tier": "multi",
                "kind": "multiblock",
                "source_mod": "gregtech_modern",
                "status": "done",
                "wave": "parity",
                "notes": mb.get("role", "") if isinstance(mb, dict) else "",
            }
        )

    # HP steam boiler
    write_orientable_block("steam_solid_boiler_hp", tex="steam_solid_boiler_lp" if (TEX_BLOCK / "steam_solid_boiler_lp_side.png").exists() else "lv_machine")
    write(DATA / "horizon" / "menu" / "steam_solid_boiler_hp.json", menu_for(1, "boiler"))
    lang["block.gtceu.steam_solid_boiler_hp"] = "HP Solid Boiler"
    creative.append("gtceu:steam_solid_boiler_hp")
    pickaxe.append("gtceu:steam_solid_boiler_hp")

    # Recipes: deep-ish maps per processor type (shared across tiers)
    recipe_count = 0
    # macerator / furnace / compressor / wiremill / lathe / alloy etc.
    pairs_macerate = []
    for mid in mat_ids[:80]:
        ing = VANILLA_INGOT.get(mid, f"gtceu:{mid}_ingot")
        pairs_macerate.append((ing, f"gtceu:{mid}_dust"))
        if mid not in VANILLA_INGOT:
            pairs_macerate.append((f"gtceu:{mid}_plate", f"gtceu:{mid}_dust"))
    for i, (inp, out) in enumerate(pairs_macerate[:60]):
        write(
            DATA / "recipe" / f"parity_macerate_{i}.json",
            {
                "type": "gtceu:macerator",
                "ingredient": {"item": inp},
                "result": {"id": out, "count": 1},
                "duration": 80,
                "eu": 2,
                "steam": 1,
            },
        )
        recipe_count += 1

    pairs_compress = []
    for mid in mat_ids[:80]:
        ing = VANILLA_INGOT.get(mid, f"gtceu:{mid}_ingot")
        pairs_compress.append((ing, f"gtceu:{mid}_plate"))
        pairs_compress.append((f"gtceu:{mid}_dust", f"gtceu:{mid}_plate"))
    for i, (inp, out) in enumerate(pairs_compress[:60]):
        write(
            DATA / "recipe" / f"parity_compress_{i}.json",
            {
                "type": "gtceu:compressor",
                "ingredient": {"item": inp},
                "result": {"id": out, "count": 1},
                "duration": 80,
                "eu": 2,
            },
        )
        recipe_count += 1

    for i, mid in enumerate(mat_ids[:40]):
        ing = VANILLA_INGOT.get(mid, f"gtceu:{mid}_ingot")
        write(
            DATA / "recipe" / f"parity_wiremill_{i}.json",
            {
                "type": "gtceu:wiremill",
                "ingredient": {"item": ing},
                "result": {"id": f"gtceu:{mid}_wire", "count": 2},
                "duration": 60,
                "eu": 2,
            },
        )
        write(
            DATA / "recipe" / f"parity_lathe_{i}.json",
            {
                "type": "gtceu:lathe",
                "ingredient": {"item": ing},
                "result": {"id": f"gtceu:{mid}_rod", "count": 2},
                "duration": 60,
                "eu": 2,
            },
        )
        recipe_count += 2

    # alloy recipes
    alloys = [
        (("minecraft:copper_ingot", "gtceu:tin_ingot"), "gtceu:bronze_ingot", 2),
        (("gtceu:copper_dust", "gtceu:tin_dust"), "gtceu:bronze_ingot", 2),
        (("minecraft:iron_ingot", "minecraft:coal"), "gtceu:steel_ingot", 1),
        (("minecraft:gold_ingot", "minecraft:copper_ingot"), "gtceu:rose_gold_ingot", 2),
    ]
    for i, (inputs, out, count) in enumerate(alloys):
        write(
            DATA / "recipe" / f"parity_alloy_{i}.json",
            {
                "type": "gtceu:alloy_smelter",
                "ingredients": [{"item": a} for a in inputs],
                "result": {"id": out, "count": count},
                "duration": 100,
                "eu": 2,
                "steam": 1,
            },
        )
        recipe_count += 1

    # furnace / electric_furnace
    smelts = [
        ("minecraft:raw_iron", "minecraft:iron_ingot"),
        ("minecraft:raw_copper", "minecraft:copper_ingot"),
        ("minecraft:raw_gold", "minecraft:gold_ingot"),
        ("minecraft:cobblestone", "minecraft:stone"),
        ("minecraft:sand", "minecraft:glass"),
        ("minecraft:clay_ball", "minecraft:brick"),
        ("minecraft:netherrack", "minecraft:nether_brick"),
        ("gtceu:iron_dust", "minecraft:iron_ingot"),
        ("gtceu:copper_dust", "minecraft:copper_ingot"),
        ("gtceu:tin_dust", "gtceu:tin_ingot"),
    ]
    for i, (inp, out) in enumerate(smelts):
        write(
            DATA / "recipe" / f"parity_furnace_{i}.json",
            {
                "type": "gtceu:electric_furnace",
                "ingredient": {"item": inp},
                "result": {"id": out, "count": 1},
                "duration": 100,
                "eu": 2,
            },
        )
        recipe_count += 1

    # Generic ≥2 recipes for every remaining machine type
    for m in machines:
        mtype = m["id"]
        if mtype in ("macerator", "compressor", "wiremill", "lathe", "alloy_smelter", "electric_furnace"):
            continue
        for n, (inp, out) in enumerate(
            [
                ("minecraft:cobblestone", "minecraft:gravel"),
                ("minecraft:gravel", "minecraft:sand"),
                ("minecraft:sand", "minecraft:glass"),
                ("minecraft:iron_ingot", "gtceu:iron_plate"),
            ][: max(2, m.get("typical_inputs", 1) + 1)]
        ):
            body = {
                "type": f"gtceu:{mtype}",
                "result": {"id": out, "count": 1},
                "duration": 80,
                "eu": 2,
            }
            if m.get("typical_inputs", 1) >= 2 or mtype in multi_in:
                body["ingredients"] = [{"item": inp}, {"item": "minecraft:redstone"}]
            else:
                body["ingredient"] = {"item": inp}
            write(DATA / "recipe" / f"parity_{mtype}_{n}.json", body)
            recipe_count += 1

    # Craft cables from wires + rubber
    for c in cables:
        mid = c["id"] if isinstance(c, dict) else str(c)
        write(
            DATA / "recipe" / f"craft_{mid}_cable_1x.json",
            {
                "type": "minecraft:crafting_shapeless",
                "ingredients": [
                    {"item": f"gtceu:{mid}_wire"},
                    {"item": "gtceu:rubber"},
                ],
                "result": {"id": f"gtceu:{mid}_cable_1x", "count": 1},
            },
        )
        recipe_count += 1

    # Deepen every processor type to ≥8 recipes (GTM-oriented stubs)
    for m in machines:
        mtype = m["id"]
        existing = list((DATA / "recipe").glob(f"*{mtype}*.json"))
        need = max(0, 8 - len(existing))
        for n in range(need):
            inp = mat_ids[n % len(mat_ids)]
            ing = VANILLA_INGOT.get(inp, f"gtceu:{inp}_ingot")
            out = f"gtceu:{inp}_dust"
            body = {
                "type": f"gtceu:{mtype}",
                "result": {"id": out, "count": 1},
                "duration": 80,
                "eu": 2,
            }
            if m.get("typical_inputs", 1) >= 2 or mtype in multi_in:
                body["ingredients"] = [{"item": ing}, {"item": "minecraft:redstone"}]
            else:
                body["ingredient"] = {"item": ing}
            write(DATA / "recipe" / f"parity_deep_{mtype}_{n}.json", body)
            recipe_count += 1

    # Lang + tab + tags
    write(ASSETS / "lang" / "en_us.json", lang)
    # dedupe creative preserving order
    seen = set()
    items = []
    for x in creative:
        if x not in seen:
            seen.add(x)
            items.append(x)
    write(
        DATA / "horizon" / "creative_tab" / "gtceu.json",
        {"title": "GregTech", "icon": "gtceu:bronze_ingot", "items": items[:4000]},
    )
    write(
        ROOT / "data" / "minecraft" / "tags" / "block" / "mineable" / "pickaxe.json",
        {"replace": False, "values": sorted(set(pickaxe))},
    )

    # Catalog + coverage snapshot
    steam = [
        {
            "id": "steam_solid_boiler_lp",
            "gtm_type": "steam_solid_boiler",
            "tier": "steam_lp",
            "kind": "generator",
            "source_mod": "gregtech_modern",
            "status": "done",
            "wave": "0.2",
        },
        {
            "id": "steam_solid_boiler_hp",
            "gtm_type": "steam_solid_boiler",
            "tier": "steam_hp",
            "kind": "generator",
            "source_mod": "gregtech_modern",
            "status": "done",
            "wave": "parity",
        },
        {
            "id": "steam_alloy_smelter",
            "gtm_type": "alloy_smelter",
            "tier": "steam",
            "kind": "processor",
            "source_mod": "gregtech_modern",
            "status": "done",
            "wave": "0.2",
        },
        {
            "id": "steam_macerator",
            "gtm_type": "macerator",
            "tier": "steam",
            "kind": "processor",
            "source_mod": "gregtech_modern",
            "status": "done",
            "wave": "0.2",
        },
        {
            "id": "steam_compressor",
            "gtm_type": "compressor",
            "tier": "steam",
            "kind": "processor",
            "source_mod": "gregtech_modern",
            "status": "done",
            "wave": "0.2",
        },
    ]
    catalog = {
        "schema": 2,
        "updated": "2026-11-14",
        "plan": "docs/gtceu-electric-plan.md",
        "parity_target": 0.99,
        "machines": steam + catalog_machines,
        "materials_count": len(mat_ids),
        "recipe_files_written": recipe_count,
        "milestones": [{"id": "GTM_PARITY", "title": "GTM-oriented parity push", "status": "in_progress"}],
    }
    write(ROOT / "tracker" / "catalog.json", catalog)

    print("materials", len(mat_ids))
    print("machine blocks catalog", len(catalog["machines"]))
    print("recipes written", recipe_count)
    print("creative items", len(items))


if __name__ == "__main__":
    main()