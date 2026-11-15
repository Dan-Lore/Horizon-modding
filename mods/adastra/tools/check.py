#!/usr/bin/env python3
"""Check generated Ad Astra content and the packed hmod."""

from __future__ import annotations

import json
import subprocess
import sys
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
MOD = ROOT / "mods" / "adastra"
WAVES = [f"W{n}" for n in range(11)]
REV = "fdc87aecdbd116bf1e08adcd062fcbaea8c2e2ca"
MIXINS = "5a64af938ec86b00d53d16a408aabc0038fb3e57"
HOOKS = 411


def fail(message: str) -> None:
    raise SystemExit(message)


def write_tracker(catalog: dict) -> None:
    lines = [
        "# Ad Astra Horizon tracker",
        "",
        f"Generated from `mods/adastra/tracker/catalog.json` (mod {catalog['version']}, Horizon `{catalog['horizon']}`, hooks {catalog['hooks']}).",
        "Regenerate with `python3 mods/adastra/tools/check.py`.",
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
    path = ROOT / "docs" / "adastra-tracker.md"
    path.write_text("\n".join(lines), encoding="utf-8")


def png_is_rgba(path: Path) -> bool:
    data = path.read_bytes()
    if data[:8] != b"\x89PNG\r\n\x1a\n":
        return False
    # IHDR: length(4) + 'IHDR'(4) + width(4) + height(4) + bit_depth(1) + color_type(1)
    if data[12:16] != b"IHDR":
        return False
    color_type = data[25]
    return color_type == 6


def main() -> None:
    gen = MOD / "tools" / "gen_content.py"
    subprocess.check_call([sys.executable, str(gen)])
    catalog = json.loads((MOD / "tracker" / "catalog.json").read_text(encoding="utf-8"))
    if catalog["version"] != "0.1.0" or catalog["horizon"] != REV:
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
    if by_id.get("w10_dimensions") != "blocked":
        fail("dimensions must stay blocked")

    for path in (
        MOD / "data" / "adastra" / "horizon" / "block" / "coal_generator.json",
        MOD / "data" / "adastra" / "horizon" / "block" / "compressor.json",
        MOD / "data" / "adastra" / "horizon" / "item" / "desh_ingot.json",
        MOD / "assets" / "adastra" / "items" / "desh_ingot.json",
        MOD / "assets" / "adastra" / "items" / "coal_generator.json",
        MOD / "assets" / "adastra" / "items" / "moon_stone.json",
        MOD / "assets" / "adastra" / "items" / "rocket_t1.json",
        MOD / "data" / "adastra" / "recipe" / "compress_desh.json",
        MOD / "data" / "adastra" / "recipe" / "refine_oil.json",
        MOD / "data" / "adastra" / "recipe" / "freeze_ice.json",
        MOD / "data" / "adastra" / "recipe" / "freeze_blue_ice.json",
        MOD / "api" / "src" / "specs.inc.rs",
        MOD / "api" / "src" / "lib.rs",
    ):
        if not path.is_file():
            fail(f"missing {path.relative_to(ROOT)}")

    items_dir = MOD / "assets" / "adastra" / "items"
    item_defs = list(items_dir.glob("*.json"))
    if len(item_defs) < 30:
        fail(f"expected ≥30 assets/adastra/items/*.json, got {len(item_defs)}")

    for block in ("moon_stone", "mars_stone", "launch_pad", "vacuum_marker", "nasa_workbench", "solar_panel"):
        model = json.loads(
            (MOD / "assets" / "adastra" / "models" / "block" / f"{block}.json").read_text(
                encoding="utf-8"
            )
        )
        if model.get("parent") != "minecraft:block/orientable":
            fail(f"{block} model must be orientable")
        states = json.loads(
            (MOD / "assets" / "adastra" / "blockstates" / f"{block}.json").read_text(
                encoding="utf-8"
            )
        )
        if "" in states.get("variants", {}):
            fail(f"{block} must not use empty blockstate variant")
        if "facing=north,lit=false" not in states.get("variants", {}):
            fail(f"{block} missing facing×lit variants")
        block_json = json.loads(
            (MOD / "data" / "adastra" / "horizon" / "block" / f"{block}.json").read_text(
                encoding="utf-8"
            )
        )
        if block_json.get("template") != "minecraft:furnace":
            fail(f"{block} must use furnace template")

    for png_path in (MOD / "assets" / "adastra" / "textures").rglob("*.png"):
        if not png_is_rgba(png_path):
            fail(f"PNG must be RGBA (color type 6): {png_path.relative_to(ROOT)}")

    specs = (MOD / "api" / "src" / "specs.inc.rs").read_text(encoding="utf-8")
    for machine in ("coal_generator", "compressor", "oxygen_loader", "fuel_refinery", "cryo_freezer"):
        if f'id: "adastra:{machine}"' not in specs:
            fail(f"spec missing {machine}")

    recipes_rs = (MOD / "api" / "src" / "recipes.rs").read_text(encoding="utf-8")
    for needle in ("adastra:compressor", "adastra:fuel_refinery", "adastra:cryo_freezer"):
        if needle not in recipes_rs:
            fail(f"fallback missing {needle}")

    draft = (ROOT / "pack" / "draft-mods.toml").read_text(encoding="utf-8")
    if 'id = "adastra"' not in draft or "on = []" not in draft:
        fail("pack/draft-mods.toml must list adastra with on = []")

    write_tracker(catalog)
    subprocess.check_call([sys.executable, str(ROOT / "tools" / "pack-adastra.py")])
    hmod = MOD / "dist" / "adastra.hmod"
    if not hmod.is_file():
        fail("pack did not write hmod")
    with zipfile.ZipFile(hmod) as archive:
        names = set(archive.namelist())
        native = json.loads(archive.read("horizon-native.json"))
    if native.get("mixins") != MIXINS:
        fail(f"horizon-native.json mixins must be {MIXINS}, got {native.get('mixins')}")
    if native.get("hooks") != HOOKS:
        fail(f"horizon-native.json hooks must be {HOOKS}, got {native.get('hooks')}")
    if native.get("horizon") != REV:
        fail("horizon-native.json horizon pin drifted")
    for required in (
        "horizon-mod.toml",
        "horizon-native.json",
        "assets/adastra/lang/en_us.json",
        "assets/adastra/items/desh_ingot.json",
        "assets/adastra/items/coal_generator.json",
        "data/adastra/horizon/block/coal_generator.json",
        "mixins/adastra/api/src/lib.rs",
        "mixins/adastra/NOTICE",
    ):
        if required not in names:
            fail(f"hmod missing {required}")
    for name in names:
        if "\\" in name:
            fail(f"non-POSIX zip path: {name}")
    print("adastra check ok")


if __name__ == "__main__":
    main()
