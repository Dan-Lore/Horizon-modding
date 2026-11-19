import json
from collections import Counter
from pathlib import Path

DATA = Path(r"C:/Dev/Horizon-modding/mods/gtceu/data/gtceu")
by: Counter[str] = Counter()
for r in (DATA / "recipe").glob("*.json"):
    o = json.loads(r.read_text(encoding="utf-8"))
    t = o.get("type", "")
    if t.startswith("gtceu:"):
        by[t.split(":", 1)[1]] += 1
machines = json.loads(
    Path(
        r"C:/Dev/Horizon-modding/mods/gtceu/tracker/gtm_extract/electric_machine_types.json"
    ).read_text(encoding="utf-8")
)["machines"]
for m in machines:
    n = by.get(m["id"], 0)
    if n < 8:
        print(f"{m['id']}: {n}")
print("total", sum(by.values()), "under8", sum(1 for m in machines if by.get(m["id"], 0) < 8))
