from pathlib import Path
root = Path(r"C:\dev\Horizon-modding\mods\adastra\data")
n = 0
for p in root.rglob("*.json"):
    t = p.read_text(encoding="utf-8")
    if '"sounds": "minecraft:metal"' in t:
        p.write_text(t.replace('"sounds": "minecraft:metal"', '"sounds": "minecraft:iron_block"'), encoding="utf-8")
        n += 1
print("fixed", n)
