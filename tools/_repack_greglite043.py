"""Pack GregTech 0.4.3 and restore content onto create-nightly-test native."""
import json
import shutil
import zipfile
from pathlib import Path

VER = "0.4.3"
NATIVE = "native-9f42064-ced9cfd3616b"
src = Path(r"C:/Dev/Horizon-modding/mods/gtceu")
stage = Path(r"C:/Dev/Horizon-modding/tools/_gtceu-pack")
out = (
    Path.home()
    / "AppData/Roaming/horizon/instances/create-nightly-test/horizon-native-mods/gtceu.hmod"
)

shutil.rmtree(stage, ignore_errors=True)
(stage / "mixins/gtceu").mkdir(parents=True)
shutil.copy(src / "horizon-mod.toml", stage)
shutil.copytree(src / "assets", stage / "assets")
shutil.copytree(src / "data", stage / "data")
shutil.copy(src / "horizon-mixin.toml", stage / "mixins/gtceu/")
shutil.copytree(src / "api", stage / "mixins/gtceu/api")
(stage / "horizon-native.json").write_text(
    json.dumps(
        {
            "schema": 1,
            "id": "gtceu",
            "version": VER,
            "game": "26.3",
            "horizon": "4e5296d1800b3f89f2ae48dfd99d431801df4d46",
            "mixins": "5a64af938ec86b00d53d16a408aabc0038fb3e57",
            "hooks": 36,
        }
    )
)
if out.exists():
    out.unlink()
with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
    for p in stage.rglob("*"):
        if p.is_file():
            z.write(p, p.relative_to(stage).as_posix())
print("packed", out, out.stat().st_size)

d = Path.home() / f"AppData/Roaming/horizon-launcher/versions/{NATIVE}/native-content/gtceu"
if d.exists():
    shutil.rmtree(d)
d.mkdir(parents=True)
shutil.copy(src / "horizon-mod.toml", d)
shutil.copytree(src / "assets", d / "assets")
shutil.copytree(src / "data", d / "data")
print("restored", NATIVE)

hm = Path.home() / "AppData/Roaming/horizon/instances/create-nightly-test/horizon-mods/gtceu"
if hm.exists():
    shutil.rmtree(hm)
hm.mkdir(parents=True)
shutil.copy(src / "horizon-mod.toml", hm)
shutil.copytree(src / "assets", hm / "assets")
shutil.copytree(src / "data", hm / "data")
cache = Path.home() / "AppData/Roaming/horizon/instances/create-nightly-test/.horizon-cache/mod-content"
if cache.exists():
    shutil.rmtree(cache)
print("done")
