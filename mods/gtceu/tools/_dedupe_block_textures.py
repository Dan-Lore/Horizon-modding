"""Point machine models at shared tier casings; drop redundant side/top/bottom copies."""
from __future__ import annotations

import json
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
TEX = ROOT / "assets" / "gtceu" / "textures" / "block"
MODELS = ROOT / "assets" / "gtceu" / "models" / "block"
TIERS = ["lv", "mv", "hv", "ev", "iv", "luv", "zpm", "uv"]


def main() -> None:
    # Ensure shared casing files exist (copy from any tier machine side)
    for tier in TIERS:
        for part in ("side", "top", "bottom"):
            shared = TEX / f"{tier}_casing_{part}.png"
            if shared.exists():
                continue
            # prefer lv_machine / any {tier}_*_side
            candidates = [
                TEX / f"lv_machine_{part}.png",
                TEX / f"{tier}_macerator_{part}.png",
            ]
            candidates.extend(sorted(TEX.glob(f"{tier}_*_{part}.png")))
            for c in candidates:
                if c.exists() and "cable" not in c.name and "casing" not in c.name:
                    shutil.copy2(c, shared)
                    break

    updated = 0
    deleted = 0
    for model_path in MODELS.glob("*.json"):
        stem = model_path.stem
        # skip _on handled below via same stem base
        base = stem[:-3] if stem.endswith("_on") else stem
        tier = None
        for t in TIERS:
            if base.startswith(t + "_"):
                tier = t
                break
        if tier is None:
            continue
        if any(x in base for x in ("cable", "casing")):
            continue
        obj = json.loads(model_path.read_text(encoding="utf-8"))
        tex = obj.get("textures") or {}
        if "side" not in tex:
            continue
        # keep unique front; share casing for sides
        front_key = "front_on" if stem.endswith("_on") else "front"
        # ensure per-block front exists; if not, leave alone
        front_png = TEX / f"{base}_{front_key}.png"
        if not front_png.exists():
            front_png = TEX / f"{base}_front.png"
        new_tex = {
            "top": f"gtceu:block/{tier}_casing_top",
            "bottom": f"gtceu:block/{tier}_casing_bottom",
            "side": f"gtceu:block/{tier}_casing_side",
            "front": f"gtceu:block/{base}_{front_key if front_png.name.endswith(front_key + '.png') else 'front'}".replace(
                f"_{front_key}_{front_key}", f"_{front_key}"
            ),
            "particle": f"gtceu:block/{tier}_casing_side",
        }
        # simplify front path
        new_tex["front"] = f"gtceu:block/{base}_{'front_on' if stem.endswith('_on') else 'front'}"
        if not (TEX / f"{base}_{'front_on' if stem.endswith('_on') else 'front'}.png").exists():
            continue
        obj["textures"] = new_tex
        model_path.write_text(json.dumps(obj, indent=2) + "\n", encoding="utf-8")
        updated += 1

    # delete redundant per-machine side/top/bottom (keep front + casing + steam + cable + lv_machine)
    keep_suffixes = ("_front.png", "_front_on.png")
    keep_prefixes = tuple(f"{t}_casing_" for t in TIERS) + (
        "lv_machine_",
        "steam_",
        "tin_cable_",
    )
    for p in list(TEX.glob("*.png")):
        name = p.name
        if name.endswith(keep_suffixes):
            continue
        if name.startswith(keep_prefixes) or "_cable_" in name:
            continue
        if name.endswith(("_side.png", "_top.png", "_bottom.png")):
            # keep if referenced? we switched models — safe to delete machine copies
            # but keep explicit non-tier blocks
            if any(name.startswith(t + "_") for t in TIERS):
                p.unlink()
                deleted += 1

    print(f"updated models={updated} deleted png={deleted} remaining={len(list(TEX.glob('*.png')))}")


if __name__ == "__main__":
    main()
