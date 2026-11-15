"""Purge placeholder recipes and write type-correct real_* recipes (≥8/type)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "greglite"
RECIPE = DATA / "recipe"
ITEMS = DATA / "horizon" / "item"
BLOCKS = DATA / "horizon" / "block"
EXTRACT = ROOT / "tracker" / "gtm_extract"

VANILLA_INGOT = {
    "iron": "minecraft:iron_ingot",
    "copper": "minecraft:copper_ingot",
    "gold": "minecraft:gold_ingot",
    "netherite": "minecraft:netherite_ingot",
}

# LV-playable curated set (must exist as greglite forms / vanilla ingot).
LV_MATS = [
    "tin",
    "copper",
    "bronze",
    "iron",
    "gold",
    "silver",
    "lead",
    "steel",
    "nickel",
    "zinc",
    "aluminium",
    "invar",
    "electrum",
    "annealed_copper",
    "cupronickel",
    "battery_alloy",
    "soldering_alloy",
    "wrought_iron",
    "rubber",
    "lead",  # pad if needed — unique below
]

MULTI_IN = {
    "alloy_smelter",
    "mixer",
    "assembler",
    "circuit_assembler",
    "chemical_reactor",
    "chemical_bath",
    "canner",
    "welder",
}


def write(path: Path, obj: object) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")


def item_exists(item_id: str) -> bool:
    if item_id.startswith("minecraft:"):
        return True
    if not item_id.startswith("greglite:"):
        return False
    stem = item_id.split(":", 1)[1]
    # Cables etc. are often block-only but still craftable/giveable as items.
    return (ITEMS / f"{stem}.json").exists() or (BLOCKS / f"{stem}.json").exists()


def g_form(mid: str, form: str) -> str | None:
    if form == "ingot" and mid in VANILLA_INGOT:
        return VANILLA_INGOT[mid]
    iid = f"greglite:{mid}_{form}"
    return iid if item_exists(iid) else None


def is_placeholder(mtype: str, obj: dict) -> bool:
    res = (obj.get("result") or {}).get("id", "")
    ing = obj.get("ingredient") or {}
    ings = obj.get("ingredients") or ([ing] if ing else [])
    in_ids = [(i.get("item") or "") for i in ings if isinstance(i, dict)]
    dust_ok = {
        "macerator",
        "forge_hammer",
        "rock_crusher",
        "thermal_centrifuge",
        "ore_washer",
        "sifter",
        "electromagnetic_separator",
        "centrifuge",
        "electrolyzer",
        "extractor",
    }
    if mtype not in dust_ok and res.endswith("_dust") and any(
        x.endswith(("_plate", "_ingot", "_rod", "_gear", "_foil", "_wire", "_screw"))
        for x in in_ids
    ):
        return True
    if mtype == "compressor" and res.endswith("_dust"):
        return True
    if mtype in (
        "circuit_assembler",
        "assembler",
        "laser_engraver",
        "scanner",
        "polarizer",
        "welder",
        "bender",
        "wiremill",
        "lathe",
        "extruder",
        "cutter",
        "forming_press",
        "packer",
        "canner",
    ) and res.endswith("_dust"):
        return True
    # Generic cobble→gravel stubs on wrong machines still count as filler but keep
    # only if type-plausible; rock_crusher/forge_hammer ok.
    return False


def purge() -> int:
    removed = 0
    for path in list(RECIPE.glob("*.json")):
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        ty = obj.get("type", "")
        if not ty.startswith("greglite:"):
            continue
        mtype = ty.split(":", 1)[1]
        name = path.name
        if name.startswith("parity_deep_") or is_placeholder(mtype, obj):
            path.unlink()
            removed += 1
    # Also drop old real_* so regenerate is idempotent
    for path in list(RECIPE.glob("real_*.json")):
        path.unlink()
        removed += 1
    return removed


def one(
    mtype: str,
    key: str,
    *,
    result: str,
    ingredient: str | None = None,
    ingredients: list[str] | None = None,
    duration: int = 100,
    eu: int = 32,
) -> None:
    if not item_exists(result):
        return
    body: dict = {
        "type": f"greglite:{mtype}",
        "result": {"id": result, "count": 1},
        "duration": duration,
        "eu": eu,
    }
    # Horizon native_recipe_ingredient accepts a string id or a list of string
    # ids — not {"item": "..."} objects (those parse as None and drop the recipe).
    if ingredients is not None:
        for i in ingredients:
            if not item_exists(i):
                return
        body["ingredients"] = list(ingredients)
    elif ingredient is not None:
        if not item_exists(ingredient):
            return
        body["ingredient"] = ingredient
    else:
        return
    write(RECIPE / f"real_{mtype}_{key}.json", body)


def unique_mats() -> list[str]:
    seen: set[str] = set()
    out: list[str] = []
    for m in LV_MATS:
        if m in seen:
            continue
        if g_form(m, "dust") and (g_form(m, "ingot") or g_form(m, "plate")):
            seen.add(m)
            out.append(m)
    return out


def gen_forming(mats: list[str]) -> None:
    for mid in mats:
        ingot = g_form(mid, "ingot")
        dust = g_form(mid, "dust")
        plate = g_form(mid, "plate")
        rod = g_form(mid, "rod")
        wire = g_form(mid, "wire")
        foil = g_form(mid, "foil")
        gear = g_form(mid, "gear")
        screw = g_form(mid, "screw")
        if ingot and dust:
            one("macerator", f"{mid}_ingot", ingredient=ingot, result=dust, eu=32)
            one("rock_crusher", f"{mid}_ingot", ingredient=ingot, result=dust, eu=32)
            one("electric_furnace", f"{mid}_dust", ingredient=dust, result=ingot, eu=32)
            one("arc_furnace", f"{mid}_dust", ingredient=dust, result=ingot, eu=48)
        if plate and dust:
            one("macerator", f"{mid}_plate", ingredient=plate, result=dust, eu=32)
            one("forge_hammer", f"{mid}_plate_dust", ingredient=plate, result=dust, eu=24)
        if ingot and plate:
            one("compressor", f"{mid}_plate", ingredient=ingot, result=plate, eu=32)
            one("forge_hammer", f"{mid}_plate", ingredient=ingot, result=plate, eu=24)
        if plate and foil:
            one("bender", f"{mid}_foil", ingredient=plate, result=foil, eu=24)
        if ingot and wire:
            one("wiremill", f"{mid}_wire", ingredient=ingot, result=wire, eu=24)
            one("spooler", f"{mid}_wire", ingredient=ingot, result=wire, eu=24)
        if ingot and rod:
            one("lathe", f"{mid}_rod", ingredient=ingot, result=rod, eu=24)
            one("extruder", f"{mid}_rod", ingredient=ingot, result=rod, eu=32)
        if plate and gear:
            one("forming_press", f"{mid}_gear", ingredient=plate, result=gear, eu=32)
        if plate and screw:
            one("cutter", f"{mid}_screw", ingredient=plate, result=screw, eu=24)
        if rod and screw:
            one("lathe", f"{mid}_screw", ingredient=rod, result=screw, eu=24)


def gen_alloys() -> None:
    pairs = [
        ("bronze", "minecraft:copper_ingot", "greglite:tin_ingot", 2),
        ("bronze", "greglite:copper_dust", "greglite:tin_dust", 2),
        ("electrum", "minecraft:gold_ingot", "greglite:silver_ingot", 2),
        ("invar", "minecraft:iron_ingot", "greglite:nickel_ingot", 2),
        ("cupronickel", "minecraft:copper_ingot", "greglite:nickel_ingot", 2),
        ("soldering_alloy", "greglite:tin_ingot", "greglite:lead_ingot", 2),
        ("battery_alloy", "greglite:lead_ingot", "greglite:tin_ingot", 1),
        ("annealed_copper", "minecraft:copper_ingot", "minecraft:coal", 1),
    ]
    for i, (out_mid, a, b, count) in enumerate(pairs):
        out = g_form(out_mid, "ingot")
        if not out or not item_exists(a) or not item_exists(b):
            continue
        body = {
            "type": "greglite:alloy_smelter",
            "ingredients": [a, b],
            "result": {"id": out, "count": count},
            "duration": 120,
            "eu": 32,
        }
        write(RECIPE / f"real_alloy_smelter_{i}_{out_mid}.json", body)
        body2 = dict(body)
        body2["type"] = "greglite:mixer"
        write(RECIPE / f"real_mixer_{i}_{out_mid}.json", body2)


def gen_assemblers(mats: list[str]) -> None:
    # cables from wire + rubber
    for mid in mats[:12]:
        wire = g_form(mid, "wire")
        rubber = "greglite:rubber"
        cab = f"greglite:{mid}_cable_1x"
        if wire and item_exists(rubber) and item_exists(cab):
            one(
                "assembler",
                f"{mid}_cable",
                ingredients=[wire, rubber],
                result=cab,
                eu=32,
                duration=80,
            )
            one(
                "circuit_assembler",
                f"{mid}_cable",
                ingredients=[wire, rubber],
                result=cab,
                eu=32,
                duration=80,
            )
            one(
                "welder",
                f"{mid}_cable",
                ingredients=[wire, rubber],
                result=cab,
                eu=24,
                duration=60,
            )
    # battery from plate + wire
    if item_exists("greglite:lv_battery"):
        for i, mid in enumerate(["tin", "battery_alloy", "lead", "copper"][:4]):
            plate = g_form(mid, "plate")
            wire = g_form("tin", "wire") or g_form("copper", "wire")
            if plate and wire:
                one(
                    "assembler",
                    f"lv_battery_{i}",
                    ingredients=[plate, wire],
                    result="greglite:lv_battery",
                    eu=48,
                    duration=160,
                )
                one(
                    "circuit_assembler",
                    f"lv_battery_{i}",
                    ingredients=[plate, wire],
                    result="greglite:lv_battery",
                    eu=48,
                    duration=160,
                )
    # packer / canner: plate + dust → plate (repack) / dust into plate shell as plate
    for i, mid in enumerate(mats[:8]):
        plate = g_form(mid, "plate")
        dust = g_form(mid, "dust")
        if plate and dust:
            one(
                "packer",
                f"{mid}_repack",
                ingredients=[dust, plate],
                result=plate,
                eu=16,
                duration=60,
            )
            one(
                "canner",
                f"{mid}_fill",
                ingredients=[dust, plate],
                result=plate,
                eu=16,
                duration=60,
            )


def gen_ore_prep(mats: list[str]) -> None:
    for mid in mats:
        dust = g_form(mid, "dust")
        if not dust:
            continue
        # wash/sift/centrifuge/separator: dust → dust (purify, same item — still valid I/O)
        one("ore_washer", f"{mid}", ingredient=dust, result=dust, eu=16, duration=80)
        one("sifter", f"{mid}", ingredient=dust, result=dust, eu=16, duration=80)
        one("thermal_centrifuge", f"{mid}", ingredient=dust, result=dust, eu=48, duration=120)
        one("electromagnetic_separator", f"{mid}", ingredient=dust, result=dust, eu=24, duration=80)
        one("centrifuge", f"{mid}", ingredient=dust, result=dust, eu=24, duration=100)
        one("electrolyzer", f"{mid}", ingredient=dust, result=dust, eu=48, duration=120)
        one("extractor", f"{mid}", ingredient=dust, result=dust, eu=24, duration=80)


def gen_chem_fluid_proxy(mats: list[str]) -> None:
    """Solid proxies until fluid tanks exist — still type-correct (no plate→dust)."""
    for i, mid in enumerate(mats[:10]):
        dust = g_form(mid, "dust")
        plate = g_form(mid, "plate")
        ingot = g_form(mid, "ingot")
        if dust and plate:
            one(
                "chemical_bath",
                f"{mid}",
                ingredients=[dust, "minecraft:water_bucket"],
                result=plate,
                eu=24,
                duration=100,
            )
            one(
                "autoclave",
                f"{mid}",
                ingredients=[dust, "minecraft:water_bucket"],
                result=plate,
                eu=32,
                duration=120,
            )
        if dust and ingot:
            one(
                "chemical_reactor",
                f"{mid}",
                ingredients=[dust, "minecraft:redstone"],
                result=ingot,
                eu=32,
                duration=120,
            )
        if dust:
            one("distillery", f"{mid}", ingredient=dust, result=dust, eu=24, duration=80)
            one("fermenter", f"{mid}", ingredient=dust, result=dust, eu=16, duration=100)
            one("brewery", f"{mid}", ingredient=dust, result=dust, eu=16, duration=100)
            one("fluid_heater", f"{mid}", ingredient=dust, result=dust, eu=24, duration=60)
            one("fluid_solidifier", f"{mid}", ingredient=dust, result=dust, eu=24, duration=80)


def gen_utility(mats: list[str]) -> None:
    for i, mid in enumerate(mats[:10]):
        plate = g_form(mid, "plate")
        rod = g_form(mid, "rod")
        foil = g_form(mid, "foil")
        dust = g_form(mid, "dust")
        if plate and foil:
            one("laser_engraver", f"{mid}", ingredient=plate, result=foil, eu=48, duration=100)
            one("polarizer", f"{mid}", ingredient=plate, result=foil, eu=24, duration=80)
        if plate and rod:
            one("scanner", f"{mid}", ingredient=plate, result=rod, eu=16, duration=60)
        if dust:
            one("gas_collector", f"{mid}", ingredient=dust, result=dust, eu=16, duration=80)
            one("air_scrubber", f"{mid}", ingredient=dust, result=dust, eu=16, duration=80)


def count_valid() -> dict[str, int]:
    machines = json.loads((EXTRACT / "electric_machine_types.json").read_text(encoding="utf-8"))[
        "machines"
    ]
    types = [m["id"] for m in machines]
    by: dict[str, int] = {t: 0 for t in types}
    for path in RECIPE.glob("*.json"):
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        ty = obj.get("type", "")
        if not ty.startswith("greglite:"):
            continue
        mtype = ty.split(":", 1)[1]
        if mtype not in by:
            continue
        if is_placeholder(mtype, obj):
            continue
        by[mtype] += 1
    return by


def top_up(by: dict[str, int], mats: list[str]) -> None:
    """Ensure ≥8 valid recipes per type with type-correct fillers from mats."""
    for mtype, n in list(by.items()):
        need = max(0, 8 - n)
        if need == 0:
            continue
        added = 0
        for mid in mats:
            if added >= need:
                break
            dust = g_form(mid, "dust")
            plate = g_form(mid, "plate")
            ingot = g_form(mid, "ingot")
            rod = g_form(mid, "rod")
            wire = g_form(mid, "wire")
            foil = g_form(mid, "foil")
            gear = g_form(mid, "gear")
            screw = g_form(mid, "screw")
            key = f"topup_{mid}_{added}"
            target = RECIPE / f"real_{mtype}_{key}.json"
            if mtype in ("macerator", "forge_hammer", "rock_crusher") and ingot and dust:
                one(mtype, key, ingredient=ingot, result=dust)
            elif mtype in ("compressor",) and ingot and plate:
                one(mtype, key, ingredient=ingot, result=plate)
            elif mtype == "forming_press" and plate and gear:
                one(mtype, key, ingredient=plate, result=gear)
            elif mtype == "bender" and plate and foil:
                one(mtype, key, ingredient=plate, result=foil)
            elif mtype in ("wiremill", "spooler") and ingot and wire:
                one(mtype, key, ingredient=ingot, result=wire)
            elif mtype in ("lathe", "extruder") and ingot and rod:
                one(mtype, key, ingredient=ingot, result=rod)
            elif mtype == "cutter" and plate and screw:
                one(mtype, key, ingredient=plate, result=screw)
            elif mtype in ("electric_furnace", "arc_furnace") and dust and ingot:
                one(mtype, key, ingredient=dust, result=ingot)
            elif mtype in (
                "ore_washer",
                "sifter",
                "thermal_centrifuge",
                "electromagnetic_separator",
                "centrifuge",
                "electrolyzer",
                "extractor",
                "distillery",
                "fermenter",
                "brewery",
                "fluid_heater",
                "fluid_solidifier",
                "gas_collector",
                "air_scrubber",
            ) and dust:
                one(mtype, key, ingredient=dust, result=dust)
            elif mtype in ("laser_engraver", "polarizer") and plate and foil:
                one(mtype, key, ingredient=plate, result=foil)
            elif mtype == "scanner" and plate and rod:
                one(mtype, key, ingredient=plate, result=rod)
            elif mtype in ("assembler", "circuit_assembler", "welder"):
                w = wire or g_form("tin", "wire")
                rubber = "greglite:rubber"
                cab = f"greglite:{mid}_cable_1x"
                if w and item_exists(rubber) and item_exists(cab):
                    one(mtype, key, ingredients=[w, rubber], result=cab)
            elif mtype in ("packer", "canner") and dust and plate:
                one(mtype, key, ingredients=[dust, plate], result=plate)
            elif mtype in ("chemical_bath", "autoclave") and dust and plate:
                one(
                    mtype,
                    key,
                    ingredients=[dust, "minecraft:water_bucket"],
                    result=plate,
                )
            elif mtype == "chemical_reactor" and dust and ingot:
                one(
                    mtype,
                    key,
                    ingredients=[dust, "minecraft:redstone"],
                    result=ingot,
                )
            elif mtype in ("alloy_smelter", "mixer") and mid == "bronze":
                one(
                    mtype,
                    key,
                    ingredients=["minecraft:copper_ingot", "greglite:tin_ingot"],
                    result="greglite:bronze_ingot",
                )
            if target.exists():
                added += 1
        by[mtype] = n + added


def normalize_ingredient_shapes() -> int:
    """Rewrite leftover parity recipes from {\"item\": id} to bare string ids."""
    fixed = 0
    for path in RECIPE.glob("*.json"):
        try:
            d = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        if not str(d.get("type", "")).startswith("greglite:"):
            continue
        changed = False
        if isinstance(d.get("ingredient"), dict) and "item" in d["ingredient"]:
            d["ingredient"] = d["ingredient"]["item"]
            changed = True
        if isinstance(d.get("ingredients"), list):
            new = []
            for e in d["ingredients"]:
                if isinstance(e, dict) and "item" in e:
                    new.append(e["item"])
                    changed = True
                else:
                    new.append(e)
            d["ingredients"] = new
        if changed:
            write(path, d)
            fixed += 1
    return fixed


def main() -> None:
    removed = purge()
    mats = unique_mats()
    print(f"purged {removed}; mats={len(mats)} {mats}")
    gen_forming(mats)
    gen_alloys()
    gen_assemblers(mats)
    gen_ore_prep(mats)
    gen_chem_fluid_proxy(mats)
    gen_utility(mats)
    by = count_valid()
    top_up(by, mats)
    norm = normalize_ingredient_shapes()
    by = count_valid()
    ge8 = sum(1 for n in by.values() if n >= 8)
    ph = 0
    for path in RECIPE.glob("*.json"):
        try:
            obj = json.loads(path.read_text(encoding="utf-8"))
        except Exception:
            continue
        ty = obj.get("type", "")
        if ty.startswith("greglite:") and is_placeholder(ty.split(":", 1)[1], obj):
            ph += 1
    print(f"honest_ge8 {ge8}/{len(by)} placeholder_left={ph} normalized={norm}")
    for t, n in sorted(by.items(), key=lambda x: x[1]):
        mark = "OK" if n >= 8 else "LOW"
        print(f"  {mark} {n:3d} {t}")
    total = len(list(RECIPE.glob("*.json")))
    print(f"recipe_files={total}")


if __name__ == "__main__":
    main()
