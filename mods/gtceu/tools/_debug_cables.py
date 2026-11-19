import json
from pathlib import Path

blocks = {
    p.stem
    for p in Path(r"C:\Dev\Horizon-modding\mods\gtceu\data\gtceu\horizon\block").glob(
        "*.json"
    )
}
cables = json.loads(
    Path(
        r"C:\Dev\Horizon-modding\mods\gtceu\tracker\gtm_extract\cable_materials.json"
    ).read_text(encoding="utf-8")
)["cables"]
print("cable blocks", len([b for b in blocks if "cable" in b]))
print("sample", sorted(b for b in blocks if "cable" in b)[:30])
print("first ids", [c["id"] for c in cables[:8]])
hit = sum(1 for c in cables if f"{c['id']}_cable_1x" in blocks)
print("hit", hit, "of", len(cables))
missing = [c["id"] for c in cables if f"{c['id']}_cable_1x" not in blocks]
print("missing sample", missing[:20])
