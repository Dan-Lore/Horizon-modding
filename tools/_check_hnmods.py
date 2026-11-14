import json
import zipfile
from pathlib import Path

nm = Path.home() / "AppData/Roaming/horizon/instances/create-nightly-test/horizon-native-mods"
for name in ["jei.hnmod", "jade.hnmod", "greglite.hmod", "create.hnmod"]:
    path = nm / name
    print("===", name, path.exists(), path.stat().st_size if path.exists() else 0, "===")
    if not path.exists():
        continue
    with zipfile.ZipFile(path) as z:
        for n in z.namelist():
            if n.endswith(("horizon-native.json", "horizon-mod.toml")) or n == "horizon-native.json":
                data = z.read(n)
                print(n, ":", data[:400].decode("utf-8", "replace"))

inst = Path.home() / "AppData/Roaming/horizon/instances/create-nightly-test"
print("instance json files:", [p.name for p in inst.glob("*.json")])
for p in ["mod-browser.json", "mods.json", "instance.json", "horizon.json"]:
    fp = inst / p
    if fp.exists():
        print("---", p, "---")
        print(fp.read_text(encoding="utf-8")[:800])
