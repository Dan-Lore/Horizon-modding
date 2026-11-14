"""Fill any missing {tier}_{type} blocks from GTM extract."""
from __future__ import annotations

import json
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parent))
from gen_gtm_parity import PROC_TIERS, human, menu_for, write, write_orientable_block  # type: ignore

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "data" / "greglite"
ASSETS = ROOT / "assets" / "greglite"
EXTRACT = ROOT / "tracker" / "gtm_extract"

machines = json.loads((EXTRACT / "electric_machine_types.json").read_text(encoding="utf-8"))[
    "machines"
]
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
lang_path = ASSETS / "lang" / "en_us.json"
lang = json.loads(lang_path.read_text(encoding="utf-8"))
n = 0
for m in machines:
    mtype = m["id"]
    inputs = 2 if mtype in multi_in else 1
    for tier in PROC_TIERS:
        block = f"{tier}_{mtype}"
        path = DATA / "horizon" / "block" / f"{block}.json"
        if path.exists():
            continue
        write_orientable_block(block)
        write(DATA / "horizon" / "menu" / f"{block}.json", menu_for(inputs, "processor"))
        lang[f"block.greglite.{block}"] = f"{tier.upper()} {human(mtype)}"
        n += 1
lang_path.write_text(json.dumps(lang, indent=2) + "\n", encoding="utf-8")
print("filled", n, "missing tier blocks")
