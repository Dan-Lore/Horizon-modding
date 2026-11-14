import json
import shutil
import zipfile
from pathlib import Path

src = Path(r"C:/Dev/Horizon-modding/mods/greglite")
toml = src / "horizon-mod.toml"
text = toml.read_text(encoding="utf-8")
text = text.replace('version = "0.4.0"', 'version = "0.4.1"')
toml.write_text(text, encoding="utf-8")

stage = Path(r"C:/Dev/Horizon-modding/tools/_greglite-pack")
out = (
    Path.home()
    / "AppData/Roaming/horizon/instances/create-nightly-test/horizon-native-mods/greglite.hmod"
)
shutil.rmtree(stage, ignore_errors=True)
(stage / "mixins/greglite").mkdir(parents=True)
shutil.copy(src / "horizon-mod.toml", stage)
shutil.copytree(src / "assets", stage / "assets")
shutil.copytree(src / "data", stage / "data")
shutil.copy(src / "horizon-mixin.toml", stage / "mixins/greglite/")
shutil.copytree(src / "api", stage / "mixins/greglite/api")
(stage / "horizon-native.json").write_text(
    json.dumps(
        {
            "schema": 1,
            "id": "greglite",
            "version": "0.4.1",
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
print("packed", out.stat().st_size)

for ver in ["native-9f42064-39096c24e354"]:
    d = Path.home() / f"AppData/Roaming/horizon-launcher/versions/{ver}/native-content/greglite"
    if d.exists():
        shutil.rmtree(d)
    d.mkdir(parents=True)
    shutil.copy(src / "horizon-mod.toml", d)
    shutil.copytree(src / "assets", d / "assets")
    shutil.copytree(src / "data", d / "data")
    print("restored", ver)

hm = Path.home() / "AppData/Roaming/horizon/instances/create-nightly-test/horizon-mods/greglite"
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
