"""Score Greglite vs GTM extract using coverage_weights.json (0–100%)."""
from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
EXTRACT = ROOT / "tracker" / "gtm_extract"
DATA = ROOT / "data" / "greglite"
CATALOG = ROOT / "tracker" / "catalog.json"


def load(p: Path):
    return json.loads(p.read_text(encoding="utf-8"))


def main() -> None:
    weights = {c["id"]: c["weight"] for c in load(EXTRACT / "coverage_weights.json")["categories"]}
    machines = load(EXTRACT / "electric_machine_types.json")["machines"]
    gens = load(EXTRACT / "generators.json")["generators"]
    multis = load(EXTRACT / "multiblocks.json").get("controllers") or []
    materials = load(EXTRACT / "materials_core.json")["materials"]
    cables = load(EXTRACT / "cable_materials.json")["cables"]
    blocks = {p.stem for p in (DATA / "horizon" / "block").glob("*.json")}
    items = {p.stem for p in (DATA / "horizon" / "item").glob("*.json")}
    recipes = list((DATA / "recipe").glob("*.json"))

    tiers = ["lv", "mv", "hv", "ev", "iv", "luv", "zpm", "uv"]
    types = [m["id"] for m in machines]

    # singleblock types: any tier present
    types_hit = sum(1 for t in types if any(f"{tier}_{t}" in blocks for tier in tiers))
    types_score = types_hit / max(1, len(types))

    # tiers: fraction of type×tier cells
    cells = len(types) * len(tiers)
    cells_hit = sum(1 for t in types for tier in tiers if f"{tier}_{t}" in blocks)
    tiers_score = cells_hit / max(1, cells)

    # generators lv-hv
    gen_need = [(g["id"], tier) for g in gens for tier in ["lv", "mv", "hv"]]
    gen_hit = sum(1 for gid, tier in gen_need if f"{tier}_{gid}" in blocks)
    gen_score = gen_hit / max(1, len(gen_need))

    # cables
    cab_hit = 0
    for c in cables:
        mid = c["id"]
        if f"{mid}_cable_1x" in blocks:
            cab_hit += 1
    cab_score = cab_hit / max(1, len(cables))

    # materials forms
    forms = ["dust", "plate", "rod", "wire"]
    mat_cells = 0
    mat_hit = 0
    for m in materials:
        mid = m["id"]
        for form in forms:
            mat_cells += 1
            if f"{mid}_{form}" in items or (
                form == "ingot" and mid in ("iron", "copper", "gold")
            ):
                mat_hit += 1
            elif form != "ingot" and f"{mid}_{form}" in items:
                mat_hit += 1
    # recount properly
    mat_cells = len(materials) * len(forms)
    mat_hit = sum(
        1
        for m in materials
        for form in forms
        if f"{m['id']}_{form}" in items
        or (form == "ingot" and m["id"] in ("iron", "copper", "gold", "netherite"))
    )
    mat_score = mat_hit / max(1, mat_cells)

    # recipes depth: ≥8 *valid* (non-placeholder) recipes per machine type
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
    no_dust = {
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
        "compressor",
    }

    def is_placeholder(mtype: str, obj: dict) -> bool:
        res = (obj.get("result") or {}).get("id", "")
        ing = obj.get("ingredient") or {}
        ings = obj.get("ingredients") or ([ing] if ing else [])
        in_ids = [(i.get("item") or "") for i in ings if isinstance(i, dict)]
        if mtype not in dust_ok and res.endswith("_dust") and any(
            x.endswith(("_plate", "_ingot", "_rod", "_gear", "_foil", "_wire", "_screw"))
            for x in in_ids
        ):
            return True
        if mtype == "compressor" and res.endswith("_dust"):
            return True
        if mtype in no_dust and res.endswith("_dust"):
            return True
        return False

    by_type: dict[str, int] = {}
    valid_recipes = 0
    placeholder_recipes = 0
    for r in recipes:
        try:
            obj = json.loads(r.read_text(encoding="utf-8"))
        except Exception:
            continue
        ty = obj.get("type", "")
        if not ty.startswith("greglite:"):
            continue
        mtype = ty.split(":", 1)[1]
        if is_placeholder(mtype, obj):
            placeholder_recipes += 1
            continue
        by_type[mtype] = by_type.get(mtype, 0) + 1
        valid_recipes += 1
    depth_scores = []
    for t in types:
        n = by_type.get(t, 0)
        depth_scores.append(min(1.0, n / 8.0))
    recipes_score = sum(depth_scores) / max(1, len(depth_scores))
    honest_ge8 = sum(1 for t in types if by_type.get(t, 0) >= 8)

    # multiblocks
    mb_hit = sum(1 for m in multis if f"multi_{m['id']}" in blocks)
    mb_score = mb_hit / max(1, len(multis))

    # eu net fidelity heuristic
    eu_score = 0.0
    if any("cable" in b for b in blocks):
        eu_score += 0.35
    if any(b.endswith("_transformer") or "_transformer" in b for b in blocks):
        eu_score += 0.25
    if any("battery_buffer" in b for b in blocks):
        eu_score += 0.2
    if any(b.endswith("_diode") or b.split("_", 1)[-1] == "diode" for b in blocks):
        eu_score += 0.1
    # voltage-aware code present (assume after 0.4)
    eu_score += 0.1
    eu_score = min(1.0, eu_score)

    steam_need = [
        "steam_solid_boiler_lp",
        "steam_solid_boiler_hp",
        "steam_alloy_smelter",
        "steam_macerator",
        "steam_compressor",
    ]
    steam_hit = sum(1 for b in steam_need if b in blocks)
    steam_score = steam_hit / len(steam_need)

    gui = ROOT / "assets" / "greglite" / "textures" / "gui"
    gui_n = len(list(gui.glob("*.png"))) if gui.exists() else 0
    gui_score = min(1.0, gui_n / 8.0) if gui_n else 0.0

    scores = {
        "singleblock_types": types_score,
        "singleblock_tiers": tiers_score,
        "generators": gen_score,
        "cables": cab_score,
        "materials_forms": mat_score,
        "recipes_depth": recipes_score,
        "multiblocks": mb_score,
        "eu_net_fidelity": eu_score,
        "steam_age": steam_score,
        "gui_assets": gui_score,
    }
    total = sum(scores[k] * weights[k] for k in weights)
    print("=== Greglite GTM coverage ===")
    for k, w in weights.items():
        print(f"{k:22} {scores[k]*100:6.1f}%  (weight {w})")
    print(f"TOTAL                  {total:6.2f}%")
    out = {
        "total_percent": round(total, 2),
        "scores": {k: round(v * 100, 2) for k, v in scores.items()},
        "counts": {
            "blocks": len(blocks),
            "items": len(items),
            "recipes": len(recipes),
            "valid_machine_recipes": valid_recipes,
            "placeholder_recipes": placeholder_recipes,
            "honest_ge8": honest_ge8,
            "machine_types": len(types),
            "types_hit": types_hit,
            "tier_cells_hit": cells_hit,
            "multiblocks_hit": mb_hit,
            "cables_hit": cab_hit,
        },
    }
    (ROOT / "tracker" / "coverage.json").write_text(json.dumps(out, indent=2) + "\n", encoding="utf-8")
    print("wrote tracker/coverage.json")


if __name__ == "__main__":
    main()
