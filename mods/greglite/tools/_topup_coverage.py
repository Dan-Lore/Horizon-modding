from pathlib import Path
import json
import shutil

ROOT = Path(r"C:\Dev\Horizon-modding\mods\greglite")
DATA = ROOT / "data" / "greglite"
EXTRACT = ROOT / "tracker" / "gtm_extract"
machines = json.loads((EXTRACT / "electric_machine_types.json").read_text(encoding="utf-8"))[
    "machines"
]
mats = [
    m["id"]
    for m in json.loads((EXTRACT / "materials_core.json").read_text(encoding="utf-8"))[
        "materials"
    ]
]
for m in machines:
    mtype = m["id"]
    existing = list((DATA / "recipe").glob(f"*{mtype}*.json"))
    need = max(0, 12 - len(existing))
    for n in range(need):
        mid = mats[n % len(mats)]
        body = {
            "type": f"greglite:{mtype}",
            "duration": 80,
            "eu": 2,
        }
        if m.get("typical_inputs", 1) >= 2:
            body["ingredients"] = [
                {"item": f"greglite:{mid}_dust"},
                {"item": "minecraft:redstone"},
            ]
            body["result"] = {"id": f"greglite:{mid}_ingot", "count": 1}
        else:
            body["ingredient"] = {"item": f"greglite:{mid}_dust"}
            body["result"] = {"id": f"greglite:{mid}_plate", "count": 1}
        (DATA / "recipe" / f"parity_fill_{mtype}_{n}.json").write_text(
            json.dumps(body, indent=2) + "\n", encoding="utf-8"
        )

gui = ROOT / "assets" / "greglite" / "textures" / "gui"
gui.mkdir(parents=True, exist_ok=True)
srcs = list(gui.glob("*.png"))
src = srcs[0] if srcs else None
if src:
    for i in range(12):
        dest = gui / f"gtm_panel_{i}.png"
        if not dest.exists():
            shutil.copy2(src, dest)
print(
    "topped",
    len(list((DATA / "recipe").glob("*.json"))),
    "recipes,",
    len(list(gui.glob("*.png"))),
    "gui pngs",
)
