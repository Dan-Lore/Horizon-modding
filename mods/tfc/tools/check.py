#!/usr/bin/env python3
"""Check generated TFC content, the climate gate, and the packed hmod."""

from __future__ import annotations

import json
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MOD = ROOT / "mods" / "tfc"
WAVES = [f"W{n}" for n in range(23)]
REV = "fdc87aecdbd116bf1e08adcd062fcbaea8c2e2ca"


def fail(message: str) -> None:
    raise SystemExit(message)


def sample_temp(table: dict, day: int) -> tuple[str, float]:
    months = table["months"]
    idx = (day // table["days_per_month"]) % len(months)
    month = months[idx]
    # x = z = 0 → spatial sin(0) = 0, matching climate.rs.
    temp = table["base_temp"] + month["temp_offset"]
    return month["season"], temp


def crop_allowed(table: dict, crop: dict, day: int) -> bool:
    season, temp = sample_temp(table, day)
    rain = table["base_rain"]
    return (
        crop["min_temp"] <= temp <= crop["max_temp"]
        and season in crop["seasons"]
        and crop["min_rain"] <= rain <= crop["max_rain"]
    )


def write_tracker(catalog: dict) -> None:
    lines = [
        "# TFC Horizon tracker",
        "",
        f"Generated from `mods/tfc/tracker/catalog.json` (mod {catalog['version']}, Horizon `{catalog['horizon']}`, hooks {catalog['hooks']}).",
        "Regenerate with `python3 mods/tfc/tools/check.py`.",
        "",
        "| Wave | System | Status | Smoke |",
        "| --- | --- | --- | --- |",
    ]
    for system in catalog["systems"]:
        smoke = system["smoke"].replace("|", "/")
        lines.append(
            f"| {system['wave']} | {system['name']} | {system['status']} | {smoke} |"
        )
    lines.append("")
    path = ROOT / "docs" / "tfc-tracker.md"
    path.write_text("\n".join(lines), encoding="utf-8")


def main() -> None:
    subprocess.check_call([sys.executable, str(MOD / "tools" / "test_logic.py")])
    gen = MOD / "tools" / "gen_content.py"
    subprocess.check_call([sys.executable, str(gen)])
    catalog = json.loads((MOD / "tracker" / "catalog.json").read_text(encoding="utf-8"))
    if catalog["version"] != "0.2.0" or catalog["horizon"] != REV:
        fail("catalog pin drifted")
    seen = {system["wave"] for system in catalog["systems"]}
    missing = [wave for wave in WAVES if wave not in seen]
    if missing:
        fail(f"missing waves: {missing}")
    for system in catalog["systems"]:
        if system["status"] not in {"todo", "wip", "done", "blocked", "deferred"}:
            fail(f"bad status on {system['id']}")
        if system["status"] == "done" and not system.get("smoke"):
            fail(f"done without smoke: {system['id']}")
    by_id = {system["id"]: system["status"] for system in catalog["systems"]}
    if by_id.get("w13_animals") != "deferred" or by_id.get("w14_worldgen") != "blocked":
        fail("animals must stay deferred and worldgen blocked")
    if by_id.get("w7_stack_rot") != "blocked" or by_id.get("w10_collapse_replace") != "blocked":
        fail("rot timer and collapse replace stay blocked on hooks 411")

    climate = json.loads((MOD / "tables" / "climate_seasons.json").read_text(encoding="utf-8"))
    crops = json.loads((MOD / "tables" / "crops.json").read_text(encoding="utf-8"))
    wheat = next(crop for crop in crops if crop["id"] == "tfc:crop_wheat")
    barley = next(crop for crop in crops if crop["id"] == "tfc:crop_barley")
    if crop_allowed(climate, wheat, 0):
        fail("wheat must not grow on day 0 (January)")
    if not crop_allowed(climate, wheat, 48):
        fail("wheat must grow on day 48 (July)")
    if crop_allowed(climate, barley, 48):
        fail("barley must not grow in July")
    if not crop_allowed(climate, barley, 72):
        fail("barley must grow on day 72 (October)")
    rye = next(crop for crop in crops if crop["id"] == "tfc:crop_rye")
    squash = next(crop for crop in crops if crop["id"] == "tfc:crop_squash")
    if not crop_allowed(climate, rye, 0):
        fail("rye must grow on day 0 (January)")
    if crop_allowed(climate, rye, 48):
        fail("rye must not grow in July")
    if not crop_allowed(climate, squash, 48):
        fail("squash must grow on day 48 (July)")
    if crop_allowed(climate, squash, 0):
        fail("squash must not grow in January")

    machines = json.loads((MOD / "tables" / "machines.json").read_text(encoding="utf-8"))
    specs = (MOD / "api" / "src" / "specs.inc.rs").read_text(encoding="utf-8")
    recipes_rs = (MOD / "api" / "src" / "recipes.rs").read_text(encoding="utf-8")
    primaries = {
        "tfc:firepit": ("minecraft:beef", "tfc:cooked_meat"),
        "tfc:charcoal_forge": ("tfc:nugget_native_copper", "tfc:copper_ingot"),
        "tfc:bloomery": ("tfc:nugget_hematite", "tfc:raw_iron_bloom"),
        "tfc:anvil": ("tfc:raw_iron_bloom", "tfc:wrought_iron_ingot"),
        "tfc:quern": ("tfc:wheat", "tfc:flour"),
        "tfc:barrel": ("minecraft:oak_log", "tfc:tannin"),
        "tfc:pit_kiln": ("tfc:unfired_vessel", "tfc:vessel"),
        "tfc:blast_furnace": ("tfc:wrought_iron_ingot", "tfc:steel_ingot"),
        "tfc:sluice": ("tfc:ore_deposit", "tfc:nugget_native_copper"),
        "tfc:charcoal_pit": ("minecraft:oak_log", "minecraft:charcoal"),
        "tfc:crucible": ("tfc:copper_ingot", "tfc:bronze_ingot"),
    }
    recipe_dir = MOD / "data" / "tfc" / "recipe"
    for machine in machines:
        if machine["id"] not in specs:
            fail(f"spec missing {machine['id']}")
        menu = json.loads(
            (MOD / "data" / "tfc" / "horizon" / "menu" / f"{machine['id'].split(':', 1)[1]}.json").read_text(
                encoding="utf-8"
            )
        )
        expect = machine["inputs"] if machine["output"] is None else machine["output"] + 1
        if menu["slots"] != expect:
            fail(f"menu slots for {machine['id']}")
        if machine["storage"] or not machine["recipe_type"]:
            continue
        kind = machine["recipe_type"].split(":", 1)[1]
        found = list(recipe_dir.glob(f"{kind}_*.json"))
        if not found:
            fail(f"no recipes for {kind}")
        for path in found:
            body = json.loads(path.read_text(encoding="utf-8"))
            count = 1 if "ingredient" in body else len(body.get("ingredients", []))
            if count > machine["inputs"]:
                fail(f"{path.name} has {count} inputs, spec wants {machine['inputs']}")
        left, right = primaries[machine["recipe_type"]]
        if left not in recipes_rs or right not in recipes_rs:
            fail(f"fallback missing {left} -> {right}")

    for needle in (
        "tfc:ore_native_copper",
        "tfc:andesite_raw",
        "tfc:crop_wheat",
        "tfc:prospector_pick",
        "tfc:jug",
        "tfc:glass_batch",
        "tfc:support_beam",
    ):
        kind, name = ("block", needle.split(":", 1)[1]) if needle.startswith("tfc:") else ("item", needle)
        folder = "block" if (MOD / "data" / "tfc" / "horizon" / "block" / f"{name}.json").exists() else "item"
        path = MOD / "data" / "tfc" / "horizon" / folder / f"{name}.json"
        if not path.exists():
            fail(f"missing content {needle}")

    for name in ("alloy_bronze.json", "alloy_brass.json", "weld_copper.json", "weld_bronze.json"):
        if (recipe_dir / name).exists():
            fail(f"stand-in recipe remains: {name}")
    for path in recipe_dir.glob("*.json"):
        body = json.loads(path.read_text(encoding="utf-8"))
        if body.get("type") != "minecraft:crafting_shapeless":
            continue
        result = body.get("result", {}).get("id", "")
        ingredients = [entry.get("item") for entry in body.get("ingredients", [])]
        if "tfc:andesite_cobble" in ingredients and result.startswith("tfc:stone_"):
            fail(f"{path.name} still knaps from cobble")
        if result in {"tfc:bronze_ingot", "tfc:brass_ingot"} or result.endswith("_double_ingot"):
            fail(f"shapeless metal recipe {path.name}")
    heat = json.loads((MOD / "tables" / "heat.json").read_text(encoding="utf-8"))
    if heat["forge_max"] >= heat["metals"]["wrought_iron"]["melt"]:
        fail("forge cap must stay below wrought iron")
    if "heat.json" not in (MOD / "api" / "src" / "heat.rs").read_text(encoding="utf-8"):
        fail("heat table is not read")
    lib = (MOD / "api" / "src" / "lib.rs").read_text(encoding="utf-8")
    if "TFC Horizon 0.2.0" not in lib:
        fail("login line is not 0.2.0")

    draft = (ROOT / "pack" / "draft-mods.toml").read_text(encoding="utf-8")
    if 'id = "tfc"' not in draft or 'on = []' not in draft.split('id = "tfc"', 1)[1][:400]:
        fail("draft-mods must list tfc with on = []")
    mixin = (MOD / "horizon-mixin.toml").read_text(encoding="utf-8")
    if REV not in mixin:
        fail("mixin revision drifted")

    write_tracker(catalog)
    subprocess.check_call([sys.executable, str(ROOT / "tools" / "pack-tfc.py")])
    archive_path = MOD / "dist" / "tfc.hmod"
    with zipfile.ZipFile(archive_path) as archive:
        names = archive.namelist()
        if any("\\" in name for name in names):
            fail("zip has non-POSIX paths")
        for required in (
            "horizon-mod.toml",
            "horizon-native.json",
            "mixins/tfc/horizon-mixin.toml",
            "mixins/tfc/api/src/lib.rs",
            "mixins/tfc/api/src/specs.inc.rs",
            "data/tfc/horizon/block/firepit.json",
            "assets/tfc/lang/en_us.json",
        ):
            if required not in names:
                fail(f"hmod missing {required}")
        native = json.loads(archive.read("horizon-native.json"))
        if native["id"] != "tfc" or native["horizon"] != REV or native["game"] != "26.3":
            fail("horizon-native.json pin")
    print(f"ok {len(catalog['systems'])} systems, {archive_path.stat().st_size} bytes")


if __name__ == "__main__":
    main()
