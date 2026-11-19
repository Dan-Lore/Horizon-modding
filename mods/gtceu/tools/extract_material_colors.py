"""Pull material RGB from GTM materials/*.java Material.Builder(GTCEu.id(..)).color(0x..)."""
from __future__ import annotations

import json
import re
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
REF = Path(
    r"C:\Dev\Horizon-modding\reference\GregTech-Modern\src\main\java\com\gregtechceu\gtceu\common\data\materials"
)
OUT = ROOT / "tracker" / "gtm_extract" / "material_colors.json"

# Builder(GTCEu.id("name")) ... .color(0xRRGGBB) within a short window
PAT = re.compile(
    r'Material\.Builder\(\s*GTCEu\.id\("([a-z0-9_]+)"\)\s*\)([\s\S]{0,800}?)(?:\.buildAndRegister\(\)|;)',
    re.I,
)
COLOR = re.compile(r"\.color\(\s*0x([0-9a-fA-F]+)\s*\)")


def main() -> None:
    colors: dict[str, int] = {}
    for p in REF.rglob("*.java"):
        text = p.read_text(encoding="utf-8", errors="ignore")
        for m in PAT.finditer(text):
            name = m.group(1)
            body = m.group(2)
            cm = COLOR.search(body)
            if cm:
                colors[name] = int(cm.group(1), 16)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps({"schema": 1, "colors": colors}, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(colors)} colors -> {OUT}")
    for k in ("tin", "silver", "bronze", "steel", "aluminium"):
        print(k, hex(colors.get(k, 0)))


if __name__ == "__main__":
    main()
